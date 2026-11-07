"""save_ops.py FILE TURN SPEC...   SPEC = POS (kind decided by the tool name)
Writes ops files for each listed call and prints a TSV-ish summary line per call (target paths to be filled in by hand)."""
import sys, os
sys.path.insert(0, "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/recovery/tools")
from parse_turn import parse, unesc
OPS = "/tmp/claude-0/-home-claude/29de5e81-e3b9-5428-a15c-fac1d206c0d4/scratchpad/recovery/ops"
f, turn = sys.argv[1], int(sys.argv[2])
calls = parse(open(f, encoding="utf-8").read())
def w(name, val):
    p = os.path.join(OPS, name)
    if os.path.exists(p):
        raise SystemExit(f"exists: {p}")
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(val)
    return name
for spec in sys.argv[3:]:
    pos = int(spec)
    name, params, off = calls[pos - 1]
    d = {}
    for k, v in params:
        if k in d:
            raise SystemExit(f"dup param {k} in {pos}")
        d[k] = unesc(v)
    T, S = f"{turn:03d}", f"{pos:02d}"
    if name == "Write":
        base = os.path.basename(d["file_path"])
        out = w(f"T{T}_S{S}_write_{base}", d["content"])
        print(f"{turn}\t{pos}\twrite\t{d['file_path']}\t-\t{out}\t{len(d['content'])} chars")
    elif name == "Edit":
        base = os.path.basename(d["file_path"])
        o = w(f"T{T}_S{S}_edit_{base}.old", d["old_string"])
        n = w(f"T{T}_S{S}_edit_{base}.new", d["new_string"])
        print(f"{turn}\t{pos}\tedit\t{d['file_path']}\t{d.get('replace_all','false')}\t{o},{n}\t")
    elif name == "Bash":
        out = w(f"T{T}_S{S}_bash.sh", d["command"])
        print(f"{turn}\t{pos}\tbash\t?\t-\t{out}\t{d.get('description','')}")
    else:
        print(f"UNHANDLED {pos} {name} {list(d)}")
