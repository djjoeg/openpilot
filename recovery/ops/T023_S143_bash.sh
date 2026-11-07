python3 - <<'EOF'
p = "assembly.py"
s = open(p).read()
s = s.replace('''from params import (ARM_SLOT, COLUMN_TILT, GRIP, HINGE_FORWARD, HINGE_UP, MOTOR_TEETH, NEMA, NEMA_LEN, ROLL_GROW,
                    Z_GEAR_TEETH, Z_MOTOR_FACE)''', '''from params import ARM_SLOT, COLUMN_TILT, GRIP, HINGE_FORWARD, HINGE_UP, NEMA, NEMA_LEN, Z_MOTOR_FACE''')
s = s.replace('''def centre_distance(t: WP.Teeth) -> float:
  return t.r_roll + pitch_radius(MOTOR_TEETH) + ROLL_GROW''', '''def centre_distance(t: WP.Teeth) -> float:
  return WP.centre_distance()''')
s = s.replace("from gears import pitch_radius\n", "")
open(p, "w").write(s)
p = "mountparts.py"
s = open(p).read()
old = '''  # nothing below the square's bottom edge: that keeps clear of the steering wheel teeth's outer band
  outline = outline ^ CrossSection.square((200, 200)).translate((-100, -PLATE_HALF))'''
new = '''  # nothing below PLATE_BOTTOM: keeps clear of the steering wheel when the roller rests on it (wheel turned far)
  outline = outline ^ CrossSection.square((200, 200)).translate((-100, PLATE_BOTTOM))'''
assert old in s; s = s.replace(old, new)
s = s.replace('''GUARD_FRONT = (Z_GEAR_TEETH[1] - Z_MOTOR_FACE) + 2.0''', '''GUARD_FRONT = (Z_GEAR_TEETH[1] - Z_MOTOR_FACE) + 2.0
PLATE_BOTTOM = -20.0                  # plate's lower edge below the motor's axis''')
open(p, "w").write(s)
EOF
export PYTHONPATH=/home/claude/pylib:. && timeout 900 python3 -c "
import time, math
import numpy as np
import wheelparts as WP, mountparts as MP, assembly as AS, render as R
from gears import *
t = WP.Teeth()
print('r_roll', round(t.r_roll,3), 'r_root', t.r_root, 'r_base', t.r_base, 'half', round(t.half,2), 'roll_half', round(t.roll_half,2), 'chamfer', round(t.chamfer_deg,2))
t0=time.time()
s = WP.teeth_solid(t)
parts = dict(teeth=WP.teeth_one_piece(t, s), gear=WP.motor_gear(), bracket=MP.motor_bracket(), arm=MP.arm(), slider=MP.arm_slider(), clamp=MP.dash_clamp())
for k,m in parts.items(): print(k, m.status(), round(m.volume()/1000,2), 'genus', m.genus(), 'parts', len(m.decompose()))
for side in ('right','left'):
  h = WP.teeth_half(t, side, s); print(side, h.status(), round(h.volume()/1000,2), h.genus(), len(h.decompose()))
print('build', round(time.time()-t0,2))
f = AS.solve(t)
print('fit', f.ok, 'arm', round(f.arm_deg,2), 'slider', round(f.slider_pos,1), 'joint', round(f.joint_deg,2), f.notes)
A = AS.Assembly(t, f, parts)
T = A.teeth(); G = A.gear(); B = A.bracket(); M = A.motor(); W = A.wheel_grip()
for name, x, y in (('teeth x gear',T,G),('teeth x bracket',T,B),('teeth x motor',T,M),('grip x gear',W,G),('grip x bracket',W,B),('grip x motor',W,M),('arm x motor',A.arm(),M),('arm x bracket',A.arm(),B),('slider x bracket',A.slider(),B),('arm x clamp',A.arm(),A.clamp())):
  print(f'{name:18s} {AS.overlap(x,y):9.3f}')
# 2D mesh check with the real outlines at this centre distance
pitch = 360/197
ring = WP.teeth_outline(t)
motor = gear_outline(19, 0.175)
cd = WP.centre_distance()
w = np.linspace(-(t.teeth_half-2.5*pitch), t.teeth_half-2.5*pitch, 181)
print('2D mesh max overlap', max(mesh_sweep(ring, 197, motor, 19, cd, w, 270.0)), 'play', free_play(ring, motor, cd, 270.0, 19))
"
