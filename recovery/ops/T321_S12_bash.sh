python3 - <<'EOF'
p = 'rightcheck.py'
s = open(p, encoding='utf-8').read()
reps = [
("""\"\"\"
Checks for the right arm mount v4 (3 Nov 2026; v3 2 Nov): that the motor carrier goes down into the tower's tube
(off the car), and the arm with everything on it into the receiver from the key side, past the plate, the column
cover, the grip and the teeth; and that every part, bolt and wing-bolt sweep clears the others, the steering wheel's
grip and the teeth piece: the carrier slid anywhere from its end on the tower's top to the deepest stop, the stop
anywhere in its +-4 mm (the teeth piece moved the same way, as when the plate sits nearer or further than measured),
the arm slid 20 mm in or out across, and the steering wheel turned, with each of the three teeth sets (11, 15 and 20;
the 20 is the one on the car). Then the gear in mesh over each set's whole arc.
""",
 """\"\"\"
Checks for the right arm mount v5 (3 Nov 2026; v4 and v3 before): that the motor carrier goes down into the tower's
tube (off the car) and the slide's wing bolt in through the groove, and the arm with everything on it into the
receiver from the key side, past the plate, the column cover, the grip and the teeth; and that every part, bolt and
wing-bolt sweep clears the others, the steering wheel's grip and the teeth piece: the carrier slid anywhere in the
groove, from its end on the tower's top to the groove's top, the teeth piece 4 mm nearer or further than drawn (as
when the plate sits nearer or further than measured) with the gear at the drawn depth in it, the arm slid 5 mm in or
20 out across, and the steering wheel turned, with each of the three teeth sets (11, 15 and 20; the 20 is the one on
the car). Then the gear in mesh over each set's whole arc.

v5 adds checks that the parts work, not only that they clear (v3's open channel and v4's turning nut passed every
clearance check): every captive nut too tight in its slot to turn, even a nut at the smallest size the standard
allows; the carrier held in every direction (the groove's top and the tower's top stop it along the column, the tube
all round); and the slide's clearances. The stiffness under the motor's push is checked by stiffness.py.
"""),
("""def m4_nut(z0: float, x: float, y: float) -> Manifold:
  \"\"\"An M4 nut along z from z0, its corners along U (as it sits in the carrier's slot).\"\"\"
  return hex_prism_z(RA.M4_NUT_AF, z0, z0 + RA.M4_NUT_T, x=x, y=y, rot=RA.THETA) - cyl(2.0, z0 - 1.0, z0 + 5.0, x=x, y=y, segments=20)
""",
 """M5_E_MIN = 8.79      # the smallest across-corners an M5 nut may have (ISO 4032): the one most likely to turn


def nut_min(rot: float) -> Manifold:
  \"\"\"An M5 nut at the standard's smallest across-corners, along z, centred on z = 0 (to show it can't turn).\"\"\"
  return hex_prism_z(M5_E_MIN * math.cos(math.radians(30)), -1.9, 1.9, rot=rot)
"""),
("""def hardware(dz: float, gap: float, swept: bool = False, arm_dx: float = 0.0) -> dict:
  \"\"\"The bolts and nuts in the steering wheel frame: the carrier slid dz from the nominal depth, the stop set with
  `gap` from its washer's top to the bar's end (RA.STOP_GAP at the drawn depth), the arm slid arm_dx across (+ to
  your right). swept: the wing bolts as the room their wings need.\"\"\"""",
 """def slide_nut(dz: float = 0.0, small_turned: bool = False) -> Manifold:
  \"\"\"The slide's M5 nut in the carrier's bar, its axis along u, flats facing along the column (as in its slot);
  small_turned: the smallest standard nut turned 30 degrees, corners towards the slot's walls.\"\"\"
  m = nut_min(0.0) if small_turned else nut(rot=30.0)
  return in_motor_frame(m.rotate((0.0, 90.0, 0.0)), sum(RA.SLIDE_NUT_U) / 2, RA.BAR_UV[1], RA.SLIDE_Z0 + dz)


def hardware(dz: float = 0.0, swept: bool = False, arm_dx: float = 0.0) -> dict:
  \"\"\"The bolts and nuts in the steering wheel frame: the carrier slid dz from the nominal depth, the arm slid
  arm_dx across (+ to your right). swept: the wing bolts as the room their wings need.\"\"\""""),
("""  # the push bolt: along -u through the tower's outer wall onto the bar's face, its nut in the slot in that wall
  pv, pzz = RA.PUSH_VZ
  out["push bolt"] = in_motor_frame(wb.rotate((0.0, 90.0, 0.0)), RA.BAR_U[1] + 20.0, pv, pzz)        # -z -> -u
  out["push nut"] = in_motor_frame(nut(rot=0.0).rotate((0.0, 90.0, 0.0)), sum(RA.PUSH_NUT_U) / 2, pv, pzz)
  # the stop (v4): an M4 x 30 up the bar's middle from below, a fender washer under its hex head, the jam nut on it
  # against the bar's end, the nut in the slot 4 mm in
  sx, sy = RA.rad(*RA.BAR_UV)
  end = RA.BAR_Z[0] + dz
  w_top = end - gap
  under = w_top - RA.WASHER_T                       # the head's underside
  out["stop bolt"] = hex_prism_z(7.0, under - 2.8, under, x=sx, y=sy, rot=RA.THETA) + \\
    cyl(1.95, under - 0.5, under + 30.0, x=sx, y=sy, segments=20)
  out["stop washer"] = cyl(RA.WASHER_OD / 2, under, w_top, x=sx, y=sy, segments=48) - cyl(2.2, under - 1.0, w_top + 1.0, x=sx, y=sy, segments=20)
  out["stop jam nut"] = m4_nut(end - RA.M4_NUT_T, sx, sy)
  out["stop nut"] = m4_nut(end + RA.M4_SLOT_IN + 0.2, sx, sy)
  fixed = ("receiver bolt", "receiver nut")                 # in the plate; the rest move with the arm across""",
 """  # the slide (v5): the wing bolt along -u through a fender washer and the groove into the nut in the carrier's bar;
  # all three move with the carrier
  bv, zz = RA.BAR_UV[1], RA.SLIDE_Z0 + dz
  face = RA.TOWER_U[1]
  out["slide bolt"] = in_motor_frame(wb.rotate((0.0, 90.0, 0.0)), face + RA.WASHER_T, bv, zz)       # -z -> -u
  washer = cyl_x(RA.WASHER_OD / 2, face, face + RA.WASHER_T, y=bv, z=zz, segments=48) - \\
    cyl_x(2.7, face - 1.0, face + RA.WASHER_T + 1.0, y=bv, z=zz, segments=24)
  out["slide washer"] = washer.rotate((0.0, 0.0, RA.THETA))
  out["slide nut"] = slide_nut(dz)
  fixed = ("receiver bolt", "receiver nut")                 # in the plate; the rest move with the arm across"""),
("""from cadlib import box, cyl, hex_prism_z, revolve""", """from cadlib import box, cyl, cyl_x, hex_prism_z, revolve"""),
]
for a, b in reps:
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
EOF
grep -n "def nut\b\|def nut(" -A 3 rightcheck.py | head; grep -n "cyl_x" cadlib.py | head -2