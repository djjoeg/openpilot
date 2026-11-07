python3 - <<'EOF'
import pathlib, re
p = pathlib.Path("popparts.py")
s = p.read_text()
s = s.replace("MOUNT_ADJ = (2.0, 6.0)    # the whole mount", "MOUNT_ADJ = (3.0, 6.0)    # the whole mount")
s = s.replace("# (towards the key) and up (towards the stalk) when fitting it: about 3:24 to 3:08.", "# (towards the key) and up (towards the stalk) when fitting it: about 3:26 to 3:08.")
s2 = re.sub(r"^SHELF_X1 = 74\.0 +# the shelf under the flange, out to here \(the springs' front bolt swings past beyond\)",
            "SHELF_X1 = 86.0               # the shelf under the flange, out to here", s, flags=re.M)
assert s2 != s
p.write_text(s2)
print("ok")
EOF
grep -n "^SHELF_X1\|^MOUNT_ADJ" popparts.py && PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 5400 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2/run_u.py 2>&1 | grep -v "^   {\|flange fit" | tail -30