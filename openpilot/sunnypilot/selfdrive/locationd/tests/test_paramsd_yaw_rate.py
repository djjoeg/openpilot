"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

paramsd with cars that measure curvature from the gyro (CP.lateralTuning.torque.useYawRate): their steering angle is
only relative to where the steering motor started, so it must not feed the learner, and must not decide whether
the learner is active.
"""
import unittest
from unittest import mock

import numpy as np

from opendbc.car import gen_empty_fingerprint
from opendbc.car.car_helpers import interfaces
from opendbc.car.hondastepper.values import CAR as HONDASTEPPER
from opendbc.car.structs import car
from opendbc.car.toyota.values import CAR as TOYOTA
from openpilot.selfdrive.locationd import paramsd
from openpilot.selfdrive.locationd.models.car_kf import CarKalman, States
from openpilot.selfdrive.locationd.models.constants import ObservationKind


class FakeKalman:
  """Stands in for the generated car Kalman filter and records what it is told."""
  initial_x = CarKalman.initial_x
  P_initial = CarKalman.P_initial

  def __init__(self, _generated_dir):
    self.observed: list[int] = []
    self.x = CarKalman.initial_x.copy()
    self.P = np.diag(CarKalman.P_initial.diagonal())
    self.t = 0.0
    self.filter = mock.MagicMock()

  def set_globals(self, **_kwargs):
    pass

  def init_state(self, x, covs, filter_time):
    self.x = np.array(x, dtype=float)

  def predict_and_observe(self, t, kind, data, R=None):
    self.observed.append(kind)


def learner_for(platform) -> paramsd.VehicleParamsLearner:
  CI = interfaces[platform]
  CP = CI.get_params(platform, gen_empty_fingerprint(), [], False, False, False)
  with mock.patch.object(paramsd, "CarKalman", FakeKalman):
    return paramsd.VehicleParamsLearner(CP.as_reader(), CP.steerRatio, 1.0, 0.0)


def car_state(angle_deg: float, v_ego: float = 20.0):
  CS = car.CarState.new_message()
  CS.steeringAngleDeg = angle_deg
  CS.vEgo = v_ego
  CS.gearShifter = car.CarState.GearShifter.drive
  return CS.as_reader()


class TestParamsdYawRateCars(unittest.TestCase):
  def test_gyro_car_ignores_steering_angle(self):
    learner = learner_for(HONDASTEPPER.HONDA_ACCORD_8G_STEPPER)
    self.assertTrue(learner.ignore_steering_angle)
    # the motor's angle reads 90 degrees because it powered up with the wheel turned
    learner.handle_log(1.0, "carState", car_state(90.0))
    self.assertTrue(learner.active)
    self.assertNotIn(ObservationKind.STEER_ANGLE, learner.kf.observed)
    self.assertIn(ObservationKind.ROAD_FRAME_X_SPEED, learner.kf.observed)
    # the angle offset stays where it started, so it can't make the parameters invalid
    msg = learner.get_msg(True)
    self.assertTrue(msg.vehicleParameters.angleOffsetValid)
    self.assertAlmostEqual(msg.vehicleParameters.angleOffsetDeg, np.degrees(learner.kf.x[States.ANGLE_OFFSET].item()))

  def test_angle_cars_unchanged(self):
    learner = learner_for(TOYOTA.TOYOTA_RAV4)
    self.assertFalse(learner.ignore_steering_angle)
    learner.handle_log(1.0, "carState", car_state(10.0))
    self.assertTrue(learner.active)
    self.assertIn(ObservationKind.STEER_ANGLE, learner.kf.observed)
    learner.kf.observed.clear()
    learner.handle_log(1.1, "carState", car_state(90.0))  # outside the linear region
    self.assertFalse(learner.active)
    self.assertEqual(learner.kf.observed, [])


if __name__ == "__main__":
  unittest.main()
