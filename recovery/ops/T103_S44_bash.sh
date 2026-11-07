python3 - <<'EOF'
src=open('margins.py').read()
add = '''

TIE_PULL_N = 100.0          # a zip tie pulled tight by hand: about this much tension (estimate on the low side)
SCREW_HOLD_N = 200.0        # a #8 self-tapping screw 8 mm into dash plastic, sideways: estimate on the low side


def side_rows(t, fit) -> list[dict]:
  """The right-side mount's own ways of failing. fit: columnassembly.SideFit."""
  import columnparts as CP
  rows = []
  k = motor_k()
  gear_r = GR.pitch_radius(P.MOTOR_TEETH) / 1000.0
  ft_most = P.BOARD_MAX_A * k / gear_r                       # the motor's most push at the teeth, N
  g = "Right-side mount"
  torque_nm = ft_most * GR.pitch_radius(P.RING_TEETH) / 1000.0
  # the push at the ring turns the bracket about the column; the screw tab holds it at the dash's screw
  r_screw = math.hypot(float(fit.screw_w[0]), float(fit.screw_w[1])) / 1000.0
  f_screw = torque_nm / r_screw
  rows.append(row(g, "The dash's screw holds the screw tab under the motor's push",
                  f"{f_screw:.0f} N sideways at the screw: the motor's most push ({ft_most:.0f} N) at the ring, {torque_nm:.1f} Nm "
                  f"about the column, held {r_screw * 1000:.0f} mm from it",
                  f"about {SCREW_HOLD_N:.0f} N: a self-tapping screw in dash plastic, estimated on the low side",
                  SCREW_HOLD_N / f_screw, "estimated",
                  check="proof pull: with the lift lever up, pull the motor sideways with a luggage scale to 5 kg each way: the "
                        "screw tab must not move at the screw and the bracket must not move on the covers"))
  # the tab bends about its last bolt
  arm_mm = (float(fit.screw_w[0]) - P.WHEEL_OD / 2.0) + P.WHEEL_OD / 2.0 - (fit.bracket_z * 0.0) - (P.COVER_W / 2.0 + CP.SB_BAR_HOLES[1])
  arm_mm = max(arm_mm, 20.0)
  w_mm3 = (CP.TAB_BAR_Z[1] - CP.TAB_BAR_Z[0]) * (CP.TAB_BAR_Y[1] - CP.TAB_BAR_Y[0]) ** 2 / 6.0
  sigma = f_screw * arm_mm / w_mm3
  rows.append(row(g, "The screw tab carries that push to the screw",
                  f"{sigma:.2f} MPa in the tab's bar: {f_screw:.0f} N, {arm_mm:.0f} mm past its last bolt",
                  f"{PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending strength across its layers, for repeated loads",
                  PETG_BEND_Z / 3 / sigma, "PETG data sheet"))
  # the bracket sliding on the covers: the push at the ring also pulls the bracket along the covers' side
  friction = RUBBER_RUB * 3 * TIE_PULL_N
  rows.append(row(g, "The side bracket doesn't slide on the covers under the motor's push",
                  f"{ft_most:.0f} N along the covers' side: the motor's most push at the ring, through the arm",
                  f"about {friction:.0f} N: two rubber strips (rubbing {RUBBER_RUB}) under three zip ties pulled to about "
                  f"{TIE_PULL_N:.0f} N each; the screw tab holds as well", friction / ft_most, "estimated",
                  check="the same proof pull"))
  clamp_c = SUN_CABIN_C + 3.0
  rows.append(row("Heat (light grey PETG)", "The side bracket and screw tab, parked in summer sun",
                  f"about {clamp_c:.0f} C: cabin air, under the dash", f"{PETG_SOFT_C:.0f} C: where PETG starts to soften",
                  (PETG_SOFT_C - HOT_DAY_C) / (clamp_c - HOT_DAY_C), "estimated from a study of parked cars",
                  note="no sunshade needed for these"))
  return rows
'''
marker = "\n\ndef weight_hold("
src = src.replace(marker, add + marker, 1)
open('margins.py','w').write(src)
print('ok')
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0,'.')
import margins as MG, columnassembly as CA, columnparts as CP, params as P
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP, shallow=True); fit = CA.solve_side()
for r in MG.side_rows(t, fit): print(round(r['factor'],2), r['status'], '|', r['what'], '|', r['load'], '|', r['capacity'])
"