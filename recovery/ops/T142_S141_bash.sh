python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)
rep('''TAB_END_R = 14.0              # the round end round its screw: wider than the cover's screw cup, so it bridges it''',
'''# Two kinds of tab: "cup", for the self-tapping screw in the round cup under the key cylinder (its round end bridges the
# cup; the screw's pan head and a washer sit in a counterbore underneath), and "slim", for the M5 right beside the
# tab's slot (a socket-head M5 in a smaller counterbore, so its end stays clear of the tab's arm).
TAB_KINDS = {"cup": {"end_r": 12.5, "head": (6.6, 4.0)}, "slim": {"end_r": 7.5, "head": (4.6, 5.0)}}
TAB_END_R = TAB_KINDS["cup"]["end_r"]''')
rep('''TAB_HEAD = (6.6, 4.0)         # the screw head's counterbore from below: radius (the M5's washer head), depth''', '')
rep('''def pop_screw_tab() -> Manifold:
  """Tab frame: its screw at the origin, its slot along +x from TAB_SLOT[0] to TAB_SLOT[1], +z towards the cover (its
  top face z = 0). The nut for the plate's bolt sits in a channel along the slot's top and can slide along it."""
  t = TAB_T
  end = cyl(TAB_END_R, -t, 0.0, 0.0, 0.0, 64)''',
'''def pop_screw_tab(kind: str = "cup") -> Manifold:
  """Tab frame: its screw at the origin, its slot along +x from TAB_SLOT[0] to TAB_SLOT[1], +z towards the cover (its
  top face z = 0). The nut for the plate's bolt sits in a channel along the slot's top and can slide along it."""
  t = TAB_T
  k = TAB_KINDS[kind]
  end = cyl(k["end_r"], -t, 0.0, 0.0, 0.0, 64)''')
rep('''  part = part - cyl(TAB_HEAD[0], -t - 1.0, -t + TAB_HEAD[1], segments=48)''',
'''  part = part - cyl(k["head"][0], -t - 1.0, -t + k["head"][1], segments=48)''')
p.write_text(s)

p = pathlib.Path("popassembly.py")
s = p.read_text()
rep('''TAB_ARM = (-34.0, -6.0, -185.0, -112.0)''', '''TAB_ARM = (-41.0, -11.0, -185.0, -112.0)    # under the paddle's left two thirds, as in your photos''')
rep('''COVER_SCREWS = (("4 x 16 self-tapping under the key cylinder", (38.0, -98.0), (12.0, 15.0), True),
                ("M5 x 12 screw-washer beside the tab's slot", (2.0, -178.0), (10.0, 15.0), True),
                ("4 x 16 self-tapping behind the paddle", (-18.0, -125.0), (10.0, 20.0), False))''',
'''COVER_SCREWS = (("4 x 16 self-tapping under the key cylinder", (38.0, -98.0), (12.0, 15.0), "cup"),
                ("M5 x 12 screw-washer beside the tab's slot", (1.0, -175.0), (4.0, 15.0), "slim"),
                ("4 x 16 self-tapping behind the paddle", (-18.0, -125.0), (10.0, 20.0), None))''')
rep('''def _keep_out_xz() -> list:
  """Rectangles (x0, x1, z0, z1) seen from below that a tab must stay out of: the paddle, the arm, your fingers."""
  m = 3.0
  return [(TAB_PADDLE[0] - m, TAB_PADDLE[1] + m, TAB_PADDLE[2] - m, TAB_PADDLE[3] + 25.0),
          (TAB_ARM[0] - m, TAB_ARM[1] + m, TAB_ARM[2] - m, TAB_ARM[3]),
          (TAB_FINGERS[0], TAB_FINGERS[1], TAB_FINGERS[4], TAB_FINGERS[5])]''',
'''def _keep_out_xz() -> list:
  """Rectangles (x0, x1, z0, z1) seen from below that a tab must stay out of: the paddle, the arm, your fingers."""
  m = 2.0
  return [(TAB_PADDLE[0] - m, TAB_PADDLE[1] + m, TAB_PADDLE[2] - m, TAB_PADDLE[3] + 25.0),
          (TAB_ARM[0] - m, TAB_ARM[1] + 1.0, TAB_ARM[2] - m, TAB_ARM[3]),
          (TAB_FINGERS[0], TAB_FINGERS[1], TAB_FINGERS[4], TAB_FINGERS[5])]''')
rep('''def _tab_clear(screw_xz, bolt_xz, others=()) -> bool:''', '''def _tab_clear(screw_xz, bolt_xz, others=(), end_r: float = PP.TAB_END_R) -> bool:''')
rep('''  pts += [np.array([sx, sz]) + PP.TAB_END_R * np.array([math.cos(a), math.sin(a)]) for a in np.linspace(0, 2 * math.pi, 24)]''',
'''  pts += [np.array([sx, sz]) + end_r * np.array([math.cos(a), math.sin(a)]) for a in np.linspace(0, 2 * math.pi, 24)]''')
rep('''def tab_options(screw_xz, others=()) -> list:
  """Every (slot index, bolt (x, z)) a tab from screw_xz can use."""
  out = []
  for i, slot in enumerate(PP.PL_SLOTS):
    for b in PP.tab_bolts_on_slot(screw_xz, slot):
      if _tab_clear(screw_xz, b, others):
        out.append((i, b))
  return out''',
'''def tab_options(screw_xz, others=(), kind: str = "cup") -> list:
  """Every (slot index, bolt (x, z)) a tab from screw_xz can use."""
  out = []
  r = PP.TAB_KINDS[kind]["end_r"]
  for i, slot in enumerate(PP.PL_SLOTS):
    for b in PP.tab_bolts_on_slot(screw_xz, slot):
      if _tab_clear(screw_xz, b, others, r):
        out.append((i, b))
  return out''')
rep('''def tab_placements(screws=None, plate_dxz=(0.0, 0.0)) -> list:
  """For each usable cover screw: (name, R, T, bolt (x, z), slot index), the plate shifted by plate_dxz. Picks each
  bolt nearest its slot's middle, the screws in order, each tab clear of the ones before."""
  screws = screws if screws is not None else [(n, xz) for n, xz, _, use in COVER_SCREWS if use]
  dx, dz = plate_dxz
  out, placed = [], []
  for name, xz in screws:
    rel = (xz[0] - dx, xz[1] - dz)               # in the plate's own frame
    opts = tab_options(rel, placed)''',
'''def tab_placements(screws=None, plate_dxz=(0.0, 0.0)) -> list:
  """For each usable cover screw: (name, R, T, bolt (x, z), slot index, kind), the plate shifted by plate_dxz. Picks
  each bolt nearest its slot's middle, the screws in order, each tab clear of the ones before."""
  screws = screws if screws is not None else [(n, xz, kind) for n, xz, _, kind in COVER_SCREWS if kind]
  dx, dz = plate_dxz
  out, placed = [], []
  for name, xz, kind in screws:
    rel = (xz[0] - dx, xz[1] - dz)               # in the plate's own frame
    opts = tab_options(rel, placed, kind)''')
rep('''    R, T, _ = PP.place_tab(xz, (b[0] + dx, b[1] + dz))
    out.append((name, R, T, (b[0] + dx, b[1] + dz), i))
  return out''', '''    R, T, _ = PP.place_tab(xz, (b[0] + dx, b[1] + dz))
    out.append((name, R, T, (b[0] + dx, b[1] + dz), i, kind))
  return out''')
rep('''  usable = [(nm, xz, tol) for nm, xz, tol, use in COVER_SCREWS if use]''', '''  usable = [(nm, xz, tol, kind) for nm, xz, tol, kind in COVER_SCREWS if kind]''')
rep('''  grids = [[(xz[0] + fx * tol[0], xz[1] + fz * tol[1]) for fx in np.linspace(-1, 1, n) for fz in np.linspace(-1, 1, n)]
           for _, xz, tol in usable]''', '''  grids = [[(xz[0] + fx * tol[0], xz[1] + fz * tol[1]) for fx in np.linspace(-1, 1, n) for fz in np.linspace(-1, 1, n)]
           for _, xz, tol, _ in usable]''')
rep('''        tab_placements([(usable[k][0], combo[k]) for k in range(len(usable))], (0.0, dz))''',
'''        tab_placements([(usable[k][0], combo[k], usable[k][3]) for k in range(len(usable))], (0.0, dz))''')
rep('''  def tabs(self) -> Manifold:
    tab = self.p["tab"]
    return union([PP.place(tab, R, T) for _, R, T, _, _ in tab_placements()]).translate((0, self.cover_bottom - P.COVER_BOTTOM, 0))''',
'''  def tabs(self) -> Manifold:
    return union([PP.place(self.p["tab_" + kind], R, T) for _, R, T, _, _, kind in tab_placements()]).translate(
      (0, self.cover_bottom - P.COVER_BOTTOM, 0))''')
rep('''    for _, R, T, (bx, bz), _ in tab_placements():''', '''    for _, R, T, (bx, bz), _, kind in tab_placements():''')
rep('''      parts.append(cyl_y(5.5, T[1] - PP.TAB_T + dy, T[1] - PP.TAB_T + PP.TAB_HEAD[1] - 0.5 + dy, x=T[0], z=T[2], segments=24))''',
'''      hr, hd = PP.TAB_KINDS[kind]["head"]
      parts.append(cyl_y(hr - 0.6, T[1] - PP.TAB_T + dy, T[1] - PP.TAB_T + hd - 0.5 + dy, x=T[0], z=T[2], segments=24))''')
p.write_text(s)
print("ok")
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && python3 - <<'EOF'
import pathlib
p = pathlib.Path("run_u.py")
s = p.read_text()
s = s.replace('''           "tab": PP.pop_screw_tab()}''', '''           "tab_cup": PP.pop_screw_tab("cup"), "tab_slim": PP.pop_screw_tab("slim")}''')
s = s.replace('''  print("tabs:", [(n, tuple(round(float(v), 1) for v in b), r) for n, R, T, b, r in PA.tab_placements()])''',
              '''  print("tabs:", [(n, tuple(round(float(v), 1) for v in b), r, k) for n, R, T, b, r, k in PA.tab_placements()])
  print("tab fit study:", PA.tab_fit_study(n=5))''')
p.write_text(s)
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib timeout 900 python3 -c "
import time; T0=time.time()
import popparts as PP, popassembly as PA
for r in PA.tab_placements(): print(r[0], tuple(round(float(v),1) for v in r[3]), 'slot', r[4], r[5])
pl = PP.pop_column_plate()
print('plate/lever overlap', round((pl ^ PA.tab_lever_sweep()).volume(), 2))
print(PA.tab_fit_study(n=5), round(time.time()-T0), 's')
"