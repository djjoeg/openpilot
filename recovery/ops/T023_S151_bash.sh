python3 - <<'EOF'
p = "mountparts.py"
s = open(p).read()
old = '''  ly2, lz2 = LEVER_PIVOT
  lugs = []
  for sgn in (-1, 1):
    x0, x1 = (LEVER_X + GAP, LEVER_X + GAP + 6.0) if sgn > 0 else (-LEVER_X - GAP - 6.0, -LEVER_X - GAP)
    lugs.append(cyl_x(6.5, x0, x1, y=ly2, z=lz2) + box(x0, x1, ly2, HB_BOTTOM + 0.5, lz2 - 6.5, lz2 + 6.5))
  # microswitch seat: a plate hanging below the block; the switch's lever reaches down onto the carrier's top
  seat = box(SWITCH_X[0] - 3.0, SWITCH_X[0], HB_BOTTOM - 10.0, HB_BOTTOM + 0.5, SWITCH_Z - 9.0, SWITCH_Z + 9.0)
  part = body + union(kn) + union(ears) + union(bridge) + union(lugs) + seat'''
new = '''  ly2, lz2 = LEVER_PIVOT     # the lever turns in a slot through the block; the block's sides hold its pivot bolt
  # microswitch seat: a plate hanging below the block; the switch's lever reaches down onto the carrier's top
  seat = box(SWITCH_X[0] - 3.0, SWITCH_X[0], HB_BOTTOM - 10.0, HB_BOTTOM + 0.5, SWITCH_Z - 9.0, SWITCH_Z + 9.0)
  part = body + union(kn) + union(ears) + union(bridge) + seat'''
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)
EOF
export PYTHONPATH=/home/claude/pylib:. && timeout 900 python3 -c "
import mountparts as MP
h = MP.hinge_block(); print('hinge block', h.status(), round(h.volume()/1000,2), h.genus(), len(h.decompose()))
c = MP.dash_clamp()
for comp in sorted(c.decompose(), key=lambda m: -m.volume()):
  print('clamp comp', round(comp.volume(),2), [round(v,1) for v in comp.bounding_box()])
"
