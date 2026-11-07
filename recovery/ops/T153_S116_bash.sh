grep -n "^RUB_DRY\|RUB_DRY =" margins.py | head -3; cat > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide/run_s.py <<'EOF'
import sys, time, json
sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import slideassembly as SA
import slideparts as SP
T0 = time.time()
D = float(sys.argv[1]) if len(sys.argv) > 1 else 110.0
mount = float(sys.argv[2]) if len(sys.argv) > 2 else SP.MOUNT_DEG_S
what = sys.argv[3] if len(sys.argv) > 3 else "fit"
A = SA.SlideAssembly(D, mount)
print(f"D {D} mount {mount}: parts {round(time.time()-T0,1)} s", flush=True)
if "latch" in what:
  print("latch:", json.dumps(SA.latch_numbers(), indent=1))
  print("switch:", SA.switch_states())
if "mesh" in what:
  print("mesh:", SA.mesh_sweep(A), round(time.time()-T0,1), "s", flush=True)
if "gaps" in what:
  for r in SA.gaps_table(A):
    print("  gap", r)
if "fit" in what:
  res = SA.check_fit(A)
  bad = SA.report_rows(res)
  print(len(res), "checks,", len(bad), "overlapping", round(time.time()-T0,1), "s")
  for k, v in bad:
    print(f"  {v:10.3f}  {k}")
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache && timeout 600 python3 run_s.py 110 -70 latch 2>&1 | tail -40