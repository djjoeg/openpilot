python3 - <<'EOF'
import pathlib
p = pathlib.Path("sideparts.py")
s = p.read_text()

def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)

# ----- the fixing constants, after the bumper section -----
rep("""# ***** the gear *****
GEAR_TEETH_Z = (7.0, 19.5)""", """# ***** the plate's fixing: the foot under the lower column cover, on the cover's own screw under the key cylinder *****
#
# Steering wheel frame (mm): z along the column towards you, 0 at the middle of the round part you hold; y up; x to your
# right. The lower column cover's underside is a level plane at COVER_Y (carscene.py: -100.5 to -106.9 over the range of
# D the design is drawn for), its screw under the key cylinder at CUP_X, CUP_Z (65.9 to 72, -120.5 to -137.6, each 4 mm
# either way). The plate's tongue runs on towards the dash along the plate's own plane, and the foot stands out from it
# level, 8 mm thick, its top FOOT_Y[1] just under the lowest underside; shims make up the rest. The window takes the
# screw wherever it falls (with the mount turned up to 3 degrees either way), and the foot bar under the foot bridges
# the window: the screw's head sits on the bar. The foot starts 2 mm behind where the bracket's tab reaches, slid in.
D_FOOT = (106.0, 125.0)           # the range of carscene.D the foot is drawn for (the cover's front edge at least 69 mm
                                  # behind the back of the round part you hold)
FOOT_Y = (-116.0, -108.0)         # the foot: its underside and its top
FOOT_X = (46.0, 95.0)             # ... across: its left end clear of the cover on the back of the steering wheel, its
                                  # right end clear of the lever's knob
FOOT_Z = (-150.0, -110.5)         # ... along the column: from 2 mm behind the bracket's tab, slid in, to well past the screw
WINDOW_X, WINDOW_Z = (54.0, 84.0), (-143.0, -115.0)   # the screw's window
TONGUE_R = (136.0, 160.0)         # the tongue: the plate's plane, this band of radius, out to the foot's far end
BAR = (40.0, 8.0, 6.0)            # the foot bar: across (x), along (z), thick; its slot along x takes the screw
BAR_SLOT_W = 4.5
SHIM_T = 2.0                      # a shim: the foot's outline and window, this thick
COVER_SCREW = "the cover's own 4 mm tapping screw under the key cylinder, 15 mm longer (the same thread), with an M4 washer"
FOOT_CLAMP_N = 400.0              # the screw's clamp on the foot: an estimate on the low side (a small tapping screw tightened by hand)

# ***** the gear *****
GEAR_TEETH_Z = (7.0, 19.5)""")

# ----- helpers: wheel frame -> carrier frame -----
rep("""def to_wheel(m: Manifold, mount_deg: float = MOUNT_DEG) -> Manifold:
  Rm = PP.rot_z(mount_deg)
  return PP.place(m, Rm @ PP.R_POP, Rm @ np.array([PP.R_FACE_P, 0.0, PP.Z_AXIS_P]))
""", """def to_wheel(m: Manifold, mount_deg: float = MOUNT_DEG) -> Manifold:
  Rm = PP.rot_z(mount_deg)
  return PP.place(m, Rm @ PP.R_POP, Rm @ np.array([PP.R_FACE_P, 0.0, PP.Z_AXIS_P]))


def from_wheel(m: Manifold, mount_deg: float = MOUNT_DEG) -> Manifold:
  \"\"\"The inverse of to_wheel: a steering-wheel-frame part into the carrier frame.\"\"\"
  Rm = PP.rot_z(mount_deg)
  R = Rm @ PP.R_POP
  T = Rm @ np.array([PP.R_FACE_P, 0.0, PP.Z_AXIS_P])
  return PP.place(m, R.T, -(R.T @ T))


def wheel_point(x: float, y: float, z: float, mount_deg: float = MOUNT_DEG) -> np.ndarray:
  \"\"\"A carrier-frame point in the steering wheel frame.\"\"\"
  Rm = PP.rot_z(mount_deg)
  return Rm @ PP.R_POP @ np.array([x, y, z]) + Rm @ np.array([PP.R_FACE_P, 0.0, PP.Z_AXIS_P])
""")

# ----- the plate: tongue + foot + window -----
rep("""  part = union(parts)
  # the rail's four M3 x 12 screws: slots along the rail, nuts sunk in the outer face""",
    """  # the tongue towards the dash, in the plate's plane, and the foot standing out from it under the column cover
  parts.append(box(x0, x1, PLATE_SLOT_Y - 0.01, -PP.Z_AXIS_P - FOOT_Z[0], TONGUE_R[0] - PP.R_FACE_P, TONGUE_R[1] - PP.R_FACE_P))
  parts.append(foot_block())
  part = union(parts)
  part = part - from_wheel(box(WINDOW_X[0], WINDOW_X[1], FOOT_Y[0] - 1.0, FOOT_Y[1] + 1.0, WINDOW_Z[0], WINDOW_Z[1]))
  # the rail's four M3 x 12 screws: slots along the rail, nuts sunk in the outer face""")
rep("""# ***** the lever *****

def lever_room(""", """def foot_block() -> Manifold:
  \"\"\"The foot (carrier frame): a level slab under the column cover, drawn in the steering wheel frame.\"\"\"
  return from_wheel(box(FOOT_X[0], FOOT_X[1], FOOT_Y[0], FOOT_Y[1], FOOT_Z[0], FOOT_Z[1]))


def foot_bar(z_screw: float | None = None) -> Manifold:
  \"\"\"The foot bar (steering wheel frame): under the foot, across the window, at the screw's z (the window's middle if
  not given); its slot along x takes the screw anywhere across the window.\"\"\"
  bw, bl, bt = BAR
  zs = z_screw if z_screw is not None else sum(WINDOW_Z) / 2
  xm = sum(WINDOW_X) / 2
  bar = box(xm - bw / 2, xm + bw / 2, FOOT_Y[0] - bt, FOOT_Y[0], zs - bl / 2, zs + bl / 2)
  slot = Manifold.batch_hull([cyl_y(BAR_SLOT_W / 2, FOOT_Y[0] - bt - 1.0, FOOT_Y[0] + 1.0, x=x, z=zs, segments=24)
                              for x in WINDOW_X])
  return clean(bar - slot)


def foot_bar_sweep() -> Manifold:
  \"\"\"Everywhere the foot bar can be (carrier frame): the screw anywhere along the window.\"\"\"
  bw, bl, bt = BAR
  xm = sum(WINDOW_X) / 2
  return from_wheel(box(xm - bw / 2, xm + bw / 2, FOOT_Y[0] - bt, FOOT_Y[0], WINDOW_Z[0] - bl / 2, WINDOW_Z[1] + bl / 2))


def foot_shim() -> Manifold:
  \"\"\"A shim (steering wheel frame): the foot's outline and window, SHIM_T thick, on the foot's top.\"\"\"
  sh = box(FOOT_X[0], FOOT_X[1], FOOT_Y[1], FOOT_Y[1] + SHIM_T, FOOT_Z[0], FOOT_Z[1])
  return clean(sh - box(WINDOW_X[0], WINDOW_X[1], FOOT_Y[1] - 1.0, FOOT_Y[1] + SHIM_T + 1.0, WINDOW_Z[0], WINDOW_Z[1]))


def cover_screw(x: float, z: float, cover_y: float) -> Manifold:
  \"\"\"The cover's screw as fitted (steering wheel frame): its shank from the bar up into the cover, its head under the bar.\"\"\"
  bt = BAR[2]
  return cyl_y(2.0, FOOT_Y[0] - bt - 0.01, cover_y + 12.0, x=x, z=z, segments=24) + \\
    cyl_y(4.0, FOOT_Y[0] - bt - 2.8, FOOT_Y[0] - bt, x=x, z=z, segments=24)


# ***** the lever *****

def lever_room(""")
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import sideparts as S, numpy as np
pl = S.side_plate(); print('plate bbox', np.round(pl.bounding_box(),1).tolist(), 'pieces', len(pl.decompose()), 'status', pl.status())
fb = S.foot_block(); print('foot', np.round(fb.bounding_box(),1).tolist())
print('tongue top r', S.TONGUE_R, 'foot top y', S.FOOT_Y[1])
w = S.to_wheel(pl); print('plate wheel bbox', np.round(w.bounding_box(),1).tolist())
print('bar', np.round(S.foot_bar().bounding_box(),1).tolist(), 'shim', np.round(S.foot_shim().bounding_box(),1).tolist())
br = S.side_bracket(); print('bracket', np.round(br.bounding_box(),1).tolist(), len(br.decompose()), br.status())
lv = S.side_lever(); print('lever', np.round(lv.bounding_box(),1).tolist())
print('screw', np.round(S.lever_screw().bounding_box(),1).tolist())
"
