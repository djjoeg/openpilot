python3 - <<'EOF'
p='frameplate.py'; s=open(p).read()
s=s.replace('''      oblong(xc, (y0 + y1) / 2, y1 - y0, SLOT_W, "y", fc="white", ec="#444", lw=1)
  # the car''','''      oblong(xc, (y0 + y1) / 2, y1 - y0, SLOT_W, "y", fc="white", ec="#444", lw=1)
  for k, xc in enumerate(STRIP_COLS, start=1):
    ax.text(xc, STRIP[3] - 3, str(k), ha="center", va="top", fontsize=7, color="#222")
  # the car''')
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 frameplate.py >/dev/null && (ruff check frameplate.py 2>/dev/null || python3 -m ruff check frameplate.py 2>/dev/null || echo "ruff not available") | tail -3