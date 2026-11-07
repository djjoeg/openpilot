import sys, time, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import faceparts as FP
import mountparts as MP
from cadlib import size_of, write_stl, on_bed

t = FP.FaceTeeth()
print("rr", t.rr, "z_root", t.z_root, "z_p", t.z_p, "z_tip", t.z_tip, "z_axis", round(t.z_axis, 3), "z_band", round(t.z_band, 3),
      "z_flat", round(t.z_flat, 3))
print("teeth_half", round(t.teeth_half, 3), "roll_half", round(t.roll_half, 3), "lead_end", round(t.lead_end, 3), "half", round(t.half, 3),
      "tracked", round(t.tracked_arc_deg, 2), "joint", round(t.joint_deg, 3), "spoke", t.spoke)
print("R_FACE", FP.R_FACE, "ROLL_BAND", FP.ROLL_BAND, "ROLLER_R_F", round(FP.ROLLER_R_F, 4), "CUT_SPAN", FP.CUT_SPAN)
print("tie angles", [round(a, 2) for a in FP.tie_angles(t)])
T0 = time.time()
whole = FP.face_solid(t)
print("face solid", round(time.time() - T0, 1), "s; volume", round(whole.volume()), "pieces", len(whole.decompose()), "bbox",
      [round(v, 1) for v in whole.bounding_box()])
T0 = time.time()
pcs = FP.face_pieces(t, whole)
for k, m in pcs.items():
  b = on_bed(m, (180, 0, 0))
  print(k, "vol", round(m.volume()), "parts", len(m.decompose()), "bed size", [round(v, 1) for v in size_of(b)], round(time.time() - T0, 1))
ft = FP.face_fit_tests(t, whole)
for k, m in ft.items():
  print("fit", k, round(m.volume()), len(m.decompose()), [round(v, 1) for v in size_of(m)])
g = FP.face_motor_gear()
print("gear", round(g.volume()), len(g.decompose()), [round(v, 1) for v in size_of(g)])
c = FP.face_carrier()
print("carrier", round(c.volume()), len(c.decompose()))
hb = FP.face_hinge_block(t)
print("hinge block", round(hb.volume()), len(hb.decompose()), [round(v, 1) for v in hb.bounding_box()])
for L in FP.ARM_LENGTHS_F:
  a = FP.face_arm(L)
  print("arm", L, round(a.volume()), len(a.decompose()))
p = FP.column_plate(t)
print("plate", round(p.volume()), len(p.decompose()), [round(v, 1) for v in p.bounding_box()])
import os
os.makedirs("out", exist_ok=True)
for k, m in pcs.items():
  write_stl(on_bed(m, (180, 0, 0)), f"out/back-teeth-{k}.stl")
write_stl(g, "out/gear.stl"); write_stl(hb, "out/hb.stl"); write_stl(p, "out/plate.stl"); write_stl(c, "out/carrier.stl")
