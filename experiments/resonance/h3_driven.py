"""H3/H6 (driven) — sustainment across the density gap eigen cannot enter.

🔴 WHY THIS RIG EXISTS. Two open questions need the same thing:

  H6  what is the minimum ne that still sustains? eta falls 0.947 (ne=1e20) ->
      0.185 (1e18), and ne=1e19 has NO DATA — it failed in h3_loaded (mesh
      ScaledJac) and in h3_eigenprobe (PCG stagnation, 92 non-convergences).
      Mass loading from a real high-TDS sample pushes ne DOWN, into exactly
      that gap. This gates H5.
  sapphire  its loaded point does not converge in eigen either (eps +11.6
      beside the plasma's -30.09).

🔑 DRIVEN COST SCALES WITH Q, so it is cheapest exactly where eigen fails. The
step must resolve the linewidth = f0/Q, so samples ~ Q. Calibrated on
e0k2_c11x8_drv (16,000 samples / 1,542 s = 96 ms/sample):

    empty cavity   Q=44,384  ->  ~24,000 samples  ~2,300 s
    loaded plasma  Q=156     ->  ~126 samples     ~12 s

⚠️ BUT THE GAP IS NOT THE LOADED REGIME. If eta at ne=1e19 is ~0.5 then
Q ~ 22,000 and a +-40 MHz sweep is ~18,000 samples (~29 min) — per point. The
cost is set by Q, which is THE UNKNOWN. So:

## Two stages, and the second is sized by the first

  COARSE  +-40 MHz, step 636 kHz (~126 samples, ~12 s). Finds WHERE the dip is.
          Too coarse to fit Q; it is not asked to.
  FINE    +-5 MHz about the located dip, step from the coarse dip's own width.
          8x cheaper than a wide fine sweep because the band, not the step,
          is what a located dip lets you shrink.

🔴 EIGEN IS NOT AN OPTION HERE (CONVENTIONS §7c: one rig, one solver — this is
the DRIVEN driver; h3_eigen and h3_superpose are the eigen ones). Driven has no
NLEPS and no divergence-free projection, which is the specific machinery that
stagnates at these permittivities.

## The mode-identity hazard, and how it is handled

🔴 A CAP LOOP CHANGES WHICH MODE IT READS. Small loops couple to a TM111
polarisation and only reach TE011 above ~176 mm^2; the dip looks the same either
way, so a driven sweep ALONE cannot tell you. This rig therefore:
  - uses the 11x8 cap loop (176 mm^2, the measured TE011 branch), and
  - VALIDATES against eigen at the two densities where eigen converges, before
    trusting driven where it does not.
⚠️ The band also protects: TM111 sits 332.7 MHz away, far outside +-40 MHz.

VERIFICATION
  V1  ne=1e20 driven must reproduce h3_superpose's eigen f0=2.481566 GHz within
      1 MHz and Q0 = Q_L(1+beta) within 15% of eigen's 163.
  V2  ne=1e18 driven must reproduce h3_loaded's eigen eta=0.185 within 0.05.
      Two anchors, one at each end of the gap, or the gap is not bridged.
  V3  every case reports its coarse dip AND its fine fit; a fine band that does
      not contain the coarse dip is a REFUSAL, not a silent re-centre.
FALSIFICATION
  🔴 F1  if eta at ne=1e19 is below 0.5, the sustaining margin is one decade or
         less and mass loading is a hard constraint on the nebuliser. Report it.
  🔴 F2  if driven ALSO fails to converge at eps ~ 0, the limitation is the
         OPERATOR and not the eigen formulation — no solver in this toolchain
         answers H6. Say so; do not reach for a third solver.
  🔴 F3  if the coupling branch is AMBIGUOUS the fit refuses rather than
         guessing beta; Q_L still stands and is reported alone.
"""
import json
import math
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import solveconf
# 🔴 GEO_DESIGN, not GEO. GEO is the BARE cavity (groove 0,0) and exists
# for instrument rigs comparing against closed form. This rig produces
# DESIGN numbers, so it needs the cavity being built — groove 5x10 (H2).
# Every result this rig produced before 2026-08-23 was groove-free and is
# DISCARDED; see CONVENTIONS §7f.
from e0_solver_vs_math import GEO_DESIGN as GEO, run
from e0k2_anchor import (design_point, wall_sigma, analyse_driven as fit,
                         LOOP_PHI, LOOP_RW, LOOP_GAP)
from h3_loaded import drude, Z_FRAC, SECTORS, LOOP_LD, LOOP_LW, CAP_R_FRAC

TAG = "h3_driven"
Q_BARE = 44384.0            # empty, NO loop — the eta reference
RI, RO = 2.00, 8.50         # h3_annular's operating point
CASE_TIMEOUT_S = 1800.0
SIZE_FACTORS = ["1.5", "1.42", "1.58"]

# the density grid. 1e18 and 1e20 are ANCHORS (eigen has them); the rest is the
# gap. 3e18 sits closest to the eps sign change (eps=+0.067).
NE_GRID = [1.0e18, 3.0e18, 1.0e19, 3.0e19, 1.0e20]
ANCHORS = {1.0e20: {"f_ghz": 2.481566, "Q": 163.0},
           1.0e18: {"eta": 0.185}}

# 🔴 STAGE 1 IS WIDE AND COARSE, and both halves of that were wrong before.
#
# v1 used a 636 kHz step — one linewidth of the ne=1e20 case — and would have
# been blind to the 68 kHz dip at ne=1e18. v2 fixed the step (20 kHz) but kept a
# 45 MHz band, and THAT was the binding constraint: the loaded resonances run
# 7 MHz to >45 MHz wide, so the 3 dB points fell outside the band on 4 of 5
# cases and a second, broader feature at ~2.447 GHz sat partly inside it.
#
# 🔑 The real requirement is to BRACKET the widest feature, not to resolve the
# narrowest. 2.30-2.65 GHz at 200 kHz is 1,750 samples — FEWER than the 2,250
# v2 spent — and it brackets 7 MHz to ~350 MHz while still putting 34 points
# across the narrowest linewidth measured (6.84 MHz at ne=1e18).
COARSE_LO_GHZ, COARSE_HI_GHZ = 2.30, 2.65
COARSE_STEP_GHZ = 200e-6
MINIMA_WINDOW = 20              # samples each side to call something a local min
FINE_MIN_SAMPLES_ACROSS = 20    # refine only if the coarse width is thinner
COARSE_MIN_DEPTH_DB = 0.05      # a real dip in a noiseless solve is still a dip
COARSE_EDGE_MHZ = 2.0           # a selected dip this close to an edge is unbracketed
CONTINUATION_JUMP_MHZ = 25.0    # a bigger step than this between cases is REPORTED

Q_EXT_EST = 50709.0
SHALLOW_DB = 0.30       # below this the dip is too shallow to trust a fit from


def save(out):
    p = pathlib.Path(f"{TAG}.result.json")
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def build_mesh(tag, a, L, zlo, zhi, eps_p, sig_p, rec):
    """Mesh with the cap loop AND the plasma. Returns meta or None."""
    thick = RO - RI
    ph_mesh = min(1.0, max(0.30, thick / 6.0))
    args = ([x for x in GEO if x != "--no-torch"]
            + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
               "--sectors", str(SECTORS),
               "--torch-material", "1.0,3.5e-05",
               "--plasma", f"{RI},{RO},{zlo:.4f},{zhi:.4f}",
               "--plasma-h", f"{ph_mesh:.3f}",
               "--loop", f"{LOOP_LD},{LOOP_LW},{LOOP_RW},{LOOP_GAP}",
               # 🔴 --loop-cap IS NOT OPTIONAL. Without it the loop mounts on the
               # BARREL, where the radius is forced to a and it links H_z rather
               # than H_r — a different coupling to a different field component,
               # i.e. a different instrument. h3_loaded and e0k2_anchor both
               # mount on the CAP at CAP_R_FRAC*a, and V1/V2 compare against
               # their numbers. Omitting it silently changes what is measured.
               "--loop-cap", f"{CAP_R_FRAC * a:.4f}",
               "--loop-phi", LOOP_PHI])
    for sf in SIZE_FACTORS:
        r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                            "--size-factor", sf] + args,
                           capture_output=True, text=True)
        if not r.returncode and pathlib.Path(f"{tag}.msh").exists():
            rec["size_factor"] = sf
            if sf != SIZE_FACTORS[0]:
                print(f"    ⚠️ mesh needed size-factor {sf}; REPORTED", flush=True)
            return solveconf.load_meta(f"{tag}.msh")
        rec["_last_mesh_err"] = (r.stdout + r.stderr)[-200:]
    return None



def local_minima(d, window=MINIMA_WINDOW):
    """Every local minimum of |S11|, not just the deepest.

    🔴 WHY THIS EXISTS. `analyse_driven` returns the GLOBAL minimum. At ne=1e20
    the band holds TWO features — a broad one at 2.4472 (-1.28 dB) and TE011 at
    2.4824 (-0.35 dB) — so the global minimum is the wrong mode, and every
    downstream guard then fires honestly on a feature nobody wanted. §1:
    "deepest" is a proxy for "the one we want", and it is a bad one.
    """
    out = []
    for i in range(window, len(d) - window):
        if d[i][1] == min(x[1] for x in d[i - window:i + window + 1]):
            if not out or abs(d[i][0] - out[-1][1]) > 2e-3:
                out.append((i, d[i][0], d[i][1]))
    return out


def fit_dip(d, i0):
    """beta, 3 dB width, Q_L, Q0 for the resonance at index i0.

    🔑 The outward search STOPS AT A LOCAL MAXIMUM. With two overlapping
    resonances the baseline is not flat, and a naive 3 dB crossing walks out of
    one feature and into its neighbour — which is how v2 got "3 dB points not
    inside the band" on cases whose dip was perfectly well resolved. The turning
    point between two dips is the honest edge of this one.
    """
    f0, s0db = d[i0]
    S0 = 10 ** (s0db / 20)
    b = (1 - S0) / (1 + S0)                 # undercoupled branch; beta<<1 here
    amax = 1 - S0 ** 2
    tgt = math.sqrt(max(0.0, 1 - amax / 2))

    def walk(rng):
        prev, pf = None, None
        for i in rng:
            v = 10 ** (d[i][1] / 20)
            if prev is not None:
                if (prev - tgt) * (v - tgt) <= 0:      # crossed the 3 dB level
                    return d[i][0], None
                if v < prev:                            # turned back down: next feature
                    return None, f"turned at {d[i][0]:.4f} GHz before reaching 3 dB"
            prev, pf = v, d[i][0]
        return None, "reached the band edge"

    fl, why_l = walk(range(i0, -1, -1))
    fh, why_h = walk(range(i0, len(d)))
    half = None
    if fl is not None and fh is not None:
        lw = fh - fl
    elif fl is not None or fh is not None:
        # 🔑 ONE-SIDED FALLBACK. A Lorentzian is symmetric about f0, so a single
        # measurable half-width determines the whole. This rescues the common
        # case where one flank runs into a neighbouring resonance or the band
        # edge while the other is clean. ⚠️ It ASSUMES symmetry, which two
        # overlapping resonances violate — so it is FLAGGED, not silent, and the
        # side used is recorded.
        half = "low" if fl is not None else "high"
        lw = 2 * (f0 - fl) if fl is not None else 2 * (fh - f0)
        if lw <= 0:
            return {"f0": f0, "s11_db": s0db, "beta": b,
                    "error": f"one-sided width came out non-positive ({half})"}
    else:
        return {"f0": f0, "s11_db": s0db, "beta": b,
                "error": f"3 dB width not measurable (low: {why_l or 'ok'}; "
                         f"high: {why_h or 'ok'})"}
    ql = f0 / lw
    r = {"f0": f0, "s11_db": s0db, "beta": b, "f_lo": fl, "f_hi": fh,
         "linewidth_mhz": lw * 1e3, "Q_L": ql, "Q0": ql * (1 + b),
         "n_across": abs(lw) / COARSE_STEP_GHZ}
    if half:
        r["one_sided"] = half
        r["one_sided_reason"] = why_h if half == "low" else why_l
    return r


def read_s11(tag):
    import csv as _csv
    rows = list(_csv.reader(open(f"postpro/{tag}/port-S.csv")))
    h = [x.strip() for x in rows[0]]
    si = next(i for i, c in enumerate(h) if "S" in c and "dB" in c)
    return [(float(r[0]), float(r[si])) for r in rows[1:] if r and r[0].strip()]


def sweep(mesh_tag, out_tag, band, step, eps_p, sig_p, attrs):
    """One driven sweep over an EXISTING mesh.

    🔴 mesh_tag AND out_tag, separately, and this cost a launch. The first
    version took one `tag`, and the caller passed `f"{tag}_coarse"` so the two
    stages would not overwrite each other's postpro — which also made it look
    for `h3_driven_n18p00_coarse.msh`, a mesh that was never built. One mesh
    feeds BOTH stages; only the OUTPUT tag differs.
    """
    # 🔴 ASK THE DIRECT QUESTION FIRST (§1). The mesh either has a plasma
    # attribute or it does not; discovering that by parsing a "dropped" message
    # afterwards is inference from a proxy.
    pa = attrs.get("plasma")
    if pa is None:
        raise RuntimeError(f"{out_tag}: mesh has NO plasma attribute — there is "
                           f"nothing to load the cavity with.")
    mats = {pa: {"Permittivity": eps_p, "Conductivity": sig_p,
                 "Permeability": 1.0}}
    c, _meta, dropped = solveconf.driven(f"{mesh_tag}.msh", out_tag, band,
                                         step=step, order=2, materials=mats)
    # ⚠️ `dropped` is mostly BENIGN: the shared template asks for a brake/mode
    # filter that this mesh does not carry (--brake 0), and driven records that
    # rather than raising. My first guard refused on ANY drop and killed all
    # five cases on it. Report them (§3) — refuse only on the one that matters.
    if dropped:
        print(f"    ⚠️ template materials not in this mesh (benign): "
              f"{dropped}", flush=True)
    # 🔑 §7d — verify with the CONSUMER, using a value the request did not
    # supply: is the plasma actually in the config being solved, with the
    # conductivity asked for? A dropped or mis-bound plasma yields a perfectly
    # plausible UNLOADED resonance and nothing downstream could tell.
    got = [m for m in c["Domains"]["Materials"] if pa in (m.get("Attributes") or [])]
    if not got:
        raise RuntimeError(f"{out_tag}: plasma attribute {pa} is in the mesh but "
                           f"NO material in the solved config covers it — this "
                           f"would solve an EMPTY cavity and call it loaded.")
    gs = float(got[0].get("Conductivity", 0.0))
    if abs(gs - sig_p) > 1e-9 * max(1.0, abs(sig_p)):
        raise RuntimeError(f"{out_tag}: plasma conductivity in the config is "
                           f"{gs}, not the {sig_p} requested.")
    print(f"    plasma: attr {pa}, eps={eps_p:+.3f}, sigma={gs:.4g} S/m "
          f"(verified in the solved config)", flush=True)
    run(out_tag, c, timeout=CASE_TIMEOUT_S)
    return fit(out_tag)


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    w = 2.0 * math.pi * 2.45e9
    zlo, zhi = -Z_FRAC * L, Z_FRAC * L
    exact = ph.spectrum(a, L, fmax=3.2)["TE011"]
    print(f"  cavity a={a:.4f} L={L:.4f}  Q_bare(no loop)={Q_BARE:,.0f}")
    print(f"  plasma r={RI}-{RO} mm  z=+-{Z_FRAC}L   cap loop "
          f"{LOOP_LD}x{LOOP_LW} mm (TE011 branch)")
    ncoarse = round((COARSE_HI_GHZ - COARSE_LO_GHZ) / COARSE_STEP_GHZ)
    print(f"  ONE wide sweep {COARSE_LO_GHZ}-{COARSE_HI_GHZ} GHz @ "
          f"{COARSE_STEP_GHZ*1e6:.0f} kHz ({ncoarse:,} samples per case)")
    print(f"  selection: CONTINUATION from the unloaded TE011, seeded at "
          f"{exact:.4f} GHz; NOT the global minimum")
    print(f"  guards: dip >{COARSE_MIN_DEPTH_DB} dB, >{COARSE_EDGE_MHZ} MHz from "
          f"a band edge, continuation step <{CONTINUATION_JUMP_MHZ:.0f} MHz, "
          f"3 dB walk stops at the turning point between features\n", flush=True)
    print("  coupling forecast (beta = Q0/Q_ext, Q_ext ~ "
          f"{Q_EXT_EST:,.0f} from e0k2's 11x8 loop):")
    print(f"    {'eta':>8}{'Q0':>9}{'beta':>9}{'|S11|min':>11}")
    for eta in (0.185, 0.5, 0.9, 0.99, 0.9963):
        q0 = Q_BARE * (1 - eta)
        b = q0 / Q_EXT_EST
        db = 20.0 * math.log10(abs((1 - b) / (1 + b)))
        print(f"    {eta:>8.4f}{q0:>9,.0f}{b:>9.4f}{db:>10.2f}dB"
              + ("" if abs(db) >= SHALLOW_DB else "   🔴 too shallow to fit"))
    print("    ⚠️ the ne=1e20 end is where driven is WEAKEST and eigen already "
          "works; the gap is where driven is strongest.\n", flush=True)
    out = {"q_bare_no_loop": Q_BARE, "ri_mm": RI, "ro_mm": RO,
           "q_ext_est": Q_EXT_EST, "shallow_db": SHALLOW_DB,
           "ne_grid": NE_GRID, "anchors": {str(k): v for k, v in ANCHORS.items()},
           "points": []}

    # continuation seed: the UNLOADED TE011. At ne=1e18 the pull is
    # only ~+2 MHz, so the first step is unambiguous.
    expect = exact
    for ne in NE_GRID:
        eps_p, sig_p = drude(ne, w)
        tag = f"{TAG}_n{math.log10(ne):.2f}".replace(".", "p").replace("+", "")
        rec = {"ne": ne, "eps": eps_p, "sigma": sig_p, "tag": tag}
        print(f"  --- ne={ne:.1e}  eps={eps_p:+.3f}  sigma={sig_p:.4g} S/m",
              flush=True)
        meta = build_mesh(tag, a, L, zlo, zhi, eps_p, sig_p, rec)
        if meta is None:
            rec["error"] = f"mesh failed: {rec.pop('_last_mesh_err','')[:150]}"
            print(f"    🔴 {rec['error']}\n    REPORTED.", flush=True)
            out["points"].append(rec); save(out); continue
        rec.pop("_last_mesh_err", None)
        attrs = meta["attributes"]
        rec["tets"] = meta["tets"]

        # ---- STAGE 1: one WIDE sweep. Everything is extracted from it.
        band = (COARSE_LO_GHZ, COARSE_HI_GHZ)
        try:
            sweep(tag, f"{tag}_wide", band, COARSE_STEP_GHZ, eps_p, sig_p, attrs)
        except RuntimeError as e:
            rec["error"] = f"wide sweep failed: {str(e)[:160]}"
            print(f"    🔴 {rec['error']}\n    REPORTED.", flush=True)
            out["points"].append(rec); save(out); continue
        d = read_s11(f"{tag}_wide")
        mins = [m for m in local_minima(d) if abs(m[2]) >= COARSE_MIN_DEPTH_DB]
        rec["minima"] = [{"f_ghz": f, "s11_db": v} for _, f, v in mins]
        print(f"    {len(mins)} local minima: "
              + "  ".join(f"{f:.4f}@{v:.2f}dB" for _, f, v in mins[:6]), flush=True)
        if not mins:
            rec["error"] = "no local minimum anywhere in 2.30-2.65 GHz"
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue

        # ---- SELECT BY CONTINUATION, not by depth.
        # 🔑 `expect` starts at the UNLOADED TE011 (the plasma is a weak
        # perturbation at the lowest density) and then follows the mode. E1b:
        # identity across a large perturbation needs CONTINUATION, not endpoint
        # pairing — and the pull here is +2 MHz to +32 MHz in smooth steps.
        i_sel, f_sel, v_sel = min(mins, key=lambda m: abs(m[1] - expect))
        jump = (f_sel - expect) * 1e3
        rec["expect_ghz"], rec["jump_mhz"] = expect, jump
        if abs(jump) > CONTINUATION_JUMP_MHZ:
            rec["error"] = (f"continuation BROKE: nearest minimum to {expect:.4f} "
                            f"is {f_sel:.4f} GHz, a {jump:+.1f} MHz jump "
                            f"(> {CONTINUATION_JUMP_MHZ} MHz). Either the mode "
                            f"moved further than one step allows or this is a "
                            f"different mode. REPORTED, not followed.")
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        edge = min(f_sel - COARSE_LO_GHZ, COARSE_HI_GHZ - f_sel) * 1e3
        if edge < COARSE_EDGE_MHZ:
            rec["error"] = (f"selected dip {f_sel:.4f} GHz is {edge:.1f} MHz from "
                            f"a band edge — not bracketed (§1)")
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        print(f"    selected {f_sel:.6f} GHz ({jump:+.2f} MHz from expected "
              f"{expect:.4f}) — by CONTINUATION, not depth", flush=True)

        fi = fit_dip(d, i_sel)
        rec["wide_fit"] = fi
        if "Q_L" not in fi:
            rec["error"] = f"wide: {fi['error']}"
            print(f"    🔴 {rec['error']}", flush=True)
            expect = f_sel                  # the LOCATION is still good
            out["points"].append(rec); save(out); continue
        if fi["n_across"] < FINE_MIN_SAMPLES_ACROSS:
            print(f"    ⚠️ only {fi['n_across']:.0f} samples across the 3 dB "
                  f"width — width is under-resolved, Q_L is indicative only",
                  flush=True)
            rec["width_under_resolved"] = True
        if abs(fi["s11_db"]) < SHALLOW_DB:
            rec["shallow"] = True
            print(f"    ⚠️ |S11|min={fi['s11_db']:.3f} dB — deeply UNDERCOUPLED, "
                  f"beta and Q0 are LOW CONFIDENCE (Q_L stands; beta<<1 makes "
                  f"Q_L ~ Q0)", flush=True)
        rec["Q0"] = fi["Q0"]
        rec["eta"] = 1.0 - fi["Q0"] / Q_BARE
        expect = fi["f0"]                   # advance the continuation
        print(f"    f0={fi['f0']:.6f} GHz  lw={fi['linewidth_mhz']:.2f} MHz  "
              f"Q_L={fi['Q_L']:,.0f}  beta={fi['beta']:.4f}  Q0={fi['Q0']:,.0f}  "
              f"eta={rec['eta']:.4f}", flush=True)
        out["points"].append(rec); save(out)
    _report(out)


def _report(out):
    print("\n" + "=" * 78)
    print(f"  {'ne':>9}{'eps':>9}{'f0 GHz':>11}{'lw MHz':>9}{'Q_L':>8}"
          f"{'beta':>8}{'Q0':>7}{'eta':>9}")
    for p in out["points"]:
        if p.get("eta") is None:
            print(f"  {p['ne']:>9.1e}{p['eps']:>9.3f}   🔴 "
                  + p.get("error", "no result")[:46])
            continue
        f = p["wide_fit"]
        flag = ""
        if f.get("one_sided"):
            flag = f"  1-sided({f['one_sided']})"
        elif p.get("width_under_resolved"):
            flag = "  width thin"
        print(f"  {p['ne']:>9.1e}{p['eps']:>9.3f}{f['f0']:>11.4f}"
              f"{f['linewidth_mhz']:>9.2f}{f['Q_L']:>8.0f}{f['beta']:>8.4f}"
              f"{f['Q0']:>7.0f}{p['eta']:>9.4f}{flag}")
    P = {p["ne"]: p for p in out["points"] if p.get("eta") is not None}
    print()
    # 🔴 THE ANCHOR IS ne=1e20 AGAINST EIGEN ON THE SAME GEOMETRY.
    # It was ne=1e18 vs h3_loaded's eta=0.185 — a 2 mm SOLID COLUMN against this
    # rig's 2.0-8.5 mm ANNULUS, 17x the plasma. That is a §4b geometry mismatch
    # and it fired on my own error, not on the method. The only eigen number for
    # THIS geometry is h3_superpose's vac_hot: f0=2.481566, Q=163, eta=0.9963.
    a = P.get(1.0e20)
    if a:
        df = abs(a["wide_fit"]["f0"] - 2.481566) * 1e3
        de = abs(a["eta"] - 0.9963)
        print(f"  V1 ne=1e20 vs eigen (SAME geometry, h3_superpose vac_hot):")
        print(f"     f0 {a['wide_fit']['f0']:.4f} vs 2.481566 -> {df:.2f} MHz "
              + ("✅" if df <= 2.0 else "🔴 FIRES"))
        print(f"     eta {a['eta']:.4f} vs 0.9963 -> {de:.4f} "
              + ("✅" if de <= 0.01 else "🔴 FIRES"))
        print(f"     ⚠️ Q0 {a['wide_fit']['Q0']:.0f} vs eigen 163 — these differ "
              f"much more than eta does, because eta = 1 - Q0/Q_bare is "
              f"INSENSITIVE to Q0 when Q0 << Q_bare. Quote eta, not Q0.")
    else:
        print("  🔴 V1 anchor ne=1e20 missing — driven is UNVALIDATED against "
              "eigen and nothing here should be quoted.")
    g = P.get(1.0e19)
    if g:
        print(f"\n  🔑 THE GAP: eta(ne=1e19, eps=-2.109) = {g['eta']:.4f}")
        print("  F1 " + ("🔴 FIRES — eta < 0.5 one decade below the operating "
                         "point; mass loading is a HARD nebuliser constraint."
                         if g["eta"] < 0.5 else
                         f"✅ eta = {g['eta']:.4f} >= 0.5 — the margin survives. "
                         f"Mass loading is NOT a hard EM constraint."))
    else:
        print("\n  🔴 ne=1e19 missing — the gap is NOT bridged (F2).")
    es = [p["eta"] for p in out["points"] if p.get("eta") is not None]
    if len(es) >= 2:
        print(f"\n  eta spans {min(es):.4f}-{max(es):.4f} across ne "
              f"{min(P):.0e}-{max(P):.0e} — absorption stays above "
              f"{100*min(es):.1f}% over {math.log10(max(P)/min(P)):.0f} decades.")
    print(f"\n  wrote {TAG}.result.json")


if __name__ == "__main__":
    main()
