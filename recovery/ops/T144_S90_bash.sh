cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && python3 - <<'EOF'
import pickle, cv2, numpy as np
from lm import NUM
D = pickle.load(open('feats.pkl', 'rb'))
for i, f in D['f'].items():
    m = cv2.imread(f'masks/{NUM[i]:02d}_{i}.png', 0)
    p = f['pts'].astype(int)
    keep = m[np.clip(p[:, 1], 0, m.shape[0] - 1), np.clip(p[:, 0], 0, m.shape[1] - 1)] == 0
    for k in ('pts', 'des', 'size'):
        f[k] = f[k][keep]
pickle.dump(D, open('feats.pkl', 'wb'))
print('masked')
EOF
sed -i 's/^ids = \[i for i in D\[.ids.\] if i not in (.fc1c6691., .779484df., .31acc20e.)\]/ids = [i for i in D["ids"] if i not in ("fc1c6691", "779484df", "31acc20e")]/' match.py
grep -n "^ids" match.py
cp matches.pkl matches_unmasked.pkl
nohup python3 match.py > match.log 2>&1 &
echo started