python3 - <<'EOF'
r=open('render.py').read()
r=r.replace('''  fig, axes = plt.subplots(1, len(imgs), figsize=(len(imgs) * size[0] / 150, size[1] / 150 + (0.3 + 0.2 * lines if suptitle else 0.2)), dpi=150)''',
'''  height = size[1] / 150 + (0.3 + 0.2 * lines if suptitle else 0.2)
  fig, axes = plt.subplots(1, len(imgs), figsize=(len(imgs) * size[0] / 150, height), dpi=150)''')
open('render.py','w').write(r)
EOF
ruff check --select E,F,W --line-length 140 render.py | tail -1