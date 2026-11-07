python3 - <<'EOF'
import pathlib
p = pathlib.Path("sideassembly.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)
rep("""               ("lever", "lever's pin")):
    res[f"{a}/{b} (both move)"] = (overlap(mv[a], mv[b]), 0.0)""",
    """               ("lever", "lever's screw"), ("motor bracket", "lever's screw")):
    res[f"{a}/{b} (both move)"] = (overlap(mv[a], mv[b]), 0.0)""")
rep("""# ... out to the plate's outer face, this far from the pin""", """# ... out to the plate's outer face, this far from the screw""")
rep("""             # N mm about the pin; below 0 it swings towards the slot""", """             # N mm about the screw; below 0 it swings towards the slot""")

# car estimates: the foot parts, and the D the foot is drawn for
rep("""  for name in ("mounting plate", "spring's coil and spool"):
    P_ = A.W(A.fixed(0.0)[name])
    for cn, c in car:
      rows.append(("fixed", name, cn, gap(P_, c, 40.0)))
  return rows""",
    """  for name in ("mounting plate", "spring's coil and spool", "foot bar (anywhere along the window)"):
    P_ = A.W(A.fixed(0.0)[name])
    for cn, c in car:
      rows.append(("fixed", name, cn, gap(P_, c, 40.0)))
  return rows


def foot_fit(D: float) -> dict:
  \"\"\"Where the cover's screw and its underside fall against the foot and its window for one value of carscene.D: the
  screw inside the window (with the mount turned up to 3 degrees either way, and the screw's place 4 mm off either
  way), and how many shims fill the gap from the foot's top to the underside.\"\"\"
  import carscene as CS
  sc = CS.CarScene(D)
  cup = sc.p["CUP"]
  r_cup = math.hypot(cup[0], sc.cover_bottom)
  swing = r_cup * math.sin(math.radians(SP.MOUNT_ADJ_S[0]))        # the window moves this far across when the mount turns
  tol = 4.0
  x_room = (cup[0] - tol - swing - S.WINDOW_X[0], S.WINDOW_X[1] - (cup[0] + tol + swing))
  z_room = (cup[2] - tol - S.WINDOW_Z[0], S.WINDOW_Z[1] - (cup[2] + tol))
  gap_y = sc.cover_bottom - S.FOOT_Y[1]
  return {"D": D, "cover's front edge behind the back of the round part (mm)": round(-sc.cover_front_z - 17.7, 1),
          "screw (x, z)": (round(float(cup[0]), 1), round(float(cup[2]), 1)), "underside y": round(sc.cover_bottom, 1),
          "room left in the window across (mm, either way)": tuple(round(v, 1) for v in x_room),
          "room left along (mm, either way)": tuple(round(v, 1) for v in z_room),
          "gap over the foot (mm)": round(gap_y, 1), "shims": int(round(gap_y / S.SHIM_T))}""")
p.write_text(s)
print("ok")
EOF
grep -n "^import\|^from" sideassembly.py | head; grep -n "slideparts\|SP\." sideassembly.py | head -3