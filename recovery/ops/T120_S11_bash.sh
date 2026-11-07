cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/mockup && python3 - <<'EOF'
p='export.py'
s=open(p).read()
old='''def spoke(a_rim0, a_rim1, a_hub0, a_hub1, z0=-26.0, z1=-2.0) -> Manifold:
  r_rim, r_hub = t.rr - 2.0, 70.0
  pts = [(r_hub * math.cos(math.radians(a)), r_hub * math.sin(math.radians(a))) for a in np.linspace(a_hub0, a_hub1, 10)]
  pts += [(r_rim * math.cos(math.radians(a)), r_rim * math.sin(math.radians(a))) for a in np.linspace(a_hub1 + 0, a_hub1, 1)]
  rim = [(r_rim * math.cos(math.radians(a)), r_rim * math.sin(math.radians(a))) for a in np.linspace(a_rim1, a_rim0, 16)]'''
new='''def spoke(a_rim0, a_rim1, a_hub0, a_hub1, z0=-14.0, z1=4.0) -> Manifold:
  """A spoke from the hub (r 70, angles a_hub0 to a_hub1) to the grip's inner side (angles a_rim0 to a_rim1)."""
  r_rim, r_hub = t.rr - 12.0, 70.0
  pts = [(r_hub * math.cos(math.radians(a)), r_hub * math.sin(math.radians(a))) for a in np.linspace(a_hub0, a_hub1, 10)]
  rim = [(r_rim * math.cos(math.radians(a)), r_rim * math.sin(math.radians(a))) for a in np.linspace(a_rim1, a_rim0, 16)]'''
assert s.count(old)==1
s=s.replace(old,new)
s=s.replace('''  bottom = spoke(-80.0, -100.0, -75.0, -105.0, z0=-24.0, z1=-6.0)''','''  bottom = spoke(-80.0, -100.0, -75.0, -105.0, z0=-12.0, z1=2.0)''')
s=s.replace('''col = CA.ColumnAssembly.__new__(CA.ColumnAssembly)
''','')
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import manifold3d as m3
help(m3.Manifold.to_mesh)
" | grep -v "^$" | head -12