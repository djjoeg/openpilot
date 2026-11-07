python3 - <<'EOF'
p='rightarm.py'; s=open(p).read()
rep = [
# docstring
('''The right arm mount (1 Nov 2026, from your note; v3 2 Nov 2026): the motor sits OUTSIDE the steering wheel's rim on
the right, at about 4 o'clock, its shaft pointing in at the wheel's middle, the gear on the teeth from outside.

v3 is two printed pieces and two slides:''',
'''The right arm mount (1 Nov 2026, from your note; v3 2 Nov 2026; v4 3 Nov 2026): the motor sits OUTSIDE the steering
wheel's rim on the right, at about 4 o'clock, its shaft pointing in at the wheel's middle, the gear on the teeth from
outside.

v4 (3 Nov, from the v3 print in your hand): the tower's channel is closed into a square tube, so the motor carrier
can't come out of it; the carrier's bar has no lug, so it slides into the tube from the tower's top end (off the car,
before the arm goes into the receiver); an M4 bolt screwed into the bar's end below the tower, a fender washer under
its head, is the stop (and what keeps the carrier in), locked with a jam nut. And the gear moved 4 degrees up the
rim, to the middle of the gap between the spokes (measured on photos of the same wheel: 6 to 46 degrees below
3 o'clock), so the 20 teeth fit between them.

v3 was two printed pieces and two slides:'''),
('''THETA = -30.0                    # where the gear meets the teeth: 4 o'clock (your note: the column's underside height
                                 # would be -40; a tangent 20 degrees off upright would be -20)''',
'''THETA = -26.0                    # where the gear meets the teeth: the middle of the gap between the spoke joins on the
                                 # back of the grip (-6 to -46, measured 3 Nov on photos of the same wheel), 4 degrees
                                 # above 4 o'clock (your note: the column's underside height would be -40; a tangent 20
                                 # degrees off upright would be -20; v3 had -30)'''),
('''BAR_U, BAR_V = (205.0, 221.0), (-39.0, -23.0)    # the carrier's bar, 16 x 16, beside the motor on its 5 o'clock side
CH_U, CH_V0 = (204.75, 221.25), -39.25           # the tower's channel round it, open towards the motor (+v)
TOWER_U, TOWER_V = (194.75, 231.25), (-47.25, -24.0)   # the inner wall 10 (the stop lands on it), the outer wall 10
                                                 # (the push bolt's nut), the back 8; the walls end 1 mm short of the
                                                 # bar's face, clear of the motor's board''',
'''BAR_U, BAR_V = (205.0, 221.0), (-39.0, -23.0)    # the carrier's bar, 16 x 16, beside the motor on its 5 o'clock side
CH_U, CH_V0 = (204.75, 221.25), -39.25           # the tower's square tube round it
CH_V1 = BAR_V[1] + 0.3                           # v4: its fourth wall, on the motor's side (0.3 clear of the bar)
COVER_T = 5.0                                    # that wall's thickness
TOWER_U, TOWER_V = (194.75, 231.25), (-47.25, CH_V1 + COVER_T)   # the inner wall 10, the outer wall 10 (the push
                                                 # bolt's nut), the back 8, the cover 5 (below the motor and its board,
                                                 # which stay above the tower's top)
BORE_CHAMFER = 0.8               # the tube's two mouths: 45 degrees, so the bar goes in and the first layers don't pinch it'''),
('''STOP_UV = (199.5, -31.0)         # the stop wing bolt: up through the lug, onto the inner wall's underside
STOP_P = 5.5                     # it pokes this far above the lug at the nominal depth (1.5 to 9.5: +-4 mm)
LUG_U, LUG_T = (192.5, 205.0), 6.0
DZ_DEEP, DZ_SHALLOW = 4.0, -4.0  # the stop's range''',
'''# v4's stop: an M4 bolt along the bar's middle into its bottom end, a captive nut in a slot 4 mm in, a fender washer
# under the bolt's head (wider than the tube, it lands on the tower's bottom face), a jam nut on the bolt against the
# bar's end. STOP_GAP: from the washer's top to the bar's end; at the nominal depth 8 (4 to 12: +-4 mm)
BAR_UV = ((BAR_U[0] + BAR_U[1]) / 2, (BAR_V[0] + BAR_V[1]) / 2)    # (213, -31): the bar's middle line
STOP_GAP = 8.0
M4_HOLE = 4.5
M4_NUT_AF, M4_NUT_T = 7.0, 3.2
M4_SLOT = (M4_NUT_AF / math.cos(math.radians(30)) + 0.4, M4_NUT_T + 0.4)   # across (corners), along the bar
M4_SLOT_IN = 4.0                 # the bar's end wall before the slot
M4_DEPTH = 27.0                  # the hole up the bar from its end (an M4 x 30 goes up to 24.4 in at the shortest stop)
WASHER_OD, WASHER_T = 24.0, 1.6  # a #8 or M4 fender washer; anything over 17 mm across lands on the tower
DZ_DEEP, DZ_SHALLOW = 4.0, -4.0  # the stop's range'''),
('''WEB_Z0 = PLATE_Z[0] - 3.0        # the web's underside, below the motor's and the board's: it lands on the tower first
BAR_Z = (TOWER_Z[0] - STOP_P - LUG_T, PLATE_Z[1])      # (-186.7, -38.35) at the nominal depth''',
'''WEB_Z0 = PLATE_Z[0] - 3.0        # the web's underside, below the motor's and the board's: it lands on the tower first
BAR_Z = (TOWER_Z[0] + STOP_GAP, PLATE_Z[1])     # (-167.2, -38.35) at the nominal depth: the end is up in the tube'''),
]
for a,b in rep:
  assert a in s, a[:70]
  s = s.replace(a,b)
open(p,'w').write(s)
EOF
grep -n "^v3 is\|^v3 was" -A 14 rightarm.py | head -20