python3 - <<'EOF'
p = "accord_lka_parts.py"
s = open(p).read()
old = '''  outer_block = (sector(big, 90.0 - t.lap, 90.0 + t.lap, r_in=t.r_split)
                 .extrude(zhi - Z_ROLL[0]).translate((0, 0, Z_ROLL[0])))'''
new = '''  z_block = Z_ROLL[0] - 0.3   # just below the back of the rolling band, so no faces coincide
  outer_block = (sector(big, 90.0 - t.lap, 90.0 + t.lap, r_in=t.r_split)
                 .extrude(zhi - z_block).translate((0, 0, z_block)))'''
assert old in s; s = s.replace(old, new)
old = '''  return part - tie_slots(t, angles)


def teeth_one_piece('''
new = '''  return clean(part - tie_slots(t, angles))


def teeth_one_piece('''
assert old in s; s = s.replace(old, new)
old = '''def manifold3d_op(name):'''
new = '''def clean(m: Manifold, min_volume: float = 0.5) -> Manifold:
  """Drops zero-volume slivers that booleans can leave on coinciding faces."""
  parts = [c for c in m.decompose() if c.volume() > min_volume]
  return union(parts) if parts else m


def manifold3d_op(name):'''
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)
EOF
cat > /home/claude/deliver/hardware/cad/render.py <<'EOF'
"""
Pictures of the parts: shaded views drawn with matplotlib from the solids' triangles.
"""
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

LIGHT = np.array([0.4, -0.5, 0.75])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def _tris(m, max_tris=120000):
  mesh = m.to_mesh()
  v = np.asarray(mesh.vert_properties)[:, :3]
  t = np.asarray(mesh.tri_verts)
  if len(t) > max_tris:
    t = t[np.linspace(0, len(t) - 1, max_tris).astype(int)]
  return v[t]


def draw(ax, parts, elev=25, azim=-60, title=None):
  """parts: list of (manifold, rgb). Draws them with simple diffuse shading."""
  allv = []
  for m, color in parts:
    tri = _tris(m)
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    shade = 0.35 + 0.65 * np.clip(n @ LIGHT, 0, 1)
    colors = np.clip(np.outer(shade, np.asarray(color)), 0, 1)
    pc = Poly3DCollection(tri, facecolors=colors, edgecolors="none", linewidths=0)
    ax.add_collection3d(pc)
    allv.append(tri.reshape(-1, 3))
  v = np.concatenate(allv)
  lo, hi = v.min(axis=0), v.max(axis=0)
  c, r = (lo + hi) / 2, (hi - lo).max() / 2
  ax.set_xlim(c[0] - r, c[0] + r)
  ax.set_ylim(c[1] - r, c[1] + r)
  ax.set_zlim(c[2] - r, c[2] + r)
  ax.set_box_aspect((1, 1, 1))
  ax.view_init(elev=elev, azim=azim)
  ax.set_axis_off()
  if title:
    ax.set_title(title, fontsize=10)


def save_views(path, parts, views=((25, -60), (25, 30), (85, -90)), title=None, size=(12, 4.4)):
  fig = plt.figure(figsize=size, dpi=110)
  for i, (e, a) in enumerate(views):
    ax = fig.add_subplot(1, len(views), i + 1, projection="3d")
    draw(ax, parts, elev=e, azim=a)
  if title:
    fig.suptitle(title, fontsize=12)
  fig.tight_layout()
  fig.savefig(path)
  plt.close(fig)
EOF
cd /home/claude/deliver/hardware/cad && mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/prev && export PYTHONPATH=/home/claude/pylib:. && timeout 600 python3 -c "
import accord_lka_parts as P, render as R
t = P.Teeth()
s = P.teeth_solid(t)
r = P.teeth_half(t, 'right', s); l = P.teeth_half(t, 'left', s)
print('right comps', len(r.decompose()), r.genus(), 'left', len(l.decompose()), l.genus())
out='/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/prev/'
R.save_views(out+'teeth_halves.png', [(r,(0.9,0.5,0.2)), (l.translate((0,0,0)),(0.3,0.6,0.9))], views=((30,-70),(20,20),(88,-90)), title='steering wheel teeth halves')
# close-up of the joint: slice near 12 o'clock
import manifold3d as m
clip = P.box(-30,30,150,205,-25,25)
R.save_views(out+'teeth_joint.png', [(r^clip,(0.9,0.5,0.2)), (l^clip,(0.3,0.6,0.9))], views=((35,-50),(35,-130),(10,-90)), title='joint at 12 oclock')
"
