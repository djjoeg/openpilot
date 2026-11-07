cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > gaps_v2.py <<'EOF'
"""Clearances (mm) for the report and the page: nominal 3:20, and the mount turned to each end of its adjustment."""
import sys, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import popparts as PP
import popassembly as PA
from cadlib import union
from mindist import min_dist
import run_u

T0 = time.time()
t, parts = run_u.build()
A = PA.PopAssembly(t, parts)
stalks = {d: PA.stalk_positions(down=d) for d in (30.0, 36.0, 42.0)}
keep = PP.MOUNT_DEG
out = {}
for adj in (0.0, -PP.MOUNT_ADJ[0], PP.MOUNT_ADJ[1]):
  PP.MOUNT_DEG = keep + adj
  fixed = union([A.block(), A.switch()])
  res = {}
  for lift in (-3.0, 0.0, 10.0, 25.0, 40.0, 55.0, 75.0):
    mov = union([A.carrier(lift), A.motor(lift), A.gear(lift), A.springs(lift), A.bolts(lift)]) + fixed
    for n, ob in [(f"stalk down {d:.0f}", s) for d, s in stalks.items()] + [("key in the ignition", A.key_head()),
                                                                          ("key cylinder", A.key())]:
      d, p = min_dist(mov, ob, spacing=1.5)
      if n not in res or d < res[n]:
        res[n] = round(d, 1)
  out[adj] = res
  print(f"mount {PP.MOUNT_DEG:+.1f} ({3 + (-PP.MOUNT_DEG) / 30:.2f} o'clock as hours):", res, round(time.time() - T0), "s", flush=True)
PP.MOUNT_DEG = keep
# the plate and tabs against the adjustment tab's swing and fingers, and the bolster
pl = A.plate() + A.pad() + A.tabs() + A.tab_bolts()
print("plate+tabs to the adjustment tab's swing and fingers:", round(min_dist(pl, A.tilt_lever(), spacing=1.0)[0], 1))
print("plate to the knee bolster:", round(min_dist(pl, A.bolster(), spacing=1.0)[0], 1))
print("teeth piece behind the grip:", round(-PP.GRIP_P / 2 - t.z_tip, 1))
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 3000 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2/gaps_v2.py 2>&1 | tail -8