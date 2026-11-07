"""Exports the pop-off mount and an approximate car around it as compact meshes for the 3D mockup page.

Frames: the steering wheel frame (mm; z along the column towards the driver, y up, x to the driver's right) for the
wheel, the car and the fixed parts; the carrier frame for the parts that swing (the page applies the swing about the
hinge and the carrier's place); the gear's own frame (= the carrier frame, turned about its shaft by the page); the
springs as a short coil and a loop the page stretches and places between their bolts every frame.
"""
import base64
import json
import math
import os
import sys
import time

sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np  # noqa: E402
from manifold3d import CrossSection, Manifold, Mesh  # noqa: E402

import columnassembly as CA  # noqa: E402
import faceparts as FP  # noqa: E402
import params as P  # noqa: E402
import popassembly as PA  # noqa: E402
import popparts as PP  # noqa: E402
from cadlib import box, cyl, cyl_x, revolve, union  # noqa: E402

T0 = time.time()
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.environ.setdefault("POP_CACHE", "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache")

# a coarser cutter sweep for the picture only (the printed files use 0.05 degree steps)
_orig_space = FP.tooth_space
FP.tooth_space = lambda t, theta_max=5.5, step=0.25: _orig_space(t, theta_max, step)

t15 = PP.PopTeeth(n_teeth=FP.N_TEETH_SHORT)
t45 = PP.PopTeeth(n_teeth=FP.N_TEETH)
short_piece = PA.cached(f"mock_short_{t15.rr:.1f}_{t15.z_axis:.2f}", lambda: PP.pop_pieces(t15)["one-piece"])
long_piece = PA.cached(f"mock_long_{t45.rr:.1f}_{t45.z_axis:.2f}", lambda: PP.pop_pieces(t45)["one-piece"])
print("teeth", round(time.time() - T0), "s")
mb = PP.motor_and_board()
block = PP.pop_hinge_block()
plate = PP.pop_column_plate()
A = PA.PopAssembly(t15, {"teeth": short_piece})


# ----- an approximate steering wheel: grip, hub, three spokes (shapes from the photos, not measured) -----

def wheel_grip(tt) -> Manifold:
  pts = [(tt.rr + (PP.GRIP_P / 2) * math.cos(a), (PP.GRIP_P / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40, endpoint=False)]
  return revolve(pts, 0.0, 360.0, step_deg=1.5)


def wheel_hub() -> Manifold:
  prof = [(0.0, -40.0), (84.0, -40.0), (86.0, -20.0), (85.0, 8.0), (80.0, 20.0), (64.0, 27.0), (30.0, 30.5), (0.0, 31.0)]
  return revolve(prof, 0.0, 360.0, step_deg=2.0)


def spoke(tt, a_rim0, a_rim1, a_hub0, a_hub1, z0=-14.0, z1=4.0) -> Manifold:
  r_rim, r_hub = tt.rr - 12.0, 70.0
  pts = [(r_hub * math.cos(math.radians(a)), r_hub * math.sin(math.radians(a))) for a in np.linspace(a_hub0, a_hub1, 10)]
  rim = [(r_rim * math.cos(math.radians(a)), r_rim * math.sin(math.radians(a))) for a in np.linspace(a_rim1, a_rim0, 16)]
  cs = CrossSection([pts + rim])
  if cs.area() < 1e-9:
    cs = CrossSection([(pts + rim)[::-1]])
  return cs.extrude(z1 - z0).translate((0, 0, z0))


def spokes(tt) -> Manifold:
  right = spoke(tt, P.RIGHT_SPOKE_DEG[1], P.RIGHT_SPOKE_DEG[0], 8.0, -38.0)
  left = right.mirror((1.0, 0.0, 0.0))
  bottom = spoke(tt, -80.0, -100.0, -75.0, -105.0, z0=-12.0, z1=2.0)
  return union([right, left, bottom])


def ties(tt) -> Manifold:
  rho = tt.rho + 0.6
  band = []
  for a in np.linspace(-26.0, 206.0, 59):
    band.append((tt.rr + rho * math.cos(math.radians(a)), rho * math.sin(math.radians(a))))
  for a in np.linspace(206.0, -26.0, 59):
    band.append((tt.rr + (rho + 1.3) * math.cos(math.radians(a)), (rho + 1.3) * math.sin(math.radians(a))))
  cs = CrossSection([band])
  if cs.area() < 1e-9:
    cs = CrossSection([band[::-1]])
  one = cs.extrude(P.TIE_W).transform([[1, 0, 0, 0], [0, 0, 1, -P.TIE_W / 2.0], [0, 1, 0, 0]])
  return union([one.rotate((0, 0, a + PP.MOUNT_DEG)) for a in FP.tie_angles(tt)])


def tilt_lever() -> Manifold:
  """The tilt lever tucked up under the column (rough, from the photos): an arm back to its pivot and a paddle."""
  arm = box(-30.0, -18.0, -58.0, -52.0, -150.0, -70.0)
  paddle = box(-40.0, -8.0, -66.0, -52.0, -85.0, -55.0)
  return arm + paddle


def stalk_rest() -> Manifold:
  base = np.array(P.STALK_FROM)
  d = np.array(P.STALK_TO) - base
  d /= np.linalg.norm(d)
  return CA.rod(base, base + PA.STALK_LEN * d, P.STALK_R)


def stalk_down() -> Manifold:
  base = np.array(P.STALK_FROM)
  d = np.array(P.STALK_TO) - base
  d /= np.linalg.norm(d)
  tip = base + PA.STALK_LEN * d
  ax = np.cross(d, [0.0, 1.0, 0.0])
  ax /= np.linalg.norm(ax)
  th = math.radians(-PA.STALK_DOWN_DEG)
  v = tip - base
  v_rot = v * math.cos(th) + np.cross(ax, v) * math.sin(th) + ax * np.dot(ax, v) * (1 - math.cos(th))
  return CA.rod(base, base + v_rot, P.STALK_R)


def flange_bolts() -> Manifold:
  out = []
  for bx, by in PP.FLANGE_BOLTS:
    z0, z1 = PP.PLATE_FLANGE_Z[0] - 6.0, PP.BLOCK_FLANGE_Z[1]
    out.append(cyl(2.5, z0 - 3.0, z1 + 1.0, bx, by, 16) + cyl(4.3, z1 + 1.0, z1 + 4.5, bx, by, 24) +
               cyl(4.6, z0 - 8.2, z0 - 3.0, bx, by, 6) + cyl(5.0, z1, z1 + 1.0, bx, by, 24) + cyl(5.0, z0 - 3.0, z0 - 2.0, bx, by, 24))
  return union(out)


def through_bolt(y, z):
  x_out = PP.SPRING_X + PP.SPRING_WIRE_P / 2 + 1.0
  return (cyl_x(2.5, -x_out, x_out + 6.2, y=y, z=z, segments=16) + cyl_x(4.3, -x_out - 3.5, -x_out, y=y, z=z, segments=24) +
          cyl_x(4.6, x_out, x_out + 5.2, y=y, z=z, segments=6) + cyl_x(5.0, -x_out, -x_out + 1.0, y=y, z=z, segments=24) +
          cyl_x(5.0, x_out - 1.0, x_out, y=y, z=z, segments=24))


def hinge_bolt():
  hy, hz = PP.HINGE_P
  k = PP.BLOCK_KNUCKLE_X[1]
  return (cyl_x(2.5, -k - 1.0, k + 6.0, y=hy, z=hz, segments=16) + cyl_x(4.3, -k - 4.5, -k, y=hy, z=hz, segments=24) +
          cyl_x(4.6, k, k + 5.2, y=hy, z=hz, segments=6))


# ----- the springs: a coil (its body at the length it has with the motor on) and one end loop -----
r_out = PP.SPRING_OD_P / 2
wire = PP.SPRING_WIRE_P
r_in = r_out - wire
LOOP_C = -PP.PIN_D / 2 + r_in            # the loop's middle, from its bolt along the spring
COIL0 = LOOP_C + r_in                    # where the coils start
L_ON = PP.spring_length_pins(0.0)
BODY_REF = L_ON - 2 * COIL0
TURNS = 24


def coil_mesh() -> Manifold:
  """A helix tube of TURNS turns from z = 0 to BODY_REF (the page scales it along z to the spring's length)."""
  n_per = 24
  ring = 8
  rm = r_out - wire / 2
  pts, tris = [], []
  N = TURNS * n_per + 1
  for i in range(N):
    a = 2 * math.pi * i / n_per
    z = BODY_REF * i / (N - 1)
    c = np.array([rm * math.cos(a), rm * math.sin(a), z])
    tng = np.array([-rm * math.sin(a), rm * math.cos(a), BODY_REF / (N - 1) * n_per / (2 * math.pi)])
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
  # cap the ends
  c0 = len(pts)
  pts.append(pts[0] * 0 + np.mean(pts[:ring], axis=0))
  c1 = len(pts)
  pts.append(np.mean(pts[(N - 1) * ring:(N - 1) * ring + ring], axis=0))
  for j in range(ring):
    tris.append((c0, j, (j + 1) % ring))
    tris.append((c1, (N - 1) * ring + (j + 1) % ring, (N - 1) * ring + j))
  m = Manifold(Mesh(vert_properties=np.array(pts, dtype=np.float32), tri_verts=np.array(tris, dtype=np.uint32)))
  if m.volume() < 0:
    m = Manifold(Mesh(vert_properties=np.array(pts, dtype=np.float32), tri_verts=np.array([(a, c, b) for a, b, c in tris], dtype=np.uint32)))
  return m


def loop_mesh() -> Manifold:
  """One end loop: a ring of wire in the plane of the spring's axis (local y-z), its middle at the origin."""
  rm = r_out - wire / 2
  pts = [(rm + (wire / 2) * math.cos(a), (wire / 2) * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 10, endpoint=False)]
  ring = revolve(pts, 0.0, 360.0, step_deg=10.0)          # in the x-y plane, axis z
  return ring.rotate((0, 90, 0))                          # axis along x: the ring lies in the y-z plane


coil = coil_mesh()
print("coil volume", round(coil.volume(), 1), "tris", coil.num_tri())

meshes = [
  ("grip", "wheel", "wheel", wheel_grip(t15)),
  ("hub", "wheel", "hub", wheel_hub()),
  ("spokes", "wheel", "spoke", spokes(t15)),
  ("teeth_short", "wheel_short", "teeth", short_piece.rotate((0, 0, PP.MOUNT_DEG))),
  ("ties_short", "wheel_short", "tie", ties(t15)),
  ("teeth_long", "wheel_long", "teeth", long_piece.rotate((0, 0, PP.MOUNT_DEG))),
  ("ties_long", "wheel_long", "tie", ties(t45)),
  ("covers", "car", "cover", A.covers()),
  ("wiper_stalk", "car", "stalk", stalk_rest()),
  ("signal_stalk", "car", "stalk", CA.rod((-P.STALK_FROM[0], P.STALK_FROM[1], P.STALK_FROM[2]),
                                          (-P.STALK_TO[0], P.STALK_TO[1], P.STALK_TO[2]), P.STALK_R)),
  ("key", "car", "key", A.key()),
  ("tilt_lever", "car", "stalk", tilt_lever()),
  ("stalk_down", "ghost", "ghost", stalk_down()),
  ("hinge_block", "world", "hinge_block", PP.to_wheel(block)),
  ("switch", "world", "switch", PP.to_wheel(PP.switch_body_pop())),
  ("plate", "world", "plate", plate),
  ("plate_pads", "world", "rubber", PP.pop_plate_pads()),
  ("flange_bolts", "world", "steel", flange_bolts()),
  ("b_bolt", "world", "steel", PP.to_wheel(through_bolt(*PP.B_BOLT) + hinge_bolt())),
  ("carrier", "carrier", "carrier", PP.pop_carrier()),
  ("motor", "carrier", "motor", mb["body"]),
  ("board", "carrier", "board", mb["board"]),
  ("plugs", "carrier", "plug", mb["plugs"]),
  ("c_bolt", "carrier", "steel", through_bolt(*PP.C_BOLT)),
  ("gear", "gear", "gear", PP.pop_motor_gear()),
  ("spring_coil", "spring_coil", "spring", coil),
  ("spring_loop", "spring_loop", "spring", loop_mesh()),
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


def drops(tt):
  AA = PA.PopAssembly(tt, {"teeth": short_piece if tt is t15 else long_piece})
  ws = [round(float(w), 2) for w in np.arange(tt.roll_half, tt.half + 4.0, 0.5)]
  return {"w": ws, "drop": [round(PA.roller_drop(AA, w), 3) for w in ws]}


R, T = PP.carrier_to_wheel()
info = {
  "meshes": index,
  "R": [[float(v) for v in row] for row in R], "T": [float(v) for v in T],
  "hinge": [0.0, PP.HINGE_P[0], PP.HINGE_P[1]],
  "c_bolt": [float(v) for v in PP.C_BOLT], "b_bolt": [float(v) for v in PP.B_BOLT], "spring_x": PP.SPRING_X,
  "loop_c": LOOP_C, "coil0": COIL0, "body_ref": BODY_REF,
  "lift_off": PP.LIFT_OFF, "dead": PP.DEAD_DEG, "lift_drop": PP.LIFT_DROP,
  "ratio": FP.FACE_RATIO, "mesh_phase": PA.MESH_PHASE, "mount_deg": PP.MOUNT_DEG,
  "sets": {"short": {"reach": round(t15.teeth_half, 2), "roll_half": round(t15.roll_half, 3), **drops(t15)},
           "long": {"reach": round(t45.teeth_half, 2), "roll_half": round(t45.roll_half, 3), **drops(t45)}},
  "springs": PA.spring_rows(),
}
open(f"{OUT}/data.bin", "wb").write(bytes(blob))
open(f"{OUT}/data.json", "w").write(json.dumps(info))
open(f"{OUT}/parts-data.txt", "w").write(base64.b64encode(bytes(blob)).decode())
print("triangles", tri_total, "bytes", len(blob), "time", round(time.time() - T0), "s")
