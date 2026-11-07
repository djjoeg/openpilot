cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='viewer3d.py'; s=open(p).read()
old_vars = '''  board_steel = union([mp[i] for i in (6, 7, 9, 10, 12, 13, 15, 16)])
  chips = union([mp[i] for i in (18, 19, 20, 23, 24)])
  plugs = union([mp[i] for i in (21, 22)])
'''
assert old_vars in s; s = s.replace(old_vars, '')
old = '''     [(mp[17], PCB, 1.0), (chips, CHIP, 1.0), (plugs, PLUG, 1.0), (board_steel, STEEL, 1.0)], motor_moves),'''
assert old in s
s = s.replace(old, '''     [(RA.motor_and_gear(0.0)["board"], BOARD, 1.0)], motor_moves),''')
s = s.replace('''  gear = RA.motor_and_gear(0.0)["gear"]\n''', '')
s = s.replace('''("gear", "Gear", n["gear"], "motor", True, [(gear, GEAR, 1.0)]''', '''("gear", "Gear", n["gear"], "motor", True, [(RA.motor_and_gear(0.0)["gear"], GEAR, 1.0)]''')
old = '''PCB = ((0.13, 0.36, 0.23), 0.20, 40)
CHIP = ((0.10, 0.10, 0.11), 0.25, 50)
PLUG = ((0.80, 0.75, 0.60), 0.10, 20)
'''
assert old in s; s = s.replace(old, '''BOARD = ((0.22, 0.25, 0.29), 0.15, 30)
''')
old = '''  "board": "On the motor's back. Drawn as a placeholder: the real board's shape and parts differ.",'''
assert old in s
s = s.replace(old, '''  "board": ("On the motor's back. Drawn as a plain box (as in the review pictures): the real board's shape and size "
            "may differ."),''')
old = '''      "overview": {"target": centre, "dir": [0.9, -0.5, 0.8], "dist": 600},
      "seat": {"target": [115.0, -70.0, -45.0], "eye": [0.0, 81.0, 734.0]},      # your eyes: about 350 up, 650 back'''
assert old in s
s = s.replace(old, '''      "overview": {"target": centre, "dir": [0.85, -0.55, -0.3], "dist": 470},
      "seat": {"target": [115.0, -70.0, -45.0], "eye": [0.0, 81.0, 734.0], "dist": 560},   # from your eyes (about
                                                                                         # 350 up, 650 back), nearer''')
s = s.replace('''the steering wheel grip and the column cover (the cover approximate). The board on the motor's back is a
placeholder (as in carphoto.py).''', '''the steering wheel grip and the column cover (the cover approximate). The board on the motor's back is a
plain box, as in the review pictures.''')
s = s.replace('''the motor, its four screws, the gear,''', '''the motor, its four screws, the gear,''')
open(p,'w').write(s)

p='viewer3d_page.html'; s=open(p).read()
rep = [
 ('''  --onink: #f8f9fb;\n  --focus: #2d6bd1;\n''', '''  --onink: #f8f9fb;\n  --focus: #2d6bd1;\n  --ring: rgba(26, 31, 38, 0.28);\n'''),
 ('''--chip: #20262c; --onink: #15191d; --focus: #6ea2ff; color-scheme: dark;\n  }\n}''', '''--chip: #20262c; --onink: #15191d; --focus: #6ea2ff; --ring: rgba(228, 232, 236, 0.45); color-scheme: dark;\n  }\n}'''),
 (''':root[data-theme="dark"] {\n  --bg: #111417; --stage: #1c2127; --panel: #15191d; --ink: #e4e8ec; --muted: #9ba6b1; --line: #2b3239;\n  --chip: #20262c; --onink: #15191d; --focus: #6ea2ff; color-scheme: dark;\n}''', ''':root[data-theme="dark"] {\n  --bg: #111417; --stage: #1c2127; --panel: #15191d; --ink: #e4e8ec; --muted: #9ba6b1; --line: #2b3239;\n  --chip: #20262c; --onink: #15191d; --focus: #6ea2ff; --ring: rgba(228, 232, 236, 0.45); color-scheme: dark;\n}'''),
 ('''.chip .dot { width: 11px; height: 11px; border-radius: 50%; border: 1px solid rgba(0, 0, 0, 0.25); flex: none; }''', '''.chip .dot { width: 11px; height: 11px; border-radius: 50%; border: 1px solid var(--ring); flex: none; }'''),
 ('''.head { position: absolute; top: 12px; left: max(16px, env(safe-area-inset-left, 0px)); right: max(16px, env(safe-area-inset-right, 0px)); pointer-events: none; }''', '''.head { position: absolute; top: 12px; left: max(16px, env(safe-area-inset-left, 0px)); right: max(16px, env(safe-area-inset-right, 0px)); pointer-events: none; text-shadow: 0 0 2px var(--stage), 0 0 6px var(--stage), 0 0 12px var(--stage); }'''),
 ('''<button type="button" data-view="below" aria-pressed="false">From below</button>''', '''<button type="button" data-view="below" aria-pressed="false">Below</button>'''),
 ('''    if (v.eye) { const d = sub(toWorld(v.eye), t); dist = Math.hypot(d[0], d[1], d[2]); dir = mul(d, 1 / dist); }''', '''    if (v.eye) { const d = sub(toWorld(v.eye), t); dir = norm(d); dist = v.dist || Math.hypot(d[0], d[1], d[2]); }'''),
 ('''    if (!v.eye) dist *= Math.max(1, 0.95 / aspect);''', '''    dist *= Math.max(1, 0.95 / aspect);'''),
 ('''@media (max-width: 520px) {\n''', '''@media (max-width: 520px) {\n  .views { gap: 5px; }\n  .views button { padding: 5px 10px; font-size: 13px; }\n'''),
 ('''<p class="fine">The printed parts are drawn from the same shapes as the print files (plates 9, 11 and 12), where they go on the car. The motor, gear and wing bolts are drawn to size. The board on the motor's back is a placeholder, and the column cover is approximate.</p>''', '''<p class="fine">The printed parts are drawn from the same shapes as the print files (plates 9, 11 and 12), where they go on the car. The motor, gear and wing bolts are drawn to size. The board on the motor's back is a plain box, and the column cover is approximate.</p>'''),
]
for a,b in rep:
  assert a in s, a[:60]
  s = s.replace(a,b)
open(p,'w').write(s)
EOF
ruff check viewer3d.py --output-format concise && export PYTHONPATH=/home/claude/pylib && timeout 600 python3 viewer3d.py