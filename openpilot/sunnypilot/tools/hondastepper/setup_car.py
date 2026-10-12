#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Car setup for the Honda Accord with the add-on steering motor (hondastepper), part 1 of 2: parked.

Run it from a phone on the comma device's hotspot (the setup page, phone.py: Part 1), or on the comma device over
SSH, with the car parked, the engine running and the steering wheel straight:

  /data/openpilot/accord_setup.sh car

It stops openpilot, then asks you to do simple things one at a time while it watches the motor (and, connected to
the car's network with car_network, the car's data: press the brake, switch a blinker on, shift gears; it checks
where the car keeps everything lane keeping needs and finds it when it's somewhere else). It checks which way the
motor turns from two turns of the steering wheel, checks with the
steering wheel held that the motor's hardest push can't make its gear slip over the steering wheel teeth, saves the
result to /data/hondastepper/config.json, and restarts the comma device, which rebuilds the software with it.

Part 2 is the drive check (Part 2 on the setup page, or accord_setup.sh drive) after a few minutes of driving. Lane
keeping stays off until both parts pass.
"""
import dataclasses
import datetime
import math
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass, field

from opendbc.car.hondastepper import discovery as dsc
from opendbc.car.hondastepper.config import (MECHANICAL_RATIOS, NO_ROLLER_ARCS, ROLL_PAST_TEETH_DEG, TEETH_SETS, load_raw_config,
                                             parse_config, save_device_config, device_config_path)
from opendbc.car.hondastepper.values import StepperControlStatus, StepperMode
from openpilot.sunnypilot.tools.hondastepper import VERSION
from openpilot.sunnypilot.tools.hondastepper.device import CanSession
from openpilot.sunnypilot.tools.hondastepper.prompter import Prompter

INTRO_STANDALONE = f"""
Honda Accord lane keeping, software {VERSION}: car setup, part 1 of 2 (parked)

This takes about 5 minutes. It asks you to do one simple thing at a time: turn or hold the steering wheel, and say
which way it turned. Do it, then press Enter. At the end it saves what it learned and restarts the comma device.

Before you start: car parked somewhere safe, engine running, steering wheel straight. It tells you when to switch
the motor on.
"""

INTRO = f"""
Honda Accord lane keeping, software {VERSION}: car setup, part 1 of 2 (parked)

This takes about 10 minutes. It asks you to do one simple thing at a time: press a pedal, switch a turn signal,
move the shifter, turn or hold the steering wheel. Do it, press Enter, and hold it for 3 seconds while it watches.
At the end it saves what it learned and restarts the comma device.

Before you start: car parked somewhere safe, engine running, steering wheel straight. It tells you when to switch
the motor on.
"""

MSG_MORE_GEARS = " ".join((
  "If the shifter goes further than D (like D3, 2 or 1), move it one more step and type what the dash shows",
  "(for example D3), then press Enter. If it doesn't go further, just press Enter.",
))
MSG_MORE_GEARS_PHONE = " ".join((
  "If the shifter goes further than D (like D3, 2 or 1), move it one more step and type what the dash shows",
  "(for example D3). If it doesn't go further, tap the button.",
))
MSG_PUSH = " ".join((
  "Turn the wheel back to straight, so the motor gear is in the middle of the teeth, and let go of the wheel completely.",
  "Watch the top of the steering wheel: the motor will turn it a little by itself, then let go.",
))
MSG_DID_IT_TURN_LEFT = " ".join((
  "Did the steering wheel just turn LEFT by itself (the top of the wheel moved towards the driver's door)?",
  "Type y or n and press Enter:",
))
MSG_DID_IT_TURN_LEFT_PHONE = "Did the steering wheel just turn LEFT by itself (the top of the wheel moved towards the driver's door)?"
MSG_TRY_OTHER_WAY = " ".join((
  "Then the motor's direction is the other way round (perhaps the wheel was turned right first a moment ago).",
  "Trying the other way.",
))
MSG_NEVER_LEFT = " ".join((
  "the motor turned the steering wheel both times, the second time the other way, but you didn't see it go left",
  "either time, so its direction couldn't be settled. Run this again and watch the top of the steering wheel during",
  "each push: one of the two pushes turns it left",
))
MSG_LEVER_DOWN = " ".join((
  "Steering wheel straight. Switch the motor on with its gear on the middle of the steering wheel teeth: pull the",
  "lift lever down until it clicks, or on the side-slide mount, pull its lever out along the slot and then towards you",
  "into the notch. Hands off the steering wheel.",
))
MSG_NO_MOTOR = " ".join((
  "No answer from the motor. Check that it is switched on (the lift lever all the way down, or the side-slide",
  "mount's lever all the way out and in its notch) and that the motor's cable is plugged in.",
))
MSG_WHICH_TEETH = " ".join((
  "Which steering wheel teeth are on the steering wheel: short ones (the short teeth, a ring of teeth, the short back",
  "teeth or the side-slide mount's teeth: they reach 15 degrees each way), the long ones (29 degrees each way), or the",
  "long back teeth (45 degrees each way)? Type 15, 29 or 45 and press Enter:",
))
MSG_WHICH_TEETH_PHONE = " ".join((
  "Which steering wheel teeth are on the steering wheel: short ones (the short teeth, a ring of teeth, the short back",
  "teeth or the side-slide mount's teeth: they reach 15 degrees each way), the long ones (29 degrees each way), or the",
  "long back teeth (45 degrees each way)?",
))
TEETH_CHOICES = (("15", "Short teeth (15)"), ("29", "Long teeth (29)"), ("45", "Long back teeth (45)"))
TEETH_NAMES = {15: "short ones", 29: "long ones", 45: "long back teeth"}
MSG_TURN_LEFT = " ".join((
  "Next, you turn the steering wheel LEFT, slowly, taking about 5 seconds, until the motor gear has run off the end of",
  "the steering wheel teeth and stopped turning (a sixteenth of a turn with the short teeth, an eighth with the long",
  "ones, a sixth with the long back teeth). Then hold the wheel still there. It records while you turn, and carries on by",
  "itself once the wheel has been still for a moment. Press Enter, then turn.",
))
MSG_TURN_LEFT_PHONE = " ".join((
  "Next, you turn the steering wheel LEFT, slowly, taking about 5 seconds, until the motor gear has run off the end of",
  "the steering wheel teeth and stopped turning (a sixteenth of a turn with the short teeth, an eighth with the long",
  "ones, a sixth with the long back teeth). Then hold the wheel still there. It records while you turn, and carries on by",
  "itself once the wheel has been still for a moment. Press the button, then turn.",
))
MSG_TURN_RIGHT = " ".join((
  "Now the same to the RIGHT: slowly, past the middle, until the motor gear has run off the other end of the teeth and",
  "stopped turning, then hold the wheel still. Press Enter, then turn.",
))
MSG_TURN_RIGHT_PHONE = " ".join((
  "Now the same to the RIGHT: slowly, past the middle, until the motor gear has run off the other end of the teeth and",
  "stopped turning, then hold the wheel still. Press the button, then turn.",
))
MSG_PART1_PASSED = " ".join((
  "Part 1 passed. Next: drive for at least 5 minutes with the motor switched ON (the lift lever down, or the side-slide",
  "mount latched out; lane keeping stays off until both parts pass, so the motor only rides along), at a mix of speeds",
  "between about 15 and 50 mph, with some curves or lane",
  "changes, where the comma device can see the sky. Then run part 2, the drive check (Part 2 on the setup page, or",
  "/data/openpilot/accord_setup.sh drive over SSH).",
))

MSG_GRIP = " ".join((
  "Grip test. Keep the motor switched on. Start it, then within 3 seconds hold the steering wheel firmly with",
  "both hands at 9 and 3 o'clock, so it can't turn. The motor then pushes as hard as it can, about 2 seconds one way,",
  "then the other (about as hard as 3 kg pulling on the edge of the steering wheel). Keep holding until it has",
  "stopped pushing both ways, about 8 seconds after you start. Nothing should click or jump.",
))
MSG_GRIP_HOLD = "Hold the steering wheel now: the motor starts pushing in 3 seconds."
MSG_GRIP_DONE = "You can let go of the steering wheel."
MSG_GRIP_TRY_AGAIN = " ".join((
  "The steering wheel moved during the grip test: it turned in your hands, or the steering wheel teeth slid on the",
  "steering wheel. Check that their zip ties are tight, hold the wheel firmly, and it tries once more.",
))
MSG_GRIP_SLIPPED = " ".join((
  "the motor gear slipped over the steering wheel teeth. Check that the motor is switched on and sits right (the lift",
  "lever clicked down with its spring in place, or the side-slide mount latched out), and that neither the motor gear's",
  "teeth nor the steering wheel teeth are worn or broken, then run the car setup again. If it slips again on a lift",
  "lever mount, put an M5 washer under the spring (see the build guide); on the side-slide mount, check that the back",
  "of the steering wheel doesn't move away from the motor as the wheel turns",
))
MSG_GRIP_MOVED = " ".join((
  "the steering wheel moved during the grip test both times: it turned in your hands, or the steering wheel teeth",
  "slide on the steering wheel (tighten their zip ties)",
))

RECORD_SECONDS = 3.0
SETTLE_SECONDS = 0.5     # the start of each recording is ignored while things settle
PUSH_NM = 3.0            # the push that shows the motor's direction: about 3 Nm at the steering wheel
PUSH_STOP_DEG = 6.0      # the push lets go once the steering wheel has turned this far
# Grip test: with the steering wheel held still, the motor pushes as hard as its controller board can (3.3 A, the
# StepperServoCAN firmware's I_MAX_A4950), which is more than lane keeping ever asks for. If its gear doesn't slip over
# the steering wheel teeth there, the motor can't make it slip at all.
BOARD_MAX_A = 3.3
TURN_MAX_S = 25.0        # a turn recording ends by itself once the motor has moved and then been still ...
TURN_STILL_S = 1.5       # ... this long, or after this many seconds in all
TURN_MOVED_FW_DEG = 2.0  # the motor counting this far from where it started counts as the wheel turning it
GRIP_RAMP_S, GRIP_HOLD_S = 0.5, 1.0
GRIP_COUNTDOWN_S = 3.0   # time to put the phone or laptop down and take hold of the steering wheel
GRIP_SLIP_DEG = 1.0      # the motor's angle jumping this far between two commands (20 ms) is its gear slipping over a
                         # tooth (one tooth is 1.8 degrees of steering wheel turn); a hand gives way much more slowly
GRIP_STOP_DEG = 3.0      # the push stops once the steering wheel has turned this far in your hands


@dataclass
class ParkedResult:
  findings: list[dsc.Finding] = field(default_factory=list)
  stats: dict = field(default_factory=dict)
  fingerprint: dict = field(default_factory=dict)
  motor: dsc.MotorCheck | None = None
  push: dsc.MotorCheck | None = None
  grip: dsc.MotorCheck | None = None
  teeth: int | None = None     # which steering wheel teeth are on: 15, 29 or 45 (TEETH_SETS)
  arc: float = 0.0             # the steering wheel turn the motor followed on them, as designed (TEETH_SETS, NO_ROLLER_ARCS)
  roll_past: float = ROLL_PAST_TEETH_DEG   # each side of it, the rolling band past the last tooth: 0 without a roller
  notes: list[str] = field(default_factory=list)
  rest: list = field(default_factory=list)   # the first recording: wheel straight, nothing pressed


def teeth_arc(teeth: int, span_deg: float) -> tuple[float, float]:
  """(tracked arc, rolling band each side) for the answered teeth: with a roller on the motor gear (TEETH_SETS), or
  without one (NO_ROLLER_ARCS), whichever the turn the motor followed (span_deg) is nearer."""
  arcs = [(TEETH_SETS[teeth], ROLL_PAST_TEETH_DEG)]
  if teeth in NO_ROLLER_ARCS:
    arcs.append((NO_ROLLER_ARCS[teeth], 0.0))
  return min(arcs, key=lambda a: abs(span_deg / a[0] - 1.0))


class CarSetup:
  def __init__(self, session: CanSession, prompter: Prompter, raw_config: dict):
    self.session = session
    self.p = prompter
    self.raw = raw_config
    self.cfg = parse_config(raw_config)
    self.frames: list[dsc.Frame] = []
    self.recorded_seconds = 0.0

  # ***** recording *****

  def _hold_motor_off(self, _t: float):
    return StepperMode.OFF, 0.0

  def record(self, text: str) -> list[dsc.Frame]:
    """Asks for something, then records the car's data for a few seconds."""
    self.p.step(text)
    self.session.drain()
    frames = self.session.run(RECORD_SECONDS, self._hold_motor_off)
    self.frames += frames
    self.recorded_seconds += RECORD_SECONDS
    if not frames:
      return []
    start = frames[0][0] + SETTLE_SECONDS
    return [f for f in frames if f[0] >= start]

  def twice(self, on_text: str, off_text: str) -> tuple[list, list]:
    """The action done twice, with a recording of each state. Returns (off windows, on windows)."""
    off, on = [], []
    for _ in range(2):
      on.append(self.record(on_text))
      off.append(self.record(off_text))
    return off, on

  # ***** the car's data *****

  def check_car_data(self) -> bool:
    self.session.drain()
    frames = self.session.run(1.0, self._hold_motor_off)
    if len(frames) < 50:
      self.p.say("No data from the car. Check the harness connection at the OBD port, and that the engine is running.")
      return False
    return True

  def parked_checks(self, manual: bool) -> ParkedResult:
    p = self.p
    res = ParkedResult()
    p.say("\nPart 1: the car's data. Each step asks for one thing; do it, then press Enter and hold it for 3 seconds.")

    rest = self.record("Engine running, shifter in P (manual: neutral with the parking brake on). Hands and feet off everything.")
    res.rest = rest
    brake_off, brake_on = self.twice("Press the brake pedal and hold it down.", "Let go of the brake pedal.")
    gas_off, gas_on = self.twice("Press the gas pedal gently so the engine speeds up a little, and hold it there.",
                                 "Let go of the gas pedal.")
    left_off, left_on = self.twice("Switch the LEFT turn signal on.", "Switch the turn signal off.")
    right_off, right_on = self.twice("Switch the RIGHT turn signal on.", "Switch the turn signal off.")
    door_off, door_on = self.twice("Open the driver's door (stay seated).", "Close the driver's door.")

    gears: dict[str, list] = {}
    if manual:
      gears["N"] = self.record("Clutch down, shifter in neutral.")
      gears["R"] = self.record("Clutch down, put it in reverse.")
      self.record("Back to neutral, clutch up, parking brake on.")
    else:
      p.say("\nNow the shifter. Keep your foot on the brake the whole time.")
      for gear in ("P", "R", "N", "D"):
        gears[gear] = self.record(f"Foot on the brake, move the shifter to {gear}.")
      while len(gears) < 10:
        label = p.ask(MSG_MORE_GEARS, (("", "It doesn't go further"),), MSG_MORE_GEARS_PHONE, free_text=True).upper()
        if not label:
          break
        if label in gears:
          p.say(f"{label} is done already.")
          continue
        gears[label] = self.record(f"Keep it in {label}, foot on the brake.")
      self.record("Foot on the brake, shifter back to P.")

    stats = dsc.message_stats(self.frames, self.recorded_seconds)
    res.stats = stats
    res.fingerprint = dsc.fingerprint(self.frames)
    cfg = self.cfg
    res.findings = [
      dsc.check_standstill_speed(cfg, rest),
      dsc.resolve_flag(cfg, "BRAKE_PRESSED", brake_off, brake_on, stats),
      dsc.resolve_pedal(cfg, "GAS_PEDAL", gas_off, gas_on, stats),
      dsc.resolve_flag(cfg, "LEFT_BLINKER", left_off, left_on, stats, flashing=True),
      dsc.resolve_flag(cfg, "RIGHT_BLINKER", right_off, right_on, stats, flashing=True),
      dsc.resolve_flag(cfg, "DOOR_OPEN", door_off, door_on, stats),
      dsc.resolve_gear(cfg, gears, stats),
    ]
    missing = dsc.missing_messages(cfg, stats)
    if missing:
      res.notes.append("Messages from the default map your car doesn't send (fine when their signals were found elsewhere): "
                     + ", ".join(missing))
    return res

  # ***** the motor *****

  def _motor_angle_after(self, seconds: float = 0.5) -> float | None:
    self.session.drain()
    self.session.run(seconds, self._hold_motor_off)
    if not self.session.motor_present() or self.session.motor is None:
      return None
    return self.session.motor.angle

  def _record_turn(self, text: str, phone_text: str) -> tuple[list[dsc.Frame], list[tuple[float, float]]]:
    """Asks for a turn of the steering wheel, then records the car's data and the motor's angle while the person
    turns, until the motor has moved and then been still for TURN_STILL_S (or TURN_MAX_S in all). Returns the
    F-CAN frames and the motor's angle over time (seconds, firmware degrees), on the session's clock."""
    self.p.ask(text, (("", "Start, then turn"),), phone_text)
    self.session.drain()
    frames: list[dsc.Frame] = []
    series: list[tuple[float, float]] = []
    start = self.session.now()
    first: float | None = None
    moved_t: float | None = None
    still_since: float | None = None
    while self.session.now() - start < TURN_MAX_S:
      frames += self.session.run(0.1, self._hold_motor_off)
      if not self.session.motor_present() or self.session.motor is None:
        break
      angle = self.session.motor.angle
      now = self.session.now()
      series.append((now, angle))
      first = angle if first is None else first
      if abs(angle - first) >= TURN_MOVED_FW_DEG and moved_t is None:
        moved_t = now
      if moved_t is not None and len(series) > 1:
        if abs(angle - series[-2][1]) < 0.3:
          still_since = now if still_since is None else still_since
          if now - still_since >= TURN_STILL_S:
            break
        else:
          still_since = None
    self.frames += frames
    self.recorded_seconds += self.session.now() - start
    return frames, series

  def which_teeth(self) -> int | None:
    for _ in range(3):
      answer = self.p.ask(MSG_WHICH_TEETH, TEETH_CHOICES, MSG_WHICH_TEETH_PHONE).strip()
      if answer.isdigit() and int(answer) in TEETH_SETS:
        return int(answer)
    return None

  def motor_checks(self, res: ParkedResult) -> None:
    p, s = self.p, self.session
    a = self.cfg.actuator
    p.say("\nPart 2: the motor. Engine still running, shifter in P." if self.cfg.car_network else
          "\nThe motor. Engine running, shifter in P.")
    res.teeth = self.which_teeth()
    if res.teeth is None:
      res.motor = dsc.MotorCheck(False, "no answer to which steering wheel teeth are on (type 15, 29 or 45)")
      return
    start = None
    for _ in range(2):
      p.step(MSG_LEVER_DOWN)
      start = self._motor_angle_after()
      if start is not None:
        break
      p.say(MSG_NO_MOTOR)
    if start is None:
      res.motor = dsc.MotorCheck(False, "the motor didn't answer")
      return

    status = s.motor
    assert status is not None
    if not status.control_status & StepperControlStatus.SENSORED:
      res.notes.append("The motor reports no position sensor reading; it may need its calibration (see the build guide).")
    res.notes.append(f"Motor temperature {status.temperature:.0f} C")

    left_frames, left_series = self._record_turn(MSG_TURN_LEFT, MSG_TURN_LEFT_PHONE)
    right_frames, right_series = self._record_turn(MSG_TURN_RIGHT, MSG_TURN_RIGHT_PHONE)
    if not left_series or not right_series or not s.motor_present():
      res.motor = dsc.MotorCheck(False, "the motor stopped answering while the wheel turned")
      return
    left, right = left_series[-1][1], right_series[-1][1]
    # the car's own steering angle, if it broadcasts one: it would follow the motor's angle during the turns
    stats = dsc.message_stats(self.frames, max(self.recorded_seconds, 1.0))
    res.stats = stats
    if self.cfg.car_network:
      res.findings.append(dsc.find_angle_signal(self.cfg, res.rest, [(left_frames, left_series), (right_frames, right_series)],
                                                stats, a.angle_scale))
    # with a roller on the motor gear it follows the wheel past the teeth along the rolling band; without one (the
    # side-slide mount, short teeth) over the teeth alone: the nearer of the two is what's fitted
    res.arc, res.roll_past = teeth_arc(res.teeth, abs(left - right) * a.angle_scale)
    res.motor = dsc.motor_direction_from_turn(start, left, right, a.angle_scale, res.arc)
    if not res.motor.ok:
      # a turn that matches the other teeth means the answer about which teeth are on was wrong, not the gearing
      others = [(k, v) for k, v in TEETH_SETS.items()] + [(k, v) for k, v in NO_ROLLER_ARCS.items()]
      for other, arc in others:
        if other != res.teeth and dsc.motor_direction_from_turn(start, left, right, a.angle_scale, arc, arc_tolerance=0.15).ok:
          detail = " ".join((f"the motor turned with the steering wheel as far as the {other} degree teeth reach,",
                             f"not the {res.teeth}: check which teeth are on"))
          res.motor = dataclasses.replace(res.motor, detail=detail)
      return

    # The direction so far rests on which way the wheel was turned first. The person's own eyes check it: the motor
    # is told to turn the wheel left, and they say which way it went.
    direction = res.motor.direction
    for attempt in range(2):
      res.push = self._push_and_measure(direction)
      if not res.push.ok:
        return
      seen_left = p.yes_no(MSG_DID_IT_TURN_LEFT, MSG_DID_IT_TURN_LEFT_PHONE)
      if seen_left is None:
        res.push = dsc.MotorCheck(False, "no clear answer to which way the wheel turned", direction)
        return
      if seen_left:
        res.push = dataclasses.replace(res.push, detail=res.push.detail + ", and you saw it go left")
        if direction != res.motor.direction:
          res.motor = dataclasses.replace(res.motor, direction=direction,
                                          detail=res.motor.detail + "; direction corrected after you saw the wheel go right")
        res.grip = self.grip_test(direction)
        return
      if attempt == 0:
        p.say(MSG_TRY_OTHER_WAY)
        direction = -direction
    res.push = dsc.MotorCheck(False, MSG_NEVER_LEFT, direction, wrong_way=True)

  def _push_and_measure(self, direction: int) -> dsc.MotorCheck:
    """The motor turns the wheel left (as direction says left is): the result from its own angle reading."""
    p = self.p
    check = dsc.MotorCheck(False, "not tried", direction)
    for attempt in range(2):
      p.step(MSG_PUSH)
      before = self._motor_angle_after(0.3)
      if before is None:
        return dsc.MotorCheck(False, "the motor stopped answering", direction)
      angles = self._push(direction, before)
      after = max(angles, key=lambda x: abs(x - before)) if angles else before
      check = dsc.motor_push_agrees(direction, before, after)
      if check.ok or check.wrong_way:
        return check
      if attempt == 0:
        p.say("The wheel barely moved. Make sure the engine is running (power steering) and nothing holds the wheel; trying once more.")
    return check

  def _push(self, direction: int, start: float) -> list[float]:
    """Turns the wheel left with the motor: ramp up, hold, ramp down, off. It lets go as soon as the wheel has turned
    PUSH_STOP_DEG, so the motor gear stays on the teeth. Returns the motor angles seen."""
    angles = []
    scale = self.cfg.actuator.angle_scale
    stopped = False

    def command(t: float):
      nonlocal stopped
      if self.session.motor is not None:
        angles.append(self.session.motor.angle)
        stopped = stopped or abs(self.session.motor.angle - start) * scale >= PUSH_STOP_DEG
      if stopped or t < 0.2 or t > 2.0:
        return StepperMode.OFF, 0.0
      ramp = min((t - 0.2) / 0.5, 1.0, (2.0 - t) / 0.3)
      return StepperMode.TORQUE_CONTROL, direction * PUSH_NM * self.cfg.actuator.torque_cmd_scale * max(ramp, 0.0)

    self.session.drain()
    self.session.run(2.3, command)
    return angles

  def grip_test(self, direction: int) -> dsc.MotorCheck:
    """The person holds the steering wheel still and the motor pushes as hard as it can, each way. Its gear must not
    slip over the steering wheel teeth, and the teeth must not slide on the steering wheel."""
    a = self.cfg.actuator
    torque = grip_torque_fw(a)
    wheel_nm = torque / a.torque_cmd_scale
    for attempt in range(2):
      self.p.step(MSG_GRIP, button="Start the grip test")
      self.p.say(MSG_GRIP_HOLD)
      outcomes = []
      for sign in (1, -1):
        before = self._motor_angle_after(GRIP_COUNTDOWN_S if sign == 1 else 0.3)
        if before is None:
          self.p.say(MSG_GRIP_DONE)
          return dsc.MotorCheck(False, "the motor stopped answering during the grip test", direction)
        outcomes.append(self._grip_push(sign * direction * torque, before))
      self.p.say(MSG_GRIP_DONE)
      if "slipped" in outcomes:
        return dsc.MotorCheck(False, MSG_GRIP_SLIPPED, direction)
      if "moved" not in outcomes:
        detail = f"nothing slipped with {wheel_nm:.1f} Nm at the steering wheel each way, the most the motor can push"
        return dsc.MotorCheck(True, detail, direction)
      if attempt == 0:
        self.p.say(MSG_GRIP_TRY_AGAIN)
    return dsc.MotorCheck(False, MSG_GRIP_MOVED, direction)

  def _grip_push(self, torque_fw: float, start: float) -> str:
    """One push of the grip test: ramp up, hold, ramp down. Returns "held", "slipped" (the motor's angle jumped, its
    gear went over a tooth) or "moved" (the steering wheel turned), stopping the push at once for either."""
    scale = self.cfg.actuator.angle_scale
    outcome = "held"
    last: float | None = None

    def command(t: float):
      nonlocal outcome, last
      if self.session.motor is not None and outcome == "held":
        angle = self.session.motor.angle
        if last is not None and abs(angle - last) * scale >= GRIP_SLIP_DEG:
          outcome = "slipped"
        elif abs(angle - start) * scale >= GRIP_STOP_DEG:
          outcome = "moved"
        last = angle
      end = GRIP_RAMP_S + GRIP_HOLD_S
      if outcome != "held" or t > end + 0.2:
        return StepperMode.OFF, 0.0
      ramp = min(t / GRIP_RAMP_S, 1.0, (end + 0.2 - t) / 0.2)
      return StepperMode.TORQUE_CONTROL, torque_fw * max(ramp, 0.0)

    self.session.drain()
    self.session.run(GRIP_RAMP_S + GRIP_HOLD_S + 0.5, command)
    return outcome


def grip_torque_fw(actuator) -> float:
  """The grip test's push in firmware torque: the most the controller board gives, in the firmware's 0.125 steps."""
  return math.floor(BOARD_MAX_A * actuator.firmware_k_torque * actuator.firmware_gearing_ratio / 0.125) * 0.125


# ***** results *****

def build_config(raw: dict, res: ParkedResult) -> tuple[dict, bool, list[str]]:
  """The config to save, whether the parked part passed, and plain-word problems."""
  problems = []
  by_name = {f.signal: f for f in res.findings}
  if parse_config(raw).car_network and not by_name["BRAKE_PRESSED"].ok:
    problems.append(f"{dsc.plain_name('BRAKE_PRESSED')}: {by_name['BRAKE_PRESSED'].detail}")
  new_raw = dsc.apply_findings(raw, res.findings)
  res.notes += dsc.update_message_rates(new_raw, res.stats)
  motor_ok = res.motor is not None and res.motor.ok and res.push is not None and res.push.ok and res.grip is not None and res.grip.ok
  if res.motor is None or not res.motor.ok:
    problems.append(f"motor: {res.motor.detail if res.motor else 'not checked'}")
  elif res.push is None or not res.push.ok:
    problems.append(f"motor push: {res.push.detail if res.push else 'not checked'}")
  elif res.grip is None or not res.grip.ok:
    problems.append(f"grip test: {res.grip.detail if res.grip else 'not done'}")
  if res.motor is not None and res.motor.ok:
    new_raw["actuator"]["direction"] = res.motor.direction
    new_raw["actuator"]["tracked_arc_deg"] = res.arc
    new_raw["actuator"]["roll_past_deg"] = res.roll_past
    new_raw["actuator"]["mechanical_ratio"] = MECHANICAL_RATIOS[res.teeth]
  new_raw.setdefault("setup", {})
  # A new parked check can change the motor's direction or the signal map, so the drive check that confirmed the old
  # ones no longer counts: lane keeping waits for both again.
  new_raw["setup"].pop("drive", None)
  passed = not problems and motor_ok
  if passed:
    new_raw["setup"]["parked"] = datetime.datetime.now().isoformat(timespec="seconds")
  else:
    new_raw["setup"].pop("parked", None)
  parse_config(new_raw)
  return new_raw, passed, problems


def report(res: ParkedResult, problems: list[str], passed: bool) -> str:
  lines = [f"hondastepper car setup, parked part, software {VERSION}, {datetime.datetime.now().isoformat(timespec='seconds')}", ""]
  for f in res.findings:
    marker = "OK  " if f.ok else ("    " if f.signal == "STEER_ANGLE" else "FAIL")   # the angle is a bonus, never a fault
    lines.append(f"  {marker} {dsc.plain_name(f.signal)}: {f.detail}")
  if res.teeth:
    roller = "" if res.roll_past or not res.arc else ", the motor gear without a roller"
    lines.append(f"  steering wheel teeth: the {TEETH_NAMES[res.teeth]} ({res.teeth} degrees each way){roller}")
  if res.motor:
    lines.append(f"  {'OK  ' if res.motor.ok else 'FAIL'} motor direction: {res.motor.detail}")
  if res.push:
    lines.append(f"  {'OK  ' if res.push.ok else 'FAIL'} motor push: {res.push.detail}")
  if res.grip:
    lines.append(f"  {'OK  ' if res.grip.ok else 'FAIL'} grip test: {res.grip.detail}")
  lines += ["", *[f"  note: {n}" for n in res.notes]]
  if problems:
    lines += ["", "Problems:", *[f"  {pr}" for pr in problems]]
  if res.fingerprint:
    lines += ["", "For the record, your car's messages (address: length): " + ", ".join(f"{a:#x}:{n}" for a, n in res.fingerprint.items())]
  lines += ["", "RESULT: " + ("PASSED" if passed else "NOT PASSED")]
  return "\n".join(lines)


def save_report(text: str, directory: str) -> str:
  os.makedirs(directory, exist_ok=True)
  path = os.path.join(directory, f"setup_report_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt")
  with open(path, "w") as f:
    f.write(text + "\n")
  return path


def run(session: CanSession, prompter: Prompter, manual: bool, save: Callable[[dict], str] = save_device_config,
        report_dir: str | None = None) -> bool:
  raw = load_raw_config()
  setup = CarSetup(session, prompter, raw)
  if setup.cfg.car_network:
    if not setup.check_car_data():
      return False
    res = setup.parked_checks(manual)
  else:
    res = ParkedResult()      # stand-alone: nothing to read from the car, only the motor to check
  setup.motor_checks(res)
  new_raw, passed, problems = build_config(raw, res)
  text = report(res, problems, passed)
  prompter.say("\n" + text)
  if report_dir:
    prompter.say(f"\nThis report is saved in {save_report(text, report_dir)}")
  required = all(f.ok for f in res.findings if f.signal == "BRAKE_PRESSED")
  if required:
    path = save(new_raw)
    prompter.say(f"Settings saved to {path}.")
  else:
    prompter.say("Nothing was saved: the brake pedal must be found.")
  if passed:
    prompter.say(MSG_PART1_PASSED)
  else:
    prompter.say("Part 1 did not pass, so lane keeping stays off. Fix what the report says and run this again.")
  return passed


def main() -> int:
  from panda import Panda
  from openpilot.sunnypilot.tools.hondastepper.device import PowerWatchdog, reboot, stop_openpilot

  p = Prompter()
  manual = False
  if parse_config(load_raw_config()).car_network:
    p.say(INTRO)
    answer = p.ask("Is the car an automatic or a manual? Type a or m and press Enter:", (("a", "Automatic"), ("m", "Manual")),
                   "Is the car an automatic or a manual?").lower()
    manual = answer.startswith("m")
  else:
    p.say(INTRO_STANDALONE)
  p.step("Car parked, engine running, comma device on its mount and plugged in. openpilot will stop and the screen will go dark until the end.",
         button="Start")
  if not stop_openpilot():
    p.say("openpilot didn't stop; restart the comma device and try again.")
    return 1
  watchdog = PowerWatchdog().start()
  session = CanSession(Panda())
  passed = False
  try:
    passed = run(session, p, manual, report_dir=os.path.dirname(device_config_path()))
  finally:
    session.close()
    watchdog.stop()
  p.ask("Press Enter to restart the comma device (it rebuilds the software first; that can take several minutes).",
        (("", "Restart the comma device"),),
        "Restart the comma device to finish. It rebuilds the software first, which can take several minutes.")
  reboot()
  return 0 if passed else 2


if __name__ == "__main__":
  sys.exit(main())
