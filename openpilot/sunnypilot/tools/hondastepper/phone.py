#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The car setup from a phone (hondastepper). The comma device serves a page on its own Wi-Fi hotspot: turn the hotspot
on, join it from the phone, and open http://192.168.43.1:8090. The page runs the car setup's two parts
(accord_setup.sh car and drive) and turns their questions into buttons. It also shows the software version, whether
each part has passed, and the steering strength sunnypilot has learned (L.A.F.), which the comma four's screen
doesn't show.

launch_chffrplus.sh starts this outside sunnypilot's manager, because part 1 stops the manager. It answers only
requests that come in over the hotspot, and starts a part only while the car stands still.
"""
import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8090
HOTSPOT_IP = "192.168.43.1"        # the comma device's address on its own hotspot (openpilot's wifi_manager)
ANY_ADDRESS_ENV = "HONDASTEPPER_PHONE_ANY_ADDRESS"   # tests only: answer on any address
COMMAND_ENV = "HONDASTEPPER_PHONE_COMMAND"           # tests only: what to run instead of accord_setup.sh (JSON list)
POST_HEADER = "X-Hondastepper"     # the page sends it with every button; other web pages can't
MOVING_M_S = 0.5
LOG_LINES = 200
PARTS = ("car", "drive")


def basedir() -> str:
  return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


def version() -> str:
  try:
    from openpilot.sunnypilot.tools.hondastepper import VERSION
    return VERSION
  except Exception:
    return "?"


def setup_status() -> dict:
  """Which parts of the car setup have passed, from the saved config."""
  try:
    from opendbc.car.hondastepper.config import load_raw_config, parse_config
    raw = load_raw_config()
    setup = raw.get("setup", {})
    return {"part1": setup.get("parked"), "part2": setup.get("drive"), "verified": bool(parse_config(raw).verified)}
  except Exception as e:
    return {"part1": None, "part2": None, "verified": False, "error": str(e)}


def learned_steering() -> dict | None:
  """The steering strength sunnypilot has learned (L.A.F.) and how far its calibration is, from its cache."""
  try:
    from openpilot.common.params import Params
    from cereal import log
    data = Params().get("LiveTorqueParameters")
    if not data:
      return None
    with log.Event.from_bytes(data) as evt:
      t = evt.lateralTorqueParameters
      return {"laf": round(float(t.latAccelFactorFiltered), 2), "calibrated_percent": int(t.calPerc)}
  except Exception:
    return None


def car_moving() -> bool | None:
  """True if sunnypilot says the car is moving, None if it can't tell (sunnypilot not running)."""
  try:
    import cereal.messaging as messaging
    sm = messaging.SubMaster(["carState"])
    end = time.monotonic() + 1.0
    while time.monotonic() < end:
      sm.update(100)
      if sm.updated["carState"]:
        return sm["carState"].vEgo > MOVING_M_S
  except Exception:
    pass
  return None


class SetupRun:
  """One run of a car setup part: the tool as a child process, its messages, and the question it waits on."""

  def __init__(self, part: str, command: list[str]):
    self.part = part
    self.log: list[dict] = []
    self.ask: dict | None = None
    self.seq = 0
    self.exit_code: int | None = None
    self.lock = threading.Lock()
    env = {**os.environ, "HONDASTEPPER_UI": "phone", "PYTHONUNBUFFERED": "1"}
    self.proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 env=env, text=True, bufsize=1, start_new_session=True)
    threading.Thread(target=self._read, daemon=True).start()

  def _add(self, entry: dict):
    self.log.append(entry)
    del self.log[:-LOG_LINES]

  def _read(self):
    assert self.proc.stdout is not None
    for line in self.proc.stdout:
      line = line.rstrip("\n")
      try:
        msg = json.loads(line)
      except ValueError:
        msg = None
      with self.lock:
        if isinstance(msg, dict) and msg.get("t") == "ask":
          self.seq += 1
          self.ask = {"seq": self.seq, "text": str(msg.get("text", "")), "choices": msg.get("choices", []),
                      "free_text": bool(msg.get("free_text"))}
          self._add({"ask": self.ask["text"]})
        elif isinstance(msg, dict) and msg.get("t") == "say":
          if str(msg.get("text", "")).strip():
            self._add({"say": str(msg["text"])})
        elif line.strip():
          self._add({"say": line})
    code = self.proc.wait()
    with self.lock:
      self.exit_code = code
      self.ask = None
      for pipe in (self.proc.stdin, self.proc.stdout):
        try:
          if pipe is not None:
            pipe.close()
        except OSError:
          pass

  def answer(self, seq: int, value: str, label: str = "") -> bool:
    with self.lock:
      if self.ask is None or self.ask["seq"] != seq or self.proc.stdin is None:
        return False
      self._add({"answer": label or value})
      self.ask = None
      try:
        self.proc.stdin.write(value.replace("\n", " ") + "\n")
        self.proc.stdin.flush()
      except OSError:
        return False
      return True

  def running(self) -> bool:
    return self.exit_code is None

  def state(self) -> dict:
    with self.lock:
      return {"part": self.part, "running": self.running(), "exit_code": self.exit_code, "ask": self.ask,
              "log": list(self.log)}


class App:
  def __init__(self):
    self.run: SetupRun | None = None
    self.lock = threading.Lock()

  def command(self, part: str) -> list[str]:
    override = os.environ.get(COMMAND_ENV)
    if override:
      return [*json.loads(override), part]
    return ["bash", os.path.join(basedir(), "accord_setup.sh"), part]

  def start(self, part: str) -> tuple[bool, str]:
    if part not in PARTS:
      return False, "unknown part"
    with self.lock:
      if self.run is not None and self.run.running():
        return False, "A part of the car setup is already running."
      if car_moving():
        return False, "The car is moving. Park first."
      self.run = SetupRun(part, self.command(part))
      return True, ""

  def state(self) -> dict:
    return {"version": version(), "setup": setup_status(), "steering": learned_steering(),
            "run": self.run.state() if self.run is not None else None}


APP = App()


class Handler(BaseHTTPRequestHandler):
  server_version = "hondastepper"

  def log_message(self, format, *args):  # noqa: A002  quiet: the device's log is no place for every poll
    pass

  def _allowed(self) -> bool:
    if os.environ.get(ANY_ADDRESS_ENV) == "1":
      return True
    return self.connection.getsockname()[0] == HOTSPOT_IP

  def _send(self, code: int, body: bytes, kind: str = "application/json"):
    self.send_response(code)
    self.send_header("Content-Type", kind)
    self.send_header("Content-Length", str(len(body)))
    self.send_header("Cache-Control", "no-store")
    self.end_headers()
    self.wfile.write(body)

  def _json(self, code: int, obj):
    self._send(code, json.dumps(obj).encode())

  def do_GET(self):
    if not self._allowed():
      return self._send(403, b"Only over the comma device's hotspot", "text/plain")
    if self.path in ("/", "/index.html"):
      return self._send(200, PAGE.replace("{{VERSION}}", version()).encode(), "text/html; charset=utf-8")
    if self.path == "/state":
      return self._json(200, APP.state())
    return self._send(404, b"Not found", "text/plain")

  def do_POST(self):
    if not self._allowed() or self.headers.get(POST_HEADER) != "1":
      return self._send(403, b"Not allowed", "text/plain")
    try:
      length = min(int(self.headers.get("Content-Length", "0")), 4096)
      body = json.loads(self.rfile.read(length) or b"{}")
    except ValueError:
      return self._json(400, {"ok": False, "error": "bad request"})
    if self.path == "/start":
      ok, err = APP.start(str(body.get("part", "")))
      return self._json(200 if ok else 409, {"ok": ok, "error": err})
    if self.path == "/answer":
      run = APP.run
      ok = run is not None and run.answer(int(body.get("seq", -1)), str(body.get("value", ""))[:40],
                                          str(body.get("label", ""))[:60])
      return self._json(200 if ok else 409, {"ok": ok})
    return self._send(404, b"Not found", "text/plain")


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Accord car setup</title>
<style>
:root { --bg: #f6f6f4; --card: #ffffff; --ink: #1d1d1b; --quiet: #5f5f5a; --line: #d9d9d4; --go: #1f6feb; --ok: #1a7f37; --bad: #b42318; }
@media (prefers-color-scheme: dark) {
  :root { --bg: #161615; --card: #22221f; --ink: #f0efe9; --quiet: #a9a8a0; --line: #3a3a36;
          --go: #4c8dff; --ok: #3fb950; --bad: #ff6b5e; }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 17px/1.45 -apple-system, system-ui, sans-serif; }
main { max-width: 560px; margin: 0 auto; padding: 16px; }
h1 { font-size: 20px; margin: 4px 0 2px; }
.sub { color: var(--quiet); font-size: 14px; margin-bottom: 14px; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; margin-bottom: 12px; }
.row { display: flex; justify-content: space-between; gap: 12px; padding: 4px 0; }
.ok { color: var(--ok); font-weight: 600; } .no { color: var(--quiet); } .bad { color: var(--bad); font-weight: 600; }
button { width: 100%; font: inherit; font-weight: 600; padding: 16px; margin: 6px 0; border-radius: 10px;
         border: 1px solid var(--line); background: var(--card); color: var(--ink); }
button.main { background: var(--go); border-color: var(--go); color: #fff; }
button:disabled { opacity: .45; }
input { width: 100%; font: inherit; padding: 14px; border-radius: 10px; border: 1px solid var(--line);
        background: var(--card); color: var(--ink); margin: 6px 0; }
.ask { font-size: 19px; font-weight: 600; margin: 0 0 8px; white-space: pre-wrap; }
.log { font-size: 14px; color: var(--quiet); white-space: pre-wrap; max-height: 40vh; overflow: auto; }
.log p { margin: 0 0 8px; } .log .me { color: var(--go); }
.hide { display: none; }
#err { color: var(--bad); font-weight: 600; }
</style></head>
<body><main>
<h1>Honda Accord lane keeping</h1>
<div class="sub">Car setup, software {{VERSION}}</div>
<div id="err"></div>
<div class="card" id="status">
  <div class="row"><span>Part 1, parked</span><span id="p1" class="no">not yet</span></div>
  <div class="row"><span>Part 2, drive check</span><span id="p2" class="no">not yet</span></div>
  <div class="row"><span>Lane keeping</span><span id="lk" class="no">off until both pass</span></div>
  <div class="row"><span>Learned steering strength (L.A.F.)</span><span id="laf" class="no">not learned yet</span></div>
</div>
<div class="card" id="choose">
  <button class="main" onclick="start('car')">Start part 1 (parked, about 10 minutes)</button>
  <button onclick="start('drive')">Start part 2 (after a 5 minute drive)</button>
</div>
<div class="card hide" id="running">
  <p class="ask" id="ask"></p>
  <div id="choices"></div>
  <div id="free" class="hide">
    <input id="text" autocomplete="off" autocapitalize="characters">
    <button class="main" onclick="send(document.getElementById('text').value)">Send</button>
  </div>
  <div class="log" id="log"></div>
</div>
</main>
<script>
let current = null, busy = false;
const H = {"Content-Type": "application/json", "X-Hondastepper": "1"};
function el(id) { return document.getElementById(id); }
async function post(path, body) {
  const r = await fetch(path, {method: "POST", headers: H, body: JSON.stringify(body)});
  return r.json();
}
async function start(part) {
  if (busy) return;
  const r = await post("/start", {part}).catch(() => ({ok: false, error: "Not connected."}));
  if (!r.ok) el("err").textContent = r.error || "Couldn't start.";
}
async function send(value, label) {
  if (!current || busy) return;
  busy = true;
  await post("/answer", {seq: current.seq, value, label: label || value}).catch(() => {});
  el("text").value = "";
  busy = false;
  tick();
}
function when(t) { return t ? "passed " + t.slice(0, 10) : null; }
function render(s) {
  el("err").textContent = "";
  const p1 = when(s.setup.part1), p2 = when(s.setup.part2);
  el("p1").textContent = p1 || "not yet"; el("p1").className = p1 ? "ok" : "no";
  el("p2").textContent = p2 || "not yet"; el("p2").className = p2 ? "ok" : "no";
  el("lk").textContent = s.setup.verified ? "allowed" : "off until both pass"; el("lk").className = s.setup.verified ? "ok" : "no";
  if (s.steering && s.steering.calibrated_percent > 0) {
    el("laf").textContent = s.steering.laf.toFixed(2) + " (" + s.steering.calibrated_percent + "% learned)";
    el("laf").className = "";
  }
  const run = s.run, live = run && run.running;
  el("choose").classList.toggle("hide", !!live);
  el("running").classList.toggle("hide", !run);
  if (!run) return;
  const log = el("log");
  log.innerHTML = "";
  const entries = run.log.slice().reverse();
  if (run.ask && entries.length && entries[0].ask !== undefined) entries.shift();   // the question shown above
  for (const e of entries) {
    const p = document.createElement("p");
    if (e.answer !== undefined) { p.className = "me"; p.textContent = "You: " + (e.answer || "done"); }
    else p.textContent = e.say || e.ask || "";
    log.appendChild(p);
  }
  const a = run.ask;
  if (a && (!current || current.seq !== a.seq)) {
    current = a;
    el("ask").textContent = a.text;
    const box = el("choices"); box.innerHTML = "";
    for (const [value, label] of a.choices) {
      const b = document.createElement("button"); b.className = "main"; b.textContent = label;
      b.onclick = () => send(value, label); box.appendChild(b);
    }
    el("free").classList.toggle("hide", !a.free_text);
  } else if (!a) {
    current = null; el("choices").innerHTML = ""; el("free").classList.add("hide");
    el("ask").textContent = live ? "Working..." : (run.exit_code === 0 ? "Finished." : "Stopped. Read the messages below.");
  }
}
async function tick() {
  try { render(await (await fetch("/state", {cache: "no-store"})).json()); }
  catch (e) {
    el("err").textContent = "Not connected. If the comma device is restarting, this page comes back by itself in a " +
      "few minutes. Otherwise check that this phone is on the comma device's Wi-Fi.";
  }
}
tick(); setInterval(tick, 800);
</script>
</body></html>
"""


def main() -> int:
  try:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
  except OSError as e:
    print(f"hondastepper phone page: can't listen on port {PORT}: {e}", file=sys.stderr)
    return 1
  server.daemon_threads = True
  server.serve_forever()
  return 0


if __name__ == "__main__":
  sys.exit(main())
