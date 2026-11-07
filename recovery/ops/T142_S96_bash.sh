python3 - <<'EOF'
import pathlib
p = pathlib.Path("popassembly.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

rep('''STALK_DOWN_DEG = 30.0      # the wiper stalk pushed all the way down (HI): an estimate, not measured''',
'''STALK_DOWN_DEG = 36.0      # the wiper stalk pushed all the way down (HI): 3 notches (your count), taken as 12 degrees
                           # each until you measure it''')
rep('''KEY_ROOM = (22.0, 60.0)    # the key in its cylinder and your fingers turning it: radius and length out from the bezel''',
'''KEY_HEAD = (20.0, 45.0)    # the key in the ignition, its head turned to any position: radius and length out from the bezel
KEY_ROOM = (22.0, 60.0)    # your fingers turning the key: radius and length out from the bezel (checked with the motor
                           # popped off; with it on the report gives the room left)''')
rep('''TILT_LEVER_ZONE = (-45.0, 8.0, -130.0, -48.0, -200.0, -45.0)   # the tilt lever, tucked up to hanging down (estimate from
                                                                 # your photos: left of the middle, under the cover)''',
'''# the adjustment tab (the steering column's tilt and reach lever), from your photos: its handle hangs under the cover
# left of the middle near the cover's steering wheel end; its steel arm runs back from the handle into the column.
# Pulled, both swing down. Boxes (x0, x1, y0, y1, z0, z1):
TAB_HANDLE_ZONE = (-58.0, 12.0, -130.0, -46.0, -150.0, -45.0)   # the handle, its swing and your fingers on it
TAB_ARM_ZONE = (-36.0, -2.5, -100.0, -46.0, -190.0, -150.0)     # its arm behind it, swinging down
TILT_LEVER_ZONE = TAB_HANDLE_ZONE
# the lower cover's three screws, where the model puts them (x, z): Honda's layout (its parts list and remote starter
# instructions), placed by your photos. The M5 is the round cup right of the tab; the other two are from Honda's drawing
# only (+-25 mm), and the screw tabs reach that far.
COVER_SCREWS = (("M5 x 12 with washer", (42.0, -100.0), 0), ("4 x 16 self-tapping, right", (36.0, -198.0), 0),
                ("4 x 16 self-tapping, middle", (-12.0, -200.0), 1))''')
# cache key includes the adjustment
rep('''def cached(name: str, build):''', '''def cached(name: str, build):''')
# the key head
rep('''def key_room() -> Manifold:
  kd = np.array(P.KEY_TO) - np.array(P.KEY_FROM)
  kd /= np.linalg.norm(kd)
  r, L = KEY_ROOM
  return CA.rod(np.array(P.KEY_TO), np.array(P.KEY_TO) + L * kd, r)''',
'''def key_room(size: tuple = KEY_ROOM) -> Manifold:
  kd = np.array(P.KEY_TO) - np.array(P.KEY_FROM)
  kd /= np.linalg.norm(kd)
  r, L = size
  return CA.rod(np.array(P.KEY_TO), np.array(P.KEY_TO) + L * kd, r)


def cover_model(back_z: float = -400.0) -> Manifold:
  """The steering column covers: a rounded box along the column (flat underneath, as in your photos), COVER_FRONT_W
  wide at its front edge widening to COVER_W at COVER_TAPER_Z, from COVER_BOTTOM up to COVER_H above it."""
  from manifold3d import CrossSection

  def section(w, z):
    r = 26.0
    cs = CrossSection.square((w - 2 * r, P.COVER_H - 2 * r), center=True).offset(r, CrossSection.JoinType.Round, circular_segments=48)
    return cs.translate((0.0, P.COVER_BOTTOM + P.COVER_H / 2)).extrude(0.5).translate((0, 0, z))

  front_w = min(P.COVER_FRONT_W, P.COVER_W)
  taper = Manifold.batch_hull([section(front_w, P.COVER_FRONT_Z - 0.5), section(P.COVER_W, P.COVER_TAPER_Z)])
  back = section(P.COVER_W, 0.0).scale((1.0, 1.0, (P.COVER_TAPER_Z + 0.5 - back_z) / 0.5)).translate((0, 0, back_z))
  return taper + back


def tab_placements() -> list:
  """For each cover screw: (name, R, T, bolt (x, z)) with its tab turned to reach its slot."""
  out = []
  for name, xz, slot_i in COVER_SCREWS:
    b = PP.tab_bolt_on_slot(xz, PP.PL_SLOTS[slot_i])
    if b is None:
      raise ValueError(f"the {name}'s tab can't reach its slot")
    R, T, bolt = PP.place_tab(xz, b)
    out.append((name, R, T, bolt))
  return out''')
# PopAssembly: plate, tabs, covers, lever zones, key head
rep('''  def plate(self) -> Manifold:
    return self.p["plate"].translate((0, self.cover_bottom - P.COVER_BOTTOM, 0))

  def pads(self) -> Manifold:
    return PP.pop_plate_pads().translate((0, self.cover_bottom - P.COVER_BOTTOM, 0))''',
'''  def plate(self) -> Manifold:
    return self.p["plate"].translate((0, self.cover_bottom - P.COVER_BOTTOM, 0))

  def tabs(self) -> Manifold:
    tab = self.p["tab"]
    return union([PP.place(tab, R, T) for _, R, T, _ in tab_placements()]).translate((0, self.cover_bottom - P.COVER_BOTTOM, 0))

  def tab_bolts(self) -> Manifold:
    """The tabs' M5 bolts (head and washer under the plate, nyloc nut in the tab) and the cover screws' heads."""
    from cadlib import cyl_y
    y1 = PP.plate_top_y_u() + self.cover_bottom - P.COVER_BOTTOM
    y0 = y1 - PP.PL_T_U
    parts = []
    for _, R, T, (bx, bz) in tab_placements():
      parts.append(cyl_y(2.5, y0 - 1.0, y1 + PP.TAB_T, x=bx, z=bz, segments=16) + cyl_y(5.0, y0 - 4.5, y0, x=bx, z=bz, segments=6))
      parts.append(cyl_y(5.5, T[1] - PP.TAB_T + self.cover_bottom - P.COVER_BOTTOM, T[1] - PP.TAB_T + PP.TAB_HEAD[1] - 0.5 + self.cover_bottom - P.COVER_BOTTOM,
                         x=T[0], z=T[2], segments=24))
    return union(parts)''')
rep('''  def covers(self) -> Manifold:
    return CA.ColumnAssembly.covers(self.side)''',
'''  def covers(self) -> Manifold:
    return cover_model()''')
rep('''  def key_room(self) -> Manifold:
    return key_room()

  def tilt_lever(self) -> Manifold:
    return box(*TILT_LEVER_ZONE)''',
'''  def key_room(self) -> Manifold:
    return key_room()

  def key_head(self) -> Manifold:
    return key_room(KEY_HEAD)

  def tilt_lever(self) -> Manifold:
    return box(*TAB_HANDLE_ZONE) + box(*TAB_ARM_ZONE)''')
rep('''  def car_parts(self) -> list:
    return [("column covers", self.covers()), ("hub", self.hub()), ("spoke sweep zone", self.spoke_zone()),
            ("wiper stalk (all positions)", self.stalk()), ("key cylinder", self.key()),
            ("the key and your fingers on it", self.key_room()), ("tilt lever's swing", self.tilt_lever()),
            ("dash below the column", self.dash())]''',
'''  def car_parts(self) -> list:
    return [("column covers", self.covers()), ("hub", self.hub()), ("spoke sweep zone", self.spoke_zone()),
            ("wiper stalk (all positions)", self.stalk()), ("key cylinder", self.key()),
            ("the key in the ignition", self.key_head()), ("adjustment tab, its arm and their swing", self.tilt_lever()),
            ("dash below the column", self.dash())]''')
p.write_text(s)
print("ok")
EOF
grep -n "pads\|PD\b\|plate's rubber" popassembly.py | head