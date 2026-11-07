python3 - <<'EOF'
import re
p = "rightcheck.py"
s = open(p).read()
s = s.replace("    for dz in (0.0, RA.DZ_END):\n", "    for dz in (0.0, RA.DZ_OUT):\n")
s = s.replace("""  # 2. the carrier goes in: with the motor on it, slid out, it comes in sideways from the motor's side (+v) into the
  # channel, past nothing
  for dz in (RA.DZ_OUT, RA.DZ_END):
""", """  # 2. the carrier goes in: with the motor on it, slid out (6 mm and all the way), it comes in sideways from the
  # motor's side (+v) into the channel, past nothing
  for dz in (-6.0, RA.DZ_OUT):
""")
s = s.replace("np.arange(RA.DZ_END, RA.DZ_DEEP + 0.5, 1.0)", "np.arange(RA.DZ_OUT, RA.DZ_DEEP + 0.5, 1.0)")
s = s.replace("""  # depth, the carrier at its stop, slid out 10 and on the tower's top; against the parts and the motor (their""",
              """  # depth, the carrier at its stop and slid all the way out (on the tower's top); against the parts and the motor (their""")
s = s.replace("    for slid in (s, RA.DZ_OUT, RA.DZ_END):\n", "    for slid in (s, RA.DZ_OUT):\n")
assert "DZ_END" not in s, [l for l in s.splitlines() if "DZ_END" in l]
open(p, "w").write(s)
p = "visuals.py"
s = open(p).read()
s = s.replace("near = [assembly_parts(dz=0.0), assembly_parts(dz=RA.DZ_END), assembly_parts(dz=RA.DZ_END, off=off)]",
              "near = [assembly_parts(dz=0.0), assembly_parts(dz=RA.DZ_OUT), assembly_parts(dz=RA.DZ_OUT, off=off)]")
s = s.replace("""f"OUT: push bolt loosened, motor slid down until the carrier sits on the tower ({-RA.DZ_END:.0f} mm; \"""",
              """f"OUT: push bolt loosened, motor slid down until the carrier sits on the tower ({-RA.DZ_OUT:.0f} mm; \"""")
assert "DZ_END" not in s, [l for l in s.splitlines() if "DZ_END" in l]
open(p, "w").write(s)
print("ok")
EOF
grep -n "DZ_OUT\|DZ_END" rightcheck.py visuals.py rightarm.py