"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
import unittest

import numpy as np

from openpilot.cereal import log
from opendbc.car import gen_empty_fingerprint
from opendbc.car.car_helpers import interfaces
from opendbc.car.hondastepper.values import CAR as HONDASTEPPER
from opendbc.car.structs import car
from opendbc.car.toyota.values import CAR as TOYOTA
from opendbc.car.vehicle_model import VehicleModel
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.car.helpers import convert_to_capnp
from openpilot.selfdrive.controls.lib.latcontrol_torque import LatControlTorque
from openpilot.selfdrive.locationd.helpers import Measurement, Pose
from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_v0 import LatControlTorque as LatControlTorqueV0
from openpilot.sunnypilot.selfdrive.controls.lib.measured_curvature import YAW_RATE_SPEEDS, get_measured_curvature, uses_yaw_rate


def make_pose(yaw_rate: float) -> Pose:
  """Calibrated pose turning at yaw_rate [rad/s]; the calibrated frame's z points down, so positive yaw is a right turn."""
  zero = Measurement(np.zeros(3), np.ones(3) * 0.01)
  return Pose(orientation=zero, velocity=zero, acceleration=zero,
              angular_velocity=Measurement(np.array([0.0, 0.0, yaw_rate]), np.ones(3) * 0.001))


def car_params(platform):
  CI = interfaces[platform]
  CP = CI.get_params(platform, gen_empty_fingerprint(), [], False, False, False)
  CP_SP = CI.get_params_sp(CP, platform, gen_empty_fingerprint(), [], False, False, False)
  return CP, CP_SP, CI(CP, CP_SP)


class TestMeasuredCurvature(unittest.TestCase):
  def setUp(self):
    self.CP, _, _ = car_params(HONDASTEPPER.HONDA_ACCORD_8G_STEPPER)
    self.VM = VehicleModel(self.CP)
    self.params = log.VehicleParameters.new_message()

  def _cs(self, v_ego: float, angle_deg: float):
    CS = car.CarState.new_message()
    CS.vEgo = v_ego
    CS.steeringAngleDeg = angle_deg
    return CS

  def test_which_cars(self):
    self.assertTrue(uses_yaw_rate(self.CP.as_reader()))
    toyota, _, _ = car_params(TOYOTA.TOYOTA_RAV4)
    self.assertFalse(uses_yaw_rate(toyota.as_reader()))

  def test_angle_cars_unchanged(self):
    CS = self._cs(20.0, 12.0)
    expected = -self.VM.calc_curvature(math.radians(12.0), 20.0, 0.0)
    self.assertAlmostEqual(get_measured_curvature(False, CS, self.VM, self.params, make_pose(0.3)), expected)
    # no pose yet: the angle, even for a gyro car
    self.assertAlmostEqual(get_measured_curvature(True, CS, self.VM, self.params, None), expected)

  def test_gyro_above_walking_pace(self):
    # the motor's angle reads 90 degrees off (it powered up with the wheel turned), the car drives straight
    CS = self._cs(20.0, 90.0)
    self.assertAlmostEqual(get_measured_curvature(True, CS, self.VM, self.params, make_pose(0.0)), 0.0)
    self.assertAlmostEqual(get_measured_curvature(True, CS, self.VM, self.params, make_pose(0.2)), 0.2 / 20.0)

  def test_blend_at_walking_pace(self):
    angle_curv = -self.VM.calc_curvature(math.radians(30.0), 1.5, 0.0)
    gyro_curv = 0.05 / 1.5
    lo, hi = YAW_RATE_SPEEDS
    for v, w in ((lo, 0.0), ((lo + hi) / 2, 0.5), (hi, 1.0), (0.2, 0.0)):
      CS = self._cs(v, 30.0)
      angle_curv = -self.VM.calc_curvature(math.radians(30.0), v, 0.0)
      gyro_curv = 0.05 / max(v, lo)
      self.assertAlmostEqual(get_measured_curvature(True, CS, self.VM, self.params, make_pose(0.05)),
                             (1 - w) * angle_curv + w * gyro_curv, places=6)

  def test_same_sign_as_angle(self):
    # a left turn: positive steering angle; the gyro sees the vehicle model's left yaw as negative z
    v, sa = 15.0, math.radians(20.0)
    yaw_left = self.VM.yaw_rate(sa, v, 0.0)
    from_angle = get_measured_curvature(False, self._cs(v, 20.0), self.VM, self.params, None)
    from_gyro = get_measured_curvature(True, self._cs(v, 0.0), self.VM, self.params, make_pose(-yaw_left))
    self.assertLess(from_angle, 0.0)
    self.assertAlmostEqual(from_gyro, from_angle, places=6)


class TestTorqueControllersWithGyro(unittest.TestCase):
  def _run(self, controller_cls, platform, angle_deg: float, yaw_rate: float):
    CP, CP_SP, CI = car_params(platform)
    controller = controller_cls(CP.as_reader(), convert_to_capnp(CP_SP).as_reader(), CI, DT_CTRL)
    VM = VehicleModel(CP)
    CS = car.CarState.new_message()
    CS.vEgo = 20.0
    CS.steeringAngleDeg = angle_deg
    params = log.VehicleParameters.new_message()
    for _ in range(100):
      torque, _, lac_log = controller.update(True, CS, VM, params, False, 0.0, make_pose(yaw_rate), False, 0.2)
    return torque, lac_log

  def test_motor_angle_ignored_at_speed(self):
    for cls in (LatControlTorque, LatControlTorqueV0):
      # straight road, straight car, motor angle reading far off: nothing to correct
      torque, lac_log = self._run(cls, HONDASTEPPER.HONDA_ACCORD_8G_STEPPER, 90.0, 0.0)
      self.assertAlmostEqual(lac_log.actualLateralAccel, 0.0, places=6, msg=cls.__module__)
      self.assertLess(abs(torque), 0.05, cls.__module__)
      # drifting right: steer back left (positive torque is left)
      torque, lac_log = self._run(cls, HONDASTEPPER.HONDA_ACCORD_8G_STEPPER, 0.0, 0.05)
      self.assertAlmostEqual(lac_log.actualLateralAccel, 0.05 * 20.0, places=4, msg=cls.__module__)
      self.assertGreater(torque, 0.05, cls.__module__)

  def test_angle_cars_still_use_angle(self):
    _, lac_log = self._run(LatControlTorqueV0, TOYOTA.TOYOTA_RAV4, 5.0, 0.0)
    self.assertLess(lac_log.actualLateralAccel, -0.1)


if __name__ == "__main__":
  unittest.main()
