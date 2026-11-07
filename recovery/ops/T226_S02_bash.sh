cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='rightarm.py'; s=open(p).read()
s=s.replace('''  return {"column-frame-plate-v4": on_bed(frame_plate_v4()),
          "right-arm": on_bed(arm(), rotate=(90.0, 0.0, 0.0)),
          "right-bar": on_bed(bar(), rotate=(0.0, 0.0, 0.0)) if False else on_bed(bar().rotate((0.0, 0.0, 0.0)), rotate=(0.0, 0.0, 0.0)),
          "right-bracket": on_bed(bracket(), rotate=(180.0, 0.0, 0.0))}''','''  return {"column-frame-plate-v4": on_bed(frame_plate_v4()),
          "right-arm": on_bed(arm()),                              # flat: 10 thick along the column
          "right-bar": on_bed(bar(), rotate=(90.0, 0.0, 0.0)),     # its underside (y) down: the flag stands
          "right-bracket": on_bed(bracket())}                       # the tab down, the face plate standing''')
open(p,'w').write(s)
EOF
ruff check --fix rightarm.py 2>&1 | tail -2; PYTHONPATH=/home/claude/pylib timeout 900 python3 rightarm.py 2>&1 | tail -8