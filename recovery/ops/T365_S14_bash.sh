cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/mark && cat > homog.py <<'EOF'
import numpy as np
P = [((0,0),(1150,800)),((97,-40),(515,652)),((97,48),(440,1172)),((106,-46),(455,625)),((88,-46),(548,630)),
     ((3,15),(1140,905)),((-47,15),(1465,922)),((3,45.4),(1150,1140)),((-47,45.4),(1495,1130))]
def fit(pairs):
    A=[]
    for (x,y),(u,v) in pairs:
        A.append([x,y,1,0,0,0,-u*x,-u*y,-u]); A.append([0,0,0,x,y,1,-v*x,-v*y,-v])
    _,_,Vt=np.linalg.svd(np.array(A,float)); return Vt[-1].reshape(3,3)
H=fit(P); Hi=np.linalg.inv(H)
def fwd(x,y):
    p=H@[x,y,1]; return p[:2]/p[2]
def inv(u,v):
    p=Hi@[u,v,1]; return p[:2]/p[2]
for (x,y),(u,v) in P: print((x,y),(u,v),np.round(fwd(x,y)))
print("photo->plate")
for name,(u,v) in {"7 top-left":(420,500),"7 top band top":(700,440),"7 top band bottom":(700,600),"7 corner":(1050,460),
  "7 stem mid":(950,700),"stem end":(850,960),"stem end2":(880,1000),"red U bottom":(450,1280),"red U top-right":(460,1070),
  "big red left top":(350,1345),"big red right top":(1050,1220),"strip left at 800":(355,800)}.items():
    print(name,(u,v),np.round(inv(u,v),1))
print("plate->photo")
for q in [(28,-14),(28,50),(-60,-14),(106,-46),(88,-46),(106,101),(88,101),(97,64),(28,20)]:
    print(q,np.round(fwd(*q)))
EOF
python3 homog.py