#!/usr/bin/env python3
"""One mesh helper for parameter sweeps, enforcing a COMMON size-factor.

R27. The size-factor fallback exists because order-2 curving intermittently
fails (SIGABRT / degenerate elements). It silently changed mesh density between
runs three separate times — R11's brake comparison, R12's filling-factor sweep,
and R21's electrode sweep — each time producing a difference that was partly
discretisation. Recording the factor per result caught it every time but only
after the fact.

This builds every case in a sweep at ONE factor: it finds the coarsest factor in
the candidate list that succeeds for ALL cases, then rebuilds any case that had
used a different one. A sweep either comes back mutually comparable or it fails
loudly. It never returns a mixed-density set.
"""
import subprocess, pathlib

MM = pathlib.Path.home() / ".local/bin/micromamba"
FACTORS = ("1.00", "0.96", "1.06", "0.90", "0.85")


def build(tag, base_args, extra, fac):
    g = subprocess.run([str(MM), "run", "-n", "emsim", "python", "geometry.py",
                        "--out", f"{tag}.msh", "--size-factor", fac]
                       + base_args + extra,
                       capture_output=True, text=True)
    return g


def sweep(cases, base_args, factors=FACTORS):
    """cases: [(tag, [extra args])]. Returns (factor, ok) or (None, None).

    `factors` overrides the candidate list for sweeps whose geometry is harder
    to curve than the design point — R36c's 1-4 mm ovality ladder found that
    each of the five default factors failed on SOME case, and a wider list is
    the difference between a comparable sweep and no sweep at all. Order it
    best-guess-first: every candidate costs a full rebuild of every case.

    Every returned mesh shares one size-factor, so differences between them are
    geometry and nothing else.

    ⚠️ EVERY case you intend to COMPARE must be in the SAME sweep call. Passing a
    single case enforces commonality across nothing, and the result is then not
    comparable to anything built by an earlier call — which is exactly how the
    R11 L=90.56 run ended up at factor 1.00 against a 0.96 baseline. The helper
    guarantees consistency WITHIN a sweep; it cannot know about earlier ones.
    """
    if len(cases) < 2:
        print("  ⚠️  sweep() called with a single case — nothing to make common.")
        print("     If this is meant to be compared with an earlier run, put BOTH")
        print("     in one sweep instead; factors are not guaranteed to match.")
    for fac in factors:
        results = {}
        for tag, extra in cases:
            g = build(tag, base_args, extra, fac)
            if g.returncode != 0:
                print(f"  size-factor {fac}: '{tag}' failed, trying next factor")
                for line in (g.stderr or g.stdout or "").strip().splitlines()[-3:]:
                    print(f"      {line}")
                break
            results[tag] = True
        else:
            print(f"  ✅ all {len(cases)} cases meshed at a COMMON size-factor {fac}")
            return fac, results
    print("  🔴 no single size-factor meshes every case — sweep is not comparable.")
    print("     Do NOT difference these results. Coarsen the geometry or split the sweep.")
    return None, None
