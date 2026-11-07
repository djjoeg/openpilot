cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > picksB.py <<'EOF'
"""Careful picks in the key photos (full-res px, sigma px). RH: hole in the steering wheel's back cover (right side).
SH: centre of the opening in the column cover where the wiper stalk goes in. ST: centre of the stalk's end face.
PU: centre of the embossed PUSH mark beside the key. CUP: the screw cup under the key. KS1/KS2: the key slot's ends."""
PB = {
    24: {'RH': (952, 547, 5), 'SH': (1697, 942, 12), 'ST': (2415, 745, 12), 'PU': (1410, 1255, 6)},
    26: {'RH': (443, 1553, 5), 'SH': (1195, 960, 12), 'ST': (1322, 140, 10), 'PU': (1350, 1322, 5),
         'KS1': (1066, 1410, 5), 'KS2': (1121, 1459, 5)},
    33: {'RH': (703, 1345, 5), 'SH': (1295, 790, 12), 'PU': (1497, 1110, 5), 'CUP': (1080, 1680, 6),
         'KS1': (1250, 1217, 5), 'KS2': (1303, 1266, 5)},
    37: {'SH': (1305, 620, 12), 'PU': (1505, 1045, 5), 'CUP': (972, 1588, 6), 'KS1': (1237, 1107, 5),
         'KS2': (1285, 1150, 5)},
}
EOF
cat > brun3.py <<'EOF'
"""Key photos in mm: SIFT tracks + bezel rings + careful picks, focal lengths near the main camera's."""
import pickle, sys
import numpy as np
import brun
from picksB import PB
from jba import Problem, lm_solve, angles_from_unit, unit_from_angles
from lm import ID, NUM, centre, load, triangulate
F0 = float(sys.argv[1]) if len(sys.argv) > 1 else 1917.0
FS = float(sys.argv[2]) if len(sys.argv) > 2 else 40.0
brun.P.clear()
brun.P.update(PB)
S = load('sfm_B2.pkl')['clusters'][0]
pb = Problem()
for i, (rv, t, f) in S['cams'].items():
    pb.cams[NUM[i]] = dict(rv=np.array(rv, float), t=np.array(t, float) * 23.5, f=F0, fprior=(F0, FS), c=centre(i))
brun.add_all(pb)
lm_solve(pb, iters=20, verbose=False)
brun.prune(pb)
for n in (37, 33):
    brun.pnp(pb, n, fs=(F0,))
    pb.cams[n]['fprior'] = (F0, FS)
    brun.add_all(pb)
    lm_solve(pb, iters=25, verbose=False)
    brun.prune(pb)
    lm_solve(pb, iters=15, verbose=False)
lm_solve(pb, iters=40, verbose=False)
brun.report(pb, worst=25)
L = {k[1]: v for k, v in pb.pts.items() if k[0] == 'L'}
bz = pb.pts[('B', 'outer')]
nrm = unit_from_angles(*pb.circles['outer']['ang'])
for k, v in sorted(L.items()):
    d = v - bz
    print('  %-4s from bezel %s  |%.1f|  along normal %.1f' % (k, np.round(d, 1), np.linalg.norm(d), d @ nrm))
if 'ST' in L and 'SH' in L:
    print('stalk SH->ST %.1f mm' % np.linalg.norm(L['ST'] - L['SH']))
pickle.dump(pb, open('b3_%d.pkl' % int(F0), 'wb'))
EOF
for f in 1917 1796; do echo "== f $f"; timeout 1500 python3 brun3.py $f 30 2>&1 | tail -32; done