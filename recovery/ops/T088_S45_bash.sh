python3 - <<'EOF'
p='columnassembly.py'; s=open(p).read()
old='def check_all(A: ColumnAssembly, wheel_turn: float = 40.0, lever_step: float = 4.0) -> dict:'
new='def check_all(A: ColumnAssembly, wheel_turn: float = 40.0, lever_step: float = 4.0, dash: bool = True) -> dict:'
assert old in s; s=s.replace(old,new)
old='''  """Overlap volumes (mm^3) between parts that must not touch, as assembly.check_all, for the column mount: the ring
  teeth in place of the steering wheel teeth, the covers, hub, spoke zone, dash and the clamp's own parts in place
  of the dash cover and dash clamp."""'''
new='''  """Overlap volumes (mm^3) between parts that must not touch, as assembly.check_all, for the column mount: the ring
  teeth in place of the steering wheel teeth, the covers, hub, spoke zone, dash and the clamp's own parts in place
  of the dash cover and dash clamp. dash: False leaves out the dash panel (its place is only an estimate)."""'''
assert old in s; s=s.replace(old,new)
old='''  fixed = (("column covers", COV), ("hub", HUB), ("spoke sweep zone", ZONE), ("dash below the column", DASH),
           ("lower saddle", CL), ("upper saddle", CU), ("rods and nuts", RD))'''
new='''  fixed = (("column covers", COV), ("hub", HUB), ("spoke sweep zone", ZONE), ("dash below the column", DASH),
           ("lower saddle", CL), ("upper saddle", CU), ("rods and nuts", RD))
  if not dash:
    fixed = tuple(f for f in fixed if f[0] != "dash below the column")'''
assert old in s; s=s.replace(old,new)
old='''                    "carrier/column covers": (Cl, COV), "motor/column covers": (Ml, COV), "motor/dash": (Ml, DASH),'''
new='''                    "carrier/column covers": (Cl, COV), "motor/column covers": (Ml, COV),'''
assert old in s; s=s.replace(old,new)
old='''            "lever bolt/hinge block": (LBr, HB), "switch screws/hinge block": (SWSr, HB), "gear/column covers": (Gr, COV),
            "carrier/column covers": (Cr, COV), "motor/dash": (Mr, DASH), "gear/spoke sweep zone": (Gr, ZONE)}'''
new='''            "lever bolt/hinge block": (LBr, HB), "switch screws/hinge block": (SWSr, HB), "gear/column covers": (Gr, COV),
            "carrier/column covers": (Cr, COV), "gear/spoke sweep zone": (Gr, ZONE)}'''
assert old in s; s=s.replace(old,new)
# rear reach helper
old='''def window_check(t: CP.RingTeeth) -> dict:'''
new='''def reach_back(A: ColumnAssembly) -> float:
  """How far behind the middle of the grip the parts reach (mm): the dash panel below the column must be further."""
  return round(-min(m.bounding_box()[2] for m in (A.motor(), A.hinge_block(), A.clamp(), A.clamp_upper(), A.rods(), A.arm())), 0)


def window_check(t: CP.RingTeeth) -> dict:'''
assert old in s; s=s.replace(old,new)
open(p,'w').write(s)

p='accord_lka_parts.py'; s=open(p).read()
old='''    rep["clearances"] = CA.margins(A)
    # how far back the parts reach: the dash panel below the column must be behind that
    rear = min(m.bounding_box()[2] for m in (A.motor(), A.hinge_block(), A.clamp(), A.clamp_upper(), A.rods(), A.arm()))
    rep["clearances"]["parts_reach_back_to_mm_behind_grip"] = round(-rear, 0)'''
new='''    rep["clearances"] = CA.margins(A)
    rep["clearances"]["parts_reach_back_to_mm_behind_grip"] = CA.reach_back(A)   # the dash below the column must be further'''
assert old in s; s=s.replace(old,new)
old='''      assy = dict(cbase, arm=arms.get(f.arm_len) or MP.arm(f.arm_len))
      res = CA.check_all(CA.ColumnAssembly(t, f, assy, args.cover_width, h, -behind), lever_step=8.0)
      bad = [k for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
      row.append(f"arm-{int(f.arm_len):03d}" if not bad else "no")'''
new='''      assy = dict(cbase, arm=arms.get(f.arm_len) or MP.arm(f.arm_len))
      A_ = CA.ColumnAssembly(t, f, assy, args.cover_width, h, -behind)
      res = CA.check_all(A_, lever_step=8.0, dash=False)
      bad = [k for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)]
      row.append(f"arm-{int(f.arm_len):03d} ({CA.reach_back(A_):.0f})" if not bad else "no")'''
assert old in s; s=s.replace(old,new)
old='''  L.append("WHICH CLAMP POSITIONS WORK (rows: the covers' height; columns: the clamp's middle, mm behind the middle of the grip). "
           "Each arm named reaches with both joints in range and nothing touching.")
  L.append("        " + "".join(f"{x:>10}" for x in gr["clamp_behind_mm"]))
  for h, row in zip(gr["cover_height_mm"], gr["cells"]):
    L.append(f"  {h:5}  " + "".join(f"{x:>10}" for x in row))'''
new='''  L.append("WHICH CLAMP POSITIONS WORK (rows: the covers' height; columns: the clamp's middle, mm behind the middle of the grip). "
           "Each arm named reaches with both joints in range and nothing touching; in brackets, how far back the parts then "
           "reach (mm behind the middle of the grip): the dash below the column must be further than that.")
  L.append("        " + "".join(f"{x:>14}" for x in gr["clamp_behind_mm"]))
  for h, row in zip(gr["cover_height_mm"], gr["cells"]):
    L.append(f"  {h:5}  " + "".join(f"{x:>14}" for x in row))'''
assert old in s; s=s.replace(old,new)
open(p,'w').write(s)
p='columnparts.py'; s=open(p).read()
s=s.replace("ROD_LEN = 200.0               # M6 threaded rod, four pieces this long (cut shorter to suit: the report says how much is used)",
            "ROD_LEN = 180.0               # M6 threaded rod, four pieces this long (cut shorter to suit: the report says how much is used)")
open(p,'w').write(s); print("ok")
EOF