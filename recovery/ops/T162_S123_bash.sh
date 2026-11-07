cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = "sideparts.py"
s = open(p).read()
s = s.replace('''POST = ((X_RAIL_BOT, -24.0), (24.0, SPOOL_Y[0] - 0.4), (SPOOL_Z - 8.0, SPOOL_Z + 8.0))''',
              '''POST = ((X_RAIL_BOT, -24.0), (20.0, SPOOL_Y[0] - 0.4), (SPOOL_Z - 8.0, SPOOL_Z + 8.0))''')
open(p, "w").write(s)
EOF
grep -n "^POST\|^SPOOL_Y\|^GEAR_\|^ROOF" sideparts.py