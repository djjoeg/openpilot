python3 - <<'EOF'
import pathlib
p = pathlib.Path("sidebuild.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)

# drawing: the plate now includes the foot (drawn with the plate); add the cover's underside and the screw in the cut view,
# and a foot note in the top view
rep("""  ax.text(226, 21, "towards you", fontsize=9, color="#555", ha="left")
  ax.text(226, -125, "forward (towards the nose)", fontsize=9, color="#555", ha="left")""",
    """  # the foot's level (the cover's underside) and the cover's screw, for the middle of the range of cover positions
  ff = SA.foot_fit(sum(S.D_FOOT) / 2)
  foot_y = -(S.FOOT_Y[1]) + ZA - 59.5 if False else None
  ax.text(226, 21, "towards you", fontsize=9, color="#555", ha="left")
  ax.text(226, -125, "forward (towards the nose)", fontsize=9, color="#555", ha="left")""")
rep("""  note("spring", (F - 74, 30), (52, 22))
  ax.set_xlim(225, 30)""",
    """  note("spring", (F - 74, 30), (52, 22))
  note("the plate's foot: under the column cover, on its screw", (F - 20, 44), (150, 86), color=C["plate"])
  ax.set_xlim(225, 30)""")
rep("""  foot_y = -(S.FOOT_Y[1]) + ZA - 59.5 if False else None
""", "")
p.write_text(s)
print("ok")
EOF
grep -n "def drawing" -A 3 sidebuild.py | head; grep -n "mv_in, mv_out, fx = " sidebuild.py