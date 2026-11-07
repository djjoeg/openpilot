python3 - << 'EOF'
p = "mountparts.py"
s = open(p).read()
a = """def lever_outline() -> CrossSection:
  cam = CrossSection([[(0.0, 0.0)] + cam_points()])"""
b = """def ccw(points) -> CrossSection:
  \"\"\"A filled outline whichever way round the points go.\"\"\"
  cs = CrossSection([list(points)])
  return cs if cs.area() > 1e-9 else CrossSection([list(points)[::-1]])


def lever_outline() -> CrossSection:
  cam = ccw([(0.0, 0.0)] + cam_points())"""
assert a in s; s = s.replace(a, b)
# the stop bar outline may have the same problem
a = """  return CrossSection([[(float(q[0]), float(q[1])) for q in pts]])"""
b = """  return ccw([(float(q[0]), float(q[1])) for q in pts])"""
assert a in s; s = s.replace(a, b)
open(p, "w").write(s)
EOF
grep -n "CrossSection(\[" mountparts.py cadlib.py wheelparts.py gears.py; PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0,'.')
import mountparts as MP
print('lever area', MP.lever_outline().area(), 'stop bar area', MP.stop_bar().area(), 'cam area', MP.ccw([(0,0)]+MP.cam_points()).area())
"; PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/lever2d.py > /dev/null; PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py 2>&1 | grep -v " 0.000  "