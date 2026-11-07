python3 - <<'EOF'
p='columnassembly.py'; s=open(p).read()
s=s.replace('''    m = self.p["clamp_upper"].rotate((0, 0, 180)).rotate((180, 0, 0))     # V opening down, +z kept towards the driver
    return m.translate((0.0, -self.saddle_org[1], self.clamp_z))''','''    m = self.p["clamp_upper"].rotate((0, 0, 180))     # V opening down; +z stays towards the driver
    return m.translate((0.0, -self.saddle_org[1], self.clamp_z))''')
s=s.replace('''    return CP.rods_and_nuts(self.cover_h + 2 * (-self.saddle_org[1] - self.cover_h / 2 - CP.PAD_T)).translate(tuple(self.saddle_org))''',
            '''    return CP.rods_and_nuts(-2.0 * self.saddle_org[1]).translate(tuple(self.saddle_org))''')
s=s.replace('''    pts = [(a * math.cos(u), b * math.sin(u)) for u in np.linspace(0, 2 * math.pi, 96, endpoint=False)]
    from manifold3d import CrossSection
    return CrossSection([pts])''','''    pts = [(a * math.cos(u), b * math.sin(u)) for u in np.linspace(0, 2 * math.pi, 96, endpoint=False)]
    return CrossSection([pts])''')
s=s.replace("from manifold3d import Manifold\n","from manifold3d import CrossSection, Manifold\n")
s=s.replace("from cadlib import box, cyl, revolve, union\n","from cadlib import box, cyl, revolve\n")
open(p,'w').write(s)
p='columnparts.py'; s=open(p).read()
old=s[s.index("def rods_and_nuts"):s.index("def pads")]
new='''def rods_and_nuts(top: float) -> Manifold:
  """The four threaded rods with a nut and washer above the upper saddle and below the lower one (lower saddle
  frame). top: the upper saddle's V middle above the lower one's (twice the saddles' distance from the column)."""
  parts = []
  for sx in (-1, 1):
    x = sx * (ROD_SLOT_X[0] + ROD_SLOT_X[1]) / 2
    for z in ROD_Z:
      y0 = SADDLE_BOTTOM - 1.5 - 5.4 - 2.0
      parts.append(cyl_y(3.0, y0, y0 + ROD_LEN, x=x, z=z, segments=24))
      parts.append(MP.hex_prism_z_at(M6_NUT_AF, 0, 5.4, 0, 0).rotate((-90, 0, 0)).translate((x, SADDLE_BOTTOM - 1.5 - 5.4, z)))
      parts.append(MP.hex_prism_z_at(M6_NUT_AF, 0, 5.4, 0, 0).rotate((-90, 0, 0)).translate((x, top - SADDLE_BOTTOM + 1.5, z)))
  return union(parts)


'''
s=s.replace(old,new)
s=s.replace("SADDLE_HALF_X = 88.0          # the saddles reach this far each side (the rod slots are near the ends)",
            "SADDLE_HALF_X = 92.0          # the saddles reach this far each side (the rod slots are near the ends)")
open(p,'w').write(s); print("ok")
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 - <<'EOF'
import time, json
t0=time.time()
import params as P, columnparts as CP, columnassembly as CA, mountparts as MP, wheelparts as WP
t = CP.RingTeeth(P.WHEEL_OD, P.GRIP)
fit = CA.solve()
print("fit:", fit.ok, "arm_deg", round(fit.arm_deg,1), "reach", round(fit.reach,1), "arm", fit.arm_len, "slide", round(fit.slide,1), fit.notes, "saddle_y", round(CA.saddle_y(),1))
parts = {"teeth": CP.ring_teeth(t), "gear": WP.motor_gear(), "gear_teeth_only": WP.motor_gear_teeth_only(),
         "carrier": MP.motor_carrier(), "hinge_block": MP.hinge_block(), "bracket": MP.lever_bracket(), "lever": MP.lift_lever(),
         "lever_no_tab": MP.lift_lever(with_finger=False), "tab": MP.lever_tab(), "clamp_lower": CP.column_clamp_lower(),
         "clamp_upper": CP.column_clamp_upper()}
A = CA.ColumnAssembly(t, fit, parts)
res = CA.check_all(A, lever_step=8.0)
bad = {k: round(v,2) for k, v in res.items() if ("should touch" not in k and v > 1e-3) or ("should touch" in k and v > -1e-3)}
print(len(res), "checks;", len(bad), "bad:"); print(json.dumps(bad, indent=1))
print("margins:", CA.margins(A))
print("window:", CA.window_check(t))
print(round(time.time()-t0,1), "s")
EOF