python3 - <<'EOF'
p = "sideassembly.py"
s = open(p).read()
s = s.replace('''    "it stays in until the car bumps up at (g on top of gravity)": round(net_in / (m_moving * 9.81 * -up) - 1.0, 2),''',
'''    "slid in, it stays in until a bump throws it outwards at (g, on top of gravity)": round(net_in / (m_moving * 9.81 * -up), 2),''')
s = s.replace('''  v_end = math.sqrt(max(0.0, 2 * (net_in - pin_on_flat * rub * 0.25) * S.STROKE / 1000.0 / m_moving))''',
'''  # let go: the spring pulls it in; the pin rides the ear's flat for the first few mm (rubbing), then is clear
  rub_work = sum(rub * pin_at(S.pin_back_at(float(s))) * 0.1 for s in np.arange(0.2, S.STROKE, 0.1)
                 if S.pin_back_at(float(s)) >= S.PIN_IN - 1e-6)
  v_end = math.sqrt(max(0.0, 2 * (net_in * S.STROKE - rub_work) / 1000.0 / m_moving))
  v_end_knob = math.sqrt(max(0.0, 2 * net_in * S.STROKE / 1000.0 / m_moving))''')
s = s.replace('''    "speed it reaches the bumper if let go (m/s, about)": round(v_end, 2),''',
'''    "speed it hits the bumper at, the knob let go at once / held out (m/s, about)": (round(v_end, 2), round(v_end_knob, 2)),
    "... its energy then (J)": (round(0.5 * m_moving * v_end ** 2, 2), round(0.5 * m_moving * v_end_knob ** 2, 2)),''')
# strip vs moving parts
s = s.replace('''  # moving parts against each other: the bracket and the motor, the block screws' heads in their pockets
  mv = A.movers(0.0)''', '''  # the spring's strip (it runs from the coil to the clamp) against everything but its coil and the tab it is clamped to
  for s in steps:
    strip = S.spring_parts(s)["strip"]
    mv, fx = A.movers(s), A.fixed(s)
    for name, part in list(mv.items()) + list(fx.items()):
      if name in ("spring's coil and spool", "spring's clamp"):
        continue
      v = overlap(strip.translate((-0.05, 0, 0)), part) if name == "motor bracket" else overlap(strip, part)
      key = f"spring's strip/{name}"
      if v > res.get(key, (0.0, None))[0]:
        res[key] = (v, s)
  # moving parts against each other: the bracket and the motor, the block screws' heads in their pockets
  mv = A.movers(0.0)''')
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 - <<'EOF'
import time, sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import sideparts as S
import sideassembly as SA
t0 = time.time()
mb = S.motor_board()
from cadlib import union
p = {"t": S.SideTeeth(), "teeth": None, "gear": S.side_gear(), "gear_teeth_only": S.side_gear_teeth_only(),
     "bracket": S.side_bracket(), "plate": S.side_plate(), "spool": S.side_spool(),
     "motor": union([mb["motor"], mb["board+cap"], mb["car plug"], mb["motor plug"], mb["motor's own plug"]]),
     "rail": S.rail(), "block": S.block(), "block screws": S.block_screws()}
A = SA.SideAssembly(p)
res = SA.internal(A)
bad = sorted([(k, v) for k, v in res.items() if v[0] > 1e-3 and "touching" not in k], key=lambda kv: -kv[1][0])
print("internal checks:", len(res), "pairs; over 0.001 mm3:")
for k, v in bad:
    print(f"  {k}: {v[0]:.3f} mm3 at s={v[1]}")
for k, v in res.items():
    if "touching" in k:
        print("  ", k, round(v[0], 4))
print(SA.touching_at_stops(A))
for k, v in SA.forces().items():
    print(" ", k, v)
print(SA.switch_states())
print("time", round(time.time() - t0, 1))
EOF