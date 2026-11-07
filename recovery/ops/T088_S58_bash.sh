python3 - <<'EOF'
p='columnparts.py'; s=open(p).read()
s=s.replace("""    zr0, zr1 = Z_ROLL_C
    zt0 = Z_TEETH_C[0]
    ring_back = zf - FRONT_RING_T""","""    zr0, zr1 = Z_ROLL_C
    ring_back = zf - FRONT_RING_T""")
s=s.replace("""  zt1 = Z_TEETH_C[1]
  zr0, zr1 = Z_ROLL_C
  zf = zt1 + t.teeth_chamfer + 2.0""","""  zt0, zt1 = Z_TEETH_C
  zr0, zr1 = Z_ROLL_C
  zf = zt1 + t.teeth_chamfer + 2.0""")
open(p,'w').write(s)
p='margins.py'; s=open(p).read()
old="""                  f"{sigma:.1f} MPa at the skirt's root: {push_n:.0f} N at the end of the {P.SKIRT_T:.0f} mm skirt, {length:.0f} mm from the "
                  f"front ring, taken over {SKIRT_SPREAD_MM:.0f} mm of its width","""
new="""                  f"{sigma:.1f} MPa at the skirt's root: {push_n:.0f} N at the end of the {P.SKIRT_T:.0f} mm skirt, {length:.0f} mm "
                  f"from the front ring, taken over {SKIRT_SPREAD_MM:.0f} mm of its width","""
assert old in s; s=s.replace(old,new); open(p,'w').write(s); print("ok")
EOF
/home/claude/bin/ruff check --output-format concise --line-length 140 --select E,F,W . ; echo "E/F/W exit $?"; PYTHONPATH=/home/claude/pylib python3 -c "
import columnparts as CP, params as P
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP); m = CP.ring_tooth_fit_test(t); print(len(m.decompose()), m.status())"