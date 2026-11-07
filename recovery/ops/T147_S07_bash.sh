cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cat > s2rigid.py <<'EOF'
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
from s2load import *
def lm(pb):
    P = {k[1]: to_car(v) for k, v in pb.pts.items() if k[0] == "L"}
    P["B"] = to_car(pb.pts[("B", "outer")])
    return P
A, B = lm(SOL[0][2]), lm(SOL[2][2])
keys = [k for k in ("KS1", "KS2", "PU", "CUP", "B", "SH", "RH") if k in A and k in B]
print(keys)
X = np.array([A[k] for k in keys]); Y = np.array([B[k] for k in keys])
# similarity fit Y = s R X + t
mx, my = X.mean(0), Y.mean(0)
Xc, Yc = X - mx, Y - my
U, S, Vt = np.linalg.svd(Yc.T @ Xc)
D = np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))])
R = U @ D @ Vt
s = (S * np.diag(D)).sum() / (Xc ** 2).sum()
t = my - s * R @ mx
ang = np.degrees(np.arccos((np.trace(R) - 1) / 2))
print("scale %.3f  rotation %.1f deg  axis %s" % (s, ang, np.round(np.array([R[2,1]-R[1,2], R[0,2]-R[2,0], R[1,0]-R[0,1]]) / (2*np.sin(np.radians(ang))+1e-12), 2)))
for k in keys:
    print("  %-4s A %s B %s  fit err %.1f" % (k, np.round(A[k], 1), np.round(B[k], 1), np.linalg.norm(s * R @ A[k] + t - B[k])))
# rigid only (s = 1)
t1 = my - R @ mx
print("rigid errors:", {k: round(float(np.linalg.norm(R @ A[k] + t1 - B[k])), 1) for k in keys})
print("translation of the key centre:", np.round(B["B"] - A["B"], 1))
EOF
PYTHONPATH=/home/claude/pylib python3 s2rigid.py