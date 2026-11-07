cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sidemock && python3 - <<'EOF'
import pathlib
p = pathlib.Path("motion.js")
s = p.read_text()
old_interp = s[s.index("  function interp(xs, ys, x) {"):s.index("  function stretchZ(")]
s = s.replace(old_interp, "")
s = s.replace("    G.pin = M.mul(BASE, M.tr(-pinBack(S.s), 0, 0));\n    G.moving = M.mul(BASE, M.tr(0, 0, -S.s));\n",
              "    G.moving = M.mul(BASE, M.tr(0, 0, -S.s));\n"
              "    const P = INFO.pivot;                 // the lever swings about its pin, towards the dash, by S.deg\n"
              "    G.lever = M.mul(G.moving, M.mul(M.tr(P[0], P[1], 0), M.mul(M.rz(-S.deg * D2R), M.tr(-P[0], -P[1], 0))));\n")
s = s.replace('const MOUNT_GROUPS = new Set(["fixed", "pin", "moving", "gear", "strip", "swlever", "teeth"]);',
              'const MOUNT_GROUPS = new Set(["fixed", "lever", "moving", "gear", "strip", "swlever", "teeth"]);')
s = s.replace("      latch: C([-36, 20, -8], window.__V_LATCH || [12, 155, 28]),",
              "      lever: C([-62, 28, -14], window.__V_LEVER || [-170, -60, 120]),")
for gone in ("pinBack", "G.pin", "latch", "interp"):
    assert gone not in s, gone
p.write_text(s)

p = pathlib.Path("labels.js")
s = p.read_text()
old = '    { text: "Latch knob", rank: 0, group: "pin", point: () => L.knob },'
assert old in s
s = s.replace(old, '    { text: "Lever", rank: 0, group: "lever", point: () => L.knob },')
p.write_text(s)

p = pathlib.Path("looks_state.js")
s = p.read_text()
assert s.count('"Rail, block, screws, plunger"') == 2
s = s.replace('"Rail, block, screws, plunger"', '"Rail, block, screws, pin"')
p.write_text(s)

p = pathlib.Path("side_export.py")
s = p.read_text()
old = '  ("lever", "swlever", "steel", sw["lever"]),'
assert old in s
s = s.replace(old, '  ("switch_lever", "swlever", "steel", sw["lever"]),')
p.write_text(s)
print("ok")
EOF
sed -n 14,40p motion.js