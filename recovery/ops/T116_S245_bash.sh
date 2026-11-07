cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && cat > rowtest.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import params as P
import faceparts as FP
import faceassembly as FA
import margins as MG
t = FP.FaceTeeth(P.WHEEL_OD, P.GRIP, P.RIGHT_SPOKE_DEG)
fit = FA.solve_face(t, P.COVER_BOTTOM)
rows = MG.back_rows(t, fit)
print("\n".join(MG.text_lines(rows)))
EOF
PYTHONPATH=/home/claude/pylib python3 rowtest.py