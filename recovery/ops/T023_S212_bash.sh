python3 - << 'EOF'
import re
p = "assembly.py"
s = open(p).read()

s = s.replace('''  if abs(joint) > MP.LOCK_RANGE - 1.0:
    notes.append(f"hinge block angle {joint:.1f} degrees, beyond +-{MP.LOCK_RANGE - 1:.0f}")''',
'''  if abs(arm - MP.ARM_NOMINAL) > MP.LOCK_RANGE - 1.0:
    notes.append(f"arm at {arm:.1f} degrees to the steering column; the angle joint covers {MP.ARM_NOMINAL - MP.LOCK_RANGE + 1:.0f}"
                 f" to {MP.ARM_NOMINAL + MP.LOCK_RANGE - 1:.0f}")''')

s = s.replace('''  def lever(self, off: bool = False):
    lv = self.p["lever"]
    if off:
      lv = lv.rotate((MP.LEVER_OFF_DEG, 0, 0))
    ly, lz = MP.LEVER_PIVOT
    return lv.translate((0.0, self.b_org[1] + ly, self.b_org[2] + lz))''',
'''  def lever(self, alpha: float = 0.0):
    """Lift lever turned up alpha degrees from lying flat (MP.A_OFF is 'up')."""
    lv = self.p["lever"]
    if alpha:
      lv = lv.rotate((alpha, 0, 0))
    ly, lz = MP.LEVER_PIVOT
    return lv.translate((0.0, self.b_org[1] + ly, self.b_org[2] + lz))

  def switch(self):
    return MP.switch_body().translate(tuple(self.b_org))''')

# check_all rewrite
start = s.index("def check_all(")
s = s[:start] + '''def check_all(A: "Assembly", wheel_turn: float = 70.0, lever_step: float = 5.0) -> dict:
  """Overlap volumes (mm^3) between parts that must not touch, in these states: lift lever down with the motor gear on
  the teeth; lift lever up (carrier at the lift the cam gives); lift lever at every angle in between; steering wheel
  turned wheel_turn degrees with the carrier dropped until the roller rests on the steering wheel or the fin meets the
  cam."""
  res = {}
  T, W = A.teeth(), A.wheel_grip()
  G, C, M = A.gear(), A.carrier(), A.motor()
  HB, S, AR, CL, LV, SW = A.hinge_block(), A.slider(), A.arm(), A.clamp(), A.lever(), A.switch()
  hood = A.hood()
  pairs = {
    "teeth/gear": (T, G), "teeth/carrier": (T, C), "teeth/motor": (T, M), "grip/carrier": (W, C), "grip/motor": (W, M),
    "carrier/motor": (C, M), "carrier/hinge block": (C, HB), "motor/hinge block": (M, HB), "carrier/lever": (C, LV),
    "lever/hinge block": (LV, HB), "carrier/switch": (C, SW), "motor/switch": (M, SW),
    "hinge block/slider": (HB, S), "hinge block/arm": (HB, AR), "slider/carrier": (S, C), "slider/motor": (S, M),
    "arm/carrier": (AR, C), "arm/motor": (AR, M), "arm/clamp": (AR, CL), "clamp/hood": (CL, hood),
    "arm/teeth": (AR, T), "slider/teeth": (S, T), "hinge block/teeth": (HB, T), "lever/slider": (LV, S), "lever/arm": (LV, AR),
  }
  for k, (a, b) in pairs.items():
    res["down: " + k] = overlap(a, b)
  # lift lever up
  lift = max(0.0, MP.cam_lift(MP.A_OFF))
  Gl, Cl, Ml, LVo = A.gear(lift), A.carrier(lift), A.motor(lift), A.lever(MP.A_OFF)
  tag = f"lever up (lift {lift:.1f} deg): "
  for k, (a, b) in {"teeth/gear": (T, Gl), "carrier/hinge block": (Cl, HB), "motor/hinge block": (Ml, HB),
                    "carrier/slider": (Cl, S), "motor/slider": (Ml, S), "carrier/arm": (Cl, AR), "motor/arm": (Ml, AR),
                    "carrier/switch": (Cl, SW), "lever/hinge block": (LVo, HB), "lever/slider": (LVo, S),
                    "lever/arm": (LVo, AR), "lever/clamp": (LVo, CL)}.items():
    res[tag + k] = overlap(a, b)
  # every lever angle: the lever clears the hinge block and the arm; the carrier (at the cam's lift, a hair lower to
  # leave room for the contact) clears everything fixed
  for alpha in np.arange(lever_step, MP.A_STOP + 1e-9, lever_step):
    lv = A.lever(alpha)
    th = max(0.0, MP.cam_lift(alpha)) + 0.05
    ca = A.carrier(th)
    for k, (a, b) in {"lever/hinge block": (lv, HB), "lever/arm": (lv, AR), "lever/slider": (lv, S),
                      "carrier/lever": (ca, lv), "carrier/hinge block": (ca, HB)}.items():
      v = overlap(a, b)
      key = "lever swept: " + k
      res[key] = max(res.get(key, 0.0), v)
  # steering wheel turned past the teeth: roller rests on the steering wheel, or the fin meets the cam
  Tt = A.teeth(wheel_turn)
  rest = A.rest_on_grip_lift()
  Gr, Cr, Mr = A.gear(rest), A.carrier(rest), A.motor(rest)
  teeth_only = turn_about_x(A.p["gear_teeth_only"].translate(tuple(A.b_org)), -rest, A.hinge_w)
  Cd = A.carrier(-MP.DROP_DEG + 0.1)
  for k, (a, b) in {"grip/gear teeth": (W, teeth_only), "grip/carrier": (W, Cr), "grip/motor": (W, Mr),
                    "turned teeth/carrier": (Tt, Cr), "turned teeth/gear": (Tt, Gr), "carrier/hinge block": (Cr, HB),
                    "motor/hinge block": (Mr, HB), "carrier/switch": (Cr, SW),
                    "carrier fully dropped/lever": (Cd, LV), "carrier fully dropped/hinge block": (Cd, HB)}.items():
    res[f"wheel turned {wheel_turn:.0f}, carrier down {-rest:.1f} deg: " + k] = overlap(a, b)
  return res
'''
s = s.replace("""  Carrier angle (negative = gear lowered) with the steering wheel turned past the teeth: the roller rests on the
    bare steering wheel, or the tail meets the lift lever's cam first (DROP_DEG), whichever comes first.""",
"""  Carrier angle (negative = gear lowered) with the steering wheel turned past the teeth: the roller rests on the
    bare steering wheel, or the fin meets the lift lever's cam first (DROP_DEG), whichever comes first.""")
open(p, "w").write(s)
EOF
grep -n "Carrier angle\|def rest_on\|tail meets" assembly.py