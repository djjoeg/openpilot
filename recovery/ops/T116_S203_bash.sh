mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && cat > closeups.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
from manifold3d import Manifold, Mesh
import render as R

def load(p):
  import struct
  d = open(p, "rb").read()
  n = struct.unpack("<I", d[80:84])[0]
  a = np.frombuffer(d[84:84 + n * 50], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
  v = a["v"].reshape(-1, 3).astype(np.float32)
  uv, inv = np.unique(v, axis=0, return_inverse=True)
  return Manifold(Mesh(vert_properties=uv, tri_verts=inv.reshape(-1, 3).astype(np.uint32)))

S = "/home/claude/deliver/hardware/stl/back-teeth-mount/"
ft = load(S + "fit-test-back-teeth.stl")
sp = load(S + "fit-test-back-teeth-spoke.stl")
up = load(S + "back-teeth-upper.stl")
lo = load(S + "back-teeth-lower.stl")
pl = load(S + "column-plate.stl")
hb = load(S + "back-hinge-block.stl")
c = (.6, .72, .9)
views = [R.look((0.3, -0.5, 1.0), (0, 1, 0)), R.look((0.2, 0.6, -1.0), (0, 1, 0)), R.look((1, -1, 0.6), (0, 0, 1))]
R.save("closeup-fit.png", [([(ft, c)], views[0]), ([(ft, c)], views[1]), ([(sp, c)], views[0]), ([(sp, c)], views[1])],
       ["fit test, bed side", "fit test, teeth side", "spoke fit test, bed side", "spoke fit test, teeth side"], size=(700, 600))
R.save("closeup-pieces.png", [([(up, c)], views[1]), ([(lo, c)], views[1]), ([(pl, c)], views[2]), ([(hb, c)], views[2])],
       ["upper piece, top", "lower piece, top", "column plate", "hinge block"], size=(700, 600))
print("ok")
EOF
PYTHONPATH=/home/claude/pylib python3 closeups.py