"""
The hondastepper setup tools run end to end against a simulated car and motor: the simulated driver does what each
prompt asks, the tool records through a fake panda, and the saved config is checked.
"""
import copy
import json
import os
import re
import tempfile
import unittest
from unittest import mock

from opendbc.car.hondastepper import discovery as dsc
from opendbc.car.hondastepper.config import CONFIG_PATH, TEETH_SETS, parse_config
from opendbc.car.hondastepper.tests.sim import MESSAGES, MOVED_GEARS, MOVED_LAYOUT, SimCar, SimMotor, turning_drive
from openpilot.sunnypilot.tools.hondastepper import check_drive, setup_car
from openpilot.sunnypilot.tools.hondastepper.device import CanSession

DEFAULT_RAW = json.load(open(CONFIG_PATH))


class SimClock:
  def __init__(self):
    self.t = 0.0

  def __call__(self) -> float:
    return self.t

  def sleep(self, dt: float):
    self.t += dt


class FakePanda:
  """The panda as the tools see it, wired to the simulated car (bus 0) and motor (bus 1)."""

  def __init__(self, car: SimCar, motor: SimMotor, clock: SimClock):
    self.car, self.motor, self.clock = car, motor, clock
    self.safety_modes = []
    self.closed = False

  def set_heartbeat_disabled(self):
    pass

  def set_power_save(self, _enabled):
    pass

  def set_safety_mode(self, mode, param=0):
    self.safety_modes.append((mode, param))

  def can_recv(self):
    t = self.clock()
    out = [(a, d, 0) for _, a, d in self.car.advance(t)]
    out += [(a, d, 1) for _, a, d in self.motor.advance(t)]
    return out

  def can_send(self, addr, dat, bus):
    if bus == 1 and addr == 0x22E:
      self.motor.command(self.clock(), bytes(dat))

  def close(self):
    self.closed = True


class SimDriver:
  """Answers the setup tool's prompts by changing the simulated car and motor."""

  def __init__(self, car: SimCar, motor: SimMotor, extra_gears=(), motor_works=True, turns_right_first=False, answer=None,
               teeth="29"):
    self.car, self.motor = car, motor
    self.teeth = teeth                           # answer to "which steering wheel teeth are on"
    self.extra_gears = list(extra_gears)
    self.motor_works = motor_works
    self.turns_right_first = turns_right_first   # mixes up left and right in the turn test
    self.answer = answer                         # fixed answer to "did it turn left?"; None: says what it saw
    self.push_start = 0.0
    self.prompts: list[str] = []

  def _straight(self):
    self.motor.turn_wheel(self.motor.teeth_center_deg)
    self.push_start = self.motor.wheel_deg

  def __call__(self, prompt: str) -> str:
    self.prompts.append(prompt)
    c, m = self.car, self.motor
    if "Which steering wheel teeth" in prompt:
      return self.teeth
    if "Did the steering wheel just turn LEFT" in prompt:
      if self.answer is not None:
        return self.answer
      return "y" if m.wheel_deg > self.push_start + 1.0 else "n"
    first = -45 if self.turns_right_first else 45
    rules = [
      ("Hands and feet off", lambda: c.state.update(BRAKE_PRESSED=0, GAS_PEDAL=0)),
      ("Press the brake pedal", lambda: c.state.update(BRAKE_PRESSED=1)),
      ("Let go of the brake", lambda: c.state.update(BRAKE_PRESSED=0)),
      ("Press the gas pedal", lambda: c.state.update(GAS_PEDAL=70)),
      ("Let go of the gas", lambda: c.state.update(GAS_PEDAL=0)),
      ("LEFT turn signal on", lambda: c.state.update(LEFT_BLINKER=1)),
      ("RIGHT turn signal on", lambda: c.state.update(RIGHT_BLINKER=1)),
      ("turn signal off", lambda: c.state.update(LEFT_BLINKER=0, RIGHT_BLINKER=0)),
      ("Open the driver's door", lambda: c.state.update(DOOR_OPEN=1)),
      ("Close the driver's door", lambda: c.state.update(DOOR_OPEN=0)),
      ("Pull the lift lever down", lambda: setattr(m, "powered", self.motor_works)),
      ("turn the steering wheel LEFT until", lambda: m.turn_wheel(m.teeth_center_deg + first)),
      ("turn the wheel RIGHT, past the middle", lambda: m.turn_wheel(m.teeth_center_deg - first)),
      ("back to straight", self._straight),
    ]
    for key, action in rules:
      if key in prompt:
        action()
        return ""
    if "move the shifter to" in prompt:
      c.state["GEAR"] = prompt.split("move the shifter to ")[1][0]
    elif "shifter back to P" in prompt:
      c.state["GEAR"] = "P"
    elif "If the shifter goes further than D" in prompt:
      if self.extra_gears:
        gear = self.extra_gears.pop(0)
        c.state["GEAR"] = gear
        return gear.lower()
    elif "Clutch down, shifter in neutral" in prompt or "Back to neutral" in prompt:
      c.state["GEAR"] = "N"
    elif "put it in reverse" in prompt:
      c.state["GEAR"] = "R"
    return ""


def run_setup(car: SimCar, motor: SimMotor, driver: SimDriver | None = None, manual: bool = False, raw: dict | None = None):
  clock = SimClock()
  panda = FakePanda(car, motor, clock)
  driver = driver or SimDriver(car, motor)
  printed: list[str] = []
  saved: list[dict] = []
  session = CanSession(panda, clock=clock, sleep=clock.sleep)
  prompter = setup_car.Prompter(input_fn=driver, print_fn=printed.append)
  with mock.patch.object(setup_car, "load_raw_config", lambda: copy.deepcopy(raw or DEFAULT_RAW)):
    passed = setup_car.run(session, prompter, manual, save=lambda r: saved.append(r) or "/data/hondastepper/config.json")
  session.close()
  return passed, (saved[-1] if saved else None), "\n".join(printed), driver


class TestSetupCar(unittest.TestCase):
  def test_default_car(self):
    car, motor = SimCar(), SimMotor(true_direction=1)
    motor.powered = False  # the lift lever starts up
    passed, raw, text, driver = run_setup(car, motor)
    self.assertTrue(passed, text)
    self.assertIn("RESULT: PASSED", text)
    cfg = parse_config(raw)
    self.assertEqual(cfg.actuator.direction, 1)
    self.assertTrue(cfg.setup.get("parked"))
    self.assertFalse(cfg.verified)  # the drive check is still to do
    self.assertEqual(raw["fcan"]["signals"], DEFAULT_RAW["fcan"]["signals"])
    # the motor turned the wheel left in the push test
    self.assertGreater(motor.wheel_deg, 2.0)
    self.assertIn("you saw it go left", text)
    # nothing it asked or printed mentions jargon the driver wouldn't know, or old names for the parts
    asked = " ".join(driver.prompts) + text
    for word in ("F-CAN", "pinion", "rim", "MADS", "panda", "gear ring", "gear lever", "arm", "MAIN"):
      self.assertIsNone(re.search(rf"\b{re.escape(word)}\b", asked, re.IGNORECASE), word)

  def test_short_teeth(self):
    car, motor = SimCar(), SimMotor(true_direction=1, arc_deg=TEETH_SETS[15])
    passed, raw, text, _ = run_setup(car, motor, SimDriver(car, motor, teeth="15"))
    self.assertTrue(passed, text)
    self.assertEqual(raw["actuator"]["tracked_arc_deg"], TEETH_SETS[15])
    self.assertIn("the short ones (15 degrees each way)", text)

  def test_wrong_teeth_answer(self):
    car, motor = SimCar(), SimMotor(true_direction=1, arc_deg=TEETH_SETS[15])
    passed, raw, text, _ = run_setup(car, motor, SimDriver(car, motor, teeth="29"))
    self.assertFalse(passed)
    self.assertIn("as far as the 15 degree teeth reach, not the 29: check which teeth are on", text)
    self.assertNotIn("parked", raw["setup"])

  def test_no_answer_about_the_teeth(self):
    car, motor = SimCar(), SimMotor()
    passed, _, text, driver = run_setup(car, motor, SimDriver(car, motor, teeth="?"))
    self.assertFalse(passed)
    self.assertIn("no answer to which steering wheel teeth are on", text)
    self.assertEqual(sum("Which steering wheel teeth" in p for p in driver.prompts), 3)

  def test_reversed_motor(self):
    car, motor = SimCar(), SimMotor(true_direction=-1)
    passed, raw, text, _ = run_setup(car, motor)
    self.assertTrue(passed, text)
    self.assertEqual(raw["actuator"]["direction"], -1)
    self.assertGreater(motor.wheel_deg, 2.0)  # with the flipped sign, "left" still turned the wheel left

  def test_wheel_turned_right_first(self):
    # the turn test alone would save the motor's direction backwards; the push the driver watches corrects it
    car, motor = SimCar(), SimMotor(true_direction=1)
    driver = SimDriver(car, motor, turns_right_first=True)
    passed, raw, text, _ = run_setup(car, motor, driver)
    self.assertTrue(passed, text)
    self.assertEqual(raw["actuator"]["direction"], 1)
    self.assertIn("direction corrected", text)
    self.assertGreater(motor.wheel_deg, motor.teeth_center_deg + 2.0)   # the last push went left

  def test_rerun_needs_the_drive_check_again(self):
    # part 1 run again on a car that had passed both checks: the drive check has to confirm the new result
    car, motor = SimCar(), SimMotor()
    done = {**copy.deepcopy(DEFAULT_RAW), "setup": {"parked": "2026-10-07T10:00:00", "drive": "2026-10-07T10:30:00"}}
    passed, raw, text, _ = run_setup(car, motor, raw=done)
    self.assertTrue(passed, text)
    self.assertTrue(raw["setup"].get("parked"))
    self.assertNotIn("drive", raw["setup"])
    self.assertFalse(parse_config(raw).verified)

  def test_wheel_never_seen_going_left(self):
    car, motor = SimCar(), SimMotor()
    passed, raw, text, _ = run_setup(car, motor, SimDriver(car, motor, answer="n"))
    self.assertFalse(passed)
    self.assertIn("couldn't be settled", text)
    self.assertNotIn("parked", raw["setup"])

  def test_push_stops_after_a_few_degrees(self):
    car, motor = SimCar(), SimMotor()
    run_setup(car, motor)
    self.assertLess(motor.wheel_deg - motor.teeth_center_deg, setup_car.PUSH_STOP_DEG + 2.0)
    self.assertTrue(motor.in_teeth(motor.wheel_deg))

  def test_other_layout_and_extra_gears(self):
    gears = {**MOVED_GEARS, "D3": 2, "2": 3}
    car = SimCar(layout=MOVED_LAYOUT, gears=gears, messages={a: v for a, v in MESSAGES.items() if a not in (0x158, 0x1A3)})
    motor = SimMotor()
    driver = SimDriver(car, motor, extra_gears=["D3", "2"])
    passed, raw, text, _ = run_setup(car, motor, driver)
    # the speed message isn't there: the drive check finds it, so part 1 can still pass
    cfg = parse_config(raw)
    self.assertEqual(cfg.message_of("DOOR_OPEN").addr, 0x405)
    self.assertEqual(cfg.message_of("GEAR").addr, 0x191)
    self.assertEqual(cfg.signals["GEAR"].values, {0: "P", 1: "D", 2: "L", 3: "L", 6: "N", 7: "R"})
    self.assertTrue(passed, text)

  def test_manual_gearbox(self):
    layout = dict(SimCar().layout)
    layout["GEAR"] = (0x1A6, 18, 1)
    car = SimCar(layout=layout, gears={"N": 0, "R": 1, "P": 0, "D": 0})
    car.state["GEAR"] = "N"
    motor = SimMotor()
    passed, raw, text, _ = run_setup(car, motor, manual=True)
    self.assertTrue(passed, text)
    self.assertEqual(raw["fcan"]["signals"]["GEAR"]["values"], {"0": "D", "1": "R"})

  def test_motor_missing(self):
    car, motor = SimCar(), SimMotor()
    motor.powered = False
    passed, raw, text, _ = run_setup(car, motor, SimDriver(car, motor, motor_works=False))
    self.assertFalse(passed)
    self.assertIn("motor", text)
    self.assertNotIn("parked", raw["setup"])  # the car's data was saved, but part 1 isn't marked passed

  def test_brake_not_found(self):
    layout = {k: v for k, v in SimCar().layout.items() if k != "BRAKE_PRESSED"}
    car, motor = SimCar(layout=layout), SimMotor()
    passed, raw, text, _ = run_setup(car, motor)
    self.assertFalse(passed)
    self.assertIsNone(raw)
    self.assertIn("Nothing was saved", text)

  def test_no_car_data(self):
    car, motor = SimCar(messages={0x7FF: (8, 1)}), SimMotor()
    passed, raw, text, _ = run_setup(car, motor)
    self.assertFalse(passed)
    self.assertIsNone(raw)
    self.assertIn("No data from the car", text)


PARKED_RAW = {**copy.deepcopy(DEFAULT_RAW), "setup": {"parked": "2026-10-07T10:00:00"}}


class TestCheckDrive(unittest.TestCase):
  def _drive(self, car: SimCar, true_direction: int = 1, with_motor: bool = True) -> check_drive.Drive:
    import math
    frames, gps = [], []
    for i in range(400):
      v = 8 + 10 * (0.5 + 0.5 * math.sin(i / 25))
      chunk = car.run(0.5, VEHICLE_SPEED=v * 3.6)
      frames += chunk
      gps.append((chunk[0][0], v))
    motor, headings = turning_drive(200.0, true_direction) if with_motor else ([], [])
    return check_drive.Drive(frames, motor, gps, headings, frames[-1][0] - frames[0][0])

  def test_speed_found_and_saved(self):
    car = SimCar(layout=MOVED_LAYOUT, gears=MOVED_GEARS, speed_factor_kph=0.005, messages={a: v for a, v in MESSAGES.items() if a != 0x158})
    new_raw, fit, motor = check_drive.check(copy.deepcopy(PARKED_RAW), self._drive(car))
    self.assertTrue(fit.ok, fit.detail)
    self.assertTrue(motor.ok, motor.detail)
    cfg = parse_config(new_raw)
    self.assertTrue(cfg.verified)
    self.assertEqual(cfg.message_of("VEHICLE_SPEED").addr, 0x309)
    self.assertEqual(cfg.signals["VEHICLE_SPEED"].factor, 0.005)

  def test_wrong_motor_direction_is_caught(self):
    raw = copy.deepcopy(PARKED_RAW)
    raw["actuator"]["direction"] = -1   # part 1 saved it backwards
    new_raw, fit, motor = check_drive.check(raw, self._drive(SimCar(), true_direction=1))
    self.assertTrue(fit.ok, fit.detail)
    self.assertIsNone(new_raw)
    self.assertTrue(motor.wrong_way)

  def test_needs_the_lift_lever_down(self):
    new_raw, _, motor = check_drive.check(copy.deepcopy(PARKED_RAW), self._drive(SimCar(), with_motor=False))
    self.assertIsNone(new_raw)
    self.assertIn("lift lever down", motor.detail)

  def test_too_little_driving(self):
    car = SimCar()
    frames = car.run(10.0, VEHICLE_SPEED=60.0)
    drive = check_drive.Drive(frames, [], [(frames[0][0], 16.7)] * 5, [], 10.0)
    new_raw, fit, motor = check_drive.check(copy.deepcopy(PARKED_RAW), drive)
    self.assertIsNone(new_raw)
    self.assertFalse(fit.ok)
    self.assertIsNone(motor)

  def test_part_1_first(self):
    printed: list[str] = []
    with mock.patch.object(check_drive, "load_raw_config", lambda: copy.deepcopy(DEFAULT_RAW)):
      self.assertFalse(check_drive.run(printed.append, "/nonexistent", save=lambda r: "x"))
    self.assertIn("Run part 1 first", printed[-1])

  def test_reads_recorded_segments(self):
    from openpilot.cereal import log
    import zstandard

    car = SimCar()
    drive = self._drive(car)
    with tempfile.TemporaryDirectory() as root:
      # two one-minute segments as loggerd writes them, the second still being written
      for seg, (lo, hi) in enumerate(((0, 120.0), (120.0, 200.0))):
        events = []
        for t, addr, dat in drive.frames:
          if lo <= t < hi:
            evt = log.Event.new_message(logMonoTime=int(t * 1e9))
            can = evt.init("can", 1)
            can[0].address, can[0].dat, can[0].src = addr, dat, 0
            events.append(evt)
        for t, angle in drive.motor:
          if lo <= t < hi:
            evt = log.Event.new_message(logMonoTime=int(t * 1e9))
            can = evt.init("can", 1)
            data = bytearray(8)
            data[5:7] = (round(angle / 0.125) & 0xFFFF).to_bytes(2, "little")
            can[0].address, can[0].dat, can[0].src = 0x22F, bytes(data), 1
            events.append(evt)
        # GPS fixes at 10 Hz: the course from the drive, the speed of the half second the car was in
        speeds = [v for _, v in drive.gps]
        for t, b, _ in drive.headings:
          if lo <= t < hi:
            evt = log.Event.new_message(logMonoTime=int(t * 1e9))
            fix = evt.init("gpsLocation")
            fix.speed, fix.hasFix, fix.speedAccuracy = speeds[min(int(t / 0.5), len(speeds) - 1)], True, 0.3
            fix.bearingDeg, fix.bearingAccuracyDeg = b, 1.0
            events.append(evt)
        events.sort(key=lambda e: e.logMonoTime)
        path = os.path.join(root, f"0000002a--abcdef1234--{seg}")
        os.makedirs(path)
        with open(os.path.join(path, "rlog.zst"), "wb") as f:
          f.write(zstandard.ZstdCompressor().compress(b"".join(e.to_bytes() for e in events)))
      open(os.path.join(root, "0000002a--abcdef1234--1", "rlog.lock"), "w").close()

      segments = check_drive.recent_segments(root)
      self.assertEqual([os.path.basename(s) for s in segments], ["0000002a--abcdef1234--0"])
      seg = check_drive.read_segment(segments[0])
      self.assertEqual(len(seg.frames), len([f for f in drive.frames if f[0] < 120.0]))
      self.assertEqual(len(seg.motor), len([m for m in drive.motor if m[0] < 120.0]))
      self.assertEqual(len(seg.headings), len([h for h in drive.headings if h[0] < 120.0]))
      fit = dsc.check_speed(parse_config(DEFAULT_RAW), seg.frames, seg.gps, dsc.message_stats(seg.frames, 120.0))
      self.assertTrue(fit.ok, fit.detail)

      printed: list[str] = []
      saved: list[dict] = []
      with mock.patch.object(check_drive, "load_raw_config", lambda: copy.deepcopy(PARKED_RAW)):
        self.assertTrue(check_drive.run(printed.append, root, save=lambda r: saved.append(r) or "x"), "\n".join(printed))
      self.assertTrue(saved[0]["setup"]["drive"])
      self.assertIn("Both parts of the setup have passed", printed[-1])


if __name__ == "__main__":
  unittest.main()
