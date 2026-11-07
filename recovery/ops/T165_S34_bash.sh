python3 - <<'EOF'
p = "sidebuild.py"
s = open(p).read()
def sub(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:80], s.count(old))
    s = s.replace(old, new)

sub('''  ("KIPP K0338.11105 spring plunger: M10 x 1 thread, 5 mm pin, knob, no rest position, no lock nut", 1, "the latch"),
  ("M10 x 1 thin hex nut (DIN 439 or ISO 4035: 16 or 17 mm across flats, 5 mm thick)", 1, "holds the plunger in the plate"),
''', '''  ("4 mm x 24 mm steel dowel pin (ISO 8734), or 4 mm steel rod cut to 24 mm", 1,
   "the lever's pivot: tapped into the bracket's ear from its inner end, through the lever, into the blind hole"),
''')
sub('''          "knob_from_middle": round(math.hypot(PP.R_FACE_P + S.PIN_Z, S.X_COLLAR - 15.0)),
          "knob_forward": (fwd(S.PIN_Y - S.KIPP["knob_d"] / 2), fwd(S.PIN_Y + S.KIPP["knob_d"] / 2))}''',
'''          "knob_from_middle": round(math.hypot(PP.R_FACE_P + sum(S.LEVER_Z) / 2, S.PIVOT[0] - S.KNOB_D)),
          "knob_forward": (fwd(S.PIVOT[1] - S.KNOB_R), fwd(S.PIVOT[1] + S.KNOB_R)),
          "knob_forward_in_slot": (fwd(slot_y - S.KNOB_R), fwd(slot_y + S.KNOB_R))}''')
sub('''  b = parts["bracket"].bounding_box()
  p = parts["plate"].bounding_box()''', '''  b = parts["bracket"].bounding_box()
  p = parts["plate"].bounding_box()
  slot_y = S.PIVOT[1] + S.KNOB_D * math.sin(math.radians(S.SLOT_DEG))   # the knob's middle, the lever in its slot''')
sub('''    (f"The latch knob. It points towards 4 o'clock behind the steering wheel, about {e['knob_from_middle']} mm from the "
     f"middle of the steering wheel and {e['knob_forward'][0]} to {e['knob_forward'][1]} mm forward of the back of the round "
     "part. Can you reach it there with the steering wheel straight?"),''',
'''    (f"The lever's knob. Latched, it sits towards 4 o'clock behind the steering wheel, about {e['knob_from_middle']} mm from "
     f"the middle of the steering wheel and {e['knob_forward'][0]} to {e['knob_forward'][1]} mm forward of the back of the "
     "round part you hold. To let go you push it away from you, towards the dash; sliding in the slot it is "
     f"{e['knob_forward_in_slot'][0]} to {e['knob_forward_in_slot'][1]} mm forward. Can you reach it there with the steering "
     "wheel straight, and is pulling it towards you to latch and pushing it away to let go the way round you want?"),''')
sub('''    "side-mounting-plate-draft": (parts["plate"], (0, -90, 0), "on its outer face (the plunger's side down)",
                                  "none needed: only hole and slot tops overhang"),''',
'''    "side-mounting-plate-draft": (parts["plate"], (0, -90, 0), "on its outer face (the lever's knob side down)",
                                  "none needed: only hole and slot tops overhang"),
    "side-lever": (parts["lever"], (0, 0, 0), "flat, on its face towards the middle of the steering wheel", "none"),''')
sub('''  res["stops"] = SA.touching_at_stops(A)''', '''  res["stops"] = SA.touching_at_stops(A)
  res["lever"] = SA.lever_notches(A)''')
sub('''  if res["mesh"]["worst_overlap_mm3"] > 1e-3:''', '''  lv = res["lever"]
  if lv["swinging into the notches (worst overlap, mm3)"] > 1e-3:
    out.append(f"the lever touches {lv['... where']} swinging into a notch")
  if lv["latched, pushed in 0.3 mm: the plate stops it (mm3 it would go into the plate)"] < 1.0:
    out.append("latched, the notch doesn't hold the lever")
  if lv["parked, pulled out 0.3 mm: the plate stops it (mm3)"] < 1.0:
    out.append("parked, the notch doesn't hold the lever")
  if lv["swung into the slot, it slides: worst overlap with the plate (mm3)"] > 1e-3:
    out.append("the lever touches the plate sliding in its slot")
  if res["mesh"]["worst_overlap_mm3"] > 1e-3:''')
sub('''  L = ["SIDE-SLIDE MOUNT", "",
       "The motor sits at 5:20 behind the steering wheel, its shaft pointing out at the steering wheel and its gear on the",
       "teeth on the back of it. It slides along its own shaft, in towards the middle of the steering wheel, on a rail. A",
       "spring pulls it in; you pull it back out along the shaft until the latch clicks. Pull the latch's knob and the",
       f"spring pulls it {S.STROKE:.0f} mm in. The power switch is on only with the motor latched out on the teeth.", ""]''',
'''  L = ["SIDE-SLIDE MOUNT", "",
       "The motor sits at 5:20 behind the steering wheel, its shaft pointing out at the steering wheel and its gear on the",
       "teeth on the back of it. It slides along its own shaft, in towards the middle of the steering wheel, on a rail. A",
       "lever on the motor's bracket comes out through an L-shaped slot in the mounting plate. Pull the lever out along the",
       "slot (the motor slides out onto the teeth), then pull it towards you into the notch at the slot's end: latched.",
       f"Push it away from you, out of the notch, and the spring pulls the motor {S.STROKE:.0f} mm in; if the spring doesn't,",
       "push the lever in along the slot, and pull it into the notch at the inner end to park it. The power switch is on",
       "only with the motor all the way out on the teeth.", ""]''')
sub('''  L.append(f"  stops: pulled out, the latch's ear meets the stop {S.STOP_GAP} mm past the latch; slid in, the bracket meets the")''',
'''  lv = res["lever"]
  L.append(f"  the lever swings between its slot and either notch touching nothing (worst {round(lv['swinging into the notches (worst overlap, mm3)'], 4)} mm3)")
  L.append(f"  latched, the notch's floor stops it sliding in (pushed in 0.3 mm it would go {lv['latched, pushed in 0.3 mm: the plate stops it (mm3 it would go into the plate)']} mm3")
  L.append(f"  into the plate); parked, likewise it can't slide out ({lv['parked, pulled out 0.3 mm: the plate stops it (mm3)']} mm3); in its slot it slides touching nothing")
  L.append(f"  stops: pulled out, the ear meets the stop {S.STOP_GAP} mm past the latched place; slid in, the bracket meets the")''')
sub('''  L.append("  complete for trying the slide, the latch, the spring and the switch on the bench.")''',
    '''  L.append("  complete for trying the slide, the lever, the spring and the switch on the bench.")''')

# drawing: the lever in place of the plunger
sub('''       "plate": "#78a85a", "rail": "#9aa0a8", "block": "#6d7179", "plunger": "#d04a4a", "switch": "#333333", "spring": "#c8b040"}''',
    '''       "plate": "#78a85a", "rail": "#9aa0a8", "block": "#6d7179", "lever": "#d04a4a", "switch": "#333333", "spring": "#c8b040"}''')
sub('''  mv_in, mv_out, fx = A.movers(0.0), A.movers(S.STROKE), A.fixed(0.0)''',
    '''  mv_in, mv_out, fx = A.movers(0.0, lever_deg=0.0), A.movers(S.STROKE), A.fixed(0.0)''')
sub('''  for m, c in ((parts["plate"], C["plate"]), (parts["rail"], C["rail"]), (fx["plunger and nut"] + fx["plunger's knob"], C["plunger"]),
               (fx["switch"], C["switch"]), (fx["spring's coil and spool"], C["spring"])):''',
    '''  for m, c in ((parts["plate"], C["plate"]), (parts["rail"], C["rail"]), (fx["switch"], C["switch"]),
               (fx["spring's coil and spool"], C["spring"])):''')
sub('''    for name, c in (("block", C["block"]), ("motor bracket", C["bracket"]), ("motor, board and plugs", C["motor"]), ("gear", C["gear"])):
      draw(ax, mv[name], "top", c, ls=ls, alpha=0.95 if ls == "-" else 1.0, lw=1.0 if ls == "-" else 1.4, z=4 if ls == "-" else 5)''',
    '''    for name, c in (("block", C["block"]), ("motor bracket", C["bracket"]), ("motor, board and plugs", C["motor"]), ("gear", C["gear"]),
                    ("lever", C["lever"])):
      draw(ax, mv[name], "top", c, ls=ls, alpha=0.95 if ls == "-" else 1.0, lw=1.0 if ls == "-" else 1.4, z=4 if ls == "-" else 5)''')
sub('''  note("latch knob:\\npull it to let go", (F - 6, 70), (122, 86), color=C["plunger"])''',
    '''  note("lever: pull it out along the slot,\\nthen towards you into the notch", (F - 11, 76), (118, 88), color=C["lever"])''')
sub('''  handles = [Rectangle((0, 0), 1, 1, fc=C[k], alpha=0.9) for k in ("motor", "bracket", "gear", "teeth", "plate", "plunger", "spring")] + \\''',
    '''  handles = [Rectangle((0, 0), 1, 1, fc=C[k], alpha=0.9) for k in ("motor", "bracket", "gear", "teeth", "plate", "lever", "spring")] + \\''')
sub('''                       "latch", "spring", f"slid in {S.STROKE:.0f} mm"], loc="lower center", ncol=8, fontsize=9, frameon=False)''',
    '''                       "lever", "spring", f"slid in {S.STROKE:.0f} mm"], loc="lower center", ncol=8, fontsize=9, frameon=False)''')

# 3D pictures
sub('''       "plunger": (0.82, 0.28, 0.28), "switch": (0.15, 0.15, 0.15), "spring": (0.80, 0.72, 0.25)}''',
    '''       "lever": (0.82, 0.28, 0.28), "switch": (0.15, 0.15, 0.15), "spring": (0.80, 0.72, 0.25)}''')
sub('''  def scene(s):
    mv, fx, W = A.movers(s), A.fixed(s), A.W''', '''  def scene(s):
    mv, fx, W = A.movers(s, lever_deg=0.0 if s == 0.0 else S.SLOT_DEG), A.fixed(s), A.W''')
sub('''            (W(fx["plunger and nut"] + fx["plunger's knob"] + fx["plunger's pin"]), C["plunger"]),''',
    '''            (W(mv["lever"]), C["lever"]),''')
sub('''    "latch knob: pull to let go": (cpt(S.X_COLLAR - 30.0, S.PIN_Y, S.PIN_Z), (-170, -60)),''',
    '''    "lever: out along the slot, then towards you into the notch": (cpt(S.PIVOT[0] - S.KNOB_D, S.PIVOT[1], sum(S.LEVER_Z) / 2), (-170, -60)),''')
sub('''  for ax, s, title in ((axes[0], 0.0, "motor out on the teeth: the latch holds it"),
                       (axes[1], S.STROKE, f"latch let go: the spring has pulled it {S.STROKE:.0f} mm in")):''',
    '''  for ax, s, title in ((axes[0], 0.0, "motor out on the teeth: the lever latched in its notch"),
                       (axes[1], S.STROKE, f"lever out of its notch: the spring has pulled the motor {S.STROKE:.0f} mm in")):''')
open(p, "w").write(s)
EOF
grep -n "plunger\|KIPP\|PIN_Y\|X_COLLAR\|latch knob" sidebuild.py; /home/claude/bin/ruff check --isolated --select E4,E7,E9,F --line-length 140 sidebuild.py