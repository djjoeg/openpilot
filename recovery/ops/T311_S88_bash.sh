python3 - <<'EOF'
p='viewer3d.py'; s=open(p).read()
a='''  chip_rgb = {}
  for it in items:'''
assert a in s
s=s.replace(a,'''  chip_rgb = {"motor": [0.4, 0.41, 0.45]}        # the motor's black would read as an empty dot on a dark page
  for it in items:''')
open(p,'w').write(s)
EOF
ruff check viewer3d.py --output-format concise && export PYTHONPATH=/home/claude/pylib && timeout 600 python3 viewer3d.py && cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/v3d && python3 wrap.py /home/claude/deliver/hardware/report/arm-3d.html page2.html && timeout 120 node speck.js && python3 -c "
from PIL import Image
ims=[Image.open(f'sp-{n}.png').resize((520,280), Image.NEAREST) for n in ('all','noteeth')]
o=Image.new('RGB',(520*2+10,280),'white')
for i,im in enumerate(ims): o.paste(im,(i*530,0))
o.save('sp-sheet2.png')"