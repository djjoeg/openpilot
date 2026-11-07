python3 - <<'EOF'
p = "accord_lka_parts.py"
s = open(p).read()
s = s.replace("""             f"{cl['parts_reach_out_from_column_mm']:.0f} mm out from the column (the grip's outer edge is "
             f"{c['_wheel_r'] if '_wheel_r' in c else 184} mm); the column plate's corner""",
"""             f"{cl['parts_reach_out_from_column_mm']:.0f} mm out from the column (the grip's outer edge is "
             f"{inp['wheel_outer_radius_mm']:.1f} mm); the column plate's corner""")
s = s.replace("""  rep = {"inputs": {"cover_bottom_below_column_axis_mm": args.cover_bottom, "right_spoke_meets_grip_deg": list(P.RIGHT_SPOKE_DEG),""",
"""  rep = {"inputs": {"cover_bottom_below_column_axis_mm": args.cover_bottom, "right_spoke_meets_grip_deg": list(P.RIGHT_SPOKE_DEG),
                    "wheel_outer_radius_mm": args.wheel_od / 2,""")
open(p, "w").write(s)
p = "faceassembly.py"
s = open(p).read()
old = """  return {"motor_gear_off_the_teeth_with_lever_up": gap(A.gear(lift), A.teeth(), (0.0, 0.0, -1.0)),"""
new = """  return {"motor_gear_off_the_teeth_with_lever_up": gap(A.gear(lift), A.teeth(), (0.0, 0.0, 1.0)),"""
assert old in s
s = s.replace(old, new)
open(p, "w").write(s)
EOF
grep -n '"seconds"' ../report/parts_report.json; tail -3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/rebuild_sa.log; cat /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/rebuild3.time 2>/dev/null