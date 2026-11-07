cp sideparts.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/sideparts_v111.py && cp sideassembly.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/sideassembly_v111.py && cp sidebuild.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/sidebuild_v111.py && python3 - <<'EOF'
import pathlib
p = pathlib.Path("sideparts.py")
s = p.read_text()

def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)

# ----- docstring -----
rep("""  mounting plate  - fixed. Carries the rail, the lever's slot and its two notches, the power switch and the spring's
                    spool. How it fixes to the car is not drawn yet (see the report's questions).""",
    """  mounting plate  - fixed. Carries the rail, the lever's slot and its two notches, the power switch and the spring's
                    spool. A tongue at its dash end carries the foot: a flat plate that lies under the lower column
                    cover's underside and is held by the cover's own screw under the key cylinder (a longer one of the
                    same thread), through a window that takes the screw wherever it falls""")
rep("""  lever           - turns on a steel pin across the ear's fork; its arm runs out through the plate's slot to a knob""",
    """  lever           - turns on an M4 x 25 screw across the ear's fork (its head sunk in the inner lug, its thread cut
                    into the outer one); its arm runs out through the plate's slot to a knob
  foot pad        - a flat plate under the foot that bridges the window: the cover's screw goes through its slot
  foot shim       - the same outline, 2 mm thick; one to three between the foot and the cover's underside""")
rep("""  steering wheel teeth - the slide mount's short teeth, the inner end of every tooth pointed to match the gear

Bought: an MGN12H block on a 100 mm MGN12 rail; a 4 mm x 24 steel dowel pin (the lever's pivot); a Lee Spring LCF 040
08 050S constant force spring; the Omron SS-5GL2 power switch (as before).""",
    """  steering wheel teeth - three sets, the same piece with 10, 14 or 18 teeth (10.8, 15.2 or 19.5 degrees each way); the
                    inner end of every tooth pointed to match the gear

Bought: an MGN12H block on a 100 mm MGN12 rail; a Lee Spring LCF 040 08 050S constant force spring; the Omron SS-5GL2
power switch (as before); screws.""")

# ----- the lever's pivot: an M4 x 25 screw -----
rep("""EAR_Z = (-25.0, 0.0)              # its outer end (+z) presses the switch and meets the stop""",
    """EAR_Z = (-26.5, 0.0)              # its outer end (+z) presses the switch and meets the stop""")
rep("""LEVER_Z = (-17.0, -5.0)           # the lever's thickness, along the shaft (motor out)""",
    """LEVER_Z = (-18.5, -6.5)           # the lever's thickness, along the shaft (motor out)""")
rep("""PIN_D, PIN_LEN = 4.0, 24.0        # a steel dowel pin (ISO 8734), tapped in from the inner end
PIN_Z = (EAR_Z[0] + 0.2, EAR_Z[0] + 0.2 + PIN_LEN)                # its ends: 0.8 short of the ear's outer face
PIN_PRESS_D, PIN_SLIP_D, LEVER_BORE_D = 3.9, 4.1, 4.3             # holes: press in the inner lug, slip in the outer""",
    """# The pivot is an M4 x 25 socket head screw (ISO 4762: head 7 across, 4 tall) in from the ear's inner end: its head
# sunk in the inner lug, its shank through the lug and the lever, its thread cut into a blind hole in the outer lug, so
# the ear's outer face (the switch's roller rides on it) stays whole. The screw carries no pull: snug, not tight.
PIVOT_SCREW_LEN, PIVOT_HEAD_D, PIVOT_HEAD_H = 25.0, 7.0, 4.0
PIVOT_CBORE = (PIVOT_HEAD_D + 0.6, PIVOT_HEAD_H + 0.2)            # the head's counterbore: across, deep
PIVOT_HEAD_Z = (EAR_Z[0] + 0.2, EAR_Z[0] + 0.2 + PIVOT_HEAD_H)    # the head sits here
PIVOT_END_Z = PIVOT_HEAD_Z[1] + PIVOT_SCREW_LEN                   # the screw's end: short of the ear's outer face
PIVOT_CLEAR_D, LEVER_BORE_D = 4.4, 4.3                            # clearance through the inner lug, the lever's bore""")

rep("""  # the lever's pin: pressed into the inner lug from its inner end; a blind hole in the outer lug, so the ear's outer face
  # (the switch's roller rides on it) stays whole; room for the lever's hub and arm swinging into either notch
  part = part - teardrop_z(PIN_PRESS_D / 2, EAR_Z[0] - 1.0, LEVER_Z[0] - LUG_GAP + 0.5, PIVOT[0], PIVOT[1])
  part = part - teardrop_z(PIN_SLIP_D / 2, LEVER_Z[1] + LUG_GAP - 0.5, PIN_Z[1], PIVOT[0], PIVOT[1])
  part = part - lever_swing_room(0.5)""",
    """  # the lever's screw: its head sunk in the inner lug's inner end, a clearance hole through the lug, a pilot hole it cuts
  # its thread into in the outer lug (blind, so the ear's outer face, which the switch's roller rides on, stays whole);
  # room for the lever's hub and arm swinging into either notch
  part = part - teardrop_z(PIVOT_CBORE[0] / 2, EAR_Z[0] - 1.0, EAR_Z[0] + PIVOT_CBORE[1], PIVOT[0], PIVOT[1])
  part = part - teardrop_z(PIVOT_CLEAR_D / 2, EAR_Z[0] - 1.0, LEVER_Z[0] - LUG_GAP + 0.5, PIVOT[0], PIVOT[1])
  part = part - teardrop_z(M4_PILOT / 2, LEVER_Z[1] + LUG_GAP - 0.5, PIVOT_END_Z + 0.5, PIVOT[0], PIVOT[1])
  part = part - lever_swing_room(0.5)""")
rep("""def lever_pin() -> Manifold:
  return cyl(PIN_D / 2, PIN_Z[0], PIN_Z[1], x=PIVOT[0], y=PIVOT[1], segments=32)""",
    """def lever_screw() -> Manifold:
  \"\"\"The M4 x 25 pivot screw as fitted: head and shank (carrier frame, motor out).\"\"\"
  px, py = PIVOT
  return cyl(PIVOT_HEAD_D / 2, PIVOT_HEAD_Z[0], PIVOT_HEAD_Z[1], x=px, y=py, segments=32) + \\
    cyl(2.0, PIVOT_HEAD_Z[1] - 0.01, PIVOT_END_Z, x=px, y=py, segments=32)""")
rep("""  \"\"\"Carrier frame, motor out, latched: the hub on the pin, the arm straight out towards 4 o'clock, the knob.\"\"\"""",
    """  \"\"\"Carrier frame, motor out, latched: the hub on the screw, the arm straight out towards 4 o'clock, the knob.\"\"\"""")
rep("""PIVOT = (-29.25, 20.0)            # the pin's axis (x, y), along the shaft""",
    """PIVOT = (-29.25, 20.0)            # the screw's axis (x, y), along the shaft""")
rep("""# ***** the lever: on a pin across the bracket's ear, out through an L-shaped slot in the plate *****""",
    """# ***** the lever: on a screw across the bracket's ear, out through an L-shaped slot in the plate *****""")
rep("""  # the strip's two clamp screws, in from the tab's 6 o'clock side""", """  # the strip's two clamp screws, in from the tab's 6 o'clock side""")

# ----- the teeth sets -----
rep("""class SideTeeth(SP.SlideTeeth):
  \"\"\"The slide mount's short back teeth, centred on the motor at 5:20.\"\"\"
""", """TEETH_SETS = {10: "straight roads", 14: "highway", 18: "winding roads"}   # teeth on the piece: 10.8, 15.2, 19.5 degrees each way
N_PIECE_MIN = FP.N_TEETH_SHORT    # a set with fewer teeth keeps the 14-tooth piece's length: its zip tie slots need it


class SideTeeth(SP.SlideTeeth):
  \"\"\"The slide mount's back teeth, centred on the motor at 5:20: n_teeth of them (10, 14 or 18). The piece's length past
  the teeth (the smooth run-out, the ramps and the zip tie slots) is that of a piece with at least 14 teeth.\"\"\"

  def __init__(self, n_teeth: int = FP.N_TEETH_SHORT, **kw):
    super().__init__(n_teeth=n_teeth, **kw)
    n_piece = max(n_teeth, N_PIECE_MIN)
    self.roll_half = n_piece / 2 * self.pitch_deg + FP.ROLL_PAST_TEETH
    self.lead_end = self.roll_half + FP.END_LEAD_IN
    self.half = self.lead_end + self.chamfer_deg
    self.joint_deg = None
    self.reach_deg = round(self.teeth_half, 1)
""")
p.write_text(s)
print("ok")
EOF
grep -n "PIN_" sideparts.py sideassembly.py sidebuild.py | head