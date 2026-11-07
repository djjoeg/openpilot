cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
s = open('carref.py').read()
rep = [
("KEY_CLOCK_DEG = -12.0          # about 3:24 (0 = 3 o'clock, + up): range 3:18-3:35",
 "KEY_CLOCK_DEG = -13.0          # about 3:26 (0 = 3 o'clock, + up): range 3:16-3:36"),
("KEY_Z = -108.0                 # ... and this far behind the middle of the grip: range -98 to -118",
 "KEY_Z = -115.0                 # ... and this far behind the middle of the grip: range -100 to -145"),
("KEY_TILT_DEG = 18.0            # the bezel faces out from the column, turned this far towards the driver: range 8-28",
 "KEY_TILT_DEG = 30.0            # the bezel faces out from the column, turned this far towards the driver: range 15-42"),
('KEY_RANGE = {"clock_deg": (-18.0, -6.0), "r": (90.0, 110.0), "z": (-118.0, -98.0), "tilt_deg": (8.0, 28.0)}',
 'KEY_RANGE = {"clock_deg": (-18.0, -8.0), "r": (90.0, 115.0), "z": (-145.0, -100.0), "tilt_deg": (15.0, 42.0)}'),
("BACK_COVER_RIM_Z = -67.0       # its edge (the tape's hook, photo 24): range -57 to -77",
 "BACK_COVER_RIM_Z = -80.0       # its edge (the tape's hook, photo 24): range -60 to -110"),
("WIPER_FROM = (80.0, 30.0, -95.0)    # where the wiper stalk comes out of the cover (range +-15 each way)\nWIPER_TO = (170.0, 72.0, -60.0)     # its end, 105 mm along (your tape)",
 "WIPER_FROM = (85.0, 32.0, -110.0)   # where the wiper stalk comes out of the cover (range +-15 each way)\n"
 "WIPER_TO = (140.0, 62.0, -27.0)     # its end, 105 mm along (your tape): 150 mm from the column's centre (photo 36: 145-155)\n"
 "WIPER_END_Z_RANGE = (-80.0, -25.0)  # how far behind the middle of the grip its end is: not pinned down by the photos"),
("CUP = (80.0, -84.0, -105.0)         # the screw cup under the key, about 65 mm below its centre: range +-15",
 "CUP = (80.0, -90.0, -112.0)         # the screw cup under the key, about 65 mm below its centre: range +-15"),
]
for a, b in rep:
    assert a in s, a[:60]
    s = s.replace(a, b)
old_rows = s[s.index("REFERENCE_ROWS = ["):]
new_rows = '''REFERENCE_ROWS = [
  ("Key: centre of the bezel", "3:16–3:36; 90–115 mm out from the column's centre; 100–145 mm behind the middle of the grip (best guess 115)",
   "photos 24, 26, 33, 37 (bezel size, grip edge, cluster numbers); your tape in photo 24"),
  ("Key: which way it faces", "out from the column, turned 15–42° towards you", "photos 24 (tape marks), 26, 33, 37"),
  ("Key bezel", "black ring 38 mm across, chrome ring about 26 mm; keyhole slot at about 45°", "your tape over it, photo 24; photos 26, 33, 37"),
  ("Wheel's back cover: its edge by the column covers", "41 mm in front of the key's centre, along the cover (60–110 mm behind the middle of the grip)",
   "your tape, photo 24"),
  ("Dash trim beside the key", "95–100 mm from the back cover's edge, along the cover", "your tape, photo 24"),
  ("Wiper stalk", "comes out about 50 mm above the key, 105 mm long, its end about 150 mm from the column's centre at about 2:10; how far its end sits behind the grip isn't pinned down (25–80 mm)",
   "photos 24, 26, 33, 37, 36; your tape, photo 25"),
  ("Screw cup under the key", "about 65 mm below the key's centre", "photos 33, 37"),
  ("Steering wheel", "372 mm across, grip 35.4 mm thick", "your tape, photos 36 and 35"),
]
'''
s = s.replace(old_rows, new_rows)
open('carref.py', 'w').write(s)
print('ok')
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && cat > mirrorcheck.py <<'EOF'
"""Where could the mount go instead? The mount's moving and fixed parts (not the plate) turned round the column, or
mirrored to the left side, against the car rebuilt from the photos."""
import os, sys, math
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
os.environ.setdefault("POP_CACHE", "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache")
import numpy as np
import carref as CR
import popassembly as PA, popparts as PP, params as P
from cadlib import union
from run_u import build
t, parts = build()
A = PA.PopAssembly(t, parts)
mount = {"hinge block": A.block() + A.switch(), "motor on": A.motor() + A.carrier() + A.springs() + A.bolts(),
         "swinging off": union([A.motor(l) + A.carrier(l) + A.springs(l) for l in (15.0, 35.0, 55.0, PP.LIFT_OFF)])}
def turned(m, deg, mirror):
    m = m.rotate((0, 0, deg))
    return m.mirror((1.0, 0.0, 0.0)) if mirror else m
def key_parts(clock, r, z, tilt):
    b = CR.bezel(clock, r, z, tilt)
    return {"key bulge": CR.key_bulge(clock, r, z, tilt) + b["ring"], "key": CR.key_in(clock, r, z, tilt),
            "hand on key": CR.key_turn_room(clock, r, z, tilt)}
import itertools
keys = {"key best": (CR.KEY_CLOCK_DEG, CR.KEY_R, CR.KEY_Z, CR.KEY_TILT_DEG),
        "key fwd": (CR.KEY_CLOCK_DEG, CR.KEY_R, -100.0, CR.KEY_TILT_DEG),
        "key back": (CR.KEY_CLOCK_DEG, CR.KEY_R, -145.0, CR.KEY_TILT_DEG)}
K = {kn: key_parts(*a) for kn, a in keys.items()}
stalk_rest = CR.stalk()
def stalk_down(deg):
    base = np.array(CR.WIPER_FROM); tip = np.array(CR.WIPER_TO)
    d = (tip - base) / np.linalg.norm(tip - base)
    ax = np.cross(d, [0.0, 1.0, 0.0]); ax /= np.linalg.norm(ax)
    th = math.radians(-deg); v = tip - base
    v2 = v * math.cos(th) + np.cross(ax, v) * math.sin(th) + ax * np.dot(ax, v) * (1 - math.cos(th))
    import columnassembly as CA
    return CA.rod(base, base + v2, CR.STALK_R)
wipers = union([stalk_down(a) for a in (0, 12, 24, 36)])
signal = union([stalk_down(a) for a in (-15, 0, 15)]).mirror((1.0, 0.0, 0.0))     # left stalk up and down for the signals
tab = A.tilt_lever()
covers = A.covers()
def report(label, deg, mirror):
    hits = []
    for mn, m0 in mount.items():
        m = turned(m0, deg, mirror)
        if not mirror:
            for kn, kp in K.items():
                for pn, pm in kp.items():
                    v = (m ^ pm).volume()
                    if v > 1.0:
                        hits.append(f"{mn}/{pn} ({kn}) {v:.0f}")
        for on, o in (("wiper stalk 0-36 deg", wipers), ("signal stalk", signal), ("adjustment tab + fingers", tab), ("covers", covers)):
            v = (m ^ o).volume()
            if v > 1.0:
                hits.append(f"{mn}/{on} {v:.0f}")
    print(f"{label}: " + ("clear" if not hits else "; ".join(hits)), flush=True)
for deg in (0.0, -10.0, -20.0, -30.0):
    clock = PP.MOUNT_DEG + deg
    report(f"right side, turned {deg:+.0f} (centre {clock:+.0f} deg from 3:00)", deg, False)
for deg in (10.0, 20.0):
    report(f"right side, turned {deg:+.0f}", deg, False)
for deg in (0.0, -10.0, 10.0):
    report(f"LEFT side, mirror, turned {deg:+.0f}", deg, True)
EOF
PYTHONPATH=/home/claude/pylib timeout 2400 python3 mirrorcheck.py 2>&1 | tail -20