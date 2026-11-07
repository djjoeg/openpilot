cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && cat > lev2.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import slideparts as SP
blk = SP.slide_block()
for d in (40.0, 20.0, 10.0):
  st = SP.cam_state(d, 4.5)
  lev = SP.slide_lever(SP.SWING_SIGN * d).translate((0, st["carrier_off"], 0))
  x = lev ^ blk
  print(d, round(x.volume(),2), [round(v,1) for v in x.bounding_box()], "reach", round(SP.cam_support(d),2), "pivot y", round(SP.PIVOT[0] + st["carrier_off"],2))
EOF
PYTHONPATH=/home/claude/pylib timeout 600 python3 lev2.py