cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
start = s.index("# The springs: McMaster-Carr 27749N488")
end = s.index("PIN_D = 5.0                   # the loops go over M5 bolts")
new = '''# The springs: McMaster-Carr 5108N591, spring steel, loop ends: 2.75 in (69.85 mm) long, 0.5 in (12.7 mm) outside,
# 0.075 in (1.9 mm) wire, 2.75 lbf (12.2 N) to start stretching, 23.2 lbf/in (4.06 N/mm), 30.51 lbf (135.7 N) at most,
# 3.95 in (100.3 mm) long at that (McMaster's table). McMaster's table doesn't say whether its length is inside the loops
# or over them: the bolts are placed for inside; over them, each spring pulls 15 N more. Either way the snap point
# stretches it to at most 1/1.44 of the most it takes and uses at most 66 % of its stretch, and the springs hold the
# gear in at least 1.5 times what lane keeping's hardest push needs. (27749N488, 2.5 in stainless, was 1.20 short.)
SPRING_PART = "McMaster-Carr 5108N591"
SPRING_OD_P, SPRING_WIRE_P = 12.7, 1.905
SPRING_FREE_P, SPRING_IT_P, SPRING_RATE_P, SPRING_MAX_P, SPRING_MAX_LEN_P = 69.85, 12.23, 4.063, 135.7, 100.3
'''
s = s[:start] + new + s[end:]
old = "SPRING_PULL_ON = 55.0         # each spring's pull with the gear on the teeth (N), the length measured inside the loops"
assert s.count(old) == 1
s = s.replace(old, "SPRING_PULL_ON = 47.8         # each spring's pull with the gear on the teeth (N), the length measured inside the loops")
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import popparts as PP, popassembly as PA
print('r', round(PP.SPRING_R, 2), 'C', PP.C_BOLT.round(2), 'B', PP.B_BOLT.round(2))
for r in PA.spring_rows(): print(r)
"