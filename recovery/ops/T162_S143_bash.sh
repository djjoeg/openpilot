python3 - <<'EOF'
p = "sideparts.py"
s = open(p).read()
old = '''POST = ((X_RAIL_BOT, -24.0), (20.0, SPOOL_Y[0] - 0.4), (SPOOL_Z - 8.0, SPOOL_Z + 8.0))'''
new = '''POST = ((X_RAIL_BOT, -24.0), (22.0, SPOOL_Y[0] - 0.4), (SPOOL_Z - 8.0, SPOOL_Z + 8.0))
POST_NARROW = (26.5, -25.5)       # below this y the post stops short at this x: the board cover passes beside it, slid in'''
assert old in s
s = s.replace(old, new)
old = '''  (px0, px1), (py0, py1), (pz0, pz1) = POST
  parts.append(box(px0, px1, py0, py1, pz0, pz1))'''
new = '''  (px0, px1), (py0, py1), (pz0, pz1) = POST
  parts.append(box(px0, px1, POST_NARROW[0], py1, pz0, pz1))
  parts.append(box(px0, POST_NARROW[1], py0, POST_NARROW[0] + 0.01, pz0, pz1))'''
assert old in s
s = s.replace(old, new)
open(p, "w").write(s)
p = "sidebuild.py"
s = open(p).read()
s = s.replace('''  ("M4 x 25 socket head screw + M4 washer", 1, "the spool's axle (cuts its own thread into the post)"),''',
              '''  ("M4 x 20 socket head screw + M4 washer", 1, "the spool's axle (cuts its own thread into the post)"),''')
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/run_internal.py