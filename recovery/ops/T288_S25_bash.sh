python3 - <<'EOF'
p = "photorender.py"
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)
rep("""  def __init__(self, albedo, spec=0.04, shine=30.0, smooth=True, crease=40.0):
    self.albedo = np.asarray(albedo, dtype=np.float32)
    self.spec, self.shine, self.smooth, self.crease = float(spec), float(shine), bool(smooth), float(crease)""",
    """  def __init__(self, albedo, spec=0.04, shine=30.0, smooth=True, crease=40.0, grain=0.0, grain_mm=0.8):
    self.albedo = np.asarray(albedo, dtype=np.float32)
    self.spec, self.shine, self.smooth, self.crease = float(spec), float(shine), bool(smooth), float(crease)
    self.grain, self.grain_mm = float(grain), float(grain_mm)       # a pebbled surface: albedo varied this much""")
rep("""  P, N, ALB, SPEC, SHINE = [], [], [], [], []""", """  P, N, ALB, SPEC, SHINE, GRAIN, GMM = [], [], [], [], [], [], []""")
rep("""    SHINE.append(np.full(len(t), mat.shine))
  P = np.concatenate(P)""", """    SHINE.append(np.full(len(t), mat.shine))
    GRAIN.append(np.full(len(t), mat.grain))
    GMM.append(np.full(len(t), mat.grain_mm))
  P = np.concatenate(P)""")
rep("""  SHINE = np.concatenate(SHINE).astype(np.float32)
""", """  SHINE = np.concatenate(SHINE).astype(np.float32)
  GRAIN = np.concatenate(GRAIN).astype(np.float32)
  GMM = np.concatenate(GMM).astype(np.float32)
""")
rep("""  # shading
  alb = ALB[t_hit].astype(np.float64)""", """  # shading
  alb = ALB[t_hit].astype(np.float64)
  g = GRAIN[t_hit].astype(np.float64)
  if g.any():
    def vnoise(q):
      c = np.floor(q)
      f = q - c
      f = f * f * (3 - 2 * f)
      def h(o):
        k = c + o
        return np.modf(np.abs(np.sin(k @ np.array([12.9898, 78.233, 37.719])) * 43758.5453))[0]
      out = 0.0
      for ox in (0, 1):
        for oy in (0, 1):
          for oz in (0, 1):
            wgt = (f[:, 0] if ox else 1 - f[:, 0]) * (f[:, 1] if oy else 1 - f[:, 1]) * (f[:, 2] if oz else 1 - f[:, 2])
            out = out + wgt * h(np.array([ox, oy, oz], float))
      return out
    sc_mm = GMM[t_hit].astype(np.float64)[:, None]
    nz = 0.65 * vnoise(pts / sc_mm) + 0.35 * vnoise(pts / (sc_mm * 0.45) + 17.0)
    alb = alb * (1 + g[:, None] * (nz[:, None] - 0.5) * 2)""")
open(p, "w").write(s)

p = "carphoto.py"
s = open(p).read()
def rep2(old, new):
    global s
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)
rep2("PLUG = PR.Mat((0.62, 0.60, 0.52), spec=0.10, shine=30, smooth=False)", "PLUG = PR.Mat((0.34, 0.31, 0.24), spec=0.10, shine=30, smooth=False)")
rep2("RIM = PR.Mat((0.014, 0.014, 0.016), spec=0.03, shine=12)", "RIM = PR.Mat((0.016, 0.016, 0.018), spec=0.03, shine=12, grain=0.35, grain_mm=0.9)")
rep2("HUB = PR.Mat((0.013, 0.013, 0.015), spec=0.025, shine=10)", "HUB = PR.Mat((0.014, 0.014, 0.016), spec=0.025, shine=10, grain=0.3, grain_mm=0.9)")
rep2("COVER = PR.Mat((0.011, 0.011, 0.013), spec=0.025, shine=10)", "COVER = PR.Mat((0.012, 0.012, 0.014), spec=0.025, shine=10, grain=0.3, grain_mm=0.7)")
rep2("DASH = PR.Mat((0.30, 0.29, 0.27), spec=0.02, shine=10, smooth=False)", "DASH = PR.Mat((0.22, 0.215, 0.20), spec=0.02, shine=10, smooth=False, grain=0.12, grain_mm=0.8)")
rep2("NYLON = PR.Mat((0.01, 0.01, 0.01), spec=0.15, shine=40)", "NYLON = PR.Mat((0.01, 0.01, 0.01), spec=0.15, shine=40)\nCABLE = PR.Mat((0.012, 0.012, 0.012), spec=0.12, shine=25)")
rep2("""  wall = box(-700.0, 700.0, -600.0, 400.0, sc.dash_z - 40.0, sc.dash_z) - (box(-1e3, 1e3, -1e3, 1e3, -1e3, 1e3) - sc.bolster().hull()) \\
    if False else sc.bolster()
  big = box""", """  big = box""")
rep2("""def build_parts() -> list:""", '''def cable() -> list:
  """The board's power and data cable: out of its plug, down beside the tower and off under the column towards the
  lever nuts (its path is a guess)."""
  start = np.array([-12.0, 14.5, -54.0])           # the plug, in the motor's frame
  c = RA.R_FACE_OUT * RA.U
  p0 = np.array([start[1] * RA.V[0] - start[2] * RA.U[0] + c[0], start[1] * RA.V[1] - start[2] * RA.U[1] + c[1],
                 start[0] + RA.Z_AXIS])
  pts = [p0, p0 + 14.0 * np.array([RA.U[0], RA.U[1], 0.0]), p0 + np.array([18.0, -40.0, -20.0]),
         np.array([215.0, -175.0, -120.0]), np.array([180.0, -205.0, -175.0]), np.array([90.0, -215.0, -230.0])]
  import columnassembly as CA
  segs = [CA.rod(a, b, 2.6) for a, b in zip(pts[:-1], pts[1:])]
  joints = [Manifold.sphere(2.6, 24).translate(tuple(float(v) for v in q)) for q in pts[1:-1]]
  return [(union(segs + joints), CABLE)]


def build_parts() -> list:''')
rep2("  return out + motor_parts(0.0) + zip_ties()", "  return out + motor_parts(0.0) + zip_ties() + cable()")
rep2("img = PR.render(sc, cam, KEY, key_power=2.4, sky_up=WORLD_UP, ambient=1.0, fill_dir=fill, fill_power=0.55, ss=2, exposure=1.25)",
     "img = PR.render(sc, cam, KEY, key_power=2.2, sky_up=WORLD_UP, ambient=0.9, fill_dir=fill, fill_power=0.5, ss=2, exposure=0.95)")
open(p, "w").write(s)
print("ok")
EOF
grep -n "def rod" -A 8 columnassembly.py | head -12; (time PYTHONPATH=/home/claude/pylib timeout 1800 python3 carphoto.py 640) 2>&1 | tail -4