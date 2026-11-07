python3 - <<'EOF'
p = "accord_lka_parts.py"
s = open(p).read()
old = """  ap.add_argument("--arm", type=float, action="append", default=[], help="also make an arm of exactly this length (mm, bolt to bolt)")
"""
new = """  ap.add_argument("--column-angle", type=float, default=None,
                  help="your steering column's angle from level in degrees, if you measured it (a phone's level app laid on "
                       "the steering wheel's face reads 90 minus this); otherwise the arm must fit the whole tilt range")
  ap.add_argument("--arm", type=float, action="append", default=[], help="also make an arm of exactly this length (mm, bolt to bolt)")
"""
assert old in s; s = s.replace(old, new)
old = """  python3 accord_lka_parts.py --clamp-up 110 --clamp-forward 160
"""
new = """  python3 accord_lka_parts.py --clamp-up 110 --clamp-forward 160
  python3 accord_lka_parts.py --clamp-up 60 --clamp-forward 175 --column-angle 20
"""
assert old in s; s = s.replace(old, new)
old = """  arm_len, why_not = arm_for(args.clamp_up, args.clamp_forward)
  fit = AS.solve(t, args.clamp_up, args.clamp_forward)
  if arm_len:
    fit = dataclasses.replace(fit, ok=True, arm_len=arm_len, slide=fit.reach - arm_len, notes=[])
  else:
    fit = dataclasses.replace(fit, ok=False, arm_len=0.0, slide=0.0, notes=fit.notes or [why_not])
"""
new = """  your_tilt = args.column_angle if args.column_angle is not None else P.COLUMN_TILT
  arm_len, why_not = arm_for(args.clamp_up, args.clamp_forward, (args.column_angle,) if args.column_angle is not None else tilts)
  fit = AS.solve(t, args.clamp_up, args.clamp_forward, your_tilt)
  if arm_len:
    fit = dataclasses.replace(fit, ok=True, arm_len=arm_len, slide=fit.reach - arm_len, notes=[])
  else:
    fit = dataclasses.replace(fit, ok=False, arm_len=0.0, slide=0.0, notes=fit.notes or [why_not])
"""
assert old in s; s = s.replace(old, new)
old = """    A = AS.Assembly(t, fit, assy)
    checks = AS.check_all(A)
"""
new = """    A = AS.Assembly(t, fit, assy, your_tilt)
    checks = AS.check_all(A)
"""
assert old in s; s = s.replace(old, new)
old = """  report["tilt_range"] = [{"tilt_deg": tl, "bolt_to_bolt_mm": round(AS.solve(t, args.clamp_up, args.clamp_forward, tl).reach, 1),
                           "slide_from_middle_mm": round(AS.solve(t, args.clamp_up, args.clamp_forward, tl).reach - fit.arm_len, 1)
                           if fit.arm_len else None} for tl in tilts]
"""
new = """  report["tilt_range"] = [{"tilt_deg": tl, "bolt_to_bolt_mm": round(AS.solve(t, args.clamp_up, args.clamp_forward, tl).reach, 1),
                           "slide_from_middle_mm": round(AS.solve(t, args.clamp_up, args.clamp_forward, tl).reach - fit.arm_len, 1)
                           if fit.arm_len else None}
                          for tl in ((args.column_angle,) if args.column_angle is not None else tilts)]
"""
assert old in s; s = s.replace(old, new)
old = """                       "column_tilt_deg": P.COLUMN_TILT, "print_bed_mm": list(args.bed)}}
"""
new = """                       "column_tilt_deg": P.COLUMN_TILT, "your_column_angle_deg": args.column_angle,
                       "print_bed_mm": list(args.bed)}}
"""
assert old in s; s = s.replace(old, new)
old = """  if f["ok"]:
    L.append("  Your position across the tilt range: " + "; ".join("""
new = """  if f["ok"]:
    L.append(("  Your position at your column angle: " if inp.get("your_column_angle_deg") is not None
              else "  Your position across the tilt range: ") + "; ".join("""
assert old in s; s = s.replace(old, new)
old = """  L.append("FIT IN THE CAR (for the dash clamp position above)")
"""
new = """  L.append("FIT IN THE CAR (for the dash clamp position above" + (
    f", steering column at {inp['your_column_angle_deg']} degrees)" if inp.get("your_column_angle_deg") is not None
    else ", at every tilt setting of the steering wheel)"))
"""
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)
print("ok")
EOF
cd /home/claude/deliver/hardware/cad && OUT=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cad6 && rm -rf $OUT && mkdir -p $OUT && PYTHONPATH=/home/claude/pylib timeout 2400 python3 accord_lka_parts.py --clamp-up 60 --clamp-forward 175 --column-angle 20 --no-pictures --out $OUT/stl --report $OUT/report > $OUT/run.log 2>&1; echo "exit $?"; sed -n '/FIT IN THE CAR/,/clearance checks/p;/Your position/p;/PROBLEMS/,$p' $OUT/run.log