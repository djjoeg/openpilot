cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
s = open('carref.py').read()
# docstring: the frame fix and the corrected sources
old = s[:s.index('import math')]
new = '''"""
The car around the steering column, rebuilt from your photos (11 October): where the key, the stalks, the steering
wheel's spokes and back cover and the cover screw under the key are, relative to the steering column.

Frame (mm), as the rest of the CAD: z along the column towards the driver, 0 = the middle of the part of the steering
wheel you hold (the grip); y up; x to the driver's right; the steering wheel straight. Clock positions are seen from the
driver's seat.

How each number was found (photo numbers as in the reference sheet, 00-39):
  - Photo 36 (the whole wheel straight on, your tape across it) sets the frame: the grip (372 mm across, 35.4 mm
    thick) fixes where the camera was. Which way is up comes from the instrument cluster in the same photo: the gear
    letters P R N D D3 run straight down the cluster and the two dials' centres sit level, and both say the phone was
    turned 10 degrees (10.1 and 10.6) from level. Every clock position below has that taken out.
  - In photo 36 the wheel itself was turned about 22 degrees to the right: its spokes are symmetric about a line 22
    degrees from the car's vertical. The spokes' places below are on the wheel, measured from its own vertical.
  - The key photos (24, 26, 33, 37) were all taken from about the same spot, right of the column. In each, the key's
    black bezel (38 mm across: your tape lies over it in photo 24) gives the camera's distance to the key (213-266 mm),
    the edge of the grip shows up 21-26 degrees from the key, and the cluster's numbers tie the photo to photo 36.
    Together they put the key's centre 100-145 mm behind the middle of the grip, 90-115 mm from the column's centre,
    at about 3:47.
  - Photo 24's tape is hooked on the edge of the steering wheel's back cover: the key's centre is 41 mm along the
    cover from it, the grey dash trim 95-100 mm.
  - The wiper stalk comes out of the cover about 50 mm above the key and is about 105 mm long (your tape along it,
    photo 25); photo 36 puts its end about 150 mm from the column's centre; you say its end is at least an inch behind
    the back of the grip.
  - The screw cup under the key: on the lower cover's underside where Honda's drawing puts it, about 60-70 mm from the
    key's centre (photos 33, 37 agree).
  - Not pinned down by the photos (estimates kept from before): the column covers' width and bottom, the hub, the knee
    bolster's depth.
"""
'''
s = s.replace(old, new)
rep = [
("KEY_CLOCK_DEG = -13.0          # about 3:26 (0 = 3 o'clock, + up): range 3:16-3:36",
 "KEY_CLOCK_DEG = -23.0          # about 3:46 (0 = 3 o'clock, + up): range 3:40-3:52"),
('KEY_RANGE = {"clock_deg": (-18.0, -8.0), "r": (90.0, 115.0), "z": (-145.0, -100.0), "tilt_deg": (15.0, 42.0)}',
 'KEY_RANGE = {"clock_deg": (-26.0, -20.0), "r": (90.0, 115.0), "z": (-145.0, -100.0), "tilt_deg": (15.0, 42.0)}'),
("AIRBAG_HOLE = (88.0, -30.0, -45.0, 6.5)    # the airbag bolt hole on its right side: radius, clock, z, hole radius",
 "AIRBAG_HOLE = (88.0, -18.0, -45.0, 6.5)    # the airbag bolt hole on its right side: radius, clock (on the wheel), z, hole radius"),
("WIPER_FROM = (85.0, 32.0, -110.0)   # where the wiper stalk comes out of the cover (range +-15 each way)\n"
 "WIPER_TO = (140.0, 62.0, -27.0)     # its end, 105 mm along (your tape): 150 mm from the column's centre (photo 36: 145-155)\n"
 "WIPER_END_Z_RANGE = (-80.0, -25.0)  # how far behind the middle of the grip its end is: not pinned down by the photos",
 "WIPER_FROM = (89.0, 16.0, -130.0)   # where the wiper stalk comes out of the cover (range +-15 each way)\n"
 "WIPER_TO = (149.0, 36.0, -48.0)     # its end, 104 mm along (your tape): 150 mm from the column's centre (photo 36)\n"
 "WIPER_END_Z = -17.7 - 25.4         # its end at least an inch behind the back of the grip (you), the closest it can be"),
("CUP = (80.0, -90.0, -112.0)         # the screw cup under the key, about 65 mm below its centre: range +-15",
 "CUP = (38.0, -50.0, -98.0)          # the screw cup under the key, on the lower cover's underside (Honda's drawing)"),
]
for a, b in rep:
    assert a in s, a[:60]
    s = s.replace(a, b)
# spokes (on the wheel, from its own vertical; + up from 3 o'clock)
old = "# ----- under the key -----"
new = """# ----- the steering wheel's spokes where they meet the grip (photo 36, measured from the wheel's own vertical) -----
RIGHT_SPOKE_DEG = (-23.0, 18.0)     # the right spoke (cruise buttons) meets the grip from about 3:46 up to 2:24
RIGHT_BAR_DEG = (-74.0, -56.0)      # the right lower spoke (the silver bar) meets the grip from about 5:28 up to 4:52
SPOKE_TOL_DEG = 3.0                 # how far off those may be (read off one photo)
# ----- under the key -----"""
assert old in s
s = s.replace(old, new)
old_rows = s[s.index("REFERENCE_ROWS = ["):]
new_rows = '''REFERENCE_ROWS = [
  ("Key: centre of the bezel", "about 3:47 (3:40–3:52); 90–115 mm out from the column's centre; 100–145 mm behind the middle of the grip (best guess 115)",
   "photos 24, 26, 33, 37 (bezel size, grip edge, cluster numbers), set level by photo 36's cluster; your tape in photo 24"),
  ("Key: which way it faces", "out from the column, turned 15–42° towards you", "photos 24 (tape marks), 26, 33, 37"),
  ("Key bezel", "black ring 38 mm across, chrome ring about 26 mm; keyhole slot at about 45°", "your tape over it, photo 24; photos 26, 33, 37"),
  ("Wheel's back cover: its edge by the column covers", "41 mm in front of the key's centre, along the cover", "your tape, photo 24"),
  ("Grey dash trim beside the key", "95–100 mm from the back cover's edge, along the cover", "your tape, photo 24"),
  ("Wiper stalk", "comes out about 50 mm above the key, about 105 mm long; its end about 150 mm from the column's centre at about 2:25, at least an inch behind the back of the grip",
   "photos 24, 26, 33, 37, 36; your tape, photo 25; you"),
  ("Right spoke (cruise buttons)", "meets the grip from about 2:24 to 3:46 (±3°)", "photo 36"),
  ("Right lower spoke (silver bar)", "meets the grip from about 4:52 to 5:28 (±3°)", "photo 36"),
  ("Screw cup under the key", "on the lower cover's underside, 60–70 mm from the key's centre", "Honda's drawing; photos 33, 37"),
  ("Steering wheel", "372 mm across, grip 35.4 mm thick", "your tape, photos 36 and 35"),
]
'''
s = s.replace(old_rows, new_rows)
open('carref.py', 'w').write(s)
print('ok')
EOF
grep -n "^[A-Z_]* = " carref.py