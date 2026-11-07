cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop && python3 - <<'EOF'
import re
s = open('explore.py').read()
s = s.replace("""  plugs = box(-6, 6, H, H + 14, -52, -43) + box(H, H + 14, -6, 6, -52, -43) + box(-H - 14, -H, -6, 6, -52, -43)""",
"""  # car plug towards the dash (+y), the board's motor plug on the side towards 12 o'clock (carrier -x), the unused debug
  # plug's bare connector on the other side (carrier +x)
  plugs = box(-6, 6, H, H + 14, -52, -43) + box(-H - 14, -H, -6, 6, -52, -43) + box(H, H + 5, -6, 6, -52, -43)""")
s = s.replace("""if __name__ == "__main__":
  import itertools
  for md, hinge in itertools.product((-10.0,), ((45.0, -50.0), (45.0, -45.0), (40.0, -55.0))):
    run(md, -56.5, hinge, 35.0, 135.0, 35.0, 55.0)""",
"""if __name__ == "__main__":
  import itertools
  for md in (-15.0, -10.0, -7.5, -5.0, -2.5, 0.0, 5.0):
    run(md, -56.5, (45.0, -50.0), 35.0, 135.0, 35.0, 55.0)""")
open('explore.py','w').write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 explore.py 2>&1 | grep -v "torque arm" | tail -60