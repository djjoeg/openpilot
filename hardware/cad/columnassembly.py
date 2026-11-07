"""
The column mounts in the car. Two mounts share the carrier parts and the ring teeth:

  the column mount (bottom): the motor under the steering wheel, behind it, its gear inside the ring teeth at 6
  o'clock; the carrier, hinge block, lever bracket, lift lever and spring as on the dash mount; the arm up to the
  column clamp round the steering column covers.

  the right-side mount: the same parts turned a quarter turn round the steering column, the ring teeth at 3 o'clock
  (its channel shallow, so it can sit over the right spoke's junction with the grip) and the motor behind the wheel
  there; the arm back to a side bracket tied to the right-hand side of the covers, which a bar (the screw tab)
  holds to the dash's own screw at the driver's right. The lift lever swings sideways: the handle moves away from the
  wheel to put the motor on, in towards the hub to take it off.

Checks that nothing touches: the ring teeth, the part of the wheel you hold, the hub, the zone the wheel's spokes
sweep through when the wheel is turned far, the steering column covers, the dash, the wiper stalk and the key
cylinder (right-side mount), and the mount's own parts, with the lift lever down, up and at every angle between.

Frames: the steering wheel frame (see assembly.py); the mount frame is the steering wheel frame with the carrier
frame moved to the motor's front face at (0, -centre distance, Z_MOTOR_FACE_C), not turned: the hinge is still on
the hub's side of the motor and the spring still presses the motor gear away from the hub, into the ring. For the
right-side mount everything in the mount frame is then turned mount_deg (90, plus the ring's angle above 3 o'clock)
about the steering column. The lower saddle's frame has its V's middle at y = 0, +y up, +z towards the driver; it
sits under the covers at (0, saddle_y, CLAMP_Z). The side bracket's frame is in columnparts.py.
"""
import math
from dataclasses import dataclass, field

import numpy as np
from manifold3d import CrossSection, Manifold

import assembly as AS
import columnparts as CP
import mountparts as MP
import wheelparts as WP
from cadlib import box, cyl, revolve, union
from params import (ARM_LENGTHS, ARM_SLIDE, CLAMP_Z, COVER_FRONT_W, COVER_FRONT_Z, COVER_H, COVER_TAPER_Z, COVER_W, DASH_Z,
                    GRIP, HUB_BACK_Z, HUB_R, KEY_FROM, KEY_R, KEY_TO, ROLLER_R, SCREW_BEHIND, SCREW_DOWN, SCREW_RIGHT,
                    SPOKE_BACK_Z, STALK_FROM, STALK_R, STALK_TO, WHEEL_OD, WINDOW_DEG, Z_GEAR_ROLLER, Z_MOTOR_FACE,
                    Z_MOTOR_FACE_C)

ROLLER_R_, Z_GEAR_ROLLER_, Z_MOTOR_FACE_ = ROLLER_R, Z_GEAR_ROLLER, Z_MOTOR_FACE


def rot_z(deg: float) -> np.ndarray:
  a = math.radians(deg)
  return np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])


def rod(a, b, r: float, segments: int = 48) -> Manifold:
  """A round rod from point a to point b (a stalk, a key cylinder), radius r."""
  a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
  d = b - a
  length = float(np.linalg.norm(d))
  z = d / length
  x = np.cross([0.0, 1.0, 0.0], z) if abs(z[1]) < 0.9 else np.cross([1.0, 0.0, 0.0], z)
  x /= np.linalg.norm(x)
  y = np.cross(z, x)
  rot = np.stack([x, y, z], axis=1)
  return AS.place(cyl(r, 0.0, length, segments=segments), rot, a)


def saddle_y(cover_w: float = COVER_W, cover_h: float = COVER_H) -> float:
  """Where the lower saddle's V middle sits below the column's axis: the covers are taken as an oval cover_w wide and
  cover_h tall, resting on the rubber strips where the oval's slope matches the V's."""
  a, b = cover_w / 2.0, cover_h / 2.0
  tv = math.tan(math.radians(CP.V_DEG))
  # slope of the oval's lower side equals tv at x_c: (b / a^2) x / sqrt(1 - (x / a)^2) = tv
  k = b / a ** 2
  x_c = math.sqrt(tv ** 2 / (k ** 2 + tv ** 2 / a ** 2))
  y_c = -b * math.sqrt(max(0.0, 1.0 - (x_c / a) ** 2))
  y_pad = x_c * tv + CP.PAD_T / math.cos(math.radians(CP.V_DEG))     # the pad's surface above the V's middle at x_c
  return y_c - y_pad


@dataclass
class ColumnFit:
  ok: bool
  arm_deg: float           # arm's angle to the steering column (0 = along it, towards the dashboard)
  reach: float             # clamp bolt to hinge block bolt, mm
  arm_len: float           # the arm to print, 0 if none fits
  slide: float
  pivot_w: np.ndarray      # the clamp's arm bolt, mount frame
  notes: list = field(default_factory=list)


@dataclass
class SideFit(ColumnFit):
  bracket_z: float = 0.0                 # the side bracket's reference place along the column (steering wheel frame z)
  screw_w: np.ndarray = None             # the dash's screw, steering wheel frame
  tab_len: float = 0.0                   # the screw tab to print, 0 if none reaches
  tab_x0: float = 0.0                    # where the tab's start sits along the bracket's bar (bracket frame x)
  plate_y: float = CP.TAB_PLATE_Y        # the tab's end plate middle (bracket frame y)
  ring_at: float = 0.0                   # the ring's middle, degrees above 3 o'clock
  warnings: list = field(default_factory=list)   # things to check that don't stop the fit


def joint_w() -> np.ndarray:
  """The hinge block's arm bolt, mount frame."""
  return np.array([0.0, -CP.centre_distance() + MP.PIVOT[0], Z_MOTOR_FACE_C + MP.PIVOT[1]])


def pivot_w(cover_w: float = COVER_W, cover_h: float = COVER_H, clamp_z: float = CLAMP_Z) -> np.ndarray:
  return np.array([0.0, saddle_y(cover_w, cover_h) + CP.PIVOT_C[0], clamp_z + CP.PIVOT_C[1]])


def arm_fit(pv: np.ndarray, joint_angles: tuple, joint_name: str) -> tuple:
  """Which arm reaches from a mount's bolt pv (mount frame) to the hinge block's bolt, and at what angle; the notes
  say what doesn't fit."""
  d = joint_w() - pv
  reach = float(math.hypot(d[1], d[2]))
  arm = math.degrees(math.atan2(-d[1], d[2]))
  notes = []
  fits = [L for L in ARM_LENGTHS if abs(reach - L) <= ARM_SLIDE - 0.5]
  arm_len = min(fits, key=lambda L: abs(reach - L)) if fits else 0.0
  if not fits:
    notes.append(f"the {joint_name}'s bolt is {reach:.0f} mm from the hinge block's; the arms cover "
                 f"{ARM_LENGTHS[0] - ARM_SLIDE:.0f} to {ARM_LENGTHS[-1] + ARM_SLIDE:.0f}")
  if abs(arm - CP.ARM_NOMINAL_C) > MP.LOCK_RANGE - 0.5:
    notes.append(f"arm at {arm:.1f} degrees to the steering column; the hinge block's joint covers "
                 f"{CP.ARM_NOMINAL_C - MP.LOCK_RANGE:.0f} to {CP.ARM_NOMINAL_C + MP.LOCK_RANGE:.0f}")
  if not (joint_angles[0] + 0.5 <= arm <= joint_angles[1] - 0.5):
    notes.append(f"arm {arm:.1f} degrees from the column; the {joint_name}'s joint covers {joint_angles[0]:.0f} to {joint_angles[1]:.0f}")
  return reach, arm, float(arm_len), notes


def solve(cover_w: float = COVER_W, cover_h: float = COVER_H, clamp_z: float = CLAMP_Z) -> ColumnFit:
  """Which arm reaches from the clamp's bolt to the hinge block's bolt, and at what angle."""
  pv = pivot_w(cover_w, cover_h, clamp_z)
  reach, arm, arm_len, notes = arm_fit(pv, CP.ARM_ANGLES, "clamp")
  return ColumnFit(not notes, arm, reach, arm_len, reach - arm_len if arm_len else 0.0, pv, notes)


def solve_side(cover_w: float = COVER_W, screw_right: float = SCREW_RIGHT, screw_down: float = SCREW_DOWN,
               screw_behind: float = SCREW_BEHIND, tab_len: float | None = None, ring_at: float = 0.0) -> SideFit:
  """The right-side mount for a dash screw screw_right mm to the right of the steering wheel's outer edge at 3 o'clock,
  screw_down below that point and screw_behind behind the front face of the wheel's rim. The bracket's back face
  sits at the screw's depth (the tab's plate bears on the dash there); the tab's length and the plate's height follow
  the screw; the arm follows from the bracket's bolt to the hinge block's. tab_len: a length other than the printed
  set. ring_at: the whole mount turned this many degrees above 3 o'clock (the tab's plate tilts with it)."""
  z_screw = GRIP / 2.0 - screw_behind
  z_b = z_screw - CP.SB_PLATE_Z[0]
  screw_w = np.array([WHEEL_OD / 2.0 + screw_right, -screw_down, z_screw])
  mount_deg = 90.0 + ring_at
  # the screw in the bracket frame (turned back by ring_at, the bracket's origin on the covers' side)
  s_b = rot_z(-ring_at) @ screw_w - np.array([cover_w / 2.0, 0.0, z_b])
  notes = []
  lo, hi = CP.tab_slide_range()
  choices = []
  for L in ((tab_len,) if tab_len else CP.TAB_LENGTHS):
    x0 = s_b[0] + CP.TAB_SCREW_FROM_END - L
    if lo <= x0 <= hi:
      choices.append((abs(x0 - (lo + hi) / 2), L, x0))
  if choices:
    _, tab, tab_x0 = min(choices)
  else:
    tab, tab_x0 = 0.0, lo
    reach_lo = cover_w / 2.0 + lo + CP.TAB_LENGTHS[0] - CP.TAB_SCREW_FROM_END - WHEEL_OD / 2.0
    reach_hi = cover_w / 2.0 + hi + CP.TAB_LENGTHS[-1] - CP.TAB_SCREW_FROM_END - WHEEL_OD / 2.0
    notes.append(f"no screw tab reaches a screw {screw_right:.0f} mm right of the wheel's edge: the printed set covers "
                 f"{reach_lo:.0f} to {reach_hi:.0f} mm for covers {cover_w:.0f} wide (a tab of another length can be made)")
  pv_w = rot_z(ring_at) @ np.array([cover_w / 2.0 + CP.SB_PIVOT[0], 0.0, z_b + CP.SB_PIVOT[1]])
  pv = rot_z(-mount_deg) @ pv_w                       # the bracket's bolt in the mount frame
  reach, arm, arm_len, arm_notes = arm_fit(pv, CP.SB_ARM_ANGLES, "side bracket")
  notes += arm_notes
  if -screw_down > CP.TAB_BAR_Y[1] - 10.0:
    notes.append(f"the screw is only {screw_down:.0f} mm below the column's axis: the screw tab's plate stops at the bracket's "
                 f"bar, so the screw must be at least {-CP.TAB_BAR_Y[1] + 10.0:.0f} mm below it")
  if z_b + CP.SB_PLATE_Z[1] > COVER_FRONT_Z - 5.0:
    notes.append(f"the side bracket would reach {z_b + CP.SB_PLATE_Z[1] - COVER_FRONT_Z:.0f} mm past the covers' front edge: "
                 "the screw is too close to the wheel for it")
  warnings = []
  if z_screw < DASH_Z:
    warnings.append(f"the screw is {DASH_Z - z_screw:.0f} mm further back than the dash below the column is estimated to be: "
                    "the covers must reach that far back for the bracket")
  return SideFit(not notes, arm, reach, arm_len, reach - arm_len if arm_len else 0.0, pv, notes,
                 bracket_z=z_b, screw_w=screw_w, tab_len=tab, tab_x0=tab_x0, plate_y=float(s_b[1]), ring_at=ring_at,
                 warnings=warnings)


class ColumnAssembly(AS.Assembly):
  """The column mount (bottom) in the steering wheel frame. mount_deg turns everything in the mount frame about the
  steering column (0 for the bottom mount)."""

  def __init__(self, t: CP.RingTeeth, fit: ColumnFit, parts: dict, cover_w: float = COVER_W, cover_h: float = COVER_H,
               clamp_z: float = CLAMP_Z, mount_deg: float = 0.0, cover_front_w: float = COVER_FRONT_W):
    self.t, self.fit, self.p = t, fit, parts
    self.cover_front_w = cover_front_w
    self.cd = CP.centre_distance()
    self.b_org = np.array([0.0, -self.cd, Z_MOTOR_FACE_C])
    self.hinge_w = self.b_org + np.array([0.0, MP.HINGE[0], MP.HINGE[1]])
    self.a_rot = AS.rot_x(fit.arm_deg)
    self.mount_deg = mount_deg
    self.cover_w, self.cover_h, self.clamp_z = cover_w, cover_h, clamp_z
    self.saddle_org = np.array([0.0, saddle_y(cover_w, cover_h), clamp_z])
    self.up, self.rear = np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0])   # column frame: up is 12 o'clock
    if fit.arm_len and "arm" not in parts:
      parts["arm"] = MP.arm(fit.arm_len)

  # mount frame -> steering wheel frame
  def _w(self, m: Manifold) -> Manifold:
    return m.rotate((0, 0, self.mount_deg)) if self.mount_deg else m

  def _carried(self, m: Manifold, lift: float) -> Manifold:
    return self._w(super()._carried(m, lift))

  def hinge_block(self):
    return self._w(self.p["hinge_block"].translate(tuple(self.b_org)))

  def arm(self):
    d = np.array([0.0, -math.sin(math.radians(self.fit.arm_deg)), math.cos(math.radians(self.fit.arm_deg))])
    return self._w(AS.place(self.p["arm"], self.a_rot, self.fit.pivot_w + self.fit.slide * d))

  def teeth(self, wheel_deg: float = 0.0):
    return self.p["teeth"].rotate((0, 0, self.mount_deg + wheel_deg))

  def clamp(self):
    """The lower saddle with the arm joint."""
    return self.p["clamp_lower"].translate(tuple(self.saddle_org))

  def clamp_upper(self):
    m = self.p["clamp_upper"].rotate((0, 0, 180))     # V opening down; +z stays towards the driver
    return m.translate((0.0, -self.saddle_org[1], self.clamp_z))

  def rods(self):
    return CP.rods_and_nuts(-2.0 * self.saddle_org[1]).translate(tuple(self.saddle_org))

  def pads(self):
    return CP.pads().translate(tuple(self.saddle_org))

  def mount_parts(self) -> list:
    """The parts fixed to the car that hold the arm, (name, solid)."""
    return [("lower saddle", self.clamp()), ("upper saddle", self.clamp_upper()), ("rods and nuts", self.rods())]

  def covers(self, back_z: float = -400.0):
    """The steering column covers: an oval cover_h tall along the column, from their front edge back; COVER_FRONT_W
    wide at the front edge, widening to cover_w at COVER_TAPER_Z and that wide from there back."""
    b = self.cover_h / 2.0

    def oval(w, z):
      pts = [(w / 2.0 * math.cos(u), b * math.sin(u)) for u in np.linspace(0, 2 * math.pi, 96, endpoint=False)]
      return CrossSection([pts]).extrude(0.5).translate((0, 0, z))

    front_w = min(self.cover_front_w, self.cover_w)
    taper = Manifold.batch_hull([oval(front_w, COVER_FRONT_Z - 0.5), oval(self.cover_w, COVER_TAPER_Z)])
    back = oval(self.cover_w, 0.0).scale((1.0, 1.0, (COVER_TAPER_Z + 0.5 - back_z) / 0.5)).translate((0, 0, back_z))
    return taper + back

  def hub(self):
    """The steering wheel's hub (the airbag cover and the spokes' roots) as a drum."""
    return cyl(HUB_R, HUB_BACK_Z, 25.0, segments=96)

  def spoke_zone(self):
    """Where the wheel's spokes sweep when it is turned far: inside the part you hold, from the spokes' back face
    forward. Nothing fixed to the car may be in it."""
    return cyl(WHEEL_OD / 2 - GRIP + 1.0, SPOKE_BACK_Z, 25.0, segments=180) + self.hub()

  def dash(self):
    """The dash panel below the column, behind DASH_Z (a wall)."""
    return box(-300, 300, -400, 60, DASH_Z - 60.0, DASH_Z)

  def dash_parts(self) -> list:
    return [("dash below the column", self.dash())]

  def car_parts(self, dash: bool = True) -> list:
    """The car around the mount, (name, solid): estimates. dash: False leaves out the dash (its place is a guess)."""
    out = [("column covers", self.covers()), ("hub", self.hub()), ("spoke sweep zone", self.spoke_zone())]
    return out + (self.dash_parts() if dash else [])

  def hood(self, thickness: float = 12.0):
    return self.covers()

  def wheel_grip(self):
    t = self.t.base
    pts = [(t.rr + (GRIP / 2) * math.cos(a), (GRIP / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48, endpoint=False)]
    return revolve(pts, 0.0, 360.0, step_deg=1.0)


class SideAssembly(ColumnAssembly):
  """The right-side mount: the mount frame turned 90 degrees (plus the ring's angle above 3 o'clock) about the
  column; the side bracket, screw tab and their bolts on the covers' right-hand side."""

  def __init__(self, t: CP.RingTeeth, fit: SideFit, parts: dict, cover_w: float = COVER_W, cover_h: float = COVER_H,
               cover_front_w: float = COVER_FRONT_W):
    super().__init__(t, fit, parts, cover_w, cover_h, fit.bracket_z, 90.0 + fit.ring_at, cover_front_w)
    self.b_fix = np.array([cover_w / 2.0, 0.0, fit.bracket_z])     # the bracket frame's origin before the ring_at turn
    if fit.tab_len and "screw_tab" not in parts:
      parts["screw_tab"] = CP.screw_tab(fit.tab_len, fit.plate_y)

  # bracket frame -> steering wheel frame
  def _b(self, m: Manifold) -> Manifold:
    m = m.translate(tuple(self.b_fix))
    return m.rotate((0, 0, self.fit.ring_at)) if self.fit.ring_at else m

  def clamp(self):
    return self._b(self.p["side_bracket"])

  def clamp_upper(self):
    return self._b(self.p["screw_tab"].translate((self.fit.tab_x0, 0.0, 0.0)))

  def rods(self):
    return self._b(CP.tab_bolts(self.fit.tab_x0, self.fit.arm_deg))

  def pads(self):
    return self._b(CP.side_bracket_pads())

  def mount_parts(self) -> list:
    return [("side bracket", self.clamp()), ("screw tab", self.clamp_upper()), ("bracket bolts", self.rods())]

  def stalk(self):
    """The wiper stalk, about 2 o'clock behind the wheel (estimate)."""
    return rod(STALK_FROM, STALK_TO, STALK_R)

  def key(self):
    """The key cylinder's bezel on the covers' right-hand side near their front (estimate)."""
    return rod(KEY_FROM, KEY_TO, KEY_R)

  def dash_at_screw(self):
    """The dash to the right of the covers, a wall at the screw's depth (taken as flat from the covers outwards)."""
    z = float(self.fit.screw_w[2])
    return box(self.cover_w / 2.0 + 15.0, 420.0, -260.0, 260.0, z - 60.0, z)

  def dash_parts(self) -> list:
    return [("dash below the column", self.dash()), ("dash at the screw", self.dash_at_screw())]

  def car_parts(self, dash: bool = True) -> list:
    out = [("column covers", self.covers()), ("hub", self.hub()), ("spoke sweep zone", self.spoke_zone()),
           ("wiper stalk", self.stalk()), ("key cylinder", self.key())]
    return out + (self.dash_parts() if dash else [])


def overlap(a: Manifold, b: Manifold) -> float:
  return (a ^ b).volume()


def check_all(A: ColumnAssembly, wheel_turn: float = 40.0, lever_step: float = 4.0, dash: bool = True) -> dict:
  """Overlap volumes (mm^3) between parts that must not touch, as assembly.check_all, for the column mounts: the ring
  teeth in place of the steering wheel teeth, the car's parts around the mount (A.car_parts) and the mount's own
  parts (A.mount_parts) in place of the dash cover and dash clamp. dash: False leaves out the dash (its place is only
  an estimate)."""
  res = {}
  T, W = A.teeth(), A.wheel_grip()
  G, C, M = A.gear(), A.carrier(), A.motor()
  HB, AR, BR, SW = A.hinge_block(), A.arm(), A.bracket(), A.switch()
  LV = A.lever(0.0, 0.0)
  car, mount = A.car_parts(dash), A.mount_parts()
  cp = dict(car)
  COV, HUB, ZONE = cp["column covers"], cp["hub"], cp["spoke sweep zone"]
  pairs = {
    "teeth/gear": (T, G), "teeth/carrier": (T, C), "teeth/motor": (T, M), "grip/carrier": (W, C), "grip/motor": (W, M),
    "grip/gear": (W, G), "carrier/motor": (C, M), "carrier/hinge block": (C, HB), "motor/hinge block": (M, HB),
    "carrier/lever": (C, LV), "lever/hinge block": (LV, HB), "lever/lever bracket": (LV, BR),
    "lever bracket/hinge block": (BR, HB), "lever bracket/carrier": (BR, C), "lever bracket/motor": (BR, M),
    "lever bracket/teeth": (BR, T), "switch/lever": (SW, LV), "switch/hinge block": (SW, HB), "switch/carrier": (SW, C),
    "hinge block/arm": (HB, AR), "arm/carrier": (AR, C), "arm/motor": (AR, M), "arm/teeth": (AR, T),
    "hinge block/teeth": (HB, T), "lever/arm": (LV, AR), "lever bracket/arm": (BR, AR), "switch/arm": (SW, AR),
  }
  for name, part in mount:
    pairs[f"arm/{name}"] = (AR, part)
  for i in range(len(mount)):
    for j in range(i + 1, len(mount)):
      pairs[f"{mount[i][0]}/{mount[j][0]}"] = (mount[i][1], mount[j][1])
  sws = {dy: A._carried(MP.switch_screws(dy=dy), 0.0) for dy in (-MP.SW_SLOT, 0.0, MP.SW_SLOT)}
  LB = A._carried(MP.lever_bolt(), 0.0)
  for dy, sw in sws.items():
    pairs[f"switch screws ({dy:+.0f} mm in slots)/hinge block"] = (sw, HB)
    pairs[f"switch screws ({dy:+.0f} mm in slots)/arm"] = (sw, AR)
  pairs.update({"lever bolt/hinge block": (LB, HB), "lever bolt/arm": (LB, AR), "lever bolt/teeth": (LB, T),
                "hinge bolt, washers and nut/hinge block": (A._carried(MP.hinge_bolt(), 0.0), HB),
                "room for a hex key and socket on the lever bolt/hinge block": (A._carried(MP.lever_bolt_tools(), 0.0), HB),
                "room for a hex key and socket on the lever bolt/arm": (A._carried(MP.lever_bolt_tools(), 0.0), AR)})
  fixed = tuple(car) + tuple(mount)
  movers = (("motor gear", G), ("carrier", C), ("motor", M), ("hinge block", HB), ("lever bracket", BR), ("switch", SW),
            ("lift lever", LV), ("lever bolt", LB), ("ring teeth", T))
  for fixed_name, fx in fixed:
    for mover_name, mover in movers:
      pairs[f"{mover_name}/{fixed_name}"] = (mover, fx)
  for name, part in car:
    pairs[f"arm/{name}"] = (AR, part)
  for k, (a, b) in pairs.items():
    res["down: " + k] = overlap(a, b)
  gauge = A._carried(MP.setup_gauge(), 0.0)
  for k, b in {"lever bracket": BR, "spring": A._carried(MP.spring_body(), 0.0), "switch": SW, "carrier": C,
               "hinge block": HB, "arm": AR, "lift lever": LV}.items():
    res[f"setup gauge in: gauge/{k}"] = overlap(gauge, b)
  # lift lever up
  lift = max(0.0, MP.cam_lift(MP.A_OFF))
  hair = lift + 0.05
  Gl, Cl, Ml, BRl, SWl = A.gear(lift), A.carrier(hair), A.motor(hair), A.bracket(hair), A.switch(hair)
  LVo = A.lever(MP.A_OFF, hair)
  tag = f"lever up (lift {lift:.1f} deg): "
  up = {"teeth/gear": (T, Gl), "carrier/hinge block": (Cl, HB), "motor/hinge block": (Ml, HB),
        "carrier/arm": (Cl, AR), "motor/arm": (Ml, AR), "lever bracket/hinge block": (BRl, HB),
        "lever bracket/arm": (BRl, AR), "switch/hinge block": (SWl, HB), "lever/hinge block": (LVo, HB),
        "lever/arm": (LVo, AR), "lever/lever bracket": (LVo, BRl), "lever/carrier": (LVo, Cl), "lever/teeth": (LVo, T),
        "lever/grip": (LVo, W), "carrier/teeth": (Cl, T), "carrier/grip": (Cl, W),
        "lever bolt/hinge block": (A._carried(MP.lever_bolt(), hair), HB),
        "switch screws/hinge block": (A._carried(MP.switch_screws(dy=-MP.SW_SLOT), hair), HB)}
  for name, part in fixed:
    up[f"lever/{name}"] = (LVo, part)
    up[f"carrier/{name}"] = (Cl, part)
    up[f"motor/{name}"] = (Ml, part)
    up[f"lever bracket/{name}"] = (BRl, part)
  for k, (a, b) in up.items():
    res[tag + k] = overlap(a, b)
  for alpha in list(np.arange(lever_step, MP.A_OFF - 0.5, lever_step)) + [MP.A_OFF - 0.5]:
    th = max(0.0, MP.cam_lift(alpha)) + 0.05
    lv = A.lever(alpha, th, part="lever_no_tab")
    br, ca = A.bracket(th), A.carrier(th)
    swept = {"lever/hinge block": (lv, HB), "lever/arm": (lv, AR), "lever/lever bracket": (lv, br),
             "lever/carrier": (lv, ca), "carrier/hinge block": (ca, HB), "carrier/arm": (ca, AR),
             "lever bracket/hinge block": (br, HB), "lever bracket/arm": (br, AR), "lever/teeth": (lv, T),
             "lever/grip": (lv, W), "carrier/teeth": (ca, T), "carrier/grip": (ca, W),
             "lever bolt/hinge block": (A._carried(MP.lever_bolt(), th), HB),
             "switch screws/hinge block": (A._carried(MP.switch_screws(dy=-MP.SW_SLOT), th), HB)}
    for name, part in fixed:
      swept[f"lever/{name}"] = (lv, part)
      swept[f"carrier/{name}"] = (ca, part)
      swept[f"lever bracket/{name}"] = (br, part)
    for k, (a, b) in swept.items():
      key = "lever swept: " + k
      res[key] = max(res.get(key, 0.0), overlap(a, b))
  tab = A.lever(0.0, 0.0, part="tab")
  res["click: tab clear of the bracket, lever down"] = overlap(tab, BR)
  res["click: tab meets its ridge lifting (should touch)"] = -max(overlap(A.lever(a, 0.0, part="tab"), BR) for a in (0.75, 1.25, 1.75))
  res["lever stops past up (should touch)"] = -overlap(A.lever(MP.A_OFF + 4.0, hair), HB)
  # the wheel turned past the ring: the carrier drops to DROP_DEG (the roller finds nothing to rest on)
  rest = -MP.DROP_DEG
  Gr, Cr, Mr, BRr, SWr = A.gear(rest), A.carrier(rest), A.motor(rest), A.bracket(rest), A.switch(rest)
  LVr, LBr = A.lever(0.0, rest), A._carried(MP.lever_bolt(), rest)
  SWSr = A._carried(MP.switch_screws(dy=-MP.SW_SLOT), rest)
  checks = {"grip/gear": (W, Gr), "grip/carrier": (W, Cr), "grip/motor": (W, Mr), "carrier/hinge block": (Cr, HB),
            "motor/hinge block": (Mr, HB), "lever bracket/hinge block": (BRr, HB), "switch/hinge block": (SWr, HB),
            "carrier/arm": (Cr, AR), "lever bracket/arm": (BRr, AR), "lever/hinge block": (LVr, HB),
            "lever bolt/hinge block": (LBr, HB), "switch screws/hinge block": (SWSr, HB), "gear/column covers": (Gr, COV),
            "carrier/column covers": (Cr, COV), "gear/spoke sweep zone": (Gr, ZONE), "lever/hub": (LVr, HUB)}
  for name, part in car:
    if name not in ("column covers", "hub", "spoke sweep zone"):
      checks[f"lever/{name}"] = (LVr, part)
      checks[f"carrier/{name}"] = (Cr, part)
  for side, TT in (("left", A.teeth(wheel_turn)), ("right", A.teeth(-wheel_turn))):
    for name, part in (("carrier", Cr), ("gear", Gr), ("lever bracket", BRr), ("motor", Mr), ("switch", SWr),
                       ("lift lever", LVr), ("lever bolt", LBr), ("switch screws", SWSr), ("hinge block", HB), ("arm", AR)):
      checks[f"teeth turned {side}/{name}"] = (TT, part)
  for k, (a, b) in checks.items():
    res[f"wheel turned {wheel_turn:.0f}, carrier down {-rest:.1f} deg: " + k] = overlap(a, b)
  # the ring turned through its arc with the motor gear turning with it (the same way, RING_TEETH / MOTOR_TEETH times
  # faster): the gear's teeth and roller and the carrier clear the ring at every 1 degree of steering wheel
  ratio = WP.RING_TEETH / WP.MOTOR_TEETH
  worst_gear = worst_carrier = 0.0
  for w in np.arange(-A.t.roll_half, A.t.roll_half + 1e-9, 1.0):
    Gw = A._carried(A.p["gear"].rotate((0, 0, float(w) * ratio)), 0.0)
    worst_gear = max(worst_gear, overlap(A.teeth(float(w)), Gw))
    worst_carrier = max(worst_carrier, overlap(A.teeth(float(w)), C))
  res["ring turned through its arc: teeth/gear (worst)"] = worst_gear
  res["ring turned through its arc: teeth/carrier (worst)"] = worst_carrier
  # past the rolling band the roller follows the lead-in outwards and the carrier drops with it (up to DROP_DEG, the
  # lever's rounded end on the hinge block): the gear's teeth and the carrier must clear the ring all along it, and
  # at the ring's end with the carrier fully dropped
  worst = 0.0
  for w in np.arange(A.t.roll_half, A.t.half + 1.0, 0.5):
    drop = roller_drop_deg(A, float(w))     # the roller itself rests on the ring there, so it is left out
    for part in (A._carried(A.p["gear_teeth_only"], -drop), A.carrier(-drop)):
      for sign in (1, -1):
        worst = max(worst, overlap(A.teeth(sign * float(w)), part))
  res["ring's lead-in with the carrier dropping: teeth/gear teeth and teeth/carrier (worst)"] = worst
  return res


def roller_drop_deg(A: ColumnAssembly, wheel_deg: float) -> float:
  """How far (degrees about the hinge) the carrier drops with the ring turned wheel_deg: until the roller rests on
  the ring's inside (the lead-in) or the lever's rounded end stops it at DROP_DEG."""
  zr0, zr1 = (z - Z_MOTOR_FACE_ for z in Z_GEAR_ROLLER_)
  roller = cyl(ROLLER_R_, zr0, zr1, segments=360)
  T = A.teeth(wheel_deg)
  if overlap(A._carried(roller, -MP.DROP_DEG), T) <= 1e-3:
    return MP.DROP_DEG
  lo, hi = 0.0, MP.DROP_DEG
  for _ in range(24):
    mid = (lo + hi) / 2
    if overlap(A._carried(roller, -mid), T) > 1e-3:
      hi = mid
    else:
      lo = mid
  return lo


def reach_back(A: ColumnAssembly) -> float:
  """How far behind the middle of the grip the parts reach (mm): the dash must be further."""
  parts = [A.motor(), A.hinge_block(), A.arm()] + [m for _, m in A.mount_parts()]
  return round(-min(m.bounding_box()[2] for m in parts), 0)


def window_check(t: CP.RingTeeth) -> dict:
  """The ring teeth must fit between the steering wheel's two lower spokes, zip ties included."""
  margin = WINDOW_DEG / 2 - t.half
  return {"ring_spans_deg": round(t.span_deg, 1), "window_between_spokes_deg": WINDOW_DEG,
          "room_each_side_deg": round(margin, 1), "room_each_side_mm_along_the_grip": round(math.radians(margin) * WHEEL_OD / 2, 0),
          "ok": margin >= 2.0}


def margins(A: ColumnAssembly) -> dict:
  """How far apart the parts that come closest are (mm)."""
  def gap(moving, fx, direction):
    lo, hi = 0.0, 25.0
    d = np.asarray(direction, dtype=float)
    for _ in range(26):
      mid = (lo + hi) / 2
      if overlap(moving.translate(tuple(d * mid)), fx) > 1e-3:
        hi = mid
      else:
        lo = mid
    return round(lo, 2)
  lift = MP.cam_lift(MP.A_OFF)
  R = rot_z(A.mount_deg)
  out_dir = R @ np.array([0.0, -1.0, 0.0])     # away from the hub, into the ring
  hub_dir = R @ np.array([0.0, 1.0, 0.0])      # towards the hub (and the covers)
  fwd = (0.0, 0.0, 1.0)                        # towards the driver
  dash = union([m for _, m in A.dash_parts()])
  out = {"motor_gear_to_ring_teeth_with_lever_up": min(gap(A.gear(lift), A.teeth(w), out_dir) for w in (0, 7, 14)),
         "lift_lever_handle_to_the_spoke_sweep_zone": gap(A.lever(0.0, 0.0), A.spoke_zone(), fwd),
         "lift_lever_up_to_the_hub": gap(A.lever(MP.A_OFF, lift), A.hub(), hub_dir),
         "motor_and_board_to_the_dash": gap(A.motor(), dash, (0.0, 0.0, -1.0)),
         "arm_to_the_column_covers": gap(A.arm(), A.covers(), hub_dir)}
  if isinstance(A, SideAssembly):
    levers = A.lever(0.0, 0.0) + A.lever(MP.A_OFF, lift)
    out["lift_lever_to_the_wiper_stalk"] = gap(levers, A.stalk(), (0.0, 1.0, 0.0))
    out["hinge_block_and_motor_to_the_wiper_stalk"] = gap(A.hinge_block() + A.motor(), A.stalk(), (0.0, 1.0, 0.0))
    out["arm_and_bracket_to_the_key_cylinder"] = gap(A.arm() + A.clamp() + A.clamp_upper(), A.key(), (0.0, 0.0, 1.0))
    out["screw_tab_plate_to_the_screw_slot_end"] = CP.TAB_SLOT_HALF - abs(A.fit.plate_y - float(A.fit.screw_w[1]))
  return out


def parts_scene(A: ColumnAssembly, lift_deg=0.0, alpha=0.0, wheel=0.0):
  """(manifold, colour) pairs for the pictures."""
  col = {"teeth": (.72, .72, .72), "grip": (.3, .3, .3), "gear": (.95, .6, .25), "carrier": (.35, .55, .85), "motor": (.25, .25, .25),
         "hinge": (.45, .75, .45), "bracket": (.6, .45, .8), "lever": (.85, .3, .3), "switch": (.9, .85, .2),
         "arm": (.6, .5, .4), "clamp": (.5, .7, .7), "covers": (.85, .85, .75), "hub": (.4, .4, .4), "rods": (.6, .6, .6),
         "car": (.8, .75, .7)}
  items = [(A.teeth(wheel), col["teeth"]), (A.wheel_grip(), col["grip"]), (A.gear(lift_deg), col["gear"]),
           (A.carrier(lift_deg), col["carrier"]), (A.motor(lift_deg), col["motor"]), (A.hinge_block(), col["hinge"]),
           (A.bracket(lift_deg), col["bracket"]), (A.lever(alpha, lift_deg), col["lever"]), (A.switch(lift_deg), col["switch"]),
           (A.arm(), col["arm"]), (A.clamp(), col["clamp"]), (A.clamp_upper(), col["clamp"]), (A.rods(), col["rods"]),
           (A.covers(-260.0), col["covers"]), (A.hub(), col["hub"])]
  if isinstance(A, SideAssembly):
    items += [(A.stalk(), col["car"]), (A.key(), col["car"])]
  return [(m, c) for m, c in items if not m.is_empty()]
