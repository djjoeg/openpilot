cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
b=open('accord_lka_parts.py').read()
b=b.replace('''  R.save(os.path.join(folder, "side-assembly-front.png"),
         [(CA.parts_scene(A), front), (CA.parts_scene(A, lift, MP.A_OFF), front), (CA.parts_scene(A), R.look((0, 1, 0), (0, 0, 1)))],
         ["lift lever down: motor gear in the ring", "lift lever up: motor gear lifted off, the handle in towards the hub",
          "from above (the driver is at the bottom)"],
         suptitle="Right-side mount, from the driver's seat: the ring teeth at 3 o'clock, the motor behind the wheel, the side "
                  "bracket on the column covers and the screw tab out to the dash's screw (the wiper stalk and key cylinder are estimates)",
         size=(700, 700))''',
'''  R.save(os.path.join(folder, "side-assembly-front.png"),
         [(CA.parts_scene(A), front), (CA.parts_scene(A, lift, MP.A_OFF), front), (CA.parts_scene(A), R.look((0, 1, 0), (0, 0, -1)))],
         ["lift lever down: motor gear in the ring", "lift lever up: motor gear lifted off, the handle in towards the hub",
          "from above: the driver at the bottom, the dash at the top"],
         suptitle="Right-side mount from the driver's seat: the ring teeth at 3 o'clock, the motor behind the wheel, the side bracket "
                  "on the column covers, the screw tab out to the dash's screw (the wiper stalk and key cylinder are estimates)",
         size=(700, 700))''')
open('accord_lka_parts.py','w').write(b)
print('ok')
EOF
grep -n "def save\|def look\|suptitle\|fontsize\|figsize" render.py | head