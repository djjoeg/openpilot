cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p = 'photocomp.py'
s = open(p).read()
a = s.index('  # the car in front: its edge blurred as the photo blurs it')
b = s.index('  out = lin_to_srgb(acc)')
new = '''  # the parts blurred as the lens blurs them: each pixel spread over its own disc (the discs sorted into a few sizes,
  # each pixel shared between the two nearest sizes so nothing shows a seam), the spreads added up
  m = A > 1e-4
  Cs = np.zeros_like(C)
  As = np.zeros_like(A)
  if m.any():
    r = np.where(m, coc_px(L["Z"], focus, aperture_mm, f_px) / 2, 0.0)
    lo, hi = max(float(r[m].min()), 0.5), max(float(r[m].max()), 0.6)
    levels = np.unique(np.round(np.geomspace(lo, hi, levels_n), 3))
    idx = np.interp(r, levels, np.arange(len(levels), dtype=float))
    for k, rk in enumerate(levels):
      wk = np.clip(1.0 - np.abs(idx - k), 0.0, 1.0) * m
      if not wk.any():
        continue
      Cs += disk_blur(C * wk[..., None], rk)
      As += disk_blur(A * wk, rk)
  Cn = Cs / np.maximum(As, 1.0)[..., None]
  An = np.clip(As, 0.0, 1.0)
  # the car in front of a part hides it, its edge blurred as the photo blurs it
  vis = np.ones_like(An)
  if L["occ"].max() > 0:
    sel = L["occ"] > 0.5 if (L["occ"] > 0.5).any() else L["occ"] > 0
    zo = occ_depth if occ_depth is not None else float(np.median(L["Zocc"][sel]))
    ro = coc_px(zo, focus, aperture_mm, f_px) / 2
    vis = 1.0 - np.clip(disk_blur(L["occ"], ro), 0, 1)
  acc = bg * (1.0 - An * vis)[..., None] + Cn * vis[..., None]
'''
s = s[:a] + new + s[b:]
s = s.replace("              occ_depth=None, slices=7, seed=2, knee=0.55):", "              occ_depth=None, levels_n=10, seed=2, knee=0.55):")
s = s.replace("    cover = np.clip(disk_blur(A, 1.0), 0, 1)[..., None]", "    cover = (An * vis)[..., None]")
open(p, 'w').write(s)
print('ok')
EOF
sed -n 289,345p photocomp.py