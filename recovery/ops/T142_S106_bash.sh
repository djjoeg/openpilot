cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > gaps_u.py <<'EOF'
import sys, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import popparts as PP
import popassembly as PA
from cadlib import union, box
from mindist import min_dist
import run_u

T0 = time.time()
t, parts = run_u.build()
A = PA.PopAssembly(t, parts)
stalk30 = PA.stalk_positions(down=30.0)
stalk36 = PA.stalk_positions(down=36.0)
fixed = union([A.block(), A.switch(), A.plate(), A.tabs()])
res = {}
for lift in (-3.0, 0.0, 10.0, 25.0, 40.0, 55.0, 75.0):
  mov = union([A.carrier(lift), A.motor(lift), A.gear(lift), A.springs(lift), A.bolts(lift)])
  allp = mov + fixed
  for n, ob in (("stalk pushed down 30", stalk30), ("stalk pushed down 36 (3 notches, estimate)", stalk36), ("key cylinder", A.key()),
                ("key in the ignition", A.key_head()), ("adjustment tab handle zone", box(*PA.TAB_HANDLE_ZONE)),
                ("adjustment tab arm zone", box(*PA.TAB_ARM_ZONE)), ("covers", A.covers()), ("spokes' sweep", A.spoke_zone())):
    target = allp if n != "covers" else (mov + A.block() + A.switch() + A.plate())
    d, p = min_dist(target, ob, spacing=1.5)
    if n not in res or d < res[n][0]:
      res[n] = (round(d, 1), lift, None if p is None else [round(v) for v in p])
  # fingers turning the key: room left with the motor on, and when popped off
  d, p = min_dist(mov + fixed, A.key_room(), spacing=1.5)
  res[f"fingers on the key, lift {lift:.0f}"] = (round(d, 1), lift, None if p is None else [round(v) for v in p])
for k, v in res.items():
  print(f"{k:50s} {v}")
print(round(time.time() - T0), "s")
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 3000 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2/gaps_u.py 2>&1 | tail -24