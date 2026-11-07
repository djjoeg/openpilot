"""
The side-slide mount put together, and the checks that it fits and works against the things known for a fact: our own
parts, the bought parts' catalogue sizes, and your steering wheel's measurements (372 mm across, 35.4 mm thick). The car
round it (the column covers, the key, the back cover) is only an estimate from photos: the report lists how close the
parts come to it as numbers to check, not as passes or fails.

  - the gear meshes the steering wheel teeth over their whole arc, motor in
  - nothing touches what it shouldn't while the motor slides in and out (every mm of the 40), only the latch's pin on
    the ear, the switch's roller on the ear's end, and the block on its rail
  - the steering wheel turned anywhere with the motor in: the teeth piece clear of everything but the gear
  - slid in: the teeth piece anywhere round the steering wheel misses everything, and nothing is left in the room your
    fingers take round the steering wheel
  - the fixed parts clear the steering wheel and the teeth piece at every angle, and your fingers
  - the forces: spring, weight, latch, switch

Frames: see popparts.py and sideparts.py.
"""
import math

import numpy as np
from manifold3d import Manifold

import faceparts as FP
import mountparts as MP
import params as P
import popassembly as PA
import popparts as PP
import sideparts as S
from cadlib import cyl, revolve, union

MESH_PHASE = PA.MESH_PHASE


def overlap(a: Manifold, b: Manifold) -> float:
  return (a ^ b).volume()


def gap(a: Manifold, b: Manifold, far: float = 20.0) -> float:
  v = overlap(a, b)
  return -round(v, 3) if v > 1e-3 else round(a.min_gap(b, far), 2)


def build_parts() -> dict:
  t = S.SideTeeth()
  name = f"side_teeth1_{t.rr:.1f}_{t.z_axis:.2f}_{t.spoke[0]:.1f}_{t.spoke[1]:.1f}_{S.ROOF_DEG:.0f}"
  teeth = PA.cached(name, lambda: S.side_teeth(t))
  mb = S.motor_board()
  return {"t": t, "teeth": teeth, "gear": S.side_gear(), "gear_teeth_only": S.side_gear_teeth_only(),
          "bracket": S.side_bracket(), "plate": S.side_plate(), "spool": S.side_spool(),
          "motor": union([mb["motor"], mb["board+cap"], mb["car plug"], mb["motor plug"], mb["motor's own plug"]]),
          "rail": S.rail(), "block": S.block(), "block screws": S.block_screws()}


class SideAssembly:
  def __init__(self, parts: dict = None, mount_deg: float = S.MOUNT_DEG):
    self.p = parts if parts is not None else build_parts()
    self.t = self.p["t"]
    self.mount = mount_deg

  # carrier frame
  def movers(self, s: float, wheel_deg: float = 0.0) -> dict:
    sp = S.spring_parts(s)
    gear = self.p["gear"].rotate((0, 0, MESH_PHASE - FP.FACE_RATIO * wheel_deg))
    return {"motor bracket": S.slid(self.p["bracket"], s), "motor, board and plugs": S.slid(self.p["motor"], s),
            "gear": S.slid(gear, s), "block": S.slid(self.p["block"], s), "block screws": S.slid(self.p["block screws"], s),
            "spring's clamp": sp["clamp"]}

  def fixed(self, s: float = 0.0) -> dict:
    """The fixed parts; the plunger's pin and the switch's roller where the ear leaves them with the motor slid in s."""
    pl = S.plunger(S.pin_back_at(s))
    roller_down = min(S.SW_HOLES_Z - S.EAR_Z[1] - (MP.SW_OP - MP.SW_PRESS) + s, MP.SW_FP - (MP.SW_OP - MP.SW_PRESS))
    sw = S.switch(roller_down)
    sp = S.spring_parts(s)
    return {"mounting plate": self.p["plate"], "rail": self.p["rail"], "plunger and nut": pl["fixed"],
            "plunger's knob": pl["knob"], "plunger's pin": pl["pin"], "switch": sw["body"],
            "switch's lever and roller": sw["lever"], "spring's coil and spool": sp["coil"] + self.p["spool"],
            "spool's screw": sp["axle"]}

  # steering wheel frame
  def W(self, m: Manifold) -> Manifold:
    return S.to_wheel(m, self.mount)

  def teeth(self, wheel_deg: float = 0.0) -> Manifold:
    return self.p["teeth"].rotate((0, 0, self.mount + wheel_deg))

  def teeth_ring(self) -> Manifold:
    """The teeth piece's cross-section all the way round: wherever it is when the steering wheel turns."""
    return revolve([(p[0], p[1]) for p in self.t.profile()], 0.0, 360.0, step_deg=1.0)

  def grip(self) -> Manifold:
    t = self.t
    pts = [(t.rr + (PP.GRIP_P / 2) * math.cos(a), (PP.GRIP_P / 2) * math.sin(a))
           for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    return revolve(pts, 0.0, 360.0, step_deg=1.0)

  def fingers(self) -> Manifold:
    t = self.t
    behind, inside, outside = PA.FINGERS
    return cyl(PP.WHEEL_OD_P / 2 + outside, behind, 0.0, segments=180) - \
      cyl(t.rr - PP.GRIP_P / 2 - inside, behind - 1, 1, segments=180)


# ***** the checks *****

EXPECTED = {("block", "rail"), ("motor bracket", "plunger's pin"), ("motor bracket", "switch's lever and roller"),
            ("block screws", "motor bracket")}


def internal(A: SideAssembly, steps=None) -> dict:
  """Moving against fixed parts at every slide position (carrier frame). Only the expected touches are left out:
  the block on its rail, the pin and the roller on the ear (they rest on it)."""
  steps = steps if steps is not None else sorted(set([0.0, 0.1, 0.2, 0.5] + list(np.arange(1.0, S.STROKE + 0.01, 1.0))))
  res = {}
  for s in steps:
    mv, fx = A.movers(s), A.fixed(s)
    for mn, m in mv.items():
      for fn, f in fx.items():
        if (mn, fn) in EXPECTED:
          continue
        v = overlap(m, f)
        key = f"{mn}/{fn}"
        if v > res.get(key, (0.0, None))[0]:
          res[key] = (v, s)
  # the pin and the roller: resting on the ear (touching), never into it
  for s in steps:
    mv, fx = A.movers(s), A.fixed(s)
    for fn in ("plunger's pin", "switch's lever and roller"):
      v = overlap(mv["motor bracket"], fx[fn].translate((-0.05 if fn == "plunger's pin" else 0.0, 0.0, 0.05 if fn != "plunger's pin" else 0.0)))
      key = f"motor bracket/{fn} (resting on it)"
      if v > res.get(key, (0.0, None))[0]:
        res[key] = (v, s)
  # moving parts against each other: the bracket and the motor, the block screws' heads in their pockets
  mv = A.movers(0.0)
  for a, b in (("motor bracket", "motor, board and plugs"), ("gear", "motor bracket"), ("gear", "motor, board and plugs"),
               ("spring's clamp", "motor, board and plugs")):
    res[f"{a}/{b} (both move)"] = (overlap(mv[a], mv[b]), 0.0)
  # the stops: pulled out 0.2 past the latch the ear meets the stop; slid in 40 the flange meets the bumper
  out = A.movers(-S.STOP_GAP)
  res["pulled out against the stop: motor bracket/mounting plate (touching)"] = (overlap(out["motor bracket"], A.p["plate"]), -S.STOP_GAP)
  res["pulled out against the stop: other parts/mounting plate"] = (max(overlap(out[k], A.p["plate"]) for k in out if k != "motor bracket"), -S.STOP_GAP)
  res["pulled out against the stop: gear/mounting plate"] = (overlap(out["gear"], A.p["plate"]), -S.STOP_GAP)
  return res


def touching_at_stops(A: SideAssembly) -> dict:
  """How close the stops come: pulled out, the ear's end to the stop; slid in, the flange's end to the bumper (mm)."""
  out = A.movers(-S.STOP_GAP + 0.01)
  inn = A.movers(S.STROKE - 0.01)
  return {"ear to the outer stop, pulled out": round(out["motor bracket"].min_gap(A.p["plate"], 5.0), 3),
          "flange to the bumper, slid in 40": round(inn["motor bracket"].min_gap(A.p["plate"], 5.0), 3),
          "block's end to the bumper, slid in 40": round(inn["block"].min_gap(A.p["plate"], 5.0), 3),
          "block's ends to the rail's ends (in, out)": (round(S.BLOCK_Z[0] - S.STROKE - S.Z_RAIL[0], 2),
                                                        round(S.Z_RAIL[1] - S.BLOCK_Z[1], 2))}


def mesh_sweep(A: SideAssembly, step: float = 0.5) -> dict:
  t = A.t
  T0 = A.p["teeth"]
  worst, at = 0.0, 0.0
  g0 = A.p["gear_teeth_only"]
  for w in np.arange(-t.teeth_half, t.teeth_half + 1e-9, step):
    T = A.teeth(float(w))
    g = A.W(g0.rotate((0, 0, MESH_PHASE - FP.FACE_RATIO * float(w))))
    v = overlap(T, g)
    if v > worst:
      worst, at = v, float(w)
  plays = []
  inner = t.n_teeth // 2 - 3
  for w in (0.0, 0.5 * t.pitch_deg, inner * t.pitch_deg, -inner * t.pitch_deg):
    T = A.teeth(w)
    res = []
    for sgn in (1, -1):
      a = 0.0
      while a < 10.0:
        g = A.W(g0.rotate((0, 0, MESH_PHASE - FP.FACE_RATIO * w + sgn * (a + 0.05))))
        if overlap(T, g) > 1e-4:
          break
        a += 0.05
      res.append(round(a, 2))
    plays.append(res)
  return {"worst_overlap_mm3": round(worst, 4), "worst_at_deg": round(at, 1), "free_play_motor_gear_deg": plays,
          "free_play_steering_wheel_deg": round(min(min(p) for p in plays) * 2 / FP.FACE_RATIO, 3)}


def slide_out_of_teeth(A: SideAssembly, step: float = 0.5) -> dict:
  """The gear sliding in (out of the teeth) and back out (into them), the steering wheel at a few angles across the
  teeth, the gear lined up with them: it moves along the tooth gaps without touching."""
  t = A.t
  worst, at = 0.0, None
  g0 = A.p["gear_teeth_only"]
  for w in (0.0, 0.5 * t.pitch_deg, 3 * t.pitch_deg + 0.3, -(t.n_teeth // 2 - 1) * t.pitch_deg):
    T = A.teeth(w)
    for s in np.arange(0.0, 14.0 + 1e-9, step):
      g = A.W(S.slid(g0.rotate((0, 0, MESH_PHASE - FP.FACE_RATIO * w)), float(s)))
      v = overlap(T, g)
      if v > worst:
        worst, at = v, (round(w, 2), float(s))
  return {"worst_overlap_mm3": round(worst, 4), "at_wheel_deg_and_slide_mm": at}


def wheel_turned(A: SideAssembly, step: float = 2.0) -> dict:
  """Motor in, the steering wheel turned through and past the teeth piece: the teeth piece against everything but the
  gear; the gear (free past the teeth: any phase) against the teeth piece past the last tooth."""
  t = A.t
  res = {}
  mv = {k: A.W(v) for k, v in A.movers(0.0).items() if k != "gear"}
  fx = {k: A.W(v) for k, v in A.fixed(0.0).items()}
  for w in np.arange(-t.half - 6.0, t.half + 6.0 + 1e-9, step):
    T = A.teeth(float(w))
    for name, part in list(mv.items()) + list(fx.items()):
      key = f"teeth piece/{name}"
      v = overlap(T, part)
      if v > res.get(key, (0.0, None))[0]:
        res[key] = (v, round(float(w), 1))
  # past the teeth: the gear stops where it left them; the steering wheel turns on. Any phase.
  g0 = A.p["gear"]
  worst, at = 0.0, None
  last = t.teeth_half + 0.6 * t.pitch_deg            # past the last tooth's tip
  for w in list(np.arange(last, t.half + 6.0, 1.0)):
    for sign in (1, -1):
      T = A.teeth(sign * float(w))
      for ph in np.arange(0.0, 22.5, 2.5):
        v = overlap(T, A.W(g0.rotate((0, 0, ph))))
        if v > worst:
          worst, at = v, (sign * round(float(w), 1), float(ph))
  res["past the teeth: gear at any phase/teeth piece"] = (worst, at)
  return res


def end_teeth_meeting(A: SideAssembly) -> dict:
  """Coming back onto the teeth from past their end, the free gear meets the two lowered end teeth first: how much of
  it they reach (the most overlap if it did not turn), at the worst phase. They turn it into step; the full teeth then
  carry on."""
  t = A.t
  g0 = A.p["gear"]
  n = t.n_teeth // 2
  out = {}
  for k, label in ((n - 0.5, "the last tooth (lowered most)"), (n - 1.5, "the next (lowered less)")):
    worst = 0.0
    for sign in (1, -1):
      w = sign * k * t.pitch_deg
      T = A.teeth(w)
      for ph in np.arange(0.0, 22.5, 1.5):
        worst = max(worst, overlap(T, A.W(g0.rotate((0, 0, ph)))))
    out[label] = round(worst, 2)
  return out


def slid_in(A: SideAssembly) -> dict:
  """Slid in 40 mm: the teeth piece anywhere round the steering wheel, the steering wheel and your fingers against every
  moving part; the fixed parts against them at any time."""
  ring, grip, fingers = A.teeth_ring(), A.grip(), A.fingers()
  res = {}
  for name, part in A.movers(S.STROKE).items():
    P_ = A.W(part)
    res[f"slid in: teeth piece anywhere round/{name}"] = overlap(ring, P_)
    res[f"slid in: steering wheel/{name}"] = overlap(grip, P_)
    res[f"slid in: your fingers round the steering wheel/{name}"] = overlap(fingers, P_)
  for name, part in A.fixed(S.STROKE).items():
    P_ = A.W(part)
    res[f"fixed: teeth piece anywhere round/{name}"] = overlap(ring, P_)
    res[f"fixed: steering wheel/{name}"] = overlap(grip, P_)
    res[f"fixed: your fingers round the steering wheel/{name}"] = overlap(fingers, P_)
  # sliding: everything but the gear (inside the teeth's gaps for the first 13 mm) against the teeth piece anywhere round
  worst = {}
  for s in np.arange(0.0, S.STROKE + 0.01, 2.0):
    for name, part in A.movers(float(s)).items():
      if name == "gear" and s < 13.0:
        continue
      v = overlap(ring, A.W(part))
      if v > worst.get(name, (0.0, None))[0]:
        worst[name] = (v, float(s))
      v = overlap(grip, A.W(part))
      if v > worst.get(name + " (steering wheel)", (0.0, None))[0]:
        worst[name + " (steering wheel)"] = (v, float(s))
  for k, v in worst.items():
    res[f"sliding: teeth piece anywhere round/{k} (worst)"] = v[0]
  return res


def clearances(A: SideAssembly) -> list:
  """Closest approach (mm) of each moving part to the fixed parts over the slide, and of everything to the steering
  wheel and the teeth piece."""
  rows = []
  ring = A.teeth_ring()
  fingers = A.fingers()
  for s, tag in ((0.0, "motor in"), (S.STROKE, "slid in")):
    for name, part in A.movers(s).items():
      if name == "gear" and s == 0.0:
        continue
      P_ = A.W(part)
      rows.append((tag, name, "teeth piece anywhere round", gap(P_, ring)))
      if s == S.STROKE:
        rows.append((tag, name, "your fingers' room", gap(P_, fingers)))
  for name, part in A.fixed(0.0).items():
    P_ = A.W(part)
    rows.append(("fixed", name, "teeth piece anywhere round", gap(P_, ring)))
    rows.append(("fixed", name, "your fingers' room", gap(P_, fingers)))
  return rows


def forces() -> dict:
  """The spring, the weight along the slide, the latch and the switch."""
  m_moving = 0.31 + 0.035 + 0.045 + 0.010 + 0.040        # motor, board and cover, bracket (PETG, about), gear, block (kg)
  w = m_moving * 9.81
  # the slide's direction in the car: out along the shaft at 5:20, on a steering wheel tilted COLUMN_TILT from upright
  a = math.radians(S.MOUNT_DEG)
  out_dir_wheel = np.array([math.cos(a), math.sin(a), 0.0])
  tilt = math.radians(P.COLUMN_TILT)
  up_of = {"x": 0.0, "y": math.cos(tilt), "z": math.sin(tilt)}   # the wheel frame's axes' upward parts
  up = out_dir_wheel[0] * up_of["x"] + out_dir_wheel[1] * up_of["y"] + out_dir_wheel[2] * up_of["z"]
  weight_out = -up * w                                  # the weight's pull outwards along the slide (towards the teeth)
  spring = S.CF["load_N"]
  rail_rub = 0.5                                         # the block's own drag, about (preloaded MGN12: a few tenths of a N)
  pin = S.KIPP["push_N"]
  pin_at = lambda back: pin[0] + (pin[1] - pin[0]) * back / S.KIPP["pin_out"]
  rub = 0.3                                              # steel pin on the printed ear, dry (about)
  pin_on_flat = pin_at(S.PIN_IN)
  ramp = math.tan(math.radians(S.BEVEL_DEG))
  pin_ramp_push = pin_at(S.PIN_IN) * (ramp + rub) / (1 - rub * ramp)
  net_in = spring - weight_out - rail_rub
  ext_in = S.CLAMP_Z - S.STROKE - S.SPOOL_Z
  ext_out = S.CLAMP_Z - S.SPOOL_Z
  v_end = math.sqrt(max(0.0, 2 * (net_in - pin_on_flat * rub * 0.25) * S.STROKE / 1000.0 / m_moving))
  return {
    "moving mass (kg, about)": round(m_moving, 3),
    "weight along the slide, outwards (N)": round(weight_out, 2),
    "spring's pull (N)": spring,
    "left to pull it in, after its weight and the block's drag (N)": round(net_in, 2),
    "it stays in until the car bumps up at (g on top of gravity)": round(net_in / (m_moving * 9.81 * -up) - 1.0, 2),
    "your pull to bring it out: spring less weight plus drag (N)": round(spring - weight_out + rail_rub, 1),
    "... while the ramp pushes the pin back (N, most)": round(spring - weight_out + rail_rub + pin_ramp_push, 1),
    "the latch holds against (N)": round(spring - weight_out, 1),
    "plunger's pin pushes on the ear with (N), out / on the flat": (pin[0], round(pin_on_flat, 1)),
    "strip pulled out, motor in / slid in (mm); Lee: at least 31.5": (round(ext_out, 1), round(ext_in, 1)),
    "spring's drum (mm), Lee: 10-20% over 14.99": (S.DRUM_D, round(S.DRUM_D / S.CF["id"] - 1, 3)),
    "speed it reaches the bumper if let go (m/s, about)": round(v_end, 2),
    "spring's life (cycles in and out, Lee)": S.CF["life"],
  }


def switch_states() -> list:
  """The switch's roller with the motor slid in s mm: how far it has come out from where it sits with the motor in (set
  0.6 mm past its click). It lets go once that passes 0.6 mm plus its let-go travel (up to 1.0 mm by Omron's table)."""
  out = []
  press = MP.SW_PRESS
  md = 1.0
  for s in (0.0, 0.5, 1.0, 1.5, 1.6, 2.0, 3.0, 5.0, 10.0, S.STROKE):
    back = min(s, MP.SW_FP - (MP.SW_OP - press))
    state = "pressed (on)" if back < press + 1e-9 else ("let go (off)" if back >= press + md else "on or off")
    out.append((s, round(back, 2), state))
  return out


def car_estimates(A: SideAssembly, D: float = None) -> list:
  """How close the parts come to the car round them as rebuilt from the photos (estimates, for you to check)."""
  import carscene as CS
  sc = CS.CarScene(D if D is not None else CS.D_REF)
  car = [("column cover", sc.column_cover()), ("back cover (turns with the wheel)", sc.back_cover())]
  for k, v in sc.key_parts().items():
    car.append((k, v))
  rows = []
  for s, tag in ((0.0, "motor in"), (S.STROKE, "slid in")):
    mv = A.movers(s)
    for name in ("motor, board and plugs", "motor bracket"):
      P_ = A.W(mv[name])
      for cn, c in car:
        rows.append((tag, name, cn, gap(P_, c, 40.0)))
  for name in ("mounting plate", "plunger's knob", "spring's coil and spool"):
    P_ = A.W(A.fixed(0.0)[name])
    for cn, c in car:
      rows.append(("fixed", name, cn, gap(P_, c, 40.0)))
  return rows
