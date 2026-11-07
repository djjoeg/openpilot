python3 - <<'EOF'
p = 'render.py'
s = open(p, encoding='utf-8').read()
a = """  if suptitle:
    fig.suptitle(suptitle, fontsize=11)
  fig.tight_layout()"""
b = """  if suptitle:
    fig.suptitle(suptitle, fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 1 - (0.12 + 0.2 * lines) / height))   # the panels' titles clear of the suptitle
  else:
    fig.tight_layout()"""
assert s.count(a) == 1
open(p, 'w', encoding='utf-8').write(s.replace(a, b))
print('ok')
EOF
(time PYTHONPATH=/home/claude/pylib python3 visuals.py) 2>&1 | tail -5