python3 - <<'EOF'
p='columnparts.py'; s=open(p).read()
# imports
s=s.replace("from params import (ARM_T, ARM_W, BACKLASH, CD_EXTRA, COVER_H, COVER_H_RANGE, COVER_W_RANGE, END_CHAMFER, END_LEAD_IN,\n                    FRONT_RING_T, M3_PILOT, M6_CLEAR, M6_NUT_AF, MOTOR_TEETH, RING_TEETH, ROLL_PAST_TEETH, ROLLER_R, SKIRT_T,\n                    TIE_T, TIE_W, Z_GEAR_ROLLER, Z_GEAR_TEETH, Z_MOTOR_FACE, Z_MOTOR_FACE_C)",
"from params import (ARM_T, BACKLASH, CD_EXTRA, COVER_H, COVER_H_RANGE, COVER_W_RANGE, END_CHAMFER, END_LEAD_IN, FRONT_RING_T,\n                    M5_CLEAR, M6_CLEAR, M6_NUT_AF, MOTOR_TEETH, RING_TEETH, ROLLER_R, SKIRT_T, Z_GEAR_ROLLER, Z_GEAR_TEETH,\n                    Z_MOTOR_FACE, Z_MOTOR_FACE_C)")
s=s.replace("from cadlib import box, circle_yz, clean, cyl, cyl_x, cyl_y, extrude_x, polar_mask, prism_x, revolve, sector, union",
            "from cadlib import box, clean, cyl, cyl_x, cyl_y, polar_mask, prism_x, revolve, sector, union")
s=s.replace("TEETH_CHAMFER = 5.0                                                 # the teeth's front ends slope back 45 degrees over this\n","")
# RingTeeth: chamfer length, inner_radius_at over the central arc
s=s.replace("    self.chamfer_deg = math.degrees(END_CHAMFER / self.r_skirt_in)\n",
            "    self.chamfer_deg = math.degrees(END_CHAMFER / self.r_skirt_in)\n    self.teeth_chamfer = self.r_root + 0.6 - self.r_tip      # the teeth's front ends slope back 45 degrees over this\n")
s=s.replace("""    a = abs(angle_from_bottom)
    if a <= self.roll_half:
      return 0.0
""","""    a = abs(angle_from_bottom)
    if a <= self.roll_half:
      return self.r_roll - 0.5
""")
s=s.replace("""  ring = GR.internal_gear_outline(RING_TEETH, BACKLASH, t.r_root + 0.6).rotate(270.0 - t.pitch_deg / 2.0)""",
            """  ring = GR.internal_gear_outline(RING_TEETH, BACKLASH, t.r_root + 0.6).rotate(270.0)""")
old=s[s.index("def ring_teeth_solid"):s.index("def tie_slots")]
new='''def ring_teeth_solid(t: RingTeeth) -> Manifold:
  """The whole ring teeth piece, before cutting the zip tie slots."""
  a0, a1 = 270.0 - t.half, 270.0 + t.half
  body = revolve(t.profile(), a0, a1)
  # the rolling band's ends: cut the skirt's inside away out to inner_radius_at(angle), over the skirt's depth
  zlo, zhi = RING_BACK_Z - 1.0, -t.base.wz_out + 0.01
  cut = polar_mask(lambda a: t.inner_radius_at(a - 270.0), a0 - 0.5, a1 + 0.5, zlo, zhi)
  cut = cut - cyl(t.r_roll - 0.3, zlo - 1, zhi + 1, segments=1440)
  body = body - cut
  # the teeth; their front ends slope back 45 degrees from the root to the tips, so the piece prints front face down
  teeth = ring_teeth_outline(t).extrude(Z_TEETH_C[1] + t.teeth_chamfer - Z_TEETH_C[0]).translate((0, 0, Z_TEETH_C[0]))
  return clean(body + (teeth ^ teeth_front(t, a0 - 1.0, a1 + 1.0)))


def teeth_front(t: RingTeeth, a0: float, a1: float) -> Manifold:
  """The region the ring's teeth may fill: behind a 45 degree slope from the root at the front to the tips."""
  zt0, zt1 = Z_TEETH_C
  c = t.teeth_chamfer
  return revolve([(t.r_root + 0.6, zt1 + c + 0.01), (t.r_tip - 1.0, zt1 - 1.0), (t.r_tip - 1.0, zt0 - 0.01),
                  (t.r_root + 0.6, zt0 - 0.01)], a0, a1)


'''
s=s.replace(old,new)
old=s[s.index("def ring_tooth_fit_test"):s.index("def internal_free_play")]
new='''def ring_tooth_fit_test(t: RingTeeth, n_teeth: int = 8) -> Manifold:
  """A few ring teeth with their rolling band on a short block, to try the printed motor gear in by hand. Prints
  front face down like the ring teeth."""
  half = n_teeth / 2 * t.pitch_deg
  a0, a1 = 270.0 - half - 1.5, 270.0 + half + 1.5
  zt0, zt1 = Z_TEETH_C
  zr0, zr1 = Z_ROLL_C
  zf = zt1 + t.teeth_chamfer + 2.0
  pts = [(t.r_skirt_in, zf), (t.r_skirt_in, zr1), (t.r_roll, zr1 - (t.r_skirt_in - t.r_roll)), (t.r_roll, zr0 - 2.0),
         (t.r_out + 3.0, zr0 - 2.0), (t.r_out + 3.0, zf)]
  body = revolve(pts, a0, a1)
  teeth = ring_teeth_outline(t, n_teeth=n_teeth, lowered_ends=False).extrude(zt1 + t.teeth_chamfer - zt0).translate((0, 0, zt0))
  return clean(body + (teeth ^ teeth_front(t, a0 - 1.0, a1 + 1.0)))


'''
s=s.replace(old,new)
# saddle block: no web
old=s[s.index("def saddle_block"):s.index("def rod_slots")]
new='''def saddle_block() -> Manifold:
  """A saddle without its V or slots (lower saddle frame): a block from SADDLE_BOTTOM up to y = 0 between the V's
  ends, and ears EAR_T thick out to SADDLE_HALF_X."""
  body = box(-V_HALF_X, V_HALF_X, SADDLE_BOTTOM, 0.0, -SADDLE_LEN / 2, SADDLE_LEN / 2)
  ears = box(-SADDLE_HALF_X, SADDLE_HALF_X, SADDLE_BOTTOM, SADDLE_BOTTOM + EAR_T, -SADDLE_LEN / 2, SADDLE_LEN / 2)
  return body + ears


'''
s=s.replace(old,new)
s=s.replace('  part = part - cyl_x(MP.M5_CLEAR / 2 if hasattr(MP, "M5_CLEAR") else 2.75, -60, 60, y=py, z=pz, segments=32)',
            '  part = part - cyl_x(M5_CLEAR / 2, -60, 60, y=py, z=pz, segments=32)')
s=s.replace('    slot.append(cyl_x(2.75, -60, 60,','    slot.append(cyl_x(M5_CLEAR / 2, -60, 60,')
s=s.replace("ROD_LEN = 160.0               # M6 threaded rod, cut to this length (four)","ROD_LEN = 200.0               # M6 threaded rod, four pieces this long (cut shorter to suit: the report says how much is used)")
open(p,'w').write(s); print('ok')
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import time, math
t0=time.time()
import columnparts as CP, params as P, wheelparts as WP
from cadlib import size_of
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP)
print("cd_int", CP.centre_distance(), "r_roll", t.r_roll, "r_tip", t.r_tip, "r_root", t.r_root, "r_out", t.r_out, "half", t.half, "span", t.span_deg)
print("Z teeth", CP.Z_TEETH_C, "roll", CP.Z_ROLL_C, "back", CP.RING_BACK_Z, "gear teeth", CP.Z_GEAR_TEETH_C, "gear roller", CP.Z_GEAR_ROLLER_C)
m = CP.ring_teeth(t)
print("ring teeth: pieces", len(m.decompose()), "status", m.status(), "size", [round(v,1) for v in size_of(m)], "vol cm3", round(m.volume()/1000,1), round(time.time()-t0,1),"s")
ft = CP.ring_tooth_fit_test(t)
print("fit test: pieces", len(ft.decompose()), ft.status(), [round(v,1) for v in size_of(ft)])
up = CP.column_clamp_upper(); lo = CP.column_clamp_lower()
print("upper", len(up.decompose()), up.status(), [round(v,1) for v in size_of(up)], round(up.volume()/1000,1))
print("lower", len(lo.decompose()), lo.status(), [round(v,1) for v in size_of(lo)], round(lo.volume()/1000,1))
print(round(time.time()-t0,1),"s")
EOF