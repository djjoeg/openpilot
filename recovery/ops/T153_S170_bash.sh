mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && cat > lev3.py <<'EOF'
import sys, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import slideassembly as SA, slideparts as SP
T0 = time.time()
A = SA.SlideAssembly(110.0)
ring = A.teeth_ring()
print("ring", round(time.time()-T0,1), "s", flush=True)
for t2t in (0.0, 4.5):
  for d in np.arange(SP.LEVER_SWING, -0.01, -5.0):
    st = SP.cam_state(float(d), t2t)
    off = st["carrier_off"]
    lev = A.lever(off, SP.SWING_SIGN * float(d))
    v = SA.overlap(ring, lev)
    g = round(lev.min_gap(ring, 10.0), 2) if v <= 1e-3 else None
    print(t2t, round(float(d),1), round(off,2), round(v,2), g, flush=True)
EOF
export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache
timeout 600 python3 lev3.py