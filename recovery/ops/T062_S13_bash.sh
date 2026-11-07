python3 - <<'EOF'
p='accord_lka_parts.py'
s=open(p).read()
old='''f"({lv['most_push_with_rubbing_N']} N counting rubbing at the rounded end, an estimate with dry printed parts; "
           f"grease brings it down), {lv['push_to_bring_it_back_down_N']} N to start it back down "'''
new='''f"({lv['most_push_with_rubbing_N']} N counting rubbing at the rounded end, an estimate with dry printed parts), "
           f"{lv['push_to_bring_it_back_down_N']} N to start it back down "'''
assert old in s; s=s.replace(old,new,1)
old2='''report["spring"] = {"part": f"{MP.SPRING_PART} ({MP.SPRING_OD} mm outside, 1.09 mm wire, {MP.SPRING_FREE:g} mm long, "'''
new2='''report["spring"] = {"part": f"{MP.SPRING_PART} ({MP.SPRING_OD} mm outside, {MP.SPRING_WIRE} mm wire, {MP.SPRING_FREE:g} mm long, "'''
assert old2 in s; s=s.replace(old2,new2,1)
open(p,'w').write(s)
EOF
S=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad; cp ../report/parts_report.txt $S/parts_report_before_spring.txt; (time PYTHONPATH=/home/claude/pylib timeout 3000 python3 accord_lka_parts.py > $S/rebuild3.log 2>&1) 2> $S/rebuild3.time; tail -25 $S/rebuild3.log