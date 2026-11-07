cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && python3 - <<'EOF'
import re
src = open("camdesign.py").read()
src = src.replace('''def torque_target(L, p):
    """N mm, + towards on (resisting lift)."""
    if L <= p["L1"]:
        return p["T_on"]
    if L <= p["Lc"]:
        return smooth(p["L1"], p["Lc"], p["T_on"], 0.0, L)
    return smooth(p["Lc"], p["L2"], 0.0, -p["T_off"], L)''', '''def _trap(L, p):
    """Linear segments: T_on to L1, straight down through 0 at Lc to -T_off at L2, then -T_off."""
    if L <= p["L1"]:
        return p["T_on"]
    if L >= p["L2"]:
        return -p["T_off"]
    if L <= p["Lc"]:
        return p["T_on"] * (p["Lc"] - L) / (p["Lc"] - p["L1"])
    return -p["T_off"] * (L - p["Lc"]) / (p["L2"] - p["Lc"])


def torque_target(L, p):
    """N mm, + towards on (resisting lift): the trapezoid, its corners rounded by averaging over +-blend degrees."""
    b = p.get("blend", 0.0)
    if b <= 0:
        return _trap(L, p)
    xs = np.linspace(L - b, L + b, 21)
    wts = np.cos(np.linspace(-np.pi / 2, np.pi / 2, 21)) ** 2
    return float(np.sum([_trap(x, p) * w for x, w in zip(xs, wts)]) / wts.sum())''')
src = src.replace('P0 = dict(gamma=0.0, e=8.0, lam0=30.0, rho=6.0, width=15.0, F0=110.0, k=9.0, T_on=2150.0, T_off=600.0,\n          L1=3.0, Lc=15.0, L2=27.0, Lmin=-6.0, Lmax=79.0)',
 'P0 = dict(gamma=0.0, e=10.0, lam0=30.0, rho=8.0, width=18.0, F0=100.0, k=11.506, T_on=2200.0, T_off=600.0,\n          L1=3.0, Lc=24.0, L2=34.0, Lmin=-6.0, Lmax=79.0, blend=2.0)')
src = src.replace('for Lq in (p["Lmin"], -3, 0, 2, 5, 10, p["Lc"], 20, p["L2"], 45, 60, 75, p["Lmax"]):', 'for Lq in (p["Lmin"], -3, 0, 3, 6, 10, 15, 20, p["Lc"], p["L2"], 45, 60, 75, p["Lmax"]):')
open("camdesign.py", "w").write(src)
EOF
for args in "" "e=12" "e=12 lam0=34" "e=10 lam0=34 Lc=22 L2=32" "rho=7 e=12 lam0=34"; do echo "== $args"; PYTHONPATH=/home/claude/pylib python3 camdesign.py $args | tail -16; done