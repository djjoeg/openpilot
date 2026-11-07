python3 - <<'EOF'
p = "sideassembly.py"
s = open(p).read()
def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:80], s.count(old))
    s = s.replace(old, new)

sub('''  - nothing touches what it shouldn't while the motor slides in and out (every mm of the 40), only the latch's pin on
    the ear, the switch's roller on the ear's end, and the block on its rail''',
'''  - nothing touches what it shouldn't while the motor slides in and out (every mm of the 40), only the switch's roller
    on the ear's end, and the block on its rail; the lever's arm runs in its slot in the plate without touching it
  - the lever swings into either notch without touching anything, and once in a notch the plate holds it: latched, the
    motor can't slide in; parked, it can't slide out''')
sub('''  - the forces: spring, weight, latch, switch''', '''  - the forces: spring, weight, the lever, switch''')
sub('''          "rail": S.rail(), "block": S.block(), "block screws": S.block_screws()}''',
    '''          "rail": S.rail(), "block": S.block(), "block screws": S.block_screws(), "lever": S.side_lever(),
          "lever's pin": S.lever_pin()}''')
sub('''  def movers(self, s: float, wheel_deg: float = 0.0) -> dict:
    sp = S.spring_parts(s)
    gear = self.p["gear"].rotate((0, 0, MESH_PHASE - FP.FACE_RATIO * wheel_deg))
    return {"motor bracket": S.slid(self.p["bracket"], s), "motor, board and plugs": S.slid(self.p["motor"], s),
            "gear": S.slid(gear, s), "block": S.slid(self.p["block"], s), "block screws": S.slid(self.p["block screws"], s),
            "spring's clamp": sp["clamp"]}''',
'''  def movers(self, s: float, wheel_deg: float = 0.0, lever_deg: float = 0.0) -> dict:
    """The moving parts, slid in s; the lever swung lever_deg towards the dash (into a notch)."""
    sp = S.spring_parts(s)
    gear = self.p["gear"].rotate((0, 0, MESH_PHASE - FP.FACE_RATIO * wheel_deg))
    return {"motor bracket": S.slid(self.p["bracket"], s), "motor, board and plugs": S.slid(self.p["motor"], s),
            "gear": S.slid(gear, s), "block": S.slid(self.p["block"], s), "block screws": S.slid(self.p["block screws"], s),
            "spring's clamp": sp["clamp"], "lever": S.lever_at(self.p["lever"], s, lever_deg),
            "lever's pin": S.slid(self.p["lever's pin"], s)}''')
sub('''    """The fixed parts; the plunger's pin and the switch's roller where the ear leaves them with the motor slid in s."""
    pl = S.plunger(S.pin_back_at(s))
    roller_down''', '''    """The fixed parts; the switch's roller where the ear leaves it with the motor slid in s."""
    roller_down''')
sub('''    return {"mounting plate": self.p["plate"], "rail": self.p["rail"], "plunger and nut": pl["fixed"],
            "plunger's knob": pl["knob"], "plunger's pin": pl["pin"], "switch": sw["body"],''',
    '''    return {"mounting plate": self.p["plate"], "rail": self.p["rail"], "switch": sw["body"],''')
sub('''EXPECTED = {("block", "rail"), ("motor bracket", "plunger's pin"), ("motor bracket", "switch's lever and roller"),
            ("block screws", "motor bracket")}''', '''EXPECTED = {("block", "rail"), ("motor bracket", "switch's lever and roller"), ("block screws", "motor bracket")}''')
sub('''  """Moving against fixed parts at every slide position (carrier frame). Only the expected touches are left out:
  the block on its rail, the pin and the roller on the ear (they rest on it)."""''',
    '''  """Moving against fixed parts at every slide position (carrier frame), the lever out of its notches. Only the expected
  touches are left out: the block on its rail, the switch's roller on the ear (it rests on it)."""''')
sub('''  # the pin and the roller: resting on the ear (touching), never into it
  for s in steps:
    mv, fx = A.movers(s), A.fixed(s)
    for fn in ("plunger's pin", "switch's lever and roller"):
      v = overlap(mv["motor bracket"], fx[fn].translate((-0.05 if fn == "plunger's pin" else 0.0, 0.0, 0.05 if fn != "plunger's pin" else 0.0)))
      key = f"motor bracket/{fn} (resting on it)"
      if v > res.get(key, (0.0, None))[0]:
        res[key] = (v, s)''', '''  # the switch's roller: resting on the ear's end (touching), never into it
  for s in steps:
    mv, fx = A.movers(s), A.fixed(s)
    v = overlap(mv["motor bracket"], fx["switch's lever and roller"].translate((0.0, 0.0, 0.05)))
    key = "motor bracket/switch's lever and roller (resting on it)"
    if v > res.get(key, (0.0, None))[0]:
      res[key] = (v, s)''')
sub('''  for a, b in (("motor bracket", "motor, board and plugs"), ("gear", "motor bracket"), ("gear", "motor, board and plugs"),
               ("spring's clamp", "motor, board and plugs")):
    res[f"{a}/{b} (both move)"] = (overlap(mv[a], mv[b]), 0.0)''', '''  for a, b in (("motor bracket", "motor, board and plugs"), ("gear", "motor bracket"), ("gear", "motor, board and plugs"),
               ("spring's clamp", "motor, board and plugs"), ("lever", "motor bracket"), ("lever", "motor, board and plugs"),
               ("lever", "lever's pin")):
    res[f"{a}/{b} (both move)"] = (overlap(mv[a], mv[b]), 0.0)
  for deg in np.arange(0.0, S.LATCH_DEG + 0.01, 3.0):
    mv = A.movers(0.0, lever_deg=float(deg))
    for b in ("motor bracket", "motor, board and plugs"):
      key = f"lever/{b} (both move, the lever swung)"
      res[key] = (max(res.get(key, (0.0, None))[0], overlap(mv["lever"], mv[b])), float(deg))''')
sub('''  res["pulled out against the stop: other parts/mounting plate"] = (max(overlap(out[k], A.p["plate"]) for k in out if k != "motor bracket"), -S.STOP_GAP)''',
    '''  res["pulled out against the stop: other parts/mounting plate"] = (max(overlap(out[k], A.p["plate"]) for k in out
                                                                         if k not in ("motor bracket", "lever")), -S.STOP_GAP)
  res["pulled out against the stop: lever/mounting plate"] = (overlap(out["lever"], A.p["plate"]), -S.STOP_GAP)''')

# the latch check, after touching_at_stops
sub('''def mesh_sweep(A: SideAssembly, step: float = 0.5) -> dict:''', '''def lever_notches(A: SideAssembly, step: float = 3.0) -> dict:
  """The lever swinging into each notch: against every fixed part, at the two ends of the slide it can be at there
  (latched: from resting on the notch's floor to pulled out against the stop; parked: from resting on the notch's
  outer face to on the bumper). Then what the notches hold: latched and pushed in 0.3 mm, or parked and pulled out 0.3,
  the plate stops the lever (an overlap means it can't go there); swung fully out of the notch, it slides freely."""
  out = {"swinging into the notches (worst overlap, mm3)": 0.0}
  for s in (-S.STOP_GAP, 0.0, S.STROKE, S.STROKE + 0.2):
    fx = A.fixed(s)
    for deg in np.arange(0.0, S.LATCH_DEG + 0.01, step):
      lv = S.lever_at(A.p["lever"], s, float(deg))
      for name, part in fx.items():
        v = overlap(lv, part)
        if v > out["swinging into the notches (worst overlap, mm3)"]:
          out["swinging into the notches (worst overlap, mm3)"] = v
          out["... where"] = (name, s, float(deg))
  plate, lv = A.p["plate"], A.p["lever"]
  out["latched, pushed in 0.3 mm: the plate stops it (mm3 it would go into the plate)"] = round(
    overlap(S.lever_at(lv, 0.3, S.LATCH_DEG), plate), 2)
  out["parked, pulled out 0.3 mm: the plate stops it (mm3)"] = round(overlap(S.lever_at(lv, S.STROKE - 0.3, S.LATCH_DEG), plate), 2)
  out["swung out of the notch, it slides: worst overlap with the plate (mm3)"] = round(
    max(overlap(S.lever_at(lv, float(s)), plate) for s in np.arange(-S.STOP_GAP, S.STROKE + 0.21, 0.5)), 4)
  out["latched, resting on the notch's floor: gap (mm)"] = round(S.lever_at(lv, 0.0, S.LATCH_DEG).min_gap(plate, 2.0), 3)
  return out


def mesh_sweep(A: SideAssembly, step: float = 0.5) -> dict:''')

# forces: the lever instead of the plunger
a = s.index('''  pin = S.KIPP["push_N"]''')
b = s.index('''  return {
    "moving mass (kg, about)": round(m_moving, 3),''')
s = s[:a] + '''  rub = MG.RUB_DRY                                       # printed lever on the printed notch, dry
  net_in = spring - weight_out - rail_rub
  ext_in = S.CLAMP_Z - S.STROKE - S.SPOOL_Z
  ext_out = S.CLAMP_Z - S.SPOOL_Z
  # let go: the spring pulls it in, the lever riding along in its slot
  v_end = math.sqrt(max(0.0, 2 * net_in * S.STROKE / 1000.0 / m_moving))
  # swinging the lever out of its notch: the spring (less the weight) presses its arm on the notch's floor; the rub
  # there, at the middle of the plate's thickness, against the knob
  d_floor = math.hypot(PLATE_MID_X - S.PIVOT[0], 0.0)
  flick = rub * (spring - weight_out) * d_floor / S.KNOB_D
''' + s[b:]
sub('''  m_moving = 0.31 + 0.035 + 0.045 + 0.010 + 0.040        # motor, board and cover, bracket (PETG, about), gear, block (kg)''',
    '''  m_moving = 0.31 + 0.035 + 0.045 + 0.010 + 0.040 + 0.013  # motor, board and cover, bracket (PETG, about), gear, block, lever (kg)''')
sub('''    "your pull to bring it out: spring less weight plus drag (N)": round(spring - weight_out + rail_rub, 1),
    "... while the ramp pushes the pin back (N, most)": round(spring - weight_out + rail_rub + pin_ramp_push, 1),
    "the latch holds against (N)": round(spring - weight_out, 1),
    "plunger's pin pushes on the ear with (N), out / on the flat": (pin[0], round(pin_on_flat, 1)),''',
'''    "your pull on the lever to bring it out: spring less weight plus drag (N)": round(spring - weight_out + rail_rub, 1),
    "your push on the lever to slide it in, if the spring doesn't: weight plus drag (N)": round(weight_out + rail_rub, 1),
    "latched, the notch holds against (N)": round(spring - weight_out, 1),
    "swinging the lever out of its notch, at the knob (N, about)": round(flick, 1),''')
sub('''    "speed it hits the bumper at, the knob let go at once / held out (m/s, about)": (round(v_end, 2), round(v_end_knob, 2)),
    "... its energy then (J)": (round(0.5 * m_moving * v_end ** 2, 2), round(0.5 * m_moving * v_end_knob ** 2, 2)),''',
'''    "speed it hits the bumper at, let go (m/s, about)": round(v_end, 2),
    "... its energy then (J)": round(0.5 * m_moving * v_end ** 2, 2),''')
sub('''  for name in ("mounting plate", "plunger's knob", "spring's coil and spool"):
    P_ = A.W(A.fixed(0.0)[name])
    for cn, c in car:
      rows.append(("fixed", name, cn, gap(P_, c, 40.0)))''', '''  for s, deg, tag in ((0.0, S.LATCH_DEG, "latched"), (S.STROKE, 0.0, "slid in")):
    P_ = A.W(A.movers(s, lever_deg=deg)["lever"])
    for cn, c in car:
      rows.append((tag, "lever", cn, gap(P_, c, 40.0)))
  for name in ("mounting plate", "spring's coil and spool"):
    P_ = A.W(A.fixed(0.0)[name])
    for cn, c in car:
      rows.append(("fixed", name, cn, gap(P_, c, 40.0)))''')

# margins: the lever in place of the plunger
a = s.index('''  hold = S.CF["load_N"] - w_along                              # what the latch holds with the motor in, still''')
b = s.index('''  # slid in, a jolt can throw the motor out along the slide''')
s = s[:a] + '''  hold = S.CF["load_N"] - w_along                              # what the notch holds, latched, still
  worst_latch = hold + bump
  # the lever's arm, a beam from its hub: latched, the notch's floor holds it at the plate; pulled or pushed, the hand at
  # the knob. Printed flat, so the bending runs along its layers.
  sec = S.SHANK_W * (S.LEVER_Z[1] - S.LEVER_Z[0]) ** 2 / 6.0
  d_hub = S.HUB_R
  sig_latch = worst_latch * (PLATE_OUT_X_D - d_hub) / sec
  rows.append(MG.row(g, "The lever holds the motor in its notch", f"{sig_latch:.1f} MPa in the lever's arm at its hub: the "
                     f"spring less the motor's weight ({hold:.1f} N), plus the moving parts thrown along the slide by a hard "
                     f"bump ({MG.BUMP_G:g} times gravity: {bump:.0f} N), on the notch's floor",
                     f"{MG.PETG_TENSILE_XY / 3:.0f} MPa: a third of PETG's tensile strength along its layers, for repeated loads",
                     MG.PETG_TENSILE_XY / 3 / sig_latch, "PETG data sheet; calculated"))
  sig_use = S.LEVER_USE_N * (S.KNOB_D - d_hub) / sec
  rows.append(MG.row(g, "The lever takes your pull and push, every time", f"{sig_use:.1f} MPa in its arm at its hub: "
                     f"{S.LEVER_USE_N:.0f} N at the knob (it needs {hold + 0.5:.1f} N out, less than {w_along + 0.5:.1f} N in)",
                     f"{MG.PETG_TENSILE_XY / 3:.0f} MPa: a third of PETG's tensile strength along its layers",
                     MG.PETG_TENSILE_XY / 3 / sig_use, "PETG data sheet; calculated"))
  sig_yank = S.LEVER_YANK_N * (S.KNOB_D - d_hub) / sec
  rows.append(MG.row(g, "The lever takes a hard yank", f"{sig_yank:.1f} MPa in its arm at its hub: {S.LEVER_YANK_N:.0f} N "
                     "at the knob (an estimate on the high side)",
                     f"{MG.PETG_TENSILE_XY:.0f} MPa: PETG's tensile strength along its layers", MG.PETG_TENSILE_XY / sig_yank,
                     "PETG data sheet; calculated"))
''' + s[b:]
sub('''                     f"{f['speed it hits the bumper at, the knob let go at once / held out (m/s, about)'][1]} m/s",''',
    '''                     f"{f['speed it hits the bumper at, let go (m/s, about)']} m/s",''')
sub('''  e_in = f["... its energy then (J)"][1]''', '''  e_in = f["... its energy then (J)"]''')
# where the plate is, for the lever's sums
sub('''MESH_PHASE = PA.MESH_PHASE''', '''MESH_PHASE = PA.MESH_PHASE
PLATE_MID_X = (S.X_PL[0] + S.X_PL[1]) / 2               # the notch's floor holds the lever's arm across the plate's thickness
PLATE_OUT_X_D = S.PIVOT[0] - S.X_PL[0]                  # ... out to the plate's outer face, this far from the pin''')
open(p, "w").write(s)
EOF
/home/claude/bin/ruff check --isolated --select E4,E7,E9,F --line-length 140 sideassembly.py; grep -n "pin_back\|plunger\|KIPP\|BEVEL\|PIN_IN\|v_end_knob\|rub_work\|pin_on_flat" sideassembly.py