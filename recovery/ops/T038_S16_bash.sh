mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety && cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety/numbers.py <<'EOF'
import math
from opendbc.car import gen_empty_fingerprint
from opendbc.car.car_helpers import interfaces
from opendbc.car.vehicle_model import VehicleModel, calc_slip_factor
from opendbc.car.hondastepper.values import CAR, CarControllerParams

P = CAR.HONDA_ACCORD_8G_STEPPER
CI = interfaces[P]
CP = CI.get_params(P, gen_empty_fingerprint(), [], False, False, False)
cp = CarControllerParams(CP)
print("STEER_MAX units", cp.STEER_MAX, "-> Nm", cp.STEER_MAX * 0.125, "| delta up", cp.STEER_DELTA_UP, "per", cp.STEER_STEP, "frames")
print("mass", CP.mass, "wheelbase", CP.wheelbase, "steerRatio", CP.steerRatio, "tireStiffnessFront", CP.tireStiffnessFront, "rear", CP.tireStiffnessRear, "cf ratio", CP.centerToFront / CP.wheelbase)

MPH = 0.44704
FT = 0.3048
G = 9.81
lane_w, car_w = 3.66, 72.7 * 0.0254
print(f"lane 3.66 m (12 ft), car {car_w:.3f} m wide -> {(lane_w - car_w) / 2:.2f} m each side when centred")

# ---- jerk at 70 mph: sideways movement if the push rises at a limit and nobody steers back ----
def drift(a_max, t_ramp, t):
  if t <= t_ramp:
    return a_max / t_ramp * t ** 3 / 6
  y_r = a_max * t_ramp ** 2 / 6
  v_r = a_max * t_ramp / 2
  dt = t - t_ramp
  return y_r + v_r * dt + 0.5 * a_max * dt ** 2

def t_to(a_max, t_ramp, y):
  t = 0.0
  while drift(a_max, t_ramp, t) < y:
    t += 0.001
  return t

margin = (lane_w - car_w) / 2
cases = [
  ("openpilot's own limits, estimated car response (4 Nm -> 1.5 m/s2, full push after 0.64 s)", 1.5, 32 / (1 / 0.02)),
  ("safety chip's limits, estimated response (4.5 Nm -> 1.69 m/s2, full after 0.36 s)", 1.5 * 36 / 32, 36 / (2 / 0.02)),
  ("safety chip's limits, if the car responds as strongly as comma's rule allows (3.0 m/s2 at full push)", 3.0, 36 / (2 / 0.02)),
]
for name, a, tr in cases:
  ds = [drift(a, tr, t) for t in (0.5, 1.0, 1.5, 2.0)]
  print(f"{name}: drift after 0.5/1/1.5/2 s = " + " / ".join(f"{d:.2f}" for d in ds) + f" m; reaches the lane line ({margin:.2f} m) after {t_to(a, tr, margin):.2f} s")
v70 = 70 * MPH
print(f"70 mph = {v70:.1f} m/s: {v70:.0f} m travelled per second")

# ---- curves: steering wheel angle and sideways acceleration ----
VM = VehicleModel(CP)
print("slip factor", calc_slip_factor(VM))
rows = [(70, 1810), (65, 1480), (60, 1200), (55, 960), (50, 758), (35, 314), (30, 214)]
for mph, r_ft in rows:
  u = mph * MPH
  R = r_ft * FT
  a = u * u / R
  for sr in (13.08, 15.3):
    CP2 = CP.copy() if hasattr(CP, "copy") else CP
    VM.update_params(1.0, sr)
    sw = math.degrees(VM.get_steer_from_curvature(1 / R, u, 0.0))
    if sr == 13.08:
      sw_a = sw
    else:
      sw_b = sw
  # with 8% superelevation the road's bank carries g*e of the sideways force
  a_tires = a - G * 0.08
  print(f"{mph} mph, minimum radius {r_ft} ft ({R:.0f} m): sideways acceleration {a:.2f} m/s2 ({a / G:.2f} g), "
        f"{a_tires:.2f} m/s2 left for the tires with 8% bank; steering wheel {sw_a:.1f} to {sw_b:.1f} deg (ratio 13.08 to 15.3)")
# typical interstate curves are far gentler: e.g. 4% bank at the design speed
for mph, r_ft in [(70, 5050), (70, 3150), (55, 1920)]:
  u = mph * MPH; R = r_ft * FT
  VM.update_params(1.0, 15.3); sw_b = math.degrees(VM.get_steer_from_curvature(1 / R, u, 0.0))
  VM.update_params(1.0, 13.08); sw_a = math.degrees(VM.get_steer_from_curvature(1 / R, u, 0.0))
  print(f"{mph} mph, radius {r_ft} ft: {u*u/R:.2f} m/s2, steering wheel {sw_a:.1f} to {sw_b:.1f} deg")
# what steering wheel angle does a jerk produce at 70 mph: angle for 1.5, 1.69 and 3.0 m/s2
for a in (1.5, 1.69, 3.0):
  u = v70; R = u * u / a
  VM.update_params(1.0, 15.3); sw_b = math.degrees(VM.get_steer_from_curvature(1 / R, u, 0.0))
  VM.update_params(1.0, 13.08); sw_a = math.degrees(VM.get_steer_from_curvature(1 / R, u, 0.0))
  print(f"70 mph at {a} m/s2: radius {R:.0f} m, steering wheel {sw_a:.1f} to {sw_b:.1f} deg")
# what a teeth arc of +-X degrees allows at 70 mph and 50 mph
for X in (10, 15, 20, 29.25):
  for mph in (70, 50):
    u = mph * MPH
    VM.update_params(1.0, 15.3)
    k = VM.calc_curvature(math.radians(X), u, 0.0)
    print(f"steering wheel at {X} deg, {mph} mph: radius {1/abs(k):.0f} m, sideways {u*u*abs(k):.1f} m/s2 (ratio 15.3)")
EOF
cd /home/claude/work/opendbc && PYTHONPATH=/home/claude/pylib:/home/claude/work/opendbc timeout 120 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/safety/numbers.py 2>&1 | grep -v "^hondastepper:"