cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/popmock && python3 - <<'EOF'
import pathlib
p = pathlib.Path("pop_export.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)
rep('''A = PA.PopAssembly(t15, {"teeth": short_piece, "tab": PP.pop_screw_tab(), "plate": plate})''',
'''A = PA.PopAssembly(t15, {"teeth": short_piece, "tab_cup": PP.pop_screw_tab("cup"), "tab_slim": PP.pop_screw_tab("slim"),
                         "plate": plate})''')
rep('''def tilt_lever() -> Manifold:
  """The adjustment tab tucked up under the column (rough, from the photos): its handle and the steel arm behind it."""
  handle = Manifold.batch_hull([box(-41.0, 3.0, -61.0, -50.0, -118.0, -66.0), cyl(5.5, -66.0, -60.0, -19.0, -56.0, 24).rotate((0, 0, 0))])
  handle = box(-41.0, 3.0, -61.0, -50.0, -118.0, -62.0) + box(-41.0, 3.0, -64.0, -58.0, -66.0, -60.0)
  arm = box(-26.0, -12.0, -55.0, -50.0, -186.0, -116.0)
  return handle + arm''',
'''def tilt_lever() -> Manifold:
  """The adjustment tab (rough, from the photos): its paddle and the steel arm back to its pivot, as the checks have them,
  the paddle's edges rounded a little for the picture."""
  x0, x1, z0, z1 = PA.TAB_PADDLE
  y0, y1 = PA.TAB_PADDLE_Y
  r = 3.0
  paddle = Manifold.batch_hull([cyl_x(r, x0 + r, x1 - r, y=y0 + r, z=z1 - r, segments=16), cyl_x(r, x0 + r, x1 - r, y=y1 - r, z=z1 - r, segments=16),
                                box(x0, x1, y0 + r, y1, z0, z1 - r), box(x0 + r, x1 - r, y0, y1, z0, z1 - r)])
  a0, a1, c0, c1 = PA.TAB_ARM
  arm = box(a0, a1, PA.TAB_ARM_Y[0], PA.TAB_ARM_Y[1], c0, c1)
  return paddle + arm''')
rep('''  ("tilt_lever", "car", "lever", tilt_lever()),''', '''  ("tilt_lever", "lever", "lever", tilt_lever()),''')
rep('''  ("tabs", "world", "tab", A.tabs()),''', '''  ("tabs", "world", "tab", A.tabs()),
  ("pad", "world", "foam", A.pad()),''')
rep('''  "stalk_down": PA.STALK_DOWN_DEG,''', '''  "stalk_down": PA.STALK_DOWN_DEG,
  "tab_pivot": [0.0, PA.TAB_PIVOT[0], PA.TAB_PIVOT[1]], "tab_swing": PA.TAB_SWING,''')
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib timeout 3000 python3 pop_export.py . 2>&1 | tail -12