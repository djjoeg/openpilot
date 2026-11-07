cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/popmock && cp pop_export.py pop_export_v2.py && cp pop.src.html pop.src.v2.html && python3 - <<'EOF'
s = open('pop_export.py').read()
# imports
s = s.replace("import popparts as PP  # noqa: E402\n", "import popparts as PP  # noqa: E402\nimport carref as CR  # noqa: E402\n")
# covers start at the back cover's edge (the photos)
s = s.replace("T0 = time.time()\n", "T0 = time.time()\nP.COVER_FRONT_Z = CR.BACK_COVER_RIM_Z - 2.0     # the covers start where the wheel's back cover ends (photos)\n", 1)
# new stalk geometry
old_rest = s[s.index("def stalk_rest() -> Manifold:"):s.index("def flange_bolts() -> Manifold:")]
new_rest = '''def stalk_rest() -> Manifold:
  return CR.stalk()


def stalk_down() -> Manifold:
  """The wiper stalk pushed all the way down (3 notches, taken as 36 degrees): about a level axis across it at its root."""
  base = np.array(CR.WIPER_FROM, float)
  tip = np.array(CR.WIPER_TO, float)
  d = (tip - base) / np.linalg.norm(tip - base)
  ax = np.cross(d, [0.0, 1.0, 0.0])
  ax /= np.linalg.norm(ax)
  th = math.radians(-PA.STALK_DOWN_DEG)
  v = tip - base
  v_rot = v * math.cos(th) + np.cross(ax, v) * math.sin(th) + ax * np.dot(ax, v) * (1 - math.cos(th))
  return CA.rod(base, base + v_rot, CR.STALK_R)


'''
s = s.replace(old_rest, new_rest)
# meshes: replace the old key / stalks, add the bezel, key, turning room, back cover
old = '''  ("wiper_stalk", "car", "stalk", stalk_rest()),
  ("signal_stalk", "car", "stalk", CA.rod((-P.STALK_FROM[0], P.STALK_FROM[1], P.STALK_FROM[2]),
                                          (-P.STALK_TO[0], P.STALK_TO[1], P.STALK_TO[2]), P.STALK_R)),
  ("key", "car", "key", A.key()),
  ("tilt_lever", "lever", "lever", tilt_lever()),
  ("key_head", "car", "key", key_head()),
  ("stalk_down", "ghost", "ghost", stalk_down()),'''
new = '''  ("wiper_stalk", "car", "stalk", stalk_rest()),
  ("signal_stalk", "car", "stalk", CR.stalk(mirror=True)),
  ("key_bulge", "car", "cover", CR.key_bulge()),
  ("bezel_ring", "car", "rubber", BZ["ring"]),
  ("bezel_chrome", "car", "steel", BZ["chrome"]),
  ("keyhole", "car", "key", BZ["face"]),
  ("key_in", "car", "keyhead", CR.key_in()),
  ("key_room", "keyroom", "keyroom", CR.key_turn_room()),
  ("back_cover", "wheel", "hub", CR.back_cover()),
  ("tilt_lever", "lever", "lever", tilt_lever()),
  ("stalk_down", "ghost", "ghost", stalk_down()),'''
assert old in s
s = s.replace(old, new)
s = s.replace("coil = coil_mesh()\n", "coil = coil_mesh()\nBZ = CR.bezel()\n", 1)
# info: the reference rows and the key's place
old = '''  "springs": PA.spring_rows(),
}'''
new = '''  "springs": PA.spring_rows(),
  "reference": [list(r) for r in CR.REFERENCE_ROWS],
  "key": {"centre": [float(v) for v in CR.key_centre()], "head": [float(v) for v in (CR.key_centre() + 45.0 * CR._frame(CR.KEY_CLOCK_DEG, CR.KEY_TILT_DEG)[0])]},
  "stalk_mid": [float(v) for v in (np.array(CR.WIPER_FROM) + np.array(CR.WIPER_TO)) / 2.0],
}'''
assert old in s
s = s.replace(old, new)
open('pop_export.py', 'w').write(s)
print('ok')
EOF
grep -n "key_head\|A.key()" pop_export.py | head