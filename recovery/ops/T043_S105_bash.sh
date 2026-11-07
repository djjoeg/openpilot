python3 - <<'EOF'
import re
s = open('assembly.py').read()
s = s.replace('''Puts the parts where they sit in the car and checks they fit: the motor gear on the steering wheel teeth, the motor
carrier and finger guard clear of the steering wheel, the hinge block over the carrier, the arm reaching from the dash
clamp to the hinge block with both angle joints within their range, the lift lever turning freely, and the motor gear
lifted clear of the teeth when the lift lever is up. With the steering wheel turned past the teeth, the carrier drops
until the roller rests on the steering wheel or the fin meets the cam, and nothing else touches.''',
'''Puts the parts where they sit in the car and checks they fit: the motor gear on the steering wheel teeth, the motor
carrier and finger guard clear of the steering wheel, the hinge block over the carrier with the lever bracket's legs
through it, the arm reaching from the dash clamp to the hinge block with both angle joints within their range, the
lift lever turning freely, its click working, and the motor gear lifted clear of the teeth when the lift lever is up.
With the steering wheel turned past the teeth, the carrier drops until the roller rests on the steering wheel or the
lift lever's rounded end meets the hinge block, and nothing else touches.''')

s = s.replace('''  def hinge_block(self):
    return self.p["hinge_block"].translate(tuple(self.b_org))

  def lever(self, alpha: float = 0.0):
    """Lift lever lifted alpha degrees from down (MP.A_OFF is 'up')."""
    return MP.lever_in_block(self.p["lever"], alpha).translate(tuple(self.b_org))

  def switch(self):
    return MP.place_yz(MP.switch_body(), MP.LEVER_ON, *MP.LEVER_PIVOT).translate(tuple(self.b_org))
''', '''  def hinge_block(self):
    return self.p["hinge_block"].translate(tuple(self.b_org))

  def bracket(self, lift=0.0):
    return self._carried(self.p["bracket"], lift)

  def lever(self, alpha: float = 0.0, lift: float | None = None, part: str = "lever"):
    """Lift lever lifted alpha degrees from down (MP.A_OFF is 'up'), on the lever bracket, with the carrier at lift
    (by default the lift its rounded end holds, and never below the motor gear on the teeth)."""
    if lift is None:
      lift = max(0.0, MP.cam_lift(alpha))
    return self._carried(MP.lever_in_carrier(self.p[part], alpha), lift)

  def switch(self, lift=0.0):
    return self._carried(MP.switch_body(), lift)
''')

# check_all
old_start = s.index('def check_all(')
s = s[:old_start] + '''def check_all(A: "Assembly", wheel_turn: float = 70.0, lever_step: float = 4.0) -> dict:
  """Overlap volumes (mm^3) between parts that must not touch, in these states: lift lever down with the motor gear on
  the teeth; lift lever up (carrier at the lift its rounded end gives); the lever at every angle from down to up;
  steering wheel turned wheel_turn degrees with the carrier dropped as far as it goes. Keys ending "(should touch)" hold
  minus the overlap, so they must be negative: the click's tab must meet its ridge, the lever's heel must stop it."""
  res = {}
  T, W = A.teeth(), A.wheel_grip()
  G, C, M = A.gear(), A.carrier(), A.motor()
  HB, AR, CL, BR, SW = A.hinge_block(), A.arm(), A.clamp(), A.bracket(), A.switch()
  LV = A.lever(0.0, 0.0)
  hood = A.hood()
  pairs = {
    "teeth/gear": (T, G), "teeth/carrier": (T, C), "teeth/motor": (T, M), "grip/carrier": (W, C), "grip/motor": (W, M),
    "carrier/motor": (C, M), "carrier/hinge block": (C, HB), "motor/hinge block": (M, HB), "carrier/lever": (C, LV),
    "lever/hinge block": (LV, HB), "lever/lever bracket": (LV, BR), "lever bracket/hinge block": (BR, HB),
    "lever bracket/carrier": (BR, C), "lever bracket/motor": (BR, M), "lever bracket/teeth": (BR, T),
    "switch/lever": (SW, LV), "switch/hinge block": (SW, HB), "switch/carrier": (SW, C), "hinge block/arm": (HB, AR),
    "arm/carrier": (AR, C), "arm/motor": (AR, M), "arm/clamp": (AR, CL), "clamp/hood": (CL, hood), "arm/hood": (AR, hood),
    "arm/teeth": (AR, T), "hinge block/teeth": (HB, T), "lever/arm": (LV, AR), "lever bracket/arm": (BR, AR),
    "switch/arm": (SW, AR),
  }
  for k, (a, b) in pairs.items():
    res["down: " + k] = overlap(a, b)
  # lift lever up: the rounded end rests on the hinge block's top (checked a hair higher, leaving room for the contact)
  lift = max(0.0, MP.cam_lift(MP.A_OFF))
  hair = lift + 0.05
  Gl, Cl, Ml, BRl, SWl = A.gear(lift), A.carrier(hair), A.motor(hair), A.bracket(hair), A.switch(hair)
  LVo = A.lever(MP.A_OFF, hair)
  tag = f"lever up (lift {lift:.1f} deg): "
  for k, (a, b) in {"teeth/gear": (T, Gl), "carrier/hinge block": (Cl, HB), "motor/hinge block": (Ml, HB),
                    "carrier/arm": (Cl, AR), "motor/arm": (Ml, AR), "lever bracket/hinge block": (BRl, HB),
                    "lever bracket/arm": (BRl, AR), "switch/hinge block": (SWl, HB), "lever/hinge block": (LVo, HB),
                    "lever/arm": (LVo, AR), "lever/clamp": (LVo, CL), "lever/lever bracket": (LVo, BRl),
                    "lever/carrier": (LVo, Cl)}.items():
    res[tag + k] = overlap(a, b)
  # every lever angle up to up: the lever (without the click's tab, which bends past its ridge) clears the bracket,
  # the hinge block and the arm; the carrier and bracket, at the lift the rounded end gives (a hair higher), clear
  # everything fixed
  for alpha in list(np.arange(lever_step, MP.A_OFF - 0.5, lever_step)) + [MP.A_OFF - 0.5]:
    th = max(0.0, MP.cam_lift(alpha)) + 0.05
    lv = A.lever(alpha, th, part="lever_no_tab")
    br, ca = A.bracket(th), A.carrier(th)
    for k, (a, b) in {"lever/hinge block": (lv, HB), "lever/arm": (lv, AR), "lever/lever bracket": (lv, br),
                      "lever/carrier": (lv, ca), "carrier/hinge block": (ca, HB), "carrier/arm": (ca, AR),
                      "lever bracket/hinge block": (br, HB), "lever bracket/arm": (br, AR)}.items():
      key = "lever swept: " + k
      res[key] = max(res.get(key, 0.0), overlap(a, b))
  # the click: lever down, the tab's hook sits just under its ridge; a degree or two up, it must meet it
  tab = A.lever(0.0, 0.0, part="tab")
  res["click: tab clear of the bracket, lever down"] = overlap(tab, BR)
  res["click: tab meets its ridge lifting (should touch)"] = -max(overlap(A.lever(a, 0.0, part="tab"), BR) for a in (0.75, 1.25, 1.75))
  # the heel stops the lever: a few degrees past up, the rounded end would be pushed into the hinge block's top
  res["lever stops past up (should touch)"] = -overlap(A.lever(MP.A_OFF + 4.0, hair), HB)
  # steering wheel turned past the teeth: roller rests on the steering wheel, or the rounded end meets the hinge block
  Tt = A.teeth(wheel_turn)
  rest = A.rest_on_grip_lift()
  Gr, Cr, Mr, BRr, SWr = A.gear(rest), A.carrier(rest), A.motor(rest), A.bracket(rest), A.switch(rest)
  teeth_only = turn_about_x(A.p["gear_teeth_only"].translate(tuple(A.b_org)), -rest, A.hinge_w)
  Ld = A.lever(0.0, -MP.DROP_DEG + 0.1)
  for k, (a, b) in {"grip/gear teeth": (W, teeth_only), "grip/carrier": (W, Cr), "grip/motor": (W, Mr),
                    "turned teeth/carrier": (Tt, Cr), "turned teeth/gear": (Tt, Gr), "turned teeth/lever bracket": (Tt, BRr),
                    "carrier/hinge block": (Cr, HB), "motor/hinge block": (Mr, HB), "lever bracket/hinge block": (BRr, HB),
                    "switch/hinge block": (SWr, HB), "carrier/arm": (Cr, AR), "lever bracket/arm": (BRr, AR),
                    "carrier fully dropped, lever/hinge block": (Ld, HB)}.items():
    res[f"wheel turned {wheel_turn:.0f}, carrier down {-rest:.1f} deg: " + k] = overlap(a, b)
  return res
'''
open('assembly.py', 'w').write(s)
EOF
grep -n "lever_in_block\|LEVER_ON\|place_yz" assembly.py