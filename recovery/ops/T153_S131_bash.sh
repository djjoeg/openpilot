python3 - <<'EOF'
p='/home/claude/deliver/hardware/cad/slideparts.py'
s=open(p).read()
old='''RSPRING = {"part": "to be chosen", "od": 10.0, "wire": 0.8, "free": 20.0, "rate": 0.55, "solid": 8.0}'''
new='''# Lee Spring LC 022D 05 S: stainless, 7.62 mm outside, 6.50 inside (on a rod up to 6.10), 0.56 mm wire, 19.05 mm long,
# 0.578 N/mm, 9.27 N at its solid height of 3.38 mm.
RSPRING = {"part": "Lee Spring LC 022D 05 S", "od": 7.62, "wire": 0.56, "free": 19.05, "rate": 0.578, "solid": 3.38,
           "max": 9.27}
END_HOLE_D = 6.8                           # the rods' holes in the block's end walls: the springs bear on the wall round them'''
assert old in s
s=s.replace(old,new)
old2='''  for x, z in RODS:
    part = part - cyl_y(ROD_D / 2 + 0.8, y0 - 1.0, y1 + 1.0, x=x, z=z, segments=48)'''
new2='''  for x, z in RODS:
    part = part - cyl_y(END_HOLE_D / 2, y0 - 1.0, y1 + 1.0, x=x, z=z, segments=48)'''
assert old2 in s
s=s.replace(old2,new2)
s += '''

# ***** the column plate: the pop-off mount's U round the adjustment tab, moved down with the column cover (carscene.py),
# with an upright flange the block bolts to *****
# The U, its slots for the screw tabs and its pad are the pop-off mount's (popparts.py), placed with the tab and the
# cover's screws (all three move with the cover). The flange hangs from the right leg, square to the column, behind
# the block's flange; its two slots run up and down (+- PL_FLANGE_SLOT) for the cover's height. The plate is made for one
# key depth D (your photo of the key sets it); its tabs slide along their slots for the rest.

PL_FLANGE_T = 5.0
PL_FLANGE_SLOT = 10.0
PL_FLANGE_PAD = 8.0


def flange_bolts_wheel(mount_deg: float = MOUNT_DEG_S) -> list:
  """The block's flange bolts (x, y) in the steering wheel frame, the mount at mount_deg (slots' middles)."""
  a = math.radians(mount_deg)
  out = []
  for xc, zc in FLANGE_BOLTS:
    r, t = PP.R_FACE_P + zc, -xc
    out.append((r * math.cos(a) - t * math.sin(a), r * math.sin(a) + t * math.cos(a)))
  return out


def flange_z() -> tuple:
  """The plate's flange (z), right behind the block's."""
  z1 = PP.Z_AXIS_P - FLANGE_Y[1]
  return (z1 - PL_FLANGE_T, z1)


def slide_column_plate(D: float = None) -> Manifold:
  """Steering wheel frame, for key depth D."""
  import carscene as CS
  sc = CS.CarScene(D if D is not None else CS.D_REF)
  dy, dz = sc.shift[1], sc.shift[2]
  y1 = PP.plate_top_y_u()
  y0 = y1 - PP.PL_T_U
  zb0, zb1 = PP.PL_BRIDGE_Z
  right = box(PP.PL_RIGHT_X[0], PP.PL_RIGHT_X[1], y0, y1, zb0, PP.PL_FRONT_Z)
  left = box(PP.PL_LEFT_X[0], PP.PL_LEFT_X[1], y0, y1, zb0, PP.PL_LEFT_FRONT_Z)
  bridge = box(PP.PL_LEFT_X[0], PP.PL_RIGHT_X[0] + 1.0, y0, y1, zb0, zb1)
  part = union([right, left, bridge])
  part = PP._round_corner(part, PP.PL_RIGHT_X[0], PP.PL_FRONT_Z, 1, -1, 8.0, y0, y1)
  part = PP._round_corner(part, PP.PL_LEFT_X[0], PP.PL_LEFT_FRONT_Z, 1, -1, 7.0, y0, y1)
  part = PP._round_corner(part, PP.PL_LEFT_X[1], PP.PL_LEFT_FRONT_Z, -1, -1, 7.0, y0, y1)
  part = PP._round_corner(part, PP.PL_LEFT_X[0], zb0, 1, 1, 8.0, y0, y1)
  ribs = [box(PP.PL_RIGHT_X[0], PP.PL_RIGHT_X[0] + 4.0, y0 - 6.0, y0 + 0.01, zb0, PP.PL_FRONT_Z - 8.0),
          box(PP.PL_LEFT_X[1] - 4.0, PP.PL_LEFT_X[1], y0 - 6.0, y0 + 0.01, zb0, PP.PL_LEFT_FRONT_Z - 7.0),
          box(PP.PL_LEFT_X[0] + 8.0, PP.PL_RIGHT_X[0] + 4.0, y0 - 6.0, y0 + 0.01, zb1 - 4.0, zb1)]
  part = union([part] + ribs)
  for x0, z0, x1, z1 in PP.PL_SLOTS:
    part = part - PP._slot_y(x0, z0, x1, z1, y0 - 8.0, y1 + 1.0)
  for z in PP.PL_TIE_Z_U:
    part = part - box(PP.PL_LEFT_X[0] - 1.0, PP.PL_LEFT_X[1] + 1.0, y0 - 7.0, y0 + 1.5, z - 4.0, z + 4.0)
  # the flange, in the plate's own frame (the cover's estimate it was drawn for): the block's bolts, less the move
  fz0, fz1 = flange_z()
  fz0, fz1 = fz0 - dz, fz1 - dz
  bolts = [(x, y - dy) for x, y in flange_bolts_wheel()]
  xs = [b[0] for b in bolts]
  ys = [b[1] for b in bolts]
  fx0 = min(xs) - PL_FLANGE_PAD - FLANGE_SLOT * 0.4
  fx1 = max(max(xs) + PL_FLANGE_PAD, PP.PL_RIGHT_X[1])
  fy0 = min(ys) - PL_FLANGE_SLOT - PL_FLANGE_PAD
  flange = box(fx0, fx1, fy0, y1, fz0, fz1)
  # a gusset behind it, along the leg's outer edge, and the leg made long enough to reach it
  reach = box(PP.PL_RIGHT_X[1] - 14.0, PP.PL_RIGHT_X[1], y0, y1, fz0, PP.PL_FRONT_Z)
  gusset = box(fx1 - 6.0, fx1, fy0 + 8.0, y1, fz0 - 22.0, fz1)
  gusset = gusset - _wedge_cut(fx1 - 7.0, fx1 + 1.0, fy0 + 7.0, y0, fz0 - 23.0, fz0)
  part = union([part, flange, reach, gusset])
  for (bx, by) in bolts:
    part = part - Manifold.batch_hull([cyl(M5_CLEAR / 2, fz0 - 1.0, fz1 + 1.0, bx, by + s, 32) for s in (-PL_FLANGE_SLOT, PL_FLANGE_SLOT)])
  return clean(part.translate((0.0, dy, dz)))


def _wedge_cut(x0, x1, y_lo, y_hi, z_back, z_front) -> Manifold:
  """Cuts the gusset's lower back corner away at a slope (from (y_lo, z_front) to (y_hi, z_back))."""
  from cadlib import prism_x
  return prism_x([(y_lo, z_front), (y_lo, z_back), (y_hi, z_back)], x0, x1)
'''
open(p,'w').write(s)
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib timeout 600 python3 -c "
import slideparts as S
print('flange bolts', [tuple(round(v,1) for v in b) for b in S.flange_bolts_wheel()], 'flange z', S.flange_z())
for D in (106,110,125):
    m=S.slide_column_plate(D); print(D, round(m.volume()), len(m.decompose()), [round(v,1) for v in m.bounding_box()])
print('release on/off', round(S.release_force(0),2), round(S.release_force(S.STROKE),2))
"