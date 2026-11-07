cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap && cat > core.py <<'EOF'
"""The carrier without the springs' bar, the old webs and the switch lobe: what any new snap must work around."""
import math
import numpy as np
from manifold3d import CrossSection, Manifold
import faceparts as FP
import mountparts as MP
import popparts as PP
from cadlib import box, clean, cyl, cyl_x, extrude_x, prism_x, sector, union
from params import M3_CLEAR, MOTOR_PLATE_T, NEMA, NEMA_BOSS, NEMA_HOLES, NEMA_LEN


def core_carrier(with_knuckle=True) -> Manifold:
  t = MOTOR_PLATE_T
  outline = CrossSection.square((2 * MP.PLATE_HALF, 2 * MP.PLATE_HALF), center=True) + CrossSection.circle(MP.GUARD_OUT, 180)
  outline = outline ^ CrossSection.square((200, 200)).translate((-100, MP.PLATE_BOTTOM))
  plate = outline.extrude(t)
  shell = cyl(MP.GUARD_OUT, t, MP.GUARD_FRONT, segments=180) - cyl(MP.GUARD_IN, t - 1, MP.GUARD_FRONT + 1, segments=180)
  lip = cyl(MP.GUARD_OUT, MP.GUARD_FRONT - 1.6, MP.GUARD_FRONT, segments=180) - \
    cyl(MP.GUARD_LIP_IN, MP.GUARD_FRONT - 3, MP.GUARD_FRONT + 1, segments=180)
  gw = FP.GUARD_WINDOW_F
  window = sector(MP.GUARD_OUT + 6, 270.0 - gw, 270.0 + gw).extrude(MP.GUARD_FRONT + 4).translate((0, 0, t - 2))
  guard = (shell + lip) - window
  top = box(-PP.SIDE_X[1], PP.SIDE_X[1], PP.TOP_Y[0], PP.TOP_Y[1], PP.TOP_BACK, t)
  walls = union([box(PP.SIDE_X[0], PP.SIDE_X[1], 0.0, PP.TOP_Y[1], PP.TOP_BACK, t),
                 box(-PP.SIDE_X[1], -PP.SIDE_X[0], 0.0, PP.TOP_Y[1], PP.TOP_BACK, t)])
  hy, hz = PP.HINGE_P
  parts = [plate, guard, top, walls]
  if with_knuckle:
    parts.append(cyl_x(PP.KNUCKLE_R, -PP.KNUCKLE_X, PP.KNUCKLE_X, y=hy, z=hz))
  part = union(parts)
  part = part - box(PP.PLUG_SLOT[0], PP.PLUG_SLOT[1], NEMA / 2 - 1.0, PP.TOP_Y[1] + 1.0, PP.PLUG_SLOT[2], PP.PLUG_SLOT[3])
  part = part - cyl(NEMA_BOSS / 2 + 0.4, -3, t + 1, segments=128)
  part = part - box(-NEMA / 2 - 0.5, NEMA / 2 + 0.5, -NEMA / 2 - 0.5, NEMA / 2 + 0.5, -NEMA_LEN - 20, 0.0)
  return clean(part)
EOF
sed -i 's/^carrier_c = parts\["carrier"\] + parts\["motor"\] + parts\["gear"\]/from core import core_carrier\ncarrier_c = core_carrier() + parts["motor"] + parts["gear"]/' layout.py
sed -i 's/^  "plate (as at 3:20)": W2C(A.plate()),/  "plate (as at 3:20)": W2C(box(12.0, 70.0, -66.0, -58.0, -208.0, -92.0)),/' layout.py
sed -i 's/ax.set_xlim(-20, 170); ax.set_ylim(-110, 40)/ax.set_xlim(-10, 160); ax.set_ylim(-100, 20)/' layout.py
PYTHONPATH=/home/claude/pylib timeout 900 python3 layout.py -63 -18,-10,-2,6,14,22