cp rightarm.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/rightarm_v4_backup.py && python3 - <<'EOF'
p = "rightarm.py"
s = open(p).read()
def rep(a, b):
  global s
  assert s.count(a) == 1, (a[:90], s.count(a))
  s = s.replace(a, b)

# ---- docstring ----
rep('''The right arm mount (1 Nov 2026, from your note): the motor sits OUTSIDE the steering wheel's rim on the right, at
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
''',
'''The right arm mount (1 Nov 2026, from your note; v2 2 Nov 2026): the motor sits OUTSIDE the steering wheel's rim on
the right, at about 4 o'clock, its shaft pointing in at the wheel's middle, the gear on the teeth from outside. The
plate's receiver runs across the car; an arm slides in it and sticks out to the right; from the arm's end a bar runs
back towards you to a flag; the motor bracket bolts to the flag on a pivot, so its angle can be set.

v2: the motor slides along the column on the bracket. Slid up against its stop, the gear is in the teeth: lane
keeping on. Slid down 6 mm or more, the gear is out of them: lane keeping off (the motor has power whenever the car
is on). The stop is a wing bolt, so how deep the gear sits is adjustable (+-4 mm), which v1 wasn't.

  frame plate v4  - frame plate v3 (your marks on v1) with the receiver turned to run across the car, under the
                    block, on the dash side of the cup; one wing bolt pinches the arm (unchanged in v2)
  arm             - a 10 x 30 x 100 bar across the car: slide it in or out to set how far right the motor sits
  bar             - a foot that laps the arm's end (two wing bolts, upright slots: up and down), a bar from its far
                    end towards you, and a flag at the bar's back end (a plate across the column)
  bracket         - a tab that laps the flag (one wing bolt as a pivot, one in a curved slot: the angle, +-15
                    degrees), with a sleeve standing up from it: the motor carrier's tongue slides in the sleeve; a
                    wing bolt through the sleeve's side pinches it, a wing bolt down through the sleeve's top is
                    the stop
  carrier         - the motor bolts to it (four M3, the shaft through its hole pointing in at the wheel); its tongue
                    slides in the bracket's sleeve
  gear            - the side-slide gear (you have it)
'''),
rep('''Rough numbers (until the test fit): COVER_Y, CUP_X, CUP_Z, THETA. Adjustable: the arm +-30 mm across, the bar
+-9 mm up and down, the bracket +-15 degrees.''',
'''Rough numbers (until the test fit): COVER_Y, CUP_X, CUP_Z, THETA. Adjustable: the arm +-30 mm across, the bar
+-9 mm up and down, the bracket +-15 degrees, the stop +-4 mm along the column (how deep the gear sits).''')

# ---- constants: the bar, flag, tab; the sleeve and carrier ----
rep('''# ***** the bar towards you, with its foot and its flag *****
FOOT_X = (140.0, 170.0)                  # clear of the receiver's end (X 120) with the arm pushed 20 mm in
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
''',
'''# ***** the bar towards you, with its foot and its flag *****
FOOT_X = (140.0, 186.0)                  # clear of the receiver's end (X 120) with the arm pushed 20 mm in; past the
                                         # arm's end, where the bar stands
FOOT_Z = (ARM_Z[1], ARM_Z[1] + 10.0)     # lapping the arm's face towards you
FOOT_Y = (-152.0, ARM_Y[1])              # down to the bar's and the flag's underside, so it prints standing on them
FOOT_SLOT_Y = (-137.0, -119.0)           # upright slots at ARM_HOLES_X: up and down +-9
BAR_X = (175.0, 186.0)                   # past the foot's two bolts (their wings reach x 173)
BAR_Y = (-152.0, -122.0)
FLAG_Z = (-118.0, -112.0)                # the flag across the column at the bar's back end, low enough for the motor
                                         # to slide 10 mm down off the teeth
BAR_Z = (FOOT_Z[0], FLAG_Z[0])
FLAG = (122.0, 200.0, -152.0, -98.0)     # x0, x1, y0, y1 (right of the column cover, which ends at x 97)
PIVOT = (190.0, -112.0)                  # (x, y) the pivot bolt
ARC_R, ARC_DEG = 25.0, 15.0              # the second bolt sits ARC_R towards -x of the pivot; the tab swings +-ARC_DEG

# ***** the bracket: the tab on the flag, the sleeve standing up from it *****
TAB_Z = (FLAG_Z[1], FLAG_Z[1] + 6.0)     # (-112, -106)
TAB = FLAG
NUT_DEEP = 4.5
# The sleeve and the carrier's tongue, in the motor's frame: u out from the wheel's middle (along U), v along the
# rim (along V), z along the column. The tongue is beside the motor, on the side towards 5 o'clock.
TONGUE_U = (177.5, 188.5)                # its inner face level with the carrier plate's
TONGUE_V = (-39.0, -29.2)
TONGUE_Z = (-95.0, -73.0)                # with the motor at its nominal place in the teeth
SLEEVE_CAV_U = (177.3, 188.7)
SLEEVE_CAV_V = (-39.2, -29.0)
SLEEVE_U = (174.3, 191.7)                # walls 3 mm, the -V wall 8 mm (the pinch nut)
SLEEVE_V = (-47.2, -25.8)
CAP_Z = (-67.0, -61.0)                   # the sleeve's top
WEB_U = (177.5, 182.5)                   # the web from the tongue to the carrier plate, through a slot in the +V wall
WEB_V = (-29.4, -25.5)
SLOT_U = (177.3, 182.8)
STOP_UV = (185.5, -34.0)                 # the stop bolt, down through the cap onto the tongue's top end
STOP_P = 6.0                             # it pokes this far below the cap at the nominal depth (2 to 10: +-4 mm)
PINCH_UZ = (183.0, -87.0)                # the pinch bolt, along v through the -V wall, onto the tongue
PINCH_NUT_V = -43.2                      # the middle of the -V wall: the pinch nut drops in from the top
DZ_DEEP, DZ_SHALLOW, DZ_OUT = 4.0, -4.0, -10.0   # the stop's range, and the lowest the motor slides
# The carrier plate and the skirt below it, in the motor's frame
PLATE_U = (R_FACE_OUT - FACE_T, R_FACE_OUT)
PLATE_V = (WEB_V[1], H + 0.35)
PLATE_Z = (Z_AXIS - H - 0.35, Z_AXIS + H)
SKIRT_V = (WEB_V[1], -5.0)
SKIRT_Z = (TONGUE_Z[0], PLATE_Z[0])
''')

# ---- functions: bar, bracket, carrier, motor ----
start = s.index("def bar() -> Manifold:")
end = s.index("# ----- the print bed -----")
new_funcs = '''def uvz(u0, u1, v0, v1, z0, z1) -> Manifold:
  """A box in the motor's frame (u along U, v along V), placed in the steering wheel frame."""
  return box(u0, u1, v0, v1, z0, z1).rotate((0.0, 0.0, THETA))


def uv_cyl_z(r, u, v, z0, z1, segments=32) -> Manifold:
  """A cylinder along z at (u, v) in the motor's frame."""
  x, y = rad(u, v)
  return cyl(r, z0, z1, x=x, y=y, segments=segments)


def bar() -> Manifold:
  foot = box(FOOT_X[0], FOOT_X[1], FOOT_Y[0], FOOT_Y[1], FOOT_Z[0], FOOT_Z[1])
  for x in ARM_HOLES_X:
    foot = foot - Manifold.batch_hull([Manifold.cylinder(12.0, M5_HOLE / 2, M5_HOLE / 2, 32).translate((x, y, FOOT_Z[0] - 1.0))
                                       for y in (FOOT_SLOT_Y[0] + M5_HOLE / 2, FOOT_SLOT_Y[1] - M5_HOLE / 2)])
  b = box(BAR_X[0], BAR_X[1], BAR_Y[0], BAR_Y[1], BAR_Z[0], BAR_Z[1] + 0.01)
  flag = box(FLAG[0], FLAG[1], FLAG[2], FLAG[3], FLAG_Z[0], FLAG_Z[1])
  m = foot + b + flag
  for x, y in (PIVOT, (PIVOT[0] - ARC_R, PIVOT[1])):
    m = m - Manifold.cylinder(10.0, M5_HOLE / 2, M5_HOLE / 2, 32).translate((x, y, FLAG_Z[0] - 1.0))
    m = m - hex_prism_z(M5_NUT_AF + 0.4, FLAG_Z[0] - 1.0, FLAG_Z[0] + NUT_DEEP, x=x, y=y)     # the nuts, dash side
  return clean(m)


def sleeve() -> Manifold:
  """The sleeve standing up from the tab: a tube along the column, closed at its top (the cap), with a slot up its +V
  wall for the carrier's web. The stop bolt goes down through the cap (its nut in a pocket in the cap's top), the
  pinch bolt in through the -V wall (its nut dropped into a slot from the top)."""
  z0 = TAB_Z[1] - 0.01
  m = uvz(SLEEVE_U[0], SLEEVE_U[1], SLEEVE_V[0], SLEEVE_V[1], z0, CAP_Z[1])
  m = m - uvz(SLEEVE_CAV_U[0], SLEEVE_CAV_U[1], SLEEVE_CAV_V[0], SLEEVE_CAV_V[1], TAB_Z[1], CAP_Z[0])
  m = m - uvz(SLOT_U[0], SLOT_U[1], SLEEVE_CAV_V[1] - 0.5, SLEEVE_V[1] + 0.5, TAB_Z[1], CAP_Z[0])
  su, sv = STOP_UV
  m = m - uv_cyl_z(M5_HOLE / 2, su, sv, CAP_Z[0] - 1.0, CAP_Z[1] + 1.0)
  sx, sy = rad(su, sv)
  m = m - hex_prism_z(M5_NUT_AF + 0.4, CAP_Z[1] - NUT_TRAP[1], CAP_Z[1] + 1.0, x=sx, y=sy, rot=30.0 + THETA)
  pu, pz = PINCH_UZ
  hole = cyl_y(M5_HOLE / 2, SLEEVE_V[0] - 1.0, SLEEVE_CAV_V[0] + 1.0, x=pu, z=pz, segments=32).rotate((0.0, 0.0, THETA))
  tw, tt = NUT_TRAP
  drop = uvz(pu - tw / 2, pu + tw / 2, PINCH_NUT_V - tt / 2, PINCH_NUT_V + tt / 2,
             pz - tw / 2 / math.cos(math.radians(30)), CAP_Z[1] + 1.0)
  return m - hole - drop


def bracket() -> Manifold:
  tab = box(TAB[0], TAB[1], TAB[2], TAB[3], TAB_Z[0], TAB_Z[1])
  tab = tab - Manifold.cylinder(10.0, M5_HOLE / 2, M5_HOLE / 2, 32).translate((PIVOT[0], PIVOT[1], TAB_Z[0] - 1.0))
  arc = [Manifold.cylinder(10.0, M5_HOLE / 2, M5_HOLE / 2, 32).translate(
    (PIVOT[0] - ARC_R * math.cos(math.radians(a)), PIVOT[1] + ARC_R * math.sin(math.radians(a)), TAB_Z[0] - 1.0))
    for a in np.linspace(-ARC_DEG, ARC_DEG, 13)]
  tab = tab - union([Manifold.batch_hull([arc[i], arc[i + 1]]) for i in range(len(arc) - 1)])
  return clean(tab + sleeve())


def carrier(dz: float = 0.0) -> Manifold:
  """The motor's carrier: the plate the motor bolts to (perpendicular to U, the motor's face against its outside),
  a skirt below it, and the tongue that slides in the bracket's sleeve, joined to them by a web through the sleeve's
  slot. dz: how far it is slid along the column from the nominal depth (+ towards you, deeper into the teeth)."""
  r0, r1 = PLATE_U
  m = uvz(r0, r1, PLATE_V[0], PLATE_V[1], PLATE_Z[0], PLATE_Z[1])
  m = m + uvz(r0, r1, SKIRT_V[0], SKIRT_V[1], SKIRT_Z[0], SKIRT_Z[1] + 0.01)
  m = m + uvz(WEB_U[0], WEB_U[1], WEB_V[0], WEB_V[1] + 0.01, TONGUE_Z[0], TONGUE_Z[1])
  m = m + uvz(TONGUE_U[0], TONGUE_U[1], TONGUE_V[0], TONGUE_V[1] + 0.01, TONGUE_Z[0], TONGUE_Z[1])
  holes = [cyl_x(BOSS_HOLE / 2, r0 - 1.0, r1 + 1.0, y=0.0, z=Z_AXIS, segments=64)]
  for b in (-NEMA_HOLES / 2, NEMA_HOLES / 2):
    for c in (-NEMA_HOLES / 2, NEMA_HOLES / 2):
      holes.append(cyl_x(1.7, r0 - 1.0, r1 + 1.0, y=b, z=Z_AXIS + c, segments=24))
  m = m - union(holes).rotate((0.0, 0.0, THETA))
  return clean(m).translate((0.0, 0.0, dz))


def motor_and_gear(dz: float = 0.0) -> dict:
  """The motor's body, board and the side-slide gear: carrier frame (z out along the shaft from the face) -> here
  the shaft points in: carrier z -> -U, carrier y -> V, carrier x -> along the column. dz as for carrier()."""
  motor = box(-H, H, -H, H, -NEMA_LEN, 0.0) + cyl(11.0, 0.0, 2.0)
  board = box(-23.0, 23.0, -23.0, 23.0, -NEMA_LEN - 11.0, -NEMA_LEN)
  c = R_FACE_OUT * U
  mat = [[0.0, V[0], -U[0], float(c[0])], [0.0, V[1], -U[1], float(c[1])], [1.0, 0.0, 0.0, Z_AXIS + dz]]
  return {"motor": motor.transform(mat), "board": board.transform(mat), "gear": S.side_gear().transform(mat)}


'''
s = s[:start] + new_funcs + s[end:]

rep('''def parts_on_bed() -> dict:
  """The plate labels up (the receiver standing on it); the arm on its side; the bar lying on its underside (the
  flag standing); the bracket on its tab (the face plate standing)."""
  return {"column-frame-plate-v4": on_bed(frame_plate_v4()),
          "right-arm": on_bed(arm()),                              # flat: 10 thick along the column
          "right-bar": on_bed(bar(), rotate=(90.0, 0.0, 0.0)),     # its underside (y) down: the flag stands
          "right-bracket": on_bed(bracket())}                       # the tab down, the face plate standing''',
'''def parts_on_bed() -> dict:
  """The plate labels up (the receiver standing on it); the arm on its side; the bar standing on its underside (the
  foot, the bar and the flag all start at y -152); the bracket on its tab (the sleeve standing, its top bridged); the
  carrier on its inside face (the face towards the wheel's middle)."""
  car = carrier().rotate((0.0, 0.0, -THETA))           # u along x: its inside face (u 177.5) is now x = 177.5
  return {"column-frame-plate-v4": on_bed(frame_plate_v4()),
          "right-arm": on_bed(arm()),                              # flat: 10 thick along the column
          "right-bar": on_bed(bar(), rotate=(90.0, 0.0, 0.0)),     # its underside (y) down: foot, bar and flag stand
          "right-bracket": on_bed(bracket()),                       # the tab down, the sleeve standing
          "right-carrier": on_bed(car, rotate=(0.0, 90.0, 0.0))}    # x -> -z: the inside face down''')
open(p, "w").write(s)
print("ok")
EOF
grep -n "right-bracket\|bambu_plates\|def picture\|def scene\|def plate_drawing\|def main" rightarm.py