cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6 && cat > gear_in.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import rightarm as RA, rightcheck as RC
pieces = {n: RC.teeth_piece(k) for k, n in RC.TEETH_SETS}
g = RC.grip()
for dz in (0.0, RA.DZ_DEEP, RA.DZ_SHALLOW):
    mg = RA.motor_and_gear(dz)
    parts = {"carrier": RA.carrier(dz), "motor": mg["motor"], "board": mg["board"]}
    for dx in (-3.5, -4.0, -4.5):
        hit = []
        for a in range(-40, 41, 5):
            for name, pc in pieces.items():
                t = pc.rotate((0.0, 0.0, RA.THETA + a)).translate((0.0, 0.0, dz))
                for n, m in parts.items():
                    v = (m.translate((dx, 0, 0)) ^ t).volume()
                    if v > 0.5:
                        hit.append((name, a, n, round(v, 1)))
            for n, m in parts.items():
                v = (m.translate((dx, 0, 0)) ^ g.translate((0, 0, dz))).volume()
                if v > 0.5:
                    hit.append(("grip", a, n, round(v, 1)))
        print(f"teeth {dz:+.0f}, arm {dx:+.1f}: {hit[:4] if hit else 'clear'}")
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 gear_in.py