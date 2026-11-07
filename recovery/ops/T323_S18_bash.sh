mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6 && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6 && cat > carparts.py <<'EOF'
"""Overlap of the v5 and v6 arm parts with the car scene's key, stalk and dash face (D=125, as rightcheck's cover)."""
import importlib.util, sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import carscene as CS
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
SP = "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/"
v6 = load("ra6", "/home/claude/deliver/hardware/cad/rightarm.py")
v5 = load("ra5", SP + "rightarm.v5.py")
for D in (125.0, 97.0):
    s = CS.CarScene(D=D)
    car = {**s.key_parts(), "stalk swept": s.stalk(), "dash face": s.bolster()}
    for tag, RA in (("v5", v5), ("v6", v6)):
        fp = RA.frame_plate_v5() if hasattr(RA, "frame_plate_v5") else RA.frame_plate_v4()
        parts = {"plate": RA.plate_to_wheel(fp), "arm": RA.arm()}
        for dz in (RA.DZ_OUT, 0.0, RA.DZ_MAX):
            mg = RA.motor_and_gear(dz)
            parts.update({f"carrier {dz:+.0f}": RA.carrier(dz), f"motor {dz:+.0f}": mg["motor"], f"board {dz:+.0f}": mg["board"]})
        for pn, pm in parts.items():
            for cn, cm in car.items():
                v = (pm ^ cm).volume()
                if v > 0.5:
                    print(f"D {D:.0f} {tag}: {pn} / {cn}: {v:.0f} mm3")
    print("done D", D)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 carparts.py