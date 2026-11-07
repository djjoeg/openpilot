python3 - <<'EOF'
p='midteeth.py'; s=open(p).read()
old=s[s.index('  def profile(self):'):s.index('def ends_cut')]
new='''  def profile(self):
    """The side-slide profile with the inner wall (its inside, its 45 degree corner and its outside) moved out by
    inner_pull towards the grip's middle; the back between the corners is that much shorter."""
    rr, rho, c1, p = self.rr, self.rho, self.c1, self.inner_pull
    w_in, k_i = self.w_in, self.k_i + p          # w_in already includes the pull; the corner's outside line is r + z = k_i
    r0 = FP.FACE_BAND[0]
    z_corner_at_teeth = k_i - r0                 # where the corner's outside line passes the teeth's inner end
    inner_outside = [(r0, z_corner_at_teeth)] if z_corner_at_teeth > self.z_root else [(k_i - self.z_root, self.z_root)]
    return [
      (rr - rho + p, FP.FRONT_Z), (rr - rho + p, -c1), (rr - c1 + p, self.z_bridge), (rr + c1, self.z_bridge), (rr + rho, -c1),
      (rr + rho, FP.FRONT_Z), (self.w_out, FP.FRONT_Z), (self.w_out, self.w_out - self.k_o),
      (self.k_o + self.z_flat, self.z_flat), (FP.ROLL_BAND[1], self.z_flat), (FP.ROLL_BAND[1], self.z_band),
      (FP.ROLL_BAND[0], self.z_band), (FP.ROLL_BAND[0], self.z_root), (FP.FACE_BAND[1], self.z_root), (FP.FACE_BAND[1], self.z_tip),
      (r0, self.z_tip), (r0, self.z_root), *inner_outside,
      (w_in, k_i - w_in), (w_in, FP.FRONT_Z),
    ]


'''
s=s.replace(old,new)
open(p,'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 midteeth.py 2>&1 | tail -8