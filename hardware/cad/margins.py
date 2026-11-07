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

import numpy as np

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
# rubbing between the teeth, dry (the build uses no grease): printed PETG measured about 0.27 against steel in
# Tribology in Industry, 2024 (static, from its friction forces at 30 and 70 N); PETG on PETG is taken a little higher.
# An estimate: the car setup's grip test proves the real teeth.
RUB_DRY = 0.3
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
MOTOR_FUSE_A = 5.0       # the fuse in the 12 V socket plug that feeds the relay and the motor
SOCKET_A = 10.0          # the car's accessory power sockets: 120 W (10 A) each, 2008-12 Accord owner's manual
DEVICE_A = 1.5           # the comma device at 12 V, stand-alone fed through the socket plug too: an estimate on the high
                         # side (comma doesn't publish its draw)
ZIP_TIE_N, TAPE_RUB = 50.0, 0.5   # a zip tie pulled tight by hand, and silicone tape's grip: estimates
MOUNTED_KG = 0.55       # the motor, its board and the printed parts on the arm
BUMP_G = 3.0            # a hard bump, in times gravity (an estimate)


def motor_k() -> float:
  """Nm per amp, the way the motor board's firmware counts it: holding torque over root 2 over rated current."""
  return P.MOTOR_HOLD_NCM / 100.0 / math.sqrt(2.0) / P.MOTOR_RATED_A


def ratio() -> float:
  return P.RING_TEETH / P.MOTOR_TEETH


def row(group, what, load, capacity, factor, basis, check="", kind="design", note=""):
  """kind: "design" counts towards the floor; "condition" is the same failure without one of the build's measures (it
  says which); "test" can only be proven by a test on the car."""
  if math.isnan(factor):
    status, factor = "proof test", None
  else:
    status = "OK" if factor >= AIM else ("meets the floor" if factor >= FLOOR else "UNDER")
    factor = round(factor, 2)
  return {"group": group, "what": what, "load": load, "capacity": capacity, "factor": factor, "status": status,
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
  sep_dry = ft * math.tan(phi + math.atan(RUB_DRY))
  # the weakest spring Lee Spring may ship: the shortest free length within its tolerance
  hold_short = MP.SPRING_RATE * (MP.SPRING_FREE - MP.SPRING_FREE_TOL - MP.SPRING_LEN) * MP.SPRING_ARM / mesh_from_hinge_mm
  grip_x = motor_most_nm / P.LANE_KEEPING_MOST_NM
  rows.append(row(g, "The motor gear stays in the steering wheel teeth at the most push lane keeping uses, teeth dry",
                  f"{sep_dry:.1f} N pushing the teeth apart at {P.LANE_KEEPING_MOST_NM} Nm, with dry teeth rubbing",
                  f"{hold:.1f} N: the spring ({hold_spring:.1f}) and the motor's own weight ({weight_hold_n:.1f})",
                  hold / sep_dry, "calculated; rubbing estimated",
                  check=f"the grip test in the car setup pushes with the most the motor can ({motor_most_nm:.2f} Nm, "
                        f"{grip_x:.2f} times the most lane keeping uses) while you hold the wheel: nothing may slip",
                  note=f"{(hold_short + weight_hold_n) / sep_dry:.2f} with the shortest spring within Lee Spring's tolerance"))

  sp_up, sp_most = spring["force_lever_up_N"], spring["most_load_N"]
  free_long = MP.SPRING_FREE + MP.SPRING_FREE_TOL
  len_up = spring["length_lever_up_mm"]
  worst = sp_most / (MP.SPRING_RATE * (free_long - len_up))
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
  up = spring["presses_roller_on_rolling_band_N"] + ft_most * math.tan(phi + math.atan(RUB_DRY))
  down = MOUNTED_KG * 9.81 * BUMP_G

  def kg(n):
    return math.ceil(1.5 * n / 9.81 * 2) / 2

  rows.append(row(g, "The arm's joints and the dash clamp hold", f"up to {sideways:.0f} N sideways at the motor gear (its most "
                  f"push), {up:.0f} N up (the spring and the teeth pushing apart) and {down:.0f} N down (the parts' weight "
                  f"on a bump, {BUMP_G:g} times gravity)", "friction in bolted printed joints: can't be worked out reliably",
                  float("nan"), "proof test", kind="test",
                  check=f"proof pulls with a luggage scale at the motor, lever up: {kg(sideways):.1f} kg sideways each way, "
                        f"{kg(up):.1f} kg up and {kg(down):.1f} kg down (1.5 times each load); nothing may move"))

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
  total_a = board_a + DEVICE_A      # stand-alone (the default): the socket plug feeds the comma device too
  rows.append(row(g, "The socket plug's 5 A fuse doesn't blow in use", f"{total_a:.1f} A: the motor board at the most current "
                  f"it gives ({board_a:.1f} A) and the comma device ({DEVICE_A:.1f} A, an estimate on the high side)",
                  f"{MOTOR_FUSE_A:.0f} A", MOTOR_FUSE_A / total_a, "calculated; the comma device's draw estimated",
                  note="connected to the car (car_network) the comma device is fed from the OBD port instead: "
                       f"{MOTOR_FUSE_A / board_a:.2f}"))
  rows.append(row(g, "The fuse protects the wires", f"{MOTOR_FUSE_A:.0f} A: the socket plug's fuse", f"{WIRE_20AWG_A} A: 20 AWG "
                  "wire, the thinnest in the build", WIRE_20AWG_A / MOTOR_FUSE_A, "wire rating"))
  rows.append(row(g, "The car's accessory power socket carries the motor and the comma device", f"{total_a:.1f} A (as above)",
                  f"{SOCKET_A:.0f} A: the socket's rating in the owner's manual", SOCKET_A / total_a, "owner's manual; calculated"))
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


# ----- the column mount -----
CLAMP_SQUEEZE_N = 300.0     # the four threaded rods tightened to "snug, then a quarter turn": about this much between the
                            # saddles (an estimate)
RUBBER_RUB = 0.4            # rubber strip on the textured covers: an estimate on the low side
SKIRT_SPREAD_MM = 60.0      # the push on the ring's skirt spreads over about this width of it (estimate on the low side)


def column_rows(t) -> list[dict]:
  """The column mount's own ways of failing (its shared parts are covered by table()). t: columnparts.RingTeeth."""
  import columnparts as CP
  rows = []
  k = motor_k()
  gear_r = GR.pitch_radius(P.MOTOR_TEETH) / 1000.0
  ft_most = P.BOARD_MAX_A * k / gear_r                       # the motor's most push at the teeth, N
  phi = math.radians(GR.PRESSURE_ANGLE)
  g = "Column mount"
  # turning the clamp round the covers: the push at the ring is a torque about the column's axis
  torque_nm = ft_most * GR.pitch_radius(P.RING_TEETH) / 1000.0
  v = math.radians(CP.V_DEG)
  normal_total = 2 * CLAMP_SQUEEZE_N / math.cos(v)         # both saddles, each V face taking half the squeeze over cos(V)
  r_contact = 0.045                                         # the rubber strips meet the covers about this far from the column's axis
  friction_nm = RUBBER_RUB * normal_total * r_contact
  rows.append(row(g, "The column clamp doesn't turn round the steering column covers under the motor's push",
                  f"{torque_nm:.1f} Nm about the column: the motor's most push ({ft_most:.0f} N) at the ring",
                  f"about {friction_nm:.0f} Nm: rubber strips (rubbing {RUBBER_RUB}) on four V faces with the rods snug "
                  f"({CLAMP_SQUEEZE_N:.0f} N between the saddles)", friction_nm / torque_nm, "estimated",
                  check="proof pull: with the lift lever up, pull the motor sideways with a luggage scale to 5 kg (1.8 times the "
                        "motor's most push), each way: the clamp must not move on the covers. On an oval cover the V's shape helps too",
                  note="the covers themselves: plastic shells of unknown stiffness; the push test in the guide is the only check"))
  # the skirt that carries the ring: the spring's press and the teeth's separating push bend it outwards at its far end
  push_n = MP.spring_torque(0) / 50.0 + ft_most * math.tan(phi + math.atan(RUB_DRY))   # roller press (29 N) and separating push
  length = (-CP.RING_BACK_Z + (t.base.wz_out - P.FRONT_RING_T)) - 5.0   # from the front ring's back face to near the roller's middle
  sigma = 6 * push_n * length / (SKIRT_SPREAD_MM * P.SKIRT_T ** 2)
  rows.append(row(g, "The ring's skirt carries the spring's press and the teeth's push",
                  f"{sigma:.1f} MPa at the skirt's root: {push_n:.0f} N at the end of the {P.SKIRT_T:.0f} mm skirt, {length:.0f} mm "
                  f"from the front ring, taken over {SKIRT_SPREAD_MM:.0f} mm of its width",
                  f"{PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending strength across its layers, for repeated loads",
                  PETG_BEND_Z / 3 / sigma, "PETG data sheet; calculated as a flat strip (the curved skirt is stiffer)"))
  # heat: the clamp sits in cabin air, not on the dashboard
  clamp_c = SUN_CABIN_C + 3.0
  rows.append(row("Heat (light grey PETG)", "The column clamp, parked in summer sun", f"about {clamp_c:.0f} C: cabin air, under the dash",
                  f"{PETG_SOFT_C:.0f} C: where PETG starts to soften", (PETG_SOFT_C - HOT_DAY_C) / (clamp_c - HOT_DAY_C),
                  "estimated from a study of parked cars", note="no sunshade needed for this clamp"))
  return rows


TIE_PULL_N = 100.0          # a zip tie pulled tight by hand: about this much tension (estimate on the low side)
SCREW_HOLD_N = 200.0        # a #8 self-tapping screw 8 mm into dash plastic, sideways: estimate on the low side


def side_rows(t, fit, cover_w: float = P.COVER_W) -> list[dict]:
  """The right-side mount's own ways of failing. fit: columnassembly.SideFit; cover_w: the covers' width at the bracket."""
  import columnparts as CP
  rows = []
  k = motor_k()
  gear_r = GR.pitch_radius(P.MOTOR_TEETH) / 1000.0
  ft_most = P.BOARD_MAX_A * k / gear_r                       # the motor's most push at the teeth, N
  g = "Right-side mount"
  torque_nm = ft_most * GR.pitch_radius(P.RING_TEETH) / 1000.0
  # the push at the ring turns the bracket about the column; the screw tab holds it at the dash's screw
  r_screw = math.hypot(float(fit.screw_w[0]), float(fit.screw_w[1])) / 1000.0
  f_screw = torque_nm / r_screw
  rows.append(row(g, "The dash's screw holds the screw tab under the motor's push",
                  f"{f_screw:.0f} N sideways at the screw: the motor's most push ({ft_most:.0f} N) at the ring, {torque_nm:.1f} Nm "
                  f"about the column, held {r_screw * 1000:.0f} mm from it",
                  f"about {SCREW_HOLD_N:.0f} N: a self-tapping screw in dash plastic, estimated on the low side",
                  SCREW_HOLD_N / f_screw, "estimated",
                  check="proof pull: with the lift lever up, pull the motor sideways with a luggage scale to 5 kg each way: the "
                        "screw tab must not move at the screw and the bracket must not move on the covers"))
  # the tab bends about its last bolt
  arm_mm = max(float(fit.screw_w[0]) - (cover_w / 2.0 + CP.SB_BAR_HOLES[1]), 20.0)   # the screw past the tab's last bolt
  w_mm3 = (CP.TAB_BAR_Z[1] - CP.TAB_BAR_Z[0]) * (CP.TAB_BAR_Y[1] - CP.TAB_BAR_Y[0]) ** 2 / 6.0
  sigma = f_screw * arm_mm / w_mm3
  rows.append(row(g, "The screw tab carries that push to the screw",
                  f"{sigma:.2f} MPa in the tab's bar: {f_screw:.0f} N, {arm_mm:.0f} mm past its last bolt",
                  f"{PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending strength across its layers, for repeated loads",
                  PETG_BEND_Z / 3 / sigma, "PETG data sheet"))
  # the bracket sliding on the covers: the push at the ring also pulls the bracket along the covers' side
  friction = RUBBER_RUB * 3 * TIE_PULL_N
  rows.append(row(g, "The side bracket doesn't slide on the covers under the motor's push",
                  f"{ft_most:.0f} N along the covers' side: the motor's most push at the ring, through the arm",
                  f"about {friction:.0f} N: two rubber strips (rubbing {RUBBER_RUB}) under three zip ties pulled to about "
                  f"{TIE_PULL_N:.0f} N each; the screw tab holds as well", friction / ft_most, "estimated",
                  check="the same proof pull"))
  clamp_c = SUN_CABIN_C + 3.0
  rows.append(row("Heat (light grey PETG)", "The side bracket and screw tab, parked in summer sun",
                  f"about {clamp_c:.0f} C: cabin air, under the dash", f"{PETG_SOFT_C:.0f} C: where PETG starts to soften",
                  (PETG_SOFT_C - HOT_DAY_C) / (clamp_c - HOT_DAY_C), "estimated from a study of parked cars",
                  note="no sunshade needed for these"))
  return rows


PLATE_SCREW_HOLD_N = 250.0  # one of the lower column cover's screws (4 mm tapping into its boss, or the 5 mm screw into the
                            # column's bracket) pulling out or tearing through the plate's slot: an estimate on the low side

# where the lower cover's screws may fall in the column plate's two slots (slot, mm behind the plate's front end); the first
# is the one the photos suggest: the cover's screws on its right-hand side, one towards the wheel and one further back
PLATE_SCREW_LAYOUTS = {
  "in the outer slot, 80 mm apart": ((1, 40.0), (1, 120.0)),
  "one in each slot, 40 mm apart": ((0, 29.0), (1, 69.0)),
  "both in the outer slot, 40 mm apart": ((1, 29.0), (1, 69.0)),
  "both in the inner slot (nearer the middle)": ((0, 40.0), (0, 120.0)),
}


def plate_screw_pull(t, push_n: float, dash_n: float, spring_dash_n: float, weight_n: float, screws) -> float:
  """The most pull on one of the column plate's screws (N). The plate sits under the cover on two rubber strips; a load
  that tips it about an edge of the strips (along or across the column) is held by the screws, each pulling in
  proportion to its distance from that edge; the tipping about both kinds of edge is added. Loads: the push at the teeth
  up or down with the teeth pushing the gear towards the dash, and the parts' weight on a bump with the spring's push."""
  import faceparts as FP
  y_top = FP.plate_top_y()
  front = P.PLATE_FRONT_Z
  x0, x1 = FP.PL_X
  at_teeth = np.array([FP.R_F, 0.0, t.z_p])
  at_motor = np.array([FP.R_FACE + 20.0, 0.0, t.z_axis])
  cases = [[(at_teeth, np.array([0.0, push_n, -dash_n]))], [(at_teeth, np.array([0.0, -push_n, -dash_n]))],
           [(at_motor, np.array([0.0, -weight_n, 0.0])), (at_teeth, np.array([0.0, 0.0, -spring_dash_n]))]]
  middle = np.array([(x0 + x1) / 2, y_top, front - FP.PL_LEN / 2])
  edges = [(np.array([x0 + 1.0, y_top, 0.0]), np.array([0.0, 0.0, 1.0])), (np.array([x1 - 1.0, y_top, 0.0]), np.array([0.0, 0.0, 1.0])),
           (np.array([0.0, y_top, front - 2.0]), np.array([1.0, 0.0, 0.0])),
           (np.array([0.0, y_top, front - FP.PL_LEN + 2.0]), np.array([1.0, 0.0, 0.0]))]
  pts = [np.array([FP.PL_SLOTS_X[k], y_top, front - dz]) for k, dz in screws]
  worst = 0.0
  for loads in cases:
    pull = np.zeros(len(pts))
    for a, u in edges:
      if np.dot(np.cross(u, middle - a), np.array([0.0, -1.0, 0.0])) < 0:
        u = -u                                  # turning this way takes the plate's middle away from the cover
      m = sum(float(np.dot(np.cross(p - a, f), u)) for p, f in loads)
      if m <= 0:
        continue
      d = np.array([np.linalg.norm(np.cross(u, q - a)) for q in pts])
      pull += m * d / float(np.sum(d ** 2))
    worst = max(worst, float(pull.max()))
  return worst



def back_rows(t, fit, shim_mm: float = 1.0) -> list[dict]:
  """The back-teeth mount's own ways of failing. t: faceparts.FaceTeeth; fit: faceassembly.FaceFit. shim_mm: the M5
  washer under the spring, standard on this mount."""
  import faceparts as FP
  rows = []
  k = motor_k()
  gear_r = FP.R_P / 1000.0
  face_r = FP.R_F / 1000.0
  ft_most = P.BOARD_MAX_A * k / gear_r                      # the motor's most push at the teeth, N
  phi = math.radians(GR.PRESSURE_ANGLE)
  g = "Back-teeth mount"
  # the spring holds the gear in the teeth: its turning force about the hinge, taken at the teeth's middle along the
  # shaft (the motor's weight doesn't help here: the hinge's axis is upright)
  mesh_from_hinge = (FP.FG_TEETH[0] + FP.FG_TEETH[1]) / 2 - MP.HINGE[1]
  force = MP.spring_force(0) + MP.SPRING_RATE * shim_mm
  hold = force * MP.SPRING_ARM / mesh_from_hinge
  ft = P.LANE_KEEPING_MOST_NM / face_r
  sep_dry = ft * math.tan(phi + math.atan(RUB_DRY))
  short = (MP.SPRING_RATE * (MP.SPRING_FREE - MP.SPRING_FREE_TOL - MP.SPRING_LEN + shim_mm)) * MP.SPRING_ARM / mesh_from_hinge
  motor_most_nm = P.BOARD_MAX_A * k * FP.FACE_RATIO
  rows.append(row(g, "The motor gear stays in the back teeth at the most push lane keeping uses, teeth dry",
                  f"{sep_dry:.1f} N pushing the teeth apart at {P.LANE_KEEPING_MOST_NM} Nm, with dry teeth rubbing (the teeth "
                  f"sit at {FP.R_F:.0f} mm, so they push apart harder than the other mounts' at {GR.pitch_radius(P.RING_TEETH):.0f})",
                  f"{hold:.1f} N: the spring with the M5 washer under it ({force:.1f} N)", hold / sep_dry,
                  "calculated; rubbing estimated",
                  check=f"the grip test in the car setup pushes with the most the motor can ({motor_most_nm:.2f} Nm) while you hold "
                        "the wheel: nothing may slip",
                  note=f"{short / sep_dry:.2f} with the shortest spring within Lee Spring's tolerance; "
                       f"{(MP.spring_force(0) * MP.SPRING_ARM / mesh_from_hinge) / sep_dry:.2f} without the washer"))
  up_n = MP.spring_force(MP.LIFT_DEG + 1.0) + MP.SPRING_RATE * shim_mm
  rows.append(row(g, "The spring with its washer isn't squashed past what it can take (lever up)",
                  f"about {up_n:.1f} N", f"{MP.SPRING_MAX_N} N: fully squashed, the most Lee Spring sizes it for",
                  MP.SPRING_MAX_N / up_n, "spring data sheet; calculated"))
  # Lewis bending at the 16-tooth motor gear's teeth at the motor's most push
  face = FP.FACE_BAND[1] - FP.FACE_BAND[0] - 2 * 1.5 * 0.5     # the tips' end chamfers take a little off
  lewis_y = 0.296               # Lewis form factor, 16 teeth, 20 degree full depth
  sigma = ft_most / (face * GR.MODULE * lewis_y)
  rows.append(row(g, "The 16-tooth motor gear's teeth don't break", f"{sigma:.1f} MPa at the motor's most push ({ft_most:.0f} N)",
                  f"{PETG_BEND_Z / 3:.0f} MPa: a third of PETG's bending strength across its layers, for repeated loads",
                  PETG_BEND_Z / 3 / sigma, "PETG data sheet; calculated (Lewis)"))
  half_flat = math.sqrt((P.SHAFT_D / 2) ** 2 - (P.SHAFT_ACROSS_FLAT - P.SHAFT_D / 2) ** 2)
  bore_len = min(P.SHAFT_LEN, FP.FG_TEETH[1]) - FP.FG_ROLLER[0]
  p_max = P.BOARD_MAX_A * k * 1000.0 * 3 / (2 * bore_len * half_flat ** 2)
  rows.append(row(g, "The motor gear doesn't turn on the motor's shaft", f"{p_max:.0f} MPa where the shaft's flat presses on the "
                  "gear at the motor's most push", f"{PETG_TENSILE_XY:.0f} MPa: PETG's tensile strength along its layers",
                  PETG_TENSILE_XY / p_max, "PETG data sheet; calculated", note="the set screw on the flat holds it too"))
  ties = 6
  grip_cap = ties * 2 * ZIP_TIE_N * TAPE_RUB
  rows.append(row(g, "The back teeth don't slide round the grip", f"{ft_most:.0f} N: the motor's most push at the teeth",
                  f"{grip_cap:.0f} N: {ties} zip ties pulled tight on silicone tape; the notch round the right spoke's junction "
                  "also stops it", grip_cap / ft_most, "estimated", check="the grip test: if the teeth slide on the grip, it fails"))
  # the column plate on the cover's screws: the loads at the teeth try to tip the plate off the cover about an edge of its
  # rubber strips; the screws in its slots hold it, each in proportion to its distance from that edge
  spring_dash = force * MP.SPRING_ARM / ((FP.FG_ROLLER[0] + FP.FG_ROLLER[1]) / 2 - MP.HINGE[1])
  up = spring_dash + ft_most * math.tan(phi + math.atan(RUB_DRY))
  down = MOUNTED_KG * 9.81 * BUMP_G
  layouts = {name: plate_screw_pull(t, ft_most, up, spring_dash, down, scr) for name, scr in PLATE_SCREW_LAYOUTS.items()}
  expected = next(iter(PLATE_SCREW_LAYOUTS))
  pull = layouts[expected]
  others = "; ".join(f"{name}: {PLATE_SCREW_HOLD_N / v:.2f}" for name, v in list(layouts.items())[1:])
  rows.append(row(g, "The column plate holds on the cover's screws", f"about {pull:.0f} N pulling on the busier screw: the "
                  f"motor's most push ({ft_most:.0f} N, up or down) and {up:.0f} N towards the dash at the teeth, tipping the plate "
                  f"about an edge of its rubber strips; two screws {expected}",
                  f"about {PLATE_SCREW_HOLD_N:.0f} N each: the cover's screws, estimated on the low side", PLATE_SCREW_HOLD_N / pull,
                  "estimated; where the screws are is a guess from the photos",
                  check="proof pulls with a luggage scale at the motor, lever up (see the guide): nothing may move",
                  note=f"other places the screws may fall: {others}. The lower cover is a plastic shell of unknown stiffness"))
  sideways = ft_most

  def kg(n):
    return math.ceil(1.5 * n / 9.81 * 2) / 2

  rows.append(row(g, "The arm's joints and the column plate hold", f"up to {sideways:.0f} N up or down at the motor gear (its most "
                  f"push), {up:.0f} N towards the dash (the spring and the teeth pushing apart) and {down:.0f} N down (the parts' "
                  f"weight on a bump, {BUMP_G:g} times gravity)", "friction in bolted printed joints: can't be worked out reliably",
                  float("nan"), "proof test", kind="test",
                  check=f"proof pulls with a luggage scale at the motor, lever up: {kg(sideways):.1f} kg up and down, {kg(up):.1f} kg "
                        f"towards the dash and {kg(down):.1f} kg down (1.5 times each load); nothing may move"))
  plate_c = SUN_CABIN_C + 3.0
  rows.append(row("Heat (light grey PETG)", "The column plate, parked in summer sun", f"about {plate_c:.0f} C: cabin air, under the column",
                  f"{PETG_SOFT_C:.0f} C: where PETG starts to soften", (PETG_SOFT_C - HOT_DAY_C) / (plate_c - HOT_DAY_C),
                  "estimated from a study of parked cars", note="the back teeth are on the wheel: the shared row above covers them"))
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
    f = r["status"] if r["factor"] is None else f"{r['factor']:.2f} {r['status']}"
    if r["kind"] == "condition":
      f += ", which is why the build includes the step under check"
    out.append(f"    {r['what']}: {f}")
    out.append(f"      worst load: {r['load']}")
    out.append(f"      it takes:   {r['capacity']}")
    out.append(f"      from:       {r['basis']}")
    if r["note"]:
      out.append(f"      note:       {r['note']}")
    if r["check"]:
      out.append(f"      check:      {r['check']}")
  return out
