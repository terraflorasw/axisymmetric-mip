#!/usr/bin/env python3
"""H3 — Q_ext on the SAME geometry and the SAME MESH the driven sweep used.

🔴 WHY THIS RIG EXISTS. The record carries two Q_ext values and they were never
compared fairly:

    eigen   9,231  (h3_loopq)   GEO_DESIGN as-is -> --no-torch: NO TORCH BODY
    driven  ~8,462 (h3_driven)  torch body at eps=1 + plasma region

User, 2026-08-25: *"Comparisons between eigen and driven have to happen on the
same geometry (torch, cavity, everything)."* Mine did not, so the "~9% method
gap" I published was WITHDRAWN (CONVENTIONS 7aq) -- not refuted, VOID. There is
no measurement of the torch's effect on Q_ext anywhere in the record; I wrongly
argued from its 0.23% effect on Q0, which is a different quantity.

🔑 THIS RIG REMOVES THE ONLY UNCONTROLLED VARIABLE: it does not build a mesh. It
BINDS the h3_driven_*.msh files that are already on disk -- the exact meshes the
driven sweep solved -- and runs the eigen pair on them.

    Q0  = eigen, port_bc="pec"      gap shorted -> no port loss -> UNLOADED Q
    Q_L = eigen, port_bc="lumped"   real 50 ohm load           -> LOADED Q
    1/Q_ext = 1/Q_L - 1/Q0     ->     beta = Q0 / Q_ext

⚠️ eigen_cfg() assigns Permittivity 1.0 to EVERY volume. That is CORRECT for
h3_driven's torch (it meshed eps=1) and WRONG for the plasma, so the plasma
attribute is overridden explicitly, exactly as e3_closure does.

CRITERIA, DECLARED BEFORE THE RUN
  V1  the COLD case needs no plasma material at all -- eigen_cfg's default IS
      the cavity h3_driven solved cold. If cold does not work, nothing else here
      is meaningful.
  V2  purity P >= 0.99 on every reported mode, or the mode is not TE011 and the
      Q attached to it means nothing (every eigen rig must emit P).
  V3  GATE 5 must pass on every solve: the mesh named must be the mesh the
      sidecar describes. This rig NEVER writes a mesh, so a GATE 5 failure means
      the binding is wrong, not the geometry.

  🔴 F1  THE POINT OF THE RIG. If cold Q_ext lands near 9,231, then eigen and
         driven genuinely disagree on ONE geometry and the disagreement is real
         and unexplained. If it lands near 8,462, the earlier "gap" was the
         torch/mesh difference and there was never a method problem.
  🔴 F2  if Q_ext varies with density by more than ~5%, h3_loopq's docstring
         claim -- "Q_ext is set by loop geometry, not by the load" -- is FALSE,
         and beta(ne) = Q0(ne)/Q_ext is not a valid shortcut anywhere.
  ⚠️ F3  if the LUMPED solve does not converge with plasma present, report it.
         e3_closure case E proved vacuum-torch + plasma converges under "pec";
         "lumped" on the same mesh is NOT covered by that result.

⚠️ NOT A DESIGN NUMBER. These meshes carry a VACUUM torch; the design torch is
sapphire (e0_solver_vs_math.GEO_DESIGN, and the warning at that constant). This
rig answers an INSTRUMENT question -- do the two solvers agree -- not "what is
Q_ext for the cavity we are building".
"""
import json
import math
import pathlib
import sys

import eigmodes
import slug as S
from e0_solver_vs_math import eigen_cfg, run
from e0k2_anchor import wall_sigma
from h3_ladder import purity, PROBE_PHI_DEG, PROBE_R_FRAC
from h3_loaded import drude   # 🔑 the SAME model h3_driven used to build these meshes
# 🔴 design_point() is NOT imported: it returns a TUPLE (a_mm, L_mm), and the
# radius is already in the mesh sidecar. Reading it from `meta` also guarantees
# the probes sit in the cavity actually being solved.

# 🔑 THE RUN NAMES ITSELF FROM ITS SLUG. `TAG = "h3_qext"` named the PROGRAM,
# so every run of it wrote to the same files and overwrote the last
# (CONVENTIONS 7ap). Now: --slug picks the config, the config supplies every
# parameter, and the stamp (hash of that config) goes into every output name so
# an edited config cannot silently reuse a filename (7bd).
SLUG = S.parse()
CFG = S.config(SLUG)
P = CFG["_run"]["parameters"]
TAG = S.out(SLUG)

# 🔑 PRIOR ART, not re-derived: h3_step3's validated eigen settings, carried by
# h3_loopq and e3_closure unchanged.
_E = P["eigen"]
N_MODES = _E["n_modes"]
EIGEN_TARGET = _E["target"]
CASE_TIMEOUT_S = float(_E["case_timeout_s"])
WINDOW = tuple(_E["window"])
CONT_MAX_MHZ = float(_E["continuation_max_mhz"])

# (mesh tag written by h3_driven, n_e, label)   -- meshes ALREADY ON DISK
# 🔑 CASES COME FROM THE CONFIG, not a literal here. The mesh tags moved in the
# 2026-08-25 migration (h3_driven_* -> h3-driven-00_*) and a hardcoded list would
# now point at files that do not exist. The seeds are the f0 h3_driven MEASURED
# on each of these very meshes, so selection is continuation from a measurement.
CASES = [(c["mesh_tag"], float(c["ne"]), c["label"], float(c["seed_ghz"]))
         for c in P["cases"]]

# What h3_driven's own S11 dip implies, for the comparison this rig exists to
# make. 🔴 UPDATED 2026-08-25: the previous values (8462 / 8221 / 9221) came from
# a fit that SNAPPED the 3 dB edges to the sample grid. Refitting with
# interpolated crossings (CONVENTIONS 7bh) moves them, and the COLD value then
# agrees with this rig's own eigen pair to 0.78% (9,045 vs 9,117) — which is what
# validates the driven fit at all. 8,462 is RETRACTED in baselines.json.
DRIVEN_IMPLIED = {0.0: 9045.0, 7.9e18: 8243.0, 1.0e20: 9322.0}
LOOPQ_EIGEN_NO_TORCH = 9231.0


def solve_one(mesh_tag, meta, ne, port_bc, w, seed):
    """One eigen solve BOUND TO AN EXISTING MESH. Returns the picked mode."""
    tag = S.out(SLUG, mesh_tag.split("_", 1)[-1], port_bc)
    attrs = meta["attributes"]
    vols = sorted({v for k, v in attrs.items()
                   if isinstance(v, int) and k not in ("wall", "port")}
                  | set(attrs.get("air") or []))
    # 🔴 mesh comes from the SIDECAR, never from `tag` -- GATE 5 exists for that.
    c = eigen_cfg(tag, meta, mesh=meta["mesh"], sigma=wall_sigma(),
                  n=N_MODES, target=EIGEN_TARGET, port_bc=port_bc)
    c["Solver"]["Order"] = 2
    if ne > 0:
        eps_p, sig_p = drude(ne, w)
        plain = sorted(set(vols) - {attrs["plasma"]})
        c["Domains"]["Materials"] = [
            {"Attributes": plain, "Permittivity": 1.0, "Permeability": 1.0},
            {"Attributes": [attrs["plasma"]], "Permittivity": eps_p,
             "Permeability": 1.0, "Conductivity": sig_p},
        ]
        print(f"    plasma: eps={eps_p:+.3f} sigma={sig_p:.4g} S/m "
              f"on attr {attrs['plasma']}", flush=True)
    else:
        print("    plasma: NONE (cold) — eigen_cfg's eps=1 default IS the "
              "cavity h3_driven solved cold", flush=True)
    c["Domains"]["Postprocessing"]["Energy"] = (
        [{"Index": 1, "Attributes": [attrs["bore"]]}]
        + [{"Index": 10 + i, "Attributes": [v]} for i, v in enumerate(vols)])
    a_mm = meta["geometry_mm"]["radius"]
    pts = [(rf * a_mm, math.radians(pd))
           for rf in PROBE_R_FRAC for pd in PROBE_PHI_DEG]
    probe_pts = [{"r_mm": r, "phi_deg": math.degrees(p_)} for r, p_ in pts]
    c["Domains"]["Postprocessing"]["Probe"] = [
        {"Index": i + 1,
         "Center": [r * 1e-3 * math.cos(p_), r * 1e-3 * math.sin(p_), 0.0]}
        for i, (r, p_) in enumerate(pts)]
    try:
        run(tag, c, allow_lossy_eigen=True, timeout=CASE_TIMEOUT_S)
    except RuntimeError as e:
        print(f"    🔴 {str(e)[:200]}", flush=True)
        return None, "solve failed"
    # 🔑 eigmodes.read() yields {m, f, sig}. Q is NOT in it -- it comes from
    # eig.csv column 3, keyed by mode index. purity() takes (tag, idx, pts) and
    # returns {P_min, spread} or None. All three READ, not assumed (7as).
    modes = eigmodes.read(tag)
    qs = {}
    for line in (pathlib.Path("postpro") / tag /
                 "eig.csv").read_text().splitlines()[1:]:
        pp = line.split(",")
        if len(pp) > 3:
            qs[round(float(pp[0]))] = float(pp[3])
    found = []
    for md in modes:
        if not (WINDOW[0] < md["f"] < WINDOW[1]):
            continue
        idx = round(float(md["m"]))
        pu = purity(tag, idx, probe_pts) or {}
        found.append({"f_ghz": md["f"], "Q": qs.get(idx), "mode_index": idx,
                      "P_min": pu.get("P_min"), "spread": pu.get("spread")})
    if not found:
        return None, f"no modes in {WINDOW}"
    m = min(found, key=lambda f: abs(f["f_ghz"] - seed))
    d = (m["f_ghz"] - seed) * 1e3
    if abs(d) > CONT_MAX_MHZ:
        return None, (f"continuation BROKE: nearest mode is {d:+.2f} MHz from "
                      f"the measured {seed:.5f} (limit {CONT_MAX_MHZ})")
    m["n_in_window"] = len(found)
    return m, f"continuation {d:+.3f} MHz"


def main():
    w = 2 * math.pi * 2.45e9
    print(f"  sigma_wall={wall_sigma():.4g} S/m   (bound from baselines.json)")
    print(f"  eigen: target={EIGEN_TARGET} N={N_MODES} order 2 — PRIOR ART "
          f"(h3_step3), not re-derived")
    print("  🔑 NO MESH IS BUILT. Every solve binds an existing h3_driven mesh.")
    out = {"slug": SLUG, "stamp": S.stamp(SLUG), "tag": TAG, "cases": [],
           "driven_implied": {str(k): v for k, v in DRIVEN_IMPLIED.items()},
           "loopq_eigen_no_torch": LOOPQ_EIGEN_NO_TORCH}
    for mesh_tag, ne, label, seed in CASES:
        mp = pathlib.Path(f"{mesh_tag}.meta.json")
        if not mp.exists():
            print(f"  🔴 {label}: {mp} MISSING — h3_driven must have run here")
            out["cases"].append({"label": label, "ne": ne,
                                 "error": f"{mp} missing"})
            continue
        meta = json.loads(mp.read_text())
        rec = {"label": label, "ne": ne, "mesh": meta["mesh"],
               "tets": meta.get("tets"), "size_factor": meta.get("size_factor")}
        print(f"\n  --- {label}   mesh={meta['mesh']}  tets={meta.get('tets')}")
        qs = {}
        for port_bc in ("pec", "lumped"):
            best, why = solve_one(mesh_tag, meta, ne, port_bc, w, seed)
            if not best or best.get("Q") is None:
                rec[f"{port_bc}_error"] = why
                print(f"    🔴 {port_bc}: {why}", flush=True)
                continue
            qs[port_bc] = best
            rec[port_bc] = best
            print(f"    {port_bc:6s} f0={best['f_ghz']:.6f}  "
                  f"Q={best['Q']:,.1f}  P_min={best.get('P_min')}  "
                  f"({why}, {best['n_in_window']} in window)", flush=True)
        if "pec" in qs and "lumped" in qs:
            Q0, QL = qs["pec"]["Q"], qs["lumped"]["Q"]
            # 🔴 CONDITIONING FLIPS WITH beta (CONVENTIONS 7at, measured
            # 2026-08-25). Q_ext = 1/(1/Q_L - 1/Q0) DIFFERENCES two nearly-equal
            # numbers whenever beta << 1: at 1e20, Q0-Q_L = 2.7 on ~163, so a
            # 0.1% error in Q_L moves Q_ext by 6.4% — a 64x amplification. The
            # DRIVEN dip does not difference anything (beta comes from the dip
            # DEPTH), so at loaded densities the driven value is ~60x better
            # conditioned. COLD is the reverse: beta=4.77, Q0/Q_L=5.8, and the
            # eigen pair is the reliable one.
            # ⚠️ Reported anyway, with the amplification alongside, so the number
            # cannot be read as comparable when it is not.
            if QL < Q0:
                qe = 1.0 / (1.0 / QL - 1.0 / Q0)
                amp = Q0 / (Q0 - QL) if Q0 > QL else float("inf")
                rec.update(Q0=Q0, Q_L=QL, Q_ext=qe, beta=Q0 / qe,
                           q_ext_amplification=amp,
                           q_ext_ill_conditioned=bool(amp > 10.0))
                d = DRIVEN_IMPLIED.get(ne)
                print(f"    ✅ Q0={Q0:,.0f}  Q_L={QL:,.0f}  "
                      f"Q_ext={qe:,.0f}  beta={Q0/qe:.4f}")
                if amp > 10.0:
                    print(f"    ⚠️  Q_ext AMPLIFIES Q_L error {amp:.0f}x "
                          f"(Q0-Q_L={Q0-QL:.1f}). At beta<<1 the DRIVEN dip is "
                          f"the better-conditioned instrument — do not read a "
                          f"few % here as a disagreement.")
                if d:
                    print(f"       driven dip implied {d:,.0f} on THIS mesh "
                          f"-> {100*(qe/d-1):+.1f}%")
                    print(f"       h3_loopq eigen (NO torch) {LOOPQ_EIGEN_NO_TORCH:,.0f} "
                          f"-> {100*(qe/LOOPQ_EIGEN_NO_TORCH-1):+.1f}%")
            else:
                rec["error"] = (f"Q_L={QL:,.0f} >= Q0={Q0:,.0f} — impossible; "
                                f"the lumped port is not loading the cavity")
                print(f"    🔴 {rec['error']}")
        out["cases"].append(rec)
        pathlib.Path(S.outfile(SLUG, "result.json")).write_text(
            json.dumps(out, indent=1) + "\n")
    print(f"\n  wrote {S.outfile(SLUG, 'result.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
