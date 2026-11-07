cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && python3 - <<'EOF'
s = open('jrun.py').read()
old = """    cv = cv_of(pb)
    nums = set(pb.cams)
    n_add = 0"""
new = """    cv = cv_of(pb)
    nums = set(pb.cams)
    n_add = 0
    have = {(c, k) for c, k, _, _ in pb.obs}"""
s = s.replace(old, new)
old = """        key = ('T', tid)
        pb.pts[key] = X
        for n, k in vs:
            pb.obs.append((n, key, FEATS[ID[n]]['pts'][k].astype(float), sigma))
        n_add += 1"""
new = """        key = ('T', tid)
        if key not in pb.pts:
            pb.pts[key] = X
            n_add += 1
        for n, k in vs:
            if (n, key) not in have:
                pb.obs.append((n, key, FEATS[ID[n]]['pts'][k].astype(float), sigma))"""
assert old in s
s = s.replace(old, new)
open('jrun.py', 'w').write(s)
EOF
timeout 3000 python3 jrun.py 2>&1 | tail -80