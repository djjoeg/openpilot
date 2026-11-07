"""
Review pictures of everything to print for the right-arm build (2 Nov 2026): the apparatus close up with its wing
bolts and nuts drawn in, then each printed piece on its own, big, two views, with its size and what it does.

  python3 visuals.py      # writes ../report/review-*.png
"""
import math
import os
import sys

import numpy as np
from manifold3d import Manifold

import midteeth as MT
import render as R
import rightarm as RA
import sideparts as S
from cadlib import box, clean, cyl, cyl_y, hex_prism_z, revolve, union

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(HERE, "..", "report")

STEEL = (0.78, 0.78, 0.80)
PLATE = (0.80, 0.82, 0.85)
BLUE = (0.35, 0.55, 0.85)
DARK = (0.25, 0.25, 0.28)
ORANGE = (0.95, 0.65, 0.3)
CAR = (0.55, 0.55, 0.58)


def wing_bolt_z(x: float, y: float, z_head: float, length: float = 20.0, down: bool = True) -> Manifold:
  """An M5 x 20 wing bolt along z: the head's underside at z_head, the shank going -z (down=True) or +z."""
  s = -1.0 if down else 1.0
  shank = cyl(2.5, 0.0, length, segments=24)
  head = cyl(5.0, -3.0, 0.0, segments=32) + box(-9.0, 9.0, -1.2, 1.2, -9.0, -2.0) + box(-6.0, 6.0, -1.2, 1.2, -3.0, 0.0)
  m = shank + head
  if down:
    m = m.rotate((180.0, 0.0, 0.0))
  return m.translate((x, y, z_head))


def nut_z(x: float, y: float, z0: float) -> Manifold:
  return hex_prism_z(8.0, z0, z0 + 4.0, x=x, y=y) - cyl(2.5, z0 - 1.0, z0 + 5.0, x=x, y=y, segments=24)


def hardware() -> list:
  """The five wing bolts and five nuts, in the steering wheel frame."""
  parts = []
  # the receiver's pinch bolt: in the plate frame it runs along -y through the dash-side wall at PINCH_X
  pz = RA.PLATE_T + RA.BORE_DEPTH / 2
  head_y = RA.TUBE_Y[1]
  bolt = wing_bolt_z(0.0, 0.0, 0.0, length=12.0)                       # along -z from the head's underside
  bolt = bolt.rotate((-90.0, 0.0, 0.0))                                 # -z -> -y
  bolt = bolt.translate((RA.PINCH_X, head_y, pz))
  yn = (RA.BORE_Y[1] + RA.TUBE_Y[1]) / 2
  nut = hex_prism_z(8.0, -2.0, 2.0, x=0.0, y=0.0).rotate((90.0, 0.0, 0.0)).translate((RA.PINCH_X, yn, pz))
  nut = nut - cyl_y(2.5, yn - 3.0, yn + 3.0, x=RA.PINCH_X, z=pz, segments=24)
  parts += [(RA.plate_to_wheel(bolt), STEEL), (RA.plate_to_wheel(nut), STEEL)]
  # the foot's two bolts: heads on the foot's face towards you, nuts in the arm's dash face
  for x in RA.ARM_HOLES_X:
    parts.append((wing_bolt_z(x, RA.ARM_HOLES_Y, RA.FOOT_Z[1]), STEEL))
    parts.append((nut_z(x, RA.ARM_HOLES_Y, RA.ARM_Z[0] - 0.5), STEEL))
  # the tab's two bolts: heads on the tab, nuts in the flag's dash face
  for x, y in (RA.PIVOT, (RA.PIVOT[0] - RA.ARC_R, RA.PIVOT[1])):
    parts.append((wing_bolt_z(x, y, RA.TAB_Z[1]), STEEL))
    parts.append((nut_z(x, y, RA.FLAG_Z[0] - 0.5), STEEL))
  return parts


def grip_segment(span: float = 45.0) -> Manifold:
  grip_r = S.FP.GRIP / 2.0
  rr = S.FP.WHEEL_OD / 2.0 - grip_r
  circle = [(rr + grip_r * math.cos(math.radians(a)), grip_r * math.sin(math.radians(a))) for a in range(0, 360, 10)]
  return revolve(circle, RA.THETA - span, RA.THETA + span, step_deg=2.0)


def assembly_parts(with_grip: bool = True) -> list:
  mg = RA.motor_and_gear()
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=10)).rotate((0.0, 0.0, RA.THETA))
  parts = [(RA.plate_to_wheel(RA.frame_plate_v4()), PLATE), (RA.arm(), BLUE), (RA.bar(), BLUE), (RA.bracket(), BLUE),
           (mg["motor"], DARK), (mg["board"], DARK), (mg["gear"], ORANGE), (teeth, ORANGE)] + hardware()
  if with_grip:
    parts.append((grip_segment(), CAR))
  return parts


def size_text(m: Manifold) -> str:
  bb = m.bounding_box()
  return " x ".join(f"{bb[i + 3] - bb[i]:.0f}" for i in range(3)) + " mm"


def assembly_picture(path: str) -> None:
  parts = assembly_parts()
  views = [(parts, R.look((0.0, 0.0, 1.0), (0, 1, 0))), (parts, R.look((0.0, -1.0, 0.0), (0, 0, 1))),
           (parts, R.look((0.9, -0.5, 0.8), (0, 1, 0))), (parts, R.look((1.0, -0.15, 0.1), (0, 1, 0)))]
  R.save(path, views, cols=2, size=(1100, 800),
         titles=["from your seat: the motor outside the rim at 4 o'clock, shaft pointing at the wheel's middle",
                 "from below, the wheel at the top (as in your photos)",
                 "from your right and below", "from the passenger's side (the right)"],
         suptitle="The right arm mount, assembled, with its five wing bolts and nuts. Plate light grey (on the column cover, "
                  "not drawn), apparatus blue, motor and board dark, gear and teeth orange, a piece of the wheel grip grey.")


def part_sheet(path: str, m: Manifold, color, title: str, note: str, views=None) -> None:
  views = views or [R.view_matrix(-50, 35), R.view_matrix(130, 25)]
  panels = [([(m, color)], v) for v in views]
  R.save(path, panels, cols=2, size=(1000, 750), titles=["from the front left, above", "from the back right, above"],
         suptitle=f"{title}: {size_text(m)}. {note}")


def teeth_sheet(path: str) -> None:
  t = MT.MidTeeth(n_teeth=10)
  m = MT.mid_teeth(t)
  bed = MT.on_bed(m)
  back = bed.rotate((180.0, 0.0, 0.0))
  panels = [([(bed, ORANGE)], R.view_matrix(-60, 40)), ([(back, ORANGE)], R.view_matrix(-60, 40)),
            ([(bed, ORANGE)], R.look((0.0, 0.0, 1.0), (0, 1, 0))), ([(back, ORANGE)], R.look((0.0, 0.0, 1.0), (0, 1, 0)))]
  R.save(path, panels, cols=2, size=(1000, 650),
         titles=["as printed: the teeth up, the wheel side down", "turned over: the channel that goes on the grip",
                 "as printed, from above", "turned over, from above"],
         suptitle=f"Teeth v2, 11 (straight roads), plate 7: {size_text(bed)}, about {round(2 * t.half / 360 * 2 * math.pi * t.w_out):.0f} mm "
                  "along the grip. The channel 8 mm narrower than the first print; the inner wall only in the middle "
                  "(23 mm each side of centre), one 12 mm zip tie slot through it; the ends are the bare back and the outer wall.")


def main():
  os.makedirs(REPORT_DIR, exist_ok=True)
  bed = RA.parts_on_bed()
  assembly_picture(os.path.join(REPORT_DIR, "review-1-assembly.png"))
  part_sheet(os.path.join(REPORT_DIR, "review-2-frame-plate.png"), bed["column-frame-plate-v4"], PLATE,
             "Plate 11, frame plate v4", "6 mm thick. Hangs on the two cover screws (the cup slot and slot 1). The square tube is "
             "the receiver: the arm slides in from the key side, one wing bolt through the tube's far wall pinches it; the nut drops "
             "into the slot in that wall. Printed labels up; in the car the labels face down.")
  part_sheet(os.path.join(REPORT_DIR, "review-3-arm.png"), bed["right-arm"], BLUE,
             "Plate 12, the arm", "10 x 30 x 100 solid bar. 47 mm sits in the receiver (nominal; slide it in or out 30 mm), the rest "
             "sticks out to the right. The two holes near the end take the foot's wing bolts; the nuts sit in the hex pockets on the "
             "dash side.")
  part_sheet(os.path.join(REPORT_DIR, "review-4-bar.png"), bed["right-bar"], BLUE,
             "Plate 12, the bar", "The foot (two upright slots: 9 mm up or down) laps the arm's end on two wing bolts; the bar runs 70 "
             "mm back towards you; the flag at the back is a plate across the column with the pivot hole and the second hole for "
             "the bracket, nuts in hex pockets on its dash side.")
  part_sheet(os.path.join(REPORT_DIR, "review-5-bracket.png"), bed["right-bracket"], BLUE,
             "Plate 12, the bracket", "The flat tab laps the flag: the pivot hole and a curved slot (15 degrees each way) set the "
             "motor's angle on two wing bolts. The face plate stands up from it, 5 mm, with the motor's four M3 holes and the 22.5 "
             "mm hole for its boss; the shaft comes through it, the gear on the end.")
  teeth_sheet(os.path.join(REPORT_DIR, "review-6-teeth-v2.png"))
  for stem, m in bed.items():
    print(f"{stem}: {size_text(m)}")


if __name__ == "__main__":
  sys.exit(main())
