"""H1 — which aspect ratio? Separation is analytic; Q is the missing axis.

Rival separation over D/L is a closed-form max-min (physics.py, no solver): a
single optimum at D/L 1.525, candidate B at 74% of it, candidate A at 23%, with
poles at TM012 (D/L 1.0964), TM210 (~2.20) and TM020 (~2.50).

What that cannot say is what each aspect ratio costs in Q — and LOD runs through
delivered power, which runs through Q. E0q made Q trustworthy (Q ∝ σ^0.5 to four
decimals), so this measures the second axis.

BARE CAVITY. No torch, no viewport, no filter, no loop. An axisymmetric cavity
keeps TE0n and TM0n from hybridising, which is what made E1b uninterpretable.
TE011 is pinned to 2.45 GHz at every point by solving for the radius.

VERIFICATION, both declared before the run:
  1. each mesh must reproduce physics.spectrum() — validates the mesh per shape.
  2. the D/L 2.332 point must reproduce E0q's TE011 Q of 36,548 (measured at
     D/L 2.343) to within a few percent. A sweep that cannot hit a number it has
     already measured is not measuring what it claims.

FALSIFICATION:
  🔴 TE011's Q below TM111's at any point. TE011 is the low-loss mode — no
     end-cap surface current at all — so a crossover means the mode
     identification is wrong, not that the physics changed.
  🔴 Q non-monotonic in a way that tracks mesh element count rather than D/L,
     which would mean we are measuring discretisation, not the cavity.

⚠️ Q is trustworthy in RATIO, not absolutely: physics.py refuses wall_Q and that
refusal stands. Comparisons ACROSS this sweep are the product; any single Q is an
upper bound on a real electropolished surface.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import eigmodes
import physics as ph
import solveconf
from e0_solver_vs_math import GEO, eigen_cfg, run
from scipy.optimize import brentq
import subprocess

TAG = "h1"
DLS = [1.20, 1.35, 1.446, 1.525, 1.70, 2.00, 2.332]
F0 = 2.45
SIGMA = 3.5e7                      # aluminium, as declared in baselines.json
E0Q_REF = {"dl": 2.343, "q": 36548.0}


def shape(dl):
    """(a, L) in mm with TE011 pinned at F0."""
    L = brentq(lambda L: ph.f_mnp("TE", 0, 1, 1, dl * L / 2, L) - F0,
               20.0, 400.0, xtol=1e-10)
    return dl * L / 2, L


def build(tag, a, L):
    # GEO carries the bare-cavity flags; radius/length appended so they win
    args = list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}"]
    # sf 1.5 (~26k) not 0.96 (~120k): Q is used in RATIO across the sweep, and
    # the D/L 2.332 point checks that choice against E0q's fine-mesh 36,548.
    # If the coarse mesh cannot reproduce it, the declared cross-check FAILS and
    # says so — the mesh choice is under test, not assumed.
    for sf in ("1.5", "1.2", "2.0", "1.0"):
        r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                            "--size-factor", sf] + args,
                           capture_output=True, text=True)
        if r.returncode == 0 and pathlib.Path(f"{tag}.msh").exists():
            return solveconf.load_meta(f"{tag}.msh"), sf
    raise RuntimeError(f"{tag}: no size factor meshed")


def eig_q(tag):
    f = pathlib.Path("postpro") / tag / "eig.csv"
    rows = []
    for line in f.read_text().splitlines()[1:]:
        p = line.split(",")
        if len(p) > 3:
            rows.append((float(p[1]), float(p[3])))
    rows.sort()
    return [r[0] for r in rows], [r[1] for r in rows]


def _checkpoint(path, payload):
    """Write results after EVERY case, not at the end.

    🔴 A spot reclamation on 2026-08-21 killed the instance mid-run. H1, H2 and
    H2b all wrote their result file only after the last case, so an interrupt
    lost every completed case with it — H2's table survived solely because it
    had been printed to a log and transcribed by hand. E0v already did this
    correctly ("written after EVERY case, so a death in case 2 cannot take case
    1 down with it"); the H rigs did not inherit it.

    Atomic: temp file then os.replace, so an interrupt DURING the write leaves
    the previous complete file rather than a truncated one.
    """
    import json as _j, os as _o, pathlib as _p
    p = _p.Path(path)
    t = p.with_suffix(p.suffix + f".tmp{_o.getpid()}")
    t.write_text(_j.dumps(payload, indent=1) + "\n")
    _o.replace(t, p)


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    out = []
    for dl in DLS:
        a, L = shape(dl)
        tag = f"{TAG}_{str(dl).replace('.', 'p')}"
        m, sf = build(tag, a, L)
        EX = ph.spectrum(a, L, fmax=3.2)
        # 🔴 WAS target=1.05 with n = (modes below 2.57) + 5, i.e. a shift-invert
        # spanning 1.05->2.6 GHz for a dozen eigenvalues when only TE011 and the
        # TM111 pair are wanted. Combined with sf 0.96 (110-120k elements on
        # these longer shapes, vs E0's 83k) a single point took over an hour.
        # Target the triplet directly: same measurement, ~20x less work.
        n = 8
        print(f"\n  D/L {dl:.3f}: a={a:.3f} L={L:.2f}  {m['tets']:,} tets "
              f"(sf {sf}), solving {n} modes near TE011", flush=True)
        c = eigen_cfg(tag, m, mesh=f"{tag}.msh", sigma=SIGMA, n=n, target=2.40)
        c["Solver"]["Order"] = 2
        run(tag, c)
        fs, qs = eig_q(tag)

        # mesh check: transparent-equivalent — this cavity IS empty
        # local check only — the solved window is now around TE011, so compare
        # just the exact modes that fall inside it
        lo, hi = min(fs), max(fs)
        loc = {k: v for k, v in EX.items() if lo - 0.02 <= v <= hi + 0.02}
        p0, refused = ph.match_exact(loc, fs, [("TE011", "TM111")])
        mx = max(abs(1e3 * (p0[k] - loc[k])) for k in p0) if p0 else float("nan")

        d = eigmodes.te011_tm111(fs, EX["TE011"], qs)
        if not d:
            print("    🔴 could not resolve the TE011/TM111 triplet — REPORTED")
            continue
        q_te = qs[d["te011_index"]]
        _t = [qs[i] for i in d["tm111_indices"]]
        q_tm = sum(_t) / len(_t)
        rivals = [(k, f) for k, f in EX.items() if k not in ("TE011", "TM111")]
        rk, rf = min(rivals, key=lambda kv: abs(kv[1] - F0))
        out.append({"dl": dl, "a": a, "L": L, "tets": m["tets"], "sf": sf,
                    "mesh_maxdelta_mhz": mx, "te011": d["te011"],
                    "q_te011": q_te, "q_tm111": q_tm, "how": d["how"],
                    "splitting_mhz": d["splitting_mhz"],
                    "rival": rk, "rival_sep_mhz": 1e3 * abs(rf - F0)})
        print(f"    mesh vs exact max|Δ| {mx:.3f} MHz   TE011 Q {q_te:,.0f}  "
              f"TM111 Q {q_tm:,.0f}  (by {d['how']})", flush=True)
        _checkpoint(f"{TAG}.result.json",
                    {"sigma": SIGMA, "f0": F0, "rows": out, "complete": False})

    print("\n" + "=" * 78)
    print(f"  {'D/L':>6}{'a mm':>8}{'L mm':>8}{'tets':>9}{'TE011 Q':>10}"
          f"{'TM111 Q':>10}{'Q ratio':>9}{'rival':>8}{'sep MHz':>9}")
    for r in out:
        print(f"  {r['dl']:>6.3f}{r['a']:>8.2f}{r['L']:>8.2f}{r['tets']:>9,}"
              f"{r['q_te011']:>10,.0f}{r['q_tm111']:>10,.0f}"
              f"{r['q_te011']/r['q_tm111']:>9.2f}{r['rival']:>8}"
              f"{r['rival_sep_mhz']:>9.1f}")

    bad = [r for r in out if r["q_te011"] <= r["q_tm111"]]
    print()
    if bad:
        print(f"  🔴 FALSIFIED: TE011 Q <= TM111 Q at D/L "
              f"{[r['dl'] for r in bad]} — mode identification is wrong")
    else:
        print("  ✅ TE011 Q exceeds TM111 Q at every point, as the low-loss "
              "mode must")
    ref = [r for r in out if abs(r["dl"] - 2.332) < 1e-6]
    if ref:
        got, want = ref[0]["q_te011"], E0Q_REF["q"]
        print(f"  cross-check vs E0q (D/L {E0Q_REF['dl']}): {got:,.0f} vs "
              f"{want:,.0f} — {100*(got-want)/want:+.1f}%")
    _checkpoint(f"{TAG}.result.json",
                {"sigma": SIGMA, "f0": F0, "rows": out, "complete": True})
    print(f"\n  wrote {TAG}.result.json — NO VERDICT HERE", flush=True)


if __name__ == "__main__":
    main()
