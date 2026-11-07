cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && cat > adj.py <<'EOF'
import sys, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import slideassembly as SA, slideparts as SP
T0 = time.time()
D = float(sys.argv[1])
for m in [float(v) for v in sys.argv[2].split(",")]:
  A = SA.SlideAssembly(D, m)
  car = dict(A.car_parts())
  cov, tab = car["column cover"], car["adjustment tab, its swing and your fingers on it"]
  dm = SA.drop_most()
  row = []
  for name, part in (("motor on", A.motor()), ("motor off", A.motor(SP.STROKE)), ("motor 1.1 on", A.motor(-dm))):
    row.append(f"{name}: cover {SA.min_gap(part, cov)} tab {SA.min_gap(part, tab)}")
  pl = A.plate()
  for name, part in (("rods on", A.rods()), ("rods off", A.rods(SP.STROKE)), ("springs on", A.springs()), ("springs off", A.springs(SP.STROKE)), ("block", A.block())):
    row.append(f"{name}/plate {SA.min_gap(part, pl)}")
  print(f"D {D} mount {m}: " + "; ".join(row), round(time.time()-T0,1), flush=True)
EOF
export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache
(timeout 900 python3 adj.py 110 -73,-72,-71,-70 > adj_110a.txt 2>&1 &) ; timeout 900 python3 adj.py 110 -69,-68,-67 > adj_110b.txt 2>&1; sleep 1; cat adj_110a.txt adj_110b.txt