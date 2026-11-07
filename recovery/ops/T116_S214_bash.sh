python3 - <<'EOF'
p='render.py'
s=open(p).read()
old='''def save(path, panels, titles=None, suptitle=None, size=(900, 700)):
  """panels: list of (parts, rot). Saves them side by side."""
  imgs = [render(parts, rot, size=size) for parts, rot in panels]
  if suptitle:
    import textwrap
    width = max(60, int(len(imgs) * size[0] / 12))      # about the characters that fit one line at this width
    suptitle = textwrap.fill(suptitle, width)
  lines = suptitle.count("\\n") + 1 if suptitle else 0
  height = size[1] / 150 + (0.3 + 0.2 * lines if suptitle else 0.2)
  fig, axes = plt.subplots(1, len(imgs), figsize=(len(imgs) * size[0] / 150, height), dpi=150)
  axes = np.atleast_1d(axes)
  for i, (ax, im) in enumerate(zip(axes, imgs)):
    ax.imshow(im)
    ax.set_axis_off()
    if titles:
      ax.set_title(titles[i], fontsize=9)
'''
new='''def save(path, panels, titles=None, suptitle=None, size=(900, 700), cols=None):
  """panels: list of (parts, rot). Saves them side by side, or in rows of cols."""
  imgs = [render(parts, rot, size=size) for parts, rot in panels]
  ncol = len(imgs) if not cols else min(cols, len(imgs))
  nrow = -(-len(imgs) // ncol)
  if suptitle:
    import textwrap
    width = max(60, int(ncol * size[0] / 12))      # about the characters that fit one line at this width
    suptitle = textwrap.fill(suptitle, width)
  lines = suptitle.count("\\n") + 1 if suptitle else 0
  height = nrow * size[1] / 150 + (0.3 + 0.2 * lines if suptitle else 0.2)
  fig, axes = plt.subplots(nrow, ncol, figsize=(ncol * size[0] / 150, height), dpi=150)
  axes = np.atleast_1d(axes).ravel()
  for ax in axes[len(imgs):]:
    ax.set_axis_off()
  for i, (ax, im) in enumerate(zip(axes, imgs)):
    ax.imshow(im)
    ax.set_axis_off()
    if titles:
      ax.set_title(titles[i], fontsize=9)
'''
assert s.count(old)==1, s.count(old)
s=s.replace(old,new)
open(p,'w').write(s)

p='accord_lka_parts.py'
s=open(p).read()
old_parts='''  front_down = "front face (the side towards you) down"
  bparts = {
    "back-teeth-upper": (pieces["upper"], (180, 0, 0), front_down, "none"),'''
assert s.count(old_parts)==1
# find the bparts block in back_mount and move it into back_part_list
i0 = s.index(old_parts)
i1 = s.index('''    bparts[f"back-arm-{int(L):03d}"] = (FP.face_arm(L), (90, 0, 0), "flat", "none")\n''', i0)
i1 = i1 + len('''    bparts[f"back-arm-{int(L):03d}"] = (FP.face_arm(L), (90, 0, 0), "flat", "none")\n''')
block = s[i0:i1]
s = s[:i0] + "  bparts = back_part_list(t, pieces, tests)\n" + s[i1:]
# the new function, before back_mount
func = '''def back_part_list(t, pieces: dict, tests: dict) -> dict:
  """The back-teeth mount's printed parts: name -> (part, how it turns onto the bed, how it prints, supports)."""
  import faceparts as FP        # noqa: E402
''' + block + '''  return bparts


'''
j = s.index("def back_mount(")
s = s[:j] + func + s[j:]
# the parts picture on its own
old_pic='''  view = R.look((0.8, -1.0, 0.7), (0, 0, 1))
  panels, titles = [], []
  for n, (m, rot, how, sup) in bparts.items():
    if n.startswith("back-arm-") and not n.endswith("165"):
      continue
    panels.append(([(on_bed(m, rot), (.55, .7, .9))], view))
    titles.append(n)
  R.save(os.path.join(folder, "back-parts.png"), panels, titles, size=(560, 500))
'''
new_pic='''  back_parts_picture(bparts, folder, on_bed)


def back_parts_picture(bparts: dict, folder: str, on_bed):
  """The back-teeth mount's parts as they sit on the bed (one arm of the three), four to a row."""
  import render as R
  view = R.look((0.8, -1.0, 0.7), (0, 0, 1))
  panels, titles = [], []
  for n, (m, rot, _how, _sup) in bparts.items():
    if n.startswith("back-arm-") and not n.endswith("165"):
      continue
    panels.append(([(on_bed(m, rot), (.55, .7, .9))], view))
    titles.append(n)
  R.save(os.path.join(folder, "back-parts.png"), panels, titles, size=(560, 500), cols=4)
'''
assert s.count(old_pic)==1
s=s.replace(old_pic,new_pic)
open(p,'w').write(s)
EOF
grep -n "def back_part_list" -A8 accord_lka_parts.py | head -12; grep -n "bparts = back_part_list" accord_lka_parts.py; /home/claude/bin/ruff check --isolated --select E,F --line-length 140 --output-format concise . ; echo "exit $?"