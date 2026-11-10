# Change log: Honda Accord lane keeping software

Versions are numbered like 1.0.0, and each one is a branch with that name (`v1.0.0`) in your GitHub copies. A
version never changes once it is made; a later one gets a new number and its own section here, newest first. The
first number goes up when a version needs something from you besides picking it (new parts, new wiring, or the car
setup again), the second when it adds or changes what lane keeping does, and the third for fixes only. The car
setup tools show the version when they start.

The code is in the `software` folder as two change files (patches), for reading or building it yourself. The comma
device installs it from your GitHub copies.

## 1.3.0 (2026-11-02): the right-arm mount, always on, the gear as the switch

The motor sits outside the steering wheel's rim at about 4 o'clock, on an arm from a plate under the lower column
cover, and it has power whenever the car is on: no lift lever, no switch, no relay. You switch lane keeping on and off
by sliding the motor along the column in the tower at the arm's end, its gear into or out of the steering wheel teeth. What it needs
from you: the parts below printed and fitted, the wiring below, the software installed from your GitHub copies, and
both parts of the car setup (part 1 asks which teeth are on: 20).

On GitHub since 2 Nov: branch `v1.3.0` of `github.com/djjoeg/openpilot` (your sunnypilot copy, renamed) and of
`github.com/djjoeg/opendbc`, with the earlier versions v1.0.0 to v1.2.1 beside it; the openpilot branch takes its
opendbc from your copy, at that branch's commit (checked on GitHub). Install with `installer.comma.ai/djjoeg/v1.3.0`.

### Software

- **The motor fitted: STEPPERONLINE 17HS15-1504S-X1, 45 Ncm at 1.5 A** (its maker's page, read 2026-11-02: 45 Ncm,
  1.5 A, 2.3 ohm, 4.4 mH, 40 mm, 5 mm D shaft; its own card, 6 Nov, says 39 ± 1 mm: all of the card is under
  "The motor's own card" below). The same holding torque as the 17HS16-2004S1 the software was written
  for, but at 1.5 A, so a third more torque per amp: `motor_k_torque` 0.212 (was 0.159), the same as the
  StepperServoCAN firmware's own motor, so a firmware torque unit is 0.125 Nm at the steering wheel. Without this the
  software would have pushed a third harder than meant and the panda's limit would have let it reach 5.9 Nm at the
  steering wheel. Lane keeping's most stays 3.9 Nm (31 units, 1.8 A in the motor); the panda's hard limit is now 35
  units, 4.4 Nm at the steering wheel (2.0 A). The grip test still pushes with the most the board gives, 3.3 A: about
  7.3 Nm at the steering wheel now, about 4 kg pulling on its edge (was about 3 kg). That is also what you would have
  to hold if the board ever failed at full push: still under the 50 N (about 5 kg) the European rule for lane keeping
  uses, but closer to it than before (a factor of about 1.26).
- **Always powered; on and off by the gear.** Lane keeping is available whenever the motor reports, so it comes on
  with the engage sound about 2 seconds after sunnypilot starts, as it did with the lever down. But the car port now
  starts every drive holding the motor back, silently, until the steering wheel has turned the motor by a degree
  (which only happens with the gear in the teeth); a second later it may push. With the gear slid out it never
  pushes, spins or chimes, for the whole drive. The 10-second retry after the gear ran off the end of the teeth is
  gone for the same reason: the motor stays off until the wheel turns it again. Slid out while lane keeping pushes,
  the motor spins for under 0.1 s, stops, and "Past the teeth: steer yourself" chimes once.
- **Messages:** the car setup and the drive check say to slide the motor gear into the teeth (on the earlier mounts:
  the lift lever) instead of switching the motor on; a slip in the grip test points at the slide's stop, the wing
  bolts and the gear's set screw; the teeth question names the 11, 15 and 20 teeth without the side-slide mount.
- **Version number** 1.3.0.

### Printed parts

Changed on 9 Nov (no printed part changed): the board came. Its maker's PCB file puts it at 56.0 x 43.3 mm, where
the model had 46 x 46. With its long side along the column it would hit the arm when the motor is slid 15 mm or
more down. With its long side around the wheel, all 8,391 checks pass, with a case 11 or 16 mm tall. So: **mount
the board with its long side running around the wheel, not toward the dash.** `rightarm.py` now models it that
way. Not checked yet: the plugs and cables coming out of its sides. (Retropilot's page gives the board 8 mm high;
the model keeps 16.)
- **What came (10 Nov, from your photos and Retropilot's page for the controller kit):**
  - the board, v0.5, with its software already on;
  - a 1 m power/CAN cable with a white 4-pin JST plug on both ends;
  - a 30 cm cable for reprogramming the board (black 5-pin end; not needed);
  - two long M3 bolts (about 40 mm) that hold the board to the back of the motor;
  - small M3 screws, for a bigger (Nema23) motor (not needed);
  - the magnet: the smooth flat discs in the clump of small screws (two seen; the screws cling to them). On 10 Nov I
    first wrote that it was missing; that was wrong;
  - the tan jig that centres the magnet.
- **Not in this kit: a motor-to-board cable** (it comes only with their motor kit). **Buy one:** a stepper cable with
  the motor's 6-pin plug (16 mm wide on the motor's card: PH 2.0) on one end and a 4-pin JST XH 2.54 on the other,
  the common 3D-printer kind. It must take the motor's pins 1, 3, 4, 6 (A+, A-, B+, B-) to the XH plug's 1, 2, 3, 4
  (the board's A1, A2, B1, B2); PartsBuilt's 1 m one says it does. Amazon pick (10 Nov, re-checked): TIEXYE
  4 x 500 mm, B0FD8PPNJY, $7.39, Fulfilled by Amazon; its page says XH 2.54 at the board end and PH 2.0 at the motor
  end, gives no wire order, and has 8 ratings (one had to swap the middle two wires). Same-day delivery is free
  only over $25. The motor's socket is PH 2.0: your card photo draws it 6 pins and 16 mm wide, and a 6-pin JST XH
  is about 17.3 mm (RS's spec for XHP-6), so 16 mm is the 2 mm PH size. The motor's own cable can't be used at the
  board: its far end (your 6 Nov photo) is a 4-pin 0.1 in plug, black, green, red, blue, which doesn't latch in
  the board's XH socket. Iverntech's 6 x 500 mm (B07Q12B6K5, 398 ratings) doesn't say which plug, so not picked. With it,
  ARCTIC MX-4 thermal paste 4 g, B07L9BDY3T, $4.99, non-conductive per its page (the board's underside says to
  apply paste). The board's software learns the motor's direction itself but not which wires pair up
  (`Learn_StepSize_WiringPolarity` in its calibration.c). Check with the 6-pin end plugged into the motor, at
  the 4-pin end (about 2.5 ohm with the meter's leads; 2.3 for the motor alone): XH pins 1 and 2 read
  about 2.5 ohm, 3 and 4 about 2.5 ohm, 1 and 3 nothing. 1 and 2 nothing but 1 and 3 about 2.5: the middle two
  wires are swapped. The 1 m power/CAN cable stays whole except its far plug,
  cut off for the lever nuts.
- **The magnet goes on the shaft's end**, which is under the middle of the motor's back sticker (you can see a dip
  there, 10 Nov). It has to be glued to the shaft itself so it turns with it, so the sticker's middle comes off at
  that step. The maker says a 1-2 mm thick, 5-6 mm magnet with about a 1 mm gap to the board's sensor.
- **Don't snap off the board's side tabs.** The page says Nema17 users may, but the board's 120 ohm CAN resistor (R44)
  sits on one of them.
- The board's own pin labels: Car (Vehicle) socket GND, CAN_H, CAN_L, Vin; Motor socket A1, A2, B1, B2; Debug socket
  GND, SWD, SCK, 3.3 V.

Changed on 7 Nov (no part changed): the design programs, lost when my workspace was replaced on 5 Nov, are rebuilt
from the chat record and kept on GitHub, branch `hardware` of `github.com/djjoeg/openpilot`, folder `hardware/cad`
(39 programs; `RECOVERED.md` there says what each makes). Checked by running them: plates 13, 14 and 15 come out
identical to your print files, part for part; the fit checks give 8,391 checks, none failing, and the stiffness
model gives the numbers below, both as before. Your copies of plates 12 and 13b turned out to be older than plate
13 (an arm from before v6), so the branch now has new ones with the v6 arm and carrier, as this log says they
should be. From now on every design-file change also goes to that branch.

Changed on 5 and 6 Nov (no software change; the version stays 1.3.0): the frame plate is being worked out again from
the plate alone, on paper first, because the v4 plate didn't fit the car. Your notes (5 Nov): the spare screws only
reached the cover's edge (two #8 x 2 in stainless pan head screws to buy), the long slot didn't reach far enough, and
the tilt lever needs room. Until the plate fits, the arm and the receiver wait; they go back on the fitted plate.

- **Frame plate, paper template v2, `frame-plate-v2-paper-template-your-printer.pdf`** (6 Nov, from your marked
  photo): the crossbar at the dash end and the link to it are gone, because they crossed the tilt lever's path. A
  new crossbar goes across at the wheel end, in the nook where the cover meets the wheel, 30 mm wide with trim lines
  A, B and C (C, 12 mm, is the narrowest), and comes down beside the lever's tip to the block's corner. The long slot
  is 14 mm longer toward the dash (your second screw sat near its end), and the long piece ends 8 mm past it. The cup
  slot, the block and the receiver's place are unchanged. Drawn 5.8% big for your printer (the first template's 4 in
  bar came out 4 1/32 in, so your printer prints at 94.5%). Not tried on the car yet. How I read the photo, for you to correct: the new crossbar's stem is drawn straight down,
  20 mm wide, ending at the block's corner, where your sketch slanted it out a little more toward the door.
- **Frame plate, paper template v1** (5 Nov), replaced by v2: it fit with both screws in their slots (6 Nov), the
  second one near the dash end of the long slot, but its crossbar at the dash end and the link crossed the tilt
  lever's path. Its printed-for-your-printer copy was drawn for 93.75% and came out 0.8% big.
- **Plate 15, `plate-15-frame-plate-fit-test.3mf`** (5 Nov), on hold: the frame plate alone in plastic, from the v1
  shape. It gets remade from whichever paper shape fits.

Changed on 3 Nov, from the prints you held on the car (no software change; the version stays 1.3.0): the arm v6
(the fit print) on the frame plate v5, and the teeth v3, replace the arm v3, the frame plate v4 and the teeth v2;
plate 14 is new (the arm v4 and v5, made earlier the same day, were never printed). Plates 9, 11, 12, 13 and 13b
carry them. The frame plate is new as well, so plate 13 is the whole reprint.

- **Plate 14, `plate-14-teeth-fit-sample.3mf`: the teeth's fit sample** (3 Nov): a 23 mm slice of the teeth's
  channel at the v3 width (1 mm wider than v2; marked 7 on the outer wall's outside), exactly the real piece
  where it touches the grip (both walls, the inner wall's lip, the inside of the back), with only 3 mm of back behind
  the channel and no teeth. 38 x 23 x 23 mm, 6.8 g if it were solid; on economy settings: 2 walls, 3 top and bottom
  layers, 15% infill. Try it on the grip before printing the teeth.
- **Plates 7 to 9, `plate-7/8/9-teeth-v3-*.3mf`: the teeth, third cut (v3)** (3 Nov): the channel 1 mm wider,
  7 mm narrower than first drawn from the 33 mm grip (v2's 8 was a little tight on the grip, plate 10's 6 was 1 to 3
  mm loose), and the ends cut back to 0.6 degrees (1.75 mm) past the middle of the last tooth space: the flat band
  (for the old roller) and the ramps beyond the teeth are gone, so the ends no longer stand up off the grip where the
  spokes' joins keep the piece from wrapping round it. The 20 set is now 42 x 131 x 46 mm, about 134 mm along the
  grip. Otherwise as v2; the v2 files are gone.
- **Plates 11 and 12: the right arm mount v6, the fit print, on the frame plate v5** (3 Nov, your note: more travel
  for the first print, and every slide worked the same way). Three pieces: the frame plate 88 g (40% gyroid), the arm
  180 g and the motor carrier 77 g (both solid).
  - **Both slides work the same way:** a groove through the outer piece's wall, an M5 wing bolt with a fender washer
    through it, screwed into an M5 nut in a slot in the inner piece (8.3 mm across the nut's flats, so it can't turn).
    Tightened, it pulls the inner piece against the outer one's wall; the groove's ends keep the inner piece in.
  - **The motor's slide along the column: 31 mm of travel** (v5: 15). The teeth piece may sit up to 12 mm nearer you
    or further than drawn (v5: 4); the groove reaches 1 mm past the deepest that needs, and down to off, 18 mm below
    the drawn depth, where the carrier sits on the tower's top (now 8 mm lower). Ticks on the carrier's bar from 18
    below to 13 above the drawn depth, 0.5 mm wide (v5's 0.8, a millimetre apart, would have run together). The bar
    is as long as before; slid all the way down, its end comes level with the tower's bottom.
  - **The arm's slide across: 17.5 mm either way** in the frame plate's receiver (v5: 5 in, 25 out, held by v4's
    pinch bolt). The arm's bar in the receiver is 20 x 30 (was 10 x 30); its nut drops into a slot in the bar's top,
    where the frame plate above keeps it in; the wing bolt comes in from the side facing you through a 42 mm groove
    in the receiver's wall. On that side you can reach it from your seat; v4's and v5's pinch bolt was on the dash
    side, where the photo estimates put its wings 3 to 10 mm into the dash. The groove is 3 mm below the bore's
    middle, so the washer passes the cup screw's head with the arm slid all the way in, and 6.4 mm tall (0.75 mm a
    side round the wing bolt) because its top edge prints as a 42 mm bridge, which may sag. The arm's deep part starts
    2 mm further out, so it stays clear of the receiver's mouth when the wing bolt reaches the groove's end.
  - **The frame plate v5:** v4 with the receiver's bore 20 wide (5 mm walls), the groove in place of the pinch bolt
    and its nut trap, and the labels cut in instead of raised: a fender washer under the cup screw would have sat on
    the raised WHEEL, and the arm slid all the way in passes over KEY.
  - **A fender washer under each cover screw** (README step 1): in the stiffness model the plate is held only under
    them, and the 25 mm washers hold it stiffer than the 18 mm ones v5's model had; with those, the arm slid 17.5 out
    with the motor 12 up gave 1.51 mm out of the teeth, at the mark.
  - **Stiffness** (`stiffness.py`, lane keeping's strongest push, 3.9 Nm at the steering wheel): as drawn, the gear
    +0.15 / -0.46 mm along the column with the arm held in the receiver, +0.49 / -0.93 with the frame plate held only
    under its two washers (v5: +0.20 / -0.49 and +0.56 / -1.00, with 18 mm washers); with the arm slid 17.5 out, the
    motor 12 up, or both, up to +0.28 / -0.71 and +0.69 / -1.27. All pass (at most 1.0 mm deeper, 1.5 out). The grip
    test pushes 1.9 times as hard: in the softer model the gear then goes 0.9 mm deeper as drawn, where its tips have
    1 mm before the bottom of the teeth (1.3 with both slides at their far ends: the tips reach the bottom), and 1.7
    out of the 3.5 mm in mesh (2.4).
  - **Checked in CAD**, 8,391 checks, none failing (`hardware/cad/rightcheck.py`). New, against the car's parts as
    estimated from your photos: the key's bulge and bezel, the key in it and the room to turn it, the wiper stalk's
    whole swing, the dash's face below the column, and the cup screw's head with a fender washer under it. The arm
    against the plate anywhere in the receiver's groove, and against the car where it can be with the gear on the
    teeth (4 mm in to 3 mm out from drawn) and on its way in from the key side; the arm's wing bolt and washer going in
    through the groove wherever the arm is; the arm's nut too tight to turn; the arm stopped past either end of the
    groove and held all round by the bore; the clearances (the arm's bar 0.2 mm a side in the bore, the wing bolt 0.75
    in its groove, its end 3.4 mm past the nut and 0.6 short of its hole's end). The rest as v5, over the longer slide
    (the teeth piece 12 mm either way).
  - **Close, in the estimates** (README, Not tested yet): with the motor slid all the way off, the wiper stalk pushed
    all the way down passes about 1 to 2 mm from the gear (it would touch with the arm 4 mm further out than drawn);
    the motor's carrier meets the teeth piece's outer edge if the arm goes about 5 mm further in than drawn; and the
    frame plate's dash-side edge, the same as on the v4 plate you held there, reaches 1.4 mm past the dash estimate,
    so the checks put the dash no nearer than that edge.
  - Not in the models: the spokes' joins and your hands near the gear.
- **The right arm mount v5** (3 Nov, replaced by v6 the same day, never printed), two pieces, both printed solid
  (about 253 g: the arm 176 g, the carrier 77 g). A review of v4 before printing found two faults: the arm bent too much
  under the motor's push, and the M4 stop's nut could turn in its slot.
  - **The arm is 50 mm deep along the column** from 5.5 mm outside the receiver to the tower, 1 mm under the frame
    plate. In v4 the 25 mm of 10 x 30 bar between the receiver and the tower twisted: in a finite-element model at
    lane keeping's strongest push (3.9 Nm at the steering wheel) the gear moved 0.9 to 1.3 mm deeper into the teeth
    one way and 1.4 to 2.1 mm out of them the other, when it has about 1 mm before its tips reach the bottom of the
    teeth and 3.5 mm in mesh; the car setup's grip test pushes 1.9 times as hard, so it would have jammed one way and
    skipped the other. v5 in the same model: +0.20 / -0.49 mm with the arm held in the receiver, +0.56 / -1.00
    mm with the frame plate held only at its two screws (the car, with the column cover under the plate, is between
    the two). `hardware/cad/stiffness.py` runs both; it passes. The cost: the arm can slide only 5 mm further into
    the receiver (out as far as you like), and 59 g.
  - **The slide is one wing bolt in a groove** (your idea): a 5.6 mm groove, 21.6 mm long, up the tower's outer wall;
    the M5 wing bolt, a fender washer under its wings, goes through it into an M5 nut in a slot across the carrier's
    bar. Loosen it, slide the motor along the column by it, tighten it: tightened, it pulls the bar against the outer
    wall. It is the lock, the depth setting, and the on and off. The groove's top end and the carrier sitting on the
    tower's top keep the carrier in. It replaces v4's push wing bolt and its M4 stop (bolt, fender washer, two nuts).
  - **How deep:** slide it up until the gear is all the way into the teeth (its tips on the bottom), back it down
    1 mm, tighten. Ticks a millimetre apart on the carrier's bar's outer face, read where the bar comes out of the
    tower's top, show where you are; the long ones are every 5, the middle one the drawn depth. The groove reaches 1
    mm past the deepest the gear could need (the teeth piece 4 mm nearer you than drawn), and 10 mm down to off.
  - **The nut can't turn:** v4's M4 slot was cut across the nut's corners, so its nut would have spun with the bolt.
    The slide's slot is 8.3 mm across the nut's flats; its bottom is the nut's own shape, a corner down, so the nut
    sits on the bolt's line.
  - Checked in CAD, 4,061 checks, none failing (`hardware/cad/rightcheck.py`): the clearances as for v4 (the arm
    slid 5 in or 20 out, the carrier anywhere in the groove, the teeth piece 4 mm either way, the wheel from -40 to
    +40 degrees, the gear in mesh over each set's arc); putting it together (the carrier down the tube, the wing bolt
    in along the groove, the arm into the receiver from 100 mm away); and new, that it works: each captive nut too
    tight in its slot to turn, even at the smallest size the standard allows (turned, its corners go 0.25 mm into the
    slide's slot's walls, 0.2 mm into the receiver's); the carrier held in every direction (past the groove's top the
    wing bolt meets its end, below off the carrier meets the tower, the tube all round); and the slide's clearances
    (the bar 0.25 to 0.3 mm a side in the tube, the wing bolt 0.35 in the groove, its end 1.2 mm past the nut).
  - Not in the models: the spokes' joins and your hands near the gear (README, Not tested yet).
- **The right arm mount v4** (3 Nov, replaced by v5 the same day, never printed), two pieces, both printed solid
  (about 195 g: the arm 118 g, the carrier 76 g).
  - **The tower is a closed square tube** (your idea; v3's was a channel open on the motor's side, so only the wing
    bolt held the carrier, with the heavy motor on it, in the channel): a fourth wall, 5 mm thick, on the motor's
    side, 0.3 mm clear of the bar. The carrier's bar goes in at the top (the end nearer the steering wheel) and
    slides all the way through. Both ends of the tube are chamfered so the bar finds its way in.
  - **The stop is an M4 x 30 bolt** up the middle of the bar from its bottom end, into an M4 nut in a slot 4 mm in,
    a fender washer under its head, locked by a jam nut against the bar's end. The washer is wider than the tube: as
    you slide the motor up, it lands on the tower's bottom face. So it is the stop, and it keeps the carrier in.
    Screwing the bolt out or in sets how deep the gear sits, +-4 mm around the drawn depth (the washer 8 mm from the
    bar's end). v3's lug and its M5 stop bolt are gone: one M5 wing bolt and two M5 nuts fewer.
  - **It goes together off the car** (README step 3): the motor and the gear on the carrier, the nuts in, the
    carrier down the tower's tube from the top, the stop bolt in below the tower; then the arm, with all of that on
    it, into the frame plate's receiver. On the car the steering wheel is in the way of the tube's top.
  - **The gear meets the teeth 4 degrees higher, at 3:52** (26 degrees below 3 o'clock; v3 had 30, 4 o'clock): the
    middle of the gap between the spokes' joins on the back of the grip, measured on 3 Nov (below), so the 20 teeth
    fit between the joins.
  - The arm's foot (where the bar runs into the tower) is cut level with the bar's top: at the new angle it stood up
    past the bar, into the frame plate's way when the arm slides across.
  - The same as v3: the arm's bar in the receiver (+-25 mm across), the tower's wing bolt pushing the bar tight, the
    motor's four M3 x 10 through the pads, and on and off by sliding the motor (up against the stop: on; down 6 mm or
    more: off; all the way down, 10 mm, the carrier sits on the tower's top).
  - Checked in CAD (`hardware/cad/rightcheck.py`), 5,384 checks, none failing: v3's checks (below) with the M4
    bolt, washer and nuts among the parts; and two new ones for putting it together: the carrier going down the
    tower's tube from 176 mm up, past the tower's nut and its wing bolt (backed out), and the arm, with everything
    on it, going into the receiver from 100 mm away, past the plate, the column cover, the grip and the teeth.
- **The right arm mount v3** (2 Nov), replaced by v4 above: two pieces, both printed solid (about 180 g).
  v3 replaced the v2 I first made on 2 Nov (four pieces, seven wing bolts), which had an adjustment for every unknown
  and a mistake I missed: its motor carrier could not have been put into the bracket's sleeve, which was closed at
  both ends.
  - **The arm:** the 10 x 30 bar slides in the receiver (+-25 mm across: in by 25 the tower meets the receiver's end),
    with a tower at its end: a channel along the column, open on the side towards the motor.
  - **The motor carrier:** the motor bolts to its plate (four M3 x 10); its 16 x 16 bar slides in the tower's channel.
    One wing bolt through the tower's outer wall pushes the bar tight (its nut dropped into a slot from the top). A
    wing bolt up through the lug at the bar's bottom end is the stop, locked by a jam nut; it sets how deep the gear
    sits, +-4 mm around the drawn depth (it has to be right to about a millimetre: the gear's tips clear the teeth's
    roots by 1 mm at the drawn depth).
  - **On and off:** slid up against the stop, the gear is in the teeth (lane keeping on); slid down 6 mm or more, out
    of them (off). All the way down (10 mm) the carrier sits on the tower's top. With the wing bolt loose, gravity
    pulls the carrier down the column and into the back of the channel.
  - **It goes on with the motor on it:** the bar comes in from the motor's side into the channel, slid down, then up
    to the stop.
  - **Pads round the motor's four screw holes:** the motor's holes are 4.5 mm deep (STEPPERONLINE's drawing for this
    motor family; not measured on yours), so an M3 x 10 through the plate alone would bottom out; with the 1 mm pads
    it goes 4 mm in.
  - **Not adjustable any more:** up and down, and the motor's angle. Where the gear sits along the teeth is set by the
    arm across and by the gear's place on its shaft (its set screw).
  - Checked in CAD (`hardware/cad/rightcheck.py`), 3,502 checks, none failing, with each of the three teeth sets (the 20 on the car): the carrier going in (motor on, slid
    out 6 and 10 mm, from 40 mm away); every part, bolt, nut and the room to turn every wing bolt, against each other,
    the column cover, the grip and the teeth piece, with the carrier anywhere from all the way down to the deepest
    stop (1 mm steps) and the stop set for the deepest, drawn and shallowest depth; the arm slid 20 mm in or out
    across; the teeth piece moved 4 mm either way along the column (the plate sitting nearer or further than
    measured), with the stop set to match; the steering wheel turned from -40 to +40 degrees; the gear in mesh over
    the teeth's whole arc (0 overlap); slid 6 mm out, the gear clears the teeth by 2.5 mm at any wheel angle.
    Tightest: the motor's side 1.85 mm from the carrier's bar; slid all the way down, the motor's board 1.8 mm from
    the tower (the board is drawn as a 46 x 46 x 11 box). Not checked: the steering wheel's spokes going past the
    gear on a full turn (they are not in the model), and the gear sliding back in out of step with the teeth (its
    pointed tips should turn it into step; try it by hand).
- **Plate 13, `plate-13-all-in-one.3mf`: one print for all four pieces** (2 Nov; 3 Nov with the teeth v3, the
  arm v6 and the frame plate v5): the frame plate v5, the 20 teeth (19 teeth, 19.5 degrees each way: the set of the first print you held on
  the wheel; answer 20 in the car setup), the arm and the motor carrier on one 256 x 256 mm bed, each with its own
  settings (the plate and the teeth 40% gyroid, the arm and the carrier solid), clear of the front-left nozzle-wipe
  corner. `plate-13b-all-but-the-frame-plate.3mf` is the same without the frame plate. Made by
  `hardware/cad/allinone.py` and read back like the other plates (every piece's mesh, place, settings, on the bed,
  inside its edge). Plates 11, 9 and 12 stay as the one-at-a-time way.
- **The teeth, second cut (v2)** (1 Nov), replaced by v3 above: the channel 8 mm narrower (plate 10's fit test: 6
  was still 1 to 3 mm loose), the inner wall only in the middle (16 degrees), one 12 mm zip tie slot there, the ends
  bare, each set only as long as its teeth, the old roller's band cut down level.
- Done or superseded: plate 0 (the slot plate, the measuring jig), 0b (frame plate v1, marked up on the car), 5 and 6
  (the arm along the column), 10 (the fit test); the arm v3, the frame plate v4 and the teeth v2 (3 Nov).
- Pictures for review: `hardware/report/review-*.png` (the assembly, the motor's slide in and out, the arm's slide
  in the receiver, each piece); made by
  `hardware/cad/visuals.py`. The plate pictures' two titles no longer run into each other (3 Nov).
- **In your car** (2 Nov; drawn again 3 Nov with the arm v6, the frame plate v5 and the teeth v3):
  `hardware/report/in-the-car-photo-00.jpg` (from your seat) and `in-the-car-photo-33.jpg` (beside the key, by your
  right knee), each with a before-and-after, are your own photos with the build drawn in:
  the printed parts, the motor, the gear, the bolts and the zip ties as the CAD has them, drawn with the camera solved
  from each photo (the key's bezel, the cluster and the grip for photo 33; the grip's outline and the cluster for photo
  00, fitted to 0.3 px), hidden behind the grip, the hub and the spokes where they are in front, lit and blurred to
  match the photo. Not exact: the motor's board (a generic board), the cable's path (a guess, tidied along the arm),
  the steering wheel's turn in photo 00 (about 17 degrees right, from its spokes and badge: the teeth are drawn turned
  with it). From your seat almost nothing shows: a grey edge round the grip from 3 to 6 o'clock, the two zip ties,
  the corner of the motor's board at 4 o'clock, and the teeth through the gap by the right lower spoke. Beside the key
  the motor sits where your phone was for that photo. Made by `hardware/cad/incar.py` and `photocomp.py`.
- **In 3D** (3 Nov; the same day for v4, v5, then v6): `hardware/report/arm-3d.html`, one page to turn round, zoom and
  take apart: the printed parts as the print files have them, where they go on the car, with the motor, the gear,
  the screws, the zip ties and the bolts, washers and nuts; the grip and the column cover round them (the cover
  approximate, the motor's board a plain box). Tap a part for its name and what it does; Back and Next take it apart
  and put it together in nine steps, in the v6 order (README steps 1 to 4: the plate, the teeth, the motor and gear
  on the carrier, the motor's nut, the carrier down the tower's tube, the motor's wing bolt into the groove, the
  arm's nut and the arm into the receiver, the arm's wing bolt into its groove, the motor slid up the groove into the
  teeth). The view buttons' views follow the parts as they
  come apart, so nothing leaves the picture; once you turn or zoom it yourself, it stays put. It draws itself
  (WebGL, no library); made by `hardware/cad/viewer3d.py` from `viewer3d_page.html`.

### Bought parts

- **Hardware for plates 11 and 12** (v6, 3 Nov): 2 M5 x 20 wing bolts (the arm's, the motor's) and 2 M5 nuts (one in
  the arm's bar, one in the carrier's bar): the 20-piece wing bolt pack, and the nuts from your own M5 kit (plain hex
  nuts, not nylon lock nuts, which are too tall for the slots); four of your fender washers (3/4 to 1 in across), one
  under each wing bolt and one under each cover screw. 4 M3 x 10 (the motor to the carrier); one M3 x 10 set screw (the gear). v4's
  M4 stop (an M4 x 30, two M4 nuts, a fender washer) is gone; v3 used 3 wing bolts and 4 M5 nuts.
- **The Amazon list, price-checked on the shop pages (2 Nov):** the wishlist "Accord lane keeping" holds the 12 V
  plug ($11.99), WAGO 221 12-piece ($12.45: three 5-way lever nuts, two are used; it replaced the 28-piece, $20.95),
  20 AWG wire ($8.48), M3 x 10 button head screws, 50 ($5.99; they replaced the K Kwokker M2 to M5 screw kit, $21.50,
  since the M5 nuts come from your own kit and nothing used M4 then; the v4 stop does, above), M3 x 10 set screws
  ($6.99), M5 x 20 wing bolts ($9.98), silicone tape ($8.99) and the multimeter ($13.99, $12.59 with its coupon):
  $78.86. Taken off earlier: the relay and the switch leads (nothing switches now), the fuses (the plug has its own
  15 A fuse), the washers and zip ties (owned).
- **Recommended, not on the list yet:** a 120 ohm resistor (a $5 pack) across the pink and blue wires at the harness
  end. The board has one at its end; a CAN pair wants one at each end, and the comma device's end has none that I
  know of. Over 1 to 2 m it will very likely work with the board's alone; the multimeter check tells (about 60 ohm
  across the pair with both, 120 with the board's alone).
- **Bought:** the motor (above), the StepperServoCAN board (Retropilot), the cover screws (Mellewell #8 x 1-1/2
  stainless, 100, $9.99); ordered 2 Nov: the Amazon list ($78.86). Owned: fender washers, zip ties, filament, the M5
  nuts. Still to buy: the comma device and the long OBD-C cable ($1,019). When: once the arm is on and the gear is set
  in the teeth (step 4). Its 30-day money-back trial starts the day it is delivered, and comma's page (2 Nov) says
  orders go out the next business day by free UPS 2nd Day Air (US, signature needed): about 3 business days, while
  you wire the plug and the board and power the board up. Its harness is needed for the rest of the wiring.

### Wiring

- **No relay, no switch.** The plug's + and - leads go into two WAGO lever nuts; from them, the comma harness (its
  two red and its two brown on +, its two black on -; it has two brown, corrected 6 Nov) and the board's Vin and GND. The board's CANH and CANL go to the
  harness's pink and blue (CAN1, the motor's network), twisted together. The harness's orange and green pairs (CAN0,
  CAN2), its second pink and blue pair and the grey loop wire are not used. The plug's own 15 A fuse is the only fuse
  (the car's socket is rated 10 A; the draw is under 4 A). Picture: `hardware/report/wiring-right-arm.png`.
- **The first power-up:** a new board may calibrate itself the first time it has power, turning the motor slowly for a
  while. Do it with the gear out of the teeth (the motor slid down, or before the carrier goes on the arm). If its blue
  light stays on, press its F1 button.
- **The harness, from comma's own drawing** (6 Nov: `harness/v3/Developer_Harness.pdf` and `Harness_Box.pdf` in
  comma's hardware repository, github.com/commaai/hardware). The Developer harness is an 18-pin Molex plug
  (501646-1800) with loose wires 120 mm (4.7 in) long; the plug goes into the harness box, and the box's other end
  takes the OBD-C cable to the comma device. Its wires: 12 V in, red, two; ignition, brown, two; ground, black, two;
  CAN0 orange (H) and green (L); CAN1 pink (H) and blue (L), two of each, the same network passed through; CAN2
  orange and green; and a 40 mm grey loop between pins 3 and 5, which switches on the box's own 120 ohm on CAN0
  (leave it as it is; it has no bare ends to tape).
  - **Two brown, not one.** Each same-colour pair (red, brown, black) is twisted together and goes in one hole of
    its lever nut: the + nut then holds 4 (plug +, red pair, brown pair, board Vin), the − nut 3.
  - **The wires are thin:** 26 AWG by a builder who used this harness (jackstromberg.com, July 2026; comma's drawing
    gives no gauge), and the lever nuts take 24 AWG at the smallest. A twisted pair is twice that, inside the range;
    a single wire (pink, blue) gets its bare end folded back on itself to double it. Tug each one after the lever
    goes down.
  - **The box has no 120 ohm on CAN1** (its drawing has them on CAN0 and CAN2 only), so the resistor across pink and
    blue at the harness end goes from optional to recommended (a $5 pack of 120 ohm resistors; not on the shopping
    list yet). **7 Nov: left out by your choice**, to keep the wiring to plain wire-to-wire joins: pink and blue each
    join their wire to the board in an inline lever nut (221-2401, one wire in each end), and check 4 reads about
    120 ohm (the board's own). On a run this short the board's resistor alone is expected to do. If the comma ever
    reports the motor's messages dropping out, this resistor is the first thing to add.
  - **With 120 mm of loose wire, the lever nuts sit right by the box.** Pink and blue get extended to the board with
    one twisted pair (a piece of old ethernet cable, 24 AWG, fits the lever nuts).
  - **The box's size isn't published** (not on comma's shop, setup or hardware pages); to measure when it comes.
    Normally it sticks on with its adhesive pad behind the rear-view mirror's cover, plugged into the car's
    lane-keeping camera (comma's setup page). This car has no such camera, so it goes where the nuts are: under the
    dash, right of the column, with the long OBD-C up to the comma device.

### The motor's own card (17HS15-1504S-X1, from your two photos of the card in its box, 6 Nov)

Written down word for word from the card, so it isn't lost; the photos are in the chat of 6 Nov.

| From the card | Value |
|---|---|
| Connection | bipolar |
| Current | 1.50 A |
| Resistance, each coil, at 25 °C | 2.30 ohm ± 10% |
| Inductance, at 1 kHz | 4.40 mH ± 20% |
| Holding torque | 0.45 Nm (3.98 lb-in) |
| Step angle, accuracy | 1.80°, ± 5% |
| Rotor inertia | 54 g·cm² |
| Weight | 0.28 kg (0.62 lb) |
| Temperature rise | 80 °C at most |
| Surroundings while running | −10 to 50 °C (14 to 122 °F); humidity 85% at most, no condensation |
| Insulation | 100 Mohm; class B, 130 °C (266 °F); 500 V AC for 1 minute |
| Body | 42.3 mm square at most, 39 ± 1 mm long |
| Mounting holes | 4 × M3, 31 ± 0.2 mm apart each way, at least 4.5 mm deep |
| Shaft | 5 mm (+0 / −0.012), 24 ± 1 mm out from the face; a flat 15 ± 0.25 mm long, 4.5 ± 0.1 mm across the flat |
| Round boss on the face | 22 mm (+0 / −0.05) across, 2 mm tall |
| Plug on the motor | a 6-pin socket on one side at the back (16 mm wide, 6.5 mm proud of the body, 11 mm along it); pins 1 A+, 3 A−, 4 B+, 6 B− |
| Cable | 1000 ± 10 mm, UL1007 24 AWG, each coil's pair twisted |
| Cable's far end | 4-way Harwin M20-1060400 housing, M20-1180046 terminals (female, 2.54 mm = 0.1 in pitch, one row) |

| Pin at the far end | Coil end | Wire |
|---|---|---|
| 1 | A+ | black |
| 2 | A− | green |
| 3 | B+ | red |
| 4 | B− | blue |

- **What it settles:** the coil pairs are black–green (coil A) and red–blue (coil B), as the wiring page's check 1
  assumes; on the meter each pair should read the card's 2.3 ohm (2.1 to 2.5) plus a little for the meter's leads.
- **For the board (due 9 Nov):** the cable ends in a 0.1 in, 4-way female plug, so it pushes straight onto a 4-pin
  0.1 in header if the board's motor socket is one. Which pin order the board wants is still to read off the board.
- **Step order, as the card gives it** (going down the list turns it clockwise, up it counter-clockwise): 1: A+ +,
  B+ +, A− −, B− −; 2: A+ −, B+ +, A− +, B− −; 3: A+ −, B+ −, A− +, B− +; 4: A+ +, B+ −, A− −, B− +.
- **To keep in mind:** the card rates it for 50 °C (122 °F) around it while running. A car parked in summer sun gets
  hotter than that inside; how much hotter it gets where the motor sits isn't measured.
- **For the CAD, when it's rebuilt:** the body was drawn 40 mm long (the maker's page); the card says 39 ± 1, so 40
  is inside its spread. The shaft's numbers above are to be checked against the gear's hole then.

### Measured so far

- The cup screw is 127 mm behind the back of the grip (the photo model said 103 to 120). The second screw is 40 mm
  towards the wheel and 85 mm towards the driver's door from it. The cover's screws go into the column assembly, not
  the upper cover (Honda's own instructions take the upper cover off first). The teeth channel wants to be 8 mm
  narrower than drawn from the 33 mm grip.
- **Where the spokes meet the grip** (2 Nov, re-read from the two head-on photos, 36 and 00, with their cameras
  solved; angles on the steering wheel itself, 0 at 3 o'clock with the wheel straight): the cruise-button spoke meets
  the grip from about +13 down to -6 degrees (2:34 to 3:12), the silver spoke below it from about -53 to -70 (4:46 to
  5:20; photo 00 says -58). The earlier figure for the cruise spoke's lower edge, -23 (3:46, from photo 36 alone), took
  in the corner of its silver frame inside the grip; photo 00 and your close-up of the test teeth show the gap open
  below the buttons. Each edge good to about 3 degrees (black on black where the spoke joins the grip). So the gap
  runs from about 3:12 to 4:46, its middle about 4 o'clock, where the gear is: the teeth piece's raised inner edge
  (3:44 to 4:16) is about 16 degrees (45 mm) clear of the cruise spoke and 15 (40 mm) of the silver one, and its bare
  ends run over both joins, as drawn. The column's underside doesn't show in the head-on photos (the hub hides it;
  through the gap below it you see the footwell); where the gear lands still comes from the side photos and the arm.
- **Where the spokes' joins leave the back of the grip** (3 Nov, for the teeth, which sit on the back): measured on
  photos of the same steering wheel from eBay listings, read the same way as yours (the rim's outline fitted, the
  light and dark read off round the grip, the angle squared up by the wheel's own symmetry, the view from behind
  mirrored). The back of the grip is clear from about 6 to 46 degrees below 3 o'clock (3:12 to 4:32), the two photos
  within about 2 degrees of each other. The silver spoke's join reaches further round on the back (46) than its edge
  seen from the front (53, above). The 20 teeth take 39 degrees, plus 0.6 at each end, so they fit only with the
  gear at the gap's middle, 26 degrees (3:52): the arm v4 puts it there. At v3's 30 the teeth's lower end would have
  sat about 4 degrees onto the silver spoke's join.

### Test results (2026-11-02, version 1.3.0)

| Suite | Result |
|---|---|
| opendbc car tests | 904 run: 560 passed, 344 skipped. New: the motor coming on waits for the steering wheel; the gear slid out never pushes; slid out while pushing stops once; a free spin holds for as long as the wheel doesn't turn the motor (no retries) |
| the panda's safety tests (the whole suite) | 8,533 run: passed, 928 skipped; MISRA check clean; the panda's firmware builds with the safety mode; the safety mode's code 100% covered by its tests |
| sunnypilot: setup tools (35), the lift lever as one system (13; two new: the gear slid out of the teeth is quiet and never pushes, slid out while steering chimes once), gyro steering and steering learner (9), phone page (5), settings (4), the two chimes (10), the comma device's own speed (6) | 82 passed |
| ruff on the changed code in both repos and the changed CAD files | clean |
| the version branch (`push_fork.sh … --dry-run`) | v1.3.0 points `opendbc_repo` at opendbc commit `dfcbdc6f` |
| the right arm mount v3, built from the CAD files | 3,502 clearance, fit and mesh checks with all three teeth sets, none failing |
| the right arm mount v4 and the teeth v3 (3 Nov), built from the CAD files | 5,384 clearance, fit, assembly and mesh checks with all three teeth sets, none failing |
| the right arm mount v5 (3 Nov), built from the CAD files | 4,061 clearance, fit, assembly, function and mesh checks with all three teeth sets, none failing |
| v5's stiffness (`stiffness.py`), lane keeping's strongest push | the gear +0.20 / -0.49 mm along the column (arm held in the receiver), +0.56 / -1.00 mm (frame plate held at its screws); pass |
| the right arm mount v6 and the frame plate v5 (3 Nov), built from the CAD files | 8,391 clearance, fit, assembly, function and mesh checks with all three teeth sets and against the car's parts round the key, none failing |
| v6's stiffness (`stiffness.py`), lane keeping's strongest push | as drawn, the gear +0.15 / -0.46 mm along the column (arm held in the receiver), +0.49 / -0.93 mm (frame plate held under its two fender washers); at the slides' far ends up to +0.69 / -1.27; pass |

None of it has run on a comma device or in the car yet: the tests are simulations of the car, the motor and the
panda.

## 1.2.1 (2026-10-26)

Print plates for Bambu Studio: the twelve printed parts laid out on four plates, each a file Bambu Studio opens
with the parts placed and their settings attached. Nothing changes in what lane keeping does. What it needs from
you: nothing, if you have 1.2.0; the plates are the same parts.

### Software

- **Version number** 1.2.1. No other change.

### Printed parts

- **Four plate files in `hardware/plates/`,** laid out for the 256 x 256 mm bed (A1, P1P, P1S, X1, X1C, X1E), 10 mm
  from the bed's edge, 8 mm between pieces, the front-left 18 x 28 mm corner (the X1's and P1's nozzle wipe) kept
  clear: plate 1 the mount (12 pieces: the mounting plate, the motor bracket, the lever, the gear, the spool, the
  board cover, the strip clamp, the foot bar and four shims), plates 2 to 4 one teeth set each. A picture of every
  plate from above and in 3D, with the pieces named.
- **Every piece carries its settings in the file:** 0.2 mm layers, 4 walls, 5 top and 5 bottom layers, 40% gyroid
  infill, no supports; the gear and the lever 100% (rectilinear, the pattern Bambu Studio allows at 100%). The
  printer, the filament and the layer-height profile stay whatever is selected in Bambu Studio: the files carry no
  printer, so one set fits any of these printers. A single project file holding all four plates would need one
  printer's full settings written into it; that can be made once the printer model is known.
- **How the files were made and checked.** `hardware/cad/plates.py` reads the twelve STL files, packs each plate
  (rows from the back of the bed, a piece turned 90° where that packs better), writes each plate as a 3MF: the
  meshes in `3D/3dmodel.model` and the names, settings and plate in `Metadata/model_settings.config`, the way Bambu
  Studio writes and reads them (its source, `bbs_3mf.cpp` and `Plater.cpp`, read on 2026-10-26: a file without
  Bambu Studio's project settings keeps the user's presets, is centred on the bed, and its per-piece settings are
  read all the same). Each file is read back and compared with what was placed: every piece's vertex and triangle
  counts, its position, that it sits on the bed, that its settings are there, that the plate lists it, that no two
  pieces are closer than 8 mm and none is in the wipe corner. **Not opened in Bambu Studio here** (no copy of it in
  this workspace); if a file will not open, the STL files and the settings in the README are the fallback.
- The STL files, the report and the pictures are unchanged from 1.2.0.

### The package

- **README:** the Print section now starts with the plates and says what Bambu Studio will say when opening them.
  The Buy table now has a link and a price for every part (prices read on 2026-10-26 where it says "today", the
  rest typical), in four orders: Amazon, comma, the Retropilot store, Lee Spring.
- **The power switch's part number corrected: Omron SS-5GL2T.** The T is the version with 2.8 mm push-on tabs
  (no soldering); the SS-5GL2-F the earlier lists named is the solder-terminal version (Octopart's listings of
  both, read 2026-10-26). Same body, same holes: nothing printed changes. The switch's two wires are now bought as
  push-on connectors with the wire already crimped on.
- The separate 20 to 30 cm motor cable is off the list: the motor's own 1 m cable reaches the board on its back,
  coiled and tied.
- **Build guide:** the "Start here" tab's print step points to the plates; its Buy section links to the README's
  table; the switch row corrected in both tabs.
- `accord-lane-keeping-other-mounts-1.2.0.zip` is not remade; it is still the one to use.
- The 1.2.1 zip sent earlier on 2026-10-26 had the old switch part number; this one replaces it (same number,
  these text changes only, nothing printed or in the software differs).

### Test results (2026-10-26, version 1.2.1)

| Suite | Result |
|---|---|
| sunnypilot: setup tools (35), settings, phone page and the lift lever as one system (20) | 55 passed; ruff clean |
| the version branch (`push_fork.sh … --dry-run`) | v1.2.1 points `opendbc_repo` at opendbc commit `5866e142` (unchanged); the opendbc patch regenerated byte for byte the same |
| the four plates, built from the STL files | every piece placed, read back and matched (counts, position, on the bed, settings, listed on its plate), no two closer than 8 mm, nothing in the wipe corner; ruff clean |

## 1.2.0 (2026-10-25)

The package is now one build: the side-slide mount, finished, with a short shopping list, twelve files to print and
three sets of steering wheel teeth (straight roads first). The other four mounts are out of the package, in a
separate file. What it needs from you if you already have a lift lever mount: nothing. If you print this one: the
measurements in the guide's first step, then part 1 of the car setup with it fitted.

### Software

- **Three teeth sets.** The car setup's question "which steering wheel teeth are on" now takes the number on the
  printed piece: 11 (the side-slide mount's straight-roads teeth, 10.8° each way, 21.7° end to end), 15 (its
  highway teeth, as the other short teeth) or 20 (its winding-roads teeth, 19.5° each way, 39° end to end), as well
  as 29 and 45 as before. The config's `tracked_arc_deg` and `mechanical_ratio` (166 / 16 on the side-slide mount's
  teeth) are saved from the answer; the curve chime uses the set's reach.
- **The turn check tells the sets apart.** Without a roller the motor gear leaves the last tooth cleanly, so part 1's
  wheel turn is matched to 20% instead of 35% on those sets, enough to tell 11, 15 and 20 from each other. A turn
  that fits another set better names that set ("as far as the 11 degree teeth reach, not the 15").
- The setup's push during part 1 stops after 6°, inside even the smallest set (10.8°).
- **Version number** 1.2.0.

### Printed parts

- **The side-slide mount is finished: its plate is fixed to the car.** A tongue at the mounting plate's dash end
  carries a foot: a level plate that lies under the lower column cover's underside and is held by the cover's own
  screw under the key cylinder (a 4.2 x 45 mm sheet metal screw in its place, the same pitch), through a 30 x 28 mm
  window that takes the screw wherever it falls: the cover anywhere from 70 to 89 mm behind the back of the round
  part you hold, the screw 4 mm off either way, the mount turned up to 3° either way. A printed bar under the foot
  bridges the window (the screw's head sits on it), and up to four 2 mm shims fill the gap between the foot and the
  cover. A layer of silicone tape goes on top. No drilling, nothing else touched.
  - Margins: the screw holds the mount's weight on a hard bump 2.73; the mount doesn't twist on its one screw 1.95
    (the foot's rub on the cover, silicone tape on it; dry it would be 1.17, so the tape is part of the build, and
    the push test proves it: 5 kg sideways at the motor with a luggage scale, nothing may move); the bar takes the
    screw's clamp 2.42; the foot holds the mount's weight 2.83. All estimates on the low side; the clamp of a small
    screw tightened by hand is taken as 600 N.
  - The plate is one print still (`side-mounting-plate`, 119 x 107 x 46 mm, 69 g solid); the foot rises from it at
    70° and needs no support. New small prints: `side-foot-bar`, `side-foot-shim` (print four).
- **Three sets of steering wheel teeth,** the same piece with 10, 14 or 18 teeth: `side-steering-wheel-teeth-11-straight-roads`
  (10.8° each way), `-15-highway` (15.2°, the set from 1.1.0) and `-20-winding-roads` (19.5°; 208 mm long, it fits a
  220 mm bed). The number is cut into the channel's outer wall so you can read which is on. Each set is checked
  with the gear over its whole arc, sliding in and out, the steering wheel turned through and past it, and slid in;
  all pass. On the highway the 10.8° set covers curves of about 240 m radius and up (steering ratio 16 to 1, wheelbase
  2.8 m; this car's ratio is somewhere between 13 and 18, so 190 to 270 m); the chime says when a curve is beyond
  the teeth.
- **The lever turns on a screw, not a dowel pin.** An M4 x 20 socket head screw goes in from the ear's inner end
  (its head sunk in the inner lug) into an M4 nut in a pocket in the outer lug; the lever's hub covers the pocket.
  No press fit, nothing to tap in. The ear is 1.5 mm longer inward and the lever sits 1.5 mm further in.
- **Bought parts, side-slide mount:** the rail and block, the constant force spring, the roller switch, the
  4.2 x 45 screw for the cover, and the screws: M3 x 6 button head (4), M3 x 6 socket head (4), M3 x 10 (6, four with
  M3 nuts), M2 x 12 with nuts (2), M4 x 20 (2: the spool's axle and the lever's pivot), M4 washers (2), an M4 nut, an
  M3 x 10 set screw, silicone tape. The dowel pin is gone; the spool's axle is now drawn as the M4 x 20 the list
  always said (it was drawn 25 long).
- The report has a new section, the foot on the column cover, with the screw's room in the window and the shims
  for three cover positions, and the car estimates for the nearest and the farthest cover position it is drawn for.
  The question about fixing the plate is answered; the question about the column cover's front edge replaces it.

### The package

- **One mount.** `hardware/stl/` holds only the side-slide mount's twelve files; `hardware/report/` its report and
  three pictures. The dash, column, right-side and back-teeth mounts (their 50 files, their report and pictures)
  are in `accord-lane-keeping-other-mounts-1.2.0.zip`, unchanged byte for byte since 1.1.0. The CAD program still
  makes all of them.
- **README:** what to buy, what to print, what to do, in that order.
- **Build guide:** a new first tab, "Start here", for this build: measure, buy, print, build, wire, install, set up,
  first drives, what is not checked. The old tab stays for the wiring, the software, the car setup and the other
  mounts.

### Test results (2026-10-25, version 1.2.0)

| Suite | Result |
|---|---|
| opendbc car tests | 901 run: 557 passed, 344 skipped (the config test now covers the three side-slide sets) |
| the safety mode's tests (its code is unchanged) | 114 run: 101 passed, 13 skipped |
| sunnypilot: setup tools (35, one new: the two new sets, and the wrong answer told by the turn), phone page and prompter (5), settings (4), the lift lever as one system (11), gyro steering and steering learner (9), the two chimes (10), the comma device's own speed (6) | 80 passed |
| ruff on the changed code in both repos | clean |
| the version branch (`push_fork.sh … --dry-run`) | v1.2.0 points `opendbc_repo` at opendbc commit `5866e142` |
| the side-slide mount, built from the CAD files | its twelve files each one closed solid that fits a 220 mm bed (the 20 set at 208 mm); every check passing for all three teeth sets; the screw inside the window with room to spare over the whole range of cover positions; built twice, the same report and the same files (the three teeth files come out with a few more or fewer triangles depending on the CAD cache, the same solid to a millionth) |
| ruff's error checks on the CAD program | clean |

## 1.1.1 (2026-10-12)

The side-slide mount's latch becomes a lever you work by hand, and the software's messages say how to use it. Nothing
changes in what lane keeping does, on any mount. What it needs from you: nothing, if you keep a lift lever mount. The
side-slide mount is still a draft; if you print it, print it from this version's files.

### Software

- **The side-slide mount's lever in the messages.** The car setup and the drive check now say to switch the motor on
  by pulling the side-slide mount's lever out along its slot and then towards you into the notch, and to switch it
  off by pushing the lever away from you, out of the notch. The car setup's "Hands off the wheel" now reads "Hands off
  the steering wheel". Nothing else changes.
- **Version number** 1.1.1.

### Printed parts

- **The side-slide mount: a lever in place of the spring plunger.** You asked to be able to break the gear's contact
  with the steering wheel by hand, quickly, without relying on a spring. The lever turns on a 4 mm steel pin in the
  motor bracket's ear and comes out through an L-shaped slot in the mounting plate, its knob towards 4 o'clock behind
  the steering wheel.
  - To latch: pull the lever out along the slot (the motor slides out along its shaft and the gear goes onto the
    teeth), then pull it towards you into the notch at the slot's end. The spring's pull holds the lever's arm on the
    notch's floor, and the floor sets where the gear sits in the teeth.
  - To let go: push the lever away from you, out of the notch (about 0.8 N at the knob). The spring pulls the motor
    40 mm in. If the spring doesn't, push the lever in along the slot yourself: it takes 4.4 N.
  - The notch at the slot's inner end is for a broken spring. Without the spring, the motor's own weight slides it back
    out onto the teeth (at 5:20 the slide leans downwards); with the lever in that notch, the weight holds it in.
  - The slide stays 40 mm. The gear is clear of the teeth after 12.5 mm, and the power switch lets go within the first
    1.6 mm, as before.

  New printed part: `side-lever` (13 g if solid, printed flat, no supports). Changed: `side-motor-bracket` (its ear is
  now a fork that holds the lever's pin) and `side-mounting-plate-draft` (the L-shaped slot with its two notches, where
  the plunger's hole was). Bought: a 4 mm x 24 mm steel dowel pin (ISO 8734), or 4 mm steel rod cut to 24 mm, in place
  of the KIPP spring plunger and its nut.

  Checked in CAD, all passing: the lever slides in its slot and swings into either notch touching nothing; latched,
  the plate stops the motor sliding in, and parked it stops it sliding out; pulled out, the ear meets its stop 0.2 mm
  past the latched place; and every check from 1.1.0 (the gear in the teeth, the slide, the steering wheel turned
  through and past the teeth, your fingers' room, the power switch). Your pull to bring the motor out is 8.3 N; the
  spring has 7.3 N left over to pull it in. Margins: the lever holding the motor in its notch 8.78, your pull and push
  every time (20 N at the knob) 2.78, a hard yank (100 N at the knob, an estimate on the high side) 1.67.

  Two new margins for the lever staying in its notch. Here gravity leans towards the dash, because the steering column
  slopes down towards it, so the lever's own weight tends to swing it out of a notch, towards its slot: 0.03 N at the
  knob standing still, 0.10 N braking hard (0.8 times gravity). Latched, the notch grips it with 0.92 N while braking
  hard, a margin of 9.44; parked with no spring, 2.19. A jolt of over 2 times gravity along the slide can lift the arm
  off the notch's floor for a moment; if the lever ever works its way out, the spring pulls the motor in and the power
  goes off.
- The side-slide report's opening and questions describe the lever. The question about the knob asks whether you can
  reach it where it is, and whether towards you to latch and away to let go is the way round you want. Its filament
  weights use the same PETG density as the other mounts (1.28 g/cm3; it had 1.27).
- The README and the build guide say 1.1.1, and the README describes the lever. Everything else in the package is
  unchanged, checked byte for byte against 1.1.0: the other mounts' files, and the side-slide mount's gear, spool,
  board cover, strip clamp and teeth.

### Test results (2026-10-12, version 1.1.1)

| Suite | Result |
|---|---|
| sunnypilot: setup tools (34), phone page and prompter (5), settings (4), the lift lever as one system (11), gyro steering and steering learner (9), the two chimes (10), the comma device's own speed (6) | 79 passed |
| opendbc | unchanged: v1.1.1 uses the same opendbc commit as v1.1.0 (`b016274d`); its tests are in the 1.1.0 results |
| ruff on the changed code | clean |
| the version branch (`push_fork.sh … --dry-run`) | v1.1.1 points `opendbc_repo` at opendbc commit `b016274d` |
| the side-slide mount, built from the CAD files | its eight parts each one closed solid that fits a 220 mm bed; every check passing |
| every file in the package against 1.1.0 | changed only where this section says |
| ruff's error checks on the CAD program | clean |

## 1.1.0 (2026-10-11)

Adds a fifth mount, the side-slide mount, as a draft, and the software it needs. Nothing changes on the other mounts:
lane keeping works as in 1.0.0, and a car setup saved by 1.0.0 still holds (it reads as a motor gear with a roller).
What it needs from you: nothing, if you keep a lift lever mount. The side-slide mount needs its own parts, and part 1
of the car setup run again with it fitted.

### Software

- **A motor gear without a roller.** On the lift lever mounts the motor gear has a smooth roller that rides on a band
  beside the teeth; past the last tooth the band keeps turning the motor with the steering wheel for another 6.5°.
  The side-slide mount's gear has no roller: its slide sets how deep it sits in the teeth, so the motor turns with the
  steering wheel over the teeth alone (on its short back teeth, 30.4° end to end, against 42.2° with a roller). The
  config gets `roll_past_deg`, the rolling band's share of that turn on each side: 6.5 with a roller, 0 without. A
  config saved before has none and reads as 6.5. The teeth's full-push reach, which the curve chime uses, is half the
  turn less that: 15.2° each way on the side-slide mount's teeth (14.6° on the short teeth with a roller).
- **The car setup tells the two apart.** You answer 15 for the side-slide mount's teeth, as for the other short teeth.
  Part 1's two wheel turns show how far the motor turned with the steering wheel; for 15 it takes the nearer of 42.2°
  (a gear with a roller) and 30.4° (without one), checks the gearing against it and saves it with the matching
  `roll_past_deg`. Its report's teeth line ends "the motor gear without a roller" when it found none. A turn that
  matches neither fails as before and says to check which teeth are on.
- **"Switch the motor on."** The car setup's and drive check's messages say "switch the motor on" and give both ways:
  pull the lift lever down until it clicks, or on the side-slide mount pull the motor out along its shaft until the
  latch clicks. On the side-slide mount the latch takes the lift lever's place: latched out, the motor has power and
  lane keeping turns on about 2 seconds later; pull the latch's knob and it turns off. The grip test's slip message
  adds what to check on the side-slide mount: that the back of the steering wheel doesn't move away from the motor as
  the wheel turns.
- **Version number** 1.1.0.

### Printed parts

- **A fifth mount, the side-slide mount, as a draft** (`hardware/stl/side-slide-mount/`; `hardware/cad/sideparts.py`,
  `sideassembly.py` and `sidebuild.py`; its own report, `hardware/report/side_slide_report.txt`, and three pictures,
  `side-slide-drawing.png`, `side-slide-3d.png` and `side-slide-parts.png`). The motor sits behind the steering wheel
  at 5:20, its shaft pointing out at the wheel and its 16-tooth gear on teeth on the back of the round part you hold
  (the back-teeth mount's short set, made for 5:20: 14 teeth of the 166-tooth face gear, 15.2° each way). The motor
  slides along its own shaft on an MGN12 rail. A constant-force spring pulls it 40 mm in, towards the middle of the
  steering wheel, out of the teeth (it is clear of them after 12.5 mm) and out of the way of your hands. You pull it
  back out along the shaft until a spring plunger's pin drops into the bracket's ear: that is the latch. Pull the
  plunger's knob and the spring takes it in again. The power switch is pressed only with the motor latched out, and
  lets go within the first 1.6 mm of the slide. Nothing springs at the teeth: the plate sets how deep the gear sits in
  them, so there is no roller and no lift lever. The gear's tooth ends and the steering wheel teeth's inner ends are
  pointed (40°), so the gear finds its place as it comes out along its shaft. Past the last tooth the gear turns
  freely and the software stops the motor, as on the other mounts; when the wheel comes back, the two lowered end
  teeth meet the gear first and turn it into step.

  Printed: `side-motor-bracket`, `side-mounting-plate-draft`, `side-gear`, `side-spool`, `side-board-cover`,
  `side-strip-clamp` and `side-steering-wheel-teeth`, in light grey PETG like the rest, none needing supports. Bought:
  a HIWIN MGN12H block on a 100 mm rail, a KIPP K0338.11105 spring plunger with an M10 x 1 thin nut, a Lee Spring
  LCF 040 08 050S constant-force spring (11.7 N), the Omron roller switch already in the parts list, and screws (the
  report lists every one).

  Checked in CAD against our own parts, the bought parts' catalogue sizes and your steering wheel (372 mm across,
  35.4 mm thick), and all passing: the gear in the teeth through their whole arc with no overlap (free play 0.17° at
  the steering wheel); the gear sliding in and out along the teeth's gaps with no overlap; the steering wheel turned
  every 0.5° through and past the teeth with nothing touching; slid in, clear of the teeth, the steering wheel and
  your fingers' room; both stops; the power switch along the slide. Margins: the gear's teeth 2.17, the gear on
  its shaft 1.51, the latch 14.57, the rail's block 22.21, the bracket's flange 5.03; the bumper that stops it slid in
  gets a proof test (let it go 20 times; nothing may crack). The spring pulls it in with 7.4 N left over after its
  weight and the block's drag. Your pull to bring it out is about 8.4 N, 19 N at most while the pin rides up its
  ramp. Slid in, it stays in through a jolt of up to about 3 times gravity along the slide.

  Why it is a draft: the plate isn't fixed to the car yet, and the car round it is only an estimate from photos,
  which puts the column cover and the cover on the back of the steering wheel where the motor slides in. You said
  there is room. Four questions go to you: the room inside the steering wheel, what the plate can bolt to, whether
  you can reach the latch's knob, and how much the back of the steering wheel moves towards or away from the dash as
  it turns. The build guide doesn't have this mount yet.
- The other mounts' files are unchanged (checked: every STL byte for byte).

### Test results (2026-10-11, version 1.1.0)

| Suite | Result |
|---|---|
| opendbc car tests | 901 run: 557 passed, 344 skipped. The car port's own tests are 81 (one new: the full-push reach with and without a roller, and the config's new limits) |
| the safety mode's tests (its code is unchanged) | 114 run: 101 passed, 13 skipped |
| sunnypilot: setup tools (34, one new: the short teeth with and without a roller), phone page and prompter (5), settings (4), the lift lever as one system (11), gyro steering and steering learner (9), the two chimes (10), the comma device's own speed (6) | 79 passed |
| ruff on the changed code in both repos | clean |
| the version branches (`push_fork.sh … --dry-run`) | v1.1.0 points `opendbc_repo` at opendbc commit `b016274d`; v1.0.0 still at `1be0dc77`, as it was made (each version's commits are now tagged, so an older version goes up unchanged) |
| the side-slide mount, built from the CAD files | its seven parts each one closed solid that fits a 220 mm bed; every check above passing; rebuilt after this version's last code changes, the same files and the same report |
| the other mounts, rebuilt from the CAD files | all their checks pass; their 50 STL files the same byte for byte; their report the same but one wording (the right-side mount's screw "behind the front face of the grip"), updated in `parts_report.txt` |
| ruff's error checks on the CAD program | clean |

## 1.0.0 (2026-10-09)

The first version to install. Everything this file describes is in it. The test builds before it (2026-10-06 to
2026-10-09, under "Before 1.0.0" at the end) were never installed. Compared with the last of them:

### Software

- **Stand-alone: the comma device isn't connected to the car at all** (the default; `"car_network": false` in the
  config). Nothing goes into the OBD port and nothing in the car is spliced: the comma device and the motor are
  powered from the 12 V socket plug, and the only network the comma device talks on is the motor's. What the car
  used to tell it now comes from elsewhere or isn't known:
  - **Speed**: the comma device's own estimate of its motion (sunnypilot's `deviceMotion`: the camera's view of the
    road going by, with its motion sensors), 20 times a second. Part 2 of the car setup compares it with GPS speed
    over the drive and saves the factor between them (`device_speed_scale`, 0.85 to 1.15); lane keeping uses the
    device's speed times that factor. While driving, GPS keeps checking it: if the two disagree by more than 2 m/s
    (or 15%) for 3 s, the motor stops pushing until they agree again for 3 s. Without a GPS fix (a tunnel, a garage)
    the device's own speed is used alone. Until the device's estimate is ready after the car starts, the motor
    doesn't push. openpilot's card hands the speed to the car port before every update
    (`openpilot/sunnypilot/selfdrive/car/hondastepper_speed.py`).
  - **Turn signals and brake**: not known, so they no longer pause lane keeping. In their place, the motor lets go
    when you turn the steering wheel against it: the motor pushing at least 60% of lane keeping's most one way while
    the wheel turns the other way faster than 20°/s on average over 0.2 s. It stays off, with no alert, until the
    wheel has turned slower than 5°/s on average for 1.5 s, then lane keeping takes over again with its torque
    ramping up from zero. So for a lane change you steer through the push (3.85 Nm at most) and it lets go; or lift
    the lever. The numbers are first guesses: how fast the wheel unwinds by itself out of a curve against the motor
    sets how low they can go, and that is only found by driving.
  - **Gear, doors and seat belt**: not known; they read as drive, closed and fastened, so their alerts never come.
  - **On and off**: unchanged, the lift lever. The comma device's ignition comes from the socket plug, so it runs
    with the key on and switches off with the key (comma's harness notes: without comma power the device "will only
    be powered while driving").
  - **The panda** (`honda_stepper` with its new stand-alone setting, param 1) checks only the motor's status and
    reads nothing from the car's network; the torque limits and the lift lever logic are the same. With the lever
    up, no message at all arrives, so the panda notices through its once-a-second check for missing messages
    (within 2 s; the motor has no power by then anyway), and openpilot within 0.1 s from its own CAN packets.
  - **Car setup**: part 1 is only the motor (which teeth, the two wheel turns, the push you watch, the grip test),
    about 5 minutes; no pedals, signals, shifter or door, and no manual-or-automatic question. Part 2 checks the
    comma device's own speed against GPS and the motor's direction against the GPS course.
  - **Steering** works from the gyro, as before when the car's own steering angle isn't found; the steering angle
    search runs only connected to the car.

  The connected setup is still there: `"car_network": true` in `/data/hondastepper/config.json`, the OBD splitter
  wiring, and part 1 run again. Everything below about the car's signals applies to it.
- **Motor: STEPPERONLINE 17HS16-2004S1** (45 Ncm, 2 A) in place of the 59 Ncm 17HS19-2004S1. European and
  Australian rules for lane keeping say a driver must be able to overpower it with 50 N at the steering wheel's
  edge: 9.2 Nm on this steering wheel. If the motor's controller board failed at full power (3.3 A), the 59 Ncm
  motor could push back with about 8 Nm, a factor of only 1.1; the 45 Ncm motor makes it 1.45. The car port's
  torque constant changed to match (0.159 Nm per amp), so the motor's firmware is asked for 1.33 times the torque
  wanted at the steering wheel. The panda's hard limit is 4.4 Nm at the steering wheel (47 units; it was 36 units
  with the old motor).
- **Lane keeping's most push: 3.85 Nm** at the steering wheel (41 firmware units, was 43 and 4.03 Nm). The grip test
  pushes with the most the motor's board gives, 5.44 Nm, which is now 1.41 times lane keeping's most: passing it proves
  on your car that the motor gear stays in the teeth with the 1.4 factor the build aims at. The starting estimate of
  how much the push turns the car scales with it (1.43 m/s² at the full push, was 1.5), so it is the same per Nm.
- **Grip test** at the end of the car setup's part 1. You start it, and within 3 seconds take hold of the steering
  wheel; the motor then pushes as hard as its controller board can (about 5.4 Nm at the steering wheel, 1.41 times
  what lane keeping ever uses), about 2 seconds each way. If the motor gear slips over the steering wheel teeth, part 1
  fails and says what to do: check the spring, the lever and the teeth, then add an M5 washer under the spring. If the
  steering wheel turns in your hands, or the teeth slide on it, the push stops after 3° and it asks once more. Lane
  keeping stays off until part 1 passes, grip test included. The push that finds the motor's direction is now set as
  3 Nm at the steering wheel, whatever the motor.
- **Free spin caught at any motor speed.** The motor's rate now comes from its angle between two status messages.
  The status's own speed field is 8 bits and wraps above 2 turns a second, so a motor spinning faster than about
  2.2 turns a second read as turning slowly the other way, and the gear running off the teeth could have gone
  unnoticed until the teeth came back under the spinning gear. How fast the motor spins free isn't measured; the
  check no longer depends on it.
- **The settings this car needs are made every time sunnypilot starts**, before anything else runs
  (`openpilot/sunnypilot/tools/hondastepper/settings.py`, called from the manager): the vehicle (Honda Accord
  2008-12), MADS on with Toggle with Main Cruise, Steering Mode on Brake Pedal: Pause, Neural Network Lateral Control
  off, Auto Lane Change by Blinker Off, and Pause Lateral Control with Blinker at every speed (Minimum Speed 255).
  Only these settings are touched. A change in a menu can't switch off what the lift lever relies on, and the
  install needs no laptop. Software updates are no longer switched off: the device follows its own version's
  branch, which never changes.
- **Install from GitHub** with comma's installer (`installer.comma.ai/YOURNAME/v1.0.0`), in place of
  `install_hondastepper.sh`. Each version is a branch in your copies of sunnypilot (renamed openpilot, the name
  comma's installer looks for) and opendbc; its last change points sunnypilot's opendbc at your copy.
  `launch_chffrplus.sh` now downloads git's large files before building if any are still placeholders, so a build
  from a GitHub copy doesn't fail on them.
- **Car setup from a phone** (`openpilot/sunnypilot/tools/hondastepper/phone.py`). The comma device serves a page on
  its own hotspot, at 192.168.43.1:8090: join the hotspot from the phone, open the page, and press **Start part 1** or
  **Start part 2**. The page runs the same two setup tools and turns their questions into buttons. It also shows the
  software version, which parts have passed, and the steering strength sunnypilot has learned (L.A.F.), which a
  comma four's own screen doesn't show. It answers only requests that arrive over the hotspot, takes button presses
  only from its own page, and starts a part only while the car stands still. `launch_chffrplus.sh` starts it outside
  sunnypilot's manager, because part 1 stops the manager, and starts it again if it ever stops. The laptop route
  (SSH, `accord_setup.sh car` and `drive`) still works the same.
- **Two chimes for the teeth** (`openpilot/sunnypilot/selfdrive/car/hondastepper_alerts.py`). "Steer: the curve
  ahead is past the teeth" when the path the driving model plans for the next 3.5 s needs more steering wheel than
  the fitted teeth reach (within 2° of the last tooth), worked out with the vehicle model the controls use and the
  car's steer ratio, an estimate the chime refines from the motor's own angle while the gear is on the teeth; it
  shows for 3 s, then stays quiet for 10. "Past the teeth: steer yourself" when the gear runs off the teeth while
  lane keeping pushes, which was silent before. Both are sunnypilot events with the prompt sound. The teeth's reach
  comes from the car setup's config (`full_push_reach_deg`: half the tracked arc less the band's 6.5° flat).
- **The car setup looks for the car's own steering angle.** Part 1 now records the car's data while you turn the
  steering wheel each way (press **Start, then turn**; it carries on by itself once the wheel has been still for a
  moment, or after 25 s), and searches every message from the car for a number that follows the motor's angle
  during the turns: both ways, either byte order, signed or not. It keeps one only if it comes at least 50 times a
  second, is 0.5° per step or finer, sits still at rest (2 steps or less) and fits both turns the same way. Whether
  this car puts its steering angle on the network the comma device reads isn't known; if it doesn't, the report says
  "not on the car's network (the motor's own angle is used; nothing to do)" and nothing changes. If one is found,
  part 2 checks it against which way the car turned (the GPS course) and drops it if they disagree. Kept, the car
  port reports it as the steering wheel angle instead of the motor's count: the steering controller measures the
  car's turning from it rather than the gyro, the steering learner learns the steer ratio and angle offset as on any
  other car, the 2 m/s lowest steering speed goes away, and the curve chime keeps its straight-ahead reference
  with the lever up or the gear off the teeth.
- **The car setup knows the back teeth.** Its which-teeth question takes 45 for the back-teeth mount's long set
  (button **Long back teeth (45)**); 15 covers the short teeth, the column mounts' ring teeth and the short back
  teeth. Part 1 now also saves the fitted set's gearing (`mechanical_ratio`: 166 / 16 for the long back teeth,
  197 / 19 for the rest), so the torque sent to the motor follows the gears on the wheel. The short back teeth reach
  15.2° against the short teeth's 14.6° and are geared 0.07% differently: taken as 15, the curve chime sounds 0.6°
  early with them, and the torque is 0.07% off.
- **Version number** 1.0.0 (`openpilot/sunnypilot/tools/hondastepper/__init__.py`), shown when the car setup starts
  and in its report.

### Printed parts and wiring

Not software; listed here so the files' changes are clear.

- **No grease anywhere. Spring: Lee Spring LC 055F 08 S** (44.45 mm long, 3.50 N/mm, 10.67 mm outside). It reaches
  down through an 11.5 mm hole in the motor carrier and rests on the top of the motor; the hinge block is 6.9 mm
  thicker for its 12.9 mm deep pocket. It presses with about 39 N with the motor gear on the teeth and 58 N with the
  lever up (its most is 88.9 N, a factor of 1.53). With the teeth dry, that keeps the motor gear in the teeth with 1.68
  times the push lane keeping can use (1.50 with the weakest spring Lee Spring may ship).
- **Longer lift lever handle** (47 mm from its bolt to its end, was 39), so the stronger spring doesn't make it
  harder to flip: about 1 kg at the end of the handle, up to 1.5 kg with its rounded end rubbing dry.
- **Parts for the 40 mm motor**: the motor carrier's side walls stop short of the motor's back, clear of the board's
  plugs, and the motor gear's hole follows the shorter shaft's flat.
- **Relay**: the lift lever switch now works a 12 V car relay, and the relay carries the motor's power. When power
  comes on, the board's capacitors take about 70 A for a moment (calculated); the switch alone is rated for 10 A at
  switch-on, a relay like the TE V23234 for 120 A.
- **Wiring, stand-alone (the default): the 12 V socket plug powers everything.** The harness's two red wires (its
  12 V in) join the socket plug's + lead with the brown ignition wires, and its two black wires join the − lead; no
  OBD splitter, no comma power, no OBD plug, and the orange and green CAN0 pair is taped off. The comma device then
  runs with the key on only. The socket plug's 5 A fuse now feeds the comma device too: the margins table's
  electrical rows count it at 1.5 A, an estimate (comma doesn't publish the device's draw). The data wires' two
  lever nuts are 5-way, so a second 120 ohm resistor fits in them if the board's own broke off with its wing.
- **Wiring connected to the car (car_network), without soldering, a fuse box or a ground bolt.** The comma device is powered by the comma power plug in
  the harness kit, in the OBD port on a splitter (comma's harness box diagram: comma power brings 12 V and the OBD
  port's data pair into the box). The car's data reaches the harness through a two-wire OBD plug with screw terminals
  on the splitter's other branch. The motor's relay and the harness's ignition wires are fed by a 12 V socket plug
  with a 5 A fuse in the car's accessory socket, live only with the key on (the owner's manual: ACCESSORY or ON,
  120 W); the motor's ground returns through it. Every join is a lever-nut connector, the 120 ohm resistor's legs
  included; the lift lever switch is the push-on terminal type (Omron SS-5GL2-F). Seven multimeter checks in place
  of ten, four of them on a table. The margins table's electrical rows follow (the socket plug's fuse, the socket's
  10 A rating).
- **Light grey PETG** in place of ASA, for printers without an enclosure. The parts report's click and weight
  figures are now worked out for PETG.
- **Margins**: the parts report has a new table with a factor for every way the build can fail, what it can take
  divided by the worst it should see. The aim is 1.5 and nothing may be under 1.4 (NASA-STD-5001B, 14 CFR 25.303);
  the CAD program ends with an error if a design falls under 1.4. Two things depend on you: a windshield sunshade
  when parked in the sun (or the dash clamp printed in ASA), and the grip test.
- Usability: the guide now says to turn the zip ties' heads to the dash side, away from your hands; to lift the lever
  when you park; and to check that you can see the road ahead past the mount.
- **A second mount, the column mount** (`hardware/stl/column-mount/`, `hardware/cad/columnparts.py` and
  `columnassembly.py`; the guide's "The column mount"). The motor hangs under the steering wheel, behind it, on an arm
  up to a two-piece clamp round the steering column covers; its gear runs inside a ring of teeth that faces the hub,
  on a skirt standing back from the bottom of the wheel between its two lower spokes. The top of the wheel and the
  gauges stay clear, the motor sits behind the grip, and the mount moves with the wheel when it is tilted or pulled
  out, so the mesh never changes with the wheel's setting. New parts: `ring-teeth` (the short set's 16 teeth, cut as
  an internal gear from the same 197-tooth circle, so the gear ratio, the tracked arc and the car setup are the same;
  zip-tied like the steering wheel teeth, through slots every 4.5 degrees along the piece; prints front face down with no supports and fits a 220 mm bed in one
  piece), `fit-test-ring-teeth`, `column-clamp-upper` and `column-clamp-lower` (V-shaped saddles with rubber strips,
  on four M6 threaded rods; the lower one carries the same arm joint the dash clamp has; slots take covers 95 to 140
  mm wide, the rods 70 to 125 tall), `hinge-block-column` (the hinge block with its arm slot centred on an arm
  20 degrees from the column instead of 62.5) and `motor-carrier-column` (the carrier with its finger guard open 64
  degrees either side of the ring instead of 60, so the guard's rounded ends clear the ring's rolling band when the
  carrier drops at the ring's ends). Shared and unchanged: the motor gear, lever bracket, lift lever, spring, arms
  and setup gauge. At the ring's ends the rolling band runs out to the skirt over 6 degrees as the steering wheel
  teeth do, and the teeth zone's root follows it, so the motor gear's teeth (which stand 2 mm outside its roller)
  clear the ring as the carrier drops; the clearance checks sweep that with the roller resting on the ring. The long teeth don't fit between the spokes, so this mount takes the short
  set only. The lift lever sits under the wheel, pointing at you: up to take the motor off, down to put it on. The
  CAD program checks it the same way (244 clearance checks with the lever down, up and in between, the wheel turned,
  the ring turning through its arc under the gear, and the carrier dropping along the ring's ends; the gears' mesh and free play; the arm and both joints over
  a table of clamp positions 180 to 340 mm behind the front of the grip and cover heights 70 to 110 mm; its own margins: the clamp
  not turning on the covers, 2.1; the ring's skirt, 1.9; heat, 2.3). Everything about the car in those checks is an
  estimate from photos (the covers an oval 120 x 95 mm, the hub, the spokes, the dash), so the guide asks for
  measurements before printing, and the parts adjust: the clamp's width and height, where it sits along the column
  (any place in the table), the arm's length and both its angles. The dash mount's files are unchanged (checked:
  every STL byte for byte).
- **A third mount, the right-side mount** (`hardware/stl/column-mount-right/`; `columnparts.py`, `columnassembly.py`;
  the guide's "The right-side mount"). The column mount's parts turned a quarter turn round the steering column: the
  ring teeth on the back of the wheel at 3 o'clock, the motor behind the wheel there, and the arm back to a `side-bracket`
  zip-tied to the right-hand side of the column covers on two rubber strips (a flat plate with twelve zip tie slots,
  the arm's fork, and a bar), which a `screw-tab` (a bar in three lengths, 100, 160 and 220 mm, each sliding 60 mm on
  two M5 bolts, with an end plate whose vertical slot takes the dash's own screw at the driver's right) holds from
  turning round the covers. Both of your sketch's connection points, then: the screw and the column. The ring teeth
  (`ring-teeth-right`) are the column mount's ring with a shallow channel (its walls reach 8 mm in from the middle of
  the grip instead of wrapping it to its middle) so it can sit over the place where the right spoke meets the grip, and
  zip tie slots every 4.5 degrees all along it (12), to tie wherever the spoke leaves room; the column mount's ring
  now has the same slots. The lift lever points at you from behind the wheel and swings sideways: the handle moves
  away from the wheel to put the motor on and in towards the hub to take it off (the lift direction is fixed by the
  gear having to come off the ring towards the hub, so "pull to turn on" would need different lever parts). The ring's
  channel and the handle take the right hand's 3 o'clock spot on the grip: the guide says to hold at 2 and 4. The
  bracket's place along the column follows the screw's depth (its back face sits level with the screw tab's plate on
  the dash), the tab's length and the plate's height follow the screw's position, and the arm follows from the
  bracket's bolt to the hinge block's: three measurements make the fit (`--screw-right`, `--screw-down`,
  `--screw-behind`; `--ring-at` turns the whole mount above 3 o'clock, `--tab-length` makes another tab, and
  `--cover-front-width` is the covers' width near the wheel, where the lifted handle swings in beside them: under
  about 118 mm clears it). The CAD program checks it as the column mount (the clearance checks now also against the
  wiper stalk, the key cylinder and the dash at the screw, all estimates from photos; the mount's own bolts; a table
  of screw positions 0 to 150 mm right of the wheel's edge and 240 to 340 behind the front of the grip naming the arm and tab;
  a table of cover widths against the lifted handle; its own margins: the dash's screw, 8.7; the tab's bending, 30;
  the bracket sliding on the covers, 4.3; heat, 2.3). The steering column covers are now drawn narrower at their
  front (100 mm, widening to 120 by 200 mm back: an estimate from the photos) for both column mounts. Shared and
  unchanged: the column mount's hinge block, carrier and fit test; the dash mount's motor gear, lever bracket, lift
  lever, spring, arms and setup gauge. The dash mount's files and the column mount's other files are unchanged (checked
  byte for byte); the column mount's `ring-teeth.stl` now has the slots every 4.5 degrees.
- **A fourth mount, the back-teeth mount** (`hardware/stl/back-teeth-mount/`; `hardware/cad/faceparts.py` and
  `faceassembly.py`; the guide's "The back-teeth mount"). Your hot dog bun: a channel that wraps the back half of the
  steering wheel's grip, open towards you, with teeth on its back facing the dash. The teeth are a face gear (166 teeth
  on a full circle, 2 mm teeth like the others, their spaces cut by rolling the motor gear itself along them), and the
  motor sits behind the wheel at 3 o'clock, just outside the grip, its shaft pointing at the steering column, its
  16-tooth `back-motor-gear` meshing the teeth from behind (166 / 16 = 10.375, 0.07% from the other mounts' 197 / 19).
  Two sets, like the steering wheel teeth: `back-teeth-15` (14 teeth reaching 15.2 degrees each way, from about 2 to 4
  o'clock, one piece) for getting used to it and for the highway, and `back-teeth-45` (42 teeth, 45.5 degrees each
  way, from 1 to 5 o'clock, two pieces glued end to end on four filament dowels, or one piece for 330 mm beds) for
  slower roads only: a wrong push to their end at highway speed could ask for more grip than the tires have. Both have
  the rolling band beside the teeth and the same ramps at their ends; over the right spoke's junction with the grip
  (read off your photo as 15 to 55 degrees below 3 o'clock) the channel keeps only its back and outer wall, and zip tie
  slots run every 4.5 degrees where the spoke leaves room. An arm (`back-arm-135`, `-165` and `-195`, each sliding 15
  mm either way) runs from a joint under the `back-hinge-block` (the hinge block with its arm's ears moved
  underneath) down to the `column-plate`, which sits under the steering column's lower cover on two rubber strips,
  held by the cover's own screws (put in 10 mm longer ones) through two long slots; so the mount moves with the wheel
  when it is tilted or pulled out, and nothing goes on top of the wheel or the dash. `back-motor-carrier` is the
  carrier with its finger guard open 72 degrees either side and its plate's lower edge cut back; `back-lift-lever` is
  the lift lever with a paddle under its handle's end, so you reach it from inside the grip at 3 o'clock: push it
  towards the dash to flip the lever up, pull it back until it clicks to put the motor on. The spring sits on an M5
  washer from the start (the teeth at 166 mm from the column's middle push the gears apart harder than at 197), and
  the back motor gear takes an M3 x 10 set screw (an M3 x 12 would stand 0.5 mm out into a tooth gap, where the back
  teeth's tips come in). Two fit tests: a piece of the teeth, and the piece over the spoke's junction. Shared and
  unchanged: the lever bracket, spring and setup gauge. The CAD program checks it as the other mounts: 564 clearance
  checks (282 with the long back teeth, 282 with the short: lever down, up and swept, the wheel turned through the
  teeth and past them, the carrier dropping along the ramps), the gears' mesh through each
  set's whole arc every degree (no overlap, free play 0.17 degrees at the wheel), the arm and both joints for the
  cover's underside 40 to 70 mm below the column's middle, its bolts, and its own margins: the motor gear held in the
  back teeth 1.52 with the teeth dry (1.36 with the weakest spring Lee Spring may ship; the grip test is the check),
  the spring with its washer squashed with the lever up 1.44, the motor gear's teeth 2.74, the gear on its shaft 1.55,
  the teeth round the grip 9.1, the plate on the cover's screws 1.59 if two of them fall in its outer slot as your
  photos suggest (1.03 if both fall in the inner one; the proof pulls are the check), and heat 2.3. Everything about
  the car is an estimate from photos (the cover's underside, its screws, the tilt lever, the spoke's junction, the
  wiper stalk, the key cylinder): `--cover-bottom`, `--spoke-from` and `--spoke-to` take your measurements, and the
  guide asks for the rest. The other mounts' files are unchanged (checked byte for byte).
- The right-side mount's estimate of where the right spoke meets the grip is now 15 to 55 degrees below 3 o'clock
  (read off a straight-on photo), shared with the back-teeth mount, in place of 2 to 25. None of the right-side
  mount's parts depended on it.
- Files changed: `motor-carrier.stl`, `hinge-block.stl`, `lever-bracket.stl`, `lift-lever.stl`, `motor-gear.stl`;
  new: everything in `hardware/stl/column-mount/`, `hardware/stl/column-mount-right/` and
  `hardware/stl/back-teeth-mount/`.

## Words used here

| Word | What it is |
|---|---|
| comma device | the comma 3X or comma four on the windshield. The same code runs on both |
| sunnypilot | the driving software on the comma device, built on comma's openpilot |
| opendbc | the part of sunnypilot that knows each car: where its signals are and how to command it |
| panda | the chip inside the comma device that connects it to the car's wiring. It checks every command before it goes out; its rules for a car are its "safety mode". The build guide calls it the safety chip |
| car's network (F-CAN) | the wires the car's own computers use to talk to each other. The comma device never sends a message on it (its chip only acknowledges messages, as every device on that network does) |
| motor's network | a separate pair of wires between the comma device and the motor's controller board. Nothing else is on it |
| stand-alone | the default setup: the comma device isn't connected to the car's network at all, only to the motor's; config `"car_network": false` |
| connected to the car, car_network | the other setup: the comma device also reads the car's network through the OBD port; config `"car_network": true` |
| signal map | where in the car's messages each signal lives (speed, brake, turn signals and so on). The code calls the file a DBC |
| MADS | a sunnypilot setting: lane keeping on its own, without the car's cruise control. With "Toggle with Main Cruise" on, a car's main cruise switch turns it on and off; on this car that switch is the lift lever |
| dashcam only | sunnypilot records but doesn't steer |
| soft-off | the motor's firmware ramping its torque to zero by itself, then waiting until it is told Off |
| free spin | the motor gear off the steering wheel teeth, so the motor spins freely when it pushes |
| gyro | the turn-rate sensor in the comma device |
| firmware unit | how the motor command counts torque: 0.125 Nm at the gearing the motor's firmware assumes. With the 45 Ncm motor and the printed gears, one unit is 0.094 Nm at the steering wheel |
| change file, patch | a file listing changes to code; git applies it |

## What the changes apply to

| Code | Version the changes are made on | Change file |
|---|---|---|
| sunnypilot | `a5f44653` (master, 2026-10-06) | `software/sunnypilot-hondastepper.patch` |
| opendbc (sunnypilot's copy, inside sunnypilot as `opendbc_repo`) | `f95f996f` (the version that sunnypilot commit uses) | `software/opendbc-hondastepper.patch` |
| panda | `74a0adce`, unchanged | none. Its firmware picks up the new safety mode from opendbc when it is built |

The car is listed in sunnypilot as **Honda Accord 2008-12** ("2.4L sedan with the add-on steering motor"). Its
internal name is `HONDA_ACCORD_8G_STEPPER` and the code calls it `hondastepper`.

## What the driver sees

- Lane keeping stays off (dashcam only) until both car setup checks have passed: part 1 while parked, then part 2
  after a drive with the lift lever down. Either from the phone page (**Start part 1**, **Start part 2**) or over SSH
  (`accord_setup.sh car`, `accord_setup.sh drive`).
- **The lift lever is the only switch.** Pull it down until it clicks: the motor powers up, and lane keeping turns
  on about 2 seconds later with the engage sound. Lift it: the motor's power is cut, and lane keeping turns off with
  the disengage sound. If the lever is already down when you start the car, lane keeping turns on by itself once
  sunnypilot is running. The cruise control buttons and the car's own cruise control play no part. There is no gas
  or brake control: your speed stays with you or the car's own cruise control.
- **Speed** (stand-alone, the default): the comma device's own, scaled to GPS by part 2 of the car setup. If GPS and
  the device disagree for 3 s, the motor stops pushing ("steering temporarily unavailable") until they agree again.
  Right after the car starts the device's estimate isn't ready, and the motor doesn't push until it is.
- **Turning the wheel against the motor** (stand-alone): the motor lets go within about 0.2 s, without an alert, and
  takes over again once you have held the wheel still (turning less than 5°/s) for 1.5 s. Stand-alone there is no
  turn signal or brake pause: change lanes by steering through the push, or lift the lever.
- **Turn signal on** (connected to the car): the motor stops pushing until the signal goes off, so you change lanes
  and turn by hand. The software sets this up every time it starts (sunnypilot's "Pause Lateral Control with
  Blinker", at every speed).
- Below about 4.5 mph (2 m/s) the motor stops pushing. Nothing shows on the screen for this.
- **Turning the steering wheel past the end of the steering wheel teeth** while the motor pushes: the motor gear
  comes off the teeth and spins. (For about 8° past the last tooth the gear's smooth roller still rides on the
  rolling band: there the motor spins once it pushes harder than the roller's grip, about 2 Nm by estimate, and a
  weaker push still turns the steering wheel.) The motor is switched off within 0.1 s, with a chime, "Past the
  teeth: steer yourself"; sunnypilot otherwise treats it like you steering. It stays off until the steering wheel
  turns it again (its gear is back on the teeth), then 1 second more. With no sign of the teeth for 10 seconds, lane
  keeping tries again.
- **A curve ahead that the teeth can't cover**: a chime and "Steer: the curve ahead is past the teeth" a few seconds
  before it, from the planned path and the car's estimated steer ratio. It can come early on a curve the motor could
  have handled; it shows for 3 s and then stays quiet for 10.
- **Brake pedal pressed** (connected to the car): the motor stops pushing until you let go (the software sets "Steering Mode on Brake
  Pedal" to Pause every time it starts).
- **The motor losing power for a moment** (a loose plug, a worn relay or switch) makes it restart: lane keeping
  turns off with the disengage sound and back on about 2 seconds after the motor runs again.
- Most torque at the steering wheel is about 3.85 Nm, which one hand easily overpowers. The panda enforces 4.4 Nm, and
  limits how fast torque can rise and how far it may run ahead of the torque the motor reports. The motor has no
  torque sensor: what it reports is the torque its firmware is putting out.

## opendbc changes

### New: the car port (`opendbc/car/hondastepper/`)

- **`config.json`** is the one place that says where the car keeps each signal on its network and how the motor is
  set up: its direction, the firmware's gearing, the printed gearing, the motor's torque constant (the 45 Ncm,
  2 A motor: 0.159 Nm per amp), and how far the motor follows the steering wheel (71.5° with the long steering wheel
  teeth; the car setup saves 42.2° when the short ones are on). The default map is comma's map for other 2008-era
  Hondas, as a starting guess. The car setup tool checks it on your car and saves the checked copy to
  `/data/hondastepper/config.json` on the device. Software updates leave that copy alone. The motor values assume
  the motor's firmware runs with its stock settings (gearbox 10.36, a 39 Ncm motor at 1.3 A); a firmware built with
  other settings changes the real torque behind every limit.
- **`config.py`** checks a config, and from it writes two generated files that must always match it: the signal map
  `opendbc/dbc/hondastepper_fcan.dbc` and the panda header `opendbc/safety/modes/honda_stepper_fcan.h`. `--check`
  reports stale files and `--write` rewrites them. It refuses a config that puts speed or brake in a message that
  comes less than 10 times a second, because the panda refuses to check slower messages. A saved config that can't
  be read or used is set aside: the default is used instead, and lane keeping stays off until the setup runs again.
  The cruise MAIN button and the car's cruise state are not part of the map; a config that names them, or a lane
  keeping button, is refused. It also lists the sets of teeth and how far the motor follows the steering wheel on
  each (`TEETH_SETS`: 42.2° for the short ones, 71.5° for the long ones, 104.1° for the long back teeth), and each
  set's gearing (`MECHANICAL_RATIOS`: 197 / 19, or 166 / 16 for the long back teeth).
- **`values.py`**: the car's listing and specs (2010 LX 2.4 weight, 2.799 m wheelbase, steering ratio 15.3), the
  torque limits (lane keeping's most 3.85 Nm at the steering wheel, 41 firmware units; the panda's 47 units, 4.4 Nm),
  the lift lever count (200 messages, 2 s) and the free spin settings. The steering ratio is a guess: Honda lists
  13.08:1, and openpilot's values usually come out higher than the listed ones (comma uses 16.33 for the 2018
  Accord, listed at 11.82). It matters little here: above walking pace steering works from the gyro, and
  sunnypilot doesn't learn this value for this car.
- **`carstate.py`** stand-alone takes its speed from `set_device_speed` (openpilot's card calls it before every
  update), reads nothing from the car's network, and times the motor's silence against the comma device's own CAN
  packets (its panda daemon sends them 100 times a second, empty or not, stamped when sent). It reports the driver
  turning the wheel against the motor as steering pressed, and the car controller lets go meanwhile (above). An
  unusable speed is a temporary steering fault. Connected to the car (car_network), it reads the car's speed, brake,
  gas, shifter, doors and turn signals (and the cruise buttons if a
  config maps them, for button events only), and the motor's status message. It reports:
  - the lift lever as down once the motor has reported for 2 s without a gap, every message saying its controller
    runs (`cruiseState.available`, which MADS with "Toggle with Main Cruise" takes as its main switch). It starts
    counting only after the panda has passed on one of openpilot's motor commands since the motor came on: the
    panda reports every message it sends, and it passes the motor's commands only once it runs this car's safety
    mode, which counts the same messages. So lane keeping turns on just after the panda allows steering, also when
    the lever was already down as the car started (the panda switches to this car's mode only once sunnypilot has
    started up);
  - the lift lever as up after 100 ms of the car's messages without one from the motor, and at once at a message
    from a motor that restarted. Timing the silence against the car's messages means a hold-up on the comma device
    itself doesn't look like a lifted lever;
  - the driver steering (without a warning) while the motor gear is off the teeth;
  - a temporary steering fault when the motor is gone, not ready, or soft-off;
  - the steering wheel angle relative to where the motor powered up, from the motor's own sensor.

  Free spin: the motor turning faster than 100°/s (counted at the steering wheel) in the direction it pushes, for
  0.1 s. The rate is worked out from the motor's angle between two of its status messages, because the status's own
  speed field is 8 bits, 2 turns a second at most, and wraps past that: a motor spinning at 2.8 turns a second
  would read as turning the other way at 1.2 (the angle field wraps too, every 8192 degrees, and that wrap is
  undone). The motor is then held off while it coasts to a stop (up to 2 s), then until the stopped motor turns 1°
  again, which means the steering wheel turns it, so its gear is back on the teeth; then 1 s more. With no sign of
  the teeth for 10 s, lane keeping may try again.
- **`carcontroller.py`** sends the motor command every 20 ms. Torque ramps up and down within the limits, and is
  never more than 1 firmware Nm (0.75 Nm at the steering wheel) ahead of what the motor reports. It sends Off
  whenever lane keeping isn't active, the motor is soft-off (Off re-arms it), or in free spin. It sends nothing while
  the motor is gone.
- **`interface.py`** asks the panda for its stand-alone setting (param 1) and sets the `STANDALONE` flag unless the
  config says car_network. Then, unless the car setup found the car's own steering angle on the network (config signal
  `STEER_ANGLE`, flag `FCAN_STEER_ANGLE`), steering works from the comma device's gyro (`useYawRate`), with 2 m/s
  as the lowest steering speed; with one found, the car port reports that angle (`carstate.py`) and the steering
  works from it as on any other car. Lane keeping stays off (dashcam only) while either
  setup check hasn't passed, while the generated files don't match the config in use, or when a saved config had to
  be set aside (the reason goes in the device's log).
- **`discovery.py`** is the logic behind the car setup tool. Stand-alone, its `check_device_speed` compares the comma
  device's own speed with GPS over the drive: it passes when they follow each other closely (95%) and differ by a
  steady factor of 0.85 to 1.15, which it returns to save. Connected to the car: It checks the default signal map against recordings
  made while you press the brake, switch a turn signal on, and so on. When a signal isn't where the map says, it
  finds where the car keeps it. When several places match, it picks the same one every time: the message the map
  names, then the message that comes most often, then the lowest message number. Speed and brake are only taken
  from messages that come at least 10 times a second. It also:
  - checks the speed reading against the GPS speed;
  - works out the motor's direction from a slow turn of the steering wheel each way, and checks the gearing from
    how far the motor followed;
  - checks the motor's direction again from a drive: when the GPS course swings left, the steering wheel must read as
    turned left. This needs no input from you;
  - looks for the car's own steering angle in the recordings of the two wheel turns: every 16-bit field of every
    message, either byte order, signed or not, fitted against the motor's angle while the gear was on the teeth.
    It keeps a field only if the fit is close on both turns with the same slope, the message comes at least 50
    times a second, a step is 0.5° or finer, the reading wanders 2 steps or less at rest, and the low byte takes at
    least 8 different values (a field read in the wrong byte order fits too well otherwise). The left turn sets
    the sign, rest sets the zero. Several candidates: the one that follows the motor most closely wins;
  - checks a found steering angle against the drive's GPS course the same way as the motor's direction, and drops
    it from the config if it reads backwards or the drive doesn't show enough turning.
- **`steppercan.py`, `checksums.py`**: the motor's command message and its checksum, matching the StepperServoCAN
  firmware.
- **`fingerprints.py`**: the car is picked by the software every time it starts (`settings.py`, below). A config that
  lists the car's message list under "fingerprint" also lets sunnypilot recognize the car by itself; the setup tool
  doesn't write that list.
- **Tests** (`tests/`):
  - a simulated car (its messages under any signal layout) and a simulated motor on the steering wheel teeth,
    including free spin off the teeth, its lift lever and its start-up. The simulated motor never pushes harder than
    its board's 3.3 A, can be held still by the driver, and its gear slips over the teeth when pushed too hard (for
    the grip test);
  - 68 tests covering the config checks, the steering angle search (found in either byte order and sign, nothing
    else matching, too coarse or too slow rejected), the motor message format against the firmware's own tool, the torque
    limits at the steering wheel, the car state (the lift lever count, waiting for the panda, a motor starting up or
    restarting, a hold-up on the comma device), the car controller, the setup logic, and the car port running
    against the simulated motor.

### New: panda safety mode `honda_stepper` (`opendbc/safety/modes/honda_stepper.h`)

- Sends only the motor command, only to the motor's network (bus 1). It never sends anything on the car's network.
- Stand-alone (safety param bit 0, the default): its rx checks are the motor's status alone and nothing on bus 0 is
  read, so no brake, gas or speed; everything below about the motor is the same. With the lever up nothing arrives
  at all; the once-a-second check for missing messages then ends steering.
- Allows only the Off, torque and soft-off modes. Angle mode would let the motor hold a position by itself, so it is
  blocked, and the angle field must be zero.
- Torque limits: 47 firmware units at most (4.4 Nm at the steering wheel), a set rise and fall rate, and at most
  8 units (0.75 Nm at the steering wheel) above what the motor reports.
- Checks every message it reads for presence, rate, checksum and counter (the car's messages and the motor's
  status). Steering stops being allowed if one goes missing for a second.
- Lane keeping is allowed only once the motor has sent 200 status messages (2 s) without a 100 ms gap, every one
  saying its controller runs: the lift lever is down and the motor has started. It stops being allowed 100 ms after
  the motor goes quiet, or at a message from a motor that restarted. Nothing on the car's network can allow it.
- Tests: `opendbc/safety/tests/test_honda_stepper.py` (85 tests, 13 of the shared ones skipped because they test
  cruise control features this car doesn't have), connected and stand-alone: in stand-alone the car's messages
  change nothing, the motor alone meets the checks, the lever on after 2 s and off through the missing-message check,
  a restarted motor, and the modes allowed.

### Changed existing files

| File | Change |
|---|---|
| `opendbc/car/values.py` | registers the new car |
| `opendbc/car/car.capnp` | adds the `hondaStepper` safety model and the `useYawRate` steering option |
| `opendbc/can/dbc.py` | knows the checksums of the two new signal files |
| `opendbc/safety/safety.h`, `declarations.h` | register the new safety mode (number 39) |
| `opendbc/safety/tests/libsafety/*` | a test hook for the signal reader |
| `opendbc/safety/tests/common.py` | the two honda_stepper test classes (connected and stand-alone) aren't compared with each other in the wrong-safety-mode test |
| `opendbc/car/torque_data/override.toml` | starting torque values for the car (estimates, refined while driving): 1.43 m/s² at the full push |
| `opendbc/car/tests/routes.py` | lists the car as having no public test drive yet |
| `opendbc/sunnypilot/car/car_list.json` | adds the car to sunnypilot's vehicle list |

## sunnypilot changes

### New: car setup tools

- **`phone.py`**: the setup page for a phone on the comma device's hotspot (http://192.168.43.1:8090). It runs the
  two tools below with their questions as buttons, and shows the software version, which parts have passed and the
  learned steering strength (L.A.F.). Only over the hotspot, only button presses from its own page, and a part starts
  only while the car stands still. `launch_chffrplus.sh` starts it outside the manager and restarts it if it stops.
- **`prompter.py`**: how the tools talk: text in a terminal over SSH, or one JSON line per message or question for
  the phone page.
- **`accord_setup.sh`** runs the tools on the device over SSH, for a laptop instead of a phone: `accord_setup.sh car`
  (parked) and `accord_setup.sh drive` (after driving).
- **`openpilot/sunnypilot/tools/hondastepper/setup_car.py`** (parked). Stand-alone, the default, about 5 minutes
  (estimated): it skips everything about the car's data and goes straight to the motor (which teeth, the two turns,
  the push, the grip test); the steering angle search is left out. Connected to the car (about 10 minutes): stops
  sunnypilot, then asks for one simple action at a time (brake, gas, turn signals, door, shifter, steering wheel)
  while it watches the car's data and the motor. It checks or finds each signal. It asks which steering wheel teeth
  are on (press **Short teeth (15)**, **Long teeth (29)** or **Long back teeth (45)**), then records a slow turn of the steering wheel each way: you
  press **Start, then turn**, it records the car's data and the motor's angle while you turn, and carries on by
  itself once the motor has moved and the wheel has then been still for 1.5 s (or after 25 s). From the two turns
  it works out the motor's direction and checks the gearing against how far the motor follows on that set; a turn
  that matches another set says to check which teeth are on. The saved config holds how far the motor follows on
  the set that is on, and its gearing. The same recordings are searched for the car's own steering angle (`discovery.py`, above);
  the report has a line for it, found or not, and neither is a failure. Then the motor
  gives the steering wheel a short push to the left (about 3 Nm; it lets go after 6°, so its gear stays on the teeth)
  and asks you whether the wheel went left. On a "no" it tries the other way once. Last comes the grip test: you hold
  the steering wheel still while the motor pushes as hard as its board can, about 2 seconds each way. A jump in the
  motor's angle means its gear slipped over the teeth, and part 1 fails with what to fix; the wheel turning in your
  hands stops the push after 3° and it asks once more. It saves the result and a report, and restarts the device,
  which rebuilds the software with the saved map. Only the brake pedal must be found, and the grip test passed, for
  it to save. Running it again clears the drive check's pass, because the motor's direction or the signal map may
  have changed: lane keeping waits until the drive check passes again.
- **`check_drive.py`** (`accord_setup.sh drive`) needs the parked check first. It reads the drive the device
  recorded. Stand-alone it compares the comma device's own speed (`deviceMotion`, valid readings only) with GPS
  and saves the factor between them; connected, it checks the car's speed reading against GPS (or finds it). Either
  way it and checks the motor's direction against the
  GPS course. It needs the lift lever down during the drive and GPS fixes with a sure course (within 5°). If the
  direction reads the wrong way, it says to run the parked check again; if the drive doesn't show enough turning, it
  asks for more. When part 1 found a steering angle on the car's network, it checks that against the GPS course
  too, and drops it from the config (back to the motor's angle) if it reads backwards or the drive doesn't show
  enough turning; the result prints as "Steering angle from the car".
- **`device.py`**: stops sunnypilot so the tool can use the car connection, keeps the device awake meanwhile, and
  reads and sends messages.
- **`__init__.py`** holds the software version (1.0.0); both tools show it when they start, and part 1's report
  records it.
- Tests: the tools run end to end against the simulated car and motor (27 tests; the phone page has 5 more of its own), including a wheel turned right
  first, a push you never see go left, a push that stops after a few degrees, a drive that shows the wrong motor
  direction, a drive with the lift lever up, a drive check run before the parked check, a parked check run again
  after both had passed, the short teeth, a wrong answer about which teeth are on, no answer to it, and the grip
  test passing, slipping, and not held, and the steering angle search: a car without one, with one (found, scaled
  and used), with one that comes too slowly, and the drive check dropping one that reads backwards. They also check
  that nothing the tools ask or print uses jargon or old part names.

### New: the comma device's own speed (stand-alone)

- **`openpilot/sunnypilot/selfdrive/car/hondastepper_speed.py`**: reads `deviceMotion` and GPS (`gpsLocation` or
  `gpsLocationExternal`, whichever the device has) and returns the speed and whether it can be used: the device's
  estimate valid (its filter, inputs and camera motion all good, under 0.3 s old), times the saved factor, unless a
  GPS fix sure of its speed (within 1 m/s) has disagreed for 3 s.
- **`openpilot/selfdrive/car/card.py`**: for this car stand-alone, hands that to the car port before every update,
  and doesn't wait for a car message before starting (only the motor is on the network, silent with the lever up).
- **`openpilot/sunnypilot/selfdrive/car/hondastepper_alerts.py`**: "Past the teeth" now chimes only when the wheel
  moved the way the motor pushed, so the wheel turned against the motor (stand-alone) gets no chime.
- Tests: `test_hondastepper_speed.py` (6 tests): the scale, the estimate not ready or stale, a short GPS glitch
  ignored, a lasting disagreement stopping the motor and agreement bringing it back, slow or unsure GPS not
  compared, readings from real messages, and card's reader on a stand-in for openpilot's messages.

### New: settings made at every start

- **`openpilot/sunnypilot/tools/hondastepper/settings.py`** makes the settings this car needs: the vehicle (the same
  entry Settings > Vehicle saves), MADS on, Toggle with Main Cruise on (on this car the lift lever is the main
  switch), Steering Mode on Brake Pedal: Pause, Neural Network Lateral Control off, Auto Lane Change by Blinker Off,
  Pause Lateral Control with Blinker on with Minimum Speed 255 (the highest value, so at every speed, in mph and
  km/h). It writes only a setting that differs, the way sunnypilot saves it, which matters on a comma four, whose
  screen has none of these settings.
- **`openpilot/system/manager/manager.py`** calls it every time sunnypilot starts, after its default settings and
  before anything else runs. If it fails, the manager logs it and carries on.
- Tests: `test_settings.py` (4 tests): every setting made on a fresh device, with the vehicle entry from the vehicle
  list; a setting changed in a menu put back, with nothing else touched; nothing rewritten when all is already
  right; and the same again with sunnypilot's own settings store.

### New: the lift lever tested as one system

- **`test_lever_system.py`** (6 tests) runs the simulated car and motor, the panda's safety code (opendbc's test
  build of it, the same C code the panda runs), and sunnypilot's car port, car events, MADS and both of its state
  machines together on one clock, in the order they run on the device, including the panda's once-a-second checks
  and openpilot's heartbeat to it. It checks:
  - lever down: the panda allows steering about 2 s after the motor runs, and lane keeping turns on within 60 ms
    after it, with the engage sound only; lever up: off within 0.12 s, with the disengage sound only;
  - the lever already down as the car starts, with sunnypilot starting up after 0.3, 1.0, 1.9, 2.5, 4.0 or 6.0 s:
    lane keeping turns on by itself 2 s after the panda enters this car's mode, panda first, with no other alert;
  - openpilot never steers while the panda refuses, and the panda refuses none of its steering commands;
  - a motor gear off the teeth, the brake pause and a 0.3 s hold-up of messages on the comma device are silent;
  - a motor restart turns lane keeping off on both sides together and on again 2 s after.

  The same test with the start-up wait removed (counting from the motor's first message) shows why it is there:
  with sunnypilot starting within 2 s, lane keeping turned on before the panda allowed it, its commands were refused,
  the motor turned itself off and "TAKE CONTROL IMMEDIATELY" came up; starting later, it never turned on.

### New: steering from the gyro

- **`openpilot/sunnypilot/selfdrive/controls/lib/measured_curvature.py`**: for cars that set `useYawRate`, how
  sharply the car is turning is measured from the comma device's gyro (turn rate ÷ speed) above 2 m/s, blending from
  the steering angle below that. This car only knows its steering angle relative to where the motor powered up, so
  the angle can't be used for this.
- Used by `controlsd.py`, `latcontrol_torque.py` and sunnypilot's `latcontrol_torque_v0.py`. Those two also skip
  the steering angle dead zone for such cars.
- **`paramsd.py`**: doesn't learn the steering ratio or angle offset from a relative steering angle.
- **`torqued.py`, `torqued_ext.py`**: the live torque learner accepts this car. sunnypilot's torque and delay
  learners skip the moments when the car reports the driver turning the steering wheel. This car can't report that
  (it has no sensor for it), so steering a lot yourself with lane keeping on can skew what they learn. Not tested on
  this car.
- Tests: `test_measured_curvature.py`, `test_paramsd_yaw_rate.py` (9 tests).

### New: the two chimes for the teeth

- **`openpilot/sunnypilot/selfdrive/car/hondastepper_alerts.py`**: `TeethAlerts`, run from sunnypilot's car-specific
  events (`car_specific.py`, which now gets selfdrived's messages) every frame. From `modelV2`'s planned path
  (turn rate ÷ speed at each point up to 3.5 s ahead) and the vehicle model, the steering wheel angle each point
  needs, times a ratio scale (0.6 to 1.6, the median of motor angle ÷ vehicle model angle while the gear is on the
  teeth, the car turning and lane keeping on; the motor's angle on a straight stretch of 2 s or more is the
  straight-ahead reference, forgotten when the lever goes up or the gear runs off). Over the reach less 2°: the
  curve chime, 3 s on then 10 s quiet. The car port's "driver steering" (free spin) rising while lane keeping pushes:
  the past-the-teeth chime, 2 s.
- **`custom.capnp`**, **`events.py`**: the two events, `hondastepperCurveAhead` and `hondastepperPastTeeth`, with
  the prompt sound and a steering wheel icon.
- Tests: `test_hondastepper_alerts.py` (9); the lift lever system test covers both chimes end to end (7).

### Changed: build and start

- **`SConstruct`** regenerates the car's signal map and panda header from the config in use (the default, or the one
  the setup tool saved) before anything that uses them is built. If the saved config can't be used, it says why and
  builds from the default.
- **`launch_chffrplus.sh`**: before building, if git's large-file tool is there and any large file is still a
  placeholder, it downloads them (`git lfs pull`). If that fails it says so and the start carries on.

## Installing from GitHub

- comma's installer runs `git clone -b v1.0.0 --depth=1 --recurse-submodules` from `github.com/YOURNAME/openpilot`,
  then `git submodule update --init`. The version branch's last change points sunnypilot's `opendbc_repo` at
  `github.com/YOURNAME/opendbc`, where the same version's opendbc branch holds the car port. Both were tried here
  with local copies standing in for GitHub, including fetching an opendbc change that isn't on that copy's main
  branch.
- The device then follows that branch for updates (Settings > Software > Target Branch). A version branch never
  changes, so nothing updates by itself; picking a newer version there installs it, and picking an older one goes
  back.
- The car setup's saved config (`/data/hondastepper/`) is outside the software's folder, so a change of version keeps
  it. Clearing the device (uninstalling) erases it.

## Test results (2026-10-10, version 1.0.0)

| Suite | Result |
|---|---|
| opendbc car tests (includes the 80 new ones) | 900 run: 556 passed, 344 skipped (the existing tests skip cars a check doesn't apply to). The tests written for the car's network run with `car_network` on; 12 new ones run stand-alone |
| opendbc safety tests (includes the 114 new ones) | 8533 run: 7605 passed, 928 skipped. The stand-alone class first ran 0 tests (it lacked one message builder the shared tests need, so the test runner skipped it without a word); found by the coverage check, fixed, and now 29 run |
| line coverage of the new safety mode by its tests | 100% (100 of 100 lines, both settings) |
| opendbc signal and sunnypilot vehicle list tests | 71 passed |
| sunnypilot: setup tools (33), phone page and prompter (5), settings (4), the lift lever as one system (11: 7 connected, 4 stand-alone), gyro steering and steering learner (9), the two chimes (10), the comma device's own speed (6) | 78 passed; the settings test ran with sunnypilot's own settings store |
| the phone page in a phone-sized browser (Chromium, 390 x 844), with a stand-in for the setup tool | starts part 1, shows each question with its buttons, sends the answers back, and shows the earlier messages under the question |
| MISRA C check of the safety code (cppcheck, as comma runs it; a coding standard for safety code) | clean (after moving each list of checked messages into its own branch) |
| panda firmware build (comma 3X chip) with the new safety mode | builds |
| ruff (a Python style checker) on the changed code in both repos | clean. sunnypilot's `SConstruct` is left out: ruff can't see the names the build tool provides there, with or without these changes |
| the version branch (`push_fork.sh … --dry-run`) | sunnypilot's v1.0.0 points `opendbc_repo` at `github.com/USER/opendbc`, at opendbc commit `1be0dc77`; nothing else differs from the tested code |
| comma installer's clone (`git clone -b v1.0.0 --depth=1 --recurse-submodules`, then `git submodule update --init`), with local copies standing in for GitHub | the opendbc change that is only on the opendbc copy's v1.0.0 branch is fetched and checked out (run on 2026-10-09 with small stand-in repositories; this version only adds a commit to each branch) |
| printed parts rebuilt from the CAD files | every part one closed solid that fits the bed, the gears of both teeth sets without overlap at the lowest, middle and highest steering column tilt, 175 clearance checks with nothing touching, every bolt and screw the right length, the lift lever's click and stop. Margins: every design row at 1.4 or more, dry teeth 1.68; the one that depends on you (the dash clamp with no sunshade, 1.07) is flagged, and the mount gets proof pulls. The package's CAD program rebuilds the same files. The CAD program passes ruff's error checks |
| the right-side mount (same run) | its five parts (the shallow ring, the side bracket, three screw tabs) closed solids that fit the bed, none needing supports; the fit for the estimated screw position (arm-090, screw-tab-160); 301 clearance checks with nothing touching (as the column mount's, plus the wiper stalk, the key cylinder, the dash at the screw and the mount's own bolts); the arm and tab named for every screw position in the table that the arms and tabs reach; the lifted handle's clearance for cover widths 90 to 125 mm; its margins 8.7 (screw), 30 (tab), 4.3 (sliding), 2.3 (heat); its bolts the right length. The dash mount's STL files and the column mount's, apart from the ring's new slots, unchanged byte for byte |
| the back-teeth mount (same run) | its 14 parts closed solids, each fitting a 220 mm bed but the long back teeth's one-piece file (made for 330 mm beds); both sets of back teeth meshing with the motor gear without overlap through their whole arc, every degree, free play 0.17° at the wheel; 564 clearance checks with nothing touching, 282 with each set (lever down, up and swept, the wheel turned through the teeth and past them, the carrier dropping along the ramps), against the photo estimates of the car; one arm (back-arm-165) for the cover's underside anywhere from 40 to 70 mm below the column's middle; its margins 1.52 (gear held in the teeth), 1.44 (spring with its washer), 2.74 (gear teeth), 1.55 (gear on its shaft), 9.1 (teeth on the grip), 1.59 (plate on the cover's screws, two in the outer slot), 2.3 (heat); its bolts the right length. Sliced every 0.25 mm along three directions, the teeth pieces show no slivers or films; the hinge block has one thin, tapering edge where the hinge bolt's room is cut, harmless. The other mounts' STL files unchanged byte for byte |
| the column mount (same run) | its six parts closed solids that fit the bed; the motor gear inside the ring without overlap through the ring's arc, free play 0.16° at the wheel; 244 clearance checks with nothing touching (lever down, up and swept, the wheel turned, the ring turning under the gear, the carrier dropping at the ring's ends), against the photo estimates of the car; the arm named for every clamp position 180 to 340 mm behind the front of the grip at cover heights 70 to 110 mm; its margins 2.1 (clamp), 1.9 (skirt), 2.3 (heat); the rods long enough over the covers' height range. The dash mount's STL files unchanged byte for byte |

## Not tested yet

Nothing here has run in a car or on a comma device. The tests use a simulated car and motor, and the panda's code
runs as a test build on a computer. These are checked for the first time in your car:

- the signal map: the setup tool checks it and finds signals that are elsewhere;
- the motor's direction and gearing: the setup tool checks them, and the drive check checks the direction again;
- the grip test on a real motor and real teeth: tested against the simulated motor only. Its sign of a slip (the
  motor's angle jumping 1° or more between two readings 20 ms apart) assumes a hand gives way much more slowly;
- dry teeth: how hard the printed teeth rub on each other with no grease (0.3) is an estimate from a published
  measurement of PETG on steel, not from these parts. The grip test is what proves the motor gear stays in;
- the phone page on a comma device, with a phone joined to its hotspot: tested on a computer, in a phone-sized
  browser, against a stand-in for the setup tools. Its address (192.168.43.1) is the one sunnypilot's own hotspot
  code gives the device. If the page doesn't open, the car setup runs over SSH the same way;
- the motor's real torque: the software works from STEPPERONLINE's rating (45 Ncm at 2 A) and the firmware's stock
  settings;
- the free spin threshold (100°/s) and the 1° sign that the gear is back on the teeth: chosen from estimates of
  the motor's speeds. How fast the motor really spins off the teeth isn't known; the check now works at any speed;
- lane keeping turning on 2 seconds after the lift lever goes down, and by itself with the lever already down as
  the car starts: tested as one system in simulation, including the panda's code, not on a device;
- how long the motor takes to start up: its firmware sends its status before its controller runs, and both the
  panda and the comma device wait for the "controller runs" bit, so a slow start only delays lane keeping;
- the steering tune: the starting torque values are estimates; sunnypilot refines them while you drive;
- installing from GitHub on a real device: comma's installer, the driving model download, the operating system
  update and the first build (20 minutes or more is an estimate);
- the settings made at every start, on a real device (tested with sunnypilot's own settings store), and on a comma
  four, whose screen doesn't show them;
- a comma four with this build at all: its menu names in the guide are read from sunnypilot's code, not seen;
- how far the motor follows the steering wheel on each set of teeth (42.2° and 71.5°; 43.4° and 104.1° on the back
  teeth): calculated from the printed parts. A hand turn should measure about 3° more, because the roller follows the rolling band a little way down its
  slope; the setup's check allows 35% either way. On the side-slide mount's teeth, where the gear has no roller,
  30.4°: for the short teeth the setup takes the nearer of 30.4 and 42.2, so a turn of up to about 35° reads as a gear
  without a roller;
- the two chimes: the curve chime rests on the car's steer ratio (13 to 18 to 1 is the range), refined only while
  driving; it can come early. Tested in simulation and in the lift lever system test. Whether sunnypilot's alert
  list shows these events on a real device the way the tests see them is checked in the car;
- the wiring through comma power and the 12 V socket plug: from comma's harness box diagram and the owner's manual,
  not tried. The multimeter checks are the proof;
- the steering angle search: whether this car sends its steering angle on the network the comma device reads isn't
  known, and the search has only run against the simulated car (with and without one). If it finds one, the car
  port and the steering learner then run as for a car with a steering angle sensor, which no test has driven: part
  2's check against the GPS course is the guard, and the first drives need the same care as with the motor's angle;
- the column mount: designed and checked against estimates of the car taken from photos (the steering column
  covers' size and shape, where their front edge and the dash are, the hub's depth, where the lower spokes' back
  faces are, the open stretch between the spokes) and on the assumption that the plastic covers are stiff enough to
  hold it. The guide's measurements and push test come before printing; the proof pulls after building;
- stand-alone (the default): the comma device's own speed as the car's speed. How close it comes to GPS on this
  car, and whether 0.85 to 1.15 covers it, is only seen in part 2's drive; the 3 s GPS cross-check and its 2 m/s or
  15% limit are chosen, not measured. Calibration (sunnypilot's 15 mph rule) and its steering learner run on that
  speed too. The motor letting go when the wheel turns against it (60% push, 20°/s, 1.5 s still) has run only in
  simulation: the first drives show whether the wheel coming back out of a curve sets it off, or a light hand on the
  wheel doesn't. The comma device powered through the harness from the socket plug, and its draw (1.5 A is an
  estimate), are as comma's harness notes describe, not tried; the multimeter checks are the proof;
- the right-side mount: the same, plus the dash's screw (where it is, and whether its boss in the dash plastic holds
  the 23 N the motor can put on it: the proof pull is the test), the wiper stalk and key cylinder (estimated from
  photos; the parts clear the estimates by 25 mm or more), where the right spoke meets the grip, under the ring's
  shallow channel, and the dash between the covers and the screw being flat. The guide's measurements replace the
  estimates before printing;
- the back-teeth mount: the same kind of estimates (the lower cover's underside 50 mm below the column's middle, its
  screws on its right-hand side, the tilt lever clear of the plate, the right spoke's junction, the wiper stalk (a
  straight-on photo suggests it may sit nearer 3 o'clock than estimated, where the lift lever's paddle is), the key
  cylinder), and how well the cover's screws hold the plate: 1.59 times the worst pull with two screws in the
  plate's outer slot 80 mm apart, but 1.03 if both fall in its inner slot. The spring holds the motor gear in these
  teeth with 1.52 times lane keeping's most push (1.36 with the weakest spring Lee Spring may ship), against 1.68 on
  the other mounts; the grip test is the proof, and a second washer isn't an option here. The guide's measurements
  come before printing; the proof pulls and the grip test after building;
- the side-slide mount (1.1.0; its lever 1.1.1; its foot and teeth sets 1.2.0): checked in CAD only. The car round
  it (the column cover, the cover on the back of the steering wheel, the key) is an estimate from photos. That
  estimate puts the cover on the back of the steering wheel where the motor slides in: the motor's back end comes
  to 63 mm from the middle of the steering wheel, and the photo model has that cover reaching out to 89 to 102 mm,
  so the two meet by 40 cm³ or more. You said there is room; the guide's first measurement settles it before
  anything is printed. The foot is drawn for the column cover's front edge 70 to 89 mm behind the back of the round
  part you hold and its screw 32 to 35 mm behind that edge; the second measurement settles that. How far the back
  of the steering wheel moves towards or away from the dash as it turns is unknown, and with nothing springing at
  the teeth that sets how deep the gear sits in them. The spring's pull and the block's drag are catalogue figures
  and estimates. The foot's hold against the motor's twist is friction (silicone tape on painted plastic, 0.5, and
  600 N from the screw: estimates), proved by the push test. The lever's grip in its notches rests on an estimate of
  how hard printed parts rub (0.3), and whether you can reach its knob is for you to say. As the gear comes out onto
  the teeth, its power still off, the pointed tooth ends turn it into the gaps: about 8 Ncm on the gear for a 20 N
  pull on the lever, against the motor's own cogging, which STEPPERONLINE doesn't publish (2.5 Ncm is an estimate);
  if it ever stops short, rock the steering wheel a little. The 20% allowance on the turn check for the sets without
  a roller is chosen from the printed parts, not measured on real teeth. The bumper gets a proof test; the grip test
  is the proof that the gear stays in the teeth.

## Planned for later versions

Nothing here is built. Each is a later version with its own number.

- **After the trial: lane changes by turn signal.** sunnypilot's auto lane change without a steering nudge
  (this car has no torque sensor), above a set speed; below it the turn signal pauses lane keeping as now. A
  highway lane change takes 3 to 6° of steering wheel, inside the short teeth. The car has no blind-spot sensor:
  nothing checks the next lane but you.
- **A fresh pull of the lift lever at every start**, instead of lane keeping coming on by itself when the lever was
  left down. Software only. Not decided.
- **Which mount.** The package is the side-slide mount (behind 5:20). The dash mount over the top of the wheel, the
  column mount under it, the right-side mount beside it at 3 o'clock and the back-teeth mount behind 3 o'clock are
  in the other-mounts file, unchanged. All of them rest on estimates of the car; the measurements in the guide
  settle whether the one you build fits as drawn. If the side-slide mount's first measurement fails (no room for
  the motor to slide in), the slide has to go another way, and that is a new design.

## Before 1.0.0: test builds

These builds were never installed. They are kept as a record of how the design got here.

### Fixes after an independent review (2026-10-06)

A separate review of the first build found these, all fixed:

- The motor's direction rested on which way you turned the steering wheel first. Now you confirm it by eye after
  the motor's push, and the drive check confirms it again from the GPS course.
- Free spin turned the motor back on 1 s after it stopped spinning, which could repeat in one turn. Now it waits
  for the gear to be back on the teeth.
- The free spin check missed spins faster than the motor's speed reading can show (it wraps above about 700°/s).
- The motor's test push could carry on far enough to take its gear off the teeth. It now lets go after 6°.
- The setup tool could pick a signal from a message too slow for the panda, which would leave lane keeping
  refusing to turn on. Those messages are now skipped, and the config check refuses them.
- When several places matched a signal, the pick depended on the order of the recording. It is now fixed.
- A damaged saved config stopped sunnypilot from starting for any car. It now falls back to the default.
- The installer of that time checked everything first, could undo its move, and set the device's settings itself.
- Wording: plainer messages throughout, and the firmware's stock-settings assumption is written down.

### 2026-10-08

- **The lift lever is the only switch.** Before, lane keeping turned on with the cruise MAIN button, and after
  lifting the lever you waited about 3 seconds and pressed MAIN twice. Now lane keeping turns on about 2 seconds
  after the lever goes down, and turns on by itself if the lever was already down as the car started. The cruise
  MAIN button and the car's cruise state are gone from the signal map, the car setup and the panda.
- **Free spin is silent.** Before, it showed "TAKE CONTROL IMMEDIATELY" with a warning sound once per turn. Now the
  motor is switched off without an alert, and lane keeping carries on once the gear is back on the teeth.
- **A motor that restarts** (power lost for a moment) turns lane keeping off on both the comma device and the panda
  at once, and back on 2 s after it runs again. Both read the motor's "controller runs" bit for this.
- **A hold-up on the comma device** no longer looks like a lifted lever: the motor's silence is timed against the
  car's own messages, as the panda times it.
- **Two sets of steering wheel teeth.** Short ones (16 teeth, reaching 15° each way) for getting used to lane
  keeping, and long ones (32 teeth, 29° each way). The parked car setup asks which set is on, checks the motor's turn
  against it, and saves how far the motor follows on that set. Nothing else in the software differs between them.
- **The lift lever is pulled down until it clicks**, on the side towards you, with a new lever bracket holding the
  lever, the power switch and the catch.
- **comma four.** The guide covers the comma four as well as the comma 3X. No code change was needed: its safety
  chip runs the same firmware as the comma 3X's, with the same rules for this car, and the setup tools don't depend
  on the device.
- Each arm's slot got 8 mm longer, and the build checks every dash clamp position at the lowest, middle and highest
  steering column tilt that NHTSA measured (22.1°, tilting 18.5° to 25.9°).

### 2026-10-09, fit check

No software changes. A second fit check found two places where bought bolts didn't fit, and one tight spot:

- The lift lever's bolt couldn't go in: the hinge block's side plates covered its line on both sides. Their front
  corners are now cut away at 45 degrees.
- The hinge bolt's head and nut didn't sit flat: the side plates reached 0.25 mm over them. They are now cut back.
- Motor screws: button heads (M3 x 6), which sit below the carrier plate's face, clear of the motor gear.
- The parts check now also covers the dash cover and the dash clamp, the bought screws and bolts, room for the tools
  on the lift lever's bolt, and the setup gauge in place, and lists every bolt's length in the parts report.
