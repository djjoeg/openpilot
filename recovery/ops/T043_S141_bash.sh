python3 - <<'EOF'
s = open('accord_lka_parts.py').read()
old = '''    report["pictures"] = ["assembly-side.png", "assembly-3d.png", "parts.png", "lift-lever-section.png"]'''
new = '''    report["pictures"] = ["assembly-side.png", "assembly-3d.png", "lift-lever-section.png"] + \\
      sorted(f for f in os.listdir(args.report) if f.startswith("parts-") and f.endswith(".png"))'''
assert old in s
s = s.replace(old, new)
open('accord_lka_parts.py', 'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 1800 python3 accord_lka_parts.py --out /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/lever2/stl --report /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/lever2/report --no-pictures 2>&1 | sed -n '1,20p;/^GEARS/,$p'