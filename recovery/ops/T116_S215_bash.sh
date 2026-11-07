cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && cat > reparts.py <<'EOF'
import sys, os, hashlib, time
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import params as P
import faceparts as FP
import accord_lka_parts as A
from cadlib import on_bed, write_stl
T0 = time.time()
t = FP.FaceTeeth(P.WHEEL_OD, P.GRIP, P.RIGHT_SPOKE_DEG)
whole = FP.face_solid(t)
pieces = FP.face_pieces(t, whole)
tests = FP.face_fit_tests(t, whole)
bparts = A.back_part_list(t, pieces, tests)
print("built", round(time.time() - T0), "s")
os.makedirs("restl", exist_ok=True)
D = "/home/claude/deliver/hardware/stl/back-teeth-mount"
bad = 0
for name, (m, rot, how, sup) in bparts.items():
  placed = on_bed(m, rot)
  # the build turns some parts about z to fit the bed: same search as back_mount
  for zr in range(0, 91, 5):
    p2 = on_bed(placed, (0, 0, zr))
    x0, y0, z0, x1, y1, z1 = p2.bounding_box()
    if x1 - x0 <= P.BED[0] and y1 - y0 <= P.BED[1] and z1 - z0 <= P.BED[2]:
      break
  else:
    p2 = placed if "one-piece" in name else p2
  if "one-piece" in name:
    p2 = on_bed(placed, (0, 0, 0))
  out = f"restl/{name}.stl"
  write_stl(p2, out, name)
  same = hashlib.md5(open(out, "rb").read()).hexdigest() == hashlib.md5(open(f"{D}/{name}.stl", "rb").read()).hexdigest()
  bad += not same
  print(("same " if same else "DIFF ") + name)
A.back_parts_picture(bparts, "/home/claude/deliver/hardware/report", on_bed)
print("picture done; differing:", bad, round(time.time() - T0), "s")
EOF
PYTHONPATH=/home/claude/pylib python3 reparts.py 2>&1 | tail -20