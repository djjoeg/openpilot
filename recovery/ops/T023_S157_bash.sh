cat >> assembly.py <<'EOF'


def check_all(A: "Assembly", lift_deg: float = 22.0, wheel_turn: float = 70.0) -> dict:
  """Overlap volumes (mm^3) between parts that must not touch, in three states: motor gear on the teeth; carrier
  lifted by lift_deg (lift lever flipped); steering wheel turned wheel_turn degrees with the roller resting on it."""
  res = {}
  T, W = A.teeth(), A.wheel_grip()
  G, C, M = A.gear(), A.carrier(), A.motor()
  HB, S, AR, CL, LV = A.hinge_block(), A.slider(), A.arm(), A.clamp(), A.lever()
  hood = A.hood()
  pairs = {
    "teeth/gear": (T, G), "teeth/carrier": (T, C), "teeth/motor": (T, M), "grip/carrier": (W, C), "grip/motor": (W, M),
    "carrier/motor": (C, M), "carrier/hinge block": (C, HB), "motor/hinge block": (M, HB), "carrier/lever": (C, LV),
    "hinge block/slider": (HB, S), "hinge block/arm": (HB, AR), "slider/carrier": (S, C), "slider/motor": (S, M),
    "arm/carrier": (AR, C), "arm/motor": (AR, M), "arm/clamp": (AR, CL), "clamp/hood": (CL, hood),
    "arm/teeth": (AR, T), "slider/teeth": (S, T), "hinge block/teeth": (HB, T),
  }
  for k, (a, b) in pairs.items():
    res["down: " + k] = overlap(a, b)
  # lifted
  Gl, Cl, Ml = A.gear(lift_deg), A.carrier(lift_deg), A.motor(lift_deg)
  for k, (a, b) in {"teeth/gear": (T, Gl), "carrier/hinge block": (Cl, HB), "motor/hinge block": (Ml, HB),
                    "carrier/slider": (Cl, S), "motor/slider": (Ml, S), "carrier/arm": (Cl, AR), "motor/arm": (Ml, AR),
                    "carrier/lever off": (Cl, A.lever(off=True))}.items():
    res[f"lifted {lift_deg:.0f}: " + k] = overlap(a, b)
  # steering wheel turned past the teeth: roller rests on the steering wheel
  Tt = A.teeth(wheel_turn)
  rest = A.rest_on_grip_lift()
  Gr, Cr, Mr = A.gear(rest), A.carrier(rest), A.motor(rest)
  teeth_only = A.p["gear_teeth_only"].translate(tuple(A.b_org))
  from assembly import turn_about_x as _t
  teeth_only = _t(teeth_only, -rest, A.hinge_w)
  for k, (a, b) in {"grip/gear teeth": (W, teeth_only), "grip/carrier": (W, Cr), "grip/motor": (W, Mr),
                    "turned teeth/carrier": (Tt, Cr), "turned teeth/gear": (Tt, Gr), "carrier/hinge block": (Cr, HB),
                    "motor/hinge block": (Mr, HB)}.items():
    res[f"wheel turned {wheel_turn:.0f}, roller on wheel ({rest:.1f} deg): " + k] = overlap(a, b)
  return res
EOF
python3 - <<'EOF'
p = "/home/claude/deliver/hardware/cad/wheelparts.py"
s = open(p).read()
s += '''

def motor_gear_teeth_only() -> Manifold:
  """Just the motor gear's teeth (for checking that only the roller touches the steering wheel)."""
  off = -Z_MOTOR_FACE
  zt0, zt1 = (z + off for z in Z_GEAR_TEETH)
  return gear_outline(MOTOR_TEETH, BACKLASH).extrude(zt1 - zt0).translate((0, 0, zt0)).rotate((0, 0, MOTOR_GEAR_PHASE))
'''
open(p, "w").write(s)
EOF
cd /home/claude/deliver/hardware/cad && export PYTHONPATH=/home/claude/pylib:. && time timeout 900 python3 -c "
import wheelparts as WP, mountparts as MP, assembly as AS
t = WP.Teeth()
parts = dict(teeth=WP.teeth_one_piece(t), gear=WP.motor_gear(), gear_teeth_only=WP.motor_gear_teeth_only(), carrier=MP.motor_carrier(), hinge_block=MP.hinge_block(), lever=MP.lift_lever(), slider=MP.arm_slider(), arm=MP.arm(), clamp=MP.dash_clamp())
f = AS.solve(t)
print('fit', f.ok, 'arm below level', round(f.arm_below_level,1), 'slider', round(f.slider_pos,1), 'joint', round(f.joint_deg,1), f.notes)
A = AS.Assembly(t, f, parts)
for k, v in AS.check_all(A).items():
  print(f'{v:10.3f}  {k}' + ('   <-- TOUCHING' if v > 0.01 else ''))
"
