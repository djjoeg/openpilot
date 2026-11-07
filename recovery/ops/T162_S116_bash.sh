python3 - <<'EOF'
p = "sideparts.py"
s = open(p).read()
old = s[s.index("def teardrop_x("):s.index("def _guard() -> Manifold:")]
new = '''def teardrop_x(r: float, x0: float, x1: float, y: float, z: float) -> Manifold:
  """A hole along x with a 45 degree point on its +y side (printed with +y up)."""
  return gothic(r, 48).extrude(x1 - x0).transform([[0, 0, 1, x0], [0, 1, 0, y], [-1, 0, 0, z]])


'''
s = s.replace(old, new)
old = s[s.index("  # the spool's post, with a round face that guides the coil's side"):s.index("  # the stop at the inner end")]
new = '''  # the spool's post, with a round face that guides the coil's side
  (px0, px1), (py0, py1), (pz0, pz1) = POST
  parts.append(box(px0, px1, py0, py1, pz0, pz1))
  parts.append(cyl_y(POST_FACE, py1 - 1.6, py1, x=SPOOL_X, z=SPOOL_Z, segments=96))
'''
s = s.replace(old, new)
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0,'.')
import sideparts as S
for n, f in (('bracket', S.side_bracket), ('plate', S.side_plate), ('spool', S.side_spool)):
    m = f(); print(n, round(m.volume()), m.genus(), len(m.decompose()), [round(v,1) for v in m.bounding_box()])
" && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && PYTHONPATH=/home/claude/pylib timeout 600 python3 orient.py 2>&1 | head -3 && PYTHONPATH=/home/claude/pylib timeout 900 python3 run_internal.py