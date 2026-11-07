python3 - <<'EOF'
p='accord_lka_parts.py'
s=open(p).read()
old='''def text_report(r: dict) -> str:
'''
i=s.index(old)
# insert after the docstring if any
j=s.index('\n',i)+1
rest=s[j:]
if rest.lstrip().startswith('"""'):
    k=rest.index('"""', rest.index('"""')+3)+3
    k=rest.index('\n',k)+1
    s=s[:j]+rest[:k]+'  import margins as MG  # already imported by main(), after the measurements were set\n'+rest[k:]
else:
    s=s[:j]+'  import margins as MG  # already imported by main(), after the measurements were set\n'+rest
open(p,'w').write(s)
EOF
sed -n 463,470p accord_lka_parts.py; S=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/m1 && rm -rf $S && mkdir -p $S && PYTHONPATH=/home/claude/pylib python3 accord_lka_parts.py --out $S/stl --report $S/report --no-pictures > $S/run.log 2>&1; echo exit $?; tail -5 $S/run.log; sed -n '/^MARGINS/,/^BOLTS/p' $S/report/parts_report.txt