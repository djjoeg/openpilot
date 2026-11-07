python3 - <<'EOF'
src=open('columnparts.py').read()
src=src.replace("SB_PIVOT = (SB_PLATE_X[1] + SB_NECK, 0.0)   # the arm's bolt (x, z); it runs along y",
"SB_PIVOT = (SB_PLATE_X[1] + SB_NECK, 30.0)  # the arm's bolt (x, z); it runs along y. 30 forward of the bracket's middle:\n"
"                                            # the arm's slot end reaches 51 back from the bolt, and the dash is 25 back")
src=src.replace('''def tab_bolts(tab_x0: float) -> Manifold:
  """The two M5 x 55 bolts through the bracket's bar and the tab (heads under the tab, nuts on the bar), and the arm's
  bolt and locking bolt through the fork, as solids for the clearance checks (bracket frame)."""''',
'''def tab_bolts(tab_x0: float, arm_deg: float = 0.0) -> Manifold:
  """The two M5 x 55 bolts through the bracket's bar and the tab (heads under the tab, nuts on the bar), and the arm's
  bolt and locking bolt through the fork (the arm at arm_deg), as solids for the clearance checks (bracket frame)."""''')
src=src.replace("  for (bx, bz) in ((px, pz), (px + MP.ARM_LOCK_R * math.sin(math.radians(0.0)), pz + MP.ARM_LOCK_R)):",
"  for (bx, bz) in ((px, pz), (px + MP.ARM_LOCK_R * math.sin(math.radians(arm_deg)), pz + MP.ARM_LOCK_R * math.cos(math.radians(arm_deg)))):")
open('columnparts.py','w').write(src)

p=open('params.py').read()
p=p.replace("COVER_FRONT_Z = -50.0      # the covers' front edge, behind the middle of the part of the wheel you hold (estimate)",
"COVER_FRONT_Z = -50.0      # the covers' front edge, behind the middle of the part of the wheel you hold (estimate)\n"
"COVER_FRONT_W = 100.0      # the covers' width at their front edge: they widen from there back to COVER_W at COVER_TAPER_Z\n"
"COVER_TAPER_Z = -200.0     # (estimates from photos; the right-side mount's lift lever, flipped up, swings in beside them)")
open('params.py','w').write(p)

a=open('columnassembly.py').read()
a=a.replace('''  def covers(self, back_z: float = -400.0):
    """The steering column covers: an oval cover_w wide and cover_h tall along the column, from their front edge back."""
    a, b = self.cover_w / 2.0, self.cover_h / 2.0
    pts = [(a * math.cos(u), b * math.sin(u)) for u in np.linspace(0, 2 * math.pi, 96, endpoint=False)]
    return CrossSection([pts]).extrude(COVER_FRONT_Z - back_z).translate((0, 0, back_z))''',
'''  def covers(self, back_z: float = -400.0):
    """The steering column covers: an oval cover_h tall along the column, from their front edge back; COVER_FRONT_W
    wide at the front edge, widening to cover_w at COVER_TAPER_Z and that wide from there back."""
    b = self.cover_h / 2.0

    def oval(w, z):
      pts = [(w / 2.0 * math.cos(u), b * math.sin(u)) for u in np.linspace(0, 2 * math.pi, 96, endpoint=False)]
      return CrossSection([pts]).extrude(0.5).translate((0, 0, z))

    front_w = min(COVER_FRONT_W, self.cover_w)
    taper = Manifold.batch_hull([oval(front_w, COVER_FRONT_Z - 0.5), oval(self.cover_w, COVER_TAPER_Z)])
    back = oval(self.cover_w, 0.0).scale((1.0, 1.0, (COVER_TAPER_Z + 0.5 - back_z) / 0.5)).translate((0, 0, back_z))
    return taper + back''')
a=a.replace("from params import (ARM_LENGTHS, ARM_SLIDE, CLAMP_Z, COVER_FRONT_Z, COVER_H, COVER_W, DASH_Z,",
            "from params import (ARM_LENGTHS, ARM_SLIDE, CLAMP_Z, COVER_FRONT_W, COVER_FRONT_Z, COVER_H, COVER_TAPER_Z, COVER_W, DASH_Z,")
a=a.replace("    return self._b(CP.tab_bolts(self.fit.tab_x0))", "    return self._b(CP.tab_bolts(self.fit.tab_x0, self.fit.arm_deg))")
open('columnassembly.py','w').write(a)
print('ok')
EOF
PYTHONPATH=/home/claude/pylib timeout 900 python3 /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side_test.py 2>&1 | tail -30