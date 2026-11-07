"""
What the right-arm build will look like in the car (2 Nov 2026): photo-style renders from the driver's seat, from
the footwell looking up (as in your photos) and from the passenger's side. The printed parts, the motor, the gear,
the teeth piece and the bolts are the CAD parts exactly, where they go; the car round them (the steering wheel's hub
and spokes, the column covers, the dash below them, the key) is drawn from your photos and the photo model, and is
approximate. The printed parts are shown in grey PETG; the motor's board is drawn as a generic board.

  python3 carphoto.py [width]     # writes ../report/in-the-car-1-drivers-seat.png, -2-from-below.png, -3-from-the-right.png

Not shipped: the car round the parts here is a rough model. incar.py draws the same parts into your own photos
instead (and takes its motor, zip ties and cable colour from here).
"""
import itertools
import math
import os
import sys

import numpy as np
from manifold3d import CrossSection, Manifold

import carscene as CS
import midteeth as MT
import photorender as PR
import rightarm as RA
import rightcheck as RC
import sideparts as S
from cadlib import box, cyl, union

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(HERE, "..", "report")

PETG = PR.Mat((0.11, 0.115, 0.125), spec=0.08, shine=60)          # grey PETG
STEEL = PR.Mat((0.45, 0.45, 0.47), spec=0.70, shine=110)
MOTOR_BLACK = PR.Mat((0.012, 0.012, 0.014), spec=0.10, shine=35)
ALU = PR.Mat((0.38, 0.38, 0.40), spec=0.45, shine=45)
PCB = PR.Mat((0.004, 0.05, 0.013), spec=0.12, shine=50, smooth=False)
CHIP = PR.Mat((0.008, 0.008, 0.008), spec=0.25, shine=60, smooth=False)
PLUG = PR.Mat((0.34, 0.31, 0.24), spec=0.10, shine=30, smooth=False)
RIM = PR.Mat((0.016, 0.016, 0.018), spec=0.03, shine=12, grain=0.35, grain_mm=0.9)
SPOKE = PR.Mat((0.24, 0.23, 0.21), spec=0.30, shine=40)
HUB = PR.Mat((0.014, 0.014, 0.016), spec=0.025, shine=10, grain=0.3, grain_mm=0.9)
COVER = PR.Mat((0.012, 0.012, 0.014), spec=0.025, shine=10, grain=0.3, grain_mm=0.7)
DASH = PR.Mat((0.22, 0.215, 0.20), spec=0.02, shine=10, smooth=False, grain=0.12, grain_mm=0.8)
NYLON = PR.Mat((0.01, 0.01, 0.01), spec=0.15, shine=40)
CABLE = PR.Mat((0.012, 0.012, 0.012), spec=0.12, shine=25)

WORLD_UP = (0.0, math.cos(math.radians(22.0)), math.sin(math.radians(22.0)))   # the column rises about 22 degrees


def to_wheel(m: Manifold, dz: float = 0.0) -> Manifold:
  """The motor's own frame (x along the column, y along V, z out along the shaft towards the gear) -> the steering
  wheel frame, as rightarm.motor_and_gear."""
  c = RA.R_FACE_OUT * RA.U
  return m.transform([[0.0, RA.V[0], -RA.U[0], float(c[0])], [0.0, RA.V[1], -RA.U[1], float(c[1])],
                      [1.0, 0.0, 0.0, RA.Z_AXIS + dz]])


def chamfered_square(half: float, c: float) -> CrossSection:
  pts = [(half - c, -half), (half, -half + c), (half, half - c), (half - c, half), (-half + c, half), (-half, half - c),
         (-half, -half + c), (-half + c, -half)]
  return CrossSection([pts])


def motor_parts(dz: float = 0.0) -> list:
  """A NEMA 17, 40 mm: aluminium end caps, the black stator between, the boss and the shaft; the four M3 screws'
  heads on the carrier's pads; the controller board on the back (a generic board: its parts are placeholders)."""
  H = RA.H
  sq = chamfered_square(H, 3.5)
  out = [(sq.extrude(8.0).translate((0.0, 0.0, -8.0)), ALU), (chamfered_square(H - 0.3, 3.5).extrude(24.0).translate((0.0, 0.0, -32.0)), MOTOR_BLACK),
         (sq.extrude(8.0).translate((0.0, 0.0, -40.0)), ALU), (cyl(11.0, 0.0, 2.0), ALU), (cyl(2.5, 2.0, 24.0, segments=32), STEEL)]
  face_to_pad = RA.R_FACE_OUT - (RA.PLATE_U[0] - RA.PAD_T)          # 6: the pads' face from the motor's face
  for bx in (-RA.NEMA_HOLES / 2, RA.NEMA_HOLES / 2):
    for by in (-RA.NEMA_HOLES / 2, RA.NEMA_HOLES / 2):
      out.append((cyl(2.85, face_to_pad, face_to_pad + 1.65, x=bx, y=by, segments=24), STEEL))      # button heads
      out.append((cyl(2.6, -40.6, -40.0, x=bx, y=by, segments=20), STEEL))                          # the back screws
      out.append((cyl(2.4, -46.0, -40.6, x=bx * 0.92, y=by * 0.92, segments=16), STEEL))            # standoffs
  out += [(box(-21.0, 21.0, -21.0, 21.0, -47.6, -46.0), PCB), (box(-4.0, 4.0, -4.0, 4.0, -48.8, -47.6), CHIP),
          (box(7.0, 12.0, -7.0, -2.0, -48.6, -47.6), CHIP), (box(7.0, 12.0, 2.0, 7.0, -48.6, -47.6), CHIP),
          (box(-17.0, -7.0, 11.0, 18.0, -54.0, -47.6), PLUG), (box(-17.0, -7.0, -18.0, -11.0, -54.0, -47.6), PLUG),
          (cyl(3.0, -55.0, -47.6, x=12.0, y=-14.0, segments=20), CHIP), (cyl(3.0, -55.0, -47.6, x=12.0, y=14.0, segments=20), CHIP)]
  return [(to_wheel(m, dz), mat) for m, mat in out]


def zip_ties() -> list:
  """Two ties side by side round the grip through the teeth piece's middle slot, heads tucked inside the rim."""
  rr, gr = S.FP.WHEEL_OD / 2.0 - S.FP.GRIP / 2.0, S.FP.GRIP / 2.0
  out = []
  for off in (-2.8, 2.8):
    ring = (Manifold.cylinder(4.6, gr + 1.6, gr + 1.6, 64) - Manifold.cylinder(4.8, gr + 0.25, gr + 0.25, 64).translate((0, 0, -0.1)))
    ring = ring.translate((0.0, 0.0, -2.3)).rotate((90.0, 0.0, 0.0)).translate((rr, off, 0.0))
    head = box(rr - gr - 6.5, rr - gr - 0.5, off - 3.5, off + 3.5, -6.0, 2.0)
    a = RA.THETA
    out.append(((ring + head).rotate((0.0, 0.0, a)), NYLON))
  return out


def wheel_parts() -> list:
  """The steering wheel straight: the grip, the hub, three spokes (from your photos: the right one with the cruise
  buttons at about 3 o'clock, the bottom one at 6), the cover on its back."""
  sc = CS.CarScene(D=125.0)
  out = [(RC.grip(), RIM), (sc.back_cover(), HUB)]
  hub = CrossSection.square((160.0, 110.0), center=True).offset(25.0, circular_segments=48).extrude(70.0).translate((0.0, 12.0, -45.0))
  out.append((hub, HUB))
  side = CrossSection.square((70.0, 40.0), center=True).offset(6.0, circular_segments=24).extrude(34.0)
  right = side.translate((128.0, 0.0, -28.0)).rotate((0.0, 0.0, 14.0))
  left = side.translate((128.0, 0.0, -28.0)).rotate((0.0, 0.0, 166.0))
  out += [(right, SPOKE), (left, SPOKE)]
  for i, (bx, by, bw) in enumerate(((108.0, 9.0, 26.0), (106.0, -6.0, 12.0), (121.0, -6.0, 12.0))):
    out.append((box(bx - bw / 2, bx + bw / 2, by - 5.0, by + 5.0, 5.5, 8.5).rotate((0.0, 0.0, 14.0)), CHIP))
  bottom = CrossSection.square((36.0, 90.0), center=True).offset(5.0, circular_segments=24).extrude(30.0).translate((0.0, -118.0, -27.0))
  out.append((bottom, HUB))
  return out


def car_parts() -> list:
  sc = CS.CarScene(D=125.0)
  big = box(-900.0, 900.0, -1400.0, 400.0, sc.dash_z - 40.0, sc.dash_z)
  hole = box(-1e3, 1e3, -1e3, 1e3, sc.dash_z - 41.0, sc.dash_z + 1.0) - sc.bolster().translate((0.0, 0.0, 0.0))
  wall = big - (hole ^ box(-300.0, 300.0, -400.0, 120.0, sc.dash_z - 41.0, sc.dash_z + 1.0))
  return [(sc.column_cover(back=130.0), COVER), (wall, DASH), (sc.key_parts()["key bulge and bezel"], COVER),
          (sc.stalk(down=0.0, up=0.0), COVER)]


def cable() -> list:
  """The board's power and data cable: out of its plug, down beside the tower and off under the column towards the
  lever nuts (its path is a guess)."""
  start = np.array([-12.0, 14.5, -54.0])           # the plug, in the motor's frame
  c = RA.R_FACE_OUT * RA.U
  p0 = np.array([start[1] * RA.V[0] - start[2] * RA.U[0] + c[0], start[1] * RA.V[1] - start[2] * RA.U[1] + c[1],
                 start[0] + RA.Z_AXIS])
  pts = [p0, p0 + 14.0 * np.array([RA.U[0], RA.U[1], 0.0]), p0 + np.array([18.0, -40.0, -20.0]),
         np.array([215.0, -175.0, -120.0]), np.array([180.0, -205.0, -175.0]), np.array([90.0, -215.0, -230.0])]
  import columnassembly as CA
  segs = [CA.rod(a, b, 2.6) for a, b in itertools.pairwise(pts)]
  joints = [Manifold.sphere(2.6, 24).translate(tuple(float(v) for v in q)) for q in pts[1:-1]]
  return [(union(segs + joints), CABLE)]


def build_parts() -> list:
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=18)).rotate((0.0, 0.0, RA.THETA))
  out = [(RA.plate_to_wheel(RA.frame_plate_v5()), PETG), (RA.arm(), PETG), (RA.carrier(0.0), PETG),
         (RA.motor_and_gear(0.0)["gear"], PETG), (teeth, PETG)]
  out += [(m, STEEL) for m in RC.hardware(0.0).values()]
  return out + motor_parts(0.0) + zip_ties() + cable()


def scene() -> list:
  return wheel_parts() + car_parts() + build_parts()


VIEWS = {
  "1-drivers-seat": {"eye": (-10.0, 75.0, 630.0), "target": (125.0, -105.0, -45.0), "up": WORLD_UP, "fov": 30.0},
  "2-from-below": {"eye": (165.0, -430.0, 70.0), "target": (150.0, -115.0, -110.0), "up": (0.0, 0.0, 1.0), "fov": 46.0},
  "3-from-the-right": {"eye": (560.0, -210.0, 170.0), "target": (165.0, -115.0, -95.0), "up": WORLD_UP, "fov": 40.0},
}
KEY = (-0.45, 0.75, 0.48)        # daylight through the driver's window: from above, the left and behind


def main(argv):
  width = int(argv[1]) if len(argv) > 1 else 1600
  size = (width, width * 3 // 4)
  sc = scene()
  os.makedirs(REPORT_DIR, exist_ok=True)
  for name, v in VIEWS.items():
    cam = PR.Camera(v["eye"], v["target"], v["up"], v["fov"], size)
    fill = np.asarray(v["eye"]) - np.asarray(v["target"])      # a soft light from where the picture is taken
    img = PR.render(sc, cam, KEY, key_power=2.0, sky_up=WORLD_UP, ambient=0.9, fill_dir=fill, fill_power=0.5, ss=2, exposure=0.95)
    path = os.path.join(REPORT_DIR, f"in-the-car-{name}.png")
    PR.save_png(path, img)
    print(path)


if __name__ == "__main__":
  sys.exit(main(sys.argv))
