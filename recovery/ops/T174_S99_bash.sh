/home/claude/bin/ruff check --line-length 140 plates.py --fix -q; python3 - <<'EOF'
p='plates.py'; s=open(p).read()
s = s.replace("SOLID = dict(STANDARD, sparse_infill_density=\"100%\", sparse_infill_pattern=\"zig-zag\")  # \"zig-zag\" is Bambu's rectilinear",
              "SOLID = {**STANDARD, \"sparse_infill_density\": \"100%\", \"sparse_infill_pattern\": \"zig-zag\"}  # \"zig-zag\" is Bambu's rectilinear")
open(p,'w').write(s)
EOF
/home/claude/bin/ruff check --output-format concise --line-length 140 plates.py; echo "ruff exit $?"; sed -n 20,40p plates.py