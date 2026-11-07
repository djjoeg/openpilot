cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fea && python3 - <<'EOF'
s = open('armfea.py').read()
# 1) the model: add the frame plate and bond the bar into its receiver when the variant has "full"
old = '''  if "flange" in variant:'''
new = '''  if "full" in variant:
    m = m + RA.plate_to_wheel(RA.frame_plate_v4()) + box(73.0, 120.0, -143.4, -113.0, -175.4, -165.0)
  if "flange" in variant:'''
assert s.count(old) == 1
s = s.replace(old, new)
# 2) the support: the plate clamped round its two screws (washers 9 mm round) instead of the bar fixed in the receiver
old = '''  fixed = xyz[:, 0] <= 120.0 + 1e-6'''
new = '''  if "full" in VARIANT:
    screws = ((RA.CUP_X, RA.CUP_Z), (RA.CUP_X - 85.0, RA.CUP_Z + 40.0))
    fixed = np.zeros(len(xyz), dtype=bool)
    for sx, sz in screws:
      fixed |= ((xyz[:, 0] - sx) ** 2 + (xyz[:, 2] - sz) ** 2 <= 9.0 ** 2) & (xyz[:, 1] >= RA.COVER_Y - RA.PLATE_T - 0.5)
  else:
    fixed = xyz[:, 0] <= 120.0 + 1e-6'''
assert s.count(old) == 1
s = s.replace(old, new)
# 3) the grid reference: keep it, fine for the plate too
open('armfea_full.py', 'w').write(s)
print("ok")
EOF
grep -n "full" armfea_full.py | head