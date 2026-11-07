"""Builds the pop-off mount and runs its checks; prints anything that touches."""
import sys
import time

sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np  # noqa: E402

import popassembly as PA  # noqa: E402
import popparts as PP  # noqa: E402

T0 = time.time()
quick = "--quick" in sys.argv
t = PP.PopTeeth()
teeth = PA.cached(f"pop_teeth_short_{t.rr:.1f}_{t.z_axis:.2f}_{t.mount_deg:.1f}", lambda: PP.pop_pieces(t)["one-piece"])
print("teeth", round(time.time() - T0, 1), "s, volume", round(teeth.volume()))
mb = PP.motor_and_board()
parts = {"teeth": teeth, "gear": PP.pop_motor_gear(), "gear_teeth_only": PP.pop_gear_teeth_only(), "carrier": PP.pop_carrier(),
         "motor": mb["body"] + mb["board"] + mb["plugs"], "block": PP.pop_hinge_block(), "plate": PP.pop_column_plate()}
A = PA.PopAssembly(t, parts)
print("parts", round(time.time() - T0, 1), "s")
print("springs:")
for r in PA.spring_rows():
  print("  ", r)
print("switch:", PA.switch_states())
if not quick:
  ms = PA.mesh_sweep(A)
  print("mesh:", ms, round(time.time() - T0, 1), "s")
res = PA.check_all(A, swing_step=5.0 if quick else 2.5, wheel_step=6.0 if quick else 3.0)
bad = {k: v for k, v in res.items() if (v > 1e-3 and "should touch" not in k) or ("should touch" in k and v > -1e-3)}
print(len(res), "checks,", len(bad), "failing", round(time.time() - T0, 1), "s")
for k, v in sorted(bad.items()):
  print(f"  {v:10.3f}  {k}")
