python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
old = '''TAB_KINDS = {"cup": {"end_r": 12.5, "head": (6.6, 4.0)}, "slim": {"end_r": 7.5, "head": (4.6, 5.0)}}'''
assert s.count(old) == 1
s = s.replace(old, '''TAB_KINDS = {"cup": {"end_r": 12.5, "head": (6.6, 4.0)}, "slim": {"end_r": 7.0, "head": (4.6, 5.0)}}''')
old = '''PL_SLOTS = ((52.0, -100.0, 52.0, -186.0), (28.0, -136.0, 28.0, -186.0), (-40.0, -198.0, 4.0, -198.0),
            (-57.0, -132.0, -57.0, -184.0))'''
assert s.count(old) == 1
s = s.replace(old, '''PL_SLOTS = ((52.0, -100.0, 52.0, -186.0), (28.0, -136.0, 28.0, -186.0), (-40.0, -198.0, 4.0, -198.0),
            (-57.0, -132.0, -57.0, -184.0), (20.0, -104.0, 44.0, -104.0))''')
p.write_text(s)
p = pathlib.Path("popassembly.py")
s = p.read_text()
old = '''          (TAB_ARM[0] - m, TAB_ARM[1] + 1.0, TAB_ARM[2] - m, TAB_ARM[3]),'''
assert s.count(old) == 1
s = s.replace(old, '''          (TAB_ARM[0] - m, TAB_ARM[1] + 0.5, TAB_ARM[2] - m, TAB_ARM[3]),''')
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib timeout 1500 python3 -c "
import time, collections; T0=time.time()
import numpy as np
import popparts as PP, popassembly as PA
s1 = [(38+fx*12, -98+fz*15) for fx in np.linspace(-1,1,5) for fz in np.linspace(-1,1,5)]
s3 = [(1+fx*4, -175+fz*15) for fx in np.linspace(-1,1,5) for fz in np.linspace(-1,1,5)]
miss = collections.Counter(); tot=0; ok=0
for a in s1:
  for b in s3:
    for dz in (-10.0, 0.0, 10.0):
      tot += 1
      try:
        PA.tab_placements([('s1', a, 'cup'), ('s3', b, 'slim')], (0.0, dz)); ok += 1
      except ValueError as e:
        miss[(str(e)[:30], round(a[0]), round(a[1]), round(b[0]), round(b[1]), dz)] += 1
print(tot, ok, round(time.time()-T0), 's')
for k, v in list(miss.items())[:20]: print(k, v)
for r in PA.tab_placements(): print(r[0], tuple(round(float(v),1) for v in r[3]), 'slot', r[4], r[5])
"