python3 - <<'EOF'
p = "render.py"
s = open(p).read()
old = '''def render(parts, rot: np.ndarray, size=(900, 700), margin=0.06, light=(0.35, 0.55, 0.75), background=(1, 1, 1)):'''
new = '''def look(direction_to_viewer, up) -> np.ndarray:
  """View matrix looking along -direction_to_viewer, with 'up' (projected) pointing up on screen."""
  d = np.asarray(direction_to_viewer, dtype=float)
  d /= np.linalg.norm(d)
  u = np.asarray(up, dtype=float)
  u = u - (u @ d) * d
  u /= np.linalg.norm(u)
  right = np.cross(u, d)
  return np.stack([right, u, d])


def render(parts, rot: np.ndarray, size=(900, 700), margin=0.06, light=(0.35, 0.55, 0.75), background=(1, 1, 1)):'''
assert old in s; s = s.replace(old, new)
open(p, "w").write(s)
EOF
export PYTHONPATH=/home/claude/pylib:. && timeout 900 python3 -c "
import numpy as np
import wheelparts as WP, mountparts as MP, assembly as AS, render as R
t = WP.Teeth()
f = AS.solve(t)
parts = dict(teeth=WP.teeth_one_piece(t), gear=WP.motor_gear(), bracket=MP.motor_bracket(), arm=MP.arm(), slider=MP.arm_slider(), clamp=MP.dash_clamp())
A = AS.Assembly(t, f, parts)
up, rear = AS.car_axes()
O=(0.9,0.55,0.2); Y=(0.95,0.8,0.25); G=(0.55,0.57,0.62); M=(0.25,0.25,0.28); BL=(0.3,0.55,0.85); GR=(0.2,0.2,0.2); HD=(0.75,0.75,0.7)
scene = [(A.teeth(),O),(A.gear(),Y),(A.bracket(),G),(A.motor(),M),(A.arm(),BL),(A.slider(),(0.35,0.7,0.45)),(A.clamp(),(0.8,0.3,0.3)),(A.hood(12),HD),(A.wheel_grip(),GR)]
out='/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/prev/'
side = R.look([1,0,0], up)
persp = R.look(np.array([1,0,0])*0.8 + up*0.5 + rear*0.6, up)
driver = R.look(rear + up*0.3, up)
R.save(out+'assembly.png', [(scene, side), (scene, persp), (scene, driver)], titles=['side (driver on the right)','from the driver\'s right','from the driver'], size=(800,650))
"
