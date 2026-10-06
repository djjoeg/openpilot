"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

How much the car is actually turning, for the lateral controllers and controlsd.

Normally this comes from the steering angle through the vehicle model. Cars that set
CP.lateralTuning.torque.useYawRate only know the steering angle relative to where their steering motor
started (hondastepper: a motor turning the steering wheel through printed teeth on the steering wheel), so above walking pace the
curvature comes from the comma device's gyro instead: curvature = yaw rate / speed. That is how openpilot
measured it for cars with useSteeringAngle = False before the field was removed. Below YAW_RATE_SPEEDS the
gyro says little about curvature, so it blends back to the steering angle.
"""
import math

import numpy as np

YAW_RATE_SPEEDS = (1.0, 2.0)  # m/s: steering angle at and below the first, gyro at and above the second


def uses_yaw_rate(CP) -> bool:
  return CP.lateralTuning.which() == 'torque' and bool(CP.lateralTuning.torque.useYawRate)


def get_measured_curvature(use_yaw_rate: bool, CS, VM, params, calibrated_pose) -> float:
  """Curvature the car is driving now [1/m], in the controllers' sign convention (opposite to steeringAngleDeg)."""
  curvature_from_angle = -VM.calc_curvature(math.radians(CS.steeringAngleDeg - params.angleOffsetDeg), CS.vEgo, params.roll)
  if not use_yaw_rate or calibrated_pose is None:
    return float(curvature_from_angle)
  curvature_from_yaw = calibrated_pose.angular_velocity.yaw / max(CS.vEgo, YAW_RATE_SPEEDS[0])
  return float(np.interp(CS.vEgo, YAW_RATE_SPEEDS, [curvature_from_angle, curvature_from_yaw]))
