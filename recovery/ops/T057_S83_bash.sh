python3 - <<'EOF'
import re
p='accord_lka_parts.py'
s=open(p).read()
s=s.replace('ASA_DENSITY = 1.07      # g/cm^3\n','PETG_DENSITY = 1.28     # g/cm^3, Bambu Lab PETG HF data sheet (V1.0)\n',1)
s=s.replace('round(vol * ASA_DENSITY, 1)','round(vol * PETG_DENSITY, 1)',1)
s=s.replace('L.append(f"CLICK (estimates for ASA): ','L.append(f"CLICK (estimates for PETG): ',1)
assert 'ASA_DENSITY' not in s and 'estimates for ASA' not in s
open(p,'w').write(s)
p='mountparts.py'
s=open(p).read()
old1='FINGER_E = 2000.0                     # ASA\'s stiffness, N/mm^2 (about 2 GPa), for the click\'s force estimate\n'
new1='FINGER_E = 1810.0                     # PETG\'s stiffness along its layers, N/mm^2 (Bambu Lab PETG HF data sheet: 1810\n                                      # MPa in X-Y; the tab is printed flat, so it bends along its layers)\n'
old2='RUB = 0.35                            # rubbing (friction) between printed ASA parts, an estimate\n'
new2='RUB = 0.35                            # rubbing (friction) between dry printed PETG parts, an estimate\n'
assert old1 in s and old2 in s
s=s.replace(old1,new1,1).replace(old2,new2,1)
open(p,'w').write(s)
EOF
grep -rn "ASA" *.py | grep -v "ASA_SOFT_C\|in ASA\|printed in ASA" 