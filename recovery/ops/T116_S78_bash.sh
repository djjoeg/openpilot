cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = "faceparts.py"
s = open(p).read()
old = """  m = cs.extrude(r1 - r0).translate((0, 0, r0))

  def warp(v):"""
new = """  # every edge short, so the flat facets the warp leaves follow the curve (the end faces at r0 and r1 included)
  m = cs.extrude(r1 - r0).translate((0, 0, r0)).refine_to_length(0.5)

  def warp(v):"""
assert old in s
s = s.replace(old, new)
# chamfer the teeth tips' inner and outer ends
old2 = """def teeth_trim(t: FaceTeeth) -> Manifold:"""
new2 = """def tip_chamfers(t: FaceTeeth, a0: float, a1: float) -> Manifold:
  \"\"\"The teeth's tips cut back 45 degrees at their inner and outer ends, 1 mm: lifting, the motor gear slides in
  across the teeth as it comes away.\"\"\"
  c = 1.0
  outer = revolve([(FACE_BAND[1] - c, t.z_tip - 0.5), (FACE_BAND[1] + 0.5, t.z_tip - 0.5), (FACE_BAND[1] + 0.5, t.z_tip + c + 0.5)],
                  a0, a1)
  inner = revolve([(FACE_BAND[0] + c, t.z_tip - 0.5), (FACE_BAND[0] - 0.5, t.z_tip - 0.5), (FACE_BAND[0] - 0.5, t.z_tip + c + 0.5)],
                  a0, a1)
  return outer + inner


def teeth_trim(t: FaceTeeth) -> Manifold:"""
assert old2 in s
s = s.replace(old2, new2)
old3 = """  body = body - tooth_spaces(t, -n, n) - teeth_trim(t) - ramps(t) - spoke_notch(t) - centre_mark(t)"""
new3 = """  body = body - tooth_spaces(t, -n, n) - teeth_trim(t) - tip_chamfers(t, -t.half - 1.0, t.half + 1.0) - ramps(t) - \\
    spoke_notch(t) - centre_mark(t)"""
assert old3 in s
s = s.replace(old3, new3)
# plate: clear the key cylinder at the front right top corner
old4 = """  for dz in PL_TIE_Z:
    z = front_z - dz
    part = part - box(PL_X[0] - 1, PL_X[1] + 1, y0 - PL_RIB_H - 1, y0 + 1.5, z - 4.0, z + 4.0)"""
new4 = """  for dz in PL_TIE_Z:
    z = front_z - dz
    part = part - box(PL_X[0] - 1, PL_X[1] + 1, y0 - PL_RIB_H - 1, y0 + 1.5, z - 4.0, z + 4.0)
  # the front right top corner cut back, clear of the key cylinder's bezel
  part = part - box(PL_X[1] - 13.0, PL_X[1] + 1.0, y1 - 4.0, y1 + 1.0, front_z - 4.0, front_z + 1.0)"""
assert old4 in s
s = s.replace(old4, new4)
open(p, "w").write(s)

p = "faceassembly.py"
s = open(p).read()
old5 = """  for fixed_name, fx in fixed:
    for mover_name, mover in movers:
      pairs[f"{mover_name}/{fixed_name}"] = (mover, fx)"""
new5 = """  for fixed_name, fx in fixed:
    for mover_name, mover in movers:
      if mover_name == "back teeth" and fixed_name in ("hub", "spoke sweep zone"):
        continue                     # parts of the steering wheel itself: the teeth turn with them
      pairs[f"{mover_name}/{fixed_name}"] = (mover, fx)"""
assert old5 in s
s = s.replace(old5, new5)
open(p, "w").write(s)
print("ok")
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/face && PYTHONPATH=/home/claude/pylib timeout 3000 python3 diag2.py && PYTHONPATH=/home/claude/pylib timeout 3000 python3 assy_test.py 2>&1 | tail -20