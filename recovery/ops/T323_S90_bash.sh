cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6/stiff_var.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import stiffness as ST, rightarm as RA
var = sys.argv[1]
if var == "dash8":
    RA.TUBE_Y = (RA.TUBE_Y[0], RA.BORE_Y[1] + 8.0)
elif var == "nogroove":
    RA.RSLOT_H = 0.2
res = ST.solve(True, RA.ARM_SLIDE, RA.DZ_DEEP)
for k, d in res.items():
    print(f"{var}: {k}: in {d['in']:+.2f}, rim {d['rim']:+.2f}")
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6 && (PYTHONPATH=/home/claude/pylib python3 stiff_var.py nogroove > svng.txt 2>&1 &); echo started