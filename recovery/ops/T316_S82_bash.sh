python3 - <<'EOF'
p='visuals.py'; s=open(p).read()
a='''def hardware(dz: float = 0.0, off=(0.0, 0.0, 0.0)) -> list:
  """The three wing bolts and their four nuts, in the steering wheel frame, the motor slid dz from its stop; the
  carrier's own (the stop bolt and its nuts) moved by off as well."""
  out = []
  for name, m in RC.hardware(dz, RA.STOP_GAP).items():
    out.append((m.translate(off) if name.startswith("stop") else m, STEEL))
  return out'''
assert a in s
s=s.replace(a,'''def hardware(dz: float = 0.0, off=(0.0, 0.0, 0.0), stop_too: bool = True) -> list:
  """The wing bolts, the stop and the nuts, in the steering wheel frame, the motor slid dz from its stop; the
  carrier's own (the M4 stop: bolt, washer and nuts) moved by off as well, unless stop_too is False (then it waits
  where it goes, below the tower)."""
  out = []
  for name, m in RC.hardware(dz, RA.STOP_GAP).items():
    out.append((m.translate(off) if name.startswith("stop") and stop_too else m, STEEL))
  return out''')
a='''def assembly_parts(with_grip: bool = True, dz: float = 0.0, off=(0.0, 0.0, 0.0)) -> list:'''
assert a in s
s=s.replace(a,'''def assembly_parts(with_grip: bool = True, dz: float = 0.0, off=(0.0, 0.0, 0.0), stop_too: bool = True) -> list:''')
a='''    [(m.translate(off), c) for m, c in mov] + hardware(dz, off)'''
assert a in s
s=s.replace(a,'''    [(m.translate(off), c) for m, c in mov] + hardware(dz, off, stop_too)''')
a='''  bench = [p for p in assembly_parts(with_grip=False, dz=RA.DZ_OUT, off=off) if p[1] is not PLATE]'''
assert a in s
s=s.replace(a,'''  bench = [p for p in assembly_parts(with_grip=False, dz=RA.DZ_OUT, off=off, stop_too=False) if p[1] is not PLATE]''')
open(p,'w').write(s)
EOF
ruff check visuals.py --output-format concise && export PYTHONPATH=/home/claude/pylib && timeout 600 python3 -c "
import visuals as V, os
V.slide_picture(os.path.join(V.REPORT_DIR, 'review-1b-slide.png'))
" && echo ok