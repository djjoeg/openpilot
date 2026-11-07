cat >> slideparts.py <<'EOF'


# ***** the back teeth for this mount *****
# The same teeth piece as the pop-off mount's short set, centred on the motor at 5:20. The right lower spoke (the silver
# bar) meets the grip right there, so the channel is cut away over its junction (only the back and the outside wall run
# across it, as over the right spoke at 3 o'clock) and the zip ties go either side of it, the upper ones in the lead-in.

BAR_DEG = (-74.0, -56.0)       # the silver bar meets the grip between these angles (carref.RIGHT_BAR_DEG)
BAR_TOL_DEG = 3.0              # read off one photo


class SlideTeeth(PP.PopTeeth):
  def __init__(self, mount_deg: float = MOUNT_DEG_S, **kw):
    super().__init__(mount_deg=mount_deg, **kw)
    lo = BAR_DEG[0] - (mount_deg + MOUNT_ADJ_S[1]) - BAR_TOL_DEG - FP.SPOKE_ROOM_DEG
    hi = BAR_DEG[1] - (mount_deg - MOUNT_ADJ_S[0]) + BAR_TOL_DEG + FP.SPOKE_ROOM_DEG
    self.spoke = (lo, hi)


def slide_tie_angles(t: SlideTeeth) -> list:
  """Zip tie slots every FP.SLOT_EVERY_DEG, outwards from the bar's notch on both sides, as far as the lead-in's end."""
  w = math.degrees(FP.TIE_W / 2.0 / t.rr) + 1.0
  out = []
  a = t.spoke[1] + w + 0.25
  while a + w <= t.lead_end:
    out.append(a)
    a += FP.SLOT_EVERY_DEG
  a = t.spoke[0] - w - 0.25
  while a - w >= -t.lead_end:
    out.append(a)
    a -= FP.SLOT_EVERY_DEG
  return sorted(out)


def slide_teeth(t: SlideTeeth = None) -> Manifold:
  t = t or SlideTeeth()
  return clean(PP.pop_solid(t) - FP.tie_slots(t, slide_tie_angles(t)))


# ***** the block's flange: bolts to the column plate's upright flange (two M5 x 25 along the column) *****
FLANGE_Y = (BLOCK_Y[1] - 4.5, BLOCK_Y[1])
FLANGE_X = (WALL_X[1] - 0.5, 12.0)
FLANGE_Z = (-18.0, 8.0)
FLANGE_BOLTS = ((-11.0, -9.0), (5.0, -1.0))   # (x, z)
FLANGE_SLOT = 8.0                              # each bolt's slot runs +- this across (x): the mount's +-3 degrees and the
                                               # plate's place


def block_flange() -> Manifold:
  fl = box(FLANGE_X[0], FLANGE_X[1], FLANGE_Y[0], FLANGE_Y[1], FLANGE_Z[0], FLANGE_Z[1])
  for x, z in FLANGE_BOLTS:
    fl = fl - Manifold.batch_hull([cyl_y(M5_CLEAR / 2, FLANGE_Y[0] - 1, FLANGE_Y[1] + 1, x=x + s, z=z, segments=32)
                                   for s in (-FLANGE_SLOT, FLANGE_SLOT)])
  return fl
EOF
python3 - <<'EOF'
p='/home/claude/deliver/hardware/cad/slideparts.py'
s=open(p).read()
old="  part = union([hs, web, pusher, join, sw_plate])\n"
new="  part = union([hs, web, pusher, join, sw_plate, box(FLANGE_X[0], -20.0, FLANGE_Y[0], FLANGE_Y[1], FLANGE_Z[0], FLANGE_Z[1])])\n"
assert old in s
s=s.replace(old,new)
old2="  part = part - box(TONGUE_X[1], WALL_X[1] + 12.0, SW_ROLL_Y - 6.0, SW_ROLL_Y + 6.0, -3.2, 3.2)\n  return clean(part)\n"
new2="  part = part - box(TONGUE_X[1], WALL_X[1] + 12.0, SW_ROLL_Y - 6.0, SW_ROLL_Y + 6.0, -3.2, 3.2)\n  part = part + block_flange()\n  return clean(part)\n"
assert old2 in s
s=s.replace(old2,new2)
open(p,'w').write(s)
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 900 python3 -c "
import slideparts as S, time
t=S.SlideTeeth()
print('spoke notch', [round(v,1) for v in t.spoke], 'half', round(t.half,1), 'roll', round(t.roll_half,1), 'lead_end', round(t.lead_end,1))
print('ties', [round(a,2) for a in S.slide_tie_angles(t)])
b=S.slide_block(); print('block', round(b.volume()), len(b.decompose()))
t0=time.time(); m=S.slide_teeth(t); print('teeth', round(m.volume()), len(m.decompose()), round(time.time()-t0,1),'s', [round(v,1) for v in m.bounding_box()])
"