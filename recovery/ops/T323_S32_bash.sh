python3 - <<'EOF'
p = "stiffness.py"
s = open(p, encoding="utf-8").read()
reps = [
("""How far the motor's push moves the gear in and out of the teeth (3 Nov 2026): a finite-element model of the arm, the
tower and the motor carrier (v5), and of the frame plate holding them.""",
 """How far the motor's push moves the gear in and out of the teeth (3 Nov 2026): a finite-element model of the arm, the
tower and the motor carrier (v6, the fit print), and of the frame plate (v5) holding them; at the drawn place and at
the slides' ends that bend it most (the arm slid 17.5 mm out of the receiver, the motor slid 12 mm up the tower)."""),
("""  receiver  the arm's bar held rigidly inside the receiver: stiffer than the car (no receiver, plate or cover);
  plate     the frame plate added, held only round its two screws (9 mm washers): softer than the car, which
            also has the column cover under the plate.""",
 """  receiver  the arm's bar held rigidly inside the receiver: stiffer than the car (no receiver, plate or cover);
  plate     the frame plate added, the arm's bar bonded into its receiver (the wing bolt pulls it tight against the
            wall), the plate held only round its two screws (9 mm washers): softer than the car, which also has the
            column cover under the plate."""),
("""v4 for the record (the 10 mm arm): receiver +0.85 to +0.99 / -1.41 to -1.63 mm (1.5 and 2 mm cubes), plate
+1.32 / -2.08 mm: it failed.

  python3 stiffness.py        # a few minutes; prints the movements and PASS or FAIL; exit 1 on FAIL""",
 """For the record: v4 (the 10 mm arm) receiver +0.85 to +0.99 / -1.41 to -1.63 mm (1.5 and 2 mm cubes), plate
+1.32 / -2.08 mm: it failed. v5 (the arm 50 deep, 10 x 30 in the receiver) +0.20 / -0.49 and +0.56 / -1.00: passed.

  python3 stiffness.py        # 15 to 20 minutes; prints the movements and PASS or FAIL; exit 1 on FAIL
  python3 stiffness.py quick  # the drawn place only, a few minutes"""),
("""def model(with_plate: bool):
  m = RA.arm() + RA.carrier(0.0) + RA.uvz(RA.CH_U[0], RA.CH_U[1], RA.CH_V0, RA.CH_V1, RA.BAR_Z[0], RA.TOWER_Z[1])
  if with_plate:                                   # the plate, the arm's bar bonded into its receiver
    m = m + RA.plate_to_wheel(RA.frame_plate_v4()) + box(RA.ARM_X[0], 120.0, -143.4, -113.0, -175.4, -165.0)
  return m""",
 """def model(with_plate: bool, dx: float = 0.0, dz: float = 0.0):
  \"\"\"The arm slid dx across in the receiver, the carrier dz up the tower; the carrier's bar bonded in the tube.\"\"\"
  bar_end = max(RA.BAR_Z[0] + dz, RA.TOWER_Z[0])
  m = RA.arm() + RA.carrier(dz) + RA.uvz(RA.CH_U[0], RA.CH_U[1], RA.CH_V0, RA.CH_V1, bar_end, RA.TOWER_Z[1])
  m = m.translate((dx, 0.0, 0.0))
  if with_plate:                                   # the plate, the arm's bar bonded into its receiver
    m = m + RA.plate_to_wheel(RA.frame_plate_v5()) + \\
      box(RA.ARM_X[0] + dx, RA.RECEIVER_MOUTH, RA.ARM_Y[0] - 0.4, RA.ARM_Y[1], RA.ARM_Z[0] - 0.2, RA.ARM_Z[1] + 0.2)
  return m"""),
("""def solve(with_plate: bool) -> dict:
  t0 = time.time()
  vox, lo = voxelize(model(with_plate), H)""",
 """def solve(with_plate: bool, dx: float = 0.0, dz: float = 0.0) -> dict:
  t0 = time.time()
  vox, lo = voxelize(model(with_plate, dx, dz), H)"""),
("""  xyz = lo + nodes * H
  u_of = xyz[:, :2] @ RA.U
  v_of = xyz[:, :2] @ RA.V""",
 """  xyz = lo + nodes * H
  xy_m = xyz[:, :2] - np.array([dx, 0.0])          # in the motor's frame, which moves with the arm
  u_of = xy_m @ RA.U
  v_of = xy_m @ RA.V"""),
("""    fixed = xyz[:, 0] <= 120.0 + 1e-6              # the bar inside the receiver""",
 """    fixed = xyz[:, 0] <= RA.RECEIVER_MOUTH + 1e-6  # the bar inside the receiver"""),
("""         (np.abs(xyz[:, 2] - RA.Z_AXIS) <= RA.H)  # the carrier's plate behind the motor's face""",
 """         (np.abs(xyz[:, 2] - RA.Z_AXIS - dz) <= RA.H)  # the carrier's plate behind the motor's face"""),
("""  P = np.array([R_PITCH * RA.U[0], R_PITCH * RA.U[1], RA.Z_AXIS + 16.0])""",
 """  P = np.array([R_PITCH * RA.U[0] + dx, R_PITCH * RA.U[1], RA.Z_AXIS + 16.0 + dz])"""),
("""  print(f"  {'with the frame plate' if with_plate else 'held in the receiver'}: {vox.sum()} cubes, {len(fd)} unknowns, "
        f"{time.time() - t0:.0f} s")
  return out


def main() -> int:
  ok = True
  for with_plate in (False, True):
    res = solve(with_plate)
    for name, d in res.items():""",
 """  print(f"  {'with the frame plate' if with_plate else 'held in the receiver'}: {vox.sum()} cubes, {len(fd)} unknowns, "
        f"{time.time() - t0:.0f} s")
  return out


CASES = ((0.0, 0.0, "as drawn"), (RA.ARM_SLIDE, 0.0, "the arm slid 17.5 out"),
         (0.0, RA.DZ_DEEP, "the motor slid 12 up"), (RA.ARM_SLIDE, RA.DZ_DEEP, "both"))


def main() -> int:
  ok = True
  cases = CASES[:1] if "quick" in sys.argv[1:] else CASES
  for dx, dz, label in cases:
   print(f"{label} (arm {dx:+.1f} across, motor {dz:+.0f} along the column):")
   for with_plate in (False, True):
    res = solve(with_plate, dx, dz)
    for name, d in res.items():"""),
]
for a, b in reps:
  assert s.count(a) == 1, a[:70]
  s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
sed -n 170,200p stiffness.py