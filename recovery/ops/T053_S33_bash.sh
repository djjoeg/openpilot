cp mountparts.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fitaudit/mountparts.before.py && cp assembly.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fitaudit/assembly.before.py && cp accord_lka_parts.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fitaudit/accord_lka_parts.before.py && python3 - <<'EOF'
p = "mountparts.py"
s = open(p).read()

# 1. counterbore depth as a named constant (same value as before)
old_const = "GUARD_IN = 26.5                       # finger guard inner radius: clears the motor screws' heads\n"
assert s.count(old_const) == 1
s = s.replace(old_const, old_const + "MOTOR_SCREW_CBORE = 2.6               # the motor screws' heads sit this deep in the plate's gear side\n")
old_cb = "      part = part - cyl(M3_CLEAR / 2, -1, t + 1, x, y, 32) - cyl(3.4, t - 2.6, t + 1, x, y, 32)\n"
assert s.count(old_cb) == 1
s = s.replace(old_cb, "      part = part - cyl(M3_CLEAR / 2, -1, t + 1, x, y, 32) - cyl(3.4, t - MOTOR_SCREW_CBORE, t + 1, x, y, 32)\n")

# 2. screws and bolts for the fit checks, and the bolt length table
s = s.rstrip("\n") + '''


# ***** screws and bolts (bought parts), for the fit checks and the bolt lengths *****

M3_BUTTON = (5.7, 1.65)      # ISO 7380 M3 button head: across, tall (the motor screws)
M3_SOCKET = (5.5, 3.0)       # ISO 4762 M3 socket head
M5_WASHER_T, M5_NYLOC_T = 1.0, 5.2
M4_WASHER_T, M4_NYLOC_T, M4_NYLOC_AF = 0.8, 5.0, 7.0
MOTOR_HOLE_DEPTH = 4.5       # the motor's front M3 holes: usual NEMA 17 depth, not confirmed for this motor


def motor_screw_heads(head=M3_BUTTON) -> Manifold:
  """The four motor screws' heads in their counterbores on the plate's gear side (carrier frame)."""
  dk, k = head
  z0 = MOTOR_PLATE_T - MOTOR_SCREW_CBORE
  return union([cyl(dk / 2, z0, z0 + k, sx * NEMA_HOLES / 2, sy * NEMA_HOLES / 2, 48) for sx in (-1, 1) for sy in (-1, 1)])


def switch_screws(length: float = 16.0) -> Manifold:
  """The switch's two M2 screws: heads on the front wall's face, tips out past the rear wall (carrier frame)."""
  parts = []
  for sx in (-1, 1):
    x = SW_X + sx * SW_PITCH / 2
    parts.append(cyl(1.0, CAGE_FRONT[1] - length, CAGE_FRONT[1], x, SW_HOLES, 24) +
                 cyl(1.9, CAGE_FRONT[1], CAGE_FRONT[1] + 2.0, x, SW_HOLES, 24))
  return union(parts)


def lever_bolt(length: float = 35.0) -> Manifold:
  """The lift lever's M4 bolt through the bracket's legs, a washer each side and the lock nut (carrier frame)."""
  y, z = LEVER_PIVOT
  half = BR_LEG_X[1]
  w = M4_WASHER_T
  x_head = -half - w
  return (cyl_x(2.0, x_head, x_head + length, y=y, z=z, segments=24) +
          cyl_x(3.5, x_head - 4.0, x_head, y=y, z=z, segments=24) +
          cyl_x(4.5, -half - w, -half, y=y, z=z, segments=24) + cyl_x(4.5, half, half + w, y=y, z=z, segments=24) +
          cyl_x(M4_NYLOC_AF / 2 / math.cos(math.pi / 6), half + w, half + w + M4_NYLOC_T, y=y, z=z, segments=6))


def spring_body() -> Manifold:
  """Room the spring takes, seat to pocket, with the motor gear on the teeth (carrier frame)."""
  return cyl_y(SPRING_OD / 2, TOP_Y[1] - SPRING_SEAT_D, HB_BOTTOM + SPRING_POCKET_D, z=SPRING_Z, segments=48)


def fastener_table() -> list:
  """Each bolt and screw: what it goes through, and how much length that leaves (mm)."""
  rows = []

  def nut_bolt(name, use, length, stack, washers, nut):
    spare = length - stack - washers - nut
    rows.append({"bolt": name, "use": use, "length": length, "through_mm": round(stack + washers, 1), "nut_mm": nut,
                 "past_the_nut_mm": round(spare, 1), "ok": spare >= 1.5})

  nut_bolt("M5 x 55", "hinge: the hinge block's knuckles and the carrier's between them, lock nut", 55.0,
           2 * BLOCK_KNUCKLE[1], 0.0, M5_NYLOC_T)
  nut_bolt("M5 x 60", "arm to hinge block: both ears and the arm, a washer each side, lock nut", 60.0,
           2 * EAR_X[1], 2 * M5_WASHER_T, M5_NYLOC_T)
  nut_bolt("M5 x 60", "arm to dash clamp: both side plates and the arm, a washer each side, lock nut", 60.0,
           2 * SIDE_PLATE_X[1], 2 * M5_WASHER_T, M5_NYLOC_T)
  nut_bolt("M4 x 35", "lift lever: both bracket legs and the lever, a washer each side, lock nut", 35.0,
           2 * BR_LEG_X[1], 2 * M4_WASHER_T, M4_NYLOC_T)
  # screws that cut their own thread or go into the motor
  into = 10.0 - BR_PLATE_T
  rows.append({"bolt": "M3 x 10", "use": "lever bracket into the carrier", "length": 10.0, "through_mm": BR_PLATE_T,
               "thread_in_mm": into, "hole_depth_mm": BR_SCREW_DEPTH, "ok": 4.0 <= into < BR_SCREW_DEPTH})
  under = MOTOR_PLATE_T - MOTOR_SCREW_CBORE
  into = 6.0 - under
  rows.append({"bolt": "M3 x 6 button head", "use": "carrier plate into the motor", "length": 6.0, "through_mm": under,
               "thread_in_mm": round(into, 1), "hole_depth_mm": MOTOR_HOLE_DEPTH, "ok": 3.0 <= into < MOTOR_HOLE_DEPTH})
  stack = CAGE_FRONT[1] - CAGE_BACK[0]
  rows.append({"bolt": "M2 x 16", "use": "switch: front wall, switch and rear wall, nut in the rear wall", "length": 16.0,
               "through_mm": stack, "past_the_wall_mm": round(16.0 - stack, 1), "ok": 16.0 - stack >= M2_NUT_T})
  # the dash clamp's screw: from under the jaw, through its nut, up to the pad under the cover's edge
  pad_socket = 3.0
  need_thin = -HOOD_EDGE_MIN - 5.0 + pad_socket - JAW_Y0
  need_thick = -HOOD_EDGE_MAX - 5.0 + pad_socket - JAW_Y0
  rows.append({"bolt": "M6 x 40", "use": f"dash clamp: under the jaw up to the pad, for a cover edge {HOOD_EDGE_MIN:.0f} to "
               f"{HOOD_EDGE_MAX:.0f} mm thick", "length": 40.0, "needs_mm": [round(need_thick, 1), round(need_thin, 1)],
               "ok": need_thin <= 40.0})
  return rows
'''
s += "\n"
open(p, "w").write(s)
EOF
grep -n "^import math\|^import" mountparts.py | head; grep -n "SW_PITCH\b" mountparts.py | head -3