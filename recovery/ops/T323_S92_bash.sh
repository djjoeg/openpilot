cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = "stiffness.py"
s = open(p, encoding="utf-8").read()
reps = [
("""WASHER_R = 9.0             # the plate held this far round each cover screw (its washer)""",
 """WASHER_R = 12.5            # the plate held this far round each cover screw: a fender washer, 25 mm across (v6;
                           # v5's model had 18 mm washers: at the slides' far ends that gave 1.51 mm out, at the mark)"""),
("""  plate     the frame plate added, the arm's bar bonded into its receiver (the wing bolt pulls it tight against the
            wall), the plate held only round its two screws (9 mm washers): softer than the car, which also has the
            column cover under the plate.""",
 """  plate     the frame plate added, the arm's bar bonded into its receiver (the wing bolt pulls it tight against the
            wall), the plate held only under the fender washers on its two screws (25 mm across): softer than the
            car, which also has the column cover under the plate."""),
]
for a, b in reps:
  assert s.count(a) == 1, a[:60]
  s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
grep -n "9 mm\|washers" stiffness.py | head; cd /home/claude/deliver/hardware/cad && ruff check stiffness.py | tail -1