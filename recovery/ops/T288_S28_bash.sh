python3 - <<'EOF'
p = "carphoto.py"
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)
rep("  big = box(-700.0, 700.0, -600.0, 400.0, sc.dash_z - 40.0, sc.dash_z)", "  big = box(-900.0, 900.0, -1400.0, 400.0, sc.dash_z - 40.0, sc.dash_z)")
rep("PETG = PR.Mat((0.15, 0.155, 0.165), spec=0.08, shine=60)          # grey PETG", "PETG = PR.Mat((0.11, 0.115, 0.125), spec=0.08, shine=60)          # grey PETG")
rep("key_power=2.2, sky_up=WORLD_UP, ambient=0.9,", "key_power=2.0, sky_up=WORLD_UP, ambient=0.9,")
open(p, "w").write(s)
print("ok")
EOF
(time PYTHONPATH=/home/claude/pylib timeout 3000 python3 carphoto.py 1600) 2>&1 | tail -5