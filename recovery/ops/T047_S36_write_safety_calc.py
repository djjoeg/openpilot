"""
Safety numbers for the Accord lane keeping build: how far the car moves sideways at 70 mph if the steering pushes the
wrong way, and how much steering wheel turn highway curves need. Uses openpilot's own vehicle model (opendbc
VehicleModel) with the car port's parameters, so the numbers match what sunnypilot assumes about the car.

Run: PYTHONPATH=/home/claude/pylib:/home/claude/work/opendbc python3 safety_calc.py
"""
import copy
import json
import math

import numpy as np

from opendbc.car.car_helpers import interfaces
from opendbc.car.vehicle_model import VehicleModel, calc_slip_factor, create_dyn_state_matrices

G = 9.81
MPH = 0.44704
DEG = math.pi / 180

CP = interfaces["HONDA_ACCORD_8G_STEPPER"].get_non_essential_params("HONDA_ACCORD_8G_STEPPER")

# Steering ratio: Honda lists 13.08:1; the port uses 15.3; openpilot's fitted ratios for Hondas run well above the
# listed ones (2018 Accord: 16.33 fitted vs 11.82 listed, 1.38 times), which applied to 13.08 gives about 18.
RATIOS = {"Honda's listed 13.08": 13.08, "the port's 15.3": 15.3, "about 18 (fitted/listed like the 2018 Accord)": 18.0}


def vm_for(sr: float) -> VehicleModel:
  cp = copy.deepcopy(CP)
  cp.steerRatio = sr
  return VehicleModel(cp)


VM = vm_for(CP.steerRatio)
sf = calc_slip_factor(VM)
understeer_deg_per_g = -sf * VM.l * G / DEG     # front wheel degrees per g of sideways acceleration, beyond L/R

out = {"car": {"mass_kg_with_cargo": round(CP.mass, 1), "wheelbase_m": round(CP.wheelbase, 3),
               "steer_ratio_port": round(CP.steerRatio, 2), "understeer_deg_per_g": round(understeer_deg_per_g, 2)}}

# ---------- 1. sideways acceleration at 70 mph with the steering wheel held at the end of the teeth ----------
U70 = 70 * MPH
TEETH = {"short teeth, full push (14.6)": 14.6, "short teeth, weak push ends (22.7)": 22.7,
         "long teeth, full push (29.2)": 29.2, "long teeth, weak push ends (37.3)": 37.3}
acc = {}
for name, sw in TEETH.items():
  acc[name] = {rn: round(U70 ** 2 * vm_for(sr).calc_curvature(sw * DEG, U70, 0.0), 2) for rn, sr in RATIOS.items()}
out["lateral_accel_70mph_at_teeth_end_m_s2"] = acc


# ---------- 2. steering wheel turn needed to hold curves ----------
# AASHTO Green Book (2018) minimum radius for each design speed, e_max 6% (urban freeways and ramps; Table 3-8,
# rounded values in feet), and e_max 8% for rural interstates (Table 3-9).
R_MIN_FT_E6 = {70: 2040, 65: 1660, 60: 1330, 55: 1060, 50: 833, 45: 643, 40: 485, 35: 340, 30: 231, 25: 144}
R_MIN_FT_E8 = {70: 1810, 65: 1480, 60: 1200}


def steer_needed(vm: VehicleModel, radius_m: float, u: float, bank: float) -> float:
  """Steering wheel degrees to hold a curve of this radius at speed u on a road banked into the turn by `bank` (rad).
  Openpilot's roll sign depends on the turn's direction, so take the sign that lowers the steering needed."""
  k = 1.0 / radius_m
  a = abs(vm.get_steer_from_curvature(k, u, bank))
  b = abs(vm.get_steer_from_curvature(k, u, -bank))
  return min(a, b) / DEG


curves = []
for v, rft in R_MIN_FT_E6.items():
  r = rft * 0.3048
  u = v * MPH
  row = {"speed_mph": v, "radius_ft": rft, "radius_m": round(r), "bank": "6%",
         "steer_deg": {rn: round(steer_needed(vm_for(sr), r, u, math.atan(0.06)), 1) for rn, sr in RATIOS.items()},
         "steer_deg_flat_road": {rn: round(steer_needed(vm_for(sr), r, u, 0.0), 1) for rn, sr in RATIOS.items()},
         "sideways_accel_m_s2": round(u ** 2 / r, 2)}
  curves.append(row)
for v, rft in R_MIN_FT_E8.items():
  r = rft * 0.3048
  u = v * MPH
  curves.append({"speed_mph": v, "radius_ft": rft, "radius_m": round(r), "bank": "8%",
                 "steer_deg": {rn: round(steer_needed(vm_for(sr), r, u, math.atan(0.08)), 1) for rn, sr in RATIOS.items()},
                 "steer_deg_flat_road": {rn: round(steer_needed(vm_for(sr), r, u, 0.0), 1) for rn, sr in RATIOS.items()},
                 "sideways_accel_m_s2": round(u ** 2 / r, 2)})
# gentler, more typical interstate curves
for v, r in ((70, 1000), (70, 1500), (55, 600)):
  u = v * MPH
  curves.append({"speed_mph": v, "radius_ft": round(r / 0.3048), "radius_m": r, "bank": "flat (worst case)",
                 "steer_deg": {rn: round(steer_needed(vm_for(sr), r, u, 0.0), 1) for rn, sr in RATIOS.items()},
                 "sideways_accel_m_s2": round(u ** 2 / r, 2)})
out["curves"] = curves


# ---------- 3. how far the car moves sideways at 70 mph if steering pushes the wrong way ----------
DT = 0.001
LANE_M, CAR_W = 3.66, 1.85                 # 12 ft lane; 2010 Accord sedan 72.7 in wide
TO_LINE = (LANE_M - CAR_W) / 2             # centred: room to the lane line
CORR_A, CORR_RAMP = 3.0, 0.3               # the driver's correction: steers back to 3 m/s^2 the other way over 0.3 s


def point_mass(acc_fn, t_end=4.0):
  """Lateral offset (m), speed and acceleration over time for a sideways acceleration profile acc_fn(t)."""
  n = int(t_end / DT) + 1
  t = np.arange(n) * DT
  a = np.array([acc_fn(x) for x in t])
  v = np.cumsum(a) * DT
  y = np.cumsum(v) * DT
  return t, y, v, a


def bicycle(sw_fn, u, t_end=4.0, vm=VM):
  """Openpilot's dynamic bicycle model driven by a steering wheel angle profile sw_fn(t) in degrees."""
  A, B = create_dyn_state_matrices(u, vm)
  n = int(t_end / DT) + 1
  t = np.arange(n) * DT
  x = np.zeros((2, 1))
  psi, y = 0.0, 0.0
  ys, vs, accs = np.zeros(n), np.zeros(n), np.zeros(n)
  for i in range(n):
    sa = sw_fn(t[i]) * DEG
    xdot = A @ x + B @ np.array([[sa], [0.0]])
    lat_v = u * math.sin(psi) + x[0, 0] * math.cos(psi)
    ys[i], vs[i] = y, lat_v
    accs[i] = xdot[0, 0] + u * x[1, 0]          # sideways acceleration = v_dot + u r
    x = x + xdot * DT
    psi += x[1, 0] * DT
    y += lat_v * DT
  return t, ys, vs, accs


def outcome(t, y, v, a, t_react):
  """Offset when the driver starts correcting, and the most it reaches before the correction stops the drift."""
  i = int(round(t_react / DT))
  y0, v0, a0 = float(y[i]), float(v[i]), float(a[i])
  # after t_react: acceleration goes from a0 to -CORR_A over CORR_RAMP, then stays, until sideways speed is zero
  yy, vv, aa, tt = y0, v0, a0, 0.0
  while vv > 0 and tt < 10:
    aa = a0 + (-CORR_A - a0) * min(1.0, tt / CORR_RAMP)
    vv += aa * DT
    yy += vv * DT
    tt += DT
  return {"offset_at_reaction_m": round(y0, 2), "sideways_speed_m_s": round(v0, 2), "most_offset_m": round(yy, 2)}


scen = {}
# A. what sunnypilot itself allows on every car: requested sideways acceleration up to 3 m/s^2, built up at most
#    5 m/s^3 (drive_helpers.clip_curvature), followed perfectly
scen["A: sunnypilot's own limits (3 m/s2, 5 m/s3), any car"] = point_mass(lambda x: min(5.0 * x, 3.0))
# B. what the safety chip allows this port: 4.5 Nm, rising at 6.25 Nm/s, with the port's estimate that 4 Nm gives
#    1.5 m/s^2 (not measured)
scen["B: safety chip limits, port's estimate of push vs turn"] = point_mass(lambda x: min(6.25 * x, 4.5) / 4.0 * 1.5)
# C. the steering wheel driven to the end of the teeth (the physical stop), rising over the safety chip's 0.72 s
#    torque ramp, or faster (0.3 s) if the steering is light
for label, sw_end in (("short teeth", 14.6), ("long teeth", 29.2)):
  for ramp in (0.72, 0.3):
    scen[f"C: wheel to the end of the {label} ({sw_end} deg) in {ramp} s"] = bicycle(
      lambda x, s=sw_end, r=ramp: s * min(1.0, x / r), U70)

res = {}
for name, (t, y, v, a) in scen.items():
  res[name] = {"most_sideways_accel_m_s2": round(float(np.max(a)), 2)}
  for tr in (0.5, 1.0, 1.5):
    res[name][f"react_{tr}s"] = outcome(t, y, v, a, tr)
  # time to move 1 m (comma's yardstick: their limits take 0.9 s of full push to move 1 m)
  idx = np.argmax(y >= 1.0) if np.any(y >= 1.0) else None
  res[name]["time_to_1m_s"] = round(float(t[idx]), 2) if idx is not None else None
  idx2 = np.argmax(y >= TO_LINE) if np.any(y >= TO_LINE) else None
  res[name]["time_to_lane_line_s"] = round(float(t[idx2]), 2) if idx2 is not None else None
out["wrong_way_push_70mph"] = res
out["lane"] = {"lane_m": LANE_M, "car_width_m": CAR_W, "room_to_line_when_centred_m": round(TO_LINE, 2),
               "correction": f"after reacting, the driver steers back to {CORR_A} m/s2 the other way over {CORR_RAMP} s"}

print(json.dumps(out, indent=1))
