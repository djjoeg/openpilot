python3 - <<'EOF'
p='faceassembly.py'
s=open(p).read()
old="import assembly as AS\nimport columnassembly as CA\nimport faceparts as FP\nimport mountparts as MP\n"
new="import assembly as AS\nimport columnassembly as CA\nimport faceparts as FP\nimport gears as GR\nimport mountparts as MP\nimport params as P\n"
assert s.count(old)==1
s=s.replace(old,new)
open(p,'w').write(s)
EOF
/home/claude/bin/ruff check --isolated --select E,F --line-length 140 --output-format concise . ; echo "exit $?"; PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0,'.')
import faceassembly as FA
for r in FA.fastener_rows(): print(r['bolt'], '|', r['use'], r['ok'])
"