cd /home/claude/deliver/hardware/cad && cp mountparts.py /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/mountparts_v2.py && PYTHONPATH=/home/claude/pylib python3 -c "
import manifold3d as m
from manifold3d import CrossSection
print([a for a in dir(CrossSection) if not a.startswith('_')])
print([a for a in dir(m.Manifold) if 'hull' in a.lower() or 'slice' in a.lower() or 'project' in a.lower()])
"