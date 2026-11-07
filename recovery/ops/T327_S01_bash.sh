mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6/skew && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6/skew && cat > skew.py <<'EOF'
"""How far the motor's shaft can point off the wheel's middle (in the wheel's plane, the red arrow) or tilt out of it
before the gear binds in the teeth: the gear turned about the pitch point, its own turn searched for the cleanest fit,
at the middle of the 20 teeth and near their ends."""
import math, sys
import numpy as np
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import rightarm as RA, rightcheck as RC, midteeth as MT, sideparts as S
from cadlib import box

g0 = S.side_gear_teeth_only()
c = RA.R_FACE_OUT * RA.U
mat = [[0.0, RA.V[0], -RA.U[0], float(c[0])], [0.0, RA.V[1], -RA.U[1], float(c[1])], [1.0, 0.0, 0.0, RA.Z_AXIS]]
P = np.array([166.0 * RA.U[0], 166.0 * RA.U[1], RA.Z_AXIS + 16.0])
piece = MT.mid_teeth(MT.MidTeeth(n_teeth=18))
th = RA.THETA

def gear(delta, w, alpha=0.0, beta=0.0):
    m = g0.rotate((0.0, 0.0, RC.MESH_PHASE + S.FP.FACE_RATIO * w + delta)).transform(mat)
    m = m.translate(tuple(-P)).rotate((0.0, 0.0, -th))      # U along x, V along y, P at 0
    m = m.rotate((0.0, beta, 0.0)).rotate((0.0, 0.0, alpha))  # beta: tilt about V... (see below); alpha: in the wheel's plane
    return m.rotate((0.0, 0.0, th)).translate(tuple(P))

def teeth(w):
    t = piece.rotate((0.0, 0.0, th + w))
    clip = box(P[0] - 40, P[0] + 40, P[1] - 40, P[1] + 40, -90.0, 0.0)
    return t ^ clip

mode = sys.argv[1]
ws = (0.0, -15.0, 15.0)
T = {w: teeth(w) for w in ws}
angles = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0] if mode == "alpha" else [0.0, 1.0, 2.0, 3.0, 4.0, 6.0]
deltas = np.arange(-6.0, 6.01, 0.25)
for a in angles:
    for sgn in ((1.0,) if a == 0 else (1.0, -1.0)):
        best = None
        clean = []
        for d in deltas:
            kw = {"alpha": sgn * a} if mode == "alpha" else {"beta": sgn * a}
            v = max((gear(float(d), w, **kw) ^ T[w]).volume() for w in ws)
            if best is None or v < best[1]:
                best = (float(d), v)
            if v < 0.01:
                clean.append(float(d))
        span = (min(clean), max(clean)) if clean else None
        print(f"{mode} {sgn * a:+.1f} deg: least overlap {best[1]:.3f} mm3 at the gear turned {best[0]:+.2f}; "
              f"clean from {span}", flush=True)
EOF
(PYTHONPATH=/home/claude/pylib timeout 1500 python3 skew.py alpha > alpha.txt 2>&1 &); (PYTHONPATH=/home/claude/pylib timeout 1500 python3 skew.py beta > beta.txt 2>&1 &); sleep 1; echo started