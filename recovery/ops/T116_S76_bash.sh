cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face/diag1.py <<'EOF'
import sys, time, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import faceparts as FP
import faceassembly as FA
import mountparts as MP

t = FP.FaceTeeth()
whole = FP.face_solid(t)
fit = FA.solve_face(t)
parts = {"teeth": whole, "gear": FP.face_motor_gear(), "gear_teeth_only": FP.face_motor_gear_teeth_only(),
         "carrier": FP.face_carrier(), "bracket": MP.lever_bracket(), "lever": MP.lift_lever(),
         "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(), "hinge_block": FP.face_hinge_block(t),
         "plate": FP.column_plate(t)}
A = FA.FaceAssembly(t, fit, parts)
pk = A.plate() ^ A.key()
print("plate/key overlap", round(pk.volume(), 2), [round(v, 1) for v in pk.bounding_box()] if pk.volume() > 0 else "")
print("plate/covers", round((A.plate() ^ A.covers()).volume(), 2), "pads/covers", round((A.plate_pads() ^ A.covers()).volume(), 2))
print("arm/key", round((A.arm() ^ A.key()).volume(), 2))
# lead-in collision
for w in np.arange(t.roll_half, t.half + 1.0, 0.5):
  for sign in (1, -1):
    drop = FA.roller_drop_deg(A, sign * float(w))
    g = A._carried(A.p["gear_teeth_only"].rotate((0, 0, FA.MESH_PHASE)), -drop)
    c = A.carrier(-drop)
    T = A.teeth(sign * float(w))
    og, oc = (T ^ g), (T ^ c)
    if og.volume() > 1e-3 or oc.volume() > 1e-3:
      print("lead-in", sign * w, "drop", round(drop, 2), "gear", round(og.volume(), 3), [round(v, 1) for v in og.bounding_box()] if og.volume() > 1e-3 else "",
            "carrier", round(oc.volume(), 3), [round(v, 1) for v in oc.bounding_box()] if oc.volume() > 1e-3 else "")
# lever swept gear/teeth
for alpha in list(np.arange(4.0, MP.A_OFF - 0.5, 4.0)) + [MP.A_OFF - 0.5]:
  th = max(0.0, MP.cam_lift(alpha)) + 0.05
  o = A.gear(th) ^ A.teeth()
  if o.volume() > 1e-4:
    print("lever", round(alpha, 1), "lift", round(th, 2), round(o.volume(), 4), [round(v, 2) for v in o.bounding_box()])
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && PYTHONPATH=/home/claude/pylib timeout 3000 python3 diag1.py 2>&1 | tail -40