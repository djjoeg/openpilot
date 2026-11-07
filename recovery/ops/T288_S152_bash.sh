python3 - <<'EOF'
p = 'incar.py'
s = open(p).read()
old = '''  out += [(m.rotate((0.0, 0.0, wheel_deg)), mat) for m, mat in CP.zip_ties()]
  out += CP.cable()
  return out
'''
new = '''  out += [(m.rotate((0.0, 0.0, wheel_deg)), mat) for m, mat in CP.zip_ties()]
  out += cable()
  return out


def cable() -> list:
  """The board's cable (power and CAN), tidied along the mount: out of its plug, down the motor carrier's outer side to
  the foot of the tower, along under the arm to the column and away under it (the path is a guess; it is how it
  would be tidied)."""
  import columnassembly as CA
  from manifold3d import Manifold
  from cadlib import union
  c = RA.R_FACE_OUT * RA.U
  start = np.array([-12.0, 14.5, -54.0])           # the plug, in the motor's frame
  p0 = np.array([start[1] * RA.V[0] - start[2] * RA.U[0] + c[0], start[1] * RA.V[1] - start[2] * RA.U[1] + c[1],
                 start[0] + RA.Z_AXIS])
  out = np.array([RA.U[0], RA.U[1], 0.0])
  def uv(u, v, z):
    x, y = RA.rad(u, v)
    return np.array([x, y, z])
  pts = [p0, p0 + 9.0 * out, uv(240.0, -36.0, -90.0), uv(238.0, -40.0, -168.0), uv(222.0, -50.0, -178.0),
         np.array([150.0, -147.0, -178.0]), np.array([95.0, -147.0, -178.0]), np.array([60.0, -150.0, -190.0]),
         np.array([10.0, -160.0, -215.0]), np.array([-50.0, -170.0, -250.0])]
  segs = [CA.rod(a, b, 2.4) for a, b in zip(pts[:-1], pts[1:])]
  joints = [Manifold.sphere(2.4, 24).translate(tuple(float(v) for v in q)) for q in pts[1:-1]]
  return [(union(segs + joints), CP.CABLE)]
'''
assert old in s
s = s.replace(old, new)
old2 = '''  return target / model, X, float(np.linalg.norm(X - cam.eye))'''
new2 = '''  g = target / model
  if not ref.get("dash"):
    g = np.full(3, float(np.mean(g)))     # the silver spoke is warm (champagne): its brightness only
  return g, X, float(np.linalg.norm(X - cam.eye))'''
s = s.replace(old2, new2)
open(p, 'w').write(s)
print('ok')
EOF
grep -n "def rad" rightarm.py