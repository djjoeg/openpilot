python3 - <<'EOF'
p='columnparts.py'; s=open(p).read()
n = s.count("if cs.area() < 0:")
s = s.replace("if cs.area() < 0:", "if cs.area() < 1e-9:")
s = s.replace("    if pie.area() < 0:\n      pie = CrossSection([pts[::-1]])", "    if pie.area() < 1e-9:\n      pie = CrossSection([pts[::-1]])")
open(p,'w').write(s); print("replaced", n)
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import columnparts as CP, render as R
from cadlib import size_of
lo = CP.column_clamp_lower()
print(len(lo.decompose()), lo.status(), [round(v,1) for v in lo.bounding_box()], round(lo.volume()/1000,1))
R.save("/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/photo/lower3.png",
       [([(lo,(.55,.7,.9))], R.look((1,-0.6,0.8),(0,1,0))), ([(lo,(.55,.7,.9))], R.look((1,0,0),(0,1,0)))], ["lower saddle", "from the right"], size=(700,600))
EOF