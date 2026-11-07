python3 - <<'EOF'
p = "sideparts.py"
s = open(p).read()
def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:80], s.count(old))
    s = s.replace(old, new)
sub('''def lever_room(clear: float = 0.0) -> Manifold:
  """The lever's hub and arm (no knob) as fitted, motor out, out of the notch; grown by `clear` across and round."""
  px, py = PIVOT
  arm = box(px - KNOB_D, px, py - SHANK_W / 2 - clear, py + SHANK_W / 2 + clear, LEVER_Z[0], LEVER_Z[1])
  return arm + cyl(HUB_R + clear, LEVER_Z[0], LEVER_Z[1], x=px, y=py, segments=64)''',
'''def lever_room(clear: float = 0.0, z_clear: float = 0.0) -> Manifold:
  """The lever's hub and arm (no knob) as fitted, motor out, out of the notch; grown by `clear` across and round, and
  by `z_clear` along the shaft."""
  px, py = PIVOT
  z0, z1 = LEVER_Z[0] - z_clear, LEVER_Z[1] + z_clear
  arm = box(px - KNOB_D, px, py - SHANK_W / 2 - clear, py + SHANK_W / 2 + clear, z0, z1)
  return arm + cyl(HUB_R + clear, z0, z1, x=px, y=py, segments=64)''')
sub('''  """The lever's hub and arm swinging into either notch (the bracket's room for them, with the bracket's own s)."""
  return lever_swing(lever_room(clear), (0.0,))''', '''  """The lever's hub and arm swinging into either notch (the bracket's room for them, with the bracket's own s): out to
  the lugs' faces along the shaft, so no sliver of the bridge is left between them."""
  return lever_swing(lever_room(clear, LUG_GAP + 0.02), (0.0,))''')
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 600 python3 -c "
import sideparts as S
br = S.side_bracket(); lv = S.side_lever()
for a in (0.0, 21.0, 42.0):
  print(a, 'gap', round(S.lever_at(lv, 0.0, a).min_gap(br, 3.0), 3))
print('pieces', len(br.decompose()))
"