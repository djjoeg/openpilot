python3 - <<'EOF'
p = 'rightarm.py'
s = open(p, encoding='utf-8').read()
reps = [
('''"12 right arm v4", list(parts),
                              "Plate 12: the right arm mount v4: the arm (its tower a closed tube) and the motor carrier")])''',
 '''"12 right arm v5", list(parts),
                              "Plate 12: the right arm mount v5: the arm (deep, the groove up its tower) and the carrier")])'''),
('''         suptitle="Right arm mount v4 on the frame plate v4: the motor outside the rim just above 4 o'clock, shaft pointing in. ''',
 '''         suptitle="Right arm mount v5 on the frame plate v4: the motor outside the rim just above 4 o'clock, shaft pointing in. '''),
]
for a, b in reps:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
p = 'allinone.py'
s = open(p, encoding='utf-8').read()
a = "One print for everything the right-arm build needs (2 Nov 2026; 3 Nov: the arm and carrier v4, the teeth v3): the"
b = "One print for everything the right-arm build needs (2 Nov 2026; 3 Nov: the arm and carrier v5, the teeth v3): the"
assert s.count(a) == 1
open(p, 'w', encoding='utf-8').write(s.replace(a, b))
print('ok')
EOF
sed -n 366,376p rightarm.py