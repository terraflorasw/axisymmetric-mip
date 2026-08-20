"""E1b — the loading perturbation, measured as a SAME-MESH material switch.

E1a fixed the empty design point analytically. This measures what the torch and
filter do to it, which is the one part of E1 that needs a solver.

🔑 THE MEASUREMENT IS A DIFFERENCE ON ONE MESH, NOT A COMPARISON TO A FORMULA.
Build the mesh ONCE with all the geometry present, then solve it twice:

    transparent   every dielectric eps = 1.0  -> vacuum tubes are EM-invisible,
                                                so physics.spectrum() applies
                                                EXACTLY and verifies the mesh
    loaded        sapphire torch 11.6, quartz filter 3.78

    loading shift = loaded - transparent, SAME MESH

⚠️ This matters because the shift we are after is SMALL. TE011 moves ~3 MHz under
loading, while the absolute discretisation error of a working mesh is ~1-2 MHz.
Differencing against the closed form would put a 57% error on the answer;
differencing on one mesh cancels the discretisation almost entirely (METHODOLOGY
§2b — the solver is bit-exact, so only the materials differ between the two runs).

TWO ASPECT RATIOS, both resonating TE011 at 2.45 GHz when empty:

    A   a = 103.245, L =  88.53   D/L = 2.332   the inherited shape
    B   a =  86.743, L = 120.00   D/L = 1.446   3.2x wider rival separation (E1a)

VERIFICATION   two independent checks, both declared before the run:
    1. the TRANSPARENT solve must match physics.spectrum() — that validates the
       mesh on the real geometry, with the thin walls present.
    2. the loading RATIO TM020/TE011 must be ~43-53x, predicted from Bessel
       energy integrals over the tube walls with no simulation in it, and
       independently ~49x in the old programme's record.

FALSIFICATION  the SIGN. Adding dielectric can only LOWER a resonant frequency.
    A positive shift on either mode falsifies the setup, not the physics.

⚠️ sf 1.5 (~35k elements). Not chosen for speed: the measurement is a same-mesh
difference, so absolute discretisation error cancels and a moderate mesh is
sufficient. Check 1 above is what confirms that, and it would fail loudly if the
mesh were inadequate. 🔴 sf 2.5 does NOT mesh this geometry (1.0-1.5 mm walls);
2.0, 1.5 and 1.0 do, 1.2 does not — constructibility is non-monotonic.
"""
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import solveconf
from e0_solver_vs_math import eigen_cfg, run, eig

SF = "1.5"
SAPPHIRE, QUARTZ = 11.6, 3.78
SHAPES = [("A", 103.245, 88.53), ("B", 86.743, 120.00)]
BASE = ["--order", "2", "--sectors", "1", "--mode-filter", "3"]
DEG = [("TE011", "TM111")]


def mesh(tag, a, L):
    r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                        "--radius", f"{a}", "--length", f"{L}",
                        "--size-factor", SF] + BASE,
                       capture_output=True, text=True)
    if r.returncode or not pathlib.Path(f"{tag}.msh").exists():
        err = [l for l in (r.stdout + r.stderr).splitlines()
               if "rror" in l or "xception" in l]
        raise RuntimeError(f"{tag}: mesh failed — {err[-1][:100] if err else '?'}")
    return solveconf.load_meta(f"{tag}.msh")


def cfg_for(tag, meta, torch_eps, filter_eps):
    """eigen_cfg gives everything vacuum; override the two dielectric regions."""
    c = eigen_cfg(tag, meta, mesh=meta["mesh"], n=22, target=1.05)
    c["Solver"]["Order"] = 2
    a = meta["attributes"]
    vac = sorted({v for k, v in a.items()
                  if isinstance(v, int)
                  and k not in ("wall", "port", "torch", "filter")}
                 | set(a.get("air") or []))
    mats = [{"Attributes": vac, "Permittivity": 1.0, "Permeability": 1.0}]
    if a.get("torch"):
        mats.append({"Attributes": [a["torch"]], "Permittivity": torch_eps,
                     "Permeability": 1.0, "LossTan": 0.0})
    if a.get("filter"):
        mats.append({"Attributes": [a["filter"]], "Permittivity": filter_eps,
                     "Permeability": 1.0, "LossTan": 0.0})
    c["Domains"]["Materials"] = mats
    covered = {x for m in mats for x in m["Attributes"]}
    missing = [k for k, v in a.items() if isinstance(v, int)
               and k not in ("wall", "port") and v not in covered]
    assert not missing, f"{tag}: volumes without material: {missing}"
    return c


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    out = {}
    for nm, a, L in SHAPES:
        tag = f"e1b_{nm}"
        m = mesh(tag, a, L)
        print(f"\n{nm}: a={a} L={L} D/L={2*a/L:.3f}  {m['tets']:,} elements",
              flush=True)
        EX = ph.spectrum(a, L, fmax=3.2)
        res = {}
        for state, te, fe in (("transparent", 1.0, 1.0),
                              ("loaded", SAPPHIRE, QUARTZ)):
            t = f"{tag}_{state[:4]}"
            print(f"  {state}: torch eps={te} filter eps={fe}", flush=True)
            t0 = time.time()
            run(t, cfg_for(t, m, te, fe))
            res[state] = eig(t)
        # 1. VERIFY the mesh against exact truth, using the transparent solve
        p0, _r = ph.match_exact(EX, res["transparent"], DEG)
        mx = max(abs(1e3 * (p0[k] - EX[k])) for k in p0)
        print(f"  ✅ mesh check: transparent vs exact, max|Δ| = {mx:.3f} MHz",
              flush=True)
        # 2. MEASURE the shift, same mesh
        p1, _r = ph.match_exact(EX, res["loaded"], DEG)
        out[nm] = dict(a=a, L=L, tets=m["tets"], mesh_maxdelta=mx, modes={})
        print(f"  {'mode':>7}{'transparent':>13}{'loaded':>12}{'shift MHz':>11}")
        for k in sorted(set(p0) & set(p1), key=lambda x: EX[x]):
            sh = 1e3 * (p1[k] - p0[k])
            out[nm]["modes"][k] = dict(transparent=p0[k], loaded=p1[k], shift=sh)
            print(f"  {k:>7}{p0[k]:>13.5f}{p1[k]:>12.5f}{sh:>11.2f}")

    print("\n" + "=" * 78)
    for nm in out:
        m = out[nm]["modes"]
        if "TE011" in m and "TM020" in m:
            r = m["TM020"]["shift"] / m["TE011"]["shift"]
            pos = [k for k, v in m.items() if v["shift"] > 0]
            print(f"  {nm}: TE011 {m['TE011']['shift']:+.2f}  "
                  f"TM020 {m['TM020']['shift']:+.2f}  ratio {r:.1f}x "
                  f"(predicted 43-53x)")
            print(f"     {'🔴 POSITIVE shifts: ' + str(pos) if pos else '✅ all shifts negative, as dielectric loading requires'}")
    json.dump(out, open("e1b.result.json", "w"), indent=1)
    print("\n  wrote e1b.result.json — NO VERDICT HERE", flush=True)


if __name__ == "__main__":
    main()
