cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sidemock && python3 - <<'EOF'
import pathlib
p = pathlib.Path("side_export.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)
rep("""def ties() -> Manifold:
  rho = t.rho + 0.6""", """def ties(t=t) -> Manifold:
  rho = t.rho + 0.6""")
rep("""  ("teeth", "teeth", "teeth", A.teeth(0.0)),
  ("ties", "teeth", "tie", ties()),""",
    """  # the three teeth sets (the page shows one at a time): "teeth_<reach>"
  *[(f"teeth_{round(st['t'].teeth_half)}", "teeth", "teeth", st["teeth"].rotate((0, 0, S.MOUNT_DEG))) for st in parts["sets"].values()],
  *[(f"ties_{round(st['t'].teeth_half)}", "teeth", "tie", ties(st["t"])) for st in parts["sets"].values()],""")
rep("""  ("lever_pin", "moving", "steel", parts["lever's pin"]),
  ("lever", "lever", "knob", parts["lever"]),""",
    """  ("lever_screw", "moving", "steel", parts["lever's screw"]),
  ("lever", "lever", "knob", parts["lever"]),
  # the foot's bar, shims and the cover's screw, for the middle of the range of cover positions
  ("foot_bar", "fixed", "steel", S.from_wheel(S.foot_bar(FOOT_FIT["screw (x, z)"][1]))),
  ("foot_shims", "fixed", "plate", S.from_wheel(union([S.foot_shim().translate((0, k * S.SHIM_T, 0)) for k in range(FOOT_FIT["shims"])]))),
  ("cover_screw", "fixed", "steel", S.from_wheel(S.cover_screw(FOOT_FIT["screw (x, z)"][0], FOOT_FIT["screw (x, z)"][1], FOOT_FIT["underside y"]))),""")
rep("""parts = SA.build_parts()
A = SA.SideAssembly(parts)
t = A.t""", """parts = SA.build_parts()
A = SA.SideAssembly(parts)
t = A.t
FOOT_FIT = SA.foot_fit(sum(S.D_FOOT) / 2)""")
rep("""  "reach": round(t.teeth_half, 3), "half": round(t.half, 3), "pitch": round(t.pitch_deg, 4),""",
    """  "reach": round(t.teeth_half, 3), "half": round(t.half, 3), "pitch": round(t.pitch_deg, 4),
  "sets": {str(round(st["t"].teeth_half)): {"teeth": n, "reach": round(st["t"].teeth_half, 3), "half": round(st["t"].half, 3),
                                             "name": S.TEETH_SETS[n]} for n, st in parts["sets"].items()},
  "foot": {"x": S.FOOT_X, "y": S.FOOT_Y, "z": S.FOOT_Z, "window_x": S.WINDOW_X, "window_z": S.WINDOW_Z,
           "cover_front_range": [round(SA.foot_fit(D)["cover's front edge behind the back of the round part (mm)"]) for D in S.D_FOOT]},""")
rep("""    "knob": [S.PIVOT[0] - S.KNOB_D, S.PIVOT[1], sum(S.LEVER_Z) / 2],""",
    """    "knob": [S.PIVOT[0] - S.KNOB_D, S.PIVOT[1], sum(S.LEVER_Z) / 2],
    "foot": [float(v) for v in S.from_wheel(Manifold.cube((0.01, 0.01, 0.01)).translate((sum(S.FOOT_X) / 2, S.FOOT_Y[1], sum(S.FOOT_Z) / 2))).bounding_box()[:3]],""")
p.write_text(s)
print("ok")
EOF
grep -n "for name, group, look, m in meshes" side_export.py && PYTHONPATH=/home/claude/pylib python3 side_export.py . > export.log 2>&1; echo "exit $?"; tail -4 export.log