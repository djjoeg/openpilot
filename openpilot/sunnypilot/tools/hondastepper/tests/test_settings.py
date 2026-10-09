"""
The settings the hondastepper car needs are made at every start, whatever was set before, and only those.
"""
import os
import unittest

from openpilot.sunnypilot.tools.hondastepper import settings

OPENDBC_CAR_LIST = os.path.join(os.path.dirname(__import__("opendbc").__file__), "sunnypilot", "car", "car_list.json")


class FakeParams:
  def __init__(self, values=None):
    self.values = dict(values or {})
    self.writes = 0

  def get(self, key):
    return self.values.get(key)

  def get_bool(self, key):
    return bool(self.values.get(key, False))

  def put(self, key, value, block=False):
    self.values[key] = value
    self.writes += 1

  def put_bool(self, key, value, block=False):
    self.put(key, bool(value))


class TestSettings(unittest.TestCase):
  def test_fresh_install(self):
    p = FakeParams()
    changed = settings.apply(p, OPENDBC_CAR_LIST)
    bundle = p.values["CarPlatformBundle"]
    self.assertEqual(bundle["platform"], "HONDA_ACCORD_8G_STEPPER")
    self.assertEqual(bundle["name"], "Honda Accord 2008-12")
    self.assertTrue(p.values["Mads"])
    self.assertTrue(p.values["MadsMainCruiseAllowed"])
    self.assertEqual(p.values["MadsSteeringMode"], 1)               # pause while the brake is pressed
    self.assertFalse(p.get_bool("NeuralNetworkLateralControl"))
    self.assertEqual(p.values["AutoLaneChangeTimer"], -1)           # off
    self.assertEqual(p.values["BlinkerPauseLateralControl"], 1)
    self.assertEqual(p.values["BlinkerMinLateralControlSpeed"], 255)
    self.assertIn("CarPlatformBundle", changed)
    # updates are left alone: the device follows its own GitHub branch
    self.assertNotIn("DisableUpdates", p.values)

  def test_changed_in_a_menu_is_put_back_and_nothing_else_is_touched(self):
    p = FakeParams()
    settings.apply(p, OPENDBC_CAR_LIST)
    p.values.update({"BlinkerPauseLateralControl": 0, "Mads": False, "AutoLaneChangeTimer": 1, "IsMetric": True})
    changed = settings.apply(p, OPENDBC_CAR_LIST)
    self.assertEqual(sorted(changed), ["AutoLaneChangeTimer", "BlinkerPauseLateralControl", "Mads"])
    self.assertEqual(p.values["BlinkerPauseLateralControl"], 1)
    self.assertTrue(p.values["IsMetric"])

  def test_nothing_written_when_already_set(self):
    p = FakeParams()
    settings.apply(p, OPENDBC_CAR_LIST)
    writes = p.writes
    self.assertEqual(settings.apply(p, OPENDBC_CAR_LIST), [])
    self.assertEqual(p.writes, writes)

  def test_real_params(self):
    try:
      from openpilot.common.params import Params
      p = Params()
    except Exception as e:  # the params library isn't built here
      self.skipTest(f"no params library: {e}")
    for key in ("CarPlatformBundle", *settings.FIXED):
      p.remove(key)
    settings.apply(p, OPENDBC_CAR_LIST)
    self.assertEqual(p.get("CarPlatformBundle")["platform"], "HONDA_ACCORD_8G_STEPPER")
    self.assertEqual(p.get("MadsSteeringMode"), 1)
    self.assertEqual(p.get("AutoLaneChangeTimer"), -1)
    self.assertTrue(p.get_bool("MadsMainCruiseAllowed"))
    self.assertEqual(settings.apply(p, OPENDBC_CAR_LIST), [])


if __name__ == "__main__":
  unittest.main()
