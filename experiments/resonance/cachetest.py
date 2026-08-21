"""Does a cache HIT equal a REBUILD, byte for byte? That is the whole claim.

The mesh cache is only safe if a hit returns exactly what meshing would have
produced. This proves it on a real geometry rather than asserting it.

VERIFICATION   sha256(mesh from cold build) == sha256(mesh from cache hit),
               and the hit must be much faster (it did no meshing).
FALSIFICATION  any hash difference; or a hit that takes as long as a build
               (which would mean it silently re-meshed and the cache is a lie);
               or a changed geometry.py failing to invalidate the entry.
"""
import hashlib
import pathlib
import shutil
import subprocess
import sys
import time

# sf 2.0: the coarsest factor known to mesh this geometry (E1b: 2.5 fails,
# 1.2 fails; constructibility is non-monotonic). Coarse on purpose - this rig
# tests cache identity, not mesh quality.
GEO = ["--radius", "103.245", "--length", "88.53", "--size-factor", "2.0",
       "--order", "2", "--sectors", "1"]
CACHE = pathlib.Path("_cachetest_dir")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def run(py, out, extra=()):
    import os
    env = {**os.environ, "AMIP_MESH_CACHE": str(CACHE.resolve())}
    t0 = time.time()
    proc = subprocess.Popen([py, "geometry.py", "--out", out] + GEO + list(extra),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, env=env)
    try:
        o = proc.communicate(timeout=1800)[0]
    except subprocess.TimeoutExpired:
        proc.kill(); proc.wait(); raise RuntimeError(f"{out}: timed out")
    if proc.returncode:
        raise RuntimeError(f"{out}: rc={proc.returncode}\n{o[-800:]}")
    return time.time() - t0, o


def main():
    py = sys.argv[1] if len(sys.argv) > 1 else sys.executable
    print(__doc__)
    shutil.rmtree(CACHE, ignore_errors=True)
    ok = True

    t1, o1 = run(py, "_ct_a.msh")
    h1 = sha("_ct_a.msh")
    print(f"  cold build : {t1:7.1f}s  {h1[:16]}  "
          f"{'stored' if 'cache: stored' in o1 else '🔴 NOT STORED'}")

    t2, o2 = run(py, "_ct_b.msh")
    h2 = sha("_ct_b.msh")
    hit = "cache HIT" in o2
    print(f"  cache hit  : {t2:7.1f}s  {h2[:16]}  "
          f"{'HIT' if hit else '🔴 MISS (expected a hit)'}")

    if h1 != h2:
        print("  🔴 FALSIFIED: hit differs from build"); ok = False
    else:
        print("  ✅ hit is byte-identical to the cold build")
    if not hit:
        ok = False
    elif t2 > 0.5 * t1:
        print(f"  🔴 hit took {t2:.1f}s vs build {t1:.1f}s — it re-meshed")
        ok = False
    else:
        print(f"  ✅ hit skipped the meshing ({t1/max(t2,1e-6):.0f}x faster)")

    # a changed geometry.py MUST invalidate every entry — the property that
    # makes the cache safe to leave on by default
    src = pathlib.Path("geometry.py")
    orig = src.read_text()
    try:
        src.write_text(orig + "\n# cachetest: source-hash invalidation probe\n")
        _, o3 = run(py, "_ct_c.msh")
        if "cache HIT" in o3:
            print("  🔴 FALSIFIED: edited geometry.py still hit the cache"); ok = False
        else:
            print("  ✅ editing geometry.py invalidated the entry (rebuilt)")
    finally:
        src.write_text(orig)

    # --no-cache must actually bypass
    _, o4 = run(py, "_ct_d.msh", ["--no-cache"])
    if "cache HIT" in o4:
        print("  🔴 FALSIFIED: --no-cache still served a hit"); ok = False
    else:
        print("  ✅ --no-cache bypassed the cache")

    for f in pathlib.Path(".").glob("_ct_*"):
        f.unlink(missing_ok=True)
    shutil.rmtree(CACHE, ignore_errors=True)
    print("\n  " + ("✅ ALL PASS" if ok else "🔴 FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
