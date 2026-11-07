python3 - <<'EOF'
p = "sideassembly.py"
s = open(p).read()
old = '''  rub = MG.RUB_DRY                                       # printed lever on the printed notch, dry'''
new = '''  import margins as MG
  rub = MG.RUB_DRY                                       # printed lever on the printed notch, dry'''
assert s.count(old) == 1
s = s.replace(old, new)
open(p, "w").write(s)
EOF
/home/claude/bin/ruff check --isolated --select E4,E7,E9,F --line-length 140 sideassembly.py && PYTHONPATH=/home/claude/pylib timeout 900 python3 - <<'EOF'
import time, json
t0 = time.time()
import sideassembly as SA
A = SA.SideAssembly()
print("parts", round(time.time() - t0), "s")
print(json.dumps(SA.forces(), indent=1))
print(json.dumps(SA.lever_notches(A), indent=1, default=str))
print("t", round(time.time() - t0), "s")
r = SA.internal(A)
bad = {k: v for k, v in r.items() if v[0] > 1e-3}
print("internal over 0.001:", bad)
print("t", round(time.time() - t0), "s")
print(SA.touching_at_stops(A))
for row in SA.side_margins():
  print(row["what"], row["factor"], row["status"], "|", row["load"])
EOF