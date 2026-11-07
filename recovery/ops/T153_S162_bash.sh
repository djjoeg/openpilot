cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && cat > lev.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import slideassembly as SA, slideparts as SP
A = SA.SlideAssembly(110.0)
out = []
for t2t in (0.0, 4.5):
  for d in np.arange(SP.LEVER_SWING, -0.01, -5.0):
    st = SP.cam_state(float(d), t2t)
    off = st["carrier_off"]
    lev = A.lever(off, SP.SWING_SIGN * float(d))
    for w in (0.0, -15.0, 15.0):
      v = SA.overlap(A.teeth(w), lev)
      if v > 1e-3: out.append(("teeth", t2t, round(float(d),1), w, round(off,2), round(v,2)))
    v = SA.overlap(lev, A.block())
    if v > 1e-3: out.append(("block", t2t, round(float(d),1), round(off,2), round(v,2)))
for o in out: print(o)
EOF
export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache && timeout 1200 python3 lev.py