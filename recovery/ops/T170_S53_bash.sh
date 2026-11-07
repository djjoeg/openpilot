python3 - <<'EOF'
import pathlib
p = pathlib.Path("sidebuild.py")
s = p.read_text()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)
rep("""  def scene(s):
    mv, fx, W = A.movers(s, lever_deg=0.0 if s == 0.0 else S.SLOT_DEG), A.fixed(s), A.W
    sp = S.spring_parts(s)
    return [(grip, C["grip"]), (teeth, C["teeth"]), (W(mv["motor, board and plugs"]), C["motor"]), (W(mv["motor bracket"]), C["bracket"]),
            (W(mv["gear"]), C["gear"]), (W(mv["block"]), C["block"]), (W(parts["plate"]), C["plate"]), (W(parts["rail"]), C["rail"]),
            (W(mv["lever"]), C["lever"]),
            (W(fx["switch"] + fx["switch's lever and roller"]), C["switch"]), (W(fx["spring's coil and spool"] + sp["strip"]), C["spring"])]""",
    """  ff = SA.foot_fit(sum(S.D_FOOT) / 2)
  sx, sz = ff["screw (x, z)"]
  bar = S.foot_bar(sz)
  screw = S.cover_screw(sx, sz, ff["underside y"])
  shims = union([S.foot_shim().translate((0, k * S.SHIM_T, 0)) for k in range(ff["shims"])]) if ff["shims"] else None

  def scene(s):
    mv, fx, W = A.movers(s, lever_deg=0.0 if s == 0.0 else S.SLOT_DEG), A.fixed(s), A.W
    sp = S.spring_parts(s)
    out = [(grip, C["grip"]), (teeth, C["teeth"]), (W(mv["motor, board and plugs"]), C["motor"]), (W(mv["motor bracket"]), C["bracket"]),
           (W(mv["gear"]), C["gear"]), (W(mv["block"]), C["block"]), (W(parts["plate"]), C["plate"]), (W(parts["rail"]), C["rail"]),
           (W(mv["lever"]), C["lever"]), (bar, C["rail"]), (screw, C["block"]),
           (W(fx["switch"] + fx["switch's lever and roller"]), C["switch"]), (W(fx["spring's coil and spool"] + sp["strip"]), C["spring"])]
    if shims is not None:
      out.append((shims, C["plate"]))
    return out""")
rep("""    "mounting plate (fixed), the rail on its far side": (cpt(S.X_PL[0], 0.0, -60.0), (-170, -40)),""",
    """    "mounting plate (fixed), the rail on its far side": (cpt(S.X_PL[0], 0.0, -60.0), (-170, -40)),
    "the plate's foot: under the column cover, on its screw": (np.array([sum(S.FOOT_X) / 2, S.FOOT_Y[1], sum(S.FOOT_Z) / 2]), (-150, 60)),""")
rep("""  pr = [(n.replace("side-", "").replace("-", " "), m, r) for n, (m, r, _, _) in printed_parts(parts).items() if "teeth" not in n]""",
    """  pr = [(n.replace("side-", "").replace("-", " "), m, r) for n, (m, r, _, _) in printed_parts(parts).items()]""")
rep("""         suptitle="The new printed parts, each as it sits on the print bed (the steering wheel teeth are the slide mount's, "
                  "with pointed tooth ends)", size=(700, 600), cols=3)""",
    """         suptitle="The printed parts, each as it sits on the print bed (the three steering wheel teeth sets are not shown: "
                  "one piece, with 10, 14 or 18 teeth)", size=(700, 600), cols=3)""")
rep("""from cadlib import on_bed, revolve, write_stl""", """from cadlib import on_bed, revolve, union, write_stl""")
p.write_text(s)
print("ok")
EOF
/home/claude/bin/ruff check --output-format concise sideparts.py sideassembly.py sidebuild.py 2>&1 | tail -8