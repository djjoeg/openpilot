"""
The arm mount, v2 (1 Nov 2026): the simple, adjustable apparatus that hangs on the frame plate under the column.
The frame plate stays on the car; the apparatus slides into it and one wing bolt holds it.

  frame plate v3  - the frame plate (v1, frameplate.py, with your marks) with a receiver under the block on the key
                    side of the cup: a square tube along the column, open at both ends, the arm's size inside
  arm             - a flat bar, 10 x 30, along the column: its front end slides into the receiver from the wheel end
                    (the tube carries the load); one M5 wing bolt through the receiver's outer wall, into a nut trapped
                    in the wall, pinches it so it can't slide. Push it in or pull it out to set how deep the gear sits
                    in the teeth. Its back end has two upright slots
  bracket         - the motor bolts to its face plate (four M3, the boss through a hole); from the face plate's
                    4 o'clock end an upright ear rises, bolted to the arm's upright slots by two wing bolts into nuts
                    trapped in the ear: slide it up or down to set the gear's reach along the teeth. A step on the ear
                    sits against the arm's end face, so the ear stays upright
  gear            - the side-slide gear (you have it)

The motor is at 5:20 behind the wheel, its shaft pointing out at the grip, the gear on the teeth: the side-slide
mount's place (sideparts.py), with its face at R_FACE from the column's axis, on the plane Z_AXIS.

Steering wheel frame (mm): z along the column towards you, 0 at the middle of the grip; y up; x to your right.
The frame plate: its top (the cover's underside) at COVER_Y, the cup screw at (CUP_X, CUP_Z); its own frame
(frameplate.py: x towards the driver's door, y towards the dash) maps as X = CUP_X - x, Z = CUP_Z - y.

Rough numbers (until the test fit): COVER_Y, CUP_X, CUP_Z, and the cover's front edge. The arm slides +-17 mm in
the receiver (more, if it must), the bracket +-9 mm up and down.

  python3 armmount.py   # writes ../stl/arm-mount/*.stl, ../plates/plate-5-frame-plate-v3.3mf, plate-6-arm-mount.3mf
                        # and ../report/arm-mount.png, column-frame-plate-v3.png
"""
import math
import os
import sys

import numpy as np
from manifold3d import CrossSection, Manifold

import frameplate as FR
import sideparts as S
from cadlib import box, clean, cyl, cyl_x, cyl_y, hex_prism_x, hex_prism_z, on_bed, union, write_stl
from params import NEMA, NEMA_LEN

HERE = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(HERE, "..", "stl", "arm-mount")
REPORT_DIR = os.path.join(HERE, "..", "report")

# ***** the car (rough) *****
COVER_Y = -107.0                 # the lower column cover's underside: the frame plate's top
CUP_X, CUP_Z = 73.0, -145.0      # the cup screw (your tape: 127 mm behind the back of the grip; x from the photo model)
COVER_FRONT_Z = -107.0           # the cover's front edge (fit B of the photo model; not measured)

# ***** the motor (the side-slide mount's place) *****
MOUNT_DEG = S.MOUNT_DEG          # -70: 5:20
R_FACE = S.PP.R_FACE_P           # 153: the motor's front face from the column's axis
Z_AXIS = S.PP.Z_AXIS_P           # -59.5: the motor's axis, along the column
U = np.array([math.cos(math.radians(MOUNT_DEG)), math.sin(math.radians(MOUNT_DEG))])      # out along the shaft
V = np.array([-math.sin(math.radians(MOUNT_DEG)), math.cos(math.radians(MOUNT_DEG))])     # across, towards 4 o'clock
H = NEMA / 2

# ***** the frame plate v3 (plate frame, as frameplate.py: x towards the driver's door, y towards the dash, 0 at the cup) *****
# v1 (frameplate.py) marked up on the car, 1 Nov 2026: the second screw lands in the strip's first slot towards the
# wheel; keep that slot, fill the one towards the dash, cut the other four columns away. So: the block round the cup,
# v1's bar across the dash end, and a narrow leg down the door side with the one slot; 6 mm thick (v1 was 4).
# Under the block, on the key side of the cup, a receiver: a square tube along the column the arm slides into from
# the wheel end, like a trailer hitch. The tube carries the load; one wing bolt through its outer wall, into a nut
# trapped in the wall, pinches the arm so it can't slide. No shoe, no other screws.
PLATE_T = 6.0
BLOCK = (-44.0, 28.0, -14.0, 50.0)       # x0, x1, y0, y1: v1's block, out to the receiver's outer wall
BAR = (-18.0, 106.0, 36.0, 50.0)         # v1's bar, across the dash end
LEG = (88.0, 106.0, -46.0, 50.0)         # the leg: v1's first slot column, with 9 mm of plastic each side of the slot
LEG_SLOT = (97.0, -40.0, -3.0)           # x, y0, y1: v1's first column, the slot towards the wheel (the second screw)
# the receiver (plate frame x; "down" is away from the cover): its bore takes the arm (ARM_X, ARM_Y below) with 0.4 mm
# to spare; the inner wall 5 mm, the outer wall 8 mm (the nut trap is in it), the floor 5 mm; open at both ends
BORE_X = (-35.2, -24.8)                  # x: the arm at steering wheel X 98..108 is plate x -25..-35
BORE_DEPTH = 30.4                        # the arm is 30 tall
TUBE_X = (BORE_X[0] - 8.0, BORE_X[1] + 5.0)
TUBE_FLOOR_T = 5.0
TUBE_Y = (BLOCK[2], BLOCK[3])            # along the column, the block's length (64)
PINCH = (18.0, PLATE_T + BORE_DEPTH / 2) # the wing bolt: y along the tube, and its height below the cover side
M5_HOLE = 5.4
M5_NUT_AF, M5_NUT_T = 8.0, 4.0
NUT_TRAP = (M5_NUT_AF + 0.4, M5_NUT_T + 0.4)   # the slot in the outer wall the nut drops into from the floor side

# ***** the arm *****
ARM_X = (CUP_X - BORE_X[1] + 0.2, CUP_X - BORE_X[0] - 0.2)      # (98, 108): in the receiver's bore
ARM_Y = (COVER_Y - PLATE_T - 30.0, COVER_Y - PLATE_T)              # 30 tall, its top edge on the bore's ceiling
ARM_Z = (-175.0, -55.0)
ARM_SLOT_Z = (-75.0, -60.0)      # the two upright slots at the back
ARM_SLOT_Y = (-146.0, -128.0)

# ***** the bracket *****
EAR_X = (ARM_X[0] - 8.0, ARM_X[0])   # the upright ear, inboard of the arm (the motor's face corner reaches x 72.2, the gear 73.3)
EAR_Y = (-148.0, -108.0)         # its bottom clears the teeth piece's outer ramps as the wheel turns
EAR_Z = (-85.0, -50.0)           # its end towards you stays 5 mm clear of the teeth piece's outer ramps as the wheel turns;
                                 # its dash end flush with the face plate's (the bracket prints standing on that end)
EAR_HOLES = ((-137.0, -75.0), (-137.0, -60.0))    # (y, z): nominal, the middle of the arm's slots
NUT_DEEP = 4.5                   # the nuts' pockets in the ear's inner face
STEP_X = ARM_X[1]                # past the arm's end the ear is thicker, out to the arm's outer face: the step the arm's
STEP_Z = ARM_Z[1]                # end face sits against, so the ear stays upright
FACE_T = 5.0
FACE_V = (-H, 44.0)              # the face plate across (towards 4 o'clock), out to the ear
FACE_R_MAX = 159.5               # the plate's far corner trimmed to this radius: inside the teeth's inner end (160.5)
BOSS_HOLE = 22.5
NEMA_HOLES = 31.0


def plate_to_wheel(m: Manifold) -> Manifold:
  """The plate's frame (x towards the door, y towards the dash, z up off the cover side, the labels on top) -> the
  steering wheel frame: X = CUP_X - x, Y = COVER_Y - z (the labels face down), Z = CUP_Z - y. A rotation, no mirror:
  printed labels up, the plate goes on the car labels down."""
  return m.transform([[-1.0, 0.0, 0.0, CUP_X], [0.0, 0.0, -1.0, COVER_Y], [0.0, -1.0, 0.0, CUP_Z]])


# ----- the frame plate v3 (printed frame, as frameplate.py: key side +x, labels up) -----

def through_slot(xc: float, yc: float, length: float, width: float, along: str) -> Manifold:
  """An oblong hole through the whole plate (frameplate.slot only reaches frameplate's 4 mm)."""
  r = width / 2
  d = (length - width) / 2
  z0, z1 = -1.0, PLATE_T + 1.0
  if along == "x":
    ends = [cyl(r, z0, z1, x=xc - d, y=yc, segments=32), cyl(r, z0, z1, x=xc + d, y=yc, segments=32)]
  else:
    ends = [cyl(r, z0, z1, x=xc, y=yc - d, segments=32), cyl(r, z0, z1, x=xc, y=yc + d, segments=32)]
  return Manifold.batch_hull(ends)


def frame_plate_v3() -> Manifold:
  T = PLATE_T
  body = box(BAR[0], BAR[1], BAR[2], BAR[3], 0.0, T) + box(LEG[0], LEG[1], LEG[2], LEG[3], 0.0, T) + \
    box(BLOCK[0], BLOCK[1], BLOCK[2], BLOCK[3], 0.0, T)
  body = body - through_slot(0.0, 0.0, FR.SLOT_L, FR.SLOT_W, "x")
  xc, y0, y1 = LEG_SLOT
  body = body - through_slot(xc, (y0 + y1) / 2, y1 - y0, FR.SLOT_W, "y")
  # the receiver, standing on the plate's labelled side (down, in the car)
  z1 = T + BORE_DEPTH + TUBE_FLOOR_T
  tube = box(TUBE_X[0], TUBE_X[1], TUBE_Y[0], TUBE_Y[1], T - 0.01, z1)
  tube = tube - box(BORE_X[0], BORE_X[1], TUBE_Y[0] - 1.0, TUBE_Y[1] + 1.0, T, T + BORE_DEPTH)
  py, pz = PINCH
  tube = tube - cyl_x(M5_HOLE / 2, TUBE_X[0] - 1.0, BORE_X[0] + 1.0, y=py, z=pz, segments=32)
  tw, tt = NUT_TRAP
  xn = (TUBE_X[0] + BORE_X[0]) / 2                      # the nut in the middle of the outer wall
  tube = tube - box(xn - tt / 2, xn + tt / 2, py - tw / 2, py + tw / 2, pz - tw / 2 / math.cos(math.radians(30)), z1 + 1.0)
  body = body + tube
  # labels on the top (in the car, the underside): read from below with the dash at the top, the key side is on the left
  import slotplate as SL
  SL.FONT.setdefault("<", ("010", "100", "111", "100", "010"))
  labels = [FR.text("< KEY", BORE_X[1] + 6.0, BLOCK[3] - 8.0, T), FR.text("WHEEL", -8.0, BLOCK[2] + 3.0, T, pix=0.9),
            FR.text("1", xc - FR.text_width("1", 0.9) / 2, LEG[2] + 3.0, T, pix=0.9)]
  return clean(body + union(labels))


frame_plate_v2 = frame_plate_v3     # the name the rest of this file uses


def plate_drawing(path: str) -> None:
  """The frame plate v3 seen from below, as in the photos, with the screws drawn in."""
  import matplotlib
  matplotlib.use("Agg")
  import matplotlib.pyplot as plt
  from matplotlib.patches import Circle, Rectangle
  fig, ax = plt.subplots(figsize=(8.5, 6.0), dpi=150)
  for r in (BLOCK, BAR, LEG):
    ax.add_patch(Rectangle((r[0], r[2]), r[1] - r[0], r[3] - r[2], fc="#cfd3d6", ec="#444", lw=1.0))
  for r in (BLOCK, BAR, LEG):
    ax.add_patch(Rectangle((r[0] + 0.5, r[2] + 0.5), r[1] - r[0] - 1.0, r[3] - r[2] - 1.0, fc="#cfd3d6", ec="none"))
  ax.add_patch(Rectangle((-FR.SLOT_L / 2, -FR.SLOT_W / 2), FR.SLOT_L, FR.SLOT_W, fc="white", ec="#444"))
  xc, y0, y1 = LEG_SLOT
  ax.add_patch(Rectangle((xc - FR.SLOT_W / 2, y0), FR.SLOT_W, y1 - y0, fc="white", ec="#444"))
  ax.add_patch(Rectangle((TUBE_X[0], TUBE_Y[0]), TUBE_X[1] - TUBE_X[0], TUBE_Y[1] - TUBE_Y[0], fc="#9aa4ad", ec="#444", lw=1.0))
  ax.add_patch(Rectangle((BORE_X[0], TUBE_Y[0]), BORE_X[1] - BORE_X[0], TUBE_Y[1] - TUBE_Y[0], fc="#e8ebee", ec="#444", lw=0.8))
  ax.add_patch(Circle((TUBE_X[0] + 4.0, PINCH[0]), 2.7, fc="white", ec="#444"))
  ax.add_patch(Circle((0, 0), 6.25, fc="none", ec="#c0392b", ls="--", lw=1.5))
  ax.text(0, -12, "cup screw", ha="center", va="top", fontsize=8, color="#c0392b")
  ax.text(xc, -44, "2nd screw", ha="center", va="top", fontsize=8, color="#c0392b")
  ax.text(-30, 58, "receiver: the arm\nslides in from\nthe wheel end", ha="center", va="top", fontsize=7, color="#444")
  ax.text(-30, 18, "wing bolt", ha="right", va="center", fontsize=7, color="#444")
  ax.text(44, 43, "6 mm thick", ha="center", va="center", fontsize=7, color="#444")
  ax.set_aspect("equal")
  ax.set_xlim(125, -60)
  ax.set_ylim(78, -62)
  ax.set_xlabel("across the car, mm (0 = cup screw; the key side to the right)")
  ax.set_ylabel("along the column, mm (0 = cup screw; the wheel is up)")
  ax.set_title("Frame plate v3 seen from below, as in your photos: the wheel at the top, the key side on the right.\n"
               "v1 with your marks (first slot column kept, its dash-side slot filled, the rest cut away), 6 mm thick, and the receiver for the arm.", fontsize=9)
  ax.grid(True, lw=0.3, alpha=0.5)
  fig.tight_layout()
  fig.savefig(path)
  plt.close(fig)


# ----- the arm and the bracket (steering wheel frame) -----

def arm() -> Manifold:
  m = box(ARM_X[0], ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1])
  for z in ARM_SLOT_Z:
    m = m - Manifold.batch_hull([cyl_x(M5_HOLE / 2, ARM_X[0] - 1.0, ARM_X[1] + 1.0, y=ARM_SLOT_Y[0] + M5_HOLE / 2, z=z, segments=32),
                                 cyl_x(M5_HOLE / 2, ARM_X[0] - 1.0, ARM_X[1] + 1.0, y=ARM_SLOT_Y[1] - M5_HOLE / 2, z=z, segments=32)])
  return clean(m)


def face_plate_local() -> Manifold:
  """The face plate in a local frame: a along the shaft (out), b across towards 4 o'clock, c along the column."""
  m = box(R_FACE, R_FACE + FACE_T, FACE_V[0], FACE_V[1], EAR_Z[0] - Z_AXIS, H)   # the plate runs on to the ear's dash end
  m = m - cyl_x(BOSS_HOLE / 2, R_FACE - 1.0, R_FACE + FACE_T + 1.0, y=0.0, z=0.0, segments=64)
  for b in (-NEMA_HOLES / 2, NEMA_HOLES / 2):
    for c in (-NEMA_HOLES / 2, NEMA_HOLES / 2):
      m = m - cyl_x(1.7, R_FACE - 1.0, R_FACE + FACE_T + 1.0, y=b, z=c, segments=24)
  return m


def local_to_wheel(m: Manifold) -> Manifold:
  """local (a out along the shaft, b across, c along the column) -> steering wheel frame."""
  return m.rotate((0.0, 0.0, MOUNT_DEG)).translate((0.0, 0.0, Z_AXIS))


def bracket() -> Manifold:
  face = local_to_wheel(face_plate_local()) ^ cyl(FACE_R_MAX, -100.0, -20.0, segments=256)   # its far corner trimmed
  ear = box(EAR_X[0], EAR_X[1], EAR_Y[0], EAR_Y[1], EAR_Z[0], EAR_Z[1])
  step = box(EAR_X[0], STEP_X, EAR_Y[0], EAR_Y[1], STEP_Z, EAR_Z[1])
  m = face + ear + step
  for y, z in EAR_HOLES:
    m = m - cyl_x(M5_HOLE / 2, EAR_X[0] - 1.0, EAR_X[1] + 1.0, y=y, z=z, segments=32)
    m = m - hex_prism_x(M5_NUT_AF + 0.4, EAR_X[0] - 1.0, EAR_X[0] + NUT_DEEP, y=y, z=z)
  return clean(m)


def motor_and_gear() -> dict:
  """The motor's body and the side-slide gear, in the steering wheel frame (S.to_wheel takes the carrier frame)."""
  motor = box(-H, H, -H, H, -NEMA_LEN, 0.0) + cyl(11.0, 0.0, 2.0)
  board = box(-23.0, 23.0, -23.0, 23.0, -NEMA_LEN - 11.0, -NEMA_LEN)
  return {"motor": S.to_wheel(motor), "board": S.to_wheel(board), "gear": S.to_wheel(S.side_gear())}


# ----- the print bed -----

def parts_on_bed() -> dict:
  """Each part turned the way it prints: the plate labels up (the receiver standing on it); the arm on its side;
  the bracket standing on its dash end (the face plate and the ear are both upright walls then)."""
  br = on_bed(bracket())                                # standing on its dash end: both plates upright
  return {"column-frame-plate-v3": on_bed(frame_plate_v3()),
          "arm-bar": on_bed(arm(), rotate=(0.0, 90.0, 0.0)),
          "arm-bracket": br}


def build(out_dir: str = STL_DIR) -> dict:
  os.makedirs(out_dir, exist_ok=True)
  info = {}
  for stem, m in parts_on_bed().items():
    write_stl(m, os.path.join(out_dir, stem + ".stl"), stem)
    bb = m.bounding_box()
    info[stem] = {"size_mm": [round(bb[i + 3] - bb[i], 1) for i in range(3)], "grams_solid": round(m.volume() / 1000 * 1.28)}
  return info


def bambu_plates() -> list:
  import plates as P
  out = []
  parts = {"column-frame-plate-v3": ("frame plate v3", 1, P.STANDARD)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-5-frame-plate-v3", "5 frame plate v3", list(parts), "Plate 5: the frame plate v3 (bolts trapped in it)")])
  parts = {"arm-bar": ("arm", 1, P.SOLID), "arm-bracket": ("bracket", 1, P.SOLID)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-6-arm-mount", "6 arm mount", list(parts), "Plate 6: the arm mount: arm, bracket")])
  return out


# ----- the picture -----

def scene() -> list:
  """(manifold, colour) pairs in the steering wheel frame: the car (grey), the plate (light), the apparatus (blue), the
  motor (dark), the gear and the teeth (orange)."""
  import carscene as CS
  import midteeth as MT
  from cadlib import revolve
  sc = CS.CarScene(D=125.0)
  cover = sc.column_cover(back=130.0)
  grip_r = S.FP.GRIP / 2.0 if hasattr(S.FP, "GRIP") else 16.5
  rr = S.FP.WHEEL_OD / 2.0 - grip_r if hasattr(S.FP, "WHEEL_OD") else 168.3
  circle = [(rr + grip_r * math.cos(math.radians(a)), grip_r * math.sin(math.radians(a))) for a in range(0, 360, 10)]
  grip = revolve(circle, -180.0, 180.0, step_deg=2.0)
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=10)).rotate((0.0, 0.0, MOUNT_DEG))
  mg = motor_and_gear()
  car, plate, app, dark, orange = (0.55, 0.55, 0.58), (0.80, 0.82, 0.85), (0.35, 0.55, 0.85), (0.25, 0.25, 0.28), (0.95, 0.65, 0.3)
  return [(cover, car), (grip, car), (teeth, orange), (mg["gear"], orange), (mg["motor"], dark), (mg["board"], dark),
          (plate_to_wheel(frame_plate_v2()), plate), (arm(), app), (bracket(), app)]


def picture(path: str) -> None:
  import render as R
  parts = scene()
  blue = (0.35, 0.55, 0.85)
  bed = parts_on_bed()
  views = [(parts, R.look((0.9, -0.6, 0.8), (0, 1, 0))), (parts, R.look((0.0, -1.0, 0.0), (0, 0, 1))),
           ([(bed["column-frame-plate-v3"], (0.8, 0.82, 0.85))], R.view_matrix(-50, 35)), ([(bed["arm-bar"], blue)], R.view_matrix(-50, 35)),
           ([(bed["arm-bracket"], blue)], R.view_matrix(-50, 35)), ([(bed["column-frame-plate-v3"], (0.8, 0.82, 0.85))], R.view_matrix(130, 25))]
  R.save(path, views, cols=2, size=(1000, 650),
         titles=["on the car, from your right and below", "from below, the wheel at the top (as in your photos)",
                 "frame plate v3, as printed (labels up, the receiver standing on it)", "arm, as printed",
                 "bracket, as printed (standing on its dash end)", "frame plate v3 from the other side"],
         suptitle="Arm mount v1 on the frame plate v3, under the column: the car grey, the plate light, the apparatus blue, "
                  "the motor dark, the gear and the teeth orange. The car is the photo model: rough.")


def main():
  info = build()
  for stem, i in info.items():
    print(f"{stem}: {i['size_mm']} mm, about {i['grams_solid']} g solid")
  for n, fname, plate_name, rows, size in bambu_plates():
    print(f"{fname}.3mf ({size / 1e3:.0f} kB)")
  os.makedirs(REPORT_DIR, exist_ok=True)
  plate_drawing(os.path.join(REPORT_DIR, "column-frame-plate-v3.png"))
  picture(os.path.join(REPORT_DIR, "arm-mount.png"))


if __name__ == "__main__":
  sys.exit(main())
