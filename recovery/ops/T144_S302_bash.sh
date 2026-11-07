cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > rimpts.py <<'EOF'
import numpy as np, cv2
from grip_guided import guided
from lm import UP, ID, OUT
POLY = {
    26: [(680, 740), (800, 830), (870, 920), (882, 1000), (875, 1100), (855, 1200), (830, 1300), (795, 1400), (760, 1480),
         (715, 1580), (680, 1650), (620, 1740)],
    33: [(800, 680), (900, 730), (960, 780), (1010, 850), (1030, 920), (1040, 1000), (1042, 1100), (1030, 1180),
         (1010, 1260), (980, 1330), (950, 1380), (900, 1430)],
    24: [(600, 690), (833, 733), (1000, 752), (1167, 758), (1333, 752), (1500, 742), (1640, 705)],
    29: [(30, 880), (222, 889), (444, 911), (667, 922), (889, 911), (1111, 878), (1244, 822), (1278, 756), (1290, 600),
         (1295, 450), (1290, 300)],
}
R = {}
tiles = []
for n, poly in POLY.items():
    pts = guided(n, poly, step=15, reach=22, smooth=2.5, tmin=0.5)
    R[n] = pts
    im = cv2.imread(UP + ID[n] + '-image.jpg')
    cv2.polylines(im, [np.array(poly, np.int32).reshape(-1, 1, 2)], False, (255, 0, 0), 2)
    for p in pts: cv2.circle(im, (int(p[0]), int(p[1])), 4, (0, 255, 255), -1)
    xs, ys = np.array(poly)[:, 0], np.array(poly)[:, 1]
    x0, x1 = max(int(xs.min()) - 150, 0), min(int(xs.max()) + 150, im.shape[1])
    y0, y1 = max(int(ys.min()) - 150, 0), min(int(ys.max()) + 150, im.shape[0])
    t = im[y0:y1, x0:x1]
    s = 420 / t.shape[0]
    tiles.append(cv2.resize(t, None, fx=s, fy=s))
    print(n, len(pts))
cv2.imwrite(OUT + 'rims.jpg', np.hstack(tiles))
np.save('rim_pts.npy', R, allow_pickle=True)
EOF
python3 rimpts.py