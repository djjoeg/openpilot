python3 - <<'EOF'
import pathlib
p = pathlib.Path("sideparts.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)
rep("""def side_teeth(t: SideTeeth = None) -> Manifold:
  t = t or SideTeeth()
  return clean(side_teeth_solid(t) - FP.tie_slots(t, SP.slide_tie_angles(t)))""",
    """# the set's number (its reach in degrees, the car setup's answer) cut 0.6 mm into the channel's outer wall, just past
# the middle towards 4 o'clock (over the lower bar's junction, where no zip tie goes): 3 x 5 pixel digits, 2 mm pixels
DIGITS = {"0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111", "4": "101101111001001",
          "5": "111100111001111", "6": "111100111101111", "7": "111001001001001", "8": "111101111101111", "9": "111101111001111"}
MARK_PX, MARK_DEPTH, MARK_Z0, MARK_DEG0 = 2.0, 0.6, -29.0, 3.0


def number_mark(t: "SideTeeth") -> Manifold:
  \"\"\"The digits of the set's reach, cut into the outer wall: read from outside the steering wheel, the piece on the car
  (the front edge up, 4 o'clock to the left).\"\"\"
  text = str(round(t.teeth_half))
  cuts = []
  a = MARK_DEG0
  for ch in text:
    px = DIGITS[ch]
    for row in range(5):
      for col in range(3):
        if px[row * 3 + col] == "1":
          a0 = a + col * math.degrees(MARK_PX / t.w_out)
          a1 = a0 + math.degrees(MARK_PX / t.w_out)
          z1 = MARK_Z0 + (5 - row) * MARK_PX
          cuts.append(FP.polar_box(t.w_out - MARK_DEPTH, t.w_out + 1.0, a0, a1, z1 - MARK_PX, z1, step_deg=0.3))
    a += 4 * math.degrees(MARK_PX / t.w_out)
  return union(cuts)


def side_teeth(t: SideTeeth = None) -> Manifold:
  t = t or SideTeeth()
  return clean(side_teeth_solid(t) - FP.tie_slots(t, SP.slide_tie_angles(t)) - number_mark(t))""")
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import numpy as np, math
import sideparts as S, faceparts as FP
t = S.SideTeeth(n_teeth=10)
m = S.number_mark(t)
print("mark bbox", np.round(m.bounding_box(),1).tolist(), "pieces", len(m.decompose()))
# render the outer wall region as seen from outside: project the mark's angular/z layout
print("digits", str(round(t.teeth_half)), "span deg", round(2 * 4 * math.degrees(2.0 / t.w_out), 2))
EOF