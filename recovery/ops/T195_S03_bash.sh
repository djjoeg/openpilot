sed -i 's/      s = str(int(round(y)))/      s = str(round(y))/; s/  labels.append(text("WHEEL ^", SIDE_RAIL - 0.3, Y \/ 2 + 6.0, T, rot=90.0))/  labels.append(text("WHEEL ^", SIDE_RAIL, Y \/ 2 + 6.0, T, rot=90.0))/' slotplate.py && /home/claude/bin/ruff check --output-format concise --line-length 140 slotplate.py && PYTHONPATH=/home/claude/pylib timeout 900 python3 slotplate.py 2>&1 | tail -2 && PYTHONPATH=/home/claude/pylib timeout 600 python3 - <<'EOF'
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import slotplate as S, render as R
p = S.plate()
img = R.render([(p, (0.62, 0.74, 0.92))], R.view_matrix(-90, 89), size=(1200, 1400), margin=0.03)
plt.imsave('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slotplate_top.png', np.clip(img, 0, 1))
print("ok")
EOF