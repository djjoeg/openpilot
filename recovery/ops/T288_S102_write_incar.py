"""
What the right-arm build will look like in your car (2 Nov 2026): your own photos with the parts drawn in.

  photo 00  from your seat, daylight (9 Oct)
  photo 33  low on the right of the column, beside the key, with the flash (10 Oct)
  photo 26  the same spot, a little higher and nearer (10 Oct)

The parts are the CAD parts exactly, where the CAD puts them: the frame plate v4 on the column cover's screws, the arm
v3 and its tower, the motor carrier with the motor (slid up to its stop, the gear in the teeth), the gear, the teeth
v2 (the 20 set) zip-tied on the grip, the wing bolts and nuts. Not exact: the motor's board (a generic board), the
cable (its path is a guess), the colour (the grey you have been printing in, from your photos of the prints).

The cameras, from the photos themselves:
  - 26 and 33: from the earlier fit of the four key photos (24, 26, 33, 37) together: the key's black bezel (38 mm
    across, your tape), the instrument cluster's numbers and the grip (372 mm across, 35.4 mm thick); the photos' own
    tilt taken out with photo 36's cluster. Of the two fits that were equally good then, the one that puts the key
    128 mm behind the grip's back, as your tape later showed (the screw cup about 5 in from the back of the wheel).
    Checked again here: the key's bezel drawn with these cameras lands on the bezel in the photos.
  - 00: the grip's outline (fitted to 0.2 px), the phone's zoom taken as the iPhone's usual (1917 px for these
    pictures; the outline alone can't tell it, and a 7% error moves the motor about 1 px). Which way is level comes
    from the cluster's dials (0 and 8 on the rev counter, 0 and 160 on the speedometer, level within 1.5 degrees).
    The steering wheel was turned about 17 degrees to the right in that photo (the spoke buttons say 20, the badge
    13-14), so the teeth piece, which turns with the wheel, is drawn turned 17 degrees; the motor and its mount stay
    with the column. With the wheel straight the teeth would sit centred on the gear.

  python3 incar.py [photo ...]      # writes ../report/in-the-car-photo-00.jpg, -33.jpg, -26.jpg (+ a side-by-side)
"""
import math
import os
import sys

import numpy as np
from PIL import Image

import carphoto as CP
import carscene as CS
import midteeth as MT
import photocomp as PC
import photorender as PR
import rightarm as RA
import rightcheck as RC

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(HERE, "..", "report")
UPLOADS = "/root/.claude/uploads/29de5e81-e3b9-5428-a15c-fac1d206c0d4/"

PRINT = PR.Mat((0.25, 0.26, 0.28), spec=0.07, shine=45, grain=0.05, grain_mm=0.45)      # your grey prints
ZINC = PR.Mat((0.52, 0.53, 0.55), spec=0.65, shine=90)                                   # the wing bolts and nuts
COVER = PR.Mat((0.035, 0.035, 0.037), spec=0.04, shine=12)                               # the black column cover
RIM = PR.Mat((0.04, 0.04, 0.042), spec=0.05, shine=14)                                   # the grip

# ----- the cameras (car frame -> camera: pixel = f (R X + t)[:2] / (R X + t)[2] + c) -----
KEY_CAMS = {   # fit B of the key photos (the stage 2 fit, 10 Oct), the photo's tilt taken out
  26: dict(R=[[0.717538, 0.103686, -0.688759], [-0.029105, -0.983531, -0.178382], [-0.695911, 0.148042, -0.702703]],
           t=[-153.06, -53.182, 187.798], f=1903.9),
  33: dict(R=[[0.572851, 0.051614, -0.818033], [-0.093312, -0.987421, -0.127646], [-0.81433, 0.149454, -0.560829]],
           t=[-136.858, -63.322, 256.255], f=1985.5),
  37: dict(R=[[0.674195, 0.167254, -0.719366], [0.07334, -0.984367, -0.160133], [-0.734903, 0.055202, -0.675922]],
           t=[-131.09, -98.243, 212.71], f=2009.6),
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


PHOTOS = {
  "00": dict(file="273a348a", cam=cam00, wheel=-17.0, light="day"),
  "33": dict(file="818fd797", cam=33, wheel=0.0, light="flash"),
  "26": dict(file="a5f478e3", cam=26, wheel=0.0, light="flash"),
}


def camera(spec) -> PC.PhotoCam:
  if callable(spec):
    return spec()
  k = KEY_CAMS[spec]
  return PC.PhotoCam(k["R"], k["t"], k["f"], (966.0, 1288.0), (1932, 2576))


# ----- what is drawn -----

def parts(wheel_deg: float) -> list:
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=18)).rotate((0.0, 0.0, RA.THETA + wheel_deg))
  out = [(RA.plate_to_wheel(RA.frame_plate_v4()), PRINT), (RA.arm(), PRINT), (RA.carrier(0.0), PRINT),
         (RA.motor_and_gear(0.0)["gear"], PRINT), (teeth, PRINT)]
  out += [(m, ZINC) for m in RC.hardware(0.0, RA.STOP_P).values()]
  out += CP.motor_parts(0.0)
  out += [(m.rotate((0.0, 0.0, wheel_deg)), mat) for m, mat in CP.zip_ties()]
  out += CP.cable()
  return out


def occluders() -> list:
  """The car where it can be in front of a part: the grip, the column covers, the key's bulge, the steering wheel's
  back cover (index 0 the cover, 1 the grip: the brightness references)."""
  sc = CS.CarScene(D=128.2)
  return [(sc.column_cover(back=130.0), COVER), (RC.grip(), RIM), (sc.key_parts()["key bulge and bezel"], COVER),
          (sc.back_cover(), COVER)]


def lights(cam: PC.PhotoCam, kind: str) -> dict:
  up = CP.WORLD_UP
  if kind == "flash":
    # the phone's flash beside the lens; a little light from the garage above
    return {"flash": dict(pos=cam.eye, power=1.0, d0=250.0, p=1.0, rgb=(1.0, 0.98, 0.95)),
            "sky": dict(up=up, sky=(0.20, 0.20, 0.21), ground=(0.06, 0.06, 0.06), power=1.0)}
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


def brightness(cam, photo, kind, ref):
  """The gain from the renderer's linear light to the photo's: the reference (0 the column cover, 1 the grip)
  drawn with the same light and compared with the photo, pixel by pixel, over the middle of it."""
  lin = PC.srgb_to_lin(photo.astype(float) / 255.0)
  box = (0, 0, cam.W, cam.H)
  L = PC.layers(cam, [], occluders(), box, ss=1, lights=lights(cam, kind), calib=[ref])
  import cv2
  m = (L["Km"] > 0.99).astype(np.uint8)
  m = cv2.erode(m, np.ones((25, 25), np.uint8)) > 0       # away from its edges (the model's edges are rough)
  K = L["K"][m]
  P = lin[m]
  lum = K.mean(axis=1)
  keep = lum > np.percentile(lum, 10)
  g = np.median(P[keep], axis=0) / np.median(K[keep], axis=0)
  return g, int(m.sum())


def make(name: str, ss: int = 2, out_dir: str = REPORT_DIR) -> str:
  spec = PHOTOS[name]
  cam = camera(spec["cam"])
  photo = np.asarray(Image.open(UPLOADS + spec["file"] + "-image.jpg").convert("RGB"))
  ps = parts(spec["wheel"])
  ref = 1 if spec["light"] == "day" else 0
  gain, npx = brightness(cam, photo, spec["light"], ref)
  print(f"photo {name}: gain {np.round(gain, 3)} from {npx} pixels of the {'grip' if ref else 'column cover'}")
  box = window(cam, ps)
  print(f"   window {box}")
  L = PC.layers(cam, ps, occluders(), box, ss=ss, lights=lights(cam, spec["light"]))
  key = CS.CarScene(D=128.2).key
  focus = float(np.linalg.norm(key - cam.eye)) if spec["light"] == "flash" else 430.0
  res = PC.composite(photo, L, gain, focus=focus, aperture_mm=3.0, f_px=cam.f, noise=0.008)
  os.makedirs(out_dir, exist_ok=True)
  path = os.path.join(out_dir, f"in-the-car-photo-{name}.jpg")
  Image.fromarray(res).save(path, quality=92)
  return path


def main(argv):
  names = argv[1:] or list(PHOTOS)
  for n in names:
    print(make(n))


if __name__ == "__main__":
  sys.exit(main(sys.argv))
