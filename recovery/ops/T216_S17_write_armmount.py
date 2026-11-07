"""
The arm mount, v1 (31 Oct 2026): the simple, adjustable apparatus that hangs on the frame plate under the column.
The frame plate stays on the car; the apparatus comes off with four wing nuts.

  frame plate v2  - the frame plate (frameplate.py) with the block round the cup screw 7 mm thick and four M5 hex bolts
                    trapped in it, heads in hex pockets on the cover side, pointing down
  shoe            - a flat plate under the block, on those four bolts (wing nuts under it); a pocket in its top clears
                    the cup screw's head and washer; a fin hangs from its outer edge, along the column, with two slots
  arm             - a flat bar, 10 x 30, along the column, bolted to the fin's inner face through the fin's slots:
                    slide it along the column to set how deep the gear sits in the teeth. Its top edge rides on the
                    shoe's underside, so it stays parallel to the plate. Its back end has two upright slots
  bracket         - the motor bolts to its face plate (four M3, the boss through a hole); from the face plate's
                    4 o'clock end an upright ear rises, bolted to the arm's upright slots by two wing bolts into nuts
                    trapped in the ear: slide it up or down to set the gear's reach along the teeth. A rib on the ear
                    sits against the arm's end face, so the ear stays upright
  gear            - the side-slide gear (you have it)

The motor is at 5:20 behind the wheel, its shaft pointing out at the grip, the gear on the teeth: the side-slide
mount's place (sideparts.py), with its face at R_FACE from the column's axis, on the plane Z_AXIS.

Steering wheel frame (mm): z along the column towards you, 0 at the middle of the grip; y up; x to your right.
The frame plate: its top (the cover's underside) at COVER_Y, the cup screw at (CUP_X, CUP_Z); its own frame
(frameplate.py: x towards the driver's door, y towards the dash) maps as X = CUP_X - x, Z = CUP_Z - y.

Rough numbers (until the test fit): COVER_Y, CUP_X, CUP_Z, and the cover's front edge. The slots take +-17 mm along
the column and +-9 mm up and down.

  python3 armmount.py   # writes ../stl/arm-mount/*.stl, ../plates/plate-5-frame-plate-v2.3mf, plate-6-arm-mount.3mf
                        # and ../report/arm-mount.png
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

# ***** the frame plate v2 *****
T_PLATE = FR.T                   # 4
BLOCK_T = 7.0                    # the block round the cup: thicker, for the bolt heads' pockets
BOLTS_P = ((0.0, 20.0), (24.0, 20.0), (0.0, 42.0), (24.0, 42.0))   # (x, y) in the plate's frame: clear of the cup slot
                                                                    # and its washer, inboard of the fin
M5_HOLE = 5.4
HEX_AF, HEX_DEEP = 8.4, 3.8      # M5 hex head (DIN 933: 8 across flats, 3.5 tall)
M5_NUT_AF, M5_NUT_T = 8.0, 4.0

# ***** the shoe *****
SHOE_X = (45.0, 108.0)
SHOE_Z = (-195.0, -131.0)
SHOE_T = 8.0
SHOE_Y = (COVER_Y - BLOCK_T - SHOE_T, COVER_Y - BLOCK_T)    # (-122, -114)
POCKET = ((53.0, 93.0), (-155.0, -135.0), 4.0)               # x, z, deep: the cup screw's head and washer
FIN_X = (96.0, 106.0)
FIN_Y = (-152.0, SHOE_Y[0])
FIN_Z = (-175.0, SHOE_Z[1])
FIN_SLOT_Y = (-130.0, -144.0)
FIN_SLOT_Z = (-170.0, -136.0)

# ***** the arm *****
ARM_X = (86.0, 96.0)
ARM_Y = (-152.0, SHOE_Y[0])      # its top edge on the shoe's underside
ARM_Z = (-175.0, -55.0)
ARM_HOLES_Z = -153.0             # the two holes to the fin (at FIN_SLOT_Y), nominal: the middle of the fin's slots
ARM_SLOT_Z = (-75.0, -60.0)      # the two upright slots at the back
ARM_SLOT_Y = (-146.0, -128.0)

# ***** the bracket *****
EAR_X = (78.0, 86.0)             # the upright ear, inboard of the arm (the motor's face corner reaches x 72.2, the gear 73.3)
EAR_Y = (-152.0, -108.0)
EAR_Z = (-85.0, -40.0)
EAR_HOLES = ((-137.0, -75.0), (-137.0, -60.0))    # (y, z): nominal, the middle of the arm's slots
NUT_DEEP = 4.5                   # the nuts' pockets in the ear's inner face
RIB = ((ARM_X[0], ARM_X[1]), (ARM_Z[1], ARM_Z[1] + 5.0))     # the rib on the ear's outer face, against the arm's end
FACE_T = 5.0
FACE_V = (-H, 32.0)              # the face plate across (towards 4 o'clock), out to the ear
BOSS_HOLE = 22.5
NEMA_HOLES = 31.0


def plate_to_wheel(m: Manifold) -> Manifold:
  """frameplate's printed (mirrored) frame -> steering wheel frame: x_m + CUP_X, z_t -> y, y -> -z."""
  return m.rotate((-90.0, 0.0, 0.0)).translate((CUP_X, COVER_Y - T_PLATE, CUP_Z))


def bolt_xz():
  """The four bolts in the steering wheel frame (x, z)."""
  return [(CUP_X - x, CUP_Z - y) for x, y in BOLTS_P]


# ----- the frame plate v2 (printed frame, as frameplate.py: key side +x, labels up) -----

def frame_plate_v2() -> Manifold:
  T = T_PLATE
  body = FR.rbox(FR.RIGHT) + FR.rbox(FR.FRONT) + FR.rbox(FR.STRIP)
  body = body - FR.slot(FR.CUP[0], FR.CUP[1], FR.SLOT_L, FR.SLOT_W, "x")
  for xc in FR.STRIP_COLS:
    for y0, y1 in FR.STRIP_SLOTS:
      body = body - FR.slot(xc, (y0 + y1) / 2, y1 - y0, FR.SLOT_W, "y")
  body = body.mirror((1.0, 0.0, 0.0))
  x0, x1, y0, y1 = FR.RIGHT
  block = box(-x1, -x0, y0, y1, 0.0, BLOCK_T)          # the block, mirrored: key side +x
  body = body + block
  for x, y in BOLTS_P:
    xm = -x
    body = body - cyl(M5_HOLE / 2, -1.0, BLOCK_T + 1.0, x=xm, y=y, segments=32)
    body = body - hex_prism_z(HEX_AF, -1.0, HEX_DEEP, x=xm, y=y)       # open on the cover side (the print bed)
  labels = []
  for k, xc in enumerate(FR.STRIP_COLS, start=1):
    s = str(k)
    labels.append(FR.text(s, -xc - FR.text_width(s, 0.9) / 2, FR.STRIP[3] - 5.0, T, pix=0.9))
  labels.append(FR.text("KEY >", -x0 - FR.text_width("KEY >") - 2.0, y1 - 8.0, BLOCK_T))
  labels.append(FR.text("WHEEL", -8.0, y0 + 3.0, BLOCK_T, pix=0.9))
  return clean(body + union(labels))


# ----- the shoe, the arm and the bracket (steering wheel frame) -----

def shoe() -> Manifold:
  m = box(SHOE_X[0], SHOE_X[1], SHOE_Y[0], SHOE_Y[1], SHOE_Z[0], SHOE_Z[1])
  (px0, px1), (pz0, pz1), pd = POCKET
  m = m - box(px0, px1, SHOE_Y[1] - pd, SHOE_Y[1] + 1.0, pz0, pz1)
  for x, z in bolt_xz():
    m = m - cyl_y(M5_HOLE / 2, SHOE_Y[0] - 1.0, SHOE_Y[1] + 1.0, x=x, z=z, segments=32)
  fin = box(FIN_X[0], FIN_X[1], FIN_Y[0], FIN_Y[1] + 0.01, FIN_Z[0], FIN_Z[1])
  for y in FIN_SLOT_Y:
    fin = fin - Manifold.batch_hull([cyl_x(M5_HOLE / 2, FIN_X[0] - 1.0, FIN_X[1] + 1.0, y=y, z=FIN_SLOT_Z[0] + M5_HOLE / 2, segments=32),
                                     cyl_x(M5_HOLE / 2, FIN_X[0] - 1.0, FIN_X[1] + 1.0, y=y, z=FIN_SLOT_Z[1] - M5_HOLE / 2, segments=32)])
  return clean(m + fin)


def arm() -> Manifold:
  m = box(ARM_X[0], ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1])
  for y in FIN_SLOT_Y:
    m = m - cyl_x(M5_HOLE / 2, ARM_X[0] - 1.0, ARM_X[1] + 1.0, y=y, z=ARM_HOLES_Z, segments=32)
  for z in ARM_SLOT_Z:
    m = m - Manifold.batch_hull([cyl_x(M5_HOLE / 2, ARM_X[0] - 1.0, ARM_X[1] + 1.0, y=ARM_SLOT_Y[0] + M5_HOLE / 2, z=z, segments=32),
                                 cyl_x(M5_HOLE / 2, ARM_X[0] - 1.0, ARM_X[1] + 1.0, y=ARM_SLOT_Y[1] - M5_HOLE / 2, z=z, segments=32)])
  return clean(m)


def face_plate_local() -> Manifold:
  """The face plate in a local frame: a along the shaft (out), b across towards 4 o'clock, c along the column."""
  m = box(R_FACE, R_FACE + FACE_T, FACE_V[0], FACE_V[1], -H, H)
  m = m - cyl_x(BOSS_HOLE / 2, R_FACE - 1.0, R_FACE + FACE_T + 1.0, y=0.0, z=0.0, segments=64)
  for b in (-NEMA_HOLES / 2, NEMA_HOLES / 2):
    for c in (-NEMA_HOLES / 2, NEMA_HOLES / 2):
      m = m - cyl_x(1.7, R_FACE - 1.0, R_FACE + FACE_T + 1.0, y=b, z=c, segments=24)
  return m


def local_to_wheel(m: Manifold) -> Manifold:
  """local (a out along the shaft, b across, c along the column) -> steering wheel frame."""
  return m.rotate((0.0, 0.0, MOUNT_DEG)).translate((0.0, 0.0, Z_AXIS))


def bracket() -> Manifold:
  face = local_to_wheel(face_plate_local())
  ear = box(EAR_X[0], EAR_X[1], EAR_Y[0], EAR_Y[1], EAR_Z[0], EAR_Z[1])
  rib = box(RIB[0][0], RIB[0][1], EAR_Y[0], EAR_Y[1], RIB[1][0], RIB[1][1])
  m = face + ear + rib
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
  """Each part turned the way it prints: the plate labels up; the shoe on its top (the fin up); the arm on its side;
  the bracket on its face plate's front (the ear rising from it, 20 degrees off upright)."""
  br = bracket().rotate((0.0, 0.0, -MOUNT_DEG))         # the shaft now along +x: the face plate's front is its +x face
  br = on_bed(br, rotate=(0.0, 90.0, 0.0))              # +x -> -z: the front face down
  return {"column-frame-plate-v2": on_bed(frame_plate_v2()),
          "arm-shoe": on_bed(shoe(), rotate=(180.0, 0.0, 0.0)),
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
  parts = {"column-frame-plate-v2": ("frame plate v2", 1, P.STANDARD)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-5-frame-plate-v2", "5 frame plate v2", list(parts), "Plate 5: the frame plate v2 (bolts trapped in it)")])
  parts = {"arm-shoe": ("shoe", 1, P.STANDARD), "arm-bar": ("arm", 1, P.SOLID), "arm-bracket": ("bracket", 1, P.SOLID)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-6-arm-mount", "6 arm mount", list(parts), "Plate 6: the arm mount: shoe, arm, bracket")])
  return out


# ----- the picture -----

def scene() -> list:
  """(manifold, colour) pairs in the steering wheel frame: the car (grey), the plate (light), the apparatus (blue), the
  motor (dark), the gear and the teeth (orange)."""
  import carscene as CS
  import midteeth as MT
  from cadlib import revolve
  sc = CS.CarScene(D=125.0)
  grip_r = S.FP.GRIP / 2.0 if hasattr(S.FP, "GRIP") else 16.5
  rr = S.FP.WHEEL_OD / 2.0 - grip_r if hasattr(S.FP, "WHEEL_OD") else 168.3
  circle = [(rr + grip_r * math.cos(math.radians(a)), grip_r * math.sin(math.radians(a))) for a in range(0, 360, 10)]
  grip = revolve(circle, -180.0, 180.0, step_deg=2.0)
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=10)).rotate((0.0, 0.0, MOUNT_DEG))
  mg = motor_and_gear()
  car, plate, app, dark, orange = (0.55, 0.55, 0.58), (0.80, 0.82, 0.85), (0.35, 0.55, 0.85), (0.25, 0.25, 0.28), (0.95, 0.65, 0.3)
  return [(sc.column_cover(), car), (grip, car), (teeth, orange), (mg["gear"], orange), (mg["motor"], dark), (mg["board"], dark),
          (plate_to_wheel(frame_plate_v2()), plate), (shoe(), app), (arm(), app), (bracket(), app)]


def picture(path: str) -> None:
  import render as R
  parts = scene()
  views = [(parts, R.look((0.9, -0.6, 0.8), (0, 1, 0))), (parts, R.look((1.0, -0.15, 0.1), (0, 1, 0))),
           (parts, R.look((0.0, -1.0, 0.0), (0, 0, -1)))]
  R.save(path, views, titles=["from your right, below", "from the right side (the wheel to the right)", "from below"],
         suptitle="Arm mount v1 on the frame plate, under the column: the car grey, the plate light, the apparatus blue, "
                  "the motor dark, the gear and the teeth orange. Rough: the car is the photo model.", size=(900, 700))


def main():
  info = build()
  for stem, i in info.items():
    print(f"{stem}: {i['size_mm']} mm, about {i['grams_solid']} g solid")
  for n, fname, plate_name, rows, size in bambu_plates():
    print(f"{fname}.3mf ({size / 1e3:.0f} kB)")
  os.makedirs(REPORT_DIR, exist_ok=True)
  picture(os.path.join(REPORT_DIR, "arm-mount.png"))


if __name__ == "__main__":
  sys.exit(main())
