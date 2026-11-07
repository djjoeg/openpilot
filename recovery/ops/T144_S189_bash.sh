cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && python3 - <<'EOF'
s = open('jba.py').read()
old = """        # distances
        for a, b, L, sig in self.dists:"""
new = """        self.n_robust = sum(len(o) for o in out)
        # distances
        for a, b, L, sig in self.dists:"""
assert old in s; s = s.replace(old, new)
old = """        a = np.abs(r)
        w = np.where(a <= delta, 1.0, np.sqrt(delta / np.maximum(a, 1e-12)))
        Jw = diags(w) @ J"""
new = """        a = np.abs(r)
        w = np.where(a <= delta, 1.0, np.sqrt(delta / np.maximum(a, 1e-12)))
        w[pb.n_robust:] = 1.0
        Jw = diags(w) @ J"""
assert old in s; s = s.replace(old, new)
old = """    def rcost(r):
        a = np.abs(r)
        return np.where(a <= delta, 0.5 * r ** 2, delta * (a - 0.5 * delta)).sum()"""
new = """    def rcost(r):
        a = np.abs(r)
        c = np.where(a <= delta, 0.5 * r ** 2, delta * (a - 0.5 * delta))
        c[pb.n_robust:] = 0.5 * r[pb.n_robust:] ** 2
        return c.sum()"""
assert old in s; s = s.replace(old, new)
open('jba.py', 'w').write(s)
EOF
timeout 3000 python3 brun.py 2>&1 | tail -90