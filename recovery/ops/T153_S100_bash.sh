python3 - <<'EOF'
p='slideparts.py'
s=open(p).read()
# add the pusher's positions after PUSH_FACE_STOP
anchor='PUSH_FACE_STOP = PIVOT[0] + STROKE + CAM_MIN + CLEAR_OFF                 # the pusher\'s nose (y), out against its stop\n'
add='''PUSH_BODY_Y = BLOCK_Y[0] + FRONT_WALL_T                                  # the body's front face, at the stop
PUSH_BODY_LEN = 10.0
PSPRING_Y0 = PUSH_BODY_Y + PUSH_BODY_LEN                                 # the spring's front end, at the stop
PSPRING_Y1 = PSPRING_Y0 + _spring_len(PUSH_STOP)                         # ... its back end, against the plug
PLUG_Y = (PSPRING_Y1, PSPRING_Y1 + 4.0)                                  # a printed plug closes the bore (two M3)
'''
assert anchor in s
s=s.replace(anchor, anchor+add)
start=s.index('# ***** the cam *****')
end=s.index('# ***** the carrier *****')
new='''# ***** the cam *****
# The cam is the convex hull of a circle round the bolt and a flat: with the lever on, the flat sits square on the
# pusher's nose CAM_FLAT from the bolt; the flat's corners are the high point the lever passes over just before (and
# just after) on, so it stays on until you push the handle back. With the lever off the circle faces the pusher.

def cam_support(short_deg: float) -> float:
  """How far the cam reaches towards the pusher (along +y from the bolt) with the lever short_deg degrees short of on."""
  d = math.radians(abs(short_deg))
  return max(CAM_MIN, CAM_FLAT * math.cos(d) + CAM_FLAT_HALF * math.sin(d))


def cam_peak() -> tuple:
  """(degrees short of on, reach) of the flat's corner, the lever's high point."""
  return math.degrees(math.atan2(CAM_FLAT_HALF, CAM_FLAT)), math.hypot(CAM_FLAT, CAM_FLAT_HALF)


def cam_outline() -> CrossSection:
  """In the lever's frame with the lever on: u along the pusher (+y), v = +z."""
  flat = CrossSection.square((0.01, 2 * CAM_FLAT_HALF)).translate((CAM_FLAT - 0.01, -CAM_FLAT_HALF))
  return CrossSection.batch_hull([CrossSection.circle(CAM_MIN, 96), flat])


def cam_state(short_deg: float, tip_to_tip: float = 0.0) -> dict:
  """The carrier's place (how far it still is from on, mm), the pusher's force (N) and the turning force the handle
  needs (N mm) with the lever short_deg short of on. tip_to_tip: the gear stopped this far short by the teeth meeting
  tip to tip."""
  reach = cam_support(short_deg)
  gap = reach - (CAM_MIN + CLEAR_OFF)               # how far the cam has pushed the carrier and the pusher apart
  if gap <= 0:
    return {"carrier_off": STROKE, "force": 0.0, "torque": 0.0}
  carrier_off = max(tip_to_tip, STROKE - gap)
  pusher_back = max(0.0, gap - (STROKE - carrier_off))
  rel = release_force(carrier_off)
  force = max(rel, PUSH_STOP + PSPRING["rate"] * pusher_back) if pusher_back > 0 else rel
  dd = 0.25
  slope = abs(cam_support(short_deg + dd) - cam_support(short_deg - dd)) / math.radians(2 * dd)
  return {"carrier_off": carrier_off, "force": force, "torque": force * slope}


def handle_len() -> float:
  return math.hypot(*HANDLE_ON)


def cam_table(step: float = 5.0) -> list:
  rows = []
  for t2t in (0.0, 4.5):
    for d in np.arange(LEVER_SWING, -0.01, -step):
      st = cam_state(float(d), t2t)
      rows.append({"tip_to_tip": t2t, "short_deg": round(float(d), 1), "carrier_off": round(st["carrier_off"], 2),
                   "force_N": round(st["force"], 1), "handle_N": round(st["torque"] / handle_len(), 1)})
  return rows


def slide_lever(swing: float = 0.0) -> Manifold:
  """The latch lever in the carrier frame, swung swing degrees from on (0 on; SWING_SIGN * LEVER_SWING off)."""
  hu, hv = HANDLE_ON
  L = math.hypot(hu, hv)
  ang = math.degrees(math.atan2(hv, hu))
  arm = CrossSection.batch_hull([CrossSection.circle(6.5, 48), CrossSection.circle(5.0, 48).translate((L - 3.0, 0.0))])
  pad = CrossSection.circle(6.5, 48).translate((L - 3.5, 0.0))
  handle = (arm + pad).rotate(ang)
  lever = (cam_outline() + handle) - CrossSection.circle(M5_CLEAR / 2, 48)
  m = extrude_x(lever, LEVER_X[0], LEVER_X[1]).translate((0.0, PIVOT[0], PIVOT[1]))
  if swing:
    m = m.translate((0.0, -PIVOT[0], -PIVOT[1])).rotate((swing, 0.0, 0.0)).translate((0.0, PIVOT[0], PIVOT[1]))
  return clean(m)


def release_force(carrier_off: float) -> float:
  """Both release springs' pull (N) with the carrier carrier_off mm back from on."""
  length_on = COLLAR_Y - BLOCK_Y[1]
  per = RSPRING["rate"] * max(0.0, RSPRING["free"] - (length_on + carrier_off))
  return 2.0 * per


'''
s=s[:start]+new+s[end:]
# pusher nose hole diameter
s=s.replace("  part = part - cyl_y(5.0, y0 - 1.0, PUSH_BODY_Y + 0.01, x=PUSHER_X, z=PIVOT[1], segments=48)",
            "  part = part - cyl_y(PUSHER_HOLE_D / 2, y0 - 1.0, PUSH_BODY_Y + 0.01, x=PUSHER_X, z=PIVOT[1], segments=48)")
open(p,'w').write(s)
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 -c "
import slideparts as S
print('CAM_FLAT', round(S.CAM_FLAT,2), 'peak', [round(v,2) for v in S.cam_peak()], 'push travel', round(S.PUSH_TRAVEL_ON,2))
print('block', S.BLOCK_Y, 'face stop', S.PUSH_FACE_STOP, 'body', S.PUSH_BODY_Y, 'spring', round(S.PSPRING_Y0,2), round(S.PSPRING_Y1,2), 'plug', [round(v,2) for v in S.PLUG_Y])
print('collar y', S.COLLAR_Y, 'release on/off', round(S.release_force(0),1), round(S.release_force(6),1))
for r in S.cam_table(5.0): print(r)
"
