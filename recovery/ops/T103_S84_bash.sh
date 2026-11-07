python3 - <<'EOF'
src=open('columnparts.py').read()
src=src.replace('''  s0, s1 = TAB_SLOT[0] + M5_CLEAR / 2, TAB_SLOT[1] - M5_CLEAR / 2
  return (SB_BAR_HOLES[1] - s1, SB_BAR_HOLES[0] - s0)''',
'''  s0, s1 = TAB_SLOT[0] + M5_CLEAR / 2, TAB_SLOT[1] - M5_CLEAR / 2
  return (max(SB_BAR_HOLES[1] - s1, SB_PLATE_X[1] + 0.5), SB_BAR_HOLES[0] - s0)   # and clear of the plate''')
open('columnparts.py','w').write(src)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import columnparts as CP, columnassembly as CA
print(CP.tab_slide_range())
for r in (-20, 0, 25, 50, 75, 100, 125, 150, 170):
    f = CA.solve_side(screw_right=r); print(r, f.ok, f.tab_len, round(f.tab_x0,1), f.notes)
"; PYTHONPATH=/home/claude/pylib timeout 900 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side_test.py 2>&1 | grep -v "^margins" | tail -4