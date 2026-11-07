python3 - <<'EOF'
p='armmount.py'; s=open(p).read()
s=s.replace('''  face = local_to_wheel(face_plate_local())
  ear = box(''','''  face = local_to_wheel(face_plate_local()) ^ cyl(FACE_R_MAX, -100.0, -20.0, segments=256)   # its far corner trimmed
  ear = box(''')
s=s.replace('''FACE_T = 5.0
FACE_V = (-H, 32.0)              # the face plate across (towards 4 o'clock), out to the ear''','''FACE_T = 5.0
FACE_V = (-H, 32.0)              # the face plate across (towards 4 o'clock), out to the ear
FACE_R_MAX = 159.5               # the plate's far corner trimmed to this radius: inside the teeth's inner end (160.5)''')
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 600 python3 - <<'EOF'
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
    for n in ("arm","bracket","shoe","plate","motor","board","gear"):
        v=(tp^parts[n]).volume()
        if v>0.01 and n!="gear": print(f"  teeth at {a} deg x {n}: {v:.1f} mm3"); bad=True
print("overlaps:", "some" if bad else "none")
# the face plate joins the ear?
br=parts["bracket"]; print("bracket pieces:", br.num_vert()>0, "decompose:", len(br.decompose()))
br=A.parts_on_bed()["arm-bracket"]
mesh=br.to_mesh(); v=np.asarray(mesh.vert_properties)[:,:3]; t=np.asarray(mesh.tri_verts); tri=v[t]; low=np.abs(tri[:,:,2]).max(axis=1)<1e-3
print("bracket on bed: area", round(0.5*np.linalg.norm(np.cross(tri[low,1]-tri[low,0],tri[low,2]-tri[low,0]),axis=1).sum()), "mm2")
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 armmount.py 2>&1 | tail -7