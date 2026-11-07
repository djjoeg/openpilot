cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='columnparts.py'; s=open(p).read()
old='''  # the rolling band's ends: cut the skirt's inside away out to inner_radius_at(angle), over the skirt's depth
  zlo, zhi = RING_BACK_Z - 1.0, -t.base.wz_out + 0.01
  cut = polar_mask(lambda a: t.inner_radius_at(a - 270.0), a0 - 0.5, a1 + 0.5, zlo, zhi)
  cut = cut - cyl(t.r_roll - 0.3, zlo - 1, zhi + 1, segments=1440)
  body = body - cut'''
new='''  # the rolling band's ends: cut the skirt's inside away out to inner_radius_at(angle) over the rolling band's depth,
  # and in the teeth zone the root follows it, the root's distance outside the band kept, so the motor gear's tips
  # (which stand that far outside its roller) stay clear of the ring as the carrier drops along the lead-in
  zlo, zhi = RING_BACK_Z - 1.0, Z_TEETH_C[0]
  cut = polar_mask(lambda a: t.inner_radius_at(a - 270.0), a0 - 0.5, a1 + 0.5, zlo, zhi)
  cut = cut - cyl(t.r_roll - 0.3, zlo - 1, zhi + 1, segments=1440)
  body = body - cut
  step = t.r_root - t.r_roll
  zlo, zhi = Z_TEETH_C[0] - 0.01, -t.base.wz_out + 0.01
  cut = polar_mask(lambda a: min(t.inner_radius_at(a - 270.0) + step, t.r_out - 1.5), a0 - 0.5, a1 + 0.5, zlo, zhi)
  cut = cut - cyl(t.r_root - 0.01, zlo - 1, zhi + 1, segments=1440)
  body = body - cut'''
assert old in s; s=s.replace(old,new); open(p,'w').write(s)

p='columnassembly.py'; s=open(p).read()
old='''  res["ring turned through its arc: teeth/gear (worst)"] = worst_gear
  res["ring turned through its arc: teeth/carrier (worst)"] = worst_carrier
  return res'''
new='''  res["ring turned through its arc: teeth/gear (worst)"] = worst_gear
  res["ring turned through its arc: teeth/carrier (worst)"] = worst_carrier
  # past the rolling band the roller follows the lead-in outwards and the carrier drops with it (up to DROP_DEG, the
  # lever's rounded end on the hinge block): the gear's teeth and the carrier must clear the ring all along it, and
  # at the ring's end with the carrier fully dropped
  worst = 0.0
  for w in np.arange(A.t.roll_half, A.t.half + 1.0, 0.5):
    drop = roller_drop_deg(A, float(w))
    for part in (A.gear(-drop), A.carrier(-drop)):
      for sign in (1, -1):
        worst = max(worst, overlap(A.teeth(sign * float(w)), part))
  res["ring's lead-in with the carrier dropping: teeth/gear and teeth/carrier (worst)"] = worst
  return res


def roller_drop_deg(A: ColumnAssembly, wheel_deg: float) -> float:
  """How far (degrees about the hinge) the carrier drops with the ring turned wheel_deg, the roller following the
  lead-in outwards until the lever's rounded end stops it at DROP_DEG."""
  want = A.t.inner_radius_at(wheel_deg) - A.t.r_roll        # how far out the rolling surface is there
  if want <= 0.0:
    return 0.0
  ry = -ROLLER_R_ - MP.HINGE[0]                              # the roller's contact line from the hinge (carrier frame)
  rz = (Z_GEAR_ROLLER_[0] + Z_GEAR_ROLLER_[1]) / 2 - Z_MOTOR_FACE_ - MP.HINGE[1]
  lo, hi = 0.0, MP.DROP_DEG
  for _ in range(30):
    mid = (lo + hi) / 2
    d = math.radians(mid)
    moved = -(ry * (math.cos(d) - 1) - rz * math.sin(d))      # how far out the roller has moved
    if moved < want:
      lo = mid
    else:
      hi = mid
  return hi'''
assert old in s; s=s.replace(old,new)
old='''from params import (ARM_LENGTHS, ARM_SLIDE, CLAMP_Z, COVER_FRONT_Z, COVER_H, COVER_W, DASH_Z, GRIP, HUB_BACK_Z, HUB_R,
                    SPOKE_BACK_Z, WHEEL_OD, WINDOW_DEG, Z_MOTOR_FACE_C)'''
new='''from params import (ARM_LENGTHS, ARM_SLIDE, CLAMP_Z, COVER_FRONT_Z, COVER_H, COVER_W, DASH_Z, GRIP, HUB_BACK_Z, HUB_R,
                    ROLLER_R, SPOKE_BACK_Z, WHEEL_OD, WINDOW_DEG, Z_GEAR_ROLLER, Z_MOTOR_FACE, Z_MOTOR_FACE_C)

ROLLER_R_, Z_GEAR_ROLLER_, Z_MOTOR_FACE_ = ROLLER_R, Z_GEAR_ROLLER, Z_MOTOR_FACE'''
assert old in s; s=s.replace(old,new)
open(p,'w').write(s); print("ok")
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import time, json
t0=time.time()
import params as P, columnparts as CP, columnassembly as CA, mountparts as MP, wheelparts as WP
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP)
fit = CA.solve()
parts = {"teeth": CP.ring_teeth(t), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
         "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(CP.ARM_NOMINAL_C), "bracket": MP.lever_bracket(), "lever": MP.lift_lever(),
         "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(), "clamp_lower": CP.column_clamp_lower(),
         "clamp_upper": CP.column_clamp_upper()}
print("ring", len(parts["teeth"].decompose()), parts["teeth"].status(), round(parts["teeth"].volume()/1000,1))
A = CA.ColumnAssembly(t, fit, parts)
res = CA.check_all(A, lever_step=4.0)
bad = {k: round(v,3) for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)}
print(len(res), "checks;", len(bad), "bad:", bad)
for w in (21.1, 23, 25, 27, 28):
  print("w", w, "drop", round(CA.roller_drop_deg(A, w),2), "inner r", round(t.inner_radius_at(w),2))
print(round(time.time()-t0,1), "s")
EOF