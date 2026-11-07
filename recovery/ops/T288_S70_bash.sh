mkdir -p /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/comp && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/comp && cat > camload.py <<'EOF'
"""Cameras for the key photos (fit B, stage 2) in the car frame (mm): pixel = f * (R X + t)[:2] / (R X + t)[2] + c."""
import os, sys, pickle
import numpy as np
SFM = "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm"
sys.path.insert(0, SFM)
_cwd = os.getcwd()
os.chdir(SFM)
import stage2
import __main__
__main__.Stage2 = stage2.Stage2
from jba import rot
SOL = pickle.load(open(os.path.join(SFM, "stage2_1.164_1.280_1.407.pkl"), "rb"))
os.chdir(_cwd)
ROLL = np.radians(-10.35)
RZ = np.array([[np.cos(ROLL), -np.sin(ROLL), 0], [np.sin(ROLL), np.cos(ROLL), 0], [0, 0, 1]])
FID = {33: '818fd797', 37: '8a88ba44', 24: 'd29ba350', 26: 'a5f478e3'}
UP = '/root/.claude/uploads/29de5e81-e3b9-5428-a15c-fac1d206c0d4/'


def key_camera(n, sol=2):
    s, cost, pb = SOL[sol]
    c = pb.cams[n]
    R = rot(c["rv"]) @ RZ.T          # car -> camera
    return dict(R=np.asarray(R, float), t=np.asarray(c["t"], float), f=float(c["f"]), c=np.asarray(c["c"], float))


def project(cam, X):
    X = np.atleast_2d(np.asarray(X, float))
    p = X @ cam["R"].T + cam["t"]
    return p[:, :2] / p[:, 2:3] * cam["f"] + cam["c"], p[:, 2]
EOF
cat > projtest.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
from PIL import Image, ImageDraw
import camload as CL
import carscene as CS
sc = CS.CarScene(D=128.2)
p = sc.p
def circle(c, n, r, k=120):
    n = n / np.linalg.norm(n)
    a = np.cross(n, [0, 0, 1.0]); a /= np.linalg.norm(a); b = np.cross(n, a)
    t = np.linspace(0, 2 * np.pi, k)
    return c[None] + r * (np.cos(t)[:, None] * a + np.sin(t)[:, None] * b)
tiles = []
for n in (26, 33, 37):
    cam = CL.key_camera(n)
    im = Image.open(CL.UP + CL.FID[n] + '-image.jpg').convert('RGB')
    d = ImageDraw.Draw(im)
    def poly(P, col, w=4):
        uv, z = CL.project(cam, P)
        pts = [tuple(q) for q, zz in zip(uv, z) if zz > 0]
        if len(pts) > 1: d.line(pts, fill=col, width=w)
    poly(circle(p["KEY"], p["N"], 19.0), (255, 0, 0))
    poly(circle(p["KEY"], p["N"], 13.0), (255, 128, 0))
    # grip ring outer and inner circles (z = 0) and its back (z=-17.7)
    for r, z, col in ((186, 0, (0, 255, 0)), (150.6, 0, (0, 200, 0)), (168.3, -17.7, (0, 255, 255))):
        t = np.linspace(0, 2 * np.pi, 720)
        poly(np.c_[r * np.cos(t), r * np.sin(t), np.full_like(t, z)], col)
    # cover: bottom flat edge corner lines along z
    yb, xr, zf, rr = sc.cover_bottom, sc.cover_right_x, sc.cover_front_z, sc.corner_r
    zs = np.linspace(zf, zf - 200, 30)
    poly(np.c_[np.full_like(zs, xr - rr), np.full_like(zs, yb), zs], (255, 255, 0))
    poly(np.c_[np.full_like(zs, xr), np.full_like(zs, yb + rr), zs], (255, 255, 0))
    xs = np.linspace(-80, xr - rr, 30)
    poly(np.c_[xs, np.full_like(xs, yb), np.full_like(xs, zf)], (255, 0, 255))
    ys = np.linspace(yb + rr, 60, 30)
    poly(np.c_[np.full_like(ys, xr), ys, np.full_like(ys, zf)], (255, 0, 255))
    for k, col in (("CUP", (255, 255, 255)), ("SH", (0, 0, 255)), ("ST", (0, 0, 255)), ("PU", (255, 0, 0)), ("HOOK", (0, 255, 255)), ("RH", (128, 0, 255))):
        uv, z = CL.project(cam, p[k])
        u, v = uv[0]
        d.ellipse([u - 15, v - 15, u + 15, v + 15], outline=col, width=5)
    # the planned cup screw and frame plate position: CUP_X, COVER_Y, CUP_Z = 73, -107, -145
    uv, z = CL.project(cam, (73, -107, -145)); u, v = uv[0]
    d.rectangle([u - 12, v - 12, u + 12, v + 12], outline=(0, 0, 0), width=5)
    im.thumbnail((900, 1200))
    tiles.append(im)
W = sum(t.width for t in tiles); H = max(t.height for t in tiles)
S = Image.new('RGB', (W, H)); x = 0
for t in tiles: S.paste(t, (x, 0)); x += t.width
S.save('projtest.jpg', quality=88)
print(S.size)
for n in (26, 33, 37):
    cam = CL.key_camera(n); print(n, 'f', round(cam['f']), 'centre', np.round(-cam['R'].T @ cam['t'], 1))
EOF
python3 projtest.py