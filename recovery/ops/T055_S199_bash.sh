python3 - <<'EOF'
p='margins.py'
s=open(p).read()
old='''    if r["kind"] == "condition":
      f += " (without one of this build's measures, below)"'''
new='''    if r["kind"] == "condition":
      f += ", which is why the build includes the step under check"'''
assert old in s; s=s.replace(old,new)
old='''  # ----- the mount -----
  g = "Mount"
  sideways = ft_most
  rows.append(row(g, "The arm's joints and the dash clamp hold", f"up to {sideways:.0f} N sideways at the motor gear (its most "
                  "push), about 30 N up (the spring) and 16 N down (the parts' weight on a bump, 3 times gravity)",
                  "friction in bolted printed joints: can't be worked out reliably", float("nan"),
                  "proof test", kind="test",
                  check=f"proof pulls with a luggage scale at the motor, lever up: {math.ceil(1.5 * sideways / 9.81 * 2) / 2:.1f} kg "
                        "sideways each way and 5 kg up and down; nothing may move"))
'''
new='''  # ----- the mount -----
  g = "Mount"
  sideways = ft_most
  up = spring["presses_roller_on_rolling_band_N"] + ft_most * math.tan(phi + math.atan(RUB_GREASED))
  down = MOUNTED_KG * 9.81 * BUMP_G

  def kg(n):
    return math.ceil(1.5 * n / 9.81 * 2) / 2

  rows.append(row(g, "The arm's joints and the dash clamp hold", f"up to {sideways:.0f} N sideways at the motor gear (its most "
                  f"push), {up:.0f} N up (the spring and the teeth pushing apart) and {down:.0f} N down (the parts' weight "
                  f"on a bump, {BUMP_G:g} times gravity)", "friction in bolted printed joints: can't be worked out reliably",
                  float("nan"), "proof test", kind="test",
                  check=f"proof pulls with a luggage scale at the motor, lever up: {kg(sideways):.1f} kg sideways each way, "
                        f"{kg(up):.1f} kg up and {kg(down):.1f} kg down (1.5 times each load); nothing may move"))
'''
assert old in s; s=s.replace(old,new)
old='''ZIP_TIE_N, TAPE_RUB = 50.0, 0.5   # a zip tie pulled tight by hand, and silicone tape's grip: estimates
'''
new='''ZIP_TIE_N, TAPE_RUB = 50.0, 0.5   # a zip tie pulled tight by hand, and silicone tape's grip: estimates
MOUNTED_KG = 0.55       # the motor, its board and the printed parts on the arm
BUMP_G = 3.0            # a hard bump, in times gravity (an estimate)
'''
assert old in s; s=s.replace(old,new)
open(p,'w').write(s)
EOF
S=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/m1 && rm -rf $S && mkdir -p $S && PYTHONPATH=/home/claude/pylib python3 accord_lka_parts.py --out $S/stl --report $S/report --no-pictures > $S/run.log 2>&1; echo exit $?; grep -n "Mount" -A 5 $S/report/parts_report.txt | head -8; grep -n "dry teeth" -A1 $S/report/parts_report.txt