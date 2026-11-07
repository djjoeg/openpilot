# Honda Accord lane keeping, version 1.3.0

Steering-only lane keeping for a 2008-12 Honda Accord 2.4L sedan. A comma four (or comma 3X) running sunnypilot
steers through a stepper motor on printed teeth on the back of the steering wheel. The motor sits outside the
steering wheel's rim just above 4 o'clock, on an arm from a plate under the lower column cover, its gear on the
teeth from outside. Nothing is spliced into the car: the comma device and the motor run from one 12 V socket plug,
and the comma device talks only to the motor.

**On and off:** the motor has power whenever the car is on. One wing bolt in a groove up the arm's tower does it all.
Loosen it, slide the motor up the column by it to your mark (the gear in the teeth) and tighten: lane keeping on.
Loosen, slide it all the way down (till the motor's carrier sits on the tower) and tighten: the gear is out of the
teeth, lane keeping off. There is no switch.

The build guide (https://claude.ai/code/artifact/0b3ce053-a508-4e38-92c4-faf3a50fd2b3) still describes the earlier
lever mounts; for this build, this README and `CHANGELOG.md` (1.3.0) are current.

## Buy

Three orders: Amazon (one cart, returns), the comma device from comma, and the motor controller from the Retropilot
store (bought). Order the comma device once the arm is on and the gear is set in the teeth (step 4 below) and the
board is close (it is needed for the wiring too): the comma device's 30-day money-back trial starts the
day it is delivered, and it comes in about 3 business days (comma's page on 2 Nov: sent the next business day, free
UPS 2nd Day Air in the US, someone has to sign). Its harness is needed for the wiring.
Prices were read on the shop pages on 2026-11-01. The Amazon items are on the wishlist "Accord lane keeping".

Bought (2026-11-01): the motor (STEPPERONLINE 17HS15-1504S-X1, 45 Ncm at 1.5 A, 40 mm), the StepperServoCAN board from
Retropilot, the cover screws (Mellewell #8 x 1-1/2 stainless, 100, $9.99). Ordered (2026-11-02): everything on the
Amazon list below. Owned: fender washers, zip ties, filament, the two M5 nuts. Still to buy: the comma device and its
cable (when: above).

Nothing new for the fit print (3 Nov: the arm v6 and the frame plate v5): each of its two slides takes one of the M5
wing bolts, one of the M5 nuts and one of your fender washers (3/4 to 1 in across), and the two cover screws take a
fender washer each: four fender washers in all.

On the way (checked 2 Nov): the motor, USPS 9214490416422007317521 (label made 1 Nov in Perth Amboy, NJ; USPS gives
a delivery date once it has the package). A parcel from Portugal, LA137988293PT, most likely the board (Portugal's
post, CTT; accepted 2 Nov; the tracking site's estimate is 13 to 19 Nov at your post office).

| What | Which | Where | Price |
|---|---|---|---|
| comma device | **comma four**, with the car harness (harness choice **Developer**; it is in the price) | [comma](https://comma.ai/shop/comma-four) | $999 |
| OBD-C cable | the **long** one, 9.5 ft | [comma](https://comma.ai/shop/obd-c-cable) | $20 |
| power plug | LANMINGLEL 12 V socket plug, 14 AWG, 2 m of cable with bare ends, 15 A fuse built in | [Amazon](https://www.amazon.com/dp/B0GXFML4TH) | $11.99 |
| connectors | WAGO 221 lever nuts, 12-piece box (three each of the 2-, 3- and 5-way and the inline; two 5-way are used) | Amazon wishlist | $12.45 |
| wire | BNTECHGO 20 AWG silicone wire, red and black, 10 ft each | Amazon wishlist | $8.48 |
| motor screws | MoyoCodi M3 x 10 button head screws, stainless, 50 with the hex key (four hold the motor to its carrier; exactly 10 mm long) | Amazon wishlist | $5.99 |
| set screws | JT Custom M3 x 10 set screws, 10, with the hex key (one for the gear) | Amazon wishlist | $6.99 |
| wing bolts | AOESIN M5 x 20 stainless wing bolts, 20 (two are used) | Amazon wishlist | $9.98 |
| tape | Anyknow silicone self-fusing tape, black, 2 rolls of 1 in x 10 ft | Amazon wishlist | $8.99 |
| multimeter | KAIWEETS KM100 (to check the wiring before anything is plugged in) | Amazon wishlist | $13.99 ($12.59 with the coupon) |

Amazon: $78.86 (with the multimeter's coupon, $77.46). Comma: $1,019, shipping free (its page, 2 Nov). All in, about
$1,180 with what was bought.
The two M5 nuts come from your own M5 kit: plain hex nuts (8 mm across, 4 mm thick), not nylon lock nuts,
which are too tall for the nut slots.

No fuses to buy: the plug has its own 15 A fuse. No relay or switch: nothing switches. Recommended, not on the list:
a pack of 120 ohm resistors (about $5) for one across the pink and blue wires at the harness end; the board has one
at its end, and a CAN pair wants one at each end (it will very likely work without it over 1 to 2 m; the multimeter
check tells). The motor's own 1 m cable reaches the board.

Tools, if you don't have them: a luggage scale (about $12), hex keys 1.5 to 10 mm (about $9), a wire stripper
(about $12), a Phillips screwdriver, a tape measure, super glue, your phone.

## Print

First, the fit sample: **`plate-14-teeth-fit-sample.3mf`**, a 23 mm slice of the teeth's channel at the new width
(1 mm wider than the v2 teeth you tried; marked 7 on the outside), on economy settings (2 walls, 15% infill), a few
grams. Push it onto the grip where the teeth go, the way they will go (on the tape, if it's on): it should go on
snug, with no gap and no forcing. If it doesn't, tell me how far off it is before printing the teeth.

Then one print, ready for Bambu Studio, in `hardware/plates/`: **`plate-13-all-in-one.3mf`**, all four pieces on one
256 x 256 mm bed, each with its own settings: the frame plate v5, the steering wheel teeth v3 (the 20 set: 19 teeth,
19.5 degrees each way; the channel 1 mm wider than the v2 you tried, the ends cut back to just past the last teeth),
the arm v6 and the motor carrier v6 (the arm and the carrier solid). Print the frame plate again: the arm's bar is
now 20 x 30 and slides by a groove in the receiver, and the v4 plate's receiver won't take it. This is the fit print:
both slides are long (the motor 31 mm along the column, the arm 35 mm across), so it fits wherever the car's real
numbers land; once you know where they sit, a later print can have shorter ones.
(`plate-13b-all-but-the-frame-plate.3mf` is the same without the frame plate.)

After printing, look at the long groove in the frame plate's square tube: its top edge prints as a 42 mm bridge. If
it sagged, the wing bolt still has 0.75 mm of room each side; if it catches, run a file along it.

The same pieces one plate at a time, if you would rather: `plate-11-frame-plate-v5.3mf`,
`plate-9-teeth-v3-20-winding-roads.3mf`, `plate-12-right-arm.3mf`. The shorter teeth sets, if ever wanted:
`plate-7-teeth-v3-11-straight-roads.3mf` (11 teeth, 10.8 degrees each way), `plate-8-teeth-v3-15-highway.3mf` (15
teeth, 15.2 degrees).

Open a plate in Bambu Studio (File > Open Project; if it asks, open it as a project, not as geometry only). The
pieces are placed on a 256 x 256 mm bed (A1, P1P, P1S, X1, X1C, X1E) and carry their own settings: 0.2 mm layers,
4 walls, 5 top and 5 bottom layers, no supports; 40% gyroid infill, or solid where it says. Pick your printer and
PETG, slice, print. Bambu Studio will say the file is not from Bambu Lab and that it loads the geometry: that is
expected. If a plate will not open, import its STL files from `hardware/stl/right-arm/` and `hardware/stl/mid-teeth/`
instead (already turned the way they go on the bed).

Pictures of every piece, for checking before you print: `hardware/report/review-*.png`. To turn it all round in
3D and take it apart step by step: `hardware/report/arm-3d.html` (open it in a web browser; the same page is on
claude.ai at https://claude.ai/artifact/2frUtDazPaeNmDnm2MzN2d).

## Then

1. **Fit the plate** on the cover's two screws (the cup slot on the key side, slot 1 on the other), a fender washer
   under each: the bigger washers hold the plate stiffer.
2. **Fit the teeth:** one wrap of silicone tape on the grip between the right spoke (the cruise buttons) and the
   silver spoke below it, the teeth piece on it with its middle (the zip tie slot) just above 4 o'clock with the
   steering wheel straight: about 64 mm (2 1/2 in) along the outside of the grip below where the cruise-button spoke
   meets the grip, the middle of the gap between the two spokes. Two zip ties through the middle slot, heads tucked
   inside the rim. (Step 4 fine-tunes it: slide it along the grip until the gear sits in the middle of the teeth.)
3. **Build the arm, off the car** (pictures: `hardware/report/review-1b-slide.png` and `review-1c-receiver.png`; the
   3D page goes through it step by step): the motor on the carrier (four M3 x 10 from the side with the four pads,
   the motor's boss in the big hole), the gear on the shaft (set screw on the flat). The motor's M5 nut into the slot
   across the carrier's bar, from the motor's side, its flats along the bar (it only goes in that way). The carrier's
   bar down the tower's tube from the top (the end nearer the steering wheel), all the way, till the carrier sits on
   the tower. The motor's wing bolt, a fender washer under its wings, in through the groove up the tower's outer wall
   and a few turns into that nut: now the carrier can't come out. Then, at the car: the arm's M5 nut into the slot in
   the top of its bar (flats along the bar; it only goes in that way), and the arm, with all of that on it, into the
   frame plate's square tube from the key side. The arm's wing bolt, a fender washer under its wings, in through the
   long groove in the tube's wall facing you and a few turns into the arm's nut: now the arm can't come out.
4. **Set the gear:** loosen the motor's wing bolt and slide the motor up by it until the gear is all the way into the
   teeth (rock the steering wheel a little if they meet tip to tip). Line the gear up with the teeth so its teeth sit
   in the middle of the steering wheel teeth's length: loosen the arm's wing bolt, slide the arm across by it and
   tighten it, or move the gear along its shaft. Keep the motor's carrier clear of the teeth piece's outer edge (that
   is about 4 mm further in than drawn). Then back the motor down 1 mm, one tick on the carrier's bar, read where the
   bar comes out of the tower's top, and tighten the motor's wing bolt. Turn the steering wheel by hand across the
   teeth: it should go smoothly. That tick is your "on" mark from now on.
5. **Wire it** (`hardware/report/wiring-right-arm.png`): the plug's + and - into two lever nuts; the harness's two
   red and brown, and the board's Vin, on +; the harness's two black and the board's GND on -; pink to the board's
   CANH and blue to CANL. Check it with the multimeter before plugging in the comma device or the board.
6. **First power-up with the gear out of the teeth:** a new board may calibrate itself, turning the motor slowly.
7. **Install the software:** it is on your GitHub copies, `github.com/djjoeg/openpilot` and `github.com/djjoeg/opendbc`
   (every version, v1.0.0 to v1.3.0, put there 2 Nov). On the comma device, at setup, enter
   `installer.comma.ai/djjoeg/v1.3.0` as its custom software (the guide's "Install the software" says what to
   press). The first start builds for 20 minutes or more.
8. **Car setup** from your phone on the comma device's hotspot (192.168.43.1:8090): part 1 parked, engine running,
   gear in the teeth (about 10 minutes; answer 20 for the teeth; the grip test pushes about 4 kg at the rim), then
   part 2 after 5 minutes or more of driving at 15 to 50 mph with some curves. Lane keeping stays off until both pass.
9. **Proof test:** push the motor sideways with the luggage scale to 5 kg each way: nothing may move.
10. **First tests** in an empty parking lot, then a quiet road.

## Everyday use

| To | Do this |
|---|---|
| turn lane keeping on | loosen the wing bolt in the groove on the arm's tower, slide the motor up by it to your mark (the tick at the tower's top), tighten. With the car on it pushes about a second after the steering wheel first turns the motor |
| turn it off | loosen, slide the motor down the column till the carrier sits on the tower (6 mm below your mark is enough), tighten |
| change lanes, turn | steer through the push: it lets go when you turn the wheel against it, and takes over again once you've held the wheel still for about 1.5 s |
| steer past the teeth (about 20 degrees of wheel) | the gear runs off them; it chimes "Past the teeth: steer yourself" and picks up again a second after you're back |
| know when a curve is too sharp | it chimes "Steer: the curve ahead is past the teeth" |

It doesn't know the brake or the turn signals: they don't pause it.

## What's here

| Folder or file | What it is |
|---|---|
| `hardware/plates/` | the print plates for Bambu Studio and a picture of each |
| `hardware/stl/right-arm/`, `hardware/stl/mid-teeth/` | the printed parts of this build, one file each |
| `hardware/report/` | `in-the-car-photo-00.jpg` and `-33.jpg` (your photos with the build drawn in, each with a before-and-after), `review-*.png` (the pieces and the assembly), `arm-3d.html` (the build in 3D, to turn round and take apart), `wiring-right-arm.png`, `column-frame-plate-v5.png` |
| `hardware/cad/` | the Python program that makes the parts: `rightarm.py` (the frame plate, the arm, the motor carrier), `midteeth.py` (the teeth), `rightcheck.py` (the clearance, fit, function and mesh checks), `stiffness.py` (how far the motor's push moves the gear), `visuals.py` (the pictures), `plates.py` (the plates), `allinone.py` (plate 13, the one print), `incar.py` (the in-car photos), `viewer3d.py` (the 3D page) |
| `software/` | the two change files (patches) that make version 1.3.0 from sunnypilot and opendbc, for reading or building it yourself; the comma device installs from your GitHub copies |
| `CHANGELOG.md` | every change, version by version, in plain words, with the test results |

The earlier mounts (side-slide: plates 1 to 4, `hardware/stl/side-slide-mount/`; dash, column, right-side and
back-teeth: `accord-lane-keeping-other-mounts-1.2.0.zip`) are still here, not used by this build.

## Versions

Each version is a branch in your GitHub copy (`v1.0.0` to `v1.3.0`) and never changes once made. The device stays
on the version you installed; to move to a newer one, pick it under settings > software > target branch.
`CHANGELOG.md` says what each version changes and whether it needs anything from you.

## Not tested yet

Nothing here has run in a car or on a comma device. The software was tested against a simulated car, motor and
safety chip. The parts were checked in CAD: 8,391 clearance, fit, assembly, function and mesh checks with all three
teeth sets and against the car's parts round the key as estimated from your photos (the column cover, the key and
the room to turn it, the wiper stalk's swing, the dash), and a stiffness model of the arm (at lane keeping's
strongest push the gear moves 0.15 to 0.5 mm deeper into the teeth one way and 0.5 to 0.9 mm out the other as
drawn, up to 0.7 and 1.3 with both slides at their far ends; in the grip test, 1.9 times that, its tips come within
0.1 mm of the bottom of the teeth one way as drawn, and reach it with both slides at their far ends). You've held
the v3 arm, the v4 frame plate and the v2 teeth on the car; the v6 arm, the v5 frame plate and the v3 teeth aren't
printed yet.

To check on the car with the parts you have, before relying on it:
- **The spokes passing the gear:** past about 20 degrees of steering either way, the spokes' joins on the back of the
  grip pass the gear, which sits about 25 mm behind the back of the grip. With the gear slid up into the teeth, turn
  the wheel slowly all the way each way: nothing may touch.
- **Your fingers:** the gear and the motor sit 22 to 25 mm behind the back of the rim at 4 o'clock. Hold the wheel
  normally at 3 and turn right past 4: see whether your fingers come near them.
- **The teeth's ends:** where the spokes' joins are comes from photos, good to about 2 degrees, and the 20 teeth's
  ends come to within about that of them. The v2 piece with its middle at the new spot shows it: v3 ends about 3 mm
  past its last tooth at each end. If that lands on a join, the 15 teeth fit with 4 degrees spare.
- **The frame plate:** with the arm tight in the receiver, push the carrier sideways hard: the plate shouldn't bend
  or lift off the cover. The stiffness model's softer case leaves the plate free except under its two washers.
- **The wiper stalk:** with lane keeping off (the motor slid all the way down), push the wiper stalk all the way
  down: in the photo estimates it passes 1 to 2 mm from the gear. If it touches, slide the motor down only 6 mm below
  your mark for off.

Not checked at all: the gear sliding back into the teeth out of step (its pointed tips should turn it into step).
The strength margins in `hardware/report/` were worked out for the side-slide mount, not for this arm; the 5 kg push
test and the stiffness model stand in for them.
