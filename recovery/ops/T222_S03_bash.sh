python3 - <<'EOF'
p='armmount.py'; s=open(p).read()
old=s[s.index('# ***** the frame plate v2 (plate frame'):s.index('# ***** the shoe (steering wheel frame) *****')]
new='''# ***** the frame plate v3 (plate frame, as frameplate.py: x towards the driver's door, y towards the dash, 0 at the cup) *****
# v1 (frameplate.py) marked up on the car, 1 Nov 2026: the second screw lands in the strip's first slot towards the
# wheel; keep that slot, fill the one towards the dash, cut the other four columns away. So: the block round the cup
# (7 mm, the shoe's four bolts trapped in it), v1's bar across the dash end, and a narrow leg down the door side with
# the one slot. The bar and the leg are 6 mm thick (v1 was 4).
T_PLATE = FR.T                   # 4 (frameplate.py's labels sit on this)
BAR_T = 6.0
BLOCK_T = 7.0                    # the block round the cup: thicker, for the bolt heads' pockets
BLOCK = (-18.0, 28.0, -14.0, 50.0)       # x0, x1, y0, y1 (v1's)
BAR = (-18.0, 106.0, 36.0, 50.0)         # v1's bar, across the dash end
LEG = (88.0, 106.0, -46.0, 50.0)         # the leg: v1's first slot column, with 9 mm of plastic each side of the slot
LEG_SLOT = (97.0, -40.0, -3.0)           # x, y0, y1: v1's first column, the slot towards the wheel (the second screw)
BOLTS_P = ((0.0, 20.0), (24.0, 20.0), (0.0, 42.0), (24.0, 42.0))   # the shoe's bolts: clear of the cup slot and washer
M5_HOLE = 5.4
HEX_AF, HEX_DEEP = 8.4, 3.8      # M5 hex head (DIN 933: 8 across flats, 3.5 tall)
M5_NUT_AF, M5_NUT_T = 8.0, 4.0

'''
s=s.replace(old,new)
s=s.replace('''SHOE_Z = (CUP_Z - BLOCK[3], CUP_Z - BLOCK[2])              # (-169, -95): under the block''','''SHOE_Z = (CUP_Z - BLOCK[3], CUP_Z - BLOCK[2])              # (-195, -131): under the block''')
s=s.replace('''FIN_Z = (-135.0, SHOE_Z[1])
FIN_SLOT_Y = (-130.0, -144.0)
FIN_SLOT_Z = (-130.0, -100.0)''','''FIN_Z = (-175.0, SHOE_Z[1])
FIN_SLOT_Y = (-130.0, -144.0)
FIN_SLOT_Z = (-170.0, -136.0)''')
s=s.replace('''ARM_Z = (-140.0, -55.0)
ARM_HOLES_Z = -115.0             # the two holes to the fin (at FIN_SLOT_Y), nominal: the middle of the fin's slots''','''ARM_Z = (-175.0, -55.0)
ARM_HOLES_Z = -153.0             # the two holes to the fin (at FIN_SLOT_Y), nominal: the middle of the fin's slots''')
old=s[s.index('def frame_plate_v2() -> Manifold:'):s.index('# ----- the shoe, the arm and the bracket')]
new='''def frame_plate_v3() -> Manifold:
  body = box(BAR[0], BAR[1], BAR[2], BAR[3], 0.0, BAR_T) + box(LEG[0], LEG[1], LEG[2], LEG[3], 0.0, BAR_T) + \\
    box(BLOCK[0], BLOCK[1], BLOCK[2], BLOCK[3], 0.0, BLOCK_T)
  body = body - FR.slot(0.0, 0.0, FR.SLOT_L, FR.SLOT_W, "x")
  xc, y0, y1 = LEG_SLOT
  body = body - FR.slot(xc, (y0 + y1) / 2, y1 - y0, FR.SLOT_W, "y")
  for x, y in BOLTS_P:
    body = body - cyl(M5_HOLE / 2, -1.0, BLOCK_T + 1.0, x=x, y=y, segments=32)
    body = body - hex_prism_z(HEX_AF, -1.0, HEX_DEEP, x=x, y=y)         # open on the cover side (the print bed)
  body = body.mirror((1.0, 0.0, 0.0))                                    # printed: key side +x, labels up
  labels = [FR.text("KEY >", -BLOCK[0] - FR.text_width("KEY >") - 2.0, BLOCK[3] - 8.0, BLOCK_T),
            FR.text("WHEEL", -8.0, BLOCK[2] + 3.0, BLOCK_T, pix=0.9),
            FR.text("1", -xc - FR.text_width("1", 0.9) / 2, LEG[2] + 3.0, BAR_T, pix=0.9)]
  return clean(body + union(labels))


frame_plate_v2 = frame_plate_v3     # the name the rest of this file uses


def plate_drawing(path: str) -> None:
  """The frame plate v3 seen from below, as in the photos, with the screws drawn in."""
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
  xc, y0, y1 = LEG_SLOT
  ax.add_patch(Rectangle((xc - FR.SLOT_W / 2, y0), FR.SLOT_W, y1 - y0, fc="white", ec="#444"))
  for x, y in BOLTS_P:
    ax.add_patch(Circle((x, y), HEX_AF / 2, fc="white", ec="#444"))
  ax.add_patch(Circle((0, 0), 6.25, fc="none", ec="#c0392b", ls="--", lw=1.5))
  ax.text(0, -12, "cup screw", ha="center", va="top", fontsize=8, color="#c0392b")
  ax.text(xc, -44, "2nd screw", ha="center", va="top", fontsize=8, color="#c0392b")
  ax.text(12, 31, "shoe bolts (heads trapped,\\nthreads down)", ha="center", va="center", fontsize=7, color="#444")
  ax.text(44, 43, "6 mm thick", ha="center", va="center", fontsize=7, color="#444")
  ax.text(5, -8, "7 mm", ha="center", va="center", fontsize=7, color="#444")
  ax.set_aspect("equal")
  ax.set_xlim(125, -40)
  ax.set_ylim(-62, 62)
  ax.set_xlabel("across the car, mm (0 = cup screw; the key side to the right)")
  ax.set_ylabel("along the column, mm (0 = cup screw; the wheel is down)")
  ax.set_title("Frame plate v3 seen from below, as in the photos (print labels up; in the car the labels face down).\\n"
               "v1 with your marks: the first slot column kept, its dash-side slot filled, the rest cut away; bar and leg 6 mm.", fontsize=9)
  ax.grid(True, lw=0.3, alpha=0.5)
  fig.tight_layout()
  fig.savefig(path)
  plt.close(fig)


'''
s=s.replace(old,new)
s=s.replace('"column-frame-plate-v2": on_bed(frame_plate_v2())','"column-frame-plate-v3": on_bed(frame_plate_v3())')
s=s.replace('''  parts = {"column-frame-plate-v2": ("frame plate v2", 1, P.STANDARD)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-5-frame-plate-v2", "5 frame plate v2", list(parts), "Plate 5: the frame plate v2 (bolts trapped in it)")])''',
'''  parts = {"column-frame-plate-v3": ("frame plate v3", 1, P.STANDARD)}
  out += P.build(out_dir=os.path.join(HERE, "..", "plates"), stl_dir=STL_DIR, parts=parts,
                 plate_list=[("plate-5-frame-plate-v3", "5 frame plate v3", list(parts), "Plate 5: the frame plate v3 (bolts trapped in it)")])''')
s=s.replace('([(bed["column-frame-plate-v2"], (0.8, 0.82, 0.85))], R.view_matrix(-50, 35))','([(bed["column-frame-plate-v3"], (0.8, 0.82, 0.85))], R.view_matrix(-50, 35))')
s=s.replace('"frame plate v2, as printed (labels up)"','"frame plate v3, as printed (labels up)"')
s=s.replace('plate_drawing(os.path.join(REPORT_DIR, "column-frame-plate-v2.png"))','plate_drawing(os.path.join(REPORT_DIR, "column-frame-plate-v3.png"))')
s=s.replace('suptitle="Arm mount v1 on the frame plate v2','suptitle="Arm mount v1 on the frame plate v3')
open(p,'w').write(s)
p='midteeth.py'; s=open(p).read()
s=s.replace('INNER_PULL = 0.0       # mm the inner wall moves out towards the grip (0 until measured)','INNER_PULL = 8.0       # mm the inner wall moves out towards the grip (fit test 1 Nov 2026: 6 was still 1 to 3 mm loose)')
open(p,'w').write(s)
EOF
rm -f ../plates/plate-5-frame-plate-v2.3mf ../plates/plate-5-frame-plate-v2.png ../stl/arm-mount/column-frame-plate-v2.stl ../report/column-frame-plate-v2.png
PYTHONPATH=/home/claude/pylib timeout 900 python3 armmount.py 2>&1 | tail -6