#!/bin/bash
export PYTHONPATH=/home/claude/pylib POP_CACHE=/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/pop/cache
cd /tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/slide
(python3 run_s.py 110 -70 fit > fit4_110.txt 2>&1; python3 run_s.py 113 -72 fit > fit4_113_72.txt 2>&1) &
(python3 run_s.py 120 -70 fit > fit4_120.txt 2>&1; python3 run_s.py 113 -68 fit > fit4_113_68.txt 2>&1) &
wait
echo done
