python3 - <<'EOF'
p='columnparts.py'; s=open(p).read()
old="Z_ROLL_C = (Z_GEAR_ROLLER_C[0] - 0.5, Z_TEETH_C[0])                 # the rolling band, behind them\nRING_BACK_Z = Z_ROLL_C[0] - 1.0                                     # the skirt's back face\n"
new="Z_ROLL_C = (Z_GEAR_ROLLER_C[0] + 0.5, Z_TEETH_C[0])                 # the rolling band, behind them; its back end is\nRING_BACK_Z = Z_ROLL_C[0]                                           # the skirt's back face, 1 mm clear of the carrier's plate\n"
assert old in s; s=s.replace(old,new); open(p,'w').write(s)
p='params.py'; s=open(p).read()
old="DASH_Z = -220.0            # the dash panel below the column, behind the middle of the grip (estimate; the motor needs 150)"
new="DASH_Z = -300.0            # the dash panel below the column, behind the middle of the grip (estimate; the report says\n                           # how far back the parts reach)"
assert old in s; s=s.replace(old,new); open(p,'w').write(s); print("ok")
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
A = CA.ColumnAssembly(t, fit, parts)
res = CA.check_all(A, lever_step=4.0)
bad = {k: round(v,2) for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)}
print(len(res), "checks;", len(bad), "bad:"); print(json.dumps(bad, indent=1))
print("margins:", CA.margins(A))
import render as R
from cadlib import box
scene = CA.parts_scene(A)
side = R.look((1, 0, 0), (0, 1, 0)); iso = R.look((1.0, -0.8, 0.9), (0, 1, 0)); front = R.look((0,0,1),(0,1,0))
lift = MP.cam_lift(MP.A_OFF)
R.save("/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/photo/col1.png",
       [(scene, side), (CA.parts_scene(A, lift, MP.A_OFF), side), (scene, front)],
       ["lever down (from the right)", "lever up", "from the driver's seat"], size=(700, 700))
crop = box(-200, 200, -260, -40, -260, 40)
R.save("/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/photo/col2.png",
       [([(m ^ crop, c) for m, c in scene if not (m ^ crop).is_empty()], iso), ([(m ^ crop, c) for m, c in CA.parts_scene(A, lift, MP.A_OFF) if not (m ^ crop).is_empty()], iso)],
       ["lever down", "lever up"], size=(900, 760))
print(round(time.time()-t0,1), "s")
EOF