"""
Review pictures of everything to print for the right-arm build (3 Nov 2026, the arm v6, the fit print, on the frame
plate v5: the arm 50 mm deep where it leaves the frame plate, the motor slides in and out of the teeth in a closed
tube, and both slides the same way, a wing bolt in a groove into a nut in the inner piece): the apparatus close up
with its bolts and nuts drawn in; the motor's slide in, out and going together; the arm's slide in the receiver;
then each printed piece on its own, big, two views, with its size and what it does.

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
STALE = ("review-4-bar.png", "review-5-bracket.png", "review-5b-carrier.png", "review-6-teeth-v2.png",   # v2's sheets
         "review-5-teeth-v2.png")


def hardware(dz: float = 0.0, off=(0.0, 0.0, 0.0), bolt_in: bool = True, receiver_in: bool = True,
             arm_dx: float = 0.0) -> list:
  """The wing bolts, the washers and the nuts, in the steering wheel frame, the motor slid dz from the drawn depth,
  the arm arm_dx across; the slide's nut (in the carrier's bar) moved by off with the carrier; the slide's wing bolt
  and washer too, unless bolt_in is False (then they wait 15 mm out from the groove, not yet in); the receiver's wing
  bolt and washer left out when receiver_in is False (they go in on the car)."""
  out = []
  wait = (15.0 * float(RA.U[0]), 15.0 * float(RA.U[1]), 0.0)
  for name, m in RC.hardware(dz, arm_dx=arm_dx).items():
    if name == "slide nut":
      m = m.translate(off)
    elif name.startswith("slide"):
      m = m.translate(off) if bolt_in else m.translate(wait)
    elif name != "receiver nut" and not receiver_in:
      continue
    out.append((m, STEEL))
  return out


def grip_segment(span: float = 45.0) -> Manifold:
  grip_r = S.FP.GRIP / 2.0
  rr = S.FP.WHEEL_OD / 2.0 - grip_r
  circle = [(rr + grip_r * math.cos(math.radians(a)), grip_r * math.sin(math.radians(a))) for a in range(0, 360, 10)]
  return revolve(circle, RA.THETA - span, RA.THETA + span, step_deg=2.0)


def assembly_parts(with_grip: bool = True, dz: float = 0.0, off=(0.0, 0.0, 0.0), bolt_in: bool = True,
                   receiver_in: bool = True, arm_dx: float = 0.0) -> list:
  """Everything, the carrier slid dz along the column and moved off (to show it going in), the arm slid arm_dx
  across in the receiver."""
  mg = RA.motor_and_gear(dz)
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=18)).rotate((0.0, 0.0, RA.THETA))      # the 20 set, the one on the car
  mov = [(RA.carrier(dz), CARRIER), (mg["motor"], DARK), (mg["board"], DARK), (mg["gear"], ORANGE)]
  a = (arm_dx, 0.0, 0.0)
  parts = [(RA.plate_to_wheel(RA.frame_plate_v5()), PLATE), (RA.arm().translate(a), BLUE)] + \
    [(m.translate(off).translate(a), c) for m, c in mov] + hardware(dz, off, bolt_in, receiver_in, arm_dx)
  if with_grip:
    parts += [(teeth, ORANGE), (grip_segment(), CAR)]
  return parts


def size_text(m: Manifold) -> str:
  bb = m.bounding_box()
  return " x ".join(f"{bb[i + 3] - bb[i]:.0f}" for i in range(3)) + " mm"


def assembly_picture(path: str) -> None:
  parts = assembly_parts()
  views = [(parts, R.look((0.0, 0.0, 1.0), (0, 1, 0))), (parts, R.look((0.0, -1.0, 0.0), (0, 0, 1))),
           (parts, R.look((0.9, -0.5, 0.8), (0, 1, 0))), (parts, R.look((1.0, -0.15, 0.1), (0, 1, 0)))]
  R.save(path, views, cols=2, size=(1100, 800),
         titles=["from your seat: the motor outside the rim just above 4 o'clock, shaft pointing at the wheel's middle",
                 "from below, the wheel at the top (as in your photos)",
                 "from your right and below", "from the passenger's side (the right)"],
         suptitle="The right arm mount v6, assembled, the motor slid up the groove: gear in the teeth, lane keeping on. "
                  "Plate light grey (on the column cover, not drawn), the arm blue, the motor carrier green, motor dark, "
                  "gear and teeth orange, the bolts, nuts and washer steel, a piece of the wheel grip grey.")


def slide_picture(path: str) -> None:
  """The slide close up: in, slid out, and the carrier going down into the tower (off the car)."""
  off = (0.0, 0.0, 95.0)
  near = [assembly_parts(dz=0.0), assembly_parts(dz=RA.DZ_OUT)]
  bench = [p for p in assembly_parts(with_grip=False, dz=RA.DZ_OUT, off=off, bolt_in=False, receiver_in=False)
           if p[1] is not PLATE]
  side, below = R.look((1.0, -0.6, 0.0), (0, 0, 1)), R.look((0.6, -1.0, 0.5), (0, 0, 1))
  views = [(near[0], side), (near[1], side), (near[0], below), (near[1], below),
           (bench, R.look((0.9, -0.9, 0.6), (0, 0, 1))),
           (bench, R.look((float(RA.U[0]), float(RA.U[1]), 0.15), (0, 0, 1)))]
  R.save(path, views, cols=2, size=(1100, 800),
         titles=["IN: the wing bolt slid up the groove, the gear in the teeth, tightened (the wheel is up, the dash down)",
                 (f"OUT: loosened, slid down until the carrier sits on the tower ({-RA.DZ_OUT:.0f} mm below the drawn "
                  "depth; 6 is enough), tightened"),
                 "IN, from below on the right", "OUT, from below on the right",
                 "PUTTING IT TOGETHER, off the car: the carrier's bar goes down the tower's tube from the top",
                 "the same from the passenger's side; then the wing bolt and washer in through the groove into its nut"],
         suptitle="On and off, and how deep: one wing bolt in the groove up the tower's outer side, screwed into a nut in "
                  "the carrier's bar. Loosen it, slide the motor along the column by it, tighten it. The groove's ends "
                  "keep the carrier in; the ticks on the bar, read at the tower's top, show how far up it is.")


def receiver_picture(path: str) -> None:
  """The arm's slide in the receiver: slid all the way in and out, from below and from your side; and going in."""
  def parts(dx, receiver_in=True, away=0.0):
    return assembly_parts(with_grip=False, dz=RA.DZ_OUT, arm_dx=dx + away, receiver_in=receiver_in)
  below, yours = R.look((0.0, -1.0, 0.0), (0, 0, 1)), R.look((0.25, -0.55, 1.0), (0, 1, 0))
  views = [(parts(-RA.ARM_SLIDE), below), (parts(RA.ARM_SLIDE), below), (parts(0.0), yours),
           (parts(0.0, receiver_in=False, away=70.0), yours)]
  R.save(path, views, cols=2, size=(1100, 800),
         titles=[f"slid all the way in ({RA.ARM_SLIDE:.1f} mm), from below, the wheel at the top",
                 f"slid all the way out ({RA.ARM_SLIDE:.1f} mm), from below",
                 "as drawn, from your seat, low: the wing bolt in the groove, on your side",
                 ("PUTTING IT ON: the arm, its nut in the slot in its top, slides in\nfrom the key side; "
                  "then the wing bolt and washer in through the groove")],
         suptitle="The arm's slide, the same as the motor's: one wing bolt through a 42 mm groove in the receiver's wall "
                  "on your side, screwed into a nut in the arm's bar. Loosen it, slide the arm across by it, tighten it: "
                  "it pulls the bar against the wall. The groove's ends keep the arm in.")


def part_sheet(path: str, m: Manifold, color, title: str, note: str, views=None, titles=None) -> None:
  views = views or [R.view_matrix(-50, 35), R.view_matrix(130, 25)]
  panels = [([(m, color)], v) for v in views]
  R.save(path, panels, cols=2, size=(1000, 750), titles=titles or ["from the front left, above", "from the back right, above"],
         suptitle=f"{title}: {size_text(m)}. {note}")


def teeth_sheet(path: str) -> None:
  t = MT.MidTeeth(n_teeth=18)
  m = MT.mid_teeth(t)
  bed = MT.on_bed(m)
  back = bed.rotate((180.0, 0.0, 0.0))
  panels = [([(bed, ORANGE)], R.view_matrix(-60, 40)), ([(back, ORANGE)], R.view_matrix(-60, 40)),
            ([(bed, ORANGE)], R.look((0.0, 0.0, 1.0), (0, 1, 0))), ([(back, ORANGE)], R.look((0.0, 0.0, 1.0), (0, 1, 0)))]
  R.save(path, panels, cols=2, size=(1000, 650),
         titles=["as printed: the teeth up, the wheel side down", "turned over: the channel that goes on the grip",
                 "as printed, from above", "turned over, from above"],
         suptitle=f"Teeth v3, 20 (winding roads: 19 teeth, 19.5 degrees each way), plate 9: {size_text(bed)}, about {round(2 * t.half / 360 * 2 * math.pi * t.w_out):.0f} mm "
                  "along the grip. The channel 1 mm wider than v2 (the inner wall pulled 7 mm); the ends cut back to just "
                  "past the last teeth, clear of the spokes; the inner wall only in the middle (23 mm each side of "
                  "centre), one 12 mm zip tie slot through it.")


def main():
  os.makedirs(REPORT_DIR, exist_ok=True)
  for stale in STALE:
    p = os.path.join(REPORT_DIR, stale)
    if os.path.exists(p):
      os.remove(p)
  bed = RA.parts_on_bed()
  assembly_picture(os.path.join(REPORT_DIR, "review-1-assembly.png"))
  slide_picture(os.path.join(REPORT_DIR, "review-1b-slide.png"))
  receiver_picture(os.path.join(REPORT_DIR, "review-1c-receiver.png"))
  part_sheet(os.path.join(REPORT_DIR, "review-2-frame-plate.png"), bed["column-frame-plate-v5"], PLATE,
             "Plate 11, frame plate v5", "6 mm thick. Hangs on the two cover screws (the cup slot and slot 1). The square tube is "
             "the receiver, its bore 20 wide: the arm slides in from the key side; one wing bolt through the long groove in "
             "the tube's wall on your side, into a nut in the arm, holds it anywhere along the groove. Printed labels up; in "
             "the car the labels face down.")
  part_sheet(os.path.join(REPORT_DIR, "review-3-arm.png"), bed["right-arm"], BLUE,
             "Plate 12, the arm v6 (printed flat, the tower standing up)", "The 20 x 30 bar goes in the receiver (47 mm "
             "in as drawn, 17.5 further in or out by the groove); its M5 nut drops into the slot in its top, flats along "
             "the bar, and the receiver's wing bolt comes in from the face on your side. Just outside the receiver the arm "
             "is 50 mm deep along the column, so it doesn't twist. The tower at its end has a square tube up it, closed all "
             "round: the motor carrier's bar slides down into it from the top. The motor's wing bolt runs in the groove up "
             "its outer wall.",
             views=[R.view_matrix(-50, 35), R.view_matrix(60, 30)],
             titles=["from the front left, above", "from the front right, above: the tube"])
  part_sheet(os.path.join(REPORT_DIR, "review-4-carrier.png"), bed["right-carrier"], CARRIER,
             "Plate 12, the motor carrier v6 (printed on its side)", "The motor bolts to the standing plate with four M3 "
             "x 10 from the side with the four round pads (the boss in the big hole, the shaft through it towards the "
             "wheel's middle). The long bar slides down the arm's tower; the slide's M5 nut drops into the slot on top "
             "(flats along the bar), the wing bolt comes in from the outer face. The ticks on that face read the slide.",
             views=[R.view_matrix(-50, 35), R.view_matrix(130, 30)])
  teeth_sheet(os.path.join(REPORT_DIR, "review-5-teeth-v3.png"))
  for stem, m in bed.items():
    print(f"{stem}: {size_text(m)}")


if __name__ == "__main__":
  sys.exit(main())
