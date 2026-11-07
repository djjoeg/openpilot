python3 - <<'EOF'
p='margins.py'
s=open(p).read()
old_start = s.index("  # the column plate on the cover's screws: the push at the teeth reaches the plate's joint as a turning force about it")
old_end = s.index("  sideways = ft_most\n", old_start)
new_block = '''  # the column plate on the cover's screws: the loads at the teeth try to tip the plate off the cover about an edge of its
  # rubber strips; the screws in its slots hold it, each in proportion to its distance from that edge
  spring_dash = force * MP.SPRING_ARM / ((FP.FG_ROLLER[0] + FP.FG_ROLLER[1]) / 2 - MP.HINGE[1])
  up = spring_dash + ft_most * math.tan(phi + math.atan(RUB_DRY))
  down = MOUNTED_KG * 9.81 * BUMP_G
  layouts = {name: plate_screw_pull(t, ft_most, up, spring_dash, down, scr) for name, scr in PLATE_SCREW_LAYOUTS.items()}
  expected = next(iter(PLATE_SCREW_LAYOUTS))
  pull = layouts[expected]
  others = "; ".join(f"{name}: {PLATE_SCREW_HOLD_N / v:.2f}" for name, v in list(layouts.items())[1:])
  rows.append(row(g, "The column plate holds on the cover's screws", f"about {pull:.0f} N pulling on the busier screw: the "
                  f"motor's most push ({ft_most:.0f} N, up or down) and {up:.0f} N towards the dash at the teeth, tipping the plate "
                  f"about an edge of its rubber strips; two screws {expected}",
                  f"about {PLATE_SCREW_HOLD_N:.0f} N each: the cover's screws, estimated on the low side", PLATE_SCREW_HOLD_N / pull,
                  "estimated; where the screws are is a guess from the photos",
                  check="proof pulls with a luggage scale at the motor, lever up (see the guide): nothing may move",
                  note=f"other places the screws may fall: {others}. The lower cover is a plastic shell of unknown stiffness"))
'''
s = s[:old_start] + new_block + s[old_end:]
# the later duplicate definitions of up/down (still used by the proof test row) are now above; drop them there
old2 = '''  sideways = ft_most
  up = (force * MP.SPRING_ARM / ((FP.FG_ROLLER[0] + FP.FG_ROLLER[1]) / 2 - MP.HINGE[1])) + ft_most * math.tan(phi + math.atan(RUB_DRY))
  down = MOUNTED_KG * 9.81 * BUMP_G
'''
assert s.count(old2) == 1
s = s.replace(old2, "  sideways = ft_most\n")
# helper and layouts, after PLATE_SCREW_HOLD_N
i = s.index("PLATE_SCREW_HOLD_N = 250.0")
j = s.index("\n\n", i)
helper = '''
# where the lower cover's screws may fall in the column plate's two slots (slot, mm behind the plate's front end); the first
# is the one the photos suggest: the cover's screws on its right-hand side, one towards the wheel and one further back
PLATE_SCREW_LAYOUTS = {
  "in the outer slot, 80 mm apart": ((1, 40.0), (1, 120.0)),
  "one in each slot, 40 mm apart": ((0, 29.0), (1, 69.0)),
  "both in the outer slot, 40 mm apart": ((1, 29.0), (1, 69.0)),
  "both in the inner slot (nearer the middle)": ((0, 40.0), (0, 120.0)),
}


def plate_screw_pull(t, push_n: float, dash_n: float, spring_dash_n: float, weight_n: float, screws) -> float:
  """The most pull on one of the column plate's screws (N). The plate sits under the cover on two rubber strips; a load
  that tips it about an edge of the strips (along or across the column) is held by the screws, each pulling in
  proportion to its distance from that edge; the tipping about both kinds of edge is added. Loads: the push at the teeth
  up or down with the teeth pushing the gear towards the dash, and the parts' weight on a bump with the spring's push."""
  import faceparts as FP
  y_top = FP.plate_top_y()
  front = P.PLATE_FRONT_Z
  x0, x1 = FP.PL_X
  at_teeth = np.array([FP.R_F, 0.0, t.z_p])
  at_motor = np.array([FP.R_FACE + 20.0, 0.0, t.z_axis])
  cases = [[(at_teeth, np.array([0.0, push_n, -dash_n]))], [(at_teeth, np.array([0.0, -push_n, -dash_n]))],
           [(at_motor, np.array([0.0, -weight_n, 0.0])), (at_teeth, np.array([0.0, 0.0, -spring_dash_n]))]]
  middle = np.array([(x0 + x1) / 2, y_top, front - FP.PL_LEN / 2])
  edges = [(np.array([x0 + 1.0, y_top, 0.0]), np.array([0.0, 0.0, 1.0])), (np.array([x1 - 1.0, y_top, 0.0]), np.array([0.0, 0.0, 1.0])),
           (np.array([0.0, y_top, front - 2.0]), np.array([1.0, 0.0, 0.0])),
           (np.array([0.0, y_top, front - FP.PL_LEN + 2.0]), np.array([1.0, 0.0, 0.0]))]
  pts = [np.array([FP.PL_SLOTS_X[k], y_top, front - dz]) for k, dz in screws]
  worst = 0.0
  for loads in cases:
    pull = np.zeros(len(pts))
    for a, u in edges:
      if np.dot(np.cross(u, middle - a), np.array([0.0, -1.0, 0.0])) < 0:
        u = -u                                  # turning this way takes the plate's middle away from the cover
      m = sum(float(np.dot(np.cross(p - a, f), u)) for p, f in loads)
      if m <= 0:
        continue
      d = np.array([np.linalg.norm(np.cross(u, q - a)) for q in pts])
      pull += m * d / float(np.sum(d ** 2))
    worst = max(worst, float(pull.max()))
  return worst
'''
s = s[:j] + "\n" + helper + s[j:]
open(p, 'w').write(s)
EOF
sed -n 315,330p margins.py; /home/claude/bin/ruff check --isolated --select E,F --line-length 140 --output-format concise . ; echo "exit $?"