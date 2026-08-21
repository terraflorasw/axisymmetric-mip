"""Is threaded meshing REPRODUCIBLE, and is it faster? Measures both.

The whole error budget rests on METHODOLOGY 2b: the solver is bit-exact, so
every difference between two solves is mesh generation. That holds only while
a mesh can be rebuilt identically. gmsh here is built with OpenMP, so
General.NumThreads is live — but threaded meshing can race, and a mesh that
differs run-to-run would silently convert "same mesh" into "same command line",
which is not the same claim at all.

VERIFICATION   at each thread count, N repeats of the SAME command must produce
               an identical SHA-256 of the .msh. (The .meta.json legitimately
               differs — it records the thread count — so only the mesh is
               hashed.)
FALSIFICATION  any hash difference at any thread count > 1 rules that thread
               count out. One differing pair is enough; this is not statistics.

Element COUNT alone is not the test — two meshes can share a tet count and
place the nodes differently, and it is node placement the solver sees.
"""
import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
import time

TIMEOUT_S = 3600


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def one(py, geo, threads, rep, out):
    # --no-cache is NOT optional and is NOT a caller's choice. This rig
    # measures mesh GENERATION; a cache hit would return a copy of an earlier
    # mesh in ~0s with a trivially identical hash, and the run would report
    # "REPRODUCIBLE" having meshed nothing. Near-miss, 2026-08-20: geometry.py
    # gained the cache while this rig was mid-flight, and repeat 1 of each
    # thread count would have been a copy of repeat 0.
    cmd = [py, "geometry.py", "--out", out, "--no-cache",
           "--threads", str(threads)] + geo
    t0 = time.time()
    # Popen+kill, not run(timeout=): run() raises without killing, and a
    # leaked gmsh would poison every timing that follows it.
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    try:
        outp = proc.communicate(timeout=TIMEOUT_S)[0]
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        raise RuntimeError(f"threads={threads} rep={rep}: TIMED OUT, killed")
    dt = time.time() - t0
    if proc.returncode or not pathlib.Path(out).exists():
        tail = (outp or "").strip().splitlines()[-3:]
        raise RuntimeError(f"threads={threads} rep={rep}: rc={proc.returncode} "
                           f"{tail}")
    n = 0
    meta = pathlib.Path(out).with_suffix(".meta.json")
    if meta.exists():
        n = json.loads(meta.read_text()).get("tets", 0)
    return dt, sha(out), n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--threads", default="1,4",
                    help="comma list of thread counts to test")
    ap.add_argument("--repeats", type=int, default=2)
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("geo", nargs=argparse.REMAINDER,
                    help="-- then geometry.py args")
    a = ap.parse_args()
    geo = [g for g in a.geo if g != "--"]
    if any(g.startswith("--out") or g == "--no-cache" for g in geo):
        sys.exit("ERROR: --out and --no-cache are set by this rig, not passed in.")
    counts = [int(t) for t in a.threads.split(",")]

    print(__doc__)
    print(f"geometry: {' '.join(geo)}")
    print(f"repeats:  {a.repeats}\n")
    rows, verdict = {}, True
    for t in counts:
        res = []
        for r in range(a.repeats):
            out = f"_det_t{t}_r{r}.msh"
            dt, h, n = one(a.python, geo, t, r, out)
            res.append((dt, h, n))
            print(f"  threads={t:<3} rep {r}: {dt:7.1f}s  {n:>8,} tets  {h[:16]}",
                  flush=True)
            if not a.keep:
                for p in (out, str(pathlib.Path(out).with_suffix(".meta.json"))):
                    pathlib.Path(p).unlink(missing_ok=True)
        same = len({h for _, h, _ in res}) == 1
        rows[t] = (min(d for d, _, _ in res), same, res[0][2], res[0][1])
        print(f"  threads={t:<3} -> {'REPRODUCIBLE' if same else '🔴 NOT REPRODUCIBLE'}"
              f"  best {rows[t][0]:.1f}s\n", flush=True)
        if not same:
            verdict = False

    base = rows[counts[0]][0]
    print("=" * 70)
    print(f"  {'threads':>8} {'best s':>9} {'speedup':>8}  reproducible")
    for t in counts:
        s, same, _, _h = rows[t]
        print(f"  {t:>8} {s:>9.1f} {base / s:>7.2f}x  {'yes' if same else 'NO'}")
    # Cross-thread-count agreement is a SEPARATE question from repeatability.
    # A thread count can be perfectly repeatable and still produce a DIFFERENT
    # mesh from the serial one — which would mean adopting it silently breaks
    # comparability with every mesh already solved, and puts the 1.3-3.3 MHz
    # cross-mesh error on results that look like a free speedup.
    print()
    ref = rows[counts[0]][3]
    diff = [t for t in counts if rows[t][3] != ref]
    if diff:
        print(f"  ⚠️  threads={diff} produce a DIFFERENT mesh from threads="
              f"{counts[0]} — repeatable, but not the same mesh. Adopting one "
              f"is a mesh change, and carries cross-mesh error against every "
              f"result already recorded.")
    else:
        print(f"  ✅ all thread counts produced the IDENTICAL mesh to "
              f"threads={counts[0]} — adoption is free of mesh change")
    print()
    if verdict:
        print("  ✅ every thread count reproduced its own mesh exactly")
    else:
        print("  🔴 at least one thread count is not reproducible — do not adopt it")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
