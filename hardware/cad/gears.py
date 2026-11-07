"""
Spur gear geometry for the steering wheel teeth and the motor gear: involute tooth outlines, and the checks that
the two mesh (no overlap through a sweep of the steering wheel, free play, and how deep they engage).

All lengths in millimetres, angles in degrees unless a name says otherwise.
"""
import math

import numpy as np
from manifold3d import CrossSection

MODULE = 2.0             # tooth size: pitch circle diameter / number of teeth
PRESSURE_ANGLE = 20.0    # the standard
ADDENDUM = 1.0           # tooth tip above the pitch circle, in modules
DEDENDUM = 1.25          # tooth root below the pitch circle, in modules


def pitch_radius(teeth: int) -> float:
  return MODULE * teeth / 2.0


def involute(a: float) -> float:
  return math.tan(a) - a


def gear_outline(teeth: int, backlash: float, tip_radius_by_tooth: dict | None = None,
                 flank_points: int = 16, addendum: float = ADDENDUM, dedendum: float = DEDENDUM) -> CrossSection:
  """External involute spur gear outline, tooth 0 centred on +X.

  backlash: how much thinner than nominal this gear's teeth are at the pitch circle (mm of arc).
  tip_radius_by_tooth: tooth index -> tip radius, to make chosen teeth shorter.
  addendum, dedendum: tooth tip above and root below the pitch circle, in modules.
  Below the base circle (gears with fewer than about 42 teeth) the flank continues as a radial line to the root."""
  alpha = math.radians(PRESSURE_ANGLE)
  rp = pitch_radius(teeth)
  rb = rp * math.cos(alpha)
  ra = rp + addendum * MODULE
  rf = rp - dedendum * MODULE
  thickness = math.pi * MODULE / 2.0 - backlash
  psi_p = thickness / (2.0 * rp)           # half the tooth's angle at the pitch circle
  pitch = 2.0 * math.pi / teeth

  def half_angle(r):
    r = max(r, rb)
    return psi_p + involute(alpha) - involute(math.acos(rb / r))

  r_flank_start = max(rf, rb)
  pts = []
  for k in range(teeth):
    c = k * pitch
    tip_r = (tip_radius_by_tooth or {}).get(k, ra)
    radii = np.linspace(r_flank_start, tip_r, flank_points)
    if rf < rb:
      pts.append((rf, c - half_angle(rb)))
    for r in radii:
      pts.append((r, c - half_angle(r)))
    for t in (-1 / 3, 1 / 3):
      pts.append((tip_r, c + t * half_angle(tip_r)))
    for r in radii[::-1]:
      pts.append((r, c + half_angle(r)))
    if rf < rb:
      pts.append((rf, c + half_angle(rb)))
    a0 = c + half_angle(r_flank_start)
    a1 = c + pitch - half_angle(r_flank_start)
    for t in np.linspace(0.0, 1.0, 5)[1:-1]:
      pts.append((rf, a0 + t * (a1 - a0)))
  return CrossSection([[(r * math.cos(a), r * math.sin(a)) for r, a in pts]])


def internal_gear_outline(teeth: int, backlash: float, r_out: float, flank_points: int = 16) -> CrossSection:
  """Internal (ring) involute gear outline, a full ring from its teeth out to r_out, tooth 0 centred on +X. Its
  teeth point inwards: tips at the pitch radius less one module, roots one and a quarter modules outside it. The
  tooth spaces are the teeth of an external gear with those radii swapped (the shape that cuts them), so a motor
  gear that meshes with the external steering wheel teeth meshes with these too.

  backlash: how much thinner than nominal the ring's teeth are at the pitch circle (mm of arc), so the cutter's
  teeth are that much thicker."""
  cutter = gear_outline(teeth, -backlash, flank_points=flank_points, addendum=DEDENDUM, dedendum=ADDENDUM)
  ring = CrossSection.circle(r_out, 4096) - CrossSection.circle(pitch_radius(teeth) - ADDENDUM * MODULE - 0.6, 4096)
  return ring - cutter


def sector(r_out: float, a0_deg: float, a1_deg: float, r_in: float = 0.0, step_deg: float = 0.25) -> CrossSection:
  """Ring sector (or pie slice when r_in is 0) from angle a0 to a1, counterclockwise."""
  n = max(2, int(math.ceil((a1_deg - a0_deg) / step_deg)) + 1)
  a = np.radians(np.linspace(a0_deg, a1_deg, n))
  outer = [(r_out * math.cos(t), r_out * math.sin(t)) for t in a]
  inner = [(r_in * math.cos(t), r_in * math.sin(t)) for t in a[::-1]] if r_in > 0 else [(0.0, 0.0)]
  return CrossSection([outer + inner])


def place(cs: CrossSection, rotate_deg: float, x: float = 0.0, y: float = 0.0) -> CrossSection:
  return cs.rotate(rotate_deg).translate((x, y))


def mesh_sweep(ring_teeth: CrossSection, ring_count: int, motor: CrossSection, motor_count: int,
               centre_distance: float, wheel_degrees: np.ndarray, motor_phase_deg: float,
               internal: bool = False) -> list[float]:
  """Overlap area (mm^2) between the steering wheel teeth and the motor gear at each steering wheel angle.

  ring_teeth is centred on the steering column (origin) with its teeth around 12 o'clock (+Y); the motor gear sits
  at (0, centre_distance) and turns the other way, ring_count / motor_count times faster. internal: the teeth are a
  ring facing the hub around 6 o'clock (-Y), the motor gear inside it at (0, -centre_distance), turning the same way."""
  ratio = ring_count / motor_count
  out = []
  for w in wheel_degrees:
    ring = ring_teeth.rotate(float(w))
    if internal:
      gear = place(motor, motor_phase_deg + float(w) * ratio, 0.0, -centre_distance)
    else:
      gear = place(motor, motor_phase_deg - float(w) * ratio, 0.0, centre_distance)
    out.append((ring ^ gear).area())
  return out


def free_play(ring_teeth: CrossSection, motor: CrossSection, centre_distance: float, motor_phase_deg: float,
              motor_count: int, step_deg: float = 0.02, limit_deg: float = 15.0) -> tuple[float, float]:
  """With the steering wheel held, how far the motor gear turns each way before it touches (degrees of the motor
  gear). Returns (counterclockwise, clockwise)."""
  res = []
  for sign in (1, -1):
    a = 0.0
    while a < limit_deg:
      gear = place(motor, motor_phase_deg + sign * (a + step_deg), 0.0, centre_distance)
      if (ring_teeth ^ gear).area() > 1e-6:
        break
      a += step_deg
    res.append(a)
  return res[0], res[1]
