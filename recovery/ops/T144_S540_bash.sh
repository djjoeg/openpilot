cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cat > camdesign.py <<'EOF'
"""2D design of the snap: a slider in the hinge block, its round nose pressed by a compression spring onto a cam on the
carrier. Carrier frame (y, z) about the hinge H. Lift L turns the carrier by -L about H."""
import math, sys
import numpy as np

H = np.array([50.0, -50.0])


def rot(v, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    v = np.asarray(v, float)
    return np.stack([c * v[..., 0] - s * v[..., 1], s * v[..., 0] + c * v[..., 1]], axis=-1)


def smooth(x0, x1, y0, y1, x):
    if x <= x0:
        return y0
    if x >= x1:
        return y1
    f = (1 - math.cos(math.pi * (x - x0) / (x1 - x0))) / 2
    return y0 + (y1 - y0) * f


def torque_target(L, p):
    """N mm, + towards on (resisting lift)."""
    if L <= p["L1"]:
        return p["T_on"]
    if L <= p["Lc"]:
        return smooth(p["L1"], p["Lc"], p["T_on"], 0.0, L)
    return smooth(p["Lc"], p["L2"], 0.0, -p["T_off"], L)


def design(p, verbose=False):
    gam = math.radians(p["gamma"])
    u = np.array([-math.cos(gam), math.sin(gam)])      # the spring pushes the nose this way
    w = np.array([u[1], -u[0]])                         # u turned -90: the side the axis is offset to (helps on)
    Ls = np.arange(p["Lmin"], p["Lmax"] + 1e-9, 0.05)
    s = np.zeros_like(Ls)
    F = lambda sv: p["F0"] + p["k"] * sv
    for i in range(1, len(Ls)):
        # midpoint integration of ds/dL = tau / F
        dL = math.radians(Ls[i] - Ls[i - 1])
        tm = torque_target((Ls[i] + Ls[i - 1]) / 2, p)
        s_mid = s[i - 1] + 0.5 * dL * tm / F(s[i - 1])
        s[i] = s[i - 1] + dL * tm / F(s_mid)
    lam = p["lam0"] + s
    Pn = H + p["e"] * w + lam[:, None] * (-u)           # nose centre, fixed frame
    Pc = H + rot(Pn - H, Ls[:, None] * 0 + Ls[:, None] * 1.0)[..., :] if False else None
    rel = Pn - H
    Pc = H + np.stack([rot(rel[i], Ls[i]) for i in range(len(Ls))])   # carrier frame
    # envelope: contact normal m (fixed frame) from the pitch curve's tangent in the carrier frame
    T = np.gradient(Pc, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    nC = np.stack([T[:, 1], -T[:, 0]], axis=1)          # one normal; flip to point from the nose to the cam
    # the cam lies towards the hinge side of the nose roughly along u (fixed) -> in the carrier frame u turned by +L
    u_c = np.stack([rot(u, Ls[i]) for i in range(len(Ls))])
    flip = np.sign(np.einsum("ij,ij->i", nC, u_c))
    nC *= flip[:, None]
    cam = Pc + p["rho"] * nC                             # contact points on the cam, carrier frame
    m_fixed = np.stack([rot(nC[i], -Ls[i]) for i in range(len(Ls))])
    alpha = np.degrees(np.arctan2(m_fixed[:, 0] * u[1] - m_fixed[:, 1] * u[0], m_fixed @ u))
    # pitch curve curvature (signed) in the carrier frame
    d1 = np.gradient(Pc, axis=0)
    d2 = np.gradient(d1, axis=0)
    k = (d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / np.linalg.norm(d1, axis=1) ** 3
    # sign: + when the pitch curve bends towards the cam (cam convex there)
    bend_to_cam = np.sign(np.einsum("ij,ij->i", np.stack([-d1[:, 1], d1[:, 0]], 1), nC))
    kc = k * bend_to_cam
    Rp = np.where(np.abs(kc) > 1e-9, 1 / kc, np.inf)    # + convex cam (pitch radius), - concave
    Rcam = Rp - p["rho"]                                 # the cam surface's radius (+ convex, - concave)
    Fs = F(s)
    N = Fs / np.cos(np.radians(alpha))
    E = 2000.0
    Es = E / (2 * (1 - 0.4 ** 2))
    Rstar = 1 / (1 / p["rho"] + 1 / np.where(np.abs(Rcam) > 1e-6, Rcam, 1e-6))
    p0 = np.sqrt(np.maximum(N * Es / (math.pi * p["width"] * np.maximum(Rstar, 1e-3)), 0))
    tau = np.array([torque_target(L, p) for L in Ls])
    out = dict(L=Ls, s=s, F=Fs, Pn=Pn, Pc=Pc, cam=cam, alpha=alpha, Rp=Rp, Rcam=Rcam, p0=p0, tau=tau, u=u, w=w)
    if verbose:
        for Lq in (p["Lmin"], -3, 0, 2, 5, 10, p["Lc"], 20, p["L2"], 45, 60, 75, p["Lmax"]):
            i = int(np.argmin(np.abs(Ls - Lq)))
            rc = np.linalg.norm(cam[i] - H)
            print(f"L {Ls[i]:6.1f}: tau {tau[i]:7.0f} Nmm  s {s[i]:5.2f}  F {Fs[i]:6.1f} N  alpha {alpha[i]:6.1f}  "
                  f"cam r {rc:5.1f} at {math.degrees(math.atan2(*(cam[i]-H)[::-1])):6.1f} deg  Rcam {Rcam[i]:7.1f}  p0 {p0[i]:5.1f} MPa")
        print("max |alpha| %.1f, min Rcam (convex) %.1f, most concave %.1f, max p0 %.1f" % (
            np.abs(alpha).max(), np.min(np.where(Rcam > 0, Rcam, np.inf)), np.max(np.where(Rcam < 0, Rcam, -np.inf)), p0.max()))
        print("stroke %.2f mm, F range %.0f-%.0f N" % (s.max() - s.min(), Fs.min(), Fs.max()))
    return out


P0 = dict(gamma=0.0, e=8.0, lam0=30.0, rho=6.0, width=15.0, F0=110.0, k=9.0, T_on=2150.0, T_off=600.0,
          L1=3.0, Lc=15.0, L2=27.0, Lmin=-6.0, Lmax=79.0)

if __name__ == "__main__":
    p = dict(P0)
    for a in sys.argv[1:]:
        k_, v = a.split("=")
        p[k_] = float(v)
    design(p, verbose=True)
EOF
PYTHONPATH=/home/claude/pylib python3 camdesign.py