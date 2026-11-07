cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6 && cat > margins.py <<'EOF'
"""How near the car's parts (D=125 scene) come to the v6 arm parts: grow each car part until it touches."""
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import carscene as CS, rightarm as RA
s = CS.CarScene(D=125.0)
parts = {"plate": RA.plate_to_wheel(RA.frame_plate_v5()), "arm": RA.arm()}
for dz in (RA.DZ_OUT, 0.0, RA.DZ_MAX):
    mg = RA.motor_and_gear(dz)
    parts.update({f"carrier {dz:+.0f}": RA.carrier(dz), f"motor {dz:+.0f}": mg["motor"], f"board {dz:+.0f}": mg["board"]})
allp = None
for m in parts.values():
    allp = m if allp is None else allp + m
for grow in (0.0, 1.0, 2.0, 3.0, 5.0, 8.0):
    st = s.stalk(r=11.0 + grow)
    hit = [n for n, m in parts.items() if (m ^ st).volume() > 0.05]
    print(f"stalk {grow:.0f} mm thicker: {hit}")
dz_ = s.dash_z
for gap in (0.0, 1.0, 2.0, 3.0, 5.0, 8.0):
    b = s.bolster().translate((0.0, 0.0, gap))
    hit = [n for n, m in parts.items() if (m ^ b).volume() > 0.05]
    print(f"dash face {gap:.0f} mm nearer: {hit}")
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 margins.py