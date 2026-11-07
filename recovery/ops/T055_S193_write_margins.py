"""
Margins: for each way this build can fail, the worst load it should ever see, what it can take, and the factor
between them (what it can take divided by the worst load). The aim is 1.5 and nothing may be under 1.4: NASA's
structures standard (NASA-STD-5001B) uses 1.4 on breaking strength for hardware whose strength is also proven by test,
and the FAA 1.5 for airliners (14 CFR 25.303). Where a number can only be estimated, a test on the car proves it, the
way NASA earns its 1.4: the grip test in the car setup and the proof pulls in the build guide.

For heat the factor applies to how far the sun heats a part above the outside air: the plastic's softening point
minus the outside air, divided by the part's temperature minus the outside air.

Each row says where its numbers come from: a data sheet, a calculation from this design, or an estimate.
"""
import math

import params as P
import gears as GR
import mountparts as MP

FLOOR, AIM = 1.4, 1.5

# ----- sources -----
# overpowering lane keeping: EU 2021/646 and Australia's ADR 107/00, "a steering effort of not more than 50 N will
# override the system"; UN R79 measures steering effort at the steering wheel's nominal radius, from its centre to
# the outer edge (para 2.4.7)
OVERRIDE_N = 50.0
MESH_EFF = 0.9          # printed spur gears, an estimate
DETENT_NCM = 2.5        # the motor's own cogging; not on its data sheet, an estimate for a motor this size
# rubbing between the teeth: greased plastic gears, and dry printed PETG (about 0.27 measured against steel in
# Tribology in Industry, 2024; PETG on PETG taken a little higher). Both estimates.
RUB_GREASED, RUB_DRY = 0.1, 0.3
# Bambu Lab PETG HF data sheet (V1.0): bending strength across the layers 48 MPa, tensile along them 34 MPa, glass
# transition (where it starts to soften) 66 C
PETG_BEND_Z, PETG_TENSILE_XY, PETG_SOFT_C = 48.0, 34.0, 66.0
ASA_SOFT_C = 95.0       # ASA's heat deflection temperature, typical data sheets (0.45 MPa)
# ASU / UC San Diego study of cars parked in Tempe, Arizona, outside air over 38 C (100 F), after one hour in the sun:
# cabin air 47 C, dashboard 69 C, steering wheel 53 C; in shade: dashboard 48 C. Silver cars.
HOT_DAY_C = 38.0
SUN_CABIN_C, SUN_DASH_C, SUN_WHEEL_C, SHADE_DASH_C = 47.0, 69.0, 53.0, 48.0
LIGHT_GREY_SHARE = 0.55  # a light grey part takes up about this share of the sunlight a dark dashboard does (estimate)
# electrical: TE V23234 mini relay (making current 120 A, 12 V coil 85 ohm); Omron SS-5 switch (inrush 10 A on its
# normally open contact; 14 V DC loads at least 2 A); the car's charging voltage at most 14.7 V; the motor board's input
# capacitor is rated 35 V (its design files)
RELAY_MAKE_A, RELAY_COIL_OHM, SWITCH_INRUSH_A, SWITCH_DC_A = 120.0, 85.0, 10.0, 2.0
CAR_MAX_V, BOARD_MAX_V = 14.7, 35.0
INRUSH_A = 70.0          # the board's capacitors charging through the wiring when power comes on: 50 to 70 A for a few
                         # hundredths of a millisecond (calculated from its capacitors and the wiring; not measured)
WIRE_20AWG_A = 7.5       # 20 AWG copper in a bundle, a common rating
MOTOR_FUSE_A, COMMA_FUSE_A = 5.0, 3.0
COMMA_MOST_A = 1.3       # the comma device's most draw at 12 V: an estimate, comma doesn't publish it
ZIP_TIE_N, TAPE_RUB = 50.0, 0.5   # a zip tie pulled tight by hand, and silicone tape's grip: estimates


def motor_k() -> float:
  """Nm per amp, the way the motor board's firmware counts it: holding torque over root 2 over rated current."""
  return P.MOTOR_HOLD_NCM / 100.0 / math.sqrt(2.0) / P.MOTOR_RATED_A


def ratio() -> float:
  return P.RING_TEETH / P.MOTOR_TEETH


def row(group, what, load, capacity, factor, basis, check="", kind="design", note=""):
  status = "OK" if factor >= AIM else ("meets the floor" if factor >= FLOOR else "UNDER")
  return {"group": group, "what": what, "load": load, "capacity": capacity, "factor": round(factor, 2), "status": status,
          "basis": basis, "check": check, "kind": kind, "note": note}


def table(spring: dict, mesh_from_hinge_mm: float, weight_hold_n: float) -> list[dict]:
  """spring: the parts report's spring numbers. mesh_from_hinge_mm: how far along the motor from the hinge the teeth
  meet. weight_hold_n: how much the motor's own weight adds to holding the teeth in mesh (least over the tilt range)."""
  rows = []
  r_out = P.WHEEL_OD / 2 / 1000.0
  override_nm = OVERRIDE_N * r_out
  k = motor_k()
  detent_nm = DETENT_NCM / 100.0 * ratio()
  motor_most_nm = P.BOARD_MAX_A * k * ratio()               # at the steering wheel, the motor pushing
  ring_r = GR.pitch_radius(P.RING_TEETH) / 1000.0
  gear_r = GR.pitch_radius(P.MOTOR_TEETH) / 1000.0
  phi = math.radians(GR.PRESSURE_ANGLE)

  # ----- the steering push -----
  g = "Steering push"
  load = P.MOST_TORQUE_NM / MESH_EFF + detent_nm
  rows.append(row(g, "You can overpower lane keeping", f"{load:.1f} Nm: the safety chip's most ({P.MOST_TORQUE_NM} Nm), "
                  "plus the gears' rubbing and the motor's cogging as you turn it back",
                  f"{override_nm:.1f} Nm: 50 N at the steering wheel's outer edge, the most lane keeping may take to "
                  "overpower under European and Australian rules", override_nm / load, "rule; calculated"))
  load = motor_most_nm / MESH_EFF + detent_nm
  rows.append(row(g, "You can overpower the motor even if its controller board fails at full power",
                  f"{load:.1f} Nm: the motor at the most current its board gives ({P.BOARD_MAX_A} A), turned back by hand",
                  f"{override_nm:.1f} Nm (as above)", override_nm / load, "motor data sheet; calculated",
                  note="the motor is the 45 Ncm one for this reason: the 59 Ncm one would make this 1.1"))

  hold_spring = spring["holds_teeth_in_mesh_up_to_N"]
  hold = hold_spring + weight_hold_n
  ft = P.LANE_KEEPING_MOST_NM / ring_r
  sep_greased = ft * math.tan(phi + math.atan(RUB_GREASED))
  sep_dry = ft * math.tan(phi + math.atan(RUB_DRY))
  rows.append(row(g, "The motor gear stays in the steering wheel teeth at the most push lane keeping uses, teeth greased",
                  f"{sep_greased:.1f} N pushing the teeth apart at {P.LANE_KEEPING_MOST_NM} Nm, with the rubbing of greased teeth",
                  f"{hold:.1f} N: the spring ({hold_spring:.1f}) and the motor's own weight ({weight_hold_n:.1f})",
                  hold / sep_greased, "calculated; rubbing estimated",
                  check="the grip test in the car setup pushes with the most the motor can (more than lane keeping uses) "
                        "while you hold the wheel: nothing may slip",
                  note=f"spring alone: {hold_spring / sep_greased:.2f}"))
  rows.append(row(g, "The same with dry teeth", f"{sep_dry:.1f} N", f"{hold:.1f} N", hold / sep_dry,
                  "calculated; rubbing estimated", kind="condition",
                  check="keep the teeth greased: the grip test catches dry teeth"))

  sp_up, sp_most = spring["force_lever_up_N"], spring["most_load_N"]
  free_long = MP.SPRING_FREE + MP.SPRING_FREE_TOL
  len_up = spring["length_lever_up_mm"]
  worst = (free_long - MP.SPRING_SOLID) / (free_long - len_up)
  rows.append(row(g, "The spring isn't squashed past what it can take (lever up)",
                  f"{sp_up:.1f} N at {len_up} mm long", f"{sp_most} N: fully squashed ({MP.SPRING_SOLID} mm), the most "
                  "Lee Spring sizes it for", sp_most / sp_up, "spring data sheet; calculated",
                  note=f"{worst:.2f} for the longest spring within Lee Spring's tolerance"))

  # Lewis bending at the motor gear's teeth (the smaller gear) at the most the motor can push
  ft_most = P.BOARD_MAX_A * k / gear_r
  face = min(P.Z_TEETH[1], P.Z_GEAR_TEETH[1]) - max(P.Z_TEETH[0], P.Z_GEAR_TEETH[0])
  lewis_y = 0.314               # Lewis form factor, 19 teeth, 20 degree full depth
  sigma = ft_most / (face * GR.MODULE * lewis_y)
  rows.append(row(g, "The printed teeth don't break", f"{sigma:.1f} MPa in the motor gear's teeth at the motor's most push",
                  f"{PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending strength across its layers, for repeated loads",
                  PETG_BEND_Z / 3 / sigma, "PETG data sheet; calculated (Lewis)"))

  # the shaft's flat pressing on the printed D-shaped bore: torque = p_max x length x (half the flat's width)^2 x 2/3
  half_flat = math.sqrt((P.SHAFT_D / 2) ** 2 - (P.SHAFT_ACROSS_FLAT - P.SHAFT_D / 2) ** 2)
  bore_len = min(P.SHAFT_LEN, P.Z_GEAR_TEETH[1] - P.Z_MOTOR_FACE) - (P.Z_GEAR_ROLLER[0] - P.Z_MOTOR_FACE)
  t_most = P.BOARD_MAX_A * k * 1000.0
  p_max = t_most * 3 / (2 * bore_len * half_flat ** 2)
  rows.append(row(g, "The motor gear doesn't turn on the motor's shaft", f"{p_max:.0f} MPa where the shaft's flat presses on "
                  "the gear at the motor's most push", f"{PETG_TENSILE_XY:.0f} MPa: PETG's tensile strength along its layers "
                  "(it takes more in compression)", PETG_TENSILE_XY / p_max, "PETG data sheet; calculated",
                  note="the set screw on the flat holds it too"))

  ties = 6
  grip_cap = ties * 2 * ZIP_TIE_N * TAPE_RUB
  rows.append(row(g, "The steering wheel teeth don't slide around the steering wheel",
                  f"{ft_most:.0f} N: the motor's most push at the teeth", f"{grip_cap:.0f} N: {ties} zip ties pulled tight "
                  "on silicone tape", grip_cap / ft_most, "estimated",
                  check="the grip test: if the teeth slide on the steering wheel, it fails"))

  # ----- the mount -----
  g = "Mount"
  sideways = ft_most
  rows.append(row(g, "The arm's joints and the dash clamp hold", f"up to {sideways:.0f} N sideways at the motor gear (its most "
                  "push), about 30 N up (the spring) and 16 N down (the parts' weight on a bump, 3 times gravity)",
                  "friction in bolted printed joints: can't be worked out reliably", float("nan"),
                  "proof test", kind="test",
                  check=f"proof pulls with a luggage scale at the motor, lever up: {math.ceil(1.5 * sideways / 9.81 * 2) / 2:.1f} kg "
                        "sideways each way and 5 kg up and down; nothing may move"))

  # ----- electrical -----
  g = "Electrical"
  coil_a = CAR_MAX_V / RELAY_COIL_OHM
  rows.append(row(g, "The lift lever switch", f"{coil_a:.2f} A: it only works the relay's coil", f"{SWITCH_DC_A:.0f} A: the "
                  "switch's rating for this kind of load at 14 V", SWITCH_DC_A / coil_a, "data sheets"))
  rows.append(row(g, "The relay, as power comes on", f"about {INRUSH_A:.0f} A for a moment: the motor board's capacitors "
                  "filling up", f"{RELAY_MAKE_A:.0f} A: the relay's making current", RELAY_MAKE_A / INRUSH_A,
                  "relay data sheet; inrush calculated",
                  note=f"without the relay the lever switch would see this: {SWITCH_INRUSH_A / INRUSH_A:.2f}"))
  board_a = (P.BOARD_MAX_A ** 2 * P.MOTOR_OHM + 1.0) / 12.0
  rows.append(row(g, "The motor's 5 A fuse doesn't blow in use", f"{board_a:.1f} A: the motor board at the most current it "
                  "gives", f"{MOTOR_FUSE_A:.0f} A", MOTOR_FUSE_A / board_a, "calculated"))
  rows.append(row(g, "The fuses protect the wires", f"{MOTOR_FUSE_A:.0f} A: the larger fuse", f"{WIRE_20AWG_A} A: 20 AWG wire",
                  WIRE_20AWG_A / MOTOR_FUSE_A, "wire rating"))
  rows.append(row(g, "The comma device's 3 A fuse doesn't blow in use", f"{COMMA_MOST_A} A: the comma device's most draw",
                  f"{COMMA_FUSE_A:.0f} A", COMMA_FUSE_A / COMMA_MOST_A, "estimated (comma doesn't publish it)"))
  rows.append(row(g, "The motor board's supply voltage", f"{CAR_MAX_V} V: the car's most while charging",
                  f"{BOARD_MAX_V:.0f} V: the board's input capacitor", BOARD_MAX_V / CAR_MAX_V, "design files",
                  note="a battery cable coming loose while the engine runs can briefly spike higher; that would harm "
                       "other add-ons too"))

  # ----- heat -----
  g = "Heat (light grey PETG)"

  def part_temp(surface_c: float) -> float:
    return SUN_CABIN_C + (surface_c - SUN_CABIN_C) * LIGHT_GREY_SHARE

  clamp_sun = max(part_temp(SUN_DASH_C), (part_temp(SUN_DASH_C) + SUN_DASH_C) / 2)   # half way to the hot cover it grips
  clamp_shade = SHADE_DASH_C + 3.0
  wheel_parts = part_temp(SUN_WHEEL_C) + 3.0
  rows.append(row(g, "Parts over the steering wheel, parked in summer sun", f"about {wheel_parts:.0f} C",
                  f"{PETG_SOFT_C:.0f} C: where PETG starts to soften", (PETG_SOFT_C - HOT_DAY_C) / (wheel_parts - HOT_DAY_C),
                  "estimated from a study of parked cars"))
  rows.append(row(g, "The dash clamp, parked in summer sun, windshield sunshade up", f"about {clamp_shade:.0f} C",
                  f"{PETG_SOFT_C:.0f} C", (PETG_SOFT_C - HOT_DAY_C) / (clamp_shade - HOT_DAY_C),
                  "estimated from a study of parked cars"))
  rows.append(row(g, "The dash clamp, parked in summer sun, no sunshade", f"about {clamp_sun:.0f} C", f"{PETG_SOFT_C:.0f} C",
                  (PETG_SOFT_C - HOT_DAY_C) / (clamp_sun - HOT_DAY_C), "estimated from a study of parked cars",
                  kind="condition", check="use a windshield sunshade when parked in sun, or have the dash clamp printed in ASA",
                  note=f"in ASA: {(ASA_SOFT_C - HOT_DAY_C) / (SUN_DASH_C - HOT_DAY_C):.2f} even at the dashboard's own temperature"))
  # the motor warming the carrier: lane keeping's most push held for a minute (a long tight curve)
  i_most = P.LANE_KEEPING_MOST_NM / (k * ratio())
  heat_j = i_most ** 2 * P.MOTOR_OHM * 60.0
  rise = heat_j / (P.MOTOR_KG * 1000 * 0.46)        # steel and copper, about 0.46 J per gram per degree
  rows.append(row(g, "The motor warming its carrier", f"{rise:.0f} C warmer after a minute at lane keeping's most push",
                  f"{PETG_SOFT_C - SUN_CABIN_C:.0f} C: from a hot cabin ({SUN_CABIN_C:.0f} C) to PETG's softening",
                  (PETG_SOFT_C - SUN_CABIN_C) / max(rise, 0.1), "calculated"))
  return rows


def weight_hold(mesh_from_hinge_mm: float, tilts) -> float:
  """How much the motor's and its board's weight presses the teeth into mesh, as a force at the teeth: the least over
  the steering column's tilt range. Only the motor and board are counted (the printed parts help a little more)."""
  hy, hz = MP.HINGE
  parts = [(P.MOTOR_KG, (0.0, -P.NEMA_LEN / 2)), (0.015, (0.0, -P.NEMA_LEN - 5.0))]
  least = math.inf
  for tilt in tilts:
    c, s = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    torque = 0.0
    for kg, (y, z) in parts:
      ry, rz = y - hy, z - hz
      fy, fz = -kg * 9.81 * c, -kg * 9.81 * s
      torque += ry * fz - rz * fy          # N mm about the hinge; positive presses the motor gear into the teeth
    least = min(least, torque / mesh_from_hinge_mm)
  return max(least, 0.0)


def text_lines(rows: list[dict]) -> list[str]:
  out = []
  group = None
  for r in rows:
    if r["group"] != group:
      group = r["group"]
      out.append(f"  {group}")
    f = "proof test" if math.isnan(r["factor"]) else f"{r['factor']:.2f} {r['status']}"
    out.append(f"    {r['what']}: {f}")
    out.append(f"      worst load: {r['load']}")
    out.append(f"      it takes:   {r['capacity']}")
    out.append(f"      from:       {r['basis']}")
    if r["note"]:
      out.append(f"      note:       {r['note']}")
    if r["check"]:
      out.append(f"      check:      {r['check']}")
  return out
