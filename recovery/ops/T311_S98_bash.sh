cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='viewer3d.py'; s=open(p).read()
rep=[
('M_PLATE = [mv(1, 0.0, 1.0, (0.0, -70.0, 0.0))]', 'M_PLATE = [mv(1, 0.0, 1.0, (0.0, -55.0, 0.0))]'),
('M_TEETH = [mv(2, 0.0, 0.6, (0.0, 0.0, -55.0))]', 'M_TEETH = [mv(2, 0.0, 0.6, (0.0, 0.0, -45.0))]'),
('M_ARM = [mv(3, 0.0, 0.5, (95.0, 0.0, 0.0))]', 'M_ARM = [mv(3, 0.0, 0.5, (80.0, 0.0, 0.0))]'),
('M_CARRIER = [mv(7, 0.0, 0.5, scale(60.0, V3)),', 'M_CARRIER = [mv(7, 0.0, 0.5, scale(45.0, V3)),'),
('motor_moves = M_CARRIER + [mv(5, 0.0, 0.35, scale(45.0, U3))]', 'motor_moves = M_CARRIER + [mv(5, 0.0, 0.35, scale(35.0, U3))]'),
('M_CARRIER + [mv(5, 0.35, 0.6, scale(-18.0, U3))]', 'M_CARRIER + [mv(5, 0.35, 0.6, scale(-15.0, U3))]'),
('M_CARRIER + [mv(5, 0.6, 1.0, scale(-30.0, U3))]', 'M_CARRIER + [mv(5, 0.6, 1.0, scale(-25.0, U3))]'),
('M_PLATE + [mv(3, 0.75, 1.0, (0.0, 0.0, -30.0))]', 'M_PLATE + [mv(3, 0.75, 1.0, (0.0, 0.0, -25.0))]'),
('M_PLATE + [mv(3, 0.5, 0.75, (0.0, -25.0, 0.0))]', 'M_PLATE + [mv(3, 0.5, 0.75, (0.0, -20.0, 0.0))]'),
('M_ARM + [mv(4, 0.4, 1.0, scale(32.0, U3)), mv(7, 0.75, 1.0, scale(8.0, U3))]', 'M_ARM + [mv(4, 0.4, 1.0, scale(28.0, U3)), mv(7, 0.75, 1.0, scale(8.0, U3))]'),
('M_ARM + [mv(4, 0.0, 0.4, (0.0, 0.0, 30.0))]', 'M_ARM + [mv(4, 0.0, 0.4, (0.0, 0.0, 25.0))]'),
('M_CARRIER + [mv(6, 0.35, 1.0, (0.0, 0.0, -35.0))]),\n    ("snut"', 'M_CARRIER + [mv(6, 0.35, 1.0, (0.0, 0.0, -30.0))]),\n    ("snut"'),
('M_CARRIER + [mv(6, 0.0, 0.3, (0.0, 0.0, 20.0))]', 'M_CARRIER + [mv(6, 0.0, 0.3, (0.0, 0.0, 15.0))]'),
('     M_CARRIER + [mv(6, 0.35, 1.0, (0.0, 0.0, -35.0))]),\n  ]', '     M_CARRIER + [mv(6, 0.35, 1.0, (0.0, 0.0, -30.0))]),\n  ]'),
('"overview": {"target": centre, "dir": [0.85, -0.55, -0.3], "dist": 470}', '"overview": {"target": centre, "dir": [0.85, -0.55, -0.3], "dist": 500}'),
]
for a,b in rep:
  assert a in s, a[:60]; s=s.replace(a,b)
open(p,'w').write(s)
EOF
grep -n "mv(" viewer3d.py | head -40 | cut -c1-150 && ruff check viewer3d.py --output-format concise && export PYTHONPATH=/home/claude/pylib && timeout 600 python3 viewer3d.py && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v3d && python3 wrap.py /home/claude/deliver/hardware/report/arm-3d.html page2.html