cd /home/claude/deliver/hardware/cad && python3 - <<'EOF'
s = open('popparts.py').read()
s = s.replace("""HINGE_P = (45.0, -50.0)       # the hinge's axis, over the motor's board, along x""",
"""HINGE_P = (50.0, -50.0)       # the hinge's axis, over the motor's board, along x""")
# a deeper chamfer on the teeth's inner ends: the motor's front edge sweeps past them as it swings off
s = s.replace("""def pop_solid(t: PopTeeth) -> Manifold:
  body = revolve(t.profile(), -t.half, t.half, step_deg=0.25)
  n = t.n_teeth // 2
  body = body - FP.tooth_spaces(t, -n, n) - FP.teeth_trim(t) - FP.tip_chamfers(t, -t.half - 1.0, t.half + 1.0) - \\
    pop_ramps(t) - pop_spoke_notch(t) - FP.centre_mark(t)
  return clean(body)""", """INNER_CHAMFER = 3.0            # the teeth's tips cut back 45 degrees at their inner end this much (the motor's front edge
                               # passes there as it swings off)


def inner_chamfer(t: PopTeeth) -> Manifold:
  c = INNER_CHAMFER
  return revolve([(FP.FACE_BAND[0] + c + 0.5, t.z_tip - 0.5), (FP.FACE_BAND[0] - 0.5, t.z_tip - 0.5),
                  (FP.FACE_BAND[0] - 0.5, t.z_tip + c + 0.5)], -t.half - 1.0, t.half + 1.0)


def pop_solid(t: PopTeeth) -> Manifold:
  body = revolve(t.profile(), -t.half, t.half, step_deg=0.25)
  n = t.n_teeth // 2
  body = body - FP.tooth_spaces(t, -n, n) - FP.teeth_trim(t) - FP.tip_chamfers(t, -t.half - 1.0, t.half + 1.0) - \\
    inner_chamfer(t) - pop_ramps(t) - pop_spoke_notch(t) - FP.centre_mark(t)
  return clean(body)""")
open('popparts.py', 'w').write(s)
EOF
PYTHONPATH=/home/claude/pylib python3 -c "
import popparts as PP
print('C', PP.C_BOLT.round(2), 'B', PP.B_BOLT.round(2), 'mount C', PP.carrier_to_mount_pt((0,)+tuple(PP.C_BOLT)).round(1), 'mount B', PP.carrier_to_mount_pt((0,)+tuple(PP.B_BOLT)).round(1))
b = PP.pop_hinge_block(); print('block pieces', len(b.decompose()))
"; rm -f /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache/*; cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop && timeout 1800 env PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache python3 pop_run.py --quick 2>&1 | tail -16 && timeout 1800 env PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache python3 probe.py 2>&1 | tail -14