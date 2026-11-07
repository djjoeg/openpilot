cd /home/claude/deliver/hardware/cad && cat >> popparts.py <<'EOF'


# ***** the hinge block *****

PAD_R = (8.0, 14.0)           # the two stops' pads, this far from the hinge, between the web and the knuckles
PARK_PAD = (2.0, WEB_LEAD - LIFT_OFF)          # degrees round the hinge: the web's leading face meets it swung off
DROP_PAD = (WEB_TRAIL - LIFT_DROP, 170.0)      # ... and its trailing face, dropped
CHEEK_X = (BLOCK_KNUCKLE_X[0], 25.5)           # the block's two cheeks, each side (the springs pass just outside)
B_BOSS_R = 7.5
SW_ROLLER_R = 2.4                              # the switch's roller (Omron SS-5GL2: 4.8 mm across)
SW_HOLES_R = LOBE_R + MP.SW_OP - MP.SW_PRESS   # the switch's holes' line, this far from the hinge along SW_BETA
SW_CAGE_X = (MP.SW_THICK / 2 + 0.4, MP.SW_THICK / 2 + 3.4)
SW_BODY_R = (LOBE_R, SW_HOLES_R + 6.0)         # the switch, its roller to its back
J2_M = (85.0, 45.0, -118.0)   # the arm's joint on the hinge block (mount frame): above the motor's side, behind it


def mount_to_carrier(p_m, z_axis: float = Z_AXIS_P) -> np.ndarray:
  x, y, z = p_m
  return np.array([-y, z_axis - z, x - R_FACE_P])


def carrier_to_mount_pt(p_c, z_axis: float = Z_AXIS_P) -> np.ndarray:
  x, y, z = p_c
  return np.array([R_FACE_P + z, -x, z_axis - y])


def j2_wheel(z_axis: float = Z_AXIS_P) -> np.ndarray:
  Rm, _ = mount_to_wheel()
  return Rm @ np.array(J2_M)


def arm_z() -> float:
  return J2_M[2]


def _hinge_pt(r: float, beta: float) -> tuple:
  p = polar_hinge(r, beta)
  return (float(p[0]), float(p[1]))


def pop_hinge_block(j1_w=None) -> Manifold:
  """Carrier frame, the carrier on (lift 0). j1_w: the column plate's joint bolt (x, y), steering wheel frame: sets
  the direction of the locking bolt's curved slot."""
  hy, hz = HINGE_P
  by, bz = B_BOLT
  parts = []
  # the knuckles
  for s0, s1 in ((BLOCK_KNUCKLE_X[0], BLOCK_KNUCKLE_X[1]), (-BLOCK_KNUCKLE_X[1], -BLOCK_KNUCKLE_X[0])):
    parts.append(cyl_x(BLOCK_KNUCKLE_R, s0, s1, y=hy, z=hz))
  # the cheeks: from the knuckles round behind the hinge to the springs' back bolt and the switch's cage, kept to the
  # angles the carrier never swings into (from 175 round through 270 to 10 degrees)
  sw_back = SW_BODY_R[1] + 4.0
  cheek_pts = [CrossSection.circle(BLOCK_KNUCKLE_R, 48).translate((hy, hz)),
               CrossSection.circle(B_BOSS_R, 48).translate((by, bz)),
               CrossSection.circle(4.0, 24).translate(_hinge_pt(sw_back, SW_BETA - 12.0)),
               CrossSection.circle(4.0, 24).translate(_hinge_pt(sw_back, SW_BETA + 25.0))]
  cheek_cs = CrossSection.batch_hull(cheek_pts) ^ (_ray_poly(200.0, 178.0, 368.0) + CrossSection.circle(BLOCK_KNUCKLE_R, 48).translate((hy, hz)))
  for s0, s1 in ((CHEEK_X[0], CHEEK_X[1]), (-CHEEK_X[1], -CHEEK_X[0])):
    parts.append(extrude_x(cheek_cs, s0, s1))
  # the bridge between the cheeks behind the switch, and the switch's cage walls
  bridge_cs = _sector_yz(SW_BODY_R[1] + 0.5, sw_back + 4.0, SW_BETA - 14.0, SW_BETA + 27.0, 1.0)
  parts.append(extrude_x(bridge_cs, -CHEEK_X[1], CHEEK_X[1]))
  cage_cs = _sector_yz(SW_BODY_R[0] + 1.5, SW_BODY_R[1] + 1.0, SW_BETA - 22.0, SW_BETA + 22.0, 1.0)
  for s0, s1 in (SW_CAGE_X, (-SW_CAGE_X[1], -SW_CAGE_X[0])):
    parts.append(extrude_x(cage_cs, s0, s1))
  # the stops' pads, from the knuckles' inside faces in towards the web
  for b0, b1 in (PARK_PAD, DROP_PAD):
    pad = _sector_yz(PAD_R[0], PAD_R[1], b0, b1, 0.5)
    for s0, s1 in ((WEB_X[0], BLOCK_KNUCKLE_X[0] + 0.01), (-BLOCK_KNUCKLE_X[0] - 0.01, -WEB_X[0])):
      parts.append(extrude_x(pad, s0, s1))
  # the arm's joint: two ears across the column at the arm's plane (the steering wheel's x, y at z = J2_M z), joined
  # to the near cheek by a web
  body = union(parts)
  joint = _j2_joint(j1_w)
  part = body + joint
  # holes: hinge bolt, the springs' back bolt, the switch's screws (slots along the switch's travel, nuts in one wall)
  part = part - cyl_x(2.75, -60.0, 60.0, y=hy, z=hz, segments=32)
  part = part - cyl_x(M5_CLEAR / 2, -60.0, 60.0, y=by, z=bz, segments=32)
  # room for the carrier's knuckle and lobe between the block's knuckles
  part = part - cyl_x(KNUCKLE_R + MP.CHANNEL_GAP, -KNUCKLE_X - MP.GAP, KNUCKLE_X + MP.GAP, y=hy, z=hz, segments=96)
  part = part - _switch_screw_slots()
  return clean(part)


def _switch_frame():
  """The switch's place: its holes' line SW_HOLES_R from the hinge along SW_BETA; returns (centre (y, z), radial unit,
  along unit) with radial pointing away from the hinge."""
  rad = np.array([math.cos(math.radians(SW_BETA)), math.sin(math.radians(SW_BETA))])
  along = np.array([-rad[1], rad[0]])
  return np.array(HINGE_P), rad, along


def _switch_screw_slots() -> Manifold:
  h, rad, along = _switch_frame()
  out = []
  for d in (-MP.SW_PITCH / 2, MP.SW_PITCH / 2):
    pts = []
    for s in (-MP.SW_SLOT, MP.SW_SLOT):
      c = h + rad * (SW_HOLES_R + s) + along * d
      pts.append(cyl_x(MP.M2_CLEAR / 2, -SW_CAGE_X[1] - 1, SW_CAGE_X[1] + 1, y=float(c[0]), z=float(c[1]), segments=20))
      # nut trap in the -x wall's outside face
      out.append(prism_hex_x(MP.M2_NUT_AF, -SW_CAGE_X[1] - 1.0, -SW_CAGE_X[1] + MP.M2_NUT_T, float(c[0]), float(c[1])))
    out.append(Manifold.batch_hull(pts))
  return union(out)


def prism_hex_x(af: float, x0: float, x1: float, y: float, z: float) -> Manifold:
  r = af / math.sqrt(3)
  pts = [(y + r * math.cos(math.radians(60 * i)), z + r * math.sin(math.radians(60 * i))) for i in range(6)]
  return extrude_x(CrossSection([pts]), x0, x1)


def switch_body_pop() -> Manifold:
  """The room the power switch takes (body, lever and roller), carrier frame on the hinge block."""
  h, rad, along = _switch_frame()
  r0, r1 = SW_BODY_R
  pts = []
  for r in (r0, r1):
    for s in (-MP.SW_LEN / 2, MP.SW_LEN / 2):
      c = h + rad * r + along * s
      pts.append((float(c[0]), float(c[1])))
  cs = CrossSection([[pts[0], pts[1], pts[3], pts[2]]])
  cs = cs if cs.area() > 0 else CrossSection([[pts[0], pts[2], pts[3], pts[1]]])
  return extrude_x(cs, -MP.SW_THICK / 2, MP.SW_THICK / 2)


def _j2_joint(j1_w=None) -> Manifold:
  """The arm's joint, built in the steering wheel frame round the bolt (as faceparts.face_hinge_block), then brought
  into the carrier frame. Its web joins the near cheek's outside."""
  j2 = j2_wheel()
  j1 = np.array(j1_w if j1_w is not None else FP.J1_W)
  u = j1 - j2[:2]
  u = u / np.linalg.norm(u)
  lock_deg = math.degrees(math.atan2(u[1], u[0]))
  zc = float(j2[2])
  half_gap = FP.ARM_T_F / 2.0 + MP.GAP
  z_lo, z_hi = zc - half_gap - FP.J_EAR_T, zc + half_gap + FP.J_EAR_T
  # the near cheek's outer face in the wheel frame: carrier x = -CHEEK_X[1] .. -CHEEK_X[0] -> mount y; tie the ears to a
  # strip along it (in the wheel's x, y at the ears' height)
  Rm, _ = mount_to_wheel()
  cheek_strip = []
  for cz_c in (-62.0, -40.0):
    for cx_c in (-CHEEK_X[1], -CHEEK_X[0]):
      pm = carrier_to_mount_pt((cx_c, 0.0, cz_c))
      pw = Rm @ pm
      cheek_strip.append((float(pw[0]), float(pw[1])))
  strip_cs = CrossSection.batch_hull([CrossSection.circle(1.0, 8).translate(p) for p in cheek_strip])
  ears = [FP.ear_plate(j2[:2], lock_deg, FP.LOCK_RANGE_F, [strip_cs], a, b)
          for a, b in ((z_lo, zc - half_gap), (zc + half_gap, z_hi))]
  web = strip_cs.extrude(z_hi - z_lo).translate((0, 0, z_lo))
  joint_w = union(ears + [web]) - FP.joint_holes(j2[:2], lock_deg, FP.LOCK_RANGE_F, z_lo, z_hi)
  px, py = float(j2[0]), float(j2[1])
  joint_w = joint_w - (cyl(FP.ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap, px, py, 96) +
                       Manifold.batch_hull([cyl(FP.ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap,
                                                px + 80 * math.cos(math.radians(a)), py + 80 * math.sin(math.radians(a)), 48)
                                            for a in (lock_deg - FP.LOCK_RANGE_F - 5, lock_deg + FP.LOCK_RANGE_F + 5)] +
                                           [cyl(FP.ARM_W_F / 2 + 1.0, zc - half_gap, zc + half_gap, px, py, 48)]))
  # wheel -> carrier: inverse of x_w = R x_c + T
  R, T = carrier_to_wheel()
  Rt = R.T
  off = -Rt @ T
  return joint_w.transform([[float(Rt[i, 0]), float(Rt[i, 1]), float(Rt[i, 2]), float(off[i])] for i in range(3)])
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import time; t0=time.time()
import popparts as PP, numpy as np
print('j2 wheel', PP.j2_wheel().round(1), 'carrier', PP.mount_to_carrier(PP.J2_M).round(1))
b = PP.pop_hinge_block(); print('block vol', round(b.volume()), [round(v,1) for v in b.bounding_box()], 'genus', b.genus(), round(time.time()-t0,1))
c = PP.pop_carrier()
for L in (-3.0, -2.9, 0.0, 10, 30, 50, 70, 74.9, 75.0):
  v = (PP.swung(c, L) ^ b).volume()
  print('lift', L, 'carrier/block overlap', round(v,3))
"
