python3 - <<'EOF'
p='frameplate.py'; s=open(p).read()
old=s[s.index('def plate() -> Manifold:'):s.index('def build(')]
new='''def plate() -> Manifold:
  """Built in the car frame, then mirrored so that, printed labels up and fitted labels down, the layout seen from
  below matches the photos (key side on the right). The labels are added after the mirror so they read correctly."""
  body = rbox(RIGHT) + rbox(FRONT) + rbox(STRIP)
  body = body - slot(CUP[0], CUP[1], SLOT_L, SLOT_W, "x")
  for xc in STRIP_COLS:
    for y0, y1 in STRIP_SLOTS:
      body = body - slot(xc, (y0 + y1) / 2, y1 - y0, SLOT_W, "y")
  body = body.mirror((1.0, 0.0, 0.0))              # x -> -x: the key side is now +x
  labels = []
  # slot numbers 1..5 on the strip's front bar, "KEY >" by the cup, "WHEEL" on the edge nearest the wheel
  for k, xc in enumerate(STRIP_COLS, start=1):
    s = str(k)
    labels.append(text(s, -xc - text_width(s, 0.9) / 2, STRIP[3] - 5.0, T, pix=0.9))
  labels.append(text("KEY >", -RIGHT[0] - text_width("KEY >") - 2.0, RIGHT[3] - 8.0, T))
  labels.append(text("WHEEL", -8.0, RIGHT[2] + 3.0, T, pix=0.9))
  return body + union(labels)


'''
s=s.replace(old,new)
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 frameplate.py && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
# check: top view of the STL as printed (seen from above the bed) should match the drawing: strip left, cup right
import sys; sys.path.insert(0,'/home/claude/deliver/hardware/cad')
import numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from cadlib import *
import struct
f=open('/home/claude/deliver/hardware/stl/column-frame-plate/column-frame-plate.stl','rb'); f.read(80); n=struct.unpack('<I',f.read(4))[0]
tri=np.frombuffer(f.read(n*50),dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]))['v'].reshape(-1,3,3)
top=tri[np.abs(tri[:,:,2]-4.0).max(axis=1)<1e-3]   # faces at z=4 (plate top)
fig,ax=plt.subplots(figsize=(8,5),dpi=120)
from matplotlib.collections import PolyCollection
ax.add_collection(PolyCollection(top[:,:,:2],fc='#bbb',ec='none'))
lab=tri[np.abs(tri[:,:,2]-4.5).max(axis=1)<1e-3]
ax.add_collection(PolyCollection(lab[:,:,:2],fc='#222',ec='none'))
ax.set_xlim(-5,165); ax.set_ylim(-5,100); ax.set_aspect('equal'); ax.set_title('STL top view as printed')
fig.savefig('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/frame_top.png')
EOF