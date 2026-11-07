cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > bbox.py <<'EOF'
import sys, os
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
os.environ.setdefault("POP_CACHE", "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache")
import numpy as np
import popassembly as PA, popparts as PP, params as P
from run_u import build
t, parts = build()
A = PA.PopAssembly(t, parts)
def bb(m):
    b = m.bounding_box()
    return [round(v, 0) for v in b]
for name, m in (("block", A.block()), ("plate", A.plate()), ("tabs", A.tabs()), ("carrier on", A.carrier()), ("motor on", A.motor()),
                ("carrier off", A.carrier(PP.LIFT_OFF)), ("motor off", A.motor(PP.LIFT_OFF)), ("springs on", A.springs()),
                ("springs off", A.springs(PP.LIFT_OFF)), ("bolts on", A.bolts()), ("switch", A.switch()), ("teeth", A.teeth())):
    print('%-12s' % name, bb(m))
print('key rod from', P.KEY_FROM, 'to', P.KEY_TO, 'stalk', P.STALK_FROM, P.STALK_TO, 'cover bottom', P.COVER_BOTTOM, 'front z', P.COVER_FRONT_Z)
EOF
POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 900 python3 bbox.py 2>&1 | tail -20