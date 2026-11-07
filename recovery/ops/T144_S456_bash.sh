cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/popmock && python3 - <<'EOF'
s = open('pop.src.html').read()
old = """    key: { eye: [INFO.key.centre[0] + 330 * INFO.key.n[0], INFO.key.centre[1] + 330 * INFO.key.n[1] + 40, INFO.key.centre[2] + 330 * INFO.key.n[2]], target: INFO.key.centre },"""
new = """    key: { eye: [INFO.key.centre[0] + 290 * INFO.key.radial[0], INFO.key.centre[1] + 290 * INFO.key.radial[1] + 50, INFO.key.centre[2] - 40], target: INFO.key.centre },"""
assert old in s
s = s.replace(old, new)
open('pop.src.html', 'w').write(s)
e = open('pop_export.py').read()
old = '''          "n": [float(v) for v in CR._frame(CR.KEY_CLOCK_DEG, CR.KEY_TILT_DEG)[0]]},'''
new = '''          "n": [float(v) for v in CR._frame(CR.KEY_CLOCK_DEG, CR.KEY_TILT_DEG)[0]],
          "radial": [math.cos(math.radians(CR.KEY_CLOCK_DEG)), math.sin(math.radians(CR.KEY_CLOCK_DEG)), 0.0]},'''
assert old in e
e = e.replace(old, new)
open('pop_export.py', 'w').write(e)
EOF
PYTHONPATH=/home/claude/pylib timeout 1700 python3 pop_export.py . 2>&1 | tail -1 && python3 build.py && timeout 300 python3 shot6.py