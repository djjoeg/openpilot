cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
import re
p = "faceparts.py"
s = open(p).read()
s = s.replace('ARM_LENGTHS_F = (150, 180, 210)', 'ARM_LENGTHS_F = (135, 165, 195)')
s = s.replace('J1_W = (45.0, COVER_BOTTOM - 36.0)   # the column plate\'s joint: its bolt (x, y), steering wheel frame (z: the hinge block\'s)',
              'J1_W = (60.0, COVER_BOTTOM - 45.0)   # the column plate\'s joint: its bolt (x, y), steering wheel frame (z: the hinge block\'s)')
old = """  between = Manifold.batch_hull([cyl(ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap,
                                     px + 90 * math.cos(math.radians(a)), py + 90 * math.sin(math.radians(a)), 48)
                                 for a in (lock_deg - LOCK_RANGE_F - 8, lock_deg + LOCK_RANGE_F + 8,
                                           lock_deg + 180 - 30, lock_deg + 180 + 30)] +
                                [cyl(ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap, px, py, 48)])
  return clean(part - between)"""
new = """  ahead = Manifold.batch_hull([cyl(ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap,
                                   px + 90 * math.cos(math.radians(a)), py + 90 * math.sin(math.radians(a)), 48)
                               for a in (lock_deg - LOCK_RANGE_F - 8, lock_deg + LOCK_RANGE_F + 8)] +
                              [cyl(ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap, px, py, 48)])
  tail = ARM_SLIDE_F + 12.0
  behind = Manifold.batch_hull([cyl(ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap,
                                    px + tail * math.cos(math.radians(a)), py + tail * math.sin(math.radians(a)), 48)
                                for a in (lock_deg + 180 - LOCK_RANGE_F - 3, lock_deg + 180 + LOCK_RANGE_F + 3)] +
                               [cyl(ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap, px, py, 48)])
  return clean(part - ahead - behind)"""
assert old in s
s = s.replace(old, new)
open(p, "w").write(s)
EOF
grep -n "J1_W =\|ARM_LENGTHS_F =" faceparts.py