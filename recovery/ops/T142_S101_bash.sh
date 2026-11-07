python3 - <<'EOF'
import pathlib
p = pathlib.Path("popparts.py")
s = p.read_text()
for old, new in [("PL_HOOK_X = (-2.0, 16.0)      # the hook behind the tab, up to its arm's swing",
                  "PL_HOOK_X = (0.0, 16.0)       # the hook behind the tab, up to its arm's swing"),
                 ("PL_SLOTS = ((40.0, -98.0, -209.0), (6.0, -158.0, -209.0))   # the tabs' slots: x, from z, to z",
                  "PL_SLOTS = ((40.0, -98.0, -209.0), (8.5, -158.0, -209.0))   # the tabs' slots: x, from z, to z")]:
    assert s.count(old) == 1, old
    s = s.replace(old, new)
p.write_text(s)
p = pathlib.Path("popassembly.py")
s = p.read_text()
old = '''                ("4 x 16 self-tapping, middle", (-12.0, -200.0), 1))'''
assert s.count(old) == 1
s = s.replace(old, '''                ("4 x 16 self-tapping, middle", (-12.0, -208.0), 1))''')
p.write_text(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import popassembly as PA
for t in PA.tab_placements(): print(t[0], tuple(round(v,1) for v in t[3]), 'reach', t[4])
"