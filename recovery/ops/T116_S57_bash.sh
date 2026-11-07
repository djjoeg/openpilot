cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && cat >> facegen_test.py <<'EOF'


def face_block(n_spaces: int = 9) -> Manifold:
  """A block of face teeth around phi = 0: the band from the root to the tips over BAND, minus n_spaces spaces."""
  sp = tooth_space()
  half = (n_spaces // 2 + 0.5) * PITCH_DEG
  from cadlib import revolve
  band = revolve([(BAND[0], Z_TIP), (BAND[1], Z_TIP), (BAND[1], Z_ROOT + 3.0), (BAND[0], Z_ROOT + 3.0)], -half, half, step_deg=0.05)
  spaces = Manifold.batch_boolean([sp.rotate((0, 0, j * PITCH_DEG)) for j in range(-(n_spaces // 2), n_spaces // 2 + 1)], OpType.Add)
  return band - spaces


def pinion_solid(x0: float = 160.0, x1: float = 172.0, z_axis: float = Z_AXIS) -> Manifold:
  return gear_prism(GR.gear_outline(NP, BACKLASH), x0, x1, 0.0, z_axis)


def pinion_at(theta: float, extra_spin: float = 0.0, z_axis: float = Z_AXIS) -> Manifold:
  """The real pinion with the wheel turned theta (face frame): the pinion's axis at -theta, spun -K*theta (+extra)."""
  m = GR.gear_outline(NP, BACKLASH).rotate(-K * theta + extra_spin).extrude(12.0).translate((0, 0, 160.0))
  return to_wheel(m, z_axis).rotate((0, 0, -theta))


if __name__ == "__main__":
  t = time.time()
  fb = face_block()
  print("face block volume", round(fb.volume(), 1), "in", round(time.time() - t, 1), "s")
  worst = 0.0
  for th in np.arange(-6.0, 6.0001, 0.1):
    v = (fb ^ pinion_at(th)).volume()
    worst = max(worst, v)
  print("worst overlap over -6..6 deg (mm^3):", worst)
  # free play: with the wheel held at theta=0, how far the pinion turns each way before touching
  for sign in (1, -1):
    a = 0.0
    while a < 10:
      if (fb ^ pinion_at(0.0, sign * (a + 0.05))).volume() > 1e-4:
        break
      a += 0.05
    print("free play", "ccw" if sign > 0 else "cw", round(a, 2), "deg of pinion =", round(math.radians(a) * RP, 3), "mm at its pitch circle")
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 facegen_test.py