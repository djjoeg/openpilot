"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Two chimes for the Honda Accord with the add-on steering motor (hondastepper). The motor can only push the steering
wheel as far as the printed steering wheel teeth reach: about 15 degrees each way from straight with the short
teeth, 29 with the long ones (the car setup saves which are on).

 - Curve ahead: the path the driving model plans for the next few seconds needs more steering wheel than the teeth
   reach, so the driver steers it. The steering wheel angle a curve needs comes from the vehicle model (the one the
   controls use) and the car's steer ratio, which isn't measured on this car: while the motor gear is on the teeth
   and the car is turning, the motor's own angle (exact while it is on the teeth) refines that ratio.
 - Past the teeth: the motor gear just ran off the teeth while lane keeping was pushing, so the push has stopped.
   The car port reports that as the driver steering, with no sound of its own.

Both are estimates until driven: the curve chime can come early on a curve the motor could have handled.
"""
import math
from collections import deque

import numpy as np

from opendbc.car.vehicle_model import VehicleModel

LOOKAHEAD_S = 3.5          # how far along the planned path to look
MARGIN_DEG = 2.0           # chime when the planned steering wheel angle is within this of the last tooth
MIN_SPEED = 5.0            # m/s; below this the model's path and the gyro say little
CHIME_S = 3.0              # the curve chime shows this long ...
QUIET_S = 10.0             # ... then stays quiet this long, so a long curve doesn't chime over and over
PAST_TEETH_S = 2.0         # the past-the-teeth chime shows this long
STRAIGHT_CURV = 0.0005     # 1/m; gentler than this (a 2 km radius) counts as straight
STRAIGHT_TAU_S = 3.0       # how fast the straight-ahead reference follows the motor's angle
STRAIGHT_MIN_S = 2.0       # straight driving needed before the reference counts
TURNING_CURV = 0.002       # 1/m; tighter than this (a 500 m radius) teaches the steer ratio
RATIO_SAMPLE_EVERY = 10    # frames between samples
RATIO_SAMPLES = 300        # 30 s of turning
RATIO_SCALE_LIMITS = (0.6, 1.6)
DT = 0.01


class TeethAlerts:
  def __init__(self, CP, reach_deg: float):
    self.VM = VehicleModel(CP)
    self.reach_deg = reach_deg
    self.ratio_scale = 1.0              # the car needs this times the vehicle model's steering wheel angle
    self.ratio_samples: deque[float] = deque(maxlen=RATIO_SAMPLES)
    self.straight_ref = 0.0             # the motor's angle (steering wheel degrees) driving straight
    self.straight_s = 0.0               # seconds of straight driving behind the reference
    self.straight_valid = False
    self.curve_s = 0.0                  # time left on the curve chime, then negative while quiet
    self.past_teeth_s = 0.0
    self.pressed_prev = False
    self.frame = 0
    self.planned_deg = 0.0              # the most steering wheel the planned path needs, for logs and tests
    self.now_deg = 0.0

  def angle_for_curvature(self, curvature: float, v: float) -> float:
    """Steering wheel degrees for a curvature at a speed, with what has been learned of the car's ratio."""
    return abs(math.degrees(self.VM.get_steer_from_curvature(abs(curvature), max(v, MIN_SPEED), 0.0))) * self.ratio_scale

  def _learn(self, CS, curvature: float, lat_active: bool) -> None:
    motor_on_teeth = CS.cruiseState.available and not CS.steeringPressed
    if not motor_on_teeth:
      # lever up, or the gear just ran off the teeth: the motor's count means nothing until it has gone straight again
      self.straight_valid, self.straight_s = False, 0.0
      return
    angle = float(CS.steeringAngleDeg)
    if CS.vEgo > MIN_SPEED and abs(curvature) < STRAIGHT_CURV:
      a = DT / STRAIGHT_TAU_S
      self.straight_ref = angle if self.straight_s == 0.0 else self.straight_ref + a * (angle - self.straight_ref)
      self.straight_s += DT
      self.straight_valid = self.straight_s >= STRAIGHT_MIN_S
    if (self.straight_valid and lat_active and CS.vEgo > MIN_SPEED and abs(curvature) > TURNING_CURV
        and self.frame % RATIO_SAMPLE_EVERY == 0):
      vm_deg = abs(math.degrees(self.VM.get_steer_from_curvature(abs(curvature), CS.vEgo, 0.0)))
      motor_deg = abs(angle - self.straight_ref)
      if vm_deg > 1.5 and motor_deg > 1.0:
        self.ratio_samples.append(motor_deg / vm_deg)
        self.ratio_scale = float(np.clip(np.median(self.ratio_samples), *RATIO_SCALE_LIMITS))

  def _planned(self, model) -> float:
    """The most steering wheel the planned path needs within LOOKAHEAD_S, in degrees."""
    rate, vel = model.orientationRate, model.velocity
    most = 0.0
    for t, yaw_rate, v in zip(rate.t, rate.z, vel.x, strict=False):
      if t > LOOKAHEAD_S:
        break
      v = max(float(v), MIN_SPEED)
      most = max(most, self.angle_for_curvature(float(yaw_rate) / v, v))
    return most

  def update(self, CS, sm) -> tuple[bool, bool]:
    """Returns (curve ahead chime, past the teeth chime) for this frame."""
    self.frame += 1
    lat_active = bool(sm['carControl'].latActive)
    curvature = float(sm['controlsState'].curvature)
    self._learn(CS, curvature, lat_active)

    # the gear running off the teeth while lane keeping pushed
    if CS.steeringPressed and not self.pressed_prev and lat_active:
      self.past_teeth_s = PAST_TEETH_S
    self.pressed_prev = bool(CS.steeringPressed)
    self.past_teeth_s = max(self.past_teeth_s - DT, 0.0)

    # the curve ahead
    self.planned_deg = self._planned(sm['modelV2']) if lat_active and CS.vEgo > MIN_SPEED else 0.0
    self.now_deg = abs(float(CS.steeringAngleDeg) - self.straight_ref) if self.straight_valid else 0.0
    needed = max(self.planned_deg, self.now_deg) if lat_active and not CS.steeringPressed else 0.0
    if self.curve_s > 0.0:
      self.curve_s -= DT
      if self.curve_s <= 0.0:
        self.curve_s = -QUIET_S
    elif self.curve_s < 0.0:
      self.curve_s = min(self.curve_s + DT, 0.0)
    elif needed > self.reach_deg - MARGIN_DEG:
      self.curve_s = CHIME_S
    return self.curve_s > 0.0, self.past_teeth_s > 0.0
