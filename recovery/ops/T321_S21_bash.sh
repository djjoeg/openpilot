python3 - <<'EOF'
p = 'rightcheck.py'
s = open(p, encoding='utf-8').read()
reps = [
("""  blocked("slide nut turned in its slot / carrier", slide_nut(0.0, small_turned=True), car0)""",
 """  blocked("slide nut turned in its slot / carrier", slide_nut(0.0, small_turned=True), car0, NUT_LOCK)"""),
("""  blocked("receiver nut turned in its slot / plate", rn, plate)""",
 """  blocked("receiver nut turned in its slot / plate", rn, plate, NUT_LOCK)"""),
("""M5_E_MIN = 8.79      # the smallest across-corners an M5 nut may have (ISO 4032): the one most likely to turn""",
 """M5_E_MIN = 8.79      # the smallest across-corners an M5 nut may have (ISO 4032): the one most likely to turn
NUT_LOCK = 0.3       # mm^3 its corners must cut into the slot's walls when turned (the receiver's 8.4 slot: 0.5, its
                     # corners 0.2 mm into each wall; the slide's 8.3: 1.6, 0.25 mm)"""),
]
for a, b in reps:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
EOF
(PYTHONPATH=/home/claude/pylib python3 rightcheck.py) 2>&1 | tail -4