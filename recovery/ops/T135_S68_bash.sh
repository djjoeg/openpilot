cat >> popparts.py <<'EOF'


# ***** the column plate and the arm *****

PL_X_P = (12.0, 66.0)          # the plate across the cover's underside (x), right of the tilt lever's swing
J1_P = (52.0, -108.0)          # its joint's bolt (x, y), steering wheel frame, at the arm's plane (z = J2_M z)
ARM_LENGTHS_P = (70,)          # the arm to print: bolt to bolt, slides +-15


def pop_arm_reach() -> float:
  return float(np.linalg.norm(j2_wheel()[:2] - np.array(J1_P)))


def pop_column_plate(front_z: float = None) -> Manifold:
  """faceparts.column_plate moved right (clear of the tilt lever) with its joint at J1_P, the arm's plane J2_M z."""
  from params import PLATE_FRONT_Z
  front_z = PLATE_FRONT_Z if front_z is None else front_z
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
  zc = arm_z()
  half_gap = FP.ARM_T_F / 2.0 + MP.GAP
  u = j2_wheel()[:2] - np.array(J1_P)
  u = u / np.linalg.norm(u)
  lock_deg = math.degrees(math.atan2(u[1], u[0]))
  top_strip = CrossSection.square((x1p - x0p - 10.0, 1.0)).translate((x0p + 10.0, y0 - FP.PL_RIB_H))
  z_lo, z_hi = zc - half_gap - FP.J_EAR_T, zc + half_gap + FP.J_EAR_T
  if z_hi > z1 or z_lo < z0:
    raise ValueError("the column plate's joint is past the plate's ends")
  ears = [FP.ear_plate(J1_P, lock_deg, FP.LOCK_RANGE_F, [top_strip], a, b) for a, b in ((z_lo, zc - half_gap), (zc + half_gap, z_hi))]
  web = box(x0p + 10.0, x1p, y0 - FP.PL_RIB_H, y0 + 0.01, z_lo, z_hi)
  part = part + union(ears + [web])
  part = part - FP.joint_holes(J1_P, lock_deg, FP.LOCK_RANGE_F, z_lo, z_hi)
  px, py = J1_P
  ahead = Manifold.batch_hull([cyl(FP.ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap,
                                   px + 90 * math.cos(math.radians(a)), py + 90 * math.sin(math.radians(a)), 48)
                               for a in (lock_deg - FP.LOCK_RANGE_F - 8, lock_deg + FP.LOCK_RANGE_F + 8)] +
                              [cyl(FP.ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap, px, py, 48)])
  tail = FP.ARM_SLIDE_F + 12.0
  behind = Manifold.batch_hull([cyl(FP.ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap,
                                    px + tail * math.cos(math.radians(a)), py + tail * math.sin(math.radians(a)), 48)
                                for a in (lock_deg + 180 - FP.LOCK_RANGE_F - 3, lock_deg + 180 + FP.LOCK_RANGE_F + 3)] +
                               [cyl(FP.ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap, px, py, 48)])
  return clean(part - ahead - behind)


def pop_plate_pads(front_z: float = None) -> Manifold:
  from params import PLATE_FRONT_Z
  front_z = PLATE_FRONT_Z if front_z is None else front_z
  y1 = FP.plate_top_y()
  x0p, x1p = PL_X_P
  return union([box(a, b, y1, y1 + FP.PL_PAD_T, front_z - FP.PL_LEN + 2.0, front_z - 2.0) for a, b in ((x0p + 1, x0p + 11),
                                                                                                       (x1p - 11, x1p - 1))])
EOF
python3 - <<'EOF'
s = open('/home/claude/deliver/hardware/cad/popparts.py').read()
s = s.replace("""  j1 = np.array(j1_w if j1_w is not None else FP.J1_W)""", """  j1 = np.array(j1_w if j1_w is not None else J1_P)""")
open('/home/claude/deliver/hardware/cad/popparts.py', 'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import popparts as PP
print('reach', round(PP.pop_arm_reach(),1))
p = PP.pop_column_plate(); print('plate', round(p.volume()), [round(v,1) for v in p.bounding_box()], len(p.decompose()))
b = PP.pop_hinge_block(); print('block', round(b.volume()), len(b.decompose()))
a = PP.FP.face_arm(70.0); print('arm', round(a.volume()))
"
