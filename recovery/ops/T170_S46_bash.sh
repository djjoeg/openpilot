python3 - <<'EOF'
import pathlib
p = pathlib.Path("sideassembly.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)
rep("""    MG.row(g, "The foot holds the mount's weight", f"{bump * 1000 * (S.FOOT_X[1] - sum(S.WINDOW_X) / 2) * (S.FOOT_Y[1] - S.FOOT_Y[0]) / 2 / ((S.FOOT_Z[1] - S.FOOT_Z[0]) * (S.FOOT_Y[1] - S.FOOT_Y[0]) ** 3 / 12):.1f} MPa "
           f"where the foot leaves the tongue, the mount's weight on a hard bump ({bump:.0f} N) on the screw",
           f"{MG.PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending strength across its layers",
           MG.PETG_BEND_Z / 3 / (bump * 1000 * (S.FOOT_X[1] - sum(S.WINDOW_X) / 2) * (S.FOOT_Y[1] - S.FOOT_Y[0]) / 2 / ((S.FOOT_Z[1] - S.FOOT_Z[0]) * (S.FOOT_Y[1] - S.FOOT_Y[0]) ** 3 / 12)),
           "PETG data sheet; calculated"),
  ]
  return rows""",
    """    MG.row(g, "The foot holds the mount's weight", f"{sig_foot:.1f} MPa where the foot leaves the tongue, the mount's "
           f"weight on a hard bump ({bump:.0f} N) on the screw", f"{MG.PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending "
           "strength across its layers", MG.PETG_BEND_Z / 3 / sig_foot, "PETG data sheet; calculated"),
  ]
  return rows""")
rep("""  pull = bump * arm / half + bump
  rows = [""", """  pull = bump * arm / half + bump
  # the foot: a beam from the tongue to the screw, bent by that pull; the bar: bent across the window by the clamp
  t_foot = S.FOOT_Y[1] - S.FOOT_Y[0]
  sig_foot = pull * (S.FOOT_X[1] - screw[0]) * (t_foot / 2) / ((S.FOOT_Z[1] - S.FOOT_Z[0]) * t_foot ** 3 / 12)
  sig_bar = 3 * S.FOOT_CLAMP_N * (S.WINDOW_X[1] - S.WINDOW_X[0]) / 2 / (2 * (bl - S.BAR_SLOT_W) / 2 * bt ** 2)
  rows = [""")
rep("""    MG.row(g, "The foot bar takes the screw's clamp", f"{3 * S.FOOT_CLAMP_N * (S.WINDOW_X[1] - S.WINDOW_X[0]) / 2 / (2 * (bl - S.BAR_SLOT_W) / 2 * bt ** 2):.1f} MPa "
           f"in the bar, bent across the window by the screw's clamp ({S.FOOT_CLAMP_N:.0f} N)",
           f"{MG.PETG_TENSILE_XY:.0f} MPa: PETG's tensile strength along its layers (the bar is printed flat)",
           MG.PETG_TENSILE_XY / (3 * S.FOOT_CLAMP_N * (S.WINDOW_X[1] - S.WINDOW_X[0]) / 2 / (2 * (bl - S.BAR_SLOT_W) / 2 * bt ** 2)),
           "PETG data sheet; calculated", note="a hard hand on the screw (1000 N) would put it at the limit: snug, then a quarter turn"),""",
    """    MG.row(g, "The foot bar takes the screw's clamp", f"{sig_bar:.1f} MPa in the bar, bent across the window by the "
           f"screw's clamp ({S.FOOT_CLAMP_N:.0f} N)", f"{MG.PETG_TENSILE_XY:.0f} MPa: PETG's tensile strength along its "
           "layers (the bar is printed flat)", MG.PETG_TENSILE_XY / sig_bar, "PETG data sheet; calculated",
           note=f"a hard hand on the screw (1000 N) would take it to {sig_bar * 1000 / S.FOOT_CLAMP_N:.0f} MPa: tighten it "
                "until the foot can't be moved by hand, then a quarter turn more"),""")
p.write_text(s)
p = pathlib.Path("sideparts.py")
s = p.read_text()
rep("""FOOT_CLAMP_N = 400.0              # the screw's clamp on the foot: an estimate on the low side (a small tapping screw tightened by hand)""",
    """FOOT_CLAMP_N = 600.0              # the screw's clamp on the foot: an estimate on the low side (a 4.2 mm screw into steel,
                                  # tightened with a screwdriver by hand, reaches about 1000 N)""")
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import sideassembly as SA
for r in SA.foot_margins(): print(r['what'], r['factor'], r['status'], '|', r['load'], '|', r['capacity'], '|', r['note'])
" 2>&1 | tail -5