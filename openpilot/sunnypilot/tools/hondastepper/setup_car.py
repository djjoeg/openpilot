#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Car setup for the Honda Accord with the add-on steering motor (hondastepper), part 1 of 2: parked.

Run it on the comma device over SSH, with the car parked, the engine running and the steering wheel straight:

  /data/openpilot/accord_setup.sh car

It stops openpilot, then asks you to do simple things one at a time (press the brake, switch a blinker on, shift
gears, turn the steering wheel) while it watches the car's data and the motor. It checks where the car keeps
everything lane keeping needs, finds it when it's somewhere else, checks which way the motor turns, saves the
result to /data/hondastepper/config.json, and restarts the comma device, which rebuilds the software with it.

Part 2 is the drive check (accord_setup.sh drive) after a few minutes of driving. Lane keeping stays off until
both parts pass.
"""
import dataclasses
import datetime
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass, field

from opendbc.car.hondastepper import discovery as dsc
from opendbc.car.hondastepper.config import TEETH_SETS, load_raw_config, parse_config, save_device_config, device_config_path
from opendbc.car.hondastepper.values import StepperControlStatus, StepperMode
from openpilot.sunnypilot.tools.hondastepper.device import CanSession

INTRO = """
Honda Accord lane keeping: car setup, part 1 of 2 (parked)

This takes about 10 minutes. It asks you to do one simple thing at a time: press a pedal, switch a turn signal,
move the shifter, turn the steering wheel. Do it, press Enter, and hold it for 3 seconds while it watches.
At the end it saves what it learned and restarts the comma device.

Before you start: car parked somewhere safe, engine running, steering wheel straight. It tells you when to pull
the lift lever down.
"""

MSG_MORE_GEARS = " ".join((
  "If the shifter goes further than D (like D3, 2 or 1), move it one more step and type what the dash shows",
  "(for example D3), then press Enter. If it doesn't go further, just press Enter.",
))
MSG_PUSH = " ".join((
  "Turn the wheel back to straight, so the motor gear is in the middle of the teeth, and let go of the wheel completely.",
  "Watch the top of the steering wheel: the motor will turn it a little by itself, then let go.",
))
MSG_DID_IT_TURN_LEFT = " ".join((
  "Did the steering wheel just turn LEFT by itself (the top of the wheel moved towards the driver's door)?",
  "Type y or n and press Enter:",
))
MSG_TRY_OTHER_WAY = " ".join((
  "Then the motor's direction is the other way round (perhaps the wheel was turned right first a moment ago).",
  "Trying the other way.",
))
MSG_NEVER_LEFT = " ".join((
  "the motor turned the steering wheel both times, the second time the other way, but you didn't see it go left",
  "either time, so its direction couldn't be settled. Run this again and watch the top of the steering wheel during",
  "each push: one of the two pushes turns it left",
))
MSG_LEVER_DOWN = " ".join((
  "Steering wheel straight. Pull the lift lever down until it clicks, so the motor gear drops onto the middle of the",
  "steering wheel teeth.",
  "Hands off the wheel.",
))
MSG_NO_MOTOR = " ".join((
  "No answer from the motor. Check that the lift lever is all the way down (it switches the motor's power on)",
  "and that the motor's cable is plugged in.",
))
MSG_WHICH_TEETH = " ".join((
  "Which steering wheel teeth are on the steering wheel: the short ones (they reach 15 degrees each way) or the long",
  "ones (29 degrees each way)? Type 15 or 29 and press Enter:",
))
MSG_TURN_LEFT = " ".join((
  "Slowly turn the steering wheel LEFT until the motor gear has run off the end of the steering wheel teeth and stopped",
  "turning (a sixteenth of a turn with the short teeth, an eighth with the long ones). Stop there and hold the wheel",
  "still.",
))
MSG_TURN_RIGHT = " ".join((
  "Now slowly turn the wheel RIGHT, past the middle, until the motor gear has run off the other end of the teeth and",
  "stopped turning. Stop there and hold the wheel still.",
))
MSG_PART1_PASSED = " ".join((
  "Part 1 passed. Next: drive for at least 5 minutes with the lift lever DOWN (lane keeping stays off until both parts",
  "pass, so the motor only rides along), at a mix of speeds between about 15 and 50 mph, with some curves or lane",
  "changes, where the comma device can see the sky. Then run the drive check: /data/openpilot/accord_setup.sh drive",
))

RECORD_SECONDS = 3.0
SETTLE_SECONDS = 0.5     # the start of each recording is ignored while things settle
PUSH_TORQUE_FW_NM = 3.0  # motor torque for the push test, about 3 Nm at the steering wheel
PUSH_STOP_DEG = 6.0      # the push lets go once the steering wheel has turned this far


class Prompter:
  def __init__(self, input_fn: Callable[[str], str] = input, print_fn: Callable[[str], None] = print):
    self.input_fn, self.print_fn = input_fn, print_fn

  def say(self, text: str = ""):
    self.print_fn(text)

  def step(self, text: str):
    self.input_fn(f"\n{text}\n  Press Enter when that's done. ")

  def ask(self, text: str) -> str:
    return self.input_fn(f"\n{text} ").strip()

  def yes_no(self, text: str) -> bool | None:
    """True for y, False for n; asks again up to three times, then None."""
    for _ in range(3):
      answer = self.ask(text).lower()
      if answer.startswith("y"):
        return True
      if answer.startswith("n"):
        return False
    return None


@dataclass
class ParkedResult:
  findings: list[dsc.Finding] = field(default_factory=list)
  stats: dict = field(default_factory=dict)
  fingerprint: dict = field(default_factory=dict)
  motor: dsc.MotorCheck | None = None
  push: dsc.MotorCheck | None = None
  teeth: int | None = None     # which steering wheel teeth are on: 15 or 29 (TEETH_SETS)
  notes: list[str] = field(default_factory=list)


class CarSetup:
  def __init__(self, session: CanSession, prompter: Prompter, raw_config: dict):
    self.session = session
    self.p = prompter
    self.raw = raw_config
    self.cfg = parse_config(raw_config)
    self.frames: list[dsc.Frame] = []
    self.recorded_seconds = 0.0

  # ***** recording *****

  def _hold_motor_off(self, _t: float):
    return StepperMode.OFF, 0.0

  def record(self, text: str) -> list[dsc.Frame]:
    """Asks for something, then records the car's data for a few seconds."""
    self.p.step(text)
    self.session.drain()
    frames = self.session.run(RECORD_SECONDS, self._hold_motor_off)
    self.frames += frames
    self.recorded_seconds += RECORD_SECONDS
    if not frames:
      return []
    start = frames[0][0] + SETTLE_SECONDS
    return [f for f in frames if f[0] >= start]

  def twice(self, on_text: str, off_text: str) -> tuple[list, list]:
    """The action done twice, with a recording of each state. Returns (off windows, on windows)."""
    off, on = [], []
    for _ in range(2):
      on.append(self.record(on_text))
      off.append(self.record(off_text))
    return off, on

  # ***** the car's data *****

  def check_car_data(self) -> bool:
    self.session.drain()
    frames = self.session.run(1.0, self._hold_motor_off)
    if len(frames) < 50:
      self.p.say("No data from the car. Check the harness connection at the OBD port, and that the engine is running.")
      return False
    return True

  def parked_checks(self, manual: bool) -> ParkedResult:
    p = self.p
    res = ParkedResult()
    p.say("\nPart 1: the car's data. Each step asks for one thing; do it, then press Enter and hold it for 3 seconds.")

    rest = self.record("Engine running, shifter in P (manual: neutral with the parking brake on). Hands and feet off everything.")
    brake_off, brake_on = self.twice("Press the brake pedal and hold it down.", "Let go of the brake pedal.")
    gas_off, gas_on = self.twice("Press the gas pedal gently so the engine speeds up a little, and hold it there.",
                                 "Let go of the gas pedal.")
    left_off, left_on = self.twice("Switch the LEFT turn signal on.", "Switch the turn signal off.")
    right_off, right_on = self.twice("Switch the RIGHT turn signal on.", "Switch the turn signal off.")
    door_off, door_on = self.twice("Open the driver's door (stay seated).", "Close the driver's door.")

    gears: dict[str, list] = {}
    if manual:
      gears["N"] = self.record("Clutch down, shifter in neutral.")
      gears["R"] = self.record("Clutch down, put it in reverse.")
      self.record("Back to neutral, clutch up, parking brake on.")
    else:
      p.say("\nNow the shifter. Keep your foot on the brake the whole time.")
      for gear in ("P", "R", "N", "D"):
        gears[gear] = self.record(f"Foot on the brake, move the shifter to {gear}.")
      while len(gears) < 10:
        label = p.ask(MSG_MORE_GEARS).upper()
        if not label:
          break
        if label in gears:
          p.say(f"{label} is done already.")
          continue
        gears[label] = self.record(f"Keep it in {label}, foot on the brake.")
      self.record("Foot on the brake, shifter back to P.")

    stats = dsc.message_stats(self.frames, self.recorded_seconds)
    res.stats = stats
    res.fingerprint = dsc.fingerprint(self.frames)
    cfg = self.cfg
    res.findings = [
      dsc.check_standstill_speed(cfg, rest),
      dsc.resolve_flag(cfg, "BRAKE_PRESSED", brake_off, brake_on, stats),
      dsc.resolve_pedal(cfg, "GAS_PEDAL", gas_off, gas_on, stats),
      dsc.resolve_flag(cfg, "LEFT_BLINKER", left_off, left_on, stats, flashing=True),
      dsc.resolve_flag(cfg, "RIGHT_BLINKER", right_off, right_on, stats, flashing=True),
      dsc.resolve_flag(cfg, "DOOR_OPEN", door_off, door_on, stats),
      dsc.resolve_gear(cfg, gears, stats),
    ]
    missing = dsc.missing_messages(cfg, stats)
    if missing:
      res.notes.append("Messages from the default map your car doesn't send (fine when their signals were found elsewhere): "
                     + ", ".join(missing))
    return res

  # ***** the motor *****

  def _motor_angle_after(self, seconds: float = 0.5) -> float | None:
    self.session.drain()
    self.session.run(seconds, self._hold_motor_off)
    if not self.session.motor_present() or self.session.motor is None:
      return None
    return self.session.motor.angle

  def which_teeth(self) -> int | None:
    for _ in range(3):
      answer = self.p.ask(MSG_WHICH_TEETH).strip()
      if answer.isdigit() and int(answer) in TEETH_SETS:
        return int(answer)
    return None

  def motor_checks(self, res: ParkedResult) -> None:
    p, s = self.p, self.session
    a = self.cfg.actuator
    p.say("\nPart 2: the motor. Engine still running, shifter in P.")
    res.teeth = self.which_teeth()
    if res.teeth is None:
      res.motor = dsc.MotorCheck(False, "no answer to which steering wheel teeth are on (type 15 or 29)")
      return
    start = None
    for _ in range(2):
      p.step(MSG_LEVER_DOWN)
      start = self._motor_angle_after()
      if start is not None:
        break
      p.say(MSG_NO_MOTOR)
    if start is None:
      res.motor = dsc.MotorCheck(False, "the motor didn't answer")
      return

    status = s.motor
    assert status is not None
    if not status.control_status & StepperControlStatus.SENSORED:
      res.notes.append("The motor reports no position sensor reading; it may need its calibration (see the build guide).")
    res.notes.append(f"Motor temperature {status.temperature:.0f} C")

    p.step(MSG_TURN_LEFT)
    left = self._motor_angle_after()
    p.step(MSG_TURN_RIGHT)
    right = self._motor_angle_after()
    if left is None or right is None:
      res.motor = dsc.MotorCheck(False, "the motor stopped answering while the wheel turned")
      return
    res.motor = dsc.motor_direction_from_turn(start, left, right, a.angle_scale, TEETH_SETS[res.teeth])
    if not res.motor.ok:
      # a turn that matches the other teeth means the answer about which teeth are on was wrong, not the gearing
      for other, arc in TEETH_SETS.items():
        if other != res.teeth and dsc.motor_direction_from_turn(start, left, right, a.angle_scale, arc, arc_tolerance=0.15).ok:
          detail = " ".join((f"the motor turned with the steering wheel as far as the {other} degree teeth reach,",
                             f"not the {res.teeth}: check which teeth are on"))
          res.motor = dataclasses.replace(res.motor, detail=detail)
      return

    # The direction so far rests on which way the wheel was turned first. The person's own eyes check it: the motor
    # is told to turn the wheel left, and they say which way it went.
    direction = res.motor.direction
    for attempt in range(2):
      res.push = self._push_and_measure(direction)
      if not res.push.ok:
        return
      seen_left = p.yes_no(MSG_DID_IT_TURN_LEFT)
      if seen_left is None:
        res.push = dsc.MotorCheck(False, "no clear answer to which way the wheel turned", direction)
        return
      if seen_left:
        res.push = dataclasses.replace(res.push, detail=res.push.detail + ", and you saw it go left")
        if direction != res.motor.direction:
          res.motor = dataclasses.replace(res.motor, direction=direction,
                                          detail=res.motor.detail + "; direction corrected after you saw the wheel go right")
        return
      if attempt == 0:
        p.say(MSG_TRY_OTHER_WAY)
        direction = -direction
    res.push = dsc.MotorCheck(False, MSG_NEVER_LEFT, direction, wrong_way=True)

  def _push_and_measure(self, direction: int) -> dsc.MotorCheck:
    """The motor turns the wheel left (as direction says left is): the result from its own angle reading."""
    p = self.p
    check = dsc.MotorCheck(False, "not tried", direction)
    for attempt in range(2):
      p.step(MSG_PUSH)
      before = self._motor_angle_after(0.3)
      if before is None:
        return dsc.MotorCheck(False, "the motor stopped answering", direction)
      angles = self._push(direction, before)
      after = max(angles, key=lambda x: abs(x - before)) if angles else before
      check = dsc.motor_push_agrees(direction, before, after)
      if check.ok or check.wrong_way:
        return check
      if attempt == 0:
        p.say("The wheel barely moved. Make sure the engine is running (power steering) and nothing holds the wheel; trying once more.")
    return check

  def _push(self, direction: int, start: float) -> list[float]:
    """Turns the wheel left with the motor: ramp up, hold, ramp down, off. It lets go as soon as the wheel has turned
    PUSH_STOP_DEG, so the motor gear stays on the teeth. Returns the motor angles seen."""
    angles = []
    scale = self.cfg.actuator.angle_scale
    stopped = False

    def command(t: float):
      nonlocal stopped
      if self.session.motor is not None:
        angles.append(self.session.motor.angle)
        stopped = stopped or abs(self.session.motor.angle - start) * scale >= PUSH_STOP_DEG
      if stopped or t < 0.2 or t > 2.0:
        return StepperMode.OFF, 0.0
      ramp = min((t - 0.2) / 0.5, 1.0, (2.0 - t) / 0.3)
      return StepperMode.TORQUE_CONTROL, direction * PUSH_TORQUE_FW_NM * max(ramp, 0.0)

    self.session.drain()
    self.session.run(2.3, command)
    return angles


# ***** results *****

def build_config(raw: dict, res: ParkedResult) -> tuple[dict, bool, list[str]]:
  """The config to save, whether the parked part passed, and plain-word problems."""
  problems = []
  by_name = {f.signal: f for f in res.findings}
  if not by_name["BRAKE_PRESSED"].ok:
    problems.append(f"{dsc.plain_name('BRAKE_PRESSED')}: {by_name['BRAKE_PRESSED'].detail}")
  new_raw = dsc.apply_findings(raw, res.findings)
  res.notes += dsc.update_message_rates(new_raw, res.stats)
  motor_ok = res.motor is not None and res.motor.ok and res.push is not None and res.push.ok
  if res.motor is None or not res.motor.ok:
    problems.append(f"motor: {res.motor.detail if res.motor else 'not checked'}")
  elif res.push is None or not res.push.ok:
    problems.append(f"motor push: {res.push.detail if res.push else 'not checked'}")
  if res.motor is not None and res.motor.ok:
    new_raw["actuator"]["direction"] = res.motor.direction
    new_raw["actuator"]["tracked_arc_deg"] = TEETH_SETS[res.teeth]
  new_raw.setdefault("setup", {})
  # A new parked check can change the motor's direction or the signal map, so the drive check that confirmed the old
  # ones no longer counts: lane keeping waits for both again.
  new_raw["setup"].pop("drive", None)
  passed = not problems and motor_ok
  if passed:
    new_raw["setup"]["parked"] = datetime.datetime.now().isoformat(timespec="seconds")
  else:
    new_raw["setup"].pop("parked", None)
  parse_config(new_raw)
  return new_raw, passed, problems


def report(res: ParkedResult, problems: list[str], passed: bool) -> str:
  lines = [f"hondastepper car setup, parked part, {datetime.datetime.now().isoformat(timespec='seconds')}", ""]
  for f in res.findings:
    lines.append(f"  {'OK  ' if f.ok else 'FAIL'} {dsc.plain_name(f.signal)}: {f.detail}")
  if res.teeth:
    lines.append(f"  steering wheel teeth: the {'short' if res.teeth == min(TEETH_SETS) else 'long'} ones ({res.teeth} degrees each way)")
  if res.motor:
    lines.append(f"  {'OK  ' if res.motor.ok else 'FAIL'} motor direction: {res.motor.detail}")
  if res.push:
    lines.append(f"  {'OK  ' if res.push.ok else 'FAIL'} motor push: {res.push.detail}")
  lines += ["", *[f"  note: {n}" for n in res.notes]]
  if problems:
    lines += ["", "Problems:", *[f"  {pr}" for pr in problems]]
  lines += ["", "For the record, your car's messages (address: length): " + ", ".join(f"{a:#x}:{n}" for a, n in res.fingerprint.items())]
  lines += ["", "RESULT: " + ("PASSED" if passed else "NOT PASSED")]
  return "\n".join(lines)


def save_report(text: str, directory: str) -> str:
  os.makedirs(directory, exist_ok=True)
  path = os.path.join(directory, f"setup_report_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt")
  with open(path, "w") as f:
    f.write(text + "\n")
  return path


def run(session: CanSession, prompter: Prompter, manual: bool, save: Callable[[dict], str] = save_device_config,
        report_dir: str | None = None) -> bool:
  raw = load_raw_config()
  setup = CarSetup(session, prompter, raw)
  if not setup.check_car_data():
    return False
  res = setup.parked_checks(manual)
  setup.motor_checks(res)
  new_raw, passed, problems = build_config(raw, res)
  text = report(res, problems, passed)
  prompter.say("\n" + text)
  if report_dir:
    prompter.say(f"\nThis report is saved in {save_report(text, report_dir)}")
  required = all(f.ok for f in res.findings if f.signal == "BRAKE_PRESSED")
  if required:
    path = save(new_raw)
    prompter.say(f"Settings saved to {path}.")
  else:
    prompter.say("Nothing was saved: the brake pedal must be found.")
  if passed:
    prompter.say(MSG_PART1_PASSED)
  else:
    prompter.say("Part 1 did not pass, so lane keeping stays off. Fix what the report says and run this again.")
  return passed


def main() -> int:
  from panda import Panda
  from openpilot.sunnypilot.tools.hondastepper.device import PowerWatchdog, reboot, stop_openpilot

  p = Prompter()
  p.say(INTRO)
  answer = p.ask("Is the car an automatic or a manual? Type a or m and press Enter:").lower()
  manual = answer.startswith("m")
  p.step("Car parked, engine running, comma device on its mount and plugged in. openpilot will stop and the screen will go dark until the end.")
  if not stop_openpilot():
    p.say("openpilot didn't stop; restart the comma device and try again.")
    return 1
  watchdog = PowerWatchdog().start()
  session = CanSession(Panda())
  passed = False
  try:
    passed = run(session, p, manual, report_dir=os.path.dirname(device_config_path()))
  finally:
    session.close()
    watchdog.stop()
  p.ask("Press Enter to restart the comma device (it rebuilds the software first; that can take several minutes).")
  reboot()
  return 0 if passed else 2


if __name__ == "__main__":
  sys.exit(main())
