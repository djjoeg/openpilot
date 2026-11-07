python3 - <<'EOF'
p='armmount.py'; s=open(p).read()
s=s.replace('''  body = body - FR.slot(0.0, 0.0, FR.SLOT_L, FR.SLOT_W, "x")
  xc, y0, y1 = LEG_SLOT
  body = body - FR.slot(xc, (y0 + y1) / 2, y1 - y0, FR.SLOT_W, "y")
  # the receiver''','''  body = body - through_slot(0.0, 0.0, FR.SLOT_L, FR.SLOT_W, "x")
  xc, y0, y1 = LEG_SLOT
  body = body - through_slot(xc, (y0 + y1) / 2, y1 - y0, FR.SLOT_W, "y")
  # the receiver''')
s=s.replace('''def frame_plate_v3() -> Manifold:''','''def through_slot(xc: float, yc: float, length: float, width: float, along: str) -> Manifold:
  """An oblong hole through the whole plate (frameplate.slot only reaches frameplate's 4 mm)."""
  r = width / 2
  d = (length - width) / 2
  z0, z1 = -1.0, PLATE_T + 1.0
  if along == "x":
    ends = [cyl(r, z0, z1, x=xc - d, y=yc, segments=32), cyl(r, z0, z1, x=xc + d, y=yc, segments=32)]
  else:
    ends = [cyl(r, z0, z1, x=xc, y=yc - d, segments=32), cyl(r, z0, z1, x=xc, y=yc + d, segments=32)]
  return Manifold.batch_hull(ends)


def frame_plate_v3() -> Manifold:''')
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 armmount.py 2>&1 | tail -3 && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import sys; sys.path.insert(0,'.')
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import armmount as A
m=A.parts_on_bed()["column-frame-plate-v3"]
mesh=m.to_mesh(); v=np.asarray(mesh.vert_properties)[:,:3]; t=np.asarray(mesh.tri_verts); tri=v[t]
fig,ax=plt.subplots(figsize=(8,5),dpi=120)
for zlev,col in ((6.0,'#bbb'),(41.4,'#888'),(6.5,'#222')):
    sel=tri[np.abs(tri[:,:,2]-zlev).max(axis=1)<1e-3]
    ax.add_collection(PolyCollection(sel[:,:,:2],fc=col,ec='none'))
bb=m.bounding_box(); ax.set_xlim(bb[0]-5,bb[3]+5); ax.set_ylim(bb[1]-5,bb[4]+5); ax.set_aspect('equal')
fig.savefig('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v3_top.png')
print("pieces", len(A.frame_plate_v3().decompose()))
EOF