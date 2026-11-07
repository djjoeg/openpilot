python3 - <<'EOF'
p='armmount.py'; s=open(p).read()
s=s.replace('''def plate_to_wheel(m: Manifold) -> Manifold:
  """frameplate's printed (mirrored) frame -> steering wheel frame: x_m + CUP_X, z_t -> y, y -> -z."""
  return m.rotate((-90.0, 0.0, 0.0)).translate((CUP_X, COVER_Y - PLATE_T, CUP_Z))''',
'''def plate_to_wheel(m: Manifold) -> Manifold:
  """The plate's frame (x towards the door, y towards the dash, z up off the cover side, the labels on top) -> the
  steering wheel frame: X = CUP_X - x, Y = COVER_Y - z (the labels face down), Z = CUP_Z - y. A rotation, no mirror:
  printed labels up, the plate goes on the car labels down."""
  return m.transform([[-1.0, 0.0, 0.0, CUP_X], [0.0, 0.0, -1.0, COVER_Y], [0.0, -1.0, 0.0, CUP_Z]])''')
s=s.replace('''  body = body + tube
  body = body.mirror((1.0, 0.0, 0.0))                                    # printed: key side +x, labels up
  labels = [FR.text("KEY >", -BLOCK[0] + 2.0, BLOCK[3] - 8.0, T), FR.text("WHEEL", -8.0, BLOCK[2] + 3.0, T, pix=0.9),
            FR.text("1", -xc - FR.text_width("1", 0.9) / 2, LEG[2] + 3.0, T, pix=0.9)]
  return clean(body + union(labels))''','''  body = body + tube
  # labels on the top (in the car, the underside): read from below with the dash at the top, the key side is on the left
  FR.FONT.setdefault("<", ("010", "100", "111", "100", "010"))
  labels = [FR.text("< KEY", BORE_X[1] + 6.0, BLOCK[3] - 8.0, T), FR.text("WHEEL", -8.0, BLOCK[2] + 3.0, T, pix=0.9),
            FR.text("1", xc - FR.text_width("1", 0.9) / 2, LEG[2] + 3.0, T, pix=0.9)]
  return clean(body + union(labels))''')
# the drawing: a real view from below (the wheel at the top, the key side on the right)
s=s.replace('''  ax.set_xlim(125, -60)
  ax.set_ylim(-62, 78)
  ax.set_xlabel("across the car, mm (0 = cup screw; the key side to the right)")
  ax.set_ylabel("along the column, mm (0 = cup screw; the wheel is down)")
  ax.set_title("Frame plate v3 seen from below, as in the photos (print labels up; in the car the labels face down).\\n"''',
'''  ax.set_xlim(125, -60)
  ax.set_ylim(78, -62)
  ax.set_xlabel("across the car, mm (0 = cup screw; the key side to the right)")
  ax.set_ylabel("along the column, mm (0 = cup screw; the wheel is up)")
  ax.set_title("Frame plate v3 seen from below, as in your photos: the wheel at the top, the key side on the right.\\n"''')
s=s.replace('''  ax.text(-30, 56, "receiver: the arm\\nslides in from\\nthe wheel end", ha="center", va="bottom", fontsize=7, color="#444")''',
'''  ax.text(-30, 58, "receiver: the arm\\nslides in from\\nthe wheel end", ha="center", va="top", fontsize=7, color="#444")''')
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 armmount.py 2>&1 | tail -5 && PYTHONPATH=/home/claude/pylib timeout 600 python3 - <<'EOF'
import sys; sys.path.insert(0,'.')
import armmount as A, midteeth as MT, numpy as np
mg=A.motor_and_gear()
plate=A.plate_to_wheel(A.frame_plate_v3())
parts={"plate":plate,"arm":A.arm(),"bracket":A.bracket(),"motor":mg["motor"],"board":mg["board"],"gear":mg["gear"]}
teeth=MT.mid_teeth(MT.MidTeeth(n_teeth=10)).rotate((0,0,A.MOUNT_DEG))
names=list(parts); bad=False
for i in range(len(names)):
    for j in range(i+1,len(names)):
        v=(parts[names[i]]^parts[names[j]]).volume()
        if v>0.01: print(f"  {names[i]} x {names[j]}: {v:.1f}"); bad=True
for a in range(-25,26,5):
    tp=teeth.rotate((0,0,a))
    for n in ("arm","bracket","plate","motor","board"):
        v=(tp^parts[n]).volume()
        if v>0.01: print(f"  teeth at {a} deg x {n}: {v:.1f} mm3"); bad=True
print("overlaps:", "some" if bad else "none")
print("plate pieces:", len(A.frame_plate_v3().decompose()))
bb=plate.bounding_box(); print("plate wheel-frame bb", [round(v,1) for v in bb])
# the arm inside the bore: the arm's x,y range must be inside the bore's
import math
print("bore X", round(A.CUP_X-A.BORE_X[1],1), round(A.CUP_X-A.BORE_X[0],1), " arm X", A.ARM_X, " bore Y", round(A.COVER_Y-A.PLATE_T-A.BORE_DEPTH,1), round(A.COVER_Y-A.PLATE_T,1), " arm Y", [round(v,1) for v in A.ARM_Y])
EOF