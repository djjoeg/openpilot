cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='/home/claude/deliver/hardware/cad/slideassembly.py'
s=open(p).read()
s=s.replace("def check_fit(A: SlideAssembly, wheel_step: float = 4.0, slide_step: float = 1.1) -> dict:",
            "def check_fit(A: SlideAssembly, wheel_step: float = 4.0, lever_step: float = 5.0) -> dict:")
s=s.replace("    for d in np.arange(SP.LEVER_SWING, -0.01, -2.5):","    for d in np.arange(SP.LEVER_SWING, -0.01, -lever_step):")
open(p,'w').write(s)
print(s.count("lever_step"))
EOF