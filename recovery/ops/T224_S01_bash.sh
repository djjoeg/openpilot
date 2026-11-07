python3 - <<'EOF'
p='armmount.py'; s=open(p).read()

# ---- geometry: the plate with a receiver tube, no shoe ----
old=s[s.index('# ***** the frame plate v3 (plate frame'):s.index('# ***** the arm *****')]
new='''# ***** the frame plate v3 (plate frame, as frameplate.py: x towards the driver's door, y towards the dash, 0 at the cup) *****
# v1 (frameplate.py) marked up on the car, 1 Nov 2026: the second screw lands in the strip's first slot towards the
# wheel; keep that slot, fill the one towards the dash, cut the other four columns away. So: the block round the cup,
# v1's bar across the dash end, and a narrow leg down the door side with the one slot; 6 mm thick (v1 was 4).
# Under the block, on the key side of the cup, a receiver: a square tube along the column the arm slides into from
# the wheel end, like a trailer hitch. The tube carries the load; one wing bolt through its outer wall, into a nut
# trapped in the wall, pinches the arm so it can't slide. No shoe, no other screws.
PLATE_T = 6.0
BLOCK = (-44.0, 28.0, -14.0, 50.0)       # x0, x1, y0, y1: v1's block, out to the receiver's outer wall
BAR = (-18.0, 106.0, 36.0, 50.0)         # v1's bar, across the dash end
LEG = (88.0, 106.0, -46.0, 50.0)         # the leg: v1's first slot column, with 9 mm of plastic each side of the slot
LEG_SLOT = (97.0, -40.0, -3.0)           # x, y0, y1: v1's first column, the slot towards the wheel (the second screw)
# the receiver (plate frame x; "down" is away from the cover): its bore takes the arm (ARM_X, ARM_Y below) with 0.4 mm
# to spare; the inner wall 5 mm, the outer wall 8 mm (the nut trap is in it), the floor 5 mm; open at both ends
BORE_X = (-35.2, -24.8)                  # x: the arm at steering wheel X 98..108 is plate x -25..-35
BORE_DEPTH = 30.4                        # the arm is 30 tall
TUBE_X = (BORE_X[0] - 8.0, BORE_X[1] + 5.0)
TUBE_FLOOR_T = 5.0
TUBE_Y = (BLOCK[2], BLOCK[3])            # along the column, the block's length (64)
PINCH = (18.0, PLATE_T + BORE_DEPTH / 2) # the wing bolt: y along the tube, and its height below the cover side
M5_HOLE = 5.4
M5_NUT_AF, M5_NUT_T = 8.0, 4.0
NUT_TRAP = (M5_NUT_AF + 0.4, M5_NUT_T + 0.4)   # the slot in the outer wall the nut drops into from the floor side

'''
s=s.replace(old,new)

# the arm and bracket x positions
s=s.replace('''ARM_X = (86.0, 96.0)
ARM_Y = (-152.0, SHOE_Y[0])      # its top edge on the shoe's underside''','''ARM_X = (CUP_X - BORE_X[1] + 0.2, CUP_X - BORE_X[0] - 0.2)      # (98, 108): in the receiver's bore
ARM_Y = (COVER_Y - PLATE_T - 30.0, COVER_Y - PLATE_T)              # 30 tall, its top edge on the bore's ceiling''')
s=s.replace('''EAR_X = (78.0, 86.0)             # the upright ear, inboard of the arm (the motor's face corner reaches x 72.2, the gear 73.3)''',
'''EAR_X = (ARM_X[0] - 8.0, ARM_X[0])   # the upright ear, inboard of the arm (the motor's face corner reaches x 72.2, the gear 73.3)''')
s=s.replace('''FACE_V = (-H, 32.0)              # the face plate across (towards 4 o'clock), out to the ear''','''FACE_V = (-H, 44.0)              # the face plate across (towards 4 o'clock), out to the ear''')

# ---- the plate builder ----
old=s[s.index('def frame_plate_v3() -> Manifold:'):s.index('frame_plate_v2 = frame_plate_v3')]
new='''def frame_plate_v3() -> Manifold:
  T = PLATE_T
  body = box(BAR[0], BAR[1], BAR[2], BAR[3], 0.0, T) + box(LEG[0], LEG[1], LEG[2], LEG[3], 0.0, T) + \\
    box(BLOCK[0], BLOCK[1], BLOCK[2], BLOCK[3], 0.0, T)
  body = body - FR.slot(0.0, 0.0, FR.SLOT_L, FR.SLOT_W, "x")
  xc, y0, y1 = LEG_SLOT
  body = body - FR.slot(xc, (y0 + y1) / 2, y1 - y0, FR.SLOT_W, "y")
  # the receiver, standing on the plate's labelled side (down, in the car)
  z1 = T + BORE_DEPTH + TUBE_FLOOR_T
  tube = box(TUBE_X[0], TUBE_X[1], TUBE_Y[0], TUBE_Y[1], T - 0.01, z1)
  tube = tube - box(BORE_X[0], BORE_X[1], TUBE_Y[0] - 1.0, TUBE_Y[1] + 1.0, T, T + BORE_DEPTH)
  py, pz = PINCH
  tube = tube - cyl_x(M5_HOLE / 2, TUBE_X[0] - 1.0, BORE_X[0] + 1.0, y=py, z=pz, segments=32)
  tw, tt = NUT_TRAP
  xn = (TUBE_X[0] + BORE_X[0]) / 2                      # the nut in the middle of the outer wall
  tube = tube - box(xn - tt / 2, xn + tt / 2, py - tw / 2, py + tw / 2, pz - tw / 2 / math.cos(math.radians(30)), z1 + 1.0)
  body = body + tube
  body = body.mirror((1.0, 0.0, 0.0))                                    # printed: key side +x, labels up
  labels = [FR.text("KEY >", -BLOCK[0] + 2.0, BLOCK[3] - 8.0, T), FR.text("WHEEL", -8.0, BLOCK[2] + 3.0, T, pix=0.9),
            FR.text("1", -xc - FR.text_width("1", 0.9) / 2, LEG[2] + 3.0, T, pix=0.9)]
  return clean(body + union(labels))


'''
s=s.replace(old,new)

# ---- drawing: the tube's footprint instead of the bolts ----
s=s.replace('''  for x, y in BOLTS_P:
    ax.add_patch(Circle((x, y), HEX_AF / 2, fc="white", ec="#444"))
  ax.add_patch(Circle((0, 0), 6.25, fc="none", ec="#c0392b", ls="--", lw=1.5))''','''  ax.add_patch(Rectangle((TUBE_X[0], TUBE_Y[0]), TUBE_X[1] - TUBE_X[0], TUBE_Y[1] - TUBE_Y[0], fc="#9aa4ad", ec="#444", lw=1.0))
  ax.add_patch(Rectangle((BORE_X[0], TUBE_Y[0]), BORE_X[1] - BORE_X[0], TUBE_Y[1] - TUBE_Y[0], fc="#e8ebee", ec="#444", lw=0.8))
  ax.add_patch(Circle((TUBE_X[0] + 4.0, PINCH[0]), 2.7, fc="white", ec="#444"))
  ax.add_patch(Circle((0, 0), 6.25, fc="none", ec="#c0392b", ls="--", lw=1.5))''')
s=s.replace('''  ax.text(12, 31, "shoe bolts (heads trapped,\\nthreads down)", ha="center", va="center", fontsize=7, color="#444")
  ax.text(44, 43, "6 mm thick", ha="center", va="center", fontsize=7, color="#444")
  ax.text(5, -8, "7 mm", ha="center", va="center", fontsize=7, color="#444")''','''  ax.text(-30, 56, "receiver: the arm\\nslides in from\\nthe wheel end", ha="center", va="bottom", fontsize=7, color="#444")
  ax.text(-30, 18, "wing bolt", ha="right", va="center", fontsize=7, color="#444")
  ax.text(44, 43, "6 mm thick", ha="center", va="center", fontsize=7, color="#444")''')
s=s.replace('''  ax.set_xlim(125, -40)
  ax.set_ylim(-62, 62)''','''  ax.set_xlim(125, -60)
  ax.set_ylim(-62, 78)''')
s=s.replace('''"v1 with your marks: the first slot column kept, its dash-side slot filled, the rest cut away; bar and leg 6 mm.", fontsize=9)''',
'''"v1 with your marks (first slot column kept, its dash-side slot filled, the rest cut away), 6 mm thick, and the receiver for the arm.", fontsize=9)''')

# ---- remove the shoe everywhere ----
old=s[s.index('def shoe() -> Manifold:'):s.index('def arm() -> Manifold:')]
s=s.replace(old,'')
s=s.replace('''          "arm-shoe": on_bed(shoe(), rotate=(180.0, 0.0, 0.0)),
''','')
s=s.replace('''  parts = {"arm-shoe": ("shoe", 1, P.STANDARD), "arm-bar": ("arm", 1, P.SOLID), "arm-bracket": ("bracket", 1, P.SOLID)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-6-arm-mount", "6 arm mount", list(parts), "Plate 6: the arm mount: shoe, arm, bracket")])''',
'''  parts = {"arm-bar": ("arm", 1, P.SOLID), "arm-bracket": ("bracket", 1, P.SOLID)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-6-arm-mount", "6 arm mount", list(parts), "Plate 6: the arm mount: arm, bracket")])''')
s=s.replace('''          (plate_to_wheel(frame_plate_v2()), plate), (shoe(), app), (arm(), app), (bracket(), app)]''','''          (plate_to_wheel(frame_plate_v2()), plate), (arm(), app), (bracket(), app)]''')
s=s.replace('''           ([(bed["arm-shoe"], blue)], R.view_matrix(-50, 35)), ([(bed["arm-bar"], blue)], R.view_matrix(-50, 35)),
           ([(bed["arm-bracket"], blue)], R.view_matrix(-50, 35)), ([(bed["column-frame-plate-v3"], (0.8, 0.82, 0.85))], R.view_matrix(-50, 35))]''',
'''           ([(bed["column-frame-plate-v3"], (0.8, 0.82, 0.85))], R.view_matrix(-50, 35)), ([(bed["arm-bar"], blue)], R.view_matrix(-50, 35)),
           ([(bed["arm-bracket"], blue)], R.view_matrix(-50, 35)), ([(bed["column-frame-plate-v3"], (0.8, 0.82, 0.85))], R.view_matrix(130, 25))]''')
s=s.replace('''         titles=["on the car, from your right and below", "from below, the wheel at the top (as in your photos)",
                 "shoe, as printed (its top on the bed, the fin up)", "arm, as printed",
                 "bracket, as printed (standing on its dash end)", "frame plate v3, as printed (labels up)"],''',
'''         titles=["on the car, from your right and below", "from below, the wheel at the top (as in your photos)",
                 "frame plate v3, as printed (labels up, the receiver standing on it)", "arm, as printed",
                 "bracket, as printed (standing on its dash end)", "frame plate v3 from the other side"],''')
s=s.replace('plate_to_wheel(m: Manifold) -> Manifold:\n  """frameplate\'s printed (mirrored) frame -> steering wheel frame: x_m + CUP_X, z_t -> y, y -> -z."""\n  return m.rotate((-90.0, 0.0, 0.0)).translate((CUP_X, COVER_Y - T_PLATE, CUP_Z))',
            'plate_to_wheel(m: Manifold) -> Manifold:\n  """frameplate\'s printed (mirrored) frame -> steering wheel frame: x_m + CUP_X, z_t -> y, y -> -z."""\n  return m.rotate((-90.0, 0.0, 0.0)).translate((CUP_X, COVER_Y - PLATE_T, CUP_Z))')
open(p,'w').write(s)
EOF
grep -n "SHOE\|shoe\|T_PLATE\|BLOCK_T\|FIN_\|HEX_\|bolt_xz\|BOLTS_P" armmount.py | head -40