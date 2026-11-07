python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
for old, new in [('''PL_BRIDGE_Z = (-205.0, -191.0)   # the bridge behind the tab's pivot; the plate's back edge''',
                  '''PL_BRIDGE_Z = (-208.0, -194.0)   # the bridge behind the tab's pivot; the plate's back edge'''),
                 ('''PL_SLOTS = ((54.0, -122.0, 54.0, -186.0), (28.0, -136.0, 28.0, -186.0), (-40.0, -198.0, 4.0, -198.0),''',
                  '''PL_SLOTS = ((54.0, -122.0, 54.0, -186.0), (28.0, -136.0, 28.0, -186.0), (-40.0, -201.0, 4.0, -201.0),''')]:
    assert s.count(old) == 1, old
    s = s.replace(old, new)
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 3000 python3 -c "
import sys; sys.path.insert(0, '/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2')
import run_u, popassembly as PA, popparts as PP
from mindist import min_dist
t, parts = run_u.build()
A = PA.PopAssembly(t, parts)
print('plate to tab swing', round(min_dist(A.plate(), A.tilt_lever(), spacing=0.8)[0], 2), 'plate to bolster', round(min_dist(A.plate(), A.bolster(), spacing=1.0)[0], 2))
" && PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 5400 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2/run_u.py 2>&1 | grep -v "^   {\|flange fit\|switch:" | tail -6