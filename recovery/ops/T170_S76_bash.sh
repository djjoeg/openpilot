sed -i 's|    "side-mounting-plate-draft": (parts\["plate"\], (0, -90, 0), "on its outer face (the lever'"'"'s knob side down)",\n                                  "none needed: only hole and slot tops overhang"),|X|' sidebuild.py && python3 - <<'EOF'
import pathlib
p = pathlib.Path("sidebuild.py")
s = p.read_text()
old = """    "side-mounting-plate-draft": (parts["plate"], (0, -90, 0), "on its outer face (the lever's knob side down)",
                                  "none needed: only hole and slot tops overhang"),"""
new = """    "side-mounting-plate": (parts["plate"], (0, -90, 0), "on its outer face (the lever's knob side down); the foot rises "
                            "from it at 70 degrees", "none needed: hole and slot tops, and the window's top, a 28 mm bridge"),"""
assert s.count(old) == 1
s = s.replace(old, new)
s = s.replace('"side-mounting-plate-draft', '"side-mounting-plate')
p.write_text(s)
print("ok")
EOF
grep -n "draft" sidebuild.py sideparts.py sideassembly.py | head; rm -f /home/claude/deliver/hardware/stl/side-slide-mount/side-mounting-plate-draft.stl /home/claude/deliver/hardware/stl/side-slide-mount/side-steering-wheel-teeth.stl; ls /home/claude/deliver/hardware/stl/side-slide-mount/