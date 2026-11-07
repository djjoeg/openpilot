python3 - <<'EOF'
s = open('mountparts.py').read()
s = s.replace("from params import (ARM_LENGTHS, ARM_SLIDE, ARM_T,", "from params import (ARM_SLIDE, ARM_T,")
open('mountparts.py', 'w').write(s)
w = open('wheelparts.py').read()
w = w.replace("  rp = pitch_radius(MOTOR_TEETH)\n  rf = rp - 1.25 * MODULE\n  teeth = gear_outline", "  rp = pitch_radius(MOTOR_TEETH)\n  teeth = gear_outline")
open('wheelparts.py', 'w').write(w)
EOF
/home/claude/bin/ruff check --line-length 130 --select F,E9 . && grep -n "MODULE" wheelparts.py | head -3; chmod +x accord_lka_parts.py; PYTHONPATH=/home/claude/pylib python3 -c "import sys; sys.path.insert(0,'.'); import wheelparts, mountparts; print('ok')"