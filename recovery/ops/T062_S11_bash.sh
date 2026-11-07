python3 - <<'EOF'
import re
p='mountparts.py'
s=open(p).read()
old_block = s[s.index("# Spring that presses the motor gear onto the steering wheel teeth: Lee Spring LCM110E12S"):s.index("SETUP_GAP = 12.0")]
new_block = '''# Spring that presses the motor gear onto the steering wheel teeth: Lee Spring LC 055F 08 S (stainless steel, 0.42 in
# (10.67 mm) outside, 0.31 in (7.87 mm) inside, 0.055 in (1.40 mm) wire, 1.75 in (44.45 mm) long +-0.05 in (1.27 mm),
# 20.0 lb/in (3.502 N/mm) +-10%, 0.765 in (19.43 mm) fully squashed, which takes 88.93 N; it needs an 0.438 in
# (11.13 mm) hole). Lee Spring sizes its stock springs so that squashing them fully is the most they can take, so that
# load is the spring's limit. The spring never gets that far here (the parts report gives its lengths). It is strong
# enough that the motor gear stays in the teeth without grease (see margins.py).
SPRING_OD, SPRING_ID, SPRING_FREE, SPRING_RATE, SPRING_SOLID, SPRING_MAX_N = 10.67, 7.87, 44.45, 3.502, 19.43, 88.93
SPRING_WIRE = 1.40
SPRING_FREE_TOL, SPRING_RATE_TOL = 1.27, 0.10        # Lee Spring's tolerances on its free length (mm) and rate
SPRING_PART = "Lee Spring LC 055F 08 S"
SPRING_Z = -4.0                       # spring's axis, in front of the hinge
SPRING_ARM = SPRING_Z - HINGE[1]      # its distance from the hinge axis
SPRING_SEAT_R = 5.75                  # hole through the carrier's top block (11.5 mm; the spring needs 11.13): the
SPRING_SEAT_D = TOP_Y[1] - NEMA / 2   # spring's lower end rests on the motor's top, 8.5 mm below the carrier's top
SPRING_POCKET_R = 5.9                 # pocket in the hinge block's underside for its upper end
SPRING_POCKET_D = 12.9                # deep enough for the spring's working length of 33.4 mm
POCKET_ROOF = 3.0                     # the hinge block above the pocket, where the lift lever's rounded end bears
SPRING_SHIM_T = 1.0                   # an M5 washer (10 mm across) under the spring adds this much push, if the grip
                                      # test in the car setup asks for it
'''
s=s.replace(old_block,new_block,1)
s=s.replace("HB_T = 9.0\n","HB_T = SPRING_POCKET_D + POCKET_ROOF   # 15.9 mm thick\n",1)
s=s.replace("EAR_CUT_Z, EAR_CUT_TOP = -4.0, 72.0   #","EAR_CUT_Z, EAR_CUT_TOP = -4.0, HB_TOP + 21.35   #",1)
open(p,'w').write(s)
p='params.py'
s=open(p).read()
s=s.replace("LANE_KEEPING_MOST_NM = 4.03","LANE_KEEPING_MOST_NM = 3.85  # lane keeping's most: the grip test (the board's most) is 1.41 times this",1)
open(p,'w').write(s)
EOF
grep -n "HB_T =\|EAR_CUT_TOP\|LANE_KEEPING_MOST_NM\|SPRING_POCKET_D\|POCKET_ROOF" mountparts.py params.py | head; grep -n "EAR_CUT_TOP" mountparts.py