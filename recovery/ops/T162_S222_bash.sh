python3 - <<'EOF'
def sub(p, old, new):
    s = open(p).read()
    assert s.count(old) == 1, (p, old, s.count(old))
    open(p, "w").write(s.replace(old, new))
sub("carscene.py", "from cadlib import box, cyl, revolve, union\n", "from cadlib import box, revolve, union\n")
sub("popparts.py", "  M5_NUT_AF,\n  M5_NUT_T,\n", "  M5_NUT_AF,\n")
sub("popparts.py", "  fx0, fy0, fx1, fy1 = fo[0][0], fo[0][1], fo[2][0], fo[2][1]\n", "  fy0, fy1 = fo[0][1], fo[2][1]\n")
sub("sideassembly.py", "  pin_at = lambda back: pin[0] + (pin[1] - pin[0]) * back / S.KIPP[\"pin_out\"]\n",
    "\n  def pin_at(back: float) -> float:\n    return pin[0] + (pin[1] - pin[0]) * back / S.KIPP[\"pin_out\"]\n\n")
sub("sidebuild.py", "  fwd = lambda y: round(back - (PP.Z_AXIS_P - y))   # carrier y -> mm forward of the back of the round part\n",
    "\n  def fwd(y: float) -> int:\n    return round(back - (PP.Z_AXIS_P - y))   # carrier y -> mm forward of the back of the round part\n\n")
sub("sideparts.py", "  rot = lambda m: m.rotate((0, 0, -90.0))\n", "\n  def rot(m: Manifold) -> Manifold:\n    return m.rotate((0, 0, -90.0))\n\n")
sub("slideparts.py", "extrude_x, hex_prism_x, hex_prism_y, sector, union", "extrude_x, sector, union")
EOF
grep -n "^from manifold3d\|^import\|Manifold" sideparts.py | head -5; /home/claude/bin/ruff check --isolated --output-format concise --line-length 140 --select E4,E7,E9,F . ; echo "exit $?"; /home/claude/bin/ruff check --output-format concise --line-length 140 sideparts.py sideassembly.py sidebuild.py; echo "exit $?"