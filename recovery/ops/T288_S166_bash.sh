python3 - <<'EOF'
p = 'incar.py'
s = open(p).read()
a = s.index('def make(name: str, ss: int = 2, out_dir: str = REPORT_DIR) -> str:')
new = '''def make(name: str, ss: int = None, out_dir: str = REPORT_DIR) -> str:
  spec = PHOTOS[name]
  ss = ss or spec.get("ss", 2)
  cam = camera(spec["cam"])
  photo = np.asarray(Image.open(UPLOADS + spec["file"] + "-image.jpg").convert("RGB"))
  ps = parts(spec["wheel"])
  gain, X, dist = brightness(cam, photo, spec["light"], spec["ref"])
  print(f"photo {name}: gain {np.round(gain, 3)} (reference patch at {np.round(X, 0)}, {dist:.0f} mm from the lens)")
  box = window(cam, ps)
  print(f"   window {box}, {ss} x {ss} samples a pixel")
  occ = occluders(cam, OPENINGS_00 if name == "00" else None)
  L = PC.layers(cam, ps, occ, box, ss=ss, lights=lights(cam, spec["light"]))
  key = CS.CarScene(D=128.2).key
  focus = float(np.linalg.norm(key - cam.eye)) if spec["light"] == "flash" else 430.0     # on the key / on the wheel
  res = PC.composite(photo, L, gain, focus=focus, aperture_mm=3.0, f_px=cam.f, noise=0.008)
  os.makedirs(out_dir, exist_ok=True)
  path = os.path.join(out_dir, f"in-the-car-photo-{name}.jpg")
  Image.fromarray(res).save(path, quality=92)
  if spec.get("pair"):
    pair(photo, res, spec["pair"], os.path.join(out_dir, f"in-the-car-photo-{name}-before-after.jpg"))
  return path


def pair(before, after, box, path, width=2400):
  """Your photo and the same with the parts, side by side, cropped to box = (x0, y0, x1, y1)."""
  from PIL import ImageDraw, ImageFont
  x0, y0, x1, y1 = box
  a = Image.fromarray(before[y0:y1, x0:x1])
  b = Image.fromarray(after[y0:y1, x0:x1])
  w = (width - 30) // 2
  h = int(round(a.height * w / a.width))
  a, b = a.resize((w, h), Image.LANCZOS), b.resize((w, h), Image.LANCZOS)
  out = Image.new("RGB", (width, h + 70), (24, 24, 26))
  out.paste(a, (10, 60))
  out.paste(b, (20 + w, 60))
  d = ImageDraw.Draw(out)
  try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
  except OSError:
    font = ImageFont.load_default()
  d.text((14, 14), "your photo", fill=(235, 235, 235), font=font)
  d.text((24 + w, 14), "with the parts drawn in", fill=(235, 235, 235), font=font)
  out.save(path, quality=92)


def main(argv):
  names = argv[1:] or list(PHOTOS)
  for n in names:
    print(make(n))


if __name__ == "__main__":
  sys.exit(main(sys.argv))
'''
s = s[:a] + new
s = s.replace('''  "00": dict(file="273a348a", cam=cam00, wheel=-17.0, light="day",''', '''  "00": dict(file="273a348a", cam=cam00, wheel=-17.0, light="day", ss=2, pair=(640, 1180, 1932, 2380),''')
s = s.replace('''  "33": dict(file="818fd797", cam=33, wheel=0.0, light="flash",''', '''  "33": dict(file="818fd797", cam=33, wheel=0.0, light="flash", ss=1, pair=(0, 0, 1932, 2576),''')
s = s.replace('''  "26": dict(file="a5f478e3", cam=26, wheel=0.0, light="flash",''', '''  "26": dict(file="a5f478e3", cam=26, wheel=0.0, light="flash", ss=1,''')
open(p, 'w').write(s)
print('ok')
EOF
grep -n '"00": dict\|"33": dict\|"26": dict' incar.py