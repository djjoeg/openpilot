python3 - <<'EOF'
import re
p='gears.py'; s=open(p).read()
old='''def gear_outline(teeth: int, backlash: float, tip_radius_by_tooth: dict | None = None,
                 flank_points: int = 16) -> CrossSection:
  """External involute spur gear outline, tooth 0 centred on +X.

  backlash: how much thinner than nominal this gear's teeth are at the pitch circle (mm of arc).
  tip_radius_by_tooth: tooth index -> tip radius, to make chosen teeth shorter.
  Below the base circle (gears with fewer than about 42 teeth) the flank continues as a radial line to the root."""
  alpha = math.radians(PRESSURE_ANGLE)
  rp = pitch_radius(teeth)
  rb = rp * math.cos(alpha)
  ra = rp + ADDENDUM * MODULE
  rf = rp - DEDENDUM * MODULE
'''
new='''def gear_outline(teeth: int, backlash: float, tip_radius_by_tooth: dict | None = None,
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
'''
assert old in s; s=s.replace(old,new)
old2='''def sector(r_out: float, a0_deg: float, a1_deg: float, r_in: float = 0.0, step_deg: float = 0.25) -> CrossSection:'''
new2='''def internal_gear_outline(teeth: int, backlash: float, r_out: float, flank_points: int = 16) -> CrossSection:
  """Internal (ring) involute gear outline, a full ring from its teeth out to r_out, tooth 0 centred on +X. Its
  teeth point inwards: tips at the pitch radius less one module, roots one and a quarter modules outside it. The
  tooth spaces are the teeth of an external gear with those radii swapped (the shape that cuts them), so a motor
  gear that meshes with the external steering wheel teeth meshes with these too.

  backlash: how much thinner than nominal the ring's teeth are at the pitch circle (mm of arc), so the cutter's
  teeth are that much thicker."""
  cutter = gear_outline(teeth, -backlash, flank_points=flank_points, addendum=DEDENDUM, dedendum=ADDENDUM)
  ring = CrossSection.circle(r_out, 4096) - CrossSection.circle(pitch_radius(teeth) - ADDENDUM * MODULE - 0.6, 4096)
  return ring - cutter


def sector(r_out: float, a0_deg: float, a1_deg: float, r_in: float = 0.0, step_deg: float = 0.25) -> CrossSection:'''
assert old2 in s; s=s.replace(old2,new2,1)
old3='''def mesh_sweep(ring_teeth: CrossSection, ring_count: int, motor: CrossSection, motor_count: int,
               centre_distance: float, wheel_degrees: np.ndarray, motor_phase_deg: float) -> list[float]:
  """Overlap area (mm^2) between the steering wheel teeth and the motor gear at each steering wheel angle.

  ring_teeth is centred on the steering column (origin) with its teeth around 12 o'clock (+Y); the motor gear sits
  at (0, centre_distance) and turns the other way, ring_count / motor_count times faster."""
  ratio = ring_count / motor_count
  out = []
  for w in wheel_degrees:
    ring = ring_teeth.rotate(float(w))
    gear = place(motor, motor_phase_deg - float(w) * ratio, 0.0, centre_distance)
    out.append((ring ^ gear).area())
  return out'''
new3='''def mesh_sweep(ring_teeth: CrossSection, ring_count: int, motor: CrossSection, motor_count: int,
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
  return out'''
assert old3 in s; s=s.replace(old3,new3)
open(p,'w').write(s); print("ok")
EOF