"""
The car around the steering column, rebuilt from your photos (11 October): where the key, the stalks, the steering
wheel's spokes and back cover and the cover screw under the key are, relative to the steering column.

Frame (mm), as the rest of the CAD: z along the column towards the driver, 0 = the middle of the part of the steering
wheel you hold (the grip); y up; x to the driver's right; the steering wheel straight. Clock positions are seen from the
driver's seat.

How each number was found (photo numbers as in the reference sheet, 00-39):
  - Photo 36 (the whole wheel straight on, your tape across it) sets the frame: the grip (372 mm across, 35.4 mm
    thick) fixes where the camera was. Which way is up comes from the instrument cluster in the same photo: the gear
    letters P R N D D3 run straight down the cluster and the two dials' centres sit level, and both say the phone was
    turned 10 degrees (10.1 and 10.6) from level. Every clock position below has that taken out.
  - In photo 36 the wheel itself was turned about 22 degrees to the right: its spokes are symmetric about a line 22
    degrees from the car's vertical. The spokes' places below are on the wheel, measured from its own vertical.
  - The key photos (24, 26, 33, 37) were all taken from about the same spot, right of the column. In each, the key's
    black bezel (38 mm across: your tape lies over it in photo 24) gives the camera's distance to the key (213-266 mm),
    the edge of the grip shows up 21-26 degrees from the key, and the cluster's numbers tie the photo to photo 36.
    Together they put the key's centre 100-145 mm behind the middle of the grip, 90-115 mm from the column's centre,
    at about 3:47.
  - Photo 24's tape is hooked on the edge of the steering wheel's back cover: the key's centre is 41 mm along the
    cover from it, the grey dash trim 95-100 mm.
  - The wiper stalk comes out of the cover about 50 mm above the key and is about 105 mm long (your tape along it,
    photo 25); photo 36 puts its end about 150 mm from the column's centre; you say its end is at least an inch behind
    the back of the grip.
  - The screw cup under the key: on the lower cover's underside where Honda's drawing puts it, about 60-70 mm from the
    key's centre (photos 33, 37 agree).
  - Not pinned down by the photos (estimates kept from before): the column covers' width and bottom, the hub, the knee
    bolster's depth.
"""
import math

import numpy as np
from manifold3d import Manifold

from cadlib import box, cyl, union

# ----- the key -----
KEY_CLOCK_DEG = -23.0          # about 3:46 (0 = 3 o'clock, + up): range 3:40-3:52
KEY_R = 100.0                  # the bezel's centre this far from the column's centre: range 90-110
KEY_Z = -115.0                 # ... and this far behind the middle of the grip: range -100 to -145
KEY_TILT_DEG = 30.0            # the bezel faces out from the column, turned this far towards the driver: range 15-42
KEY_RANGE = {"clock_deg": (-26.0, -20.0), "r": (90.0, 115.0), "z": (-145.0, -100.0), "tilt_deg": (15.0, 42.0)}
BEZEL_D = 38.0                 # the black ring across (your tape, photo 24)
BEZEL_CHROME_D = 26.0          # the chrome ring inside it (ratio to the black ring 1.40-1.50 in the photos)
SLOT_DEG = 45.0                # the keyhole's slot, as it sits with the key out (photos 26, 33, 37)
KEY_HEAD = (36.0, 52.0, 15.0)  # the remote head key's head: width, length, thickness (Honda's 4-button head, approx.)
KEY_SHANK = 8.0                # the blade showing between the bezel and the head
KEY_TURN_ROOM = (36.0, 62.0)   # your fingers turning it: radius round the key's line, and how far out from the bezel

# ----- the steering wheel's back cover (turns with the wheel) -----
BACK_COVER_R = 90.0            # its outside, where it meets the column covers: range 85-100
BACK_COVER_RIM_Z = -80.0       # its edge (the tape's hook, photo 24): range -60 to -110
AIRBAG_HOLE = (88.0, -18.0, -45.0, 6.5)    # the airbag bolt hole on its right side: radius, clock (on the wheel), z, hole radius
                                           # (the left one mirrored)
# ----- the stalks -----
WIPER_FROM = (89.0, 16.0, -130.0)   # where the wiper stalk comes out of the cover (range +-15 each way)
WIPER_TO = (149.0, 36.0, -48.0)     # its end, 104 mm along (your tape): 150 mm from the column's centre (photo 36)
WIPER_END_Z = -17.7 - 25.4         # its end at least an inch behind the back of the grip (you), the closest it can be
STALK_R = 11.0
# ----- the steering wheel's spokes where they meet the grip (photo 36, measured from the wheel's own vertical) -----
RIGHT_SPOKE_DEG = (-23.0, 18.0)     # the right spoke (cruise buttons) meets the grip from about 3:46 up to 2:24
RIGHT_BAR_DEG = (-74.0, -56.0)      # the right lower spoke (the silver bar) meets the grip from about 5:28 up to 4:52
SPOKE_TOL_DEG = 3.0                 # how far off those may be (read off one photo)
# ----- under the key -----
CUP = (38.0, -50.0, -98.0)          # the screw cup under the key, on the lower cover's underside (Honda's drawing)
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
  ("Key: centre of the bezel", "about 3:47 (3:40–3:52); 90–115 mm out from the column's centre; 100–145 mm behind the middle of the grip (best guess 115)",
   "photos 24, 26, 33, 37 (bezel size, grip edge, cluster numbers), set level by photo 36's cluster; your tape in photo 24"),
  ("Key: which way it faces", "out from the column, turned 15–42° towards you", "photos 24 (tape marks), 26, 33, 37"),
  ("Key bezel", "black ring 38 mm across, chrome ring about 26 mm; keyhole slot at about 45°", "your tape over it, photo 24; photos 26, 33, 37"),
  ("Wheel's back cover: its edge by the column covers", "41 mm in front of the key's centre, along the cover", "your tape, photo 24"),
  ("Grey dash trim beside the key", "95–100 mm from the back cover's edge, along the cover", "your tape, photo 24"),
  ("Wiper stalk", "comes out about 50 mm above the key, about 105 mm long; its end about 150 mm from the column's centre at about 2:25, at least an inch behind the back of the grip",
   "photos 24, 26, 33, 37, 36; your tape, photo 25; you"),
  ("Right spoke (cruise buttons)", "meets the grip from about 2:24 to 3:46 (±3°)", "photo 36"),
  ("Right lower spoke (silver bar)", "meets the grip from about 4:52 to 5:28 (±3°)", "photo 36"),
  ("Screw cup under the key", "on the lower cover's underside, 60–70 mm from the key's centre", "Honda's drawing; photos 33, 37"),
  ("Steering wheel", "372 mm across, grip 35.4 mm thick", "your tape, photos 36 and 35"),
]
