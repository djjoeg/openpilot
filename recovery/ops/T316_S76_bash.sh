python3 - <<'EOF'
p='viewer3d_page.html'; s=open(p).read()
a='''  // ---- the steps ----
  const slider = $("assy");'''
assert a in s
s=s.replace(a,'''  // ---- the steps ----
  const slider = $("assy");
  slider.max = String(NSTEP * 100);
  slider.value = String(NSTEP * 100);''')
s=s.replace('''<input type="range" id="assy" min="0" max="700" step="1" value="700" aria-label="Apart to together">''','''<input type="range" id="assy" min="0" max="800" step="1" value="800" aria-label="Apart to together">''')
open(p,'w').write(s)
EOF
grep -n 'id="assy"' viewer3d_page.html; cat /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v3d/rightcheck2.log 2>/dev/null | head