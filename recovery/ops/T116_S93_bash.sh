cat >> faceassembly.py <<'EOF'


def parts_scene(A: FaceAssembly, lift_deg=0.0, alpha=0.0, wheel=0.0, covers_back: float = -240.0):
  """(manifold, colour) pairs for the pictures."""
  col = {"teeth": (.72, .72, .72), "grip": (.3, .3, .3), "gear": (.95, .6, .25), "carrier": (.35, .55, .85),
         "motor": (.25, .25, .25), "hinge": (.45, .75, .45), "bracket": (.6, .45, .8), "lever": (.85, .3, .3),
         "switch": (.9, .85, .2), "arm": (.6, .5, .4), "plate": (.5, .7, .7), "covers": (.85, .85, .75), "hub": (.4, .4, .4),
         "car": (.8, .75, .7)}
  from cadlib import box
  covers = A.covers() ^ box(-200, 200, -200, 200, covers_back, 50)
  items = [(A.teeth(wheel), col["teeth"]), (A.wheel_grip(), col["grip"]), (A.gear(lift_deg, wheel), col["gear"]),
           (A.carrier(lift_deg), col["carrier"]), (A.motor(lift_deg), col["motor"]), (A.hinge_block(), col["hinge"]),
           (A.bracket(lift_deg), col["bracket"]), (A.lever(alpha, lift_deg), col["lever"]), (A.switch(lift_deg), col["switch"]),
           (A.arm(), col["arm"]), (A.plate(), col["plate"]), (covers, col["covers"]), (A.hub(), col["hub"]),
           (A.stalk(), col["car"]), (A.key(), col["car"])]
  return [(m, c) for m, c in items if not m.is_empty()]


def fastener_rows() -> list:
  """The back-teeth mount's own bolts, screws, ties and dowels."""
  rows = []
  stack = 2 * FP.J_EAR_T + FP.ARM_T_F + 2 * MP.GAP
  spare = 40.0 - stack - 2 * MP.M5_WASHER_T - MP.M5_NYLOC_T
  rows.append({"bolt": "M5 x 40 (4)", "use": "the arm's two joints: both ears and the arm, a washer each side, lock nut (each "
               "joint's bolt and its locking bolt)", "length": 40.0, "through_mm": round(stack + 2 * MP.M5_WASHER_T, 1),
               "nut_mm": MP.M5_NYLOC_T, "past_the_nut_mm": round(spare, 1), "ok": spare >= 1.5})
  rows.append({"bolt": "the lower column cover's own screws, 10 mm longer (same thread), and a washer each",
               "use": f"column plate to the cover's underside: through the plate ({FP.PL_T:.0f} mm) and the rubber strips "
                      f"({FP.PL_PAD_T:.0f} mm), wherever the screws fall in its two slots", "length": 0.0, "through_mm": FP.PL_T + FP.PL_PAD_T,
               "nut_mm": 0.0, "past_the_nut_mm": 0.0, "ok": True})
  rows.append({"bolt": "zip ties, 4.8 mm wide, 200 mm or longer (6 or more)", "use": "back teeth round the grip, through the slots",
               "length": 0.0, "through_mm": 0.0, "nut_mm": 0.0, "past_the_nut_mm": 0.0, "ok": True})
  rows.append({"bolt": "1.75 mm filament, four 16 mm pieces", "use": "dowels across the joint of the two back teeth pieces, glued in",
               "length": 0.0, "through_mm": 0.0, "nut_mm": 0.0, "past_the_nut_mm": 0.0, "ok": True})
  rows.append({"bolt": "M5 washer, 10 mm across (1)", "use": "under the spring, from the start on this mount", "length": 0.0,
               "through_mm": 0.0, "nut_mm": 0.0, "past_the_nut_mm": 0.0, "ok": True})
  return rows
EOF
python3 - <<'EOF'
p = "/home/claude/deliver/hardware/cad/accord_lka_parts.py"
s = open(p).read()
# docstring
old = """  The hinge block (column), motor carrier (column) and the fit test are the column mount's.

Run it with no options"""
new = """  The hinge block (column), motor carrier (column) and the fit test are the column mount's.

  back-teeth mount (hardware/stl/back-teeth-mount): teeth on the back of a channel round the grip from 1 to 5
  o'clock, facing the dash; the motor behind the wheel at 3 o'clock, just outside the grip, its shaft pointing at the
  column; the arm down to a plate under the steering column's lower cover, on the cover's own screws (faceparts.py):
  back teeth            - the channel with the teeth (a face gear, 166 teeth on a full circle) and the rolling band on
                          its back; two pieces glued end to end, or one piece for 330 mm beds
  back motor gear       - 16 teeth (166 / 16 = 10.375, the other mounts' 197 / 19 = 10.368)
  back motor carrier    - the carrier with its finger guard open wider and the plate's lower edge cut back
  back hinge block      - the hinge block with the arm's joint underneath instead of on top
  back lift lever       - the lift lever with a paddle under its handle's end
  back arms             - three lengths, each slides +-15 mm
  column plate          - under the lower column cover, with the arm's other joint
  fit tests             - a short piece of the back teeth, and the piece over the right spoke's junction
  The lever bracket, spring (on an M5 washer) and setup gauge are the same parts.

Run it with no options"""
assert old in s
s = s.replace(old, new)
old = """  python3 accord_lka_parts.py --screw-right 50 --screw-down 70 --screw-behind 270 --cover-front-width 102
"""
new = """  python3 accord_lka_parts.py --screw-right 50 --screw-down 70 --screw-behind 270 --cover-front-width 102
  python3 accord_lka_parts.py --cover-bottom 55 --spoke-from -50 --spoke-to -16
"""
assert old in s
s = s.replace(old, new)
# args
old = """  ap.add_argument("--bed", type=float, nargs=3, default=list(P.BED), metavar=("X", "Y", "Z"), help="print bed size (mm)")"""
new = """  ap.add_argument("--cover-bottom", type=float, default=-P.COVER_BOTTOM,
                  help="back-teeth mount: the lower column cover's underside, mm below the column's axis where the plate sits")
  ap.add_argument("--spoke-from", type=float, default=P.RIGHT_SPOKE_DEG[0],
                  help="back-teeth mount: the right spoke meets the grip from this angle (degrees from 3 o'clock, + up)")
  ap.add_argument("--spoke-to", type=float, default=P.RIGHT_SPOKE_DEG[1], help="back-teeth mount: ... to this angle")
  ap.add_argument("--bed", type=float, nargs=3, default=list(P.BED), metavar=("X", "Y", "Z"), help="print bed size (mm)")"""
assert old in s
s = s.replace(old, new)
old = """  report["side_mount"] = side_mount(args, base, arms, problems, on_bed, write_stl, part_rows, bed)
"""
new = """  report["side_mount"] = side_mount(args, base, arms, problems, on_bed, write_stl, part_rows, bed)
  report["back_mount"] = back_mount(args, base, problems, on_bed, write_stl, part_rows, bed)
"""
assert old in s
s = s.replace(old, new)
old = """  if "side_mount" in r:
    L += side_text(r["side_mount"], MG)
"""
new = """  if "side_mount" in r:
    L += side_text(r["side_mount"], MG)
  if "back_mount" in r:
    L += back_text(r["back_mount"], MG)
"""
assert old in s
s = s.replace(old, new)
# the right-side mount's spoke estimate: the same one as the back mount's now
old = """                                  "right_spoke_meets_grip_deg_below_3_oclock": [2, 25]}}}"""
new = """                                  "right_spoke_meets_grip_deg_below_3_oclock": [-P.RIGHT_SPOKE_DEG[1], -P.RIGHT_SPOKE_DEG[0]]}}}"""
assert old in s
s = s.replace(old, new)
open(p, "w").write(s)
print("ok")
EOF