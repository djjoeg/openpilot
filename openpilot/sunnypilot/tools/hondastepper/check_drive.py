#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Car setup for the Honda Accord with the add-on steering motor (hondastepper), part 2 of 2: the drive check.

After part 1 (accord_setup.sh car) has passed, drive for at least 5 minutes with the lift lever down (lane keeping
stays off until this check passes), at a mix of speeds with some curves or lane changes. Park, then run on the comma
device over SSH:

  /data/openpilot/accord_setup.sh drive

It reads the drive openpilot just recorded: the car's data, the motor's angle and the GPS. It checks the car's
speed reading against the GPS speed (and finds it when it's somewhere else), and checks the motor's saved direction
against which way the car actually turned, with nothing from part 1's turn test. It saves the result to
/data/hondastepper/config.json and restarts the comma device. Lane keeping turns on once both parts have passed.
"""
import bz2
import datetime
import glob
import os
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field

from opendbc.car.hondastepper import discovery as dsc
from opendbc.car.hondastepper.config import load_raw_config, parse_config, save_device_config
from openpilot.sunnypilot.tools.hondastepper import VERSION

LOG_ROOT = "/data/media/0/realdata"
MAX_SEGMENTS = 12          # the last 12 minutes of driving is plenty
MAX_AGE_SECONDS = 6 * 3600
FCAN_BUS = 0
MOTOR_BUS = 1
GPS_MAX_SPEED_ERROR = 1.0  # m/s, GPS fixes less sure of their speed than this are skipped
GPS_MAX_BEARING_ERROR = 5.0  # degrees, same for the course

MSG_DRIVE_MORE = " ".join((
  "Nothing was saved. Drive at least 5 minutes with the lift lever down, at a mix of speeds between about 15 and",
  "50 mph with some curves or lane changes, where the comma device can see the sky, then run this again.",
))
MSG_PART1_FIRST = "Run part 1 first: /data/openpilot/accord_setup.sh car"
MSG_ALL_PASSED = " ".join((
  "Both parts of the setup have passed. After the restart, lane keeping turns on by itself about 2 seconds after you",
  "pull the lift lever down until it clicks, and off when you lift it. If the lever is already down when you start the",
  "car, lane keeping turns on by itself once sunnypilot is running. Do the first test in an empty parking lot (see",
  "the build guide).",
))


def recent_segments(root: str = LOG_ROOT, max_segments: int = MAX_SEGMENTS, max_age: float = MAX_AGE_SECONDS,
                    now: float | None = None) -> list[str]:
  """Finished segment folders (rlog written and closed), newest first."""
  now = time.time() if now is None else now  # noqa: TID251  file times are wall clock times
  segments = []
  for path in glob.glob(os.path.join(root, "*--*")):
    rlogs = [f for f in ("rlog.zst", "rlog.bz2", "rlog") if os.path.isfile(os.path.join(path, f))]
    if not rlogs or os.path.exists(os.path.join(path, "rlog.lock")):
      continue
    mtime = os.path.getmtime(os.path.join(path, rlogs[0]))
    if now - mtime <= max_age:
      segments.append((mtime, path))
  return [p for _, p in sorted(segments, reverse=True)[:max_segments]]


@dataclass
class Drive:
  """What the drive check reads from a recorded drive. Times in seconds."""
  frames: list[dsc.Frame] = field(default_factory=list)                 # the car's F-CAN
  motor: list[tuple[float, float]] = field(default_factory=list)        # (time, motor angle in firmware degrees)
  gps: list[tuple[float, float]] = field(default_factory=list)          # (time, speed m/s), good fixes only
  headings: list[tuple[float, float, float]] = field(default_factory=list)  # (time, course clockwise from north, m/s)
  seconds: float = 0.0                                                   # how much driving the F-CAN covers


def read_segment(path: str) -> Drive:
  """One recorded segment."""
  from openpilot.cereal import log

  for name in ("rlog.zst", "rlog.bz2", "rlog"):
    fn = os.path.join(path, name)
    if os.path.isfile(fn):
      break
  with open(fn, "rb") as f:
    dat = f.read()
  if fn.endswith(".zst") or dat.startswith(b"\x28\xB5\x2F\xFD"):
    import zstandard
    with zstandard.ZstdDecompressor().stream_reader(dat) as reader:
      dat = reader.read()
  elif fn.endswith(".bz2") or dat.startswith(b"BZh"):
    dat = bz2.decompress(dat)

  drive = Drive()
  try:
    for evt in log.Event.read_multiple_bytes(dat):
      which = evt.which()
      t = evt.logMonoTime * 1e-9
      if which == "can":
        for c in evt.can:
          if c.src == FCAN_BUS:
            drive.frames.append((t, c.address, bytes(c.dat)))
          elif c.src == MOTOR_BUS and c.address == dsc.MOTOR_STATUS_ADDR and len(c.dat) == 8:
            drive.motor.append((t, dsc.motor_angle_fw(bytes(c.dat))))
      elif which in ("gpsLocation", "gpsLocationExternal"):
        g = getattr(evt, which)
        if g.hasFix and 0 < g.speedAccuracy <= GPS_MAX_SPEED_ERROR:
          drive.gps.append((t, float(g.speed)))
          if 0 < g.bearingAccuracyDeg <= GPS_MAX_BEARING_ERROR:
            drive.headings.append((t, float(g.bearingDeg), float(g.speed)))
  except Exception:  # a segment cut short by a power loss ends in a broken event; keep what came before it
    pass
  if drive.frames:
    drive.seconds = drive.frames[-1][0] - drive.frames[0][0]
  return drive


def load_drive(segments: list[str], reader: Callable[[str], Drive] = read_segment) -> Drive:
  """All segments together. Each segment's times are shifted apart so a reboot between drives can't mix them up."""
  out = Drive()
  for i, path in enumerate(reversed(segments)):
    seg = reader(path)
    if not seg.frames:
      continue
    offset = i * 10_000.0 - seg.frames[0][0]
    out.frames += [(t + offset, a, d) for t, a, d in seg.frames]
    out.motor += [(t + offset, a) for t, a in seg.motor]
    out.gps += [(t + offset, v) for t, v in seg.gps]
    out.headings += [(t + offset, b, v) for t, b, v in seg.headings]
    out.seconds += seg.seconds
  return out


def check(raw: dict, drive: Drive) -> tuple[dict | None, dsc.SpeedFit, dsc.MotorCheck | None]:
  """The config to save (None when a check failed), the speed result, and the motor direction result (None when the
  speed check already failed)."""
  cfg = parse_config(raw)
  stats = dsc.message_stats(drive.frames, max(drive.seconds, 1.0))
  fit = dsc.check_speed(cfg, drive.frames, drive.gps, stats)
  if not fit.ok:
    return None, fit, None
  motor = dsc.motor_direction_from_drive(drive.motor, drive.headings, cfg.actuator.direction, cfg.actuator.angle_scale)
  if not motor.ok:
    return None, fit, motor
  findings = []
  if fit.signal_def is not None:
    findings.append(dsc.Finding("VEHICLE_SPEED", True, fit.detail, signal_def=fit.signal_def, message_def=fit.message_def))
  new_raw = dsc.apply_findings(raw, findings)
  dsc.update_message_rates(new_raw, stats)
  new_raw.setdefault("setup", {})["drive"] = datetime.datetime.now().isoformat(timespec="seconds")
  parse_config(new_raw)
  return new_raw, fit, motor


def run(print_fn: Callable[[str], None] = print, root: str = LOG_ROOT, save: Callable[[dict], str] = save_device_config) -> bool:
  raw = load_raw_config()
  if not raw.get("setup", {}).get("parked"):
    print_fn(MSG_PART1_FIRST)
    return False
  segments = recent_segments(root)
  if not segments:
    print_fn("No recent drive found. Drive for at least 5 minutes first (the comma device must be on and recording).")
    return False
  print_fn(f"Reading the last {len(segments)} minutes of driving...")
  drive = load_drive(segments)
  new_raw, fit, motor = check(raw, drive)
  print_fn(f"Speed: {fit.detail}")
  if motor is not None:
    print_fn(f"Motor direction: {motor.detail}")
  if new_raw is None:
    print_fn(MSG_DRIVE_MORE)
    return False
  path = save(new_raw)
  print_fn(f"Settings saved to {path}.")
  print_fn(MSG_ALL_PASSED if parse_config(new_raw).verified else MSG_PART1_FIRST)
  return True


INTRO = f"""
Honda Accord lane keeping, software {VERSION}: car setup, part 2 of 2 (drive check)

This reads the drive the comma device just recorded. It checks the car's speed reading against the GPS, and the
motor's direction against the way the car turned.
"""


def main() -> int:
  from openpilot.sunnypilot.tools.hondastepper.device import reboot

  print(INTRO)
  if not run():
    return 2
  input("\nPress Enter to restart the comma device (it rebuilds the software first; that can take several minutes). ")
  reboot()
  return 0


if __name__ == "__main__":
  sys.exit(main())
