python3 - <<'EOF'
import pathlib
p = pathlib.Path("popassembly.py")
s = p.read_text()
old = "    cs = CrossSection.square((w - 2 * r, P.COVER_H - 2 * r), center=True).offset(r, CrossSection.JoinType.Round, circular_segments=48)"
assert s.count(old) == 1
s = s.replace(old, "    cs = CrossSection.square((w - 2 * r, P.COVER_H - 2 * r), center=True).offset(r, circular_segments=48)")
# tab placement avoiding the adjustment tab's zones, with two bolt positions on each tab
old2 = '''def tab_placements() -> list:
  """For each cover screw: (name, R, T, bolt (x, z)) with its tab turned to reach its slot."""
  out = []
  for name, xz, slot_i in COVER_SCREWS:
    b = PP.tab_bolt_on_slot(xz, PP.PL_SLOTS[slot_i])
    if b is None:
      raise ValueError(f"the {name}'s tab can't reach its slot")
    R, T, bolt = PP.place_tab(xz, b)
    out.append((name, R, T, bolt))
  return out'''
new2 = '''def _tab_clear(screw_xz, bolt_xz) -> bool:
  """A tab from screw to bolt (its whole width) stays out of the adjustment tab's zones, seen from below."""
  sx, sz = screw_xz
  bx, bz = bolt_xz
  d = np.array([bx - sx, bz - sz]) / math.hypot(bx - sx, bz - sz)
  n = np.array([-d[1], d[0]])
  half = PP.TAB_W / 2 + 2.0
  L = math.hypot(bx - sx, bz - sz)
  pts = [np.array([sx, sz]) + d * u + n * v for u in np.linspace(-half, L + half, 25) for v in np.linspace(-half, half, 7)]
  for zone in (TAB_HANDLE_ZONE, TAB_ARM_ZONE):
    x0, x1, _, _, z0, z1 = zone
    if any(x0 <= p[0] <= x1 and z0 <= p[1] <= z1 for p in pts):
      return False
  return True


def tab_placements() -> list:
  """For each cover screw: (name, R, T, bolt (x, z), reach) with its tab turned to reach its slot, using whichever of
  the tab's two nut positions lands on the slot without the tab crossing the adjustment tab or its arm."""
  out = []
  for name, xz, slot_i in COVER_SCREWS:
    best = None
    for reach in PP.TAB_REACHES:
      for b in PP.tab_bolts_on_slot(xz, PP.PL_SLOTS[slot_i], reach):
        if _tab_clear(xz, b):
          x, za, zb = PP.PL_SLOTS[slot_i]
          score = abs(b[1] - (za + zb) / 2.0)
          if best is None or score < best[0]:
            best = (score, b, reach)
    if best is None:
      raise ValueError(f"the {name}'s tab can't reach its slot")
    R, T, _ = PP.place_tab(xz, best[1])
    out.append((name, R, T, best[1], best[2]))
  return out'''
assert s.count(old2) == 1
s = s.replace(old2, new2)
s = s.replace("    return union([PP.place(tab, R, T) for _, R, T, _ in tab_placements()]).translate((0, self.cover_bottom - P.COVER_BOTTOM, 0))",
              "    return union([PP.place(tab, R, T) for _, R, T, _, _ in tab_placements()]).translate((0, self.cover_bottom - P.COVER_BOTTOM, 0))")
s = s.replace("    for _, R, T, (bx, bz) in tab_placements():", "    for _, R, T, (bx, bz), _ in tab_placements():")
p.write_text(s)

p = pathlib.Path("popparts.py")
s = p.read_text()
old = '''TAB_L = 40.0                  # its screw to its bolt'''
assert s.count(old) == 1
s = s.replace(old, '''TAB_L = 40.0                  # its screw to its far bolt hole; the near one is TAB_REACHES[0] out
TAB_REACHES = (24.0, 40.0)''')
old = '''  # the bolt end: through hole and a pocket for an M5 nyloc nut, from the top
  part = part - cyl(M5_CLEAR / 2, -t - 1.0, 1.0, TAB_L, 0.0, 32)
  r = M5_NUT_AF / math.sqrt(3.0)
  hexagon = CrossSection([[(TAB_L + r * math.cos(math.radians(60 * i)), r * math.sin(math.radians(60 * i))) for i in range(6)]])
  part = part - hexagon.extrude(M5_NUT_T + 0.3).translate((0, 0, -M5_NUT_T - 0.3))
  return clean(part)'''
new = '''  # two bolt holes, each with a pocket for an M5 nyloc nut from the top: use whichever lands on the plate's slot
  r = M5_NUT_AF / math.sqrt(3.0)
  for xb in TAB_REACHES:
    part = part - cyl(M5_CLEAR / 2, -t - 1.0, 1.0, xb, 0.0, 32)
    hexagon = CrossSection([[(xb + r * math.cos(math.radians(60 * i)), r * math.sin(math.radians(60 * i))) for i in range(6)]])
    part = part - hexagon.extrude(M5_NUT_T + 0.3).translate((0, 0, -M5_NUT_T - 0.3))
  return clean(part)'''
assert s.count(old) == 1
s = s.replace(old, new)
old = '''def tab_bolt_on_slot(screw_xz: tuple, slot: tuple) -> tuple | None:'''
new = '''def tab_bolts_on_slot(screw_xz: tuple, slot: tuple, reach: float = TAB_L) -> list:
  """The points on a plate slot (x, z_a, z_b) a tab from screw_xz reaches with a bolt hole reach away."""
  x, za, zb = slot
  sx, sz = screw_xz
  dx = x - sx
  if abs(dx) > reach:
    return []
  h = math.sqrt(reach ** 2 - dx ** 2)
  lo, hi = min(za, zb) + 3.0, max(za, zb) - 3.0
  return [(x, z) for z in (sz + h, sz - h) if lo <= z <= hi]


def tab_bolt_on_slot(screw_xz: tuple, slot: tuple) -> tuple | None:'''
assert s.count(old) == 1
s = s.replace(old, new)
# place_tab: the bolt may be at either reach: orient by direction only
p.write_text(s)
print("ok")
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 -c "
import popassembly as PA
for t in PA.tab_placements(): print(t[0], tuple(round(v,1) for v in t[3]), 'reach', t[4])
"