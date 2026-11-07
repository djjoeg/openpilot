python3 - <<'EOF'
p = 'incar.py'
s = open(p).read()
a = s.index('def occluders() -> list:')
b = s.index('def main(argv):')
new = '''def backproject(cam: PC.PhotoCam, uv, z: float) -> np.ndarray:
  """The point on the plane z (steering wheel frame) that the photo's pixel uv shows."""
  d = cam.R.T @ np.array([(uv[0] - cam.c[0]) / cam.f, (uv[1] - cam.c[1]) / cam.f, 1.0])
  e = cam.eye
  return e + (z - e[2]) / d[2] * d


def wheel_front(cam: PC.PhotoCam, openings, r: float = 152.0, z: float = 15.0):
  """The steering wheel's hub, spokes and buttons as a thin sheet just in front of the grip: a disc inside the grip
  less the openings you can see through (outlined on the photo, carried onto the sheet's plane)."""
  from manifold3d import CrossSection
  disc = CrossSection.circle(r, 180)
  for poly in openings:
    pts = [tuple(backproject(cam, uv, z)[:2]) for uv in poly]
    area = 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    if area < 0:
      pts = pts[::-1]
    disc = disc - CrossSection([pts])
  return disc.extrude(0.6).translate((0.0, 0.0, z))


def occluders(cam: PC.PhotoCam = None, openings=None) -> list:
  """The car where it can be in front of a part: the column covers, the grip, the key's bulge, the steering wheel's
  back cover; in the photo from your seat also the wheel's hub and spokes."""
  sc = CS.CarScene(D=128.2)
  out = [(sc.column_cover(back=130.0), COVER), (RC.grip(), RIM), (sc.key_parts()["key bulge and bezel"], COVER),
         (sc.back_cover(), COVER)]
  if openings:
    out.append((wheel_front(cam, openings), COVER))
  return out


def lights(cam: PC.PhotoCam, kind: str) -> dict:
  up = CP.WORLD_UP
  if kind == "flash":
    # the phone's flash beside the lens (its fall-off softened, as the phone's processing does); a little light from
    # the garage above
    return {"flash": dict(pos=cam.eye, power=1.0, d0=250.0, p=0.5, rgb=(1.0, 0.98, 0.95)),
            "sky": dict(up=up, sky=(0.16, 0.16, 0.17), ground=(0.05, 0.05, 0.05), power=1.0)}
  # daylight from in front, through the windscreen and the open garage door; the cabin's light round about
  fwd = np.array([0.0, math.sin(math.radians(22.0)), -math.cos(math.radians(22.0))])
  sun = 0.75 * fwd + 0.66 * np.asarray(up)
  return {"sun": dict(dir=sun, power=0.9, rgb=(1.0, 0.99, 0.97)),
          "sky": dict(up=up, sky=(0.55, 0.57, 0.60), ground=(0.22, 0.21, 0.20), power=1.0)}


def window(cam: PC.PhotoCam, ps: list, margin: int = 60) -> tuple:
  pts = np.concatenate([PR.mesh_of(m)[0] for m, _ in ps])
  u, v, z = cam.project(pts)
  ok = z > 1
  x0 = int(max(0, np.floor(u[ok].min()) - margin))
  x1 = int(min(cam.W, np.ceil(u[ok].max()) + margin))
  y0 = int(max(0, np.floor(v[ok].min()) - margin))
  y1 = int(min(cam.H, np.ceil(v[ok].max()) + margin))
  return x0, y0, x1 - x0, y1 - y0


DASH_F = np.array([0.0, math.sin(math.radians(22.0)), -math.cos(math.radians(22.0))])     # the car's forward
DASH_D = 164.0           # the grey panel under the column: the upright plane forward . X = 164 (about 200 mm behind the grip)


def brightness(cam: PC.PhotoCam, photo, kind: str, ref: dict):
  """The gain from the renderer's light to the photo's: a print-grey surface where the reference patch is, facing
  the way it faces, drawn with the photo's light, against the patch's median colour in the photo."""
  lin = PC.srgb_to_lin(photo.astype(float) / 255.0)
  vals = np.concatenate([lin[y0:y1, x0:x1].reshape(-1, 3) for x0, y0, x1, y1 in ref["boxes"]])
  target = np.median(vals, axis=0)
  u = np.mean([(b[0] + b[2]) / 2 for b in ref["boxes"]])
  v = np.mean([(b[1] + b[3]) / 2 for b in ref["boxes"]])
  if ref.get("dash"):
    d = cam.R.T @ np.array([(u - cam.c[0]) / cam.f, (v - cam.c[1]) / cam.f, 1.0])
    X = cam.eye + (DASH_D - DASH_F @ cam.eye) / (DASH_F @ d) * d
    n = -DASH_F
  else:
    X = backproject(cam, (u, v), ref["plane_z"])
    n = np.asarray(ref["normal"], float)
  grey = PR.Mat((float(np.mean(PRINT.albedo)),) * 3, spec=PRINT.spec, shine=PRINT.shine)
  vd = cam.eye - X
  vd /= np.linalg.norm(vd)
  if n @ vd < 0:
    n = -n
  model = PC.shade([grey], np.array([0]), X[None], n[None] / np.linalg.norm(n), vd[None], np.array([1.0]), lights(cam, kind))[0]
  return target / model, X, float(np.linalg.norm(X - cam.eye))


def make(name: str, ss: int = 2, out_dir: str = REPORT_DIR) -> str:
  spec = PHOTOS[name]
  cam = camera(spec["cam"])
  photo = np.asarray(Image.open(UPLOADS + spec["file"] + "-image.jpg").convert("RGB"))
  ps = parts(spec["wheel"])
  gain, X, dist = brightness(cam, photo, spec["light"], spec["ref"])
  print(f"photo {name}: gain {np.round(gain, 3)} (reference patch at {np.round(X, 0)}, {dist:.0f} mm from the lens)")
  box = window(cam, ps)
  print(f"   window {box}")
  occ = occluders(cam, OPENINGS_00 if name == "00" else None)
  L = PC.layers(cam, ps, occ, box, ss=ss, lights=lights(cam, spec["light"]))
  key = CS.CarScene(D=128.2).key
  focus = float(np.linalg.norm(key - cam.eye)) if spec["light"] == "flash" else 430.0
  res = PC.composite(photo, L, gain, focus=focus, aperture_mm=3.0, f_px=cam.f, noise=0.008)
  os.makedirs(out_dir, exist_ok=True)
  path = os.path.join(out_dir, f"in-the-car-photo-{name}.jpg")
  Image.fromarray(res).save(path, quality=92)
  return path


'''
s = s[:a] + new + s[b:]
open(p, 'w').write(s)
print('ok')
EOF
grep -n "def \|^PHOTOS\|^OPENINGS" incar.py