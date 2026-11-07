python3 - <<'EOF'
p='midteeth.py'; s=open(p).read()
a='''def mark_text(t: MidTeeth, text: str, deg0: float = 0.0) -> Manifold:
  """S.number_mark with any text, centred on deg0."""'''
assert a in s
s=s.replace(a,'''def mark_text(t: MidTeeth, text: str, deg0: float = 0.0, z0: float = S.MARK_Z0) -> Manifold:
  """S.number_mark with any text, centred on deg0, its bottom row at z0."""''')
a='''          z1 = S.MARK_Z0 + (5 - row) * S.MARK_PX'''
assert a in s
s=s.replace(a,'''          z1 = z0 + (5 - row) * S.MARK_PX''')
a='''  return clean(body - mark_text(t, str(round(pull))))


def build_fit_tests'''
assert a in s
s=s.replace(a,'''  return clean(body - mark_text(t, str(round(pull)), z0=-10.5))     # on the outer wall's flat outside


def build_fit_tests''')
open(p,'w').write(s)
EOF
export PYTHONPATH=/home/claude/pylib && timeout 300 python3 -c "
import midteeth as MT, render as R
m = MT.fit_sample(); b = MT.on_bed(m)
print('g solid', round(m.volume()/1000*1.28,1), 'genus', m.genus(), [round(x,1) for x in b.bounding_box()])
R.save('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v3d/sample.png', [([(m,(0.89,0.58,0.27))], R.view_matrix(-20, 15)), ([(m,(0.89,0.58,0.27))], R.view_matrix(160, 20)), ([(b,(0.89,0.58,0.27))], R.view_matrix(-50, 35))], titles=['from the outer side','from the inner side','as printed'], cols=3, size=(600,500))
" && ls -la /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v3d/sample.png