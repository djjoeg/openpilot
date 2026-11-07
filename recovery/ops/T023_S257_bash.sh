python3 - << 'EOF'
p = "accord_lka_parts.py"
s = open(p).read()
a = """  overlap_mm = WP.pitch_radius_tip_overlap() if hasattr(WP, "pitch_radius_tip_overlap") else \\
    (GR.pitch_radius(P.MOTOR_TEETH) + GR.MODULE) + (GR.pitch_radius(P.RING_TEETH) + GR.MODULE) - WP.centre_distance()"""
b = """  overlap_mm = (GR.pitch_radius(P.MOTOR_TEETH) + GR.MODULE) + (GR.pitch_radius(P.RING_TEETH) + GR.MODULE) - WP.centre_distance()"""
assert a in s; s = s.replace(a, b); open(p, "w").write(s)
EOF
time PYTHONPATH=/home/claude/pylib python3 accord_lka_parts.py --no-pictures 2>&1 | sed -n '/LIFT LEVER/,/SPRING/p;/PROBLEMS/,$p;/All checks/p'; ls -la ../report ../stl ../stl/arms | head -40