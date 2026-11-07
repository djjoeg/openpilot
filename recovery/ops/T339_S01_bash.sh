cd /home/claude/deliver && python3 - <<'EOF'
p = "hardware/cad/platefit.py"
s = open(p, encoding="utf-8").read()
a = """YOUR_PRINTER = 3.75 / 4.0 # your printer's page: the template's 4 in bar came out 3 3/4 in (4 Nov)
"""
b = """YOUR_PRINTER = 3.75 / 4.0 # your printer's page: the template's 4 in bar came out 3 3/4 in (4 Nov)
PAPER_SCALE = 4.03125 / 4.0   # the scaled template as you printed it: its 4 in bar came out 4 1/32 in (4 Nov), so
                              # it is 0.78% big; measurements read off it are divided by this. (So the printer
                              # really prints at about 94.5%: use 0.945 for YOUR_PRINTER next time.)
"""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)

p = "CHANGELOG.md"
s = open(p, encoding="utf-8").read()
a = """  check the printer shrinks both ways the same."""
b = """  check the printer shrinks both ways the same. As printed, its 4 in bar measures 4 1/32 in: the paper template you
  have is 0.78% big (1.3 mm over the plate's 166 mm width), which comes off any measurement read from it."""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
cd hardware/cad && ruff check platefit.py | tail -1