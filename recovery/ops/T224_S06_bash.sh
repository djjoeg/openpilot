sed -i 's/  FR.FONT.setdefault("<", ("010", "100", "111", "100", "010"))/  import slotplate as SL\n  SL.FONT.setdefault("<", ("010", "100", "111", "100", "010"))/' armmount.py && PYTHONPATH=/home/claude/pylib timeout 900 python3 armmount.py 2>&1 | tail -5 && PYTHONPATH=/home/claude/pylib timeout 600 python3 - <<'EOF'
import sys; sys.path.insert(0,'.')
import armmount as A, midteeth as MT, numpy as np
mg=A.motor_and_gear()
plate=A.plate_to_wheel(A.frame_plate_v3())
parts={"plate":plate,"arm":A.arm(),"bracket":A.bracket(),"motor":mg["motor"],"board":mg["board"],"gear":mg["gear"]}
teeth=MT.mid_teeth(MT.MidTeeth(n_teeth=10)).rotate((0,0,A.MOUNT_DEG))
names=list(parts); bad=False
for i in range(len(names)):
    for j in range(i+1,len(names)):
        v=(parts[names[i]]^parts[names[j]]).volume()
        if v>0.01: print(f"  {names[i]} x {names[j]}: {v:.1f}"); bad=True
for a in range(-25,26,5):
    tp=teeth.rotate((0,0,a))
    for n in ("arm","bracket","plate","motor","board"):
        v=(tp^parts[n]).volume()
        if v>0.01: print(f"  teeth at {a} deg x {n}: {v:.1f} mm3"); bad=True
print("overlaps:", "some" if bad else "none")
print("plate pieces:", len(A.frame_plate_v3().decompose()))
bb=plate.bounding_box(); print("plate wheel-frame bb", [round(v,1) for v in bb])
print("bore X", round(A.CUP_X-A.BORE_X[1],1), round(A.CUP_X-A.BORE_X[0],1), " arm X", A.ARM_X, " bore Y", round(A.COVER_Y-A.PLATE_T-A.BORE_DEPTH,1), round(A.COVER_Y-A.PLATE_T,1), " arm Y", [round(v,1) for v in A.ARM_Y])
EOF