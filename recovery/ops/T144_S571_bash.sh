cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cat > s2proj.py <<'EOF'
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
from s2load import *
from PIL import Image, ImageDraw
U = '/root/.claude/uploads/29de5e81-e3b9-5428-a15c-fac1d206c0d4/'
FID = {33: '818fd797', 37: '8a88ba44', 24: 'd29ba350', 26: 'a5f478e3'}
for si in (0, 2):
    s, cost, pb = SOL[si]
    for n in (37, 33, 24, 26):
        im = Image.open(U + FID[n] + '-image.jpg').convert('RGB')
        d = ImageDraw.Draw(im)
        cols = {-50: (255, 60, 60), -75: (255, 200, 0), -97: (0, 255, 0), -115: (0, 200, 255)}
        for yv, col in cols.items():
            for z in np.arange(-80, -200, -10):
                pts = []
                for x in np.arange(-40, 81, 4):
                    uv, dep = project(pb, n, (x, yv, z))
                    if dep > 0:
                        pts.append(tuple(uv))
                if len(pts) > 1:
                    d.line(pts, fill=col, width=3)
            for x in (0, 40, 80):
                pts = [tuple(project(pb, n, (x, yv, z))[0]) for z in np.arange(-80, -200, -5)]
                d.line(pts, fill=col, width=2)
        # the hinge at 5:05 and the cup
        for X, col in (((46.8, -91.8, -109.5), (255, 0, 255)), ((38, -50, -98), (255, 255, 255))):
            uv, _ = project(pb, n, X)
            d.ellipse([uv[0] - 14, uv[1] - 14, uv[0] + 14, uv[1] + 14], outline=col, width=5)
        im.thumbnail((1000, 1000))
        im.save(f"proj_{n}_s{si}.jpg", quality=85)
        print(f"proj_{n}_s{si}.jpg")
EOF
PYTHONPATH=/home/claude/pylib python3 s2proj.py