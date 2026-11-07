"""
The car around the steering column, rebuilt from your photos (11 October): where the key, the stalks, the steering
wheel's back cover, the cover screw under the key and the dash trim are, relative to the steering wheel.

Frame (mm), as the rest of the CAD: z along the column towards the driver, 0 = the middle of the part of the steering
wheel you hold (the grip); y up; x to the driver's right. Clock positions are seen from the driver's seat.

How each number was found (photo numbers as in the reference sheet, 00-39):
  - The key photos (24, 26, 33, 37) were all taken from about the same spot, right of the column and a little towards
    the driver. In each, the key's black bezel (38 mm across: your tape lies over it in photo 24, 24 mm to 62 mm) gives
    the camera's distance to the key (213-266 mm), and the edge of the grip (35.4 mm thick, 372 mm across) shows up
    21-26 degrees from the key. Photo 24's tape runs along the column; its millimetre marks shrink about 7 % from the
    hook end to the 90 mm mark, so that camera looked at the key about 15-20 degrees from straight across. Those angles
    and distances put the key's centre 100-115 mm behind the middle of the grip in all four photos.
  - The same tape is hooked on the edge of the steering wheel's back cover: the key's centre is 41 mm along the cover
    from it, and the grey dash trim 95-100 mm.
  - Where the key sits round the column (about 3:20-3:35) and how far out (90-110 mm from the column's centre) come
    from solving the four key photos together with the cluster's numbers and the grip; the clock position agreed in
    every solution, the depth didn't (the key photos all look along nearly the same line), which is why the depth
    comes from the tape and grip-edge angles above instead.
  - The wiper stalk comes out of the cover about 50 mm above the key (photos 24, 26, 33, 37) and is about 105 mm long
    (your tape along it, photo 25); its end shows next to the grip in photo 36.
  - The screw cup under the key is about 65 mm below the key's centre (photos 33, 37).
  - Not pinned down by the photos (estimates kept from before): the column covers' width and bottom, the hub.
"""
import math

import numpy as np
from manifold3d import Manifold

from cadlib import box, cyl, union

# ----- the key -----
KEY_CLOCK_DEG = -12.0          # about 3:24 (0 = 3 o'clock, + up): range 3:18-3:35
KEY_R = 100.0                  # the bezel's centre this far from the column's centre: range 90-110
KEY_Z = -108.0                 # ... and this far behind the middle of the grip: range -98 to -118
KEY_TILT_DEG = 18.0            # the bezel faces out from the column, turned this far towards the driver: range 8-28
KEY_RANGE = {"clock_deg": (-18.0, -6.0), "r": (90.0, 110.0), "z": (-118.0, -98.0), "tilt_deg": (8.0, 28.0)}
BEZEL_D = 38.0                 # the black ring across (your tape, photo 24)
BEZEL_CHROME_D = 26.0          # the chrome ring inside it (ratio to the black ring 1.40-1.50 in the photos)
SLOT_DEG = 45.0                # the keyhole's slot, as it sits with the key out (photos 26, 33, 37)
KEY_HEAD = (36.0, 52.0, 15.0)  # the remote head key's head: width, length, thickness (Honda's 4-button head, approx.)
KEY_SHANK = 8.0                # the blade showing between the bezel and the head
KEY_TURN_ROOM = (36.0, 62.0)   # your fingers turning it: radius round the key's line, and how far out from the bezel

# ----- the steering wheel's back cover (turns with the wheel) -----
BACK_COVER_R = 90.0            # its outside, where it meets the column covers: range 85-100
BACK_COVER_RIM_Z = -67.0       # its edge (the tape's hook, photo 24): range -57 to -77
AIRBAG_HOLE = (88.0, -30.0, -45.0, 6.5)    # the airbag bolt hole on its right side: radius, clock, z, hole radius
                                           # (the left one mirrored)
# ----- the stalks -----
WIPER_FROM = (80.0, 30.0, -95.0)    # where the wiper stalk comes out of the cover (range +-15 each way)
WIPER_TO = (170.0, 72.0, -60.0)     # its end, 105 mm along (your tape)
STALK_R = 11.0
# ----- under the key -----
CUP = (80.0, -78.0, -105.0)         # the screw cup under the key: range +-15
DASH_TRIM_Z = -164.0                # the grey dash trim beside the column on the key's side: range -152 to -176


def _frame(clock_deg: float, tilt_deg: float):
  """Unit vectors: n (the way the key points out), and two across it."""
  c = math.radians(clock_deg)
  radial = np.array([math.cos(c), math.sin(c), 0.0])
  zax = np.array([0.0, 0.0, 1.0])
  t = math.radians(tilt_deg)
  n = math.cos(t) * radial + math.sin(t) * zax
  a = np.cross(n, zax)
  a /= np.linalg.norm(a)
  b = np.cross(n, a)
  return n, a, b


def key_centre(clock_deg=KEY_CLOCK_DEG, r=KEY_R, z=KEY_Z) -> np.ndarray:
  c = math.radians(clock_deg)
  return np.array([r * math.cos(c), r * math.sin(c), z])


def _place(m: Manifold, origin, n, a, b) -> Manifold:
  """m built with its local z along the key's line (n), x along a, y along b, origin at the bezel's face."""
  R = np.stack([a, b, n], axis=1)
  T = np.asarray(origin, float)
  return m.transform([[R[0, 0], R[0, 1], R[0, 2], T[0]], [R[1, 0], R[1, 1], R[1, 2], T[1]], [R[2, 0], R[2, 1], R[2, 2], T[2]]])


def bezel(clock_deg=KEY_CLOCK_DEG, r=KEY_R, z=KEY_Z, tilt_deg=KEY_TILT_DEG) -> dict:
  """The bezel's black ring, chrome ring and the keyhole's face with its slot (a recess), on the key's line."""
  n, a, b = _frame(clock_deg, tilt_deg)
  o = key_centre(clock_deg, r, z)
  ring = cyl(BEZEL_D / 2, -6.0, 1.5, segments=72) - cyl(BEZEL_CHROME_D / 2 + 0.5, -7.0, 2.5, segments=72)
  chrome = cyl(BEZEL_CHROME_D / 2 + 0.5, -6.0, 0.5, segments=72) - cyl(BEZEL_CHROME_D / 2 - 2.0, -7.0, 1.5, segments=72)
  face = cyl(BEZEL_CHROME_D / 2 - 2.0, -6.0, -2.0, segments=64)
  slot = box(-1.6, 1.6, -7.0, 7.0, -5.0, 0.0).rotate((0, 0, SLOT_DEG))
  return {"ring": _place(ring, o, n, a, b), "chrome": _place(chrome, o, n, a, b), "face": _place(face - slot, o, n, a, b)}


def key_in(clock_deg=KEY_CLOCK_DEG, r=KEY_R, z=KEY_Z, tilt_deg=KEY_TILT_DEG, turned_deg=90.0) -> Manifold:
  """The key in the ignition (at ON: turned 90 degrees from where it goes in): blade showing, then the head."""
  n, a, b = _frame(clock_deg, tilt_deg)
  o = key_centre(clock_deg, r, z)
  w, L, t = KEY_HEAD
  shank = box(-4.0, 4.0, -1.0, 1.0, 0.0, KEY_SHANK + 2.0)
  head = Manifold.batch_hull([cyl(w / 2, KEY_SHANK, KEY_SHANK + t, segments=48).scale((1.0, t / w, 1.0)),
                              cyl(w / 2 - 4.0, KEY_SHANK + L - 1.0, KEY_SHANK + L, segments=48).scale((1.0, t / w, 1.0))])
  head = Manifold.batch_hull([box(-w / 2 + 4, w / 2 - 4, -t / 2, t / 2, KEY_SHANK, KEY_SHANK + L),
                              box(-w / 2, w / 2, -t / 2 + 2, t / 2 - 2, KEY_SHANK + 4, KEY_SHANK + L - 4)])
  return _place((shank + head).rotate((0, 0, SLOT_DEG + turned_deg)), o, n, a, b)


def key_turn_room(clock_deg=KEY_CLOCK_DEG, r=KEY_R, z=KEY_Z, tilt_deg=KEY_TILT_DEG) -> Manifold:
  """Everywhere the key's head and your fingers turning it go."""
  n, a, b = _frame(clock_deg, tilt_deg)
  o = key_centre(clock_deg, r, z)
  rr, L = KEY_TURN_ROOM
  return _place(cyl(rr, 3.0, L, segments=48), o, n, a, b)


def key_bulge(clock_deg=KEY_CLOCK_DEG, r=KEY_R, z=KEY_Z, tilt_deg=KEY_TILT_DEG) -> Manifold:
  """The column cover's bulge round the key: a rounded lump from the cover's side out to the bezel."""
  n, a, b = _frame(clock_deg, tilt_deg)
  o = key_centre(clock_deg, r, z)
  lump = Manifold.batch_hull([cyl(30.0, -45.0, -8.0, segments=48), cyl(24.0, -8.0, -4.0, segments=48)])
  return _place(lump, o, n, a, b)


def back_cover() -> Manifold:
  """The steering wheel's back cover: from behind the hub to its edge by the column covers, with the airbag holes."""
  shell = cyl(BACK_COVER_R, BACK_COVER_RIM_Z, -25.0, segments=96) - cyl(BACK_COVER_R - 3.0, BACK_COVER_RIM_Z - 1.0, -28.0, segments=96)
  hr, hc, hz, hrad = AIRBAG_HOLE
  holes = []
  for side in (1.0, -1.0):
    c = math.radians(hc if side > 0 else 180.0 - hc)
    p = np.array([hr * math.cos(c), hr * math.sin(c), hz])
    d = np.array([math.cos(c), math.sin(c), 0.0])
    h = cyl(hrad, -15.0, 15.0, segments=24)
    zax = np.array([0.0, 0.0, 1.0])
    a = np.cross(d, zax)
    b = np.cross(d, a)
    holes.append(_place(h, p, d, a, b))
  return shell - union(holes)


def stalk(frm=WIPER_FROM, to=WIPER_TO, mirror=False) -> Manifold:
  import columnassembly as CA
  f, t = np.array(frm, float), np.array(to, float)
  if mirror:
    f[0], t[0] = -f[0], -t[0]
  return CA.rod(f, t, STALK_R)


def dash_trim() -> Manifold:
  """The grey trim round the column where it goes into the dash, on the key's side (a thin plate with the opening)."""
  return box(30.0, 220.0, -140.0, 40.0, DASH_TRIM_Z - 6.0, DASH_TRIM_Z) - box(29.0, 95.0, -95.0, 70.0, DASH_TRIM_Z - 7.0, DASH_TRIM_Z + 1.0)


REFERENCE_ROWS = [
  ("Key: centre of the bezel", "3:18–3:35, 90–110 mm out from the column's centre, 98–118 mm behind the middle of the grip",
   "photos 24, 26, 33, 37 (bezel size, grip edge); your tape in photo 24"),
  ("Key: which way it faces", "straight out from the column, turned 8–28° towards you", "photo 24 (tape marks), 26, 33, 37"),
  ("Key bezel", "black ring 38 mm across, chrome ring about 26 mm", "your tape over it, photo 24"),
  ("Wheel's back cover: its edge by the column covers", "57–77 mm behind the middle of the grip (41 mm in front of the key's centre)",
   "your tape, photo 24"),
  ("Dash trim beside the key", "95–100 mm behind the back cover's edge, along the cover", "your tape, photo 24"),
  ("Wiper stalk", "comes out about 50 mm above the key; 105 mm long; its end just inside the grip, about 2:15", "photos 24, 26, 33, 37, 36; your tape, photo 25"),
  ("Screw cup under the key", "about 65 mm below the key's centre", "photos 33, 37"),
  ("Steering wheel", "372 mm across, grip 35.4 mm thick", "your tape, photos 36 and 35"),
]
