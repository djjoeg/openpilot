"""Exports the slide mount and an approximate car round it as compact meshes for the 3D page.

Frames: the steering wheel frame (mm; z along the column towards the driver, y up, x to the driver's right) for the
wheel and the car; the carrier frame for the mount (the page places it with R, T and turns it round the column by the
mount's adjustment); the carrier's parts move along its y, the lever turns about its bolt, the gear about its shaft.
The car is exported for a few key depths D (the one distance the photos can't settle).
"""
import base64
import json
import math
import os
import sys
import time

sys.path.insert(0, "/home/claude/deliver/hardware/cad")
os.environ.setdefault("POP_CACHE", "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache")
import numpy as np  # noqa: E402
from manifold3d import CrossSection, Manifold, Mesh  # noqa: E402

import carref as CR  # noqa: E402
import carscene as CS  # noqa: E402
import columnassembly as CA  # noqa: E402
import faceparts as FP  # noqa: E402
import params as P  # noqa: E402
import popassembly as PA  # noqa: E402
import popparts as PP  # noqa: E402
import slideassembly as SA  # noqa: E402
import slideparts as SP  # noqa: E402
from cadlib import box, cyl, cyl_x, cyl_y, revolve, union  # noqa: E402

T0 = time.time()
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
DS = (107.0, 113.0, 120.0)

# a coarser cutter sweep for the picture only (the printed files use 0.05 degree steps)
_orig_space = FP.tooth_space
FP.tooth_space = lambda t, theta_max=5.5, step=0.25: _orig_space(t, theta_max, step)
t = SP.SlideTeeth()
teeth = PA.cached(f"mock_slide_teeth_{t.rr:.1f}_{t.z_axis:.2f}_{t.spoke[0]:.1f}_{t.spoke[1]:.1f}_{SP.MOUNT_DEG_S:.0f}",
                  lambda: SP.slide_teeth(t))
print("teeth", round(time.time() - T0), "s", flush=True)


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
  return union([one.rotate((0, 0, a + SP.MOUNT_DEG_S)) for a in SP.slide_tie_angles(t)])


def tilt_lever() -> Manifold:
  """The adjustment tab (rough, from the photos): its paddle and the steel arm back to its pivot."""
  x0, x1, z0, z1 = PA.TAB_PADDLE
  y0, y1 = PA.TAB_PADDLE_Y
  r = 3.0
  paddle = Manifold.batch_hull([cyl_x(r, x0 + r, x1 - r, y=y0 + r, z=z1 - r, segments=16), cyl_x(r, x0 + r, x1 - r, y=y1 - r, z=z1 - r, segments=16),
                                box(x0, x1, y0 + r, y1, z0, z1 - r), box(x0 + r, x1 - r, y0, y1, z0, z1 - r)])
  a0, a1, c0, c1 = PA.TAB_ARM
  return paddle + box(a0, a1, PA.TAB_ARM_Y[0], PA.TAB_ARM_Y[1], c0, c1)


def tab_bolts(sc: CS.CarScene) -> Manifold:
  """The tabs' M5 bolts under the plate and the cover screws' heads, moved with the cover."""
  y1 = PP.plate_top_y_u()
  y0 = y1 - PP.PL_T_U
  parts = []
  for _, R, T, (bx, bz), _, kind in PA.tab_placements():
    top = y1 + PP.TAB_T - PP.NUT_CHANNEL_T
    parts.append(cyl_y(4.6, top, top + 3.5, x=bx, z=bz, segments=6) + cyl_y(2.5, top - 20.0, top, x=bx, z=bz, segments=16) +
                 cyl_y(5.0, y0 - 1.0, y0, x=bx, z=bz, segments=24) + cyl_y(4.6, y0 - 6.2, y0 - 1.0, x=bx, z=bz, segments=6))
    hr, hd = PP.TAB_KINDS[kind]["head"]
    parts.append(cyl_y(hr - 0.6, T[1] - PP.TAB_T, T[1] - PP.TAB_T + hd - 0.5, x=T[0], z=T[2], segments=24))
  return sc.moved(union(parts))


def stalk_rest(sc: CS.CarScene, mirror: bool = False) -> Manifold:
  base, tip = np.array(sc.p["SH"], float), np.array(sc.p["ST"], float)
  if mirror:
    base[0], tip[0] = -base[0], -tip[0]
  return CA.rod(base, tip, 11.0)


# ----- the mount (carrier frame) -----

def lever_bolt() -> Manifold:
  py, pz = SP.PIVOT
  x0, x1 = SP.LEVER_X[0] - 0.5, SP.WALL_X[1] - 3.0
  return (cyl_x(2.5, x0 - 1.0, x1, y=py, z=pz, segments=16) + cyl_x(4.3, x0 - 4.5, x0, y=py, z=pz, segments=24) +
          cyl_x(5.0, x0 - 0.5, x0, y=py, z=pz, segments=24))


def flange_bolts() -> Manifold:
  """The block's two M5 bolts through the flanges (carrier frame: along y)."""
  out = []
  y0, y1 = SP.FLANGE_Y
  for bx, bz in SP.FLANGE_BOLTS:
    out.append(cyl_y(2.5, y0 - 3.0, y1 + SP.PL_FLANGE_T + 3.0, x=bx, z=bz, segments=16) +
               cyl_y(4.3, y0 - 3.5, y0, x=bx, z=bz, segments=24) +
               cyl_y(4.6, y1 + SP.PL_FLANGE_T, y1 + SP.PL_FLANGE_T + 4.5, x=bx, z=bz, segments=6))
  return union(out)


def grub_screws() -> Manifold:
  out = []
  for x, z in SP.RODS:
    if z > 0:
      out.append(cyl(1.5, z + SP.ROD_D / 2, z + SP.ROD_D / 2 + 6.0, x=x, y=0.0, segments=12))
    else:
      out.append(cyl(1.5, z - SP.ROD_D / 2 - 6.0, z - SP.ROD_D / 2, x=x, y=0.0, segments=12))
  return union(out)


TURNS = 6
COIL_REF = 10.0


def coil_mesh(od: float, wire: float, turns: int, length: float) -> Manifold:
  """A helix tube of `turns` turns along z from 0 to `length` (the page scales it along z)."""
  n_per, ring = 20, 6
  rm = od / 2 - wire / 2
  pts, tris = [], []
  N = turns * n_per + 1
  for i in range(N):
    a = 2 * math.pi * i / n_per
    z = length * i / (N - 1)
    c = np.array([rm * math.cos(a), rm * math.sin(a), z])
    tng = np.array([-rm * math.sin(a), rm * math.cos(a), length / (N - 1) * n_per / (2 * math.pi)])
    tng /= np.linalg.norm(tng)
    nrm = np.array([math.cos(a), math.sin(a), 0.0])
    bnm = np.cross(tng, nrm)
    for j in range(ring):
      b = 2 * math.pi * j / ring
      pts.append(c + (wire / 2) * (math.cos(b) * nrm + math.sin(b) * bnm))
  for i in range(N - 1):
    for j in range(ring):
      a0 = i * ring + j
      a1 = i * ring + (j + 1) % ring
      b0 = (i + 1) * ring + j
      b1 = (i + 1) * ring + (j + 1) % ring
      tris += [(a0, b0, a1), (a1, b0, b1)]
  c0 = len(pts)
  pts.append(np.mean(pts[:ring], axis=0))
  c1 = len(pts)
  pts.append(np.mean(pts[(N - 1) * ring:(N - 1) * ring + ring], axis=0))
  for j in range(ring):
    tris.append((c0, j, (j + 1) % ring))
    tris.append((c1, (N - 1) * ring + (j + 1) % ring, (N - 1) * ring + j))
  m = Manifold(Mesh(vert_properties=np.array(pts, dtype=np.float32), tri_verts=np.array(tris, dtype=np.uint32)))
  if m.volume() < 0:
    m = Manifold(Mesh(vert_properties=np.array(pts, dtype=np.float32), tri_verts=np.array([(a, c, b) for a, b, c in tris], dtype=np.uint32)))
  return m


mb = SP.motor_board()
side_spokes, bars = spokes()
meshes = [
  ("grip", "wheel", "wheel", wheel_grip()),
  ("hub", "wheel", "hub", wheel_hub()),
  ("spokes", "wheel", "spoke", side_spokes),
  ("bars", "wheel", "bar", bars),
  ("teeth", "teeth", "teeth", teeth.rotate((0, 0, SP.MOUNT_DEG_S))),
  ("ties", "teeth", "tie", ties()),
  # the mount's fixed parts (carrier frame)
  ("block", "block", "block", SP.slide_block()),
  ("plug", "block", "block", SP.plug()),
  ("bearings", "block", "steel", SP.bearings()),
  ("switch", "block", "switch", SP.switch_body()),
  ("flange_bolts", "block", "steel", flange_bolts()),
  ("pusher", "pusher", "pusher", SP.pusher()),
  # the moving parts
  ("carrier", "carrier", "carrier", SP.slide_carrier()),
  ("motor", "carrier", "motor", mb["motor"]),
  ("cap", "carrier", "cap", SP.board_cap()),
  ("plugs", "carrier", "plug", union([mb["car plug"], mb["motor plug"], mb["motor's own plug"]])),
  ("rods", "carrier", "steel", SP.rods()),
  ("collars", "carrier", "steel", SP.collars()),
  ("grubs", "carrier", "steel", grub_screws()),
  ("lever_bolt", "carrier", "steel", lever_bolt()),
  ("lever", "lever", "lever", SP.slide_lever(0.0)),
  ("gear", "gear", "gear", PP.pop_motor_gear()),
  ("spring_coil", "spring", "spring", coil_mesh(SP.RSPRING["od"], SP.RSPRING["wire"], TURNS, COIL_REF)),
]
cars = {}
for D in DS:
  sc = CS.CarScene(D)
  tag = f"{D:.0f}"
  kp = sc.key_parts()
  A = SA.SlideAssembly(D, SP.MOUNT_DEG_S, parts={})
  meshes += [
    (f"cover@{tag}", f"car@{tag}", "cover", sc.column_cover()),
    (f"key_bulge@{tag}", f"car@{tag}", "cover", kp["key bulge and bezel"]),
    (f"key_in@{tag}", f"car@{tag}", "keyhead", kp["the key in it"]),
    (f"key_room@{tag}", f"keyroom@{tag}", "keyroom", kp["room to turn the key"]),
    (f"stalk@{tag}", f"car@{tag}", "stalk", stalk_rest(sc)),
    (f"signal@{tag}", f"car@{tag}", "stalk", stalk_rest(sc, mirror=True)),
    (f"tab_lever@{tag}", f"car@{tag}", "tablever", sc.moved(tilt_lever())),
    (f"back_cover@{tag}", f"backcover@{tag}", "hub", sc.back_cover()),
    (f"dash@{tag}", f"dash@{tag}", "dash", sc.bolster()),
    (f"plate@{tag}", f"plate@{tag}", "plate", A.plate()),
    (f"tabs@{tag}", f"plate@{tag}", "tab", A.tabs()),
    (f"tab_bolts@{tag}", f"plate@{tag}", "steel", tab_bolts(sc)),
  ]
  s = sc.summary()
  cars[tag] = {"D": D, "key": [float(v) for v in sc.key], "stalk_mid": [float(v) for v in (sc.p["SH"] + sc.p["ST"]) / 2.0],
               "summary": {k: (list(v) if isinstance(v, tuple) else v) for k, v in s.items()},
               "tab_label": [float(v) for v in np.array([-19.0, -64.0, -80.0]) + np.array(sc.shift)],
               "plate_label": [float(v) for v in np.array([-57.0, -66.0, -150.0]) + np.array(sc.shift)],
               "dash_z": float(sc.dash_z)}
  print("car", tag, round(time.time() - T0), "s", flush=True)

blob = bytearray()
index = []
tri_total = 0
for name, group, look, m in meshes:
  m = m.simplify(0.02).calculate_normals(0, 38.0)
  mesh = m.to_mesh()
  vp = np.asarray(mesh.vert_properties, dtype=np.float64)
  tv = np.asarray(mesh.tri_verts, dtype=np.int64)
  pos, nrm = vp[:, :3], vp[:, 3:6]
  lo, hi = pos.min(axis=0), pos.max(axis=0)
  centre = (lo + hi) / 2
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
  print(f"{name:16s} {len(pos):7d} verts {len(tv):7d} tris", flush=True)

# ----- how things move -----
lever = []
for d in np.arange(0.0, SP.LEVER_SWING + 1e-6, 1.0):
  row = [round(float(d), 1)]
  for t2t in (0.0, 4.5):
    st = SP.cam_state(float(d), t2t)
    off = st["carrier_off"]
    back = max(0.0, (SP.cam_support(float(d)) - SP.CAM_MIN - SP.CLEAR_OFF) - (SP.STROKE - off))
    row += [round(off, 3), round(back, 3)]
  lever.append(row)

A = SA.SlideAssembly(DS[1], SP.MOUNT_DEG_S, parts={"teeth": PA.cached(f"slide_teeth2_{t.rr:.1f}_{t.z_axis:.2f}_{t.spoke[0]:.1f}_{t.spoke[1]:.1f}", lambda: SP.slide_teeth(t))})
ws = [round(float(w), 2) for w in np.arange(t.roll_half, t.half + 4.01, 0.5)]
drops = {"w": ws, "left": [round(SA.roller_drop(A, w), 3) for w in ws], "right": [round(SA.roller_drop(A, -w), 3) for w in ws]}
print("drops", round(time.time() - T0), "s", flush=True)

Rm = PP.rot_z(SP.MOUNT_DEG_S)
R = Rm @ PP.R_POP
T = Rm @ np.array([PP.R_FACE_P, 0.0, PP.Z_AXIS_P])
latch = SA.latch_numbers()
info = {
  "meshes": index,
  "R": [[float(v) for v in row] for row in R], "T": [float(v) for v in T],
  "pivot": [0.0, SP.PIVOT[0], SP.PIVOT[1]], "swing_sign": SP.SWING_SIGN, "lever_swing": SP.LEVER_SWING,
  "lever": lever, "stroke": SP.STROKE, "drop_most": SA.drop_most(), "drops": drops,
  "roll_half": round(t.roll_half, 3), "reach": round(t.teeth_half, 3), "half": round(t.half, 3),
  "rods": [list(r) for r in SP.RODS], "spring_y0": SP.BLOCK_Y[1], "collar_y": SP.COLLAR_Y, "coil_ref": COIL_REF,
  "ratio": FP.FACE_RATIO, "mesh_phase": PA.MESH_PHASE, "mount_deg": SP.MOUNT_DEG_S, "mount_adj": list(SP.MOUNT_ADJ_S),
  "cars": cars, "ds": [f"{D:.0f}" for D in DS],
  "latch": latch, "switch": SA.switch_states(),
  "labels": {"block": [-31.0, 50.0, 24.0], "lever": [-47.0, SP.PIVOT[0] + 6.0, SP.PIVOT[1] - 6.0], "motor": [0.0, 21.0, -20.0],
             "gear": [0.0, 0.0, 22.0], "cap": [0.0, 0.0, -51.0], "springs": [-31.0, 76.0, 15.0], "rods": [-31.0, 60.0, -15.0]},
}
open(f"{OUT}/data.json", "w").write(json.dumps(info))
open(f"{OUT}/parts-data.txt", "w").write(base64.b64encode(bytes(blob)).decode())
print("triangles", tri_total, "bytes", len(blob), "time", round(time.time() - T0), "s")
