cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/sfm && cat > grip_pts.py <<'EOF'
import numpy as np
# photo 36, picked by eye: the grip's outer outline and the inner outline at the top (full-res pixels)
G36 = np.array([(353, 673), (433, 580), (567, 507), (700, 463), (833, 440), (967, 433), (1100, 447), (1233, 480),
                (1353, 527), (1433, 573), (1617, 700), (1667, 850), (1697, 1017), (1708, 1183), (1708, 1350), (1700, 1517),
                (1683, 1633), (175, 917), (133, 1083), (117, 1250), (113, 1417), (125, 1583), (150, 1750),
                (633, 1992), (883, 2058), (1133, 2075), (1300, 2058), (1467, 2000),
                (607, 633), (767, 593), (900, 580), (1033, 587), (1167, 613), (1300, 667)], float)
EOF
python3 - <<'EOF'
import numpy as np
G = np.load('gripB_guided.npy', allow_pickle=True).item()
# keep only the grip's outline, dropping points that landed on the cover or the legs
keep = {}
keep[26] = G[26]
keep[24] = G[24][G[24][:, 1] < 360]
g = G[33]; keep[33] = g[(g[:, 1] < 1650)]
g = G[37]; keep[37] = g[(g[:, 1] < 700)]
g = G[29]; keep[29] = g[(g[:, 0] < 1150) & (np.abs(g[:, 1] - (850 - 0.72 * g[:, 0])) < 80)]
for n, p in keep.items(): print(n, len(p))
np.save('gripB_clean.npy', keep, allow_pickle=True)
EOF