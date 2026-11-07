python3 - <<'EOF'
p='armmount.py'; s=open(p).read()
s=s.replace('''EAR_Z = (-85.0, Z_AXIS + H)      # flush with the face plate's end towards you (the bracket prints standing on that end)''',
'''EAR_Z = (-85.0, -50.0)           # its end towards you stays 5 mm clear of the teeth piece's outer ramps as the wheel turns;
                                 # its dash end flush with the face plate's (the bracket prints standing on that end)''')
s=s.replace('''  m = box(R_FACE, R_FACE + FACE_T, FACE_V[0], FACE_V[1], -H, H)''','''  m = box(R_FACE, R_FACE + FACE_T, FACE_V[0], FACE_V[1], EAR_Z[0] - Z_AXIS, H)   # the plate runs on to the ear's dash end''')
s=s.replace('''  br = on_bed(bracket(), rotate=(180.0, 0.0, 0.0))      # standing on its end towards you: both plates upright''',
'''  br = on_bed(bracket())                                # standing on its dash end: both plates upright''')
s=s.replace('''the bracket standing on its end towards the wheel (the face plate and the ear are both upright walls then).''','''the bracket standing on its dash end (the face plate and the ear are both upright walls then).''')
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 - <<'EOF'
import sys; sys.path.insert(0,'.')
import armmount as A, midteeth as MT, numpy as np
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
# clearances by growing the teeth sweep: offset via Minkowski with a small cube
from manifold3d import Manifold
sweep=Manifold.compose([teeth.rotate((0,0,a)) for a in range(-25,26,5)])
for n in ("arm","bracket","gear","motor"):
    for d in (1,2,3,5):
        grown=Manifold.batch_hull([parts[n].translate((dx,dy,dz)) for dx in (-d,d) for dy in (-d,d) for dz in (-d,d)]) if False else None
    # cheap: bounding gap along the worst axis is not meaningful; use the sweep's distance by boolean with translated copies
    hit=None
    for d in (1,2,3,4,5,8):
        g=Manifold.compose([parts[n].translate((dx*d/1.7,dy*d/1.7,dz*d/1.7)) for dx in (-1,0,1) for dy in (-1,0,1) for dz in (-1,0,1)])
        if (g^sweep).volume()>0.01: hit=d; break
    print(f"  {n}: the teeth sweep comes within about {hit if hit else '>8'} mm")
br=A.parts_on_bed()["arm-bracket"]
mesh=br.to_mesh(); v=np.asarray(mesh.vert_properties)[:,:3]; t=np.asarray(mesh.tri_verts); tri=v[t]; low=np.abs(tri[:,:,2]).max(axis=1)<1e-3
print("bracket on bed: area", round(0.5*np.linalg.norm(np.cross(tri[low,1]-tri[low,0],tri[low,2]-tri[low,0]),axis=1).sum()), "mm2")
EOF