python3 - <<'EOF'
p='rightarm.py'; s=open(p).read()
s=s.replace('''TUBE_X = (-60.0, 3.0)                    # along the plate, from the key-side end in to just short of the cup's washer''',
'''TUBE_X = (-47.0, 3.0)                    # along the plate: 50 long, from just short of the cup's washer out to the key side''')
s=s.replace('''ARM_X = (CUP_X - TUBE_X[1] + 3.0, CUP_X - TUBE_X[1] + 103.0)   # (70, 170): 60 in the receiver, nominal''',
'''ARM_X = (CUP_X - TUBE_X[1] + 3.0, CUP_X - TUBE_X[1] + 103.0)   # (73, 173): 47 in the receiver, nominal''')
s=s.replace('''FOOT_X = (130.0, 170.0)''','''FOOT_X = (140.0, 170.0)                  # clear of the receiver's end (X 120) with the arm pushed 20 mm in''')
s=s.replace('''  m = box(R_FACE_OUT, R_FACE_OUT + FACE_T, FACE_V[0], FACE_V[1], FACE_Z[0], FACE_Z[1])
  m = m - cyl_x(BOSS_HOLE / 2, R_FACE_OUT - 1.0, R_FACE_OUT + FACE_T + 1.0, y=0.0, z=Z_AXIS, segments=64)
  for b in (-NEMA_HOLES / 2, NEMA_HOLES / 2):
    for c in (-NEMA_HOLES / 2, NEMA_HOLES / 2):
      m = m - cyl_x(1.7, R_FACE_OUT - 1.0, R_FACE_OUT + FACE_T + 1.0, y=b, z=Z_AXIS + c, segments=24)''',
'''  r0, r1 = R_FACE_OUT - FACE_T, R_FACE_OUT          # the plate just inside the motor's face: the shaft through it
  m = box(r0, r1, FACE_V[0], FACE_V[1], FACE_Z[0], FACE_Z[1])
  m = m - cyl_x(BOSS_HOLE / 2, r0 - 1.0, r1 + 1.0, y=0.0, z=Z_AXIS, segments=64)
  for b in (-NEMA_HOLES / 2, NEMA_HOLES / 2):
    for c in (-NEMA_HOLES / 2, NEMA_HOLES / 2):
      m = m - cyl_x(1.7, r0 - 1.0, r1 + 1.0, y=b, z=Z_AXIS + c, segments=24)''')
s=s.replace('''  """The face plate, standing on the tab: perpendicular to U at R_FACE_OUT, FACE_T thick outwards."""''',
'''  """The face plate, standing on the tab: perpendicular to U, FACE_T thick, its outer face at R_FACE_OUT (the motor's)."""''')
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 - <<'EOF'
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
for a in range(-25,26,5):
    tp=teeth.rotate((0,0,a))
    for n in ("arm","bar","bracket","plate","motor","board"):
        v=(tp^parts[n]).volume()
        if v>0.01: print(f"  teeth at {a} deg x {n}: {v:.1f} mm3"); bad=True
for n in parts:
    v=(grip^parts[n]).volume()
    if v>0.01: print(f"  grip x {n}: {v:.1f}"); bad=True
print("overlaps:", "some" if bad else "none")
# the arm slid in 20 and out 25 with the bar and bracket following: vs the plate
for dx in (-20.0, 25.0):
    moved=[parts[n].translate((dx,0,0)) for n in ("arm","bar","bracket","motor","board","gear")]
    v=sum((m^parts["plate"]).volume() for m in moved)
    vt=sum((m^teeth.rotate((0,0,a))).volume() for m in moved for a in (-20,0,20))
    vg=sum((m^grip).volume() for m in moved)
    print(f"  arm slid {dx:+.0f}: vs plate {v:.1f}, vs teeth {vt:.1f}, vs grip {vg:.1f} mm3")
# the bracket turned +-15 about the pivot
from manifold3d import Manifold
for deg in (-15.0, 15.0):
    px,py=RA.PIVOT
    rot=lambda m: m.translate((-px,-py,0)).rotate((0,0,deg)).translate((px,py,0))
    moved=[rot(parts[n]) for n in ("bracket","motor","board","gear")]
    vt=sum((m^teeth.rotate((0,0,a))).volume() for m in moved for a in (-20,0,20))
    vg=sum((m^grip).volume() for m in moved); vb=sum((m^parts["bar"]).volume() for m in moved[1:])
    print(f"  bracket turned {deg:+.0f}: vs teeth {vt:.1f}, vs grip {vg:.1f}, motor/gear vs bar {vb:.1f} mm3")
EOF