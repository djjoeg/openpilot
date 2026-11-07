python3 - <<'EOF'
p='mountparts.py'; s=open(p).read()
old='''def motor_carrier() -> Manifold:
  t = MOTOR_PLATE_T'''
new='''def motor_carrier(guard_window: float = GUARD_WINDOW) -> Manifold:
  """guard_window: the finger guard is open this many degrees either side of straight down, where the gears meet
  (GUARD_WINDOW for the dash mount; the column mount's carrier opens a little wider, so the guard's rounded ends
  clear the ring's rolling band when the carrier drops at the ring's ends)."""
  t = MOTOR_PLATE_T'''
assert old in s; s=s.replace(old,new)
old='''  window = sector(GUARD_OUT + 6, 270.0 - GUARD_WINDOW, 270.0 + GUARD_WINDOW).extrude(GUARD_FRONT + 4).translate((0, 0, t - 2))
  guard = (shell + lip) - window
  for sgn in (-1, 1):   # rounded lower ends: a hand that meets the guard pushes it up instead of catching an edge
    a = math.radians(270.0 + sgn * GUARD_WINDOW)'''
new='''  window = sector(GUARD_OUT + 6, 270.0 - guard_window, 270.0 + guard_window).extrude(GUARD_FRONT + 4).translate((0, 0, t - 2))
  guard = (shell + lip) - window
  for sgn in (-1, 1):   # rounded lower ends: a hand that meets the guard pushes it up instead of catching an edge
    a = math.radians(270.0 + sgn * guard_window)'''
assert old in s; s=s.replace(old,new)
open(p,'w').write(s)

p='columnparts.py'; s=open(p).read()
old='''  step = t.r_root - t.r_roll
  zlo, zhi = Z_TEETH_C[0] - 0.01, -t.base.wz_out + 0.01'''
new='''  step = t.r_root - t.r_roll
  zlo, zhi = Z_TEETH_SPLIT, -t.base.wz_out + 0.01'''
assert old in s; s=s.replace(old,new)
old='''  zlo, zhi = RING_BACK_Z - 1.0, Z_TEETH_C[0]
  cut = polar_mask(lambda a: t.inner_radius_at(a - 270.0), a0 - 0.5, a1 + 0.5, zlo, zhi)'''
new='''  zlo, zhi = RING_BACK_Z - 1.0, Z_TEETH_SPLIT + 0.01
  cut = polar_mask(lambda a: t.inner_radius_at(a - 270.0), a0 - 0.5, a1 + 0.5, zlo, zhi)'''
assert old in s; s=s.replace(old,new)
old='''Z_ROLL_C = (RING_BACK_Z, Z_TEETH_C[0])     # the rolling band, behind the teeth
'''
new='''Z_ROLL_C = (RING_BACK_Z, Z_TEETH_C[0])     # the rolling band, behind the teeth
# Dropping (the carrier turned DROP_DEG about its hinge, the roller off the rolling band), the motor gear's teeth also
# move about 3 mm back along the column into the rolling band's zone; from here forward the ring's inside follows
# the lead-in at the teeth root's distance, so those teeth clear it
Z_TEETH_SPLIT = Z_GEAR_TEETH_C[0] - 3.2
GUARD_WINDOW_C = 64.0                       # the column mount's carrier: finger guard open this far either side of down
'''
assert old in s; s=s.replace(old,new)
open(p,'w').write(s)

p='columnassembly.py'; s=open(p).read()
old=s[s.index("def roller_drop_deg"):s.index("def reach_back")]
new='''def roller_drop_deg(A: ColumnAssembly, wheel_deg: float) -> float:
  """How far (degrees about the hinge) the carrier drops with the ring turned wheel_deg: until the roller rests on
  the ring's inside (the lead-in) or the lever's rounded end stops it at DROP_DEG."""
  zr0, zr1 = (z - Z_MOTOR_FACE_ for z in Z_GEAR_ROLLER_)
  roller = cyl(ROLLER_R_, zr0, zr1, segments=360)
  T = A.teeth(wheel_deg)
  if overlap(A._carried(roller, -MP.DROP_DEG), T) <= 1e-3:
    return MP.DROP_DEG
  lo, hi = 0.0, MP.DROP_DEG
  for _ in range(24):
    mid = (lo + hi) / 2
    if overlap(A._carried(roller, -mid), T) > 1e-3:
      hi = mid
    else:
      lo = mid
  return lo


'''
s=s.replace(old,new)
open(p,'w').write(s); print("ok")
EOF
cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='accord_lka_parts.py'; s=open(p).read()
old='''    "hinge-block-column": (MP.hinge_block(CP.ARM_NOMINAL_C), (180, 0, 0), "front end (the end towards you) down",
                           "tree supports, everywhere (small areas under the hinge, the spring's pocket and the ears)"),
  }'''
new='''    "hinge-block-column": (MP.hinge_block(CP.ARM_NOMINAL_C), (180, 0, 0), "front end (the end towards you) down",
                           "tree supports, everywhere (small areas under the hinge, the spring's pocket and the ears)"),
    "motor-carrier-column": (MP.motor_carrier(CP.GUARD_WINDOW_C), (180, 0, 0), "finger guard down",
                             "inside the finger guard only (supports touching the build plate only)"),
  }'''
assert old in s; s=s.replace(old,new)
old='''  cbase = dict(base, teeth=cparts["ring-teeth"][0], hinge_block=cparts["hinge-block-column"][0],
               clamp_lower=cparts["column-clamp-lower"][0], clamp_upper=cparts["column-clamp-upper"][0])'''
new='''  cbase = dict(base, teeth=cparts["ring-teeth"][0], hinge_block=cparts["hinge-block-column"][0],
               carrier=cparts["motor-carrier-column"][0],
               clamp_lower=cparts["column-clamp-lower"][0], clamp_upper=cparts["column-clamp-upper"][0])'''
assert old in s; s=s.replace(old,new)
s=s.replace('''  hinge block (column)  - the hinge block with its arm slot centred on an arm closer to the column
  fit test              - a few ring teeth to try the printed motor gear in
  The motor gear, carrier, lever bracket, lift lever, arm and setup gauge are the same parts.''',
'''  hinge block (column)  - the hinge block with its arm slot centred on an arm closer to the column
  motor carrier (column)- the carrier with its finger guard open a little wider towards the ring
  fit test              - a few ring teeth to try the printed motor gear in
  The motor gear, lever bracket, lift lever, arm and setup gauge are the same parts.''')
s=s.replace('''  L.append("PARTS (column-mount folder; the motor gear, carrier, lever bracket, lift lever, arm and setup gauge are shared)")''',
            '''  L.append("PARTS (column-mount folder; the motor gear, lever bracket, lift lever, arm and setup gauge are shared)")''')
open(p,'w').write(s); print("ok2")
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import time, json
t0=time.time()
import params as P, columnparts as CP, columnassembly as CA, mountparts as MP, wheelparts as WP
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP)
fit = CA.solve()
parts = {"teeth": CP.ring_teeth(t), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
         "carrier": MP.motor_carrier(CP.GUARD_WINDOW_C), "hinge_block": MP.hinge_block(CP.ARM_NOMINAL_C), "bracket": MP.lever_bracket(), "lever": MP.lift_lever(),
         "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(), "clamp_lower": CP.column_clamp_lower(),
         "clamp_upper": CP.column_clamp_upper()}
print("ring", len(parts["teeth"].decompose()), parts["teeth"].status(), "carrier", len(parts["carrier"].decompose()), parts["carrier"].status())
A = CA.ColumnAssembly(t, fit, parts)
res = CA.check_all(A, lever_step=4.0)
bad = {k: round(v,3) for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)}
print(len(res), "checks;", len(bad), "bad:", bad)
for w in (21.1, 23, 25, 27, 28, 29):
  print("w", w, "drop", round(CA.roller_drop_deg(A, w),2))
print("margins", CA.margins(A))
print(round(time.time()-t0,1), "s")
EOF