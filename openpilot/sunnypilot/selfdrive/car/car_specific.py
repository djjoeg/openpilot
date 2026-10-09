"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.cereal import log, custom
from opendbc.car import structs

from opendbc.car.chrysler.values import RAM_DT
from openpilot.selfdrive.selfdrived.events import Events
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP

EventName = log.OnroadEvent.EventName
EventNameSP = custom.OnroadEventSP.EventName
GearShifter = structs.CarState.GearShifter


class CarSpecificEventsSP:
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP):
    self.CP = CP
    self.CP_SP = CP_SP

    self.low_speed_alert = False
    self.hondastepper = None
    if self.CP.brand == 'hondastepper':
      from opendbc.car.hondastepper.values import CONFIG
      from openpilot.sunnypilot.selfdrive.car.hondastepper_alerts import TeethAlerts
      self.hondastepper = TeethAlerts(self.CP, CONFIG.actuator.full_push_reach_deg)

  def update(self, CS: structs.CarState, events: Events, sm=None):
    """sm: selfdrived's messages (carControl, controlsState, modelV2), for the cars whose alerts need them."""
    events_sp = EventsSP()

    if self.CP.brand == 'chrysler':
      if self.CP.carFingerprint in RAM_DT:
        # remove belowSteerSpeed event from CarSpecificEvents as RAM_DT uses a different logic
        if events.has(EventName.belowSteerSpeed):
          events.remove(EventName.belowSteerSpeed)

        # TODO-SP: use if/elif to have the gear shifter condition takes precedence over the speed condition
        # TODO-SP: add 1 m/s hysteresis
        if CS.vEgo >= self.CP.minEnableSpeed:
          self.low_speed_alert = False
        if self.CP.minEnableSpeed >= 14.5 and CS.gearShifter != GearShifter.drive:
          self.low_speed_alert = True
      if self.low_speed_alert:
        events.add(EventName.belowSteerSpeed)

    elif self.CP.brand == 'toyota':
      if self.CP.openpilotLongitudinalControl:
        if CS.cruiseState.standstill and not CS.brakePressed and self.CP_SP.enableGasInterceptor:
          if events.has(EventName.resumeRequired):
            events.remove(EventName.resumeRequired)

    elif self.hondastepper is not None and sm is not None:
      # the add-on steering motor only pushes as far as the printed steering wheel teeth reach
      curve_ahead, past_teeth = self.hondastepper.update(CS, sm)
      if curve_ahead:
        events_sp.add(EventNameSP.hondastepperCurveAhead)
      if past_teeth:
        events_sp.add(EventNameSP.hondastepperPastTeeth)

    return events_sp
