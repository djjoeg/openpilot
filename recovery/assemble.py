"""Rebuild the design programs from the ops the helpers copied out of the chat record.

Reads recovery/index/*.tsv (turn, position, kind, path(s), replace_all, ops file(s), note), sorts every operation by
(turn, position, k) and replays Write and Edit operations into an in-memory file set. Bash operations are listed for
review; with --run-bash they are run inside a sandbox root, with absolute paths moved under it.

Usage: python3 assemble.py [--run-bash] [--out DIR]
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

R = os.path.dirname(os.path.abspath(__file__))
OPS = os.path.join(R, "ops")
SB = os.path.join(R, "sandbox")
ROOTS = ["/home/claude/", "/tmp/claude-0/", "/mnt/user-data/"]
CAD = "/home/claude/deliver/hardware/cad/"
REAL_PY = sys.executable

# Wrappers put first on PATH inside the sandbox: running a design program needs 3D libraries this workspace can't
# install, so a run of a design program is skipped (exit 0) and an edit script still runs; ruff is a no-op.
PY_WRAPPER = """#!/bin/bash
for a in "$@"; do
  case "$a" in
    -*) ;;
    *.py) f=$(readlink -f "$a" 2>/dev/null); case "$f" in "%(sb)s%(cad)s"*) echo "[replay: skipped running $a]"; exit 0;; esac; break;;
    *) break;;
  esac
done
exec %(py)s "$@"
"""


def load_index():
    rows = []
    for fn in sorted(os.listdir(os.path.join(R, "index"))):
        if not fn.endswith(".tsv"):
            continue
        for line in open(os.path.join(R, "index", fn), encoding="utf8"):
            line = line.rstrip("\n")
            if not line.strip() or line.lower().startswith("turn\t"):
                continue
            f = line.split("\t")
            if len(f) < 6:
                print("short index line:", fn, line[:120], file=sys.stderr)
                continue
            try:
                turn, pos = int(f[0]), int(f[1])
            except ValueError:
                print("bad index line:", fn, line[:120], file=sys.stderr)
                continue
            rows.append(dict(turn=turn, pos=pos, kind=f[2].strip().lower(), path=f[3].strip(),
                             replace_all=f[4].strip().lower() == "true", opsfiles=f[5].strip(),
                             note=f[6].strip() if len(f) > 6 else "", src=fn))
    return rows


def ops_for(row):
    """Expand a row into concrete operations, using the ops folder as the truth for file names."""
    t, s = row["turn"], row["pos"]
    pre = f"T{t:03d}_S{s:02d}_"
    names = sorted(n for n in os.listdir(OPS) if n.startswith(pre))
    out = []
    if row["kind"] == "write":
        for n in names:
            if "_write_" in n:
                out.append(("write", row["path"], os.path.join(OPS, n), None, 0))
    elif row["kind"] in ("edit", "multiedit"):
        olds = [n for n in names if n.endswith(".old")]
        for n in olds:
            m = re.match(re.escape(pre) + r"(?:m(\d+)_)?edit_", n)
            k = int(m.group(1)) if m and m.group(1) else 0
            out.append(("edit", row["path"], os.path.join(OPS, n), os.path.join(OPS, n[:-4] + ".new"), k))
        out.sort(key=lambda o: o[4])
    elif row["kind"] == "bash":
        for n in names:
            if n.endswith("_bash.sh"):
                out.append(("bash", row["path"], os.path.join(OPS, n), None, 0))
    return out


def read(p):
    with open(p, encoding="utf8", newline="") as fh:
        return fh.read()


ROOT_RE = re.compile("|".join(re.escape(r) for r in ROOTS))


def to_sb(text):
    # one pass, so the sandbox's own path (itself under /tmp/claude-0/) is never moved twice
    return ROOT_RE.sub(lambda m: SB + m.group(0), text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-bash", action="store_true")
    ap.add_argument("--out", default=os.path.join(R, "rebuilt"))
    ap.add_argument("--stop", default="", help="TURN,POS: stop after this operation (to look at the sandbox)")
    a = ap.parse_args()
    rows = sorted(load_index(), key=lambda r: (r["turn"], r["pos"]))
    files = {}
    problems = []
    if a.run_bash:
        shutil.rmtree(os.path.join(R, "replay_fail"), ignore_errors=True)
        shutil.rmtree(SB, ignore_errors=True)
        os.makedirs(SB + "/bin")
        for name in ("python3", "python"):
            with open(f"{SB}/bin/{name}", "w") as fh:
                fh.write(PY_WRAPPER % dict(sb=SB, cad=CAD, py=REAL_PY))
            os.chmod(f"{SB}/bin/{name}", 0o755)
        os.makedirs(f"{SB}/home/claude/bin")
        for rp in (f"{SB}/bin/ruff", f"{SB}/home/claude/bin/ruff"):  # the chat also called ruff by its full path
            with open(rp, "w") as fh:
                fh.write("#!/bin/bash\necho '[replay: ruff skipped]'\nexit 0\n")
            os.chmod(rp, 0o755)
        # manifold3d can't be installed here; a stand-in ends any run that imports it with exit 0, so commands
        # chained after a run (a && b) still happen, as they did when the run succeeded in the original chat
        # the chat's commands set PYTHONPATH=/home/claude/pylib, where manifold3d was installed, so the stand-in goes
        # there too
        for d in (f"{SB}/stubs/manifold3d", f"{SB}/home/claude/pylib/manifold3d"):
            os.makedirs(d)
            with open(f"{d}/__init__.py", "w") as fh:
                fh.write("import sys\nprint('[replay: 3D run skipped at manifold3d import]')\nsys.exit(0)\n")
        env = dict(os.environ, PATH=f"{SB}/bin:" + os.environ["PATH"], PYTHONPATH=f"{SB}/stubs")
    stop = tuple(int(x) for x in a.stop.split(",")) if a.stop else None
    for row in rows:
        if stop and (row["turn"], row["pos"]) > stop:
            break
        for kind, path, f1, f2, k in ops_for(row):
            tag = f"T{row['turn']:03d} S{row['pos']:02d} {kind:5s} {os.path.basename(path)}"
            if kind == "write":
                files[path] = read(f1)
            elif kind == "edit":
                if a.run_bash and path not in files and os.path.exists(SB + path):
                    files[path] = read(SB + path).replace(SB, "")
                if path not in files:
                    problems.append(f"{tag}: edit before the file exists")
                    continue
                old, new = read(f1), read(f2)
                n = files[path].count(old)
                if n == 0:
                    problems.append(f"{tag}: old text not found")
                    continue
                if n > 1 and not row["replace_all"]:
                    problems.append(f"{tag}: old text found {n} times (replaced the first)")
                files[path] = files[path].replace(old, new) if row["replace_all"] else files[path].replace(old, new, 1)
            elif kind == "bash":
                if not a.run_bash:
                    problems.append(f"{tag}: bash not run ({row['note'][:60]})")
                    continue
                # write the current state into the sandbox, run, read back every file it may have changed
                for p, txt in files.items():
                    q = SB + p
                    os.makedirs(os.path.dirname(q), exist_ok=True)
                    with open(q, "w", encoding="utf8", newline="") as fh:
                        fh.write(to_sb(txt))  # paths inside scripts point into the sandbox too; undone on read-back
                for d in ROOTS:
                    os.makedirs(SB + d, exist_ok=True)
                ov = os.path.join(R, "overrides", os.path.basename(f1))
                if os.path.exists(ov):  # a hand-made stand-in for a command that can't replay as recorded (see its notes)
                    problems.append(f"{tag}: replayed from overrides/{os.path.basename(f1)}")
                    f1 = ov
                raw = read(f1)
                cmd = to_sb(raw)
                # folders the command cds into existed in the old workspace; make them here
                for d in re.findall(r"(?:^|[\s;&|(])cd\s+([\"']?)(/[^\s;&|)\"']+)\1", raw):
                    if ROOT_RE.match(d[1]):
                        os.makedirs(SB + d[1], exist_ok=True)
                # the old shell kept its folder between commands; a command that doesn't start with cd ran where its
                # target file is (the helpers traced that folder into the index's path column)
                cwd = SB + "/home/claude"
                if not re.match(r"\s*cd\s", raw) and path.startswith("/"):
                    # the path column can list several files (";" or "," separated); a command that touches a design
                    # program ran in the cad folder (it copies bare names from there), otherwise use the first file's
                    plist = [x for x in re.split(r"[;,\s]+", path) if x.startswith("/")]
                    incad = [x for x in plist if x.startswith(CAD)]
                    d = os.path.dirname((incad or plist or [path])[0])
                    if os.path.isdir(SB + d) or d.startswith(("/home/claude", "/tmp/claude-0")):
                        os.makedirs(SB + d, exist_ok=True)
                        cwd = SB + d
                before = set(files)
                try:
                    r = subprocess.run(["bash", "-c", cmd], cwd=cwd, capture_output=True, text=True, timeout=120,
                                       env=env)
                except subprocess.TimeoutExpired:
                    problems.append(f"{tag}: bash timed out")
                    r = None
                # a command whose folder was guessed wrong fails on a bare name; most such commands ran in cad
                if (r is not None and r.returncode and cwd != SB + CAD.rstrip("/") and not re.match(r"\s*cd\s", raw)
                        and "No such file" in (r.stderr + r.stdout)):
                    r2 = subprocess.run(["bash", "-c", cmd], cwd=SB + CAD, capture_output=True, text=True,
                                        timeout=120, env=env)
                    problems.append(f"{tag}: failed in {cwd[len(SB):]}, re-run in cad: exit {r2.returncode}")
                    cwd, r = SB + CAD, r2
                for p in list(before):
                    if not os.path.exists(SB + p):
                        del files[p]
                for root, _, fns in os.walk(SB):
                    for fn in fns:
                        q = os.path.join(root, fn)
                        p = q[len(SB):]
                        # every file already tracked (whatever its type, e.g. the 3D page template), plus new
                        # program and data files the command made in a cad folder
                        if p in files or (q.endswith((".py", ".json", ".csv", ".txt", ".scad")) and "/cad" in p):
                            try:
                                files[p] = read(q).replace(SB, "")
                            except UnicodeDecodeError:
                                pass
                if r is not None and r.returncode:
                    problems.append(f"{tag}: bash exit {r.returncode}: {(r.stderr or r.stdout or '').strip()[-200:]}")
                    os.makedirs(os.path.join(R, "replay_fail"), exist_ok=True)
                    with open(os.path.join(R, "replay_fail", os.path.basename(f1) + ".txt"), "w") as fh:
                        fh.write(f"cwd {cwd}\n--- stdout\n{r.stdout}\n--- stderr\n{r.stderr}\n")
    shutil.rmtree(a.out, ignore_errors=True)  # (replay_fail/ is cleared at the start of a run)
    for p, txt in files.items():
        q = os.path.join(a.out, p.lstrip("/"))
        os.makedirs(os.path.dirname(q), exist_ok=True)
        with open(q, "w", encoding="utf8", newline="") as fh:
            fh.write(txt)
    print(f"{len(rows)} index rows, {len(files)} files rebuilt into {a.out}")
    for p in sorted(files):
        print(f"  {p}  ({files[p].count(chr(10))} lines)")
    print(f"{len(problems)} problems")
    for x in problems:
        print("  " + x)


if __name__ == "__main__":
    main()
