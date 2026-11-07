python3 - <<'EOF'
p = 'viewer3d_page.html'
s = open(p, encoding='utf-8').read()
a = 'text.textContent = "The motor slid up against its stop, the gear in the teeth: lane keeping on. Press Back, or slide left, to take it apart in the order it goes together.";'
b = 'text.textContent = "The motor slid up the groove by its wing bolt, the gear in the teeth: lane keeping on. Press Back, or slide left, to take it apart in the order it goes together.";'
assert s.count(a) == 1
open(p, 'w', encoding='utf-8').write(s.replace(a, b))
print('ok')
EOF
grep -rn "stop" viewer3d_page.html | grep -v "stopPropagation\|desktop\|stop-color" | head -5; PYTHONPATH=/home/claude/pylib python3 viewer3d.py 2>&1 | tail -1