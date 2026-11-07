cd /home/claude/deliver && python3 - <<'EOF'
p = "README.md"
s = open(p, encoding="utf-8").read()
reps = [
("""1. **Fit the plate** on the cover's two screws (the cup slot on the key side, slot 1 on the other), with washers.""",
 """1. **Fit the plate** on the cover's two screws (the cup slot on the key side, slot 1 on the other), a fender washer
   under each: the bigger washers hold the plate stiffer."""),
("""Nothing new for the fit print (3 Nov: the arm v6 and the frame plate v5): each of its two slides takes one of the M5
wing bolts, one of the M5 nuts and one of your fender washers (3/4 to 1 in across).""",
 """Nothing new for the fit print (3 Nov: the arm v6 and the frame plate v5): each of its two slides takes one of the M5
wing bolts, one of the M5 nuts and one of your fender washers (3/4 to 1 in across), and the two cover screws take a
fender washer each: four fender washers in all."""),
]
for a, b in reps:
  assert s.count(a) == 1, a[:60]
  s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)

p = "hardware/cad/viewer3d.py"
s = open(p, encoding="utf-8").read()
a = """  ("Fit the frame plate on the column cover's two screws, with washers: the cup slot on the key side, slot 1 on the "
   "other. Its flat side goes up against the cover; the square tube hangs underneath, the printed labels facing down."),"""
b = """  ("Fit the frame plate on the column cover's two screws, a fender washer under each: the cup slot on the key side, "
   "slot 1 on the other. Its flat side goes up against the cover; the square tube hangs underneath, the labels facing "
   "down."),"""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
grep -n "fender" README.md | head