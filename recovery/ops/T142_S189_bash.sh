python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
old = '''            (-57.0, -132.0, -57.0, -184.0), (18.0, -117.0, 40.0, -117.0))'''
assert s.count(old) == 1
s = s.replace(old, '''            (-57.0, -132.0, -57.0, -184.0), (18.0, -117.0, 40.0, -117.0), (19.0, -100.0, 35.0, -100.0))''')
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib timeout 3000 python3 -c "
import time; T0 = time.time()
import popassembly as PA
for r in PA.tab_placements(): print(r[0], tuple(round(float(v),1) for v in r[3]), r[4], r[5])
res = PA.tab_fit_study(n=5)
print(res['cases'], res['fit'], res['misses'][:3], round(time.time() - T0), 's')
"