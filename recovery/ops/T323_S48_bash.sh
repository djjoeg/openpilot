python3 - <<'EOF'
p = "allinone.py"
s = open(p, encoding="utf-8").read()
a = s[s.index('"""\nOne print'):s.index("  python3 allinone.py")]
b = '''"""
One print for everything the right-arm build needs (2 Nov 2026; 3 Nov: the arm and carrier v6, the fit print, the
frame plate v5, the teeth v3): the frame plate v5, the steering wheel teeth v3 (the 20 set: 19 teeth, 19.5 degrees
each way, the channel 7 mm in, the ends cut back to the teeth), the arm and the motor carrier, on one 256 x 256 mm
bed, each piece with its own settings (the frame plate and the teeth 40% gyroid, the arm and the carrier solid).
Plate 13b is the same without the frame plate.

'''
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
sed -n 1,10p allinone.py