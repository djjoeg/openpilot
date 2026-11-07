"""
The slide mount in the car, and the checks that it fits and works, for any key depth D the photos allow (carscene.py):
the gear meshing the back teeth through their whole arc; nothing touching with the motor on (wheel straight, turned
through the teeth, and past them with the carrier following the roller down the lead-in), while it slides off and the
latch lever swings, and slid off with the teeth anywhere round; everything clear of the column covers, the back cover,
the key and your fingers on it, the wiper stalk, the adjustment tab, its swing and your fingers on it, the dash face,
the spokes and the grip; the latch's forces, the springs, the power switch.

Frames: see popparts.py and slideparts.py.
"""
import math
import os

import numpy as np
from manifold3d import Manifold

import carscene as CS
import faceparts as FP
import params as P
import popassembly as PA
import popparts as PP
import slideparts as SP
from cadlib import revolve, union

MESH_PHASE = PA.MESH_PHASE


def overlap(a: Manifold, b: Manifold) -> float:
  return (a ^ b).volume()


def min_gap(a: Manifold, b: Manifold, far: float = 15.0) -> float:
  v = overlap(a, b)
  return -v if v > 1e-3 else round(a.min_gap(b, far), 2)


def to_wheel(m: Manifold, mount_deg: float, off: float = 0.0) -> Manifold:
  """A carrier-frame solid -> steering wheel frame, the mount at mount_deg, slid off by off mm (negative: further on)."""
  Rm = PP.rot_z(mount_deg)
  R = Rm @ PP.R_POP
  T = Rm @ np.array([PP.R_FACE_P, 0.0, PP.Z_AXIS_P])
  return PP.place(m.translate((0.0, off, 0.0)) if off else m, R, T)


def drop_most() -> float:
  """How far the carrier can go past on (towards the wheel) with the wheel turned past the teeth: until the pusher is out
  against its stop and the cam's flat leaves it (the pull springs then hold it there)."""
  return SP.PUSH_TRAVEL_ON


class SlideAssembly:
  def __init__(self, D: float = CS.D_REF, mount_deg: float = SP.MOUNT_DEG_S, parts: dict = None):
    self.D, self.mount = float(D), float(mount_deg)
    self.sc = CS.CarScene(self.D)
    self.t = SP.SlideTeeth(mount_deg=SP.MOUNT_DEG_S)
    self.p = parts if parts is not None else build_parts(self.t)

  # ----- the mount's parts -----
  def place(self, m: Manifold, off: float = 0.0) -> Manifold:
    return to_wheel(m, self.mount, off)

  def teeth(self, wheel_deg: float = 0.0) -> Manifold:
    return self.p["teeth"].rotate((0, 0, self.mount + wheel_deg))

  def gear(self, off: float = 0.0, wheel_deg: float = 0.0, part: str = "gear") -> Manifold:
    return self.place(self.p[part].rotate((0, 0, MESH_PHASE - FP.FACE_RATIO * wheel_deg)), off)

  def carrier(self, off: float = 0.0) -> Manifold:
    return self.place(self.p["carrier"], off)

  def motor(self, off: float = 0.0) -> Manifold:
    return self.place(self.p["motor"], off)

  def rods(self, off: float = 0.0) -> Manifold:
    return self.place(SP.rods(), off) + self.place(SP.collars(), off)

  def lever(self, off: float = 0.0, swing: float = 0.0) -> Manifold:
    return self.place(SP.slide_lever(swing), off)

  def lever_sweep(self, off: float, step: float = 5.0) -> Manifold:
    return union([self.place(SP.slide_lever(SP.SWING_SIGN * a), off) for a in np.arange(0.0, SP.LEVER_SWING + 1e-6, step)])

  def springs(self, off: float = 0.0) -> Manifold:
    return self.place(SP.release_springs(off))

  def block(self) -> Manifold:
    return self.place(self.p["block"])

  def fixed_bits(self) -> Manifold:
    """The pusher (out), its plug, the bearings, the switch."""
    return self.place(SP.pusher() + SP.plug() + SP.bearings() + SP.switch_body())

  # ----- the car -----
  def grip(self) -> Manifold:
    t = self.t
    pts = [(t.rr + (PP.GRIP_P / 2) * math.cos(a), (PP.GRIP_P / 2) * math.sin(a))
           for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    return revolve(pts, 0.0, 360.0, step_deg=1.0)

  def teeth_ring(self) -> Manifold:
    t = self.t
    return revolve([(p[0], p[1]) for p in t.profile()], 0.0, 360.0, step_deg=1.0)

  def spoke_zone(self) -> Manifold:
    from cadlib import cyl
    return cyl(PP.WHEEL_OD_P / 2 - PP.GRIP_P + 1.0, P.SPOKE_BACK_Z, 25.0, segments=180) + cyl(P.HUB_R, P.HUB_BACK_Z, 25.0)

  def fingers(self) -> Manifold:
    from cadlib import cyl
    t = self.t
    behind, inside, outside = PA.FINGERS
    return cyl(PP.WHEEL_OD_P / 2 + outside, behind, 0.0, segments=180) - \
      cyl(t.rr - PP.GRIP_P / 2 - inside, behind - 1, 1, segments=180)

  def car_parts(self) -> list:
    sc = self.sc
    out = [("column cover", sc.column_cover()), ("back cover (it turns with the wheel)", sc.back_cover()),
           ("dash face", sc.bolster()), ("wiper stalk (all positions)", sc.stalk()),
           ("adjustment tab, its swing and your fingers on it", sc.moved(PA.tab_lever_sweep()))]
    for k, v in sc.key_parts().items():
      out.append((k, v))
    out.append(("the spokes' sweep", self.spoke_zone()))
    return out


def _cache_dir() -> str:
  d = os.environ.get("POP_CACHE", os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache"))
  os.makedirs(d, exist_ok=True)
  return d


def build_parts(t: SP.SlideTeeth = None) -> dict:
  t = t or SP.SlideTeeth()
  name = f"slide_teeth_{t.rr:.1f}_{t.z_axis:.2f}_{t.spoke[0]:.1f}_{t.spoke[1]:.1f}"
  teeth = PA.cached(name, lambda: SP.slide_teeth(t))
  mb = SP.motor_board()
  return {"teeth": teeth, "gear": PP.pop_motor_gear(), "gear_teeth_only": PP.pop_gear_teeth_only(),
          "carrier": SP.slide_carrier(), "block": SP.slide_block(),
          "motor": union([mb["motor"], mb["board+cap"], mb["car plug"], mb["motor plug"], mb["motor's own plug"]])}


# ***** the checks *****

def roller_drop(A: SlideAssembly, wheel_deg: float) -> float:
  """How far (mm) the carrier goes past on with the wheel turned wheel_deg: until the roller rests on the teeth piece's
  lead-in, or the pusher reaches its stop."""
  roller = PP.pop_roller()
  T = A.teeth(wheel_deg)
  most = drop_most()
  if overlap(A.place(roller, -most), T) <= 1e-3:
    return most
  lo, hi = 0.0, most
  for _ in range(22):
    mid = (lo + hi) / 2
    if overlap(A.place(roller, -mid), T) > 1e-3:
      hi = mid
    else:
      lo = mid
  return lo


def mesh_sweep(A: SlideAssembly, step: float = 1.0) -> dict:
  worst, at = 0.0, 0.0
  t = A.t
  for w in np.arange(-t.roll_half, t.roll_half + 1e-9, step):
    v = overlap(A.teeth(float(w)), A.gear(0.0, float(w)))
    if v > worst:
      worst, at = v, float(w)
  plays = []
  inner = t.n_teeth // 2 - 3
  for w in (0.0, 0.5 * t.pitch_deg, min(10, inner) * t.pitch_deg, -min(15, inner) * t.pitch_deg):
    T = A.teeth(w)
    res = []
    for sgn in (1, -1):
      a = 0.0
      while a < 10.0:
        g = A.place(A.p["gear_teeth_only"].rotate((0, 0, MESH_PHASE - FP.FACE_RATIO * w + sgn * (a + 0.05))))
        if overlap(T, g) > 1e-4:
          break
        a += 0.05
      res.append(round(a, 2))
    plays.append(res)
  return {"worst_overlap_mm3": round(worst, 4), "worst_at_deg": round(at, 1), "free_play_motor_gear_deg": plays,
          "free_play_steering_wheel_deg": round(min(min(p) for p in plays) * 2 / FP.FACE_RATIO, 3)}


def check_fit(A: SlideAssembly, wheel_step: float = 4.0, slide_step: float = 1.1) -> dict:
  """Overlap volumes (mm^3) between things that must not touch, for this assembly's key depth and mount angle."""
  res = {}
  T, W = A.teeth(), A.grip()
  movers_on = [("gear", A.gear()), ("carrier", A.carrier()), ("motor, board and plugs", A.motor()),
               ("rods and collars", A.rods()), ("latch lever", A.lever())]
  fixed = [("block", A.block()), ("pusher, bearings, switch", A.fixed_bits()), ("pull springs", A.springs())]
  car = A.car_parts()
  # on, wheel straight
  for mn, m in movers_on:
    if mn != "gear":
      res[f"on: teeth/{mn}"] = overlap(T, m)
    res[f"on: grip/{mn}"] = overlap(W, m)
    for fn, f in fixed:
      if (mn, fn) in (("rods and collars", "block"), ("rods and collars", "pusher, bearings, switch"),
                      ("rods and collars", "pull springs"), ("latch lever", "pusher, bearings, switch"),
                      ("carrier", "pusher, bearings, switch"), ("carrier", "block")):
        continue
      res[f"on: {mn}/{fn}"] = overlap(m, f)
    for cn, c in car:
      res[f"on: {mn}/{cn}"] = overlap(m, c)
  for fn, f in fixed:
    res[f"teeth/{fn}"] = overlap(T, f)
    for cn, c in car:
      res[f"{fn}/{cn}"] = overlap(f, c)
  # the carrier's tongue and the lever in the block: only where they should (the land on the switch's roller, the cam on
  # the pusher's nose); the carrier against the block: not with the motor on
  res["on: carrier/block"] = overlap(A.carrier(), A.block())
  # the wheel turned through the teeth and past them (motor on)
  t = A.t
  for w in np.arange(-t.half - 4.0, t.half + 4.0 + 1e-9, wheel_step):
    Tw = A.teeth(float(w))
    for name, part in movers_on[1:] + fixed:
      key = f"wheel turned, on: teeth/{name} (worst)"
      res[key] = max(res.get(key, 0.0), overlap(Tw, part))
  # past the teeth the carrier follows the roller down the lead-in, at most to the pusher's stop
  worst = 0.0
  for w in np.arange(t.roll_half, t.half + 1.0, 0.5):
    for sign in (1, -1):
      d = roller_drop(A, sign * float(w))
      for part in (A.gear(-d, 0.0, "gear_teeth_only"), A.carrier(-d), A.motor(-d), A.rods(-d), A.lever(-d)):
        worst = max(worst, overlap(A.teeth(sign * float(w)), part))
  res["lead-in, the carrier following the roller: teeth/gear teeth, carrier, motor, rods, lever (worst)"] = worst
  dm = drop_most()
  for side, w in (("left", t.half + 3.0), ("right", -t.half - 3.0)):
    Tw = A.teeth(w)
    for name, part in (("gear", A.gear(-dm)), ("carrier", A.carrier(-dm)), ("motor", A.motor(-dm)), ("lever", A.lever(-dm))):
      res[f"past the teeth ({side}), {dm:.1f} mm further on: teeth/{name}"] = overlap(Tw, part)
  for name, part in (("gear", A.gear(-dm)), ("carrier", A.carrier(-dm)), ("motor", A.motor(-dm)), ("lever", A.lever(-dm))):
    res[f"{dm:.1f} mm further on: grip/{name}"] = overlap(W, part)
    for cn, c in car:
      res[f"{dm:.1f} mm further on: {name}/{cn}"] = overlap(part, c)
  # sliding off with the lever swinging off, then slid off: the wheel straight and a little either way
  for off in list(np.arange(slide_step, SP.STROKE + 1e-6, slide_step)) + [SP.STROKE]:
    frac = off / SP.STROKE
    sw = SP.SWING_SIGN * SP.LEVER_SWING * frac
    parts = [("gear", A.gear(off)), ("carrier", A.carrier(off)), ("motor, board and plugs", A.motor(off)),
             ("rods and collars", A.rods(off)), ("latch lever", A.lever(off, sw))]
    for name, part in parts:
      for w in (0.0, -15.0, 15.0):
        key = f"sliding off: teeth/{name} (worst)"
        res[key] = max(res.get(key, 0.0), overlap(A.teeth(w), part))
      res[f"sliding off: grip/{name} (worst)"] = max(res.get(f"sliding off: grip/{name} (worst)", 0.0), overlap(W, part))
      for cn, c in car:
        key = f"sliding off: {name}/{cn} (worst)"
        res[key] = max(res.get(key, 0.0), overlap(part, c))
  # slid off, the latch lever swung through its whole travel
  sweep = A.lever_sweep(SP.STROKE)
  res["slid off, the lever's swing: teeth"] = overlap(T, sweep)
  res["slid off, the lever's swing: grip"] = overlap(W, sweep)
  for cn, c in car:
    res[f"slid off, the lever's swing: {cn}"] = overlap(sweep, c)
  for fn, f in fixed:
    if fn != "pusher, bearings, switch":
      res[f"slid off, the lever's swing: {fn}"] = overlap(sweep, f)
  # slid off: the teeth anywhere round the wheel must miss everything
  ring = A.teeth_ring()
  off = SP.STROKE
  for name, part in (("gear", A.gear(off)), ("carrier", A.carrier(off)), ("motor, board and plugs", A.motor(off)),
                     ("rods and collars", A.rods(off)), ("latch lever", A.lever(off, SP.SWING_SIGN * SP.LEVER_SWING)),
                     ("block", A.block()), ("pusher, bearings, switch", A.fixed_bits()), ("pull springs", A.springs(off))):
    res[f"slid off: the teeth anywhere round the wheel/{name}"] = overlap(ring, part)
  return res


def report_rows(res: dict, limit: float = 1e-3) -> list:
  return sorted([(k, v) for k, v in res.items() if v > limit], key=lambda kv: -kv[1])


def gaps_table(A: SlideAssembly) -> list:
  """The closest each moving part comes to the column cover, the back cover and the adjustment tab's room, on and slid
  off (mm; negative = overlap mm^3)."""
  car = dict(A.car_parts())
  rows = []
  for name, on, off in (("motor, board and plugs", A.motor(), A.motor(SP.STROKE)), ("carrier", A.carrier(), A.carrier(SP.STROKE)),
                        ("latch lever", A.lever(), A.lever(SP.STROKE, SP.SWING_SIGN * SP.LEVER_SWING)),
                        ("block", A.block(), A.block())):
    for cn in ("column cover", "back cover (it turns with the wheel)", "adjustment tab, its swing and your fingers on it"):
      rows.append((name, cn, min_gap(on, car[cn]), min_gap(off, car[cn])))
  return rows


def switch_states() -> list:
  """Where the switch's roller sits (mm from its holes' line) with the carrier this far off (mm): pressed with the
  motor on, let go a millimetre and a half off and further."""
  out = []
  for off in (-SP.PUSH_TRAVEL_ON, -1.0, 0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.5, SP.STROKE):
    land_from = SP.LAND_FROM + off
    if SP.SW_ROLL_Y >= land_from + SP.LAND_H:
      x = SP.TONGUE_X[1] + SP.LAND_H
    elif SP.SW_ROLL_Y <= land_from:
      x = SP.TONGUE_X[1]
    else:
      x = SP.TONGUE_X[1] + (SP.SW_ROLL_Y - land_from)
    pos = SP.SW_HOLES_X - x
    state = "pressed" if pos <= MP_SW["op"] - MP_SW["tol"] else ("let go" if pos >= MP_SW["op"] + MP_SW["tol"] + MP_SW["md"]
                                                               else "between")
    out.append((round(off, 2), round(pos, 2), state))
  return out


import mountparts as _MP  # noqa: E402

MP_SW = {"op": _MP.SW_OP, "tol": _MP.SW_OP_TOL, "md": _MP.SW_MD, "fp": _MP.SW_FP}


def latch_numbers() -> dict:
  """The latch's forces with the motor on: what holds the gear in, against what lane keeping's push takes."""
  from margins import RUB_DRY
  phi = math.radians(FP.GR.PRESSURE_ANGLE) if hasattr(FP, "GR") else math.radians(20.0)
  ft_lk = P.LANE_KEEPING_MOST_NM * 1000.0 / FP.R_F          # N at the teeth
  ft_most = P.MOST_TORQUE_NM * 1000.0 / FP.R_F
  sep_lk = ft_lk * math.tan(phi + math.atan(RUB_DRY))
  sep_most = ft_most * math.tan(phi + math.atan(RUB_DRY))
  pull_on = SP.release_force(0.0)
  weight_n = 0.45 * 9.81
  along = math.sin(math.radians(P.COLUMN_TILT))           # the column slopes down towards the dash
  brake = 0.8 * weight_n                                  # hard braking pushes it towards the dash too
  holds = SP.PUSH_ON - pull_on - weight_n * along - brake
  return {"pusher_on_N": SP.PUSH_ON, "pull_springs_on_N": round(pull_on, 1), "pull_springs_off_N": round(SP.release_force(SP.STROKE), 1),
          "weight_along_column_N": round(weight_n * along, 1), "hard_braking_N": round(brake, 1),
          "left_to_hold_the_gear_in_N": round(holds, 1), "teeth_separating_push_lane_keeping_N": round(sep_lk, 1),
          "teeth_separating_push_safety_limit_N": round(sep_most, 1),
          "factor_lane_keeping": round(holds / sep_lk, 2), "factor_safety_limit": round(holds / sep_most, 2),
          "pusher_spring_most_N": round(max(r["force_N"] for r in SP.cam_table(1.0)), 1),
          "pusher_spring_factor": round(SP.PSPRING["max"] / max(r["force_N"] for r in SP.cam_table(1.0)), 2),
          "handle_force_most_N": round(max(r["handle_N"] for r in SP.cam_table(1.0) if r["tip_to_tip"] == 0.0), 1),
          "handle_force_most_tip_to_tip_N": round(max(r["handle_N"] for r in SP.cam_table(1.0)), 1),
          "handle_force_to_switch_off_N": round(max(SP.cam_state(d)["torque"] for d in np.arange(0.0, SP.cam_peak()[0] + 0.01, 0.5))
                                                / SP.handle_len(), 1)}
