cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = 'photocomp.py'
s = open(p).read()
old = '''  - lit as the photo was lit (the phone's flash for the night photos, daylight through the windscreen for the day one),
    the brightness matched to something in the same photo that the car model also has (the black column cover, the grip);'''
new = '''  - lit as the photo was lit (the phone's flash for the night photos, the cabin's daylight for the day one), the
    brightness matched to a light grey patch of the same photo (incar.py says which);'''
assert old in s
s = s.replace(old, new)
open(p, 'w').write(s)
p = 'carphoto.py'
s = open(p).read()
old = '''  python3 carphoto.py [width]     # writes ../report/in-the-car-1-drivers-seat.png, -2-from-below.png, -3-from-the-right.png
"""'''
new = '''  python3 carphoto.py [width]     # writes ../report/in-the-car-1-drivers-seat.png, -2-from-below.png, -3-from-the-right.png

Not shipped: the car round the parts here is a rough model. incar.py draws the same parts into your own photos
instead (and takes its motor, zip ties and cable colour from here).
"""'''
assert old in s
s = s.replace(old, new)
open(p, 'w').write(s)
print('ok')
EOF
ruff check incar.py photocomp.py carphoto.py photorender.py --output-format concise | tail -1