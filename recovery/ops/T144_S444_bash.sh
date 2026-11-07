cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > ringcheck.py <<'EOF'
import os, sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
os.environ.setdefault("POP_CACHE", "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache")
import numpy as np
import popparts as PP, faceparts as FP, params as P
t = PP.PopTeeth()
prof = np.array([(p[0], p[1]) for p in t.profile()])
print('teeth piece profile (r, z): r from %.1f to %.1f, z from %.1f to %.1f' % (prof[:, 0].min(), prof[:, 0].max(), prof[:, 1].min(), prof[:, 1].max()))
# the profile's inner edge at each depth
for z in (-45, -40, -35, -30, -25, -20, -15, -10, -5, 0):
    sel = prof[np.abs(prof[:, 1] - z) < 2.5]
    if len(sel):
        print('   z %4d: r %.1f .. %.1f' % (z, sel[:, 0].min(), sel[:, 0].max()))
print('ties ring: r', round(t.w_in - 6.0, 1), '..', round(t.w_out + 6.0, 1), 'z', round(-t.rho - 3.0, 1), '.. 4')
print('grip: centre radius', t.rr, 'thickness', PP.GRIP_P)
EOF
PYTHONPATH=/home/claude/pylib python3 ringcheck.py