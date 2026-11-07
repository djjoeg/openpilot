python3 - <<'EOF'
p='armmount.py'; s=open(p).read()
s=s.replace('''EAR_Y = (-152.0, -108.0)
EAR_Z = (-85.0, -40.0)
EAR_HOLES = ((-137.0, -75.0), (-137.0, -60.0))    # (y, z): nominal, the middle of the arm's slots
NUT_DEEP = 4.5                   # the nuts' pockets in the ear's inner face
RIB = ((ARM_X[0], ARM_X[1]), (ARM_Z[1], ARM_Z[1] + 5.0))     # the rib on the ear's outer face, against the arm's end''',
'''EAR_Y = (-148.0, -108.0)         # its bottom clears the teeth piece's outer ramps as the wheel turns
EAR_Z = (-85.0, Z_AXIS + H)      # flush with the face plate's end towards you (the bracket prints standing on that end)
EAR_HOLES = ((-137.0, -75.0), (-137.0, -60.0))    # (y, z): nominal, the middle of the arm's slots
NUT_DEEP = 4.5                   # the nuts' pockets in the ear's inner face
STEP_X = ARM_X[1]                # past the arm's end the ear is thicker, out to the arm's outer face: the step the arm's
STEP_Z = ARM_Z[1]                # end face sits against, so the ear stays upright''')
s=s.replace('''  ear = box(EAR_X[0], EAR_X[1], EAR_Y[0], EAR_Y[1], EAR_Z[0], EAR_Z[1])
  rib = box(RIB[0][0], RIB[0][1], EAR_Y[0], EAR_Y[1], RIB[1][0], RIB[1][1])
  m = face + ear + rib''','''  ear = box(EAR_X[0], EAR_X[1], EAR_Y[0], EAR_Y[1], EAR_Z[0], EAR_Z[1])
  step = box(EAR_X[0], STEP_X, EAR_Y[0], EAR_Y[1], STEP_Z, EAR_Z[1])
  m = face + ear + step''')
s=s.replace('''  br = bracket().rotate((0.0, 0.0, -MOUNT_DEG))         # the shaft now along +x: the face plate's front is its +x face
  br = on_bed(br, rotate=(0.0, 90.0, 0.0))              # +x -> -z: the front face down
  return''','''  br = on_bed(bracket(), rotate=(180.0, 0.0, 0.0))      # standing on its end towards you: both plates upright
  return''')
s=s.replace('''the bracket on its face plate's front (the ear rising from it, 20 degrees off upright).''','''the bracket standing on its end towards the wheel (the face plate and the ear are both upright walls then).''')
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 - <<'EOF'
import sys; sys.path.insert(0,'.')
import armmount as A, midteeth as MT, numpy as np
from manifold3d import Manifold
mg=A.motor_and_gear()
parts={"plate":A.plate_to_wheel(A.frame_plate_v2()),"shoe":A.shoe(),"arm":A.arm(),"bracket":A.bracket(),"motor":mg["motor"],"board":mg["board"],"gear":mg["gear"]}
teeth=MT.mid_teeth(MT.MidTeeth(n_teeth=10)).rotate((0,0,A.MOUNT_DEG))
names=list(parts); bad=False
for i in range(len(names)):
    for j in range(i+1,len(names)):
        v=(parts[names[i]]^parts[names[j]]).volume()
        if v>0.01: print(f"  {names[i]} x {names[j]}: {v:.1f}"); bad=True
for a in range(-25,26,5):
    tp=teeth.rotate((0,0,a))
    for n in ("arm","bracket","shoe","plate","motor","board"):
        v=(tp^parts[n]).volume()
        if v>0.01: print(f"  teeth at {a} deg x {n}: {v:.1f} mm3"); bad=True
print("overlaps:", "some" if bad else "none")
br=A.parts_on_bed()["arm-bracket"]
mesh=br.to_mesh(); v=np.asarray(mesh.vert_properties)[:,:3]; t=np.asarray(mesh.tri_verts); tri=v[t]; low=np.abs(tri[:,:,2]).max(axis=1)<1e-3
print("bracket on bed: area", round(0.5*np.linalg.norm(np.cross(tri[low,1]-tri[low,0],tri[low,2]-tri[low,0]),axis=1).sum()), "mm2; size", [round(x,1) for x in A.cadlib.size_of(br)] if hasattr(A,'cadlib') else [round(br.bounding_box()[i+3]-br.bounding_box()[i],1) for i in range(3)])
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 armmount.py 2>&1 | tail -7