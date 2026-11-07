grep -n "M4_NUT\|M3_NUT_AF\|M3_NUT_T\|^M5_NUT" params.py mountparts.py | head -5 && python3 - <<'EOF'
import pathlib
p = pathlib.Path("sideparts.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)
rep("""  parts.append(box(x0, x1, PLATE_SLOT_Y - 0.01, -PP.Z_AXIS_P - FOOT_Z[0], TONGUE_R[0] - PP.R_FACE_P, TONGUE_R[1] - PP.R_FACE_P))""",
    """  parts.append(box(x0, x1, PLATE_SLOT_Y - 0.01, PP.Z_AXIS_P - FOOT_Z[0], TONGUE_R[0] - PP.R_FACE_P, TONGUE_R[1] - PP.R_FACE_P))""")
rep("""# The pivot is an M4 x 25 socket head screw (ISO 4762: head 7 across, 4 tall) in from the ear's inner end: its head
# sunk in the inner lug, its shank through the lug and the lever, its thread cut into a blind hole in the outer lug, so
# the ear's outer face (the switch's roller rides on it) stays whole. The screw carries no pull: snug, not tight.
PIVOT_SCREW_LEN, PIVOT_HEAD_D, PIVOT_HEAD_H = 25.0, 7.0, 4.0
PIVOT_CBORE = (PIVOT_HEAD_D + 0.6, PIVOT_HEAD_H + 0.2)            # the head's counterbore: across, deep
PIVOT_HEAD_Z = (EAR_Z[0] + 0.2, EAR_Z[0] + 0.2 + PIVOT_HEAD_H)    # the head sits here
PIVOT_END_Z = PIVOT_HEAD_Z[1] + PIVOT_SCREW_LEN                   # the screw's end: short of the ear's outer face
PIVOT_CLEAR_D, LEVER_BORE_D = 4.4, 4.3                            # clearance through the inner lug, the lever's bore""",
    """# The pivot is an M4 x 20 socket head screw (ISO 4762: head 7 across, 4 tall) in from the ear's inner end: its head
# sunk in the inner lug, its shank through the lug and the lever, into an M4 nut in a pocket in the outer lug's inner
# face (the lever's hub covers the pocket), so the ear's outer face (the switch's roller rides on it) stays whole. The
# screw carries no pull: snug, not tight, so the lever swings freely.
PIVOT_SCREW_LEN, PIVOT_HEAD_D, PIVOT_HEAD_H = 20.0, 7.0, 4.0
PIVOT_CBORE = (PIVOT_HEAD_D + 0.6, PIVOT_HEAD_H + 0.2)            # the head's counterbore: across, deep
PIVOT_HEAD_Z = (EAR_Z[0] + 0.2, EAR_Z[0] + 0.2 + PIVOT_HEAD_H)    # the head sits here
PIVOT_END_Z = PIVOT_HEAD_Z[1] + PIVOT_SCREW_LEN                   # the screw's end: short of the ear's outer face
PIVOT_CLEAR_D, LEVER_BORE_D = 4.4, 4.3                            # clearance through the lugs, the lever's bore
M4_NUT_AF, M4_NUT_T = 7.0, 3.2                                    # ISO 4032 M4 nut: across flats, thick
PIVOT_NUT_Z = (LEVER_Z[1] + LUG_GAP, LEVER_Z[1] + LUG_GAP + M4_NUT_T + 0.2)   # its pocket, from the outer lug's inner face""")
rep("""  part = part - teardrop_z(PIVOT_CBORE[0] / 2, EAR_Z[0] - 1.0, EAR_Z[0] + PIVOT_CBORE[1], PIVOT[0], PIVOT[1])
  part = part - teardrop_z(PIVOT_CLEAR_D / 2, EAR_Z[0] - 1.0, LEVER_Z[0] - LUG_GAP + 0.5, PIVOT[0], PIVOT[1])
  part = part - teardrop_z(M4_PILOT / 2, LEVER_Z[1] + LUG_GAP - 0.5, PIVOT_END_Z + 0.5, PIVOT[0], PIVOT[1])""",
    """  part = part - teardrop_z(PIVOT_CBORE[0] / 2, EAR_Z[0] - 1.0, EAR_Z[0] + PIVOT_CBORE[1], PIVOT[0], PIVOT[1])
  part = part - teardrop_z(PIVOT_CLEAR_D / 2, EAR_Z[0] - 1.0, LEVER_Z[0] - LUG_GAP + 0.5, PIVOT[0], PIVOT[1])
  part = part - teardrop_z(PIVOT_CLEAR_D / 2, LEVER_Z[1] + LUG_GAP - 0.5, PIVOT_END_Z + 0.8, PIVOT[0], PIVOT[1])
  nut_r = (M4_NUT_AF + 0.3) / 2 / math.cos(math.radians(30.0))
  part = part - Manifold.cylinder(PIVOT_NUT_Z[1] - PIVOT_NUT_Z[0] + 0.5, nut_r, nut_r, 6).translate(
    (PIVOT[0], PIVOT[1], PIVOT_NUT_Z[0] - 0.5))""")
rep("""def lever_screw() -> Manifold:
  \"\"\"The M4 x 25 pivot screw as fitted: head and shank (carrier frame, motor out).\"\"\"
  px, py = PIVOT
  return cyl(PIVOT_HEAD_D / 2, PIVOT_HEAD_Z[0], PIVOT_HEAD_Z[1], x=px, y=py, segments=32) + \\
    cyl(2.0, PIVOT_HEAD_Z[1] - 0.01, PIVOT_END_Z, x=px, y=py, segments=32)""",
    """def lever_screw() -> Manifold:
  \"\"\"The M4 x 20 pivot screw and its nut as fitted: head, shank, nut (carrier frame, motor out).\"\"\"
  px, py = PIVOT
  nut_r = M4_NUT_AF / 2 / math.cos(math.radians(30.0))
  return cyl(PIVOT_HEAD_D / 2, PIVOT_HEAD_Z[0], PIVOT_HEAD_Z[1], x=px, y=py, segments=32) + \\
    cyl(2.0, PIVOT_HEAD_Z[1] - 0.01, PIVOT_END_Z, x=px, y=py, segments=32) + \\
    Manifold.cylinder(M4_NUT_T, nut_r, nut_r, 6).translate((px, py, PIVOT_NUT_Z[0]))""")
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import sideparts as S, numpy as np
pl = S.side_plate(); print('plate bbox', np.round(pl.bounding_box(),1).tolist(), 'pieces', len(pl.decompose()), pl.status())
w = S.to_wheel(pl); print('plate wheel bbox', np.round(w.bounding_box(),1).tolist())
br = S.side_bracket(); print('bracket', np.round(br.bounding_box(),1).tolist(), len(br.decompose()), br.status())
print('screw', np.round(S.lever_screw().bounding_box(),1).tolist(), 'END', S.PIVOT_END_Z, 'nut z', S.PIVOT_NUT_Z)
print('ear overlap with screw', (br ^ S.lever_screw()).volume())
"
