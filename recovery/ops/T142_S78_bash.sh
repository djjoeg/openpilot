cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > explore_overlap.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import popparts as PP
from mindist import min_dist
from explore_mount import stalk_cfgs, key_room, key
mb = PP.motor_and_board()
PP.MOUNT_DEG = -7.5
for name in ("body", "board", "plugs"):
  m = PP.to_wheel(mb[name], -3.0, -56.5)
  for sn, s in (("stalk36", stalk_cfgs[36.0]), ("stalk45", stalk_cfgs[45.0]), ("keyroom", key_room)):
    x = m ^ s
    if x.volume() > 1e-3:
      bb = x.bounding_box()
      print(name, sn, "overlap", round(x.volume(), 1), "mm3 box", [round(v, 1) for v in bb])
    else:
      d, p = min_dist(m, s, spacing=1.0)
      print(name, sn, "gap", round(d, 1), [round(v) for v in p] if p is not None else "")
# the plug shapes in the carrier frame
for k in ("body", "board", "plugs"):
  print(k, [round(v, 1) for v in mb[k].bounding_box()])
EOF
PYTHONPATH=/home/claude/pylib python3 explore_overlap.py 2>&1 | tail -15; grep -n "def motor_and_board" -A 14 /home/claude/deliver/hardware/cad/popparts.py