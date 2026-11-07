python3 - << 'EOF'
p = "mountparts.py"
s = open(p).read()
rep = [
("REST_D = (14.0, HANDLE_LEN + 1.0)     # the rest under the handle, from/to this far from the pivot",
 "REST_D = (14.0, HANDLE_LEN + 4.0)     # the rest under the handle, from/to this far from the pivot"),
("SW_D = 28.0                           # switch's middle, this far from the pivot along the handle",
 "SW_D = 32.0                           # switch's middle, this far from the pivot along the handle"),
("  cy0 = SW_HOLES - 8.5\n", "  cy0 = SW_HOLES - 6.0\n"),
("""def stop_bar_corner() -> np.ndarray:
  \"\"\"Where the handle's top face, 11 mm from the pivot, is when the lever reaches A_HARD_STOP.\"\"\"
  return _lever_frame_point(HANDLE_T / 2 + 0.2, -11.0, A_HARD_STOP)
""",
"""def stop_bar() -> CrossSection:
  \"\"\"The bar the handle's top face meets when the lever reaches A_HARD_STOP, (y, z) in the hinge block's frame.\"\"\"
  ht = HANDLE_T / 2
  pts = [_lever_frame_point(y, z, A_HARD_STOP) for y, z in ((ht + 0.05, -9.0), (ht + 0.05, -15.0), (ht + 4.5, -15.0), (ht + 4.5, -9.0))]
  return CrossSection([[(float(q[0]), float(q[1])) for q in pts]])
"""),
("""  c = stop_bar_corner()
  bar = rect_yz(float(c[0]), float(c[0]) + 4.0, float(c[1]) - 5.0, float(c[1]))
""", """  bar = stop_bar()
"""),
("  tail = box(-TAIL_X, TAIL_X, TOP_Y[0], TOP_Y[1], vz - FIN_LEN / 2 - 2.0, BLOCK_BACK + 0.01)",
 "  tail = box(-TAIL_X, TAIL_X, TOP_Y[0], TOP_Y[1], vz - FIN_LEN / 2 - 0.5, BLOCK_BACK + 0.01)"),
]
for a, b in rep:
  assert a in s, a[:60]
  s = s.replace(a, b)
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/cadwork/check.py 2>&1 | grep -v " 0.000  "