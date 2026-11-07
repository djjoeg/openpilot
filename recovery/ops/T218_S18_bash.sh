python3 - <<'EOF'
p='armmount.py'; s=open(p).read()
s=s.replace('"from below (the wheel at the bottom)"','"from below, the wheel at the top (as in your photos)"')
s=s.replace('''  ax.text(87, -27, "2nd screw\\n(washer over\\nthe window)", ha="center", va="top", fontsize=8, color="#c0392b")''',
'''  ax.text(112, -40, "2nd screw:\\nwasher over\\nthe window", ha="right", va="center", fontsize=8, color="#c0392b")''')
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 armmount.py >/dev/null 2>&1 && ls -la ../plates/plate-5-frame-plate-v2.3mf ../plates/plate-6-arm-mount.3mf ../plates/plate-10-teeth-fit-test.3mf ../report/arm-mount.png ../report/column-frame-plate-v2.png | awk '{print $5, $9}'