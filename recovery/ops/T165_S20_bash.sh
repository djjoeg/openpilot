python3 - <<'EOF'
p = "sideparts.py"
s = open(p).read()

def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:80], s.count(old))
    s = s.replace(old, new)

# teardrop along z, next to teardrop_x
sub('''def _guard() -> Manifold:''', '''def teardrop_z(r: float, z0: float, z1: float, x: float, y: float) -> Manifold:
  """A hole along z with a 45 degree point on its +y side (printed with +y up)."""
  return gothic(r, 48).extrude(z1 - z0).translate((x, y, z0))


def _guard() -> Manifold:''')

# the ear's ramp goes
a = s.index("def ear_bevel() -> Manifold:")
b = s.index("def side_bracket() -> Manifold:")
s = s[:a] + s[b:]

sub('''  ear = box(X_EAR[0], X_EAR[1], EAR_Y[0] - 0.5, EAR_Y[1], EAR_Z[0], EAR_Z[1])
  tab = box''', '''  # the ear: a fork of two lugs round the lever's hub, joined past the hub on the motor's side
  lug_in = box(X_EAR[0], X_EAR[1], EAR_Y[0] - 0.5, EAR_Y[1], EAR_Z[0], LEVER_Z[0] - LUG_GAP)
  lug_out = box(X_EAR[0], X_EAR[1], EAR_Y[0] - 0.5, EAR_Y[1], LEVER_Z[1] + LUG_GAP, EAR_Z[1])
  bridge = box(BRIDGE[0][0], BRIDGE[0][1], BRIDGE[1][0], BRIDGE[1][1], LEVER_Z[0] - LUG_GAP - 0.01, LEVER_Z[1] + LUG_GAP + 0.01)
  ear = lug_in + lug_out + bridge
  tab = box''')
sub('''  # the latch: the pin's hole, and the ramp before it
  part = part - teardrop_x(PIN_HOLE_D / 2, X_EAR[0] - 1.0, X_EAR[1] + 1.0, PIN_Y, PIN_Z)
  part = part - ear_bevel()
''', '''  # the lever's pin: pressed into the inner lug from its inner end; a blind hole in the outer lug, so the ear's outer face
  # (the switch's roller rides on it) stays whole; room for the lever's hub and arm swinging into either notch
  part = part - teardrop_z(PIN_PRESS_D / 2, EAR_Z[0] - 1.0, LEVER_Z[0] - LUG_GAP + 0.5, PIVOT[0], PIVOT[1])
  part = part - teardrop_z(PIN_SLIP_D / 2, LEVER_Z[1] + LUG_GAP - 0.5, PIN_Z[1], PIVOT[0], PIVOT[1])
  part = part - lever_swing_room(0.5)
''')

# the plate
sub('''  """The plate's parts (y, z ranges): along the rail; round the latch's nut; under the switch's holder; down to the
  spool's post."""
  return [((-16.0, 12.0), (BUMPER_Z[0], -26.0)), ((-13.0, 12.0), (-26.0, Z_RAIL[1])),
          ((8.0, 33.0), (PIN_Z - 13.0, Z_RAIL[1])), ((HOLDER_Y[0], HOLDER_Y[1]), (-2.0, HOLDER_Z[1])),
          ((12.0, POST[1][1]), (POST[2][0], PIN_Z - 12.0))]''',
'''  """The plate's parts (y, z ranges): along the rail; round the lever's slot and its notches; under the switch's holder;
  down to the spool's post."""
  return [((-16.0, 12.0), (BUMPER_Z[0], -26.0)), ((-13.0, 12.0), (-26.0, Z_RAIL[1])),
          ((8.0, PLATE_SLOT_Y), (PLATE_SLOT_Z, Z_RAIL[1])), ((HOLDER_Y[0], HOLDER_Y[1]), (-2.0, HOLDER_Z[1])),
          ((12.0, POST[1][1]), (POST[2][0], PLATE_SLOT_Z + 1.0))]''')
sub('''  parts.append(box(hx[1] - 0.01, BEVEL_TOP + 4.6, hy[0], SW_Y0 - 0.3, hz[0], hz[0] + 7.0))''',
    '''  parts.append(box(hx[1] - 0.01, STOP_X[1], hy[0], SW_Y0 - 0.3, hz[0], hz[0] + 7.0))''')
sub('''  # the plunger: through the boss and the plate; its nut goes on the inside
  part = part - cyl_x(5.2, X_COLLAR - 1.0, x1 + 1.0, y=PIN_Y, z=PIN_Z, segments=64)
''', '''  # the lever's slot and its two notches
  part = part - lever_cutter()
''')

# the lever, in place of the plunger and the pin's travel
a = s.index("def plunger(pin_back: float = 0.0) -> dict:")
b = s.index("def switch(roller_down: float = 0.0) -> dict:")
s = s[:a] + s[b:]
a = s.index("def pin_back_at(s: float) -> float:")
s = s[:a].rstrip() + "\n"

sub('''# ***** the spool *****''', '''# ***** the lever *****

def lever_room(clear: float = 0.0) -> Manifold:
  """The lever's hub and arm (no knob) as fitted, motor out, out of the notch; grown by `clear` across and round."""
  px, py = PIVOT
  arm = box(px - KNOB_D, px, py - SHANK_W / 2 - clear, py + SHANK_W / 2 + clear, LEVER_Z[0], LEVER_Z[1])
  return arm + cyl(HUB_R + clear, LEVER_Z[0], LEVER_Z[1], x=px, y=py, segments=64)


def side_lever() -> Manifold:
  """Carrier frame, motor out, out of the notch: the hub on the pin, the arm out towards 4 o'clock, the knob."""
  px, py = PIVOT
  z0, z1 = LEVER_Z
  part = lever_room() + cyl(KNOB_R, z0, z1, x=px - KNOB_D, y=py, segments=96)
  return clean(part - cyl(LEVER_BORE_D / 2, z0 - 1.0, z1 + 1.0, x=px, y=py, segments=48))


def lever_at(m: Manifold, s: float = 0.0, deg: float = 0.0) -> Manifold:
  """A part drawn with the lever (carrier frame) swung deg towards the dash about its pin, then slid in s."""
  if deg:
    px, py = PIVOT
    m = m.translate((-px, -py, 0.0)).rotate((0.0, 0.0, -deg)).translate((px, py, 0.0))
  return slid(m, s)


def lever_swing(m: Manifold, s_range, steps: int = 15) -> Manifold:
  """Everywhere `m` (drawn with the lever) goes swinging into a notch, slid in anywhere in s_range."""
  angles = np.linspace(0.0, LATCH_DEG, steps)
  return union([Manifold.batch_hull([lever_at(m, s, a) for s in s_range for a in (a0, a1)])
                for a0, a1 in zip(angles[:-1], angles[1:])])


def lever_swing_room(clear: float) -> Manifold:
  """The lever's hub and arm swinging into either notch (the bracket's room for them, with the bracket's own s)."""
  return lever_swing(lever_room(clear), (0.0,))


def lever_cutter() -> Manifold:
  """The plate's slot and notches: the arm in the slot from pulled out against the stop to slid in on the bumper, and
  swung into each notch. The notches' load faces are exactly where the arm rests on them: the outer notch's floor where
  the spring pulls it (motor fully out), the inner notch's outer face where the motor's weight pulls it (slid in)."""
  arm = lever_room(SLOT_CLEAR)
  straight = Manifold.batch_hull([lever_at(arm, s) for s in (-0.6, STROKE + 0.6)])
  cut = straight + lever_swing(arm, (-0.6, 0.0)) + lever_swing(arm, (STROKE, STROKE + 0.6))
  return cut ^ box(X_PL[0] - 1.0, X_PL[1] + 1.0, -100.0, 100.0, -200.0, 100.0)


def lever_pin() -> Manifold:
  return cyl(PIN_D / 2, PIN_Z[0], PIN_Z[1], x=PIVOT[0], y=PIVOT[1], segments=32)


# ***** the spool *****''')

# the plate's slot band
sub('''STOP_GAP = 0.2                    # pulled out against the stop, the ear is this far past where the notch holds it''',
    '''STOP_GAP = 0.2                    # pulled out against the stop, the ear is this far past where the notch holds it
PLATE_SLOT_Y = 42.0               # the plate reaches this far towards the dash round the notches
PLATE_SLOT_Z = -62.0              # ... and this far in, past the inner notch''')
open(p, "w").write(s)
EOF
/home/claude/bin/ruff check --isolated --select E4,E7,E9,F --line-length 140 sideparts.py; grep -n "PIN_Y\|BEVEL\|KIPP\|X_COLLAR\|X_PIN_TIP\|PIN_HOLE_D\|NUT_M10\|pin_back\|plunger" sideparts.py