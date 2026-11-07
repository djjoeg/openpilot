cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
import re
p = 'incar.py'
s = open(p).read()
old_photos = s[s.index('PHOTOS = {'):s.index('def camera(spec)')]
new_photos = '''# per photo: the photo, its camera, how far the steering wheel was turned (the teeth turn with it), the light, and a
# light-grey patch of the photo the prints are matched to (box in pixels, where it is in the car, which way it faces):
# the silver spoke by day (your prints look as light as it in your photo of the test teeth on the wheel), the grey
# panel under the column at night
PHOTOS = {
  "00": dict(file="273a348a", cam=cam00, wheel=-17.0, light="day",
             ref=dict(boxes=[(1225, 1795, 1250, 1815), (1170, 1845, 1195, 1865), (1120, 1895, 1145, 1915)], plane_z=30.0,
                      normal=(0.0, 0.0, 1.0))),
  "33": dict(file="818fd797", cam=33, wheel=0.0, light="flash",
             ref=dict(boxes=[(1000, 1790, 1500, 1880)], dash=True)),
  "26": dict(file="a5f478e3", cam=26, wheel=0.0, light="flash",
             ref=dict(boxes=[(700, 1880, 1100, 1960)], dash=True)),
}

# where you can see through the steering wheel in photo 00 (between the right lower spoke, the cruise buttons, the
# hub and the grip; between the two lower spokes): everything else inside the grip is the wheel itself, in front of
# the parts. The outlines run into the grip, which hides what is behind it on its own.
OPENINGS_00 = [
  [(1350, 1690), (1400, 1684), (1460, 1700), (1520, 1712), (1720, 1712), (1720, 2320), (950, 2320), (1000, 2030),
   (1080, 1985), (1170, 1900), (1265, 1800)],
  [(580, 1748), (800, 1752), (1000, 1772), (1100, 1790), (1165, 1800), (1080, 1900), (975, 2005), (960, 2320),
   (580, 2320)],
]


'''
s = s.replace(old_photos, new_photos)
open(p, 'w').write(s)
print('ok')
EOF