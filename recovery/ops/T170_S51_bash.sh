python3 - <<'EOF'
import pathlib
p = pathlib.Path("sidebuild.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)
rep("""       "The notch at the slot's inner end is for a broken spring: without the spring, the motor's own weight slides it back",
       "out onto the teeth; with the lever in that notch, the weight holds it in instead.", ""]""",
    """       "The notch at the slot's inner end is for a broken spring: without the spring, the motor's own weight slides it back",
       "out onto the teeth; with the lever in that notch, the weight holds it in instead.",
       "The mounting plate's foot lies under the lower column cover and is held by the cover's own screw under the key",
       "cylinder (a longer one), through a window that takes the screw wherever it falls; a bar under the foot bridges the",
       "window, and shims fill the gap up to the cover. The steering wheel teeth come in three sets, the same piece with",
       "10, 14 or 18 teeth: " + ", ".join(f"{S.SideTeeth(n_teeth=n).reach_deg:.1f} degrees each way ({w})" for n, w in S.TEETH_SETS.items()) + ".", ""]""")
rep("""  m = res["mesh"]
  L.append(f"  gear in the teeth over their whole arc: worst overlap {m['worst_overlap_mm3']} mm3; free play at the steering wheel "
           f"{m['free_play_steering_wheel_deg']} degrees")
  L.append(f"  the gear sliding in and out along the teeth's gaps: worst overlap {res['slide_out_of_teeth']['worst_overlap_mm3']} mm3")
  L.append("  the steering wheel turned through and past the teeth piece (every 0.5 degree), motor out: nothing touches")
  L.append("  past the teeth the gear is free (the motor is switched off there); coming back, the two lowered end teeth meet it")
  L.append(f"  first and turn it into step: they reach {res['end_teeth']['the last tooth (lowered most)']} and "
           f"{res['end_teeth']['the next (lowered less)']} mm3 into it at the worst angle if it didn't turn")
  L.append(f"  slid in {S.STROKE:.0f} mm: clear of the teeth piece anywhere round, the steering wheel and your fingers' room")""",
    """  for n, r in res["sets"].items():
    m = r["mesh"]
    L.append(f"  the {n}-tooth set ({r['reach_deg']} degrees each way):")
    L.append(f"    gear in the teeth over their whole arc: worst overlap {m['worst_overlap_mm3']} mm3; free play at the steering "
             f"wheel {m['free_play_steering_wheel_deg']} degrees")
    L.append(f"    the gear sliding in and out along the teeth's gaps: worst overlap {r['slide_out_of_teeth']['worst_overlap_mm3']} mm3")
    L.append("    the steering wheel turned through and past the teeth piece (every 0.5 degree), motor out: nothing touches")
    L.append("    past the teeth the gear is free (the motor is switched off there); coming back, the two lowered end teeth meet")
    L.append(f"    it first and turn it into step: they reach {r['end_teeth']['the last tooth (lowered most)']} and "
             f"{r['end_teeth']['the next (lowered less)']} mm3 into it at the worst angle if it didn't turn")
    L.append(f"    slid in {S.STROKE:.0f} mm: clear of the teeth piece anywhere round, the steering wheel and your fingers' room")""")
rep("""  L.append("  side-mounting-plate-draft: a draft. How it fixes to the car isn't drawn yet (see the questions); it is")
  L.append("  complete for trying the slide, the lever, the spring and the switch on the bench.")
  L.append("")""",
    """  L.append("  side-foot-shim: print four; use as many as fill the gap between the foot and the cover's underside.")
  L.append("")
  L.append("THE FOOT ON THE COLUMN COVER (from the photo model, for the range of cover positions it is drawn for)")
  for ff in res["foot_fit"]:
    L.append(f"  the cover's front edge {ff[\"cover's front edge behind the back of the round part (mm)\"]} mm behind the back of the round part: "
             f"the screw lands {min(ff['room left in the window across (mm, either way)']):.1f} mm or more inside the window across and "
             f"{min(ff['room left along (mm, either way)']):.1f} along (its place 4 mm off either way, the mount turned up to 3 degrees); "
             f"gap over the foot {ff['gap over the foot (mm)']} mm: {ff['shims']} shim(s)")
  L.append("")""")
rep("""  L.append("THE CAR ROUND IT: ESTIMATES FROM PHOTOS, NOT CHECKED (closest approach in mm; negative = overlap in mm3)")
  for tag, a, b, g in res["car_estimates"]:
    L.append(f"  {tag:9s} {a} to {b}: {g}")
  L.append("")""",
    """  L.append("THE CAR ROUND IT: ESTIMATES FROM PHOTOS, NOT CHECKED (closest approach in mm; negative = overlap in mm3)")
  for D, rows in res["car_estimates"].items():
    ff = SA.foot_fit(float(D))
    L.append(f"  with the column cover's front edge {ff[\"cover's front edge behind the back of the round part (mm)\"]} mm behind the back of the round part (D {D}):")
    for tag, a, b, g in rows:
      L.append(f"    {tag:9s} {a} to {b}: {g}")
  L.append("")""")
rep("""  for n, (m, rot, how, supports) in printed_parts(parts).items():""", """  for n, (m, rot, how, supports) in printed_parts(parts).items():""", 0)
p.write_text(s)
print("ok")
EOF
grep -n "res\[\"car_estimates\"\]\|res\['car_estimates'\]\|res\[\"mesh\"\]\|res\[\"clearances\"\]\|res\[\"wheel_turned\"\]\|res\[\"slid_in\"\]" sidebuild.py