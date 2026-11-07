python3 - <<'EOF'
import pathlib
p = pathlib.Path("sideparts.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)
rep("""WINDOW_X, WINDOW_Z = (54.0, 84.0), (-143.0, -115.0)   # the screw's window""",
    """WINDOW_X, WINDOW_Z = (54.0, 84.0), (-144.0, -116.0)   # the screw's window""")
rep("""BAR = (40.0, 8.0, 6.0)            # the foot bar: across (x), along (z), thick; its slot along x takes the screw""",
    """BAR = (40.0, 12.0, 16.0)          # the foot bar: across (x), along (z), thick; its slot along x takes the screw. Thick,
                                  # because the screw's clamp bends it across the window""")
rep("""D_FOOT = (106.0, 125.0)           # the range of carscene.D the foot is drawn for (the cover's front edge at least 69 mm""",
    """D_FOOT = (107.0, 125.0)           # the range of carscene.D the foot is drawn for (the cover's front edge at least 70 mm""")
rep("""COVER_SCREW = "the cover's own 4 mm tapping screw under the key cylinder, 15 mm longer (the same thread), with an M4 washer\"""",
    """COVER_SCREW = ("a 4.2 x 45 mm (#8 x 1 3/4 in) pan head sheet metal screw with an M4 washer, in place of the cover's own 4 x 16 "
               "tapping screw under the key cylinder (the same pitch, 1.41 mm; it goes through the bar, the foot and the shims)")""")
rep("""  return cyl_y(2.0, FOOT_Y[0] - bt - 0.01, cover_y + 12.0, x=x, z=z, segments=24) + \\
    cyl_y(4.0, FOOT_Y[0] - bt - 2.8, FOOT_Y[0] - bt, x=x, z=z, segments=24)""",
    """  return cyl_y(2.1, FOOT_Y[0] - bt - 0.01, cover_y + 10.0, x=x, z=z, segments=24) + \\
    cyl_y(4.0, FOOT_Y[0] - bt - 2.8, FOOT_Y[0] - bt, x=x, z=z, segments=24)""")
p.write_text(s)

p = pathlib.Path("sideassembly.py")
s = p.read_text()
rep("""# motor, board and cover, bracket (PETG, about), gear, block, lever (kg)
MOVING_KG = 0.31 + 0.035 + 0.045 + 0.010 + 0.040 + 0.013""",
    """# motor, board and cover, bracket (PETG, about), gear, block, lever (kg)
MOVING_KG = 0.31 + 0.035 + 0.045 + 0.010 + 0.040 + 0.013
# plate with its foot, rail, spool and spring, switch, bar and shims, screws (kg, about)
FIXED_KG = 0.06 + 0.065 + 0.025 + 0.01 + 0.02 + 0.02""")
rep("""  e_in = f["... its energy then (J)"]
  rows.append(MG.row(g, "The bumper takes the motor's arrival, slid in", """,
    """  # the plate's fixing: the foot on the cover's screw. Its weight (the whole mount) hangs on the screw, and tips the foot
  # about its front edge; the motor's push twists the mount about the screw, held by the foot's rub on the cover
  foot = foot_margins()
  rows.extend(foot)
  e_in = f["... its energy then (J)"]
  rows.append(MG.row(g, "The bumper takes the motor's arrival, slid in", """)
rep("""def slid_in_hold_g() -> float:""",
    """def foot_margins() -> list:
  \"\"\"The foot on the lower column cover's screw: what the screw holds, the twist the foot's rub holds, the foot and the
  bar themselves.\"\"\"
  import gears as GR
  import margins as MG
  g = "Side-slide mount"
  k = MG.motor_k()
  ft_most = P.BOARD_MAX_A * k / (FP.R_P / 1000.0)
  sep = ft_most * math.tan(math.radians(GR.PRESSURE_ANGLE) + math.atan(MG.RUB_DRY))
  # where things are, steering wheel frame: the gear's teeth, the screw (its window's middle), the foot's front edge
  gear = S.wheel_point(0.0, 0.0, sum(S.GEAR_TEETH_Z) / 2)
  screw = np.array([sum(S.WINDOW_X) / 2, S.FOOT_Y[1], sum(S.WINDOW_Z) / 2])
  dz = abs(gear[2] - screw[2])                                     # the push's lever arm about the screw
  twist = ft_most * dz / 1000.0                                    # Nm about the screw, from the push across
  bw, bl, bt = S.BAR
  contact_r = 15.0                                                  # the rub's mean radius from the screw (the clamp spreads
  rub_nm = MG.TAPE_RUB * S.FOOT_CLAMP_N * contact_r / 1000.0        # from the bar through the foot): an estimate
  rub_dry = MG.RUB_DRY * S.FOOT_CLAMP_N * contact_r / 1000.0
  w_all = (MOVING_KG + FIXED_KG) * 9.81
  bump = w_all * MG.BUMP_G
  # the mount's weight hangs at the motor, dz behind the screw along the column and off to one side: it tips the foot
  # about its front edge (on the cover's underside) and the screw takes the pull, foot half-length away
  cg = S.wheel_point(0.0, 0.0, -20.0)
  arm = math.hypot(cg[0] - screw[0], cg[2] - screw[2]) / 1000.0
  half = (S.FOOT_Z[1] - S.FOOT_Z[0]) / 2 / 1000.0
  pull = bump * arm / half + bump
  rows = [
    MG.row(g, "The cover's screw holds the mount", f"{pull:.0f} N on the screw: the mount's weight ({w_all:.1f} N) on a hard "
           f"bump ({MG.BUMP_G:g} times gravity), hanging {arm * 1000:.0f} mm from the screw, tipping the foot about its "
           "front edge", f"{MG.PLATE_SCREW_HOLD_N:.0f} N: the cover's screw into the column's bracket, pulling out or "
           "tearing through the foot's window: an estimate on the low side", MG.PLATE_SCREW_HOLD_N / pull,
           "estimated; calculated"),
    MG.row(g, "The mount doesn't twist on its one screw", f"{twist:.2f} Nm about the screw: the motor's most push "
           f"({ft_most:.0f} N) at the gear, {dz:.0f} mm from the screw along the column",
           f"{rub_nm:.2f} Nm: the foot's rub on the cover's underside, silicone tape on it ({MG.TAPE_RUB:g}), the screw's "
           f"clamp {S.FOOT_CLAMP_N:.0f} N (an estimate on the low side) spread over {contact_r:.0f} mm round the screw",
           rub_nm / twist, "estimates; calculated",
           check=f"push the motor sideways with a luggage scale to {ft_most * 1.5 / 9.81:.0f} kg each way: the plate may "
                 "not move on the cover (mark its edge with tape first)",
           note=f"without the tape (dry, {MG.RUB_DRY:g}) it would be {rub_dry / twist:.2f}: put the tape on"),
    MG.row(g, "The foot bar takes the screw's clamp", f"{3 * S.FOOT_CLAMP_N * (S.WINDOW_X[1] - S.WINDOW_X[0]) / 2 / (2 * (bl - S.BAR_SLOT_W) / 2 * bt ** 2):.1f} MPa "
           f"in the bar, bent across the window by the screw's clamp ({S.FOOT_CLAMP_N:.0f} N)",
           f"{MG.PETG_TENSILE_XY:.0f} MPa: PETG's tensile strength along its layers (the bar is printed flat)",
           MG.PETG_TENSILE_XY / (3 * S.FOOT_CLAMP_N * (S.WINDOW_X[1] - S.WINDOW_X[0]) / 2 / (2 * (bl - S.BAR_SLOT_W) / 2 * bt ** 2)),
           "PETG data sheet; calculated", note="a hard hand on the screw (1000 N) would put it at the limit: snug, then a quarter turn"),
    MG.row(g, "The foot holds the mount's weight", f"{bump * 1000 * (S.FOOT_X[1] - sum(S.WINDOW_X) / 2) * (S.FOOT_Y[1] - S.FOOT_Y[0]) / 2 / ((S.FOOT_Z[1] - S.FOOT_Z[0]) * (S.FOOT_Y[1] - S.FOOT_Y[0]) ** 3 / 12):.1f} MPa "
           f"where the foot leaves the tongue, the mount's weight on a hard bump ({bump:.0f} N) on the screw",
           f"{MG.PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending strength across its layers",
           MG.PETG_BEND_Z / 3 / (bump * 1000 * (S.FOOT_X[1] - sum(S.WINDOW_X) / 2) * (S.FOOT_Y[1] - S.FOOT_Y[0]) / 2 / ((S.FOOT_Z[1] - S.FOOT_Z[0]) * (S.FOOT_Y[1] - S.FOOT_Y[0]) ** 3 / 12)),
           "PETG data sheet; calculated"),
  ]
  return rows


def slid_in_hold_g() -> float:""")
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import sideassembly as SA
for r in SA.foot_margins(): print(r['what'], r['factor'], r['status'], '|', r['load'], '|', r['capacity'])
" 2>&1 | tail -8