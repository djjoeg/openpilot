python3 - <<'EOF'
p = 'photocomp.py'
s = open(p).read()
old = '''  fl = lights.get("flash")'''
new = '''  ws = lights.get("wheel_shade")
  if ws:
    # behind the steering wheel the hub and spokes keep most of the cabin's light off: less light the further in
    r = np.hypot(pts[:, 0], pts[:, 1])
    f = ws["k"] + (1 - ws["k"]) * np.clip((r - ws["r0"]) / (ws["r1"] - ws["r0"]), 0, 1)
    col *= np.where(pts[:, 2] < ws["z"], f, 1.0)[:, None]
  fl = lights.get("flash")'''
assert old in s
s = s.replace(old, new, 1)
open(p, 'w').write(s)

p = 'incar.py'
s = open(p).read()
old = '''  # daylight from in front, through the windscreen and the open garage door; the cabin's light round about
  fwd = np.array([0.0, math.sin(math.radians(22.0)), -math.cos(math.radians(22.0))])
  sun = 0.75 * fwd + 0.66 * np.asarray(up)
  return {"sun": dict(dir=sun, power=0.9, rgb=(1.0, 0.99, 0.97)),
          "sky": dict(up=up, sky=(0.55, 0.57, 0.60), ground=(0.22, 0.21, 0.20), power=1.0)}'''
new = '''  # daylight: the windscreen's light does not reach under the dash, so the parts get the cabin's light, from behind
  # and above (the side and back windows, the seats); behind the wheel's hub and spokes less of it
  fwd = np.array([0.0, math.sin(math.radians(22.0)), -math.cos(math.radians(22.0))])
  back = -fwd + 0.6 * np.asarray(up)
  return {"sky": dict(up=back / np.linalg.norm(back), sky=(0.60, 0.61, 0.63), ground=(0.10, 0.10, 0.10), power=1.0),
          "wheel_shade": dict(k=0.4, r0=150.0, r1=215.0, z=-12.0)}'''
assert old in s
s = s.replace(old, new)
open(p, 'w').write(s)
print('ok')
EOF
cd /home/claude/deliver/hardware/cad && (time PYTHONPATH=/home/claude/pylib timeout 2400 python3 incar.py 00) 2>&1 | tail -5