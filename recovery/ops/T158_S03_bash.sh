cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && cat > sideroom.py <<'EOF'
"""How far the motor can slide in towards the middle of the wheel (along its own shaft) and forward (towards the nose),
and how far it has to go to get the gear out of the teeth and everything out of the fingers' room round the grip."""
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import slideassembly as SA, slideparts as SP, popparts as PP
from cadlib import union
D = float(sys.argv[1]) if len(sys.argv) > 1 else 113.0
A = SA.SlideAssembly(D, -70.0, parts={})
mb = SP.motor_board()
mov = {"motor": mb["motor"], "board cover": SP.board_cap(), "car plug": mb["car plug"], "motor plug": mb["motor plug"],
       "motor's own plug": mb["motor's own plug"], "carrier": SP.slide_carrier(), "gear": PP.pop_motor_gear()}
car = dict(A.car_parts())
fixed = {"back cover": car["back cover (it turns with the wheel)"], "column cover": car["column cover"]}
fingers = A.fingers()
ring = A.teeth_ring()
def placed(m, d_in=0.0, d_fwd=0.0):
  return A.place(m.translate((0.0, d_fwd, -d_in)))
def first_hit(name, m, fx, step=0.25, most=45.0):
  s = 0.0
  while s <= most:
    pm = placed(m, *fx(s))
    for cn, c in fixed.items():
      if SA.overlap(pm, c) > 0.05:
        return round(s - step, 2), cn
    s += step
  return None, None
def clear_of(target, m, fx, step=0.25, most=45.0):
  s = 0.0
  while s <= most:
    if SA.overlap(placed(m, *fx(s)), target) <= 0.05:
      return round(s, 2)
    s += step
  return None
print(f"D {D:.0f}")
for name, m in mov.items():
  a = first_hit(name, m, lambda s: (s, 0.0))
  b = first_hit(name, m, lambda s: (0.0, s))
  f_in = clear_of(fingers, m, lambda s: (s, 0.0))
  f_fwd = clear_of(fingers, m, lambda s: (0.0, s))
  print(f"  {name:16s} in-room {a}  fwd-room {b}  | clear of fingers: in {f_in} fwd {f_fwd}")
g = PP.pop_motor_gear()
print("  gear out of the teeth: in", clear_of(ring, g, lambda s: (s, 0.0)), " fwd", clear_of(ring, g, lambda s: (0.0, s)))
EOF
export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache
timeout 1200 python3 sideroom.py 113 2>&1 | tail -12