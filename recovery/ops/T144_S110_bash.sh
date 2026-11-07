cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat >> asift_test.py <<'EOF'

def draw(a, b, name):
    n, (g, inl) = match(F[a], F[b])
    ia = cv2.imread(UP + ID[a] + '-image.jpg'); ib = cv2.imread(UP + ID[b] + '-image.jpg')
    s = 0.35
    ia = cv2.resize(ia, None, fx=s, fy=s); ib = cv2.resize(ib, None, fx=s, fy=s)
    H = max(ia.shape[0], ib.shape[0])
    canvas = np.zeros((H, ia.shape[1] + ib.shape[1], 3), np.uint8)
    canvas[:ia.shape[0], :ia.shape[1]] = ia; canvas[:ib.shape[0], ia.shape[1]:] = ib
    pa, pb = F[a][0], F[b][0]
    for (qa, qb), ok in zip(g, inl.ravel()):
        if not ok: continue
        p = tuple(int(v) for v in pa[qa] * s); q = tuple(int(v) for v in pb[qb] * s + np.array([ia.shape[1], 0]))
        col = tuple(int(c) for c in np.random.randint(80, 255, 3))
        cv2.line(canvas, p, q, col, 1); cv2.circle(canvas, p, 4, col, 2); cv2.circle(canvas, q, 4, col, 2)
    cv2.imwrite(name, canvas)
draw(26, 7, 'look/as_26_7.jpg'); draw(21, 7, 'look/as_21_7.jpg')
EOF
sed -i 's/^for a, b in ((26, 7), (26, 9), (33, 7), (26, 21), (21, 7), (33, 21)):/for a, b in ():/' asift_test.py
sed -i 's/^F = {n: feats(n) for n in (26, 33, 7, 9, 21)}/F = {n: feats(n) for n in (26, 7, 21)}/' asift_test.py
timeout 900 python3 asift_test.py