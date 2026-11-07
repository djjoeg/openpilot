cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache && cat > dsweep.py <<'EOF'
import sys
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import slideassembly as SA, slideparts as SP
for D in [float(v) for v in sys.argv[1].split(",")]:
  out = []
  for m in [float(v) for v in sys.argv[2].split(",")]:
    A = SA.SlideAssembly(D, m, parts={})
    car = dict(A.car_parts())
    mb = SP.motor_board()
    allm = SP.union([mb["motor"], mb["board+cap"], mb["car plug"], mb["motor plug"], mb["motor's own plug"]]) if hasattr(SP, "union") else None
    from cadlib import union
    allm = union([mb["motor"], SP.board_cap(), mb["car plug"], mb["motor plug"], mb["motor's own plug"]])
    off = SA.min_gap(A.place(allm, SP.STROKE), car["column cover"])
    on = SA.min_gap(A.place(allm), car["column cover"])
    tab = min(SA.min_gap(A.place(allm, o), car["adjustment tab, its swing and your fingers on it"]) for o in (-SA.drop_most(), 0.0, SP.STROKE))
    bc = min(SA.min_gap(A.place(allm, o), car["back cover (it turns with the wheel)"]) for o in (-SA.drop_most(), 0.0, SP.STROKE))
    out.append(f"{m:.0f}: cover on {on} off {off}, tab {tab}, back cover {bc}")
  print(f"D {D:.0f}: " + " | ".join(out), flush=True)
EOF
(timeout 900 python3 dsweep.py 105,107,108,109,110 -70 > ds_a.txt 2>&1 &); timeout 900 python3 dsweep.py 112,113,115,120,125 -70 > ds_b.txt 2>&1; sleep 2; cat ds_a.txt ds_b.txt