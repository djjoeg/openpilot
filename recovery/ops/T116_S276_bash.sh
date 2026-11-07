python3 - <<'EOF'
p='faceparts.py'
s=open(p).read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:60], s.count(old))
    s = s.replace(old, new)

rep('''N_TEETH = 42                      # teeth printed: 21 each side of 3 o'clock, reaching 45.5 degrees each way''',
'''N_TEETH = 42                      # the long back teeth: 21 each side of 3 o'clock, reaching 45.5 degrees each way
N_TEETH_SHORT = 14                # the short back teeth: 7 each side, reaching 15.2 degrees each way (the other mounts' short
                                  # teeth reach 14.6): the set for the highway, in one piece from about 2 to 4 o'clock''')
rep('''JOINT_TEETH = 4                   # the two pieces meet at the tooth space this many teeth above 3 o'clock''',
'''JOINT_TEETH = 4                   # the long set's two pieces meet at the tooth space this many teeth above 3 o'clock''')
rep('''  def __init__(self, wheel_od: float = WHEEL_OD, grip: float = GRIP, spoke_deg: tuple = RIGHT_SPOKE_DEG):
    self.wheel_od, self.grip = wheel_od, grip''',
'''  def __init__(self, wheel_od: float = WHEEL_OD, grip: float = GRIP, spoke_deg: tuple = RIGHT_SPOKE_DEG, n_teeth: int = N_TEETH):
    self.wheel_od, self.grip, self.n_teeth = wheel_od, grip, n_teeth''')
rep('''    self.teeth_half = N_TEETH / 2 * self.pitch_deg''', '''    self.teeth_half = n_teeth / 2 * self.pitch_deg''')
rep('''    self.joint_deg = JOINT_TEETH * self.pitch_deg''',
'''    # two pieces glued end to end when one would not fit a 220 mm print bed (the long set); the short set is one piece
    self.joint_deg = JOINT_TEETH * self.pitch_deg if self.half > 40.0 else None''')
rep('''  p = t.pitch_deg
  n = N_TEETH // 2
  r0, r1 = CUT_SPAN''', '''  p = t.pitch_deg
  n = t.n_teeth // 2
  r0, r1 = CUT_SPAN''')
rep('''      if t.spoke[0] - w < s < t.spoke[1] + w or abs(s - t.joint_deg) < w + 1.0:''',
'''      if t.spoke[0] - w < s < t.spoke[1] + w or (t.joint_deg is not None and abs(s - t.joint_deg) < w + 1.0):''')
rep('''  body = revolve(t.profile(), -t.half, t.half, step_deg=0.25)
  n = N_TEETH // 2''', '''  body = revolve(t.profile(), -t.half, t.half, step_deg=0.25)
  n = t.n_teeth // 2''')
rep('''def face_pieces(t: FaceTeeth, whole: Manifold | None = None) -> dict:
  """The back teeth: the upper piece (from the joint up), the lower piece (from the joint down) and the one piece."""
  whole = whole if whole is not None else face_solid(t)
  slots = tie_slots(t)''', '''def face_pieces(t: FaceTeeth, whole: Manifold | None = None) -> dict:
  """The back teeth: the upper piece (from the joint up), the lower piece (from the joint down) and the one piece; the
  one piece only for a set without a joint."""
  whole = whole if whole is not None else face_solid(t)
  slots = tie_slots(t)
  if t.joint_deg is None:
    return {"one-piece": clean(whole - slots)}''')
open(p,'w').write(s)

p='faceassembly.py'
s=open(p).read()
rep('''  for w in (0.0, 0.5 * t.pitch_deg, 10.0 * t.pitch_deg, -15.0 * t.pitch_deg):''',
'''  inner = t.n_teeth // 2 - 3            # stay clear of the lowered end teeth
  for w in (0.0, 0.5 * t.pitch_deg, min(10, inner) * t.pitch_deg, -min(15, inner) * t.pitch_deg):''')
open(p,'w').write(s)
EOF
grep -n "N_TEETH" faceparts.py faceassembly.py margins.py accord_lka_parts.py | head