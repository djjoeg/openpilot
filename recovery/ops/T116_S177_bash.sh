python3 - <<'EOF'
import re
p='accord_lka_parts.py'
s=open(p).read()
old='''  L.append(f"BACK TEETH: {tt['teeth']} teeth of a {tt['teeth_on_a_full_circle']}-tooth face gear (2 mm teeth, {tt['pitch_radius_mm']:.0f} mm "
           f"from the column's axis), the motor gear'''
new='''  L.append(f"BACK TEETH: {tt['teeth']} teeth of a {tt['teeth_on_a_full_circle']}-tooth face gear (2 mm teeth, "
           f"{tt['pitch_radius_mm']:.0f} mm from the column's axis), the motor gear'''
assert s.count(old)==1
s=s.replace(old,new)
open(p,'w').write(s)
p='faceassembly.py'
s=open(p).read()
old='''                      f"({FP.PL_PAD_T:.0f} mm), wherever the screws fall in its two slots", "length": 0.0, "through_mm": FP.PL_T + FP.PL_PAD_T,
               "nut_mm": 0.0,'''
new='''                      f"({FP.PL_PAD_T:.0f} mm), wherever the screws fall in its two slots", "length": 0.0,
               "through_mm": FP.PL_T + FP.PL_PAD_T, "nut_mm": 0.0,'''
assert s.count(old)==1
s=s.replace(old,new)
open(p,'w').write(s)
EOF
/home/claude/bin/ruff check --isolated --select E,F --line-length 140 --output-format concise . ; echo "exit $?"; R=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/facebuild/report && PYTHONPATH=/home/claude/pylib python3 -c "
import json, accord_lka_parts as A
r = json.load(open('$R/parts_report.json'))
open('$R/parts_report.txt','w').write(A.text_report(r))
" && grep -c "" $R/parts_report.txt && grep -n "BACK TEETH:" $R/parts_report.txt | cut -c1-200