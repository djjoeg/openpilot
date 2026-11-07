python3 - <<'EOF'
import pathlib
p = pathlib.Path("sideassembly.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)

rep("""def build_parts() -> dict:
  t = S.SideTeeth()
  name = f"side_teeth1_{t.rr:.1f}_{t.z_axis:.2f}_{t.spoke[0]:.1f}_{t.spoke[1]:.1f}_{S.ROOF_DEG:.0f}"
  teeth = PA.cached(name, lambda: S.side_teeth(t))
  mb = S.motor_board()
  return {"t": t, "teeth": teeth, "gear": S.side_gear(), "gear_teeth_only": S.side_gear_teeth_only(),
          "bracket": S.side_bracket(), "plate": S.side_plate(), "spool": S.side_spool(),
          "motor": union([mb["motor"], mb["board+cap"], mb["car plug"], mb["motor plug"], mb["motor's own plug"]]),
          "rail": S.rail(), "block": S.block(), "block screws": S.block_screws(), "lever": S.side_lever(),
          "lever's pin": S.lever_pin()}


class SideAssembly:
  def __init__(self, parts: dict | None = None, mount_deg: float = S.MOUNT_DEG):
    self.p = parts if parts is not None else build_parts()
    self.t = self.p["t"]
    self.mount = mount_deg
""", """def teeth_set(n_teeth: int) -> dict:
  t = S.SideTeeth(n_teeth=n_teeth)
  name = f"side_teeth2_{n_teeth}_{t.rr:.1f}_{t.z_axis:.2f}_{t.spoke[0]:.1f}_{t.spoke[1]:.1f}_{S.ROOF_DEG:.0f}"
  return {"t": t, "teeth": PA.cached(name, lambda: S.side_teeth(t))}


def build_parts(sets=tuple(S.TEETH_SETS)) -> dict:
  \"\"\"The mount's parts (carrier frame) and the teeth sets; "t" and "teeth" are the 14-tooth set's.\"\"\"
  mb = S.motor_board()
  out = {"gear": S.side_gear(), "gear_teeth_only": S.side_gear_teeth_only(),
         "bracket": S.side_bracket(), "plate": S.side_plate(), "spool": S.side_spool(),
         "motor": union([mb["motor"], mb["board+cap"], mb["car plug"], mb["motor plug"], mb["motor's own plug"]]),
         "rail": S.rail(), "block": S.block(), "block screws": S.block_screws(), "lever": S.side_lever(),
         "lever's screw": S.lever_screw(), "foot bar": S.foot_bar(), "foot shim": S.foot_shim(),
         "sets": {n: teeth_set(n) for n in sets}}
  main = FP.N_TEETH_SHORT if FP.N_TEETH_SHORT in out["sets"] else next(iter(out["sets"]))
  out["t"], out["teeth"] = out["sets"][main]["t"], out["sets"][main]["teeth"]
  return out


class SideAssembly:
  def __init__(self, parts: dict | None = None, mount_deg: float = S.MOUNT_DEG, n_teeth: int | None = None):
    self.p = parts if parts is not None else build_parts()
    if n_teeth is not None:
      self.p = dict(self.p, t=self.p["sets"][n_teeth]["t"], teeth=self.p["sets"][n_teeth]["teeth"])
    self.t = self.p["t"]
    self.mount = mount_deg
""")
rep("""            "spring's clamp": sp["clamp"], "lever": S.lever_at(self.p["lever"], s, lever_deg),
            "lever's pin": S.slid(self.p["lever's pin"], s)}""",
    """            "spring's clamp": sp["clamp"], "lever": S.lever_at(self.p["lever"], s, lever_deg),
            "lever's screw": S.slid(self.p["lever's screw"], s)}""")
rep("""    return {"mounting plate": self.p["plate"], "rail": self.p["rail"], "switch": sw["body"],
            "switch's lever and roller": sw["lever"], "spring's coil and spool": sp["coil"] + self.p["spool"].translate((S.SPOOL_X, 0.0, S.SPOOL_Z)),
            "spool's screw": sp["axle"]}""",
    """    return {"mounting plate": self.p["plate"], "rail": self.p["rail"], "switch": sw["body"],
            "switch's lever and roller": sw["lever"], "spring's coil and spool": sp["coil"] + self.p["spool"].translate((S.SPOOL_X, 0.0, S.SPOOL_Z)),
            "spool's screw": sp["axle"], "foot bar (anywhere along the window)": S.foot_bar_sweep()}""")
rep("""EXPECTED = {("block", "rail"), ("motor bracket", "switch's lever and roller"), ("block screws", "motor bracket")}""",
    """EXPECTED = {("block", "rail"), ("motor bracket", "switch's lever and roller"), ("block screws", "motor bracket")}
FOOT_PARTS = ("mounting plate", "foot bar (anywhere along the window)")""")
p.write_text(s)
print("ok")
EOF
grep -n "lever's pin\|pin\b" sideassembly.py sidebuild.py | head