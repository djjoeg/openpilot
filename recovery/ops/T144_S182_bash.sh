cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat >> jba.py <<'EOF'


def lm_solve(pb, iters=30, delta=1.5, verbose=True, lam0=1e-2):
    """Damped Gauss-Newton with Huber weights (re-weighted each step) and a sparse finite-difference Jacobian."""
    from scipy.optimize._numdiff import approx_derivative
    from scipy.sparse import diags
    from scipy.sparse.linalg import spsolve
    pb._prepare()
    x = pb.pack()
    r = pb.residuals(x)
    S = pb.sparsity(len(r))

    def rcost(r):
        a = np.abs(r)
        return np.where(a <= delta, 0.5 * r ** 2, delta * (a - 0.5 * delta)).sum()

    cost = rcost(r)
    lam = lam0
    for it in range(iters):
        J = approx_derivative(pb.residuals, x, method='2-point', sparsity=S, f0=r).tocsr()
        a = np.abs(r)
        w = np.where(a <= delta, 1.0, np.sqrt(delta / np.maximum(a, 1e-12)))
        Jw = diags(w) @ J
        H = (Jw.T @ Jw).tocsc()
        g = Jw.T @ (w * r)
        dg = H.diagonal()
        improved = False
        for _ in range(12):
            A = H + diags(lam * (dg + 1e-9))
            dx = spsolve(A.tocsc(), -g)
            xn = x + dx
            rn = pb.residuals(xn)
            cn = rcost(rn)
            if cn < cost:
                x, r = xn, rn
                rel = (cost - cn) / cost
                cost = cn
                lam = max(lam / 3.0, 1e-7)
                improved = True
                break
            lam *= 6.0
        if verbose:
            print('   it %2d cost %.1f lam %.1e %s' % (it, cost, lam, '' if improved else '(no step)'), flush=True)
        if not improved or rel < 1e-6:
            break
    pb.unpack(x)
    return cost
EOF
timeout 1800 python3 - 2>&1 <<'EOF' | grep -v "^camera\|^landmarks\|^  landmark"
import numpy as np
import jinit, jrun
from jba import lm_solve
pb, L3 = jinit.build()
jrun.add_landmarks(pb)
jrun.add_bezel(pb)
jrun.add_tracks(pb)
lm_solve(pb, iters=25)
jrun.report(pb)
EOF