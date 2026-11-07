python3 - <<'EOF'
p = "mountparts.py"
s = open(p).read()
start = s.index("TOP_Y = (NEMA / 2 + 0.5, NEMA / 2 + 8.5)")
end = s.index("def motor_carrier() -> Manifold:")
new = '''TOP_Y = (NEMA / 2 + 0.5, NEMA / 2 + 8.5)      # block over the motor (y range): its top face is TOP_Y[1]
SIDE_X = (NEMA / 2 + 0.5, NEMA / 2 + 3.4)     # walls beside the motor's upper half (x range each side)
BLOCK_BACK = -46.0                    # the block and walls reach back over the motor body this far (motor is 48 long)
HINGE = (TOP_Y[1] + 7.0, -40.0)       # carrier hinge axis (y, z)
HINGE_R = 7.5
CARRIER_KNUCKLE = 15.0                # carrier's knuckle spans x +-this
BLOCK_KNUCKLE = (CARRIER_KNUCKLE + GAP, CARRIER_KNUCKLE + GAP + 7.0)   # hinge block's knuckles, x range each side
TAIL_Z = (-60.0, -47.0)               # tail behind the hinge: the lift lever's cam and the power switch sit over it
TAIL_X = 18.0                         # tail spans x +-this
SPRING_Z = -6.0                       # spring post on the carrier's top, in front of the hinge
SPRING_POST_R = 2.3                   # for a compression spring 5 mm or more inside diameter
SETUP_GAP = 12.0                      # carrier top to hinge block underside with the motor gear on the teeth
LIFT_DEG = 10.0                       # the lift lever turns the carrier up this much (motor gear about 11 mm up)
DROP_DEG = 7.0                        # with the steering wheel turned past the teeth the carrier drops this much,
                                      # until its tail meets the lift lever's cam


'''
s = s[:start] + new + s[end:]
old = '''  tail = box(-CARRIER_KNUCKLE, CARRIER_KNUCKLE, TOP_Y[0], TOP_Y[1], TAIL_Z[0], BLOCK_BACK + 0.01)'''
new = '''  tail = box(-TAIL_X, TAIL_X, TOP_Y[0], TOP_Y[1], TAIL_Z[0], BLOCK_BACK + 0.01)'''
assert old in s; s = s.replace(old, new)

start = s.index("# ***** hinge block *****")
end = s.index("# ***** arm slider *****")
new = '''# ***** hinge block *****

HB_BOTTOM = TOP_Y[1] + SETUP_GAP      # hinge block underside
HB_T = 9.0
HB_Z = (-70.0, 4.0)
HB_HALF = BLOCK_KNUCKLE[1]
EAR_X = (HB_HALF + GAP, HB_HALF + GAP + 6.0)    # ears for the angle joint, outside the block
PIVOT = (HB_BOTTOM + HB_T + 9.0, -24.0)         # angle joint pivot (y, z)
LOCK_R = 22.0                                   # locking bolt's distance from the pivot (straight back)
LOCK_RANGE = 40.0                               # the angle joint adjusts +- this many degrees
SPRING_POCKET = (5.0, 4.6)                      # pocket radius and depth in the underside, for an 8 mm spring

# lift lever: an eccentric cam over the carrier's tail
CAM_Z = -53.5                                   # cam's contact point along the tail
CAM_GAP = 1.5                                   # cam's low point above the tail with the motor gear on the teeth
TAIL_ARM = HINGE[1] - CAM_Z                     # cam contact's distance behind the hinge axis
CAM_THROW = TAIL_ARM * math.sin(math.radians(LIFT_DEG)) + CAM_GAP   # extra reach when flipped
CAM_LOW = 12.0                                  # cam radius at its low point
LEVER_PIVOT = (TOP_Y[1] + CAM_GAP + CAM_LOW, CAM_Z)
LEVER_X = 8.0                                   # lever spans x +-this
# power switch (KW11-3Z, 20 x 10.3 x 6.4 mm, M2 holes 9.5 mm apart): body against a seat on the block, lever tip
# pressing on the tail; pressed (motor powered) with the motor gear on the teeth, released when the carrier lifts
SWITCH_X = (-LEVER_X - GAP - 0.8 - 6.4, -LEVER_X - GAP - 0.8)
SWITCH_Z = (-68.0, -48.0)
SWITCH_HOLES_Y = HB_BOTTOM - 3.5                # middle of the slotted M2 holes (+-2 mm)


def lock_point(pivot=PIVOT):
  return (pivot[0], pivot[1] - LOCK_R)


def hinge_block() -> Manifold:
  hy, hz = HINGE
  z0, z1 = HB_Z
  body = box(-HB_HALF, HB_HALF, HB_BOTTOM, HB_BOTTOM + HB_T, z0, z1)
  kn = []
  for sgn in (-1, 1):
    x0, x1 = (BLOCK_KNUCKLE[0], BLOCK_KNUCKLE[1]) if sgn > 0 else (-BLOCK_KNUCKLE[1], -BLOCK_KNUCKLE[0])
    kn.append(cyl_x(HINGE_R, x0, x1, y=hy, z=hz) + box(x0, x1, hy, HB_BOTTOM + 0.5, hz - HINGE_R, hz + HINGE_R))
  py, pz = PIVOT
  ly, lz = lock_point()
  ears = []
  for sgn in (-1, 1):
    x0, x1 = (EAR_X[0], EAR_X[1]) if sgn > 0 else (-EAR_X[1], -EAR_X[0])
    outline = [(HB_BOTTOM, pz + 12.0), (py, pz + 12.0), (py + 7.0, pz + 2.0), (ly + 7.0, lz), (ly, lz - 7.0), (HB_BOTTOM, lz - 7.0)]
    ears.append(prism_x(outline, x0, x1) + cyl_x(9.0, x0, x1, y=py, z=pz) + cyl_x(7.0, x0, x1, y=ly, z=lz))
  bridge = [box(HB_HALF - 0.1, EAR_X[0] + 0.1, HB_BOTTOM, HB_BOTTOM + HB_T, lz - 7.0, pz + 12.0),
            box(-EAR_X[0] - 0.1, -HB_HALF + 0.1, HB_BOTTOM, HB_BOTTOM + HB_T, lz - 7.0, pz + 12.0)]
  # power switch seat: a plate hanging below the block on the switch's outer side
  seat = box(SWITCH_X[0] - 3.0, SWITCH_X[0], HB_BOTTOM - 7.0, HB_BOTTOM + 0.5, SWITCH_Z[0], SWITCH_Z[1])
  part = body + union(kn) + union(ears) + union(bridge) + seat
  # the carrier's knuckle and its web turn in a slot through the block
  part = part - (cyl_x(HINGE_R + 3.5, -CARRIER_KNUCKLE - GAP, CARRIER_KNUCKLE + GAP, y=hy, z=hz) +
                 box(-CARRIER_KNUCKLE - GAP, CARRIER_KNUCKLE + GAP, HB_BOTTOM - 1, HB_BOTTOM + HB_T + 1, hz - HINGE_R - 3.5, hz + HINGE_R + 3.5))
  part = part - cyl_x(2.75, -60, 60, y=hy, z=hz, segments=32)
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=py, z=pz, segments=32)
  part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=ly, z=lz, segments=32)
  ly2, lz2 = LEVER_PIVOT
  part = part - cyl_x(M4_CLEAR / 2, -60, 60, y=ly2, z=lz2, segments=32)
  # the lever turns in a slot through the block (wide enough for the cam and the handle)
  part = part - box(-LEVER_X - GAP, LEVER_X + GAP, HB_BOTTOM - 1.0, HB_BOTTOM + HB_T + 1.0, lz2 - CAM_LOW - CAM_THROW - 2.0, lz2 + CAM_LOW + CAM_THROW + 2.0)
  # room for the switch body beside the lever slot
  part = part - box(SWITCH_X[0], SWITCH_X[1], HB_BOTTOM - 1.0, HB_BOTTOM + 2.0, SWITCH_Z[0], SWITCH_Z[1])
  part = part - cyl_y(SPRING_POCKET[0], HB_BOTTOM - 1.0, HB_BOTTOM + SPRING_POCKET[1], z=SPRING_Z, segments=48)
  # switch screw slots: M2 screws through the seat, +-2 mm up and down to set where it clicks
  zc = (SWITCH_Z[0] + SWITCH_Z[1]) / 2
  for dz in (-4.75, 4.75):
    for dy in np.linspace(-2.0, 2.0, 9):
      part = part - cyl_x(1.15, SWITCH_X[0] - 4.0, SWITCH_X[0] + 0.5, y=SWITCH_HOLES_Y + dy, z=zc + dz, segments=16)
  return clean(part)


# ***** lift lever *****

LEVER_HANDLE = 48.0


def lift_lever() -> Manifold:
  """Lever frame: pivot axis along x through the origin, drawn 'on' (handle pointing back, -z, a little up). The cam
  is an eccentric disc whose low point faces straight down onto the carrier's tail when 'on'. Flipping the handle over
  the top (about 200 degrees) turns the high point down, just past the middle, so the carrier's push holds it there."""
  e = CAM_THROW / 2.0
  r = CAM_LOW + e
  cam = cyl_x(r, -LEVER_X, LEVER_X, y=e, z=0.0, segments=96)
  handle = prism_x([(e - 3.0, 0.0), (e + 4.0, 0.0), (e + 14.0, -LEVER_HANDLE), (e + 8.0, -LEVER_HANDLE)], -LEVER_X, LEVER_X)
  grip = cyl_x(5.0, -LEVER_X, LEVER_X, y=e + 11.0, z=-LEVER_HANDLE, segments=48)
  part = cam + handle + grip
  part = part - cyl_x(M4_CLEAR / 2, -LEVER_X - 1, LEVER_X + 1, segments=32)
  return clean(part)


LEVER_OFF_DEG = 200.0     # the lever turns this far from 'on' to 'off'


'''
s = s[:start] + new + s[end:]
open(p, "w").write(s)

p = "assembly.py"
s = open(p).read()
old = '''  def lever(self, off: bool = False):
    lv = self.p["lever"]
    if off:
      lv = lv.rotate((200.0, 0, 0))'''
new = '''  def lever(self, off: bool = False):
    lv = self.p["lever"]
    if off:
      lv = lv.rotate((MP.LEVER_OFF_DEG, 0, 0))'''
assert old in s; s = s.replace(old, new)
old = '''def check_all(A: "Assembly", lift_deg: float = 22.0, wheel_turn: float = 70.0) -> dict:'''
new = '''def check_all(A: "Assembly", lift_deg: float = MP.LIFT_DEG, wheel_turn: float = 70.0) -> dict:'''
assert old in s; s = s.replace(old, new)
old = '''  def rest_on_grip_lift(self) -> float:
    """Carrier angle (negative = gear lowered) at which the roller rests on the bare steering wheel."""
    lo, hi = -15.0, 0.0'''
new = '''  def rest_on_grip_lift(self) -> float:
    """Carrier angle (negative = gear lowered) with the steering wheel turned past the teeth: the roller rests on the
    bare steering wheel, or the tail meets the lift lever's cam first (DROP_DEG), whichever comes first."""
    lo, hi = -MP.DROP_DEG, 0.0
    if overlap(self.gear(lo), self.wheel_grip()) <= 1e-3:
      return lo'''
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)
EOF
export PYTHONPATH=/home/claude/pylib:. && timeout 900 python3 -c "
import mountparts as MP
print('cam throw', round(MP.CAM_THROW,2), 'tail arm', MP.TAIL_ARM, 'lever pivot', MP.LEVER_PIVOT, 'HB bottom', MP.HB_BOTTOM)
import wheelparts as WP, assembly as AS
t = WP.Teeth()
parts = dict(teeth=WP.teeth_one_piece(t), gear=WP.motor_gear(), gear_teeth_only=WP.motor_gear_teeth_only(), carrier=MP.motor_carrier(), hinge_block=MP.hinge_block(), lever=MP.lift_lever(), slider=MP.arm_slider(), arm=MP.arm(), clamp=MP.dash_clamp())
for k in ('carrier','hinge_block','lever'): print(k, parts[k].status(), round(parts[k].volume()/1000,2), parts[k].genus(), len(parts[k].decompose()))
f = AS.solve(t)
A = AS.Assembly(t, f, parts)
for k, v in AS.check_all(A).items():
  print(f'{v:10.3f}  {k}' + ('   <-- TOUCHING' if v > 0.01 else ''))
"
