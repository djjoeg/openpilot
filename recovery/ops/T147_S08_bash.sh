cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cat > coverfit.py <<'EOF'
"""Candidate lower-column-cover shapes, placed from each photo-scale solution's landmarks, drawn over photos 33 and 37."""
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
from s2load import *
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from PIL import Image
from manifold3d import Manifold, CrossSection

U = '/root/.claude/uploads/29de5e81-e3b9-5428-a15c-fac1d206c0d4/'
FID = {33: '818fd797', 37: '8a88ba44', 24: 'd29ba350', 26: 'a5f478e3'}
HOOK = {0: np.array([80.5, -34.5, -62.4]), 2: np.array([90.8, -48.9, -106.9])}

def cover(si, front="round", chamfer=30.0):
    s, cost, pb = SOL[si]
    cup = to_car(pb.pts[("L", "CUP")])
    yb, xc = cup[1], cup[0]
    xR = xc + 25.0
    zf = HOOK[si][2] - 3.0
    yt = 60.0
    w = xR + xR
    cs = CrossSection.square((w - 50, yt - yb - 50), center=True).offset(25.0, circular_segments=48)
    cs = cs.translate((0.0, (yt + yb) / 2))
    body = cs.extrude(300.0).translate((0, 0, zf - 300.0))
    if front == "chamfer":
        # cut the front-bottom edge back at 45 degrees, `chamfer` mm each way
        c = chamfer
        tri = CrossSection([[(yb - 1, zf + 1), (yb - 1, zf - c - 1), (yb + c + 1, zf + 1)]])
        tri = tri if tri.area() > 0 else CrossSection([[(yb - 1, zf + 1), (yb + c + 1, zf + 1), (yb - 1, zf - c - 1)]])
        cut = tri.extrude(400.0).transform([[0, 0, 1, -200.0], [1, 0, 0, 0], [0, 1, 0, 0]])
        body = body - cut
    return body, dict(yb=yb, xc=xc, xR=xR, zf=zf, cup=cup)

def draw(si, n, ax, body, col, label):
    s, cost, pb = SOL[si]
    mesh = body.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    t = np.asarray(mesh.tri_verts)
    uv = np.array([project(pb, n, p)[0] for p in v])
    polys = uv[t]
    ax.add_collection(PolyCollection(polys, facecolor=col, edgecolor="none", alpha=0.08))
    ax.plot([], [], color=col, label=label, lw=4)

for si in (0, 2):
    for n in (37, 33):
        im = Image.open(U + FID[n] + '-image.jpg').convert('RGB')
        fig, axs = plt.subplots(1, 2, figsize=(18, 12))
        for ax, (front, col) in zip(axs, (("round", "#00ff00"), ("chamfer", "#ff00ff"))):
            ax.imshow(im)
            body, info = cover(si, front)
            draw(si, n, ax, body, col, front)
            # the motor's board at 5:05 (the inner-back corner region) for reference
            import popparts as PP
            PP.MOUNT_DEG = -63.0
            for X in [PP.carrier_point_to_wheel((x, y, -54.0)) for x in (-21.15, 21.15) for y in (-21.15, 21.15)]:
                uvp, _ = project(pb, n, X)
                ax.plot(uvp[0], uvp[1], "y*", ms=14)
            ax.set_xlim(300, 1700); ax.set_ylim(2100, 900)
            ax.set_title(f"photo {n}, scale solution {si} ({'near' if si == 0 else 'far'}), front {front}; zf {info['zf']:.0f} yb {info['yb']:.0f}")
            ax.legend()
        plt.tight_layout()
        plt.savefig(f"/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap/cfit_{n}_{si}.jpg", dpi=55)
        plt.close(fig)
print("done")
EOF
PYTHONPATH=/home/claude/pylib timeout 600 python3 coverfit.py