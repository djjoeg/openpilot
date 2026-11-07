#!/usr/bin/env python3
"""
Builds the side-slide mount: its printed parts as STL files, the checks (sideassembly.py), a report and pictures.

  python3 sidebuild.py [--out ../stl] [--report ../report]

Writes <out>/side-slide-mount/*.stl, <report>/side_slide_report.txt and .json, and three pictures in <report>.
Ends with an error if a check fails.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

import faceparts as FP
import margins as MG
import popparts as PP
import sideassembly as SA
import sideparts as S
from cadlib import on_bed, revolve, union, write_stl

PETG_DENSITY = 1.28     # g/cm^3, Bambu Lab PETG HF data sheet (V1.0), as the other mounts

BOUGHT = [
  ("HIWIN MGN12H block on a 100 mm MGN12 rail (or any MGN12H block with a 100 mm rail cut to HIWIN's sizes)", 1,
   "the slide"),
  ("Lee Spring LCF 040 08 050S constant force spring (11.7 N, 12.7 mm wide)", 1, "pulls the motor in"),
  ("Omron SS-5GL2-F roller switch (the one already in the parts list)", 1, "power switch"),
  (S.COVER_SCREW, 1, "the plate's foot to the lower column cover's underside"),
  ("M3 x 6 button head screw", 4, "motor to motor bracket (a socket head can rub the gear)"),
  ("M3 x 6 socket head screw", 4, "motor bracket to the rail's block (heads sink into the bracket)"),
  ("M3 x 10 socket head screw", 6, ("4: rail to mounting plate, with M3 nuts (the nuts sink into the plate's outer face); "
                                    "2: the spring's strip, through the bracket's tab from the 6 o'clock side into the strip clamp")),
  ("M3 nut", 4, "the rail's screws"),
  ("M2 x 12 screw + M2 nut", 2, "power switch to the plate (nuts slide in slots from the top)"),
  ("M4 x 20 socket head screw", 2, ("the spool's axle (through a washer, cuts its own thread into the post), and the lever's "
                                    "pivot (in from the ear's inner end, into the nut in the outer lug)")),
  ("M4 washer", 2, "under the spool's axle head, and under the cover screw's head"),
  ("M4 nut", 1, "the lever's pivot, in the pocket in the ear's outer lug"),
  ("M3 x 10 set screw", 1, "gear onto the shaft's flat (cuts its own thread)"),
  ("silicone self-fusing tape (the roll already in the parts list)", 1, ("one layer on the foot's top (or the top shim), "
                                                                         "where it meets the column cover")),
]

def envelope() -> dict:
  """Where the mount reaches, from the CAD: how far in from the steering wheel's inside edge, how far forward of the
  back of the round part you hold, and how wide across (mm)."""
  parts = {"bracket": S.side_bracket(), "plate": S.side_plate()}
  r_in = PP.WHEEL_OD_P / 2 - PP.GRIP_P
  back = -PP.GRIP_P / 2
  cap = S.side_board_cap().bounding_box()
  mot_z0 = cap[2] - S.STROKE                        # the board cover's back, slid in (carrier z)

  def fwd(y: float) -> int:
    return round(back - (PP.Z_AXIS_P - y))   # carrier y -> mm forward of the back of the round part

  b = parts["bracket"].bounding_box()
  p = parts["plate"].bounding_box()
  slot_y = S.PIVOT[1] + S.KNOB_D * math.sin(math.radians(S.SLOT_DEG))   # the knob's middle, the lever in its slot
  sp = S.spring_parts(0.0)
  y_spring = max(sp["axle"].bounding_box()[4], b[4])
  return {"motor_in_now": round(r_in - (PP.R_FACE_P + cap[2])), "motor_in_slid": round(r_in - (PP.R_FACE_P + mot_z0)),
          "motor_forward": (fwd(cap[1]), fwd(cap[4])), "moving_across": round(max(b[3], cap[3]) - b[0]),
          "plate_in": round(r_in - (PP.R_FACE_P + p[2])), "dash_side_forward": fwd(y_spring),
          "knob_from_middle": round(math.hypot(PP.R_FACE_P + sum(S.LEVER_Z) / 2, S.PIVOT[0] - S.KNOB_D)),
          "knob_forward": (fwd(S.PIVOT[1] - S.KNOB_R), fwd(S.PIVOT[1] + S.KNOB_R)),
          "knob_forward_in_slot": (fwd(slot_y - S.KNOB_R), fwd(slot_y + S.KNOB_R)),
          "cover_front_range": tuple(round(SA.foot_fit(D)["cover's front edge behind the back of the round part (mm)"])
                                     for D in S.D_FOOT)}


def questions() -> list:
  e = envelope()
  return [
    (f"Room inside the steering wheel. Slid in, the motor's back end is {e['motor_in_slid']} mm in from the steering wheel's "
     f"inside edge at 5:20 ({e['motor_in_now']} mm with the motor out on the teeth). It sits {e['motor_forward'][0]} to {e['motor_forward'][1]} mm "
     f"forward of the back of the round part you hold, and with its bracket it is {e['moving_across']} mm across. Is that "
     "space clear, and does it stay clear as the steering wheel turns? Anything on the back of the steering wheel turns "
     f"with it. Beside it, towards 4 o'clock, the mounting plate reaches {e['plate_in']} mm in; on the motor's dash side the "
     f"spring and the bracket's tab reach {e['dash_side_forward']} mm forward. My photo model says the cover on the back of "
     "the steering wheel and the column cover are in the way. You said there is room, so measure it at the car."),
    (f"The column cover. The plate's foot lies under the lower column cover's underside and is held by the cover's own "
     "screw under the key cylinder. It is drawn for that cover's front edge being between "
     f"{e['cover_front_range'][0]} and {e['cover_front_range'][1]} mm behind the back of the round part you hold at 5 "
     "o'clock, and the screw 32 to 35 mm behind that edge, 60 to 76 mm to the right of the column's middle. Measure the "
     "edge; if it is nearer the steering wheel than that, the motor's slide has no room there either, and I need to "
     "know."),
    (f"The lever's knob. Latched, it sits towards 4 o'clock behind the steering wheel, about {e['knob_from_middle']} mm from "
     f"the middle of the steering wheel and {e['knob_forward'][0]} to {e['knob_forward'][1]} mm forward of the back of the "
     "round part you hold. To let go you push it away from you, towards the dash; sliding in the slot it is "
     f"{e['knob_forward_in_slot'][0]} to {e['knob_forward_in_slot'][1]} mm forward. Can you reach it there with the steering "
     "wheel straight, and is pulling it towards you to latch and pushing it away to let go the way round you want?"),
    ("Wobble. With the motor out on the teeth, how deep the teeth mesh is set by the plate; nothing springs. Turn the "
     "steering wheel slowly through its whole turn and watch the back of it at 5 o'clock against something fixed. Does "
     "it move towards or away from the dash, and by how much? Up to about 0.5 mm is fine."),
  ]


def support_area(m, max_angle: float = 45.0) -> float:
  """Area (mm2) of downward faces leaning more than max_angle from upright that are not on the bed."""
  mesh = m.to_mesh()
  v = np.asarray(mesh.vert_properties)[:, :3]
  tri = np.asarray(mesh.tri_verts)
  a, b, c = v[tri[:, 0]], v[tri[:, 1]], v[tri[:, 2]]
  n = np.cross(b - a, c - a)
  area = np.linalg.norm(n, axis=1) / 2
  nz = n[:, 2] / np.maximum(np.linalg.norm(n, axis=1), 1e-12)
  zmin = np.minimum(np.minimum(a[:, 2], b[:, 2]), c[:, 2]) - v[:, 2].min()
  steep = (nz < -math.cos(math.radians(max_angle)) - 0.01) & (zmin > 0.3)
  return float(area[steep].sum())


def printed_parts(parts: dict) -> dict:
  """name -> (solid, rotation onto the bed, how it sits, supports)."""
  return {
    "side-motor-bracket": (parts["bracket"], (90, 0, 0), "on its side towards you (the guard's point up)",
                           "none needed: only hole tops overhang"),
    "side-mounting-plate": (parts["plate"], (0, -90, 0), ("on its outer face (the lever's knob side down); the foot rises "
                                                          "from it at 70 degrees"),
                            "none needed: hole and slot tops, and the window's top, a 28 mm bridge"),
    "side-lever": (parts["lever"], (0, 0, 0), "flat, on its face towards the middle of the steering wheel", "none"),
    "side-gear": (parts["gear"], (0, 0, 0), "on its motor end, the pointed tooth ends up", "none"),
    "side-spool": (parts["spool"], (-90, 0, 0), "on its flange", "none"),
    "side-board-cover": (S.side_board_cap(), (0, 0, 0), "on its closed back", "none"),
    "side-strip-clamp": (S.strip_clamp(), (0, 90, 0), "flat", "none"),
    "side-foot-bar": (parts["foot bar"], (90, 0, 0), "flat, on its wide face", "none"),
    "side-foot-shim": (parts["foot shim"], (90, 0, 0), "flat (print four)", "none"),
  }


def teeth_file(n: int) -> str:
  t = S.SideTeeth(n_teeth=n)
  return f"side-steering-wheel-teeth-{round(t.teeth_half):02d}-{S.TEETH_SETS[n].replace(' ', '-')}"


def printed_teeth(parts: dict) -> dict:
  return {teeth_file(n): (st["teeth"], (180, 0, 0), "on the channel's two front edges, the teeth up",
                          "none in the channel: its inside corners are 45 degrees") for n, st in parts["sets"].items()}


def write_stls(parts: dict, out: str, bed=(220.0, 220.0, 250.0)) -> list:
  os.makedirs(out, exist_ok=True)
  rows = []
  for name, (m, rot, how, supports) in {**printed_parts(parts), **printed_teeth(parts)}.items():
    placed = on_bed(m, rot)
    best = None
    for zr in range(0, 91, 5):
      p2 = on_bed(placed, (0, 0, zr))
      x0, y0, z0, x1, y1, z1 = p2.bounding_box()
      size = (x1 - x0, y1 - y0, z1 - z0)
      fits = size[0] <= bed[0] and size[1] <= bed[1] and size[2] <= bed[2]
      if best is None or (fits and not best[0]):
        best = (fits, p2, size, zr)
      if fits:
        break
    fits, p2, size, zr = best
    write_stl(p2, os.path.join(out, name + ".stl"), name)
    vol = m.volume() / 1000.0
    rows.append({"file": f"side-slide-mount/{name}.stl", "print": how + (f", turned {zr} degrees on the bed" if zr else ""),
                 "supports": supports, "size_mm": [round(v, 1) for v in size], "fits_bed": fits,
                 "solid_volume_cm3": round(vol, 1), "filament_if_solid_g": round(vol * PETG_DENSITY, 1),
                 "pieces": len(m.decompose()), "closed_solid": str(m.status()).endswith("NoError"),
                 "overhang_mm2": round(support_area(p2))})
  return rows


def run_checks(A: SA.SideAssembly) -> dict:
  """The mount's own checks once, and the checks that involve the steering wheel teeth for every set (the report's
  "mesh", "wheel_turned" and so on are the 14-tooth set's; "sets" has every set's)."""
  res = {}
  internal = SA.internal(A)
  res["internal"] = {k: [round(float(v[0]), 3), v[1]] for k, v in internal.items()}
  res["stops"] = SA.touching_at_stops(A)
  res["lever"] = SA.lever_notches(A)
  res["sets"] = {}
  for n in A.p["sets"]:
    An = SA.SideAssembly(A.p, A.mount, n_teeth=n)
    r = {"teeth": n, "reach_deg": An.t.reach_deg, "mesh": SA.mesh_sweep(An), "slide_out_of_teeth": SA.slide_out_of_teeth(An),
         "wheel_turned": {k: [round(float(v[0]), 3), v[1]] for k, v in SA.wheel_turned(An, step=0.5).items()},
         "end_teeth": SA.end_teeth_meeting(An), "slid_in": {k: round(float(v), 3) for k, v in SA.slid_in(An).items()},
         "clearances": SA.clearances(An)}
    res["sets"][n] = r
    if n == A.t.n_teeth:
      res.update({k: r[k] for k in ("mesh", "slide_out_of_teeth", "wheel_turned", "end_teeth", "slid_in", "clearances")})
  res["forces"] = SA.forces()
  res["switch"] = SA.switch_states()
  res["slid_in_hold_g"] = round(SA.slid_in_hold_g(), 2)
  res["margins"] = SA.side_margins()
  res["car_estimates"] = {D: SA.car_estimates(A, D) for D in (S.D_FOOT[0], S.D_FOOT[1])}
  res["foot_fit"] = [SA.foot_fit(D) for D in (S.D_FOOT[0], (S.D_FOOT[0] + S.D_FOOT[1]) / 2, S.D_FOOT[1])]
  return res


def problems_of(res: dict) -> list:
  out = []
  for k, v in res["internal"].items():
    if "touching" in k:
      continue
    if v[0] > 1e-3:
      out.append(f"slide: {k} overlap {v[0]} mm3 at {v[1]} mm")
  lv = res["lever"]
  if lv["swinging into the notches (worst overlap, mm3)"] > 1e-3:
    out.append(f"the lever touches {lv['... where']} swinging into a notch")
  if lv["latched, pushed in 0.3 mm: the plate stops it (mm3 it would go into the plate)"] < 1.0:
    out.append("latched, the notch doesn't hold the lever")
  if lv["parked, pulled out 0.3 mm: the plate stops it (mm3)"] < 1.0:
    out.append("parked, the notch doesn't hold the lever")
  if lv["swung into the slot, it slides: worst overlap with the plate (mm3)"] > 1e-3:
    out.append("the lever touches the plate sliding in its slot")
  for n, r in res["sets"].items():
    tag = f"{n} teeth: "
    if r["mesh"]["worst_overlap_mm3"] > 1e-3:
      out.append(f"{tag}the gear and the teeth overlap {r['mesh']['worst_overlap_mm3']} mm3")
    if r["slide_out_of_teeth"]["worst_overlap_mm3"] > 1e-3:
      out.append(f"{tag}the gear touches the teeth sliding out")
    for k, v in r["wheel_turned"].items():
      if v[0] > 1e-3:
        out.append(f"{tag}steering wheel turned: {k} overlap {v[0]} mm3")
    for k, v in r["slid_in"].items():
      if v > 1e-3:
        out.append(f"{tag}{k} overlap {v} mm3")
  for ff in res["foot_fit"]:
    if min(ff["room left in the window across (mm, either way)"]) < 0 or min(ff["room left along (mm, either way)"]) < 0:
      out.append(f"the cover's screw misses the foot's window at D {ff['D']}")
  for r in res["margins"]:
    if r["factor"] is not None and r["factor"] < MG.FLOOR:
      out.append(f"margin under {MG.FLOOR}: {r['what']} ({r['factor']})")
  return out


def report_text(res: dict, stl_rows: list, problems: list) -> str:
  L = ["SIDE-SLIDE MOUNT", "",
       "The motor sits at 5:20 behind the steering wheel, its shaft pointing out at the steering wheel and its gear on the",
       "teeth on the back of it. It slides along its own shaft, in towards the middle of the steering wheel, on a rail. A",
       "lever on the motor's bracket comes out through an L-shaped slot in the mounting plate. Pull the lever out along the",
       "slot (the motor slides out onto the teeth), then pull it towards you into the notch at the slot's end: latched.",
       f"Push it away from you, out of the notch, and the spring pulls the motor {S.STROKE:.0f} mm in; if the spring doesn't,",
       "push the lever in along the slot. The power switch is on only with the motor all the way out on the teeth.",
       "The notch at the slot's inner end is for a broken spring: without the spring, the motor's own weight slides it back",
       "out onto the teeth; with the lever in that notch, the weight holds it in instead.",
       "The mounting plate's foot lies under the lower column cover and is held by the cover's own screw under the key",
       "cylinder (a longer one), through a window that takes the screw wherever it falls; a bar under the foot bridges the",
       "window, and shims fill the gap up to the cover. The steering wheel teeth come in three sets, the same piece with",
       "10, 14 or 18 teeth: " + ", ".join(f"{S.SideTeeth(n_teeth=n).reach_deg:.1f} degrees each way ({w})" for n, w in S.TEETH_SETS.items()) + ".", ""]
  L.append("CHECKS (against our own parts, the bought parts' catalogue sizes and your steering wheel: 372 mm across, 35.4 thick)")
  L.append("  " + ("all pass" if not problems else "PROBLEMS:"))
  for p in problems:
    L.append("    " + p)
  for n, r in res["sets"].items():
    m = r["mesh"]
    L.append(f"  the {n}-tooth set ({r['reach_deg']} degrees each way):")
    L.append(f"    gear in the teeth over their whole arc: worst overlap {m['worst_overlap_mm3']} mm3; free play at the steering "
             f"wheel {m['free_play_steering_wheel_deg']} degrees")
    L.append(f"    the gear sliding in and out along the teeth's gaps: worst overlap {r['slide_out_of_teeth']['worst_overlap_mm3']} mm3")
    L.append("    the steering wheel turned through and past the teeth piece (every 0.5 degree), motor out: nothing touches")
    L.append("    past the teeth the gear is free (the motor is switched off there); coming back, the two lowered end teeth meet")
    L.append(f"    it first and turn it into step: they reach {r['end_teeth']['the last tooth (lowered most)']} and "
             f"{r['end_teeth']['the next (lowered less)']} mm3 into it at the worst angle if it didn't turn")
    L.append(f"    slid in {S.STROKE:.0f} mm: clear of the teeth piece anywhere round, the steering wheel and your fingers' room")
  st = res["stops"]
  block_gap = st["block's end to the bumper, slid in 40"]
  rail_ends = st["block's ends to the rail's ends (in, out)"]
  lv = res["lever"]
  L.append(f"  the lever swings between its slot and either notch touching nothing (worst {round(lv['swinging into the notches (worst overlap, mm3)'], 4)} mm3)")
  L.append(f"  latched, the notch's floor stops it sliding in (pushed in 0.3 mm it would go {lv['latched, pushed in 0.3 mm: the plate stops it (mm3 it would go into the plate)']} mm3")
  L.append(f"  into the plate); parked, likewise it can't slide out ({lv['parked, pulled out 0.3 mm: the plate stops it (mm3)']} mm3); in its slot it slides touching nothing")
  L.append(f"  stops: pulled out, the ear meets the stop {S.STOP_GAP} mm past the latched place; slid in, the bracket meets the")
  L.append(f"  bumper with the block {block_gap} mm short of it; the block stays {rail_ends[0]} and {rail_ends[1]} mm from the "
           "rail's ends")
  L.append("")
  L.append("CLOSEST APPROACHES (mm; negative = overlap in mm3)")
  for tag, a, b, g in res["clearances"]:
    if g < 20.0:
      L.append(f"  {tag:9s} {a} to {b}: {g}")
  L.append("")
  L.append("FORCES")
  for k, v in res["forces"].items():
    L.append(f"  {k}: {v}")
  L.append(f"  slid in, the spring holds it in up to a jolt of {res['slid_in_hold_g']} times gravity along the slide; harder")
  L.append("  than that it can knock out a little and back (unpowered, 27 mm short of the teeth)")
  L.append("")
  L.append("POWER SWITCH (slid in s mm: how far its roller has come out, from where it sits latched)")
  for s, back, state in res["switch"]:
    L.append(f"  {s:5.1f} mm: {back:4.2f} mm out, {state}")
  L.append("  so the motor's power is cut within the first 1.6 mm, long before the gear starts leaving the teeth (12.5 mm)")
  L.append("")
  L.append("MARGINS (aim 1.5, floor 1.4)")
  L += MG.text_lines(res["margins"])
  L.append("")
  L.append("PRINTED PARTS (light grey PETG, as the rest)")
  for r in stl_rows:
    L.append(f"  {r['file']}: {r['size_mm'][0]} x {r['size_mm'][1]} x {r['size_mm'][2]} mm, about {r['filament_if_solid_g']} g "
             f"if solid; print {r['print']}; supports: {r['supports']}")
  L.append("  side-foot-shim: print four; use as many as fill the gap between the foot and the cover's underside.")
  L.append("")
  L.append("THE FOOT ON THE COLUMN COVER (from the photo model, for the range of cover positions it is drawn for)")
  for ff in res["foot_fit"]:
    L.append(f"  the cover's front edge {ff["cover's front edge behind the back of the round part (mm)"]} mm behind the back of the round part: "
             f"the screw lands {min(ff['room left in the window across (mm, either way)']):.1f} mm or more inside the window across and "
             f"{min(ff['room left along (mm, either way)']):.1f} along (its place 4 mm off either way, the mount turned up to 3 degrees); "
             f"gap over the foot {ff['gap over the foot (mm)']} mm: {ff['shims']} shim(s)")
  L.append("")
  L.append("BOUGHT PARTS")
  for what, n, use in BOUGHT:
    L.append(f"  {n} x {what}: {use}")
  L.append("")
  L.append("THE CAR ROUND IT: ESTIMATES FROM PHOTOS, NOT CHECKED (closest approach in mm; negative = overlap in mm3)")
  for D, rows in res["car_estimates"].items():
    ff = SA.foot_fit(float(D))
    L.append(f"  with the column cover's front edge {ff["cover's front edge behind the back of the round part (mm)"]} mm behind the back of the round part (D {D}):")
    for tag, a, b, g in rows:
      L.append(f"    {tag:9s} {a} to {b}: {g}")
  L.append("")
  L.append("QUESTIONS FOR YOU")
  for i, q in enumerate(questions(), 1):
    L.append(f"  {i}. {q}")
  return "\n".join(L) + "\n"


# ***** pictures *****

def drawing(A: SA.SideAssembly, path: str):
  """From behind the steering wheel (the motor turned to lie flat on the page) and a cut along the shaft."""
  import matplotlib
  matplotlib.use("Agg")
  import matplotlib.pyplot as plt
  from matplotlib.patches import Circle, Polygon, Rectangle
  parts, t = A.p, A.t
  R_IN, R_OUT, R_MID = PP.WHEEL_OD_P / 2 - PP.GRIP_P, PP.WHEEL_OD_P / 2, t.rr
  BACK = -PP.GRIP_P / 2
  F, ZA = PP.R_FACE_P, PP.Z_AXIS_P
  TOP = [[0, 0, 1, 0], [-1, 0, 0, 0], [0, -1, 0, 0]]
  CUT = [[0, 0, 1, 0], [0, -1, 0, 0], [1, 0, 0, 0]]
  C = {"wheel": "#2b2b2e", "teeth": "#c9ccd1", "motor": "#5b6b7d", "bracket": "#3f7fd0", "gear": "#e0962b",
       "plate": "#78a85a", "rail": "#9aa0a8", "block": "#6d7179", "lever": "#d04a4a", "switch": "#333333", "spring": "#c8b040"}

  def draw(ax, m, how, c, ls="-", alpha=1.0, lw=1.0, z=2, dz=0.0):
    polys = m.transform(TOP).project().to_polygons() if how == "top" else m.transform(CUT).slice(0.0).to_polygons()
    for p in polys:
      p = np.asarray(p)
      if len(p) < 3:
        continue
      q = np.c_[F + p[:, 0], p[:, 1] + dz]
      ax.add_patch(Polygon(q, closed=True, fc=c if ls == "-" else "none", ec=c, lw=lw, ls=ls, alpha=alpha, zorder=z))

  mv_in, mv_out, fx = A.movers(0.0, lever_deg=0.0), A.movers(S.STROKE), A.fixed(0.0)
  fig, (a1, a2) = plt.subplots(1, 2, figsize=(17, 8.6), gridspec_kw={"width_ratios": [1.05, 1.0]})

  def band(r0, r1, b0, b1):
    a = np.radians(np.linspace(b0, b1, 120))
    return np.r_[np.c_[r0 * np.cos(a), r0 * np.sin(a)], np.c_[r1 * np.cos(a[::-1]), r1 * np.sin(a[::-1])]]

  ax = a1
  ax.add_patch(Polygon(band(R_IN, R_OUT, -40, 40), closed=True, fc=C["wheel"], ec=C["wheel"], alpha=0.85, zorder=1))
  ax.add_patch(Polygon(band(t.w_in, t.w_out, -t.half, t.half), closed=True, fc=C["teeth"], ec="#777", alpha=0.55, zorder=1.5))
  ax.add_patch(Polygon(band(FP.FACE_BAND[0], FP.FACE_BAND[1], -t.teeth_half, t.teeth_half), closed=True, fc="none", ec="#777",
                       hatch="////", lw=0.6, zorder=1.6))
  for m, c in ((parts["plate"], C["plate"]), (parts["rail"], C["rail"]), (fx["switch"], C["switch"]),
               (fx["spring's coil and spool"], C["spring"])):
    draw(ax, m, "top", c, alpha=0.55, z=3)
  draw(ax, S.spring_parts(0.0)["strip"], "top", C["spring"], alpha=0.9, z=3.5)
  for mv, ls in ((mv_in, "-"), (mv_out, "--")):
    for name, c in (("block", C["block"]), ("motor bracket", C["bracket"]), ("motor, board and plugs", C["motor"]), ("gear", C["gear"]),
                    ("lever", C["lever"])):
      draw(ax, mv[name], "top", c, ls=ls, alpha=0.95 if ls == "-" else 1.0, lw=1.0 if ls == "-" else 1.4, z=4 if ls == "-" else 5)
  ax.annotate("", xy=(F - 50.5 - S.STROKE, -36), xytext=(F - 50.5, -36), arrowprops={"arrowstyle": "->", "lw": 2.2, "color": "#c0392b"}, zorder=8)
  ax.text(F - 50.5 - S.STROKE / 2, -41.5, f"the spring pulls it in {S.STROKE:.0f} mm", ha="center", va="top", color="#c0392b", fontsize=10)

  def note(text, xy, xytext, color="#222"):
    ax.annotate(text, xy=xy, xytext=xytext, ha="center", va="center", fontsize=9, color=color, zorder=9,
                arrowprops={"arrowstyle": "-", "lw": 0.7, "color": "#555", "shrinkA": 0, "shrinkB": 2})
  note("steering wheel\n(the round part you hold)", (R_IN + 6, 70), (200, 84))
  note("teeth piece", (178, -30), (205, -50))
  note("gear (no roller now)", (F + 13, -10), (196, -30))
  note("finger guard", (F + 22, 20), (205, 30))
  note("motor", (F - 25, -5), (120, -50))
  note("board cover", (F - 46, -10), (95, -50))
  note("motor bracket: its flange\nbolts to the rail's block", (F - 40, 29), (80, 64))
  note("mounting plate (fixed),\nthe rail on it", (F - 75, 47), (62, 84))
  note("lever: pull it out along the slot,\nthen towards you into the notch", (F - 11, 78), (195, 57), color=C["lever"])
  note("power switch", (F + 11, 27), (196, 8))
  note("spring", (F - 74, 30), (52, 22))
  note("the plate's foot: under the column cover, on its screw", (F - 20, 44), (150, 86), color=C["plate"])
  ax.set_xlim(225, 30)
  ax.set_ylim(-62, 92)
  ax.set_aspect("equal")
  ax.grid(alpha=0.2)
  ax.set_xlabel("mm from the middle of the steering wheel, along the motor's shaft")
  ax.set_ylabel("towards 6 o'clock   (mm)   towards 4 o'clock", fontsize=9)
  ax.set_title("From behind the steering wheel (the dash side), the motor at 5:20\nturned to lie flat on the page", fontsize=11)

  ax = a2
  ax.add_patch(Circle((R_MID, 0.0), PP.GRIP_P / 2, fc=C["wheel"], ec=C["wheel"], alpha=0.85, zorder=1))
  ax.add_patch(Polygon(np.array(t.profile()), closed=True, fc=C["teeth"], ec="#555", alpha=0.6, lw=0.8, zorder=1.5))
  for mv, ls in ((mv_in, "-"), (mv_out, "--")):
    for name, c in (("motor bracket", C["bracket"]), ("motor, board and plugs", C["motor"]), ("gear", C["gear"])):
      draw(ax, mv[name], "cut", c, ls=ls, alpha=0.95 if ls == "-" else 1.0, lw=1.0 if ls == "-" else 1.4, z=4 if ls == "-" else 5, dz=ZA)
  cap_in = F - S.NEMA_LEN - S.SP.CAP_DEPTH
  _x0, y0, _z0, _x1, y1, _z1 = S.side_board_cap().bounding_box()
  z_hi, z_lo = ZA - y0, ZA - y1
  ax.axhspan(z_lo, z_hi, color="#f3d9a6", alpha=0.35, zorder=0)
  ax.plot([R_IN, R_IN], [-128, 22], color="#333", lw=0.8, ls=":")
  for xx, txt, y in ((cap_in, f"motor in: its back end {R_IN - cap_in:.0f} mm in from the inside edge", -108),
                     (cap_in - S.STROKE, f"slid in: {R_IN - cap_in + S.STROKE:.0f} mm in", -121)):
    ax.annotate("", xy=(xx, y + 5), xytext=(R_IN, y + 5), arrowprops={"arrowstyle": "<->", "lw": 1, "color": "#333"})
    ax.text((xx + R_IN) / 2 + 6, y, txt, ha="center", va="top", fontsize=9)
  ax.text(R_IN - 1, 24, "inside edge of the\nsteering wheel", ha="left", va="bottom", fontsize=9)
  ax.annotate("", xy=(212, z_hi), xytext=(212, BACK), arrowprops={"arrowstyle": "<->", "lw": 1, "color": "#333"})
  ax.annotate("", xy=(220, z_lo), xytext=(220, BACK), arrowprops={"arrowstyle": "<->", "lw": 1, "color": "#333"})
  ax.plot([206, 224], [BACK, BACK], color="#333", lw=0.8)
  ax.text(210, (z_hi + BACK) / 2, f"{BACK - z_hi:.0f}", fontsize=9, va="center", ha="right")
  ax.text(218, z_lo + 8, f"{BACK - z_lo:.0f}", fontsize=9, va="center", ha="right")
  ax.text(48, ZA - 4, "?", ha="center", va="center", fontsize=22, color="#8a5a00")
  ax.text(100, -96, f"is this band clear {R_IN - cap_in + S.STROKE:.0f} mm in from the inside edge,\nall the way round as the steering wheel turns?",
          ha="center", va="center", fontsize=9.5, color="#8a5a00")
  ax.text(226, 21, "towards you", fontsize=9, color="#555", ha="left")
  ax.text(226, -125, "forward (towards the nose)", fontsize=9, color="#555", ha="left")
  ax.text(R_MID, -27, "teeth piece", ha="center", fontsize=9)
  ax.set_xlim(228, 35)
  ax.set_ylim(-130, 30)
  ax.set_aspect("equal")
  ax.grid(alpha=0.2)
  ax.set_xlabel("mm from the middle of the steering wheel")
  ax.set_ylabel("mm from the middle of the round part you hold")
  ax.set_title("Cut along the motor's shaft: the motor, its cover, bracket and gear\n(the mounting plate is beside it, towards 4 o'clock)", fontsize=11)
  handles = [Rectangle((0, 0), 1, 1, fc=C[k], alpha=0.9) for k in ("motor", "bracket", "gear", "teeth", "plate", "lever", "spring")] + \
    [Rectangle((0, 0), 1, 1, fc="none", ec="#333", ls="--")]
  fig.legend(handles, ["motor and board cover", "motor bracket and finger guard", "gear", "teeth piece", "mounting plate and rail",
                       "lever", "spring", f"slid in {S.STROKE:.0f} mm"], loc="lower center", ncol=8, fontsize=9, frameon=False)
  plt.tight_layout(rect=(0, 0.04, 1, 1))
  plt.savefig(path, dpi=110)
  plt.close(fig)


def pictures_3d(A: SA.SideAssembly, path_3d: str, path_parts: str):
  import matplotlib
  matplotlib.use("Agg")
  import matplotlib.pyplot as plt
  import render as R
  from manifold3d import Manifold
  parts, t = A.p, A.t
  pts = [(t.rr + (PP.GRIP_P / 2) * math.cos(a), (PP.GRIP_P / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 36, endpoint=False)]
  grip = revolve(pts, S.MOUNT_DEG - 50, S.MOUNT_DEG + 50, step_deg=1.5)
  teeth = A.teeth(0.0)
  C = {"grip": (0.22, 0.22, 0.24), "teeth": (0.80, 0.80, 0.78), "motor": (0.36, 0.42, 0.50), "bracket": (0.25, 0.50, 0.82),
       "gear": (0.90, 0.58, 0.18), "plate": (0.47, 0.66, 0.35), "rail": (0.72, 0.72, 0.76), "block": (0.50, 0.50, 0.55),
       "lever": (0.82, 0.28, 0.28), "switch": (0.15, 0.15, 0.15), "spring": (0.80, 0.72, 0.25)}

  ff = SA.foot_fit(sum(S.D_FOOT) / 2)
  sx, sz = ff["screw (x, z)"]
  bar = S.foot_bar(sz)
  screw = S.cover_screw(sx, sz, ff["underside y"])
  shims = union([S.foot_shim().translate((0, k * S.SHIM_T, 0)) for k in range(ff["shims"])]) if ff["shims"] else None

  def scene(s):
    mv, fx, W = A.movers(s, lever_deg=0.0 if s == 0.0 else S.SLOT_DEG), A.fixed(s), A.W
    sp = S.spring_parts(s)
    out = [(grip, C["grip"]), (teeth, C["teeth"]), (W(mv["motor, board and plugs"]), C["motor"]), (W(mv["motor bracket"]), C["bracket"]),
           (W(mv["gear"]), C["gear"]), (W(mv["block"]), C["block"]), (W(parts["plate"]), C["plate"]), (W(parts["rail"]), C["rail"]),
           (W(mv["lever"]), C["lever"]), (bar, C["rail"]), (screw, C["block"]),
           (W(fx["switch"] + fx["switch's lever and roller"]), C["switch"]), (W(fx["spring's coil and spool"] + sp["strip"]), C["spring"])]
    if shims is not None:
      out.append((shims, C["plate"]))
    return out

  def projector(parts_list, rot, size, margin=0.06):
    w, h = size
    allp = np.concatenate([np.asarray(m.to_mesh().vert_properties)[:, :3] @ rot.T for m, _ in parts_list])
    lo, hi = allp.min(axis=0), allp.max(axis=0)
    scale = min(w * (1 - 2 * margin) / (hi[0] - lo[0]), h * (1 - 2 * margin) / (hi[1] - lo[1]))
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2

    def f(p):
      q = np.asarray(p, float) @ rot.T
      return ((q[0] - cx) * scale + w / 2, h / 2 - (q[1] - cy) * scale)
    return f

  def cpt(x, y, z):
    return np.asarray(S.to_wheel(Manifold.cube((0.01, 0.01, 0.01)).translate((x, y, z))).bounding_box()[:3])

  a = math.radians(S.MOUNT_DEG)
  radial = np.array([math.cos(a), math.sin(a), 0.0])
  tang4 = np.array([-math.sin(a), math.cos(a), 0.0])
  rot = R.look(-0.95 * np.array([0, 0, 1.0]) + 0.45 * tang4 - 0.30 * radial, [0, 1, 0])
  size = (1100, 900)
  anchors = {
    "steering wheel (the round part you hold)": ((PP.WHEEL_OD_P / 2 - 8) * np.array([math.cos(a + 0.55), math.sin(a + 0.55), 0.0]) + [0, 0, -10.0], (-60, -90)),
    "teeth piece": ((t.rr + 10) * np.array([math.cos(a - 0.30), math.sin(a - 0.30), 0.0]) + [0, 0, -40.0], (-40, 110)),
    "gear (inside the finger guard)": (cpt(0.0, 22.0, 14.0), (-160, 60)),
    "motor bracket": (cpt(-27.0, 0.0, -30.0), (120, 90)),
    "motor": (cpt(0.0, 21.2, -20.0), (150, -40)),
    "board cover": (cpt(10.0, 25.0, -45.0), (150, -10)),
    "mounting plate (fixed), the rail on its far side": (cpt(S.X_PL[0], 0.0, -60.0), (-170, -40)),
    "the plate's foot: under the column cover, on its screw": (np.array([sum(S.FOOT_X) / 2, S.FOOT_Y[1], sum(S.FOOT_Z) / 2]), (-150, 60)),
    "lever: out along the slot, then towards you into the notch": (cpt(S.PIVOT[0] - S.KNOB_D, S.PIVOT[1], sum(S.LEVER_Z) / 2), (-170, -60)),
    "power switch": (cpt(-27.0, 34.0, 16.0), (-120, -100)),
    "spring": (cpt(S.SPOOL_X, 45.4, S.SPOOL_Z), (120, -60)),
  }
  fig, axes = plt.subplots(1, 2, figsize=(2 * size[0] / 110, size[1] / 110 + 0.6), dpi=110)
  for ax, s, title in ((axes[0], 0.0, "motor out on the teeth: the lever latched in its notch"),
                       (axes[1], S.STROKE, f"lever out of its notch: the spring has pulled the motor {S.STROKE:.0f} mm in")):
    sc = scene(s)
    ax.imshow(R.render(sc, rot, size=size))
    ax.set_axis_off()
    ax.set_title(title, fontsize=11)
    if s == 0.0:
      f = projector(sc, rot, size)
      for name, (p, (dx, dy)) in anchors.items():
        x, y = f(p)
        ax.annotate(name, xy=(x, y), xytext=(x + dx, y + dy), fontsize=9, ha="center", va="center",
                    bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "#888", "lw": 0.6, "alpha": 0.9},
                    arrowprops={"arrowstyle": "-", "lw": 0.8, "color": "#333"})
  fig.suptitle("From behind the steering wheel (the dash side), a little from 4 o'clock", fontsize=12)
  fig.tight_layout()
  fig.savefig(path_3d)
  plt.close(fig)
  pr = [(n.replace("side-", "").replace("-", " "), m, r) for n, (m, r, _, _) in printed_parts(parts).items()]
  view = R.view_matrix(-60, 35)
  R.save(path_parts, [([(on_bed(m, r), (.55, .7, .9))], view) for _, m, r in pr], titles=[n for n, _, _ in pr],
         suptitle="The printed parts, each as it sits on the print bed (the three steering wheel teeth sets are not shown: "
                  "one piece, with 10, 14 or 18 teeth)", size=(700, 600), cols=3)


def main():
  here = os.path.dirname(os.path.abspath(__file__))
  ap = argparse.ArgumentParser(description=__doc__)
  ap.add_argument("--out", default=os.path.join(here, "..", "stl"))
  ap.add_argument("--report", default=os.path.join(here, "..", "report"))
  ap.add_argument("--no-pictures", action="store_true")
  args = ap.parse_args()
  parts = SA.build_parts()
  A = SA.SideAssembly(parts)
  res = run_checks(A)
  problems = problems_of(res)
  stl_rows = write_stls(parts, os.path.join(args.out, "side-slide-mount"))
  for r in stl_rows:
    if r["pieces"] != 1 or not r["closed_solid"]:
      problems.append(f"{r['file']}: not one closed solid")
    if not r["fits_bed"]:
      problems.append(f"{r['file']}: doesn't fit a 220 x 220 mm bed")
  os.makedirs(args.report, exist_ok=True)
  text = report_text(res, stl_rows, problems)
  with open(os.path.join(args.report, "side_slide_report.txt"), "w") as f:
    f.write(text)
  with open(os.path.join(args.report, "side_slide_report.json"), "w") as f:
    json.dump({"checks": res, "parts": stl_rows, "bought": BOUGHT, "questions": questions(), "envelope": envelope(),
               "problems": problems}, f, indent=1,
              default=lambda o: float(o) if isinstance(o, (np.floating,)) else str(o))
  if not args.no_pictures:
    drawing(A, os.path.join(args.report, "side-slide-drawing.png"))
    pictures_3d(A, os.path.join(args.report, "side-slide-3d.png"), os.path.join(args.report, "side-slide-parts.png"))
  print(text)
  if problems:
    sys.exit("side-slide mount: " + "; ".join(problems))


if __name__ == "__main__":
  main()
