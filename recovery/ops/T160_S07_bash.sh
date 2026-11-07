cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side && python3 - <<'EOF'
import pathlib
p = pathlib.Path("layout.py")
s = p.read_text()
reps = [
('ax.text(t.w_out + 2, 52, "teeth piece (on the\\ngrip\'s back, facing you)", fontsize=9, color="#555", ha="left")',
 'ax.text(218, 54, "teeth piece on the\\nback of the grip", fontsize=9, color="#444", ha="left", va="top")'),
('ax.text(R_IN - 2, 28, "inside edge of the grip", ha="right", fontsize=9)',
 'ax.text(R_IN - 2, 31, "inside edge of the grip", ha="left", fontsize=9)'),
('ax.text(212, 28, "towards you (front of the wheel)", ha="left", fontsize=9, color="#555")',
 'ax.text(218, 31, "towards you\\n(front of the wheel)", ha="left", fontsize=9, color="#555", va="center")'),
('ax.text(R_MID, -128, "forward (towards the nose)", ha="center", fontsize=9, color="#555")',
 'ax.text(218, -127, "forward (towards the nose)", ha="left", fontsize=9, color="#555")'),
('ax.text(213, -110, f"the motor sits', 'ax.text(218, -98, f"the motor sits'),
]
for a, b in reps:
  assert s.count(a) == 1, a[:70]
  s = s.replace(a, b)
p.write_text(s)
EOF
export PYTHONPATH=/home/claude/pylib && python3 layout.py