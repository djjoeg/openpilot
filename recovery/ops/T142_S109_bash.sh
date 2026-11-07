cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/popmock && cp pop_export.py pop_export_v1.py && python3 - <<'EOF'
import pathlib
p = pathlib.Path("pop_export.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)
rep('''short_piece = PA.cached(f"mock_short_{t15.rr:.1f}_{t15.z_axis:.2f}", lambda: PP.pop_pieces(t15)["one-piece"])
long_piece = PA.cached(f"mock_long_{t45.rr:.1f}_{t45.z_axis:.2f}", lambda: PP.pop_pieces(t45)["one-piece"])''',
'''short_piece = PA.cached(f"mock_short_{t15.rr:.1f}_{t15.z_axis:.2f}_{t15.mount_deg:.1f}_adj{PP.MOUNT_ADJ:.0f}", lambda: PP.pop_pieces(t15)["one-piece"])
long_piece = PA.cached(f"mock_long_{t45.rr:.1f}_{t45.z_axis:.2f}_{t45.mount_deg:.1f}_adj{PP.MOUNT_ADJ:.0f}", lambda: PP.pop_pieces(t45)["one-piece"])''')
rep('''A = PA.PopAssembly(t15, {"teeth": short_piece})''', '''A = PA.PopAssembly(t15, {"teeth": short_piece, "tab": PP.pop_screw_tab(), "plate": plate})''')
rep('''def tilt_lever() -> Manifold:
  """The tilt lever tucked up under the column (rough, from the photos): an arm back to its pivot and a paddle."""
  arm = box(-30.0, -18.0, -58.0, -52.0, -150.0, -70.0)
  paddle = box(-40.0, -8.0, -66.0, -52.0, -85.0, -55.0)
  return arm + paddle''',
'''def tilt_lever() -> Manifold:
  """The adjustment tab tucked up under the column (rough, from the photos): its handle and the steel arm behind it."""
  handle = Manifold.batch_hull([box(-41.0, 3.0, -61.0, -50.0, -118.0, -66.0), cyl(5.5, -66.0, -60.0, -19.0, -56.0, 24).rotate((0, 0, 0))])
  handle = box(-41.0, 3.0, -61.0, -50.0, -118.0, -62.0) + box(-41.0, 3.0, -64.0, -58.0, -66.0, -60.0)
  arm = box(-26.0, -12.0, -55.0, -50.0, -186.0, -116.0)
  return handle + arm


def key_head() -> Manifold:
  """The key in the ignition: a flat head along the key's axis out of the bezel."""
  kd = np.array(P.KEY_TO) - np.array(P.KEY_FROM)
  kd /= np.linalg.norm(kd)
  a = np.array(P.KEY_TO)
  head = Manifold.batch_hull([cyl(17.0, 0.0, 3.5, 0.0, 22.0, 32), cyl(9.0, 0.0, 3.5, 0.0, 40.0, 24)]).translate((0, 0, -1.75))
  blade = box(-4.0, 4.0, 2.0, 22.0, -1.0, 1.0)
  local = (head + blade).rotate((0, 0, 90))            # the key turned to ON: its head across
  # local: y along the key, z through its thickness -> place y along kd
  y = kd
  x = np.cross(y, [0.0, 1.0, 0.0]); x /= np.linalg.norm(x)
  z = np.cross(x, y)
  R = np.stack([x, y, z], axis=1)
  return PP.place(local.rotate((0, 0, -90)), R, a)''')
rep('''def flange_bolts() -> Manifold:
  out = []
  for bx, by in PP.FLANGE_BOLTS:
    z0, z1 = PP.PLATE_FLANGE_Z[0] - 6.0, PP.BLOCK_FLANGE_Z[1]''',
'''def flange_bolts() -> Manifold:
  out = []
  for bx, by in PP.flange_bolts_wheel():
    z0, z1 = PP.plate_flange_z()[0], PP.block_flange_z()[1]''')
rep('''  ("tilt_lever", "car", "stalk", tilt_lever()),''', '''  ("tilt_lever", "car", "lever", tilt_lever()),
  ("key_head", "car", "key", key_head()),''')
rep('''  ("hinge_block", "world", "hinge_block", PP.to_wheel(block)),
  ("switch", "world", "switch", PP.to_wheel(PP.switch_body_pop())),
  ("plate", "world", "plate", plate),
  ("plate_pads", "world", "rubber", PP.pop_plate_pads()),
  ("flange_bolts", "world", "steel", flange_bolts()),
  ("b_bolt", "world", "steel", PP.to_wheel(through_bolt(*PP.B_BOLT) + hinge_bolt())),''',
'''  ("hinge_block", "block", "hinge_block", PP.to_wheel(block)),
  ("switch", "block", "switch", PP.to_wheel(PP.switch_body_pop())),
  ("flange_bolts", "block", "steel", flange_bolts()),
  ("b_bolt", "block", "steel", PP.to_wheel(through_bolt(*PP.B_BOLT) + hinge_bolt())),
  ("plate", "world", "plate", plate),
  ("tabs", "world", "tab", A.tabs()),
  ("tab_bolts", "world", "steel", A.tab_bolts()),''')
rep('''  "ratio": FP.FACE_RATIO, "mesh_phase": PA.MESH_PHASE, "mount_deg": PP.MOUNT_DEG,''',
'''  "ratio": FP.FACE_RATIO, "mesh_phase": PA.MESH_PHASE, "mount_deg": PP.MOUNT_DEG, "mount_adj": PP.MOUNT_ADJ,
  "stalk_down": PA.STALK_DOWN_DEG,''')
p.write_text(s)
print("ok")
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/popmock && PYTHONPATH=/home/claude/pylib timeout 3000 python3 pop_export.py . 2>&1 | tail -40