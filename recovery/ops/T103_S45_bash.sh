python3 - <<'EOF'
src=open('margins.py').read()
src=src.replace("def side_rows(t, fit) -> list[dict]:\n  \"\"\"The right-side mount's own ways of failing. fit: columnassembly.SideFit.\"\"\"",
"def side_rows(t, fit, cover_w: float = P.COVER_W) -> list[dict]:\n  \"\"\"The right-side mount's own ways of failing. fit: columnassembly.SideFit; cover_w: the covers' width at the bracket.\"\"\"")
src=src.replace("  arm_mm = (float(fit.screw_w[0]) - P.WHEEL_OD / 2.0) + P.WHEEL_OD / 2.0 - (fit.bracket_z * 0.0) - (P.COVER_W / 2.0 + CP.SB_BAR_HOLES[1])\n  arm_mm = max(arm_mm, 20.0)",
"  arm_mm = max(float(fit.screw_w[0]) - (cover_w / 2.0 + CP.SB_BAR_HOLES[1]), 20.0)   # the screw past the tab's last bolt")
open('margins.py','w').write(src)
EOF
grep -n "arm_mm" margins.py | head