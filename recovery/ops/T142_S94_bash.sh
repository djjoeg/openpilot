python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
old = "  M5_CLEAR,\n  MOTOR_PLATE_T,"
assert s.count(old) == 1
s = s.replace(old, "  M5_CLEAR,\n  M5_NUT_AF,\n  M5_NUT_T,\n  MOTOR_PLATE_T,")
p.write_text(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import sys; sys.path.insert(0,'.')
import popparts as PP
tb = PP.pop_screw_tab(); print('tab', round(tb.volume()), [round(v,1) for v in tb.bounding_box()], len(tb.decompose()))
blk = PP.pop_hinge_block(); print('block', round(blk.volume()), len(blk.decompose()), [round(v,1) for v in blk.bounding_box()])
car = PP.pop_carrier(); print('carrier', round(car.volume()), len(car.decompose()))
# where is the block's flange in the wheel frame now?
bf = PP.to_wheel(PP._block_flange(), 0.0)
print('block flange wheel bbox', [round(v,1) for v in bf.bounding_box()])
bw = PP.to_wheel(blk, 0.0); print('block wheel bbox', [round(v,1) for v in bw.bounding_box()])
pl = PP.pop_column_plate()
print('block/plate overlap', round((bw ^ pl).volume(), 2))
"