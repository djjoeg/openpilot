python3 - <<'EOF'
p = "stiffness.py"
s = open(p, encoding="utf-8").read()
a = s[s.index("def main() -> int:"):s.index('if __name__ == "__main__":')]
b = '''def main() -> int:
  ok = True
  cases = CASES[:1] if "quick" in sys.argv[1:] else CASES
  k = GRIP_TEST / TORQUE
  for dx, dz, label in cases:
    print(f"{label} (the arm {dx:+.1f} across, the motor {dz:+.0f} along the column):")
    for with_plate in (False, True):
      for name, d in solve(with_plate, dx, dz).items():
        deeper, out_ = max(d["in"], 0.0), max(-d["in"], 0.0)
        good = deeper <= LIMIT_IN and out_ <= LIMIT_OUT
        ok = ok and good
        print(f"    {name}: the gear {d['in']:+.2f} mm along the column (+ deeper into the teeth), {d['rim']:+.2f} along "
              f"the rim, the motor turned {d['motor turned deg']:.2f} deg; in the grip test {k * d['in']:+.2f} mm  "
              f"{'pass' if good else 'FAIL'}")
  print("PASS" if ok else "FAIL")
  return 0 if ok else 1


'''
s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok")
EOF
cd /home/claude/deliver/hardware/cad && (time PYTHONPATH=/home/claude/pylib python3 stiffness.py) > /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6/stiff1.txt 2>&1; cat /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v6/stiff1.txt