cd /home/claude/deliver/hardware/cad && grep -n "81.0\|9 mm washers" stiffness.py && python3 - <<'EOF'
p = "stiffness.py"
s = open(p, encoding="utf-8").read()
a = """      fixed |= ((xyz[:, 0] - sx) ** 2 + (xyz[:, 2] - sz) ** 2 <= 81.0) & (xyz[:, 1] >= RA.COVER_Y - RA.PLATE_T - 0.5)"""
b = """      fixed |= ((xyz[:, 0] - sx) ** 2 + (xyz[:, 2] - sz) ** 2 <= WASHER_R ** 2) & (xyz[:, 1] >= RA.COVER_Y - RA.PLATE_T - 0.5)"""
assert s.count(a) == 1
s = s.replace(a, b)
a = """LIMIT_IN, LIMIT_OUT = 1.0, 1.5"""
b = """LIMIT_IN, LIMIT_OUT = 1.0, 1.5
WASHER_R = 9.0             # the plate held this far round each cover screw (its washer)"""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6/stiff_washer.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import stiffness as ST, rightarm as RA
ST.WASHER_R = float(sys.argv[1])
res = ST.solve(True, RA.ARM_SLIDE, RA.DZ_DEEP)
for k, d in res.items():
    print(f"washer r {ST.WASHER_R}: {k}: in {d['in']:+.2f}, rim {d['rim']:+.2f}")
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6 && (PYTHONPATH=/home/claude/pylib python3 stiff_washer.py 12.5 > sw125.txt 2>&1 &) ; echo started