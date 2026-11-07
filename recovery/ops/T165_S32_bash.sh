python3 - <<'EOF'
import re
p = "sideparts.py"
s = open(p).read()
def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:80], s.count(old))
    s = s.replace(old, new)

sub('''teeth. A lever on the motor's bracket sticks out through an L-shaped slot in the mounting plate (where the latch's knob
was). Pull the lever out along the slot and the motor slides out onto the teeth; swing it into the notch at the slot's
outer end, towards the dash, and it is latched. Swing it out of the notch and the spring pulls the motor in; if the
spring doesn't, push the lever in along the slot. A second notch at the slot's inner end parks it there.''',
'''teeth. A lever on the motor's bracket sticks out through an L-shaped slot in the mounting plate (where the latch's knob
was). Pull the lever out along the slot and the motor slides out onto the teeth; at the slot's outer end, pull it
towards you into the notch and it is latched. Push it away from you, out of the notch, and the spring pulls the motor in;
if the spring doesn't, push the lever in along the slot. A second notch at the slot's inner end parks it there.''')
sub('''# ***** the lever: on a pin across the bracket's ear, out through an L-shaped slot in the plate *****
# Its arm leaves the ear towards 4 o'clock, through the slot to a knob outside the plate. Pulled out against the stop it
# swings LATCH_DEG towards the dash into the notch at the slot's outer end; the spring then pulls its arm down onto the
# notch's floor, which sets where the motor sits on the teeth. Swung out of the notch, it runs in the straight slot with
# the motor. The notch at the inner end takes it the same way, slid in, so the motor stays in without the spring.''',
'''# ***** the lever: on a pin across the bracket's ear, out through an L-shaped slot in the plate *****
# Its arm leaves the ear towards 4 o'clock, through the plate to a knob outside it. It runs along the slot swung SLOT_DEG
# towards the dash. Pulled out against the stop, it swings back towards you, straight out, into the notch at the slot's
# outer end; the spring then pulls its arm onto the notch's floor, which sets where the motor sits on the teeth. So the
# knob is nearest you when latched. The notch at the inner end takes it the same way, slid in, so the motor stays in
# without the spring. Drawn here as latched: motor out, the lever straight out.''')
sub('''LATCH_DEG = 42.0                  # swung this far into a notch''', '''SLOT_DEG = 42.0                   # in the slot the lever is swung this far towards the dash; in a notch, straight out''')
sub('''  """The lever's hub and arm (no knob) as fitted, motor out, out of the notch; grown by `clear` across and round, and
  by `z_clear` along the shaft."""''', '''  """The lever's hub and arm (no knob) as fitted, motor out, latched; grown by `clear` across and round, and by
  `z_clear` along the shaft."""''')
sub('''  """Carrier frame, motor out, out of the notch: the hub on the pin, the arm out towards 4 o'clock, the knob."""''',
    '''  """Carrier frame, motor out, latched: the hub on the pin, the arm straight out towards 4 o'clock, the knob."""''')
sub('''  """Everywhere `m` (drawn with the lever) goes swinging into a notch, slid in anywhere in s_range."""
  angles = np.linspace(0.0, LATCH_DEG, steps)''', '''  """Everywhere `m` (drawn with the lever) goes swinging between the slot and a notch, slid in anywhere in s_range."""
  angles = np.linspace(0.0, SLOT_DEG, steps)''')
sub('''  """The lever's hub and arm swinging into either notch (the bracket's room for them, with the bracket's own s): out to
  the lugs' faces along the shaft, so no sliver of the bridge is left between them."""''', '''  """The lever's hub and arm swinging between the slot and either notch (the bracket's room for them, with the
  bracket's own s): out to the lugs' faces along the shaft, so no sliver of the bridge is left between them."""''')
sub('''  """The plate's slot and notches: the arm in the slot from pulled out against the stop to slid in on the bumper, and
  swung into each notch. The notches' load faces are exactly where the arm rests on them: the outer notch's floor where
  the spring pulls it (motor fully out), the inner notch's outer face where the motor's weight pulls it (slid in)."""
  arm = lever_room(SLOT_CLEAR)
  straight = Manifold.batch_hull([lever_at(arm, s) for s in (-0.6, STROKE + 0.6)])''',
'''  """The plate's slot and notches: the arm in the slot (swung SLOT_DEG) from pulled out against the stop to slid in on
  the bumper, and swung back into each notch. The notches' load faces are exactly where the arm rests on them: the outer
  notch's floor where the spring pulls it (motor fully out), the inner notch's outer face where the motor's weight pulls
  it (slid in)."""
  arm = lever_room(SLOT_CLEAR)
  straight = Manifold.batch_hull([lever_at(arm, s, SLOT_DEG) for s in (-0.6, STROKE + 0.6)])''')
open(p, "w").write(s)

p = "sideassembly.py"
s = open(p).read()
sub('''  - the lever swings into either notch without touching anything, and once in a notch the plate holds it: latched, the
    motor can't slide in; parked, it can't slide out''', '''  - the lever swings between its slot and either notch without touching anything, and once in a notch the plate holds
    it: latched, the motor can't slide in; parked, it can't slide out''')
sub('''  def movers(self, s: float, wheel_deg: float = 0.0, lever_deg: float = 0.0) -> dict:
    """The moving parts, slid in s; the lever swung lever_deg towards the dash (into a notch)."""''',
    '''  def movers(self, s: float, wheel_deg: float = 0.0, lever_deg: float = S.SLOT_DEG) -> dict:
    """The moving parts, slid in s; the lever swung lever_deg towards the dash (S.SLOT_DEG: in its slot, 0: in a notch,
    latched or parked)."""''')
sub('''  """Moving against fixed parts at every slide position (carrier frame), the lever out of its notches. Only the expected''',
    '''  """Moving against fixed parts at every slide position (carrier frame), the lever in its slot. Only the expected''')
sub('''  for deg in np.arange(0.0, S.LATCH_DEG + 0.01, 3.0):''', '''  for deg in np.arange(0.0, S.SLOT_DEG + 0.01, 3.0):''')
sub('''def lever_notches(A: SideAssembly, step: float = 3.0) -> dict:
  """The lever swinging into each notch: against every fixed part, at the two ends of the slide it can be at there
  (latched: from resting on the notch's floor to pulled out against the stop; parked: from resting on the notch's
  outer face to on the bumper). Then what the notches hold: latched and pushed in 0.3 mm, or parked and pulled out 0.3,
  the plate stops the lever (an overlap means it can't go there); swung fully out of the notch, it slides freely."""''',
'''def lever_notches(A: SideAssembly, step: float = 3.0) -> dict:
  """The lever swinging between its slot and each notch: against every fixed part, at the two ends of the slide it can
  be at there (latched: from resting on the notch's floor to pulled out against the stop; parked: from resting on the
  notch's outer face to on the bumper). Then what the notches hold: latched and pushed in 0.3 mm, or parked and pulled
  out 0.3, the plate stops the lever (an overlap means it can't go there); swung into the slot, it slides freely."""''')
sub('''    for deg in np.arange(0.0, S.LATCH_DEG + 0.01, step):''', '''    for deg in np.arange(0.0, S.SLOT_DEG + 0.01, step):''')
sub('''    overlap(S.lever_at(lv, 0.3, S.LATCH_DEG), plate), 2)
  out["parked, pulled out 0.3 mm: the plate stops it (mm3)"] = round(overlap(S.lever_at(lv, S.STROKE - 0.3, S.LATCH_DEG), plate), 2)
  out["swung out of the notch, it slides: worst overlap with the plate (mm3)"] = round(
    max(overlap(S.lever_at(lv, float(s)), plate) for s in np.arange(-S.STOP_GAP, S.STROKE + 0.21, 0.5)), 4)
  out["latched, resting on the notch's floor: gap (mm)"] = round(S.lever_at(lv, 0.0, S.LATCH_DEG).min_gap(plate, 2.0), 3)''',
'''    overlap(S.lever_at(lv, 0.3), plate), 2)
  out["parked, pulled out 0.3 mm: the plate stops it (mm3)"] = round(overlap(S.lever_at(lv, S.STROKE - 0.3), plate), 2)
  out["swung into the slot, it slides: worst overlap with the plate (mm3)"] = round(
    max(overlap(S.lever_at(lv, float(s), S.SLOT_DEG), plate) for s in np.arange(-S.STOP_GAP, S.STROKE + 0.21, 0.5)), 4)
  out["latched, resting on the notch's floor: gap (mm)"] = round(S.lever_at(lv, 0.0).min_gap(plate, 2.0), 3)''')
sub('''  for s, deg, tag in ((0.0, S.LATCH_DEG, "latched"), (S.STROKE, 0.0, "slid in")):''',
    '''  for s, deg, tag in ((0.0, 0.0, "latched"), (S.STROKE, S.SLOT_DEG, "slid in")):''')
open(p, "w").write(s)
EOF
grep -n "LATCH_DEG" sideparts.py sideassembly.py sidebuild.py; /home/claude/bin/ruff check --isolated --select E4,E7,E9,F --line-length 140 sideparts.py sideassembly.py && PYTHONPATH=/home/claude/pylib timeout 900 python3 - <<'EOF'
import json
import sideassembly as SA
import sideparts as S
A = SA.SideAssembly()
print(json.dumps(SA.lever_notches(A), indent=1, default=str))
r = SA.internal(A)
print("internal over 0.001:", {k: v for k, v in r.items() if v[0] > 1e-3})
print(SA.touching_at_stops(A))
lv = A.p["lever"]
for deg in (0, 42):
  print("knob bbox at", deg, [round(v, 1) for v in S.lever_at(lv, 0, deg).bounding_box()])
EOF