cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide && cat > runs3.sh <<'EOF'
#!/bin/bash
export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide
(python3 run_s.py 110 -70 fit,latch > fit3_110.txt 2>&1; python3 run_s.py 106 -70 fit > fit3_106.txt 2>&1; python3 run_s.py 110 -73 fit > fit3_110_73.txt 2>&1) &
(python3 run_s.py 120 -70 fit > fit3_120.txt 2>&1; python3 run_s.py 110 -67 fit > fit3_110_67.txt 2>&1; python3 run_s.py 110 -70 mesh,gaps > mesh3_110.txt 2>&1) &
wait
echo done
EOF
chmod +x runs3.sh && echo ok