#!/usr/bin/env python3
"""
Printed parts for the lane keeping motor on a 2008-2012 Honda Accord.

  steering wheel teeth  - zip-tied around the top of the steering wheel (one piece, or two halves for smaller printers);
                          two sets: 15 (reach 15 degrees each way, for getting used to it) and 29 (29 degrees each way)
  motor gear            - on the motor's shaft; meshes with the steering wheel teeth
  motor carrier         - the motor bolts to it; finger guard around the motor gear; turns on the hinge block's hinge
  lever bracket         - screws onto the carrier; holds the lift lever, the power switch and the lever's click
  hinge block           - holds the carrier's hinge and the spring; the lift lever presses on it; the arm bolts to it
  lift lever            - on the driver's side. Down: motor gear on the teeth, motor powered. Flipped up: motor's power
                          cut, motor gear lifted off
  arm                   - dash clamp to hinge block; printed in several lengths, each slides +-15 mm at the dash clamp
  dash clamp            - grips the edge of the cover over the gauges
  clamp pad             - swivel pad on the end of the dash clamp's screw
  setup gauge           - spacer used while adjusting the arm (sets the gap between the carrier and the hinge block)
  fit tests             - a short piece of the steering wheel teeth to try on your steering wheel, and a few teeth to
                          try against the printed motor gear

  column mount (hardware/stl/column-mount): the motor under the steering wheel, behind it, on a clamp round the
  steering column covers instead of the dash (columnparts.py):
  ring teeth            - zip-tied round the bottom of the steering wheel; a skirt behind the wheel carries a ring of
                          teeth facing the hub, the motor gear runs inside it (the short set only)
  column clamp          - two V saddles round the steering column covers on four M6 threaded rods; the lower one
                          carries the arm's joint
  hinge block (column)  - the hinge block with its arm slot centred on an arm closer to the column
  motor carrier (column)- the carrier with its finger guard open a little wider towards the ring
  fit test              - a few ring teeth to try the printed motor gear in
  The motor gear, lever bracket, lift lever, arm and setup gauge are the same parts.

  right-side mount (hardware/stl/column-mount-right): the same motor parts turned a quarter turn round the column,
  the ring teeth at 3 o'clock on the back of the wheel and the motor behind it there; the arm back to a bracket on the
  right-hand side of the column covers, held to the dash's own screw at the driver's right (columnparts.py):
  ring teeth (right)    - the ring teeth with a shallow channel, so it can sit over the right spoke's junction with the
                          grip; zip tie slots all along it
  side bracket          - a flat plate zip-tied to the covers' right-hand side on two rubber strips, with the arm's
                          joint and a bar for the screw tab
  screw tab             - a bar from the side bracket to the dash's screw, three lengths, each adjustable
  The hinge block (column), motor carrier (column) and the fit test are the column mount's.

  back-teeth mount (hardware/stl/back-teeth-mount): teeth on the back of a channel round the grip from 1 to 5
  o'clock, facing the dash; the motor behind the wheel at 3 o'clock, just outside the grip, its shaft pointing at the
  column; the arm down to a plate under the steering column's lower cover, on the cover's own screws (faceparts.py):
  back teeth            - the channel with the teeth (a face gear, 166 teeth on a full circle) and the rolling band on
                          its back, in two sets: 15 degrees each way (one piece, for the highway) and 45 (two pieces
                          glued end to end, or one piece for 330 mm beds; off the highway)
  back motor gear       - 16 teeth (166 / 16 = 10.375, the other mounts' 197 / 19 = 10.368)
  back motor carrier    - the carrier with its finger guard open wider and the plate's lower edge cut back
  back hinge block      - the hinge block with the arm's joint underneath instead of on top
  back lift lever       - the lift lever with a paddle under its handle's end
  back arms             - three lengths, each slides +-15 mm
  column plate          - under the lower column cover, with the arm's other joint
  fit tests             - a short piece of the back teeth, and the piece over the right spoke's junction
  The lever bracket, spring (on an M5 washer) and setup gauge are the same parts.

Run it with no options to write every STL file (already turned the way it should sit on the print bed), a report,
and pictures. Options let you enter your own steering wheel's measurements, where your dash clamp ends up, or an
arm of an exact length:

  python3 accord_lka_parts.py
  python3 accord_lka_parts.py --wheel-od 366 --grip 32.5
  python3 accord_lka_parts.py --clamp-up 110 --clamp-forward 160
  python3 accord_lka_parts.py --clamp-up 60 --clamp-forward 175 --column-angle 20
  python3 accord_lka_parts.py --arm 143
  python3 accord_lka_parts.py --cover-width 118 --cover-height 92 --clamp-behind 180
  python3 accord_lka_parts.py --screw-right 50 --screw-down 70 --screw-behind 270 --cover-front-width 102
  python3 accord_lka_parts.py --cover-bottom 55 --spoke-from -50 --spoke-to -16

It checks that every part is one closed solid that fits the print bed; that the gears mesh without touching through
the whole range of the teeth; that nothing touches anything it shouldn't (the dash cover, the dash clamp and the bought
screws and bolts included) with the lift lever down, up and at every angle between, with the steering wheel turned
past the teeth either way, and with the setup gauge in place; that every bolt and screw is the right length; and which
dash clamp positions the parts can reach. It exits with an error if any check fails.
"""
import argparse
import dataclasses
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import params as P  # noqa: E402

PETG_DENSITY = 1.28     # g/cm^3, Bambu Lab PETG HF data sheet (V1.0)


def parse_args():
  ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  ap.add_argument("--wheel-od", type=float, default=P.WHEEL_OD, help="steering wheel, outside edge to outside edge (mm)")
  ap.add_argument("--grip", type=float, default=P.GRIP, help="thickness of the part of the steering wheel you hold, at the top (mm)")
  ap.add_argument("--clamp-up", type=float, default=P.ARM_PIVOT_UP,
                  help="dash clamp's bolt: mm above the motor gear's centre (in the car)")
  ap.add_argument("--clamp-forward", type=float, default=P.ARM_PIVOT_FORWARD,
                  help="dash clamp's bolt: mm ahead of the motor gear's centre (towards the windshield)")
  ap.add_argument("--column-angle", type=float, default=None,
                  help="your steering column's angle from level in degrees, if you measured it (a phone's level app laid on "
                       "the steering wheel's face reads 90 minus this); otherwise the arm must fit the whole tilt range")
  ap.add_argument("--arm", type=float, action="append", default=[], help="also make an arm of exactly this length (mm, bolt to bolt)")
  ap.add_argument("--cover-width", type=float, default=P.COVER_W,
                  help="column mount: the steering column covers, side to side, where the clamp sits (mm)")
  ap.add_argument("--cover-height", type=float, default=P.COVER_H, help="column mount: the covers, top to bottom, there (mm)")
  ap.add_argument("--clamp-behind", type=float, default=-P.CLAMP_Z,
                  help="column mount: the middle of the clamp, mm behind the middle of the part of the steering wheel you hold")
  ap.add_argument("--screw-right", type=float, default=P.SCREW_RIGHT,
                  help="right-side mount: the dash's screw, right of the steering wheel's outer edge at 3 o'clock (mm)")
  ap.add_argument("--screw-down", type=float, default=P.SCREW_DOWN, help="right-side mount: the screw below that point (mm)")
  ap.add_argument("--screw-behind", type=float, default=P.SCREW_BEHIND,
                  help="right-side mount: the screw's trim behind the front face of the steering wheel's rim (mm)")
  ap.add_argument("--cover-front-width", type=float, default=P.COVER_FRONT_W,
                  help="the column covers, side to side, at their front edge near the wheel (mm)")
  ap.add_argument("--ring-at", type=float, default=0.0,
                  help="right-side mount: turn the whole mount this many degrees above 3 o'clock (the screw tab's plate tilts with it)")
  ap.add_argument("--tab-length", type=float, default=None, help="right-side mount: also make a screw tab of exactly this length (mm)")
  ap.add_argument("--cover-bottom", type=float, default=-P.COVER_BOTTOM,
                  help="back-teeth mount: the lower column cover's underside, mm below the column's axis where the plate sits")
  ap.add_argument("--spoke-from", type=float, default=P.RIGHT_SPOKE_DEG[0],
                  help="back-teeth mount: the right spoke meets the grip from this angle (degrees from 3 o'clock, + up)")
  ap.add_argument("--spoke-to", type=float, default=P.RIGHT_SPOKE_DEG[1], help="back-teeth mount: ... to this angle")
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
  P.COVER_BOTTOM = -args.cover_bottom
  P.RIGHT_SPOKE_DEG = (args.spoke_from, args.spoke_to)

  import assembly as AS      # noqa: E402  (imported after the measurements are set)
  import gears as GR         # noqa: E402
  import mountparts as MP    # noqa: E402
  import wheelparts as WP    # noqa: E402
  import margins as MG       # noqa: E402
  from cadlib import on_bed, write_stl  # noqa: E402

  os.makedirs(args.out, exist_ok=True)
  os.makedirs(os.path.join(args.out, "arms"), exist_ok=True)
  os.makedirs(args.report, exist_ok=True)
  problems = []
  report = {"inputs": {"steering_wheel_across_mm": args.wheel_od, "grip_mm": args.grip,
                       "dash_clamp_bolt_up_mm": args.clamp_up, "dash_clamp_bolt_forward_mm": args.clamp_forward,
                       "column_tilt_deg": P.COLUMN_TILT, "your_column_angle_deg": args.column_angle,
                       "print_bed_mm": list(args.bed)}}

  # ----- parts -----
  teeth_sets = {reach: WP.Teeth(args.wheel_od, args.grip, reach) for reach in sorted(P.TEETH_SETS)}
  t = teeth_sets[29]
  parts = {}       # file name -> (solid in its own frame, rotation for the bed, how to print, supports)
  front_down = "front face (the side towards you) down"
  for reach, ts in teeth_sets.items():
    whole = WP.teeth_solid(ts)
    parts[f"steering-wheel-teeth-{reach}-one-piece"] = (WP.teeth_one_piece(ts, whole), (180, 0, 0), front_down, "none")
    parts[f"steering-wheel-teeth-{reach}-left-half"] = (WP.teeth_half(ts, "left", whole), (180, 0, 0), front_down, "none")
    parts[f"steering-wheel-teeth-{reach}-right-half"] = (WP.teeth_half(ts, "right", whole), (180, 0, 0), front_down, "none")
  parts["fit-test-steering-wheel"] = (WP.grip_fit_test(t), (180, 0, 0), front_down, "none")
  parts["fit-test-teeth"] = (WP.tooth_fit_test(t), (180, 0, 0), front_down, "none")
  parts["motor-gear"] = (WP.motor_gear(), (180, 0, 0), "teeth down", "none")
  parts["motor-carrier"] = (MP.motor_carrier(), (180, 0, 0), "finger guard down",
                            "inside the finger guard only (supports touching the build plate only)")
  parts["hinge-block"] = (MP.hinge_block(), (180, 0, 0), "front end (the end towards you) down",
                          "tree supports, everywhere (small areas under the hinge, the spring's pocket and the ears)")
  parts["lever-bracket"] = (MP.lever_bracket(), (90, 0, 0), "base plate down", "none")
  parts["lift-lever"] = (MP.lift_lever(), (0, 90, 0), "on its side, the side with the thin tab under the handle down", "none")
  parts["dash-clamp"] = (MP.dash_clamp(), (0, 90, 0), "on its side",
                         "tree supports under the upper side plate, everywhere")
  parts["clamp-pad"] = (MP.clamp_pad(), (180, 0, 0), "flat face down", "none")
  parts["setup-gauge"] = (MP.setup_gauge(), (90, 0, 0), "flat", "none")
  arm_lengths = list(P.ARM_LENGTHS) + [L for L in args.arm if L not in P.ARM_LENGTHS]
  arms = {}
  for L in arm_lengths:
    arms[L] = MP.arm(L)
    label = f"{int(L):03d}" if float(L).is_integer() else f"{L:05.1f}"
    parts[f"arms/arm-{label}"] = (arms[L], (0, 90, 0), "on its side", "none")

  part_rows = []
  bed = args.bed
  for name, (m, rot, how, supports) in parts.items():
    placed = on_bed(m, rot)
    # turn it about the vertical only if it needs that to fit the bed
    best = None
    for zr in range(0, 91, 5):
      p2 = on_bed(placed, (0, 0, zr))
      x0, y0, z0, x1, y1, z1 = p2.bounding_box()
      sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
      fit = sx <= bed[0] and sy <= bed[1] and sz <= bed[2]
      if best is None or (fit and not best[0]) or (not fit and not best[0] and max(sx / bed[0], sy / bed[1]) < best[2]):
        best = (fit, p2, max(sx / bed[0], sy / bed[1]), (sx, sy, sz), zr)
      if fit:
        break
    fits, p2, _, size, zr = best
    pieces = len(m.decompose())
    status = str(m.status()).split(".")[-1]
    support_mm2, _ = support_area(p2)
    vol = m.volume() / 1000.0
    row = {"file": name + ".stl", "print": how + (f", turned {zr} degrees on the bed" if zr else ""), "supports": supports,
           "size_mm": [round(s, 1) for s in size], "fits_bed": fits, "solid_volume_cm3": round(vol, 1),
           "filament_if_solid_g": round(vol * PETG_DENSITY, 1), "pieces": pieces, "closed_solid": status == "NoError",
           "overhang_needing_support_mm2": round(support_mm2)}
    part_rows.append(row)
    if pieces != 1 or status != "NoError":
      problems.append(f"{name}: not one closed solid ({pieces} pieces, {status})")
    if not fits and "one-piece" not in name:
      problems.append(f"{name}: {size[0]:.0f} x {size[1]:.0f} x {size[2]:.0f} mm does not fit the print bed")
    write_stl(p2, os.path.join(args.out, name + ".stl"), name.split("/")[-1])
  report["parts"] = part_rows

  # ----- gears mesh through the whole range of each set of teeth -----
  motor = GR.gear_outline(P.MOTOR_TEETH, P.BACKLASH)
  cd = WP.centre_distance()
  phase = WP.MOTOR_GEAR_PHASE
  ratio = P.RING_TEETH / P.MOTOR_TEETH
  report["gears"] = {"gear_ratio": round(ratio, 4), "sets": {}}
  for reach, ts in teeth_sets.items():
    ring = WP.teeth_outline(ts)
    sweep = np.linspace(-ts.teeth_half, ts.teeth_half, 601)
    over = GR.mesh_sweep(ring, P.RING_TEETH, motor, P.MOTOR_TEETH, cd, sweep, phase)
    plays = []
    for w in np.linspace(-ts.teeth_half + 3 * ts.pitch_deg, ts.teeth_half - 3 * ts.pitch_deg, 7):
      ccw, cw = GR.free_play(ring.rotate(float(w)), motor, cd, phase - float(w) * ratio, P.MOTOR_TEETH)
      plays.append((ccw + cw) / ratio)      # free play in steering wheel degrees
    report["gears"]["sets"][str(reach)] = {
      "teeth_on_steering_wheel": ts.n_teeth, "steering_wheel_turn_with_teeth_deg": round(ts.teeth_arc_deg, 1),
      "steering_wheel_turn_tracked_deg": round(ts.tracked_arc_deg, 1), "piece_spans_deg": round(2 * ts.half, 1),
      "zip_ties_deg": list(ts.tie_angles), "most_overlap_mm2": round(max(over), 4),
      "free_play_steering_wheel_deg": [round(min(plays), 3), round(max(plays), 3)]}
    if max(over) > 1e-3:
      problems.append(f"the gears overlap by {max(over):.3f} mm2 somewhere in the range of the {reach} teeth")

  # ----- lift lever, spring, power switch -----
  rows = MP.lever_lift_table(1.0)
  lift_up = MP.cam_lift(MP.A_OFF)
  up_rows = [r for r in rows if r[0] <= MP.A_OFF + 1e-9]
  most = max(r[1] for r in up_rows)
  first_lift = next(r[0] for r in rows if r[1] > 0.05)
  # the handle's underside over the switch's roller rises SW_PRESS + SW_MD before the switch is sure to let go
  switch_release = math.degrees(math.asin((MP.SW_PRESS + MP.SW_MD) / MP.SW_D))
  # carrier lift at which the motor gear's teeth come clear of the steering wheel teeth
  overlap_mm = (GR.pitch_radius(P.MOTOR_TEETH) + GR.MODULE) + (GR.pitch_radius(P.RING_TEETH) + GR.MODULE) - WP.centre_distance()
  gz = (P.Z_GEAR_TEETH[0] + P.Z_GEAR_TEETH[1]) / 2 - P.Z_MOTOR_FACE - MP.HINGE[1]
  gy = -MP.HINGE[0]
  clear_deg = next(th / 10 for th in range(1, 300)
                   if gy * math.cos(math.radians(th / 10)) + gz * math.sin(math.radians(th / 10)) - gy >= overlap_mm)
  clear_alpha = next(r[0] for r in rows if r[1] >= clear_deg)
  at_up = next(r for r in rows if abs(r[0] - MP.A_OFF) < 1e-9)
  past_up = next(r for r in rows if r[0] > MP.A_OFF + 1e-9)
  click = MP.finger_force()
  report["lift_lever"] = {
    "turns_deg": MP.A_OFF, "carrier_lift_up_deg": round(lift_up, 2), "most_lift_deg": round(most, 2),
    "starts_lifting_at_deg": first_lift, "switch_releases_by_deg": round(switch_release, 1),
    "motor_gear_out_of_mesh_at_deg": clear_alpha, "carrier_lift_out_of_mesh_deg": round(clear_deg, 1),
    "most_push_at_handle_end_N": round(max(r[2] for r in up_rows), 1),
    "most_push_with_rubbing_N": round(max(r[2] + r[3] for r in up_rows), 1),
    "push_to_bring_it_back_down_N": round(-at_up[2], 1), "push_to_bring_it_back_down_with_rubbing_N": round(-at_up[2] + at_up[3], 1),
    "push_to_go_past_up_N": round(past_up[2], 1), "rubbing_estimate": MP.RUB,
    "drop_gap_mm": round(MP.DROP_GAP, 2), "click": click,
    "table_deg_liftdeg_N_rubN": [[r[0], round(r[1], 2), round(r[2], 2), round(r[3], 2)] for r in rows[::2]]}
  # What the spring does at the motor gear with the gear on the teeth, leaving out the motor's own weight (which adds to
  # it). Its turning force about the hinge presses the roller onto the rolling band and holds the teeth in mesh; the
  # push that drives the teeth apart (the torque's share along the line between the gears' centres, at the 20 degree
  # tooth angle) acts at the teeth, further from the hinge than the roller.
  def from_hinge(z_range):
    """Distance along the shaft from the hinge to the middle of a contact (z range in the steering wheel frame)."""
    return (z_range[0] + z_range[1]) / 2 - P.Z_MOTOR_FACE - MP.HINGE[1]
  band_flat = (P.Z_ROLL[0], P.Z_ROLL[1] - max(0.0, t.r_roll - t.r_root))      # the rolling band's flat top
  roller_z = (max(band_flat[0], P.Z_GEAR_ROLLER[0]), min(band_flat[1], P.Z_GEAR_ROLLER[1]))
  mesh_z = (max(P.Z_TEETH[0], P.Z_GEAR_TEETH[0]), min(P.Z_TEETH[1], P.Z_GEAR_TEETH[1]))
  roller_n = MP.spring_torque(0) / from_hinge(roller_z)
  hold_n = MP.spring_torque(0) / from_hinge(mesh_z)
  apart_n = P.MOST_TORQUE_NM * 1000 / GR.pitch_radius(P.RING_TEETH) * math.tan(math.radians(GR.PRESSURE_ANGLE))
  report["spring"] = {"part": f"{MP.SPRING_PART} ({MP.SPRING_OD} mm outside, {MP.SPRING_WIRE} mm wire, {MP.SPRING_FREE:g} mm long, "
                              f"{MP.SPRING_RATE} N/mm)",
                      "length_gear_on_teeth_mm": MP.SPRING_LEN, "force_gear_on_teeth_N": round(MP.spring_force(0), 1),
                      "length_lever_up_mm": round(MP.SPRING_LEN - MP.SPRING_ARM * math.sin(math.radians(most)), 1),
                      "force_lever_up_N": round(MP.spring_force(most), 1), "most_load_N": MP.SPRING_MAX_N,
                      "fully_squashed_mm": MP.SPRING_SOLID,
                      "presses_roller_on_rolling_band_N": round(roller_n, 1), "holds_teeth_in_mesh_up_to_N": round(hold_n, 1),
                      "most_torque_at_steering_wheel_Nm": P.MOST_TORQUE_NM,
                      "most_torque_pushes_teeth_apart_N": round(apart_n, 1), "times_what_it_needs": round(hold_n / apart_n, 2)}
  if MP.spring_force(most) > MP.SPRING_MAX_N:
    problems.append("the spring is pushed past its most load when the lever is up")
  if hold_n <= apart_n:
    problems.append(f"the spring holds the teeth in mesh against {hold_n:.1f} N, less than the {apart_n:.1f} N the most "
                    "torque pushes them apart with")

  # ----- margins: every failure mode's factor (margins.py) -----
  mesh_mm = from_hinge(mesh_z)
  weight_n = MG.weight_hold(mesh_mm, (P.COLUMN_TILT_RANGE[0], P.COLUMN_TILT, P.COLUMN_TILT_RANGE[1]))
  report["margins"] = MG.table(report["spring"], mesh_mm, weight_n)
  for r in report["margins"]:
    if r["kind"] == "design" and r["status"] == "UNDER":
      problems.append(f"under the {MG.FLOOR} floor: {r['what']} ({r['factor']})")

  # Past the last tooth the roller still rides on the rolling band: ROLL_PAST_TEETH degrees flat, then down the band's
  # slope until the carrier stops dropping (DROP_DEG, the lift lever's rounded end on the hinge block). Through the
  # roller's grip the motor can still push the steering wheel there, much more weakly than through the teeth.
  ry, rz = -P.ROLLER_R - MP.HINGE[0], from_hinge(roller_z)       # roller's contact line, from the hinge (y, z)
  d = math.radians(MP.DROP_DEG)
  roller_drop = -(ry * (math.cos(d) - 1) - rz * math.sin(d))    # how far the roller can follow the band down (mm)
  on_slope_deg = P.END_LEAD_IN * min(1.0, roller_drop / (t.r_roll - t.r_base))
  weak_push_nm = roller_n * MP.RUB * t.r_roll / 1000
  report["past_last_tooth"] = {
    "roller_on_band_more_deg": round(P.ROLL_PAST_TEETH + on_slope_deg, 1), "flat_deg": P.ROLL_PAST_TEETH,
    "on_slope_deg": round(on_slope_deg, 1), "push_there_Nm_estimate": round(weak_push_nm, 2), "rubbing_estimate": MP.RUB,
    "sets": {str(reach): {"full_push_to_deg": round(ts.teeth_half, 1),
                          "weak_push_to_deg": round(ts.roll_half + on_slope_deg, 1)} for reach, ts in teeth_sets.items()}}
  if switch_release >= first_lift:
    problems.append("the power switch may still be on when the motor gear starts to lift")
  if switch_release >= clear_alpha - 3.0:
    problems.append("the power switch lets go too late (the motor gear is nearly out of mesh by then)")
  if abs(lift_up - MP.LIFT_DEG) > 0.05:
    problems.append(f"lever up holds the carrier at {lift_up:.2f} degrees, not {MP.LIFT_DEG}")
  if not (at_up[2] < 0 < past_up[2]):
    problems.append("the lift lever doesn't stay up by itself")

  # ----- bolt and screw lengths -----
  report["fasteners"] = MP.fastener_table()
  for row in report["fasteners"]:
    if not row["ok"]:
      problems.append(f"{row['bolt']} ({row['use']}) is the wrong length")

  # ----- fit in the car -----
  base = {"teeth": parts["steering-wheel-teeth-29-one-piece"][0], "gear": parts["motor-gear"][0],
          "gear_teeth_only": WP.motor_gear_teeth_only(), "carrier": parts["motor-carrier"][0],
          "hinge_block": parts["hinge-block"][0], "bracket": parts["lever-bracket"][0], "lever": parts["lift-lever"][0],
          "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(), "clamp": parts["dash-clamp"][0]}
  tilts = (P.COLUMN_TILT_RANGE[0], P.COLUMN_TILT, P.COLUMN_TILT_RANGE[1])

  def arm_for(up: float, forward: float, at_tilts=tilts) -> tuple[float, str]:
    """The arm that fits a dash clamp bolt this far up and forward of the motor gear's centre at each of these tilt
    settings of the steering wheel: it reaches, both joints are within their range and nothing touches. Of several,
    the one nearest the middle of its slide with the tilt in the middle. Returns (length, "") or (0, why not)."""
    sols = [AS.solve(t, up, forward, tl) for tl in at_tilts]
    angle_notes = [n for sol in sols for n in sol.notes if "arms cover" not in n]
    if angle_notes:
      return 0.0, angle_notes[0]
    cands = [L for L in P.ARM_LENGTHS if all(abs(sol.reach - L) <= P.ARM_SLIDE - 0.5 for sol in sols)]
    if not cands:
      reaches = sorted(sol.reach for sol in sols)
      return 0.0, (f"the dash clamp's bolt is {reaches[0]:.0f} to {reaches[-1]:.0f} mm from the hinge block's; "
                   "no arm covers all of it")
    middle = sols[len(sols) // 2]
    for L in sorted(cands, key=lambda L: abs(middle.reach - L)):
      assy = dict(base)
      assy["arm"] = arms.get(L) or MP.arm(L)
      for tl, sol in zip(at_tilts, sols):
        g = dataclasses.replace(sol, ok=True, arm_len=float(L), slide=sol.reach - L, notes=[])
        res = AS.check_all(AS.Assembly(t, g, dict(assy), tl), lever_step=8.0)
        bad = [k for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
        if bad:
          break
      else:
        return float(L), ""
    return 0.0, f"parts touch ({bad[0]})"

  your_tilt = args.column_angle if args.column_angle is not None else P.COLUMN_TILT
  arm_len, why_not = arm_for(args.clamp_up, args.clamp_forward, (args.column_angle,) if args.column_angle is not None else tilts)
  fit = AS.solve(t, args.clamp_up, args.clamp_forward, your_tilt)
  if arm_len:
    fit = dataclasses.replace(fit, ok=True, arm_len=arm_len, slide=fit.reach - arm_len, notes=[])
  else:
    fit = dataclasses.replace(fit, ok=False, arm_len=0.0, slide=0.0, notes=fit.notes or [why_not])
  report["fit"] = {"ok": fit.ok, "arm_to_steering_column_deg": round(fit.arm_deg, 1),
                   "arm_below_level_deg": round(fit.arm_below_level, 1), "bolt_to_bolt_mm": round(fit.reach, 1),
                   "arm_to_print": f"arm-{int(fit.arm_len):03d}.stl" if fit.arm_len else None,
                   "slide_from_middle_mm": round(fit.slide, 1), "notes": fit.notes}
  checks = {}
  if fit.ok:
    assy = dict(base)
    assy["arm"] = arms.get(fit.arm_len) or MP.arm(fit.arm_len)
    A = AS.Assembly(t, fit, assy, your_tilt)
    checks = AS.check_all(A)
    # the short teeth: the same checks, with the steering wheel turned past their end
    short = teeth_sets[15]
    assy15 = dict(assy, teeth=parts["steering-wheel-teeth-15-one-piece"][0])
    A15 = AS.Assembly(short, fit, assy15, your_tilt)
    for k, v in AS.check_all(A15, wheel_turn=short.half + 17.0).items():
      if "wheel turned" in k or "teeth" in k:
        checks["15 teeth, " + k] = v
    bad = [k for k, v in checks.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
    for k in bad:
      problems.append(f"parts touch: {k} ({checks[k]:.2f} mm3)")
    report["clearances"] = margins(A, AS, MP)
  else:
    problems.append("the parts do not reach from your dash clamp position: " + "; ".join(fit.notes))
  report["touching_checks_mm3"] = {k: round(v, 3) for k, v in checks.items()}

  # which dash clamp positions work, each with the arm that fits at every tilt setting
  grid = {"up_mm": [40, 60, 80, 105, 130, 160], "forward_mm": [80, 110, 140, 175, 210, 250], "tilt_deg": list(tilts),
          "cells": []}
  for u in grid["up_mm"]:
    row = []
    for f in grid["forward_mm"]:
      L, why_not = arm_for(u, f)
      if L:
        row.append(f"arm-{int(L):03d}")
        continue
      L_middle, _ = arm_for(u, f, (P.COLUMN_TILT,))
      # * fits with the tilt in the middle, but not at both ends of its range
      row.append(f"arm-{int(L_middle):03d}*" if L_middle else "no: " + why_not)
    grid["cells"].append(row)
  report["dash_clamp_positions"] = grid
  # the arm's slide at each tilt setting, for your position
  report["tilt_range"] = [{"tilt_deg": tl, "bolt_to_bolt_mm": round(AS.solve(t, args.clamp_up, args.clamp_forward, tl).reach, 1),
                           "slide_from_middle_mm": round(AS.solve(t, args.clamp_up, args.clamp_forward, tl).reach - fit.arm_len, 1)
                           if fit.arm_len else None}
                          for tl in ((args.column_angle,) if args.column_angle is not None else tilts)]

  # ----- pictures -----
  if not args.no_pictures and fit.ok:
    pictures(A, MP, AS, parts, args.report, on_bed)
    report["pictures"] = ["assembly-side.png", "assembly-3d.png", "lift-lever-section.png"] + \
      sorted(f for f in os.listdir(args.report) if f.startswith("parts-") and f.endswith(".png"))

  # ----- the column mount -----
  report["column_mount"] = column_mount(args, base, arms, problems, on_bed, write_stl, part_rows, bed)
  report["side_mount"] = side_mount(args, base, arms, problems, on_bed, write_stl, part_rows, bed)
  report["back_mount"] = back_mount(args, base, problems, on_bed, write_stl, part_rows, bed)

  report["problems"] = problems
  report["seconds"] = round(time.time() - t_start, 1)
  with open(os.path.join(args.report, "parts_report.json"), "w") as f:
    json.dump(report, f, indent=2)
  with open(os.path.join(args.report, "parts_report.txt"), "w") as f:
    f.write(text_report(report))
  print(text_report(report))
  return 1 if problems else 0


def column_mount(args, base: dict, arms: dict, problems: list, on_bed, write_stl, part_rows: list, bed) -> dict:
  """The column mount's parts, checks and report (columnparts.py, columnassembly.py). Its own STL files go to
  <out>/column-mount; the shared parts are the ones already written."""
  import columnassembly as CA   # noqa: E402
  import columnparts as CP      # noqa: E402
  import gears as GR            # noqa: E402
  import margins as MG          # noqa: E402
  import mountparts as MP       # noqa: E402
  import wheelparts as WP       # noqa: E402

  out = os.path.join(args.out, "column-mount")
  os.makedirs(out, exist_ok=True)
  rep = {"inputs": {"cover_width_mm": args.cover_width, "cover_height_mm": args.cover_height,
                    "clamp_middle_behind_grip_mm": args.clamp_behind, "motor_face_behind_grip_mm": -P.Z_MOTOR_FACE_C,
                    "estimates": {"hub_radius_mm": P.HUB_R, "hub_back_mm": -P.HUB_BACK_Z,
                                  "spokes_back_at_lever_mm": -P.SPOKE_BACK_Z, "dash_below_column_behind_grip_mm": -P.DASH_Z,
                                  "covers_front_edge_behind_grip_mm": -P.COVER_FRONT_Z,
                                  "open_arc_between_lower_spokes_deg": P.WINDOW_DEG}}}
  t = CP.RingTeeth(args.wheel_od, args.grip)
  front_down = "front face (the side towards you) down"
  cparts = {
    "ring-teeth": (CP.ring_teeth(t), (180, 0, 0), front_down, "none"),
    "fit-test-ring-teeth": (CP.ring_tooth_fit_test(t), (180, 0, 0), front_down, "none"),
    "column-clamp-upper": (CP.column_clamp_upper(), (0, 0, 0), "V up", "none"),
    "column-clamp-lower": (CP.column_clamp_lower(), (0, 0, 90), "on its side",
                           "tree supports under the upper side plate, everywhere"),
    "hinge-block-column": (MP.hinge_block(CP.ARM_NOMINAL_C), (180, 0, 0), "front end (the end towards you) down",
                           "tree supports, everywhere (small areas under the hinge, the spring's pocket and the ears)"),
    "motor-carrier-column": (MP.motor_carrier(CP.GUARD_WINDOW_C), (180, 0, 0), "finger guard down",
                             "inside the finger guard only (supports touching the build plate only)"),
  }
  rows = []
  for name, (m, rot, how, supports) in cparts.items():
    placed = on_bed(m, rot)
    best = None
    for zr in range(0, 91, 5):
      p2 = on_bed(placed, (0, 0, zr))
      x0, y0, z0, x1, y1, z1 = p2.bounding_box()
      sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
      fit_bed = sx <= bed[0] and sy <= bed[1] and sz <= bed[2]
      if best is None or (fit_bed and not best[0]):
        best = (fit_bed, p2, (sx, sy, sz), zr)
      if fit_bed:
        break
    fits, p2, size, zr = best
    pieces = len(m.decompose())
    status = str(m.status()).split(".")[-1]
    support_mm2, _ = support_area(p2)
    vol = m.volume() / 1000.0
    row = {"file": "column-mount/" + name + ".stl", "print": how + (f", turned {zr} degrees on the bed" if zr else ""),
           "supports": supports, "size_mm": [round(v, 1) for v in size], "fits_bed": fits, "solid_volume_cm3": round(vol, 1),
           "filament_if_solid_g": round(vol * PETG_DENSITY, 1), "pieces": pieces, "closed_solid": status == "NoError",
           "overhang_needing_support_mm2": round(support_mm2)}
    rows.append(row)
    part_rows.append(row)
    if pieces != 1 or status != "NoError":
      problems.append(f"column mount, {name}: not one closed solid ({pieces} pieces, {status})")
    if not fits:
      problems.append(f"column mount, {name}: {size[0]:.0f} x {size[1]:.0f} x {size[2]:.0f} mm does not fit the print bed")
    write_stl(p2, os.path.join(out, name + ".stl"), name)
  rep["parts"] = rows

  # the ring's teeth and the motor gear inside it: no overlap through the ring's whole arc, and the free play
  motor = GR.gear_outline(P.MOTOR_TEETH, P.BACKLASH)
  cd = CP.centre_distance()
  ring = CP.ring_teeth_outline(t)
  sweep = np.linspace(-t.teeth_half, t.teeth_half, 601)
  over = GR.mesh_sweep(ring, P.RING_TEETH, motor, P.MOTOR_TEETH, cd, sweep, WP.MOTOR_GEAR_PHASE, internal=True)
  ratio = P.RING_TEETH / P.MOTOR_TEETH
  plays = []
  for w in np.linspace(-t.teeth_half + 3 * t.pitch_deg, t.teeth_half - 3 * t.pitch_deg, 7):
    ccw, cw = CP.internal_free_play(ring.rotate(float(w)), motor, cd, WP.MOTOR_GEAR_PHASE + float(w) * ratio)
    plays.append((ccw + cw) / ratio)
  rep["gears"] = {"centre_distance_mm": round(cd, 2), "rolling_band_radius_mm": round(t.r_roll, 2), "teeth": t.n_teeth,
                  "steering_wheel_turn_with_teeth_deg": round(t.teeth_arc_deg, 1),
                  "steering_wheel_turn_tracked_deg": round(t.tracked_arc_deg, 1), "piece_spans_deg": round(t.span_deg, 1),
                  "zip_tie_slots": len(CP.slot_angles(t)), "slots_every_deg": CP.SLOT_EVERY_DEG,
                  "most_overlap_mm2": round(max(over), 4),
                  "free_play_steering_wheel_deg": [round(min(plays), 3), round(max(plays), 3)]}
  if max(over) > 1e-3:
    problems.append(f"column mount: the ring's teeth and the motor gear overlap by {max(over):.3f} mm2 somewhere in the ring's range")
  rep["window"] = CA.window_check(t)
  if not rep["window"]["ok"]:
    problems.append("column mount: the ring teeth don't fit between the steering wheel's lower spokes")

  # fit in the car for the given covers and clamp position, and the clearance checks
  cfit = CA.solve(args.cover_width, args.cover_height, -args.clamp_behind)
  rep["fit"] = {"ok": cfit.ok, "arm_to_steering_column_deg": round(cfit.arm_deg, 1), "bolt_to_bolt_mm": round(cfit.reach, 1),
                "arm_to_print": f"arm-{int(cfit.arm_len):03d}.stl" if cfit.arm_len else None,
                "slide_from_middle_mm": round(cfit.slide, 1),
                "saddle_middle_below_column_axis_mm": round(-CA.saddle_y(args.cover_width, args.cover_height), 1),
                "notes": cfit.notes}
  checks = {}
  cbase = dict(base, teeth=cparts["ring-teeth"][0], hinge_block=cparts["hinge-block-column"][0],
               carrier=cparts["motor-carrier-column"][0],
               clamp_lower=cparts["column-clamp-lower"][0], clamp_upper=cparts["column-clamp-upper"][0])
  cbase.pop("clamp", None)
  if cfit.ok:
    cbase["arm"] = arms.get(cfit.arm_len) or MP.arm(cfit.arm_len)
    A = CA.ColumnAssembly(t, cfit, cbase, args.cover_width, args.cover_height, -args.clamp_behind)
    checks = CA.check_all(A)
    bad = [k for k, v in checks.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
    for k in bad:
      problems.append(f"column mount, parts touch: {k} ({checks[k]:.2f} mm3)")
    rep["clearances"] = CA.margins(A)
    rep["clearances"]["parts_reach_back_to_mm_behind_grip"] = CA.reach_back(A)   # the dash below the column must be further
    if not args.no_pictures:
      column_pictures(A, CA, MP, cparts, args.report, on_bed)
  else:
    problems.append("column mount: the parts do not reach from the clamp position: " + "; ".join(cfit.notes))
  rep["touching_checks_mm3"] = {k: round(v, 3) for k, v in checks.items()}

  # which clamp positions work, for a range of cover heights (the arm that fits, after the clearance checks)
  grid = {"clamp_behind_mm": [160, 180, 200, 220, 250, 280, 310, 340], "cover_height_mm": [70, 85, 95, 110, 125], "cells": []}
  for h in grid["cover_height_mm"]:
    row = []
    for behind in grid["clamp_behind_mm"]:
      f = CA.solve(args.cover_width, h, -behind)
      if not f.ok:
        row.append("no")
        continue
      assy = dict(cbase, arm=arms.get(f.arm_len) or MP.arm(f.arm_len))
      A_ = CA.ColumnAssembly(t, f, assy, args.cover_width, h, -behind)
      res = CA.check_all(A_, lever_step=8.0, dash=False)
      bad = [k for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
      row.append(f"arm-{int(f.arm_len):03d} ({CA.reach_back(A_):.0f})" if not bad else "no")
    grid["cells"].append(row)
  rep["clamp_positions"] = grid

  # margins and the rods
  rep["margins"] = MG.column_rows(t)
  for r in rep["margins"]:
    if r["kind"] == "design" and r["status"] == "UNDER":
      problems.append(f"column mount, under the {MG.FLOOR} floor: {r['what']} ({r['factor']})")
  rep["fasteners"] = CP.clamp_fastener_rows(args.cover_height)
  for r in rep["fasteners"]:
    if not r["ok"]:
      problems.append(f"column mount: {r['bolt']} is too short for the covers' height range")
  return rep


def side_mount(args, base: dict, arms: dict, problems: list, on_bed, write_stl, part_rows: list, bed) -> dict:
  """The right-side mount's parts, checks and report (columnparts.py, columnassembly.py). Its own STL files go to
  <out>/column-mount-right; the hinge block, carrier and fit test are the column mount's, already written."""
  import columnassembly as CA   # noqa: E402
  import columnparts as CP      # noqa: E402
  import margins as MG          # noqa: E402
  import mountparts as MP       # noqa: E402

  out = os.path.join(args.out, "column-mount-right")
  os.makedirs(out, exist_ok=True)
  rep = {"inputs": {"screw_right_of_wheel_edge_mm": args.screw_right, "screw_below_that_mm": args.screw_down,
                    "screw_behind_rim_front_mm": args.screw_behind, "cover_width_mm": args.cover_width,
                    "cover_front_width_mm": args.cover_front_width, "cover_height_mm": args.cover_height,
                    "ring_above_3_oclock_deg": args.ring_at, "motor_face_behind_grip_mm": -P.Z_MOTOR_FACE_C,
                    "estimates": {"wiper_stalk_from_to_mm": [list(P.STALK_FROM), list(P.STALK_TO)],
                                  "key_cylinder_from_to_mm": [list(P.KEY_FROM), list(P.KEY_TO)],
                                  "covers_front_edge_behind_grip_mm": -P.COVER_FRONT_Z, "hub_radius_mm": P.HUB_R,
                                  "right_spoke_meets_grip_deg_below_3_oclock": [-P.RIGHT_SPOKE_DEG[1], -P.RIGHT_SPOKE_DEG[0]]}}}
  t = CP.RingTeeth(args.wheel_od, args.grip, shallow=True)
  sfit = CA.solve_side(args.cover_width, args.screw_right, args.screw_down, args.screw_behind, args.tab_length, args.ring_at)
  front_down = "front face (the side towards you) down"
  cparts = {
    "ring-teeth-right": (CP.ring_teeth(t), (180, 0, 0), front_down, "none"),
    "side-bracket": (CP.side_bracket(), (0, 90, 0), "the plate's inner face (the covers' side) down", "none"),
  }
  tab_lengths = list(CP.TAB_LENGTHS) + ([args.tab_length] if args.tab_length and args.tab_length not in CP.TAB_LENGTHS else [])
  for L in tab_lengths:
    cparts[f"screw-tab-{int(L):03d}"] = (CP.screw_tab(L, sfit.plate_y), (0, 0, 0), "back face (the dash's side) down", "none")
  rows = []
  for name, (m, rot, how, supports) in cparts.items():
    placed = on_bed(m, rot)
    best = None
    for zr in range(0, 91, 5):
      p2 = on_bed(placed, (0, 0, zr))
      x0, y0, z0, x1, y1, z1 = p2.bounding_box()
      sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
      fit_bed = sx <= bed[0] and sy <= bed[1] and sz <= bed[2]
      if best is None or (fit_bed and not best[0]):
        best = (fit_bed, p2, (sx, sy, sz), zr)
      if fit_bed:
        break
    fits, p2, size, zr = best
    pieces = len(m.decompose())
    status = str(m.status()).split(".")[-1]
    support_mm2, _ = support_area(p2)
    vol = m.volume() / 1000.0
    row = {"file": "column-mount-right/" + name + ".stl", "print": how + (f", turned {zr} degrees on the bed" if zr else ""),
           "supports": supports, "size_mm": [round(v, 1) for v in size], "fits_bed": fits, "solid_volume_cm3": round(vol, 1),
           "filament_if_solid_g": round(vol * PETG_DENSITY, 1), "pieces": pieces, "closed_solid": status == "NoError",
           "overhang_needing_support_mm2": round(support_mm2)}
    rows.append(row)
    part_rows.append(row)
    if pieces != 1 or status != "NoError":
      problems.append(f"right-side mount, {name}: not one closed solid ({pieces} pieces, {status})")
    if not fits:
      problems.append(f"right-side mount, {name}: {size[0]:.0f} x {size[1]:.0f} x {size[2]:.0f} mm does not fit the print bed")
    write_stl(p2, os.path.join(out, name + ".stl"), name)
  rep["parts"] = rows
  slots = sorted(CP.slot_angles(t))
  rep["ring"] = {"teeth": t.n_teeth, "piece_spans_deg": round(t.span_deg, 1), "zip_tie_slots": len(slots),
                 "slots_every_deg": CP.SLOT_EVERY_DEG, "channel_walls_reach_in_mm": CP.SHALLOW_REACH,
                 "piece_reaches_below_3_oclock_deg": round(t.half - args.ring_at, 1),
                 "piece_reaches_above_3_oclock_deg": round(t.half + args.ring_at, 1),
                 "note": "the teeth, rolling band and lead-in are the column mount's ring teeth, so its mesh sweep and free play apply"}

  rep["fit"] = {"ok": sfit.ok, "arm_to_steering_column_deg": round(sfit.arm_deg, 1), "bolt_to_bolt_mm": round(sfit.reach, 1),
                "arm_to_print": f"arm-{int(sfit.arm_len):03d}.stl" if sfit.arm_len else None,
                "slide_from_middle_mm": round(sfit.slide, 1),
                "screw_tab_to_print": f"screw-tab-{int(sfit.tab_len):03d}.stl" if sfit.tab_len else None,
                "tab_start_along_the_bar_mm": round(sfit.tab_x0 - CP.tab_slide_range()[0], 1),
                "bracket_middle_behind_grip_mm": round(-sfit.bracket_z, 1),
                "bracket_back_face_behind_rim_front_mm": round(P.GRIP / 2 - (sfit.bracket_z + CP.SB_PLATE_Z[0]), 1),
                "notes": sfit.notes, "warnings": sfit.warnings}
  checks = {}
  sbase = dict(base, teeth=cparts["ring-teeth-right"][0], hinge_block=MP.hinge_block(CP.ARM_NOMINAL_C),
               carrier=MP.motor_carrier(CP.GUARD_WINDOW_C), side_bracket=cparts["side-bracket"][0])
  sbase.pop("clamp", None)
  if sfit.ok:
    sbase["arm"] = arms.get(sfit.arm_len) or MP.arm(sfit.arm_len)
    sbase["screw_tab"] = cparts[f"screw-tab-{int(sfit.tab_len):03d}"][0]
    A = CA.SideAssembly(t, sfit, sbase, args.cover_width, args.cover_height, args.cover_front_width)
    checks = CA.check_all(A)
    bad = [k for k, v in checks.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
    for k in bad:
      problems.append(f"right-side mount, parts touch: {k} ({checks[k]:.2f} mm3)")
    rep["clearances"] = CA.margins(A)
    rep["clearances"]["parts_reach_back_to_mm_behind_grip"] = CA.reach_back(A)
    if not args.no_pictures:
      side_pictures(A, CA, MP, cparts, args.report, on_bed)
  else:
    problems.append("right-side mount: the parts do not reach: " + "; ".join(sfit.notes))
  rep["touching_checks_mm3"] = {k: round(v, 3) for k, v in checks.items()}

  # which screw positions work (the arm and tab that fit, after the clearance checks without the dash estimates)
  grid = {"screw_behind_mm": [240, 260, 280, 300, 320, 340], "screw_right_mm": [0, 25, 50, 75, 100, 125, 150], "cells": []}
  for right in grid["screw_right_mm"]:
    row = []
    for behind in grid["screw_behind_mm"]:
      f = CA.solve_side(args.cover_width, right, args.screw_down, behind, None, args.ring_at)
      if not f.ok:
        row.append("no")
        continue
      assy = dict(sbase, arm=arms.get(f.arm_len) or MP.arm(f.arm_len), screw_tab=cparts[f"screw-tab-{int(f.tab_len):03d}"][0])
      A_ = CA.SideAssembly(t, f, assy, args.cover_width, args.cover_height, args.cover_front_width)
      res = CA.check_all(A_, lever_step=8.0, dash=False)
      bad = [k for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
      row.append(f"arm-{int(f.arm_len):03d}/tab-{int(f.tab_len):03d}" if not bad else "no")
    grid["cells"].append(row)
  rep["screw_positions"] = grid

  # the lift lever flipped up swings in beside the covers: how wide they can be at their front
  widths = {"cover_front_width_mm": [90, 95, 100, 105, 110, 115, 120, 125], "lever_up_clear_by_mm": []}
  if sfit.ok:
    lift = MP.cam_lift(MP.A_OFF)
    lever_up = A.lever(MP.A_OFF, lift + 0.05)
    for w in widths["cover_front_width_mm"]:
      A_ = CA.SideAssembly(t, sfit, sbase, max(args.cover_width, w), args.cover_height, w)
      cov = A_.covers()
      lo, hi = 0.0, 30.0
      if CA.overlap(lever_up, cov) > 1e-3:
        widths["lever_up_clear_by_mm"].append("touches")
        continue
      for _ in range(20):
        mid = (lo + hi) / 2
        if CA.overlap(lever_up.translate((-mid, 0, 0)), cov) > 1e-3:
          hi = mid
        else:
          lo = mid
      widths["lever_up_clear_by_mm"].append(round(lo, 1))
  rep["cover_widths"] = widths

  rep["margins"] = MG.side_rows(t, sfit, args.cover_width)
  for r in rep["margins"]:
    if r["kind"] == "design" and r["status"] == "UNDER":
      problems.append(f"right-side mount, under the {MG.FLOOR} floor: {r['what']} ({r['factor']})")
  rep["fasteners"] = CP.bracket_fastener_rows()
  for r in rep["fasteners"]:
    if not r["ok"]:
      problems.append(f"right-side mount: {r['bolt']} is the wrong length")
  return rep


def back_part_list(t, pieces: dict, tests: dict, short_piece) -> dict:
  """The back-teeth mount's printed parts: name -> (part, how it turns onto the bed, how it prints, supports). pieces:
  the long back teeth's (45 degrees each way); short_piece: the short back teeth (15 degrees each way), one piece."""
  import faceparts as FP        # noqa: E402
  front_down = "front face (the side towards you) down"
  bparts = {
    "back-teeth-15": (short_piece, (180, 0, 0), front_down, "none"),
    "back-teeth-45-upper": (pieces["upper"], (180, 0, 0), front_down, "none"),
    "back-teeth-45-lower": (pieces["lower"], (180, 0, 0), front_down, "none"),
    "back-teeth-45-one-piece": (pieces["one-piece"], (180, 0, 0), front_down + " (for print beds 330 mm across)", "none"),
    "back-motor-gear": (FP.face_motor_gear(), (180, 0, 0), "teeth down", "none"),
    "back-motor-carrier": (FP.face_carrier(), (180, 0, 0), "finger guard down",
                           "inside the finger guard only (supports touching the build plate only)"),
    "back-hinge-block": (FP.face_hinge_block(t), (180, 0, 0), "front end (the end towards the column) down",
                         "tree supports, everywhere (small areas under the hinge, the spring's pocket and the ears)"),
    "back-lift-lever": (FP.back_lift_lever(), (0, 90, 0), "on its side, the side with the thin tab under the handle down", "none"),
    "column-plate": (FP.column_plate(t), (-90, 0, 0), "the flat top (the cover's side) down", "none"),
    "fit-test-back-teeth": (tests["teeth"], (180, 0, 0), front_down, "none"),
    "fit-test-back-teeth-spoke": (tests["spoke"], (180, 0, 0), front_down, "none"),
  }
  for L in FP.ARM_LENGTHS_F:
    bparts[f"back-arm-{int(L):03d}"] = (FP.face_arm(L), (90, 0, 0), "flat", "none")
  return bparts


def back_mount(args, base: dict, problems: list, on_bed, write_stl, part_rows: list, bed) -> dict:
  """The back-teeth mount's parts, checks and report (faceparts.py, faceassembly.py). Its STL files go to
  <out>/back-teeth-mount; the lever bracket and setup gauge are the dash mount's, already written."""
  import faceassembly as FA     # noqa: E402
  import faceparts as FP        # noqa: E402
  import margins as MG          # noqa: E402
  import mountparts as MP       # noqa: E402

  out = os.path.join(args.out, "back-teeth-mount")
  os.makedirs(out, exist_ok=True)
  t = FP.FaceTeeth(args.wheel_od, args.grip, P.RIGHT_SPOKE_DEG)
  rep = {"inputs": {"cover_bottom_below_column_axis_mm": args.cover_bottom, "right_spoke_meets_grip_deg": list(P.RIGHT_SPOKE_DEG),
                    "wheel_outer_radius_mm": args.wheel_od / 2,
                    "plate_front_behind_grip_mm": -P.PLATE_FRONT_Z,
                    "estimates": {"wiper_stalk_from_to_mm": [list(P.STALK_FROM), list(P.STALK_TO)],
                                  "key_cylinder_from_to_mm": [list(P.KEY_FROM), list(P.KEY_TO)],
                                  "covers_front_edge_behind_grip_mm": -P.COVER_FRONT_Z, "hub_radius_mm": P.HUB_R}}}
  whole = FP.face_solid(t)
  pieces = FP.face_pieces(t, whole)
  tests = FP.face_fit_tests(t, whole)
  t15 = FP.FaceTeeth(args.wheel_od, args.grip, P.RIGHT_SPOKE_DEG, n_teeth=FP.N_TEETH_SHORT)
  short_piece = FP.face_pieces(t15)["one-piece"]
  fit = FA.solve_face(t, P.COVER_BOTTOM)
  bparts = back_part_list(t, pieces, tests, short_piece)
  rows = []
  for name, (m, rot, how, supports) in bparts.items():
    placed = on_bed(m, rot)
    best = None
    for zr in range(0, 91, 5):
      p2 = on_bed(placed, (0, 0, zr))
      x0, y0, z0, x1, y1, z1 = p2.bounding_box()
      sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
      fit_bed = sx <= bed[0] and sy <= bed[1] and sz <= bed[2]
      if best is None or (fit_bed and not best[0]):
        best = (fit_bed, p2, (sx, sy, sz), zr)
      if fit_bed:
        break
    fits, p2, size, zr = best
    n_pieces = len(m.decompose())
    status = str(m.status()).split(".")[-1]
    support_mm2, _ = support_area(p2)
    vol = m.volume() / 1000.0
    row = {"file": "back-teeth-mount/" + name + ".stl", "print": how + (f", turned {zr} degrees on the bed" if zr else ""),
           "supports": supports, "size_mm": [round(v, 1) for v in size], "fits_bed": fits, "solid_volume_cm3": round(vol, 1),
           "filament_if_solid_g": round(vol * PETG_DENSITY, 1), "pieces": n_pieces, "closed_solid": status == "NoError",
           "overhang_needing_support_mm2": round(support_mm2)}
    rows.append(row)
    part_rows.append(row)
    if n_pieces != 1 or status != "NoError":
      problems.append(f"back-teeth mount, {name}: not one closed solid ({n_pieces} pieces, {status})")
    if not fits and "one-piece" not in name:
      problems.append(f"back-teeth mount, {name}: {size[0]:.0f} x {size[1]:.0f} x {size[2]:.0f} mm does not fit the print bed")
    write_stl(p2, os.path.join(out, name + ".stl"), name)
  rep["parts"] = rows

  def teeth_info(tt):
    return {"teeth": tt.n_teeth, "teeth_on_a_full_circle": FP.FACE_TEETH, "motor_gear_teeth": FP.FACE_MOTOR_TEETH,
            "gear_ratio": round(FP.FACE_RATIO, 4), "pitch_radius_mm": FP.R_F, "teeth_from_to_radius_mm": list(FP.FACE_BAND),
            "rolling_band_radius_mm": list(FP.ROLL_BAND), "steering_wheel_turn_with_teeth_deg": round(tt.teeth_arc_deg, 1),
            "steering_wheel_turn_tracked_deg": round(tt.tracked_arc_deg, 2), "full_push_reach_deg": round(tt.teeth_half, 1),
            "piece_spans_deg": round(tt.span_deg, 1),
            "joint_deg_above_3_oclock": round(tt.joint_deg, 2) if tt.joint_deg is not None else None,
            "zip_tie_slots_deg": [round(a, 2) for a in FP.tie_angles(tt)],
            "notch_for_the_right_spoke_deg": [round(a, 1) for a in tt.spoke], "notch_radius_mm": FP.NOTCH_R,
            "teeth_behind_grip_middle_mm": [round(-tt.z_root, 1), round(-tt.z_tip, 1)],
            "motor_face_from_column_axis_mm": FP.R_FACE, "motor_shaft_behind_grip_middle_mm": round(-tt.z_axis, 1)}
  rep["teeth"] = teeth_info(t)
  rep["teeth_short"] = teeth_info(t15)
  rep["fit"] = {"ok": fit.ok, "bolt_to_bolt_mm": round(fit.reach, 1),
                "arm_to_print": f"back-arm-{int(fit.arm_len):03d}.stl" if fit.arm_len else None,
                "slide_from_middle_mm": round(fit.slide, 1), "arm_up_from_level_deg": round(fit.j1_deg, 1),
                "joints_from_the_middle_of_their_slots_deg": round(fit.j1_off, 1),
                "plate_joint_mm": [round(v, 1) for v in fit.j1], "hinge_block_joint_mm": [round(v, 1) for v in fit.j2],
                "notes": fit.notes}
  checks = {}
  fparts = {"teeth": pieces["one-piece"], "gear": bparts["back-motor-gear"][0], "gear_teeth_only": FP.face_motor_gear_teeth_only(),
            "carrier": bparts["back-motor-carrier"][0], "bracket": base["bracket"], "lever": bparts["back-lift-lever"][0],
            "lever_no_tab": FP.back_lift_lever(with_finger=False), "tab": MP.lever_tab(),
            "hinge_block": bparts["back-hinge-block"][0], "plate": bparts["column-plate"][0]}
  if fit.ok:
    fparts["arm"] = bparts[f"back-arm-{int(fit.arm_len):03d}"][0]
    A = FA.FaceAssembly(t, fit, fparts, args.cover_width, args.cover_height, args.cover_front_width)
    mesh = FA.mesh_sweep(A, step=1.0)
    rep["mesh"] = mesh
    if mesh["worst_overlap_mm3"] > 1e-3:
      problems.append(f"back-teeth mount: the motor gear and the back teeth overlap by {mesh['worst_overlap_mm3']} mm3 at "
                      f"{mesh['worst_at_deg']} degrees")
    checks = FA.check_all(A)
    # the short back teeth: the same mount, the teeth piece ending sooner (the carrier drops at their ends)
    A15 = FA.FaceAssembly(t15, fit, dict(fparts, teeth=short_piece), args.cover_width, args.cover_height, args.cover_front_width)
    mesh15 = FA.mesh_sweep(A15, step=1.0)
    rep["mesh_short"] = mesh15
    if mesh15["worst_overlap_mm3"] > 1e-3:
      problems.append(f"back-teeth mount: the motor gear and the short back teeth overlap by {mesh15['worst_overlap_mm3']} mm3 at "
                      f"{mesh15['worst_at_deg']} degrees")
    for k, v in FA.check_all(A15, lever_step=8.0).items():
      checks["short back teeth: " + k] = v
    bad = [k for k, v in checks.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
    for k in bad:
      problems.append(f"back-teeth mount, parts touch: {k} ({checks[k]:.2f} mm3)")
    rep["clearances"] = FA.clearances(A)
    lift = MP.cam_lift(MP.A_OFF)
    tip_down = A.lever(0.0, 0.0).bounding_box()
    tip_up = A.lever(MP.A_OFF, lift).bounding_box()
    rep["clearances"]["lift_lever_nearest_you_down_mm_behind_grip"] = round(-tip_down[5], 0)
    rep["clearances"]["lift_lever_nearest_you_up_mm_behind_grip"] = round(-tip_up[5], 0)
    rep["clearances"]["parts_reach_out_from_column_mm"] = round(max(A.motor().bounding_box()[3], A.hinge_block().bounding_box()[3]), 0)
    if not args.no_pictures:
      back_pictures(A, FA, MP, bparts, args.report, on_bed)
  else:
    problems.append("back-teeth mount: the parts do not reach: " + "; ".join(fit.notes))
  rep["touching_checks_mm3"] = {k: round(v, 3) for k, v in checks.items()}
  rep["margins"] = MG.back_rows(t, fit)
  for r in rep["margins"]:
    if r["kind"] == "design" and r["status"] == "UNDER":
      problems.append(f"back-teeth mount, under the {MG.FLOOR} floor: {r['what']} ({r['factor']})")
  rep["fasteners"] = FA.fastener_rows()
  for r in rep["fasteners"]:
    if not r["ok"]:
      problems.append(f"back-teeth mount: {r['bolt']} is the wrong length")
  # where the cover's underside may be: the plate's joint moves with it; the arm and joints that still reach
  heights = {"cover_bottom_mm": [40, 45, 50, 55, 60, 65, 70], "fits": []}
  for h in heights["cover_bottom_mm"]:
    f_ = FA.solve_face(t, -h)
    heights["fits"].append(f"back-arm-{int(f_.arm_len):03d}, joints {f_.j1_off:+.0f} deg" if f_.ok else "no")
  rep["cover_heights"] = heights
  return rep


def back_pictures(A, FA, MP, bparts, folder, on_bed):
  import render as R
  from cadlib import box
  lift = MP.cam_lift(MP.A_OFF)
  front = R.look((0, 0, 1), (0, 1, 0))
  above = R.look((0, 1, 0), (0, 0, -1))
  R.save(os.path.join(folder, "back-assembly-front.png"),
         [(FA.parts_scene(A), front), (FA.parts_scene(A, lift, MP.A_OFF), front), (FA.parts_scene(A), above)],
         ["lift lever down: the motor gear on the back teeth", "lift lever up: the motor gear lifted off",
          "from above: the driver at the bottom, the dash at the top"],
         suptitle="Back-teeth mount from the driver's seat: the teeth on the back of the grip from 1 to 5 o'clock, the motor behind "
                  "the wheel at 3 o'clock, the arm down to the plate under the column (the wiper stalk and key cylinder are estimates)",
         size=(700, 700))
  iso = R.look((1.0, -0.6, -0.9), (0, 1, 0))
  crop = box(-60, 320, -200, 140, -260, 40)
  R.save(os.path.join(folder, "back-assembly-3d.png"),
         [([(m ^ crop, c) for m, c in FA.parts_scene(A) if not (m ^ crop).is_empty()], iso),
          ([(m ^ crop, c) for m, c in FA.parts_scene(A, lift, MP.A_OFF) if not (m ^ crop).is_empty()], iso)],
         ["lift lever down", "lift lever up"], size=(900, 760))
  back_parts_picture(bparts, folder, on_bed)


def back_parts_picture(bparts: dict, folder: str, on_bed):
  """The back-teeth mount's parts as they sit on the bed (one arm of the three), four to a row."""
  import render as R
  view = R.look((0.8, -1.0, 0.7), (0, 0, 1))
  panels, titles = [], []
  for n, (m, rot, _how, _sup) in bparts.items():
    if n.startswith("back-arm-") and not n.endswith("165"):
      continue
    panels.append(([(on_bed(m, rot), (.55, .7, .9))], view))
    titles.append(n)
  R.save(os.path.join(folder, "back-parts.png"), panels, titles, size=(560, 500), cols=4)


def back_text(c: dict, MG) -> list:
  L = [""]
  inp = c["inputs"]
  L.append("=" * 100)
  L.append("BACK-TEETH MOUNT: teeth on the back of a channel round the grip from 1 to 5 o'clock, facing the dash; the motor behind "
           "the wheel at 3 o'clock, its shaft pointing at the column; the arm down to a plate under the lower column cover")
  est = inp["estimates"]
  L.append(f"The lower column cover's underside {inp['cover_bottom_below_column_axis_mm']:.0f} mm below the column's axis where the "
           f"plate sits; the right spoke meets the grip from {inp['right_spoke_meets_grip_deg'][0]:.0f} to "
           f"{inp['right_spoke_meets_grip_deg'][1]:.0f} degrees from 3 o'clock (+ up); the plate's front end "
           f"{inp['plate_front_behind_grip_mm']:.0f} mm behind the middle of the grip. Estimates used for the checks: the wiper stalk "
           f"from {est['wiper_stalk_from_to_mm'][0]} to {est['wiper_stalk_from_to_mm'][1]}, the key cylinder from "
           f"{est['key_cylinder_from_to_mm'][0]} to {est['key_cylinder_from_to_mm'][1]} (steering wheel frame, mm: right, up, "
           "towards you from the middle of the grip).")
  L.append("")
  L.append("PARTS (back-teeth-mount folder; the lever bracket and setup gauge are the dash mount's)")
  for p in c["parts"]:
    s_ = p["size_mm"]
    L.append(f"  {p['file']:<48} {s_[0]:5.0f} x {s_[1]:4.0f} x {s_[2]:4.0f} mm  {'fits' if p['fits_bed'] else 'TOO BIG'}  "
             f"{p['filament_if_solid_g']:5.0f} g if solid")
    L.append(f"      print {p['print']}; supports: {p['supports']}")
  tt = c["teeth"]
  L.append("")
  L.append(f"BACK TEETH: a face gear, {tt['teeth_on_a_full_circle']} teeth on a full circle (2 mm teeth, {tt['pitch_radius_mm']:.0f} mm "
           f"from the column's axis), the motor gear {tt['motor_gear_teeth']} teeth: ratio {tt['gear_ratio']}. The teeth stand "
           f"{tt['teeth_behind_grip_middle_mm'][0]} to {tt['teeth_behind_grip_middle_mm'][1]} mm behind the middle of the grip; the "
           f"motor's front face {tt['motor_face_from_column_axis_mm']:.0f} mm from the column's axis, its shaft "
           f"{tt['motor_shaft_behind_grip_middle_mm']} mm behind the middle of the grip. No inner wall inside "
           f"{tt['notch_radius_mm']:.0f} mm from {tt['notch_for_the_right_spoke_deg'][0]} to {tt['notch_for_the_right_spoke_deg'][1]} "
           "degrees, over the right spoke's junction. Two sets:")
  for key, mkey, label in (("teeth_short", "mesh_short", "back-teeth-15, the short set (for the highway)"),
                           ("teeth", "mesh", "back-teeth-45, the long set (off the highway)")):
    s_ = c.get(key)
    if not s_:
      continue
    joint = (f"in two pieces meeting {s_['joint_deg_above_3_oclock']} degrees above 3 o'clock"
             if s_["joint_deg_above_3_oclock"] is not None else "one piece")
    L.append(f"  {label}: {s_['teeth']} teeth reaching {s_['full_push_reach_deg']} degrees each way; with the rolling band past "
             f"them the motor gear turns with the wheel over {s_['steering_wheel_turn_tracked_deg']} degrees. It spans "
             f"{s_['piece_spans_deg']} degrees, {joint}; zip tie slots at {s_['zip_tie_slots_deg']} degrees.")
    if mkey in c:
      m = c[mkey]
      L.append(f"    gear mesh through its whole arc (every 1 degree): worst overlap {m['worst_overlap_mm3']} mm3; free play "
               f"{m['free_play_steering_wheel_deg']} degrees of steering wheel (the motor gear turns {m['free_play_motor_gear_deg'][0][0]} "
               "degrees each way before its teeth touch).")
  f = c["fit"]
  L.append("")
  L.append("FIT IN THE CAR")
  if f["ok"]:
    L.append(f"  print {f['arm_to_print']}: bolt to bolt {f['bolt_to_bolt_mm']} mm, the arm slid {f['slide_from_middle_mm']:+.1f} mm "
             f"from the middle of its slot, rising {f['arm_up_from_level_deg']} degrees from the plate towards the motor; both "
             f"joints {f['joints_from_the_middle_of_their_slots_deg']:+.1f} degrees from the middle of their slots.")
  else:
    L.append("  does not fit: " + "; ".join(f["notes"]))
  if "clearances" in c:
    cl = c["clearances"]
    L.append(f"  lever up: the motor gear {cl['motor_gear_off_the_teeth_with_lever_up']} mm off the teeth (25 means more than 25); "
             f"the lift lever's paddle, lever down, {cl['lift_lever_nearest_you_down_mm_behind_grip']:.0f} mm behind the middle of "
             f"the grip, lever up {cl['lift_lever_nearest_you_up_mm_behind_grip']:.0f} mm; the parts reach "
             f"{cl['parts_reach_out_from_column_mm']:.0f} mm out from the column (the grip's outer edge is "
             f"{inp['wheel_outer_radius_mm']:.1f} mm); the column plate's corner {cl['joint_ears_to_the_key_cylinder']} mm "
             f"behind the key cylinder; the lever {cl['lift_lever_to_the_wiper_stalk']} mm and the hinge block and motor "
             f"{cl['hinge_block_and_motor_to_the_wiper_stalk']} mm below the wiper stalk.")
  touching = [k for k, v in c["touching_checks_mm3"].items() if ("should touch" not in k and v > 1e-3)]
  n_short = len([k for k in c["touching_checks_mm3"] if k.startswith("short back teeth: ")])
  L.append(f"  {len(c['touching_checks_mm3'])} clearance checks ({len(c['touching_checks_mm3']) - n_short} with the long back teeth, "
           f"{n_short} with the short), {len(touching)} touching")
  h = c["cover_heights"]
  L.append("")
  L.append("WHERE THE COVER'S UNDERSIDE MAY BE (mm below the column's axis): the arm and how far the joints turn from the middle of "
           "their slots (they turn 25 degrees each way)")
  for x, fit_ in zip(h["cover_bottom_mm"], h["fits"], strict=True):
    L.append(f"  {x:3d} mm: {fit_}")
  L.append("")
  L.append("MARGINS (the back-teeth mount's own; the shared parts' margins are above)")
  L += MG.text_lines(c["margins"])
  L.append("")
  L.append("BOLTS, SCREWS, TIES AND DOWELS")
  for b in c["fasteners"]:
    if b["length"]:
      L.append(f"  {b['bolt']:20s} {b['use']}: through {b['through_mm']} mm, then a {b['nut_mm']} mm lock nut: {b['past_the_nut_mm']} mm "
               f"to spare{'' if b['ok'] else '  WRONG LENGTH'}")
    else:
      L.append(f"  {b['bolt']}: {b['use']}")
  return L


def side_pictures(A, CA, MP, cparts, folder, on_bed):
  import render as R
  from cadlib import box
  lift = MP.cam_lift(MP.A_OFF)
  front = R.look((0, 0, 1), (0, 1, 0))
  R.save(os.path.join(folder, "side-assembly-front.png"),
         [(CA.parts_scene(A), front), (CA.parts_scene(A, lift, MP.A_OFF), front), (CA.parts_scene(A), R.look((0, 1, 0), (0, 0, -1)))],
         ["lift lever down: motor gear in the ring", "lift lever up: motor gear lifted off, the handle in towards the hub",
          "from above: the driver at the bottom, the dash at the top"],
         suptitle="Right-side mount from the driver's seat: the ring teeth at 3 o'clock, the motor behind the wheel, the side bracket "
                  "on the column covers, the screw tab out to the dash's screw (the wiper stalk and key cylinder are estimates)",
         size=(700, 700))
  iso = R.look((1.0, 0.8, 0.9), (0, 1, 0))
  crop = box(40, 320, -170, 130, -290, 40)
  R.save(os.path.join(folder, "side-assembly-3d.png"),
         [([(m ^ crop, c) for m, c in CA.parts_scene(A) if not (m ^ crop).is_empty()], iso),
          ([(m ^ crop, c) for m, c in CA.parts_scene(A, lift, MP.A_OFF) if not (m ^ crop).is_empty()], iso)],
         ["lift lever down", "lift lever up"], size=(900, 760))
  view = R.look((0.8, -1.0, 0.7), (0, 0, 1))
  panels, titles = [], []
  for n, (m, rot, how, sup) in cparts.items():
    panels.append(([(on_bed(m, rot), (.55, .7, .9))], view))
    titles.append(n)
  R.save(os.path.join(folder, "side-parts.png"), panels, titles, size=(560, 500))


def side_text(c: dict, MG) -> list:
  L = [""]
  inp = c["inputs"]
  L.append("=" * 100)
  L.append("RIGHT-SIDE MOUNT: the ring teeth at 3 o'clock on the back of the steering wheel, the motor behind the wheel there; the "
           "arm back to a side bracket zip-tied to the column covers' right-hand side, held to the dash's own screw by the screw tab")
  est = inp["estimates"]
  L.append(f"The dash's screw: {inp['screw_right_of_wheel_edge_mm']:.0f} mm right of the wheel's outer edge at 3 o'clock, "
           f"{inp['screw_below_that_mm']:.0f} mm below that point, {inp['screw_behind_rim_front_mm']:.0f} mm behind the front face of "
           f"the rim (estimates: measure yours). Covers {inp['cover_width_mm']:.0f} wide at the bracket, "
           f"{inp['cover_front_width_mm']:.0f} at their front edge, {inp['cover_height_mm']:.0f} tall; the mount "
           f"{inp['ring_above_3_oclock_deg']:.0f} degrees above 3 o'clock. Estimates used for the checks: the wiper stalk from "
           f"{est['wiper_stalk_from_to_mm'][0]} to {est['wiper_stalk_from_to_mm'][1]}, the key cylinder from "
           f"{est['key_cylinder_from_to_mm'][0]} to {est['key_cylinder_from_to_mm'][1]} (steering wheel frame, mm: right, up, "
           f"towards you from the middle of the grip), the right spoke meeting the grip "
           f"{est['right_spoke_meets_grip_deg_below_3_oclock'][0]} to {est['right_spoke_meets_grip_deg_below_3_oclock'][1]} degrees "
           "below 3 o'clock.")
  L.append("")
  L.append("PARTS (column-mount-right folder; the hinge block, motor carrier and fit test are the column mount's, the motor gear, "
           "lever bracket, lift lever, arm and setup gauge the dash mount's)")
  for p in c["parts"]:
    s_ = p["size_mm"]
    L.append(f"  {p['file']:<42} {s_[0]:5.0f} x {s_[1]:4.0f} x {s_[2]:4.0f} mm  {'fits' if p['fits_bed'] else 'TOO BIG'}  "
             f"{p['filament_if_solid_g']:5.0f} g if solid")
    L.append(f"      print {p['print']}; supports: {p['supports']}")
  r = c["ring"]
  L.append("")
  L.append(f"RING TEETH (right): {r['teeth']} teeth, the same teeth, rolling band and lead-in as the column mount's ring; the piece "
           f"spans {r['piece_spans_deg']} degrees ({r['piece_reaches_below_3_oclock_deg']} below 3 o'clock to "
           f"{r['piece_reaches_above_3_oclock_deg']} above), with {r['zip_tie_slots']} zip tie slots every {r['slots_every_deg']} degrees: "
           f"tie it wherever the spoke leaves room. Its channel's walls reach only {r['channel_walls_reach_in_mm']:.0f} mm in from "
           "the middle of the grip, so it can sit over the right spoke's junction with the grip.")
  f = c["fit"]
  L.append("")
  L.append("FIT IN THE CAR (for the screw and covers above)")
  if f["ok"]:
    L.append(f"  print {f['arm_to_print']} and {f['screw_tab_to_print']}: bolt to bolt {f['bolt_to_bolt_mm']} mm, the arm slid "
             f"{f['slide_from_middle_mm']:+.1f} mm from the middle of its slot, pointing {f['arm_to_steering_column_deg']} degrees out "
             f"from the column towards you; the screw tab's start {f['tab_start_along_the_bar_mm']} mm along the bracket's bar from "
             f"its innermost place. The bracket's back face sits {f['bracket_back_face_behind_rim_front_mm']:.0f} mm behind the front "
             f"of the rim (at the screw's depth), its middle {f['bracket_middle_behind_grip_mm']:.0f} mm behind the middle of the grip.")
  else:
    L.append("  does not fit: " + "; ".join(f["notes"]))
  for w in f.get("warnings", []):
    L.append("  check: " + w)
  if "clearances" in c:
    cl = c["clearances"]
    L.append(f"  lever up: motor gear {cl['motor_gear_to_ring_teeth_with_lever_up']} mm clear of the ring's teeth; the lift lever's "
             f"handle {cl['lift_lever_handle_to_the_spoke_sweep_zone']} mm behind where the spokes sweep; lever up, the handle "
             f"{cl['lift_lever_up_to_the_hub']} mm from the hub (25 means more than 25); the arm {cl['arm_to_the_column_covers']} mm "
             f"from the covers; the lift lever {cl['lift_lever_to_the_wiper_stalk']} mm and the hinge block and motor "
             f"{cl['hinge_block_and_motor_to_the_wiper_stalk']} mm below the wiper stalk; the arm and bracket "
             f"{cl['arm_and_bracket_to_the_key_cylinder']} mm behind the key cylinder; the parts reach "
             f"{cl['parts_reach_back_to_mm_behind_grip']:.0f} mm back from the middle of the grip.")
  touching = [k for k, v in c["touching_checks_mm3"].items() if ("should touch" not in k and v > 1e-3)]
  L.append(f"  {len(c['touching_checks_mm3'])} clearance checks, {len(touching)} touching")
  gr = c["screw_positions"]
  L.append("")
  L.append("WHICH SCREW POSITIONS WORK (rows: the screw right of the wheel's edge, mm; columns: behind the front of the rim, mm). "
           "Each cell names the arm and screw tab that reach with both joints in range and nothing touching (the dash estimates "
           "left out). A screw less than 250 mm behind the rim's front puts the bracket, which sits level with it, so close to "
           "the hinge block that the arm's fork meets it; past 300 the column covers must reach further back than the dash "
           "below the column is estimated to be.")
  L.append("        " + "".join(f"{x:>16}" for x in gr["screw_behind_mm"]))
  for h, row in zip(gr["screw_right_mm"], gr["cells"]):
    L.append(f"  {h:5}  " + "".join(f"{x:>16}" for x in row))
  cw = c["cover_widths"]
  L.append("")
  L.append("THE COVERS' WIDTH AT THEIR FRONT: the lift lever, flipped up, swings in beside the covers about 85 mm behind the "
           "middle of the grip. How far the handle then clears them, for covers this wide at their front edge:")
  L.append("        " + "".join(f"{x:>10}" for x in cw["cover_front_width_mm"]))
  L.append("        " + "".join(f"{str(x):>10}" for x in cw["lever_up_clear_by_mm"]))
  L.append("  (wider: turn the mount up with --ring-at, or measure the covers 85 mm behind the rim and use that width)")
  L.append("")
  L.append("MARGINS (the right-side mount's own; the shared parts' margins are above)")
  L += MG.text_lines(c["margins"])
  L.append("")
  L.append("BOLTS, SCREW AND TIES")
  for b in c["fasteners"]:
    if b["length"]:
      L.append(f"  {b['bolt']:20s} {b['use']}: through {b['through_mm']} mm, then a {b['nut_mm']} mm lock nut: {b['past_the_nut_mm']} mm "
               f"to spare{'' if b['ok'] else '  WRONG LENGTH'}")
    else:
      L.append(f"  {b['bolt']:20s} {b['use']}")
  return L


def column_pictures(A, CA, MP, cparts, folder, on_bed):
  import render as R
  from cadlib import box
  lift = MP.cam_lift(MP.A_OFF)
  side = R.look((1, 0, 0), (0, 1, 0))
  R.save(os.path.join(folder, "column-assembly-side.png"),
         [(CA.parts_scene(A), side), (CA.parts_scene(A, lift, MP.A_OFF), side), (CA.parts_scene(A), R.look((0, 0, 1), (0, 1, 0)))],
         ["lift lever down: motor gear in the ring", "lift lever up: motor gear lifted off", "from the driver's seat"],
         suptitle="Column mount, seen from the driver's right (the driver is on the left; the steering column covers at the top)",
         size=(700, 700))
  iso = R.look((1.0, -0.8, 0.9), (0, 1, 0))
  crop = box(-200, 200, -260, -40, -260, 40)
  R.save(os.path.join(folder, "column-assembly-3d.png"),
         [([(m ^ crop, c) for m, c in CA.parts_scene(A) if not (m ^ crop).is_empty()], iso),
          ([(m ^ crop, c) for m, c in CA.parts_scene(A, lift, MP.A_OFF) if not (m ^ crop).is_empty()], iso)],
         ["lift lever down", "lift lever up"], size=(900, 760))
  view = R.look((0.8, -1.0, 0.7), (0, 0, 1))
  panels, titles = [], []
  for n, (m, rot, how, sup) in cparts.items():
    panels.append(([(on_bed(m, rot), (.55, .7, .9))], view))
    titles.append(n)
  R.save(os.path.join(folder, "column-parts.png"), panels, titles, size=(560, 500))


def column_text(c: dict, MG) -> list:
  L = [""]
  inp = c["inputs"]
  L.append("=" * 100)
  L.append("COLUMN MOUNT: the motor under the steering wheel, behind it, its gear inside a ring of teeth; the arm up to a clamp "
           "round the steering column covers")
  est = inp["estimates"]
  L.append(f"Covers {inp['cover_width_mm']:.0f} wide, {inp['cover_height_mm']:.0f} tall; the clamp's middle "
           f"{inp['clamp_middle_behind_grip_mm']:.0f} mm behind the middle of the part of the wheel you hold; the motor's face "
           f"{inp['motor_face_behind_grip_mm']:.0f} mm behind it. Estimates used for the checks (measure yours): hub radius "
           f"{est['hub_radius_mm']:.0f}, hub reaching {est['hub_back_mm']:.0f} back, the lower spokes' back face "
           f"{est['spokes_back_at_lever_mm']:.0f} back where the lift lever is, the covers' front edge "
           f"{est['covers_front_edge_behind_grip_mm']:.0f} back, the dash below the column "
           f"{est['dash_below_column_behind_grip_mm']:.0f} back, {est['open_arc_between_lower_spokes_deg']:.0f} degrees open "
           "between the lower spokes.")
  L.append("")
  L.append("PARTS (column-mount folder; the motor gear, lever bracket, lift lever, arm and setup gauge are shared)")
  for p in c["parts"]:
    s_ = p["size_mm"]
    L.append(f"  {p['file']:<42} {s_[0]:5.0f} x {s_[1]:4.0f} x {s_[2]:4.0f} mm  {'fits' if p['fits_bed'] else 'TOO BIG'}  "
             f"{p['filament_if_solid_g']:5.0f} g if solid")
    L.append(f"      print {p['print']}; supports: {p['supports']}")
  g = c["gears"]
  L.append("")
  L.append(f"RING TEETH: {g['teeth']} teeth facing the hub, the motor gear inside at {g['centre_distance_mm']} mm from the column "
           f"(its roller rides a band of radius {g['rolling_band_radius_mm']}). They cover {g['steering_wheel_turn_with_teeth_deg']} "
           f"degrees of steering wheel turn; the motor gear follows over {g['steering_wheel_turn_tracked_deg']}; the piece spans "
           f"{g['piece_spans_deg']} degrees, with {g['zip_tie_slots']} zip tie slots every {g['slots_every_deg']} degrees (tie it "
           f"wherever the spokes leave room). Most overlap anywhere in the range: {g['most_overlap_mm2']} mm2 (should be 0). Free "
           f"play at the steering wheel: {g['free_play_steering_wheel_deg'][0]} to {g['free_play_steering_wheel_deg'][1]} degrees.")
  w = c["window"]
  L.append(f"  Between the wheel's two lower spokes ({w['window_between_spokes_deg']:.0f} degrees open, an estimate from photos) "
           f"the piece leaves {w['room_each_side_deg']} degrees ({w['room_each_side_mm_along_the_grip']:.0f} mm along the grip) "
           "each side" + ("." if w["ok"] else ": NOT ENOUGH."))
  f = c["fit"]
  L.append("")
  L.append("FIT IN THE CAR (for the covers and clamp position above)")
  if f["ok"]:
    L.append(f"  print {f['arm_to_print']}: bolt to bolt {f['bolt_to_bolt_mm']} mm, the arm slid {f['slide_from_middle_mm']:+.1f} mm "
             f"from the middle of its slot, pointing {f['arm_to_steering_column_deg']} degrees below the column towards you. The "
             f"lower saddle's V sits {f['saddle_middle_below_column_axis_mm']} mm below the column's axis.")
  else:
    L.append("  does not fit: " + "; ".join(f["notes"]))
  if "clearances" in c:
    cl = c["clearances"]
    L.append(f"  lever up: motor gear {cl['motor_gear_to_ring_teeth_with_lever_up']} mm clear of the ring's teeth; the lift lever's "
             f"handle {cl['lift_lever_handle_to_the_spoke_sweep_zone']} mm behind where the spokes sweep; lever up, the handle "
             f"{cl['lift_lever_up_to_the_hub']} mm from the hub (25 means more than 25); the arm {cl['arm_to_the_column_covers']} mm "
             f"below the covers; the parts reach {cl['parts_reach_back_to_mm_behind_grip']:.0f} mm back from the middle of the grip "
             "(the dash below the column must be further).")
  touching = [k for k, v in c["touching_checks_mm3"].items() if ("should touch" not in k and v > 1e-3)]
  L.append(f"  {len(c['touching_checks_mm3'])} clearance checks, {len(touching)} touching")
  gr = c["clamp_positions"]
  L.append("")
  L.append("WHICH CLAMP POSITIONS WORK (rows: the covers' height; columns: the clamp's middle, mm behind the middle of the "
           "grip). Each arm named reaches with both joints in range and nothing touching; in brackets, how far back the parts "
           "then reach (mm behind the middle of the grip): the dash below the column must be further than that. A row of "
           "no: the lift lever, flipped up, meets covers that tall (if their front edge is where estimated).")
  L.append("        " + "".join(f"{x:>14}" for x in gr["clamp_behind_mm"]))
  for h, row in zip(gr["cover_height_mm"], gr["cells"]):
    L.append(f"  {h:5}  " + "".join(f"{x:>14}" for x in row))
  L.append("")
  L.append("MARGINS (the column mount's own; the shared parts' margins are above)")
  L += MG.text_lines(c["margins"])
  L.append("")
  L.append("RODS")
  for b in c["fasteners"]:
    L.append(f"  {b['bolt']:28s} {b['use']}: needs {b['needs_mm'][0]} to {b['needs_mm'][1]} mm over the covers' height "
             f"range; {b['used_for_your_cover_mm']} mm for yours{'' if b['ok'] else '  TOO SHORT'}")
  return L


def support_area(m, max_angle: float = 45.0):
  """Area (mm^2) of downward faces leaning more than max_angle from upright that are not on the bed (faces at
  exactly 45 degrees print fine and are not counted), and the bed area."""
  mesh = m.to_mesh()
  v = np.asarray(mesh.vert_properties)[:, :3]
  tri = np.asarray(mesh.tri_verts)
  a, b, c = v[tri[:, 0]], v[tri[:, 1]], v[tri[:, 2]]
  n = np.cross(b - a, c - a)
  area = np.linalg.norm(n, axis=1) / 2
  nz = n[:, 2] / np.maximum(np.linalg.norm(n, axis=1), 1e-12)
  zmin = np.minimum(np.minimum(a[:, 2], b[:, 2]), c[:, 2]) - v[:, 2].min()
  steep = (nz < -math.cos(math.radians(max_angle)) - 0.01) & (zmin > 0.3)
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
         "hinge": (.45, .75, .45), "bracket": (.6, .45, .8), "lever": (.85, .3, .3), "switch": (.9, .85, .2),
         "arm": (.6, .5, .4), "clamp": (.5, .7, .7), "hood": (.85, .85, .75)}

  def scene(lift_deg=0.0, alpha=0.0, wheel=0.0, crop=None, cut_x=None):
    items = [(A.teeth(wheel), col["teeth"]), (A.wheel_grip(), col["grip"]), (A.gear(lift_deg), col["gear"]),
             (A.carrier(lift_deg), col["carrier"]), (A.motor(lift_deg), col["motor"]), (A.hinge_block(), col["hinge"]),
             (A.bracket(lift_deg), col["bracket"]), (A.lever(alpha, lift_deg), col["lever"]),
             (A.switch(lift_deg), col["switch"]), (A.arm(), col["arm"]), (A.clamp(), col["clamp"]), (A.hood(), col["hood"])]
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
         ["lever down (cut through the middle)", "lever up: its rounded end presses on the hinge block, lifting the motor gear"],
         size=(900, 760))
  # every part as it sits on the bed
  names = ["steering-wheel-teeth-29-left-half", "steering-wheel-teeth-15-one-piece", "motor-gear", "motor-carrier",
           "hinge-block", "lever-bracket", "lift-lever", "dash-clamp", "clamp-pad", "setup-gauge", "fit-test-steering-wheel",
           "fit-test-teeth"]
  view = R.look((0.8, -1.0, 0.7), (0, 0, 1))
  panels, titles = [], []
  for n in names:
    m, rot, how, sup = parts[n]
    panels.append(([(on_bed(m, rot), (.55, .7, .9))], view))
    titles.append(n.split("/")[-1])
  for i in range(0, len(panels), 4):
    R.save(os.path.join(folder, f"parts-{i // 4 + 1}.png"), panels[i:i + 4], titles[i:i + 4], size=(560, 500))


def text_report(r: dict) -> str:
  import margins as MG  # already imported by main(), after the measurements were set
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
  L.append(f"GEARS: ratio {g['gear_ratio']} (motor turns {g['gear_ratio']:.2f} times per steering wheel turn).")
  for reach, gs in g["sets"].items():
    L.append(f"  {reach} teeth: {gs['teeth_on_steering_wheel']} teeth cover {gs['steering_wheel_turn_with_teeth_deg']} degrees "
             f"of steering wheel turn; the motor gear follows over {gs['steering_wheel_turn_tracked_deg']}; the piece spans "
             f"{gs['piece_spans_deg']} degrees, zip ties at {', '.join(str(a) for a in gs['zip_ties_deg'])} degrees each side. "
             f"Most overlap anywhere in the range: {gs['most_overlap_mm2']} mm2 (should be 0). Free play at the steering "
             f"wheel: {gs['free_play_steering_wheel_deg'][0]} to {gs['free_play_steering_wheel_deg'][1]} degrees.")
  lv = r["lift_lever"]
  sp = r["spring"]
  ck = lv["click"]
  L.append("")
  L.append(f"LIFT LEVER: turns {lv['turns_deg']:.0f} degrees from down to up. The power switch lets go within "
           f"{lv['switch_releases_by_deg']} degrees; the motor gear starts to lift at {lv['starts_lifting_at_deg']:.0f} degrees "
           f"and is out of mesh by {lv['motor_gear_out_of_mesh_at_deg']:.0f} degrees. "
           f"Up, the carrier is turned {lv['carrier_lift_up_deg']} degrees (most {lv['most_lift_deg']} on the way). "
           f"Pushes at the end of the handle: up to {lv['most_push_at_handle_end_N']} N to lift against the spring "
           f"({lv['most_push_with_rubbing_N']} N counting rubbing at the rounded end, an estimate with dry printed parts), "
           f"{lv['push_to_bring_it_back_down_N']} N to start it back down "
           f"({lv['push_to_bring_it_back_down_with_rubbing_N']} N with rubbing), and {lv['push_to_go_past_up_N']} N or more to "
           f"push it past up. Lever down, its rounded end is {lv['drop_gap_mm']} mm above the hinge block.")
  L.append(f"CLICK (estimates for PETG): the tab bends {ck['bend_mm']} mm ({ck['tab_strain_percent']}% stretch at its root) "
           f"with {ck['tab_force_N']} N; about {ck['to_click_at_handle_end_N']} N at the end of the handle to click it down "
           f"and {ck['to_unclick_at_handle_end_N']} N to unclick it.")
  L.append(f"SPRING: {sp['part']}. {sp['length_gear_on_teeth_mm']} mm long and {sp['force_gear_on_teeth_N']} N with the motor gear "
           f"on the teeth; {sp['length_lever_up_mm']} mm and {sp['force_lever_up_N']} N with the lever up (its most is "
           f"{sp['most_load_N']} N at {sp['fully_squashed_mm']} mm). With the motor gear on the teeth it presses the roller "
           f"onto the rolling band with {sp['presses_roller_on_rolling_band_N']} N and holds the teeth in mesh against up to "
           f"{sp['holds_teeth_in_mesh_up_to_N']} N pushing them apart (by calculation, leaving out the motor's own weight, "
           f"which adds to both). MARGINS below compares that with the push of the most torque, rubbing between the teeth "
           f"included.")
  pt = r["past_last_tooth"]
  L.append(f"PAST THE LAST TOOTH: the roller stays on the rolling band for {pt['roller_on_band_more_deg']} more degrees of "
           f"steering wheel turn each way ({pt['flat_deg']} flat, then {pt['on_slope_deg']} down its slope until the carrier "
           f"stops dropping). Its grip there can still push the steering wheel: about {pt['push_there_Nm_estimate']} Nm at "
           f"most (an estimate, {pt['rubbing_estimate']} rubbing between printed parts), against "
           f"{sp['most_torque_at_steering_wheel_Nm']} Nm through the teeth. " + "; ".join(
             f"{reach} teeth: full push to {s['full_push_to_deg']} degrees each way, weak push to {s['weak_push_to_deg']}"
             for reach, s in pt["sets"].items()) + ".")
  L.append("")
  L.append(f"MARGINS: for each way it can fail, the worst load, what it takes, and the factor between them. Aim {MG.AIM}, "
           f"nothing under {MG.FLOOR} (NASA-STD-5001B uses 1.4 for tested hardware, the FAA 1.5). For heat, the factor is on "
           "how far the sun heats a part above the outside air (38 C).")
  L += MG.text_lines(r["margins"])
  L.append("")
  L.append("BOLTS AND SCREWS")
  for b in r["fasteners"]:
    if "past_the_nut_mm" in b:
      what = f"through {b['through_mm']} mm, then a {b['nut_mm']} mm lock nut: {b['past_the_nut_mm']} mm to spare"
    elif "thread_in_mm" in b:
      what = f"through {b['through_mm']} mm, then {b['thread_in_mm']} mm of thread into a hole {b['hole_depth_mm']} mm deep"
    elif "past_the_wall_mm" in b:
      what = f"through {b['through_mm']} mm, its tip {b['past_the_wall_mm']} mm past the rear wall"
    else:
      what = f"needs {b['needs_mm'][0]} to {b['needs_mm'][1]} mm"
    L.append(f"  {b['bolt']:20s} {b['use']}: {what}{'' if b['ok'] else '  WRONG LENGTH'}")
  f = r["fit"]
  L.append("")
  L.append("FIT IN THE CAR (for the dash clamp position above" + (
    f", steering column at {inp['your_column_angle_deg']} degrees)" if inp.get("your_column_angle_deg") is not None
    else ", at every tilt setting of the steering wheel)"))
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
  tl = gr["tilt_deg"]
  L.append("WHICH DASH CLAMP POSITIONS WORK (rows: mm up from the motor gear's centre; columns: mm forward). Each arm "
           f"named fits at every tilt setting of the steering wheel: the steering column at {tl[0]} to {tl[2]} degrees "
           f"from level, {tl[1]} in the middle (measured by NHTSA, tests 6229 and 7078).")
  L.append("        " + "".join(f"{x:>12}" for x in gr["forward_mm"]))
  for u, row in zip(gr["up_mm"], gr["cells"]):
    L.append(f"  {u:5}  " + "".join(f"{(c if not c.startswith('no') else 'no'):>12}" for c in row))
  if any(c.endswith("*") for row in gr["cells"] for c in row):
    L.append("  * fits with the tilt in the middle of its range, but not at both ends: check yours with this script.")
  if f["ok"]:
    L.append(("  Your position at your column angle: " if inp.get("your_column_angle_deg") is not None
              else "  Your position across the tilt range: ") + "; ".join(
      f"at {t_['tilt_deg']} degrees bolt to bolt {t_['bolt_to_bolt_mm']} mm, slid {t_['slide_from_middle_mm']:+.1f} mm"
      for t_ in r["tilt_range"]) + ".")
  if "column_mount" in r:
    L += column_text(r["column_mount"], MG)
  if "side_mount" in r:
    L += side_text(r["side_mount"], MG)
  if "back_mount" in r:
    L += back_text(r["back_mount"], MG)
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
