cp rightarm.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/rightarm.v4.py && cp rightcheck.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/rightcheck.v4.py && python3 - <<'EOF'
p = 'rightarm.py'
s = open(p, encoding='utf-8').read()
reps = [
# docstring: the v5 paragraph
("""v4 (3 Nov, from the v3 print in your hand): the tower's channel is closed into a square tube, so the motor carrier""",
 """v5 (3 Nov, after a stiffness check of v4, and your idea for the slide): the arm 50 mm deep along the column from
just outside the receiver to the tower, so it no longer twists under the motor's push (v4's 10 mm bar let the gear
move 1 to 2 mm in and out of the teeth); and the slide is one wing bolt in a groove up the tower's outer wall,
screwed into a nut in the carrier's bar: loosen it, slide the motor up into the teeth or down out of them, tighten.
It is the lock, the depth setting and the on and off; the groove's ends keep the carrier in. No M4 stop any more.

v4 (3 Nov, from the v3 print in your hand): the tower's channel is closed into a square tube, so the motor carrier"""),
("""Rough numbers (until the test fit): COVER_Y, CUP_X, CUP_Z, THETA. Adjustable: the arm +-25 mm across (in by 25 the
tower meets the receiver's end), the stop +-4 mm along the column (how deep the gear sits). Not adjustable: up and
down, and the angle; where the gear sits along the teeth is set by the arm across and by the gear's place on its
shaft.""",
 """Rough numbers (until the test fit): COVER_Y, CUP_X, CUP_Z, THETA. Adjustable: the arm 5 mm further in across (then
its deep part meets the receiver's end) and 25 out; the motor's slide along the column, anywhere in the groove (how
deep the gear sits). Not adjustable: up and down, and the angle; where the gear sits along the teeth is set by the arm
across and by the gear's place on its shaft."""),
# constants: the groove slide replaces the push bolt and the M4 stop
("""PUSH_VZ = (-31.0, -104.0)        # the push wing bolt: along -u through the outer wall, onto the bar
PUSH_NUT_U = (222.85, 227.25)    # its nut, dropped into a slot from the tower's top (skins 1.6 inside, 4 outside)
# v4's stop: an M4 bolt along the bar's middle into its bottom end, a captive nut in a slot 4 mm in, a fender washer
# under the bolt's head (wider than the tube, it lands on the tower's bottom face), a jam nut on the bolt against the
# bar's end. STOP_GAP: from the washer's top to the bar's end; at the nominal depth 8 (4 to 12: +-4 mm)
BAR_UV = ((BAR_U[0] + BAR_U[1]) / 2, (BAR_V[0] + BAR_V[1]) / 2)    # (213, -31): the bar's middle line
STOP_GAP = 8.0
M4_HOLE = 4.5
M4_NUT_AF, M4_NUT_T = 7.0, 3.2
M4_SLOT = (M4_NUT_AF / math.cos(math.radians(30)) + 0.4, M4_NUT_T + 0.4)   # across (corners), along the bar
M4_SLOT_IN = 4.0                 # the bar's end wall before the slot
M4_DEPTH = 27.0                  # the hole up the bar from its end (an M4 x 30 goes up to 24.4 in at the shortest stop)
WASHER_OD, WASHER_T = 24.0, 1.6  # a fender washer 19 to 25 mm across, #8 or M4 hole: over 18.2 it sits on the
                                 # tower's bottom face clear of the tube's chamfer (DIN 9021 M4, 12 mm, is too small)
DZ_DEEP, DZ_SHALLOW = 4.0, -4.0  # the stop's range""",
 """BAR_UV = ((BAR_U[0] + BAR_U[1]) / 2, (BAR_V[0] + BAR_V[1]) / 2)    # (213, -31): the bar's middle line
BAR_END_UP = 8.0                 # the bar's bottom end this far up the tube at the drawn depth (2 below it slid out)
DZ_DEEP, DZ_SHALLOW = 4.0, -4.0  # where the gear may need to sit for the drawn depth: the teeth piece 4 mm nearer you or
                                 # further than drawn (the plate on the cover, the tape under the teeth)
DZ_MAX = DZ_DEEP + 1.0           # the groove's top: the gear's tips reach the bottom of the teeth 1 mm past the drawn depth
# v5's slide (your idea): an M5 x 20 wing bolt and a fender washer, through a groove up the tower's outer wall along
# -u, into an M5 nut in a slot in the carrier's bar; tightened, it pulls the bar against the outer wall
SLIDE_Z0 = -108.0                # the wing bolt's height at the drawn depth
SLOT_W = 5.6                     # the groove, across
SLIDE_NUT_U = (213.6, 218.0)     # the nut's slot in the bar: 3 mm of bar outside it, the bolt's end 1 mm past the nut
WASHER_OD, WASHER_T = 25.0, 1.6  # the fender washer under the wing bolt (19 to 25 mm across; the checks use 25)
TICK_DZ = range(-10, 7)          # depth ticks on the bar's outer face, one a millimetre: the one at the tower's top
TICK_LONG = (-10, -5, 0, 5)      # edge reads the slide (0 the drawn depth; longer ticks every 5)"""),
("""DZ_OUT = TOWER_Z[1] - WEB_Z0     # -10: slid all the way out, the web sits on the tower's top (6 mm is enough)""",
 """DZ_OUT = TOWER_Z[1] - WEB_Z0     # -10: slid all the way out, the web sits on the tower's top (6 mm is enough)
GROOVE_Z = (SLIDE_Z0 + DZ_OUT - SLOT_W / 2 - 0.5, SLIDE_Z0 + DZ_MAX + SLOT_W / 2 + 0.5)    # (-121.3, -99.7)
DEEP = 50.0                      # v5: the arm this deep along the column, from DEEP_X0 to the tower
DEEP_X0 = ARM_X[0] + 47.0 + 5.5  # 125.5: 5.5 outside the receiver's mouth at the nominal place (5 mm left to slide in)"""),
("""BAR_Z = (TOWER_Z[0] + STOP_GAP, PLATE_Z[1])     # (-167.2, -38.35) at the nominal depth: the end is up in the tube""",
 """BAR_Z = (TOWER_Z[0] + BAR_END_UP, PLATE_Z[1])   # (-167.2, -38.35) at the nominal depth: the end is up in the tube"""),
]
for a, b in reps:
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
EOF
grep -n "^DZ_OUT\|^GROOVE_Z\|^DEEP\|^BAR_Z\|^WEB_Z0\|^PLATE_Z" rightarm.py