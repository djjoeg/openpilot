python3 - <<'EOF'
p = "platefit.py"
s = open(p, encoding="utf-8").read()
reps = [
('''  ax.text(xc - 9, SLOT_Y1_V4, "v4's slot ended here", ha="right", va="center", fontsize=7, color="#c0392b")''',
 '''  ax.text(LEG[0] - 2.0, SLOT_Y1_V4, "< v4's slot ended here", ha="left", va="center", fontsize=7, color="#c0392b")'''),
('''  ax.text(57, (BAR[3] + BAR_V4[3]) / 2, "cross bar 51 mm\\n(2 in) further back", ha="right", va="center", fontsize=8,''',
 '''  ax.text(63, (BAR[3] + BAR_V4[3]) / 2, "cross bar 51 mm\\n(2 in) further back", ha="right", va="center", fontsize=8,'''),
]
for a, b in reps:
  assert s.count(a) == 1, a[:50]
  s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
ruff check platefit.py | tail -1 && PYTHONPATH=/home/claude/pylib timeout 600 python3 platefit.py | tail -1