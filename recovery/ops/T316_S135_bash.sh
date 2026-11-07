python3 - <<'EOF'
p = 'midteeth.py'
s = open(p, encoding='utf-8').read()
old = 'f"Plate 14: a short piece of the teeth channel, the inner wall pulled {round(SAMPLE_PULL)} mm, to try on the grip")]'
new = 'f"Plate 14: teeth fit sample, the inner wall pulled {round(SAMPLE_PULL)} mm")]'
assert s.count(old) == 1
open(p, 'w', encoding='utf-8').write(s.replace(old, new))
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import midteeth as MT
print(MT.build_sample())
for n, fname, plate_name, rows, size in MT.sample_plate(): print(fname, size)
"