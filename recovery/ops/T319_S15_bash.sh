cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fea && python3 - <<'EOF'
s = open('armfea.py').read()
old = '''    import re
    depth = float(re.match(r"deep(\\d*)", variant).group(1) or 50)
    z1 = RA.ARM_Z[0] + depth
    blk = box(120.5, 150.0, RA.ARM_Y[0], RA.ARM_Y[1], RA.ARM_Z[0], z1)
    tw = RA.uvz(RA.TOWER_U[0], RA.TOWER_U[1], RA.TOWER_V[0], RA.TOWER_V[1], RA.ARM_Z[0], z1)
    web = Manifold.batch_hull([blk, tw]) ^ box(120.5, 400.0, -400.0, RA.ARM_Y[1], RA.ARM_Z[0], z1)'''
new = '''    import re
    mm = re.match(r"deep(\\d*)(?:@([\\d.]+))?", variant)
    depth = float(mm.group(1) or 50)
    x0 = float(mm.group(2) or 120.5)
    z1 = RA.ARM_Z[0] + depth
    blk = box(x0, 150.0, RA.ARM_Y[0], RA.ARM_Y[1] - 1.0, RA.ARM_Z[0], z1)
    tw = RA.uvz(RA.TOWER_U[0], RA.TOWER_U[1], RA.TOWER_V[0], RA.TOWER_V[1], RA.ARM_Z[0], z1)
    web = Manifold.batch_hull([blk, tw]) ^ box(x0, 400.0, -400.0, RA.ARM_Y[1] - 1.0, RA.ARM_Z[0], z1)'''
assert s.count(old) == 1
s = s.replace(old, new)
open('armfea.py', 'w').write(s)
EOF
for v in "deep50@120.5" "deep50@125.5" "deep50@130.5"; do echo "== $v"; PYTHONPATH=/home/claude/pylib timeout 900 python3 armfea.py 2.0 1800 "$v" 2>&1 | grep -E "^left|^right" | sed -E 's/F_t [0-9.]+ N, F_s [0-9.]+ N -> the gear.s pitch point moves: //'; done