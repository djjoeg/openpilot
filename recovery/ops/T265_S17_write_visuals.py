"""
Review pictures of everything to print for the right-arm build (2 Nov 2026, the arm v3: two printed pieces, the
motor slides in and out of the teeth): the apparatus close up with its wing bolts and nuts drawn in; slid in, slid
out and going on; then each printed piece on its own, big, two views, with its size and what it does.

  python3 visuals.py      # writes ../report/review-*.png
"""
import math
import os
import sys

from manifold3d import Manifold

import midteeth as MT
import render as R
import rightarm as RA
import rightcheck as RC
import sideparts as S
from cadlib import revolve

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(HERE, "..", "report")

STEEL = (0.78, 0.78, 0.80)
PLATE = (0.80, 0.82, 0.85)
BLUE = (0.35, 0.55, 0.85)
CARRIER = (0.45, 0.70, 0.45)
DARK = (0.25, 0.25, 0.28)
ORANGE = (0.95, 0.65, 0.3)
CAR = (0.55, 0.55, 0.58)
STALE = ("review-4-bar.png", "review-5-bracket.png", "review-5b-carrier.png", "review-6-teeth-v2.png")   # v2's sheets


def hardware(dz: float = 0.0, off=(0.0, 0.0, 0.0)) -> list:
  """The three wing bolts and their four nuts, in the steering wheel frame, the motor slid dz from its stop; the
  carrier's own (the stop bolt and its nuts) moved by off as well."""
  out = []
  for name, m in RC.hardware(dz, RA.STOP_P).items():
    out.append((m.translate(off) if name.startswith("stop") else m, STEEL))
  return out


def grip_segment(span: float = 45.0) -> Manifold:
  grip_r = S.FP.GRIP / 2.0
  rr = S.FP.WHEEL_OD / 2.0 - grip_r
  circle = [(rr + grip_r * math.cos(math.radians(a)), grip_r * math.sin(math.radians(a))) for a in range(0, 360, 10)]
  return revolve(circle, RA.THETA - span, RA.THETA + span, step_deg=2.0)


def assembly_parts(with_grip: bool = True, dz: float = 0.0, off=(0.0, 0.0, 0.0)) -> list:
  """Everything, the carrier slid dz along the column and moved off (to show it going in)."""
  mg = RA.motor_and_gear(dz)
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=10)).rotate((0.0, 0.0, RA.THETA))
  mov = [(RA.carrier(dz), CARRIER), (mg["motor"], DARK), (mg["board"], DARK), (mg["gear"], ORANGE)]
  parts = [(RA.plate_to_wheel(RA.frame_plate_v4()), PLATE), (RA.arm(), BLUE)] + \
    [(m.translate(off), c) for m, c in mov] + [(teeth, ORANGE)] + hardware(dz, off)
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
         suptitle="The right arm mount v3, assembled, the motor slid up against its stop: gear in the teeth, lane keeping "
                  "on. Plate light grey (on the column cover, not drawn), the arm blue, the motor carrier green, motor "
                  "dark, gear and teeth orange, the wing bolts and nuts steel, a piece of the wheel grip grey.")


def slide_picture(path: str) -> None:
  """The slide close up: in, slid out, and the carrier going on."""
  t = 30.0
  off = (float(t * RA.V[0]), float(t * RA.V[1]), 0.0)
  near = [assembly_parts(dz=0.0), assembly_parts(dz=RA.DZ_OUT), assembly_parts(dz=RA.DZ_OUT, off=off)]
  side, below = R.look((1.0, -0.6, 0.0), (0, 0, 1)), R.look((0.6, -1.0, 0.5), (0, 0, 1))
  views = [(near[0], side), (near[1], side), (near[0], below), (near[1], below),
           (near[2], R.look((0.9, -0.9, 0.6), (0, 0, 1))), (near[2], R.look((0.3, 1.0, 0.2), (0, 0, 1)))]
  R.save(path, views, cols=2, size=(1100, 800),
         titles=["IN: slid up against the stop, the push wing bolt tight (the wheel is up, the dash down)",
                 "OUT: push bolt loosened, motor slid 10 mm down the column (6 mm is enough), tightened",
                 "IN, from below on the right", "OUT, from below on the right",
                 "PUTTING IT ON: the carrier, motor on it, comes in from the motor's side into the channel",
                 "the same from above the column, looking down past the motor"],
         suptitle="On and off: loosen the wing bolt on the tower's outer side, slide the motor along the column, tighten "
                  "it. The wing bolt up through the lug at the bottom of the motor carrier's bar is the stop: it sets "
                  "how deep the gear sits in the teeth (set it once; the jam nut above its wings holds it).")


def part_sheet(path: str, m: Manifold, color, title: str, note: str, views=None, titles=None) -> None:
  views = views or [R.view_matrix(-50, 35), R.view_matrix(130, 25)]
  panels = [([(m, color)], v) for v in views]
  R.save(path, panels, cols=2, size=(1000, 750), titles=titles or ["from the front left, above", "from the back right, above"],
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
  for stale in STALE:
    p = os.path.join(REPORT_DIR, stale)
    if os.path.exists(p):
      os.remove(p)
  bed = RA.parts_on_bed()
  assembly_picture(os.path.join(REPORT_DIR, "review-1-assembly.png"))
  slide_picture(os.path.join(REPORT_DIR, "review-1b-slide.png"))
  part_sheet(os.path.join(REPORT_DIR, "review-2-frame-plate.png"), bed["column-frame-plate-v4"], PLATE,
             "Plate 11, frame plate v4", "6 mm thick. Hangs on the two cover screws (the cup slot and slot 1). The square tube is "
             "the receiver: the arm slides in from the key side, one wing bolt through the tube's far wall pinches it; the nut drops "
             "into the slot in that wall. Printed labels up; in the car the labels face down.")
  part_sheet(os.path.join(REPORT_DIR, "review-3-arm.png"), bed["right-arm"], BLUE,
             "Plate 12, the arm (printed flat, the tower standing up)", "The 10 x 30 bar goes in the receiver (47 mm in, "
             "nominal; slide it 25 mm either way). The tower at its end has a channel up it, open on the side towards the "
             "motor: the motor carrier's bar slides in it. The wing bolt goes in through the tower's outer wall and pushes "
             "the bar tight; its nut drops into the slot from the top.",
             views=[R.view_matrix(-50, 35), R.view_matrix(60, 30)],
             titles=["from the front left, above", "from the front right, above: the channel"])
  part_sheet(os.path.join(REPORT_DIR, "review-4-carrier.png"), bed["right-carrier"], CARRIER,
             "Plate 12, the motor carrier (printed on its side)", "The motor bolts to the standing plate with four M3 x 10 "
             "from the side with the four round pads (the boss in the big hole, the shaft through it towards the wheel's "
             "middle). The long bar slides in the arm's tower; the lug at its far end takes the stop wing bolt, its nut "
             "in the hex pocket.",
             views=[R.view_matrix(-50, 35), R.view_matrix(130, 30)])
  teeth_sheet(os.path.join(REPORT_DIR, "review-5-teeth-v2.png"))
  for stem, m in bed.items():
    print(f"{stem}: {size_text(m)}")


if __name__ == "__main__":
  sys.exit(main())
