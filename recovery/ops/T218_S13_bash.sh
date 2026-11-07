python3 - <<'EOF'
p='armmount.py'; s=open(p).read()
old=s[s.index('def picture(path: str) -> None:'):s.index('def main():')]
new='''def picture(path: str) -> None:
  import render as R
  parts = scene()
  blue = (0.35, 0.55, 0.85)
  bed = parts_on_bed()
  views = [(parts, R.look((0.9, -0.6, 0.8), (0, 1, 0))), (parts, R.look((0.0, -1.0, 0.0), (0, 0, 1))),
           ([(bed["arm-shoe"], blue)], R.view_matrix(-50, 35)), ([(bed["arm-bar"], blue)], R.view_matrix(-50, 35)),
           ([(bed["arm-bracket"], blue)], R.view_matrix(-50, 35)), ([(bed["column-frame-plate-v2"], (0.8, 0.82, 0.85))], R.view_matrix(-50, 35))]
  R.save(path, views, cols=2, size=(1000, 650),
         titles=["on the car, from your right and below", "from below (the wheel at the bottom)",
                 "shoe, as printed (its top on the bed, the fin up)", "arm, as printed",
                 "bracket, as printed (standing on its dash end)", "frame plate v2, as printed (labels up)"],
         suptitle="Arm mount v1 on the frame plate v2, under the column: the car grey, the plate light, the apparatus blue, "
                  "the motor dark, the gear and the teeth orange. The car is the photo model: rough.")


'''
s=s.replace(old,new)
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 armmount.py >/dev/null 2>&1; (ruff check armmount.py midteeth.py 2>&1 || true) | tail -5