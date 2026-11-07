"""Compare the parts in two sets of 3MF print files, object by object (matched by name).

For each part: volume, size (bounding box), triangle count, and how far apart the two surfaces are: every vertex of
one is matched to the nearest point sampled on the other's surface, after centring both and trying the four quarter
turns about the vertical (a plate may lay a part turned). Prints one line per part.

Usage: python3 compare3mf.py THEIRS_DIR OURS_DIR
"""
import glob
import os
import re
import sys
import zipfile

import numpy as np
from scipy.spatial import cKDTree


def objects(path):
    z = zipfile.ZipFile(path)
    out = {}
    for n in z.namelist():
        if not n.endswith(".model"):
            continue
        t = z.read(n).decode("utf8", "ignore")
        for m in re.finditer(r"<object\b([^>]*)>(.*?)</object>", t, re.S):
            attrs, body = m.group(1), m.group(2)
            name = re.search(r'name="([^"]*)"', attrs)
            if "<mesh>" not in body:
                continue
            v = np.array(re.findall(r'<vertex x="([-\d.eE+]+)" y="([-\d.eE+]+)" z="([-\d.eE+]+)"', body), float)
            f = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', body), int)
            key = name.group(1) if name else f"{os.path.basename(n)}#{len(out)}"
            out[key] = (v, f)
    # Bambu files keep names in the config, keyed by object id; fall back to those
    if any(k.startswith(("3dmodel", "object_")) or "#" in k for k in out):
        for n in z.namelist():
            if n.endswith("model_settings.config"):
                cfg = z.read(n).decode("utf8", "ignore")
                names = re.findall(r'<object id="(\d+)">\s*<metadata key="name" value="([^"]+)"', cfg)
                if names and len(names) == len(out):
                    out = {nm: val for (_, nm), val in zip(names, out.values())}
    return out


def volume(v, f):
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    return abs(np.einsum("ij,ij->i", a, np.cross(b, c)).sum()) / 6.0


def surface_samples(v, f, n=60000, seed=0):
    rng = np.random.default_rng(seed)
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    area = np.linalg.norm(np.cross(b - a, c - a), axis=1) / 2
    idx = rng.choice(len(f), size=n, p=area / area.sum())
    r1, r2 = rng.random(n), rng.random(n)
    s = np.sqrt(r1)
    return (1 - s)[:, None] * a[idx] + (s * (1 - r2))[:, None] * b[idx] + (s * r2)[:, None] * c[idx]


def gap(va, fa, vb, fb):
    """Largest and 99th-percentile distance between the two surfaces, best of four quarter turns."""
    ca = (va.max(0) + va.min(0)) / 2
    cb = (vb.max(0) + vb.min(0)) / 2
    pa = np.vstack([va, surface_samples(va, fa)]) - ca
    sb = np.vstack([vb, surface_samples(vb, fb)]) - cb
    best = None
    for k in range(4):
        c, s = np.cos(k * np.pi / 2), np.sin(k * np.pi / 2)
        rot = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        q = pa @ rot.T
        d1 = cKDTree(sb).query(q)[0]
        d2 = cKDTree(q).query(sb)[0]
        d = np.concatenate([d1, d2])
        r = (d.max(), np.percentile(d, 99))
        if best is None or r[0] < best[0]:
            best = r
    return best


def main(theirs, ours):
    for f in sorted(glob.glob(os.path.join(theirs, "*.3mf"))):
        g = os.path.join(ours, os.path.basename(f))
        print(f"== {os.path.basename(f)}")
        if not os.path.exists(g):
            print("   (not made by the rebuilt programs)")
            continue
        A, B = objects(f), objects(g)
        for name in sorted(set(A) | set(B)):
            if name not in A or name not in B:
                print(f"   {name}: only in {'yours' if name in A else 'rebuilt'}")
                continue
            (va, fa), (vb, fb) = A[name], B[name]
            ea, eb = np.sort(va.max(0) - va.min(0)), np.sort(vb.max(0) - vb.min(0))
            vola, volb = volume(va, fa), volume(vb, fb)
            mx, p99 = gap(va, fa, vb, fb)
            print(f"   {name}: size {np.round(ea, 2)} vs {np.round(eb, 2)}; volume {vola / 1000:.2f} vs {volb / 1000:.2f} cm3 "
                  f"({100 * (volb - vola) / vola:+.3f}%); triangles {len(fa)} vs {len(fb)}; surfaces apart: "
                  f"max {mx:.3f} mm, 99% within {p99:.3f} mm")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
