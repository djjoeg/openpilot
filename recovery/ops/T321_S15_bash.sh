python3 - <<'EOF'
import re
p = 'rightcheck.py'
s = open(p, encoding='utf-8').read()
src = open('/dev/stdin').read() if False else None
# reuse the replacement list from the previous attempt, with section 1's old text as it really is
old1 = """  rx = hardware(0.0, RA.STOP_GAP, True)["receiver bolt"]
  for dx in (-20.0, 20.0):
    sh = {"arm": arm.translate((dx, 0.0, 0.0))}
    for dz in (0.0, RA.DZ_OUT):
      sh.update({f"{k} slid {dz:+.0f}": m.translate((dx, 0.0, 0.0)) for k, m in moving(dz).items()})
    sh.update({f"{k} wings turning": m for k, m in hardware(0.0, RA.STOP_GAP, True, dx).items()
               if "receiver" not in k and "nut" not in k})"""
new1 = """  rx = hardware(0.0, True)["receiver bolt"]
  for dx in (-5.0, 20.0):                  # v5: in by more than 5.5 the deep part meets the receiver's end
    sh = {"arm": arm.translate((dx, 0.0, 0.0))}
    for dz in (0.0, RA.DZ_OUT):
      sh.update({f"{k} slid {dz:+.0f}": m.translate((dx, 0.0, 0.0)) for k, m in moving(dz).items()})
    sh.update({f"{k} wings turning": m for k, m in hardware(0.0, True, dx).items()
               if "receiver" not in k and "nut" not in k})"""
assert s.count(old1) == 1
s = s.replace(old1, new1)
s = s.replace("""  # 1. the fixed parts against each other (the arm in the receiver); then the arm slid 20 mm in or out across, with
  # the carrier and its bolts on it, against the plate, the cover and the receiver's wing bolt turning""",
"""  # 1. the fixed parts against each other (the arm in the receiver); then the arm slid 5 mm in or 20 out across, with
  # the carrier and its bolts on it, against the plate, the cover and the receiver's wing bolt turning""")
open(p, 'w', encoding='utf-8').write(s)
print('section 1 ok')
EOF