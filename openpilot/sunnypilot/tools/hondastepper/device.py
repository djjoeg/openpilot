"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The comma device side of the hondastepper setup tools: stopping openpilot so the tool can talk to the panda
itself, keeping the device awake meanwhile, and reading and sending CAN through the panda.
"""
import os
import signal
import subprocess
import threading
import time
from collections.abc import Callable

from opendbc.can import CANPacker, CANParser
from opendbc.car.can_definitions import CanData
from opendbc.car.hondastepper.config import SERVO_DBC_NAME
from opendbc.car.hondastepper.steppercan import STEERING_STATUS, create_steer_command
from opendbc.car.hondastepper.values import StepperMode
from opendbc.car.structs import CarParams

FCAN_BUS = 0
MOTOR_BUS = 1
MOTOR_STATUS_ADDR = 0x22F
COMMAND_PERIOD = 0.02          # the motor wants a command every 20 ms and gives up after 60 ms
MOTOR_TIMEOUT = 0.1            # no status for this long: the lift lever is up or the motor isn't connected

POWER_WATCHDOG_FILE = "/var/tmp/power_watchdog"  # openpilot's manager keeps this fresh so the device stays on


def _pids_matching(pattern: str) -> list[int]:
  out = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True, check=False).stdout
  return [int(p) for p in out.split() if int(p) != os.getpid()]


def stop_openpilot(timeout: float = 30.0) -> bool:
  """Stops openpilot's manager, which stops every openpilot process, so the panda is free. Returns False if
  something that uses the panda is still running after timeout."""
  for pid in set(_pids_matching("system/manager/manager.py") + _pids_matching("./manager.py")):
    try:
      os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
      pass
  end = time.monotonic() + timeout
  while time.monotonic() < end:
    if not _pids_matching("pandad"):
      return True
    time.sleep(0.5)
  return False


def reboot() -> None:
  subprocess.run(["sudo", "reboot"], check=False)


class PowerWatchdog:
  """Does the manager's job of telling the device's power monitor that someone is using it."""

  def __init__(self, path: str = POWER_WATCHDOG_FILE, period: float = 5.0):
    self.path, self.period = path, period
    self._stop = threading.Event()
    self._thread = threading.Thread(target=self._run, daemon=True)

  def _run(self):
    while not self._stop.is_set():
      try:
        with open(self.path, "w") as f:
          f.write(str(time.monotonic()))
      except OSError:
        pass
      self._stop.wait(self.period)

  def start(self):
    self._thread.start()
    return self

  def stop(self):
    self._stop.set()


class MotorStatus:
  def __init__(self, values: dict):
    self.angle = float(values["STEERING_ANGLE"])          # firmware degrees, zero where the motor powered up
    self.torque = float(values["STEERING_TORQUE"])        # firmware Nm
    self.control_status = int(values["CONTROL_STATUS"])
    self.temperature = float(values["TEMPERATURE"])
    self.debug_states = int(values["DEBUG_STATES"])


class CanSession:
  """The panda in all-output mode: records the car's bus and talks to the motor. Clock and sleep can be
  replaced for tests."""

  def __init__(self, panda, clock: Callable[[], float] = time.monotonic, sleep: Callable[[float], None] = time.sleep):
    self.panda = panda
    self.clock, self.sleep = clock, sleep
    self.t0 = clock()
    panda.set_heartbeat_disabled()
    panda.set_power_save(False)
    panda.set_safety_mode(CarParams.SafetyModel.allOutput, 0)
    self.packer = CANPacker(SERVO_DBC_NAME)
    self.parser = CANParser(SERVO_DBC_NAME, [(STEERING_STATUS, float("nan"))], MOTOR_BUS)
    self.counter = 0
    self.motor_seen_t = -1.0
    self.motor: MotorStatus | None = None
    self.last_command_t = -1.0

  def now(self) -> float:
    return self.clock() - self.t0

  def _poll(self, fcan: list | None):
    msgs = self.panda.can_recv()
    t = self.now()
    motor_frames = []
    for addr, dat, bus in msgs:
      if bus == FCAN_BUS and fcan is not None:
        fcan.append((t, addr, bytes(dat)))
      elif bus == MOTOR_BUS and addr == MOTOR_STATUS_ADDR:
        motor_frames.append(CanData(addr, bytes(dat), bus))
    if motor_frames and MOTOR_STATUS_ADDR in self.parser.update([(int(t * 1e9), motor_frames)]):
      self.motor_seen_t = t
      self.motor = MotorStatus(self.parser.vl[STEERING_STATUS])
    return msgs

  def drain(self):
    """Throws away whatever the panda collected while nobody was reading."""
    for _ in range(100):
      if not self._poll(None):
        break

  def motor_present(self) -> bool:
    return self.motor_seen_t >= 0 and self.now() - self.motor_seen_t < MOTOR_TIMEOUT

  def send_motor(self, mode: StepperMode, torque_fw_nm: float = 0.0):
    addr, dat, bus = create_steer_command(self.packer, self.counter, mode, torque_fw_nm)
    self.panda.can_send(addr, dat, bus)
    self.counter = (self.counter + 1) % 16
    self.last_command_t = self.now()

  def run(self, seconds: float, motor_command: Callable[[float], tuple[StepperMode, float]] | None = None) -> list:
    """Records the car's bus for seconds. With motor_command (time since start -> mode, torque), commands the motor
    every 20 ms meanwhile. Returns the F-CAN frames as (seconds, address, data)."""
    fcan: list = []
    start = self.now()
    next_command = start
    while self.now() - start < seconds:
      self._poll(fcan)
      if motor_command is not None and self.now() >= next_command:
        self.send_motor(*motor_command(self.now() - start))
        next_command += COMMAND_PERIOD
      self.sleep(0.002)
    return fcan

  def close(self):
    try:
      self.send_motor(StepperMode.OFF)
      self.panda.set_safety_mode(CarParams.SafetyModel.noOutput, 0)
    finally:
      self.panda.close()
