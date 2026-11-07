cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='/home/claude/deliver/hardware/cad/slideparts.py'
s=open(p).read()
old="PUSH_STOP = 15.0                           # N: the pusher's spring with the pusher out against the block's front wall"
new="PUSH_STOP = 30.0                           # N: the pusher's spring with the pusher out against the block's front wall (it\n                                           # also limits how far the carrier follows the roller past the teeth: 1.1 mm)"
assert old in s
s=s.replace(old,new)
old2='''def slide_teeth(t: SlideTeeth = None) -> Manifold:
  t = t or SlideTeeth()
  return clean(PP.pop_solid(t) - FP.tie_slots(t, slide_tie_angles(t)))'''
new2='''def slide_ramps(t: SlideTeeth) -> Manifold:
  """Past the rolling band at each end the back falls away towards the wheel, as on the pop-off mount; but here the
  carrier follows the roller straight along the column, so the gear's teeth keep their full reach out (radius 172) and
  the teeth's zone and the band's split just outside it."""
  zt_end = t.z_root + FP.TEETH_END_DROP
  zb_end = t.z_band + FP.BAND_END_DROP
  z_last = t.z_bridge - 2.0
  r_split = FP.ROLL_BAND[0] - 0.9
  fast = 0.45 * FP.END_LEAD_IN
  overlap = 0.05
  cuts = []
  for sgn in (1, -1):
    def band_z(u, s=sgn):
      a = s * u
      if a <= t.lead_end:
        return t.z_band + (zb_end - t.z_band) * min(1.0, (a - t.roll_half) / FP.END_LEAD_IN)
      return zb_end + (z_last - zb_end) * min(1.0, (a - t.lead_end) / t.chamfer_deg)

    def teeth_z(u, s=sgn):
      a = s * u
      if a <= t.lead_end:
        z = t.z_root + (zt_end - t.z_root) * min(1.0, (a - t.roll_half) / fast)
      else:
        z = zt_end + (z_last - zt_end) * min(1.0, (a - t.lead_end) / t.chamfer_deg)
      return max(z, band_z(u, s))

    a0, a1 = t.roll_half, t.half + 0.5
    lo, hi = (a0, a1) if sgn > 0 else (-a1, -a0)
    cuts.append(FP.polar_ramp_cut(t.r_flat - 3.0, r_split + overlap, lo, hi, teeth_z, t.z_tip - 3.0))
    cuts.append(FP.polar_ramp_cut(r_split - overlap, t.w_out + 1.0, lo, hi, band_z, t.z_tip - 3.0))
  return union(cuts)


def slide_solid(t: SlideTeeth) -> Manifold:
  from cadlib import revolve
  body = revolve(t.profile(), -t.half, t.half, step_deg=0.25)
  n = t.n_teeth // 2
  body = body - FP.tooth_spaces(t, -n, n) - FP.teeth_trim(t) - FP.tip_chamfers(t, -t.half - 1.0, t.half + 1.0) - \\
    PP.inner_chamfer(t) - slide_ramps(t) - PP.pop_spoke_notch(t) - FP.centre_mark(t)
  return clean(body)


def slide_teeth(t: SlideTeeth = None) -> Manifold:
  t = t or SlideTeeth()
  return clean(slide_solid(t) - FP.tie_slots(t, slide_tie_angles(t)))'''
assert old2 in s
s=s.replace(old2,new2)
open(p,'w').write(s)
p='/home/claude/deliver/hardware/cad/slideassembly.py'
s=open(p).read()
s=s.replace('name = f"slide_teeth_{t.rr:.1f}_{t.z_axis:.2f}_{t.spoke[0]:.1f}_{t.spoke[1]:.1f}"',
            'name = f"slide_teeth2_{t.rr:.1f}_{t.z_axis:.2f}_{t.spoke[0]:.1f}_{t.spoke[1]:.1f}"')
open(p,'w').write(s)
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache && timeout 1200 python3 -c "
import sys; sys.path.insert(0,'/home/claude/deliver/hardware/cad')
import slideparts as SP, slideassembly as SA
print('push travel', round(SP.PUSH_TRAVEL_ON,2), 'flat', round(SP.CAM_FLAT,2))
import json; print(json.dumps(SA.latch_numbers()))
" && timeout 1500 python3 leadin.py