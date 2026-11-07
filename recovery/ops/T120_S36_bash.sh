cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/mockup && python3 - <<'EOF'
p='export.py'
s=open(p).read()
old='''  ("dash", "car", "dash", dash + hood),
'''
assert s.count(old)==1
s=s.replace(old,'')
s=s.replace('''dash = box(-420, 420, -380, 60, P.DASH_Z - 40.0, P.DASH_Z) - A.covers().scale((1.04, 1.04, 1.0))
hood = box(-260, 260, 60, 150, P.DASH_Z - 40.0, P.DASH_Z + 60.0)
''','')
open(p,'w').write(s)

p='page.src.html'
s=open(p).read()
def rep(old,new,cnt=1):
    global s
    assert s.count(old)==cnt,(old[:70],s.count(old))
    s=s.replace(old,new)
rep('''          <button type="button" data-view="right">From the right</button>
          <button type="button" data-view="behind">Behind the wheel</button>
          <button type="button" data-view="driver">Driver's seat</button>
          <button type="button" data-view="under">Underneath</button>
          <button type="button" data-view="close">Gear on the teeth</button>
          <button type="button" data-view="plate">Plate and arm</button>''',
'''          <button type="button" data-view="behind">Behind the wheel</button>
          <button type="button" data-view="driver">Driver's seat</button>
          <button type="button" data-view="right">From the right</button>
          <button type="button" data-view="above">From above</button>
          <button type="button" data-view="close">Gear on the teeth</button>
          <button type="button" data-view="under">Underneath</button>''')
rep('''    right: { eye: [610, 150, -30], target: [95, -45, -95] },
    behind: { eye: [430, 175, -330], target: [120, -15, -60] },
    driver: { eye: [-30, 330, 660], target: [45, -15, -50] },
    under: { eye: [330, -430, 60], target: [70, -75, -150] },
    close: { eye: [320, 120, -250], target: [165, -12, -42] },
    plate: { eye: [420, -260, -60], target: [60, -95, -160] }''',
'''    behind: { eye: [430, 175, -330], target: [120, -15, -60] },
    driver: { eye: [-30, 330, 660], target: [45, -15, -50] },
    right: { eye: [720, 210, 60], target: [100, -40, -100] },
    above: { eye: [150, 760, 140], target: [90, -20, -90] },
    close: { eye: [365, 150, -305], target: [165, -12, -42] },
    under: { eye: [330, -430, 60], target: [70, -75, -150] }''')
rep('''  S.cam = camFrom(VIEWS.right);
  document.querySelector('#views button[data-view="right"]').setAttribute("aria-pressed", "true");''',
'''  S.cam = camFrom(VIEWS.behind);
  document.querySelector('#views button[data-view="behind"]').setAttribute("aria-pressed", "true");''')
rep('''    { text: "Back teeth", group: "wheel", point: () => {
      const a = (S.set === "long" ? 34 : 12) * D2R, r = 167; return [r * Math.cos(a), r * Math.sin(a), -27];
    } },''',
'''    { text: "Back teeth", group: "wheel", point: () => {
      // stays near the top of the teeth as the wheel turns, and always on them
      const reach = teethSet().reach - 3;
      const a = Math.max(-reach, Math.min(reach, (S.set === "long" ? 30 : 10) - S.w)) * D2R, r = 167;
      return [r * Math.cos(a), r * Math.sin(a), -27];
    } },''')
rep('''    if (S.alpha !== S.alphaTo) {
      const step = 140 * (1 / 60);''',
'''    const dt = Math.min(0.1, (now - (S.lastNow || now)) / 1000);
    S.lastNow = now;
    if (S.alpha !== S.alphaTo) {
      const step = 140 * Math.max(dt, 1 / 120);''')
rep('''<p class="fine">Drawn from the CAD files that make the printed parts. The steering wheel's hub and spokes, the column covers, the stalks and the dash are rough shapes from your photos, not measurements.</p>''',
'''<p class="fine">Drawn from the CAD files that make the printed parts. The steering wheel's hub and spokes, the column covers and the stalks are rough shapes from your photos, not measurements; the dash is left out so it doesn't hide the mount.</p>''')
rep('''<label class="check"><input type="checkbox" id="showCar" checked> Column covers, stalks and dash</label>''',
'''<label class="check"><input type="checkbox" id="showCar" checked> Column covers and stalks</label>''')
open(p,'w').write(s)
print('ok')
EOF
PYTHONPATH=/home/claude/pylib timeout 1500 python3 export.py . 2>&1 | tail -1 && python3 - <<'EOF'
s=open('page.src.html').read()
info=open('data.json').read()
assert '</' not in info
out=s.replace('/*MESHINFO*/', info)
open('back-teeth-mockup.html','w').write(out)
print(len(out))
EOF
ls -la back-teeth-mockup.html data.bin