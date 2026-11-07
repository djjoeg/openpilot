sed -i 's/^import sideparts as S$/import sideparts as S\nimport slideparts as SP/' sideassembly.py && PYTHONPATH=/home/claude/pylib python3 -c "
import sideassembly as SA, json
for D in (106.0, 110.0, 116.0, 125.0):
  print(SA.foot_fit(D))
"