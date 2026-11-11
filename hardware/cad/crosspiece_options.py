"""Frame plate v3: three ways for the new crosspiece, drawn for you to pick from (11 Nov).

From your marked paper (11 Nov): the old crossbar at the wheel end is cut off at your purple line, and a new
crosspiece goes where you drew it in yellow: right behind the block, across to the long piece. It folds up about
45 degrees with the cover (your photos of 6 Nov, from the key side), into the space above the tilt lever's tab, so
the tab passes under it. Over the tab, the fold's lower edge is cut back so the tab stays clear.

The three options differ only in the line it folds up along (numbered, not lettered, so they don't get mixed up with
the trim lines A, B and C printed on the v2 paper):
  1  straight across, right behind the block
  2  on a slant, 16 mm nearer the wheel on the door side (the way your yellow line leans)
  3  on a slant the other way, 16 mm nearer the wheel on the key side

Frame here (mm): x toward the driver's door, y toward the dash, 0 at the cup screw, z up toward the cover (the plate
lies under the cover, z -6 to 0). That is rightarm.py's plate frame with z turned over, so for the 3D pictures it is
mirrored into the car's own frame (x to the right, y forward, z up). The cover's turn and the tab are rough, from
your photos (5 mm or worse); the paper template checks them.

  python3 crosspiece_options.py     # writes ../report/frame-plate-v3-options.png
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402
from manifold3d import Manifold  # noqa: E402

import render as R  # noqa: E402
from cadlib import box, cyl  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "..", "report")

T = 6.0                                  # plate thickness (v5)
BLOCK = (-60.0, 28.0, -14.0, 50.0)       # x0, x1, y0, y1: the block round the cup screw, unchanged
LONG_X, LONG_END = (88.0, 106.0), 70.0   # the long piece on the door side, and its dash end
STEM_X = 8.0                             # where the crosspiece starts on the key side (the old stem's key-side edge)
CUT_Y = -39.0                            # your purple line
W = 25.0                                 # the folded strip's width up the slope: from the block to your purple line
UP = 45.0                                # how far it folds up
TAB = (36.0, 68.0, -40.0, -6.0, -12.0, -3.0)   # the tilt lever's tab, rough: x0, x1, y0, y1 (it sticks out toward the wheel), z0, z1
CLEAR = 2.0                              # kept clear round the tab
RECEIVER = (-47.0, 3.0, 15.0, 45.4)      # the receiver tube under the block (v5)
TUBE_DEPTH = 41.4
V2 = [(-60, -14), (2, -14), (8, -20), (8, -76), (106, -76), (106, 70), (88, 70), (88, -40), (82, -46), (34, -46),
      (28, -40), (28, 50), (-60, 50)]   # the v2 paper's outline

OPTIONS = {
  "1": dict(title="1: straight across", fold=((STEM_X, -14.0), (LONG_X[1], -14.0)),
            note="Folds up right behind the block, straight across."),
  "2": dict(title="2: slanted, door side nearer the wheel", fold=((STEM_X, -14.0), (LONG_X[1], -30.0)),
            note="Right behind the block on the key side, 16 mm nearer\nthe wheel on the door side (your yellow line's lean)."),
  "3": dict(title="3: slanted, key side nearer the wheel", fold=((STEM_X, -30.0), (LONG_X[1], -14.0)),
            note="16 mm nearer the wheel on the key side,\nright behind the block on the door side."),
}
Z = np.array([0.0, 0.0, 1.0])
BLUE, BLUE_DARK, BLUE_LIGHT, BLUE_MID = "#3a80e0", "#1f4e9a", "#d6e5f8", "#8cb8f0"
RED, PURPLE = "#c0392b", "#7b61ff"


def axes(fold):
  """p0, the fold's length, a: along the fold toward the door, b: across it in the plate's plane, toward the wheel."""
  p0, p1 = np.array(fold[0]), np.array(fold[1])
  a2 = (p1 - p0) / np.linalg.norm(p1 - p0)
  b2 = np.array([a2[1], -a2[0]])
  if b2[1] > 0:
    b2 = -b2
  return p0, float(np.linalg.norm(p1 - p0)), np.r_[a2, 0.0], np.r_[b2, 0.0]


def frame(fold, angle=0.0):
  """3x4 matrix from local (s along the fold, t across it toward the wheel, n its normal) to the plate frame, with the
  (t, n) plane turned up by `angle` about the fold line."""
  p0, _, a, b = axes(fold)
  c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
  e_t, e_n = b * c + Z * s, -b * s + Z * c
  return np.column_stack([a, e_t, e_n, np.r_[p0, 0.0]])


def inverse(m):
  r, p = m[:, :3], m[:, 3]
  return np.column_stack([r.T, -r.T @ p])


def in_front(m: Manifold, fold) -> Manifold:
  """The part of m on the dash side of the fold line."""
  p0, _, _, b = axes(fold)
  return m.trim_by_plane(tuple(-b), float(-b[:2] @ p0))


def fold_y(fold, x):
  p0, _, a, _ = axes(fold)
  return float(p0[1] + (x - p0[0]) / a[0] * a[1])


def across(m: Manifold) -> Manifold:
  """m between the crosspiece's two ends, x STEM_X to the long piece's outer edge."""
  return m ^ box(STEM_X, LONG_X[1], -300.0, 300.0, -300.0, 300.0)


def flat_parts(fold) -> Manifold:
  """The block, the long piece, and the flat bit between the block's back edge and the fold, less the tab's room."""
  body = box(BLOCK[0], BLOCK[1], BLOCK[2], BLOCK[3], -T, 0.0)
  body = body + in_front(box(LONG_X[0], LONG_X[1], -80.0, LONG_END, -T, 0.0), fold)
  body = body + in_front(box(STEM_X, LONG_X[1], -80.0, BLOCK[2] + 0.01, -T, 0.0), fold)
  x0, x1, y0, y1, _, _ = TAB
  return body - box(x0 - CLEAR, x1 + CLEAR, y0 - CLEAR, y1 + CLEAR, -50.0, 50.0)


def notch_t() -> float:
  """How far up the slope the fold's lower edge is cut back over the tab: until its underside is CLEAR above the tab."""
  u = math.radians(UP)
  return (TAB[5] + CLEAR + T * math.cos(u)) / math.sin(u)


def notch(fold) -> Manifold:
  x0, x1 = TAB[0] - CLEAR, TAB[1] + CLEAR
  return box(x0, x1, -300.0, 300.0, -300.0, 300.0) ^ box(-300.0, 300.0, -40.0, notch_t(), -40.0, 40.0).transform(
    frame(fold, UP).tolist())


def folded(fold) -> Manifold:
  """The strip that folds up, with the hinge filled, less the notch over the tab."""
  _, length, _, _ = axes(fold)
  ramp = box(-20.0, length + 20.0, 0.0, W, -T, 0.0).transform(frame(fold, UP).tolist())
  hinge = Manifold.batch_hull([box(-20.0, length + 20.0, -0.3, 0.0, -T, 0.0).transform(frame(fold, 0.0).tolist()),
                               box(-20.0, length + 20.0, 0.0, 0.3, -T, 0.0).transform(frame(fold, UP).tolist())])
  return across(ramp + hinge) - notch(fold)


def slots(fold) -> Manifold:
  cup = Manifold.batch_hull([cyl(3.0, -40, 40, x=-7.0, y=0.0), cyl(3.0, -40, 40, x=7.0, y=0.0)])
  long_slot = Manifold.batch_hull([cyl(3.0, -40, 40, x=97.0, y=fold_y(fold, 97.0) + 9.0),
                                   cyl(3.0, -40, 40, x=97.0, y=59.0)])
  return cup + long_slot


def plate(fold) -> Manifold:
  return (flat_parts(fold) + folded(fold)) - slots(fold)


def cover(fold) -> Manifold:
  """The cover's underside, rough, as a solid for the side view: flat in front of the fold line, turning up 45 degrees
  behind it."""
  front = box(-400.0, 400.0, -400.0, 0.0, 0.0, 60.0).transform(frame(fold, 0.0).tolist())
  behind = box(-400.0, 400.0, 0.0, 120.0, 0.0, 120.0).transform(frame(fold, UP).tolist())
  return (front + behind) ^ box(-75.0, 125.0, -60.0, 80.0, 0.0, 40.0)


def cover_skin(fold) -> Manifold:
  """The cover's underside, rough, as a thin skin behind the plate for the 3D pictures."""
  front = box(-400.0, 400.0, -400.0, 0.0, 0.0, 2.0).transform(frame(fold, 0.0).tolist())
  behind = box(-400.0, 400.0, 0.0, 34.0, 0.0, 2.0).transform(frame(fold, UP).tolist())
  return (front + behind) ^ box(-68.0, 114.0, -70.0, 72.0, -1.0, 40.0)


def tab() -> Manifold:
  x0, x1, y0, y1, z0, z1 = TAB
  return box(x0, x1, y0, y1, z0, z1)


def tube() -> Manifold:
  x0, x1, y0, y1 = RECEIVER
  return box(x0, x1, y0, y1, -TUBE_DEPTH, -T)


# ----- the 3D pictures, in the car's frame -----

TO_CAR = np.array([[-1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]])
VIEW = R.look((0.8, -0.38, -0.46), (0.0, 0.0, 1.0))    # from the key side, a little behind (the wheel's side) and below
SIZE, MARGIN = (760, 600), 0.03


def car(p):
  return np.asarray(p, dtype=float) @ TO_CAR[:, :3].T


def scene(fold):
  parts = [(plate(fold), (0.24, 0.52, 0.90)), (tab(), (0.16, 0.16, 0.18)), (tube(), (0.66, 0.68, 0.72)),
           (cover_skin(fold), (0.84, 0.84, 0.84))]
  return [(m.transform(TO_CAR.tolist()), c) for m, c in parts]


def screen_box():
  """The smallest picture frame that holds all three options, so they come out at the same scale and place."""
  pts = np.concatenate([np.asarray(m.to_mesh().vert_properties)[:, :3] for opt in OPTIONS.values()
                        for m, _ in scene(opt["fold"])]) @ VIEW.T
  return pts.min(axis=0), pts.max(axis=0)


def anchors(lo, hi):
  """Two specks too small to see, at the frame's corners (in the car's frame)."""
  return [(box(*sum(((c, c + 0.01) for c in VIEW.T @ np.array([sx, sy, 0.0])), ())), (1.0, 1.0, 1.0))
          for sx, sy in ((lo[0], lo[1]), (hi[0], hi[1]))]


def projector(parts):
  """Plate-frame points to pixels in R.render's picture of `parts` (the same scale and centre it works out)."""
  pts = np.concatenate([np.asarray(m.to_mesh().vert_properties)[:, :3] for m, _ in parts]) @ VIEW.T
  lo, hi = pts.min(axis=0), pts.max(axis=0)
  w, h = SIZE
  scale = min(w * (1 - 2 * MARGIN) / (hi[0] - lo[0]), h * (1 - 2 * MARGIN) / (hi[1] - lo[1]))
  cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2

  def f(p):
    q = car(p) @ VIEW.T
    return (q[..., 0] - cx) * scale + w / 2, h / 2 - (q[..., 1] - cy) * scale
  return f


LABEL_BOX = dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9)


def view3d(ax, fold, frame_box):
  parts = scene(fold) + anchors(*frame_box)
  ax.imshow(R.render(parts, VIEW, size=SIZE, margin=MARGIN))
  px = projector(parts)

  def label(p, text, to, color="#222222"):
    u, v = px(np.array(p, dtype=float))
    ax.annotate(text, (u, v), to, fontsize=9, ha="center", va="center", color=color, bbox=LABEL_BOX,
                arrowprops=dict(arrowstyle="-", color="#444444", lw=0.8))
  def on_slope(s, t, n):
    return (frame(fold, UP) @ np.array([s, t, n, 1.0])).tolist()
  label(on_slope(0.5, 9.0, -3.0), "folds up 45°", (120, 115), color=RED)
  label(on_slope(-16.0, 20.0, 2.0), "cover (rough)", (330, 55), color="#555555")
  label((0.0, 0.0, -T), "cup screw", (560, 120))
  label((44.0, -36.0, -12.0), "tilt lever's tab", (80, 470))
  label((-47.0, 30.0, -25.0), "receiver", (705, 395))
  label((97.0, 40.0, -T), "second screw's slot", (610, 578))
  ax.set_xlim(0, SIZE[0])
  ax.set_ylim(SIZE[1], 0)
  ax.set_axis_off()


# ----- the side view and the paper -----

PERM_YZ = [[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]]   # (x, y, z) -> (y, z, x): look along x


def fill(ax, cs, **kw):
  for poly in cs.to_polygons():
    ys, zs = zip(*(list(poly) + [poly[0]]))
    ax.fill(ys, zs, **kw)


def section(ax, fold, x_cut=52.0):
  """Side view from the key side: the cut through the tab (solid) over the whole plate's outline (pale)."""
  fill(ax, cover(fold).transform(PERM_YZ).slice(x_cut), fc="#dcdcdc", ec="#9a9a9a", lw=0.8, zorder=1)
  fill(ax, tube().transform(PERM_YZ).project(), fc="#ececec", ec="#b0b0b0", lw=0.8, zorder=2)
  fill(ax, plate(fold).transform(PERM_YZ).project(), fc=BLUE_LIGHT, ec="#8fb3e3", lw=0.8, zorder=2)
  fill(ax, plate(fold).transform(PERM_YZ).slice(x_cut), fc=BLUE, ec=BLUE_DARK, lw=0.9, zorder=3)
  fill(ax, tab().transform(PERM_YZ).slice(x_cut), fc="#2b2b2b", ec="#2b2b2b", lw=0.8, zorder=4)
  fy = fold_y(fold, x_cut)
  r = 13.0
  th = np.linspace(180.0, 180.0 - UP, 20)
  ax.plot(fy + r * np.cos(np.radians(th)), r * np.sin(np.radians(th)), color=RED, lw=1.0, zorder=5)
  ax.plot([fy - r - 4, fy], [0, 0], color=RED, lw=0.8, ls=(0, (3, 2)), zorder=5)
  ax.text(fy - r - 5, 3.0, "45°", color=RED, fontsize=9, ha="right", va="bottom", zorder=5)
  ax.text(62, 28, "cover (rough)", ha="right", va="center", fontsize=8.5, color="#666666")
  ax.text(-26, -15.5, "tilt lever's tab", ha="center", va="top", fontsize=8.5, color="#2b2b2b")
  ax.text(30, -26, "receiver", ha="center", va="center", fontsize=8.5, color="#777777")
  ax.text(64, -4.5, "plate", ha="left", va="center", fontsize=8.5, color=BLUE_DARK)
  ax.text(-62, -45, "< wheel", fontsize=8.5, color="#555555", va="bottom")
  ax.text(84, -45, "dash >", fontsize=8.5, color="#555555", ha="right", va="bottom")
  ax.set_xlim(-64, 86)
  ax.set_ylim(-46, 40)
  ax.set_aspect("equal")
  ax.set_xticks([])
  ax.set_yticks([])


def paper(fold):
  """The paper's outline: the flat parts, and the folding strip laid flat behind the fold line."""
  p0, _, a, b = axes(fold)
  flat2d = flat_parts(fold).project()
  strip_local = folded(fold).transform(inverse(frame(fold, UP)).tolist())
  strip_local = strip_local ^ box(-300.0, 300.0, 0.0, 300.0, -50.0, 50.0)     # drop the hinge's filler
  strip2d = strip_local.project().transform([[a[0], b[0], p0[0]], [a[1], b[1], p0[1]]])
  return flat2d, strip2d


def paper_view(ax, fold):
  """Turned like your photo of 11 Nov: the wheel end on the left, the key side at the top."""
  p0, length, a, _ = axes(fold)
  ox, oy = zip(*(V2 + [V2[0]]))
  ax.plot(oy, ox, color="#b5b5b5", lw=1.0, ls=(0, (4, 3)), zorder=1)
  flat2d, strip2d = paper(fold)
  for cs, fc in ((flat2d, BLUE_LIGHT), (strip2d, BLUE_MID)):
    for poly in cs.to_polygons():
      px, py = zip(*(list(poly) + [poly[0]]))
      ax.fill(py, px, fc=fc, ec=BLUE_DARK, lw=1.2, zorder=2)
  q1 = p0 + a[:2] * length
  ax.plot([p0[1], q1[1]], [p0[0], q1[0]], color=RED, lw=1.8, ls=(0, (5, 3)), zorder=4)
  ax.plot([CUT_Y, CUT_Y], [-66, 112], color=PURPLE, lw=1.3, zorder=0)
  x0, x1, y0, y1, _, _ = TAB
  ax.add_patch(plt.Rectangle((y0, x0), y1 - y0, x1 - x0, fc="none", ec="#2b2b2b", lw=1.0, ls=(0, (2, 2)), zorder=5))
  ax.text((y0 + y1) / 2, (x0 + x1) / 2, "tab", fontsize=7.5, color="#2b2b2b", ha="center", va="center", zorder=5)
  rx0, rx1, ry0, ry1 = RECEIVER
  ax.add_patch(plt.Rectangle((ry0, rx0), ry1 - ry0, rx1 - rx0, fc="none", ec="#777777", lw=0.8, ls=(0, (1, 2)), zorder=5))
  ax.text((ry0 + ry1) / 2, (rx0 + rx1) / 2, "receiver", fontsize=7.5, color="#555555", ha="center", va="center", zorder=5)
  sy = fold_y(fold, 97.0) + 9.0
  ax.add_patch(plt.Rectangle((sy - 3, 94), 59 + 3 - sy + 3, 6, fc="white", ec="#555555", lw=0.8, zorder=5))
  ax.add_patch(plt.Rectangle((-3, -10), 6, 20, fc="white", ec="#555555", lw=0.8, zorder=5))
  ax.text(0, -12, "cup screw", fontsize=7.5, color="#444444", ha="center", va="bottom", zorder=5)
  ax.text(CUT_Y - 2, -62, "your cut", fontsize=7.5, color=PURPLE, ha="right", va="center", zorder=5)
  ax.text(-88, -30, "KEY\nSIDE", fontsize=7.5, color="#444444", ha="center", va="center", zorder=5)
  ax.text(-88, 97, "DOOR\nSIDE", fontsize=7.5, color="#444444", ha="center", va="center", zorder=5)
  ax.set_xlim(-98, 76)
  ax.set_ylim(114, -68)
  ax.set_aspect("equal")
  ax.set_xticks([])
  ax.set_yticks([])


def main():
  os.makedirs(REPORT, exist_ok=True)
  fig = plt.figure(figsize=(15.0, 15.2), dpi=110)
  gs = GridSpec(3, 3, figure=fig, height_ratios=[1.0, 1.08, 0.78], hspace=0.24, wspace=0.04,
                left=0.01, right=0.99, top=0.93, bottom=0.03)
  frame_box = screen_box()
  for i, (k, opt) in enumerate(OPTIONS.items()):
    ax = fig.add_subplot(gs[0, i])
    view3d(ax, opt["fold"], frame_box)
    ax.set_title(opt["title"], fontsize=14, fontweight="bold", color=BLUE_DARK)
    ax.text(0.01, -0.01, opt["note"], transform=ax.transAxes, fontsize=9.5, color="#333333", va="top")
    ax = fig.add_subplot(gs[1, i])
    paper_view(ax, opt["fold"])
    ax.set_title(f"{k}: the paper, turned like your photo (wheel end left)", fontsize=9.5)
  ax = fig.add_subplot(gs[2, 0:2])
  section(ax, OPTIONS["1"]["fold"])
  ax.set_title("All three from the side, cut through the tab (from the key side, like your photos of 6 Nov): the "
               "crosspiece lies against\nthe cover where it turns up, in the space above the tab", fontsize=9.5)
  ax = fig.add_subplot(gs[2, 2])
  ax.set_axis_off()
  ax.text(0.02, 0.95,
          "Blue: the plate (in the paper, the darker strip\nis the part that folds up).\n"
          "Grey: the cover and the receiver.\n"
          "Black: the tilt lever's tab.\n"
          "Red dashes: where it folds up.\n"
          "Purple: your cut line.\n"
          "Grey dashes: the paper you have (v2).\n\n"
          "Over the tab, the fold's bottom edge is cut\nback so the tab stays 2 mm clear.\n\n"
          "The cover and the tab are rough, from your\nphotos (5 mm or worse). The paper checks them.",
          transform=ax.transAxes, fontsize=9.5, color="#333333", va="top", linespacing=1.35)
  fig.suptitle("Frame plate v3: where the new crosspiece folds up. Pick 1, 2 or 3, or tell me what's different.\n"
               "Top: the plate on the cover, from the key side, a little behind and below (like your photos of "
               "6 Nov).", fontsize=13)
  out = os.path.join(REPORT, "frame-plate-v3-options.png")
  fig.savefig(out)
  print(out)


if __name__ == "__main__":
  main()
