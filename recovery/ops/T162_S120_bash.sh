python3 - <<'EOF'
p = "sideassembly.py"
s = open(p).read()
old = s[s.index('  net = S.CF["load_N"] - 0.5\n  rows.append(MG.row(g, "Slid in, the spring keeps the motor in on bumps"'):s.index("  # the block's moments:")]
new = '''  # slid in, a jolt can throw the motor out along the slide: the spring holds it up to this many times gravity (not a
  # failure if it doesn't: it knocks out a little and back, unpowered, 27 mm short of the teeth)
'''
s = s.replace(old, new)
s = s.replace('''def side_margins() -> list:''', '''def slid_in_hold_g() -> float:
  """Slid in, the jolt (times gravity, along the slide's lean) the spring still holds the motor in against."""
  f = forces()
  return (S.CF["load_N"] - 0.5) / f["weight along the slide, outwards (N)"]


def side_margins() -> list:''')
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0,'.')
import sideassembly as SA, margins as MG
rows = SA.side_margins(); print([ (r['what'], r['factor']) for r in rows]); print('hold g', round(SA.slid_in_hold_g(), 2))
"