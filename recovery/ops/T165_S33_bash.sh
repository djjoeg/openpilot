python3 - <<'EOF'
p = "sideassembly.py"
s = open(p).read()
def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:80], s.count(old))
    s = s.replace(old, new)
sub('''  """Motor in, the steering wheel turned through and past the teeth piece: the teeth piece against everything but the
  gear; the gear (free past the teeth: any phase) against the teeth piece past the last tooth."""
  t = A.t
  res = {}
  mv = {k: A.W(v) for k, v in A.movers(0.0).items() if k != "gear"}''',
'''  """Motor in, the steering wheel turned through and past the teeth piece: the teeth piece against everything but the
  gear (the lever latched, and in its slot as when you latch it); the gear (free past the teeth: any phase) against the
  teeth piece past the last tooth."""
  t = A.t
  res = {}
  mv = {k: A.W(v) for k, v in A.movers(0.0, lever_deg=0.0).items() if k != "gear"}
  mv["lever, in its slot"] = A.W(A.movers(0.0)["lever"])''')
sub('''  for name, part in A.movers(S.STROKE).items():
    P_ = A.W(part)
    res[f"slid in: teeth piece anywhere round/{name}"] = overlap(ring, P_)''', '''  slid = A.movers(S.STROKE)
  slid["lever, parked"] = A.movers(S.STROKE, lever_deg=0.0)["lever"]
  for name, part in slid.items():
    P_ = A.W(part)
    res[f"slid in: teeth piece anywhere round/{name}"] = overlap(ring, P_)''')
sub('''  for s, tag in ((0.0, "motor in"), (S.STROKE, "slid in")):
    for name, part in A.movers(s).items():
      if name == "gear" and s == 0.0:
        continue
      P_ = A.W(part)
      rows.append((tag, name, "teeth piece anywhere round", gap(P_, ring)))
      if s == S.STROKE:
        rows.append((tag, name, "your fingers' room", gap(P_, fingers)))''',
'''  for s, deg, tag in ((0.0, 0.0, "motor in"), (S.STROKE, S.SLOT_DEG, "slid in"), (S.STROKE, 0.0, "parked")):
    for name, part in A.movers(s, lever_deg=deg).items():
      if (name == "gear" and s == 0.0) or (tag == "parked" and name != "lever"):
        continue
      P_ = A.W(part)
      rows.append((tag, name, "teeth piece anywhere round", gap(P_, ring)))
      if s == S.STROKE or name == "lever":
        rows.append((tag, name, "your fingers' room", gap(P_, fingers)))''')
open(p, "w").write(s)
EOF
/home/claude/bin/ruff check --isolated --select E4,E7,E9,F --line-length 140 sideassembly.py