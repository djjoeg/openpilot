python3 - <<'EOF'
import pathlib
p = pathlib.Path("sideparts.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)
rep("""  axle = cyl_y(2.0, POST[1][0], SPOOL_Y[1] + SPOOL_FLANGE[1] + 0.8, x=SPOOL_X, z=SPOOL_Z, segments=24) + \\""",
    """  y_head = SPOOL_Y[1] + SPOOL_FLANGE[1] + 0.8                     # the washer under the head, then the head
  axle = cyl_y(2.0, y_head - AXLE_LEN, y_head, x=SPOOL_X, z=SPOOL_Z, segments=24) + \\""")
rep("""SPOOL_Z = -76.0                   # the spool's axle (an M4 x 25 screw along y), on the plate""",
    """SPOOL_Z = -76.0                   # the spool's axle (an M4 x 20 screw along y, through a washer), on the plate
AXLE_LEN = 20.0                   # ... it cuts its own thread 4.8 mm into the post""")
p.write_text(s)

p = pathlib.Path("sidebuild.py")
s = p.read_text()
rep("""BOUGHT = [
  ("HIWIN MGN12H block on a 100 mm MGN12 rail (or any MGN12H block with a 100 mm rail cut to HIWIN's sizes)", 1,
   "the slide"),
  ("4 mm x 24 mm steel dowel pin (ISO 8734), or 4 mm steel rod cut to 24 mm", 1,
   "the lever's pivot: tapped into the bracket's ear from its inner end, through the lever, into the blind hole"),
  ("Lee Spring LCF 040 08 050S constant force spring (11.7 N, 12.7 mm wide)", 1, "pulls the motor in"),
  ("Omron SS-5GL2-F roller switch (the one already in the parts list)", 1, "power switch"),
  ("M3 x 6 button head screw", 4, "motor to motor bracket (a socket head can rub the gear)"),
  ("M3 x 6 socket head screw", 4, "motor bracket to the rail's block (heads sink into the bracket)"),
  ("M3 x 10 socket head screw + M3 nut", 4, "rail to mounting plate (nuts sink into the plate's outer face)"),
  ("M3 x 10 socket head screw", 2, "the spring's strip: through the bracket's tab from the 6 o'clock side into the strip clamp"),
  ("M2 x 12 screw + M2 nut", 2, "power switch to the plate (nuts slide in slots from the top)"),
  ("M4 x 20 socket head screw + M4 washer", 1, "the spool's axle (cuts its own thread into the post)"),
  ("M3 x 10 set screw", 1, "gear onto the shaft's flat (cuts its own thread)"),
]""",
    """BOUGHT = [
  ("HIWIN MGN12H block on a 100 mm MGN12 rail (or any MGN12H block with a 100 mm rail cut to HIWIN's sizes)", 1,
   "the slide"),
  ("Lee Spring LCF 040 08 050S constant force spring (11.7 N, 12.7 mm wide)", 1, "pulls the motor in"),
  ("Omron SS-5GL2-F roller switch (the one already in the parts list)", 1, "power switch"),
  (S.COVER_SCREW, 1, "the plate's foot to the lower column cover's underside"),
  ("M3 x 6 button head screw", 4, "motor to motor bracket (a socket head can rub the gear)"),
  ("M3 x 6 socket head screw", 4, "motor bracket to the rail's block (heads sink into the bracket)"),
  ("M3 x 10 socket head screw", 6, "4: rail to mounting plate, with M3 nuts (the nuts sink into the plate's outer face); "
   "2: the spring's strip, through the bracket's tab from the 6 o'clock side into the strip clamp"),
  ("M3 nut", 4, "the rail's screws"),
  ("M2 x 12 screw + M2 nut", 2, "power switch to the plate (nuts slide in slots from the top)"),
  ("M4 x 20 socket head screw", 2, "the spool's axle (through a washer, cuts its own thread into the post), and the lever's "
   "pivot (in from the ear's inner end, into the nut in the outer lug)"),
  ("M4 washer", 2, "under the spool's axle head, and under the cover screw's head"),
  ("M4 nut", 1, "the lever's pivot, in the pocket in the ear's outer lug"),
  ("M3 x 10 set screw", 1, "gear onto the shaft's flat (cuts its own thread)"),
  ("silicone self-fusing tape (the roll already in the parts list)", 1, "one layer on the foot's top (or the top shim), "
   "where it meets the column cover"),
]""")
rep("""    ("Fixing the mounting plate. The plate isn't fixed to the car yet. What is under and beside the steering column at "
     "4 to 5 o'clock, 50 to 100 mm in from the steering wheel, that it can bolt to? A photo from below and one from "
     "the right side would do."),""",
    """    (f"The column cover. The plate's foot lies under the lower column cover's underside and is held by the cover's own "
     "screw under the key cylinder. It is drawn for that cover's front edge being between "
     f"{e['cover_front_range'][0]} and {e['cover_front_range'][1]} mm behind the back of the round part you hold at 5 "
     "o'clock, and the screw 32 to 35 mm behind that edge, 60 to 76 mm to the right of the column's middle. Measure the "
     "edge; if it is nearer the steering wheel than that, the motor's slide has no room there either, and I need to "
     "know."),""")
rep("""          "knob_forward_in_slot": (fwd(slot_y - S.KNOB_R), fwd(slot_y + S.KNOB_R))}""",
    """          "knob_forward_in_slot": (fwd(slot_y - S.KNOB_R), fwd(slot_y + S.KNOB_R)),
          "cover_front_range": tuple(round(SA.foot_fit(D)["cover's front edge behind the back of the round part (mm)"])
                                     for D in S.D_FOOT)}""")
rep("""    "side-strip-clamp": (S.strip_clamp(), (0, 90, 0), "flat", "none"),
    "side-steering-wheel-teeth": (parts["teeth"], (180, 0, 0), "on the channel's two front edges, the teeth up",
                                  "none in the channel: its inside corners are 45 degrees"),
  }""",
    """    "side-strip-clamp": (S.strip_clamp(), (0, 90, 0), "flat", "none"),
    "side-foot-bar": (S.from_wheel(S.foot_bar()).rotate((0, 0, 0)), (0, 0, 0), "flat (see below)", "none"),
    "side-foot-shim": (S.foot_shim(), (0, 0, 0), "flat", "none"),
  }


def teeth_file(n: int) -> str:
  t = S.SideTeeth(n_teeth=n)
  return f"side-steering-wheel-teeth-{round(t.teeth_half):02d}-{S.TEETH_SETS[n].replace(' ', '-')}"


def printed_teeth(parts: dict) -> dict:
  return {teeth_file(n): (st["teeth"], (180, 0, 0), "on the channel's two front edges, the teeth up",
                          "none in the channel: its inside corners are 45 degrees") for n, st in parts["sets"].items()}""")
p.write_text(s)
print("ok")
EOF
grep -n "def write_stls" -A 6 sidebuild.py | head -10