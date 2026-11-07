cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && python3 - <<'EOF'
p='study90.py'
s=open(p).read()
old_start=s.index('def radial_parts(')
old_end=s.index('def bevel_parts(')
new='''def radial_parts(mount_deg: float, dash: str = "motor"):
  """The board lies flat on the motor's back (its bare side down), its parts and side-entry plugs facing the column
  (6 mm), under a printed cap (1 mm gap, 2 mm wall). dash = which of the board's two plugs faces the dash: "motor" (the
  car plug then faces 6 o'clock) or "car" (the motor plug then faces 4 o'clock)."""
  cs = board_cs().mirror((0, 1))            # KiCad y down -> carrier y_c = -y_k
  if dash == "car":
    cs = cs.rotate(90.0)
  board = cs.offset(1.0 + 2.0, CrossSection.JoinType.Round).extrude(10.5).translate((0, 0, -50.5)) ^ \\
    box(-30, 30, -30, 30, -50.5, -40.0)
  z0, z1 = -47.6, -41.6
  if dash == "motor":
    plug_side = box(20.05, 20.05 + PLUG, -13.3, 1.7, z0, z1)          # car plug, 6 o'clock side
    plug_dash = box(-8.7, 6.3, 22.94, 22.94 + PLUG, z0, z1)           # motor plug, to the dash
    names = ("car plug (6 o'clock)", "motor plug (to dash)")
  else:
    plug_dash = box(-1.7, 13.3, 20.05, 20.05 + PLUG, z0, z1)          # car plug, to the dash
    plug_side = box(-22.94 - PLUG, -22.94, -8.7, 6.3, z0, z1)         # motor plug, 4 o'clock side
    names = ("motor plug (4 o'clock)", "car plug (to dash)")
  own_plug = box(-8.0, 8.0, H, H + PLUG, -38.0, -22.0)    # the motor's own 6-pin plug, on its dash side
  motor = box(-H, H, -H, H, -40.0, 0.0) + cyl(11.0, 0.0, 2.0)
  return {"motor": motor, "board+cap": board, names[0]: plug_side, names[1]: plug_dash,
          "motor's own plug": own_plug, "plate+guard": core_carrier(with_knuckle=False) ^ box(-60, 60, -60, 6.0, -1.0, 60),
          "gear": PP.pop_motor_gear()}


'''
s=s[:old_start]+new+s[old_end:]
s=s.replace('PLUG = 12.0               # a plug and its cable\'s first bend stand this far out from the board\'s edge (estimate)',
            'PLUG = 10.0               # a plug and its cable\'s first bend stand this far out from the board\'s edge (estimate)')
s=s.replace('  parts = radial_parts(mount) if which == "radial" else bevel_parts(a)',
            '  parts = radial_parts(mount, which.split(":")[1] if ":" in which else "motor") if which.startswith("radial") else bevel_parts(a)')
open(p,'w').write(s)
EOF
grep -n "PLUG =\|def radial_parts\|parts = radial" study90.py