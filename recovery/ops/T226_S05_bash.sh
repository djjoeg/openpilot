sed -i 's/^R_FACE_OUT = 180.0 .*/R_FACE_OUT = 182.5               # the motor'"'"'s face from the wheel'"'"'s middle: the face plate (5 mm, just inside it) clears the\n                                 # teeth piece'"'"'s outer band (radius 177); the gear'"'"'s teeth then reach in to radius 163/' rightarm.py && grep -n "^R_FACE_OUT" -A 1 rightarm.py && PYTHONPATH=/home/claude/pylib timeout 900 python3 - <<'EOF'
import sys; sys.path.insert(0,'.')
import rightarm as RA, midteeth as MT, numpy as np, math
from cadlib import revolve
mg=RA.motor_and_gear()
parts={"plate":RA.plate_to_wheel(RA.frame_plate_v4()),"arm":RA.arm(),"bar":RA.bar(),"bracket":RA.bracket(),"motor":mg["motor"],"board":mg["board"],"gear":mg["gear"]}
teeth=MT.mid_teeth(MT.MidTeeth(n_teeth=10)).rotate((0,0,RA.THETA))
grip_r=RA.S.FP.GRIP/2; rr=RA.S.FP.WHEEL_OD/2-grip_r
grip=revolve([(rr+grip_r*math.cos(math.radians(a)), grip_r*math.sin(math.radians(a))) for a in range(0,360,10)], -180, 180, step_deg=2)
names=list(parts); bad=False
for i in range(len(names)):
    for j in range(i+1,len(names)):
        v=(parts[names[i]]^parts[names[j]]).volume()
        if v>0.01: print(f"  {names[i]} x {names[j]}: {v:.1f}"); bad=True
worst=0
for a in np.arange(-12,12.1,1.0):
    tp=teeth.rotate((0,0,a))
    for n in ("arm","bar","bracket","plate","motor","board","gear"):
        v=(tp^parts[n]).volume()
        if n=="gear": worst=max(worst,v); continue
        if v>0.01: print(f"  teeth at {a} deg x {n}: {v:.1f} mm3"); bad=True
for n in parts:
    v=(grip^parts[n]).volume()
    if v>0.01: print(f"  grip x {n}: {v:.1f}"); bad=True
print("overlaps (not the gear):", "some" if bad else "none", "; gear in the teeth, worst overlap over +-12 deg:", round(worst,1), "mm3")
g=parts["gear"]; bb=g.bounding_box(); print("gear R range", round(math.hypot(bb[0],bb[4]),1), round(math.hypot(bb[3],bb[1]),1))
EOF