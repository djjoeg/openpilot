python3 - <<'EOF'
a=open('columnassembly.py').read()
a=a.replace('''  def __init__(self, t: CP.RingTeeth, fit: ColumnFit, parts: dict, cover_w: float = COVER_W, cover_h: float = COVER_H,
               clamp_z: float = CLAMP_Z, mount_deg: float = 0.0):
    self.t, self.fit, self.p = t, fit, parts''', '''  def __init__(self, t: CP.RingTeeth, fit: ColumnFit, parts: dict, cover_w: float = COVER_W, cover_h: float = COVER_H,
               clamp_z: float = CLAMP_Z, mount_deg: float = 0.0, cover_front_w: float = COVER_FRONT_W):
    self.t, self.fit, self.p = t, fit, parts
    self.cover_front_w = cover_front_w''')
a=a.replace("    front_w = min(COVER_FRONT_W, self.cover_w)", "    front_w = min(self.cover_front_w, self.cover_w)")
a=a.replace('''  def __init__(self, t: CP.RingTeeth, fit: SideFit, parts: dict, cover_w: float = COVER_W, cover_h: float = COVER_H):
    super().__init__(t, fit, parts, cover_w, cover_h, fit.bracket_z, 90.0 + fit.ring_at)''',
'''  def __init__(self, t: CP.RingTeeth, fit: SideFit, parts: dict, cover_w: float = COVER_W, cover_h: float = COVER_H,
               cover_front_w: float = COVER_FRONT_W):
    super().__init__(t, fit, parts, cover_w, cover_h, fit.bracket_z, 90.0 + fit.ring_at, cover_front_w)''')
open('columnassembly.py','w').write(a)
print('ok')
EOF
echo done