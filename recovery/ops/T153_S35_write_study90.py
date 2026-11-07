"""Two drive layouts against the rebuilt car, for key depths D, engaged and slid off:
  radial - the motor's shaft pointing out from the column, the gear on it (as now)
  bevel  - a 90 degree bevel pair: the gear on its own short shaft, the motor lying along the column towards the dash
Carrier frame: origin on the gear's shaft axis at radius 153, +z_c out along that shaft, +y_c towards the dash, x_c across
(+x_c towards 6 o'clock at the 5 o'clock mount)."""
import math
import sys

sys.path.insert(0, "/home/claude/deliver/hardware/cad")
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/snap")
import numpy as np  # noqa: E402
from manifold3d import CrossSection, Manifold  # noqa: E402

import carscene as CS  # noqa: E402
import popassembly as PA  # noqa: E402
import popparts as PP  # noqa: E402
from cadlib import box, cyl, union  # noqa: E402
from core import core_carrier  # noqa: E402

H = 21.15                 # half the motor's square
PLUG = 12.0               # a plug and its cable's first bend stand this far out from the board's edge (estimate)


def board_cs() -> CrossSection:
  """The StepperServoCAN board with its side tabs broken off (KiCad outline), board-centred, KiCad x right, y down."""
  core = CrossSection.square((40.1, 40.8)).translate((-20.05, -20.4))
  tab = CrossSection.square((15.9, 2.6)).translate((-8.3, -22.94))
  return core + tab


def radial_parts(mount_deg: float):
  """Board turned so the car plug faces +x_c (6 o'clock side) and the motor plug faces +y_c (the dash)."""
  cs = board_cs().mirror((0, 1))            # KiCad y down -> carrier y_c = -y_k
  board = cs.extrude(14.0).translate((0, 0, -54.0))
  plug_car = box(20.05, 20.05 + PLUG, -13.3, 1.7, -52.0, -42.0)
  plug_mot = box(-8.7, 6.3, 22.94, 22.94 + PLUG, -52.0, -42.0)
  own_plug = box(H, H + PLUG, -8.0, 8.0, -38.0, -22.0)    # the motor's own 6-pin plug, on its 6 o'clock side
  motor = box(-H, H, -H, H, -40.0, 0.0) + cyl(11.0, 0.0, 2.0)
  return {"motor": motor, "board": board, "car plug": plug_car, "motor plug (to dash)": plug_mot,
          "motor's own plug": own_plug, "carrier": core_carrier(with_knuckle=False), "gear": PP.pop_motor_gear()}


def bevel_parts(a: float = 14.0, dp: float = 24.0):
  """The bevel pair's crossing point a below the old motor face on the gear's shaft; the motor along +y_c, its face
  dp/2 + 5 from the crossing point; board and plugs at its dash end (car plug out, motor plug to 6 o'clock)."""
  d = dp / 2 + 5.0
  zc = -a
  head = box(-17.0, 17.0, -dp / 2 - 4.0, d, zc - dp / 2 - 5.0, 5.0)
  motor = box(-H, H, d, d + 40.0, zc - H, zc + H)
  board = box(-20.05, 20.05, d + 40.0, d + 54.0, zc - 20.4, zc + 20.4)
  plug_out = box(-7.5, 7.5, d + 42.0, d + 52.0, zc + 20.4, zc + 20.4 + PLUG)
  plug_side = box(20.05, 20.05 + PLUG, d + 42.0, d + 52.0, zc - 7.5, zc + 7.5)
  own_plug = box(H, H + PLUG, d + 22.0, d + 38.0, zc - 8.0, zc + 8.0)
  plate = core_carrier(with_knuckle=False) ^ box(-60, 60, -60, 6.0, -1.0, 60)     # the plate and finger guard only
  return {"head": head, "motor": motor, "board": board, "car plug (out)": plug_out, "motor plug (6 o'clock)": plug_side,
          "motor's own plug": own_plug, "plate+guard": plate, "gear": PP.pop_motor_gear()}


def place(m: Manifold, mount_deg: float, slide=(0.0, 0.0, 0.0)) -> Manifold:
  keep = PP.MOUNT_DEG
  PP.MOUNT_DEG = mount_deg
  try:
    return PP.to_wheel(m.translate(slide))
  finally:
    PP.MOUNT_DEG = keep


def gap(a: Manifold, b: Manifold, far: float = 20.0) -> float:
  v = (a ^ b).volume()
  if v > 0.5:
    return -round(v)
  return round(a.min_gap(b, far), 1)


def fixed_car(mount_deg: float):
  keep = PP.MOUNT_DEG
  PP.MOUNT_DEG = mount_deg
  try:
    t = PP.PopTeeth(mount_deg=mount_deg)
    A = PA.PopAssembly(t, {})
    return {"spokes' sweep": A.spoke_zone(), "teeth (swept)": A.teeth_ring(), "fingers on the grip": A.fingers()}
  finally:
    PP.MOUNT_DEG = keep


def car_for(D: float):
  sc = CS.CarScene(D)
  out = {"column cover": sc.column_cover(), "back cover (swept)": sc.back_cover(), "dash face": sc.bolster(),
         "wiper stalk": sc.stalk()}
  out.update(sc.key_parts())
  return sc, out


if __name__ == "__main__":
  which = sys.argv[1] if len(sys.argv) > 1 else "radial"
  mount = float(sys.argv[2]) if len(sys.argv) > 2 else -63.0
  Ds = [float(v) for v in sys.argv[3].split(",")] if len(sys.argv) > 3 else [90.0, 97.0, 103.0, 106.0, 110.0, 115.0]
  alpha = float(sys.argv[4]) if len(sys.argv) > 4 else 45.0
  stroke = float(sys.argv[5]) if len(sys.argv) > 5 else 7.0
  a = float(sys.argv[6]) if len(sys.argv) > 6 else 14.0
  parts = radial_parts(mount) if which == "radial" else bevel_parts(a)
  sv = (0.0, stroke * math.cos(math.radians(alpha)), stroke * math.sin(math.radians(alpha)))
  fixed = fixed_car(mount)
  placed = {k: (place(v, mount), place(v, mount, sv)) for k, v in parts.items()}
  # the wheel-side checks don't depend on D
  rows = []
  for pn, (on, off) in placed.items():
    for cn, cm in fixed.items():
      g0, g1 = gap(on, cm), gap(off, cm)
      if min(g0, g1) < 8:
        rows.append(f"{pn}/{cn}: on {g0} off {g1}")
  print(f"{which} mount {mount:+.0f} slide {alpha:.0f} deg out x {stroke} mm" + (f" a {a}" if which != "radial" else ""))
  print("   wheel side: " + ("; ".join(rows) if rows else "all >= 8 mm"), flush=True)
  for D in Ds:
    sc, car = car_for(D)
    rows = []
    for pn, (on, off) in placed.items():
      for cn, cm in car.items():
        g0, g1 = gap(on, cm), gap(off, cm)
        if min(g0, g1) < 8:
          rows.append(f"{pn}/{cn}: on {g0} off {g1}")
    print(f"   D {D:.0f} (cover underside {sc.cover_bottom:.0f}, front {sc.cover_front_z:.0f}): " +
          ("; ".join(rows) if rows else "all >= 8 mm"), flush=True)
