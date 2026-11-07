mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/springs && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/springs && cat > pick.py <<'EOF'
"""Which McMaster 1/2 in OD loop-end extension spring gives the pop-off toggle 1.4 on everything, for either reading
of McMaster's length (inside the loops, or over them)."""
import math
LBF, IN = 4.44822, 25.4
PIN_D, DEAD = 5.0, 50.0
S65, C25 = math.sin(math.radians((180 - DEAD) / 2)), math.cos(math.radians(DEAD / 2))
HOLD_REF = 1.65 / (55.0 * 38.57)      # hold factor per N mm of (pull x radius), from the current design
cands = [  # part, material, length in, wire in, IT lb, rate lbf/in, max lb, ext len at max in
  ("27749N488", "302 SS", 2.5, 0.075, 2.29, 22.41, 25.41, 3.53),
  ("7749N54", "302 SS", 2.75, 0.075, 2.29, 19.33, 25.41, 3.95),
  ("7749N539", "302 SS", 2.75, 0.069, 1.82, 12.33, 20.17, 4.24),
  ("7749N438", "302 SS", 2.25, 0.075, 2.29, 26.66, 25.41, 3.12),
  ("5108N591", "spring steel", 2.75, 0.075, 2.75, 23.2, 30.51, 3.95),
  ("5108N582", "spring steel", 2.75, 0.069, 2.18, 14.8, 24.21, 4.24),
  ("5108N589", "spring steel", 2.25, 0.075, 2.75, 32.0, 30.51, 3.12),
  ("5108N58", "spring steel", 2.25, 0.069, 2.18, 20.3, 24.21, 3.33),
]
for part, mat, L, w, it, k, mx, ext in cands:
  L0, wd, IT, K, MX = L * IN, w * IN, it * LBF, k * LBF / IN, mx * LBF
  best = None
  for r10 in range(250, 520):
    r = r10 / 10.0
    Lon = 2 * r * S65 + PIN_D
    Ldc = 2 * r + PIN_D
    rows = {}
    for reading, l0 in (("inside", L0), ("over", L0 - 2 * wd)):
      if Lon < l0:
        rows = None
        break
      Fon = IT + K * (Lon - l0)
      Fdc = IT + K * (Ldc - l0)
      defl = (Ldc - l0) / (ext * IN - L0)      # share of the stretch McMaster rates it for
      rows[reading] = (Fon, Fdc, MX / Fdc, Fon * r * HOLD_REF, defl)
    if rows is None:
      continue
    hold_lo = rows["inside"][3]
    spring_lo = min(rows["inside"][2], rows["over"][2])
    if hold_lo >= 1.5 and (best is None or spring_lo > best[1]):
      best = (r, spring_lo, rows)
  if best:
    r, sm, rows = best
    i, o = rows["inside"], rows["over"]
    print(f"{part:10s} {mat:12s} {L:.2f}in w{w:.3f}: r {r:5.1f}  pull on {i[0]:5.1f}/{o[0]:5.1f} N  at the snap {i[1]:5.1f}/{o[1]:5.1f} N"
          f"  spring margin {i[2]:.2f}/{o[2]:.2f}  hold {i[3]:.2f}/{o[3]:.2f}  stretch used {i[4]:.0%}/{o[4]:.0%}")
  else:
    print(part, "no radius gives hold 1.5")
EOF
python3 pick.py