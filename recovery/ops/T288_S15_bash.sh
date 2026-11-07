python3 - <<'EOF'
p = "photorender.py"
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)
rep("ss=2, shadow_res=4096, ao_radius=22.0,", "ss=2, shadow_res=4096, soft_mm=2.5, ao_radius=22.0,")
rep("""  taps = [(0, 0)] + [(2.2 * math.cos(a), 2.2 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]] + \\
         [(4.4 * math.cos(a + 0.4), 4.4 * math.sin(a + 0.4)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]""",
    """  rad = soft_mm * scale
  taps = [(0, 0)] + [(0.5 * rad * math.cos(a), 0.5 * rad * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]] + \\
         [(rad * math.cos(a + 0.4), rad * math.sin(a + 0.4)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]""")
rep("  img = img.reshape(cam.H // ss if False else H // ss, ss, W // ss, ss, 3).mean(axis=(1, 3))",
    "  img = img.reshape(H // ss, ss, W // ss, ss, 3).mean(axis=(1, 3))")
open(p, "w").write(s)
print("ok")
EOF