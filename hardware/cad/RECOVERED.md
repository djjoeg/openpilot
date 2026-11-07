# The design programs, rebuilt (7 Nov 2026)

These files were lost when the workspace was replaced on 5 Nov. They were rebuilt from the chat record: every
command and file write that made or changed them was copied out exactly and replayed in order
(`recovery/assemble.py`, from the operations in `recovery/ops` listed in `recovery/index`).

## What is here

The current build (right-arm mount):

| File | What it makes |
|---|---|
| rightarm.py | the right arm, the carrier and the frame plate (print plate 12) |
| midteeth.py | the steering-wheel teeth v3 and the teeth fit sample (plate 14) |
| allinone.py | everything in one print (plates 13 and 13b) |
| platefit.py | the frame-plate fit test and its paper template (plate 15) |
| platefit2.py | frame plate v2: paper template and before/after picture |
| rightcheck.py | the fit, clearance and mesh checks |
| stiffness.py | how far the motor's push bends the arm |
| visuals.py, viewer3d.py (+ viewer3d_page.html) | review pictures and the 3D page |
| incar.py, carphoto.py, photocomp.py, photorender.py | the parts drawn into your car photos |
| margins.py | the load margins for each way the build can fail |
| cadlib.py, params.py, frameplate.py, slotplate.py, armmount.py, carscene.py, carref.py, gears.py, wheelparts.py, render.py, plates.py | shared pieces |

Earlier mounts, kept for the record: accord_lka_parts.py, mountparts.py, assembly.py (the first mount);
column*, face*, pop*, side*, slide* (the column, back-teeth, pop-off, side-slide and slide mounts).

## How far it has been checked

- All 39 programs are valid Python.
- platefit2.py, the one program that survived, comes out of the replay identical to the surviving copy, byte for byte.
- The frame-plate fit test from platefit.py matches the printed file plate-15 exactly in size (166 x 147 x 6 mm). Its
  volume also matches: 64.9 cm3 in the file, and 68.8 cm3 drawn less about 3.9 cm3 of slots.
- **Not yet run.** The programs need the 3D library manifold3d, which can't be installed in this workspace. So
  the other parts haven't been re-made and compared against the print files yet.
- Five times in the chat, a tidy-up tool (`ruff --fix`) changed files automatically, and what it changed is not in
  the record. At most this leaves an unused import or two. It does not change any part.
- incar.py reads your original car photos from the chat's upload folder, so it needs those photos put back
  before it can run.
