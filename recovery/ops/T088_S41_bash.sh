python3 - <<'EOF'
p='margins.py'; s=open(p).read()
old='''def weight_hold(mesh_from_hinge_mm: float, tilts) -> float:'''
new='''# ----- the column mount -----
CLAMP_SQUEEZE_N = 300.0     # the four threaded rods tightened to "snug, then a quarter turn": about this much between the saddles (estimate)
RUBBER_RUB = 0.4            # rubber strip on the textured covers: an estimate on the low side
SKIRT_SPREAD_MM = 60.0      # the push on the ring's skirt spreads over about this width of it (estimate on the low side)


def column_rows(t) -> list[dict]:
  """The column mount's own ways of failing (its shared parts are covered by table()). t: columnparts.RingTeeth."""
  import columnparts as CP
  rows = []
  k = motor_k()
  gear_r = GR.pitch_radius(P.MOTOR_TEETH) / 1000.0
  ft_most = P.BOARD_MAX_A * k / gear_r                       # the motor's most push at the teeth, N
  phi = math.radians(GR.PRESSURE_ANGLE)
  g = "Column mount"
  # turning the clamp round the covers: the push at the ring is a torque about the column's axis
  torque_nm = ft_most * GR.pitch_radius(P.RING_TEETH) / 1000.0
  v = math.radians(CP.V_DEG)
  normal_total = 2 * CLAMP_SQUEEZE_N / math.cos(v)         # both saddles, each V face taking half the squeeze over cos(V)
  r_contact = 0.045                                         # the rubber strips meet the covers about this far from the column's axis
  friction_nm = RUBBER_RUB * normal_total * r_contact
  rows.append(row(g, "The column clamp doesn't turn round the steering column covers under the motor's push",
                  f"{torque_nm:.1f} Nm about the column: the motor's most push ({ft_most:.0f} N) at the ring",
                  f"about {friction_nm:.0f} Nm: rubber strips (rubbing {RUBBER_RUB}) on four V faces with the rods snug "
                  f"({CLAMP_SQUEEZE_N:.0f} N between the saddles)", friction_nm / torque_nm, "estimated",
                  check="with the lift lever up, push the motor sideways by hand as hard as you can (about 10 kg, 1.8 times the "
                        "motor's most push): the clamp must not move on the covers. On an oval cover the V's shape helps too",
                  note="the covers themselves: plastic shells of unknown stiffness; the push test in the guide is the only check"))
  # the skirt that carries the ring: the spring's press and the teeth's separating push bend it outwards at its far end
  push_n = MP.spring_torque(0) / 50.0 + ft_most * math.tan(phi + math.atan(RUB_DRY))   # roller press (about 29 N) plus separating push
  length = (-CP.RING_BACK_Z + (t.base.wz_out - P.FRONT_RING_T)) - 5.0   # from the front ring's back face to near the roller's middle
  sigma = 6 * push_n * length / (SKIRT_SPREAD_MM * P.SKIRT_T ** 2)
  rows.append(row(g, "The ring's skirt carries the spring's press and the teeth's push",
                  f"{sigma:.1f} MPa at the skirt's root: {push_n:.0f} N at the end of the {P.SKIRT_T:.0f} mm skirt, {length:.0f} mm from the "
                  f"front ring, taken over {SKIRT_SPREAD_MM:.0f} mm of its width",
                  f"{PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending strength across its layers, for repeated loads",
                  PETG_BEND_Z / 3 / sigma, "PETG data sheet; calculated as a flat strip (the curved skirt is stiffer)"))
  # heat: the clamp sits in cabin air, not on the dashboard
  clamp_c = SUN_CABIN_C + 3.0
  rows.append(row("Heat (light grey PETG)", "The column clamp, parked in summer sun", f"about {clamp_c:.0f} C: cabin air, under the dash",
                  f"{PETG_SOFT_C:.0f} C: where PETG starts to soften", (PETG_SOFT_C - HOT_DAY_C) / (clamp_c - HOT_DAY_C),
                  "estimated from a study of parked cars", note="no sunshade needed for this clamp"))
  return rows


def weight_hold(mesh_from_hinge_mm: float, tilts) -> float:'''
assert old in s; s=s.replace(old,new,1)
open(p,'w').write(s); print("ok")
EOF
cd /home/claude/deliver/hardware/cad && grep -n "spring_torque\|presses_roller" margins.py | head -3; grep -n "def spring_torque" mountparts.py