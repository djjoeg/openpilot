cat >> sideassembly.py <<'EOF'


def side_margins() -> list:
  """The side-slide mount's own ways of failing, in the margins table's form (margins.py): the worst load, what it can
  take, the factor between them."""
  import gears as GR
  import margins as MG
  rows = []
  g = "Side-slide mount"
  k = MG.motor_k()
  ft_most = P.BOARD_MAX_A * k / (FP.R_P / 1000.0)              # the motor's most push at the teeth, N
  # the gear's teeth: the length they bear on the steering wheel teeth, less the pointed ends and the tips' chamfers
  tb = math.tan(math.radians(S.ROOF_DEG))
  half_at_pitch = (math.pi * GR.MODULE / 2 - P.BACKLASH) / 2
  face = (FP.FACE_BAND[1] - 0.75) - (FP.FACE_BAND[0] + half_at_pitch * tb + 1.5)
  sigma = ft_most / (face * GR.MODULE * 0.296)
  rows.append(MG.row(g, "The 16-tooth gear's teeth don't break", f"{sigma:.1f} MPa at the motor's most push ({ft_most:.0f} N), "
                     f"over the {face:.1f} mm the teeth bear on (the pointed ends and the tips' chamfers left out)",
                     f"{MG.PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending strength across its layers, for repeated loads",
                     MG.PETG_BEND_Z / 3 / sigma, "PETG data sheet; calculated (Lewis)"))
  half_flat = math.sqrt((P.SHAFT_D / 2) ** 2 - (P.SHAFT_ACROSS_FLAT - P.SHAFT_D / 2) ** 2)
  bore_len = min(P.SHAFT_LEN, S.GEAR_HUB[1]) - max(S.GEAR_TEETH_Z[0], P.SHAFT_LEN - P.SHAFT_FLAT_LEN)
  p_max = P.BOARD_MAX_A * k * 1000.0 * 3 / (2 * bore_len * half_flat ** 2)
  rows.append(MG.row(g, "The gear doesn't turn on the motor's shaft", f"{p_max:.0f} MPa where the shaft's flat presses on the "
                     f"gear ({bore_len:.1f} mm of it) at the motor's most push", f"{MG.PETG_TENSILE_XY:.0f} MPa: PETG's tensile "
                     "strength along its layers", MG.PETG_TENSILE_XY / p_max, "PETG data sheet; calculated",
                     note="the set screw on the flat holds it too"))
  f = forces()
  m = f["moving mass (kg, about)"]
  w_along = f["weight along the slide, outwards (N)"]
  bump = w_along * MG.BUMP_G                                   # the parts' weight along the slide on a hard bump
  hold = S.CF["load_N"] - w_along                              # what the latch holds with the motor in, still
  worst_latch = hold + bump
  pin_area = S.KIPP["pin_d"] * S.PIN_IN
  bearing = MG.PETG_BEND_Z / 3 * pin_area
  rows.append(MG.row(g, "The latch holds the motor in", f"{worst_latch:.0f} N: the spring less the motor's weight ({hold:.1f} N), "
                     f"plus the moving parts thrown along the slide by a hard bump ({MG.BUMP_G:g} times gravity: {bump:.0f} N)",
                     f"{bearing:.0f} N: the ear's hole bearing on the pin ({pin_area:.1f} mm2 at a third of PETG's bending "
                     "strength); the steel pin and the plunger's thread take far more", bearing / worst_latch, "calculated"))
  net = S.CF["load_N"] - 0.5
  rows.append(MG.row(g, "Slid in, the spring keeps the motor in on bumps", f"{bump:.0f} N: the moving parts ({m:.2f} kg) along "
                     f"the slide on a hard bump ({MG.BUMP_G:g} times gravity)", f"{net:.1f} N: the spring's pull less the "
                     "block's drag", net / bump, "spring data sheet; calculated; the bump an estimate", kind="condition",
                     note="on a bump harder than that it can move out a little and back; the switch stays off (it would "
                          "have to come 38 mm out) and the gear is 27 mm from the teeth, so nothing happens but a knock"))
  # the block's moments: the gear's push (across) and the teeth pushing it away (towards the dash), at the gear, about
  # the block's middle
  arm_z = (S.GEAR_TEETH_Z[0] + S.GEAR_TEETH_Z[1]) / 2 - S.Z_BLOCK
  sep = ft_most * math.tan(math.radians(GR.PRESSURE_ANGLE) + math.atan(MG.RUB_DRY))
  m_most = math.hypot(ft_most, sep) * arm_z / 1000.0
  rows.append(MG.row(g, "The rail's block takes the gear's push", f"{m_most:.2f} Nm about the block at the motor's most push "
                     f"({ft_most:.0f} N across and {sep:.0f} N pushing the teeth apart, {arm_z:.0f} mm out along the shaft)",
                     "37.5 Nm: the MGN12H block's static moment rating (HIWIN's catalogue)", 37.5 / m_most,
                     "HIWIN catalogue; calculated"))
  # the bracket's flange: the gear's push across bends it where it leaves the block
  lever = (S.GEAR_TEETH_Z[0] + S.GEAR_TEETH_Z[1]) / 2 - S.BLOCK_Z[1]
  sec = (S.FL_Y[1] - S.FL_Y[0]) * S.FLANGE_T ** 2 / 6.0
  sig_f = ft_most * lever / sec
  rows.append(MG.row(g, "The motor bracket's flange doesn't break", f"{sig_f:.1f} MPa where it leaves the block, at the motor's "
                     "most push", f"{MG.PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending strength across its layers",
                     MG.PETG_BEND_Z / 3 / sig_f, "PETG data sheet; calculated"))
  e_in = f["... its energy then (J)"][1]
  rows.append(MG.row(g, "The bumper takes the motor's arrival, slid in", f"{e_in:.2f} J: the moving parts at "
                     f"{f['speed it hits the bumper at, the knob let go at once / held out (m/s, about)'][1]} m/s",
                     "printed bumper and flange end, 100 mm2 of contact: can't be worked out reliably", float("nan"),
                     "proof test", kind="test", check="let it go 20 times at the start: the flange's end and the bumper "
                                                   "may get shiny, nothing may crack"))
  return rows
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0,'.')
import sideassembly as SA, margins as MG
for l in MG.text_lines(SA.side_margins()): print(l)
"