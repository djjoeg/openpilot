python3 - <<'EOF'
import pathlib
p = pathlib.Path("sideassembly.py")
s = p.read_text()
old = """       f"a jolt over {lift_g:.1f} times gravity along the slide lifts the arm off the floor for a moment; if the lever ever "
       "works its way out, the spring pulls the motor in and the power goes off"),"""
new = """       (f"a jolt over {lift_g:.1f} times gravity along the slide lifts the arm off the floor for a moment; if the lever "
        "ever works its way out, the spring pulls the motor in and the power goes off")),"""
assert s.count(old) == 1; s = s.replace(old, new)
old = """       "with the spring working nothing holds the lever there and its weight swings it back into the slot: no harm, the "
       "spring holds the motor in")):"""
new = """       ("with the spring working nothing holds the lever there and its weight swings it back into the slot: no harm, "
        "the spring holds the motor in"))):"""
assert s.count(old) == 1; s = s.replace(old, new)
p.write_text(s)
p = pathlib.Path("sideparts.py")
s = p.read_text()
old = "                for a0, a1 in zip(angles[:-1], angles[1:])])"
assert s.count(old) == 1
s = s.replace(old, "                for a0, a1 in itertools.pairwise(angles)])")
if "import itertools" not in s:
    s = s.replace("import math\n", "import itertools\nimport math\n", 1)
p.write_text(s)
EOF
grep -n "^import" sideparts.py | head; sed -i 's/^PETG_DENSITY = 1.27$/PETG_DENSITY = 1.28     # g\/cm^3, Bambu Lab PETG HF data sheet (V1.0), as the other mounts/' sidebuild.py; grep -n "PETG_DENSITY =" sidebuild.py; ruff check sideassembly.py sidebuild.py sideparts.py --output-format concise