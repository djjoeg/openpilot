python3 - <<'EOF'
import re
def dict_to_literal(src):
    """Turn dict(a=..., b=...) calls into {"a": ..., "b": ...}, handling nesting."""
    out = []
    i = 0
    while True:
        j = src.find('dict(', i)
        if j < 0:
            out.append(src[i:]); break
        # make sure it's a call, not e.g. 'xdict('
        if j > 0 and (src[j-1].isalnum() or src[j-1] in '_.'):
            out.append(src[i:j+5]); i = j + 5; continue
        out.append(src[i:j])
        # find the matching paren
        k = j + 5; depth = 1
        while depth:
            ch = src[k]
            if ch in '([{': depth += 1
            elif ch in ')]}': depth -= 1
            k += 1
        inner = src[j+5:k-1]
        inner = dict_to_literal(inner)
        # split top-level args by commas
        parts, depth, cur = [], 0, ''
        for ch in inner:
            if ch in '([{': depth += 1
            if ch in ')]}': depth -= 1
            if ch == ',' and depth == 0:
                parts.append(cur); cur = ''
            else:
                cur += ch
        if cur.strip(): parts.append(cur)
        new = []
        for p in parts:
            m = re.match(r'(\s*)([A-Za-z_]\w*)=(.*)', p, re.S)
            assert m, p
            new.append(f'{m.group(1)}"{m.group(2)}": {m.group(3)}')
        out.append('{' + ','.join(new) + '}')
        i = k
    return ''.join(out)

for p in ('incar.py', 'carphoto.py'):
    s = open(p).read()
    s2 = dict_to_literal(s)
    open(p, 'w').write(s2)
    print(p, s.count('dict('), '->', s2.count('dict('))
EOF
python3 - <<'EOF'
p = '/home/claude/deliver/hardware/cad/incar.py'
s = open(p).read()
s = s.replace('''  import columnassembly as CA
  from manifold3d import Manifold
  from cadlib import union
  c = RA.R_FACE_OUT * RA.U''', '''  c = RA.R_FACE_OUT * RA.U''')
s = s.replace('''import numpy as np
from PIL import Image

import carphoto as CP
import carscene as CS
''', '''import numpy as np
from manifold3d import Manifold
from PIL import Image

import carphoto as CP
import carscene as CS
import columnassembly as CA
''')
s = s.replace('''import rightcheck as RC
''', '''import rightcheck as RC
from cadlib import union
''', 1)
s = s.replace("  segs = [CA.rod(a, b, 2.4) for a, b in zip(pts[:-1], pts[1:])]", "  segs = [CA.rod(a, b, 2.4) for a, b in itertools.pairwise(pts)]")
s = s.replace("import math\nimport os\nimport sys\n", "import itertools\nimport math\nimport os\nimport sys\n", 1)
s = s.replace("def make(name: str, ss: int = None, out_dir: str = REPORT_DIR) -> str:", "def make(name: str, ss: int | None = None, out_dir: str = REPORT_DIR) -> str:")
s = s.replace("def occluders(cam: PC.PhotoCam = None, openings=None) -> list:", "def occluders(cam: PC.PhotoCam | None = None, openings=None) -> list:")
s = s.replace("  h = int(round(a.height * w / a.width))", "  h = round(a.height * w / a.width)")
s = s.replace("  from manifold3d import CrossSection\n  disc = CrossSection.circle(r, 180)", "  disc = CrossSection.circle(r, 180)")
s = s.replace("from manifold3d import Manifold\n", "from manifold3d import CrossSection, Manifold\n", 1)
open(p, 'w').write(s)
p = '/home/claude/deliver/hardware/cad/photocomp.py'
s = open(p).read()
s = s.replace("  R = int(math.ceil(r))", "  R = math.ceil(r)")
open(p, 'w').write(s)
p = '/home/claude/deliver/hardware/cad/carphoto.py'
s = open(p).read()
s = s.replace("  segs = [CA.rod(a, b, 2.6) for a, b in zip(pts[:-1], pts[1:])]", "  segs = [CA.rod(a, b, 2.6) for a, b in itertools.pairwise(pts)]")
s = s.replace("import math\nimport os\nimport sys\n", "import itertools\nimport math\nimport os\nimport sys\n", 1)
open(p, 'w').write(s)
EOF
cd /home/claude/deliver/hardware/cad && ruff check incar.py photocomp.py carphoto.py photorender.py --output-format concise 2>&1 | tail -8