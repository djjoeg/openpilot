python3 - <<'EOF'
p = "carphoto.py"
s = open(p).read()
import re
new_mats = '''PETG = PR.Mat((0.15, 0.155, 0.165), spec=0.08, shine=60)          # grey PETG
STEEL = PR.Mat((0.45, 0.45, 0.47), spec=0.70, shine=110)
MOTOR_BLACK = PR.Mat((0.012, 0.012, 0.014), spec=0.10, shine=35)
ALU = PR.Mat((0.38, 0.38, 0.40), spec=0.45, shine=45)
PCB = PR.Mat((0.004, 0.05, 0.013), spec=0.12, shine=50, smooth=False)
CHIP = PR.Mat((0.008, 0.008, 0.008), spec=0.25, shine=60, smooth=False)
PLUG = PR.Mat((0.62, 0.60, 0.52), spec=0.10, shine=30, smooth=False)
RIM = PR.Mat((0.014, 0.014, 0.016), spec=0.03, shine=12)
SPOKE = PR.Mat((0.24, 0.23, 0.21), spec=0.30, shine=40)
HUB = PR.Mat((0.013, 0.013, 0.015), spec=0.025, shine=10)
COVER = PR.Mat((0.011, 0.011, 0.013), spec=0.025, shine=10)
DASH = PR.Mat((0.30, 0.29, 0.27), spec=0.02, shine=10, smooth=False)
NYLON = PR.Mat((0.01, 0.01, 0.01), spec=0.15, shine=40)
'''
start = s.index("PETG = PR.Mat(")
end = s.index("WORLD_UP = ")
s = s[:start] + new_mats + "\n" + s[end:]
s = s.replace('"1-drivers-seat": dict(eye=(-10.0, 75.0, 630.0), target=(105.0, -95.0, -45.0), up=WORLD_UP, fov=36.0),',
              '"1-drivers-seat": dict(eye=(-10.0, 75.0, 630.0), target=(125.0, -105.0, -45.0), up=WORLD_UP, fov=30.0),')
s = s.replace("img = PR.render(sc, cam, KEY, sky_up=WORLD_UP, fill_dir=fill, fill_power=0.45, ss=2, exposure=1.15)",
              "img = PR.render(sc, cam, KEY, key_power=2.4, sky_up=WORLD_UP, ambient=1.0, fill_dir=fill, fill_power=0.55, ss=2, exposure=1.25)")
open(p, "w").write(s)
# a bigger dash wall so its edges stay out of the pictures
p = "carscene.py"
EOF
grep -n "def bolster" -A 3 carscene.py | head -5; python3 - <<'EOF'
p = "/home/claude/deliver/hardware/cad/carphoto.py"
s = open(p).read()
old = "  return [(sc.column_cover(back=130.0), COVER), (sc.bolster(), DASH),"
new = """  wall = box(-700.0, 700.0, -600.0, 400.0, sc.dash_z - 40.0, sc.dash_z) - (box(-1e3, 1e3, -1e3, 1e3, -1e3, 1e3) - sc.bolster().hull()) \\
    if False else sc.bolster()
  big = box(-700.0, 700.0, -600.0, 400.0, sc.dash_z - 40.0, sc.dash_z)
  hole = box(-1e3, 1e3, -1e3, 1e3, sc.dash_z - 41.0, sc.dash_z + 1.0) - sc.bolster().translate((0.0, 0.0, 0.0))
  wall = big - (hole ^ box(-300.0, 300.0, -400.0, 120.0, sc.dash_z - 41.0, sc.dash_z + 1.0))
  return [(sc.column_cover(back=130.0), COVER), (wall, DASH),"""
assert s.count(old) == 1
s = s.replace(old, new)
open(p, "w").write(s)
print("ok")
EOF
cd /home/claude/deliver/hardware/cad && (time PYTHONPATH=/home/claude/pylib timeout 1800 python3 carphoto.py 640) 2>&1 | tail -4