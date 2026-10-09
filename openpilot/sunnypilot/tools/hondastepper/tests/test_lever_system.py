"""
The lift lever as one system. The simulated car and motor, the panda's safety code (opendbc's test build of it) and
openpilot's car port, car events, MADS and state machines run together on one clock, in the order they run on the
comma device. The checks are what the driver sees and hears: lane keeping turns on about 2 s after the lift lever goes
down and off when it comes up, with only the engage and disengage sounds, also when the lever was already down as the
car started; the panda allows steering whenever openpilot steers; a motor gear off the steering wheel teeth is silent.
"""
import math
import unittest
from types import SimpleNamespace

from opendbc.car import gen_empty_fingerprint, structs
from opendbc.car.can_definitions import CanData
from opendbc.car.car_helpers import interfaces
from opendbc.car.hondastepper.tests.sim import SimCar, SimMotor
from opendbc.car.hondastepper.values import CAR, CanBus, StepperMode
from opendbc.safety.tests.libsafety import libsafety_py
from openpilot.cereal import custom, log
from openpilot.selfdrive.car.car_events import CarEvents
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.selfdrived.events import Events
from openpilot.selfdrive.selfdrived.state import StateMachine
from openpilot.sunnypilot.mads.helpers import MadsSteeringModeOnBrake, set_alternative_experience
from openpilot.sunnypilot.mads.mads import ModularAssistiveDrivingSystem
from openpilot.sunnypilot.selfdrive.car.car_specific import CarSpecificEventsSP
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP

SafetyModel = structs.CarParams.SafetyModel
MadsState = custom.ModularAssistiveDrivingSystem.ModularAssistiveDrivingSystemState
EventName = log.OnroadEvent.EventName
AudibleAlert = log.SelfdriveState.AudibleAlert
AlertSize = log.SelfdriveState.AlertSize
PLATFORM = CAR.HONDA_ACCORD_8G_STEPPER

DT = 0.01            # openpilot's step
CARD_OFFSET = 0.005  # where in each 10 ms the comma device takes its step
DRIVE_KPH = 90.0

try:
  libsafety_py.ffi.cdef("extern bool safety_rx_checks_invalid;")
except Exception:  # declared already by another test in this process
  pass

# what the installer sets (install_hondastepper.sh), the rest at sunnypilot's defaults
INSTALLED_PARAMS = {
  "Mads": True,
  "MadsMainCruiseAllowed": True,
  "MadsSteeringMode": MadsSteeringModeOnBrake.PAUSE,
  "MadsUnifiedEngagementMode": True,
  "DisengageOnAccelerator": False,
}


class FakeParams:
  def __init__(self, values):
    self.values = values

  def get_bool(self, key, *args, **kwargs):
    return bool(self.values.get(key, False))

  def get(self, key, *args, **kwargs):
    return self.values.get(key)


class Panda:
  """The panda's safety code on the simulated clock: ELM327 mode until openpilot has started up, then this car's mode,
  set the way pandad does it. Its once-a-second loop checks for lagging messages and for openpilot's heartbeat."""

  def __init__(self):
    self.lib = libsafety_py.libsafety
    self.lib.init_tests()
    self.lib.set_safety_hooks(SafetyModel.elm327, 1)
    self.mode = SafetyModel.elm327
    self.next_tick = 1.0
    self.heartbeat_mads = False

  def _timer(self, t: float):
    self.lib.set_timer(int(round(t * 1e6)))

  def set_car_mode(self, t: float, alternative_experience: int):
    self._timer(t)
    self.lib.set_alternative_experience(alternative_experience)
    self.lib.mads_apply_alternative_experience(alternative_experience)
    self.lib.set_safety_hooks(SafetyModel.hondaStepper, 0)
    self.mode = SafetyModel.hondaStepper

  def rx(self, t: float, frame: CanData):
    self._timer(t)
    self.lib.safety_rx_hook(libsafety_py.make_CANPacket(frame.address, frame.src, frame.dat))

  def tx(self, t: float, addr: int, dat: bytes, bus: int) -> bool:
    self._timer(t)
    return bool(self.lib.safety_tx_hook(libsafety_py.make_CANPacket(addr, bus, dat)))

  def tick(self, t: float):
    while t >= self.next_tick:
      self._timer(self.next_tick)
      self.lib.set_heartbeat_engaged_mads(self.heartbeat_mads)
      self.lib.mads_heartbeat_engaged_check()
      self.lib.safety_tick_current_safety_config()
      self.next_tick += 1.0

  def lateral_allowed(self) -> bool:
    return bool(self.lib.get_controls_allowed_lateral())

  def state(self):
    return SimpleNamespace(controlsAllowedLateral=self.lateral_allowed(), safetyModel=self.mode,
                           safetyRxChecksInvalid=bool(self.lib.safety_rx_checks_invalid))


class Selfdrive:
  """What MADS needs from selfdrived, with selfdrived's own steps that matter here."""

  def __init__(self, CP, CP_SP, params):
    self.CP, self.CP_SP, self.params = CP, CP_SP, params
    self.events = Events()
    self.events_sp = EventsSP()
    self.state_machine = StateMachine()
    self.enabled = False
    self.active = False
    self.enabled_prev = False
    self.initialized = False
    self.CS_prev = structs.CarState()
    self.sm = {"pandaStates": [], "carControl": structs.CarControl(), "controlsState": SimpleNamespace(curvature=0.0),
               "modelV2": planned_path(0.0)}


def planned_path(curvature: float, v: float = DRIVE_KPH / 3.6):
  """What the driving model plans, as the teeth chimes read it: one curvature from 1 s ahead on."""
  t_idxs = ModelConstants.T_IDXS
  z = [curvature * v if t >= 1.0 else 0.0 for t in t_idxs]
  return SimpleNamespace(orientationRate=SimpleNamespace(t=t_idxs, z=z), velocity=SimpleNamespace(t=t_idxs, x=[v] * len(t_idxs)))


class LeverSystem:
  def __init__(self, lever_down: bool = False, t_init: float = 0.5, pandad_delay: float = 0.05):
    self.t = 0.0
    self.t_init = t_init                       # selfdrived has started up; card starts sending
    self.t_car_mode = t_init + pandad_delay    # pandad puts the panda in this car's mode
    self.car = SimCar()
    self.car.state.update(VEHICLE_SPEED=DRIVE_KPH, GEAR="D")
    self.motor = SimMotor()
    if not lever_down:
      self.motor.lever(False)
    self.torque = lambda t: 0.3 * math.sin(2 * math.pi * t / 4.0)   # lane keeping's steering, -1..1

    CI = interfaces[PLATFORM]
    fingerprint = gen_empty_fingerprint()
    self.CP = CI.get_params(PLATFORM, fingerprint, [], False, False, False)
    self.CP_SP = CI.get_params_sp(self.CP, PLATFORM, fingerprint, [], False, False, False)
    self.params = FakeParams(INSTALLED_PARAMS)
    set_alternative_experience(self.CP, self.CP_SP, self.params)
    self.CI = CI(self.CP, self.CP_SP)
    self.sd = Selfdrive(self.CP, self.CP_SP, self.params)
    self.car_events = CarEvents(self.CP)
    self.car_events_sp = CarSpecificEventsSP(self.CP, self.CP_SP)
    self.mads = ModularAssistiveDrivingSystem(self.sd)
    self.panda = Panda()

    self.to_device: list[tuple[float, CanData]] = []   # frames on their way from the panda to openpilot
    self.stalled_until = -1.0
    self.CC_prev = structs.CarControl()
    self.nanos = 0
    self.next_card = CARD_OFFSET
    self.next_pandad = 0.0
    self.log: list[SimpleNamespace] = []

  # ***** what happens in each 1 ms *****

  def run(self, seconds: float):
    end = self.t + seconds
    while self.t < end - 1e-9:
      self.t = round(self.t + 0.001, 6)
      frames = [(ts, CanData(addr, dat, 0)) for ts, addr, dat in self.car.advance(self.t)]
      frames += [(ts, CanData(addr, dat, CanBus.SERVO)) for ts, addr, dat in self.motor.advance(self.t)]
      for ts, frame in sorted(frames, key=lambda f: f[0]):
        self.panda.rx(ts, frame)
        self.to_device.append((ts, frame))
      if self.panda.mode != SafetyModel.hondaStepper and self.t >= self.t_car_mode:
        self.panda.set_car_mode(self.t, self.CP.alternativeExperience)
      self.panda.tick(self.t)
      if self.t >= self.next_pandad:
        # pandad: the panda's state to openpilot and openpilot's heartbeat to the panda, 10 times a second
        self.sd.sm["pandaStates"] = [self.panda.state()]
        self.panda.heartbeat_mads = self.mads.enabled
        self.next_pandad = round(self.next_pandad + 0.1, 6)
      if self.t >= self.next_card:
        self.device_step()
        self.next_card = round(self.next_card + DT, 6)

  def device_step(self):
    t = self.t
    # card: the CAN that pandad passed on in the last 10 ms
    if t < self.stalled_until:
      batch = []
    else:
      frames = [f for ts, f in self.to_device if ts < t - 0.001]
      self.to_device = [(ts, f) for ts, f in self.to_device if ts >= t - 0.001]
      self.nanos = int(t * 1e9)
      batch = [(self.nanos, frames)]
    CS, _ = self.CI.update(batch)

    # selfdrived
    sd = self.sd
    sd.initialized = t >= self.t_init
    sd.events.clear()
    sd.events_sp.clear()
    if not sd.initialized:
      sd.events.add(EventName.selfdriveInitializing)
    else:
      if CS.canValid:
        sd.events.add_from_msg(self.car_events.update(CS, sd.CS_prev, self.CC_prev).to_msg())
        sd.sm["carControl"] = self.CC_prev
        sd.events_sp.add_from_msg(self.car_events_sp.update(CS, sd.events, sd.sm).to_msg())
        if CS.brakePressed and (not sd.CS_prev.brakePressed or not CS.standstill):
          sd.events.add(EventName.pedalPressed)
      for ps in sd.sm["pandaStates"]:
        safety_mismatch = ps.safetyModel != self.CP.safetyConfigs[0].safetyModel
        if (safety_mismatch and t > 10.0) or ps.safetyRxChecksInvalid:
          sd.events.add(EventName.controlsMismatch)
      sd.enabled, sd.active = sd.state_machine.update(sd.events)
    self.mads.update(CS)
    args = [self.CP, CS, sd.sm, False, sd.state_machine.soft_disable_timer, None]
    alerts = sd.events.create_alerts(sd.state_machine.current_alert_types, args) + \
             sd.events_sp.create_alerts(sd.state_machine.current_alert_types, args)
    sd.CS_prev = CS

    # controlsd
    CC = structs.CarControl()
    CC.enabled = sd.enabled
    standstill = abs(CS.vEgo) <= max(self.CP.minSteerSpeed, 0.3) or CS.standstill
    CC.latActive = self.mads.active and not CS.steerFaultTemporary and not CS.steerFaultPermanent and not standstill
    CC.actuators.torque = self.torque(t) if CC.latActive else 0.0
    self.CC_prev = CC

    # card sends once selfdrived has started up; the panda passes a command on or refuses it
    blocked_torque = []
    if sd.initialized:
      _, sends = self.CI.apply(CC.as_reader(), structs.CarControlSP(), self.nanos)
      for addr, dat, bus in sends:
        dat = bytes(dat)
        if self.panda.tx(t, addr, dat, bus):
          self.motor.command(t, dat)
          self.to_device.append((t, CanData(addr, dat, bus + 128)))
        elif dat[4] != 0:
          blocked_torque.append(dat[4])

    self.log.append(SimpleNamespace(
      t=t, mads=self.mads.state_machine.state, mads_enabled=self.mads.enabled, mads_active=self.mads.active,
      panda_lateral=self.panda.lateral_allowed(), lat_active=CC.latActive, blocked_torque=blocked_torque,
      motor_mode=self.motor.mode, soft_off=self.motor.soft_off, CS=CS,
      alerts=[a for a in alerts if a.audible_alert != AudibleAlert.none or a.alert_size != AlertSize.none],
      sounds={a.audible_alert for a in alerts if a.audible_alert != AudibleAlert.none}))

  # ***** reading the log *****

  def since(self, t0: float) -> list[SimpleNamespace]:
    return [r for r in self.log if r.t >= t0]

  def first(self, t0: float, cond) -> float | None:
    return next((r.t for r in self.since(t0) if cond(r)), None)


class TestLeverSystem(unittest.TestCase):
  def assertQuiet(self, rows, allowed_sounds=(), allowed_texts=()):
    """No alert on screen or sound, other than the given sounds and the alerts with the given texts."""
    for r in rows:
      for a in r.alerts:
        if a.alert_text_1 in allowed_texts:
          continue
        self.assertIn(a.audible_alert, allowed_sounds, (r.t, a.alert_type, a.alert_text_1, a.alert_text_2))
        self.assertEqual(a.alert_size, AlertSize.none, (r.t, a.alert_type, a.alert_text_1, a.alert_text_2))

  def assertInStep(self, rows):
    """openpilot never steers without the panda allowing it, and the panda refuses none of its steering."""
    out_of_step = [r.t for r in rows if r.mads_active and not r.panda_lateral]
    self.assertLessEqual(len(out_of_step), 1, out_of_step[:5])
    self.assertEqual([(r.t, r.blocked_torque) for r in rows if r.blocked_torque], [])
    self.assertFalse(any(r.soft_off for r in rows))

  def _engaged(self, s: LeverSystem, t_down: float) -> tuple[float, float]:
    t_panda = s.first(t_down, lambda r: r.panda_lateral)
    t_on = s.first(t_down, lambda r: r.mads == MadsState.enabled)
    self.assertIsNotNone(t_panda)
    self.assertIsNotNone(t_on)
    return t_panda, t_on

  def test_lever_down_turns_lane_keeping_on_and_up_turns_it_off(self):
    s = LeverSystem(lever_down=False)
    s.run(5.0)
    self.assertFalse(any(r.mads_enabled or r.panda_lateral for r in s.log))
    self.assertQuiet(s.log)

    s.motor.lever(True)
    s.run(4.0)
    t_panda, t_on = self._engaged(s, 5.0)
    # 2 s of messages from the running motor (it starts up in 0.05 s), the panda first, openpilot just after
    self.assertAlmostEqual(t_panda, 5.0 + s.motor.boot_s + 2.0, delta=0.03)
    self.assertGreaterEqual(t_on, t_panda)
    self.assertLess(t_on - t_panda, 0.06)
    on = s.since(t_on)
    self.assertTrue(all(r.mads == MadsState.enabled and r.panda_lateral for r in on))
    self.assertTrue(any(r.lat_active for r in on))
    self.assertEqual(s.motor.mode, StepperMode.TORQUE_CONTROL)   # steering
    self.assertQuiet(s.since(5.0), allowed_sounds=(AudibleAlert.engage,))
    self.assertEqual(sum(AudibleAlert.engage in r.sounds for r in s.log), 1)

    s.motor.lever(False)
    s.run(1.0)
    t_off = s.first(9.0, lambda r: not r.mads_enabled)
    self.assertLess(t_off - 9.0, 0.12)
    self.assertFalse(s.log[-1].panda_lateral)
    self.assertEqual(sum(AudibleAlert.disengage in r.sounds for r in s.since(9.0)), 1)
    self.assertQuiet(s.since(9.0), allowed_sounds=(AudibleAlert.disengage,))
    self.assertInStep(s.log)

    # and again: down, on 2 s later
    s.motor.lever(True)
    s.run(2.5)
    t_panda, t_on = self._engaged(s, 10.0)
    self.assertAlmostEqual(t_on, 10.0 + s.motor.boot_s + 2.0, delta=0.08)
    self.assertInStep(s.log)

  def test_lever_already_down_as_the_car_starts(self):
    # the motor runs from the start; selfdrived starts up at different times, and pandad puts the panda in this
    # car's mode 50 ms later. Lane keeping turns on 2 s after that, by itself, without any other alert.
    for t_init in (0.3, 1.0, 1.9, 2.5, 4.0, 6.0):
      with self.subTest(t_init=t_init):
        s = LeverSystem(lever_down=True, t_init=t_init)
        s.run(t_init + 4.0)
        t_panda, t_on = self._engaged(s, 0.0)
        self.assertAlmostEqual(t_panda, s.t_car_mode + 2.0, delta=0.03)
        self.assertGreaterEqual(t_on, t_panda)
        self.assertLess(t_on - t_panda, 0.06)
        self.assertTrue(all(r.mads == MadsState.enabled for r in s.since(t_on)))
        self.assertQuiet(s.log, allowed_sounds=(AudibleAlert.engage,))
        self.assertEqual(sum(AudibleAlert.engage in r.sounds for r in s.log), 1)
        self.assertInStep(s.log)

  def test_motor_gear_off_the_teeth_chimes_once(self):
    s = LeverSystem(lever_down=True)
    s.run(3.0)
    _, t_on = self._engaged(s, 0.0)
    s.torque = lambda t: 0.3        # lane keeping pushes left, as in a long left curve
    s.run(0.5)
    # the driver turns the wheel left past the end of the steering wheel teeth: the motor gear comes off them
    s.motor.turn_wheel(s.motor.teeth_center_deg + 50.0)
    s.run(3.0)
    held = [r for r in s.since(4.0) if r.mads == MadsState.overriding]
    self.assertTrue(held)
    self.assertEqual(s.motor.mode, StepperMode.OFF)
    spun = s.motor.free_spin_deg
    self.assertGreater(spun, 0.0)
    # one chime, "past the teeth", when the gear came off; no other alert
    chimes = [r for r in s.since(t_on + DT / 2) if r.alerts]
    self.assertTrue(chimes)
    self.assertTrue(all(a.alert_text_1 == "Past the teeth: steer yourself" for r in chimes for a in r.alerts))
    self.assertLess(chimes[0].t - held[0].t, 0.05)
    self.assertAlmostEqual(chimes[-1].t - chimes[0].t, 2.0, delta=0.05)
    self.assertQuiet(s.since(t_on + DT / 2), allowed_sounds=(AudibleAlert.prompt,), allowed_texts=("Past the teeth: steer yourself",))
    # back to straight: the teeth turn the motor again, and lane keeping steers again 1 s later
    s.motor.turn_wheel(s.motor.teeth_center_deg)
    s.run(2.0)
    self.assertEqual(s.log[-1].mads, MadsState.enabled)
    self.assertEqual(s.motor.mode, StepperMode.TORQUE_CONTROL)
    self.assertEqual(s.motor.free_spin_deg, spun)
    self.assertTrue(all(r.mads_enabled and r.panda_lateral for r in s.since(t_on)))
    self.assertQuiet(s.since(chimes[-1].t + DT / 2))
    self.assertInStep(s.log)

  def test_curve_ahead_past_the_teeth_chimes(self):
    s = LeverSystem(lever_down=True)
    s.run(3.0)
    _, t_on = self._engaged(s, 0.0)
    self.assertQuiet(s.since(t_on + DT / 2))
    # the driving model plans a curve 1 s ahead that needs about 40 degrees of steering wheel: past the long teeth
    VM = s.car_events_sp.hondastepper.VM
    s.sd.sm["modelV2"] = planned_path(VM.calc_curvature(math.radians(40.0), DRIVE_KPH / 3.6, 0.0))
    s.run(3.5)
    chimes = [r for r in s.since(3.0) if r.alerts]
    self.assertTrue(chimes)
    self.assertLess(chimes[0].t - 3.0, 0.05)
    self.assertAlmostEqual(chimes[-1].t - chimes[0].t, 3.0, delta=0.05)   # shows for 3 s, then quiet for a while
    self.assertTrue(all(a.alert_text_1 == "Steer: the curve ahead is past the teeth" for r in chimes for a in r.alerts))
    self.assertIn(AudibleAlert.prompt, chimes[0].sounds)
    self.assertTrue(all(r.mads_enabled and r.lat_active for r in s.since(3.0)))   # the chime changes nothing else
    # a gentler curve, 20 degrees: within the long teeth, quiet
    s.sd.sm["modelV2"] = planned_path(VM.calc_curvature(math.radians(20.0), DRIVE_KPH / 3.6, 0.0))
    s.run(12.0)
    self.assertQuiet(s.since(chimes[-1].t + DT / 2))

  def test_brake_pauses_lane_keeping_quietly(self):
    # Steering Mode on Brake Pedal: Pause
    s = LeverSystem(lever_down=True)
    s.run(3.0)
    _, t_on = self._engaged(s, 0.0)
    s.car.state["BRAKE_PRESSED"] = 1
    s.run(1.0)
    self.assertEqual(s.log[-1].mads, MadsState.paused)
    self.assertFalse(s.log[-1].panda_lateral)
    s.car.state["BRAKE_PRESSED"] = 0
    s.run(1.0)
    self.assertEqual(s.log[-1].mads, MadsState.enabled)
    self.assertTrue(s.log[-1].panda_lateral)
    self.assertQuiet(s.since(t_on + DT / 2))
    self.assertInStep(s.log)

  def test_motor_restart_turns_lane_keeping_off_and_on(self):
    # the motor loses power for 30 ms (a loose plug): it restarts, both sides turn lane keeping off together and on
    # again once it has run for 2 s
    s = LeverSystem(lever_down=True)
    s.run(3.0)
    s.motor.lever(False)
    s.run(0.03)
    s.motor.lever(True)
    s.run(3.0)
    t_off = s.first(3.0, lambda r: not r.mads_enabled)
    t_panda_off = s.first(3.0, lambda r: not r.panda_lateral)
    self.assertLess(abs(t_off - t_panda_off), 0.03)
    t_panda, t_on = self._engaged(s, t_off)
    self.assertLess(t_on - t_panda, 0.06)
    self.assertEqual(sum(AudibleAlert.disengage in r.sounds for r in s.since(3.0)), 1)
    self.assertQuiet(s.since(3.0), allowed_sounds=(AudibleAlert.engage, AudibleAlert.disengage))
    self.assertInStep(s.log)

  def test_a_hold_up_in_openpilot_changes_nothing(self):
    # no messages reach openpilot for 0.3 s, then they all come at once
    s = LeverSystem(lever_down=True)
    s.run(3.0)
    _, t_on = self._engaged(s, 0.0)
    s.stalled_until = s.t + 0.3
    s.run(1.0)
    self.assertTrue(all(r.mads == MadsState.enabled and r.panda_lateral for r in s.since(t_on)))
    self.assertQuiet(s.since(t_on + DT / 2))


if __name__ == "__main__":
  unittest.main()
