"""
The right arm mount (1 Nov 2026, from your note): the motor sits OUTSIDE the steering wheel's rim on the right, at
about 4 o'clock, its shaft pointing in at the wheel's middle, the gear on the teeth from outside. The plate's receiver
runs across the car; an arm slides in it and sticks out to the right; from the arm's end a bar runs back towards you
("5 inches") to a flag; the motor bracket bolts to the flag on a pivot, so its angle can be set.

  frame plate v4  - frame plate v3 (your marks on v1) with the receiver turned to run across the car, under the
                    block, on the dash side of the cup; one wing bolt pinches the arm
  arm             - a 10 x 30 x 100 bar across the car: slide it in or out to set how far right the motor sits
  bar             - a 10 x 30 bar towards you, with a foot at its front end that laps the arm's end (two wing bolts,
                    upright slots: up and down) and a flag at its back end (a plate across the column)
  bracket         - a tab that laps the flag (one wing bolt as a pivot, one in a curved slot: the angle, +-15
                    degrees), with the motor's face plate standing up from it; the motor bolts to the face plate
                    (four M3), the shaft through its hole pointing in at the wheel
  gear            - the side-slide gear (you have it)

Steering wheel frame (mm): z along the column towards you, 0 at the middle of the grip; y up; x to your right.
THETA is where the gear meets the teeth, degrees from 3 o'clock (-30 is 4 o'clock); R_FACE_OUT the motor's face
from the wheel's middle (the gear's teeth reach in to the same radius as before, 160.5 to 173).

Rough numbers (until the test fit): COVER_Y, CUP_X, CUP_Z, THETA. Adjustable: the arm +-30 mm across, the bar
+-9 mm up and down, the bracket +-15 degrees.

  python3 rightarm.py   # writes ../stl/right-arm/*.stl, ../plates/plate-11-frame-plate-v4.3mf, plate-12-right-arm.3mf
                        # and ../report/right-arm.png, column-frame-plate-v4.png
"""
import math
import os
import sys

import numpy as np
from manifold3d import CrossSection, Manifold

import armmount as AM
import frameplate as FR
import sideparts as S
from cadlib import box, clean, cyl, cyl_x, cyl_y, hex_prism_x, hex_prism_y, hex_prism_z, on_bed, union, write_stl
from params import NEMA, NEMA_LEN

HERE = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(HERE, "..", "stl", "right-arm")
REPORT_DIR = os.path.join(HERE, "..", "report")

# ***** the car (rough) *****
COVER_Y, CUP_X, CUP_Z = AM.COVER_Y, AM.CUP_X, AM.CUP_Z       # -107, 73, -145

# ***** the motor: outside the rim, shaft pointing in *****
THETA = -30.0                    # where the gear meets the teeth: 4 o'clock (your note: the column's underside height
                                 # would be -40; a tangent 20 degrees off upright would be -20)
R_FACE_OUT = 180.0               # the motor's face from the wheel's middle (the gear's teeth: 7 to 19.5 mm in from it)
Z_AXIS = S.PP.Z_AXIS_P           # -59.5: the motor's axis, along the column (as the side-slide mount)
U = np.array([math.cos(math.radians(THETA)), math.sin(math.radians(THETA))])      # out from the wheel's middle
V = np.array([-math.sin(math.radians(THETA)), math.cos(math.radians(THETA))])     # along the rim, anticlockwise
H = NEMA / 2
FACE_T = 5.0
FACE_V = (-H, H)                 # the face plate along the rim
M5_HOLE = 5.4
M5_NUT_AF, M5_NUT_T = 8.0, 4.0
NUT_TRAP = (M5_NUT_AF + 0.4, M5_NUT_T + 0.4)
BOSS_HOLE, NEMA_HOLES = 22.5, 31.0

# ***** the frame plate v4 (plate frame: x towards the door, y towards the dash, 0 at the cup) *****
PLATE_T = 6.0
BLOCK = (-60.0, 28.0, -14.0, 50.0)       # v1's block, out to the receiver's far end on the key side
BAR, LEG, LEG_SLOT = AM.BAR, AM.LEG, AM.LEG_SLOT
BORE_Y = (20.0, 30.4)                    # the receiver's bore along the column (10 wide), on the dash side of the cup
BORE_DEPTH = 30.4                        # the arm is 30 tall
TUBE_Y = (BORE_Y[0] - 5.0, BORE_Y[1] + 8.0)   # walls: 5 on the wheel side, 8 on the dash side (the nut trap)
TUBE_X = (-60.0, 3.0)                    # along the plate, from the key-side end in to just short of the cup's washer
TUBE_FLOOR_T = 5.0
PINCH_X = -30.0                          # the wing bolt, through the dash-side wall

# ***** the arm (steering wheel frame): across, in the receiver *****
ARM_Z = (CUP_Z - BORE_Y[1] + 0.2, CUP_Z - BORE_Y[0] - 0.2)      # (-175.2, -165.2)
ARM_Y = (COVER_Y - PLATE_T - 30.0, COVER_Y - PLATE_T)          # (-143, -113)
ARM_X = (CUP_X - TUBE_X[1] + 3.0, CUP_X - TUBE_X[1] + 103.0)   # (70, 170): 60 in the receiver, nominal
ARM_HOLES_X = (150.0, 164.0)             # the foot's bolts (along the column), near the arm's end
ARM_HOLES_Y = -128.0

# ***** the bar towards you, with its foot and its flag *****
FOOT_X = (130.0, 170.0)
FOOT_Z = (ARM_Z[1], ARM_Z[1] + 10.0)     # lapping the arm's face towards you
FOOT_Y = (-150.0, ARM_Y[1])              # down to the bar's underside, so it prints lying flat
FOOT_SLOT_Y = (-137.0, -119.0)           # upright slots at ARM_HOLES_X: up and down +-9
BAR_X = (160.0, 170.0)
BAR_Y = (-150.0, -120.0)                 # below the motor's lowest corner, outside the rim and the teeth piece
BAR_Z = (FOOT_Z[0], -95.0)
FLAG_Z = (-95.0, -90.0)                  # the flag across the column at the bar's back end
FLAG_X = (140.0, 200.0)
FLAG_Y = (-150.0, -95.0)
PIVOT = (177.0, -135.0)                  # (x, y) the pivot bolt, outside the motor's body
ARC_R, ARC_DEG = 26.0, 15.0              # the second bolt swings on this radius, +-ARC_DEG about the -x direction

# ***** the bracket: the tab on the flag, the face plate standing up from it *****
TAB_Z = (FLAG_Z[1], FLAG_Z[1] + 5.0)     # (-90, -85)
TAB_X = (140.0, 200.0)
TAB_Y = (-150.0, -65.0)
FACE_Z = (TAB_Z[1] - 0.01, Z_AXIS + H)   # standing up from the tab to the motor's far side
NUT_DEEP = 4.5


def rad(t_u: float, t_v: float) -> tuple:
  """A point at t_u out along U and t_v along V, in the steering wheel frame (x, y)."""
  p = t_u * U + t_v * V
  return float(p[0]), float(p[1])


# ----- the frame plate v4 (plate frame, labels up) -----

def frame_plate_v4() -> Manifold:
  T = PLATE_T
  body = box(BAR[0], BAR[1], BAR[2], BAR[3], 0.0, T) + box(LEG[0], LEG[1], LEG[2], LEG[3], 0.0, T) + \
    box(BLOCK[0], BLOCK[1], BLOCK[2], BLOCK[3], 0.0, T)
  body = body - AM.through_slot(0.0, 0.0, FR.SLOT_L, FR.SLOT_W, "x")
  xc, y0, y1 = LEG_SLOT
  body = body - AM.through_slot(xc, (y0 + y1) / 2, y1 - y0, FR.SLOT_W, "y")
  z1 = T + BORE_DEPTH + TUBE_FLOOR_T
  tube = box(TUBE_X[0], TUBE_X[1], TUBE_Y[0], TUBE_Y[1], T - 0.01, z1)
  tube = tube - box(TUBE_X[0] - 1.0, TUBE_X[1] + 1.0, BORE_Y[0], BORE_Y[1], T, T + BORE_DEPTH)
  pz = T + BORE_DEPTH / 2
  tube = tube - cyl_y(M5_HOLE / 2, BORE_Y[1] - 1.0, TUBE_Y[1] + 1.0, x=PINCH_X, z=pz, segments=32)
  tw, tt = NUT_TRAP
  yn = (BORE_Y[1] + TUBE_Y[1]) / 2
  tube = tube - box(PINCH_X - tw / 2, PINCH_X + tw / 2, yn - tt / 2, yn + tt / 2, pz - tw / 2 / math.cos(math.radians(30)), z1 + 1.0)
  body = body + tube
  import slotplate as SL
  SL.FONT.setdefault("<", ("010", "100", "111", "100", "010"))
  labels = [FR.text("< KEY", -16.0, BLOCK[3] - 8.0, T), FR.text("WHEEL", -8.0, BLOCK[2] + 3.0, T, pix=0.9),
            FR.text("1", xc - FR.text_width("1", 0.9) / 2, LEG[2] + 3.0, T, pix=0.9)]
  return clean(body + union(labels))


def plate_to_wheel(m: Manifold) -> Manifold:
  return m.transform([[-1.0, 0.0, 0.0, CUP_X], [0.0, 0.0, -1.0, COVER_Y], [0.0, -1.0, 0.0, CUP_Z]])


# ----- the arm, the bar, the bracket (steering wheel frame) -----

def arm() -> Manifold:
  m = box(ARM_X[0], ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1])
  for x in ARM_HOLES_X:
    m = m - Manifold.cylinder(20.0, M5_HOLE / 2, M5_HOLE / 2, 32).translate((x, ARM_HOLES_Y, ARM_Z[0] - 5.0))
    m = m - hex_prism_z(M5_NUT_AF + 0.4, ARM_Z[0] - 1.0, ARM_Z[0] + NUT_DEEP, x=x, y=ARM_HOLES_Y)   # the nut, dash side
  return clean(m)


def bar() -> Manifold:
  foot = box(FOOT_X[0], FOOT_X[1], FOOT_Y[0], FOOT_Y[1], FOOT_Z[0], FOOT_Z[1])
  for x in ARM_HOLES_X:
    foot = foot - Manifold.batch_hull([Manifold.cylinder(12.0, M5_HOLE / 2, M5_HOLE / 2, 32).translate((x, y, FOOT_Z[0] - 1.0))
                                       for y in (FOOT_SLOT_Y[0] + M5_HOLE / 2, FOOT_SLOT_Y[1] - M5_HOLE / 2)])
  b = box(BAR_X[0], BAR_X[1], BAR_Y[0], BAR_Y[1], BAR_Z[0], BAR_Z[1] + 0.01)
  flag = box(FLAG_X[0], FLAG_X[1], FLAG_Y[0], FLAG_Y[1], FLAG_Z[0], FLAG_Z[1])
  m = foot + b + flag
  for x, y in (PIVOT, (PIVOT[0] - ARC_R, PIVOT[1])):
    m = m - Manifold.cylinder(10.0, M5_HOLE / 2, M5_HOLE / 2, 32).translate((x, y, FLAG_Z[0] - 1.0))
    m = m - hex_prism_z(M5_NUT_AF + 0.4, FLAG_Z[0] - 1.0, FLAG_Z[0] + NUT_DEEP, x=x, y=y)     # the nuts, dash side
  return clean(m)


def face_plate() -> Manifold:
  """The face plate, standing on the tab: perpendicular to U at R_FACE_OUT, FACE_T thick outwards."""
  m = box(R_FACE_OUT, R_FACE_OUT + FACE_T, FACE_V[0], FACE_V[1], FACE_Z[0], FACE_Z[1])
  m = m - cyl_x(BOSS_HOLE / 2, R_FACE_OUT - 1.0, R_FACE_OUT + FACE_T + 1.0, y=0.0, z=Z_AXIS, segments=64)
  for b in (-NEMA_HOLES / 2, NEMA_HOLES / 2):
    for c in (-NEMA_HOLES / 2, NEMA_HOLES / 2):
      m = m - cyl_x(1.7, R_FACE_OUT - 1.0, R_FACE_OUT + FACE_T + 1.0, y=b, z=Z_AXIS + c, segments=24)
  return m.rotate((0.0, 0.0, THETA))


def bracket() -> Manifold:
  tab = box(TAB_X[0], TAB_X[1], TAB_Y[0], TAB_Y[1], TAB_Z[0], TAB_Z[1])
  tab = tab - Manifold.cylinder(10.0, M5_HOLE / 2, M5_HOLE / 2, 32).translate((PIVOT[0], PIVOT[1], TAB_Z[0] - 1.0))
  arc = [Manifold.cylinder(10.0, M5_HOLE / 2, M5_HOLE / 2, 32).translate(
    (PIVOT[0] - ARC_R * math.cos(math.radians(a)), PIVOT[1] + ARC_R * math.sin(math.radians(a)), TAB_Z[0] - 1.0))
    for a in np.linspace(-ARC_DEG, ARC_DEG, 13)]
  tab = tab - union([Manifold.batch_hull([arc[i], arc[i + 1]]) for i in range(len(arc) - 1)])
  return clean(tab + face_plate())


def motor_and_gear() -> dict:
  """The motor's body, board and the side-slide gear: carrier frame (z out along the shaft from the face) -> here
  the shaft points in: carrier z -> -U, carrier y -> V, carrier x -> along the column."""
  motor = box(-H, H, -H, H, -NEMA_LEN, 0.0) + cyl(11.0, 0.0, 2.0)
  board = box(-23.0, 23.0, -23.0, 23.0, -NEMA_LEN - 11.0, -NEMA_LEN)
  c = R_FACE_OUT * U
  mat = [[0.0, V[0], -U[0], float(c[0])], [0.0, V[1], -U[1], float(c[1])], [1.0, 0.0, 0.0, Z_AXIS]]
  return {"motor": motor.transform(mat), "board": board.transform(mat), "gear": S.side_gear().transform(mat)}


# ----- the print bed -----

def parts_on_bed() -> dict:
  """The plate labels up (the receiver standing on it); the arm on its side; the bar lying on its underside (the
  flag standing); the bracket on its tab (the face plate standing)."""
  return {"column-frame-plate-v4": on_bed(frame_plate_v4()),
          "right-arm": on_bed(arm(), rotate=(90.0, 0.0, 0.0)),
          "right-bar": on_bed(bar(), rotate=(0.0, 0.0, 0.0)) if False else on_bed(bar().rotate((0.0, 0.0, 0.0)), rotate=(0.0, 0.0, 0.0)),
          "right-bracket": on_bed(bracket(), rotate=(180.0, 0.0, 0.0))}


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
  parts = {"column-frame-plate-v4": ("frame plate v4", 1, P.STANDARD)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-11-frame-plate-v4", "11 frame plate v4", list(parts), "Plate 11: the frame plate v4 (the receiver across)")])
  parts = {"right-arm": ("arm", 1, P.SOLID), "right-bar": ("bar", 1, P.SOLID), "right-bracket": ("bracket", 1, P.SOLID)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-12-right-arm", "12 right arm", list(parts), "Plate 12: the right arm mount: arm, bar, bracket")])
  return out


# ----- pictures -----

def scene() -> list:
  import carscene as CS
  import midteeth as MT
  from cadlib import revolve
  sc = CS.CarScene(D=125.0)
  grip_r = S.FP.GRIP / 2.0
  rr = S.FP.WHEEL_OD / 2.0 - grip_r
  circle = [(rr + grip_r * math.cos(math.radians(a)), grip_r * math.sin(math.radians(a))) for a in range(0, 360, 10)]
  grip = revolve(circle, -180.0, 180.0, step_deg=2.0)
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=10)).rotate((0.0, 0.0, THETA))
  mg = motor_and_gear()
  car, plate, app, dark, orange = (0.55, 0.55, 0.58), (0.80, 0.82, 0.85), (0.35, 0.55, 0.85), (0.25, 0.25, 0.28), (0.95, 0.65, 0.3)
  return [(sc.column_cover(back=130.0), car), (grip, car), (teeth, orange), (mg["gear"], orange), (mg["motor"], dark),
          (mg["board"], dark), (plate_to_wheel(frame_plate_v4()), plate), (arm(), app), (bar(), app), (bracket(), app)]


def picture(path: str) -> None:
  import render as R
  parts = scene()
  blue = (0.35, 0.55, 0.85)
  bed = parts_on_bed()
  views = [(parts, R.look((0.9, -0.5, 0.8), (0, 1, 0))), (parts, R.look((0.0, 0.0, 1.0), (0, 1, 0))),
           (parts, R.look((0.0, -1.0, 0.0), (0, 0, 1))),
           ([(bed["column-frame-plate-v4"], (0.8, 0.82, 0.85))], R.view_matrix(-50, 35)),
           ([(bed["right-arm"], blue)], R.view_matrix(-50, 35)), ([(bed["right-bar"], blue)], R.view_matrix(-50, 35)),
           ([(bed["right-bracket"], blue)], R.view_matrix(-50, 35))]
  R.save(path, views, cols=2, size=(1000, 650),
         titles=["on the car, from your right and below", "from your seat (the dash behind)",
                 "from below, the wheel at the top (as in your photos)", "frame plate v4, as printed",
                 "arm, as printed", "bar, as printed", "bracket, as printed"],
         suptitle="Right arm mount on the frame plate v4: the motor outside the rim at 4 o'clock, shaft pointing in. "
                  "The car grey, the plate light, the apparatus blue, the motor dark, the gear and the teeth orange. Rough.")


def plate_drawing(path: str) -> None:
  import matplotlib
  matplotlib.use("Agg")
  import matplotlib.pyplot as plt
  from matplotlib.patches import Circle, Rectangle
  fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=150)
  for r in (BLOCK, BAR, LEG):
    ax.add_patch(Rectangle((r[0], r[2]), r[1] - r[0], r[3] - r[2], fc="#cfd3d6", ec="#444", lw=1.0))
  for r in (BLOCK, BAR, LEG):
    ax.add_patch(Rectangle((r[0] + 0.5, r[2] + 0.5), r[1] - r[0] - 1.0, r[3] - r[2] - 1.0, fc="#cfd3d6", ec="none"))
  ax.add_patch(Rectangle((TUBE_X[0], TUBE_Y[0]), TUBE_X[1] - TUBE_X[0], TUBE_Y[1] - TUBE_Y[0], fc="#9aa4ad", ec="#444", lw=1.0))
  ax.add_patch(Rectangle((TUBE_X[0], BORE_Y[0]), TUBE_X[1] - TUBE_X[0], BORE_Y[1] - BORE_Y[0], fc="#e8ebee", ec="#444", lw=0.8))
  ax.add_patch(Circle((PINCH_X, TUBE_Y[1] - 4.0), 2.7, fc="white", ec="#444"))
  ax.add_patch(Rectangle((-FR.SLOT_L / 2, -FR.SLOT_W / 2), FR.SLOT_L, FR.SLOT_W, fc="white", ec="#444"))
  xc, y0, y1 = LEG_SLOT
  ax.add_patch(Rectangle((xc - FR.SLOT_W / 2, y0), FR.SLOT_W, y1 - y0, fc="white", ec="#444"))
  ax.add_patch(Circle((0, 0), 6.25, fc="none", ec="#c0392b", ls="--", lw=1.5))
  ax.text(0, -12, "cup screw", ha="center", va="top", fontsize=8, color="#c0392b")
  ax.text(xc, -44, "2nd screw", ha="center", va="top", fontsize=8, color="#c0392b")
  ax.text(-30, 44, "receiver across the car: the arm\nslides in from the key side", ha="center", va="center", fontsize=7, color="#444")
  ax.text(PINCH_X, 12, "wing bolt", ha="center", va="center", fontsize=7, color="#444")
  ax.set_aspect("equal")
  ax.set_xlim(125, -75)
  ax.set_ylim(78, -62)
  ax.set_xlabel("across the car, mm (0 = cup screw; the key side to the right)")
  ax.set_ylabel("along the column, mm (0 = cup screw; the wheel is up)")
  ax.set_title("Frame plate v4 seen from below, as in your photos: the wheel at the top, the key side on the right.\n"
               "v3 with the receiver turned across the car; 6 mm thick.", fontsize=9)
  ax.grid(True, lw=0.3, alpha=0.5)
  fig.tight_layout()
  fig.savefig(path)
  plt.close(fig)


def main():
  info = build()
  for stem, i in info.items():
    print(f"{stem}: {i['size_mm']} mm, about {i['grams_solid']} g solid")
  for n, fname, plate_name, rows, size in bambu_plates():
    print(f"{fname}.3mf ({size / 1e3:.0f} kB)")
  os.makedirs(REPORT_DIR, exist_ok=True)
  plate_drawing(os.path.join(REPORT_DIR, "column-frame-plate-v4.png"))
  picture(os.path.join(REPORT_DIR, "right-arm.png"))


if __name__ == "__main__":
  sys.exit(main())
