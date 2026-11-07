python3 - <<'EOF'
p='armmount.py'; s=open(p).read()

# --- the car and the plate v2 geometry ---
old=s[s.index('# ***** the frame plate v2 *****'):s.index('# ***** the bracket *****')]
new='''# ***** the frame plate v2 (plate frame, as frameplate.py: x towards the driver's door, y towards the dash, 0 at the cup) *****
# The tilt lever's handle block is beside the cup towards the wheel, its boot runs from the pivot pin towards the dash:
# so the bar that joins the two sides runs across the WHEEL end (v1 had it across the dash end, on the boot), the second
# screw (40 mm towards the wheel from the cup, 85 mm towards the door) lands in a window at the bar's end, and the leg on
# the door side stops short of the pin and the boot.
T_PLATE = FR.T                   # 4
BLOCK_T = 7.0                    # the block round the cup: thicker, for the bolt heads' pockets
BLOCK = (-18.0, 28.0, -50.0, 24.0)       # x0, x1, y0, y1
BAR = (-18.0, 106.0, -50.0, -38.0)
LEG = (78.0, 106.0, -50.0, 22.0)
WINDOW = (78.0, 100.0, -46.0, -34.0)     # the second screw, with a 3/4 in fender washer over the window
LEG_SLOTS = ((84.0, -30.0, 18.0), (92.0, -30.0, 18.0))   # x, y0, y1: if the second screw is further towards the dash
CAP = (32.0, 70.0, -33.0, 9.0)           # the lever's handle block (photo, rough): x0, x1, y0 (wheel side), y1
BOLTS_P = ((0.0, -34.0), (24.0, -34.0), (0.0, 16.0), (24.0, 16.0))   # the shoe's bolts: clear of the cup slot and washer
M5_HOLE = 5.4
HEX_AF, HEX_DEEP = 8.4, 3.8      # M5 hex head (DIN 933: 8 across flats, 3.5 tall)
M5_NUT_AF, M5_NUT_T = 8.0, 4.0

# ***** the shoe (steering wheel frame) *****
SHOE_X = (45.0, 108.0)
SHOE_Z = (CUP_Z - BLOCK[3], CUP_Z - BLOCK[2])              # (-169, -95): under the block
SHOE_T = 8.0
SHOE_Y = (COVER_Y - BLOCK_T - SHOE_T, COVER_Y - BLOCK_T)    # (-122, -114)
POCKET = ((53.0, 93.0), (-155.0, -135.0), 4.0)               # x, z, deep: the cup screw's head and washer
FIN_X = (96.0, 106.0)
FIN_Y = (-152.0, SHOE_Y[0])
FIN_Z = (-135.0, SHOE_Z[1])
FIN_SLOT_Y = (-130.0, -144.0)
FIN_SLOT_Z = (-130.0, -100.0)

# ***** the arm *****
ARM_X = (86.0, 96.0)
ARM_Y = (-152.0, SHOE_Y[0])      # its top edge on the shoe's underside
ARM_Z = (-140.0, -55.0)
ARM_HOLES_Z = -115.0             # the two holes to the fin (at FIN_SLOT_Y), nominal: the middle of the fin's slots
ARM_SLOT_Z = (-75.0, -60.0)      # the two upright slots at the back
ARM_SLOT_Y = (-146.0, -128.0)

'''
s=s.replace(old,new)

# --- the plate v2 builder ---
old=s[s.index('def frame_plate_v2() -> Manifold:'):s.index('# ----- the shoe, the arm and the bracket')]
new='''def frame_plate_v2() -> Manifold:
  T = T_PLATE
  body = FR.rbox(BAR) + FR.rbox(LEG) + box(BLOCK[0], BLOCK[1], BLOCK[2], BLOCK[3], 0.0, BLOCK_T)
  body = body - FR.slot(0.0, 0.0, FR.SLOT_L, FR.SLOT_W, "x")
  body = body - box(WINDOW[0], WINDOW[1], WINDOW[2], WINDOW[3], -1.0, BLOCK_T + 1.0)
  for xc, y0, y1 in LEG_SLOTS:
    body = body - FR.slot(xc, (y0 + y1) / 2, y1 - y0, FR.SLOT_W, "y")
  for x, y in BOLTS_P:
    body = body - cyl(M5_HOLE / 2, -1.0, BLOCK_T + 1.0, x=x, y=y, segments=32)
    body = body - hex_prism_z(HEX_AF, -1.0, HEX_DEEP, x=x, y=y)         # open on the cover side (the print bed)
  body = body.mirror((1.0, 0.0, 0.0))                                    # printed: key side +x, labels up
  labels = [FR.text("KEY >", -BLOCK[0] - FR.text_width("KEY >") - 2.0, BLOCK[3] - 8.0, BLOCK_T),
            FR.text("WHEEL", -8.0, BLOCK[2] + 3.0, BLOCK_T, pix=0.9),
            FR.text("1", -84.0 - FR.text_width("1", 0.9) / 2, LEG[3] - 4.0, T, pix=0.9),
            FR.text("2", -92.0 - FR.text_width("2", 0.9) / 2, LEG[3] - 4.0, T, pix=0.9)]
  return clean(body + union(labels))


def plate_drawing(path: str) -> None:
  """The frame plate v2 seen from below, as in the photos, with the lever and the screws drawn in."""
  import matplotlib
  matplotlib.use("Agg")
  import matplotlib.pyplot as plt
  from matplotlib.patches import Circle, Rectangle
  fig, ax = plt.subplots(figsize=(8.5, 6.0), dpi=150)
  for r in (BLOCK, BAR, LEG):
    ax.add_patch(Rectangle((r[0], r[2]), r[1] - r[0], r[3] - r[2], fc="#cfd3d6", ec="#444", lw=1.0))
  for r in (BLOCK, BAR, LEG):
    ax.add_patch(Rectangle((r[0] + 0.5, r[2] + 0.5), r[1] - r[0] - 1.0, r[3] - r[2] - 1.0, fc="#cfd3d6", ec="none"))
  ax.add_patch(Rectangle((-FR.SLOT_L / 2, -FR.SLOT_W / 2), FR.SLOT_L, FR.SLOT_W, fc="white", ec="#444"))
  ax.add_patch(Rectangle((WINDOW[0], WINDOW[2]), WINDOW[1] - WINDOW[0], WINDOW[3] - WINDOW[2], fc="white", ec="#444"))
  for xc, y0, y1 in LEG_SLOTS:
    ax.add_patch(Rectangle((xc - FR.SLOT_W / 2, y0), FR.SLOT_W, y1 - y0, fc="white", ec="#444"))
  for x, y in BOLTS_P:
    ax.add_patch(Circle((x, y), HEX_AF / 2, fc="white", ec="#444"))
  ax.add_patch(Circle((0, 0), 6.25, fc="none", ec="#c0392b", ls="--", lw=1.5))
  ax.add_patch(Circle((87.0, -40.0), 3.0, fc="none", ec="#c0392b", ls="--", lw=1.5))
  ax.add_patch(Rectangle((CAP[0], CAP[2]), CAP[1] - CAP[0], CAP[3] - CAP[2], fc="#f7d9d4", ec="#c0392b", ls="--", lw=1.5))
  ax.add_patch(Rectangle((55.0, 23.0), 31.0, 60.0, fc="#f7d9d4", ec="#c0392b", ls="--", lw=1.5))
  ax.add_patch(Circle((80.0, 30.0), 3.0, fc="none", ec="#c0392b", ls="--", lw=1.5))
  ax.text(0, -12, "cup screw", ha="center", va="top", fontsize=8, color="#c0392b")
  ax.text(87, -27, "2nd screw\\n(washer over\\nthe window)", ha="center", va="top", fontsize=8, color="#c0392b")
  ax.text(51, -12, "lever handle", ha="center", va="center", fontsize=8, color="#c0392b")
  ax.text(70.5, 55, "lever boot", ha="center", va="center", fontsize=8, color="#c0392b")
  ax.text(78, 30, "pin", ha="right", va="center", fontsize=8, color="#c0392b")
  ax.text(12, 8, "shoe bolts", ha="center", va="center", fontsize=7, color="#444")
  ax.set_aspect("equal")
  ax.set_xlim(125, -40)
  ax.set_ylim(-62, 90)
  ax.set_xlabel("across the car, mm (0 = cup screw; the key side to the right)")
  ax.set_ylabel("along the column, mm (0 = cup screw; the wheel is down)")
  ax.set_title("Frame plate v2 seen from below, as in the photos (print labels up; in the car the labels face down).\\n"
               "Red dashed: the car, from the photos (rough). The bar is at the wheel end; the dash end is open for the boot.", fontsize=9)
  ax.grid(True, lw=0.3, alpha=0.5)
  fig.tight_layout()
  fig.savefig(path)
  plt.close(fig)


'''
s=s.replace(old,new)
s=s.replace('''  os.makedirs(REPORT_DIR, exist_ok=True)
  picture(os.path.join(REPORT_DIR, "arm-mount.png"))''','''  os.makedirs(REPORT_DIR, exist_ok=True)
  plate_drawing(os.path.join(REPORT_DIR, "column-frame-plate-v2.png"))
  picture(os.path.join(REPORT_DIR, "arm-mount.png"))''')
# the picture: a tighter cover (back 120) and the views
s=s.replace('''  sc = CS.CarScene(D=125.0)''','''  sc = CS.CarScene(D=125.0)
  cover = sc.column_cover(back=130.0)''')
s=s.replace('''  return [(sc.column_cover(), car), (grip, car)''','''  return [(cover, car), (grip, car)''')
open(p,'w').write(s)
EOF
grep -n "COVER_Y\b" armmount.py | head -3; PYTHONPATH=/home/claude/pylib timeout 900 python3 armmount.py 2>&1 | tail -8