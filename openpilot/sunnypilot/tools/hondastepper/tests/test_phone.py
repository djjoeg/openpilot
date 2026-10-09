"""
The car setup's phone page (phone.py) against a stand-in for the setup tool that asks its questions through the same
prompter: the page starts it, shows its messages, turns its questions into buttons, passes the answers back, and
refuses what it should.
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from openpilot.sunnypilot.tools.hondastepper import phone
from openpilot.sunnypilot.tools.hondastepper.prompter import PHONE, UI_ENV

STAND_IN = """
import sys
from openpilot.sunnypilot.tools.hondastepper.prompter import Prompter
p = Prompter()
p.say("Hello from part " + sys.argv[1])
answer = p.ask("Automatic or manual? Type a or m and press Enter:", (("a", "Automatic"), ("m", "Manual")),
               "Automatic or manual?")
p.say("You said " + answer)
p.step("Press the brake", button="Done")
p.say("Finished")
"""


class TestPhonePage(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.tmp = tempfile.TemporaryDirectory()
    tool = os.path.join(cls.tmp.name, "stand_in.py")
    with open(tool, "w") as f:
      f.write(STAND_IN)
    os.environ[phone.COMMAND_ENV] = json.dumps([sys.executable, tool])
    os.environ[phone.ANY_ADDRESS_ENV] = "1"
    cls.server = ThreadingHTTPServer(("127.0.0.1", 0), phone.Handler)
    cls.url = f"http://127.0.0.1:{cls.server.server_address[1]}"
    threading.Thread(target=cls.server.serve_forever, daemon=True).start()

  @classmethod
  def tearDownClass(cls):
    cls.server.shutdown()
    cls.server.server_close()
    os.environ.pop(phone.COMMAND_ENV, None)
    os.environ.pop(phone.ANY_ADDRESS_ENV, None)
    cls.tmp.cleanup()

  def setUp(self):
    phone.APP.run = None

  def get(self, path):
    with urllib.request.urlopen(self.url + path, timeout=5) as r:
      return r.status, r.read()

  def post(self, path, body, header=True):
    req = urllib.request.Request(self.url + path, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **({phone.POST_HEADER: "1"} if header else {})})
    try:
      with urllib.request.urlopen(req, timeout=5) as r:
        return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
      return e.code, None

  def state(self):
    return json.loads(self.get("/state")[1])

  def wait_for(self, check, timeout=10.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
      s = self.state()
      if check(s):
        return s
      time.sleep(0.05)
    self.fail(f"timed out; last state {s}")

  def test_page(self):
    status, body = self.get("/")
    self.assertEqual(status, 200)
    self.assertIn(b"Start part 1", body)
    self.assertNotIn(b"{{VERSION}}", body)

  def test_a_whole_run(self):
    self.assertEqual(self.post("/start", {"part": "car"})[0], 200)
    s = self.wait_for(lambda s: s["run"] and s["run"]["ask"])
    ask = s["run"]["ask"]
    self.assertEqual(ask["text"], "Automatic or manual?")
    self.assertEqual(ask["choices"], [["a", "Automatic"], ["m", "Manual"]])
    self.assertIn({"say": "Hello from part car"}, s["run"]["log"])
    # a second start while it runs, and an answer to a question that isn't the current one, are refused
    self.assertEqual(self.post("/start", {"part": "drive"})[0], 409)
    self.assertEqual(self.post("/answer", {"seq": ask["seq"] + 5, "value": "m"})[0], 409)
    self.assertEqual(self.post("/answer", {"seq": ask["seq"], "value": "a"})[0], 200)
    s = self.wait_for(lambda s: s["run"]["ask"] and s["run"]["ask"]["seq"] != ask["seq"])
    self.assertEqual(s["run"]["ask"]["choices"], [["", "Done"]])
    self.assertIn({"say": "You said a"}, s["run"]["log"])
    self.post("/answer", {"seq": s["run"]["ask"]["seq"], "value": ""})
    s = self.wait_for(lambda s: not s["run"]["running"])
    self.assertEqual(s["run"]["exit_code"], 0)
    self.assertIn({"say": "Finished"}, s["run"]["log"])

  def test_refusals(self):
    self.assertEqual(self.post("/start", {"part": "car"}, header=False)[0], 403)   # another web page can't press buttons
    self.assertEqual(self.post("/start", {"part": "erase"})[0], 409)
    self.assertIsNone(phone.APP.run)
    os.environ.pop(phone.ANY_ADDRESS_ENV)
    try:   # only over the hotspot's address
      with self.assertRaises(urllib.error.HTTPError) as e:
        self.get("/state")
      self.assertEqual(e.exception.code, 403)
    finally:
      os.environ[phone.ANY_ADDRESS_ENV] = "1"


class TestPrompterPhoneMode(unittest.TestCase):
  def test_json_lines(self):
    code = "\n".join((
      "from openpilot.sunnypilot.tools.hondastepper.prompter import Prompter",
      "p = Prompter()",
      "p.say('hi')",
      "print('answer=' + str(p.yes_no('Did it turn LEFT? Type y or n and press Enter:', 'Did it turn LEFT?')))",
    ))
    out = subprocess.run([sys.executable, "-c", code], input="y\n", capture_output=True, text=True, timeout=30,
                         env={**os.environ, UI_ENV: PHONE}, check=True).stdout.splitlines()
    self.assertEqual(json.loads(out[0]), {"t": "say", "text": "hi"})
    self.assertEqual(json.loads(out[1]), {"t": "ask", "text": "Did it turn LEFT?", "choices": [["y", "Yes"], ["n", "No"]],
                                          "free_text": False})
    self.assertEqual(out[2], "answer=True")

  def test_terminal_unchanged(self):
    printed, asked = [], []
    from openpilot.sunnypilot.tools.hondastepper.prompter import Prompter
    p = Prompter(input_fn=lambda q: asked.append(q) or "n", print_fn=printed.append, ui=PHONE)
    p.say("hi")
    self.assertFalse(p.yes_no("Type y or n and press Enter:"))
    self.assertEqual(printed, ["hi"])
    self.assertEqual(asked, ["\nType y or n and press Enter: "])


if __name__ == "__main__":
  unittest.main()
