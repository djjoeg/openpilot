python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
start = s.index("# The hinge block bolts to a flange on the column plate's post")
end = s.index("def mount_to_carrier(p_m, z_axis: float = Z_AXIS_P) -> np.ndarray:")
new_consts = '''# The hinge block bolts to a flange on the column plate: two M5 bolts along the column, each through a slot across the
# block's flange (its own x, which turns with the mount) and an upright slot (y) in the plate's. The block's flange is
# part of the block, so it turns with the mount when that is set (MOUNT_ADJ); the plate's slots are long enough for that
# and for the cover's underside sitting higher or lower than estimated. The plate itself slides along the column and
# across on its screw tabs, so the block sets where the plate ends up.
FLANGE_T = 5.0
BLOCK_FLANGE_DZ = (-72.5, -66.0)     # the block's flange along the column, from the motor's axis
_FL0_DEG = -7.5                      # the flange's shape, as the 3:15 build had it in the steering wheel frame


def _to_mount(pts, deg: float = _FL0_DEG):
  """Steering wheel (x, y) points at mount angle deg -> mount frame."""
  c, s_ = math.cos(math.radians(-deg)), math.sin(math.radians(-deg))
  return tuple((float(c * x - s_ * y), float(s_ * x + c * y)) for x, y in pts)


BLOCK_FLANGE_M = _to_mount(((62.0, -34.0), (104.0, -34.0), (104.0, -2.0), (62.0, -2.0)))
FLANGE_BOLTS_M = _to_mount(((72.0, -26.0), (94.0, -12.0)))
SLOT_X = 12.0                 # the block's slots: +- this across
SLOT_Y = 26.0                 # the plate's slots: +- this up and down


def block_flange_z(z_axis: float = Z_AXIS_P) -> tuple:
  return (z_axis + BLOCK_FLANGE_DZ[0], z_axis + BLOCK_FLANGE_DZ[1])


def flange_bolts_wheel(mount_deg: float = None) -> list:
  """The two flange bolts (x, y) in the steering wheel frame with the mount at mount_deg."""
  deg = MOUNT_DEG if mount_deg is None else mount_deg
  c, s_ = math.cos(math.radians(deg)), math.sin(math.radians(deg))
  return [(c * x - s_ * y, s_ * x + c * y) for x, y in FLANGE_BOLTS_M]


'''
s = s[:start] + new_consts + s[end:]
# the block's flange built in the mount frame
old_bf = s[s.index("def _block_flange() -> Manifold:"):s.index("# ***** the column plate and the arm *****")]
new_bf = '''def mount_solid_to_carrier(m: Manifold, z_axis: float = Z_AXIS_P) -> Manifold:
  """A mount-frame solid -> carrier frame (the inverse of carrier_to_mount)."""
  Rt = R_POP.T
  off = -Rt @ np.array([R_FACE_P, 0.0, z_axis])
  return m.transform([[float(Rt[i, 0]), float(Rt[i, 1]), float(Rt[i, 2]), float(off[i])] for i in range(3)])


def _block_flange() -> Manifold:
  """The block's flange, built in the mount frame (so it turns with the mount), with a slot across at each bolt."""
  z0, z1 = block_flange_z()
  fl = _xy_poly(BLOCK_FLANGE_M).extrude(z1 - z0).translate((0, 0, z0))
  for bx, by in FLANGE_BOLTS_M:
    fl = fl - Manifold.batch_hull([cyl(M5_CLEAR / 2, z0 - 1, z1 + 1, bx + s, by, 32) for s in (-SLOT_X, SLOT_X)])
  return mount_solid_to_carrier(fl)


'''
s = s.replace(old_bf, new_bf)
p.write_text(s)
print("ok")
EOF
grep -n "wheel_to_carrier\|BLOCK_FLANGE_XY\|FLANGE_BOLTS\b\|PLATE_FLANGE" popparts.py popassembly.py