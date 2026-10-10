"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The two chimes for the add-on steering motor: a curve ahead past the teeth, and the gear running off them.
"""
import math
import unittest

from opendbc.car import gen_empty_fingerprint
from opendbc.car.car_helpers import interfaces
from opendbc.car.hondastepper.values import CAR, CONFIG
from opendbc.car.structs import car
from openpilot.cereal import log
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.sunnypilot.selfdrive.car.hondastepper_alerts import (CHIME_S, LOOKAHEAD_S, MARGIN_DEG, PAST_TEETH_S, QUIET_S,
                                                                      STRAIGHT_MIN_S, TeethAlerts)

PLATFORM = CAR.HONDA_ACCORD_8G_STEPPER
V = 30.0   # m/s, 67 mph
SHORT_TEETH_REACH = 42.2 / 2 - 6.5   # 14.6 degrees


def car_params():
  CI = interfaces[PLATFORM]
  return CI.get_params(PLATFORM, gen_empty_fingerprint(), [], False, False, False)


def model_path(curvature_at_s: dict[float, float], v: float = V):
  """A planned path: curvature (1/m) from each listed time on, straight before the first."""
  m = log.ModelDataV2.new_message()
  t_idxs = ModelConstants.T_IDXS
  curvs = []
  for t in t_idxs:
    c = 0.0
    for t0 in sorted(curvature_at_s):
      if t >= t0:
        c = curvature_at_s[t0]
    curvs.append(c)
  m.orientationRate.t = t_idxs
  m.orientationRate.z = [c * v for c in curvs]
  m.velocity.t = t_idxs
  m.velocity.x = [v] * len(t_idxs)
  return m


class Messages:
  def __init__(self, lat_active: bool = True, curvature: float = 0.0, model=None, torque: float = 0.5):
    cc = car.CarControl.new_message(latActive=lat_active)
    cc.actuators.torque = torque         # lane keeping pushing left
    self.msgs = {
      'carControl': cc,
      'controlsState': log.ControlsState.new_message(curvature=curvature),
      'modelV2': model if model is not None else model_path({}),
    }

  def __getitem__(self, key):
    return self.msgs[key]


def car_state(v: float = V, angle_deg: float = 0.0, pressed: bool = False, lever_down: bool = True, rate: float | None = None):
  """pressed: the car port reports the driver steering; by default the motor spinning off the teeth the way it pushes
  (left, 300 degrees a second)."""
  CS = car.CarState.new_message()
  CS.vEgo = v
  CS.steeringAngleDeg = angle_deg
  CS.steeringRateDeg = (300.0 if pressed else 0.0) if rate is None else rate
  CS.steeringPressed = pressed
  CS.cruiseState.available = lever_down
  return CS


class TestTeethAlerts(unittest.TestCase):
  def setUp(self):
    self.CP = car_params()
    self.alerts = TeethAlerts(self.CP, SHORT_TEETH_REACH)

  def run_frames(self, n: int, CS, sm) -> list[tuple[bool, bool]]:
    return [self.alerts.update(CS, sm) for _ in range(n)]

  def curvature_for(self, deg: float) -> float:
    """The curvature at V that needs this many degrees of steering wheel by the vehicle model."""
    return self.alerts.VM.calc_curvature(math.radians(deg), V, 0.0)

  def test_reach_from_the_config(self):
    self.assertAlmostEqual(CONFIG.actuator.full_push_reach_deg, 71.5 / 2 - 6.5)

  def test_straight_road_is_quiet(self):
    out = self.run_frames(500, car_state(), Messages())
    self.assertFalse(any(c or p for c, p in out))

  def test_curve_ahead_past_the_teeth_chimes_then_goes_quiet(self):
    # a curve 2 s ahead that needs 18 degrees: more than the short teeth's 14.6
    sm = Messages(model=model_path({2.0: self.curvature_for(18.0)}))
    out = self.run_frames(int((CHIME_S + QUIET_S + 1.0) / 0.01), car_state(), sm)
    curve = [c for c, _ in out]
    self.assertTrue(curve[0])
    self.assertGreater(self.alerts.planned_deg, SHORT_TEETH_REACH - MARGIN_DEG)
    self.assertEqual(sum(curve[:int(CHIME_S / 0.01)]), int(CHIME_S / 0.01))   # chimes for CHIME_S
    self.assertFalse(any(curve[int(CHIME_S / 0.01) + 1:int((CHIME_S + QUIET_S) / 0.01) - 1]))   # then quiet
    self.assertTrue(curve[-1])   # still past the teeth after the quiet time: chimes again

  def test_gentle_curve_or_far_curve_is_quiet(self):
    for path in ({2.0: self.curvature_for(10.0)}, {LOOKAHEAD_S + 1.0: self.curvature_for(25.0)}):
      alerts = TeethAlerts(self.CP, SHORT_TEETH_REACH)
      sm = Messages(model=model_path(path))
      self.assertFalse(any(alerts.update(car_state(), sm)[0] for _ in range(200)), path)

  def test_long_teeth_take_more(self):
    alerts = TeethAlerts(self.CP, 71.5 / 2 - 6.5)
    sm = Messages(model=model_path({1.0: self.curvature_for(18.0)}))
    self.assertFalse(any(alerts.update(car_state(), sm)[0] for _ in range(100)))
    sm = Messages(model=model_path({1.0: self.curvature_for(30.0)}))
    self.assertTrue(alerts.update(car_state(), sm)[0])

  def test_quiet_when_lane_keeping_is_off_or_slow(self):
    sm = Messages(lat_active=False, model=model_path({1.0: self.curvature_for(25.0)}))
    self.assertFalse(any(c for c, _ in self.run_frames(50, car_state(), sm)))
    sm = Messages(model=model_path({1.0: self.curvature_for(25.0)}, v=3.0))
    self.assertFalse(any(c for c, _ in self.run_frames(50, car_state(v=3.0), sm)))

  def test_past_the_teeth_chimes_once(self):
    sm = Messages()
    self.run_frames(10, car_state(), sm)
    out = self.run_frames(int(PAST_TEETH_S / 0.01) + 50, car_state(pressed=True), sm)
    past = [p for _, p in out]
    self.assertTrue(past[0])
    self.assertAlmostEqual(sum(past), int(PAST_TEETH_S / 0.01), delta=1)
    self.assertFalse(past[-1])
    # not when lane keeping wasn't pushing
    alerts = TeethAlerts(self.CP, SHORT_TEETH_REACH)
    alerts.update(car_state(), Messages(lat_active=False))
    self.assertFalse(alerts.update(car_state(pressed=True), Messages(lat_active=False))[1])
    # nor when the driver turns the wheel against the motor (stand-alone reports that as pressed too)
    alerts = TeethAlerts(self.CP, SHORT_TEETH_REACH)
    alerts.update(car_state(), Messages())
    self.assertFalse(alerts.update(car_state(pressed=True, rate=-40.0), Messages())[1])

  def test_motor_angle_refines_the_ratio_and_the_wheel_near_the_end_chimes(self):
    # straight for a while: the motor's angle then is the straight-ahead reference (it powered up 40 degrees off)
    self.run_frames(int(STRAIGHT_MIN_S / 0.01) + 10, car_state(angle_deg=40.0), Messages())
    self.assertTrue(self.alerts.straight_valid)
    self.assertAlmostEqual(self.alerts.straight_ref, 40.0, places=3)
    # a curve the vehicle model puts at 8 degrees needs 10.4 on this car: the ratio scale learns 1.3
    curv = self.curvature_for(8.0)
    self.run_frames(400, car_state(angle_deg=40.0 + 10.4), Messages(curvature=curv))
    self.assertAlmostEqual(self.alerts.ratio_scale, 1.3, places=2)
    # so a planned curve the model would put at 12 degrees (15.6 here) now chimes
    sm = Messages(curvature=curv, model=model_path({1.0: self.curvature_for(12.0)}))
    self.assertTrue(self.alerts.update(car_state(angle_deg=40.0 + 10.4), sm)[0])
    # and the wheel itself within the margin of the last tooth chimes, planned path or not
    alerts = TeethAlerts(self.CP, SHORT_TEETH_REACH)
    for _ in range(int(STRAIGHT_MIN_S / 0.01) + 10):
      alerts.update(car_state(angle_deg=40.0), Messages())
    self.assertTrue(alerts.update(car_state(angle_deg=40.0 + SHORT_TEETH_REACH - 1.0), Messages(curvature=curv))[0])

  def test_the_car_own_angle_keeps_the_reference(self):
    from opendbc.car.hondastepper.values import HondaStepperFlags
    CP = car_params()
    CP.flags |= HondaStepperFlags.FCAN_STEER_ANGLE.value
    alerts = TeethAlerts(CP, SHORT_TEETH_REACH)
    for _ in range(int(STRAIGHT_MIN_S / 0.01) + 10):
      alerts.update(car_state(angle_deg=2.0), Messages())
    self.assertTrue(alerts.straight_valid)
    alerts.update(car_state(angle_deg=2.0, pressed=True), Messages())
    alerts.update(car_state(angle_deg=2.0, lever_down=False), Messages())
    self.assertTrue(alerts.straight_valid)

  def test_lever_up_or_free_spin_forgets_the_reference(self):
    self.run_frames(int(STRAIGHT_MIN_S / 0.01) + 10, car_state(angle_deg=40.0), Messages())
    self.assertTrue(self.alerts.straight_valid)
    self.alerts.update(car_state(pressed=True), Messages())
    self.assertFalse(self.alerts.straight_valid)
    self.run_frames(int(STRAIGHT_MIN_S / 0.01) + 10, car_state(angle_deg=40.0), Messages())
    self.assertTrue(self.alerts.straight_valid)
    self.alerts.update(car_state(lever_down=False), Messages())
    self.assertFalse(self.alerts.straight_valid)


if __name__ == "__main__":
  unittest.main()
