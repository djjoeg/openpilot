python3 - <<'EOF'
import re
p='viewer3d.py'; s=open(p).read()
s=s.replace("import base64\nimport json\nimport math\nimport os\n","import base64\nimport json\nimport os\n")
open(p,'w').write(s)
p='viewer3d_page.html'; s=open(p).read()
s=s.replace("html { height: 100%; box-sizing: border-box; }","[hidden] { display: none !important; }\nhtml { height: 100%; box-sizing: border-box; }")
open(p,'w').write(s)
EOF
export PYTHONPATH=/home/claude/pylib && time timeout 600 python3 viewer3d.py && ruff check viewer3d.py 2>&1 | tail -5