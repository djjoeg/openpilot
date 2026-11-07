"""
The right arm mount (1 Nov 2026, from your note; v3 2 Nov 2026): the motor sits OUTSIDE the steering wheel's rim on
the right, at about 4 o'clock, its shaft pointing in at the wheel's middle, the gear on the teeth from outside.

v3 is two printed pieces and two slides:

  frame plate v4  - unchanged: on the column cover's two screws; the receiver under it runs across the car, one wing
                    bolt pinches the arm in it
  arm             - a 10 x 30 bar across the car (slide it in or out of the receiver: how far right the motor sits),
                    with a tower at its end: a channel along the column, open on the side towards the motor
  motor carrier   - the motor bolts to its plate (four M3, the shaft through the big hole pointing in at the wheel's
                    middle); its bar slides along the column in the tower's channel. A wing bolt through the tower's
                    outer wall pushes the bar tight. A wing bolt up through the lug at the bar's bottom end is the stop,
                    locked with a jam nut: slid up against it, the gear is in the teeth (lane keeping on); slid 6 mm or
                    more down the column, out of them (off; the motor has power whenever the car is on)
  gear            - the side-slide gear (you have it)

v2 (a foot, a bar, a flag and a bracket, for up and down and the angle) is gone: too many joints, and its motor
carrier could not have been put into the bracket's sleeve, which was closed at both ends.

Steering wheel frame (mm): z along the column towards you, 0 at the middle of the grip; y up; x to your right.
THETA is where the gear meets the teeth, degrees from 3 o'clock (-30 is 4 o'clock); R_FACE_OUT the motor's face
from the wheel's middle (the gear's teeth reach in to the same radius as before, 160.5 to 173).

Rough numbers (until the test fit): COVER_Y, CUP_X, CUP_Z, THETA. Adjustable: the arm +-25 mm across (in by 25 the
tower meets the receiver's end), the stop +-4 mm along the column (how deep the gear sits). Not adjustable: up and
down, and the angle; where the gear sits along the teeth is set by the arm across and by the gear's place on its
shaft.

  python3 rightarm.py   # writes ../stl/right-arm/*.stl, ../plates/plate-11-frame-plate-v4.3mf, plate-12-right-arm.3mf
                        # and ../report/right-arm.png, column-frame-plate-v4.png
"""
import math
import os
import sys

import numpy as np
from manifold3d import Manifold

import armmount as AM
import frameplate as FR
import sideparts as S
from cadlib import (
  box,
  clean,
  cyl,
  cyl_x,
  cyl_y,
  hex_prism_z,
  on_bed,
  union,
  write_stl,
)
from params import NEMA, NEMA_LEN

HERE = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(HERE, "..", "stl", "right-arm")
REPORT_DIR = os.path.join(HERE, "..", "report")

# ***** the car (rough) *****
COVER_Y, CUP_X, CUP_Z = AM.COVER_Y, AM.CUP_X, AM.CUP_Z       # -107, 73, -145

# ***** the motor: outside the rim, shaft pointing in *****
THETA = -30.0                    # where the gear meets the teeth: 4 o'clock (your note: the column's underside height
                                 # would be -40; a tangent 20 degrees off upright would be -20)
R_FACE_OUT = 182.5               # the motor's face from the wheel's middle: the face plate (5 mm, just inside it) clears the
                                 # teeth piece's outer band (radius 177); the gear's teeth then reach in to radius 163
Z_AXIS = S.PP.Z_AXIS_P           # -59.5: the motor's axis, along the column (as the side-slide mount)
U = np.array([math.cos(math.radians(THETA)), math.sin(math.radians(THETA))])      # out from the wheel's middle
V = np.array([-math.sin(math.radians(THETA)), math.cos(math.radians(THETA))])     # along the rim, anticlockwise
H = NEMA / 2
FACE_T = 5.0
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
TUBE_X = (-47.0, 3.0)                    # along the plate: 50 long, from just short of the cup's washer out to the key side
TUBE_FLOOR_T = 5.0
PINCH_X = -30.0                          # the wing bolt, through the dash-side wall

# ***** the arm (steering wheel frame): across, in the receiver *****
ARM_Z = (CUP_Z - BORE_Y[1] + 0.2, CUP_Z - BORE_Y[0] - 0.2)      # (-175.2, -165.2)
ARM_Y = (COVER_Y - PLATE_T - 30.0, COVER_Y - PLATE_T)          # (-143, -113)
ARM_X = (CUP_X - TUBE_X[1] + 3.0, 150.0)                       # (73, 150): 47 in the receiver, nominal

# ***** the tower at the arm's end and the motor carrier, in the motor's frame: u out from the wheel's middle (along
# U), v along the rim (along V), z along the column *****
BAR_U, BAR_V = (205.0, 221.0), (-39.0, -23.0)    # the carrier's bar, 16 x 16, beside the motor on its 5 o'clock side
CH_U, CH_V0 = (204.75, 221.25), -39.25           # the tower's channel round it, open towards the motor (+v)
TOWER_U, TOWER_V = (194.75, 231.25), (-47.25, -24.0)   # the inner wall 10 (the stop lands on it), the outer wall 10
                                                 # (the push bolt's nut), the back 8; the walls end 1 mm short of the
                                                 # bar's face, clear of the motor's board
TOWER_Z = (ARM_Z[0], -94.0)
PUSH_VZ = (-31.0, -104.0)        # the push wing bolt: along -u through the outer wall, onto the bar
PUSH_NUT_U = (222.85, 227.25)    # its nut, dropped into a slot from the tower's top (skins 1.6 inside, 4 outside)
STOP_UV = (199.5, -31.0)         # the stop wing bolt: up through the lug, onto the inner wall's underside
STOP_P = 5.5                     # it pokes this far above the lug at the nominal depth (1.5 to 9.5: +-4 mm)
LUG_U, LUG_T = (192.5, 205.0), 6.0
DZ_DEEP, DZ_SHALLOW = 4.0, -4.0  # the stop's range
DZ_OUT = -10.0                   # slid out (6 mm is enough)
# the carrier's plate (the motor's face against its outside), the web joining it to the bar, the bar's length
PLATE_U = (R_FACE_OUT - FACE_T, R_FACE_OUT)
PLATE_V = (BAR_V[0], H + 0.35)
PLATE_Z = (Z_AXIS - H - 0.35, Z_AXIS + H)
BAR_Z = (TOWER_Z[0] - STOP_P - LUG_T, PLATE_Z[1])      # (-186.7, -38.35) at the nominal depth
DZ_END = PLATE_Z[0] - TOWER_Z[1]                        # -13: slid out this far, the web sits on the tower's top
PAD_R, PAD_T = 3.5, 1.0          # pads round the four M3 holes on the plate's inside: the motor's holes are 4.5 deep
                                 # (STEPPERONLINE's drawing for this motor family), so an M3 x 10 goes 4 into them


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


# ----- the arm and the motor carrier (steering wheel frame) -----

def uvz(u0, u1, v0, v1, z0, z1) -> Manifold:
  """A box in the motor's frame (u along U, v along V), placed in the steering wheel frame."""
  return box(u0, u1, v0, v1, z0, z1).rotate((0.0, 0.0, THETA))


def uv_cyl_z(r, u, v, z0, z1, segments=32) -> Manifold:
  """A cylinder along z at (u, v) in the motor's frame."""
  x, y = rad(u, v)
  return cyl(r, z0, z1, x=x, y=y, segments=segments)


def teardrop_x(r: float, x0: float, x1: float, y: float, z: float, flat: float = 2.0) -> Manifold:
  """A hole along x that prints without support with +y up: a circle with a 45 degree roof, cut flat `flat` above
  the circle."""
  c = cyl_x(r, x0, x1, y=y, z=z, segments=64)
  tip = cyl_x(0.01, x0, x1, y=y + r * math.sqrt(2.0), z=z, segments=8)
  return Manifold.batch_hull([c, tip]) ^ box(x0 - 1.0, x1 + 1.0, y - r - 1.0, y + r + flat, z - r - 1.0, z + r + 1.0)


def arm() -> Manifold:
  """The arm and the tower at its end, one piece (printed flat, the tower standing up): the arm runs into the
  tower's foot (the hull of the arm's end and the tower, as thick as the arm); the channel up the tower is open
  towards the motor; the push bolt goes in through the outer wall, its nut dropped into the slot from the top."""
  a = box(ARM_X[0], ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1])
  foot = Manifold.batch_hull([box(ARM_X[1] - 5.0, ARM_X[1], ARM_Y[0], ARM_Y[1], ARM_Z[0], ARM_Z[1]),
                              uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], ARM_Z[0], ARM_Z[1])])
  tower = uvz(TOWER_U[0], TOWER_U[1], TOWER_V[0], TOWER_V[1], TOWER_Z[0], TOWER_Z[1])
  m = a + foot + tower
  m = m - uvz(CH_U[0], CH_U[1], CH_V0, CH_V0 + 80.0, TOWER_Z[0] - 1.0, TOWER_Z[1] + 1.0)
  pv, pz = PUSH_VZ
  hole = cyl_x(M5_HOLE / 2, CH_U[1] - 1.0, TOWER_U[1] + 1.0, y=pv, z=pz, segments=32).rotate((0.0, 0.0, THETA))
  tw, tt = NUT_TRAP
  slot = uvz(PUSH_NUT_U[0], PUSH_NUT_U[1], pv - tw / 2, pv + tw / 2, pz - tw / 2 / math.cos(math.radians(30)),
             TOWER_Z[1] + 1.0)
  return clean(m - hole - slot)


def carrier(dz: float = 0.0) -> Manifold:
  """The motor carrier, one piece (printed on its side towards 5 o'clock): the bar that slides in the tower's
  channel; the lug at its bottom end (the stop bolt up through it, its nut in the pocket on top); at its top the web
  and the plate the motor bolts to (perpendicular to U, the motor's face against its outside; pads round the four
  M3 holes inside; the big hole a teardrop so it prints). dz: slid along the column from the nominal depth
  (+ towards you, deeper into the teeth)."""
  lug_top = TOWER_Z[0] - STOP_P
  m = uvz(BAR_U[0], BAR_U[1], BAR_V[0], BAR_V[1], BAR_Z[0], BAR_Z[1])
  m = m + uvz(PLATE_U[0], BAR_U[0] + 0.01, BAR_V[0], BAR_V[1], PLATE_Z[0], PLATE_Z[1])           # the web
  m = m + uvz(PLATE_U[0], PLATE_U[1], PLATE_V[0], PLATE_V[1], PLATE_Z[0], PLATE_Z[1])            # the plate
  m = m + uvz(LUG_U[0], LUG_U[1] + 0.01, BAR_V[0], BAR_V[1], lug_top - LUG_T, lug_top)           # the lug
  r0, r1 = PLATE_U
  corners = [(b, c) for b in (-NEMA_HOLES / 2, NEMA_HOLES / 2) for c in (-NEMA_HOLES / 2, NEMA_HOLES / 2)]
  pads = [cyl_x(PAD_R, r0 - PAD_T, r0 + 0.01, y=b, z=Z_AXIS + c, segments=32) for b, c in corners]
  m = m + union(pads).rotate((0.0, 0.0, THETA))
  holes = [teardrop_x(BOSS_HOLE / 2, r0 - 1.0, r1 + 1.0, y=0.0, z=Z_AXIS)]
  holes += [cyl_x(1.7, r0 - PAD_T - 1.0, r1 + 1.0, y=b, z=Z_AXIS + c, segments=24) for b, c in corners]
  m = m - union(holes).rotate((0.0, 0.0, THETA))
  su, sv = STOP_UV
  sx, sy = rad(su, sv)
  m = m - uv_cyl_z(M5_HOLE / 2, su, sv, lug_top - LUG_T - 1.0, lug_top + 1.0)
  m = m - hex_prism_z(NUT_TRAP[0], lug_top - NUT_TRAP[1], lug_top + 1.0, x=sx, y=sy, rot=30.0 + THETA)
  return clean(m).translate((0.0, 0.0, dz))


def motor_and_gear(dz: float = 0.0) -> dict:
  """The motor's body, board and the side-slide gear: carrier frame (z out along the shaft from the face) -> here
  the shaft points in: carrier z -> -U, carrier y -> V, carrier x -> along the column. dz as for carrier()."""
  motor = box(-H, H, -H, H, -NEMA_LEN, 0.0) + cyl(11.0, 0.0, 2.0)
  board = box(-23.0, 23.0, -23.0, 23.0, -NEMA_LEN - 11.0, -NEMA_LEN)
  c = R_FACE_OUT * U
  mat = [[0.0, V[0], -U[0], float(c[0])], [0.0, V[1], -U[1], float(c[1])], [1.0, 0.0, 0.0, Z_AXIS + dz]]
  return {"motor": motor.transform(mat), "board": board.transform(mat), "gear": S.side_gear().transform(mat)}


# ----- the print bed -----

def parts_on_bed() -> dict:
  """The plate labels up (the receiver standing on it); the arm flat, the tower standing up (the channel open on
  one side, its top flat); the carrier on its side towards 5 o'clock (the bar, the web, the lug and the plate's edge
  all start at v -39), the plate standing up from it."""
  car = carrier().rotate((0.0, 0.0, -THETA))           # into the motor's frame: u along x, v along y
  return {"column-frame-plate-v4": on_bed(frame_plate_v4()),
          "right-arm": on_bed(arm()),
          "right-carrier": on_bed(car, rotate=(90.0, 0.0, 0.0))}   # y -> z: v -39 down, the teardrop's roof up


def build(out_dir: str = STL_DIR) -> dict:
  os.makedirs(out_dir, exist_ok=True)
  info = {}
  for stem, m in parts_on_bed().items():
    write_stl(m, os.path.join(out_dir, stem + ".stl"), stem)
    bb = m.bounding_box()
    info[stem] = {"size_mm": [round(bb[i + 3] - bb[i], 1) for i in range(3)], "grams_solid": round(m.volume() / 1000 * 1.28)}
  for stale in ("right-bar", "right-bracket"):          # v2's pieces
    p = os.path.join(out_dir, stale + ".stl")
    if os.path.exists(p):
      os.remove(p)
  return info


def bambu_plates() -> list:
  import plates as P
  out = []
  parts = {"column-frame-plate-v4": ("frame plate v4", 1, P.STANDARD)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-11-frame-plate-v4", "11 frame plate v4", list(parts), "Plate 11: the frame plate v4 (the receiver across)")])
  parts = {"right-arm": ("arm", 1, P.SOLID), "right-carrier": ("motor carrier", 1, P.SOLID)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-12-right-arm", "12 right arm v3", list(parts),
                              "Plate 12: the right arm mount v3: the arm (with its tower) and the motor carrier")])
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
  car, plate, app, green, dark, orange = (0.55, 0.55, 0.58), (0.80, 0.82, 0.85), (0.35, 0.55, 0.85), (0.45, 0.70, 0.45), \
    (0.25, 0.25, 0.28), (0.95, 0.65, 0.3)
  return [(sc.column_cover(back=130.0), car), (grip, car), (teeth, orange), (mg["gear"], orange), (mg["motor"], dark),
          (mg["board"], dark), (plate_to_wheel(frame_plate_v4()), plate), (arm(), app), (carrier(), green)]


def picture(path: str) -> None:
  import render as R
  parts = scene()
  bed = parts_on_bed()
  views = [(parts, R.look((0.9, -0.5, 0.8), (0, 1, 0))), (parts, R.look((0.0, 0.0, 1.0), (0, 1, 0))),
           (parts, R.look((0.0, -1.0, 0.0), (0, 0, 1))),
           ([(bed["column-frame-plate-v4"], (0.8, 0.82, 0.85))], R.view_matrix(-50, 35)),
           ([(bed["right-arm"], (0.35, 0.55, 0.85))], R.view_matrix(-50, 35)),
           ([(bed["right-carrier"], (0.45, 0.70, 0.45))], R.view_matrix(-50, 35))]
  R.save(path, views, cols=2, size=(1000, 650),
         titles=["on the car, from your right and below", "from your seat (the dash behind)",
                 "from below, the wheel at the top (as in your photos)", "frame plate v4, as printed",
                 "arm, as printed", "motor carrier, as printed"],
         suptitle="Right arm mount v3 on the frame plate v4: the motor outside the rim at 4 o'clock, shaft pointing in. "
                  "The car grey, the plate light, the arm blue, the motor carrier green, the motor dark, the gear and the "
                  "teeth orange. Rough.")


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
