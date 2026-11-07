python3 - <<'EOF'
p = "faceparts.py"
s = open(p).read()
s = s.replace("from cadlib import box, clean, cyl, cyl_x, cyl_y, extrude_x, prism_x, revolve, sector, union",
              "from cadlib import box, clean, cyl, cyl_x, cyl_y, prism_x, revolve, sector, union")
s = s.replace("""    def span(a, b):
      return (a, b) if sgn > 0 else (-b, -a)""", """    def span(a, b, s=sgn):
      return (a, b) if s > 0 else (-b, -a)""")
open(p, "w").write(s)
p = "faceassembly.py"
s = open(p).read()
s = s.replace("""  car, mount = A.car_parts(dash), A.mount_parts()
  cp = dict(car)
  pairs = {""", """  car, mount = A.car_parts(dash), A.mount_parts()
  pairs = {""")
open(p, "w").write(s)
EOF
ruff check --line-length 140 --fix faceparts.py faceassembly.py 2>&1 | tail -3; sed -n 185,195p faceparts.py