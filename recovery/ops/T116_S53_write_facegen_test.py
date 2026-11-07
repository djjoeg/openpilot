"""Experiment: generate the face (crown) teeth by sweeping the 16-tooth pinion, then check the real pinion meshes."""
import math
import sys
import time

sys.path.insert(0, "/home/claude/deliver/hardware/cad")
import numpy as np
from manifold3d import CrossSection, Manifold, OpType

import gears as GR
from cadlib import box, cyl, union

NF, NP = 166, 16
K = NF / NP
RF = GR.pitch_radius(NF)          # 166
RP = GR.pitch_radius(NP)          # 16
BACKLASH = 0.175
CD_EXTRA = 0.3
Z_ROOT = -22.5
Z_P = Z_ROOT - GR.DEDENDUM * GR.MODULE      # -25
Z_TIP = Z_P - GR.ADDENDUM * GR.MODULE       # -27
Z_AXIS = Z_P - RP - CD_EXTRA                # -41.3 (real pinion)
Z_AXIS_CUT = Z_P - RP                       # cutter: pitch circle on the pitch plane
BAND = (160.5, 171.5)
PITCH_DEG = 360.0 / NF


def to_wheel(m: Manifold, z_axis: float) -> Manifold:
  """A solid drawn with its axis along local +w (extruded), tooth 0 on +a, into the wheel frame: axis along x at
  (y=0, z=z_axis), local a -> +z, local b -> -y."""
  return m.transform([[0, 0, 1, 0], [0, -1, 0, 0], [1, 0, 0, z_axis]])


def gear_prism(outline: CrossSection, x0: float, x1: float, spin_deg: float, z_axis: float) -> Manifold:
  """The outline turned by spin_deg about its centre (counterclockwise in (a, b)), extruded over x0..x1, placed."""
  m = outline.rotate(spin_deg).extrude(x1 - x0).translate((0, 0, x0))
  return to_wheel(m, z_axis)


def tooth_space(theta_max: float = 5.5, step: float = 0.05, x0: float = 158.5, x1: float = 173.5) -> Manifold:
  cutter = GR.gear_outline(NP, -BACKLASH, addendum=GR.DEDENDUM, dedendum=GR.ADDENDUM)
  near = CrossSection.square((40, 40)).translate((RP - 4.0, -20))     # only the part near the face (a >= RP - 4)
  pieces = []
  for th in np.arange(-theta_max, theta_max + 1e-9, step):
    spin = -K * th      # see notes: rotation about +x by -K*theta; in the (a, b) plane that is ...
    cs = cutter.rotate(spin) ^ near
    m = cs.extrude(x1 - x0).translate((0, 0, x0))
    m = to_wheel(m, Z_AXIS_CUT).rotate((0, 0, -th))
    pieces.append(m)
  t = time.time()
  swept = Manifold.batch_boolean(pieces, OpType.Add)
  print("union", len(pieces), "in", round(time.time() - t, 2), "s; verts", swept.num_vert())
  # one space: the wedge |phi| <= pitch/2
  wedge_cs = CrossSection([[(0, 0)] + [(300 * math.cos(math.radians(a)), 300 * math.sin(math.radians(a)))
                                       for a in np.linspace(-PITCH_DEG / 2, PITCH_DEG / 2, 9)]])
  wedge = wedge_cs.extrude(40).translate((0, 0, -45))
  return swept ^ wedge


if __name__ == "__main__":
  sp = tooth_space()
  print("space volume", sp.volume(), "bbox", [round(v, 2) for v in sp.bounding_box()])
