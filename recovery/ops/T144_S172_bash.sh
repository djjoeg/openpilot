cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && python3 - <<'EOF'
import picks
picks.P[29] = {'S60': (1717, 570, 5), 'S80': (1825, 530, 5), 'RH': (814, 500, 5), 'CUP': (870, 1232, 6),
               'CL1': (1647, 1008, 5), 'CL2': (1675, 1042, 5)}
src = open('picks.py').read()
add = "    29: {'S60': (1717, 570, 5), 'S80': (1825, 530, 5), 'RH': (814, 500, 5), 'CUP': (870, 1232, 6), 'CL1': (1647, 1008, 5),\n         'CL2': (1675, 1042, 5)},\n"
src = src.replace("    36: {'S0'", add + "    36: {'S0'")
open('picks.py', 'w').write(src)
EOF
python3 jinit.py