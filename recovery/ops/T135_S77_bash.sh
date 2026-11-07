cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop && cat > probe.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import popassembly as PA, popparts as PP
t = PP.PopTeeth()
teeth = PA.cached(f"pop_teeth_short_{t.rr:.1f}_{t.z_axis:.2f}_{t.mount_deg:.1f}", lambda: PP.pop_pieces(t)["one-piece"])
mb = PP.motor_and_board()
parts = {"teeth": teeth, "gear": PP.pop_motor_gear(), "gear_teeth_only": PP.pop_gear_teeth_only(), "carrier": PP.pop_carrier(),
         "motor": mb["body"] + mb["board"] + mb["plugs"], "block": PP.pop_hinge_block(), "plate": PP.pop_column_plate()}
A = PA.PopAssembly(t, parts)
for L in np.arange(0.5, 20.1, 0.5):
  x = A.teeth(0.0) ^ A.motor(float(L))
  if x.volume() > 1e-4:
    print("motor/teeth at lift", L, round(x.volume(), 4), [round(v, 1) for v in x.bounding_box()])
for name, part in (("springs", A.springs(0.0)), ("block", A.block()), ("bolts", A.bolts(0.0))):
  x = part ^ A.key()
  print(name, "/key", round(x.volume(), 2), [round(v, 1) for v in x.bounding_box()])
# stalk margin: how far the parts can move up (+y) before meeting the stalk, on and parked
for L in (0.0, 75.0):
  for name, part in (("motor", A.motor(L)), ("carrier", A.carrier(L)), ("springs", A.springs(L)), ("bolts", A.bolts(L)), ("block", A.block())):
    print(f"lift {L}: {name} up to the stalk {PA.gap(part, A.stalk(), (0, 1, 0))}  down to the key {PA.gap(part, A.key(), (0, -1, 0))}  key room {PA.gap(part, A.key_room(), (0, -1, 0))}")
EOF
timeout 1800 env PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache python3 probe.py 2>&1 | tail -30