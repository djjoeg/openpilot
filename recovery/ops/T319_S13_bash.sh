cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fea && python3 - <<'EOF'
s = open('armfea.py').read()
old = '''    depth = float(variant[4:] or 50)'''
new = '''    import re
    depth = float(re.match(r"deep(\\d*)", variant).group(1) or 50)'''
assert s.count(old) == 1
s = s.replace(old, new)
# an iterative solve when asked (memory-light), else the direct one
old2 = '''  print(f"free dof {len(fd)}; factorizing ... {time.time() - t0:.0f} s")
  lu = spla.splu(Kf, permc_spec="COLAMD")
  print(f"factorized; {time.time() - t0:.0f} s")
'''
new2 = '''  print(f"free dof {len(fd)}; factorizing ... {time.time() - t0:.0f} s")
  if "cg" in sys.argv[4:5]:
    Kc = Kf.tocsr()
    dinv = 1.0 / Kc.diagonal()
    Mpre = spla.LinearOperator(Kc.shape, matvec=lambda x: dinv * x)

    class _CG:
      def solve(self, b):
        it = [0]
        x, info = spla.cg(Kc, b, rtol=1e-9, maxiter=60000, M=Mpre, callback=lambda xk: it.__setitem__(0, it[0] + 1))
        print(f"   cg: {it[0]} iterations, info {info}, {time.time() - t0:.0f} s")
        return x
    lu = _CG()
  else:
    lu = spla.splu(Kf, permc_spec="COLAMD")
  print(f"factorized; {time.time() - t0:.0f} s")
'''
assert s.count(old2) == 1
s = s.replace(old2, new2)
open('armfea.py', 'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 armfea.py 2.0 1800 deep50flange 2>&1 | grep -E "voxels|left|right"