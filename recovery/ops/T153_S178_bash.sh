cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && cat > levsweep.py <<'EOF'
import sys, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import popparts as PP, slideparts as SP, slideassembly as SA
A = SA.SlideAssembly(110.0)
ring = A.teeth_ring()
Rm = PP.rot_z(A.mount); R = Rm @ PP.R_POP; T = Rm @ np.array([PP.R_FACE_P, 0.0, PP.Z_AXIS_P])
Rt = R.T; off = -Rt @ T
ring_c = ring.transform([[float(Rt[i,0]), float(Rt[i,1]), float(Rt[i,2]), float(off[i])] for i in range(3)])
variants = [(12, (-24, -8), 6.5), (12, (-22, -8), 5.5), (12, (-20, -8), 5.5), (14, (-24, -8), 6.0), (15, (-24, -8), 6.0),
            (15, (-24, -8), 6.5), (15, (-22, -8), 6.0), (16, (-24, -8), 6.5)]
for py, h, pr in variants:
  SP.PIVOT = (float(py), 0.0); SP.HANDLE_ON = (float(h[0]), float(h[1])); SP.PAD_R = pr
  worst = (99.0, None)
  for t2t in (0.0, 4.5):
    for d in np.arange(SP.LEVER_SWING, -0.01, -2.5):
      st = SP.cam_state(float(d), t2t)
      lev = SP.slide_lever(SP.SWING_SIGN * float(d)).translate((0.0, st["carrier_off"], 0.0))
      v = (lev ^ ring_c).volume()
      g = -v if v > 1e-3 else lev.min_gap(ring_c, 10.0)
      if g < worst[0]:
        worst = (round(g, 2), (t2t, float(d)))
  print("pivot", py, "handle", h, "pad", pr, "reach", round(np.hypot(*h) - 3.5 + pr, 1), "-> worst gap", worst,
        "handle N (normal, t2t)", round(216.0 / np.hypot(*h), 1), round(795.0 / np.hypot(*h), 1), flush=True)
EOF
export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache
timeout 900 python3 levsweep.py