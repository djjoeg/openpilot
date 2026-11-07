cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && python3 - <<'EOF'
s = open('sfm.py').read()
s = s.replace("MIN_INL = 40", "MIN_INL = int(sys.argv[3]) if len(sys.argv) > 3 else 25")
# initial pair given on the command line
old = """    best = None
    for (a, b), (mm, Fm, n) in sorted(pairs.items(), key=lambda kv: -kv[1][2]):"""
new = """    best = None
    if INIT is not None:
        a, b = INIT
        key = (a, b) if (a, b) in pairs else (b, a)
        mm = pairs[key][0] if key == (a, b) else pairs[key][0][:, ::-1]
        best = (a, b, mm)
    for (a, b), (mm, Fm, n) in ([] if best else sorted(pairs.items(), key=lambda kv: -kv[1][2])):"""
assert old in s; s = s.replace(old, new)
s = s.replace("if not cand or cand[0][0] < 30:", "if not cand or cand[0][0] < 12:")
s = s.replace("if bestp is None or bestp[0] < 25:", "if bestp is None or bestp[0] < 10 or bestp[0] < 0.4 * n:")
old = """    pool = set(ids)
    clusters = []"""
new = """    from lm import ID
    nums = [int(x) for x in sys.argv[1].split(',')]
    pool = set(ID[n] for n in nums)
    ia, ib = [int(x) for x in sys.argv[2].split(',')]
    INIT = (ID[ia], ID[ib])
    clusters = []"""
assert old in s; s = s.replace(old, new)
s = s.replace("pickle.dump(dict(clusters=clusters, tracks=tracks), open('sfm.pkl', 'wb'))",
              "pickle.dump(dict(clusters=clusters, tracks=tracks), open(sys.argv[4] if len(sys.argv) > 4 else 'sfm.pkl', 'wb'))")
s = s.replace("        if c is None or len(c['cams']) < 2:\n            break", "        if c is None or len(c['cams']) < 2:\n            break\n        INIT = None")
s = s.replace("logf = open('sfm.log', 'w')", "logf = open('sfm_%s.log' % sys.argv[2].replace(',', '_'), 'w')")
open('sfm.py', 'w').write(s)
EOF
grep -n "INIT" sfm.py | head; python3 sfm.py 24,26,29,33,37 33,37 20 sfm_B.pkl 2>&1 | tail -30