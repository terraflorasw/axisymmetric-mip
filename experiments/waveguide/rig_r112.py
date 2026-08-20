"""R112 — CLOSE THE ROUND TRIP. Benchmark gmsh + Palace against exact mathematics.

The user's framing, and it names a real gap:

    "there is a concept of a sort of 'semantic closure', where we resolve the
     round trip between the known physics and the simulation instrument. Much of
     the time, we go from known physics to simulation and decide the result is
     wrong by the simulation result, without ever going back the other way."

🔴 THIS RECORD HAS DONE EXACTLY THAT. R2 compared a closed-form wall Q (49,182)
against a measured ~95,000 and closed with "closed forms are the fault, not the
model" — legitimate, because our cavity is not an empty right cylinder. But the
escape hatch was then used and never removed: THE PIPELINE HAS NEVER BEEN CHECKED
AGAINST A CASE WHERE THE CLOSED FORM IS EXACT. Every "the simulation is right and
the formula is indicative" ruling since has rested on that unclosed loop.

An EMPTY right circular cylinder removes the escape hatch. Its spectrum is exact:

        f_mnp = (c/2pi) * sqrt( (chi/a)^2 + (p*pi/L)^2 )

with chi = chi_mn (TM, zeros of J_m) or chi'_mn (TE, zeros of J'_m). At the design
dimensions a = 103.7 mm, L = 88.53 mm:

    TM010  1.106485      TE211  2.200375        TM020  2.539846
    TM110  1.763008      TM210  2.362953
    TE111  1.893272      TE011  2.444385  <-- EXACTLY degenerate
    TM011  2.022654      TM111  2.444385  <--   (chi'01 = chi11 = 3.83171)

🔑 THE DEGENERATE PAIR IS THE BEST ARTIFACT PROBE IN THIS PROJECT. TE011 and TM111
are degenerate to ALL orders in an ideal empty cylinder — not approximately,
identically. ANY SPLITTING THE SOLVER REPORTS IS PURE NUMERICAL SYMMETRY BREAKING,
with a true value of exactly zero. That is stronger than the rotation probe (R89)
and the translation probe (R109), because those have zero true change in a
quantity we then measure; this has zero true DIFFERENCE between two things the
solver must report separately.

════════════════════════════════════════════════════════════════════════════════
CRITERIA, DECLARED BEFORE THE RUN
════════════════════════════════════════════════════════════════════════════════

1. ACCURACY — for each NON-degenerate mode, |f_solved - f_exact|. This is the
   first number in this project that has a known-true reference. Report it in MHz
   and against the R105 mesh floor (1.3-3.3 MHz). 🔴 A systematic offset common
   to all modes is a scale or units error; a mode-DEPENDENT error is a
   discretisation signature; a random one is mesh noise.

2. DEGENERACY SPLITTING — |f(TE011) - f(TM111)| must be ZERO. Whatever comes out
   is the solver's numerical symmetry breaking, and it BOUNDS every claim this
   project makes near that degeneracy — including the R107 hybridisation result
   and the entire justification for the mode filter.

3. 🔴 R37 — the SAME empty cavity is solved in DRIVEN and EIGENMODE. They must
   agree, and both must match the closed form. R37 has been open since
   2026-08-15 on a 3.7x eigenmode/driven disagreement in epsilon sensitivity,
   resolved by CHOOSING driven rather than by diagnosis. With NO dielectric
   present, epsilon sensitivity cannot be the cause of any disagreement here, so
   this isolates whether the two paths differ at all on identical physics.

4. CONVERGENCE — two size factors. The exact answer is known, so this measures
   the ACTUAL discretisation error rather than a self-referential drift, and it
   independently checks offset.te011 = +24.54, which has only ever been measured
   as order-1-vs-order-2 on a loaded cavity.

⚠️ WHAT THIS CANNOT DO. There is no coupling loop, so no port, so DRIVEN needs
   one. A loop perturbs the cavity, so the driven case is compared to eigenmode
   AND to closed form with that perturbation stated, not hidden. The eigenmode
   case is the pure one: a genuinely empty cylinder, nothing in it at all.
"""
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import solveconf
import solver

try:
    from scipy.special import jn_zeros, jnp_zeros
except ImportError:
    sys.exit("scipy needed for the Bessel zeros — the reference must be exact")

import math
C = 299792458.0
A_MM, L_MM = 103.70, 88.53


def exact(a_mm=A_MM, l_mm=L_MM):
    a, L = a_mm * 1e-3, l_mm * 1e-3
    def f(chi, p):
        return C / (2 * math.pi) * math.hypot(chi / a, p * math.pi / L) / 1e9
    return {
        "TM010": f(jn_zeros(0, 1)[0], 0), "TM110": f(jn_zeros(1, 1)[0], 0),
        "TE111": f(jnp_zeros(1, 1)[0], 1), "TM011": f(jn_zeros(0, 1)[0], 1),
        "TE211": f(jnp_zeros(2, 1)[0], 1), "TM210": f(jn_zeros(2, 1)[0], 0),
        "TE011": f(jnp_zeros(0, 1)[0], 1), "TM111": f(jn_zeros(1, 1)[0], 1),
        "TM020": f(jn_zeros(0, 2)[1], 0),
    }


# 🔴 EVERY perturbing feature must be OFF, and the first attempt at this run
# proves why it needs saying. I wrote --no-torch --mode-filter 0 and called the
# cavity empty. It was not: R98/R99 made the VIEWPORT and LIGHT TRAP default to
# 10 mm, so the "empty cylinder" carried two 10x25 mm stubs at 108 and 288 deg.
# The closed form then disagreed by 1.5-45.6 MHz with mixed signs, and the
# obvious reading was "gmsh or Palace is wrong".
#
# 🔑 THAT IS THE SEMANTIC-CLOSURE FAILURE RUNNING IN REVERSE. R2 trusted the
# instrument over the formula; I was one step from trusting the formula over the
# instrument — while the actual fault was that MY MODEL WAS NOT THE REFERENCE
# GEOMETRY. Both directions have the same cure: check that the thing you solved
# is the thing the formula describes, BEFORE attributing the difference.
GEO = ["--radius", f"{A_MM}", "--length", f"{L_MM}", "--order", "2",
       "--sectors", "1", "--no-torch", "--mode-filter", "0",
       "--viewport", "0", "--trap", "0,0,0", "--chimney", "0,41",
       "--feed", "0,41"]
DRIVEN_BAND, DRIVEN_STEP = (2.35, 2.55), 5e-5
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")

print(__doc__)
print("=" * 78, flush=True)
ex = exact()
print("EXACT REFERENCE (closed form, no simulation involved):")
for k, v in sorted(ex.items(), key=lambda kv: kv[1]):
    print(f"    {k}  {v:.6f} GHz")
print(f"\n  🔑 TE011 - TM111 = {1e3*(ex['TE011']-ex['TM111']):+.9f} MHz "
      "— identically zero\n", flush=True)
pathlib.Path("r112.exact.json").write_text(json.dumps(ex, indent=1))
print("  wrote r112.exact.json — the reference is on disk BEFORE any solve, so "
      "it cannot be\n  retro-fitted to whatever the solver returns.\n", flush=True)

FACTORS = ["0.96", "1.06", "1.00", "1.20", "0.90"]


def mesh(tag, extra):
    """Build, retrying size factors — an empty cylinder curves differently from
    the loaded one, and R105 found 2 of 6 factors fail on the design geometry."""
    for fac in FACTORS:
        r = subprocess.run(
            [sys.executable, "geometry.py", "--out", f"{tag}.msh",
             "--size-factor", fac] + GEO + extra,
            capture_output=True, text=True)
        if r.returncode == 0 and pathlib.Path(f"{tag}.msh").exists():
            m = solveconf.load_meta(f"{tag}.msh")
            # 🔴 GATE: assert the cavity really is a right circular cylinder.
            # A benchmark against a closed form is worthless if the geometry is
            # not the one the closed form describes, and defaults change under
            # you — these two flipped to 10 mm three entries ago.
            g = m["geometry_mm"]
            bad = {k: g[k] for k in ("viewport", "trap", "chimney", "feed",
                                     "groove")
                   if g.get(k) and g[k][0]}
            if (g.get("torch_material") or [1.0])[0] != 1.0:
                bad["torch_material"] = g["torch_material"]
            if bad and "--loop" not in extra:
                raise RuntimeError(
                    f"{tag}: NOT an empty cylinder — {bad}. The closed form "
                    "describes a right circular cylinder and nothing else.")
            print(f"  {tag}: sf {fac}, {m['tets']:,} tets, "
                  f"attrs {sorted(k for k, v in m['attributes'].items() if v)}"
                  f"{' [loop present, PERTURBED by design]' if '--loop' in extra else ' [clean cylinder]'}",
                  flush=True)
            return m, fac
        print(f"    sf {fac} failed, trying next", flush=True)
    raise RuntimeError(f"{tag}: no size factor produced a valid mesh")


def eigen_cfg(tag, meta, order=1, n=20, target=1.05):
    """Eigenmode config built from the SIDECAR, not from a template.

    ⚠️ PEC IS USED HERE DELIBERATELY, and it is the one place in this project
    where it is correct: the closed form assumes perfectly conducting walls, so
    a finite-conductivity wall would compare the solver against a formula it is
    not solving. This is PEC as a MATHEMATICAL REFERENCE, not as a physical
    model of the build.
    """
    a = meta["attributes"]
    # 🔴 R113, THIRD instance of one error class in this benchmark. I first
    # forgot the viewport, then found `--viewport 0` could not disable it, and
    # then assigned materials to {bore, air} while the mesh also carried the
    # torch (attribute 2) and the upstream channels (11) — two volumes with NO
    # material. Each time I enumerated what I remembered instead of asserting
    # the whole state.
    #
    # 🔑 THE FIX IS NOT A LONGER LIST. Take EVERY volume attribute the sidecar
    # reports and give it vacuum, then assert nothing was missed. A whitelist
    # you maintain by hand is the same failure as a name you maintain by hand.
    vols = sorted({v for k, v in a.items()
                   if k not in ("wall", "port") and isinstance(v, int)}
                  | set(a["air"] or []))
    missing = [k for k, v in a.items()
               if k not in ("wall", "port", "air") and isinstance(v, int)
               and v not in vols]
    assert not missing, f"volume attributes without material: {missing}"
    return {
        "Problem": {"Type": "Eigenmode", "Verbose": 2,
                    "Output": f"postpro/{tag}"},
        "Model": {"Mesh": pathlib.Path(f"{tag}.msh").name, "L0": 1.0,
                  "Refinement": {"UniformLevels": 0}},
        "Domains": {"Materials": [{"Attributes": vols, "Permittivity": 1.0,
                                   "Permeability": 1.0}],
                    "Postprocessing": {"Energy": [{"Index": 1,
                                                   "Attributes": [a["bore"]]}]}},
        "Boundaries": {"PEC": {"Attributes": [a["wall"]]}},
        "Solver": {"Order": order, "Device": "CPU",
                   "Eigenmode": {"Target": target, "N": n, "Tol": 1e-08,
                                 "MaxIts": 200, "Save": 0},
                   "Linear": {"Type": "Default", "KSPType": "GMRES",
                              "Tol": 1e-08, "MaxIts": 500}},
    }


def run(tag, cfg):
    pathlib.Path(f"{tag}.json").write_text(json.dumps(cfg, indent=2))
    t0 = time.time()
    rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"], env=solver.ENV,
                        stdout=open(f"{tag}_p.log", "w"),
                        stderr=subprocess.STDOUT,
                        timeout=solver.DEFAULT_TIMEOUT_S).returncode
    dt = time.time() - t0
    if rc or dt < solver.MIN_SECONDS:
        tail = pathlib.Path(f"{tag}_p.log").read_text().strip().splitlines()
        raise RuntimeError(f"{tag}: rc={rc} in {dt:.0f}s — "
                           f"{tail[-1] if tail else '(empty log)'}")
    print(f"    solved in {dt:.0f}s", flush=True)


def eigenfreqs(tag):
    """Palace writes eig.csv for an eigenmode solve. Frequencies in GHz."""
    f = pathlib.Path("postpro") / tag / "eig.csv"
    if not f.exists():
        raise RuntimeError(f"{tag}: no eig.csv — eigenmode produced nothing")
    out = []
    for line in f.read_text().splitlines()[1:]:
        parts = [x.strip() for x in line.split(",")]
        if len(parts) >= 2:
            try:
                out.append(float(parts[1]))
            except ValueError:
                pass
    return sorted(out)


print("MESHING", flush=True)
meta096, fac096 = mesh("r112e096", [])
meta120, fac120 = mesh("r112e120", ["--n-wl", "8"])     # coarser by wavelength count

print("\nEIGENMODE — a genuinely empty cylinder, PEC walls, nothing in it",
      flush=True)
run("r112e096", eigen_cfg("r112e096", meta096))
run("r112e120", eigen_cfg("r112e120", meta120))

fine, coarse = eigenfreqs("r112e096"), eigenfreqs("r112e120")
print(f"\n  {len(fine)} eigenvalues (fine), {len(coarse)} (coarse)", flush=True)

# --- R37. Driven and eigenmode must be compared under the SAME boundary
# condition or the comparison carries a confound. The eigenmode above uses PEC
# to match the closed form; this one uses the finite-conductivity wall the
# driven path uses, so driven-vs-eigenmode differences cannot be blamed on the
# boundary.
print("\nEIGENMODE, finite-conductivity wall — the like-for-like partner for "
      "the driven solve", flush=True)
cfgc = eigen_cfg("r112c096", meta096)
cfgc["Model"]["Mesh"] = "r112e096.msh"          # same mesh, different BC
del cfgc["Boundaries"]["PEC"]
cfgc["Boundaries"]["Conductivity"] = [
    {"Attributes": [meta096["attributes"]["wall"]],
     "Conductivity": json.loads(pathlib.Path("baselines.json").read_text())
     ["wall.conductivity"]["value"], "Permeability": 1.0}]
run("r112c096", cfgc)
cond = eigenfreqs("r112c096")

print("\nDRIVEN — needs a port, so this mesh HAS a loop and is therefore "
      "PERTURBED.\n  Stated, not hidden: it is compared to the eigenmode on "
      "the same BC, not to the\n  closed form.", flush=True)
metad, facd = mesh("r112d096", ["--loop", "25.8,19.4,1.5,0.3", "--loop-phi", "36"])
cfgd, _m, _d = solveconf.driven("r112d096.msh", "r112d096", DRIVEN_BAND,
                                step=DRIVEN_STEP, order=1)
run("r112d096", cfgd)

json.dump({"exact": ex, "eig_pec_fine": fine, "eig_pec_coarse": coarse,
           "eig_cond_fine": cond,
           "size_factor_fine": fac096, "tets_fine": meta096["tets"],
           "tets_coarse": meta120["tets"], "tets_driven": metad["tets"],
           "driven_tag": "r112d096", "driven_band": DRIVEN_BAND},
          open("r112.result.json", "w"), indent=1)
print("  wrote r112.result.json", flush=True)
print("\n  ⚠️ NO VERDICT HERE — run evaluate.py r112", flush=True)
