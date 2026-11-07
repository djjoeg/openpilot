set -e; A=/mnt/user-data/attachments/29de5e81-e3b9-5428-a15c-fac1d206c0d4; S=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad; B=$S/backup/accord-lane-keeping; rm -rf $S/backup; mkdir -p $B/hardware/print $B/hardware/cad $B/hardware/report $B/hardware/wiring $B/hardware/motor-card $B/hardware/photos-marked
cp /home/claude/deliver/CHANGELOG.md $B/CHANGELOG.md
cp $A/fef8448c-README.md $B/README.md
for f in $A/*.3mf $A/*template*.pdf; do b=$(basename "$f"); cp "$f" "$B/hardware/print/${b#*-}"; done
cp /home/claude/deliver/hardware/print/* $B/hardware/print/
cp /home/claude/deliver/hardware/cad/platefit2.py $B/hardware/cad/
for f in $A/e94c467a-review-1c-receiver.png $A/5d961c1a-frame-plate-fit-test.png $A/896ba33c-plate-13-all-in-one.png $A/4befcbe0-arm-v4-v5-below.png $A/2ac458c9-in-the-car-photo-00.jpg $A/b2d54f32-in-the-car-photo-00-before-after.jpg $A/cdd494ea-in-the-car-photo-33-before-after.jpg; do b=$(basename "$f"); cp "$f" "$B/hardware/report/${b#*-}"; done
cp $S/wiring-canvas/project/Main.dc.html $B/hardware/wiring/wiring-page-source.dc.html
cp $S/wiring-canvas/project/canvas.json $B/hardware/wiring/wiring-page-canvas.json
node $S/render_check.js $S/wiring-canvas/project/Main.dc.html $B/hardware/wiring/wiring-page.png >/dev/null 2>&1 || true
cp /home/claude/deliver/hardware/motor-card/*.jpg $B/hardware/motor-card/
cp $S/tab/crosspiece-reading.jpg $B/hardware/photos-marked/
cat > $B/WHATS-HERE.md <<'EOF'
# What's in this backup (7 Nov 2026)

Everything from the project that exists right now, in one place.

- `CHANGELOG.md`: the change log, current (7 Nov).
- `README.md`: the 1.3.0 README as of 3 Nov (step-by-step build; the frame plate part is being redone).
- `hardware/print/`: every print file and paper template made so far (plates 12 to 15, the teeth fit sample,
  the paper templates v1 and v2).
- `hardware/cad/platefit2.py`: the program that draws the paper template v2.
- `hardware/report/`: the design pictures that survived.
- `hardware/wiring/`: the wiring page's source and a picture of it.
- `hardware/motor-card/`: the motor's card, both sides.
- `hardware/photos-marked/`: your photo with the crosspiece spot marked.

Missing: the programs that drew and checked the parts up to 5 Nov (`rightarm.py`, `midteeth.py`,
`rightcheck.py`, `stiffness.py`, `visuals.py`, `plates.py`, `allinone.py`, `platefit.py` and the earlier
mounts' programs). They were only on the workspace that was replaced on 5 Nov. The parts they made are safe:
their print files are in `hardware/print/`.

The software is on GitHub: branch `v1.3.0` (and the earlier versions) of github.com/djjoeg/openpilot and
github.com/djjoeg/opendbc.
EOF
cd $S/backup && zip -qr accord-lane-keeping-2026-11-07.zip accord-lane-keeping && ls -la accord-lane-keeping-2026-11-07.zip && unzip -l accord-lane-keeping-2026-11-07.zip | tail -1 && cp accord-lane-keeping-2026-11-07.zip /mnt/user-data/outputs/