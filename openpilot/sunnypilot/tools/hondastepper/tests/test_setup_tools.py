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
from opendbc.car.hondastepper.config import CONFIG_PATH, NO_ROLLER_ARCS, ROLL_PAST_TEETH_DEG, TEETH_SETS, parse_config
from opendbc.car.hondastepper.tests.sim import MESSAGES, MOVED_GEARS, MOVED_LAYOUT, SimCar, SimMotor, turning_drive
from openpilot.sunnypilot.tools.hondastepper import check_drive, setup_car
from openpilot.sunnypilot.tools.hondastepper.device import CanSession

STANDALONE_RAW = json.load(open(CONFIG_PATH))   # the checked-in default: not connected to the car
# most tests here run connected to the car's network (car_network), the setup that reads the car's data
DEFAULT_RAW = {**copy.deepcopy(STANDALONE_RAW), "car_network": True}


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
               teeth="29", grip_holds=True):
    self.car, self.motor = car, motor
    self.grip_holds = grip_holds                 # holds the wheel still when the grip test asks
    self.teeth = teeth                           # answer to "which steering wheel teeth are on"
    self.extra_gears = list(extra_gears)
    self.motor_works = motor_works
    self.turns_right_first = turns_right_first   # mixes up left and right in the turn test
    self.answer = answer                         # fixed answer to "did it turn left?"; None: says what it saw
    self.push_start = 0.0
    self.prompts: list[str] = []

  def _straight(self):
    self.motor.plan = None          # a turn still going on stops: the driver turns back to straight and lets go
    self.motor.turn_wheel(self.motor.teeth_center_deg)
    self.push_start = self.motor.wheel_deg

  def __call__(self, prompt: str) -> str:
    self.prompts.append(prompt)
    c, m = self.car, self.motor
    # the wheel is held only for the grip test, until the next thing asked
    m.held = "Grip test" in prompt and self.grip_holds
    if m.held:
      return ""
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
      ("Switch the motor on with its gear", lambda: setattr(m, "powered", self.motor_works)),
      ("turn the steering wheel LEFT", lambda: m.plan_turn(m.teeth_center_deg + first, 15.0)),   # over the next seconds
      ("the same to the RIGHT", lambda: m.plan_turn(m.teeth_center_deg - first, 15.0)),
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


class NoCarPanda(FakePanda):
  """Stand-alone: the panda hears only the motor; the car isn't connected."""

  def can_recv(self):
    return [(a, d, 1) for _, a, d in self.motor.advance(self.clock())]


def run_setup(car: SimCar, motor: SimMotor, driver: SimDriver | None = None, manual: bool = False, raw: dict | None = None,
              panda_cls=FakePanda):
  clock = SimClock()
  panda = panda_cls(car, motor, clock)
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

  def test_no_steering_angle_on_the_network(self):
    car, motor = SimCar(), SimMotor()
    passed, raw, text, driver = run_setup(car, motor)
    self.assertTrue(passed, text)
    self.assertIn("steering angle: not on the car's network (the motor's own angle is used; nothing to do)", text)
    self.assertNotIn("FAIL steering angle", text)
    self.assertNotIn("STEER_ANGLE", raw["fcan"]["signals"])
    # the turns were recorded while the wheel turned: the driver was asked to start, then turn
    self.assertEqual(sum("Press Enter, then turn" in p for p in driver.prompts), 2)

  def test_steering_angle_found_and_scaled(self):
    # a car that broadcasts its steering wheel angle like a newer Honda: 16 bits, big-endian, signed, -0.1 degrees a step
    for factor, arc in ((-0.1, TEETH_SETS[29]), (0.0625, TEETH_SETS[15])):
      motor = SimMotor(true_direction=-1, arc_deg=arc)
      layout = {**SimCar().layout, "STEER_ANGLE": (0x1C2, 7, 16)}
      car = SimCar(layout=layout, messages={**MESSAGES, 0x1C2: (8, 100)}, wheel_deg_fn=lambda m=motor: m.wheel_deg, angle_factor_deg=factor)
      passed, raw, text, _ = run_setup(car, motor, SimDriver(car, motor, teeth="29" if arc == TEETH_SETS[29] else "15"))
      self.assertTrue(passed, text)
      found = f"steering angle: follows the motor's angle while the gear is on the teeth; found (message 0x1c2, byte 0, {abs(factor):g} degrees per step)"
      self.assertIn(found, text)
      sig = raw["fcan"]["signals"]["STEER_ANGLE"]
      self.assertEqual((sig["message"], sig["start_bit"], sig["size"], sig["byte_order"], sig["signed"]), ("MSG_1C2", 7, 16, "big", True))
      self.assertEqual(sig["factor"], factor)
      self.assertAlmostEqual(sig["offset"], 0.0, places=3)
      cfg = parse_config(raw)
      self.assertEqual(cfg.message_of("STEER_ANGLE").freq, 100)
      # the saved signal reads the wheel's angle, left positive, whichever way the motor counts
      frame = next(d for _, a, d in car.run(0.05) if a == 0x1C2)
      self.assertAlmostEqual(dsc.read_signal(frame, cfg.signals["STEER_ANGLE"]), motor.wheel_deg, delta=abs(factor))

  def test_steering_angle_too_slow_is_not_used(self):
    motor = SimMotor()
    layout = {**SimCar().layout, "STEER_ANGLE": (0x1C2, 7, 16)}
    car = SimCar(layout=layout, messages={**MESSAGES, 0x1C2: (8, 20)}, wheel_deg_fn=lambda: motor.wheel_deg)
    passed, raw, text, _ = run_setup(car, motor)
    self.assertTrue(passed, text)
    self.assertIn("found only in a message that comes less than 50 times a second", text)
    self.assertNotIn("STEER_ANGLE", raw["fcan"]["signals"])

  def test_grip_test(self):
    car, motor = SimCar(), SimMotor()
    passed, raw, text, driver = run_setup(car, motor)
    self.assertTrue(passed, text)
    self.assertEqual(sum("Grip test" in p for p in driver.prompts), 1)
    # it pushed with the most the board gives: 58 firmware units, 5.4 Nm at the steering wheel with the 45 Ncm motor
    a = parse_config(raw).actuator
    self.assertEqual(setup_car.grip_torque_fw(a), 7.25)
    self.assertIn("nothing slipped with 5.4 Nm at the steering wheel each way", text)
    self.assertEqual(motor.slips, 0)

  def test_grip_test_slipping(self):
    car, motor = SimCar(), SimMotor()
    motor.slip_fw_nm = 5.0   # a weak spring or dry teeth: the gear jumps a tooth under the hardest push
    passed, raw, text, _ = run_setup(car, motor)
    self.assertFalse(passed)
    self.assertIn("FAIL grip test: the motor gear slipped over the steering wheel teeth", text)
    self.assertNotIn("parked", raw["setup"])
    # the push stopped at the first slip in each direction
    self.assertEqual(motor.slips, 2)

  def test_grip_test_wheel_not_held(self):
    car, motor = SimCar(), SimMotor()
    passed, raw, text, driver = run_setup(car, motor, SimDriver(car, motor, grip_holds=False))
    self.assertFalse(passed)
    self.assertEqual(sum("Grip test" in p for p in driver.prompts), 2)   # asked once more
    self.assertIn("FAIL grip test: the steering wheel moved during the grip test both times", text)
    self.assertNotIn("parked", raw["setup"])
    # each push stopped after a few degrees, so the motor gear stayed on the teeth
    self.assertTrue(motor.in_teeth(motor.wheel_deg))

  def test_short_teeth(self):
    car, motor = SimCar(), SimMotor(true_direction=1, arc_deg=TEETH_SETS[15])
    passed, raw, text, _ = run_setup(car, motor, SimDriver(car, motor, teeth="15"))
    self.assertTrue(passed, text)
    self.assertEqual(raw["actuator"]["tracked_arc_deg"], TEETH_SETS[15])
    self.assertIn("the short ones (15 degrees each way)", text)

  def test_short_teeth_with_and_without_a_roller(self):
    # with a roller (every mount but the side-slide one) the motor follows the wheel along the rolling band too
    car, motor = SimCar(), SimMotor(true_direction=1, arc_deg=TEETH_SETS[15])
    passed, raw, text, _ = run_setup(car, motor, SimDriver(car, motor, teeth="15"))
    self.assertTrue(passed, text)
    self.assertEqual(raw["actuator"]["roll_past_deg"], ROLL_PAST_TEETH_DEG)
    self.assertNotIn("without a roller", text)
    # the side-slide mount's gear has none: the motor follows the teeth alone, and the full push reaches their end
    car, motor = SimCar(), SimMotor(true_direction=1, arc_deg=NO_ROLLER_ARCS[15])
    passed, raw, text, _ = run_setup(car, motor, SimDriver(car, motor, teeth="15"))
    self.assertTrue(passed, text)
    self.assertEqual(raw["actuator"]["tracked_arc_deg"], NO_ROLLER_ARCS[15])
    self.assertEqual(raw["actuator"]["roll_past_deg"], 0.0)
    self.assertAlmostEqual(parse_config(raw).actuator.full_push_reach_deg, NO_ROLLER_ARCS[15] / 2)
    self.assertIn("the short ones (15 degrees each way), the motor gear without a roller", text)

  def test_side_slide_teeth_sets(self):
    # the side-slide mount's other two sets: straight roads (10 teeth, answer 11) and winding roads (18 teeth, answer 20),
    # both without a roller, on the face gear's ratio
    for answer, name in ((11, "straight-roads ones"), (20, "winding-roads ones")):
      car, motor = SimCar(), SimMotor(true_direction=1, arc_deg=NO_ROLLER_ARCS[answer])
      passed, raw, text, _ = run_setup(car, motor, SimDriver(car, motor, teeth=str(answer)))
      self.assertTrue(passed, text)
      self.assertEqual(raw["actuator"]["tracked_arc_deg"], NO_ROLLER_ARCS[answer])
      self.assertEqual(raw["actuator"]["roll_past_deg"], 0.0)
      self.assertAlmostEqual(raw["actuator"]["mechanical_ratio"], 166 / 16)
      self.assertAlmostEqual(parse_config(raw).actuator.full_push_reach_deg, NO_ROLLER_ARCS[answer] / 2)
      self.assertIn(f"the {name} ({answer} degrees each way), the motor gear without a roller", text)
    # the straight-roads teeth on the car with the highway teeth answered: the turn gives it away
    car, motor = SimCar(), SimMotor(true_direction=1, arc_deg=NO_ROLLER_ARCS[11])
    passed, raw, text, _ = run_setup(car, motor, SimDriver(car, motor, teeth="15"))
    self.assertFalse(passed)
    self.assertIn("as far as the 11 degree teeth reach, not the 15: check which teeth are on", text)

  def test_back_teeth(self):
    car, motor = SimCar(), SimMotor(true_direction=1, arc_deg=TEETH_SETS[45])
    passed, raw, text, _ = run_setup(car, motor, SimDriver(car, motor, teeth="45"))
    self.assertTrue(passed, text)
    self.assertEqual(raw["actuator"]["tracked_arc_deg"], TEETH_SETS[45])
    self.assertAlmostEqual(raw["actuator"]["mechanical_ratio"], 166 / 16)
    self.assertIn("the long back teeth (45 degrees each way)", text)
    # the long teeth keep the other mounts' gearing
    car, motor = SimCar(), SimMotor(true_direction=1, arc_deg=TEETH_SETS[29])
    passed, raw, text, _ = run_setup(car, motor, SimDriver(car, motor, teeth="29"))
    self.assertTrue(passed, text)
    self.assertAlmostEqual(raw["actuator"]["mechanical_ratio"], 197 / 19)

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
    r = check_drive.check(copy.deepcopy(PARKED_RAW), self._drive(car))
    new_raw, fit, motor = r.new_raw, r.fit, r.motor
    self.assertTrue(fit.ok, fit.detail)
    self.assertTrue(motor.ok, motor.detail)
    cfg = parse_config(new_raw)
    self.assertTrue(cfg.verified)
    self.assertEqual(cfg.message_of("VEHICLE_SPEED").addr, 0x309)
    self.assertEqual(cfg.signals["VEHICLE_SPEED"].factor, 0.005)

  def _angle_car(self, factor: float) -> SimCar:
    """A car whose steering angle follows the drive's steering (turning_drive: 8 sin(2 pi t / 30) + 3 degrees)."""
    import math
    layout = {**SimCar().layout, "STEER_ANGLE": (0x1C2, 7, 16)}
    car = SimCar(layout=layout, messages={**MESSAGES, 0x1C2: (8, 100)}, angle_factor_deg=factor)
    car.wheel_deg_fn = lambda: 8.0 * math.sin(2 * math.pi * car.t / 30.0) + 3.0
    return car

  def _angle_raw(self, factor: float) -> dict:
    raw = copy.deepcopy(PARKED_RAW)
    raw["fcan"]["messages"].append({"name": "MSG_1C2", "addr": "0x1C2", "len": 8, "freq": 100, "checksum": "honda", "counter": True})
    raw["fcan"]["signals"]["STEER_ANGLE"] = {"message": "MSG_1C2", "start_bit": 7, "size": 16, "byte_order": "big", "signed": True,
                                             "factor": factor, "offset": 0.0, "unit": "deg"}
    return raw

  def test_steering_angle_checked_against_the_car_turning(self):
    r = check_drive.check(self._angle_raw(-0.1), self._drive(self._angle_car(-0.1)))
    self.assertTrue(r.fit.ok and r.motor.ok)
    self.assertTrue(r.angle.ok, r.angle.detail)
    self.assertIn("STEER_ANGLE", r.new_raw["fcan"]["signals"])
    self.assertTrue(parse_config(r.new_raw).verified)
    # saved backwards in part 1 (a left turn read as right): dropped, the drive still passes on the motor's angle
    r = check_drive.check(self._angle_raw(0.1), self._drive(self._angle_car(-0.1)))
    self.assertFalse(r.angle.ok)
    self.assertIn("reads the opposite way", r.angle.detail)
    self.assertNotIn("STEER_ANGLE", r.new_raw["fcan"]["signals"])
    self.assertTrue(parse_config(r.new_raw).verified)

  def test_wrong_motor_direction_is_caught(self):
    raw = copy.deepcopy(PARKED_RAW)
    raw["actuator"]["direction"] = -1   # part 1 saved it backwards
    r = check_drive.check(raw, self._drive(SimCar(), true_direction=1))
    new_raw, fit, motor = r.new_raw, r.fit, r.motor
    self.assertTrue(fit.ok, fit.detail)
    self.assertIsNone(new_raw)
    self.assertTrue(motor.wrong_way)

  def test_needs_the_lift_lever_down(self):
    r = check_drive.check(copy.deepcopy(PARKED_RAW), self._drive(SimCar(), with_motor=False))
    new_raw, motor = r.new_raw, r.motor
    self.assertIsNone(new_raw)
    self.assertIn("lift lever down", motor.detail)

  def test_too_little_driving(self):
    car = SimCar()
    frames = car.run(10.0, VEHICLE_SPEED=60.0)
    drive = check_drive.Drive(frames, [], [(frames[0][0], 16.7)] * 5, [], 10.0)
    r = check_drive.check(copy.deepcopy(PARKED_RAW), drive)
    new_raw, fit, motor = r.new_raw, r.fit, r.motor
    self.assertIsNone(new_raw)
    self.assertFalse(fit.ok)
    self.assertIsNone(motor)

  def test_part_1_first(self):
    printed: list[str] = []
    with mock.patch.object(check_drive, "load_raw_config", lambda: copy.deepcopy(DEFAULT_RAW)):
      self.assertFalse(check_drive.run(printed.append, "/nonexistent", save=lambda r: "x"))
    self.assertIn("Run part 1 of the car setup first", printed[-1])

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


class TestStandalone(unittest.TestCase):
  """The default: the comma device not connected to the car. Part 1 checks only the motor; part 2 checks the comma
  device's own speed against GPS and saves the factor between them."""

  def test_part_1_checks_only_the_motor(self):
    car, motor = SimCar(), SimMotor(true_direction=-1)
    motor.powered = False
    passed, raw, text, driver = run_setup(car, motor, raw=STANDALONE_RAW, panda_cls=NoCarPanda)
    self.assertTrue(passed, text)
    cfg = parse_config(raw)
    self.assertFalse(cfg.car_network)
    self.assertEqual(cfg.actuator.direction, -1)
    self.assertTrue(cfg.setup.get("parked"))
    self.assertGreater(motor.wheel_deg - motor.teeth_center_deg, 2.0)   # the push turned the wheel left
    asked = " ".join(driver.prompts)
    for thing in ("brake", "gas pedal", "turn signal", "shifter to", "Open the driver"):
      self.assertNotIn(thing, asked)                      # nothing asked about the car itself
    self.assertNotIn("your car's messages", text)
    self.assertNotIn("No data from the car", text)
    for word in ("F-CAN", "pinion", "rim", "MADS", "panda", "gear ring", "gear lever", "arm", "MAIN"):
      self.assertIsNone(re.search(rf"\b{re.escape(word)}\b", asked + text, re.IGNORECASE), word)

  def test_part_1_without_the_motor(self):
    car, motor = SimCar(), SimMotor()
    driver = SimDriver(car, motor, motor_works=False)
    motor.powered = False
    passed, raw, text, _ = run_setup(car, motor, driver=driver, raw=STANDALONE_RAW, panda_cls=NoCarPanda)
    self.assertFalse(passed)
    self.assertNotIn("parked", raw.get("setup", {}))

  def _drive(self, device_scale: float = 1.0, true_direction: int = 1, device: bool = True) -> check_drive.Drive:
    import math
    gps, dev = [], []
    for i in range(4000):          # 200 s: the device's own speed 20 times a second, GPS twice
      t = i * 0.05
      v = 8 + 10 * (0.5 + 0.5 * math.sin(t / 12.5))
      dev.append((t, v * device_scale))
      if i % 10 == 0:
        gps.append((t, v))
    motor, headings = turning_drive(200.0, true_direction)
    return check_drive.Drive([], motor, gps, headings, 0.0, dev if device else [])

  def test_part_2_saves_the_speed_factor(self):
    raw = {**copy.deepcopy(STANDALONE_RAW), "setup": {"parked": "2026-10-10T10:00:00"}}
    r = check_drive.check(raw, self._drive(device_scale=0.96))
    self.assertTrue(r.fit.ok, r.fit.detail)
    self.assertTrue(r.motor.ok, r.motor.detail)
    cfg = parse_config(r.new_raw)
    self.assertTrue(cfg.verified)
    self.assertAlmostEqual(cfg.device_speed_scale, 1 / 0.96, delta=0.005)
    self.assertEqual(r.new_raw["fcan"], STANDALONE_RAW["fcan"])     # the car's map is left alone

  def test_part_2_fails_without_the_devices_speed_or_with_a_wrong_direction(self):
    raw = {**copy.deepcopy(STANDALONE_RAW), "setup": {"parked": "2026-10-10T10:00:00"}}
    r = check_drive.check(raw, self._drive(device=False))
    self.assertIsNone(r.new_raw)
    self.assertIn("missing", r.fit.detail)
    r = check_drive.check(raw, self._drive(device_scale=1.3))
    self.assertIsNone(r.new_raw)
    raw["actuator"]["direction"] = -1
    r = check_drive.check(raw, self._drive(true_direction=1))
    self.assertIsNone(r.new_raw)
    self.assertTrue(r.motor.wrong_way)

  def test_part_2_reads_the_devices_speed_from_the_recording(self):
    from openpilot.cereal import log
    import zstandard

    drive = self._drive(device_scale=1.04)
    raw = {**copy.deepcopy(STANDALONE_RAW), "setup": {"parked": "2026-10-10T10:00:00"}}
    with tempfile.TemporaryDirectory() as root:
      events = []
      for t, v in drive.device:
        evt = log.Event.new_message(logMonoTime=int(t * 1e9), valid=True)
        dm = evt.init("deviceMotion")
        dm.velocityDevice.x, dm.velocityDevice.y, dm.velocityDevice.z, dm.velocityDevice.valid = v, 0.0, 0.0, True
        dm.inputsOK, dm.posenetOK = True, True
        events.append(evt)
      for t, angle in drive.motor:
        evt = log.Event.new_message(logMonoTime=int(t * 1e9))
        can = evt.init("can", 1)
        data = bytearray(8)
        data[5:7] = (round(angle / 0.125) & 0xFFFF).to_bytes(2, "little")
        can[0].address, can[0].dat, can[0].src = 0x22F, bytes(data), 1
        events.append(evt)
      speeds = dict(drive.gps)
      for t, b, _ in drive.headings:
        evt = log.Event.new_message(logMonoTime=int(t * 1e9))
        fix = evt.init("gpsLocation")
        nearest = min(speeds, key=lambda x: abs(x - t))
        fix.speed, fix.hasFix, fix.speedAccuracy = speeds[nearest], True, 0.3
        fix.bearingDeg, fix.bearingAccuracyDeg = b, 1.0
        events.append(evt)
      events.sort(key=lambda e: e.logMonoTime)
      path = os.path.join(root, "0000002b--abcdef1234--0")
      os.makedirs(path)
      with open(os.path.join(path, "rlog.zst"), "wb") as f:
        f.write(zstandard.ZstdCompressor().compress(b"".join(e.to_bytes() for e in events)))
      seg = check_drive.read_segment(path)
      self.assertEqual(len(seg.device), len(drive.device))
      self.assertEqual(seg.frames, [])
      printed: list[str] = []
      saved: list[dict] = []
      with mock.patch.object(check_drive, "load_raw_config", lambda: copy.deepcopy(raw)):
        self.assertTrue(check_drive.run(printed.append, root, save=lambda r: saved.append(r) or "x"), "\n".join(printed))
      self.assertAlmostEqual(saved[0]["device_speed_scale"], 1 / 1.04, delta=0.01)
      self.assertIn("Both parts of the setup have passed", printed[-1])

if __name__ == "__main__":
  unittest.main()
