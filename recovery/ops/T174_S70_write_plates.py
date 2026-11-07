"""
Print plates for Bambu Studio.

Lays the twelve printed parts of the side-slide mount out on print plates and writes each plate as a 3MF file
that Bambu Studio opens with the parts already placed and every part's print settings attached: 0.2 mm layers,
4 walls, 5 top and 5 bottom layers, 40% gyroid infill, no supports; the gear and the lever solid. Also draws a
picture of each plate and checks the files by reading them back.

  python3 plates.py          # writes ../plates/plate-*.3mf and plate-*.png and prints what went where

The plates are laid out for the 256 x 256 mm bed (Bambu Lab A1, P1P, P1S, X1, X1C, X1E) with nothing in the
front-left corner the X1 and P1 keep for their nozzle wipe. One file per plate: a 3MF without a printer in it
keeps whatever printer, filament and process the user has selected, and Bambu Studio centres its parts on that
bed. (A single project file holding several plates needs the printer's own settings written into it, so it is
only right for one printer model; make that once the printer is known.)

The file format follows Bambu Studio's own source (src/libslic3r/Format/bbs_3mf.cpp and src/slic3r/GUI/Plater.cpp,
read 2026-10-26): a plain 3MF model with the meshes in 3D/3dmodel.model, plus Metadata/model_settings.config with
each part's name and settings, which Bambu Studio reads whether or not the file came from Bambu Studio. The files
were checked by reading them back here, not by opening them in Bambu Studio. If a file will not open, import the
STL files instead and press A (arrange); the settings are then set by hand (see the README).
"""
import io
import os
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402

import render as R  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(HERE, "..", "stl", "side-slide-mount")
OUT_DIR = os.path.join(HERE, "..", "plates")

BED = (256.0, 256.0)      # mm; Bambu Lab A1, P1P, P1S, X1, X1C, X1E
EDGE = 10.0               # nothing closer than this to the bed's edge
GAP = 8.0                 # between parts: room for a brim if one is added
NO_GO = (18.0, 28.0)      # the front-left corner the X1 and P1 keep for the nozzle wipe (bed_exclude_area)

# the settings attached to every part, in Bambu Studio's own option names and spellings
STANDARD = {
  "layer_height": "0.2",
  "wall_loops": "4",
  "top_shell_layers": "5",
  "bottom_shell_layers": "5",
  "sparse_infill_density": "40%",
  "sparse_infill_pattern": "gyroid",
  "enable_support": "0",
}
SOLID = dict(STANDARD, sparse_infill_density="100%", sparse_infill_pattern="zig-zag")  # "zig-zag" is Bambu's rectilinear

# file stem -> (label on the picture, how many to print, settings)
PARTS = {
  "side-mounting-plate": ("mounting plate", 1, STANDARD),
  "side-motor-bracket": ("motor bracket", 1, STANDARD),
  "side-lever": ("lever (solid)", 1, SOLID),
  "side-gear": ("gear (solid)", 1, SOLID),
  "side-spool": ("spool", 1, STANDARD),
  "side-board-cover": ("board cover", 1, STANDARD),
  "side-strip-clamp": ("strip clamp", 1, STANDARD),
  "side-foot-bar": ("foot bar", 1, STANDARD),
  "side-foot-shim": ("foot shim", 4, STANDARD),
  "side-steering-wheel-teeth-11-straight-roads": ("teeth 11, straight roads", 1, STANDARD),
  "side-steering-wheel-teeth-15-highway": ("teeth 15, highway", 1, STANDARD),
  "side-steering-wheel-teeth-20-winding-roads": ("teeth 20, winding roads", 1, STANDARD),
}

# (file name, plate name as Bambu Studio shows it, the parts on it)
PLATES = [
  ("plate-1-mount", "1 of 4 the mount", ["side-mounting-plate", "side-motor-bracket", "side-lever", "side-gear", "side-spool",
                                         "side-board-cover", "side-strip-clamp", "side-foot-bar", "side-foot-shim"]),
  ("plate-2-teeth-11-straight-roads", "2 of 4 teeth 11 straight roads", ["side-steering-wheel-teeth-11-straight-roads"]),
  ("plate-3-teeth-15-highway", "3 of 4 teeth 15 highway", ["side-steering-wheel-teeth-15-highway"]),
  ("plate-4-teeth-20-winding-roads", "4 of 4 teeth 20 winding roads", ["side-steering-wheel-teeth-20-winding-roads"]),
]

PART_COLOR = (0.55, 0.70, 0.90)
SOLID_COLOR = (0.95, 0.72, 0.45)
BED_COLOR = (0.82, 0.82, 0.80)


# ---------- meshes ----------

def read_stl(path):
  """Binary STL -> (vertices (N, 3) float32, triangles (M, 3) int). Shared corners become one vertex."""
  with open(path, "rb") as f:
    f.read(80)
    n = struct.unpack("<I", f.read(4))[0]
    rec = np.dtype([("n", "<f4", 3), ("v0", "<f4", 3), ("v1", "<f4", 3), ("v2", "<f4", 3), ("a", "<u2")])
    data = np.frombuffer(f.read(), dtype=rec, count=n)
  corners = np.stack([data["v0"], data["v1"], data["v2"]], axis=1).reshape(-1, 3)
  verts, inverse = np.unique(corners, axis=0, return_inverse=True)
  tris = inverse.reshape(-1, 3)
  keep = (tris[:, 0] != tris[:, 1]) & (tris[:, 1] != tris[:, 2]) & (tris[:, 0] != tris[:, 2])
  return verts.astype(np.float32), tris[keep].astype(np.int64)


def footprint(verts):
  lo, hi = verts.min(axis=0), verts.max(axis=0)
  return float(hi[0] - lo[0]), float(hi[1] - lo[1])


def place(verts, x0, y0, rotated):
  """Move a mesh (any position) so its footprint's lower-left corner sits at (x0, y0), turned 90 degrees if asked."""
  v = verts.astype(np.float64)
  if rotated:
    v = np.stack([-v[:, 1], v[:, 0], v[:, 2]], axis=1)
  lo = v.min(axis=0)
  v[:, 0] += x0 - lo[0]
  v[:, 1] += y0 - lo[1]
  v[:, 2] -= lo[2]
  return v.astype(np.float32)


# ---------- layout ----------

def pack(items, usable_w):
  """Shelf packing. items: list of (key, (sx, sy)); rows run left to right, the first row at the back.
  Each part goes into the first row it fits (either way round), else starts a new row the flatter way round.
  Returns rows: list of (height, [(key, x_in_row, w, h, rotated)]) and the total depth."""
  rows = []
  for key, (sx, sy) in sorted(items, key=lambda it: -min(it[1])):
    ways = [((sx, sy), False), ((sy, sx), True)]
    done = False
    for row in rows:
      used = sum(w for _, _, w, _, _ in row[1]) + GAP * len(row[1])
      for (w, h), rot in ways:
        if h <= row[0] + 1e-9 and used + w <= usable_w + 1e-9:
          row[1].append((key, used, w, h, rot))
          done = True
          break
      if done:
        break
    if not done:
      (w, h), rot = min(ways, key=lambda wr: wr[0][1])
      if w > usable_w:
        raise ValueError(f"{key} is {w:.1f} mm wide: it does not fit a {BED[0]:.0f} x {BED[1]:.0f} bed")
      rows.append((h, [(key, 0.0, w, h, rot)]))
  depth = sum(h for h, _ in rows) + GAP * (len(rows) - 1)
  return rows, depth


def layout(plate_parts, meshes):
  """Where each piece goes on the bed: list of (stem, copy index, x0, y0, rotated, w, h). The group is centred
  on the bed, which is where Bambu Studio puts it anyway, with the front-left corner kept clear."""
  items = []
  for stem in plate_parts:
    for k in range(PARTS[stem][1]):
      items.append(((stem, k), footprint(meshes[stem][0])))
  usable_w = BED[0] - 2 * EDGE
  rows, depth = pack(items, usable_w)
  if depth > BED[1] - 2 * EDGE:
    raise ValueError(f"the parts need {depth:.0f} mm of bed depth, more than {BED[1] - 2 * EDGE:.0f}")
  width = max(sum(w for _, _, w, _, _ in r) + GAP * (len(r) - 1) for _, r in rows)
  x_left = (BED[0] - width) / 2
  y_top = (BED[1] + depth) / 2
  out = []
  y = y_top
  for h, row in rows:
    y -= h
    row_w = sum(w for _, _, w, _, _ in row) + GAP * (len(row) - 1)
    shift = 0.0
    if y < NO_GO[1] and x_left < NO_GO[0]:            # this row reaches the wipe corner: slide it right
      shift = min(NO_GO[0] + GAP - x_left, usable_w - row_w)
    for (stem, k), x, w, hh, rot in row:
      out.append((stem, k, x_left + shift + x, y, rot, w, hh))
    y -= GAP
  return out


def check_layout(placed):
  """No two pieces closer than GAP, everything inside the bed's edge, nothing in the wipe corner."""
  boxes = [(s, k, x, y, x + w, y + h) for s, k, x, y, _, w, h in placed]
  for i, a in enumerate(boxes):
    assert a[2] >= EDGE - 1e-6 and a[3] >= EDGE - 1e-6 and a[4] <= BED[0] - EDGE + 1e-6 and a[5] <= BED[1] - EDGE + 1e-6, a
    assert not (a[2] < NO_GO[0] and a[3] < NO_GO[1]), f"{a[0]} sits in the nozzle-wipe corner"
    for b in boxes[i + 1:]:
      apart = a[4] + GAP <= b[2] + 1e-6 or b[4] + GAP <= a[2] + 1e-6 or a[5] + GAP <= b[3] + 1e-6 or b[5] + GAP <= a[3] + 1e-6
      assert apart, f"{a[0]} and {b[0]} overlap"


# ---------- the 3MF file ----------

def xml_text(s):
  return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def model_xml(objects, title):
  """objects: list of (id, name, verts, tris). A plain 3MF core model, millimetres, one build item per object."""
  out = io.StringIO()
  out.write('<?xml version="1.0" encoding="UTF-8"?>\n')
  out.write('<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n')
  out.write(f' <metadata name="Application">accord-lane-keeping plates.py</metadata>\n')
  out.write(f' <metadata name="Title">{xml_text(title)}</metadata>\n')
  out.write(' <resources>\n')
  for oid, name, verts, tris in objects:
    out.write(f'  <object id="{oid}" name="{xml_text(name)}" type="model">\n   <mesh>\n    <vertices>\n')
    out.write("".join(f'     <vertex x="{x:.9g}" y="{y:.9g}" z="{z:.9g}"/>\n' for x, y, z in verts.tolist()))
    out.write('    </vertices>\n    <triangles>\n')
    out.write("".join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>\n' for a, b, c in tris.tolist()))
    out.write('    </triangles>\n   </mesh>\n  </object>\n')
  out.write(' </resources>\n <build>\n')
  for oid, _, _, _ in objects:
    out.write(f'  <item objectid="{oid}" transform="1 0 0 0 1 0 0 0 1 0 0 0" printable="1"/>\n')
  out.write(' </build>\n</model>\n')
  return out.getvalue()


def settings_xml(objects, plate_name):
  """Metadata/model_settings.config: each part's name and print settings, and the plate they are on."""
  out = io.StringIO()
  out.write('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n')
  for oid, name, settings, faces in objects:
    out.write(f'  <object id="{oid}">\n    <metadata key="name" value="{xml_text(name)}"/>\n    <metadata key="extruder" value="1"/>\n')
    for key, value in settings.items():
      out.write(f'    <metadata key="{key}" value="{value}"/>\n')
    out.write(f'    <part id="{oid}" subtype="normal_part">\n      <metadata key="name" value="{xml_text(name)}"/>\n')
    out.write('      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n')
    out.write(f'      <mesh_stat face_count="{faces}" edges_fixed="0" degenerate_facets="0" facets_removed="0" '
              'facets_reversed="0" backwards_edges="0"/>\n    </part>\n  </object>\n')
  out.write('  <plate>\n    <metadata key="plater_id" value="1"/>\n')
  out.write(f'    <metadata key="plater_name" value="{xml_text(plate_name)}"/>\n    <metadata key="locked" value="false"/>\n')
  out.write('    <metadata key="thumbnail_file" value="Metadata/plate_1.png"/>\n')
  for oid, _, _, _ in objects:
    out.write(f'    <model_instance>\n      <metadata key="object_id" value="{oid}"/>\n      <metadata key="instance_id" value="0"/>\n'
              f'      <metadata key="identify_id" value="{1000 + oid}"/>\n    </model_instance>\n')
  out.write('  </plate>\n  <assemble>\n')
  for oid, _, _, _ in objects:
    out.write(f'   <assemble_item object_id="{oid}" instance_id="0" transform="1 0 0 0 1 0 0 0 1 0 0 0" offset="0 0 0" />\n')
  out.write('  </assemble>\n</config>\n')
  return out.getvalue()


CONTENT_TYPES = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
                 ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
                 ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
                 ' <Default Extension="png" ContentType="image/png"/>\n</Types>')
RELS = ('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
        ' <Relationship Target="/Metadata/plate_1.png" Id="rel-2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"/>\n'
        '</Relationships>')


def write_3mf(path, title, plate_name, pieces, thumbnail_png):
  """pieces: list of (name, verts placed on the bed, tris, settings)."""
  objects = [(i + 1, name, v, t) for i, (name, v, t, _) in enumerate(pieces)]
  settings = [(i + 1, name, s, len(t)) for i, (name, _, t, s) in enumerate(pieces)]
  with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", CONTENT_TYPES)
    z.writestr("_rels/.rels", RELS)
    z.writestr("3D/3dmodel.model", model_xml(objects, title))
    z.writestr("Metadata/model_settings.config", settings_xml(settings, plate_name))
    z.writestr("Metadata/plate_1.png", thumbnail_png)


def read_back(path):
  """Read a 3MF the way a slicer would, enough to check it: objects with their meshes, build items, settings."""
  ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
  with zipfile.ZipFile(path) as z:
    names = set(z.namelist())
    for must in ("[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model", "Metadata/model_settings.config", "Metadata/plate_1.png"):
      assert must in names, f"{path}: {must} missing"
    model = ET.fromstring(z.read("3D/3dmodel.model"))
    config = ET.fromstring(z.read("Metadata/model_settings.config"))
    ET.fromstring(z.read("_rels/.rels"))
    ET.fromstring(z.read("[Content_Types].xml"))
    assert z.read("Metadata/plate_1.png")[:8] == b"\x89PNG\r\n\x1a\n"
  assert model.get("unit") == "millimeter"
  objects = {}
  for obj in model.findall("m:resources/m:object", ns):
    oid = int(obj.get("id"))
    assert oid > 0 and oid not in objects
    v = np.array([[float(e.get(a)) for a in "xyz"] for e in obj.findall("m:mesh/m:vertices/m:vertex", ns)])
    t = np.array([[int(e.get(a)) for a in ("v1", "v2", "v3")] for e in obj.findall("m:mesh/m:triangles/m:triangle", ns)])
    assert len(v) >= 4 and len(t) >= 4 and t.min() >= 0 and t.max() < len(v)
    assert (t[:, 0] != t[:, 1]).all() and (t[:, 1] != t[:, 2]).all() and (t[:, 0] != t[:, 2]).all()
    objects[oid] = (obj.get("name"), v, t)
  items = [int(e.get("objectid")) for e in model.findall("m:build/m:item", ns)]
  assert sorted(items) == sorted(objects), "build items do not match the objects"
  settings = {}
  for obj in config.findall("object"):
    oid = int(obj.get("id"))
    assert oid in objects, f"settings for an object that is not in the model: {oid}"
    settings[oid] = {m.get("key"): m.get("value") for m in obj.findall("metadata")}
    assert obj.find("part").get("id") == str(oid)
  plate = config.find("plate")
  on_plate = [int(mi.find("metadata[@key='object_id']").get("value")) for mi in plate.findall("model_instance")]
  assert sorted(on_plate) == sorted(objects), "the plate does not list every object"
  return objects, settings, {m.get("key"): m.get("value") for m in plate.findall("metadata")}


# ---------- pictures ----------

class _Mesh:
  """What render.render expects of a part: to_mesh() with vert_properties and tri_verts."""
  def __init__(self, verts, tris):
    self.vert_properties, self.tri_verts = verts, tris

  def to_mesh(self):
    return self


def bed_slab(thick=3.0):
  x1, y1 = BED
  v = np.array([[0, 0, -thick], [x1, 0, -thick], [x1, y1, -thick], [0, y1, -thick],
                [0, 0, 0], [x1, 0, 0], [x1, y1, 0], [0, y1, 0]], dtype=np.float64)
  t = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5],
                [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
  return _Mesh(v, t)


def view_3d(pieces, size):
  parts = [(bed_slab(), BED_COLOR)]
  for _, v, t, s in pieces:
    parts.append((_Mesh(v.astype(np.float64), t), SOLID_COLOR if s is SOLID else PART_COLOR))
  return R.render(parts, R.view_matrix(-62, 38), size=size, margin=0.03, background=(0.985, 0.985, 0.985))


def draw_top(ax, pieces, labels):
  """Looking down on the bed: every part's upward faces, shaded, and a label on each."""
  ax.add_patch(plt.Rectangle((0, 0), BED[0], BED[1], facecolor=(0.94, 0.94, 0.93), edgecolor="0.35", lw=1.2))
  ax.add_patch(plt.Rectangle((0, 0), NO_GO[0], NO_GO[1], facecolor=(0.90, 0.80, 0.80), edgecolor="none"))
  for g in range(50, int(BED[0]), 50):
    ax.plot([g, g], [0, BED[1]], color="0.82", lw=0.5, zorder=1)
    ax.plot([0, BED[0]], [g, g], color="0.82", lw=0.5, zorder=1)
  for (name, v, t, s), label in zip(pieces, labels):
    p = v[t]
    n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
    nz = n[:, 2] / np.maximum(np.linalg.norm(n, axis=1), 1e-12)
    up = nz > 0.02
    order = np.argsort(p[up][:, :, 2].mean(axis=1))
    base = np.array(SOLID_COLOR if s is SOLID else PART_COLOR)
    shade = (0.55 + 0.45 * nz[up][order])[:, None]
    ax.add_collection(PolyCollection(p[up][order][:, :, :2], facecolors=np.clip(base * shade, 0, 1), edgecolors="none", zorder=2))
    lo, hi = v.min(axis=0), v.max(axis=0)
    ax.text((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, label, ha="center", va="center", fontsize=7, zorder=3,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.85, edgecolor="none"))
  ax.set_xlim(-6, BED[0] + 6)
  ax.set_ylim(-6, BED[1] + 6)
  ax.set_aspect("equal")
  ax.set_xlabel("mm, left to right")
  ax.set_ylabel("mm, front to back")
  ax.set_xticks(range(0, int(BED[0]) + 1, 50))
  ax.set_yticks(range(0, int(BED[1]) + 1, 50))
  ax.tick_params(labelsize=7)


def picture(path, title, pieces, labels):
  img = view_3d(pieces, (900, 700))
  fig = plt.figure(figsize=(12.5, 5.6), dpi=150)
  ax1 = fig.add_axes([0.04, 0.09, 0.42, 0.80])
  draw_top(ax1, pieces, labels)
  ax1.set_title("from above", fontsize=9)
  ax2 = fig.add_axes([0.48, 0.03, 0.51, 0.90])
  ax2.imshow(img)
  ax2.set_axis_off()
  ax2.set_title("as it sits on the bed", fontsize=9)
  fig.suptitle(title, fontsize=11)
  fig.savefig(path)
  plt.close(fig)


def thumbnail(pieces):
  img = view_3d(pieces, (512, 512))
  buf = io.BytesIO()
  plt.imsave(buf, np.clip(img, 0, 1), format="png")
  return buf.getvalue()


# ---------- main ----------

def build(out_dir=OUT_DIR, stl_dir=STL_DIR):
  os.makedirs(out_dir, exist_ok=True)
  meshes = {stem: read_stl(os.path.join(stl_dir, stem + ".stl")) for stem in PARTS}
  report = []
  for n, (fname, plate_name, stems) in enumerate(PLATES, start=1):
    placed = layout(stems, meshes)
    check_layout(placed)
    pieces, labels = [], []
    for stem, k, x0, y0, rot, w, h in placed:
      verts, tris = meshes[stem]
      label, count, settings = PARTS[stem]
      name = stem if count == 1 else f"{stem} {k + 1} of {count}"
      pieces.append((name, place(verts, x0, y0, rot), tris, settings))
      labels.append(label if count == 1 else f"{label} {k + 1}")
    title = f"Plate {n} of {len(PLATES)}: {plate_name.split(' ', 3)[3]}"
    png = os.path.join(out_dir, fname + ".png")
    picture(png, f"{title}  ({BED[0]:.0f} x {BED[1]:.0f} mm bed)", pieces, labels)
    path = os.path.join(out_dir, fname + ".3mf")
    write_3mf(path, title, plate_name, pieces, thumbnail(pieces))
    # read it back and compare with what was placed
    objects, settings, plate = read_back(path)
    assert len(objects) == len(pieces) and plate["plater_name"] == plate_name
    for oid, (name, v, t) in objects.items():
      want = pieces[oid - 1]
      assert name == want[0] and len(v) == len(want[1]) and len(t) == len(want[2])
      assert np.allclose(v.min(axis=0), want[1].min(axis=0), atol=1e-4) and np.allclose(v.max(axis=0), want[1].max(axis=0), atol=1e-4)
      assert abs(v.min(axis=0)[2]) < 1e-6, "a part floats above the bed"
      for key, value in want[3].items():
        assert settings[oid][key] == value, (name, key)
    rows = [(PARTS[s][0] + ("" if PARTS[s][1] == 1 else f" {k + 1}"), x0, y0, rot, w, h) for s, k, x0, y0, rot, w, h in placed]
    report.append((n, fname, plate_name, rows, os.path.getsize(path)))
  return report


def main():
  report = build()
  print(f"Plates for a {BED[0]:.0f} x {BED[1]:.0f} mm bed, {EDGE:.0f} mm from the edge, {GAP:.0f} mm between parts, "
        f"the front-left {NO_GO[0]:.0f} x {NO_GO[1]:.0f} mm kept clear.\n")
  for n, fname, plate_name, rows, size in report:
    print(f"Plate {n}: {fname}.3mf ({size / 1e6:.1f} MB), {len(rows)} piece{'s' if len(rows) != 1 else ''}")
    for label, x0, y0, rot, w, h in rows:
      print(f"   {label:28s} at x {x0:6.1f}..{x0 + w:6.1f}  y {y0:6.1f}..{y0 + h:6.1f}{'  (turned 90 degrees)' if rot else ''}")
    print()
  print("Every part carries its settings: 0.2 mm layers, 4 walls, 5 top and 5 bottom layers, 40% gyroid, no supports;")
  print("the gear and the lever 100% (rectilinear). Read back and checked. Not opened in Bambu Studio here.")


if __name__ == "__main__":
  sys.exit(main())
