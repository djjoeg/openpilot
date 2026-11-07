python3 - <<'EOF'
src=open('columnparts.py').read()
old='''  pz0, pz1 = TAB_PLATE_Z
  plate = box(length - w, length, min(plate_y - h / 2, ya - 0.01), max(plate_y + h / 2, yb + 0.01), pz0, pz1)
  xs = length - TAB_SCREW_FROM_END
  plate = plate - Manifold.batch_hull([cyl(SCREW_CLEAR / 2, pz0 - 1, pz1 + 1, xs, plate_y - TAB_SLOT_HALF, 24),
                                       cyl(SCREW_CLEAR / 2, pz0 - 1, pz1 + 1, xs, plate_y + TAB_SLOT_HALF, 24)])
  return clean(bar + plate)'''
new='''  pz0, pz1 = TAB_PLATE_Z
  top = min(plate_y + h / 2, yb)      # never above the tab's bar: the bracket's bar is right above that
  plate = box(length - w, length, min(plate_y - h / 2, ya - 0.01), top, pz0, pz1)
  xs = length - TAB_SCREW_FROM_END
  slot_top = min(plate_y + TAB_SLOT_HALF, top - 5.0)
  plate = plate - Manifold.batch_hull([cyl(SCREW_CLEAR / 2, pz0 - 1, pz1 + 1, xs, plate_y - TAB_SLOT_HALF, 24),
                                       cyl(SCREW_CLEAR / 2, pz0 - 1, pz1 + 1, xs, slot_top, 24)])
  return clean(bar + plate)'''
assert old in src
src=src.replace(old,new)
src=src.replace('''  the screw. tab_len: a length other than the printed''','''  the screw. tab_len: a length other than the printed''')
open('columnparts.py','w').write(src)
a=open('columnassembly.py').read()
old2='''  if z_b + CP.SB_PLATE_Z[1] > COVER_FRONT_Z - 5.0:'''
new2='''  if -screw_down > CP.TAB_BAR_Y[1] - 10.0:
    notes.append(f"the screw is only {screw_down:.0f} mm below the column's axis: the screw tab's plate stops at the bracket's "
                 f"bar, so the screw must be at least {-CP.TAB_BAR_Y[1] + 10.0:.0f} mm below it")
  if z_b + CP.SB_PLATE_Z[1] > COVER_FRONT_Z - 5.0:'''
assert old2 in a
a=a.replace(old2,new2)
open('columnassembly.py','w').write(a)
b=open('accord_lka_parts.py').read()
b=b.replace('''"left out). A screw less than 240 mm behind the rim's front puts the bracket, which sits level with it, too close to "
           "the hinge block for the shortest arm; past 300 the column covers must reach further back than the dash below the "
           "column is estimated to be.")''','''"left out). A screw less than 250 mm behind the rim's front puts the bracket, which sits level with it, so close to "
           "the hinge block that the arm's fork meets it; past 300 the column covers must reach further back than the dash "
           "below the column is estimated to be.")''')
open('accord_lka_parts.py','w').write(b)
print('ok')
EOF
PYTHONPATH=/home/claude/pylib timeout 600 python3 - <<'EOF'
import sys
sys.path.insert(0, '/home/claude/deliver/hardware/cad')
import columnassembly as CA, columnparts as CP, mountparts as MP, wheelparts as WP, params as P
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP, shallow=True)
base = {"gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(), "bracket": MP.lever_bracket(),
        "lever": MP.lift_lever(), "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(),
        "teeth": CP.ring_teeth(t), "hinge_block": MP.hinge_block(CP.ARM_NOMINAL_C), "carrier": MP.motor_carrier(CP.GUARD_WINDOW_C),
        "side_bracket": CP.side_bracket()}
for right, behind, down in ((0, 280, 60), (0, 280, 45), (25, 250, 60), (45, 265, 60), (150, 340, 90)):
    f = CA.solve_side(120.0, right, down, behind)
    print(right, behind, down, f.ok, f.notes, f.arm_len, f.tab_len, round(f.tab_x0, 1), f.plate_y)
    if not f.ok: continue
    tab = CP.screw_tab(f.tab_len, f.plate_y); print('   tab', tab.status(), len(tab.decompose()), [round(v,1) for v in tab.bounding_box()])
    parts = dict(base, arm=MP.arm(f.arm_len), screw_tab=tab)
    A = CA.SideAssembly(t, f, parts)
    res = CA.check_all(A, lever_step=8.0, dash=False)
    bad = {k: v for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)}
    for k, v in bad.items(): print('   ', round(v, 2), k)
EOF