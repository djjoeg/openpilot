python3 - <<'EOF'
src=open('columnparts.py').read()
src=src.replace("    out.append(cyl_y(4.3, ya - 4.0, ya, x=hx, z=SB_BOLT_Z, segments=24))                                        # head\n    out.append(cyl_y(4.6, SB_BAR_Y[1], SB_BAR_Y[1] + MP.M5_WASHER_T + MP.M5_NYLOC_T, x=hx, z=SB_BOLT_Z, segments=24))   # nut",
"    out.append(cyl_y(4.3, ya - 4.0, ya - 0.01, x=hx, z=SB_BOLT_Z, segments=24))                                        # head\n    out.append(cyl_y(4.6, SB_BAR_Y[1] + 0.01, SB_BAR_Y[1] + MP.M5_WASHER_T + MP.M5_NYLOC_T, x=hx, z=SB_BOLT_Z, segments=24))   # nut")
src=src.replace("    out.append(cyl_y(4.6, yo, yo + MP.M5_WASHER_T + MP.M5_NYLOC_T, x=bx, z=bz, segments=24))\n    out.append(cyl_y(4.3, -yo - MP.M5_WASHER_T - 5.0, -yo, x=bx, z=bz, segments=24))",
"    out.append(cyl_y(4.6, yo + 0.01, yo + MP.M5_WASHER_T + MP.M5_NYLOC_T, x=bx, z=bz, segments=24))\n    out.append(cyl_y(4.3, -yo - MP.M5_WASHER_T - 5.0, -yo - 0.01, x=bx, z=bz, segments=24))")
open('columnparts.py','w').write(src)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side_test.py 2>&1 | tail -8