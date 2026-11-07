python3 - <<'EOF'
p = "mountparts.py"
s = open(p).read()
old = '''def spring_body() -> Manifold:'''
new = '''def hinge_bolt(washers: bool = True) -> Manifold:
  """The M5 hinge bolt's head and lock nut on the hinge block's knuckles (with a washer under each, if used)."""
  hy, hz = HINGE
  k = BLOCK_KNUCKLE[1]
  w = M5_WASHER_T if washers else 0.0
  return union([cyl_x(4.25, -k - w - 5.0, -k - w, y=hy, z=hz, segments=32),
                cyl_x(5.0, -k - w, -k, y=hy, z=hz, segments=32) if w else cyl_x(2.5, -k - 0.01, -k, y=hy, z=hz),
                cyl_x(5.0, k, k + w, y=hy, z=hz, segments=32) if w else cyl_x(2.5, k, k + 0.01, y=hy, z=hz),
                cyl_x(8.0 / 2 / math.cos(math.pi / 6), k + w, k + w + M5_NYLOC_T, y=hy, z=hz, segments=6)])


def lever_bolt_tools() -> Manifold:
  """Room to put in and tighten the lift lever's bolt from the sides: a 3 mm hex key in its head, a 7 mm socket on
  its nut (carrier frame, lever down)."""
  y, z = LEVER_PIVOT
  half = BR_LEG_X[1] + M4_WASHER_T
  return (cyl_x(1.6, -60.0, -half - 4.0, y=y, z=z, segments=16) +
          cyl_x(6.0, half, 60.0, y=y, z=z, segments=32))


def spring_body() -> Manifold:'''
assert s.count(old) == 1
s = s.replace(old, new)
open(p, "w").write(s)

p = "assembly.py"
s = open(p).read()
old = '''  pairs.update({"lever bolt/hinge block": (LB, HB), "lever bolt/arm": (LB, AR), "lever bolt/teeth": (LB, T)})'''
new = '''  pairs.update({"lever bolt/hinge block": (LB, HB), "lever bolt/arm": (LB, AR), "lever bolt/teeth": (LB, T),
                "hinge bolt, washers and nut/hinge block": (A._carried(MP.hinge_bolt(), 0.0), HB),
                "room for a hex key and socket on the lever bolt/hinge block": (A._carried(MP.lever_bolt_tools(), 0.0), HB),
                "room for a hex key and socket on the lever bolt/arm": (A._carried(MP.lever_bolt_tools(), 0.0), AR)})'''
assert s.count(old) == 1
s = s.replace(old, new)
open(p, "w").write(s)
EOF
md5sum -c --quiet /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/stl_md5_before2.txt 2>/dev/null && echo "STLs still as before the build"; time PYTHONPATH=/home/claude/pylib python3 accord_lka_parts.py > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fitaudit/build.log 2>&1; echo "exit $?"; tail -4 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fitaudit/build.log; md5sum -c /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/stl_md5_before2.txt 2>/dev/null | grep -v ": OK$"; sed -n '/clearance checks/p;/^  hinge-block.stl/,+1p' ../report/parts_report.txt