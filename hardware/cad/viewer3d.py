"""
The right arm mount v6, the fit print, as a 3D model to turn round in a web page (3 Nov 2026). The printed parts are
the CAD parts exactly (the same shapes as the print files), where they go on the car: the frame plate v5, the arm,
the motor carrier and the teeth; with the motor, its four screws, the gear, the zip ties, the wing bolts, washers and
nuts. Round
them the steering wheel grip and the column cover (the cover approximate). The board on the motor's back is a
plain box, as in the review pictures. A slider takes it apart in the order it goes together (README steps 1 to 4).

The page draws with WebGL itself (no library, nothing fetched but its fonts): viewer3d_page.html is the page,
this file puts the parts and the steps into it.

  python3 viewer3d.py      # writes ../report/arm-3d.html
"""
import base64
import json
import os
import sys

import numpy as np

import carphoto as CP
import carscene as CS
import midteeth as MT
import rightarm as RA
import rightcheck as RC
from cadlib import union

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, "viewer3d_page.html")
OUT = os.path.join(HERE, "..", "report", "arm-3d.html")
Q = 100.0                      # positions stored in 0.01 mm steps

U3 = (float(RA.U[0]), float(RA.U[1]), 0.0)
V3 = (float(RA.V[0]), float(RA.V[1]), 0.0)


def scale(k: float, v) -> tuple:
  return tuple(k * c for c in v)


def mv(step: int, s0: float, s1: float, vec) -> list:
  """A move: during step `step` (from s0 to s1 of it) the part goes the last `vec` mm (steering wheel frame) into
  its place. Before it, the part sits vec away."""
  return [step, s0, s1] + [round(float(c), 2) for c in vec]


# the moves, in the order it goes together (README steps 1 to 4); a part on another part takes that part's moves too
M_PLATE = [mv(1, 0.0, 1.0, (0.0, -55.0, 0.0))]                    # up onto the cover's two screws
M_TEETH = [mv(2, 0.0, 0.6, (0.0, 0.0, -45.0))]                    # onto the back of the grip
M_ARM = [mv(7, 0.35, 0.85, (80.0, 0.0, 0.0))]                     # into the receiver from the key side, all on it
M_UP = [mv(9, 0.0, 0.6, (0.0, 0.0, RA.DZ_OUT))]                   # the motor slid up the groove into the teeth
M_CARRIER = M_ARM + M_UP + [mv(5, 0.0, 1.0, (0.0, 0.0, 100.0))]   # down the tower's tube from the top, off the car

STEPS = [
  ("Fit the frame plate on the column cover's two screws, with washers: the cup slot on the key side, slot 1 on the "
   "other. Its flat side goes up against the cover; the square tube hangs underneath, the printed labels facing down."),
  ("Fit the teeth on the grip just above 4 o'clock (one wrap of silicone tape under them), between the two spokes, "
   "two zip ties through the middle slot, heads tucked inside the rim."),
  ("Off the car: the motor on the carrier, against the outside of its plate: four M3 x 10 from the side with the "
   "four round pads, the motor's boss in the big hole. Then the gear on the shaft (set screw on the flat)."),
  ("The slide's M5 nut into the slot in the carrier's bar, from the motor's side, its flats along the bar."),
  ("The carrier's bar down the tower's tube from the top, all the way, till the carrier sits on the tower."),
  ("The slide's wing bolt, a fender washer under its wings, in through the groove up the tower's outer wall and a few "
   "turns into that nut. Now the carrier can't come out."),
  ("The arm's M5 nut into the slot in the top of its bar, flats along the bar (it only goes in that way). Then the "
   "arm, with all of that on it, into the frame plate's square tube from the key side."),
  ("The arm's wing bolt, a fender washer under its wings, in through the long groove in the tube's wall on your side "
   "and a few turns into the arm's nut. Now the arm can't come out. Slide the arm across by it till the gear lines up "
   "with the teeth, and tighten: it pulls the arm against the wall."),
  ("Loosen the motor's wing bolt, slide it up the groove till the gear is all the way into the teeth, back it down "
   "1 mm (one tick on the bar at the tower's top) and tighten: lane keeping on. Down till the carrier sits on the "
   "tower: off."),
]

# display colours (screen RGB), specular strength, shininess
PLATE = ((0.72, 0.75, 0.79), 0.12, 30)
BLUE = ((0.35, 0.55, 0.85), 0.12, 30)
GREEN = ((0.43, 0.70, 0.44), 0.12, 30)
TEETH = ((0.89, 0.58, 0.27), 0.12, 30)
GEAR = ((0.96, 0.67, 0.32), 0.12, 30)
STEEL = ((0.70, 0.72, 0.76), 0.55, 70)
MOTOR = ((0.17, 0.17, 0.19), 0.25, 40)
BOARD = ((0.22, 0.25, 0.29), 0.15, 30)
NYLON = ((0.15, 0.15, 0.16), 0.15, 30)
GRIP = ((0.26, 0.26, 0.28), 0.10, 20)
COVER = ((0.42, 0.44, 0.47), 0.05, 10)


BOLT = "M5 x 20 stainless wing bolt. "
NOTES = {
  "cover": ("The car's column cover, drawn roughly from your photos and measurements. The frame plate hangs on its "
            "two screws."),
  "grip": "The grip, 367 mm across and 33 mm thick, the steering wheel straight.",
  "plate": ("v5. 166 x 96 x 41 mm. Hangs on the column cover's two screws (the cup slot on the key side, slot 1 on "
            "the other). The square tube underneath is the receiver, its bore 20 wide: the arm slides in from the key "
            "side, held by a wing bolt through the long groove in the wall on your side. The labels (KEY, WHEEL, 1), "
            "cut into the plate, face down."),
  "teeth": ("v3: on the grip between the two spokes, just above 4 o'clock, on one wrap of silicone tape; the gear meets "
            "them from outside the rim. The ends stop just past the last teeth, clear of the spokes' joins."),
  "zips": "Two zip ties round the grip through the teeth's middle slot, heads tucked inside the rim.",
  "arm": ("v6, the fit print. Its 20 x 30 bar goes into the frame plate's square tube (47 mm in as drawn, 17.5 "
          "further in or out by the groove: how far right the motor sits), its M5 nut in the slot in its top; just "
          "outside, the arm is 50 mm deep along the column so it doesn't twist. The tower at its end runs along the "
          "column: a square tube, closed all round, that the motor carrier's bar slides in, with the motor's groove "
          "up its outer wall."),
  "carrier": ("v6. The motor bolts to the outside of its plate. Its long bar slides along the column in the tower's "
              "tube, in from the top, 31 mm of travel; the slide's M5 nut sits in a slot across it, and the ticks on "
              "its outer face, read at the tower's top, show how far up it is (the long one in the middle is the drawn "
              "depth)."),
  "motor": ("42 x 42 x 40 mm, against the outside of the carrier's plate, the shaft through the big hole pointing in "
            "at the steering wheel's middle."),
  "board": ("On the motor's back. Drawn as a plain box (as in the review pictures): the real board's shape and size "
            "may differ."),
  "screws": "Button heads, in from the side with the four round pads, into the motor.",
  "gear": "On the motor's shaft, set screw on the flat. Slid up the groove, it sits in the teeth.",
  "rbolt": (BOLT + "The arm's slide: in through the long groove in the square tube's wall on your side, screwed into "
            "the nut in the arm's bar. Loosen it and slide the arm across by it; tighten it to hold (it pulls the bar "
            "against the wall). The groove's ends keep the arm in."),
  "rwasher": "Fender washer under the arm's wing bolt, wider than the groove.",
  "rnut": "M5 nut in the slot in the top of the arm's bar, its flats along the bar so it can't turn; the frame plate above keeps it in.",
  "sbolt": (BOLT + "The slide: in the groove up the tower's outer wall, screwed into the nut in the carrier's bar. "
            "Loosen it and slide the motor by it along the column (lane keeping on and off, and how deep the gear "
            "sits); tighten it to hold. The groove's ends keep the carrier in."),
  "swasher": "Fender washer under the slide's wing bolt, wider than the groove.",
  "snut": "M5 nut in the slot across the carrier's bar, its flats along the bar so it can't turn; the slide's wing bolt screws into it.",
}


def parts() -> list:
  """The parts in the steering wheel frame: (id, name, note, chip, pickable, [(manifold, look, alpha)], moves)."""
  hw = RC.hardware(0.0)
  mp = [m for m, _ in CP.motor_parts(0.0)]
  motor = union([mp[i] for i in (0, 1, 2, 3)])                     # the end caps, the body and the boss
  heads = union([mp[i] for i in (5, 8, 11, 14)])                   # the four M3 button heads on the pads
  zips = union([m for m, _ in CP.zip_ties()])
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=18)).rotate((0.0, 0.0, RA.THETA))      # the 20 set, the one on the car
  motor_moves = M_CARRIER + [mv(3, 0.0, 0.4, scale(35.0, U3))]
  slide_moves = M_ARM + M_UP + [mv(6, 0.0, 1.0, scale(25.0, U3))]   # waits outside the groove, then in along it
  n = NOTES
  return [
    ("cover", "Column cover (the car)", n["cover"], "car", False,
     [(CS.CarScene(D=125.0).column_cover(back=130.0), COVER, 0.26)], []),
    ("grip", "Steering wheel grip (the car)", n["grip"], "car", True, [(RC.grip(), GRIP, 1.0)], []),
    ("plate", "Frame plate v5 (plate 11)", n["plate"], "plate", True,
     [(RA.plate_to_wheel(RA.frame_plate_v5()), PLATE, 1.0)], M_PLATE),
    ("teeth", "Steering wheel teeth (plate 9)", n["teeth"], "teeth", True, [(teeth, TEETH, 1.0)], M_TEETH),
    ("zips", "Zip ties (2)", n["zips"], "teeth", True, [(zips, NYLON, 1.0)],
     M_TEETH + [mv(2, 0.6, 1.0, scale(30.0, U3))]),
    ("arm", "Arm with its tower (plate 12)", n["arm"], "arm", True, [(RA.arm(), BLUE, 1.0)], M_ARM),
    ("carrier", "Motor carrier (plate 12)", n["carrier"], "carrier", True, [(RA.carrier(), GREEN, 1.0)], M_CARRIER),
    ("motor", "Stepper motor (17HS15-1504S-X1)", n["motor"], "motor", True,
     [(motor, MOTOR, 1.0), (mp[4], STEEL, 1.0)], motor_moves),
    ("board", "Motor board (StepperServoCAN)", n["board"], "motor", True,
     [(RA.motor_and_gear(0.0)["board"], BOARD, 1.0)], motor_moves),
    ("screws", "Motor screws (4 x M3 x 10)", n["screws"], "motor", True, [(heads, STEEL, 1.0)],
     M_CARRIER + [mv(3, 0.4, 0.65, scale(-15.0, U3))]),
    ("gear", "Gear", n["gear"], "motor", True, [(RA.motor_and_gear(0.0)["gear"], GEAR, 1.0)],
     M_CARRIER + [mv(3, 0.65, 1.0, scale(-25.0, U3))]),
    ("rbolt", "Arm wing bolt", n["rbolt"], "bolts", True, [(hw["receiver bolt"], STEEL, 1.0)],
     M_PLATE + [mv(8, 0.0, 1.0, (0.0, 0.0, 25.0))]),             # waits by the groove, then in along the column
    ("rwasher", "Arm washer (fender washer)", n["rwasher"], "bolts", True, [(hw["receiver washer"], STEEL, 1.0)],
     M_PLATE + [mv(8, 0.0, 1.0, (0.0, 0.0, 25.0))]),
    ("rnut", "Arm nut (M5)", n["rnut"], "bolts", True, [(hw["receiver nut"], STEEL, 1.0)],
     M_ARM + [mv(7, 0.0, 0.35, (0.0, 25.0, 0.0))]),
    ("snut", "Motor nut (M5)", n["snut"], "bolts", True, [(hw["slide nut"], STEEL, 1.0)],
     M_CARRIER + [mv(4, 0.0, 1.0, scale(20.0, V3))]),
    ("sbolt", "Motor wing bolt", n["sbolt"], "bolts", True, [(hw["slide bolt"], STEEL, 1.0)], slide_moves),
    ("swasher", "Motor washer (fender washer)", n["swasher"], "bolts", True, [(hw["slide washer"], STEEL, 1.0)], slide_moves),
  ]


CHIPS = [("plate", "Frame plate"), ("arm", "Arm"), ("carrier", "Motor carrier"), ("motor", "Motor and gear"),
         ("bolts", "Bolts and nuts"), ("teeth", "Teeth"), ("car", "Wheel and cover")]


def mesh_arrays(m) -> tuple:
  mesh = m.to_mesh()
  p = np.asarray(mesh.vert_properties, dtype=np.float64)[:, :3]
  t = np.asarray(mesh.tri_verts, dtype=np.int64)
  q = np.round(p * Q)
  assert np.abs(q).max() < 32767, "a part reaches past 327 mm"
  assert len(p) < 65536, "too many corners for 16-bit indices"
  return q.astype("<i2"), t.astype("<u2")


def build() -> tuple:
  blob, meshes, items = bytearray(), [], []
  lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
  for pid, name, note, chip, pick, looks, moves in parts():
    ms = []
    plo, phi = np.full(3, np.inf), np.full(3, -np.inf)
    for m, (rgb, spec, shine), alpha in looks:
      q, t = mesh_arrays(m)
      po = len(blob)
      blob += q.tobytes()
      io = len(blob)
      blob += t.tobytes()
      meshes.append({"nv": len(q), "nt": len(t), "po": po, "io": io})
      ms.append({"m": len(meshes) - 1, "c": [round(c, 3) for c in rgb], "s": spec, "sh": shine, "a": alpha})
      bb = m.bounding_box()
      plo, phi = np.minimum(plo, bb[:3]), np.maximum(phi, bb[3:])
      if pid in ("plate", "arm", "carrier", "motor"):
        lo, hi = np.minimum(lo, bb[:3]), np.maximum(hi, bb[3:])
    item = {"id": pid, "name": name, "note": note, "chip": chip, "pick": pick, "meshes": ms, "moves": moves}
    if moves:                                  # the page keeps the parts that move in the picture
      item["bb"] = [round(float(c), 1) for c in (*plo, *phi)]
    items.append(item)
  centre = [round(float(c), 1) for c in (lo + hi) / 2]
  chip_rgb = {"motor": [0.4, 0.41, 0.45]}        # the motor's black would read as an empty dot on a dark page
  for it in items:
    chip_rgb.setdefault(it["chip"], it["meshes"][0]["c"])
  meta = {
    "q": 1.0 / Q,
    "tilt_deg": 22.0,                          # the column rises about 22 degrees (carphoto.WORLD_UP)
    "parts": items,
    "meshes": meshes,
    "steps": STEPS,
    "chips": [{"id": c, "label": label, "c": chip_rgb[c]} for c, label in CHIPS],
    "centre": centre,
    "views": {                                 # steering wheel frame; dist in mm
      "overview": {"target": centre, "dir": [0.85, -0.55, -0.3], "dist": 500},
      "seat": {"target": [115.0, -70.0, -45.0], "eye": [0.0, 81.0, 734.0], "dist": 560},   # from your eyes (about
                                                                                         # 350 up, 650 back), nearer
      "right": {"target": centre, "dir": [1.0, -0.12, 0.05], "dist": 560},
      "below": {"target": centre, "world_dir": [0.0, -0.97, 0.24], "dist": 560},
    },
  }
  return meta, bytes(blob)


def main():
  meta, blob = build()
  with open(PAGE, encoding="utf-8") as f:
    page = f.read()
  js = json.dumps(meta, separators=(",", ":")).replace("</", "<\\/")
  data = base64.b64encode(blob).decode("ascii")
  data = "\n".join(data[i:i + 4096] for i in range(0, len(data), 4096))
  out = page.replace("__META__", js).replace("__DATA__", data)
  with open(OUT, "w", encoding="utf-8") as f:
    f.write(out)
  tris = sum(m["nt"] for m in meta["meshes"])
  print(f"{OUT}: {len(out) / 1e6:.2f} MB, {len(meta['parts'])} parts, {tris} triangles; centre {meta['centre']}")


if __name__ == "__main__":
  sys.exit(main())
