python3 - <<'EOF'
p = "sideparts.py"
s = open(p).read()
old = '''  lug_in = box(X_EAR[0], X_EAR[1], EAR_Y[0] - 0.5, EAR_Y[1], EAR_Z[0], LEVER_Z[0] - LUG_GAP)'''
new = '''  lug_in = box(X_EAR[0], X_EAR[1], EAR_Y[0] - 0.5, LUG_IN_Y1, EAR_Z[0], LEVER_Z[0] - LUG_GAP)'''
assert s.count(old) == 1
s = s.replace(old, new)
old = '''EAR_Z = (-25.0, 0.0)              # its outer end (+z) presses the switch and meets the stop'''
new = '''EAR_Z = (-25.0, 0.0)              # its outer end (+z) presses the switch and meets the stop
LUG_IN_Y1 = 28.0                  # the inner lug stops short of the spool's post towards the dash (slid in, they're level)'''
assert s.count(old) == 1
s = s.replace(old, new)
open(p, "w").write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 - <<'EOF'
import sideassembly as SA
A = SA.SideAssembly()
r = SA.internal(A)
print("internal over 0.001:", {k: v for k, v in r.items() if v[0] > 1e-3})
print(SA.touching_at_stops(A))
print(SA.lever_notches(A))
EOF