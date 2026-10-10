"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The Honda Accord with the add-on steering motor (hondastepper), stand-alone: the comma device isn't connected to the
car, so the car's speed comes from the comma device itself. Its estimate of its own motion (locationd's deviceMotion:
the camera's view of the road moving past, fused with its motion sensors) gives the speed 20 times a second, scaled by
the factor the car setup's drive check measured against GPS. GPS keeps checking it while driving: if the two disagree
for a few seconds, the speed is marked unusable and the motor doesn't push until they agree again. Without a GPS fix
(a tunnel, a parking garage) the device's own speed is used alone.

openpilot's card hands the result to the car port before every update (CarState.set_device_speed).
"""
import math
from dataclasses import dataclass

DEVICE_MAX_AGE_S = 0.3       # deviceMotion comes 20 times a second; older than this it's gone
GPS_MAX_AGE_S = 1.5          # a GPS fix older than this isn't compared (GPS comes 1 to 10 times a second)
GPS_MAX_SPEED_ERROR = 1.0    # m/s: a fix less sure of its speed than this isn't compared
DISAGREE_MPS = 2.0           # the two speeds disagree by more than this ...
DISAGREE_SHARE = 0.15        # ... or this share of the GPS speed, whichever is more ...
DISAGREE_S = 3.0             # ... for this long: the speed is unusable ...
AGREE_S = 3.0                # ... until they agree again for this long


@dataclass
class DeviceReading:
  t: float          # seconds, monotonic
  speed: float      # m/s, unscaled
  ok: bool          # the estimate is valid: its filter runs, its inputs and the camera's motion look right


@dataclass
class GpsReading:
  t: float
  speed: float      # m/s
  ok: bool          # a fix, sure of its speed


class SpeedJudge:
  """The speed lane keeping uses, from the latest device and GPS readings. Plain logic, for the tests."""

  def __init__(self, scale: float = 1.0):
    self.scale = scale
    self.disagree = False
    self.since: float | None = None    # when the current run of (dis)agreement that would flip it started

  def update(self, now: float, device: DeviceReading | None, gps: GpsReading | None) -> tuple[float, bool]:
    if device is None or not device.ok or now - device.t > DEVICE_MAX_AGE_S:
      self.since = None
      return 0.0, False
    speed = device.speed * self.scale
    if gps is not None and gps.ok and now - gps.t <= GPS_MAX_AGE_S:
      off = abs(speed - gps.speed) > max(DISAGREE_MPS, DISAGREE_SHARE * gps.speed)
      if off != self.disagree:
        self.since = now if self.since is None else self.since
        if now - self.since >= (DISAGREE_S if off else AGREE_S):
          self.disagree, self.since = off, None
      else:
        self.since = None
    else:
      self.since = None    # nothing to compare with: the last verdict stands
    return speed, not self.disagree


def device_reading(t: float, dm) -> DeviceReading:
  """From a deviceMotion message."""
  v = dm.velocityDevice
  speed = math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z)
  return DeviceReading(t, speed, bool(v.valid and dm.inputsOK and dm.posenetOK and math.isfinite(speed)))


def gps_reading(t: float, g) -> GpsReading:
  """From a gpsLocation or gpsLocationExternal message."""
  return GpsReading(t, float(g.speed), bool(g.hasFix and 0 < g.speedAccuracy <= GPS_MAX_SPEED_ERROR))


class DeviceSpeed:
  """Reads deviceMotion and GPS for openpilot's card. update() returns (speed m/s, usable)."""

  def __init__(self, scale: float):
    import openpilot.cereal.messaging as messaging
    self.sm = messaging.SubMaster(['deviceMotion', 'gpsLocation', 'gpsLocationExternal'], ignore_alive=['gpsLocation', 'gpsLocationExternal'],
                                  ignore_valid=['gpsLocation', 'gpsLocationExternal'])
    self.judge = SpeedJudge(scale)
    self.device: DeviceReading | None = None
    self.gps: GpsReading | None = None

  def update(self) -> tuple[float, bool]:
    import time
    self.sm.update(0)
    now = time.monotonic()
    if self.sm.updated['deviceMotion']:
      self.device = device_reading(now, self.sm['deviceMotion'])
      self.device.ok = self.device.ok and self.sm.valid['deviceMotion']
    for which in ('gpsLocationExternal', 'gpsLocation'):
      if self.sm.updated[which]:
        self.gps = gps_reading(now, self.sm[which])
    return self.judge.update(now, self.device, self.gps)
