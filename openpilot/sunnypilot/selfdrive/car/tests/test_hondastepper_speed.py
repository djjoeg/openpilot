"""
The hondastepper stand-alone speed: the comma device's own, checked against GPS while driving.
"""
import unittest
from unittest import mock

from openpilot.cereal import log
from openpilot.sunnypilot.selfdrive.car import hondastepper_speed
from openpilot.sunnypilot.selfdrive.car.hondastepper_speed import (AGREE_S, DEVICE_MAX_AGE_S, DISAGREE_S, DeviceReading, GpsReading, SpeedJudge,
                                                                   device_reading, gps_reading)

DT = 0.05


def run(judge: SpeedJudge, t0: float, seconds: float, device_speed: float, gps_speed: float | None, gps_ok: bool = True):
  """Device readings 20 times a second, GPS once a second (when given). Returns (t, speed, usable) per reading."""
  out = []
  gps = None
  t = t0
  while t < t0 + seconds - 1e-9:
    if gps_speed is not None and round(t * 20) % 20 == 0:
      gps = GpsReading(t, gps_speed, gps_ok)
    speed, ok = judge.update(t, DeviceReading(t, device_speed, True), gps)
    out.append((t, speed, ok))
    t = round(t + DT, 6)
  return out


class TestSpeedJudge(unittest.TestCase):
  def test_device_speed_scaled(self):
    judge = SpeedJudge(scale=1.05)
    out = run(judge, 0.0, 2.0, 20.0, None)
    self.assertAlmostEqual(out[-1][1], 21.0)
    self.assertTrue(all(ok for _, _, ok in out))

  def test_device_not_ready_or_stale(self):
    judge = SpeedJudge()
    self.assertEqual(judge.update(1.0, None, None), (0.0, False))
    self.assertEqual(judge.update(1.0, DeviceReading(1.0, 20.0, False), None), (0.0, False))
    self.assertEqual(judge.update(1.0 + DEVICE_MAX_AGE_S + 0.01, DeviceReading(1.0, 20.0, True), None), (0.0, False))

  def test_gps_disagreeing_for_a_while_stops_steering(self):
    judge = SpeedJudge()
    out = run(judge, 0.0, 5.0, 20.0, 20.5)
    self.assertTrue(all(ok for _, _, ok in out))
    # a short disagreement (a GPS glitch) changes nothing
    out = run(judge, 5.0, DISAGREE_S - 0.5, 20.0, 28.0)
    self.assertTrue(all(ok for _, _, ok in out))
    out = run(judge, 5.0 + DISAGREE_S - 0.5, 1.0, 20.0, 20.0)
    self.assertTrue(all(ok for _, _, ok in out))
    # a lasting one: unusable after DISAGREE_S, usable again after AGREE_S of agreement
    out = run(judge, 10.0, DISAGREE_S + 1.0, 20.0, 28.0)
    first_bad = next(t for t, _, ok in out if not ok)
    self.assertAlmostEqual(first_bad - 10.0, DISAGREE_S, delta=1.05)
    out = run(judge, 20.0, AGREE_S + 1.5, 20.0, 20.0)
    first_good = next(t for t, _, ok in out if ok)
    self.assertAlmostEqual(first_good - 20.0, AGREE_S, delta=1.05)

  def test_slow_or_unsure_gps_is_not_compared(self):
    judge = SpeedJudge()
    out = run(judge, 0.0, 10.0, 3.0, 4.5)            # within 2 m/s at low speed
    self.assertTrue(all(ok for _, _, ok in out))
    out = run(judge, 10.0, 10.0, 20.0, 30.0, gps_ok=False)
    self.assertTrue(all(ok for _, _, ok in out))
    # GPS gone (a tunnel): the last verdict stands, the device's own speed is used
    out = run(judge, 20.0, 10.0, 20.0, None)
    self.assertTrue(all(ok for _, _, ok in out))

  def test_readings_from_messages(self):
    dm = log.DeviceMotion.new_message(inputsOK=True, posenetOK=True)
    dm.velocityDevice.x, dm.velocityDevice.y, dm.velocityDevice.z, dm.velocityDevice.valid = 19.9, 0.5, -1.2, True
    r = device_reading(3.0, dm)
    self.assertTrue(r.ok)
    self.assertAlmostEqual(r.speed, (19.9 ** 2 + 0.5 ** 2 + 1.2 ** 2) ** 0.5, places=4)
    dm.posenetOK = False
    self.assertFalse(device_reading(3.0, dm).ok)
    g = log.GpsLocationData.new_message(speed=20.0, hasFix=True, speedAccuracy=0.4)
    self.assertTrue(gps_reading(3.0, g).ok)
    g.speedAccuracy = 2.0
    self.assertFalse(gps_reading(3.0, g).ok)


class FakeSubMaster:
  """What card's speed reader sees of openpilot's messages."""
  def __init__(self, services, **_kw):
    self.msgs = dict.fromkeys(services)
    self.updated = dict.fromkeys(services, False)
    self.valid = dict.fromkeys(services, True)
    self.pending = {}

  def update(self, _timeout):
    self.updated = {s: s in self.pending for s in self.msgs}
    self.msgs.update(self.pending)
    self.pending = {}

  def __getitem__(self, key):
    return self.msgs[key]


class TestDeviceSpeed(unittest.TestCase):
  def test_reads_device_motion_and_gps(self):
    import openpilot.cereal.messaging as messaging
    with mock.patch.object(messaging, "SubMaster", FakeSubMaster):
      ds = hondastepper_speed.DeviceSpeed(scale=0.98)
    self.assertEqual(ds.update(), (0.0, False))          # nothing yet
    dm = log.DeviceMotion.new_message(inputsOK=True, posenetOK=True)
    dm.velocityDevice.x, dm.velocityDevice.valid = 25.0, True
    ds.sm.pending = {"deviceMotion": dm, "gpsLocationExternal": log.GpsLocationData.new_message(speed=24.6, hasFix=True, speedAccuracy=0.3)}
    speed, ok = ds.update()
    self.assertAlmostEqual(speed, 24.5, places=3)
    self.assertTrue(ok)
    ds.sm.valid["deviceMotion"] = False                  # locationd's filter not valid
    ds.sm.pending = {"deviceMotion": dm}
    self.assertFalse(ds.update()[1])


if __name__ == "__main__":
  unittest.main()
