cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && cat > tiltroom.py <<'EOF'
"""Room along a tilted slide: forward along the column, tilted out (+) or in (-) by th degrees."""
import sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import slideassembly as SA, slideparts as SP
from cadlib import union
D = float(sys.argv[1])
A = SA.SlideAssembly(D, -70.0, parts={})
mb = SP.motor_board()
back = union([SP.board_cap(), mb["car plug"], mb["motor plug"], mb["motor's own plug"], mb["motor"]])
car = dict(A.car_parts())
cov, bc, tab = car["column cover"], car["back cover (it turns with the wheel)"], car["adjustment tab, its swing and your fingers on it"]
fingers = A.fingers()
for th in [float(v) for v in sys.argv[2].split(",")]:
  c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
  def at(S):
    return A.place(back.translate((0.0, S * c, S * s)))
  S, hit = 0.0, None
  while S < 30:
    m = at(S)
    for n, o in (("column cover", cov), ("back cover", bc), ("tab room", tab)):
      if SA.overlap(m, o) > 0.05:
        hit = n; break
    if hit: break
    S += 0.25
  Sf = 0.0
  while Sf < 30 and SA.overlap(A.place(mb["motor"].translate((0.0, Sf * c, Sf * s))), fingers) > 0.05:
    Sf += 0.25
  print(f"D {D:.0f} tilt {th:+.0f}: room {S - 0.25:.2f} along the slide ({(S - 0.25) * c:.2f} forward) before the {hit}; motor clear of the fingers after {Sf:.2f} ({Sf * c:.2f} forward)", flush=True)
EOF
export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache
(timeout 1500 python3 tiltroom.py 110 -20,0,15,25,35 > tilt_110.txt 2>&1 &); timeout 1500 python3 tiltroom.py 113 -20,0,15,25,35 > tilt_113.txt 2>&1; cat tilt_113.txt; cat tilt_110.txt