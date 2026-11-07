python3 - <<'EOF'
p = "accord_lka_parts.py"
s = open(p).read()

old = '''  # ----- fit in the car -----
'''
new = '''  # ----- bolt and screw lengths -----
  report["fasteners"] = MP.fastener_table()
  for row in report["fasteners"]:
    if not row["ok"]:
      problems.append(f"{row['bolt']} ({row['use']}) is the wrong length")

  # ----- fit in the car -----
'''
assert s.count(old) == 1
s = s.replace(old, new)

old_txt = '''  f = r["fit"]
  L.append("")
  L.append("FIT IN THE CAR'''
new_txt = '''  L.append("")
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
  L.append("FIT IN THE CAR'''
assert s.count(old_txt) == 1
s = s.replace(old_txt, new_txt)
open(p, "w").write(s)
EOF
grep -n "clearance checks\|touching" accord_lka_parts.py | head