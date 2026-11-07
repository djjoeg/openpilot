python3 - <<'EOF'
p='mountparts.py'; s=open(p).read()
old='''def hinge_block() -> Manifold:
  hy, hz = HINGE
  py, pz = PIVOT
  body = box(-HB_HALF, HB_HALF, HB_BOTTOM, HB_TOP, HB_BODY_BACK, HB_FRONT)'''
new='''def hinge_block(arm_nominal: float = ARM_NOMINAL) -> Manifold:
  """arm_nominal: the arm's angle to the steering column in the middle of the joint's range (ARM_NOMINAL for the dash
  mount; the column mount's arm runs closer to the column, so its hinge block has the slot centred lower)."""
  hy, hz = HINGE
  py, pz = PIVOT
  body = box(-HB_HALF, HB_HALF, HB_BOTTOM, HB_TOP, HB_BODY_BACK, HB_FRONT)'''
assert old in s; s=s.replace(old,new)
old='''  slot_pts = [np.array([py, pz]) + LOCK_R * arm_direction(a)
              for a in np.linspace(ARM_NOMINAL - LOCK_RANGE, ARM_NOMINAL + LOCK_RANGE, 15)]'''
new='''  slot_pts = [np.array([py, pz]) + LOCK_R * arm_direction(a)
              for a in np.linspace(arm_nominal - LOCK_RANGE, arm_nominal + LOCK_RANGE, 15)]'''
assert old in s; s=s.replace(old,new)
old='''  part = part - union([cyl_x(M5_CLEAR / 2, -60, 60, y=float(q[0]), z=float(q[1]), segments=20)
                       for q in [np.array([py, pz]) + LOCK_R * arm_direction(a)
                                 for a in np.linspace(ARM_NOMINAL - LOCK_RANGE, ARM_NOMINAL + LOCK_RANGE, 71)]])'''
new='''  part = part - union([cyl_x(M5_CLEAR / 2, -60, 60, y=float(q[0]), z=float(q[1]), segments=20)
                       for q in [np.array([py, pz]) + LOCK_R * arm_direction(a)
                                 for a in np.linspace(arm_nominal - LOCK_RANGE, arm_nominal + LOCK_RANGE, 71)]])'''
assert old in s; s=s.replace(old,new)
open(p,'w').write(s)

p='columnparts.py'; s=open(p).read()
old=s[s.index("SADDLE_HALF_X = 92.0"):s.index("def saddle_v_cut")]
new='''SADDLE_HALF_X = 92.0          # the saddles reach this far each side (the rod slots are near the ends)
SADDLE_LEN = 50.0             # along the column
V_DEG = 20.0                  # the V's faces rise this much from flat, away from the middle
V_HALF_X = 35.0               # the V runs this far each side of the middle
SADDLE_T = 6.0                # plastic under the V's middle
EAR_T = 10.0                  # the ears with the rod slots
ROD_SLOT_X = (COVER_W_RANGE[0] / 2 + 10.0 - M6_CLEAR / 2, COVER_W_RANGE[1] / 2 + 10.0 + M6_CLEAR / 2)  # rods 10 mm clear of the covers
ROD_Z = (-18.0, 18.0)
PAD_T = 4.0                   # rubber strip on each V face (self-adhesive, 20 mm wide; squashed a little)
V_DEPTH = V_HALF_X * math.tan(math.radians(V_DEG))      # the V's faces end this far above its middle
SADDLE_BOTTOM = -SADDLE_T                                # the lower saddle's underside (its frame: V middle at y = 0, +y up)
NECK = 22.0                   # the arm's bolt this far below the saddle's underside: room for the arm's end past the
                              # bolt (the slot end) at the steepest the arm gets
PIVOT_C = (SADDLE_BOTTOM - NECK, 0.0)                    # the arm's bolt (y, z) in the lower saddle's frame
SIDE_PLATE_X = MP.SIDE_PLATE_X
ARM_ANGLES = (0.0, 60.0)      # the arm can point from along the column (towards you) to 60 degrees below it
ARM_NOMINAL_C = 20.0          # the column mount's hinge block has its slot centred on the arm at this angle to the column
ROD_LEN = 200.0               # M6 threaded rod, four pieces this long (cut shorter to suit: the report says how much is used)


'''
s=s.replace(old,new)
old=s[s.index("def saddle_v_cut"):s.index("def rod_slots")]
new='''def saddle_v_cut(length: float, extra: float = 1.0) -> Manifold:
  """The V the covers sit in: a trough along z, its middle on the x axis, faces rising away from it (lower saddle
  frame). Everything above the V is cut away."""
  t = math.tan(math.radians(V_DEG))
  w = V_HALF_X + extra
  pts = [(-w, w * t), (0.0, 0.0), (w, w * t), (w, 80.0), (-w, 80.0)]
  cs = CrossSection([pts])
  if cs.area() < 0:
    cs = CrossSection([pts[::-1]])
  return cs.extrude(length + 2).translate((0, 0, -length / 2 - 1))


def saddle_block() -> Manifold:
  """A saddle without its V or slots (lower saddle frame): a block from SADDLE_BOTTOM up to the V's rim between the
  V's ends, and ears EAR_T thick out to SADDLE_HALF_X."""
  body = box(-V_HALF_X, V_HALF_X, SADDLE_BOTTOM, V_DEPTH, -SADDLE_LEN / 2, SADDLE_LEN / 2)
  ears = box(-SADDLE_HALF_X, SADDLE_HALF_X, SADDLE_BOTTOM, SADDLE_BOTTOM + EAR_T, -SADDLE_LEN / 2, SADDLE_LEN / 2)
  return body + ears


'''
s=s.replace(old,new)
s=s.replace('''def rod_slots() -> Manifold:
  slots = []
  for sx in (-1, 1):
    for z in ROD_Z:
      x0, x1 = sorted((sx * ROD_SLOT_X[0], sx * ROD_SLOT_X[1]))
      slots.append(Manifold.batch_hull([cyl_y(M6_CLEAR / 2, SADDLE_BOTTOM - 1, 1.0, x=x0 + M6_CLEAR / 2, z=z, segments=32),
                                        cyl_y(M6_CLEAR / 2, SADDLE_BOTTOM - 1, 1.0, x=x1 - M6_CLEAR / 2, z=z, segments=32)]))
  return union(slots)''','''def rod_slots() -> Manifold:
  slots = []
  for sx in (-1, 1):
    for z in ROD_Z:
      x0, x1 = sorted((sx * ROD_SLOT_X[0], sx * ROD_SLOT_X[1]))
      slots.append(Manifold.batch_hull([cyl_y(M6_CLEAR / 2, SADDLE_BOTTOM - 1, V_DEPTH + 1.0, x=x0 + M6_CLEAR / 2, z=z, segments=32),
                                        cyl_y(M6_CLEAR / 2, SADDLE_BOTTOM - 1, V_DEPTH + 1.0, x=x1 - M6_CLEAR / 2, z=z, segments=32)]))
  return union(slots)''')
# pads: on the V faces (rising)
old=s[s.index("def pads"):s.index("def clamp_fastener_rows")]
new='''def pads() -> Manifold:
  """Where the rubber strips sit on the lower saddle's V faces (lower saddle frame)."""
  t = math.tan(math.radians(V_DEG))
  out = []
  for sgn in (-1, 1):
    pts = [(0.0, 0.0), (sgn * V_HALF_X, V_HALF_X * t), (sgn * V_HALF_X, V_HALF_X * t + PAD_T), (0.0, PAD_T)]
    cs = CrossSection([pts])
    if cs.area() < 0:
      cs = CrossSection([pts[::-1]])
    out.append(cs.extrude(SADDLE_LEN - 4.0).translate((0, 0, -SADDLE_LEN / 2 + 2.0)))
  return union(out)


'''
s=s.replace(old,new)
s=s.replace('''  stack = lambda h: h + 2 * PAD_T + 2 * (-SADDLE_BOTTOM)   # noqa: E731  from the lower saddle's underside to the upper's top''',
            '''  stack = lambda h: h + 2 * PAD_T + 2 * (-SADDLE_BOTTOM)   # noqa: E731  from the lower saddle's underside to the upper's top
  # (the saddles' V middles sit about 9 mm outside the covers' top and bottom; close enough for the rods)''')
open(p,'w').write(s)

p='columnassembly.py'; s=open(p).read()
s=s.replace('''  y_pad = -x_c * tv + CP.PAD_T / math.cos(math.radians(CP.V_DEG))
  return y_c - y_pad''','''  y_pad = x_c * tv + CP.PAD_T / math.cos(math.radians(CP.V_DEG))     # the pad's surface above the V's middle at x_c
  return y_c - y_pad''')
s=s.replace('''  if abs(arm - MP.ARM_NOMINAL) > MP.LOCK_RANGE - 0.5:
    notes.append(f"arm at {arm:.1f} degrees to the steering column; the hinge block's joint covers "
                 f"{MP.ARM_NOMINAL - MP.LOCK_RANGE:.0f} to {MP.ARM_NOMINAL + MP.LOCK_RANGE:.0f}")''',
'''  if abs(arm - CP.ARM_NOMINAL_C) > MP.LOCK_RANGE - 0.5:
    notes.append(f"arm at {arm:.1f} degrees to the steering column; the hinge block's joint covers "
                 f"{CP.ARM_NOMINAL_C - MP.LOCK_RANGE:.0f} to {CP.ARM_NOMINAL_C + MP.LOCK_RANGE:.0f}")''')
open(p,'w').write(s); print("ok")
EOF
cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='params.py'; s=open(p).read()
s=s.replace("Z_MOTOR_FACE_C = -82.0     # the motor's front face, behind the middle of the grip: the lift lever's handle (47 mm\n                           # long, from the motor's face towards you) then ends 5 mm behind SPOKE_BACK_Z",
            "Z_MOTOR_FACE_C = -84.0     # the motor's front face, behind the middle of the grip: the lift lever's handle (47 mm\n                           # long, from the motor's face towards you) then ends 7 mm behind SPOKE_BACK_Z")
s=s.replace("CLAMP_Z = -170.0           # the middle of the clamp along the column, behind the middle of the grip: you choose where\n                           # (behind the stalks and the key); the report says which places work",
            "CLAMP_Z = -200.0           # the middle of the clamp along the column, behind the middle of the grip: you choose where\n                           # (behind the stalks and the key); the report says which places work")
open(p,'w').write(s); print("params ok")
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import time, json
t0=time.time()
import params as P, columnparts as CP, columnassembly as CA, mountparts as MP, wheelparts as WP
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP)
fit = CA.solve()
print("fit:", fit.ok, "arm_deg", round(fit.arm_deg,1), "reach", round(fit.reach,1), "arm", fit.arm_len, "slide", round(fit.slide,1), fit.notes, "saddle_y", round(CA.saddle_y(),1), "pivot", fit.pivot_w)
parts = {"teeth": CP.ring_teeth(t), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
         "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(CP.ARM_NOMINAL_C), "bracket": MP.lever_bracket(), "lever": MP.lift_lever(),
         "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(), "clamp_lower": CP.column_clamp_lower(),
         "clamp_upper": CP.column_clamp_upper()}
for k in ("clamp_lower","clamp_upper","hinge_block"):
  print(k, len(parts[k].decompose()), parts[k].status(), [round(v,1) for v in parts[k].bounding_box()])
A = CA.ColumnAssembly(t, fit, parts)
res = CA.check_all(A, lever_step=8.0)
bad = {k: round(v,2) for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)}
print(len(res), "checks;", len(bad), "bad:"); print(json.dumps(bad, indent=1))
print("margins:", CA.margins(A))
for cz in (-160, -180, -200, -240, -280, -320, -360):
  f = CA.solve(clamp_z=cz); print(cz, f.ok, round(f.arm_deg,1), round(f.reach,1), f.arm_len, f.notes)
print(round(time.time()-t0,1), "s")
EOF