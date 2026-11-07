cp sideassembly.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/sideassembly_pre_holds.py && python3 - <<'EOF'
import pathlib
p = pathlib.Path("sideassembly.py")
s = p.read_text()

def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:70])
    s = s.replace(old, new)

rep("  - the forces: spring, weight, the lever, switch\n",
    "  - the forces: spring, weight, the lever, switch; what keeps the lever in its notches against its own weight\n")
rep("""PLATE_OUT_X_D = S.PIVOT[0] - S.X_PL[0]                  # ... out to the plate's outer face, this far from the pin
""", """PLATE_OUT_X_D = S.PIVOT[0] - S.X_PL[0]                  # ... out to the plate's outer face, this far from the pin
# motor, board and cover, bracket (PETG, about), gear, block, lever (kg)
MOVING_KG = 0.31 + 0.035 + 0.045 + 0.010 + 0.040 + 0.013
RAIL_RUB = 0.5                                          # the block's own drag, about (preloaded MGN12: a few tenths of a N)
PETG_KG_PER_MM3 = 1.28e-6                               # Bambu Lab PETG HF data sheet (V1.0): 1.28 g/cm3
BRAKE_G = 0.8                                           # braking hard, in times gravity (an estimate on the high side)
""")
rep("""def build_parts() -> dict:""", '''def volume_centre(m: Manifold) -> tuple:
  """A solid's volume (mm3) and the middle of its volume (mm), from its surface's triangles."""
  mesh = m.to_mesh()
  v = np.asarray(mesh.vert_properties)[:, :3].astype(float)
  tri = np.asarray(mesh.tri_verts)
  a, b, c = v[tri[:, 0]], v[tri[:, 1]], v[tri[:, 2]]
  six = np.einsum("ij,ij->i", a, np.cross(b, c))        # six times each triangle's cone to the origin, signed
  return six.sum() / 6.0, (six[:, None] * (a + b + c)).sum(axis=0) / (4.0 * six.sum())


def lever_holds() -> dict:
  """The lever's own weight against what keeps it in a notch, each as a push at the knob (N): standing still, and
  braking hard. Gravity leans towards the dash here (the column slopes down towards it), so the lever's weight swings
  it towards its slot, out of a notch; braking leans it further. Latched, the spring's pull (less the motor's weight)
  presses the arm on the notch's floor; parked with no spring, the motor's weight presses it on the inner notch's side.
  A positive "own" swings it towards its slot."""
  import margins as MG
  a = math.radians(P.COLUMN_TILT)
  up_w = np.array([0.0, math.cos(a), math.sin(a)])       # steering wheel frame: z along the column towards the driver
  nose_w = np.array([0.0, math.sin(a), -math.cos(a)])    # level, towards the car's nose
  R = PP.rot_z(S.MOUNT_DEG) @ PP.R_POP                   # carrier frame -> steering wheel frame
  vol, cen = volume_centre(S.side_lever())
  m_lever = vol * PETG_KG_PER_MM3
  ax, ay = cen[0] - S.PIVOT[0], cen[1] - S.PIVOT[1]
  d_floor = abs(PLATE_MID_X - S.PIVOT[0])
  out = {"lever (g, solid)": round(m_lever * 1000.0, 1)}
  for name, brake in (("still", 0.0), ("braking", BRAKE_G)):
    g = 9.81 * (R.T @ (-up_w + brake * nose_w))         # what the parts feel, carrier frame (m/s2)
    turn = m_lever * (ax * g[1] - ay * g[0])             # N mm about the pin; below 0 it swings towards the slot
    weight_out = MOVING_KG * g[2]                         # the moving parts' weight along the slide, outwards (N)
    out[name] = {"own": -turn / S.KNOB_D,
                 "latched": MG.RUB_DRY * (S.CF["load_N"] - weight_out) * d_floor / S.KNOB_D,
                 "parked_no_spring": MG.RUB_DRY * max(0.0, weight_out - RAIL_RUB) * d_floor / S.KNOB_D}
  return out


def build_parts() -> dict:''')
rep("""  m_moving = 0.31 + 0.035 + 0.045 + 0.010 + 0.040 + 0.013  # motor, board and cover, bracket (PETG, about), gear, block, lever (kg)
""", """  m_moving = MOVING_KG
""")
rep("""  rail_rub = 0.5                                         # the block's own drag, about (preloaded MGN12: a few tenths of a N)
""", """  rail_rub = RAIL_RUB
""")
rep("""  flick = rub * (spring - weight_out) * d_floor / S.KNOB_D
""", """  flick = rub * (spring - weight_out) * d_floor / S.KNOB_D
  holds = lever_holds()["still"]
""")
rep("""    "swinging the lever out of its notch, at the knob (N, about)": round(flick, 1),
""", """    "swinging the lever out of its notch, at the knob (N, about)": round(flick, 1),
    "the lever's own weight swings it towards its slot, at the knob (N, about)": round(holds["own"], 2),
    "latched, a jolt along the slide lifts the lever off the notch's floor from (g, on top of gravity)":
      round((spring - weight_out) / (m_moving * 9.81 * -up), 2),
    "parked with no spring: the motor's weight holds the lever in the inner notch; swinging it out (N at the knob, about)":
      round(holds["parked_no_spring"], 2),
""")
rep("""  # slid in, a jolt can throw the motor out along the slide: the spring holds it up to this many times gravity (not a
""", """  # the lever stays in its notch: its own weight swings it towards its slot (gravity leans towards the dash here),
  # against the notch's grip; braking hard makes that worse
  h = lever_holds()["braking"]
  lift_g = hold / w_along
  for what, grip, by, note in (
      ("The lever stays latched in its notch", h["latched"],
       "the notch's grip: the spring's pull less the motor's weight presses the arm on the notch's floor",
       f"a jolt over {lift_g:.1f} times gravity along the slide lifts the arm off the floor for a moment; if the lever ever "
       "works its way out, the spring pulls the motor in and the power goes off"),
      ("Parked with no spring, the lever stays in the inner notch", h["parked_no_spring"],
       "the notch's grip: the motor's weight presses the arm on the inner notch's side",
       "with the spring working nothing holds the lever there and its weight swings it back into the slot: no harm, the "
       "spring holds the motor in")):
    rows.append(MG.row(g, what, f"{h['own']:.2f} N at the knob: the lever's own weight swinging it towards its slot, "
                       f"braking hard ({BRAKE_G:g} times gravity)",
                       f"{grip:.2f} N at the knob: {by}, rubbing {MG.RUB_DRY:g} (an estimate)",
                       grip / h["own"] if h["own"] > 0 else float("inf"), "calculated; the rubbing is an estimate", note=note))
  # slid in, a jolt can throw the motor out along the slide: the spring holds it up to this many times gravity (not a
""")
p.write_text(s)
print("ok")
EOF
grep -n "def row" -A 12 margins.py | head -20