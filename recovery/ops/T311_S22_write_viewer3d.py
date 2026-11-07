"""
The right arm mount v3 as a 3D model to turn round in a web page (3 Nov 2026). The printed parts are the CAD parts
exactly (the same shapes as the print files), where they go on the car: the frame plate v4, the arm, the motor
carrier and the teeth; with the motor, its four screws, the gear, the zip ties and the wing bolts and nuts. Round
them the steering wheel grip and the column cover (the cover approximate). The board on the motor's back is a
placeholder (as in carphoto.py). A slider takes it apart in the order it goes together (README steps 1 to 4).

The page draws with WebGL itself (no library, nothing fetched but its fonts): viewer3d_page.html is the page,
this file puts the parts and the steps into it.

  python3 viewer3d.py      # writes ../report/arm-3d.html
"""
import base64
import json
import math
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
M_PLATE = [mv(1, 0.0, 1.0, (0.0, -70.0, 0.0))]                    # up onto the cover's two screws
M_TEETH = [mv(2, 0.0, 0.6, (0.0, 0.0, -55.0))]                    # onto the back of the grip
M_ARM = [mv(3, 0.0, 0.5, (95.0, 0.0, 0.0))]                       # into the receiver from the key side
M_CARRIER = [mv(7, 0.0, 0.5, scale(60.0, V3)),                    # into the tower's channel from the motor's side,
             mv(7, 0.5, 0.75, (0.0, 0.0, -8.0))]                  # slid down; then up the column to the stop

STEPS = [
  "Fit the frame plate on the column cover's two screws, with washers: the cup slot on the key side, slot 1 on the "
  "other. Its flat side goes up against the cover; the square tube hangs underneath, the printed labels facing down.",
  "Fit the teeth on the grip at 4 o'clock (one wrap of silicone tape under them), two zip ties through the middle "
  "slot, heads tucked inside the rim.",
  "Slide the arm's flat bar into the square tube from the key side. Push the nut up into the slot in the tube's far "
  "wall (the dash side), and turn the wing bolt in through that wall: it pinches the bar.",
  "The tower's wing bolt: its nut into the slot at the top of the tower's outer wall, the bolt in through the wall "
  "a few turns.",
  "The motor on the carrier, against the outside of its plate: four M3 x 10 from the side with the four round "
  "pads, the motor's boss in the big hole. Then the gear on the shaft (set screw on the flat).",
  "The stop: its nut into the hex pocket on the carrier's lug, the jam nut onto the stop wing bolt, then the bolt up "
  "through the lug and its nut.",
  "The carrier, motor on it, into the tower's channel from the motor's side, slid down; then up the column against "
  "the stop, the gear in the teeth. Tighten the tower's wing bolt.",
]

# display colours (screen RGB), specular strength, shininess
PLATE = ((0.72, 0.75, 0.79), 0.12, 30)
BLUE = ((0.35, 0.55, 0.85), 0.12, 30)
GREEN = ((0.43, 0.70, 0.44), 0.12, 30)
TEETH = ((0.89, 0.58, 0.27), 0.12, 30)
GEAR = ((0.96, 0.67, 0.32), 0.12, 30)
STEEL = ((0.70, 0.72, 0.76), 0.55, 70)
MOTOR = ((0.17, 0.17, 0.19), 0.25, 40)
PCB = ((0.13, 0.36, 0.23), 0.20, 40)
CHIP = ((0.10, 0.10, 0.11), 0.25, 50)
PLUG = ((0.80, 0.75, 0.60), 0.10, 20)
NYLON = ((0.15, 0.15, 0.16), 0.15, 30)
GRIP = ((0.26, 0.26, 0.28), 0.10, 20)
COVER = ((0.42, 0.44, 0.47), 0.05, 10)


def parts() -> list:
  """The parts in the steering wheel frame: (id, name, note, chip, pickable, [(manifold, look, alpha)], moves)."""
  hw = RC.hardware(0.0, RA.STOP_P)
  mp = [m for m, _ in CP.motor_parts(0.0)]
  motor = union([mp[i] for i in (0, 1, 2, 3)])                     # the end caps, the body and the boss
  heads = union([mp[i] for i in (5, 8, 11, 14)])                   # the four M3 button heads on the pads
  board_steel = union([mp[i] for i in (6, 7, 9, 10, 12, 13, 15, 16)])
  chips = union([mp[i] for i in (18, 19, 20, 23, 24)])
  plugs = union([mp[i] for i in (21, 22)])
  zips = union([m for m, _ in CP.zip_ties()])
  teeth = MT.mid_teeth(MT.MidTeeth(n_teeth=18)).rotate((0.0, 0.0, RA.THETA))      # the 20 set, the one on the car
  gear = RA.motor_and_gear(0.0)["gear"]
  bolt_note = "M5 x 20 stainless wing bolt."
  motor_moves = M_CARRIER + [mv(5, 0.0, 0.35, scale(45.0, U3))]
  return [
    ("cover", "Column cover (the car)", "The car's column cover, drawn roughly from your photos and measurements. "
     "The frame plate hangs on its two screws.", "car", False, [(CS.CarScene(D=125.0).column_cover(back=130.0), COVER, 0.26)], []),
    ("grip", "Steering wheel grip (the car)", "The grip, 367 mm across and 33 mm thick, the wheel straight.", "car", True,
     [(RC.grip(), GRIP, 1.0)], []),
    ("plate", "Frame plate v4 (plate 11)", "166 x 96 x 41 mm. Hangs on the column cover's two screws (the cup slot on "
     "the key side, slot 1 on the other). The square tube underneath is the receiver: the arm slides in from the key "
     "side. The printed labels (KEY, WHEEL, 1) face down.", "plate", True, [(RA.plate_to_wheel(RA.frame_plate_v4()), PLATE, 1.0)], M_PLATE),
    ("teeth", "Steering wheel teeth (plate 9)", "On the grip at 4 o'clock, on one wrap of silicone tape; the gear meets "
     "them from outside the rim.", "teeth", True, [(teeth, TEETH, 1.0)], M_TEETH),
    ("zips", "Zip ties (2)", "Two zip ties round the grip through the teeth's middle slot, heads tucked inside the rim.",
     "teeth", True, [(zips, NYLON, 1.0)], M_TEETH + [mv(2, 0.6, 1.0, scale(30.0, U3))]),
    ("arm", "Arm with its tower (plate 12)", "115 x 44 x 81 mm. Its 10 x 30 bar goes into the frame plate's square "
     "tube (47 mm in; slide it up to 25 mm either way to set how far right the motor sits). The tower at its end runs "
     "along the column; its channel, open towards the motor, takes the motor carrier's bar.", "arm", True,
     [(RA.arm(), BLUE, 1.0)], M_ARM),
    ("carrier", "Motor carrier (plate 12)", "44 x 148 x 61 mm. The motor bolts to the outside of its plate. Its long "
     "bar slides along the column in the tower's channel; the lug at the bar's far end takes the stop wing bolt, its "
     "nut in the hex pocket.", "carrier", True, [(RA.carrier(), GREEN, 1.0)], M_CARRIER),
    ("motor", "Stepper motor (17HS15-1504S-X1)", "42 x 42 x 40 mm, against the outside of the carrier's plate, the "
     "shaft through the big hole pointing in at the steering wheel's middle.", "motor", True,
     [(motor, MOTOR, 1.0), (mp[4], STEEL, 1.0)], motor_moves),
    ("board", "Motor board (StepperServoCAN)", "On the motor's back. Drawn as a placeholder: the real board's shape "
     "and parts differ.", "motor", True, [(mp[17], PCB, 1.0), (chips, CHIP, 1.0), (plugs, PLUG, 1.0),
                                         (board_steel, STEEL, 1.0)], motor_moves),
    ("screws", "Motor screws (4 x M3 x 10)", "Button heads, in from the side with the four round pads, into the motor.",
     "motor", True, [(heads, STEEL, 1.0)], M_CARRIER + [mv(5, 0.35, 0.6, scale(-18.0, U3))]),
    ("gear", "Gear", "On the motor's shaft, set screw on the flat. Slid up against the stop, it sits in the teeth.",
     "motor", True, [(gear, GEAR, 1.0)], M_CARRIER + [mv(5, 0.6, 1.0, scale(-30.0, U3))]),
    ("rbolt", "Receiver wing bolt", bolt_note + " In through the square tube's far (dash-side) wall; it pinches the "
     "arm's bar.", "bolts", True, [(hw["receiver bolt"], STEEL, 1.0)], M_PLATE + [mv(3, 0.75, 1.0, (0.0, 0.0, -30.0))]),
    ("rnut", "Receiver nut (M5)", "In the slot in the square tube's far wall, pushed up into it from below.", "bolts",
     True, [(hw["receiver nut"], STEEL, 1.0)], M_PLATE + [mv(3, 0.5, 0.75, (0.0, -25.0, 0.0))]),
    ("pbolt", "Tower wing bolt", bolt_note + " In through the tower's outer wall onto the carrier's bar. Loosen it to "
     "slide the motor (lane keeping on and off).", "bolts", True, [(hw["push bolt"], STEEL, 1.0)],
     M_ARM + [mv(4, 0.4, 1.0, scale(32.0, U3)), mv(7, 0.75, 1.0, scale(8.0, U3))]),
    ("pnut", "Tower nut (M5)", "Dropped into the slot at the top of the tower's outer wall.", "bolts", True,
     [(hw["push nut"], STEEL, 1.0)], M_ARM + [mv(4, 0.0, 0.4, (0.0, 0.0, 30.0))]),
    ("sbolt", "Stop wing bolt", bolt_note + " Up through the carrier's lug; its tip stops the carrier against the "
     "tower: how deep the gear sits in the teeth.", "bolts", True, [(hw["stop bolt"], STEEL, 1.0)],
     M_CARRIER + [mv(6, 0.35, 1.0, (0.0, 0.0, -35.0))]),
    ("snut", "Stop nut (M5)", "In the hex pocket on the carrier's lug.", "bolts", True, [(hw["stop nut"], STEEL, 1.0)],
     M_CARRIER + [mv(6, 0.0, 0.3, (0.0, 0.0, 20.0))]),
    ("jnut", "Stop jam nut (M5)", "On the stop wing bolt under the lug: tightened up against the lug, it locks the stop.",
     "bolts", True, [(hw["stop jam nut"], STEEL, 1.0)], M_CARRIER + [mv(6, 0.35, 1.0, (0.0, 0.0, -35.0))]),
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
    for m, (rgb, spec, shine), alpha in looks:
      q, t = mesh_arrays(m)
      po = len(blob)
      blob += q.tobytes()
      io = len(blob)
      blob += t.tobytes()
      meshes.append({"nv": int(len(q)), "nt": int(len(t)), "po": po, "io": io})
      ms.append({"m": len(meshes) - 1, "c": [round(c, 3) for c in rgb], "s": spec, "sh": shine, "a": alpha})
      if pid in ("plate", "arm", "carrier", "motor"):
        bb = m.bounding_box()
        lo, hi = np.minimum(lo, bb[:3]), np.maximum(hi, bb[3:])
    items.append({"id": pid, "name": name, "note": note, "chip": chip, "pick": pick, "meshes": ms, "moves": moves})
  centre = [round(float(c), 1) for c in (lo + hi) / 2]
  chip_rgb = {}
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
      "overview": {"target": centre, "dir": [0.9, -0.5, 0.8], "dist": 600},
      "seat": {"target": [115.0, -70.0, -45.0], "eye": [0.0, 81.0, 734.0]},      # your eyes: about 350 up, 650 back
      "right": {"target": centre, "dir": [1.0, -0.12, 0.05], "dist": 560},
      "below": {"target": centre, "world_dir": [0.0, -0.97, 0.24], "dist": 560},
    },
  }
  return meta, bytes(blob)


def main():
  meta, blob = build()
  page = open(PAGE, encoding="utf-8").read()
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
