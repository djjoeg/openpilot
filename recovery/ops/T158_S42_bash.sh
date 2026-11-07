cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slidemock && cp slide.src.html slide.src.v1.html && python3 - <<'EOF'
import pathlib
p = pathlib.Path("slide.src.html")
s = p.read_text()
reps = [
("""<p>The motor sits behind the steering wheel at about 5:20, its gear on the teeth on the back of the grip. Swing the latch lever back and two springs slide the motor 5.5 mm back along the column, clear of the teeth. Swing it forward and it slides on, and the lever stays there until you swing it back. A switch cuts the motor's power unless it's all the way on.</p>""",
 """<p>The motor sits behind the steering wheel at about 5:20, its gear on the teeth on the back of the grip. Swing the latch lever back and two springs slide the motor 8.25 mm forward along the column, towards the nose: the gear leaves the teeth and the motor gets out of the way of your fingers when you hold the grip there. Swing the lever towards you and the motor slides back on; the lever stays there until you swing it back. A switch cuts the motor's power unless it's all the way on.</p>"""),
("""<li>How far the key sits behind the back of the grip. From about 112 mm on, everything clears. Nearer than about 109 mm, the board's plug hits the column cover when the motor slides back.</li>""",
 """<li>How far the key sits behind the back of the grip. From about 115 mm on, everything clears. Nearer than about 113 mm, the board's plug hits the column cover when the motor slides forward. If yours is nearer, the slide can tilt outward, forward and away from the column, where there's more room.</li>"""),
("""<button type="button" id="motorOff" aria-pressed="false">Off<small>slid back 5.5 mm</small></button>""",
 """<button type="button" id="motorOff" aria-pressed="false">Off<small>slid forward 8.25 mm</small></button>"""),
("""<p class="note">Swing the handle towards you: its cam pushes against a spring-loaded pusher in the block and slides the motor on. The cam's flat sits on the pusher, so it stays on. Swing it back past the click and two springs pull the motor off.</p>""",
 """<p class="note">Swing the handle towards you: its cam pushes against a spring-loaded pusher in the block and slides the motor on. The cam's flat sits on the pusher, so it stays on. Swing it back past the click and two springs pull the motor off.</p>
        <p class="note">Why forward and not in towards the middle of the wheel: that way the gear would have to slide 17 mm just to leave the teeth, and the motor's back end hits the cover on the back of the steering wheel after 7.5 mm.</p>"""),
("""<button type="button" data-d="107" aria-pressed="false">107 mm<small>plug hits</small></button>
          <button type="button" data-d="113" aria-pressed="true">113 mm<small>clears</small></button>
          <button type="button" data-d="120" aria-pressed="false">120 mm<small>clears</small></button>""",
 """<button type="button" data-d="110" aria-pressed="false">110 mm<small>plug hits</small></button>
          <button type="button" data-d="115" aria-pressed="true">115 mm<small>clears</small></button>
          <button type="button" data-d="120" aria-pressed="false">120 mm<small>clears</small></button>"""),
("""<p class="note">The block's slots let the whole mount turn from 5:14 to 5:26 when you fit it. Stay at 5:24 or earlier: further towards 6, the motor's board gets into the room your fingers need on the adjustment tab.</p>""",
 """<p class="note">The block's slots let the whole mount turn from 5:14 to 5:26 when you fit it. Keep it between 5:20 and 5:24. Later than 5:24 (towards 6), the motor's board gets into the room your fingers need on the adjustment tab. Earlier than 5:20, its plug comes closer to the column cover when it slides forward.</p>"""),
("""          <dt>The pusher holds the gear in with (its 50 N, less the pull springs, the motor's weight and hard braking)</dt><dd>34 N</dd>
          <dt>… against lane keeping's hardest push apart at the teeth</dt><dd>1.99×</dd>
          <dt>… against the push at the safety limit</dt><dd>1.73×</dd>
          <dt>Handle, swinging it on</dt><dd>10 N at most</dd>
          <dt>… with the teeth tip to tip</dt><dd>34 N</dd>
          <dt>Swinging it off, over the click</dt><dd>8 N</dd>
          <dt>Pusher's spring at its most, of what it takes</dt><dd>140 of 199 N</dd>
          <dt>Pull springs</dt><dd>10.5 N on · 4.1 off</dd>
          <dt>Gear clear of the teeth, slid back</dt><dd>2 mm</dd>
          <dt>Lever clear of the teeth as it swings, wheel anywhere</dt><dd>2.7 mm</dd>
          <dt>Gear's free play, at the steering wheel</dt><dd>0.17°</dd>
          <dt>Power switch</dt><dd>on in the last 1 mm · off 3 mm back</dd>
          <dt>Board's plug to the column cover, slid back</dt><dd id="gapPlug">2.2 mm</dd>
          <dt>Motor to the wheel's back cover</dt><dd id="gapBack">6.2 mm</dd>
          <dt>Motor to your fingers on the adjustment tab</dt><dd>5.1 mm</dd>""",
 """          <dt>The pusher holds the gear in with (its 50 N, less the pull springs, the motor's weight and hard braking)</dt><dd>33 N</dd>
          <dt>… against lane keeping's hardest push apart at the teeth</dt><dd>1.90×</dd>
          <dt>… against the push at the safety limit</dt><dd>1.66×</dd>
          <dt>Handle, swinging it on</dt><dd>11 N at most</dd>
          <dt>… with the teeth tip to tip</dt><dd>38 N</dd>
          <dt>Swinging it off, over the click</dt><dd>8 N</dd>
          <dt>Pusher's spring at its most, of what it takes</dt><dd>139 of 199 N</dd>
          <dt>Pull springs</dt><dd>12 N on · 5.4 off</dd>
          <dt>Slid forward: the nearest part to your fingers round the grip</dt><dd id="gapFingers">1.6 mm</dd>
          <dt>Slid forward: the gear clear of the teeth</dt><dd>4.5 mm</dd>
          <dt>Lever clear of the teeth as it swings, wheel anywhere</dt><dd>2.7 mm</dd>
          <dt>Gear's free play, at the steering wheel</dt><dd>0.17°</dd>
          <dt>Power switch</dt><dd>on in the last 1 mm · off 3 mm forward</dd>
          <dt>Board's plug to the column cover, slid forward</dt><dd id="gapPlug">1.2 mm</dd>
          <dt>Motor to the wheel's back cover</dt><dd id="gapBack">6.2 mm</dd>
          <dt>Motor to your fingers on the adjustment tab</dt><dd>5.1 mm</dd>"""),
("""    else if (!S.on) { state = "off"; text = "Motor off · slid back 5.5 mm, its gear 2 mm clear of the teeth, no power"; }""",
 """    else if (!S.on) { state = "off"; text = "Motor off · slid forward 8.25 mm, out of your fingers' way, no power"; }"""),
("""    document.getElementById("gapPlug").textContent = g.plug_cover;
    document.getElementById("gapBack").textContent = g.back_cover;""",
 """    document.getElementById("gapPlug").textContent = g.plug_cover;
    document.getElementById("gapBack").textContent = g.back_cover;
    document.getElementById("gapFingers").textContent = g.fingers;"""),
("""    on: true, lever: 0, off: 0, back: INFO.lever[0][2], t2t: false, w: 0, adj: 0, D: "113", gearDeg: INFO.mesh_phase,""",
 """    on: true, lever: 0, off: 0, back: INFO.lever[0][2], t2t: false, w: 0, adj: 0, D: INFO.ds[1], gearDeg: INFO.mesh_phase,"""),
]
for a, b in reps:
  assert s.count(a) == 1, a[:80]
  s = s.replace(a, b)
p.write_text(s)
print("ok")
EOF
grep -n "slid back\|back along\|5\.5 mm" slide.src.html | head; sed -i 's/^DS = (107.0, 113.0, 120.0)/DS = (110.0, 115.0, 120.0)/' slide_export.py && grep -n "^DS" slide_export.py