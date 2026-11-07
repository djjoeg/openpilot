"""Exports the side-slide mount, the steering wheel and an approximate car round it as compact meshes for the 3D page.

Frames: the steering wheel frame (mm; z along the column towards the driver, y up, x to the driver's right) for the
wheel, the teeth and the car; the carrier frame for the mount (sideparts.py: origin on the shaft at the motor's front
face, +z out along the shaft, +y towards the dash). The page places the carrier frame with R and T. Moving parts slide
along -z by s (0 latched out, 40 slid in); the gear turns about z; the plunger's pin and knob move along -x; the
spring's strip and the switch's lever stretch along z.
"""
import base64
import json
import math
import os
import sys
import time

sys.path.insert(0, "/home/claude/deliver/hardware/cad")
os.environ.setdefault("POP_CACHE", "/tmp/pop_cache")
import numpy as np  # noqa: E402
from manifold3d import CrossSection, Manifold  # noqa: E402

import carref as CR  # noqa: E402
import carscene as CS  # noqa: E402
import columnassembly as CA  # noqa: E402
import faceparts as FP  # noqa: E402
import mountparts as MP  # noqa: E402
import params as P  # noqa: E402
import popparts as PP  # noqa: E402
import sideassembly as SA  # noqa: E402
import sideparts as S  # noqa: E402
import slideparts as SP  # noqa: E402
from cadlib import revolve, union  # noqa: E402

T0 = time.time()
OUT = sys.argv[1] if len(sys.argv) > 1 else "."

parts = SA.build_parts()
A = SA.SideAssembly(parts)
t = A.t
print("parts", round(time.time() - T0), "s", flush=True)


# ----- an approximate steering wheel: grip, hub, two side spokes and two lower bars (shapes from the photos) -----

def wheel_grip() -> Manifold:
  pts = [(t.rr + (PP.GRIP_P / 2) * math.cos(a), (PP.GRIP_P / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
  return revolve(pts, 0.0, 360.0, step_deg=1.5)


def wheel_hub() -> Manifold:
  prof = [(0.0, -40.0), (84.0, -40.0), (86.0, -20.0), (85.0, 8.0), (80.0, 20.0), (64.0, 27.0), (30.0, 30.5), (0.0, 31.0)]
  return revolve(prof, 0.0, 360.0, step_deg=2.0)


def spoke(a_rim0, a_rim1, a_hub0, a_hub1, z0, z1) -> Manifold:
  r_rim, r_hub = t.rr - 12.0, 70.0
  pts = [(r_hub * math.cos(math.radians(a)), r_hub * math.sin(math.radians(a))) for a in np.linspace(a_hub0, a_hub1, 10)]
  rim = [(r_rim * math.cos(math.radians(a)), r_rim * math.sin(math.radians(a))) for a in np.linspace(a_rim1, a_rim0, 16)]
  cs = CrossSection([pts + rim])
  if cs.area() < 1e-9:
    cs = CrossSection([(pts + rim)[::-1]])
  return cs.extrude(z1 - z0).translate((0, 0, z0))


def spokes() -> tuple:
  a0, a1 = CR.RIGHT_SPOKE_DEG
  side = spoke(a0, a1, -32.0, 32.0, -18.0, 6.0)
  b0, b1 = CR.RIGHT_BAR_DEG
  bar = spoke(b0, b1, -66.0, -50.0, -24.0, -6.0)
  return side + side.mirror((1.0, 0.0, 0.0)), bar + bar.mirror((1.0, 0.0, 0.0))


def ties() -> Manifold:
  rho = t.rho + 0.6
  band = []
  for a in np.linspace(-26.0, 206.0, 59):
    band.append((t.rr + rho * math.cos(math.radians(a)), rho * math.sin(math.radians(a))))
  for a in np.linspace(206.0, -26.0, 59):
    band.append((t.rr + (rho + 1.3) * math.cos(math.radians(a)), (rho + 1.3) * math.sin(math.radians(a))))
  cs = CrossSection([band])
  if cs.area() < 1e-9:
    cs = CrossSection([band[::-1]])
  one = cs.extrude(P.TIE_W).transform([[1, 0, 0, 0], [0, 0, 1, -P.TIE_W / 2.0], [0, 1, 0, 0]])
  return union([one.rotate((0, 0, a + S.MOUNT_DEG)) for a in SP.slide_tie_angles(t)])


def stalk_rest(sc: CS.CarScene, mirror: bool = False) -> Manifold:
  base, tip = np.array(sc.p["SH"], float), np.array(sc.p["ST"], float)
  if mirror:
    base[0], tip[0] = -base[0], -tip[0]
  return CA.rod(base, tip, 11.0)


# ----- the mount (carrier frame, motor latched out) -----
mb = S.motor_board()
pl = S.plunger(0.0)
sw = S.switch(0.0)
sp = S.spring_parts(0.0)
side_spokes, bars = spokes()
sc = CS.CarScene(CS.D_REF)
kp = sc.key_parts()
meshes = [
  # the steering wheel (turns with the wheel)
  ("grip", "wheel", "wheel", wheel_grip()),
  ("hub", "wheel", "hub", wheel_hub()),
  ("spokes", "wheel", "spoke", side_spokes),
  ("bars", "wheel", "bar", bars),
  ("teeth", "wheel", "teeth", A.teeth(0.0)),
  ("ties", "wheel", "tie", ties()),
  # fixed to the car
  ("plate", "fixed", "plate", parts["plate"]),
  ("rail", "fixed", "steel", parts["rail"]),
  ("plunger", "fixed", "steel", pl["fixed"]),
  ("switch", "fixed", "switch", sw["body"]),
  ("spool", "fixed", "spool", parts["spool"].translate((S.SPOOL_X, 0.0, S.SPOOL_Z))),
  ("coil", "fixed", "spring", sp["coil"]),
  ("axle", "fixed", "steel", sp["axle"]),
  ("pin", "pin", "steel", pl["pin"]),
  ("knob", "pin", "knob", pl["knob"]),
  ("lever", "swlever", "steel", sw["lever"]),
  ("strip", "strip", "spring", sp["strip"]),
  # sliding with the motor
  ("bracket", "moving", "bracket", parts["bracket"]),
  ("motor", "moving", "motor", mb["motor"]),
  ("cap", "moving", "cap", S.side_board_cap()),
  ("plugs", "moving", "plug", union([mb["car plug"], mb["motor plug"], mb["motor's own plug"]])),
  ("block", "moving", "steel", parts["block"]),
  ("block_screws", "moving", "steel", parts["block screws"]),
  ("clamp", "moving", "clamp", sp["clamp"]),
  ("gear", "gear", "gear", parts["gear"]),
  # the car round it: estimates from photos
  ("cover", "car", "cover", sc.column_cover()),
  ("key_bulge", "car", "cover", kp["key bulge and bezel"]),
  ("key_in", "car", "keyhead", kp["the key in it"]),
  ("key_room", "keyroom", "keyroom", kp["room to turn the key"]),
  ("stalk", "car", "stalk", stalk_rest(sc)),
  ("signal", "car", "stalk", stalk_rest(sc, mirror=True)),
  ("back_cover", "backcover", "hub", sc.back_cover()),
]

blob = bytearray()
index = []
tri_total = 0
centres = {}
for name, group, look, m in meshes:
  tol = 0.05 if name == "teeth" else 0.02
  m = m.simplify(tol).calculate_normals(0, 38.0)
  mesh = m.to_mesh()
  vp = np.asarray(mesh.vert_properties, dtype=np.float64)
  tv = np.asarray(mesh.tri_verts, dtype=np.int64)
  pos, nrm = vp[:, :3], vp[:, 3:6]
  lo, hi = pos.min(axis=0), pos.max(axis=0)
  centre = (lo + hi) / 2
  centres[name] = {"lo": lo.round(2).tolist(), "hi": hi.round(2).tolist()}
  scale = max(float((hi - lo).max()) / 2 / 32000.0, 1e-6)
  q = np.round((pos - centre) / scale).astype(np.int16)
  n = nrm / np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
  nq = np.round(n * 127).astype(np.int8)
  big = len(pos) > 65535
  idx = tv.astype(np.uint32 if big else np.uint16).ravel()
  entry = {"name": name, "group": group, "look": look, "verts": int(len(pos)), "tris": int(len(tv)),
           "centre": [round(float(c), 4) for c in centre], "scale": scale, "index32": big}
  while len(blob) % 4:
    blob += b"\0"
  entry["pos"] = len(blob)
  blob += q.tobytes()
  while len(blob) % 4:
    blob += b"\0"
  entry["nrm"] = len(blob)
  blob += nq.tobytes()
  while len(blob) % 4:
    blob += b"\0"
  entry["idx"] = len(blob)
  blob += idx.tobytes()
  index.append(entry)
  tri_total += len(tv)
  print(f"{name:14s} {len(pos):7d} verts {len(tv):7d} tris", flush=True)

# ----- how things move -----
ss = [round(float(s), 2) for s in np.arange(-0.2, S.STROKE + 1e-6, 0.25)]
pin_back = [round(S.pin_back_at(s), 3) for s in ss]
rd_max = MP.SW_FP - (MP.SW_OP - MP.SW_PRESS)
Rm = PP.rot_z(S.MOUNT_DEG)
R = Rm @ PP.R_POP
T = Rm @ np.array([PP.R_FACE_P, 0.0, PP.Z_AXIS_P])
f = SA.forces()


def mid(name: str, k=(0.5, 0.5, 0.5)) -> list:
  lo, hi = np.array(centres[name]["lo"]), np.array(centres[name]["hi"])
  return [round(float(v), 2) for v in lo + (hi - lo) * np.array(k)]


info = {
  "meshes": index,
  "R": [[float(v) for v in row] for row in R], "T": [float(v) for v in T],
  "stroke": S.STROKE, "clear_of_teeth": 12.5, "switch_off": 1.6,
  "slide": {"s": ss, "pin_back": pin_back},
  "strip": [S.SPOOL_Z, S.CLAMP_Z + 5.0],
  "swlever": [S.EAR_Z[1], S.SW_HOLES_Z - MP.SW_H / 2 + 0.01, round(rd_max, 3)],
  "reach": round(t.teeth_half, 3), "half": round(t.half, 3), "pitch": round(t.pitch_deg, 4),
  "ratio": FP.FACE_RATIO, "mesh_phase": SA.MESH_PHASE, "mount_deg": S.MOUNT_DEG,
  "labels": {
    "motor": [0.0, S.H, -20.0], "gear": [0.0, 0.0, 22.0], "bracket": mid("bracket", (0.15, 0.5, 0.9)),
    "plate": mid("plate", (0.0, 0.5, 0.25)), "rail": mid("rail", (1.0, 0.5, 0.2)), "knob": mid("knob", (0.0, 0.5, 0.5)),
    "spring": mid("coil", (0.5, 1.0, 0.5)), "switch": mid("switch", (1.0, 0.5, 0.5)), "cap": [0.0, 0.0, -51.0],
    "key": [float(v) for v in sc.key], "stalk": [float(v) for v in (np.array(sc.p["SH"]) + np.array(sc.p["ST"])) / 2.0],
    "cover": [float(sc.cover_right_x) - 10.0, float(sc.cover_bottom) + 10.0, float(sc.cover_front_z) - 40.0],
  },
  "forces": f,
  "centres": centres,
}
open(f"{OUT}/data.json", "w").write(json.dumps(info))
open(f"{OUT}/parts-data.txt", "w").write(base64.b64encode(bytes(blob)).decode())
print("triangles", tri_total, "bytes", len(blob), "time", round(time.time() - T0), "s")
