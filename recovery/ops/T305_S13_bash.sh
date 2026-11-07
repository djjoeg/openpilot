cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/comp && cat > cam36.py <<'EOF'
import os, sys, pickle
import numpy as np
SFM = "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm"
sys.path.insert(0, SFM); _c = os.getcwd(); os.chdir(SFM)
import keyfit as KF
os.chdir(_c)
ROLL = np.radians(-10.35)
RZ = np.array([[np.cos(ROLL), -np.sin(ROLL), 0], [np.sin(ROLL), np.cos(ROLL), 0], [0, 0, 1]])
Rw, C = KF.wheel_from_cam36(KF.SOLS36[1])
R = Rw.T @ RZ.T          # car -> camera 36
t = np.asarray(C, float)
F = KF.F
EOF
PYTHONPATH=/home/claude/pylib:/home/claude/deliver/hardware/cad python3 - <<'EOF'
import sys; sys.path.insert(0, '/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/comp')
import numpy as np, math
import cam36 as C36
import photocomp as PC
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
cam = PC.PhotoCam(C36.R, C36.t, C36.F, (966.0, 1288.0), (1932, 2576))
print('camera 36 eye (car frame)', np.round(cam.eye, 1), 'f', C36.F)
U = '/root/.claude/uploads/29de5e81-e3b9-5428-a15c-fac1d206c0d4/'
base = ImageEnhance.Brightness(Image.open(U + 'edf19dda-image.jpg').convert('RGB')).enhance(1.5)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 14)
def P(x, y, z):
    u, v, w = cam.project(np.array([[x, y, z]]))
    return float(u[0]), float(v[0])
S = '/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/comp/'
full = base.copy(); d = ImageDraw.Draw(full)
for deg in range(-180, 180):
    a = math.radians(deg)
    r0 = 136.0 if deg % 5 == 0 else 144.0
    d.line([P(r0*math.cos(a), r0*math.sin(a), 0), P(150.6*math.cos(a), 150.6*math.sin(a), 0)], fill=(255, 60, 60) if deg % 5 == 0 else (255, 255, 0), width=2)
    if deg % 10 == 0:
        pt = P(124*math.cos(a), 124*math.sin(a), 0); d.text((pt[0]-14, pt[1]-8), str(deg), fill=(0, 255, 255), font=font)
for r, z, col in ((150.6, 0.0, (0, 255, 0)), (186.0, 0.0, (0, 160, 255))):
    d.line([P(r*math.cos(math.radians(q)), r*math.sin(math.radians(q)), z) for q in range(0, 361)], fill=col, width=1)
full.resize((966, 1288)).save(S + 'prot36_half.jpg', quality=88)
full.save(S + 'prot36.jpg', quality=92)
EOF