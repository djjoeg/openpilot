cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
s = open('params.py').read()
old = '''RING_TEETH = 197      # tooth count of the full circle the steering wheel teeth are cut from (197 mm pitch radius)
MOTOR_TEETH = 19      # motor gear: 38 mm pitch circle
TEETH_ON_WHEEL = 32   # teeth actually printed, centred on 12 o'clock: 58.5 degrees of steering wheel turn'''
new = '''RING_TEETH = 197      # tooth count of the full circle the steering wheel teeth are cut from (197 mm pitch radius)
MOTOR_TEETH = 19      # motor gear: 38 mm pitch circle
# Two sets of steering wheel teeth, named by how far they reach each way from straight ahead (degrees of steering wheel
# turn): the teeth printed, centred on 12 o'clock, and the zip tie positions each side of 12 o'clock. The motor can't
# turn the steering wheel further than its teeth reach, so the short set is for getting used to lane keeping.
TEETH_SETS = {
  15: {"teeth": 16, "ties": (9.5, 16.5, 23.5)},   # 29.2 degrees of steering wheel turn
  29: {"teeth": 32, "ties": (9.5, 20.5, 31.0)},   # 58.5 degrees
}
TEETH_ON_WHEEL = TEETH_SETS[29]["teeth"]'''
assert old in s
s = s.replace(old, new)
old = '''SPLIT_LAP = 3           # the two halves overlap this many teeth at 12 o'clock (glued)
TIE_ANGLES = (9.5, 20.5, 31.0)   # zip tie positions each side of 12 o'clock
TIE_W, TIE_T = 5.8, 2.4          # zip tie slot, for ties 4.8 mm wide'''
new = '''SPLIT_LAP = 3           # the two halves overlap this many teeth at 12 o'clock (glued)
TIE_W, TIE_T = 5.8, 2.4          # zip tie slot, for ties 4.8 mm wide'''
assert old in s
s = s.replace(old, new)
open('params.py', 'w').write(s)

w = open('wheelparts.py').read()
w = w.replace('''from params import (BACKLASH, CD_EXTRA, END_CHAMFER, END_LEAD_IN, GRIP, M3_PILOT, MOTOR_TEETH, PAD, RING_TEETH, ROLL_PAST_TEETH,
                    ROLLER_R, SHAFT_ACROSS_FLAT, SHAFT_D, SHAFT_FLAT_LEN, SHAFT_LEN, SPLIT_LAP, TEETH_ON_WHEEL, TIE_ANGLES,
                    TIE_T, TIE_W, WALL, WHEEL_OD, Z_GEAR_ROLLER, Z_GEAR_TEETH, Z_MOTOR_FACE, Z_ROLL, Z_TEETH)''',
'''from params import (BACKLASH, CD_EXTRA, END_CHAMFER, END_LEAD_IN, GRIP, M3_PILOT, MOTOR_TEETH, PAD, RING_TEETH, ROLL_PAST_TEETH,
                    ROLLER_R, SHAFT_ACROSS_FLAT, SHAFT_D, SHAFT_FLAT_LEN, SHAFT_LEN, SPLIT_LAP, TEETH_SETS, TIE_T, TIE_W,
                    WALL, WHEEL_OD, Z_GEAR_ROLLER, Z_GEAR_TEETH, Z_MOTOR_FACE, Z_ROLL, Z_TEETH)''')
old = '''class Teeth:
  """Radii and angles of the steering wheel teeth for one steering wheel size."""

  def __init__(self, wheel_od: float = WHEEL_OD, grip: float = GRIP):
    self.wheel_od, self.grip = wheel_od, grip'''
new = '''class Teeth:
  """Radii and angles of the steering wheel teeth for one steering wheel size and one teeth set (TEETH_SETS: 15 or 29,
  how far they reach each way)."""

  def __init__(self, wheel_od: float = WHEEL_OD, grip: float = GRIP, reach: int = 29):
    self.wheel_od, self.grip = wheel_od, grip
    self.reach = reach
    self.n_teeth = TEETH_SETS[reach]["teeth"]
    self.tie_angles = TEETH_SETS[reach]["ties"]'''
assert old in w
w = w.replace(old, new)
old = '''    self.teeth_half = TEETH_ON_WHEEL / 2 * self.pitch_deg'''
new = '''    self.teeth_half = self.n_teeth / 2 * self.pitch_deg'''
assert old in w
w = w.replace(old, new)
old = '''    if self.r_split + 1.0 > self.r_base:
      raise ValueError("no room for the overlap between the two halves")'''
new = '''    if self.r_split + 1.0 > self.r_base:
      raise ValueError("no room for the overlap between the two halves")
    if max(self.tie_angles) + TIE_W / 2 / self.r_in * 57.3 > self.half - 1.0:
      raise ValueError("a zip tie slot runs off the end of the steering wheel teeth")'''
assert old in w
w = w.replace(old, new)
old = '''  n_teeth = n_teeth or TEETH_ON_WHEEL'''
new = '''  n_teeth = n_teeth or t.n_teeth'''
assert old in w
w = w.replace(old, new)
w = w.replace('''    angles = [90.0 - a for a in TIE_ANGLES]
  else:''', '''    angles = [90.0 - a for a in t.tie_angles]
  else:''')
w = w.replace('''    angles = [90.0 + a for a in TIE_ANGLES]
  return clean(part - tie_slots(t, angles))''', '''    angles = [90.0 + a for a in t.tie_angles]
  return clean(part - tie_slots(t, angles))''')
w = w.replace('''  return clean(whole - tie_slots(t, [90.0 + a for a in TIE_ANGLES] + [90.0 - a for a in TIE_ANGLES]))''',
'''  return clean(whole - tie_slots(t, [90.0 + a for a in t.tie_angles] + [90.0 - a for a in t.tie_angles]))''')
open('wheelparts.py', 'w').write(w)
EOF
grep -n "TIE_ANGLES\|TEETH_ON_WHEEL" *.py