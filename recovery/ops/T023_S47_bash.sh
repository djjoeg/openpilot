cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/recover && python3 - <<'EOF'
import json
calls = json.load(open("calls_ordered.json"))
for c in calls:
    if c["name"] == "Write" and c["input"]["file_path"].endswith("accord_lka_parts.py"):
        open("accord_lka_parts_v1.py", "w").write(c["input"]["content"])
        print("written", len(c["input"]["content"]))
EOF
wc -l accord_lka_parts_v1.py