cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
import re
s = open('carref.py').read()
old = """  head = Manifold.batch_hull([cyl(w / 2, KEY_SHANK, KEY_SHANK + t, segments=48).scale((1.0, t / w, 1.0)),
                              cyl(w / 2 - 4.0, KEY_SHANK + L - 1.0, KEY_SHANK + L, segments=48).scale((1.0, t / w, 1.0))])
  head = Manifold.batch_hull"""
new = """  head = Manifold.batch_hull"""
assert old in s
s = s.replace(old, new)
s = s.replace('CUP = (80.0, -78.0, -105.0)         # the screw cup under the key: range +-15',
              'CUP = (80.0, -84.0, -105.0)         # the screw cup under the key, about 65 mm below its centre: range +-15')
open('carref.py', 'w').write(s)
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > refcheck.py <<'EOF'
"""The pop-off mount as designed, against the car rebuilt from the photos (carref.py): overlap volumes."""
import os, sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
os.environ.setdefault("POP_CACHE", "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache")
import numpy as np
import carref as CR
import popassembly as PA, popparts as PP
from run_u import build
from mindist import min_dist
t, parts = build()
A = PA.PopAssembly(t, parts)
mount = {"hinge block": A.block(), "springs (motor on)": A.springs(), "bolts (motor on)": A.bolts(), "motor (on)": A.motor(),
         "carrier (on)": A.carrier(), "motor (popped off)": A.motor(PP.LIFT_OFF), "carrier (popped off)": A.carrier(PP.LIFT_OFF),
         "column plate": A.plate(), "screw tabs": A.tabs()}
def car(clock, r, z, tilt):
    b = CR.bezel(clock, r, z, tilt)
    return {"key bulge and bezel": CR.key_bulge(clock, r, z, tilt) + b["ring"] + b["chrome"] + b["face"],
            "the key in it": CR.key_in(clock, r, z, tilt), "room to turn the key": CR.key_turn_room(clock, r, z, tilt)}
cases = {"best estimate": (CR.KEY_CLOCK_DEG, CR.KEY_R, CR.KEY_Z, CR.KEY_TILT_DEG)}
lo, hi = CR.KEY_RANGE["z"]
cases["key 10 mm further back"] = (CR.KEY_CLOCK_DEG, CR.KEY_R, lo, CR.KEY_TILT_DEG)
cases["key 10 mm further forward"] = (CR.KEY_CLOCK_DEG, CR.KEY_R, hi, CR.KEY_TILT_DEG)
cases["key lower (3:35)"] = (CR.KEY_RANGE["clock_deg"][0], CR.KEY_R, CR.KEY_Z, CR.KEY_TILT_DEG)
for cname, args in cases.items():
    print("==", cname, args)
    for kn, km in car(*args).items():
        for mn, mm in mount.items():
            v = (km ^ mm).volume()
            if v > 1e-3:
                print("   %-22s overlaps %-22s %8.0f mm3" % (kn, mn, v))
bc = CR.back_cover()
for mn, mm in mount.items():
    v = (bc ^ mm).volume()
    if v > 1e-3:
        print("back cover overlaps", mn, round(v))
ws = CR.stalk()
for mn, mm in mount.items():
    v = (ws ^ mm).volume()
    if v > 1e-3:
        print("wiper stalk (at rest) overlaps", mn, round(v))
EOF
PYTHONPATH=/home/claude/pylib timeout 1500 python3 refcheck.py 2>&1 | tail -40