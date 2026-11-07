python3 - <<'EOF'
s = open('mountparts.py').read()
s = s.replace('RIDGE_H = 0.65                        # the ridge stands this far out from the catch\'s face',
              'RIDGE_H = 0.75                        # the ridge stands this far out from the catch\'s face')
s = s.replace('FINGER_GAP = 0.6                      # the tab\'s inside face to the catch\'s face',
              'FINGER_GAP = 1.0                      # the tab\'s inside face to the catch\'s face (it clears the ridge by 0.25)')
s = s.replace('BUMP_H = 0.45                         # the tab\'s hook stands this far in from its inside face',
              'BUMP_H = 0.75                         # the tab\'s hook stands this far in from its inside face (it clears\n                                      # the catch\'s face by 0.25)')
s = s.replace("# the front of the switch walls whose face is a circle round the lever's bolt. Lifting, the tab bends 0.5 mm out to\n# pass the ridge; pulling down, it bends again and snaps under it.",
              "# the front of the switch walls whose face is a circle round the lever's bolt. Lifting, the tab bends 0.5 mm out to\n# pass the ridge; pulling down, it bends again and snaps under it. Lever up, the tab is clear of everything, so it\n# doesn't stay bent (printed plastic slowly gives way under a constant load, more so in a hot car).")
open('mountparts.py', 'w').write(s)
EOF
grep -n "RIDGE_H =\|FINGER_GAP =\|BUMP_H =" mountparts.py; PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import sys; sys.path.insert(0, '/home/claude/deliver/hardware/cad')
import numpy as np
import mountparts as MP
br = MP.lever_bracket(); tab = MP.lever_tab()
for a in np.arange(-0.5, 3.6, 0.25):
  print(round(a, 2), round((MP.lever_in_carrier(tab, a) ^ br).volume(), 4), end=" | ")
print()
# tab vs bracket over the whole travel above the ridge
mx = max((MP.lever_in_carrier(tab, a) ^ br).volume() for a in np.arange(4, 40, 1.0))
print("tab beyond 4 deg:", mx)
print(MP.finger_force(), MP.finger_angles())
EOF