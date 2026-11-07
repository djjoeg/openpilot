python3 - <<'EOF'
p = 'CHANGELOG.md'
s = open(p, encoding='utf-8').read()
reps = [
 ("since the M5 nuts come from your own kit and nothing uses M4), M3 x 10 set screws",
  "since the M5 nuts come from your own kit and nothing used M4 then; the v4 stop does, above), M3 x 10 set screws"),
 ("""  ends run over both joins, as drawn. The column's underside doesn't show in the head-on photos (the hub hides it;
  through the gap below it you see the footwell); where the gear lands still comes from the side photos and the arm.
""",
  """  ends run over both joins, as drawn. The column's underside doesn't show in the head-on photos (the hub hides it;
  through the gap below it you see the footwell); where the gear lands still comes from the side photos and the arm.
- **Where the spokes' joins leave the back of the grip** (3 Nov, for the teeth, which sit on the back): measured on
  photos of the same steering wheel from eBay listings, read the same way as yours (the rim's outline fitted, the
  light and dark read off round the grip, the angle squared up by the wheel's own symmetry, the view from behind
  mirrored). The back of the grip is clear from about 6 to 46 degrees below 3 o'clock (3:12 to 4:32), the two photos
  within about 2 degrees of each other. The silver spoke's join reaches further round on the back (46) than its edge
  seen from the front (53, above). The 20 teeth take 39 degrees, plus 0.6 at each end, so they fit only with the
  gear at the gap's middle, 26 degrees (3:52): the arm v4 puts it there. At v3's 30 the teeth's lower end would have
  sat about 4 degrees onto the silver spoke's join.
"""),
 ("""| the right arm mount v3, built from the CAD files | 3,502 clearance, fit and mesh checks with all three teeth sets, none failing |
""",
  """| the right arm mount v3, built from the CAD files | 3,502 clearance, fit and mesh checks with all three teeth sets, none failing |
| the right arm mount v4 and the teeth v3 (3 Nov), built from the CAD files | 5,384 clearance, fit, assembly and mesh checks with all three teeth sets, none failing |
"""),
]
for a, b in reps:
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
p = 'hardware/cad/rightarm.py'
s = open(p, encoding='utf-8').read()
a = "WASHER_OD, WASHER_T = 24.0, 1.6  # a #8 or M4 fender washer; anything over 17 mm across lands on the tower"
b = ("WASHER_OD, WASHER_T = 24.0, 1.6  # a fender washer 19 to 25 mm across, #8 or M4 hole: over 18.2 it sits on the\n"
     "                                 # tower's bottom face clear of the tube's chamfer (DIN 9021 M4, 12 mm, is too small)")
assert s.count(a) == 1
s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
EOF