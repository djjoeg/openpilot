cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cat > s2rim.py <<'EOF'
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
from s2load import *
from PIL import Image, ImageDraw
U = '/root/.claude/uploads/29de5e81-e3b9-5428-a15c-fac1d206c0d4/'
FID = {33: '818fd797', 37: '8a88ba44', 24: 'd29ba350', 26: 'a5f478e3'}
th = np.radians(np.arange(-150, 30, 2))
for si in (0, 2):
    s, cost, pb = SOL[si]
    for n in (37, 33, 24):
        im = Image.open(U + FID[n] + '-image.jpg').convert('RGB')
        d = ImageDraw.Draw(im)
        for z, col in ((-60, (255, 0, 0)), (-80, (255, 200, 0)), (-100, (0, 255, 0)), (-120, (0, 200, 255)), (-140, (200, 0, 255))):
            for r in (90, 110, 130):
                pts = []
                for a in th:
                    uv, dep = project(pb, n, (r * np.cos(a), r * np.sin(a), z))
                    if dep > 0:
                        pts.append(tuple(uv))
                d.line(pts, fill=col, width=4 if r == 90 else 2)
        # the motor's board corners and the 5:05 hinge
        for X, col in (((46.8, -91.8, -109.5), (255, 0, 255)), ((62.5, -96.8, -111), (255, 255, 255))):
            uv, _ = project(pb, n, X)
            d.ellipse([uv[0] - 14, uv[1] - 14, uv[0] + 14, uv[1] + 14], outline=col, width=5)
        im.thumbnail((1000, 1000))
        im.save(f"/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap/rim_{n}_s{si}.jpg", quality=85)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib python3 s2rim.py