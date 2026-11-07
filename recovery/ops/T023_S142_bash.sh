python3 - <<'EOF'
p = "params.py"
s = open(p).read()
old = '''BACKLASH = 0.175      # each gear's teeth are this much thinner than nominal (mm at the pitch circle)
ROLL_GROW = 0.15      # the rolling band and the motor gear's roller are this much bigger than the pitch circles

ROLL_PAST_TEETH = 6.5   # degrees of rolling band past the last tooth, each side (the roller spins up before the teeth meet)
END_LEAD_IN = 2.5       # degrees over which the rolling band slopes down at each end'''
new = '''BACKLASH = 0.175      # each gear's teeth are this much thinner than nominal (mm at the pitch circle)
CD_EXTRA = 0.3        # gear centres this much further apart than the pitch circles touching (a little free play)
ROLLER_R = 22.5       # motor gear's roller: bigger than its teeth (21 mm), so with the steering wheel turned past
                      # the teeth the roller, not the teeth, rests on the steering wheel

ROLL_PAST_TEETH = 6.5   # degrees of rolling band past the last tooth, each side (the roller spins up before the teeth meet)
END_LEAD_IN = 4.0       # degrees over which the rolling band slopes down at each end
END_CHAMFER = 3.5       # mm: the very end slopes from the outer band down to the steering wheel'''
assert old in s; s = s.replace(old, new)
old = '''# Along the steering column (z), the bands the two gears share
Z_ROLL = (-7.0, -1.65)        # rolling band on the steering wheel teeth
Z_TEETH = (1.0, 13.0)         # teeth on the steering wheel teeth
Z_MOTOR_FACE = -13.5          # front face of the motor (where the shaft comes out)
MOTOR_PLATE_T = 5.0           # motor bracket plate, between the motor and the motor gear
Z_GEAR_ROLLER = (-8.0, 0.5)   # motor gear: roller
Z_GEAR_TEETH = (1.25, 12.5)   # motor gear: teeth'''
new = '''# Along the steering column (z), the bands the two gears share. The roller is centred on the part you hold.
Z_ROLL = (-3.5, 4.5)          # rolling band on the steering wheel teeth
Z_TEETH = (5.5, 17.5)         # teeth on the steering wheel teeth
Z_MOTOR_FACE = -9.5           # front face of the motor (where the shaft comes out)
MOTOR_PLATE_T = 5.0           # motor bracket plate, between the motor and the motor gear
Z_GEAR_ROLLER = (-4.0, 4.0)   # motor gear: roller
Z_GEAR_TEETH = (5.75, 17.0)   # motor gear: teeth'''
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)

p = "wheelparts.py"
s = open(p).read()
s = s.replace('''from params import (BACKLASH, END_LEAD_IN, GRIP, M3_PILOT, MOTOR_TEETH, PAD, RING_TEETH, ROLL_GROW, ROLL_PAST_TEETH,
                    SHAFT_ACROSS_FLAT, SHAFT_D, SHAFT_FLAT_LEN, SHAFT_LEN, SPLIT_LAP, TEETH_ON_WHEEL, TIE_ANGLES, TIE_T,
                    TIE_W, WALL, WHEEL_OD, Z_GEAR_ROLLER, Z_GEAR_TEETH, Z_MOTOR_FACE, Z_ROLL, Z_TEETH)''',
'''from params import (BACKLASH, CD_EXTRA, END_CHAMFER, END_LEAD_IN, GRIP, M3_PILOT, MOTOR_TEETH, PAD, RING_TEETH, ROLL_PAST_TEETH,
                    ROLLER_R, SHAFT_ACROSS_FLAT, SHAFT_D, SHAFT_FLAT_LEN, SHAFT_LEN, SPLIT_LAP, TEETH_ON_WHEEL, TIE_ANGLES,
                    TIE_T, TIE_W, WALL, WHEEL_OD, Z_GEAR_ROLLER, Z_GEAR_TEETH, Z_MOTOR_FACE, Z_ROLL, Z_TEETH)


def centre_distance() -> float:
  """Steering column to the motor's axis with the motor gear on the teeth."""
  return pitch_radius(RING_TEETH) + pitch_radius(MOTOR_TEETH) + CD_EXTRA''')
old = '''    self.r_roll = self.rp + ROLL_GROW
    self.r_base = self.r_in + WALL                     # outer band where it carries no teeth or rolling band
    self.pitch_deg = 360.0 / RING_TEETH
    self.teeth_half = TEETH_ON_WHEEL / 2 * self.pitch_deg
    self.roll_half = self.teeth_half + ROLL_PAST_TEETH
    self.half = self.roll_half + END_LEAD_IN'''
new = '''    self.r_roll = centre_distance() - ROLLER_R         # rolling band: the motor gear's roller rides on it
    self.r_base = self.r_in + WALL                     # outer band where it carries no teeth or rolling band
    self.pitch_deg = 360.0 / RING_TEETH
    self.teeth_half = TEETH_ON_WHEEL / 2 * self.pitch_deg
    self.roll_half = self.teeth_half + ROLL_PAST_TEETH
    self.chamfer_deg = math.degrees(END_CHAMFER / self.r_base)
    self.half = self.roll_half + END_LEAD_IN + self.chamfer_deg'''
assert old in s; s = s.replace(old, new)
old = '''    if self.r_root - self.r_base < 2.0:
      raise ValueError(f"a steering wheel {wheel_od} mm across leaves no room under {RING_TEETH} teeth")
    if self.r_split + 1.0 > self.r_roll - (self.wz_out - Z_TEETH[1]):
      raise ValueError("no room for the overlap between the two halves")'''
new = '''    if self.r_roll - self.r_base < 2.0:
      raise ValueError(f"a steering wheel {wheel_od} mm across leaves no room under {RING_TEETH} teeth")
    if self.r_split + 1.0 > self.r_base:
      raise ValueError("no room for the overlap between the two halves")'''
assert old in s; s = s.replace(old, new)
start = s.index("  def profile(self, roll_r: float):")
end = s.index("def teeth_outline(")
new = '''  def profile(self, outer_r: float | None = None):
    """(r, z) outline of the piece at one angle. outer_r: cap on the outer radius (the end slopes); None: none."""
    zf, zk = self.wz_out, -self.wz_out
    zr0, zr1 = Z_ROLL
    zt0, zt1 = Z_TEETH
    pts = [
      (self.front_inner, zf),                       # front wall (driver side): inner end, outer face
      (self.front_inner, self.wz),                  # front wall inner face
      (self.r_in, self.wz),                         # channel: the part you hold sits here
      (self.r_in, self.z_slope_top),
      (self.back_inner, zk),                        # back wall: 45 degree slope down to its outer face
      (self.r_base, zk),
      (self.r_base, zr0),                           # up the back of the outer band
      (self.r_roll, zr0),                           # rolling band (the motor gear's roller rides here)
      (self.r_roll, zr1),
      (self.r_root, zr1),                           # step up to the teeth's root
      (self.r_root, zt1),
      (self.r_tip, zt1),                            # under the teeth's front ends
      (self.r_tip - (zf - zt1), zf),                # 45 degree slope to the front face
    ]
    return pts

  def outer_radius_at(self, angle_from_top: float) -> float:
    """Plan-view cap on the outer radius: none over the teeth and rolling band, then the rolling band slopes down
    to the outer band, and the very end slopes down to the steering wheel."""
    a = abs(angle_from_top)
    if a <= self.roll_half:
      return self.r_tip + 2.0
    if a <= self.roll_half + END_LEAD_IN:
      f = (a - self.roll_half) / END_LEAD_IN
      return self.r_roll - f * (self.r_roll - self.r_base)
    f = min(1.0, (a - self.roll_half - END_LEAD_IN) / self.chamfer_deg)
    return self.r_base - f * (self.r_base - self.r_in)


'''
s = s[:start] + new + s[end:]
old = '''  a0, a1 = 90.0 - t.half, 90.0 + t.half
  body = revolve(t.profile(t.r_roll), a0, a1)
  # plan-view mask: the rolling band and its slopes at full height over the middle, lowered at the ends
  mask = polar_mask(lambda a: t.roll_radius_at(a - 90.0) + 0.01, a0, a1, -t.wz_out - 1, t.wz_out + 1)
  body = body ^ (mask + cyl(t.r_base, -t.wz_out - 1, t.wz_out + 1, segments=1440))'''
new = '''  a0, a1 = 90.0 - t.half, 90.0 + t.half
  body = revolve(t.profile(), a0, a1)
  # plan view: full height over the middle; at each end the rolling band slopes down, then the end slopes to the wheel
  mask = polar_mask(lambda a: t.outer_radius_at(a - 90.0), a0, a1, -t.wz_out - 1, t.wz_out + 1)
  body = body ^ mask'''
assert old in s; s = s.replace(old, new)
old = '''  a0, a1 = 90.0 - span_deg / 2, 90.0 + span_deg / 2
  body = revolve(t.profile(t.r_base), a0, a1)
  return clean(body - tie_slots(t, [90.0]))'''
new = '''  a0, a1 = 90.0 - span_deg / 2, 90.0 + span_deg / 2
  body = revolve(t.profile(), a0, a1) ^ box(-400, 400, -400, 400, -100, 100) ^ \\
    cyl(t.r_base, -t.wz_out - 1, t.wz_out + 1, segments=1440)
  return clean(body - tie_slots(t, [90.0]))'''
assert old in s; s = s.replace(old, new)
old = '''  pts = [(r0, zf), (r0, zk), (t.r_roll, zk), (t.r_roll, Z_ROLL[1]), (t.r_root, Z_TEETH[0]), (t.r_root, Z_TEETH[1]),
         (t.r_roll, Z_TEETH[1]), (t.r_roll - 3.0, zf)]'''
new = '''  pts = [(r0, zf), (r0, zk), (t.r_roll, zk), (t.r_roll, Z_ROLL[1]), (t.r_root, Z_ROLL[1]), (t.r_root, Z_TEETH[1]),
         (t.r_tip, Z_TEETH[1]), (t.r_tip - 3.0, zf)]'''
assert old in s; s = s.replace(old, new)
s = s.replace('''  roller = cyl(rp + ROLL_GROW, zr0, zr1, segments=360)
  core = cyl(rf, zr1 - 0.01, zt0 + 0.01, segments=180)
  # turn the gear''', '''  roller = cyl(ROLLER_R, zr0, zr1, segments=360)
  core = cyl(rf, zr1 - 0.01, zt0 + 0.01, segments=180)
  # turn the gear''')
open(p, "w").write(s)
EOF
grep -n "ROLL_GROW\|roll_radius_at\|profile(t.r" wheelparts.py assembly.py mountparts.py | head