cat >> faceparts.py <<'EOF'


# ***** the lift lever with a paddle *****

PADDLE_LEN = 44.0                 # the paddle reaches this far below the handle's end (lever frame: towards you, lever down)
PADDLE_Z = (MP.HANDLE_LEN - 8.0, MP.HANDLE_LEN)    # ... from this part of the handle


def back_lift_lever(with_finger: bool = True) -> Manifold:
  """The dash mount's lift lever with a paddle under the end of its handle. On this mount the lever sits behind the
  wheel with its handle pointing at the column; the paddle comes down from the handle's end towards you, so with the
  lever down its tip is about 60 mm behind the middle of the grip, inside the rim at 3 o'clock: push it away from
  you to flip the lever up. Lever frame (see mountparts.py); prints on its side like the lift lever."""
  lever = MP.lift_lever(with_finger)
  z0, z1 = PADDLE_Z
  ht = MP.HANDLE_T / 2
  x0, x1 = MP.HANDLE_X
  bar = box(x0, x1, -ht - PADDLE_LEN + ht, 0.0, z0, z1)
  tip = cyl_x((z1 - z0) / 2, x0, x1, y=-ht - PADDLE_LEN + ht, z=(z0 + z1) / 2, segments=48)
  # the corner where the paddle leaves the handle, filled at 45 degrees
  fillet = prism_x([(-ht + 0.01, z0 - 6.0), (-ht + 0.01, z0 + 0.01), (-ht - 6.0, z0 + 0.01)], x0, x1)
  return clean(lever + bar + tip + fillet)


def back_lever_tab() -> Manifold:
  return MP.lever_tab()
EOF
python3 - <<'EOF'
p = "/home/claude/deliver/hardware/cad/faceparts.py"
s = open(p).read()
s = s.replace("""  back hinge block  - the hinge block without its ears on top: its arm's joint hangs underneath instead
""", """  back hinge block  - the hinge block without its ears on top: its arm's joint hangs underneath instead
  back lift lever   - the lift lever with a paddle under its handle's end, so you reach it from inside the rim
""")
s = s.replace("""The motor carrier's other parts (lever bracket, lift lever, spring, setup gauge) are the dash mount's, unchanged.""",
              """The motor carrier's other parts (lever bracket, spring, setup gauge) are the dash mount's, unchanged; the spring sits
on an M5 washer from the start on this mount (the teeth's smaller radius pushes them apart harder).""")
open(p, "w").write(s)
EOF
grep -n "back lift lever\|M5 washer from the start" faceparts.py