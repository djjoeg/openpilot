cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fea && python3 - <<'EOF'
s = open('armfea.py').read()
old = '''def solid_model(variant=None):
  arm = RA.arm()
  car = RA.carrier(0.0)
  fill = RA.uvz(RA.CH_U[0], RA.CH_U[1], RA.CH_V0, RA.CH_V1, RA.BAR_Z[0], RA.TOWER_Z[1])
  return arm + car + fill
'''
new = '''VARIANT = sys.argv[3] if len(sys.argv) > 3 else "v4"


def solid_model(variant=None):
  from cadlib import box
  from manifold3d import Manifold
  variant = variant or VARIANT
  arm = RA.arm()
  car = RA.carrier(0.0)
  fill = RA.uvz(RA.CH_U[0], RA.CH_U[1], RA.CH_V0, RA.CH_V1, RA.BAR_Z[0], RA.TOWER_Z[1])
  m = arm + car + fill
  if variant.startswith("deep"):
    # the arm 50 deep along the column from just outside the receiver's mouth (x 120.5) to the tower, under the plate
    depth = float(variant[4:] or 50)
    z1 = RA.ARM_Z[0] + depth
    blk = box(120.5, 150.0, RA.ARM_Y[0], RA.ARM_Y[1], RA.ARM_Z[0], z1)
    tw = RA.uvz(RA.TOWER_U[0], RA.TOWER_U[1], RA.TOWER_V[0], RA.TOWER_V[1], RA.ARM_Z[0], z1)
    web = Manifold.batch_hull([blk, tw]) ^ box(120.5, 400.0, -400.0, RA.ARM_Y[1], RA.ARM_Z[0], z1)
    m = m + web
  return m
'''
assert s.count(old) == 1
s = s.replace(old, new)
open('armfea.py', 'w').write(s)
EOF
cp armfea.py armfea_v.py
(PYTHONPATH=/home/claude/pylib timeout 900 python3 armfea.py 2.0 1800 deep50 2>&1 | grep -E "voxels|left|right|largest") ; echo ---; (PYTHONPATH=/home/claude/pylib timeout 900 python3 armfea.py 2.0 1800 deep80 2>&1 | grep -E "voxels|left|right")