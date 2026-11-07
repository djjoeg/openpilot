python3 - <<'EOF'
p = "assembly.py"
s = open(p).read()

old_imp = "from params import ARM_LENGTHS, ARM_PIVOT_FORWARD, ARM_PIVOT_UP, ARM_SLIDE, COLUMN_TILT, GRIP, NEMA, NEMA_LEN, Z_MOTOR_FACE\n"
assert s.count(old_imp) == 1
s = s.replace(old_imp, "from params import (ARM_LENGTHS, ARM_PIVOT_FORWARD, ARM_PIVOT_UP, ARM_SLIDE, COLUMN_TILT, GRIP, NEMA, NEMA_LEN,\n"
                       "                    ROLLER_R, Z_GEAR_ROLLER, Z_MOTOR_FACE)\n")

# docstring of check_all: mention the new states
old_doc = '''  steering wheel turned wheel_turn degrees with the carrier dropped as far as it goes. Keys ending "(should touch)" hold
  minus the overlap, so they must be negative: the click's tab must meet its ridge, the lever's heel must stop it."""'''
new_doc = '''  steering wheel turned wheel_turn degrees either way with the carrier dropped as far as it goes; the setup gauge in place.
  Every moving part is also checked against the dash cover and the dash clamp, and the bought screws and bolts (motor
  screws, the switch's screws anywhere in their slots, the lift lever's bolt and nut) against what is near them. Keys
  ending "(should touch)" hold minus the overlap, so they must be negative: the click's tab must meet its ridge, the
  lever's heel must stop it."""'''
assert s.count(old_doc) == 1
s = s.replace(old_doc, new_doc)

# lever down: extra pairs
old_down = '''  for k, (a, b) in pairs.items():
    res["down: " + k] = overlap(a, b)
'''
new_down = '''  # the bought hardware, and everything against the dash cover and the dash clamp
  sws = {dy: A._carried(MP.switch_screws(dy=dy), 0.0) for dy in (-MP.SW_SLOT, 0.0, MP.SW_SLOT)}
  LB = A._carried(MP.lever_bolt(), 0.0)
  for dy, sw in sws.items():
    pairs[f"switch screws ({dy:+.0f} mm in slots)/hinge block"] = (sw, HB)
    pairs[f"switch screws ({dy:+.0f} mm in slots)/arm"] = (sw, AR)
  pairs.update({"lever bolt/hinge block": (LB, HB), "lever bolt/arm": (LB, AR), "lever bolt/teeth": (LB, T)})
  for fixed_name, fixed in (("dash cover", hood), ("dash clamp", CL)):
    for mover_name, mover in (("motor gear", G), ("carrier", C), ("motor", M), ("hinge block", HB), ("lever bracket", BR),
                              ("switch", SW), ("lift lever", LV), ("lever bolt", LB), ("teeth", T)):
      pairs[f"{mover_name}/{fixed_name}"] = (mover, fixed)
  pairs["lever bolt/clamp"] = (LB, CL)
  for k, (a, b) in pairs.items():
    res["down: " + k] = overlap(a, b)
  # the motor's screw heads (button heads in their counterbores) clear the motor gear even pushed right against the
  # plate with its roller 0.15 mm oversize
  zr0, zr1 = (z - Z_MOTOR_FACE for z in Z_GEAR_ROLLER)
  worst_gear = (A.p["gear"] + cyl(ROLLER_R + 0.15, zr0, zr1, segments=360)).translate((0, 0, -0.5))
  res["motor screw heads/motor gear (gear against the plate, roller 0.15 mm oversize)"] = overlap(MP.motor_screw_heads(), worst_gear)
  # the setup gauge in place, motor gear on the teeth
  gauge = A._carried(MP.setup_gauge(), 0.0)
  for k, b in {"lever bracket": BR, "spring": A._carried(MP.spring_body(), 0.0), "switch": SW, "carrier": C,
               "hinge block": HB, "arm": AR, "lift lever": LV}.items():
    res[f"setup gauge in: gauge/{k}"] = overlap(gauge, b)
'''
assert s.count(old_down) == 1
s = s.replace(old_down, new_down)

# lever up: extra pairs
old_up = '''                    "lever/arm": (LVo, AR), "lever/clamp": (LVo, CL), "lever/lever bracket": (LVo, BRl),
                    "lever/carrier": (LVo, Cl)}.items():
    res[tag + k] = overlap(a, b)
'''
new_up = '''                    "lever/arm": (LVo, AR), "lever/clamp": (LVo, CL), "lever/lever bracket": (LVo, BRl),
                    "lever/carrier": (LVo, Cl), "lever/dash cover": (LVo, hood), "carrier/dash cover": (Cl, hood),
                    "motor/dash cover": (Ml, hood), "lever bracket/dash cover": (BRl, hood), "switch/dash cover": (SWl, hood),
                    "carrier/clamp": (Cl, CL), "motor/clamp": (Ml, CL), "lever bracket/clamp": (BRl, CL),
                    "lever bolt/hinge block": (A._carried(MP.lever_bolt(), hair), HB),
                    "lever bolt/dash cover": (A._carried(MP.lever_bolt(), hair), hood),
                    "switch screws/hinge block": (A._carried(MP.switch_screws(dy=-MP.SW_SLOT), hair), HB)}.items():
    res[tag + k] = overlap(a, b)
'''
assert s.count(old_up) == 1
s = s.replace(old_up, new_up)

# swept: extra pairs
old_sw = '''    for k, (a, b) in {"lever/hinge block": (lv, HB), "lever/arm": (lv, AR), "lever/lever bracket": (lv, br),
                      "lever/carrier": (lv, ca), "carrier/hinge block": (ca, HB), "carrier/arm": (ca, AR),
                      "lever bracket/hinge block": (br, HB), "lever bracket/arm": (br, AR)}.items():'''
new_sw = '''    for k, (a, b) in {"lever/hinge block": (lv, HB), "lever/arm": (lv, AR), "lever/lever bracket": (lv, br),
                      "lever/carrier": (lv, ca), "carrier/hinge block": (ca, HB), "carrier/arm": (ca, AR),
                      "lever bracket/hinge block": (br, HB), "lever bracket/arm": (br, AR),
                      "lever/dash cover": (lv, hood), "lever/clamp": (lv, CL), "carrier/dash cover": (ca, hood),
                      "lever bracket/dash cover": (br, hood),
                      "lever bolt/hinge block": (A._carried(MP.lever_bolt(), th), HB),
                      "switch screws/hinge block": (A._carried(MP.switch_screws(dy=-MP.SW_SLOT), th), HB)}.items():'''
assert s.count(old_sw) == 1
s = s.replace(old_sw, new_sw)

# wheel turned: both ways, and the hardware
old_wt = '''  for k, (a, b) in {"grip/gear teeth": (W, teeth_only), "grip/carrier": (W, Cr), "grip/motor": (W, Mr),
                    "turned teeth/carrier": (Tt, Cr), "turned teeth/gear": (Tt, Gr), "turned teeth/lever bracket": (Tt, BRr),
                    "carrier/hinge block": (Cr, HB), "motor/hinge block": (Mr, HB), "lever bracket/hinge block": (BRr, HB),
                    "switch/hinge block": (SWr, HB), "carrier/arm": (Cr, AR), "lever bracket/arm": (BRr, AR),
                    "carrier fully dropped, lever/hinge block": (Ld, HB)}.items():
    res[f"wheel turned {wheel_turn:.0f}, carrier down {-rest:.1f} deg: " + k] = overlap(a, b)'''
new_wt = '''  Tt2 = A.teeth(-wheel_turn)
  LVr, LBr = A.lever(0.0, rest), A._carried(MP.lever_bolt(), rest)
  SWSr = A._carried(MP.switch_screws(dy=-MP.SW_SLOT), rest)
  checks = {"grip/gear teeth": (W, teeth_only), "grip/carrier": (W, Cr), "grip/motor": (W, Mr),
            "carrier/hinge block": (Cr, HB), "motor/hinge block": (Mr, HB), "lever bracket/hinge block": (BRr, HB),
            "switch/hinge block": (SWr, HB), "carrier/arm": (Cr, AR), "lever bracket/arm": (BRr, AR),
            "carrier fully dropped, lever/hinge block": (Ld, HB), "lever bolt/hinge block": (LBr, HB),
            "switch screws/hinge block": (SWSr, HB)}
  for side, TT in (("left", Tt), ("right", Tt2)):
    for name, part in (("carrier", Cr), ("gear", Gr), ("lever bracket", BRr), ("motor", Mr), ("switch", SWr),
                       ("lift lever", LVr), ("lever bolt", LBr), ("switch screws", SWSr)):
      checks[f"teeth turned {side}/{name}"] = (TT, part)
  for k, (a, b) in checks.items():
    res[f"wheel turned {wheel_turn:.0f}, carrier down {-rest:.1f} deg: " + k] = overlap(a, b)'''
assert s.count(old_wt) == 1
s = s.replace(old_wt, new_wt)
open(p, "w").write(s)
EOF
grep -n "^from cadlib import" assembly.py