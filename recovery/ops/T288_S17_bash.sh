python3 - <<'EOF'
p = "carphoto.py"
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)
rep("hub = CrossSection.square((190.0, 130.0), center=True).offset(28.0, circular_segments=48).extrude(70.0).translate((0.0, 12.0, -45.0))",
    "hub = CrossSection.square((160.0, 110.0), center=True).offset(25.0, circular_segments=48).extrude(70.0).translate((0.0, 12.0, -45.0))")
rep("""KEY = (0.35, 0.80, -0.45)        # sunlight through the windshield: from above, in front, a little from the right
FILL = (-0.80, 0.40, 0.45)       # the driver's window""",
    """KEY = (-0.45, 0.75, 0.48)        # daylight through the driver's window: from above, the left and behind""")
rep("""    cam = PR.Camera(v["eye"], v["target"], v["up"], v["fov"], size)
    img = PR.render(sc, cam, KEY, sky_up=WORLD_UP, fill_dir=FILL, ss=2, exposure=1.15)""",
    """    cam = PR.Camera(v["eye"], v["target"], v["up"], v["fov"], size)
    fill = np.asarray(v["eye"]) - np.asarray(v["target"])      # a soft light from where the picture is taken
    img = PR.render(sc, cam, KEY, sky_up=WORLD_UP, fill_dir=fill, fill_power=0.45, ss=2, exposure=1.15)""")
open(p, "w").write(s)
print("ok")
EOF
(time PYTHONPATH=/home/claude/pylib timeout 1800 python3 carphoto.py 640) 2>&1 | tail -6