python3 - << 'EOF'
p = "mountparts.py"
s = open(p).read()
s = s.replace("HUMP_DEG = 1.2          # the lever goes over this much more lift either side of 'up', so it clicks in and stays\n", "")
s = s.replace("""  lift lever     - down (on): it hangs back towards the dashboard, the motor gear sits on the teeth and the handle
                   holds the power switch pressed. Up (off): its cam lifts the motor gear off the teeth and the switch
                   cuts the motor's power. It clicks into the up position and stays there until pushed back down.""",
"""  lift lever     - down (on): it hangs back towards the dashboard, the motor gear sits on the teeth and the handle
                   holds the power switch pressed. Up (off): its cam lifts the motor gear off the teeth and the switch
                   cuts the motor's power. Up, it rests against a stop just past the cam's highest point, so the spring
                   holds it there until it is pushed back down.""")
s = s.replace("HANDLE_LEN = 40.0                     # pivot to the end of the handle", "HANDLE_LEN = 38.0                     # pivot to the end of the handle")
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import mountparts as MP, math, numpy as np
rows = MP.lever_lift_table(2.0, MP.A_HARD_STOP + 4)
for a, th, f in rows: print('%5.0f  sched %6.2f  lift %6.2f  force %5.2f N' % (a, MP.lift_schedule(a), th, f))
pts = np.array(MP.cam_points(1.0)); r = np.hypot(pts[:,0], pts[:,1])
print('cam radius min %.2f max %.2f' % (r.min(), r.max()))
print('lift at stop %.2f, at dead centre %.2f' % (MP.cam_lift(MP.A_HARD_STOP), MP.cam_lift(MP.A_DEAD)))
"