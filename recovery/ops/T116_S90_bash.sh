python3 - <<'EOF'
p = "margins.py"
s = open(p).read()
anchor = "def weight_hold(mesh_from_hinge_mm: float, tilts) -> float:"
assert anchor in s
new = '''PLATE_SCREW_HOLD_N = 250.0  # one of the lower column cover's screws (4 mm tapping into its boss, or the 5 mm screw into the
                            # column's bracket) pulling out or tearing through the plate's slot: an estimate on the low side


def back_rows(t, fit, shim_mm: float = 1.0) -> list[dict]:
  """The back-teeth mount's own ways of failing. t: faceparts.FaceTeeth; fit: faceassembly.FaceFit. shim_mm: the M5
  washer under the spring, standard on this mount."""
  import faceparts as FP
  rows = []
  k = motor_k()
  gear_r = FP.R_P / 1000.0
  face_r = FP.R_F / 1000.0
  ft_most = P.BOARD_MAX_A * k / gear_r                      # the motor's most push at the teeth, N
  phi = math.radians(GR.PRESSURE_ANGLE)
  g = "Back-teeth mount"
  # the spring holds the gear in the teeth: its turning force about the hinge, taken at the teeth's middle along the
  # shaft (the motor's weight doesn't help here: the hinge's axis is upright)
  mesh_from_hinge = (FP.FG_TEETH[0] + FP.FG_TEETH[1]) / 2 - MP.HINGE[1]
  force = MP.spring_force(0) + MP.SPRING_RATE * shim_mm
  hold = force * MP.SPRING_ARM / mesh_from_hinge
  ft = P.LANE_KEEPING_MOST_NM / face_r
  sep_dry = ft * math.tan(phi + math.atan(RUB_DRY))
  short = (MP.SPRING_RATE * (MP.SPRING_FREE - MP.SPRING_FREE_TOL - MP.SPRING_LEN + shim_mm)) * MP.SPRING_ARM / mesh_from_hinge
  motor_most_nm = P.BOARD_MAX_A * k * FP.FACE_RATIO
  rows.append(row(g, "The motor gear stays in the back teeth at the most push lane keeping uses, teeth dry",
                  f"{sep_dry:.1f} N pushing the teeth apart at {P.LANE_KEEPING_MOST_NM} Nm, with dry teeth rubbing (the teeth "
                  f"sit at {FP.R_F:.0f} mm, so they push apart harder than the other mounts' at {GR.pitch_radius(P.RING_TEETH):.0f})",
                  f"{hold:.1f} N: the spring with the M5 washer under it ({force:.1f} N)", hold / sep_dry,
                  "calculated; rubbing estimated",
                  check=f"the grip test in the car setup pushes with the most the motor can ({motor_most_nm:.2f} Nm) while you hold "
                        "the wheel: nothing may slip",
                  note=f"{short / sep_dry:.2f} with the shortest spring within Lee Spring's tolerance; "
                       f"{(MP.spring_force(0) * MP.SPRING_ARM / mesh_from_hinge) / sep_dry:.2f} without the washer"))
  up_n = MP.spring_force(MP.LIFT_DEG + 1.0) + MP.SPRING_RATE * shim_mm
  rows.append(row(g, "The spring with its washer isn't squashed past what it can take (lever up)",
                  f"about {up_n:.1f} N", f"{MP.SPRING_MAX_N} N: fully squashed, the most Lee Spring sizes it for",
                  MP.SPRING_MAX_N / up_n, "spring data sheet; calculated"))
  # Lewis bending at the 16-tooth motor gear's teeth at the motor's most push
  face = FP.FACE_BAND[1] - FP.FACE_BAND[0] - 2 * 1.5 * 0.5     # the tips' end chamfers take a little off
  lewis_y = 0.296               # Lewis form factor, 16 teeth, 20 degree full depth
  sigma = ft_most / (face * GR.MODULE * lewis_y)
  rows.append(row(g, "The 16-tooth motor gear's teeth don't break", f"{sigma:.1f} MPa at the motor's most push ({ft_most:.0f} N)",
                  f"{PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending strength across its layers, for repeated loads",
                  PETG_BEND_Z / 3 / sigma, "PETG data sheet; calculated (Lewis)"))
  half_flat = math.sqrt((P.SHAFT_D / 2) ** 2 - (P.SHAFT_ACROSS_FLAT - P.SHAFT_D / 2) ** 2)
  bore_len = min(P.SHAFT_LEN, FP.FG_TEETH[1]) - FP.FG_ROLLER[0]
  p_max = P.BOARD_MAX_A * k * 1000.0 * 3 / (2 * bore_len * half_flat ** 2)
  rows.append(row(g, "The motor gear doesn't turn on the motor's shaft", f"{p_max:.0f} MPa where the shaft's flat presses on the "
                  "gear at the motor's most push", f"{PETG_TENSILE_XY:.0f} MPa: PETG's tensile strength along its layers",
                  PETG_TENSILE_XY / p_max, "PETG data sheet; calculated", note="the set screw on the flat holds it too"))
  ties = 6
  grip_cap = ties * 2 * ZIP_TIE_N * TAPE_RUB
  rows.append(row(g, "The back teeth don't slide round the grip", f"{ft_most:.0f} N: the motor's most push at the teeth",
                  f"{grip_cap:.0f} N: {ties} zip ties pulled tight on silicone tape; the notch round the right spoke's junction "
                  "also stops it", grip_cap / ft_most, "estimated", check="the grip test: if the teeth slide on the grip, it fails"))
  # the column plate on the cover's screws: the push at the teeth reaches the plate's joint as a turning force about it
  arm_mm = float(np.linalg.norm(fit.j2[:2] - fit.j1[:2])) if fit is not None else 165.0
  screws = 2
  span = (FP.PL_SLOT_Z[1] - FP.PL_SLOT_Z[0]) / 2
  pull = ft_most * (arm_mm + span) / span / screws
  rows.append(row(g, "The column plate holds on the cover's screws", f"about {pull:.0f} N on each of {screws} screws: the motor's most "
                  f"push ({ft_most:.0f} N) on the arm, {arm_mm:.0f} mm out from the plate's joint, against screws about "
                  f"{span:.0f} mm apart along the plate", f"about {PLATE_SCREW_HOLD_N:.0f} N each: the cover's screws, estimated "
                  "on the low side", PLATE_SCREW_HOLD_N / pull, "estimated",
                  check="proof pulls with a luggage scale at the motor, lever up (see the guide): nothing may move",
                  note="the lower cover itself is a plastic shell of unknown stiffness; the proof pulls are the check"))
  sideways = ft_most
  up = (force * MP.SPRING_ARM / ((FP.FG_ROLLER[0] + FP.FG_ROLLER[1]) / 2 - MP.HINGE[1])) + ft_most * math.tan(phi + math.atan(RUB_DRY))
  down = MOUNTED_KG * 9.81 * BUMP_G

  def kg(n):
    return math.ceil(1.5 * n / 9.81 * 2) / 2

  rows.append(row(g, "The arm's joints and the column plate hold", f"up to {sideways:.0f} N up or down at the motor gear (its most "
                  f"push), {up:.0f} N towards the dash (the spring and the teeth pushing apart) and {down:.0f} N down (the parts' "
                  f"weight on a bump, {BUMP_G:g} times gravity)", "friction in bolted printed joints: can't be worked out reliably",
                  float("nan"), "proof test", kind="test",
                  check=f"proof pulls with a luggage scale at the motor, lever up: {kg(sideways):.1f} kg up and down, {kg(up):.1f} kg "
                        f"towards the dash and {kg(down):.1f} kg down (1.5 times each load); nothing may move"))
  plate_c = SUN_CABIN_C + 3.0
  rows.append(row("Heat (light grey PETG)", "The column plate, parked in summer sun", f"about {plate_c:.0f} C: cabin air, under the column",
                  f"{PETG_SOFT_C:.0f} C: where PETG starts to soften", (PETG_SOFT_C - HOT_DAY_C) / (plate_c - HOT_DAY_C),
                  "estimated from a study of parked cars", note="the back teeth are on the wheel: the shared row above covers them"))
  return rows


'''
s = s.replace(anchor, new + anchor)
if "import numpy as np" not in s:
  s = s.replace("import math\n", "import math\n\nimport numpy as np\n", 1)
open(p, "w").write(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0,'.')
import faceparts as FP, faceassembly as FA, margins as MG
t = FP.FaceTeeth(); fit = FA.solve_face(t)
for r in MG.back_rows(t, fit):
  print(r['factor'], r['status'], '|', r['what'], '|', r['load'][:90], '|', r['note'][:100])
"