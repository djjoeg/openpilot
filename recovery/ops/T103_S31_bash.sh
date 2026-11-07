python3 - <<'EOF'
src=open('columnparts.py').read()
src=src.replace("  stack = 2 * (SB_FORK_Y[1] - SB_FORK_Y[0]) + ARM_T + 2 * GAP\n", "  stack = 2 * (SB_FORK_Y[1] - SB_FORK_Y[0]) + ARM_W + 2 * GAP     # the bolts run across the arm's width\n")
src=src.replace("from params import (ARM_T, BACKLASH,", "from params import (ARM_T, ARM_W, BACKLASH,")
open('columnparts.py','w').write(src)
EOF
grep -n "ARM_T" columnparts.py | head -5