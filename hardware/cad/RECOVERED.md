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

## How far it has been checked (7 Nov)

The programs were run with the 3D library manifold3d 3.5.4, built from its source. Each result was compared with
your print files and with the numbers in the change log:

- **Plate 13, the whole reprint:** the frame plate v5, the arm v6, the carrier and the teeth v3 all come out
  identical to your file. The sizes, volumes and triangle counts are the same, and the surfaces are 0.000 mm apart.
- **Plate 14 (teeth fit sample) and plate 15 (frame-plate fit test):** identical to your files.
- **Your copies of plates 12 and 13b are older than plate 13.** They hold an arm from before v6 (115 mm long, where
  v6 is 127). The rebuilt programs make them with v6, as the change log says they should be. The new copies are
  in hardware/print, and the old ones stay in this branch's history.
- **rightcheck.py:** 8,391 checks, 0 failed, the same as the change log.
- **stiffness.py:** +0.15 / -0.46 mm and +0.49 / -0.93 mm, up to +0.28 / -0.71 and +0.69 / -1.27, all passing.
  These are the change log's numbers exactly.
- platefit2.py, the one program that survived, comes out of the replay identical to the surviving copy.
- Five times in the chat a tidy-up tool (`ruff --fix`) changed files, and what it changed isn't recorded. At most
  that leaves an unused import; the results above show no part changed.
- incar.py reads your original car photos from the chat's upload folder, so it needs those photos put back
  before it can run.
