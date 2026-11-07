python3 - <<'EOF'
s = open('popparts.py').read()
s = s.replace("""PL_X_P = (12.0, 66.0)          # the plate across the cover's underside (x), right of the tilt lever's swing""",
"""PL_X_P = (12.0, 66.0)          # the plate across the cover's underside (x), right of the tilt lever's swing
PLATE_FRONT_Z_P = -92.0        # its front end, behind the middle of the grip: behind the key cylinder's bulge""")
s = s.replace("""  from params import COVER_BOTTOM, PLATE_FRONT_Z
  front_z = PLATE_FRONT_Z if front_z is None else front_z""", """  from params import COVER_BOTTOM
  front_z = PLATE_FRONT_Z_P if front_z is None else front_z""")
s = s.replace("""  from params import PLATE_FRONT_Z
  front_z = PLATE_FRONT_Z if front_z is None else front_z""", """  front_z = PLATE_FRONT_Z_P if front_z is None else front_z""")
open('popparts.py', 'w').write(s)
EOF
rm -f /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache/*; cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop && timeout 1800 env PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache python3 pop_run.py --quick 2>&1 | tail -40