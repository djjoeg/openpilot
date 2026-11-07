python3 - <<'EOF'
import pathlib
p = pathlib.Path("sideparts.py")
s = p.read_text()
old = """  text = str(round(t.teeth_half))
  cuts = []
  a = MARK_DEG0
  for ch in text:
    px = DIGITS[ch]
    for row in range(5):
      for col in range(3):
        if px[row * 3 + col] == "1":
          a0 = a + col * math.degrees(MARK_PX / t.w_out)
          a1 = a0 + math.degrees(MARK_PX / t.w_out)
          z1 = MARK_Z0 + (5 - row) * MARK_PX
          cuts.append(FP.polar_box(t.w_out - MARK_DEPTH, t.w_out + 1.0, a0, a1, z1 - MARK_PX, z1, step_deg=0.3))
    a += 4 * math.degrees(MARK_PX / t.w_out)
  return union(cuts)"""
new = """  text = str(round(t.teeth_half))
  w = math.degrees(MARK_PX / t.w_out)
  cuts = []
  a = MARK_DEG0 + (4 * len(text) - 1) * w        # seen from outside, 4 o'clock is to the left: the text runs down in angle
  for ch in text:
    px = DIGITS[ch]
    for row in range(5):
      for col in range(3):
        if px[row * 3 + col] == "1":
          a1 = a - col * w
          z1 = MARK_Z0 + (5 - row) * MARK_PX
          cuts.append(FP.polar_box(t.w_out - MARK_DEPTH, t.w_out + 1.0, a1 - w, a1, z1 - MARK_PX, z1, step_deg=0.3))
    a -= 4 * w
  return union(cuts)"""
assert s.count(old) == 1
p.write_text(s.replace(old, new))
print("ok")
EOF
PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import numpy as np, math
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import sideparts as S
t = S.SideTeeth(n_teeth=18)
m = S.number_mark(t)
mesh = m.to_mesh(); v = np.asarray(mesh.vert_properties)[:, :3]
ang = np.degrees(np.arctan2(v[:,1], v[:,0]))
# view from outside: angle increasing to the LEFT
fig, ax = plt.subplots(figsize=(4,2)); ax.scatter(-ang, v[:,2], s=4); ax.set_aspect("equal"); ax.set_title("20: from outside (x = -angle)")
plt.savefig("/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/mark20.png", dpi=90)
EOF