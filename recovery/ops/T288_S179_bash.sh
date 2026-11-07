python3 - <<'EOF'
p = 'incar.py'
s = open(p).read()
a = 0
b = s.index('import math')
new_doc = '''"""
What the right-arm build will look like in your car (2 Nov 2026): your own photos with the parts drawn in.

  photo 00  from your seat, daylight (9 Oct): what you will see when you drive
  photo 33  low on the right of the column, beside the key, with the flash (10 Oct): the mount from beside your
            right knee. (Photo 26 works too, but it was taken nearer still: the motor fills it.)

The parts are the CAD parts exactly, where the CAD puts them: the frame plate v4 on the column cover's screws, the arm
v3 and its tower, the motor carrier with the motor (slid up to its stop, the gear in the teeth), the gear, the teeth
v2 (the 20 set) zip-tied on the grip, the wing bolts and nuts, the motor's four screws. Not exact: the motor's board
(a generic board), the cable (its path is a guess: tidied along the arm), the colour (the grey you have been printing
in, from your photos of the prints), the light (matched to a grey patch in the same photo: the silver spoke by day,
the grey panel under the column at night).

The cameras, from the photos themselves:
  - 33 (and 26): from the earlier fit of the four key photos (24, 26, 33, 37) together: the key's black bezel (38 mm
    across, your tape), the instrument cluster's numbers and the grip (372 mm across, 35.4 mm thick); the photos' own
    tilt taken out with photo 36's cluster. Of the two fits that were equally good then, the one your tape agrees
    with: it puts the screw cup 123 mm in front of the back of the grip, your tape said 5 in (127); the other said 82.
    Checked again here: the key's bezel, the stalk and the screw cup drawn with this camera land on them in the photo.
  - 00: the grip's outline (fitted to 0.2 px), the phone's zoom taken as the iPhone's usual (1917 px for these
    pictures; the outline alone can't tell it, and a 7% error moves the motor about 1 px). Of the outline's two mirror
    fits, the one whose inner edge matches the grip's inner edge and that looks down at the wheel (the photo shows the
    ground outside). Which way is level comes from the cluster's dials (0 and 8 on the rev counter, 0 and 160 on the
    speedometer: level within 1.5 degrees). The steering wheel was turned about 17 degrees to the right in that photo
    (the spoke buttons say 20, the badge 13-14), so the teeth piece and its zip ties, which turn with the wheel, are
    drawn turned 17 degrees; the motor and its mount stay with the column. With the wheel straight the teeth sit
    centred on the gear. The hub, spokes and buttons hide what is behind them: their outline round the two openings
    you can see through was traced by hand on the photo.

  python3 incar.py [photo ...]      # default 00 and 33: writes ../report/in-the-car-photo-00.jpg (+ -before-after.jpg)
                                    # and in-the-car-photo-33.jpg
"""
'''
s = new_doc + s[b:]
s = s.replace('''def main(argv):
  names = argv[1:] or list(PHOTOS)''', '''def main(argv):
  names = argv[1:] or ["00", "33"]''')
s = s.replace('''  "33": dict(file="818fd797", cam=33, wheel=0.0, light="flash", ss=1, pair=(0, 0, 1932, 2576),''', '''  "33": dict(file="818fd797", cam=33, wheel=0.0, light="flash", ss=1,''')
open(p, 'w').write(s)
print('ok')
EOF
ruff check --select E,F,W --line-length 120 incar.py photocomp.py 2>&1 | tail -20 || python3 -m ruff check incar.py photocomp.py