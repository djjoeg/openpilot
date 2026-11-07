python3 - <<'EOF'
p='accord_lka_parts.py'
s=open(p).read()
s=s.replace('''import params as P  # noqa: E402
import margins as MG  # noqa: E402
''','''import params as P  # noqa: E402
''')
old='''  import wheelparts as WP    # noqa: E402
'''
new='''  import wheelparts as WP    # noqa: E402
  import margins as MG       # noqa: E402
'''
assert old in s; s=s.replace(old,new,1)
open(p,'w').write(s)
EOF
sed -n 76,90p accord_lka_parts.py; grep -n "def write_text\|def report_text\|MG\." accord_lka_parts.py | head