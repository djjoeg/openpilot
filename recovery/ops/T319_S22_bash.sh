cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/fea && python3 - <<'EOF'
for fn in ('armfea.py', 'armfea_full.py'):
    s = open(fn).read()
    old = '''  umax = np.abs(u.reshape(-1, 3)).max()'''
    new = '''  umax = np.abs(u.reshape(-1, 3)).max()
  if "save" in sys.argv[4:]:
    np.savez_compressed(f"sol_{VARIANT}_{H}.npz", xyz=xyz, u=u.reshape(-1, 3), en=en, fixed=fixed, load=load)'''
    assert s.count(old) == 1
    s = s.replace(old, new)
    open(fn, 'w').write(s)
print('ok')
EOF
sleep 1; cat aligned125.log