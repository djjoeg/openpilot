cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety && cat > curves_indot.py <<'EOF'
"""Steering wheel turn needed for the tightest curve allowed at each design speed, from the Indiana Design Manual
(INDOT 2012) Figure 43-2A (open roadway, e_max 8%) and 43-2B (low-speed urban, e 6%)."""
import json, math
from opendbc.car.car_helpers import interfaces
from opendbc.car.vehicle_model import VehicleModel

MPH, DEG = 0.44704, math.pi / 180
CP = interfaces["HONDA_ACCORD_8G_STEPPER"].get_non_essential_params("HONDA_ACCORD_8G_STEPPER")
RATIOS = (13.08, 15.3, 18.0)
STIFF = (1.0, 1.0 / 3.0)
FIG_A = {70: 1810, 65: 1480, 60: 1200, 55: 960, 50: 760, 45: 585, 40: 445, 35: 315, 30: 215, 25: 135}   # e 8%
FIG_B = {45: 645, 40: 485, 35: 340, 30: 230, 25: 145}                                                   # e 6%


def steer(vm, r, u, bank):
  k = 1.0 / r
  return min(abs(vm.get_steer_from_curvature(k, u, bank)), abs(vm.get_steer_from_curvature(k, u, -bank))) / DEG


rows = []
for fig, table, e in (("43-2A e 8%", FIG_A, 0.08), ("43-2B e 6%", FIG_B, 0.06)):
  for v, rft in table.items():
    vals = []
    for sr in RATIOS:
      for k in STIFF:
        vm = VehicleModel(CP)
        vm.update_params(k, sr)
        vals.append(steer(vm, rft * 0.3048, v * MPH, math.atan(e)))
    vm = VehicleModel(CP)
    vm.update_params(1.0, 15.3)
    port = steer(vm, rft * 0.3048, v * MPH, math.atan(e))
    rows.append({"fig": fig, "mph": v, "radius_ft": rft, "steer_min": round(min(vals), 1), "steer_max": round(max(vals), 1),
                 "steer_port_model": round(port, 1)})
print(json.dumps(rows, indent=0))
EOF
PYTHONPATH=/home/claude/pylib:/home/claude/work/opendbc python3 curves_indot.py 2>&1 | grep -v "setup checks" > curves_indot.json; python3 -c "
import json
for r in json.load(open('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety/curves_indot.json')):
  print(f\"{r['fig']:11s} {r['mph']:3d} mph R {r['radius_ft']:5d} ft  steer {r['steer_min']:5.1f} - {r['steer_max']:5.1f}  (port model {r['steer_port_model']})\")
"