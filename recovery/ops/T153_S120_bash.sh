cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='slideparts.py'
s=open(p).read()
old_start=s.index('# ***** the power switch (as before: Omron SS-5GL2, push-on terminals) *****')
old_end=s.index('# ***** the motor plate (as the pop-off carrier\'s) *****')
new='''# ***** the power switch (as before: Omron SS-5GL2, push-on terminals) *****
# It lies flat behind the motor, its roller pointing across at the carrier's tongue, which has a land on its side: with
# the motor on the land holds the roller pressed; a millimetre off it starts down a 45 degree ramp and the switch lets go
# by 3 mm off (the teeth meeting tip to tip leave it 4.5 mm off: no power until the gear drops in). The switch's two
# screws sit in slots across (+- SW_SLOT): with the motor on, push it towards the tongue until it clicks, 0.6 mm more.
TONGUE_X = (-36.0, -30.0)                  # the carrier's tongue that works it, between the rods
TONGUE_Z = (-3.0, 3.0)
TONGUE_Y1 = 58.0                           # its back end (carrier on)
SW_ROLL_Y = 48.0                           # the switch's roller sits here (y), pressing the tongue's +x face
LAND_H = 4.0                               # the land on the tongue: this much proud ...
LAND_TOP_FROM = SW_ROLL_Y - 1.0            # ... from here back to the tongue's end (carrier on), a 45 degree ramp before it
SW_HOLES_X = TONGUE_X[1] + LAND_H + MP.SW_OP - MP.SW_PRESS   # the switch's holes' line (x), its roller towards -x
SW_SLOT = 2.0


'''
s=s[:old_start]+new+s[old_end:]
old_c='''  land = box(TONGUE_X[1] - 0.5, TONGUE_X[1] + LAND_H, LAND_FROM + LAND_H, TONGUE_Y1, TONGUE_Z[0], TONGUE_Z[1])
  ramp = Manifold.batch_hull([box(TONGUE_X[1] - 0.5, TONGUE_X[1] + 0.01, LAND_FROM, LAND_FROM + 0.01, TONGUE_Z[0], TONGUE_Z[1]),
                              box(TONGUE_X[1] - 0.5, TONGUE_X[1] + LAND_H, LAND_FROM + LAND_H, LAND_FROM + LAND_H + 0.01,
                                  TONGUE_Z[0], TONGUE_Z[1])])'''
new_c='''  land = box(TONGUE_X[1] - 0.5, TONGUE_X[1] + LAND_H, LAND_TOP_FROM, TONGUE_Y1, TONGUE_Z[0], TONGUE_Z[1])
  ramp = Manifold.batch_hull([box(TONGUE_X[1] - 0.5, TONGUE_X[1] + 0.01, LAND_TOP_FROM - LAND_H, LAND_TOP_FROM - LAND_H + 0.01,
                                  TONGUE_Z[0], TONGUE_Z[1]),
                              box(TONGUE_X[1] - 0.5, TONGUE_X[1] + LAND_H, LAND_TOP_FROM, LAND_TOP_FROM + 0.01,
                                  TONGUE_Z[0], TONGUE_Z[1])])'''
assert old_c in s
s=s.replace(old_c,new_c)
# switch window/plate positions follow SW_HOLES_X; the window's x range
s=s.replace("  part = part - box(TONGUE_X[1], WALL_X[1] + 12.0, SW_ROLL_Y - 6.0, SW_ROLL_Y + 6.0, -3.2, 3.2)",
            "  part = part - box(TONGUE_X[1], SW_HOLES_X - 4.0, SW_ROLL_Y - 6.0, SW_ROLL_Y + 6.0, -3.2, 3.2)")
open(p,'w').write(s)

p='slideassembly.py'
s=open(p).read()
start=s.index('def switch_states() -> list:')
end=s.index('import mountparts as _MP')
new='''def switch_states() -> list:
  """The switch's roller with the carrier this far off (mm): how far it has come back out from where it sits with the
  motor on (set 0.6 mm past its click). It lets go once that passes 0.6 mm plus the switch's own let-go travel (1.2)."""
  out = []
  for off in (-SP.PUSH_TRAVEL_ON, -1.0, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.5, SP.STROKE):
    top = SP.LAND_TOP_FROM + off
    if SP.SW_ROLL_Y >= top:
      out_mm = 0.0
    elif SP.SW_ROLL_Y <= top - SP.LAND_H:
      out_mm = SP.LAND_H
    else:
      out_mm = top - SP.SW_ROLL_Y
    state = "pressed" if out_mm <= 1e-6 else ("let go" if out_mm >= _MP.SW_PRESS + MP_SW["md"] else "between")
    out.append((round(off, 2), round(out_mm, 2), state))
  return out


'''
s=s[:start]+new+s[end:]
open(p,'w').write(s)
EOF
grep -n "LAND_FROM" /home/claude/deliver/hardware/cad/slideparts.py /home/claude/deliver/hardware/cad/slideassembly.py; cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache && timeout 900 python3 -c "
import sys; sys.path.insert(0,'/home/claude/deliver/hardware/cad')
import slideassembly as SA, slideparts as SP
print(SA.switch_states())
print('SW_HOLES_X', SP.SW_HOLES_X)
b=SP.slide_block(); c=SP.slide_carrier(); print(round(b.volume()), len(b.decompose()), round(c.volume()), len(c.decompose()))
"