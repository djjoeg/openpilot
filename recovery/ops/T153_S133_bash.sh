cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='/home/claude/deliver/hardware/cad/slideassembly.py'
s=open(p).read()
start=s.index('  # sliding off with the lever swinging off, then slid off: the wheel straight and a little either way')
end=s.index('  # slid off: the teeth anywhere round the wheel must miss everything')
new='''  # the lever swung from off to on as it really moves things: the cam slides the carrier on, then pushes the pusher back
  # (normally; and with the teeth meeting tip to tip, the carrier stopped 4.5 mm off while the lever goes all the way)
  for t2t in (0.0, 4.5):
    tag = "lever swinging" + (" (teeth tip to tip)" if t2t else "")
    for d in np.arange(SP.LEVER_SWING, -0.01, -2.5):
      st = SP.cam_state(float(d), t2t)
      off = st["carrier_off"]
      back = max(0.0, (SP.cam_support(float(d)) - SP.CAM_MIN - SP.CLEAR_OFF) - (SP.STROKE - off))
      lev = A.lever(off, SP.SWING_SIGN * float(d))
      parts = [("gear", A.gear(off)), ("carrier", A.carrier(off)), ("motor, board and plugs", A.motor(off)),
               ("rods and collars", A.rods(off)), ("latch lever", lev)]
      for name, part in parts:
        for w in (0.0, -15.0, 15.0):
          if name == "gear" and off < SP.STROKE - 1e-6 and t2t == 0.0:
            continue                      # the gear going into the teeth: the mesh sweep checks that
          key = f"{tag}: teeth/{name} (worst)"
          if name == "gear" and t2t:
            continue                      # tip to tip, by definition
          res[key] = max(res.get(key, 0.0), overlap(A.teeth(w), part))
        key = f"{tag}: grip/{name} (worst)"
        res[key] = max(res.get(key, 0.0), overlap(W, part))
        for cn, c in car:
          key = f"{tag}: {name}/{cn} (worst)"
          res[key] = max(res.get(key, 0.0), overlap(part, c))
      # the lever against the block: only its cam on the pusher's nose, never the block itself
      key = f"{tag}: latch lever/block (worst)"
      res[key] = max(res.get(key, 0.0), overlap(lev, A.block()))
      key = f"{tag}: pusher (pushed back {back:.1f})/block, carrier (worst)"
      pz = A.place(SP.pusher().translate((0.0, back, 0.0)))
      res[key.split(" (pushed")[0] + " pushed back/carrier (worst)"] = max(res.get(key.split(" (pushed")[0] + " pushed back/carrier (worst)", 0.0),
                                                                            overlap(pz, A.carrier(off)))
'''
s=s[:start]+new+s[end:]
open(p,'w').write(s)
EOF
cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide/leadin.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
import slideassembly as SA, slideparts as SP
A = SA.SlideAssembly(110.0)
t = A.t
worst = []
for w in np.arange(t.roll_half, t.half + 1.0, 0.5):
  for sign in (1, -1):
    d = SA.roller_drop(A, sign * float(w))
    T = A.teeth(sign * float(w))
    for name, part in (("gear teeth", A.gear(-d, 0.0, "gear_teeth_only")), ("carrier", A.carrier(-d)), ("motor", A.motor(-d)), ("rods", A.rods(-d)), ("lever", A.lever(-d))):
      v = SA.overlap(T, part)
      if v > 1e-3:
        worst.append((round(sign*float(w),1), round(d,2), name, round(v,3)))
print(worst)
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache && timeout 900 python3 leadin.py