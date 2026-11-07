"""
Small solid-modelling helpers on top of manifold3d, plus STL writing and print-bed placement.
"""
import math
import struct

import manifold3d
import numpy as np
from manifold3d import CrossSection, Manifold

manifold3d.set_circular_segments(64)


def box(x0, x1, y0, y1, z0, z1) -> Manifold:
  return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def cyl(r, z0, z1, x=0.0, y=0.0, segments=64) -> Manifold:
  """Cylinder along Z."""
  return Manifold.cylinder(z1 - z0, r, r, segments).translate((x, y, z0))


def cone(r0, r1, z0, z1, x=0.0, y=0.0, segments=64) -> Manifold:
  return Manifold.cylinder(z1 - z0, r0, r1, segments).translate((x, y, z0))


def cyl_x(r, x0, x1, y=0.0, z=0.0, segments=64) -> Manifold:
  """Cylinder along X from x0 to x1, centred at (y, z)."""
  return Manifold.cylinder(x1 - x0, r, r, segments).rotate((0, 90, 0)).translate((x0, y, z))


def cyl_y(r, y0, y1, x=0.0, z=0.0, segments=64) -> Manifold:
  """Cylinder along Y from y0 to y1, centred at (x, z)."""
  return Manifold.cylinder(y1 - y0, r, r, segments).rotate((-90, 0, 0)).translate((x, y0, z))


def hex_prism_z(af, z0, z1, x=0.0, y=0.0, rot=30.0) -> Manifold:
  """Hexagonal prism along Z (a nut pocket): af = across flats."""
  r = af / math.sqrt(3)
  pts = [(x + r * math.cos(math.radians(rot + 60 * i)), y + r * math.sin(math.radians(rot + 60 * i))) for i in range(6)]
  return CrossSection([pts]).extrude(z1 - z0).translate((0, 0, z0))


def hex_prism_x(af, x0, x1, y=0.0, z=0.0) -> Manifold:
  return hex_prism_z(af, 0, x1 - x0).rotate((0, 90, 0)).translate((x0, y, z))


def hex_prism_y(af, y0, y1, x=0.0, z=0.0) -> Manifold:
  return hex_prism_z(af, 0, y1 - y0).rotate((-90, 0, 0)).translate((x, y0, z))


def side_profile_x(points_yz, x0, x1) -> Manifold:
  """Extrudes a (y, z) outline along X from x0 to x1."""
  cs = CrossSection([[(z, y) for y, z in points_yz]])
  # extrude along +Z, then map: new x <- old z, new y <- old y, new z <- old x
  m = cs.extrude(x1 - x0)
  return m.warp(lambda v: (v[2] + x0, v[1], v[0])) if _orientation(points_yz) else m.warp(lambda v: (v[2] + x0, v[1], v[0]))


def _orientation(points):
  return True


def prism_x(points_yz, x0, x1) -> Manifold:
  """Extrudes a (y, z) outline along X from x0 to x1 (any winding)."""
  pts = [(z, y) for y, z in points_yz]
  cs = CrossSection([pts])
  if cs.area() < 1e-9:
    cs = CrossSection([pts[::-1]])
  m = cs.extrude(x1 - x0)
  # m is in (u=z, v=y, w=x-x0); map to (x, y, z)
  return Manifold.compose([m]).warp(lambda v: (v[2] + x0, v[1], v[0])) if False else _swap_to_x(m, x0)


def _swap_to_x(m: Manifold, x0: float) -> Manifold:
  # (u, v, w) -> (w + x0, v, u): a reflection, so flip to keep it a proper solid
  r = m.rotate((0, -90, 0))           # (u, v, w) -> (-w, v, u)
  return r.mirror((1, 0, 0)).translate((x0, 0, 0))   # (w, v, u) + x0


def union(parts) -> Manifold:
  parts = [p for p in parts if p is not None]
  if not parts:
    return Manifold()
  return Manifold.batch_boolean(parts, manifold3d.OpType.Add) if len(parts) > 1 else parts[0]


def clean(m: Manifold, min_volume: float = 0.5) -> Manifold:
  """Drops zero-volume slivers that booleans can leave where faces coincide."""
  parts = [c for c in m.decompose() if c.volume() > min_volume]
  return union(parts) if parts else m


def revolve(points, a0_deg: float, a1_deg: float, step_deg: float = 0.5) -> Manifold:
  """Revolves an (r, z) outline about the Z axis from angle a0 to a1 (counterclockwise seen from +Z)."""
  span = a1_deg - a0_deg
  segs = max(4, int(math.ceil(span / step_deg)))
  full = int(round(segs * 360.0 / span))
  cs = CrossSection([points])
  if cs.area() < 1e-9:
    cs = CrossSection([points[::-1]])
  return Manifold.revolve(cs, full, span).rotate((0, 0, a0_deg))


def sector(r_out: float, a0_deg: float, a1_deg: float, r_in: float = 0.0, step_deg: float = 0.25) -> CrossSection:
  n = max(2, int(math.ceil((a1_deg - a0_deg) / step_deg)) + 1)
  a = np.radians(np.linspace(a0_deg, a1_deg, n))
  outer = [(r_out * math.cos(t), r_out * math.sin(t)) for t in a]
  inner = [(r_in * math.cos(t), r_in * math.sin(t)) for t in a[::-1]] if r_in > 0 else [(0.0, 0.0)]
  return CrossSection([outer + inner])


def polar_mask(radius_of, a0_deg, a1_deg, z0, z1, step_deg=0.25) -> Manifold:
  """Plan-view outline r = radius_of(angle) from a0 to a1 (pie shape from the centre), extruded from z0 to z1."""
  n = max(2, int(math.ceil((a1_deg - a0_deg) / step_deg)) + 1)
  pts = [(0.0, 0.0)]
  for a in np.linspace(a0_deg, a1_deg, n):
    r = radius_of(a)
    pts.append((r * math.cos(math.radians(a)), r * math.sin(math.radians(a))))
  return CrossSection([pts]).extrude(z1 - z0).translate((0, 0, z0))


def rot_x(m: Manifold, deg: float, about_y=0.0, about_z=0.0) -> Manifold:
  """Rotates about an axis parallel to X through (about_y, about_z). Positive turns +Y towards +Z."""
  return m.translate((0, -about_y, -about_z)).rotate((deg, 0, 0)).translate((0, about_y, about_z))


def write_stl(m: Manifold, path: str, name: str = "Honda Accord lane keeping part"):
  mesh = m.to_mesh()
  v = np.asarray(mesh.vert_properties)[:, :3].astype(np.float64)
  t = np.asarray(mesh.tri_verts)
  p0, p1, p2 = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
  n = np.cross(p1 - p0, p2 - p0)
  n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
  data = np.zeros(len(t), dtype=[("n", "<f4", 3), ("v0", "<f4", 3), ("v1", "<f4", 3), ("v2", "<f4", 3), ("a", "<u2")])
  data["n"], data["v0"], data["v1"], data["v2"] = n, p0, p1, p2
  with open(path, "wb") as f:
    f.write(name.encode("ascii", "replace")[:80].ljust(80, b" "))
    f.write(struct.pack("<I", len(t)))
    f.write(data.tobytes())


def read_stl_triangle_count(path: str) -> int:
  with open(path, "rb") as f:
    f.seek(80)
    return struct.unpack("<I", f.read(4))[0]


def on_bed(m: Manifold, rotate=(0.0, 0.0, 0.0)) -> Manifold:
  """Rotates (degrees about X, then Y, then Z), then centres on the bed with the lowest point at z = 0."""
  m = m.rotate(rotate)
  x0, y0, z0, x1, y1, z1 = m.bounding_box()
  return m.translate((-(x0 + x1) / 2, -(y0 + y1) / 2, -z0))


def size_of(m: Manifold):
  x0, y0, z0, x1, y1, z1 = m.bounding_box()
  return (x1 - x0, y1 - y0, z1 - z0)


def fits_bed(m: Manifold, bed) -> bool:
  sx, sy, sz = size_of(m)
  return (sx <= bed[0] and sy <= bed[1] and sz <= bed[2]) or (sy <= bed[0] and sx <= bed[1] and sz <= bed[2])
