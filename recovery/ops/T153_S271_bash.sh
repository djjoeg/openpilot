cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slidemock && python3 - <<'EOF'
import pathlib
p = pathlib.Path("slide_export.py")
s = p.read_text()
a = '''  "labels": {"block": [-31.0, 50.0, 24.0], "lever": [-47.0, SP.PIVOT[0] + 6.0, SP.PIVOT[1] - 6.0], "motor": [0.0, 21.0, -20.0],
             "gear": [0.0, 0.0, 22.0], "cap": [0.0, 0.0, -51.0], "springs": [-31.0, 76.0, 15.0], "rods": [-31.0, 60.0, -15.0]},
}'''
b = '''  "labels": {"block": [-31.0, 50.0, 24.0], "lever": [-47.0, SP.PIVOT[0] + _PAD * math.cos(_HA), SP.PIVOT[1] + _PAD * math.sin(_HA)],
             "motor": [0.0, 21.0, -20.0], "gear": [0.0, 0.0, 22.0], "cap": [0.0, 0.0, -51.0], "springs": [-31.0, 76.0, 15.0],
             "rods": [-31.0, 60.0, -15.0], "pusher": [SP.PUSHER_X, SP.PUSH_FACE_STOP + 2.0, SP.NOSE_HALF[1]]},
  # from the checks (dsweep.py, mount at 5:20): the board's plug to the column cover slid back, the motor to the back cover
  "gaps": {"107": {"plug_cover": "touches", "back_cover": "7.1 mm"}, "113": {"plug_cover": "2.2 mm", "back_cover": "6.2 mm"},
           "120": {"plug_cover": "6.6 mm", "back_cover": "4.8 mm"}},
}'''
assert s.count(a) == 1
s = s.replace(a, b)
a2 = "latch = SA.latch_numbers()\n"
b2 = "latch = SA.latch_numbers()\n_HA = math.atan2(SP.HANDLE_ON[1], SP.HANDLE_ON[0])\n_PAD = math.hypot(*SP.HANDLE_ON) - 3.5\n"
assert s.count(a2) == 1
s = s.replace(a2, b2)
p.write_text(s)
q = pathlib.Path("slide.src.html")
t = q.read_text()
assert t.count('s["back cover rim r, z"]') == 1
q.write_text(t.replace('s["back cover rim r, z"]', 's["back cover edge r, z"]'))
print("ok")
EOF
export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache && timeout 900 python3 slide_export.py . > export.log 2>&1; tail -2 export.log && python3 -c "
import json; d=json.load(open('data.json')); print(d['labels']['lever'], d['gaps']['113'], d['cars']['113']['summary'].get('back cover edge r, z'))" && python3 build.py