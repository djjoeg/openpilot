python3 - <<'EOF'
r=open('render.py').read()
r=r.replace('''  imgs = [render(parts, rot, size=size) for parts, rot in panels]
  fig, axes = plt.subplots(1, len(imgs), figsize=(len(imgs) * size[0] / 150, size[1] / 150 + (0.5 if suptitle else 0.2)), dpi=150)''',
'''  imgs = [render(parts, rot, size=size) for parts, rot in panels]
  if suptitle:
    import textwrap
    width = max(60, int(len(imgs) * size[0] / 12))      # about the characters that fit one line at this width
    suptitle = textwrap.fill(suptitle, width)
  lines = suptitle.count("\\n") + 1 if suptitle else 0
  fig, axes = plt.subplots(1, len(imgs), figsize=(len(imgs) * size[0] / 150, size[1] / 150 + (0.3 + 0.2 * lines if suptitle else 0.2)), dpi=150)''')
open('render.py','w').write(r)
EOF
ruff check --select E,F,W --line-length 140 render.py | tail -1