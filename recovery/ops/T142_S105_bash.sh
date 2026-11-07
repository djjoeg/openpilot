python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
old = '''  wall = box(PL_MAIN_X[1] - 8.0, PL_MAIN_X[1], y0, fy1, fz0 - 30.0, fz1)
  shelf = box(PL_MAIN_X[1] - 8.0, fx1, y0, y0 + 6.0, fz0 - 22.0, fz1) if fy0 <= y0 + 6.0 else box(PL_MAIN_X[1] - 8.0, fx1, fy0, fy0 + 6.0, fz0 - 22.0, fz1)
  gusset = prism_x([(fy0 + 3.0, fz0), (fy1 - 2.0, fz0), (fy0 + 3.0, fz0 - 22.0)], fx1 - 6.0, fx1)
  low = min(y0, fy0)
  skirt = box(PL_MAIN_X[1] - 8.0, fx1, low, y0 + 6.0, fz0 - 22.0, fz1)
  part = union([part, flange, wall, shelf, gusset, skirt])'''
new = '''  # behind the flange's right part the springs' front bolt swings past as the motor pops off: the shelf stops short
  wall = box(PL_MAIN_X[1] - 8.0, PL_MAIN_X[1], y0, fy1, fz0 - 30.0, fz1)
  low = min(y0, fy0)
  shelf = box(PL_MAIN_X[1] - 8.0, SHELF_X1, low, y0 + 6.0, fz0 - 16.0, fz1)
  gusset = prism_x([(y0 + 5.0, fz0), (fy1 - 4.0, fz0), (y0 + 5.0, fz0 - 26.0)], PL_MAIN_X[1] - 8.0, PL_MAIN_X[1])
  part = union([part, flange, wall, shelf, gusset])'''
assert s.count(old) == 1
s = s.replace(old, new)
old = "FLANGE_PAD = 9.0              # plate's flange beyond its slots' ends and the bolts' outermost positions"
assert s.count(old) == 1
s = s.replace(old, old + "\nSHELF_X1 = 88.0               # the shelf under the flange, out to here (the springs' front bolt swings past beyond)")
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 3000 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2/run_u.py --quick 2>&1 | grep -v "^   {\|flange fit\|switch:" | tail -20