cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)
rep('''# turns to reach one of the plate's two long slots, and bolts to it from below into a nut held in the tab. A tab reaches
# 40 mm from its screw and the slots are long, so the plate fits them wherever they really are (+-25 mm or more).''',
'''# turns to reach one of the plate's long slots, and holds an M5 x 20 hex bolt hanging down from a channel along its
# top (the cover above keeps it there): the plate goes up onto the bolts and a washer and lock nut under it hold it.''')
rep('''TAB_SLOT = (18.0, 40.0)       # the slot along it for the bolt to the plate, with a channel on top for the nut''',
'''TAB_SLOT = (18.0, 40.0)       # the slot along it for the bolt to the plate, with a channel on top for the bolt's head''')
rep('''NUT_CHANNEL_T = 5.5           # the nut's channel depth (an M5 nyloc nut, 5.2 mm)''',
'''NUT_CHANNEL_T = 5.5           # the channel for the bolt's hex head (8 mm across flats, 3.5 mm tall): it can slide, not turn''')
rep('''  """Tab frame: its screw at the origin, its slot along +x from TAB_SLOT[0] to TAB_SLOT[1], +z towards the cover (its
  top face z = 0). The nut for the plate's bolt sits in a channel along the slot's top and can slide along it."""''',
'''  """Tab frame: its screw at the origin, its slot along +x from TAB_SLOT[0] to TAB_SLOT[1], +z towards the cover (its
  top face z = 0). The plate's bolt hangs from its hex head in a channel along the slot's top and can slide along it."""''')
rep('''  # the nut's channel from the top: its flats against the channel's sides so it can't turn''',
'''  # the bolt head's channel from the top: its flats against the channel's sides so it can't turn''')
p.write_text(s)
p = pathlib.Path("popassembly.py")
s = p.read_text()
rep('''      # the plate's bolt: hex head and washer under the plate, up into the nut in the tab's channel
      parts.append(cyl_y(2.5, y0 - 1.0, y1 + PP.TAB_T - 0.5, x=bx, z=bz, segments=16) +
                   cyl_y(4.6, y0 - 4.5, y0 - 1.0, x=bx, z=bz, segments=6) + cyl_y(5.0, y0 - 1.0, y0, x=bx, z=bz, segments=24))''',
'''      # the plate's bolt: M5 x 20 hex head in the tab's channel, down through the plate, washer and lock nut under it
      top = y1 + PP.TAB_T - PP.NUT_CHANNEL_T
      parts.append(cyl_y(4.6, top, top + 3.5, x=bx, z=bz, segments=6) + cyl_y(2.5, top - 20.0, top, x=bx, z=bz, segments=16) +
                   cyl_y(5.0, y0 - 1.0, y0, x=bx, z=bz, segments=24) + cyl_y(4.6, y0 - 6.2, y0 - 1.0, x=bx, z=bz, segments=6))''')
p.write_text(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 3000 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2/run_u.py --quick 2>&1 | grep -v "^   {\|flange fit\|switch:" | tail -4