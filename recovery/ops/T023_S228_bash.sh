python3 - << 'EOF'
p = "mountparts.py"
s = open(p).read()
start = s.index("# Lever angles (degrees up from down) for the lift the cam is shaped to give")
end = s.index("REST_D = ")
s = s[:start] + '''# Lever angles (degrees up from down). The cam lifts the carrier to the most at A_DEAD; the handle goes on past it to
# the stop bar at A_HARD_STOP, so the spring's push holds the lever against the bar ('over centre').
A_DEAD, A_HARD_STOP, A_END = 55.0, 63.0, 70.0
A_OFF = A_HARD_STOP
CAM_BEND = 4.0          # mm per radian squared: how sharply the fin's travel turns over at A_DEAD (the cam has to stay
                        # rounded where it touches the fin's flat top, which limits this to about half the cam radius)
''' + s[end:]

start = s.index("def _trapezoid(")
end = s.index("def fin_plane(")
s = s[:start] + '''def fin_travel(alpha: float) -> float:
  """How far (mm) the cam has pushed the fin down from where the fin meets the cam with the carrier fully dropped,
  at lever angle alpha (degrees up from down)."""
  rise = TAIL_ARM * (math.sin(math.radians(LIFT_DEG)) + math.sin(math.radians(DROP_DEG)))
  peak = rise + CAM_BEND * math.radians(A_HARD_STOP - A_DEAD) ** 2
  return max(0.0, peak - CAM_BEND * math.radians(alpha - A_DEAD) ** 2)


def lift_schedule(alpha: float) -> float:
  """Carrier lift (degrees) the cam is shaped for at lever angle alpha: the fin's travel turns into carrier angle."""
  return math.degrees(math.asin(fin_travel(alpha) / TAIL_ARM - math.sin(math.radians(DROP_DEG))))


''' + s[end:]
open(p, "w").write(s)
EOF
grep -n "A_START\|A_PEAK\|A_HUMP2\|A_STOP\b\|HUMP_DEG\|_trapezoid\|_blend" mountparts.py assembly.py