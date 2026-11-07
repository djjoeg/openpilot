python3 - <<'EOF'
import pathlib
p = pathlib.Path("sideparts.py")
s = p.read_text()
old = """FOOT_X = (46.0, 95.0)             # ... across: its left end clear of the cover on the back of the steering wheel, its
                                  # right end clear of the lever's knob"""
new = """FOOT_X = (46.0, 92.0)             # ... across: its left end clear of the cover on the back of the steering wheel, its
                                  # right end flush with the plate's outer face (so the plate prints on that face)"""
assert s.count(old) == 1
p.write_text(s.replace(old, new))
EOF
PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import numpy as np, math
import sideparts as S, sidebuild as B
from cadlib import on_bed
pl = S.side_plate()
m = on_bed(pl, (0, -90, 0))
print("bbox", np.round(m.bounding_box(),1), "pieces", len(pl.decompose()), "overhang", round(B.support_area(m)))
fb = S.to_wheel(S.foot_block()); print("foot wheel bbox", np.round(fb.bounding_box(),1).tolist())
EOF