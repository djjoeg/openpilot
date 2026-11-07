python3 - <<'EOF'
import re
p = "sideparts.py"
s = open(p).read()
old_prism = s[s.index("def prism_y("):s.index("def _box_poly(")]
new_prism = '''def prism_y(points_xz, y0, y1) -> Manifold:
  """Extrudes an (x, z) outline along Y from y0 to y1 (either winding)."""
  cs = CrossSection([list(points_xz)])
  if cs.area() < 1e-9:
    cs = CrossSection([list(points_xz)[::-1]])
  # extruded points are (u=x, v=z, w); map (u, v, w) -> (u, y1 - w, v), a proper rotation
  return cs.extrude(y1 - y0).transform([[1, 0, 0, 0], [0, 0, -1, y1], [0, 1, 0, 0]])


'''
s = s.replace(old_prism, new_prism)
# drop the unused helper
s = s.replace(s[s.index("def _box_poly("):s.index("# ***** the gear *****\n\ndef gear_roofs")], "")
old_pin = s[s.index("def pin_back_at("):]
new_pin = '''def pin_back_at(s: float) -> float:
  """How far the ear holds the plunger's pin back (mm) with the bracket slid in s mm: 0 in its hole or clear of the ear,
  PIN_IN on the flat, between on the ramp."""
  rel = PIN_Z + s                            # the pin's middle along the ear (the ear's own place, motor on)
  pin_r = KIPP["pin_d"] / 2
  hole0, hole1 = PIN_Z - PIN_HOLE_D / 2, PIN_Z + PIN_HOLE_D / 2
  top, ramp0 = EAR_Z[1], EAR_Z[1] - BEVEL_LEN

  def back(z):
    if z < EAR_Z[0] or z > top or hole0 < z < hole1:
      return 0.0
    if z <= ramp0:
      return X_PIN_TIP - X_EAR[0]
    x_face = X_EAR[0] + (BEVEL_TOP - X_EAR[0]) * (z - ramp0) / BEVEL_LEN
    return max(0.0, X_PIN_TIP - x_face)

  return float(max(back(z) for z in np.linspace(rel - pin_r, rel + pin_r, 41)))
'''
s = s.replace(old_pin, new_pin)
open(p, "w").write(s)
EOF
grep -n "_box_poly\|def prism_y\|def pin_back_at" sideparts.py