"""Exports the back-teeth mount and an approximate car around it as compact meshes for the 3D mockup page.

Frames: everything in the steering wheel frame (mm; z along the column towards the driver, y up, x to the driver's
right), except the parts that move with the motor carrier (carrier frame; the page applies the carrier's placement and
its lift about the hinge) and the lift lever (lever frame; placed on its pivot, then carried).

Output: data.bin (all meshes back to back) and data.json (where each one is, how to place it, and the tables the page
needs: the lever's lift, the carrier's drop past the teeth, the gear ratio).
"""
import json
import math
import struct
import sys
import time

sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np  # noqa: E402
from manifold3d import CrossSection, Manifold  # noqa: E402

import assembly as AS  # noqa: E402
import columnassembly as CA  # noqa: E402
import faceassembly as FA  # noqa: E402
import faceparts as FP  # noqa: E402
import mountparts as MP  # noqa: E402
import params as P  # noqa: E402
from cadlib import box, cyl, revolve, union  # noqa: E402

T0 = time.time()
OUT = sys.argv[1] if len(sys.argv) > 1 else "."

# a coarser cutter sweep for the picture only (the printed files use 0.05 degree steps)
_orig_space = FP.tooth_space


def _coarse_space(t, theta_max=5.5, step=0.25):
  return _orig_space(t, theta_max, step)


FP.tooth_space = _coarse_space

t = FP.FaceTeeth(P.WHEEL_OD, P.GRIP, P.RIGHT_SPOKE_DEG)
t15 = FP.FaceTeeth(P.WHEEL_OD, P.GRIP, P.RIGHT_SPOKE_DEG, n_teeth=FP.N_TEETH_SHORT)
long_piece = FP.face_pieces(t, FP.face_solid(t))["one-piece"]
short_piece = FP.face_pieces(t15, FP.face_solid(t15))["one-piece"]
print("teeth", round(time.time() - T0), "s")
fit = FA.solve_face(t, P.COVER_BOTTOM)
parts = {"teeth": long_piece, "gear": FP.face_motor_gear(), "gear_teeth_only": FP.face_motor_gear_teeth_only(),
         "carrier": FP.face_carrier(), "bracket": MP.lever_bracket(), "lever": FP.back_lift_lever(),
         "lever_no_tab": FP.back_lift_lever(with_finger=False), "tab": MP.lever_tab(),
         "hinge_block": FP.face_hinge_block(t), "plate": FP.column_plate(t), "arm": FP.face_arm(fit.arm_len)}
A = FA.FaceAssembly(t, fit, parts)
A15 = FA.FaceAssembly(t15, fit, dict(parts, teeth=short_piece))


# ----- an approximate steering wheel: grip, hub, three spokes (shapes from the photos, not measured) -----

def wheel_hub() -> Manifold:
  prof = [(0.0, -40.0), (84.0, -40.0), (86.0, -20.0), (85.0, 8.0), (80.0, 20.0), (64.0, 27.0), (30.0, 30.5), (0.0, 31.0)]
  return revolve(prof, 0.0, 360.0, step_deg=2.0)


def spoke(a_rim0, a_rim1, a_hub0, a_hub1, z0=-26.0, z1=-2.0) -> Manifold:
  r_rim, r_hub = t.rr - 2.0, 70.0
  pts = [(r_hub * math.cos(math.radians(a)), r_hub * math.sin(math.radians(a))) for a in np.linspace(a_hub0, a_hub1, 10)]
  pts += [(r_rim * math.cos(math.radians(a)), r_rim * math.sin(math.radians(a))) for a in np.linspace(a_hub1 + 0, a_hub1, 1)]
  rim = [(r_rim * math.cos(math.radians(a)), r_rim * math.sin(math.radians(a))) for a in np.linspace(a_rim1, a_rim0, 16)]
  cs = CrossSection([pts + rim])
  if cs.area() < 0:
    cs = CrossSection([(pts + rim)[::-1]])
  return cs.extrude(z1 - z0).translate((0, 0, z0))


def spokes() -> Manifold:
  right = spoke(P.RIGHT_SPOKE_DEG[1], P.RIGHT_SPOKE_DEG[0], 8.0, -38.0)
  left = right.mirror((1.0, 0.0, 0.0))
  bottom = spoke(-80.0, -100.0, -75.0, -105.0, z0=-24.0, z1=-6.0)
  return union([right, left, bottom])


# ----- zip ties: the visible band over the front of the grip at each slot -----

def ties(tt) -> Manifold:
  rho = tt.rho + 0.6
  band = []
  for a in np.linspace(-26.0, 206.0, 59):
    band.append((tt.rr + rho * math.cos(math.radians(a)), rho * math.sin(math.radians(a))))
  for a in np.linspace(206.0, -26.0, 59):
    band.append((tt.rr + (rho + 1.3) * math.cos(math.radians(a)), (rho + 1.3) * math.sin(math.radians(a))))
  cs = CrossSection([band])
  if cs.area() < 0:
    cs = CrossSection([band[::-1]])
  one = cs.extrude(P.TIE_W).transform([[1, 0, 0, 0], [0, 0, 1, -P.TIE_W / 2.0], [0, 1, 0, 0]])
  return union([one.rotate((0, 0, a)) for a in FP.tie_angles(tt)])


# ----- the motor in the carrier frame (as assembly.Assembly.motor) -----

def motor_parts():
  h = P.NEMA / 2
  body = box(-h, h, -h, h, -P.NEMA_LEN, 0.0) + cyl(11.0, 0.0, 2.0)
  board = box(-h, h, -h, h, -P.NEMA_LEN - 14.0, -P.NEMA_LEN)
  plugs = box(-6, 6, -h - 14, -h, -P.NEMA_LEN - 12.0, -P.NEMA_LEN - 3.0) + \
    box(h, h + 14, -6, 6, -P.NEMA_LEN - 12.0, -P.NEMA_LEN - 3.0) + box(-h - 14, -h, -6, 6, -P.NEMA_LEN - 12.0, -P.NEMA_LEN - 3.0)
  motor_plug = box(-8, 8, -h - 12, -h, -P.NEMA_LEN + 2.0, -P.NEMA_LEN + 18.0)
  return body, board, plugs + motor_plug


body, board, plugs = motor_parts()
left_stalk = CA.rod((-P.STALK_FROM[0], P.STALK_FROM[1], P.STALK_FROM[2]), (-P.STALK_TO[0], P.STALK_TO[1], P.STALK_TO[2]), P.STALK_R)
col = CA.ColumnAssembly.__new__(CA.ColumnAssembly)
dash = box(-420, 420, -380, 60, P.DASH_Z - 40.0, P.DASH_Z) - A.covers().scale((1.04, 1.04, 1.0))
hood = box(-260, 260, 60, 150, P.DASH_Z - 40.0, P.DASH_Z + 60.0)

meshes = [
  # name, group, look, solid
  ("grip", "wheel", "wheel", A.wheel_grip()),
  ("hub", "wheel", "hub", wheel_hub()),
  ("spokes", "wheel", "spoke", spokes()),
  ("teeth_long", "wheel_long", "teeth", long_piece),
  ("ties_long", "wheel_long", "tie", ties(t)),
  ("teeth_short", "wheel_short", "teeth", short_piece),
  ("ties_short", "wheel_short", "tie", ties(t15)),
  ("covers", "car", "cover", A.covers()),
  ("dash", "car", "dash", dash + hood),
  ("wiper_stalk", "car", "stalk", A.stalk()),
  ("signal_stalk", "car", "stalk", left_stalk),
  ("key", "car", "key", A.key()),
  ("hinge_block", "world", "hinge_block", A.hinge_block()),
  ("arm", "world", "arm", A.arm()),
  ("plate", "world", "plate", A.plate()),
  ("plate_pads", "world", "rubber", A.plate_pads()),
  ("joint_bolts", "world", "steel", A.joint_bolts()),
  ("hinge_bolt", "world", "steel", A._carried(MP.hinge_bolt(), 0.0)),
  ("carrier", "carrier", "carrier", parts["carrier"]),
  ("motor", "carrier", "motor", body),
  ("board", "carrier", "board", board),
  ("plugs", "carrier", "plug", plugs),
  ("bracket", "carrier", "bracket", parts["bracket"]),
  ("switch", "carrier", "switch", MP.switch_body()),
  ("switch_screws", "carrier", "steel", MP.switch_screws()),
  ("lever_bolt", "carrier", "steel", MP.lever_bolt()),
  ("gear", "gear", "gear", parts["gear"]),
  ("lever", "lever", "lever", parts["lever"]),
]

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
  print(f"{name:14s} {len(pos):7d} verts {len(tv):7d} tris")

# the lift lever's lift (carrier turns this many degrees about the hinge) against the lever's angle
alphas = [round(float(a), 2) for a in np.linspace(0.0, MP.A_OFF, 40)]
lift = [round(max(0.0, MP.cam_lift(a)), 3) for a in alphas]


def drops(AA, tt):
  ws = [round(float(w), 2) for w in np.arange(tt.roll_half, tt.half + 4.0, 0.5)]
  return {"w": ws, "drop": [round(FA.roller_drop_deg(AA, w), 3) for w in ws]}


info = {
  "meshes": index,
  "R": [[float(v) for v in row] for row in A.R], "T": [float(v) for v in A.T],
  "hinge": [float(v) for v in A.hinge_c], "lever_pivot": [0.0, float(MP.LEVER_PIVOT[0]), float(MP.LEVER_PIVOT[1])],
  "lever": {"alpha": alphas, "lift": lift, "a_off": MP.A_OFF},
  "ratio": FP.FACE_RATIO, "mesh_phase": FA.MESH_PHASE,
  "sets": {"long": {"reach": round(t.teeth_half, 2), "roll_half": round(t.roll_half, 3), **drops(A, t)},
           "short": {"reach": round(t15.teeth_half, 2), "roll_half": round(t15.roll_half, 3), **drops(A15, t15)}},
  "wheel": {"od": P.WHEEL_OD, "grip": P.GRIP},
}
open(f"{OUT}/data.bin", "wb").write(bytes(blob))
open(f"{OUT}/data.json", "w").write(json.dumps(info))
print("triangles", tri_total, "bytes", len(blob), "time", round(time.time() - T0), "s")
