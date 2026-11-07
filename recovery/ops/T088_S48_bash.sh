python3 - <<'EOF'
p='columnparts.py'; s=open(p).read()
old='''  plates = []
  for sgn in (-1, 1):
    x0, x1 = (SIDE_PLATE_X[0], SIDE_PLATE_X[1]) if sgn > 0 else (-SIDE_PLATE_X[1], -SIDE_PLATE_X[0])
    a0, a1 = ARM_ANGLES[0] - 15.0, ARM_ANGLES[1] + 15.0
    pts = [(py, pz)]
    for a in np.linspace(-a1, -a0, 41):
      pts.append((py + (r + 9.0) * math.sin(math.radians(a)), pz + (r + 9.0) * math.cos(math.radians(a))))
    pie = prism_x(pts, x0, x1)
    web = box(x0, x1, min(p[0] for p in pts), SADDLE_BOTTOM + 0.01, min(p[1] for p in pts), pz + 1.0)
    plates.append(pie + web + cyl_x(10.0, x0, x1, y=py, z=pz))
  part = part + union(plates)'''
new='''  plates = []
  for sgn in (-1, 1):
    x0, x1 = (SIDE_PLATE_X[0], SIDE_PLATE_X[1]) if sgn > 0 else (-SIDE_PLATE_X[1], -SIDE_PLATE_X[0])
    a0, a1 = ARM_ANGLES[0] - 15.0, ARM_ANGLES[1] + 15.0
    pts = [(py, pz)]
    for a in np.linspace(-a1, -a0, 41):
      pts.append((py + (r + 9.0) * math.sin(math.radians(a)), pz + (r + 9.0) * math.cos(math.radians(a))))
    pie = CrossSection([pts])
    if pie.area() < 0:
      pie = CrossSection([pts[::-1]])
    # one plate: the pie round the arm's bolt, hulled with a strip along the saddle's underside
    plate = CrossSection.batch_hull([pie, circle_yz(10.0, py, pz), rect_yz(SADDLE_BOTTOM - 0.01, SADDLE_BOTTOM + 1.0, -SADDLE_LEN / 2, SADDLE_LEN / 2)])
    plates.append(extrude_x(plate, x0, x1))
  part = part + union(plates)'''
assert old in s; s=s.replace(old,new)
s=s.replace("from cadlib import box, clean, cyl, cyl_x, cyl_y, polar_mask, prism_x, revolve, sector, union",
            "from cadlib import box, circle_yz, clean, cyl, cyl_x, cyl_y, extrude_x, polar_mask, rect_yz, revolve, sector, union")
open(p,'w').write(s); print("ok")
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import columnparts as CP, render as R
from cadlib import on_bed, size_of
lo = CP.column_clamp_lower()
print(len(lo.decompose()), lo.status(), [round(v,1) for v in size_of(lo)], round(lo.volume()/1000,1))
R.save("/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/photo/lower2.png",
       [([(lo,(.55,.7,.9))], R.look((1,-0.6,0.8),(0,1,0))), ([(lo,(.55,.7,.9))], R.look((1,0,0),(0,1,0)))], ["lower saddle", "from the right"], size=(700,600))
EOF