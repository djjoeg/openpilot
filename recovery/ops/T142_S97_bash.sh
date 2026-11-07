python3 - <<'EOF'
import pathlib
p = pathlib.Path("popassembly.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)
rep('''  B, SW, PL, PD = A.block(), A.switch(), A.plate(), A.pads()''', '''  B, SW, PL, TB = A.block(), A.switch(), A.plate(), A.tabs()''')
rep('''  fixed = [("hinge block", B), ("power switch", SW), ("column plate", PL), ("plate's rubber strips", PD)]''',
'''  fixed = [("hinge block", B), ("power switch", SW), ("column plate", PL), ("screw tabs", TB)]''')
rep('''  for cn, c in car:
    for mn, m in movers + fixed:
      pairs[f"{mn}/{cn}"] = (m, c)
  for k, (a, b) in pairs.items():''', '''  for cn, c in car:
    for mn, m in movers + fixed:
      if mn == "screw tabs" and cn == "column covers":
        continue                          # they're screwed to it, their bosses in its screw cups
      pairs[f"{mn}/{cn}"] = (m, c)
  pairs["hinge block/screw tabs"] = (B, TB)
  for k, (a, b) in pairs.items():''')
rep('''  for name, part in parked + [("hinge block", B), ("power switch", SW), ("column plate", PL)]:
    res[f"parked: the teeth anywhere round the wheel/{name}"] = overlap(ring, part)
    res[f"parked: your fingers round the grip anywhere/{name}"] = overlap(fingers, part)
  return res''', '''  room = A.key_room()
  for name, part in parked + [("hinge block", B), ("power switch", SW), ("column plate", PL), ("screw tabs", TB)]:
    res[f"parked: the teeth anywhere round the wheel/{name}"] = overlap(ring, part)
    res[f"parked: your fingers round the grip anywhere/{name}"] = overlap(fingers, part)
    res[f"parked: your fingers turning the key/{name}"] = overlap(room, part)
  for name, part in (("hinge block", B), ("power switch", SW), ("column plate", PL), ("screw tabs", TB)):
    res[f"on: your fingers turning the key/{name}"] = overlap(room, part)
  return res


def flange_fit(mount_deg: float, cover_dy: float = 0.0, plate_dx: float = 0.0) -> dict:
  """With the mount turned to mount_deg, the cover's underside cover_dy higher (+) than the model, and the plate
  dx to the right: where each flange bolt sits along its block slot (+-SLOT_X) and its plate slot (+-SLOT_Y)."""
  block_c = PP.flange_bolts_wheel(mount_deg)          # the bolts' slot middles in the block, now
  plate_c = PP.flange_bolts_wheel()                   # the plate's slot middles (it was made for the nominal mount)
  a = math.radians(mount_deg)
  ux = (math.cos(a), math.sin(a))                     # the block's slots run along its own x
  out = []
  for (bx, by), (px, py) in zip(block_c, plate_c):
    px += plate_dx
    py += cover_dy
    # the bolt is on the plate slot's line x = px, and on the block slot's line through (bx, by) along ux
    s_along = (px - bx) / ux[0]
    y = by + s_along * ux[1]
    out.append({"along_block_slot": round(s_along, 1), "along_plate_slot": round(y - py, 1),
                "fits": abs(s_along) <= PP.SLOT_X and abs(y - py) <= PP.SLOT_Y})
  return {"bolts": out, "fits": all(o["fits"] for o in out)}''')
p.write_text(s)
print("ok")
EOF
grep -n "^import\|^from" popassembly.py | head