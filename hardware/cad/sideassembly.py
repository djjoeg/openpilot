"""
The side-slide mount put together, and the checks that it fits and works against the things known for a fact: our own
parts, the bought parts' catalogue sizes, and your steering wheel's measurements (372 mm across, 35.4 mm thick). The car
round it (the column covers, the key, the back cover) is only an estimate from photos: the report lists how close the
parts come to it as numbers to check, not as passes or fails.

  - the gear meshes the steering wheel teeth over their whole arc, motor in
  - nothing touches what it shouldn't while the motor slides in and out (every mm of the 40), only the switch's roller
    on the ear's end, and the block on its rail; the lever's arm runs in its slot in the plate without touching it
  - the lever swings between its slot and either notch without touching anything, and once in a notch the plate holds
    it: latched, the motor can't slide in; parked, it can't slide out
  - the steering wheel turned anywhere with the motor in: the teeth piece clear of everything but the gear
  - slid in: the teeth piece anywhere round the steering wheel misses everything, and nothing is left in the room your
    fingers take round the steering wheel
  - the fixed parts clear the steering wheel and the teeth piece at every angle, and your fingers
  - the forces: spring, weight, the lever, switch; what keeps the lever in its notches against its own weight

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
import slideparts as SP
from cadlib import cyl, revolve, union

MESH_PHASE = PA.MESH_PHASE
PLATE_MID_X = (S.X_PL[0] + S.X_PL[1]) / 2               # the notch's floor holds the lever's arm across the plate's thickness
PLATE_OUT_X_D = S.PIVOT[0] - S.X_PL[0]                  # ... out to the plate's outer face, this far from the screw
# motor, board and cover, bracket (PETG, about), gear, block, lever (kg)
MOVING_KG = 0.31 + 0.035 + 0.045 + 0.010 + 0.040 + 0.013
# plate with its foot, rail, spool and spring, switch, bar and shims, screws (kg, about)
FIXED_KG = 0.06 + 0.065 + 0.025 + 0.01 + 0.02 + 0.02
RAIL_RUB = 0.5                                          # the block's own drag, about (preloaded MGN12: a few tenths of a N)
PETG_KG_PER_MM3 = 1.28e-6                               # Bambu Lab PETG HF data sheet (V1.0): 1.28 g/cm3
BRAKE_G = 0.8                                           # braking hard, in times gravity (an estimate on the high side)


def overlap(a: Manifold, b: Manifold) -> float:
  return (a ^ b).volume()


def gap(a: Manifold, b: Manifold, far: float = 20.0) -> float:
  v = overlap(a, b)
  return -round(v, 3) if v > 1e-3 else round(a.min_gap(b, far), 2)


def volume_centre(m: Manifold) -> tuple:
  """A solid's volume (mm3) and the middle of its volume (mm), from its surface's triangles."""
  mesh = m.to_mesh()
  v = np.asarray(mesh.vert_properties)[:, :3].astype(float)
  tri = np.asarray(mesh.tri_verts)
  a, b, c = v[tri[:, 0]], v[tri[:, 1]], v[tri[:, 2]]
  six = np.einsum("ij,ij->i", a, np.cross(b, c))        # six times each triangle's cone to the origin, signed
  return six.sum() / 6.0, (six[:, None] * (a + b + c)).sum(axis=0) / (4.0 * six.sum())


def lever_holds() -> dict:
  """The lever's own weight against what keeps it in a notch, each as a push at the knob (N): standing still, and
  braking hard. Gravity leans towards the dash here (the column slopes down towards it), so the lever's weight swings
  it towards its slot, out of a notch; braking leans it further. Latched, the spring's pull (less the motor's weight)
  presses the arm on the notch's floor; parked with no spring, the motor's weight presses it on the inner notch's side.
  A positive "own" swings it towards its slot."""
  import margins as MG
  a = math.radians(P.COLUMN_TILT)
  up_w = np.array([0.0, math.cos(a), math.sin(a)])       # steering wheel frame: z along the column towards the driver
  nose_w = np.array([0.0, math.sin(a), -math.cos(a)])    # level, towards the car's nose
  R = PP.rot_z(S.MOUNT_DEG) @ PP.R_POP                   # carrier frame -> steering wheel frame
  vol, cen = volume_centre(S.side_lever())
  m_lever = vol * PETG_KG_PER_MM3
  ax, ay = cen[0] - S.PIVOT[0], cen[1] - S.PIVOT[1]
  d_floor = abs(PLATE_MID_X - S.PIVOT[0])
  out = {"lever (g, solid)": round(m_lever * 1000.0, 1)}
  for name, brake in (("still", 0.0), ("braking", BRAKE_G)):
    g = 9.81 * (R.T @ (-up_w + brake * nose_w))         # what the parts feel, carrier frame (m/s2)
    turn = m_lever * (ax * g[1] - ay * g[0])             # N mm about the screw; below 0 it swings towards the slot
    weight_out = MOVING_KG * g[2]                         # the moving parts' weight along the slide, outwards (N)
    out[name] = {"own": -turn / S.KNOB_D,
                 "latched": MG.RUB_DRY * (S.CF["load_N"] - weight_out) * d_floor / S.KNOB_D,
                 "parked_no_spring": MG.RUB_DRY * max(0.0, weight_out - RAIL_RUB) * d_floor / S.KNOB_D}
  return out


def teeth_set(n_teeth: int) -> dict:
  t = S.SideTeeth(n_teeth=n_teeth)
  name = f"side_teeth3_{n_teeth}_{t.rr:.1f}_{t.z_axis:.2f}_{t.spoke[0]:.1f}_{t.spoke[1]:.1f}_{S.ROOF_DEG:.0f}"
  return {"t": t, "teeth": PA.cached(name, lambda: S.side_teeth(t))}


def build_parts(sets=tuple(S.TEETH_SETS)) -> dict:
  """The mount's parts (carrier frame) and the teeth sets; "t" and "teeth" are the 14-tooth set's."""
  mb = S.motor_board()
  out = {"gear": S.side_gear(), "gear_teeth_only": S.side_gear_teeth_only(),
         "bracket": S.side_bracket(), "plate": S.side_plate(), "spool": S.side_spool(),
         "motor": union([mb["motor"], mb["board+cap"], mb["car plug"], mb["motor plug"], mb["motor's own plug"]]),
         "rail": S.rail(), "block": S.block(), "block screws": S.block_screws(), "lever": S.side_lever(),
         "lever's screw": S.lever_screw(), "foot bar": S.foot_bar(), "foot shim": S.foot_shim(),
         "sets": {n: teeth_set(n) for n in sets}}
  main = FP.N_TEETH_SHORT if FP.N_TEETH_SHORT in out["sets"] else next(iter(out["sets"]))
  out["t"], out["teeth"] = out["sets"][main]["t"], out["sets"][main]["teeth"]
  return out


class SideAssembly:
  def __init__(self, parts: dict | None = None, mount_deg: float = S.MOUNT_DEG, n_teeth: int | None = None):
    self.p = parts if parts is not None else build_parts()
    if n_teeth is not None:
      self.p = dict(self.p, t=self.p["sets"][n_teeth]["t"], teeth=self.p["sets"][n_teeth]["teeth"])
    self.t = self.p["t"]
    self.mount = mount_deg

  # carrier frame
  def movers(self, s: float, wheel_deg: float = 0.0, lever_deg: float = S.SLOT_DEG) -> dict:
    """The moving parts, slid in s; the lever swung lever_deg towards the dash (S.SLOT_DEG: in its slot, 0: in a notch,
    latched or parked)."""
    sp = S.spring_parts(s)
    gear = self.p["gear"].rotate((0, 0, MESH_PHASE - FP.FACE_RATIO * wheel_deg))
    return {"motor bracket": S.slid(self.p["bracket"], s), "motor, board and plugs": S.slid(self.p["motor"], s),
            "gear": S.slid(gear, s), "block": S.slid(self.p["block"], s), "block screws": S.slid(self.p["block screws"], s),
            "spring's clamp": sp["clamp"], "lever": S.lever_at(self.p["lever"], s, lever_deg),
            "lever's screw": S.slid(self.p["lever's screw"], s)}

  def fixed(self, s: float = 0.0) -> dict:
    """The fixed parts; the switch's roller where the ear leaves it with the motor slid in s."""
    roller_down = min(S.SW_HOLES_Z - S.EAR_Z[1] - (MP.SW_OP - MP.SW_PRESS) + s, MP.SW_FP - (MP.SW_OP - MP.SW_PRESS))
    sw = S.switch(roller_down)
    sp = S.spring_parts(s)
    return {"mounting plate": self.p["plate"], "rail": self.p["rail"], "switch": sw["body"],
            "switch's lever and roller": sw["lever"], "spring's coil and spool": sp["coil"] + self.p["spool"].translate((S.SPOOL_X, 0.0, S.SPOOL_Z)),
            "spool's screw": sp["axle"], "foot bar (anywhere along the window)": S.foot_bar_sweep()}

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

EXPECTED = {("block", "rail"), ("motor bracket", "switch's lever and roller"), ("block screws", "motor bracket")}
FOOT_PARTS = ("mounting plate", "foot bar (anywhere along the window)")


def internal(A: SideAssembly, steps=None) -> dict:
  """Moving against fixed parts at every slide position (carrier frame), the lever in its slot. Only the expected
  touches are left out: the block on its rail, the switch's roller on the ear (it rests on it)."""
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
  # the switch's roller: resting on the ear's end (touching), never into it
  for s in steps:
    mv, fx = A.movers(s), A.fixed(s)
    v = overlap(mv["motor bracket"], fx["switch's lever and roller"].translate((0.0, 0.0, 0.05)))
    key = "motor bracket/switch's lever and roller (resting on it)"
    if v > res.get(key, (0.0, None))[0]:
      res[key] = (v, s)
  # the spring's strip (it runs from the coil to the clamp) against everything but its coil and the tab it is clamped to
  for s in steps:
    strip = S.spring_parts(s)["strip"]
    mv, fx = A.movers(s), A.fixed(s)
    for name, part in list(mv.items()) + list(fx.items()):
      if name in ("spring's coil and spool", "spring's clamp"):
        continue
      v = overlap(strip.translate((-0.05, 0, 0)), part) if name == "motor bracket" else overlap(strip, part)
      key = f"spring's strip/{name}"
      if v > res.get(key, (0.0, None))[0]:
        res[key] = (v, s)
  # moving parts against each other: the bracket and the motor, the block screws' heads in their pockets
  mv = A.movers(0.0)
  for a, b in (("motor bracket", "motor, board and plugs"), ("gear", "motor bracket"), ("gear", "motor, board and plugs"),
               ("spring's clamp", "motor, board and plugs"), ("lever", "motor bracket"), ("lever", "motor, board and plugs"),
               ("lever", "lever's screw"), ("motor bracket", "lever's screw")):
    res[f"{a}/{b} (both move)"] = (overlap(mv[a], mv[b]), 0.0)
  for deg in np.arange(0.0, S.SLOT_DEG + 0.01, 3.0):
    mv = A.movers(0.0, lever_deg=float(deg))
    for b in ("motor bracket", "motor, board and plugs"):
      key = f"lever/{b} (both move, the lever swung)"
      res[key] = (max(res.get(key, (0.0, None))[0], overlap(mv["lever"], mv[b])), float(deg))
  # the stops: pulled out 0.2 past the latch the ear meets the stop; slid in 40 the flange meets the bumper
  out = A.movers(-S.STOP_GAP)
  res["pulled out against the stop: motor bracket/mounting plate (touching)"] = (overlap(out["motor bracket"], A.p["plate"]), -S.STOP_GAP)
  res["pulled out against the stop: other parts/mounting plate"] = (max(overlap(out[k], A.p["plate"]) for k in out
                                                                         if k not in ("motor bracket", "lever")), -S.STOP_GAP)
  res["pulled out against the stop: lever/mounting plate"] = (overlap(out["lever"], A.p["plate"]), -S.STOP_GAP)
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


def lever_notches(A: SideAssembly, step: float = 3.0) -> dict:
  """The lever swinging between its slot and each notch: against every fixed part, at the two ends of the slide it can
  be at there (latched: from resting on the notch's floor to pulled out against the stop; parked: from resting on the
  notch's outer face to on the bumper). Then what the notches hold: latched and pushed in 0.3 mm, or parked and pulled
  out 0.3, the plate stops the lever (an overlap means it can't go there); swung into the slot, it slides freely."""
  out = {"swinging into the notches (worst overlap, mm3)": 0.0}
  for s in (-S.STOP_GAP, 0.0, S.STROKE, S.STROKE + 0.2):
    fx = A.fixed(s)
    for deg in np.arange(0.0, S.SLOT_DEG + 0.01, step):
      lv = S.lever_at(A.p["lever"], s, float(deg))
      for name, part in fx.items():
        v = overlap(lv, part)
        if v > out["swinging into the notches (worst overlap, mm3)"]:
          out["swinging into the notches (worst overlap, mm3)"] = v
          out["... where"] = (name, s, float(deg))
  plate, lv = A.p["plate"], A.p["lever"]
  out["latched, pushed in 0.3 mm: the plate stops it (mm3 it would go into the plate)"] = round(
    overlap(S.lever_at(lv, 0.3), plate), 2)
  out["parked, pulled out 0.3 mm: the plate stops it (mm3)"] = round(overlap(S.lever_at(lv, S.STROKE - 0.3), plate), 2)
  out["swung into the slot, it slides: worst overlap with the plate (mm3)"] = round(
    max(overlap(S.lever_at(lv, float(s), S.SLOT_DEG), plate) for s in np.arange(-S.STOP_GAP, S.STROKE + 0.21, 0.5)), 4)
  out["latched, resting on the notch's floor: gap (mm)"] = round(S.lever_at(lv, 0.0).min_gap(plate, 2.0), 3)
  return out


def mesh_sweep(A: SideAssembly, step: float = 0.5) -> dict:
  t = A.t
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
  gear (the lever latched, and in its slot as when you latch it); the gear (free past the teeth: any phase) against the
  teeth piece past the last tooth."""
  t = A.t
  res = {}
  mv = {k: A.W(v) for k, v in A.movers(0.0, lever_deg=0.0).items() if k != "gear"}
  mv["lever, in its slot"] = A.W(A.movers(0.0)["lever"])
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
  slid = A.movers(S.STROKE)
  slid["lever, parked"] = A.movers(S.STROKE, lever_deg=0.0)["lever"]
  for name, part in slid.items():
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
  for s, deg, tag in ((0.0, 0.0, "motor in"), (S.STROKE, S.SLOT_DEG, "slid in"), (S.STROKE, 0.0, "parked")):
    for name, part in A.movers(s, lever_deg=deg).items():
      if (name == "gear" and s == 0.0) or (tag == "parked" and name != "lever"):
        continue
      P_ = A.W(part)
      rows.append((tag, name, "teeth piece anywhere round", gap(P_, ring)))
      if s == S.STROKE or name == "lever":
        rows.append((tag, name, "your fingers' room", gap(P_, fingers)))
  for name, part in A.fixed(0.0).items():
    P_ = A.W(part)
    rows.append(("fixed", name, "teeth piece anywhere round", gap(P_, ring)))
    rows.append(("fixed", name, "your fingers' room", gap(P_, fingers)))
  return rows


def forces() -> dict:
  """The spring, the weight along the slide, the latch and the switch."""
  m_moving = MOVING_KG
  w = m_moving * 9.81
  # the slide's direction in the car: out along the shaft at 5:20, on a steering wheel tilted COLUMN_TILT from upright
  a = math.radians(S.MOUNT_DEG)
  out_dir_wheel = np.array([math.cos(a), math.sin(a), 0.0])
  tilt = math.radians(P.COLUMN_TILT)
  up_of = {"x": 0.0, "y": math.cos(tilt), "z": math.sin(tilt)}   # the wheel frame's axes' upward parts
  up = out_dir_wheel[0] * up_of["x"] + out_dir_wheel[1] * up_of["y"] + out_dir_wheel[2] * up_of["z"]
  weight_out = -up * w                                  # the weight's pull outwards along the slide (towards the teeth)
  spring = S.CF["load_N"]
  rail_rub = RAIL_RUB
  import margins as MG
  rub = MG.RUB_DRY                                       # printed lever on the printed notch, dry
  net_in = spring - weight_out - rail_rub
  ext_in = S.CLAMP_Z - S.STROKE - S.SPOOL_Z
  ext_out = S.CLAMP_Z - S.SPOOL_Z
  # let go: the spring pulls it in, the lever riding along in its slot
  v_end = math.sqrt(max(0.0, 2 * net_in * S.STROKE / 1000.0 / m_moving))
  # swinging the lever out of its notch: the spring (less the weight) presses its arm on the notch's floor; the rub
  # there, at the middle of the plate's thickness, against the knob
  d_floor = math.hypot(PLATE_MID_X - S.PIVOT[0], 0.0)
  flick = rub * (spring - weight_out) * d_floor / S.KNOB_D
  holds = lever_holds()["still"]
  return {
    "moving mass (kg, about)": round(m_moving, 3),
    "weight along the slide, outwards (N)": round(weight_out, 2),
    "spring's pull (N)": spring,
    "left to pull it in, after its weight and the block's drag (N)": round(net_in, 2),
    "slid in, it stays in until a bump throws it outwards at (g, on top of gravity)": round(net_in / (m_moving * 9.81 * -up), 2),
    "your pull on the lever to bring it out: spring less weight plus drag (N)": round(spring - weight_out + rail_rub, 1),
    "your push on the lever to slide it in, if the spring doesn't: weight plus drag (N)": round(weight_out + rail_rub, 1),
    "latched, the notch holds against (N)": round(spring - weight_out, 1),
    "swinging the lever out of its notch, at the knob (N, about)": round(flick, 1),
    "the lever's own weight swings it towards its slot, at the knob (N, about)": round(holds["own"], 2),
    "latched, a jolt along the slide lifts the lever off the notch's floor from (g, on top of gravity)":
      round((spring - weight_out) / (m_moving * 9.81 * -up), 2),
    "parked with no spring: the motor's weight holds the lever in the inner notch; swinging it out (N at the knob, about)":
      round(holds["parked_no_spring"], 2),
    "strip pulled out, motor in / slid in (mm); Lee: at least 31.5": (round(ext_out, 1), round(ext_in, 1)),
    "spring's drum (mm), Lee: 10-20% over 14.99": (S.DRUM_D, round(S.DRUM_D / S.CF["id"] - 1, 3)),
    "speed it hits the bumper at, let go (m/s, about)": round(v_end, 2),
    "... its energy then (J)": round(0.5 * m_moving * v_end ** 2, 2),
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


def car_estimates(A: SideAssembly, D: float | None = None) -> list:
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
  for s, deg, tag in ((0.0, 0.0, "latched"), (S.STROKE, S.SLOT_DEG, "slid in")):
    P_ = A.W(A.movers(s, lever_deg=deg)["lever"])
    for cn, c in car:
      rows.append((tag, "lever", cn, gap(P_, c, 40.0)))
  for name in ("mounting plate", "spring's coil and spool", "foot bar (anywhere along the window)"):
    P_ = A.W(A.fixed(0.0)[name])
    for cn, c in car:
      rows.append(("fixed", name, cn, gap(P_, c, 40.0)))
  return rows


def foot_fit(D: float) -> dict:
  """Where the cover's screw and its underside fall against the foot and its window for one value of carscene.D: the
  screw inside the window (with the mount turned up to 3 degrees either way, and the screw's place 4 mm off either
  way), and how many shims fill the gap from the foot's top to the underside."""
  import carscene as CS
  sc = CS.CarScene(D)
  cup = sc.p["CUP"]
  r_cup = math.hypot(cup[0], sc.cover_bottom)
  swing = r_cup * math.sin(math.radians(SP.MOUNT_ADJ_S[0]))        # the window moves this far across when the mount turns
  tol = 4.0
  x_room = (cup[0] - tol - swing - S.WINDOW_X[0], S.WINDOW_X[1] - (cup[0] + tol + swing))
  z_room = (cup[2] - tol - S.WINDOW_Z[0], S.WINDOW_Z[1] - (cup[2] + tol))
  gap_y = sc.cover_bottom - S.FOOT_Y[1]
  return {"D": D, "cover's front edge behind the back of the round part (mm)": round(-sc.cover_front_z - 17.7, 1),
          "screw (x, z)": (round(float(cup[0]), 1), round(float(cup[2]), 1)), "underside y": round(sc.cover_bottom, 1),
          "room left in the window across (mm, either way)": tuple(round(v, 1) for v in x_room),
          "room left along (mm, either way)": tuple(round(v, 1) for v in z_room),
          "gap over the foot (mm)": round(gap_y, 1), "shims": round(gap_y / S.SHIM_T)}


def foot_margins() -> list:
  """The foot on the lower column cover's screw: what the screw holds, the twist the foot's rub holds, the foot and the
  bar themselves."""
  import margins as MG
  g = "Side-slide mount"
  k = MG.motor_k()
  ft_most = P.BOARD_MAX_A * k / (FP.R_P / 1000.0)
  # where things are, steering wheel frame: the gear's teeth, the screw (its window's middle), the foot's front edge
  gear = S.wheel_point(0.0, 0.0, sum(S.GEAR_TEETH_Z) / 2)
  screw = np.array([sum(S.WINDOW_X) / 2, S.FOOT_Y[1], sum(S.WINDOW_Z) / 2])
  dz = abs(gear[2] - screw[2])                                     # the push's lever arm about the screw
  twist = ft_most * dz / 1000.0                                    # Nm about the screw, from the push across
  _bw, bl, bt = S.BAR
  contact_r = 15.0                                                  # the rub's mean radius from the screw (the clamp spreads
  rub_nm = MG.TAPE_RUB * S.FOOT_CLAMP_N * contact_r / 1000.0        # from the bar through the foot): an estimate
  rub_dry = MG.RUB_DRY * S.FOOT_CLAMP_N * contact_r / 1000.0
  w_all = (MOVING_KG + FIXED_KG) * 9.81
  bump = w_all * MG.BUMP_G
  # the mount's weight hangs at the motor, dz behind the screw along the column and off to one side: it tips the foot
  # about its front edge (on the cover's underside) and the screw takes the pull, foot half-length away
  cg = S.wheel_point(0.0, 0.0, -20.0)
  arm = math.hypot(cg[0] - screw[0], cg[2] - screw[2]) / 1000.0
  half = (S.FOOT_Z[1] - S.FOOT_Z[0]) / 2 / 1000.0
  pull = bump * arm / half + bump
  # the foot: a beam from the tongue to the screw, bent by that pull; the bar: bent across the window by the clamp
  t_foot = S.FOOT_Y[1] - S.FOOT_Y[0]
  sig_foot = pull * (S.FOOT_X[1] - screw[0]) * (t_foot / 2) / ((S.FOOT_Z[1] - S.FOOT_Z[0]) * t_foot ** 3 / 12)
  sig_bar = 3 * S.FOOT_CLAMP_N * (S.WINDOW_X[1] - S.WINDOW_X[0]) / 2 / (2 * (bl - S.BAR_SLOT_W) / 2 * bt ** 2)
  rows = [
    MG.row(g, "The cover's screw holds the mount", f"{pull:.0f} N on the screw: the mount's weight ({w_all:.1f} N) on a hard "
           f"bump ({MG.BUMP_G:g} times gravity), hanging {arm * 1000:.0f} mm from the screw, tipping the foot about its "
           "front edge", f"{MG.PLATE_SCREW_HOLD_N:.0f} N: the cover's screw into the column's bracket, pulling out or "
           "tearing through the foot's window: an estimate on the low side", MG.PLATE_SCREW_HOLD_N / pull,
           "estimated; calculated"),
    MG.row(g, "The mount doesn't twist on its one screw", f"{twist:.2f} Nm about the screw: the motor's most push "
           f"({ft_most:.0f} N) at the gear, {dz:.0f} mm from the screw along the column",
           f"{rub_nm:.2f} Nm: the foot's rub on the cover's underside, silicone tape on it ({MG.TAPE_RUB:g}), the screw's "
           f"clamp {S.FOOT_CLAMP_N:.0f} N (an estimate on the low side) spread over {contact_r:.0f} mm round the screw",
           rub_nm / twist, "estimates; calculated",
           check=f"push the motor sideways with a luggage scale to {ft_most * 1.5 / 9.81:.0f} kg each way: the plate may "
                 "not move on the cover (mark its edge with tape first)",
           note=f"without the tape (dry, {MG.RUB_DRY:g}) it would be {rub_dry / twist:.2f}: put the tape on"),
    MG.row(g, "The foot bar takes the screw's clamp", f"{sig_bar:.1f} MPa in the bar, bent across the window by the "
           f"screw's clamp ({S.FOOT_CLAMP_N:.0f} N)", f"{MG.PETG_TENSILE_XY:.0f} MPa: PETG's tensile strength along its "
           "layers (the bar is printed flat)", MG.PETG_TENSILE_XY / sig_bar, "PETG data sheet; calculated",
           note=f"a hard hand on the screw (1000 N) would take it to {sig_bar * 1000 / S.FOOT_CLAMP_N:.0f} MPa: tighten it "
                "until the foot can't be moved by hand, then a quarter turn more"),
    MG.row(g, "The foot holds the mount's weight", f"{sig_foot:.1f} MPa where the foot leaves the tongue, the mount's "
           f"weight on a hard bump ({bump:.0f} N) on the screw", f"{MG.PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending "
           "strength across its layers", MG.PETG_BEND_Z / 3 / sig_foot, "PETG data sheet; calculated"),
  ]
  return rows


def slid_in_hold_g() -> float:
  """Slid in, the jolt (times gravity, along the slide's lean) the spring still holds the motor in against."""
  f = forces()
  return (S.CF["load_N"] - 0.5) / f["weight along the slide, outwards (N)"]


def side_margins() -> list:
  """The side-slide mount's own ways of failing, in the margins table's form (margins.py): the worst load, what it can
  take, the factor between them."""
  import gears as GR
  import margins as MG
  rows = []
  g = "Side-slide mount"
  k = MG.motor_k()
  ft_most = P.BOARD_MAX_A * k / (FP.R_P / 1000.0)              # the motor's most push at the teeth, N
  # the gear's teeth: the length they bear on the steering wheel teeth, less the pointed ends and the tips' chamfers
  tb = math.tan(math.radians(S.ROOF_DEG))
  half_at_pitch = (math.pi * GR.MODULE / 2 - P.BACKLASH) / 2
  face = (FP.FACE_BAND[1] - 0.75) - (FP.FACE_BAND[0] + half_at_pitch * tb + 1.5)
  sigma = ft_most / (face * GR.MODULE * 0.296)
  rows.append(MG.row(g, "The 16-tooth gear's teeth don't break", f"{sigma:.1f} MPa at the motor's most push ({ft_most:.0f} N), "
                     f"over the {face:.1f} mm the teeth bear on (the pointed ends and the tips' chamfers left out)",
                     f"{MG.PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending strength across its layers, for repeated loads",
                     MG.PETG_BEND_Z / 3 / sigma, "PETG data sheet; calculated (Lewis)"))
  half_flat = math.sqrt((P.SHAFT_D / 2) ** 2 - (P.SHAFT_ACROSS_FLAT - P.SHAFT_D / 2) ** 2)
  bore_len = min(P.SHAFT_LEN, S.GEAR_HUB[1]) - max(S.GEAR_TEETH_Z[0], P.SHAFT_LEN - P.SHAFT_FLAT_LEN)
  p_max = P.BOARD_MAX_A * k * 1000.0 * 3 / (2 * bore_len * half_flat ** 2)
  rows.append(MG.row(g, "The gear doesn't turn on the motor's shaft", f"{p_max:.0f} MPa where the shaft's flat presses on the "
                     f"gear ({bore_len:.1f} mm of it) at the motor's most push", f"{MG.PETG_TENSILE_XY:.0f} MPa: PETG's tensile "
                     "strength along its layers", MG.PETG_TENSILE_XY / p_max, "PETG data sheet; calculated",
                     note="the set screw on the flat holds it too"))
  f = forces()
  w_along = f["weight along the slide, outwards (N)"]
  bump = w_along * MG.BUMP_G                                   # the parts' weight along the slide on a hard bump
  hold = S.CF["load_N"] - w_along                              # what the notch holds, latched, still
  worst_latch = hold + bump
  # the lever's arm, a beam from its hub: latched, the notch's floor holds it at the plate; pulled or pushed, the hand at
  # the knob. Printed flat, so the bending runs along its layers.
  sec = S.SHANK_W * (S.LEVER_Z[1] - S.LEVER_Z[0]) ** 2 / 6.0
  d_hub = S.HUB_R
  sig_latch = worst_latch * (PLATE_OUT_X_D - d_hub) / sec
  rows.append(MG.row(g, "The lever holds the motor in its notch", f"{sig_latch:.1f} MPa in the lever's arm at its hub: the "
                     f"spring less the motor's weight ({hold:.1f} N), plus the moving parts thrown along the slide by a hard "
                     f"bump ({MG.BUMP_G:g} times gravity: {bump:.0f} N), on the notch's floor",
                     f"{MG.PETG_TENSILE_XY / 3:.0f} MPa: a third of PETG's tensile strength along its layers, for repeated loads",
                     MG.PETG_TENSILE_XY / 3 / sig_latch, "PETG data sheet; calculated"))
  sig_use = S.LEVER_USE_N * (S.KNOB_D - d_hub) / sec
  rows.append(MG.row(g, "The lever takes your pull and push, every time", f"{sig_use:.1f} MPa in its arm at its hub: "
                     f"{S.LEVER_USE_N:.0f} N at the knob (it needs {hold + 0.5:.1f} N out, less than {w_along + 0.5:.1f} N in)",
                     f"{MG.PETG_TENSILE_XY / 3:.0f} MPa: a third of PETG's tensile strength along its layers",
                     MG.PETG_TENSILE_XY / 3 / sig_use, "PETG data sheet; calculated"))
  sig_yank = S.LEVER_YANK_N * (S.KNOB_D - d_hub) / sec
  rows.append(MG.row(g, "The lever takes a hard yank", f"{sig_yank:.1f} MPa in its arm at its hub: {S.LEVER_YANK_N:.0f} N "
                     "at the knob (an estimate on the high side)",
                     f"{MG.PETG_TENSILE_XY:.0f} MPa: PETG's tensile strength along its layers", MG.PETG_TENSILE_XY / sig_yank,
                     "PETG data sheet; calculated"))
  # the lever stays in its notch: its own weight swings it towards its slot (gravity leans towards the dash here),
  # against the notch's grip; braking hard makes that worse
  h = lever_holds()["braking"]
  lift_g = hold / w_along
  for what, grip, by, note in (
      ("The lever stays latched in its notch", h["latched"],
       "the notch's grip: the spring's pull less the motor's weight presses the arm on the notch's floor",
       (f"a jolt over {lift_g:.1f} times gravity along the slide lifts the arm off the floor for a moment; if the lever "
        "ever works its way out, the spring pulls the motor in and the power goes off")),
      ("Parked with no spring, the lever stays in the inner notch", h["parked_no_spring"],
       "the notch's grip: the motor's weight presses the arm on the inner notch's side",
       ("with the spring working nothing holds the lever there and its weight swings it back into the slot: no harm, "
        "the spring holds the motor in"))):
    rows.append(MG.row(g, what, f"{h['own']:.2f} N at the knob: the lever's own weight swinging it towards its slot, "
                       f"braking hard ({BRAKE_G:g} times gravity)",
                       f"{grip:.2f} N at the knob: {by}, rubbing {MG.RUB_DRY:g} (an estimate)",
                       grip / h["own"] if h["own"] > 0 else float("inf"), "calculated; the rubbing is an estimate", note=note))
  # slid in, a jolt can throw the motor out along the slide: the spring holds it up to this many times gravity (not a
  # failure if it doesn't: it knocks out a little and back, unpowered, 27 mm short of the teeth)
  # the block's moments: the gear's push (across) and the teeth pushing it away (towards the dash), at the gear, about
  # the block's middle
  arm_z = (S.GEAR_TEETH_Z[0] + S.GEAR_TEETH_Z[1]) / 2 - S.Z_BLOCK
  sep = ft_most * math.tan(math.radians(GR.PRESSURE_ANGLE) + math.atan(MG.RUB_DRY))
  m_most = math.hypot(ft_most, sep) * arm_z / 1000.0
  rows.append(MG.row(g, "The rail's block takes the gear's push", f"{m_most:.2f} Nm about the block at the motor's most push "
                     f"({ft_most:.0f} N across and {sep:.0f} N pushing the teeth apart, {arm_z:.0f} mm out along the shaft)",
                     "37.5 Nm: the MGN12H block's static moment rating (HIWIN's catalogue)", 37.5 / m_most,
                     "HIWIN catalogue; calculated"))
  # the bracket's flange: the gear's push across bends it where it leaves the block
  lever = (S.GEAR_TEETH_Z[0] + S.GEAR_TEETH_Z[1]) / 2 - S.BLOCK_Z[1]
  sec = (S.FL_Y[1] - S.FL_Y[0]) * S.FLANGE_T ** 2 / 6.0
  sig_f = ft_most * lever / sec
  rows.append(MG.row(g, "The motor bracket's flange doesn't break", f"{sig_f:.1f} MPa where it leaves the block, at the motor's "
                     "most push", f"{MG.PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending strength across its layers",
                     MG.PETG_BEND_Z / 3 / sig_f, "PETG data sheet; calculated"))
  # the plate's fixing: the foot on the cover's screw. Its weight (the whole mount) hangs on the screw, and tips the foot
  # about its front edge; the motor's push twists the mount about the screw, held by the foot's rub on the cover
  foot = foot_margins()
  rows.extend(foot)
  e_in = f["... its energy then (J)"]
  rows.append(MG.row(g, "The bumper takes the motor's arrival, slid in", f"{e_in:.2f} J: the moving parts at "
                     f"{f['speed it hits the bumper at, let go (m/s, about)']} m/s",
                     "printed bumper and flange end, 100 mm2 of contact: can't be worked out reliably", float("nan"),
                     "proof test", kind="test", check="let it go 20 times at the start: the flange's end and the bumper "
                                                   "may get shiny, nothing may crack"))
  return rows
