python3 - <<'EOF'
src=open('accord_lka_parts.py').read()
src=src.replace('''  if "column_mount" in r:
    L += column_text(r["column_mount"], MG)
''', '''  if "column_mount" in r:
    L += column_text(r["column_mount"], MG)
  if "side_mount" in r:
    L += side_text(r["side_mount"], MG)
''')
# the column ring's tie wording: slots every 4.5 degrees instead of three fixed ties
src=src.replace('''                  "zip_ties_deg": list(t.tie_angles), "most_overlap_mm2": round(max(over), 4),
                  "free_play_steering_wheel_deg": [round(min(plays), 3), round(max(plays), 3)]}
  if max(over) > 1e-3:
    problems.append(f"column mount: the ring's teeth''', '''                  "zip_tie_slots": len(CP.slot_angles(t)), "slots_every_deg": CP.SLOT_EVERY_DEG,
                  "most_overlap_mm2": round(max(over), 4),
                  "free_play_steering_wheel_deg": [round(min(plays), 3), round(max(plays), 3)]}
  if max(over) > 1e-3:
    problems.append(f"column mount: the ring's teeth''')
src=src.replace('''           f"{g['piece_spans_deg']} degrees, zip ties at {', '.join(str(a) for a in g['zip_ties_deg'])} degrees each side of "
           f"6 o'clock. Most overlap anywhere in the range: {g['most_overlap_mm2']} mm2 (should be 0). Free play at the steering "
           f"wheel: {g['free_play_steering_wheel_deg'][0]} to {g['free_play_steering_wheel_deg'][1]} degrees.")''',
'''           f"{g['piece_spans_deg']} degrees, with {g['zip_tie_slots']} zip tie slots every {g['slots_every_deg']} degrees (tie it "
           f"wherever the spokes leave room). Most overlap anywhere in the range: {g['most_overlap_mm2']} mm2 (should be 0). Free "
           f"play at the steering wheel: {g['free_play_steering_wheel_deg'][0]} to {g['free_play_steering_wheel_deg'][1]} degrees.")''')
open('accord_lka_parts.py','w').write(src)
print('ok')
EOF
grep -n "zip_ties_deg" accord_lka_parts.py | head; grep -n "side_text\|side_mount" accord_lka_parts.py | head