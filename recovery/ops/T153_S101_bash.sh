python3 - <<'EOF'
p='slideparts.py'
s=open(p).read()
start=s.index('def slide_carrier() -> Manifold:')
end=s.index('# ***** the block *****')
new='''def slide_carrier() -> Manifold:
  wall = box(WALL_X[0], WALL_X[1], WALL_Y[0], WALL_Y[1], WALL_Z[0], WALL_Z[1])
  socks = union([cyl_y(ROD_D / 2 + 4.5, WALL_Y[0], WALL_Y[1], x=x, z=z, segments=48) for x, z in RODS])
  boss = cyl_x(7.0, PIVOT_BOSS_X[0], WALL_X[0] + 0.5, y=PIVOT[0], z=PIVOT[1], segments=48)
  tongue = box(TONGUE_X[0], TONGUE_X[1], WALL_Y[1] - 0.5, TONGUE_Y1, TONGUE_Z[0], TONGUE_Z[1])
  land = box(TONGUE_X[1] - 0.5, TONGUE_X[1] + LAND_H, LAND_FROM + LAND_H, TONGUE_Y1, TONGUE_Z[0], TONGUE_Z[1])
  ramp = Manifold.batch_hull([box(TONGUE_X[1] - 0.5, TONGUE_X[1] + 0.01, LAND_FROM, LAND_FROM + 0.01, TONGUE_Z[0], TONGUE_Z[1]),
                              box(TONGUE_X[1] - 0.5, TONGUE_X[1] + LAND_H, LAND_FROM + LAND_H, LAND_FROM + LAND_H + 0.01,
                                  TONGUE_Z[0], TONGUE_Z[1])])
  part = union([_motor_plate(), wall, socks, boss, tongue, land, ramp])
  part = part - _plate_holes()
  part = part - box(-H - 0.3, H + 0.3, -H - 0.3, H + 0.3, -NEMA_LEN - 20, 0.0)
  for x, z in RODS:
    part = part - cyl_y(ROD_HOLE / 2, WALL_Y[0] - 1.0, WALL_Y[1] + 1.0, x=x, z=z, segments=48)
    # an M3 x 6 grub screw into each rod, cut into the plastic from outside (top for the upper rod, bottom the lower)
    if z > 0:
      part = part - cyl(M3_PILOT / 2, z, WALL_Z[1] + 1.0, x=x, y=0.0, segments=24)
    else:
      part = part - cyl(M3_PILOT / 2, WALL_Z[0] - 1.0, z, x=x, y=0.0, segments=24)
  # the lever's bolt: through the boss into the wall, its lock nut slid in from the wall's front along a slot
  part = part - cyl_x(M5_CLEAR / 2, PIVOT_BOSS_X[0] - 1.0, WALL_X[1] - 3.0, y=PIVOT[0], z=PIVOT[1], segments=32)
  nut_x = (-33.0, -33.0 + 6.4)
  part = part - box(nut_x[0], nut_x[1], WALL_Y[0] - 1.0, PIVOT[0] + 4.8, PIVOT[1] - 4.25, PIVOT[1] + 4.25)
  return clean(part)


'''
s=s[:start]+new+s[end:]
open(p,'w').write(s)
EOF
cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide/chk.py <<'EOF'
"""Slide mount draft against the car for several key depths: carrier, motor, lever (on and off and its swing), block,
rods, springs, collars, switch."""
import math, sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
import numpy as np
import popparts as PP
import slideparts as S
import study90 as SD
from cadlib import union

M = float(sys.argv[1]) if len(sys.argv) > 1 else S.MOUNT_DEG_S
Ds = [float(v) for v in sys.argv[2].split(",")] if len(sys.argv) > 2 else [103.0, 106.0, 110.0, 115.0, 120.0, 125.0]
mb = S.motor_board()
st = S.STROKE
off = SD.SWING = S.SWING_SIGN * S.LEVER_SWING
swing = union([S.slide_lever(S.SWING_SIGN * a) for a in np.arange(0.0, S.LEVER_SWING + 0.1, 8.5)])
moving_on = {"carrier": S.slide_carrier(), "motor": mb["motor"], "board+cap": mb["board+cap"], "car plug": mb["car plug"],
             "motor plug": mb["motor plug"], "own plug": mb["motor's own plug"], "gear": PP.pop_motor_gear(),
             "rods": S.rods(), "collars": S.collars()}
moving_on["lever on"] = S.slide_lever(0.0)
fixed = {"block": S.slide_block(), "switch": S.switch_body(), "release springs (on)": S.release_springs()}
placed = {}
for k, v in moving_on.items():
  placed[k + " [on]"] = SD.place(v, M)
  placed[k + " [off]"] = SD.place(v.translate((0.0, st, 0.0)) if k != "lever on" else S.slide_lever(off).translate((0.0, st, 0.0)), M)
placed["lever swing (slid off)"] = SD.place(swing.translate((0.0, st, 0.0)), M)
for k, v in fixed.items():
  placed[k] = SD.place(v, M)
wheel = SD.fixed_car(M)
rows = []
for pn, pm in placed.items():
  for cn, cm in wheel.items():
    if cn == "fingers on the grip" and "[on]" in pn:
      continue
    g = SD.gap(pm, cm)
    if g < 6:
      rows.append(f"{pn}/{cn}: {g}")
print(f"mount {M:+.0f}  wheel side: " + ("; ".join(rows) if rows else "all >= 6 mm"), flush=True)
for D in Ds:
  sc, car = SD.car_for(D)
  rows = []
  for pn, pm in placed.items():
    for cn, cm in car.items():
      g = SD.gap(pm, cm)
      if g < 6:
        rows.append(f"{pn}/{cn}: {g}")
  print(f"   D {D:.0f}: " + ("; ".join(rows) if rows else "all >= 6 mm"), flush=True)
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache && python3 -c "
import sys; sys.path.insert(0,'/home/claude/deliver/hardware/cad')
import slideparts as S
for n,f in [('carrier',S.slide_carrier),('block',S.slide_block),('lever',S.slide_lever),('pusher',S.pusher),('plug',S.plug)]:
    m=f(); print(n, round(m.volume()), len(m.decompose()), [round(v,1) for v in m.bounding_box()])
"