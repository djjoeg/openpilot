#!/usr/bin/env python3
"""
Printed parts for the lane keeping motor on a 2008-2012 Honda Accord.

  steering wheel teeth  - zip-tied around the top of the steering wheel (one piece, or two halves for smaller printers)
  motor gear            - on the motor's shaft; meshes with the steering wheel teeth
  motor carrier         - the motor bolts to it; finger guard around the motor gear; turns on the hinge block's hinge
  hinge block           - holds the carrier's hinge, the spring, the lift lever and the power switch; the arm bolts to it
  lift lever            - down: motor gear on the teeth, motor powered. Up: motor gear lifted off, motor's power cut
  arm                   - dash clamp to hinge block; printed in several lengths, each slides +-11 mm at the dash clamp
  dash clamp            - grips the edge of the cover over the gauges
  clamp pad             - swivel pad on the end of the dash clamp's screw
  setup gauge           - spacer used while adjusting the arm (sets the gap between the carrier and the hinge block)
  fit tests             - a short piece of the steering wheel teeth to try on your steering wheel, and a few teeth to
                          try against the printed motor gear

Run it with no options to write every STL file (already turned the way it should sit on the print bed), a report,
and pictures. Options let you enter your own steering wheel's measurements, where your dash clamp ends up, or an
arm of an exact length:

  python3 accord_lka_parts.py
  python3 accord_lka_parts.py --wheel-od 366 --grip 32.5
  python3 accord_lka_parts.py --clamp-up 110 --clamp-forward 160
  python3 accord_lka_parts.py --arm 143

It checks that every part is one closed solid that fits the print bed; that the gears mesh without touching through
the whole range of the teeth; that nothing touches anything it shouldn't with the lift lever down, up and at every
angle between, and with the steering wheel turned past the teeth; and which dash clamp positions the parts can reach.
It exits with an error if any check fails.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import params as P  # noqa: E402

ASA_DENSITY = 1.07      # g/cm^3


def parse_args():
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument("--wheel-od", type=float, default=P.WHEEL_OD, help="steering wheel, outside edge to outside edge (mm)")
  ap.add_argument("--grip", type=float, default=P.GRIP, help="thickness of the part of the steering wheel you hold, at the top (mm)")
  ap.add_argument("--clamp-up", type=float, default=P.ARM_PIVOT_UP,
                  help="dash clamp's bolt: mm above the motor gear's centre (in the car)")
  ap.add_argument("--clamp-forward", type=float, default=P.ARM_PIVOT_FORWARD,
                  help="dash clamp's bolt: mm ahead of the motor gear's centre (towards the windshield)")
  ap.add_argument("--arm", type=float, action="append", default=[], help="also make an arm of exactly this length (mm, bolt to bolt)")
  ap.add_argument("--bed", type=float, nargs=3, default=list(P.BED), metavar=("X", "Y", "Z"), help="print bed size (mm)")
  ap.add_argument("--out", default=os.path.join(HERE, "..", "stl"), help="folder for the STL files")
  ap.add_argument("--report", default=os.path.join(HERE, "..", "report"), help="folder for the report and pictures")
  ap.add_argument("--no-pictures", action="store_true", help="skip the pictures (faster)")
  return ap.parse_args()


def main():
  args = parse_args()
  t_start = time.time()
  P.WHEEL_OD, P.GRIP = args.wheel_od, args.grip
  P.BED = tuple(args.bed)

  import assembly as AS      # noqa: E402  (imported after the measurements are set)
  import gears as GR         # noqa: E402
  import mountparts as MP    # noqa: E402
  import wheelparts as WP    # noqa: E402
  from cadlib import on_bed, write_stl  # noqa: E402

  os.makedirs(args.out, exist_ok=True)
  os.makedirs(os.path.join(args.out, "arms"), exist_ok=True)
  os.makedirs(args.report, exist_ok=True)
  problems = []
  report = {"inputs": {"steering_wheel_across_mm": args.wheel_od, "grip_mm": args.grip,
                       "dash_clamp_bolt_up_mm": args.clamp_up, "dash_clamp_bolt_forward_mm": args.clamp_forward,
                       "column_tilt_deg": P.COLUMN_TILT, "print_bed_mm": list(args.bed)}}

  # ----- parts -----
  t = WP.Teeth(args.wheel_od, args.grip)
  whole = WP.teeth_solid(t)
  parts = {}       # file name -> (solid in its own frame, rotation for the bed, how to print, supports)
  front_down = "front face (the side towards you) down"
  parts["steering-wheel-teeth-one-piece"] = (WP.teeth_one_piece(t, whole), (180, 0, 0), front_down, "none")
  parts["steering-wheel-teeth-left-half"] = (WP.teeth_half(t, "left", whole), (180, 0, 0), front_down, "none")
  parts["steering-wheel-teeth-right-half"] = (WP.teeth_half(t, "right", whole), (180, 0, 0), front_down, "none")
  parts["fit-test-steering-wheel"] = (WP.grip_fit_test(t), (180, 0, 0), front_down, "none")
  parts["fit-test-teeth"] = (WP.tooth_fit_test(t), (180, 0, 0), front_down, "none")
  parts["motor-gear"] = (WP.motor_gear(), (0, 0, 0), "roller down", "none")
  parts["motor-carrier"] = (MP.motor_carrier(), (180, 0, 0), "finger guard down",
                            "inside the finger guard only (supports touching the build plate only)")
  parts["hinge-block"] = (MP.hinge_block(), (180, 0, 0), "front end (the end towards you) down",
                          "tree supports, everywhere (small areas under the switch cage, the lever's walls and the hinge)")
  parts["lift-lever"] = (MP.lift_lever(), (0, 90, 0), "on its side", "none")
  parts["dash-clamp"] = (MP.dash_clamp(), (0, 90, 0), "on its side",
                         "tree supports under the upper side plate, everywhere")
  parts["clamp-pad"] = (MP.clamp_pad(), (180, 0, 0), "flat face down", "none")
  parts["setup-gauge"] = (MP.setup_gauge(), (90, 0, 0), "flat", "none")
  arm_lengths = list(P.ARM_LENGTHS) + [L for L in args.arm if L not in P.ARM_LENGTHS]
  arms = {}
  for L in arm_lengths:
    arms[L] = MP.arm(L)
    parts[f"arms/arm-{L:05.1f}".replace(".0", "") if L != int(L) else f"arms/arm-{int(L):03d}"] = (arms[L], (0, 90, 0), "on its side", "none")

  part_rows = []
  bed = args.bed
  for name, (m, rot, how, supports) in parts.items():
    placed = on_bed(m, rot)
    # turn it about the vertical to fit the bed if it needs to
    best = None
    for zr in range(0, 91, 5):
      p2 = on_bed(placed, (0, 0, zr))
      x0, y0, z0, x1, y1, z1 = p2.bounding_box()
      sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
      fit = sx <= bed[0] and sy <= bed[1] and sz <= bed[2]
      if best is None or (fit and not best[0]) or (fit == best[0] and max(sx / bed[0], sy / bed[1]) < best[2]):
        best = (fit, p2, max(sx / bed[0], sy / bed[1]), (sx, sy, sz), zr)
    fits, p2, _, size, zr = best
    pieces = len(m.decompose())
    status = str(m.status()).split(".")[-1]
    support_mm2, _ = support_area(p2)
    vol = m.volume() / 1000.0
    row = {"file": name + ".stl", "print": how + (f", turned {zr} degrees on the bed" if zr else ""), "supports": supports,
           "size_mm": [round(s, 1) for s in size], "fits_bed": fits, "solid_volume_cm3": round(vol, 1),
           "filament_if_solid_g": round(vol * ASA_DENSITY, 1), "pieces": pieces, "closed_solid": status == "NoError",
           "overhang_needing_support_mm2": round(support_mm2)}
    part_rows.append(row)
    if pieces != 1 or status != "NoError":
      problems.append(f"{name}: not one closed solid ({pieces} pieces, {status})")
    if not fits and "one-piece" not in name:
      problems.append(f"{name}: {size[0]:.0f} x {size[1]:.0f} x {size[2]:.0f} mm does not fit the print bed")
    write_stl(p2, os.path.join(args.out, name + ".stl"), name.split("/")[-1])
  report["parts"] = part_rows

  # ----- gears mesh through the whole range of the teeth -----
  ring = WP.teeth_outline(t)
  motor = GR.gear_outline(P.MOTOR_TEETH, P.BACKLASH)
  cd = WP.centre_distance()
  phase = WP.MOTOR_GEAR_PHASE
  sweep = np.linspace(-t.teeth_half, t.teeth_half, 601)
  over = GR.mesh_sweep(ring, P.RING_TEETH, motor, P.MOTOR_TEETH, cd, sweep, phase)
  plays = []
  for w in np.linspace(-t.teeth_half + 3 * t.pitch_deg, t.teeth_half - 3 * t.pitch_deg, 7):
    ratio = P.RING_TEETH / P.MOTOR_TEETH
    ccw, cw = GR.free_play(ring.rotate(float(w)), motor, cd, phase - float(w) * ratio, P.MOTOR_TEETH)
    plays.append((ccw + cw) / ratio)      # free play in steering wheel degrees
  report["gears"] = {"teeth_on_steering_wheel": P.TEETH_ON_WHEEL, "steering_wheel_turn_with_teeth_deg": round(t.teeth_arc_deg, 1),
                     "steering_wheel_turn_tracked_deg": round(t.tracked_arc_deg, 1),
                     "gear_ratio": round(P.RING_TEETH / P.MOTOR_TEETH, 4), "most_overlap_mm2": round(max(over), 4),
                     "free_play_steering_wheel_deg": [round(min(plays), 3), round(max(plays), 3)]}
  if max(over) > 1e-3:
    problems.append(f"the gears overlap by {max(over):.3f} mm2 somewhere in the range of the teeth")

  # ----- lift lever, spring, power switch -----
  rows = MP.lever_lift_table(1.0)
  lift_up = MP.cam_lift(MP.A_OFF)
  most = max(r[1] for r in rows)
  first_lift = next(r[0] for r in rows if r[1] > 0.05)
  switch_release = math.degrees(math.asin((MP.SW_PRESS + 1.0) / (MP.SW_D - MP.SW_LEN / 2)))
  report["lift_lever"] = {
    "turns_deg": MP.A_HARD_STOP, "carrier_lift_up_deg": round(lift_up, 2), "most_lift_deg": round(most, 2),
    "starts_lifting_at_deg": first_lift, "switch_releases_by_deg": round(switch_release, 1),
    "most_push_at_handle_end_N": round(max(r[2] for r in rows), 1),
    "push_to_bring_it_back_down_N": round(-min(r[2] for r in rows), 1),
    "table_deg_liftdeg_N": [[r[0], round(r[1], 2), round(r[2], 2)] for r in rows[::2]]}
  report["spring"] = {"part": "Lee Spring LCM100E03S (9 mm outside, 1 mm wire, 28.5 mm long, 1.98 N/mm)",
                      "length_gear_on_teeth_mm": MP.SPRING_LEN, "force_gear_on_teeth_N": round(MP.spring_force(0), 1),
                      "length_lever_up_mm": round(MP.SPRING_LEN - MP.SPRING_ARM * math.sin(math.radians(most)), 1),
                      "force_lever_up_N": round(MP.spring_force(most), 1), "most_load_N": MP.SPRING_MAX_N,
                      "fully_squashed_mm": MP.SPRING_SOLID}
  if MP.spring_force(most) > MP.SPRING_MAX_N:
    problems.append("the spring is pushed past its most load when the lever is up")
  if switch_release >= first_lift:
    problems.append("the power switch lets go after the motor gear starts to lift")

  # ----- fit in the car -----
  fit = AS.solve(t, args.clamp_up, args.clamp_forward)
  report["fit"] = {"ok": fit.ok, "arm_to_steering_column_deg": round(fit.arm_deg, 1),
                   "arm_below_level_deg": round(fit.arm_below_level, 1), "bolt_to_bolt_mm": round(fit.reach, 1),
                   "arm_to_print": f"arm-{int(fit.arm_len):03d}.stl" if fit.arm_len else None,
                   "slide_from_middle_mm": round(fit.slide, 1), "notes": fit.notes}
  base = {"teeth": parts["steering-wheel-teeth-one-piece"][0], "gear": parts["motor-gear"][0],
          "gear_teeth_only": WP.motor_gear_teeth_only(), "carrier": parts["motor-carrier"][0],
          "hinge_block": parts["hinge-block"][0], "lever": parts["lift-lever"][0], "clamp": parts["dash-clamp"][0]}
  checks = {}
  if fit.ok:
    assy = dict(base)
    assy["arm"] = arms.get(fit.arm_len) or MP.arm(fit.arm_len)
    A = AS.Assembly(t, fit, assy)
    checks = AS.check_all(A)
    bad = [k for k, v in checks.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
    for k in bad:
      problems.append(f"parts touch: {k} ({checks[k]:.2f} mm3)")
    report["clearances"] = margins(A, AS, MP)
  else:
    problems.append("the parts do not reach from your dash clamp position: " + "; ".join(fit.notes))
  report["touching_checks_mm3"] = {k: round(v, 3) for k, v in checks.items()}

  # which dash clamp positions work
  grid = {"up_mm": [40, 60, 80, 105, 130, 160], "forward_mm": [80, 110, 140, 175, 210, 250], "cells": []}
  for u in grid["up_mm"]:
    row = []
    for f in grid["forward_mm"]:
      g = AS.solve(t, u, f)
      if not g.ok:
        row.append("no: " + g.notes[0])
        continue
      assy = dict(base)
      assy["arm"] = arms.get(g.arm_len) or MP.arm(g.arm_len)
      res = AS.check_all(AS.Assembly(t, g, assy), lever_step=8.0)
      bad = [k for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
      row.append(f"arm-{int(g.arm_len):03d}" if not bad else "no: parts touch (" + bad[0] + ")")
    grid["cells"].append(row)
  report["dash_clamp_positions"] = grid

  # ----- pictures -----
  if not args.no_pictures and fit.ok:
    pictures(A, MP, AS, parts, args.report, on_bed)
    report["pictures"] = ["assembly-side.png", "assembly-3d.png", "parts.png", "lift-lever-section.png"]

  report["problems"] = problems
  report["seconds"] = round(time.time() - t_start, 1)
  with open(os.path.join(args.report, "parts_report.json"), "w") as f:
    json.dump(report, f, indent=2)
  with open(os.path.join(args.report, "parts_report.txt"), "w") as f:
    f.write(text_report(report))
  print(text_report(report))
  return 1 if problems else 0


def support_area(m, max_angle: float = 45.0):
  """Area (mm^2) of downward faces steeper than max_angle from upright that are not on the bed, and the bed area."""
  mesh = m.to_mesh()
  v = np.asarray(mesh.vert_properties)[:, :3]
  tri = np.asarray(mesh.tri_verts)
  a, b, c = v[tri[:, 0]], v[tri[:, 1]], v[tri[:, 2]]
  n = np.cross(b - a, c - a)
  area = np.linalg.norm(n, axis=1) / 2
  nz = n[:, 2] / np.maximum(np.linalg.norm(n, axis=1), 1e-12)
  zmin = np.minimum(np.minimum(a[:, 2], b[:, 2]), c[:, 2]) - v[:, 2].min()
  steep = (nz < -math.cos(math.radians(max_angle))) & (zmin > 0.3)
  on_bed_faces = (nz < -0.999) & (zmin <= 0.3)
  return float(area[steep].sum()), float(area[on_bed_faces].sum())


def margins(A, AS, MP) -> dict:
  """How far apart the parts that come closest are (mm)."""
  def gap(moving, fixed, direction):
    lo, hi = 0.0, 25.0
    d = np.asarray(direction, dtype=float)
    for _ in range(26):
      mid = (lo + hi) / 2
      if AS.overlap(moving.translate(tuple(d * mid)), fixed) > 1e-3:
        hi = mid
      else:
        lo = mid
    return round(lo, 2)
  lift = MP.cam_lift(MP.A_OFF)
  down = (0.0, -1.0, 0.0)
  out = {"motor_gear_to_teeth_with_lever_up": min(gap(A.gear(lift), A.teeth(w), down) for w in (0, 10, 20, 29)),
         "carrier_to_steering_wheel_wheel_turned": gap(A.carrier(-MP.DROP_DEG), A.wheel_grip(), down),
         "motor_gear_teeth_to_steering_wheel_wheel_turned":
           gap(AS.turn_about_x(A.p["gear_teeth_only"].translate(tuple(A.b_org)), MP.DROP_DEG, A.hinge_w), A.wheel_grip(), down)}
  return out


def pictures(A, MP, AS, parts, folder, on_bed):
  import render as R
  from cadlib import box
  lift = MP.cam_lift(MP.A_OFF)
  col = {"teeth": (.72, .72, .72), "grip": (.3, .3, .3), "gear": (.95, .6, .25), "carrier": (.35, .55, .85), "motor": (.25, .25, .25),
         "hinge": (.45, .75, .45), "lever": (.85, .3, .3), "switch": (.9, .85, .2), "arm": (.6, .5, .4), "clamp": (.5, .7, .7),
         "hood": (.85, .85, .75)}

  def scene(lift_deg=0.0, alpha=0.0, wheel=0.0, crop=None, cut_x=None):
    items = [(A.teeth(wheel), col["teeth"]), (A.wheel_grip(), col["grip"]), (A.gear(lift_deg), col["gear"]),
             (A.carrier(lift_deg), col["carrier"]), (A.motor(lift_deg), col["motor"]), (A.hinge_block(), col["hinge"]),
             (A.lever(alpha), col["lever"]), (A.switch(), col["switch"]), (A.arm(), col["arm"]), (A.clamp(), col["clamp"]),
             (A.hood(), col["hood"])]
    out = []
    for m, c in items:
      if crop is not None:
        m = m ^ crop
      if cut_x is not None:
        m = m ^ box(-400, cut_x, -2000, 2000, -2000, 2000)
      if not m.is_empty():
        out.append((m, c))
    return out

  side = R.look((1, 0, 0), A.up)
  R.save(os.path.join(folder, "assembly-side.png"),
         [(scene(), side), (scene(lift, MP.A_OFF), side), (scene(-MP.DROP_DEG, 0.0, 70.0), side)],
         ["lift lever down: motor gear on the teeth", "lift lever up: motor gear lifted off",
          "steering wheel turned 70 degrees"],
         suptitle="Seen from the driver's right (the driver is on the left; cover over the gauges at the top right)",
         size=(700, 760))
  iso = R.look((1.0, 0.8, 0.9), A.up)
  crop = box(-200, 200, A.b_org[1] - 70, A.b_org[1] + 120, A.b_org[2] - 140, A.b_org[2] + 50)
  R.save(os.path.join(folder, "assembly-3d.png"),
         [(scene(crop=crop), iso), (scene(lift, MP.A_OFF, crop=crop), iso)], ["lift lever down", "lift lever up"],
         size=(900, 760))
  R.save(os.path.join(folder, "lift-lever-section.png"),
         [(scene(crop=crop, cut_x=0.0), side), (scene(lift, MP.A_OFF, crop=crop, cut_x=0.0), side)],
         ["lever down (cut through the middle)", "lever up: the cam pushes the carrier's fin down"], size=(900, 760))
  # every part as it sits on the bed
  names = ["steering-wheel-teeth-left-half", "steering-wheel-teeth-right-half", "motor-gear", "motor-carrier", "hinge-block",
           "lift-lever", "dash-clamp", "clamp-pad", "setup-gauge", "fit-test-steering-wheel", "fit-test-teeth", "arms/arm-130"]
  view = R.look((0.8, -1.0, 0.7), (0, 0, 1))
  panels, titles = [], []
  for n in names:
    m, rot, how, sup = parts[n]
    panels.append(([(on_bed(m, rot), (.55, .7, .9))], view))
    titles.append(n.split("/")[-1])
  for i in range(0, len(panels), 4):
    R.save(os.path.join(folder, f"parts-{i // 4 + 1}.png"), panels[i:i + 4], titles[i:i + 4], size=(560, 500))


def text_report(r: dict) -> str:
  L = []
  inp = r["inputs"]
  L.append("Honda Accord lane keeping motor: printed parts report")
  L.append("")
  L.append(f"Steering wheel {inp['steering_wheel_across_mm']} mm across, {inp['grip_mm']} mm thick where you hold it. "
           f"Dash clamp bolt {inp['dash_clamp_bolt_up_mm']} mm up and {inp['dash_clamp_bolt_forward_mm']} mm forward of the "
           f"motor gear's centre. Print bed {inp['print_bed_mm'][0]:.0f} x {inp['print_bed_mm'][1]:.0f} x {inp['print_bed_mm'][2]:.0f} mm.")
  L.append("")
  L.append("PARTS (each STL is already turned the way it goes on the print bed)")
  for p in r["parts"]:
    s = p["size_mm"]
    L.append(f"  {p['file']:<42} {s[0]:5.0f} x {s[1]:4.0f} x {s[2]:4.0f} mm  {'fits' if p['fits_bed'] else 'TOO BIG'}  "
             f"{p['filament_if_solid_g']:5.0f} g if solid")
    L.append(f"      print {p['print']}; supports: {p['supports']}")
  g = r["gears"]
  L.append("")
  L.append(f"GEARS: ratio {g['gear_ratio']} (motor turns {g['gear_ratio']:.2f} times per steering wheel turn). Teeth cover "
           f"{g['steering_wheel_turn_with_teeth_deg']} degrees of steering wheel turn; the motor gear follows over "
           f"{g['steering_wheel_turn_tracked_deg']} degrees. Most overlap anywhere in the range: {g['most_overlap_mm2']} mm2 "
           f"(should be 0). Free play at the steering wheel: {g['free_play_steering_wheel_deg'][0]} to "
           f"{g['free_play_steering_wheel_deg'][1]} degrees.")
  lv = r["lift_lever"]
  sp = r["spring"]
  L.append("")
  L.append(f"LIFT LEVER: turns {lv['turns_deg']:.0f} degrees from down to up. The power switch lets go within "
           f"{lv['switch_releases_by_deg']} degrees; the motor gear starts to lift at {lv['starts_lifting_at_deg']:.0f} degrees. "
           f"Up, the carrier is turned {lv['carrier_lift_up_deg']} degrees (most {lv['most_lift_deg']} on the way). "
           f"It takes up to {lv['most_push_at_handle_end_N']} N (about {lv['most_push_at_handle_end_N'] / 9.81:.1f} kg) at the end of "
           f"the handle to lift, and {lv['push_to_bring_it_back_down_N']} N to start it back down.")
  L.append(f"SPRING: {sp['part']}. {sp['length_gear_on_teeth_mm']} mm long and {sp['force_gear_on_teeth_N']} N with the motor gear "
           f"on the teeth; {sp['length_lever_up_mm']} mm and {sp['force_lever_up_N']} N with the lever up (its most is "
           f"{sp['most_load_N']} N at {sp['fully_squashed_mm']} mm).")
  f = r["fit"]
  L.append("")
  L.append("FIT IN THE CAR (for the dash clamp position above)")
  if f["ok"]:
    L.append(f"  print {f['arm_to_print']}: bolt to bolt {f['bolt_to_bolt_mm']} mm, the arm slid {f['slide_from_middle_mm']:+.1f} mm "
             f"from the middle of its slot; the arm points {f['arm_below_level_deg']} degrees below level "
             f"({f['arm_to_steering_column_deg']} degrees to the steering column).")
  else:
    L.append("  does not fit: " + "; ".join(f["notes"]))
  if "clearances" in r:
    c = r["clearances"]
    L.append(f"  lever up: motor gear {c['motor_gear_to_teeth_with_lever_up']} mm clear of the steering wheel teeth")
    L.append(f"  steering wheel turned past the teeth: carrier {c['carrier_to_steering_wheel_wheel_turned']} mm and the motor "
             f"gear's teeth {c['motor_gear_teeth_to_steering_wheel_wheel_turned']} mm clear of the steering wheel")
  touching = [k for k, v in r["touching_checks_mm3"].items() if ("should touch" not in k and v > 1e-3)]
  L.append(f"  {len(r['touching_checks_mm3'])} clearance checks, {len(touching)} touching")
  gr = r["dash_clamp_positions"]
  L.append("")
  L.append("WHICH DASH CLAMP POSITIONS WORK (rows: mm up from the motor gear's centre; columns: mm forward)")
  L.append("        " + "".join(f"{x:>12}" for x in gr["forward_mm"]))
  for u, row in zip(gr["up_mm"], gr["cells"]):
    L.append(f"  {u:5}  " + "".join(f"{(c if not c.startswith('no') else 'no'):>12}" for c in row))
  L.append("")
  if r["problems"]:
    L.append("PROBLEMS")
    for p in r["problems"]:
      L.append("  " + p)
  else:
    L.append("All checks passed.")
  L.append("")
  return "\n".join(L)


if __name__ == "__main__":
  sys.exit(main())
