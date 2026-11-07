python3 - <<'EOF'
s = open('popparts.py').read()
old = s[s.index("  def __init__(self, wheel_od: float = WHEEL_OD_P"):s.index("  def profile(self):")]
new = '''  def __init__(self, wheel_od: float = WHEEL_OD_P, grip: float = GRIP_P, spoke_deg: tuple = None,
               n_teeth: int = FP.N_TEETH_SHORT, z_axis: float = Z_AXIS_P, mount_deg: float = MOUNT_DEG):
    from params import PAD, RIGHT_SPOKE_DEG
    spoke_deg = spoke_deg if spoke_deg is not None else RIGHT_SPOKE_DEG
    self.wheel_od, self.grip, self.n_teeth, self.mount_deg = wheel_od, grip, n_teeth, mount_deg
    self.rr = wheel_od / 2.0 - grip / 2.0
    self.rho = grip / 2.0 + PAD
    self.c1 = self.rho * (math.sqrt(2.0) - 1.0)
    self.z_bridge = -self.rho
    self.z_axis = z_axis
    self.z_p = z_axis + FP.R_P + CD_EXTRA
    self.z_root = self.z_p + GR.DEDENDUM * GR.MODULE
    self.z_tip = self.z_p - GR.ADDENDUM * GR.MODULE
    self.back_t = self.z_bridge - self.z_root
    self.z_band = z_axis + FP.ROLLER_R_F
    self.z_flat = z_axis - MP.PLATE_BOTTOM + FP.FLAT_CLEAR     # inside the teeth: clear of the carrier plate's edge
    self.r_flat = R_FACE_P + MOTOR_PLATE_T + 0.5               # ... out to here
    self.w_out = self.rr + self.rho + WALL
    self.w_in = self.rr - self.rho - WALL
    self.k_o = self.rr + self.c1 + self.rho + FP.CORNER_T * math.sqrt(2.0)
    self.k_i = self.rr - self.c1 - self.rho - FP.CORNER_T * math.sqrt(2.0)
    self.pitch_deg = 360.0 / FP.FACE_TEETH
    self.teeth_half = n_teeth / 2 * self.pitch_deg
    self.roll_half = self.teeth_half + FP.ROLL_PAST_TEETH
    self.lead_end = self.roll_half + FP.END_LEAD_IN
    self.chamfer_deg = math.degrees(FP.END_CHAMFER / FP.ROLL_BAND[1])
    self.half = self.lead_end + self.chamfer_deg
    self.joint_deg = FP.JOINT_TEETH * self.pitch_deg if self.half > 40.0 else None
    # the right spoke's junction, in degrees from the mount's middle (the piece is centred on the motor)
    self.spoke = (spoke_deg[0] - mount_deg - FP.SPOKE_ROOM_DEG, spoke_deg[1] - mount_deg + FP.SPOKE_ROOM_DEG)
    if self.back_t < 4.0:
      raise ValueError("the teeth would sit inside the channel")
    if not (self.w_in < self.r_flat - 5.0 and FP.ROLL_BAND[1] < self.w_out - 3.0):
      raise ValueError(f"a steering wheel {wheel_od} mm across and {grip} mm thick puts the grip off the teeth's radius")

'''
s = s.replace(old, new)
open('popparts.py', 'w').write(s)
EOF
cd /home/claude/deliver/hardware/cad && PYTHONPATH=/home/claude/pylib python3 -c "
import time; t0=time.time()
import popparts as PP
print('z_axis', PP.Z_AXIS_P, 'spring r', round(PP.SPRING_R,2), 'C', PP.C_BOLT.round(2), 'B', PP.B_BOLT.round(2))
for L in (-3,0,10,25,40,50,60,75):
  print(L, round(PP.spring_length_pins(L),2), round(PP.spring_force(L),1), round(PP.spring_torque(L)/1000,3), 'Nm  (over loops:', round(PP.spring_force(L, inside_loops=False),1), round(PP.spring_torque(L, inside_loops=False)/1000,3),')')
t = PP.PopTeeth()
print('rr', t.rr, 'rho', t.rho, 'back_t', round(t.back_t,2), 'z_root', round(t.z_root,2), 'z_flat', round(t.z_flat,2), 'z_band', round(t.z_band,2), 'z_tip', round(t.z_tip,2), 'w_in', t.w_in, 'w_out', t.w_out, 'spoke', t.spoke, 'half', round(t.half,2))
c = PP.pop_carrier(); print('carrier vol', round(c.volume()), 'bbox', [round(v,1) for v in c.bounding_box()], 'genus', c.genus(), round(time.time()-t0,1),'s')
g = PP.pop_motor_gear(); print('gear vol', round(g.volume()), [round(v,1) for v in g.bounding_box()])
s = PP.pop_solid(t); print('teeth vol', round(s.volume()), [round(v,1) for v in s.bounding_box()], round(time.time()-t0,1),'s')
"
