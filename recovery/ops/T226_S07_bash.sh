python3 - <<'EOF'
p='midteeth.py'; s=open(p).read()
s=s.replace('''def mid_solid(t: MidTeeth) -> Manifold:
  from cadlib import revolve
  body = revolve(t.profile(), -t.half, t.half, step_deg=0.25)
  n = t.n_teeth // 2
  body = body - FP.tooth_spaces(t, -n, n) - FP.teeth_trim(t) - FP.tip_chamfers(t, -t.half - 1.0, t.half + 1.0) - \\
    PP.inner_chamfer(t) - SP.slide_ramps(t) - ends_cut(t) - FP.centre_mark(t) - S.face_roofs(t)
  return clean(body)''','''def band_cut(t: MidTeeth) -> Manifold:
  """The rolling band (the ridge the old roller rode on, just outside the teeth) cut down level with the flat beside
  it: nothing rolls on it now, and the gear's outer teeth just touched it."""
  return FP.polar_box(FP.ROLL_BAND[0] - 0.3, FP.ROLL_BAND[1] + 0.5, -t.half - 1.0, t.half + 1.0, -80.0, t.z_flat)


def mid_solid(t: MidTeeth) -> Manifold:
  from cadlib import revolve
  body = revolve(t.profile(), -t.half, t.half, step_deg=0.25)
  n = t.n_teeth // 2
  body = body - FP.tooth_spaces(t, -n, n) - FP.teeth_trim(t) - FP.tip_chamfers(t, -t.half - 1.0, t.half + 1.0) - \\
    PP.inner_chamfer(t) - SP.slide_ramps(t) - ends_cut(t) - FP.centre_mark(t) - S.face_roofs(t) - band_cut(t)
  return clean(body)''')
s=s.replace('''  - each set is only as long as its own teeth need (the old pieces kept the 14-tooth length for their end ties).''','''  - each set is only as long as its own teeth need (the old pieces kept the 14-tooth length for their end ties);
  - the rolling band outside the teeth (for the old roller) cut down level: the gear now comes in from outside.''')
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 - <<'EOF'
import sys; sys.path.insert(0,'.')
import rightarm as RA, midteeth as MT, numpy as np, math
t=MT.MidTeeth(n_teeth=10); print("z_flat", round(t.z_flat,2), "z_band", round(t.z_band,2), "z_tip", round(t.z_tip,2), "z_root", round(t.z_root,2))
teeth=MT.mid_teeth(t).rotate((0,0,RA.THETA))
gear=RA.motor_and_gear()["gear"]
U=RA.U; c=RA.R_FACE_OUT*U
def spin(m,deg):
    ang=math.degrees(math.atan2(U[1],U[0]))
    return m.translate((-c[0],-c[1],-RA.Z_AXIS)).rotate((0,0,-ang)).rotate((deg,0,0)).rotate((0,0,ang)).translate((c[0],c[1],RA.Z_AXIS))
worst=0
for a in np.arange(-11,11.1,1.0):
    tp=teeth.rotate((0,0,a))
    best=min((spin(gear,d)^tp).volume() for d in np.arange(0,22.5,1.5))
    worst=max(worst,best)
print("gear in the teeth, phased, worst overlap over +-11 deg:", round(worst,2), "mm3")
# and the other parts vs the new piece
mg=RA.motor_and_gear()
parts={"plate":RA.plate_to_wheel(RA.frame_plate_v4()),"arm":RA.arm(),"bar":RA.bar(),"bracket":RA.bracket(),"motor":mg["motor"],"board":mg["board"]}
bad=False
for a in range(-25,26,5):
    tp=teeth.rotate((0,0,a))
    for n,m in parts.items():
        v=(tp^m).volume()
        if v>0.01: print(f"  teeth at {a} x {n}: {v:.1f}"); bad=True
print("other overlaps:", "some" if bad else "none")
EOF