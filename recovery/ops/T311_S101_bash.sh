cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='viewer3d_page.html'; s=open(p).read()
a='.steptext { margin: 6px 0 10px; min-height: 4.35em; max-width: 62ch; }'
assert a in s
s=s.replace(a,'.steptext { margin: 6px 0 10px; min-height: 5.8em; max-width: 62ch; }')
open(p,'w').write(s)
EOF
export PYTHONPATH=/home/claude/pylib && timeout 600 python3 viewer3d.py && head -c 600 ../report/arm-3d.html && grep -c "__META__\|__DATA__" ../report/arm-3d.html