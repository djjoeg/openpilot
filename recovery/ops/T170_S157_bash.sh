python3 - <<'EOF'
import pathlib
p = pathlib.Path("sideassembly.py"); s = p.read_text()
old = '"shims": int(round(gap_y / S.SHIM_T))}'
assert s.count(old) == 1
p.write_text(s.replace(old, '"shims": round(gap_y / S.SHIM_T)}'))
p = pathlib.Path("sidebuild.py"); s = p.read_text()
old = '''    "side-mounting-plate": (parts["plate"], (0, -90, 0), "on its outer face (the lever's knob side down); the foot rises "
                            "from it at 70 degrees", "none needed: hole and slot tops, and the window's top, a 28 mm bridge"),'''
new = '''    "side-mounting-plate": (parts["plate"], (0, -90, 0), ("on its outer face (the lever's knob side down); the foot rises "
                                                          "from it at 70 degrees"),
                            "none needed: hole and slot tops, and the window's top, a 28 mm bridge"),'''
assert s.count(old) == 1
p.write_text(s.replace(old, new))
EOF
/home/claude/bin/ruff check --output-format concise sideparts.py sideassembly.py sidebuild.py | tail -1 && md5sum ../stl/side-slide-mount/*.stl > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/stl_120.md5 && cp ../report/side_slide_report.txt /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/report_120_before.txt && (time PYTHONPATH=/home/claude/pylib python3 sidebuild.py > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/build10.log 2>&1; echo "exit $?" >> /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/build10.log) 2>> /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/build10.log &
echo started