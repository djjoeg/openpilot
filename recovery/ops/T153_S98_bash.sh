python3 - <<'EOF'
p='slideparts.py'
s=open(p).read()
start=s.index('# ***** the latch: lever with a cam on the carrier')
end=s.index('# ***** the release springs on the rods')
new='''# ***** the latch: lever with a cam on the carrier, spring-loaded pusher in the block *****
LEVER_X = (-50.0, -44.0)                   # the lever's thickness (x)
PIVOT = (12.0, 0.0)                        # (y, z) its bolt (M5 x 35 and a lock nut), on the carrier
PIVOT_BOSS_X = (-44.0, -40.0)              # the boss on the carrier's wall the bolt goes through (lever outside it)
CAM_MIN = 8.0                              # the cam round the bolt (it faces the pusher with the lever off)
CAM_FLAT_HALF = 3.6                        # the flat that sits on the pusher with the lever on: +- this wide
LEVER_SWING = 85.0                         # degrees from off to on (the cam starts pushing about 77 degrees before on)
PUSHER_X = -47.0                           # the pusher's axis (x); it points at the bolt (z = PIVOT[1])
PUSHER_NOSE_D = 11.6                       # the nose that the cam pushes, through a 12.2 mm hole in the block's front
PUSHER_HOLE_D = 12.2
PUSHER_BODY_D = 14.0                       # its body behind the block's front wall; the spring behind it
PUSHER_BORE = 14.4
CLEAR_OFF = 0.5                            # slid off with the lever off, the cam clears the pusher by this much
FRONT_WALL_T = 2.5                         # the block's wall in front of the pusher's body
HANDLE_ON = (-24.0, -8.0)                  # (y, z) the handle's end from the bolt, lever on: forward, a little in
SWING_SIGN = -1.0                          # turning the lever off swings the handle out (away from the column)
# The pusher's spring: Lee Spring LC 072G 05 M (music wire, 12.19 mm outside, 1.83 mm wire, 25.4 mm long, 18.214 N/mm,
# 198.65 N at its solid height of 14.53 mm). Pre-loaded to PUSH_STOP in the block; the lever on presses it to PUSH_ON
# (with the gear on the teeth), so the gear stays pressed in while the teeth piece wobbles as the wheel turns.
PSPRING = {"part": "Lee Spring LC 072G 05 M", "od": 12.19, "wire": 1.83, "free": 25.4, "rate": 18.214, "solid": 14.53,
           "max": 198.65}
PUSH_STOP = 15.0                           # N: the pusher's spring with the pusher out against the block's front wall
PUSH_ON = 50.0                             # N: ... with the lever on and the gear on the teeth


def _spring_len(force: float) -> float:
  return PSPRING["free"] - force / PSPRING["rate"]


PUSH_TRAVEL_ON = _spring_len(PUSH_STOP) - _spring_len(PUSH_ON)           # the pusher goes back this far with the lever on
CAM_FLAT = CAM_MIN + CLEAR_OFF + STROKE + PUSH_TRAVEL_ON                # the flat's distance from the bolt
PUSH_FACE_STOP = PIVOT[0] + STROKE + CAM_MIN + CLEAR_OFF                 # the pusher's nose (y), out against its stop

'''
s=s[:start]+new+s[end:]
# block y and wall y
s=s.replace("WALL_Y = (-12.0, 22.0)                     # ... its front and back (its back stops against the block, slid off)",
            "WALL_Y = (-12.0, 23.5)                     # ... its front and back (its back stops against the block, slid off)")
s=s.replace("BLOCK_Y = (28.0, 70.0)","BLOCK_Y = (WALL_Y[1] + STROKE, WALL_Y[1] + STROKE + 42.0)")
s=s.replace("BRG_Y = ((29.5, 48.5), (49.5, 68.5))","BRG_Y = ((BLOCK_Y[0] + 1.5, BLOCK_Y[0] + 20.5), (BLOCK_Y[0] + 21.5, BLOCK_Y[0] + 40.5))")
open(p,'w').write(s)
EOF
grep -n "PUSH_BODY_Y\|PSPRING_Y0\|PLUG_Y\|BLOCK_Y\b" slideparts.py | head -30