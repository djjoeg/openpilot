"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The settings the Honda Accord with the add-on steering motor (hondastepper) needs. The manager makes them every time
sunnypilot starts, before anything else runs, so an install straight from GitHub needs no laptop, and a setting
changed in a menu can't switch off something the lift lever relies on. Only these settings are touched.
"""
import json
import os

from openpilot.common.basedir import BASEDIR

CAR_NAME = "Honda Accord 2008-12"
CAR_LIST = os.path.join(BASEDIR, "openpilot", "sunnypilot", "selfdrive", "car", "car_list.json")

# key: (value, where a comma 3X shows it)
FIXED = {
  "Mads": (True, "Steering > Modular Assistive Driving System: on"),
  # the lift lever switches the motor's power, and the car port reports that as the main switch
  "MadsMainCruiseAllowed": (True, "Customize MADS > Toggle with Main Cruise: on"),
  "MadsSteeringMode": (1, "Customize MADS > Steering Mode on Brake Pedal: Pause"),
  "NeuralNetworkLateralControl": (False, "Steering > Neural Network Lateral Control: off"),
  "AutoLaneChangeTimer": (-1, "Customize Lane Change > Auto Lane Change by Blinker: Off"),
  "BlinkerPauseLateralControl": (1, "Pause Lateral Control with Blinker: on"),
  "BlinkerMinLateralControlSpeed": (255, "Minimum Speed to Pause Lateral Control: its highest value, so at every speed"),
}


def car_bundle(car_list: str = CAR_LIST) -> dict:
  """The vehicle the way choosing it under Settings > Vehicle saves it."""
  with open(car_list) as f:
    return {**json.load(f)[CAR_NAME], "name": CAR_NAME}


def apply(params, car_list: str = CAR_LIST) -> list[str]:
  """Makes the settings; returns the keys it had to change."""
  changed = []
  bundle = car_bundle(car_list)
  if params.get("CarPlatformBundle") != bundle:
    params.put("CarPlatformBundle", bundle, block=True)
    changed.append("CarPlatformBundle")
  for key, (value, _) in FIXED.items():
    if isinstance(value, bool):
      if params.get_bool(key) != value:
        params.put_bool(key, value, block=True)
        changed.append(key)
    elif params.get(key) != value:
      params.put(key, value, block=True)
      changed.append(key)
  return changed
