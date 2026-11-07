cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/popmock && python3 - <<'EOF'
s = open('pop.src.html').read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:70], s.count(old))
    s = s.replace(old, new)
rep("""          <button type="button" data-view="under">Underneath</button>""",
    """          <button type="button" data-view="under">Underneath</button>
          <button type="button" data-view="key">The key</button>
          <button type="button" data-view="keyside">Key, from the side</button>""")
rep("""    behind: { eye: [420, 230, -360], target: [110, -10, -80] },""",
    """    behind: { eye: [420, 230, -360], target: [110, -10, -80] },
    key: { eye: [INFO.key.centre[0] + 330 * INFO.key.n[0], INFO.key.centre[1] + 330 * INFO.key.n[1] + 40, INFO.key.centre[2] + 330 * INFO.key.n[2]], target: INFO.key.centre },
    keyside: { eye: [INFO.key.centre[0] + 120, INFO.key.centre[1] + 380, INFO.key.centre[2] + 60], target: [INFO.key.centre[0] - 10, INFO.key.centre[1], INFO.key.centre[2] + 20] },""")
rep("""<strong>From your photos:</strong> the key sits at about 3:25, around 108 mm behind the middle of the grip, right where this mount is.""",
    """<strong>From your photos:</strong> the key sits at about 3:25, 100–145 mm behind the middle of the grip, right where this mount is.""")
open('pop.src.html', 'w').write(s)
e = open('pop_export.py').read()
old = '''  "key": {"centre": [float(v) for v in CR.key_centre()], "head": [float(v) for v in (CR.key_centre() + 45.0 * CR._frame(CR.KEY_CLOCK_DEG, CR.KEY_TILT_DEG)[0])]},'''
new = '''  "key": {"centre": [float(v) for v in CR.key_centre()], "head": [float(v) for v in (CR.key_centre() + 45.0 * CR._frame(CR.KEY_CLOCK_DEG, CR.KEY_TILT_DEG)[0])],
          "n": [float(v) for v in CR._frame(CR.KEY_CLOCK_DEG, CR.KEY_TILT_DEG)[0]]},'''
assert old in e
e = e.replace(old, new)
open('pop_export.py', 'w').write(e)
print('ok')
EOF
PYTHONPATH=/home/claude/pylib timeout 1700 python3 pop_export.py . 2>&1 | tail -3 && python3 build.py && cat > shot6.py <<'EOF'
import asyncio, subprocess, sys, time
from playwright.async_api import async_playwright
PORT = 8772
srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.0)
async def main():
  async with async_playwright() as p:
    b = await p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    logs = []
    pg = await b.new_page(viewport={"width": 1400, "height": 860})
    pg.on("console", lambda m: logs.append(f"{m.type}: {m.text}") if "GPU stall" not in m.text and "TUNNEL" not in m.text else None)
    pg.on("pageerror", lambda e: logs.append(f"pageerror: {e}"))
    await pg.goto(f"http://127.0.0.1:{PORT}/preview.html")
    await pg.wait_for_timeout(5000)
    await pg.click('#views button[data-view="key"]')
    await pg.wait_for_timeout(1800)
    await pg.screenshot(path="x-key.png")
    await pg.click("#motorOff")
    await pg.wait_for_timeout(6000)
    await pg.click("#showRoom")
    await pg.wait_for_timeout(600)
    await pg.screenshot(path="x-key-off.png")
    await pg.click('#views button[data-view="keyside"]')
    await pg.wait_for_timeout(1800)
    await pg.screenshot(path="x-keyside-off.png")
    await pg.click("#motorOn")
    await pg.click("#showRoom")
    await pg.wait_for_timeout(6000)
    await pg.screenshot(path="x-keyside-on.png")
    print("\n".join(logs[:30]) or "no console output")
    await b.close()
asyncio.run(main())
srv.terminate()
EOF
timeout 300 python3 shot6.py