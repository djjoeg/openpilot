python3 - << 'EOF'
p = "params.py"
s = open(p).read()
old = s[s.index("# ***** arm, dash clamp, lift lever *****"):s.index("BED = ")]
new = '''# ***** arm and dash clamp *****

ARM_W, ARM_T = 36.0, 18.0     # arm bar: width (across, along the bolts) and thickness
ARM_LENGTHS = (70, 90, 110, 130, 150, 170, 190)   # arms to print: dash clamp bolt to hinge block bolt, mm
ARM_SLIDE = 10.0              # each arm slides +- this much at the dash clamp, so the lengths overlap
HOOD_EDGE_MIN, HOOD_EDGE_MAX = 3.0, 26.0   # thickness range of the cover edge the dash clamp grips
CLAMP_DEPTH = 75.0            # how far the dash clamp's top plate reaches back over the cover

'''
s = s.replace(old, new)
open(p, "w").write(s)
EOF
grep -n "ARM_\|HOOD\|CLAMP_DEPTH\|TAIL\|HINGE_R\|KNUCKLE" params.py