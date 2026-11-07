cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cat > dbg1.py <<'EOF'
import os, sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2")
os.environ.setdefault("POP_CACHE", "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache")
import popparts as PP
PP.MOUNT_DEG = -63.0
import popassembly as PA
from run_u import build
t, parts = build()
A = PA.PopAssembly(t, parts)
pl = A.plate()
print("plate wheel bbox", [round(v, 1) for v in pl.bounding_box()])
c = PP.wheel_to_carrier(pl)
print("plate carrier bbox", [round(v, 1) for v in c.bounding_box()])
print("hinge wheel", PP.carrier_point_to_wheel((0, PP.HINGE_P[0], PP.HINGE_P[1])))
for xc in (-20, 0, 20):
    print(xc, "plate underside z_c at y_c 80:", [round(v,1) for v in PP.wheel_to_carrier(pl).bounding_box()])
EOF
PYTHONPATH=/home/claude/pylib python3 dbg1.py