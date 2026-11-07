python3 - << 'EOF'
p = "accord_lka_parts.py"
s = open(p).read()
a = """    parts[f"arms/arm-{L:05.1f}".replace(".0", "") if L != int(L) else f"arms/arm-{int(L):03d}"] = (arms[L], (0, 90, 0), "on its side", "none")"""
b = """    label = f"{int(L):03d}" if float(L).is_integer() else f"{L:05.1f}"
    parts[f"arms/arm-{label}"] = (arms[L], (0, 90, 0), "on its side", "none")"""
assert a in s; s = s.replace(a, b); open(p, "w").write(s)
EOF
rm -rf /home/claude/deliver/hardware/stl /home/claude/deliver/hardware/report; time PYTHONPATH=/home/claude/pylib python3 accord_lka_parts.py; echo "exit $?"