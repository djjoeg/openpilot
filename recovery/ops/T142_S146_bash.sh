python3 - <<'EOF'
import pathlib
p = pathlib.Path("popassembly.py")
s = p.read_text()
old = '''  fixed = [("hinge block", B), ("power switch", SW), ("column plate", PL), ("screw tabs", TB)]'''
assert s.count(old) == 1
s = s.replace(old, '''  fixed = [("hinge block", B), ("power switch", SW), ("column plate", PL), ("screw tabs", TB + A.tab_bolts())]''')
s += '''

def check_adjusted(A: PopAssembly, adj: float, swing_step: float = 5.0) -> dict:
  """The mount turned adj degrees round the column from where it was made for (the plate and its tabs stay put): the
  mount's parts against the plate, the tabs, the covers, the knee bolster and the adjustment tab, on and swinging off.
  (The wiper stalk and the key are what the turning is for, so they're left to you in the car.)"""
  res = {}
  keep = PP.MOUNT_DEG
  try:
    PP.MOUNT_DEG = keep + adj
    B, SW = A.block(), A.switch()
    PL, TB = A.plate() + A.pad(), A.tabs() + A.tab_bolts()
    others = [("column covers", A.covers()), ("knee bolster", A.bolster()), ("adjustment tab, its swing and your fingers", A.tilt_lever()),
              ("column plate", PL), ("screw tabs", TB)]
    res[f"turned {adj:+.0f}: hinge block/column plate"] = overlap(B, PL)
    res[f"turned {adj:+.0f}: hinge block/screw tabs"] = overlap(B, TB)
    res[f"turned {adj:+.0f}: power switch/column plate"] = overlap(SW, PL)
    for lift in list(np.arange(PP.LIFT_DROP, PP.LIFT_OFF + 1e-9, swing_step)) + [PP.LIFT_OFF]:
      movers = [("gear", A.gear(lift)), ("carrier", A.carrier(lift)), ("motor", A.motor(lift)), ("springs", A.springs(lift)),
                ("bolts", A.bolts(lift))]
      for mn, m in movers:
        for on, o in others:
          k = f"turned {adj:+.0f}, swinging: {mn}/{on} (worst)"
          res[k] = max(res.get(k, 0.0), overlap(m, o))
    for on, o in others[:3]:
      res[f"turned {adj:+.0f}: hinge block/{on}"] = overlap(B, o)
    fit = flange_fit(PP.MOUNT_DEG)
    res[f"turned {adj:+.0f}: the flange bolts outside their slots"] = 0.0 if fit["fits"] else 1.0
  finally:
    PP.MOUNT_DEG = keep
  return res
'''
p.write_text(s)
print("ok")
EOF
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2 && python3 - <<'EOF'
import pathlib
p = pathlib.Path("run_u.py")
s = p.read_text()
old = '''  res = PA.check_all(A, swing_step=5.0 if quick else 2.5, wheel_step=6.0 if quick else 3.0)'''
assert s.count(old) == 1
s = s.replace(old, '''  res = PA.check_all(A, swing_step=5.0 if quick else 2.5, wheel_step=6.0 if quick else 3.0)
  for adj in (-PP.MOUNT_ADJ, PP.MOUNT_ADJ):
    res.update(PA.check_adjusted(A, adj, swing_step=7.5 if quick else 5.0))''')
p.write_text(s)
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache timeout 3000 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop2/run_u.py --quick 2>&1 | grep -v "^   {\|flange fit\|switch:" | tail -30