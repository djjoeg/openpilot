cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6 && cat > slide_vs_teeth.py <<'EOF'
"""How far the arm can slide across before the carrier, motor or gear meets the grip or the teeth piece (v6 geometry)."""
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import rightarm as RA, rightcheck as RC
g = RC.grip()
piece = RC.teeth_piece(18)
mg = RA.motor_and_gear(0.0)
parts = {"carrier": RA.carrier(0.0), "motor": mg["motor"], "board": mg["board"], "gear": mg["gear"]}
teeth = {a: piece.rotate((0.0, 0.0, RA.THETA + a)) for a in range(-40, 41, 10)}
for dx in (-0.25, -0.5, -1.0, -2.0, -3.0, -5.0, 2.0, 5.0, 10.0):
    worst = {}
    for n, m in parts.items():
        mm = m.translate((dx, 0.0, 0.0))
        vg = (mm ^ g).volume()
        vt = max(((mm ^ t).volume() if n != "gear" else 0.0) for t in teeth.values())
        if vg > 0.5 or vt > 0.5:
            worst[n] = (round(vg, 1), round(vt, 1))
    print(f"arm slid {dx:+.2f}: {worst if worst else 'clear (gear vs teeth not judged)'}")
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 slide_vs_teeth.py