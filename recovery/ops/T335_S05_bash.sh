python3 - <<'EOF'
p = "platefit.py"
s = open(p, encoding="utf-8").read()
a = """  pw, ph = letter
  c = canvas.Canvas(path, pagesize=letter)"""
b = """  c = canvas.Canvas(path, pagesize=letter)"""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
ruff check platefit.py | tail -1; PYTHONPATH=/home/claude/pylib timeout 600 python3 -c "
import os, platefit as F, rightarm as RA
F.paper_template(os.path.join(RA.REPORT_DIR, 'frame-plate-fit-test-template.pdf'))
" && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/photos && pdftoppm -r 100 -png /home/claude/deliver/hardware/report/frame-plate-fit-test-template.pdf tmpl && ls tmpl*