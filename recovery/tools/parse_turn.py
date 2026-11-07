"""Parse one saved read_conversation result (a single turn) into its tool calls.

Usage:
  python3 parse_turn.py FILE list            -> one line per tool call: position, name, key params
  python3 parse_turn.py FILE show POS PARAM  -> print the unescaped value of one parameter
  python3 parse_turn.py FILE save POS PARAM OUT -> write the unescaped value of one parameter to OUT (exact bytes)
"""
import re, sys

ENT = {"lt": "<", "gt": ">", "amp": "&", "quot": '"', "#x27": "'", "#39": "'"}
ENT_RE = re.compile(r"&(lt|gt|amp|quot|#x27|#39);")


def unesc(s):
    return ENT_RE.sub(lambda m: ENT[m.group(1)], s)


TOOL_OPEN = re.compile(r'&lt;tool name="([^"]*)"&gt;\n')
PARAM_OPEN = re.compile(r'&lt;parameter name="([^"]*)"&gt;')
PARAM_END = "&lt;/parameter&gt;\n"
TOOL_END = "&lt;/tool&gt;"


def parse(text):
    calls = []
    pos = 0
    while True:
        m = TOOL_OPEN.search(text, pos)
        if not m:
            break
        name = m.group(1)
        i = m.end()
        params = []
        while True:
            if text.startswith(TOOL_END, i):
                i += len(TOOL_END)
                break
            if not params and text.startswith("\n" + TOOL_END, i):   # a call with no parameters
                i += 1 + len(TOOL_END)
                break
            pm = PARAM_OPEN.match(text, i)
            if not pm:
                raise SystemExit(f"parse error at {i}: {text[i:i+200]!r}")
            pname = pm.group(1)
            j = pm.end()
            # value ends at '</parameter>\n' followed by another '<parameter name=' or '</tool>'
            k = j
            while True:
                k = text.find(PARAM_END, k)
                if k < 0:
                    raise SystemExit(f"unterminated parameter {pname} in call {len(calls)+1}")
                nxt = k + len(PARAM_END)
                if text.startswith(TOOL_END, nxt) or PARAM_OPEN.match(text, nxt):
                    break
                k = nxt
            params.append((pname, text[j:k]))
            i = k + len(PARAM_END)
        calls.append((name, params, m.start()))
        pos = i
    return calls


def main():
    f = sys.argv[1]
    text = open(f, encoding="utf-8").read()
    calls = parse(text)
    cmd = sys.argv[2]
    if cmd == "list":
        for n, (name, params, off) in enumerate(calls, 1):
            d = dict(params)
            bits = []
            for key in ("file_path", "path", "description"):
                if key in d:
                    bits.append(f"{key}={unesc(d[key])[:140]!r}")
            if "command" in d:
                c = unesc(d["command"])
                bits.append(f"cmd[{len(c)}]={c[:300]!r}")
            if "content" in d:
                bits.append(f"content[{len(unesc(d['content']))}]")
            if "old_string" in d:
                bits.append(f"old[{len(unesc(d['old_string']))}] new[{len(unesc(d.get('new_string','')))}] replace_all={d.get('replace_all','-')}")
            if "edits" in d:
                bits.append(f"edits[{len(d['edits'])}]")
            print(f"{n:02d} {name} | " + " | ".join(bits))
    elif cmd in ("show", "save"):
        posn = int(sys.argv[3])
        pname = sys.argv[4]
        name, params, off = calls[posn - 1]
        vals = [v for p, v in params if p == pname]
        if len(vals) != 1:
            raise SystemExit(f"call {posn} ({name}) has {len(vals)} params named {pname}: {[p for p,_ in params]}")
        v = unesc(vals[0])
        if cmd == "show":
            sys.stdout.write(v)
        else:
            with open(sys.argv[5], "w", encoding="utf-8", newline="") as fh:
                fh.write(v)
            print(f"wrote {sys.argv[5]} ({len(v)} chars)")
    elif cmd == "params":
        posn = int(sys.argv[3])
        name, params, off = calls[posn - 1]
        print(name, [(p, len(v)) for p, v in params])


if __name__ == "__main__":
    main()
