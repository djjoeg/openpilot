cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
src=open('columnparts.py').read()
src=src.replace("SB_BAR_X1 = 92.0                            # the bar's end\nSB_BAR_HOLES = (60.0, 80.0)                 # the screw tab's two M5 bolts through the bar, along y, at these x",
"SB_BAR_X1 = 112.0                           # the bar's end\nSB_BAR_HOLES = (80.0, 100.0)                # the screw tab's two M5 bolts through the bar, along y, at these x")
src=src.replace("TAB_LENGTHS = (100.0, 140.0, 180.0)         # screw tabs to print: bar length from the tab's start to the end plate",
"TAB_LENGTHS = (100.0, 160.0, 220.0)         # screw tabs to print: bar length from the tab's start to the end plate")
src=src.replace("TAB_SLOT = (3.0, 108.0)" if False else "TAB_SLOT = (3.0, 68.0)                      # the tab's slot for the bracket's two bolts, x range (tab frame)",
"TAB_SLOT = (3.0, 108.0)                     # the tab's slot for the bracket's two bolts, x range (tab frame): slides 60 mm")
open('columnparts.py','w').write(src)
a=open('columnassembly.py').read()
a=a.replace('''  if z_screw < DASH_Z:
    notes.append(f"the screw is {DASH_Z - z_screw:.0f} mm further back than the dash below the column is estimated to be; "
                 "check the covers reach that far back")
  return SideFit(not notes, arm, reach, arm_len, reach - arm_len if arm_len else 0.0, pv, notes,
                 bracket_z=z_b, screw_w=screw_w, tab_len=tab, tab_x0=tab_x0, plate_y=float(s_b[1]), ring_at=ring_at)''',
'''  warnings = []
  if z_screw < DASH_Z:
    warnings.append(f"the screw is {DASH_Z - z_screw:.0f} mm further back than the dash below the column is estimated to be: "
                    "the covers must reach that far back for the bracket")
  return SideFit(not notes, arm, reach, arm_len, reach - arm_len if arm_len else 0.0, pv, notes,
                 bracket_z=z_b, screw_w=screw_w, tab_len=tab, tab_x0=tab_x0, plate_y=float(s_b[1]), ring_at=ring_at,
                 warnings=warnings)''')
a=a.replace('''  plate_y: float = CP.TAB_PLATE_Y        # the tab's end plate middle (bracket frame y)
  ring_at: float = 0.0                   # the ring's middle, degrees above 3 o'clock''',
'''  plate_y: float = CP.TAB_PLATE_Y        # the tab's end plate middle (bracket frame y)
  ring_at: float = 0.0                   # the ring's middle, degrees above 3 o'clock
  warnings: list = field(default_factory=list)   # things to check that don't stop the fit''')
open('columnassembly.py','w').write(a)
b=open('accord_lka_parts.py').read()
b=b.replace('''                "notes": sfit.notes}
  checks = {}
  sbase = dict(base, teeth=cparts["ring-teeth-right"][0]''', '''                "notes": sfit.notes, "warnings": sfit.warnings}
  checks = {}
  sbase = dict(base, teeth=cparts["ring-teeth-right"][0]''')
b=b.replace('''  grid = {"screw_behind_mm": [200, 225, 250, 265, 280, 300, 320], "screw_right_mm": [20, 40, 60, 80, 100, 120], "cells": []}''',
'''  grid = {"screw_behind_mm": [240, 260, 280, 300, 320, 340], "screw_right_mm": [0, 25, 50, 75, 100, 125, 150], "cells": []}''')
b=b.replace('''  L.append("WHICH SCREW POSITIONS WORK (rows: the screw right of the wheel's edge, mm; columns: behind the front of the rim, mm). "
           "Each cell names the arm and screw tab that reach with both joints in range and nothing touching (the dash estimates "
           "left out).")
  L.append("        " + "".join(f"{x:>16}" for x in gr["screw_behind_mm"]))
  for h, row in zip(gr["screw_right_mm"], gr["cells"]):
    L.append(f"  {h:5}  " + "".join(f"{x:>16}" for x in row))''',
'''  L.append("WHICH SCREW POSITIONS WORK (rows: the screw right of the wheel's edge, mm; columns: behind the front of the rim, mm). "
           "Each cell names the arm and screw tab that reach with both joints in range and nothing touching (the dash estimates "
           "left out). A screw less than 240 mm behind the rim's front puts the bracket, which sits level with it, too close to "
           "the hinge block for the shortest arm; past 300 the column covers must reach further back than the dash below the "
           "column is estimated to be.")
  L.append("        " + "".join(f"{x:>16}" for x in gr["screw_behind_mm"]))
  for h, row in zip(gr["screw_right_mm"], gr["cells"]):
    L.append(f"  {h:5}  " + "".join(f"{x:>16}" for x in row))''')
b=b.replace('''  else:
    L.append("  does not fit: " + "; ".join(f["notes"]))
  if "clearances" in c:
    cl = c["clearances"]
    L.append(f"  lever up: motor gear {cl['motor_gear_to_ring_teeth_with_lever_up']} mm clear of the ring's teeth; the lift lever's "
             f"handle {cl['lift_lever_handle_to_the_spoke_sweep_zone']} mm behind where the spokes sweep; lever up, the handle "
             f"{cl['lift_lever_up_to_the_hub']} mm from the hub (25 means more than 25); the arm {cl['arm_to_the_column_covers']} mm "
             f"from the covers; the lift lever''', '''  else:
    L.append("  does not fit: " + "; ".join(f["notes"]))
  for w in f.get("warnings", []):
    L.append("  check: " + w)
  if "clearances" in c:
    cl = c["clearances"]
    L.append(f"  lever up: motor gear {cl['motor_gear_to_ring_teeth_with_lever_up']} mm clear of the ring's teeth; the lift lever's "
             f"handle {cl['lift_lever_handle_to_the_spoke_sweep_zone']} mm behind where the spokes sweep; lever up, the handle "
             f"{cl['lift_lever_up_to_the_hub']} mm from the hub (25 means more than 25); the arm {cl['arm_to_the_column_covers']} mm "
             f"from the covers; the lift lever''')
open('accord_lka_parts.py','w').write(b)
print('ok')
EOF
grep -n "TAB_SLOT = \|TAB_LENGTHS = \|SB_BAR_HOLES = " columnparts.py; PYTHONPATH=/home/claude/pylib python3 -c "
import columnparts as CP, columnassembly as CA
print(CP.tab_slide_range())
for r in (0, 25, 50, 75, 100, 125, 150):
    f = CA.solve_side(screw_right=r); print(r, f.ok, f.tab_len, round(f.tab_x0,1), f.notes)
"