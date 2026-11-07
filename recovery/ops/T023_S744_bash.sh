python3 - <<'EOF'
p='accord_lka_parts.py'
s=open(p).read()
old='''["lever down (cut through the middle)", "lever up: the cam pushes the carrier's fin down"]'''
new='''["lever down (cut through the middle)", "lever up: its rounded end presses the motor carrier's tab, lifting the motor gear"]'''
assert s.count(old)==1
s=s.replace(old,new)
open(p,'w').write(s)
EOF
S=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad; rm -rf $S/cad2; mkdir -p $S/cad2/stl $S/cad2/report; PYTHONPATH=/home/claude/pylib timeout 590 python3 accord_lka_parts.py --out $S/cad2/stl --report $S/cad2/report > $S/cad2/run.log 2>&1; echo "exit $?"; tail -2 $S/cad2/run.log; cd /home/claude/deliver/hardware && n=0; for f in $(cd stl && find . -name "*.stl"); do cmp -s stl/$f $S/cad2/stl/$f || { echo "DIFF $f"; n=1; }; done; echo "stl differences: $n"; diff <(sed 1,3d report/parts_report.txt) <(sed 1,3d $S/cad2/report/parts_report.txt) && echo "report text same"; for f in assembly-3d assembly-side parts-1 parts-2 parts-3 lift-lever-section; do cmp -s report/$f.png $S/cad2/report/$f.png && echo "same $f.png" || echo "changed $f.png"; done