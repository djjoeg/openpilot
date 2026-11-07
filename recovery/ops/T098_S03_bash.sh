cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
p='columnparts.py'; s=open(p).read()

# 1. RingTeeth: shallow channel option and stored channel reach
old='''class RingTeeth:
  """Radii and angles of the ring teeth (the short set) for one steering wheel size."""

  def __init__(self, wheel_od: float, grip: float):
    self.base = WP.Teeth(wheel_od, grip, 15)        # the channel round the grip and the zip ties: the short set's
    b = self.base
    self.n_teeth = b.n_teeth
    self.tie_angles = b.tie_angles'''
new='''SHALLOW_REACH = 8.0           # a shallow channel's walls reach only this far in from the middle of the grip, so the
                              # piece can sit over a spoke's junction with the grip (the right-side ring)
SLOT_EVERY_DEG = 4.5          # zip tie slots all along the piece, this far apart: tie it where the spokes allow


class RingTeeth:
  """Radii and angles of the ring teeth (the short set) for one steering wheel size. shallow: the channel's walls
  reach only SHALLOW_REACH in from the middle of the grip instead of wrapping it to its middle."""

  def __init__(self, wheel_od: float, grip: float, shallow: bool = False):
    self.base = WP.Teeth(wheel_od, grip, 15)        # the channel round the grip and the zip ties: the short set's
    b = self.base
    self.shallow = shallow
    self.front_inner = b.rr + SHALLOW_REACH if shallow else b.front_inner
    self.back_inner = b.rr + SHALLOW_REACH + 1.0 if shallow else b.back_inner
    self.z_slope_top = b.r_in - (self.back_inner + b.wz_out)   # the 45 degree back slope meets the outer band here
    self.n_teeth = b.n_teeth
    self.tie_angles = b.tie_angles'''
assert old in s; s=s.replace(old,new)
old='''    return [
      (b.front_inner, zf), (b.front_inner, b.wz), (b.r_in, b.wz), (b.r_in, b.z_slope_top), (b.back_inner, zk),
      (b.r_base, zk), (b.r_base, ring_back), (self.r_skirt_in, ring_back),'''
new='''    return [
      (self.front_inner, zf), (self.front_inner, b.wz), (b.r_in, b.wz), (b.r_in, self.z_slope_top), (self.back_inner, zk),
      (b.r_base, zk), (b.r_base, ring_back), (self.r_skirt_in, ring_back),'''
assert old in s; s=s.replace(old,new)

# 2. tie slots everywhere, and the ring at any clock position
old='''def tie_slots(t: RingTeeth) -> Manifold:
  angles = [270.0 + a for a in t.tie_angles] + [270.0 - a for a in t.tie_angles]
  return WP.tie_slots(t.base, angles)


def ring_teeth(t: RingTeeth) -> Manifold:
  """The ring teeth in one piece (it spans about 56 degrees, so it fits a 220 mm bed)."""
  return clean(ring_teeth_solid(t) - tie_slots(t))'''
new='''def slot_angles(t: RingTeeth) -> list:
  """Zip tie slots every SLOT_EVERY_DEG, from near the middle out to near the ends, each side of the middle."""
  out = []
  a = SLOT_EVERY_DEG / 2
  while a + WP.TIE_W / 2 / t.base.r_in * 57.3 < t.half - 1.0:
    out += [a, -a]
    a += SLOT_EVERY_DEG
  return out


def tie_slots(t: RingTeeth) -> Manifold:
  return WP.tie_slots(t.base, [270.0 + a for a in slot_angles(t)])


def ring_teeth(t: RingTeeth, centre_deg: float = 270.0) -> Manifold:
  """The ring teeth in one piece (it spans about 56 degrees, so it fits a 220 mm bed), centred at centre_deg on the
  steering wheel (270 is 6 o'clock, 0 is 3 o'clock)."""
  return clean((ring_teeth_solid(t) - tie_slots(t)).rotate((0, 0, centre_deg - 270.0)))'''
assert old in s; s=s.replace(old,new)
open(p,'w').write(s); print("ok")
EOF
grep -n "TIE_W" /home/claude/deliver/hardware/cad/wheelparts.py | head -3