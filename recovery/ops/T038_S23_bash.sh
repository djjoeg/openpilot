cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety/arc_caps.py <<'EOF'
import math
from opendbc.car import gen_empty_fingerprint
from opendbc.car.car_helpers import interfaces
from opendbc.car.vehicle_model import VehicleModel
from opendbc.car.hondastepper.values import CAR
P = CAR.HONDA_ACCORD_8G_STEPPER
CP = interfaces[P].get_params(P, gen_empty_fingerprint(), [], False, False, False)
VM = VehicleModel(CP)
MPH = 0.44704
for X in (15, 20, 21.5, 29.25, 35.75):
  out = []
  for mph in (40, 55, 70):
    u = mph * MPH
    vals = []
    for sr in (13.08, 15.3):
      VM.update_params(1.0, sr)
      k = VM.calc_curvature(math.radians(X), u, 0.0)
      vals.append(u * u * abs(k))
    out.append(f"{mph} mph {min(vals):.1f}-{max(vals):.1f} m/s2")
  print(f"wheel {X} deg: " + ", ".join(out))
EOF
cd /home/claude/work/opendbc && PYTHONPATH=/home/claude/pylib:/home/claude/work/opendbc timeout 120 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety/arc_caps.py 2>&1 | grep -v "^hondastepper:"