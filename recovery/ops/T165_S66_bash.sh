sed -i 's/(F - 11, 78), (204, 57), color=C\["lever"\])/(F - 11, 78), (195, 57), color=C["lever"])/' sidebuild.py && grep -n 'note("lever' sidebuild.py && PYTHONPATH=/home/claude/pylib python3 -c "
import sidebuild as B, sideassembly as SA
A = SA.SideAssembly(SA.build_parts())
B.drawing(A, '/home/claude/deliver/hardware/report/side-slide-drawing.png')
" && python3 -c "
from PIL import Image
im = Image.open('/home/claude/deliver/hardware/report/side-slide-drawing.png'); im.crop((60,100,560,420)).save('/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/side/drawing-crop.png')"