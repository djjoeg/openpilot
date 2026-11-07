"""
What the right-arm build will look like in your car (2 Nov 2026): your own photos with the parts drawn in.

  photo 00  from your seat, daylight (9 Oct): what you will see when you drive
  photo 33  low on the right of the column, beside the key, with the flash (10 Oct): the mount from beside your
            right knee. (Photo 26 works too, but it was taken nearer still: the motor fills it.)

The parts are the CAD parts exactly, where the CAD puts them: the frame plate v5 on the column cover's screws, the arm
v6 and its tower, the motor carrier with the motor (slid up the groove, the gear in the teeth), the gear, the teeth
v2 (the 20 set) zip-tied on the grip, the wing bolts and nuts, the motor's four screws. Not exact: the motor's board
(a generic board), the cable (its path is a guess: tidied along the arm), the colour (the grey you have been printing
in, from your photos of the prints), the light (matched to a grey patch in the same photo: the silver spoke by day,
the grey panel under the column at night).

The cameras, from the photos themselves:
  - 33 (and 26): from the earlier fit of the four key photos (24, 26, 33, 37) together: the key's black bezel (38 mm
    across, your tape), the instrument cluster's numbers and the grip (372 mm across, 35.4 mm thick); the photos' own
    tilt taken out with photo 36's cluster. Of the two fits that were equally good then, the one your tape agrees
    with: it puts the screw cup 123 mm in front of the back of the grip, your tape said 5 in (127); the other said 82.
    Checked again here: the key's bezel, the stalk and the screw cup drawn with this camera land on them in the photo.
  - 00: the grip's outline (fitted to 0.3 px), the phone's zoom taken as the iPhone's usual (1917 px for these
    pictures; the outline alone can't tell it, and a 7% error moves the motor about 1 px). Of the outline's two mirror
    fits, the one whose inner edge matches the grip's inner edge and that looks down at the wheel (the photo shows the
    ground outside). Which way is level comes from the cluster's dials (0 and 8 on the rev counter, 0 and 160 on the
    speedometer: level within 1.5 degrees). The steering wheel was turned about 17 degrees to the right in that photo
    (the spoke buttons say 20, the badge 13-14), so the teeth piece and its zip ties, which turn with the wheel, are
    drawn turned 17 degrees; the motor and its mount stay with the column. With the wheel straight the teeth sit
    centred on the gear. The hub, spokes and buttons hide what is behind them: their outline round the two openings
    you can see through was traced by hand on the photo.

  python3 incar.py [photo ...]      # default 00 and 33: writes ../report/in-the-car-photo-00.jpg (+ -before-after.jpg)
                                    # and in-the-car-photo-33.jpg (+ -before-after.jpg)
"""
import itertools
import math
import os
import sys

import numpy as np
from manifold3d import CrossSection, Manifold
from PIL import Image

import carphoto as CP
import carscene as CS
import columnassembly as CA
import midteeth as MT
import photocomp as PC
import photorender as PR
import rightarm as RA
import rightcheck as RC
from cadlib import union

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(HERE, "..", "report")
UPLOADS = "/root/.claude/uploads/29de5e81-e3b9-5428-a15c-fac1d206c0d4/"

PRINT = PR.Mat((0.25, 0.26, 0.28), spec=0.07, shine=45, grain=0.05, grain_mm=0.45)      # your grey prints
ZINC = PR.Mat((0.52, 0.53, 0.55), spec=0.65, shine=90)                                   # the wing bolts and nuts
COVER = PR.Mat((0.035, 0.035, 0.037), spec=0.04, shine=12)                               # the black column cover
RIM = PR.Mat((0.04, 0.04, 0.042), spec=0.05, shine=14)                                   # the grip

# ----- the cameras (car frame -> camera: pixel = f (R X + t)[:2] / (R X + t)[2] + c) -----
KEY_CAMS = {   # fit B of the key photos (the stage 2 fit, 10 Oct), the photo's tilt taken out
  26: {"R": [[0.717538, 0.103686, -0.688759], [-0.029105, -0.983531, -0.178382], [-0.695911, 0.148042, -0.702703]],
           "t": [-153.06, -53.182, 187.798], "f": 1903.9},
  33: {"R": [[0.572851, 0.051614, -0.818033], [-0.093312, -0.987421, -0.127646], [-0.81433, 0.149454, -0.560829]],
           "t": [-136.858, -63.322, 256.255], "f": 1985.5},
  37: {"R": [[0.674195, 0.167254, -0.719366], [0.07334, -0.984367, -0.160133], [-0.734903, 0.055202, -0.675922]],
           "t": [-131.09, -98.243, 212.71], "f": 2009.6},
}


def cam00():
  """Photo 00: the grip's centre and axis in the camera (the ring fit), level from the cluster (its dials' row,
  y = 860 px, runs level in the car)."""
  f, c = 1917.0, np.array([966.0, 1288.0])
  C = np.array([-0.1, 42.7, 429.1])
  a = np.array([-0.079, -0.284, 0.956])
  a /= np.linalg.norm(a)                     # the column's axis, away from you
  zc = -a
  n = np.array([0.0, -f, 860.0 - c[1]])      # the plane through the lens and the cluster's row of pixels
  xc = np.cross(a, n)
  xc /= np.linalg.norm(xc)
  if xc[0] < 0:
    xc = -xc
  yc = np.cross(zc, xc)
  return PC.PhotoCam(np.column_stack([xc, yc, zc]), C, f, c, (1932, 2576))


# per photo: the photo, its camera, how far the steering wheel was turned (the teeth turn with it), the light, and a
# light-grey patch of the photo the prints are matched to (box in pixels, where it is in the car, which way it faces):
# the silver spoke by day (your prints look as light as it in your photo of the test teeth on the wheel), the grey
# panel under the column at night
PHOTOS = {
  "00": {"file": "273a348a", "cam": cam00, "wheel": -17.0, "light": "day", "ss": 2, "pair": (640, 1180, 1932, 2380),
             "ref": {"boxes": [(1225, 1795, 1250, 1815), (1170, 1845, 1195, 1865), (1120, 1895, 1145, 1915)], "plane_z": 30.0,
                      "normal": (0.0, 0.0, 1.0)}},
  "33": {"file": "818fd797", "cam": 33, "wheel": 0.0, "light": "flash", "ss": 1, "pair": (0, 0, 1932, 2576),
             "ref": {"boxes": [(1000, 1790, 1500, 1880)], "dash": True}},
  "26": {"file": "a5f478e3", "cam": 26, "wheel": 0.0, "light": "flash", "ss": 1,
             "ref": {"boxes": [(700, 1880, 1100, 1960)], "dash": True}},
}

# where you can see through the steering wheel in photo 00 (between the right lower spoke, the cruise buttons, the
# hub and the grip; between the two lower spokes): everything else inside the grip is the wheel itself, in front of
# the parts. The outlines run into the grip, which hides what is behind it on its own.
OPENINGS_00 = [
  [(1350, 1690), (1400, 1684), (1460, 1700), (1520, 1712), (1720, 1712), (1720, 2320), (950, 2320), (1000, 2030),
   (1080, 1985), (1170, 1900), (1265, 1800)],
  [(580, 1748), (800, 1752), (1000, 1772), (1100, 1790), (1165, 1800), (1080, 1900), (975, 2005), (960, 2320),
   (580, 2320)],
]


def camera(spec) -> PC.PhotoCam:
  if callable(spec):
    return spec()
  k = KEY_CAMS[spec]
  return PC.PhotoCam(k["R"], k["t"], k["f"], (966.0, 1288.0), (1932, 2576))


# ----- what is drawn -----

def parts(wheel_deg: float) -> list:
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=18)).rotate((0.0, 0.0, RA.THETA + wheel_deg))
  out = [(RA.plate_to_wheel(RA.frame_plate_v5()), PRINT), (RA.arm(), PRINT), (RA.carrier(0.0), PRINT),
         (RA.motor_and_gear(0.0)["gear"], PRINT), (teeth, PRINT)]
  out += [(m, ZINC) for m in RC.hardware(0.0).values()]
  out += motor_parts()
  out += [(m.rotate((0.0, 0.0, wheel_deg)), mat) for m, mat in CP.zip_ties()]
  out += cable()
  return out


MOTOR = PR.Mat((0.018, 0.018, 0.020), spec=0.12, shine=40)                     # the motor: black caps, black body
STAINLESS = PR.Mat((0.50, 0.50, 0.52), spec=0.6, shine=80)


def motor_parts() -> list:
  """The NEMA 17 (17HS15-1504S-X1, as in its listing: black end caps and body, the front face bare aluminium against
  the carrier), the four stainless M3 button heads on the carrier's pads, and the board on its back (a generic
  board: its parts are placeholders)."""
  out = []
  for m, mat in CP.motor_parts(0.0):
    if mat is CP.ALU or mat is CP.MOTOR_BLACK:
      out.append((m, MOTOR))
    elif mat is CP.STEEL:
      out.append((m, STAINLESS))
    else:
      out.append((m, mat))
  return out


def cable() -> list:
  """The board's cable (power and CAN), tidied along the mount: out of its plug, down the motor carrier's outer side to
  the foot of the tower, along under the arm to the column and away under it (the path is a guess; it is how it
  would be tidied)."""
  c = RA.R_FACE_OUT * RA.U
  start = np.array([-12.0, 14.5, -54.0])           # the plug, in the motor's frame
  p0 = np.array([start[1] * RA.V[0] - start[2] * RA.U[0] + c[0], start[1] * RA.V[1] - start[2] * RA.U[1] + c[1],
                 start[0] + RA.Z_AXIS])
  out = np.array([RA.U[0], RA.U[1], 0.0])
  def uv(u, v, z):
    x, y = RA.rad(u, v)
    return np.array([x, y, z])
  pts = [p0, p0 + 9.0 * out, uv(240.0, -36.0, -84.0), uv(238.0, -51.0, -100.0), uv(236.0, -51.0, -170.0), uv(222.0, -52.0, -179.0),
         np.array([150.0, -148.0, -180.0]), np.array([125.0, -156.0, -182.0]), np.array([60.0, -157.0, -192.0]),
         np.array([10.0, -160.0, -215.0]), np.array([-50.0, -170.0, -250.0])]
  segs = [CA.rod(a, b, 2.4) for a, b in itertools.pairwise(pts)]
  joints = [Manifold.sphere(2.4, 24).translate(tuple(float(v) for v in q)) for q in pts[1:-1]]
  return [(union(segs + joints), CP.CABLE)]


def backproject(cam: PC.PhotoCam, uv, z: float) -> np.ndarray:
  """The point on the plane z (steering wheel frame) that the photo's pixel uv shows."""
  d = cam.R.T @ np.array([(uv[0] - cam.c[0]) / cam.f, (uv[1] - cam.c[1]) / cam.f, 1.0])
  e = cam.eye
  return e + (z - e[2]) / d[2] * d


def wheel_front(cam: PC.PhotoCam, openings, r: float = 152.0, z: float = 15.0):
  """The steering wheel's hub, spokes and buttons as a thin sheet just in front of the grip: a disc inside the grip
  less the openings you can see through (outlined on the photo, carried onto the sheet's plane)."""
  disc = CrossSection.circle(r, 180)
  for poly in openings:
    pts = [tuple(backproject(cam, uv, z)[:2]) for uv in poly]
    area = 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    if area < 0:
      pts = pts[::-1]
    disc = disc - CrossSection([pts])
  return disc.extrude(0.6).translate((0.0, 0.0, z))


def occluders(cam: PC.PhotoCam | None = None, openings=None) -> list:
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
    return {"flash": {"pos": cam.eye, "power": 1.0, "d0": 250.0, "p": 0.5, "rgb": (1.0, 0.98, 0.95)},
            "sky": {"up": up, "sky": (0.16, 0.16, 0.17), "ground": (0.05, 0.05, 0.05), "power": 1.0}}
  # daylight: the windscreen's light does not reach under the dash, so the parts get the cabin's light, from behind
  # and above (the side and back windows, the seats); behind the wheel's hub and spokes less of it
  fwd = np.array([0.0, math.sin(math.radians(22.0)), -math.cos(math.radians(22.0))])
  back = -fwd + 0.6 * np.asarray(up)
  return {"sky": {"up": back / np.linalg.norm(back), "sky": (0.60, 0.61, 0.63), "ground": (0.40, 0.40, 0.40), "power": 1.0},
          "wheel_shade": {"k": 0.55, "r0": 150.0, "r1": 215.0, "z": -12.0}}


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
  g = target / model
  if not ref.get("dash"):
    g = np.full(3, float(np.mean(g)))     # the silver spoke is warm (champagne): its brightness only
  return g, X, float(np.linalg.norm(X - cam.eye))


def make(name: str, ss: int | None = None, out_dir: str = REPORT_DIR) -> str:
  spec = PHOTOS[name]
  ss = ss or spec.get("ss", 2)
  cam = camera(spec["cam"])
  photo = np.asarray(Image.open(UPLOADS + spec["file"] + "-image.jpg").convert("RGB"))
  ps = parts(spec["wheel"])
  gain, X, dist = brightness(cam, photo, spec["light"], spec["ref"])
  print(f"photo {name}: gain {np.round(gain, 3)} (reference patch at {np.round(X, 0)}, {dist:.0f} mm from the lens)")
  box = window(cam, ps)
  print(f"   window {box}, {ss} x {ss} samples a pixel")
  occ = occluders(cam, OPENINGS_00 if name == "00" else None)
  L = PC.layers(cam, ps, occ, box, ss=ss, lights=lights(cam, spec["light"]))
  key = CS.CarScene(D=128.2).key
  focus = float(np.linalg.norm(key - cam.eye)) if spec["light"] == "flash" else 430.0     # on the key / on the wheel
  res = PC.composite(photo, L, gain, focus=focus, aperture_mm=3.0, f_px=cam.f, noise=0.008)
  os.makedirs(out_dir, exist_ok=True)
  path = os.path.join(out_dir, f"in-the-car-photo-{name}.jpg")
  Image.fromarray(res).save(path, quality=92)
  if spec.get("pair"):
    pair(photo, res, spec["pair"], os.path.join(out_dir, f"in-the-car-photo-{name}-before-after.jpg"))
  return path


def pair(before, after, box, path, width=2400):
  """Your photo and the same with the parts, side by side, cropped to box = (x0, y0, x1, y1)."""
  from PIL import ImageDraw, ImageFont
  x0, y0, x1, y1 = box
  a = Image.fromarray(before[y0:y1, x0:x1])
  b = Image.fromarray(after[y0:y1, x0:x1])
  w = (width - 30) // 2
  h = round(a.height * w / a.width)
  a, b = a.resize((w, h), Image.LANCZOS), b.resize((w, h), Image.LANCZOS)
  out = Image.new("RGB", (width, h + 70), (24, 24, 26))
  out.paste(a, (10, 60))
  out.paste(b, (20 + w, 60))
  d = ImageDraw.Draw(out)
  try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
  except OSError:
    font = ImageFont.load_default()
  d.text((14, 14), "your photo", fill=(235, 235, 235), font=font)
  d.text((24 + w, 14), "with the parts drawn in", fill=(235, 235, 235), font=font)
  out.save(path, quality=92)


def main(argv):
  names = argv[1:] or ["00", "33"]
  for n in names:
    print(make(n))


if __name__ == "__main__":
  sys.exit(main(sys.argv))
