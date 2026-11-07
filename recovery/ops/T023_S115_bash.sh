python3 - <<'EOF'
p = "accord_lka_parts.py"
s = open(p).read()
old = '''    self.r_split = self.r_in + TIE_T + 0.8             # the halves' overlap: outer part on the left half, inner on the right'''
new = '''    self.r_split = self.r_in + 2.5                     # the halves' overlap: outer part on the left half, inner on the right'''
assert old in s; s = s.replace(old, new)
old = '''    if self.r_split > self.r_base - 0.6:
      raise ValueError("no room for the overlap between the two halves")'''
new = '''    if self.r_split + 1.0 > max(self.r_base, self.r_roll - (self.wz_out - Z_TEETH[1])):
      raise ValueError("no room for the overlap between the two halves")'''
assert old in s; s = s.replace(old, new)
old = '''def teeth_half(t: Teeth, side: str) -> Manifold:
  """side 'right': from 12 o'clock towards 3 o'clock (driver's right). 'left': towards 9 o'clock.
  The left half carries the outer band across 12 o'clock for SPLIT_LAP teeth into the right half's side; the
  right half carries the channel part there. Glue the overlap."""
  whole = teeth_solid(t)
  zlo, zhi = -t.wz_out - 2, t.wz_out + 2
  big = t.r_tip + 5
  if side == "right":
    keep = (sector(big, 90.0 - t.half - 1, 90.0 - t.lap, r_in=0.0)
            + sector(t.r_split, 90.0 - t.lap - 0.5, 90.0 + t.lap, r_in=0.0))
    angles = [90.0 - a for a in TIE_ANGLES]
  else:
    keep = (sector(big, 90.0 + t.lap, 90.0 + t.half + 1, r_in=0.0)
            + (sector(big, 90.0 - t.lap, 90.0 + t.lap + 0.5, r_in=0.0) - sector(t.r_split, 90.0 - t.lap - 1, 90.0 + t.lap + 1)))
    angles = [90.0 + a for a in TIE_ANGLES]
  part = whole ^ keep.extrude(zhi - zlo).translate((0, 0, zlo))
  return part - tie_slots(t, angles)'''
new = '''def teeth_half(t: Teeth, side: str, whole: Manifold | None = None) -> Manifold:
  """side 'right': from 12 o'clock towards 3 o'clock (driver's right). 'left': towards 9 o'clock.
  Across 12 o'clock, for SPLIT_LAP teeth each side, the left half carries the outer band with the teeth and the
  rolling band (r > r_split, from the back of the rolling band to the front face); the right half carries the
  channel part under it. Both print front face down without supports. Glue the overlap."""
  whole = whole if whole is not None else teeth_solid(t)
  zlo, zhi = -t.wz_out - 2, t.wz_out + 2
  big = t.r_tip + 5
  lap_zone = sector(big, 90.0 - t.lap, 90.0 + t.lap, r_in=0.0).extrude(zhi - zlo).translate((0, 0, zlo))
  outer_block = (sector(big, 90.0 - t.lap, 90.0 + t.lap, r_in=t.r_split)
                 .extrude(zhi - Z_ROLL[0]).translate((0, 0, Z_ROLL[0])))
  left_side = sector(big, 90.0 + t.lap, 90.0 + t.half + 1, r_in=0.0).extrude(zhi - zlo).translate((0, 0, zlo))
  right_side = sector(big, 90.0 - t.half - 1, 90.0 - t.lap, r_in=0.0).extrude(zhi - zlo).translate((0, 0, zlo))
  if side == "right":
    part = (whole ^ right_side) + (whole ^ (lap_zone - outer_block))
    angles = [90.0 - a for a in TIE_ANGLES]
  else:
    part = (whole ^ left_side) + (whole ^ lap_zone ^ outer_block)
    angles = [90.0 + a for a in TIE_ANGLES]
  return part - tie_slots(t, angles)


def teeth_one_piece(t: Teeth, whole: Manifold | None = None) -> Manifold:
  """The steering wheel teeth in one piece, for print beds about 250 mm or more across."""
  whole = whole if whole is not None else teeth_solid(t)
  return whole - tie_slots(t, [90.0 + a for a in TIE_ANGLES] + [90.0 - a for a in TIE_ANGLES])'''
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)
EOF
export PYTHONPATH=/home/claude/pylib:. && timeout 600 python3 -c "
import time
import accord_lka_parts as P
from manifold3d import CrossSection
t = P.Teeth()
for k in ('r_wheel','rr','rho','r_in','wz','wz_out','rp','r_root','r_tip','r_roll','r_base','teeth_half','roll_half','half','lap','r_split','front_inner','back_line','z_slope_top','back_inner'):
  print(k, round(getattr(t,k),3))
pr = t.profile(t.r_roll)
print(pr)
print('area', CrossSection([pr]).area())
pr2 = t.profile(t.r_base)
print(pr2, CrossSection([pr2]).area())
t0=time.time()
s = P.teeth_solid(t)
print('solid', s.status(), round(s.volume()/1000,2), s.genus(), s.num_tri(), round(time.time()-t0,2))
for side in ('right','left'):
  t0=time.time()
  h = P.teeth_half(t, side, s)
  print(side, h.status(), round(h.volume()/1000,2), h.genus(), h.num_tri(), [round(v,1) for v in h.bounding_box()], round(time.time()-t0,2))
o = P.teeth_one_piece(t, s)
print('one', o.status(), round(o.volume()/1000,2), o.genus(), [round(v,1) for v in o.bounding_box()])
"
