python3 - <<'EOF'
p = "rightarm.py"
s = open(p).read()
for a, b in (("TONGUE_Z = (-95.0, -73.0)                # with the motor at its nominal place in the teeth",
              "TONGUE_Z = (-94.5, -72.5)                # with the motor at its nominal place in the teeth"),
             ("STOP_P = 6.0                             # it pokes this far below the cap at the nominal depth (2 to 10: +-4 mm)",
              "STOP_P = 5.5                             # it pokes this far below the cap at the nominal depth (1.5 to 9.5: +-4 mm)")):
  assert s.count(a) == 1, a
  s = s.replace(a, b)
open(p, "w").write(s)

p = "rightcheck.py"
s = open(p).read()
start = s.index("  # 3. the bolts and nuts")
end = s.index("  # 4. the steering wheel turned")
s = s[:start] + '''  # 3. the bolts and nuts, and the room to turn the wing bolts, with the motor at the deepest, nominal and
  # shallowest stop and slid out, against the parts and the motor (their shanks go through clearance holes)
  for dz in (RA.DZ_DEEP, 0.0, RA.DZ_SHALLOW):
    p = RA.STOP_P - dz
    for slid in (dz, RA.DZ_OUT):
      mg = RA.motor_and_gear(slid)
      moving = {"carrier": RA.carrier(slid), "motor": mg["motor"], "board": mg["board"], "gear": mg["gear"]}
      for swept in (False, True):
        for hn, hm in hardware(slid, p, swept).items():
          if swept and "nut" in hn:
            continue
          for on, om in {**fixed, **moving}.items():
            check(f"stop {p:.1f}, slid {slid:+.0f}: {hn}{' wings turning' if swept else ''} / {on}", hm, om)

''' + s[end:]
start = s.index("def hardware_shank(")
end = s.index('if __name__ == "__main__":')
s = s[:start] + s[end:]
s = s.replace('''  pin = (sweep() if swept else wing_bolt()).rotate((-90.0, 0.0, 0.0))          # -z -> +y (the shank along +v)''',
              '''  pin = (sweep() if swept else wing_bolt()).rotate((90.0, 0.0, 0.0))           # -z -> +y: the shank along +v''')
s = s.replace('''  pn = (hex_prism_z(7.95, -2.0, 2.0) - cyl(2.5, -3.0, 3.0, segments=24)).rotate((-90.0, 0.0, 0.0))''',
              '''  pn = (hex_prism_z(7.95, -2.0, 2.0) - cyl(2.5, -3.0, 3.0, segments=24)).rotate((90.0, 0.0, 0.0))''')
open(p, "w").write(s)
print("ok")
EOF
PYTHONPATH=/home/claude/pylib timeout 3000 python3 rightcheck.py 2>&1 | tail -70