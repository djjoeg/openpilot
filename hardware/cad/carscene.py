"""
The car round the bottom of the steering column, rebuilt from your photos, for any value of the one distance the photos
can't settle: D, how far the key hole sits behind the back of the grip (the part of the steering wheel you hold),
measured along the column.

Why one number: the key photos (24, 26, 33, 37) fix everything round the key to a few millimetres, because the key's
black bezel (38 mm across, your tape) is in all of them: the key slot, the PUSH mark, the screw cup under the key, the
stalk's opening and the round hole in the cover on the back of the steering wheel all sit in the same places relative
to the key in every fit. What the photos can't fix is how far that whole group sits from the steering wheel: two fits,
equally good, put the key 85 mm and 128 mm behind the grip's back, and the group slides almost rigidly between them
(within 4 mm). Everything below is interpolated between those two fits by D.

Frame (mm), as the rest of the CAD: z along the column towards the driver, 0 = the middle of the grip; y up; x to the
driver's right; the steering wheel straight.

Facts from the photos that don't depend on D:
  - the screw cup under the key (on the underside of the lower column cover) is 59 mm below the key's centre, 30 mm
    nearer the column's middle line and 4 mm nearer the wheel: the cover's underside is about 100 mm below the column's
    centre (it was 50 in the old estimate);
  - the tape in photo 24, hooked on the edge of the cover on the back of the steering wheel, reads 41 mm at the key's
    centre: that edge is 39-40 mm in front of the key (along the column) and about 10 mm nearer the column's centre;
  - the round hole in that back cover is about 62 mm in front of the key.
"""
import math

import numpy as np
from manifold3d import CrossSection, Manifold

from cadlib import box, revolve, union

D_FITS = (84.9, 128.2)          # the two photo fits
D_REF = 97.0                    # the best single estimate so far (the earlier key reference, z -115)
D_RANGE = (88.0, 125.0)         # what's still possible (your note that the wiper stalk's end is at least an inch behind
                                # the grip's back rules out the nearest fits)

# landmarks in the two fits (car frame, mm)
_A = {"KEY": (88.3, -33.0, -102.6), "KS1": (77.1, -28.6, -106.1), "KS2": (79.3, -33.0, -113.7),
      "PU": (100.6, -14.6, -124.4), "CUP": (58.5, -92.5, -99.5), "SH": (84.4, 26.0, -100.2), "ST": (164.4, 35.0, -25.1),
      "RH": (59.5, -53.7, -41.2), "HOOK": (80.5, -34.5, -62.4), "N": (0.799, 0.110, 0.592)}
_B = {"KEY": (103.5, -49.3, -145.9), "KS1": (91.5, -44.3, -151.7), "KS2": (93.4, -49.1, -159.9),
      "PU": (117.0, -31.5, -169.7), "CUP": (73.1, -108.1, -140.6), "SH": (96.2, 14.0, -152.1), "ST": (179.1, 19.7, -61.9),
      "RH": (73.7, -67.0, -82.2), "HOOK": (90.8, -48.9, -106.9), "N": (0.746, 0.101, 0.658)}

GRIP_BACK_Z = -17.7             # the back of the grip (35.4 thick, centred on z = 0)

# the old estimates the tab, its paddle and the cover screws were drawn against (popassembly.py); they move with the cover
OLD_COVER_BOTTOM, OLD_CUP_Z = -50.0, -98.0


class CarScene:
  def __init__(self, D: float = D_REF, front_round: float = 8.0, corner_r: float = 25.0):
    self.D = float(D)
    self.t = (self.D - D_FITS[0]) / (D_FITS[1] - D_FITS[0])
    self.front_round = front_round
    self.corner_r = corner_r
    self.p = {k: self._lerp(k) for k in _A}
    n = self.p["N"]
    self.p["N"] = n / np.linalg.norm(n)

  def _lerp(self, k):
    a, b = np.array(_A[k], float), np.array(_B[k], float)
    return a + self.t * (b - a)

  # ----- the key -----
  @property
  def key(self) -> np.ndarray:
    return self.p["KEY"]

  @property
  def key_clock(self) -> float:
    return math.degrees(math.atan2(self.key[1], self.key[0]))

  @property
  def key_r(self) -> float:
    return float(math.hypot(self.key[0], self.key[1]))

  @property
  def key_tilt(self) -> float:
    n = self.p["N"]
    rad = np.array([self.key[0], self.key[1], 0.0]) / self.key_r
    return math.degrees(math.atan2(n[2], n @ rad))

  def key_args(self):
    return (self.key_clock, self.key_r, float(self.key[2]), self.key_tilt)

  def key_parts(self) -> dict:
    import carref as CR
    a = self.key_args()
    b = CR.bezel(*a)
    return {"key bulge and bezel": CR.key_bulge(*a) + b["ring"] + b["chrome"] + b["face"], "the key in it": CR.key_in(*a),
            "room to turn the key": CR.key_turn_room(*a)}

  # ----- the lower column cover -----
  @property
  def cover_bottom(self) -> float:
    return float(self.p["CUP"][1])

  @property
  def cover_front_z(self) -> float:
    return float(self.p["HOOK"][2] - 3.0)

  @property
  def cover_right_x(self) -> float:
    return float(self.p["CUP"][0] + self.corner_r)

  def column_cover(self, back: float = 260.0) -> Manifold:
    """The column covers near the wheel: a rounded box (the underside flat at the screw cup's height, the bottom corners
    rounded so the cup sits where the flat underside starts to curve up the side), its front edges rounded."""
    yb, xr, zf, r = self.cover_bottom, self.cover_right_x, self.cover_front_z, self.corner_r
    yt = 75.0
    w, h = 2 * xr, yt - yb
    cs = CrossSection.square((w - 2 * r, h - 2 * r), center=True).offset(r, circular_segments=64).translate((0.0, (yt + yb) / 2))
    f = self.front_round
    body = cs.extrude(back - f).translate((0, 0, zf - back))
    # the rounded front: the section shrunk by f at the very front, blended over f
    lip = Manifold.batch_hull([cs.offset(-f, circular_segments=48).extrude(0.2).translate((0, 0, zf - 0.2)),
                               cs.extrude(0.2).translate((0, 0, zf - f - 0.2))]) if f > 0 else Manifold()
    return body + lip

  # ----- the cover on the back of the steering wheel (turns with the wheel) -----
  @property
  def back_cover_rim(self) -> tuple:
    h = self.p["HOOK"]
    return float(math.hypot(h[0], h[1])), float(h[2])

  def back_cover(self) -> Manifold:
    """Everywhere the back cover goes as the wheel turns: a body of revolution through the round hole (r, z) and out to
    the rim (the tape's hook), kept at the hole's radius from there forward to the hub."""
    rh = self.p["RH"]
    r_h, z_h = float(math.hypot(rh[0], rh[1])), float(rh[2])
    r_r, z_r = self.back_cover_rim
    pts = [(0.0, -25.0), (r_h, -25.0), (r_h, z_h), (r_r, z_r), (0.0, z_r)]
    return revolve(pts, 0.0, 360.0, step_deg=2.0)

  # ----- the knee bolster / dash face below the column -----
  @property
  def dash_z(self) -> float:
    return float(self.p["HOOK"][2] - 90.0)

  def bolster(self, gap: float = 3.0) -> Manifold:
    wall = box(-300.0, 300.0, -400.0, 120.0, self.dash_z - 40.0, self.dash_z)
    yb, xr = self.cover_bottom, self.cover_right_x
    opening = Manifold.batch_hull([box(-xr - gap, xr + gap, yb - gap + self.corner_r, 120.0, self.dash_z - 41, self.dash_z + 1),
                                   box(-xr - gap + self.corner_r, xr + gap - self.corner_r, yb - gap, 120.0, self.dash_z - 41, self.dash_z + 1)])
    return wall - opening

  # ----- the adjustment tab and the cover's screws, moved with the cover -----
  @property
  def shift(self) -> tuple:
    return (0.0, self.cover_bottom - OLD_COVER_BOTTOM, float(self.p["CUP"][2]) - OLD_CUP_Z)

  def moved(self, m: Manifold) -> Manifold:
    return m.translate(self.shift)

  def cover_screws(self) -> list:
    """(name, (x, z) on the cover's underside, (x, z) tolerance, tab kind): the cup screw from the photos, the other two
    where Honda's drawing puts them relative to it (their sideways places are less certain)."""
    cup = self.p["CUP"]
    dz = self.shift[2]
    return [("4 x 16 self-tapping under the key cylinder", (float(cup[0]), float(cup[2])), (4.0, 4.0), "cup"),
            ("M5 x 12 screw-washer beside the tab's slot", (1.0, -175.0 + dz), (12.0, 15.0), "slim"),
            ("4 x 16 self-tapping behind the paddle", (-18.0, -125.0 + dz), (12.0, 20.0), None)]

  # ----- the wiper stalk -----
  def stalk(self, down: float = 36.0, up: float = 10.0, step: float = 4.0, r: float = 11.0) -> Manifold:
    import columnassembly as CA
    base, tip = self.p["SH"], self.p["ST"]
    d = tip - base
    L = float(np.linalg.norm(d))
    d /= L
    ax = np.cross(d, [0.0, 1.0, 0.0])
    ax /= np.linalg.norm(ax)
    out = []
    for a in np.arange(-up, down + 1e-9, step):
      th = math.radians(-a)
      v = tip - base
      v_rot = v * math.cos(th) + np.cross(ax, v) * math.sin(th) + ax * np.dot(ax, v) * (1 - math.cos(th))
      out.append(CA.rod(base, base + v_rot, r))
    return union(out)

  def summary(self) -> dict:
    r_r, z_r = self.back_cover_rim
    return {"D": self.D, "key centre": tuple(round(float(v), 1) for v in self.key), "key clock": round(self.key_clock, 1),
            "key r": round(self.key_r, 1), "key tilt": round(self.key_tilt, 1), "cover underside y": round(self.cover_bottom, 1),
            "cover front z": round(self.cover_front_z, 1), "cover right x": round(self.cover_right_x, 1),
            "back cover rim r, z": (round(r_r, 1), round(z_r, 1)), "dash face z": round(self.dash_z, 1),
            "stalk end": tuple(round(float(v), 1) for v in self.p["ST"])}
