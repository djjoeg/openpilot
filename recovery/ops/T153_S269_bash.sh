python3 - <<'EOF'
import pathlib
edits = {
  "CHANGELOG.md": [
    ("the motor sits behind the rim,", "the motor sits behind the grip,"),
    ("a table of clamp positions 180 to 340 mm behind the rim and", "a table of clamp positions 180 to 340 mm behind the front of the grip and"),
    ("so it can sit over the right spoke's junction with the rim, and", "so it can sit over the place where the right spoke meets the grip, and"),
    ("the right hand's 3 o'clock spot on the rim:", "the right hand's 3 o'clock spot on the grip:"),
    ("and 240 to 340 behind the rim naming", "and 240 to 340 behind the front of the grip naming"),
    ("so you reach it from inside the rim at 3 o'clock", "so you reach it from inside the grip at 3 o'clock"),
    ("180 to 340 mm behind the rim at cover heights", "180 to 340 mm behind the front of the grip at cover heights"),
    ("the right spoke's junction with the rim under", "where the right spoke meets the grip, under"),
  ],
  "hardware/report/parts_report.txt": [
    ("265 mm behind the front face of the rim (estimates", "265 mm behind the front of the grip (estimates"),
    ("behind the front of the rim (at the screw's depth)", "behind the front of the grip (at the screw's depth)"),
    ("columns: behind the front of the rim, mm)", "columns: behind the front of the grip, mm)"),
    ("A screw less than 250 mm behind the rim's front puts", "A screw less than 250 mm behind the grip's front puts"),
    ("measure the covers 85 mm behind the rim and use that width", "measure the covers 85 mm behind the front of the grip and use that width"),
  ],
  "hardware/cad/accord_lka_parts.py": [
    ("the screw's trim behind the front face of the steering wheel's rim (mm)", "the screw's trim behind the front of the steering wheel's grip (mm)"),
    ("f\"the rim (estimates: measure yours).", "f\"the grip (estimates: measure yours)."),
    ("f\"of the rim (at the screw's depth)", "f\"of the grip (at the screw's depth)"),
    ("columns: behind the front of the rim, mm). ", "columns: behind the front of the grip, mm). "),
    ("A screw less than 250 mm behind the rim's front puts", "A screw less than 250 mm behind the grip's front puts"),
    ("measure the covers 85 mm behind the rim and use that width", "measure the covers 85 mm behind the front of the grip and use that width"),
  ],
  "hardware/cad/faceparts.py": [
    ("so you reach it from inside the rim", "so you reach it from inside the grip"),
    ("inside the rim at 3 o'clock", "inside the grip at 3 o'clock"),
  ],
  "hardware/cad/columnassembly.py": [("behind the front face of the wheel's rim.", "behind the front of the steering wheel's grip.")],
  "hardware/cad/columnparts.py": [("up to the V's rim between", "up to the V's top edge between")],
  "hardware/cad/params.py": [("behind the front face of the steering wheel's rim (estimate", "behind the front of the steering wheel's grip (estimate")],
  "hardware/cad/carscene.py": [
    ("the rim (the tape's hook)", "its edge (the tape's hook)"),
    ("def back_cover_rim(self)", "def back_cover_edge(self)"),
    ("r_r, z_r = self.back_cover_rim\n", "r_r, z_r = self.back_cover_edge\n"),
    ("\"back cover rim r, z\"", "\"back cover edge r, z\""),
  ],
}
for f, reps in edits.items():
  p = pathlib.Path(f)
  s = p.read_text()
  for a, b in reps:
    n = s.count(a)
    assert n >= 1, (f, a)
    s = s.replace(a, b)
  p.write_text(s)
  print(f, "ok")
EOF
grep -rnwi "rim" --include=*.md --include=*.txt --include=*.py . | grep -v "sunnypilot-hondastepper.patch" | head