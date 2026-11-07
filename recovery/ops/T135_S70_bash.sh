python3 - <<'EOF'
s = open('popparts.py').read()
# replace the arm joint on the block with a flange (cross slots)
start = s.index("J2_M = (66.0, -30.0, -125.0)")
end = s.index("def mount_to_carrier(")
s = s[:start] + '''# The hinge block bolts to a flange on the column plate's post: two M5 bolts along the column, each through a slot across
# (x) in the block's flange and an upright slot (y) in the plate's: the block can be set anywhere in a 16 x 30 mm box
# before the bolts are tightened; the plate slides along the column on the cover's screws.
FLANGE_T = 5.0
BLOCK_FLANGE_Z = (-124.0, -118.0 + 0.5)     # the block's flange, in front (towards you) ...
PLATE_FLANGE_Z = (-129.0, -124.0)           # ... the plate's behind it (steering wheel z)
FLANGE_BOLTS = ((72.0, -26.0), (94.0, -12.0))   # the two bolts (x, y), steering wheel frame, everything in the middle
SLOT_X = 8.0                  # the block's slots: +- this across
SLOT_Y = 15.0                 # the plate's slots: +- this up and down
BLOCK_FLANGE_XY = ((62.0, -34.0), (104.0, -34.0), (104.0, -2.0), (62.0, -2.0))


''' + s[end:]
# remove the old joint helpers from the block
start = s.index("def j2_wheel(")
end = s.index("def _hinge_pt(")
s = s[:start] + s[end:]
# block: replace the joint with the flange
s = s.replace('''def pop_hinge_block(j1_w=None) -> Manifold:
  """Carrier frame, the carrier on (lift 0). j1_w: the column plate's joint bolt (x, y), steering wheel frame: sets
  the direction of the locking bolt's curved slot."""''', '''def pop_hinge_block() -> Manifold:
  """Carrier frame, the carrier on (lift 0)."""''')
s = s.replace('''  # the arm's joint: two ears across the column at the arm's plane (the steering wheel's x, y at z = J2_M z), joined
  # to the near cheek by a web
  body = union(parts)
  joint = _j2_joint(j1_w)
  part = body + joint''', '''  # the flange that bolts to the column plate's post (built in the steering wheel frame)
  body = union(parts)
  part = body + _block_flange()''')
start = s.index("def _j2_joint(")
end = s.index("# ***** the column plate and the arm *****")
s = s[:start] + '''def wheel_to_carrier(m: Manifold, z_axis: float = Z_AXIS_P) -> Manifold:
  R, T = carrier_to_wheel(z_axis)
  Rt = R.T
  off = -Rt @ T
  return m.transform([[float(Rt[i, 0]), float(Rt[i, 1]), float(Rt[i, 2]), float(off[i])] for i in range(3)])


def _xy_poly(pts) -> CrossSection:
  cs = CrossSection([list(pts)])
  return cs if cs.area() > 0 else CrossSection([list(pts)[::-1]])


def _block_flange() -> Manifold:
  """Steering wheel frame -> carrier frame: the block's flange, with a slot across (x) at each bolt."""
  z0, z1 = BLOCK_FLANGE_Z
  fl = _xy_poly(BLOCK_FLANGE_XY).extrude(z1 - z0).translate((0, 0, z0))
  for bx, by in FLANGE_BOLTS:
    fl = fl - Manifold.batch_hull([cyl(M5_CLEAR / 2, z0 - 1, z1 + 1, bx + s, by, 32) for s in (-SLOT_X, SLOT_X)])
  return wheel_to_carrier(fl)


''' + s[end:]
# plate: post and flange instead of the arm's joint
start = s.index("PL_X_P = (12.0, 66.0)")
end = s.index("def pop_plate_pads(")
s = s[:start] + '''PL_X_P = (12.0, 66.0)          # the plate across the cover's underside (x), right of the tilt lever's swing
POST_X = (60.0, 68.0)          # the post rising from the plate's right end beside the cover, up to the flange
PLATE_FLANGE_XY = ((60.0, -36.0), (102.0, -36.0), (102.0, 6.0), (60.0, 6.0))


def pop_column_plate(front_z: float = None, cover_bottom: float = None) -> Manifold:
  """faceparts.column_plate moved right (clear of the tilt lever), with a post at its right end rising beside the cover
  to the flange the hinge block bolts to (upright slots)."""
  from params import COVER_BOTTOM, PLATE_FRONT_Z
  front_z = PLATE_FRONT_Z if front_z is None else front_z
  dy = 0.0 if cover_bottom is None else cover_bottom - COVER_BOTTOM
  y1 = FP.plate_top_y()
  y0 = y1 - FP.PL_T
  z0, z1 = front_z - FP.PL_LEN, front_z
  x0p, x1p = PL_X_P
  plate = box(x0p, x1p, y0, y1, z0, z1)
  ribs = [box(x0p + a, x0p + b, y0 - FP.PL_RIB_H, y0 + 0.01, z0, z1) for a, b in FP.PL_RIB_X]
  part = union([plate] + ribs)
  for sx in FP.PL_SLOTS_X:
    x = x0p + sx
    part = part - Manifold.batch_hull([cyl_y(M5_CLEAR / 2, y0 - FP.PL_RIB_H - 1, y1 + 1, x=x, z=front_z - FP.PL_SLOT_Z[0], segments=32),
                                       cyl_y(M5_CLEAR / 2, y0 - FP.PL_RIB_H - 1, y1 + 1, x=x, z=front_z - FP.PL_SLOT_Z[1], segments=32)])
  for dz in FP.PL_TIE_Z:
    z = front_z - dz
    part = part - box(x0p - 1, x1p + 1, y0 - FP.PL_RIB_H - 1, y0 + 1.5, z - 4.0, z + 4.0)
  # the post: from the plate up beside the cover to the flange, its back face the flange's
  fz0, fz1 = PLATE_FLANGE_Z
  post = box(POST_X[0], POST_X[1], y0 - FP.PL_RIB_H, PLATE_FLANGE_XY[2][1] - dy, fz0, fz1 + 6.0)
  gusset = prism_x([(y0, fz1 + 6.0), (y0, fz1 + 26.0), (y0 + 20.0, fz1 + 6.0)], POST_X[0], POST_X[1])
  flange = _xy_poly([(x, y - dy) for x, y in PLATE_FLANGE_XY]).extrude(fz1 - fz0).translate((0, 0, fz0))
  part = part + post + gusset + flange
  for bx, by in FLANGE_BOLTS:
    part = part - Manifold.batch_hull([cyl(M5_CLEAR / 2, fz0 - 1, fz1 + 7, bx, by - dy + s, 32) for s in (-SLOT_Y, SLOT_Y)])
  return clean(part)


''' + s[end:]
open('popparts.py', 'w').write(s)
EOF
grep -n "J2_M\|j2_wheel\|arm_z\|J1_P\|ARM_LENGTHS_P\|pop_arm_reach" popparts.py | head; PYTHONPATH=/home/claude/pylib python3 -c "
import popparts as PP, numpy as np
b = PP.pop_hinge_block(); print('block', round(b.volume()), len(b.decompose()), [round(v,1) for v in b.bounding_box()])
p = PP.pop_column_plate(); print('plate', round(p.volume()), len(p.decompose()), [round(v,1) for v in p.bounding_box()])
bw = PP.to_wheel(b)
print('block/plate overlap', round((bw ^ p).volume(),2))
"
