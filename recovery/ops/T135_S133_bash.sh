cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/popmock && python3 - <<'EOF'
import json, pathlib, re, sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
sys.path.insert(0, "/home/claude/pylib")
import popparts as PP
v = (PP.BLOCK_KNUCKLE_X[0] + PP.BLOCK_KNUCKLE_X[1]) / 2.0
print("block knuckle x", v)
ex = pathlib.Path("pop_export.py")
t = ex.read_text()
old = '"spring_x": PP.SPRING_X,'
assert t.count(old) == 1
t = t.replace(old, '"spring_x": PP.SPRING_X, "block_knuckle_x": (PP.BLOCK_KNUCKLE_X[0] + PP.BLOCK_KNUCKLE_X[1]) / 2.0,')
ex.write_text(t)
d = json.load(open("data.json"))
d["block_knuckle_x"] = v
json.dump(d, open("data.json", "w"))
print("ok")
EOF
python3 build.py && timeout 300 python3 shot.py 2>&1 | grep -v "GPU stall" | tail -5