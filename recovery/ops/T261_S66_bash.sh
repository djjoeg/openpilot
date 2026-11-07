sed -n 30,42p visuals.py && /home/claude/bin/ruff check --fix --line-length 140 --select F401 rightcheck.py visuals.py -q; python3 - <<'EOF'
p = "visuals.py"
s = open(p).read()
a = '''  s = -1.0 if down else 1.0
'''
if s.count(a) == 1:
  s = s.replace(a, "")
  open(p, "w").write(s)
  print("removed unused s")
EOF
/home/claude/bin/ruff check --output-format concise --line-length 140 --select E9,F rightarm.py rightcheck.py visuals.py midteeth.py && PYTHONPATH=/home/claude/pylib timeout 600 python3 -c "import visuals, rightcheck; print('imports ok')"