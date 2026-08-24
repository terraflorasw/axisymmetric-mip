"""H3 — COLD and LOADED in the cavity that is actually being built.

**The first measurement of the re-do.** Everything H3 produced on 2026-08-23 ran
on a groove-free cavity and is discarded. This rig uses `GEO_DESIGN` — H2's
groove, frozen at 5 x 10 mm — and `run()` refuses a plasma solve without it.

## What it settles, and it is three queue items at once

  1a  **the eta REFERENCE.** Every loaded eta on 2026-08-23 divided by
      Q_BARE = 44,384: the NO-LOOP, NO-GROOVE value. 29,854 is not the
      (⚠️ 2026-08-24: the DESIGN cavity's own reference is 12,368 — groove
      5x10 + loop 11x8, `h3_ladder`. Neither bare number substitutes.)
      substitute either — it is groove-free AND from a different loop. There is
      no number to look up. **Q_bare must be SOLVED, per loop size, on the
      grooved looped mesh.** That is the unloaded case here.
  1c  **mode identity under the groove.** h3_groove's F2 fired: TE011 appeared to
      move -12.80 MHz at 28x20 but +0.00 at 11x8. A driven |S11| minimum cannot
      tell a shifted mode from a misidentified one. Eigen + azimuthal order can.
  2   **H3 COLD** — f0, Q0 and the mode landscape a tuner sees before ignition.

## Why EIGEN

INSTRUMENT's own rule: *"if the criterion is 'which mode, at what frequency,
with what Q0', it is eigen."* All three items are exactly that. Driven returns a
dip, not a label — which is what left 1c unresolved in the first place.
⚠️ The eigen convergence envelope in INSTRUMENT is itself groove-free and flagged
for re-check. If a case here fails to converge, that is DATA about the envelope,
not a reason to switch solvers mid-rig (§7c).

## Anchors, named before starting (§7g)

**E0** — the unloaded frequency must agree with `physics.spectrum()` closed form.
**H1** — the design point a = 88.0045, L = 115.4158 (analytic max-min optimum).
**H2** — the groove, 5 x 10 mm, whose sufficiency was established against the
LDMOS band. Not against any earlier result of mine.

VERIFICATION
  V1  the groove must be IN THE MESH (sidecar `groove == [5.0, 10.0]`), or the
      case is refused. Not inferred from the flag list.
  V2  TE011 identified by AZIMUTHAL ORDER (m=0) and reported with its A2/A0,
      never by max-Q and never by proximity to 2.45.
  V3  unloaded TE011 must sit within 2 MHz of `physics.spectrum()`'s closed form
      after allowing for the loop (e0k2: a cap loop shifts 0.37-0.44 MHz).
FALSIFICATION
  🔴 F1  **if MORE THAN ONE mode sits in 2.40-2.50 GHz unloaded, the filter is
         not doing its job in this configuration.** Report it and stop — do NOT
         build mode-selection machinery around it. That is CONVENTIONS §7i, and
         it is the error that cost 2026-08-23.
  🔴 F2  if TE011's Q_bare with groove+loop is not between 20,000 and 45,000,
         something is wrong with the loop, the groove or the wall binding.
         The empty no-loop no-groove value is 44,384; a loop costs real Q.
  🔴 F3  if the 28x20 case shows TE011 more than 2 MHz from the 11x8 case
         unloaded, loop size is perturbing the MODE, not just the coupling —
         which would explain h3_groove's -12.80 MHz without any groove effect.
  🔴 F4  if a loaded case does not converge, REPORT it as envelope data. Do not
         retarget, do not switch to driven inside this rig.
"""
import csv
import json
import math
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import solveconf
import eigmodes
import azimuthal
from e0_solver_vs_math import GEO_DESIGN, eigen_cfg, run
from e0k2_anchor import (design_point, wall_sigma, LOOP_PHI, LOOP_RW, LOOP_GAP,
                         CAP_R_FRAC)
from e0k2_azim import sector_bins, read_sector_energy
from h3_loaded import drude, Z_FRAC, SECTORS

TAG = "h3_cold"
BAND = (2.40, 2.50)          # the LDMOS band — what a tuner can reach
WINDOW = (2.35, 2.65)        # identification window, WIDER than the band so an
                             # out-of-band mode is REPORTED, not swallowed
NE_HOT = 1.0e20
RI, RO = 2.00, 8.50
# 🔴 SPAN, NOT WALL TIME. Run 1 used target 2.30 / N=6 — a 307 MHz shift-invert
# — and 11x8 cold timed out at 174 NLEPS while PROGRESSING (budget 1,000). The
# precedent: H1 inherited `target 1.05` from E0 and paid an hour per point;
# retargeted, the same measurement took ~2 minutes. Narrow the span first.
# Cold modes measured at 28x20: 2.4048, 2.4460, 2.5314, 2.6028, 2.6067.
# target 2.38 sits below the band and above the groove-displaced TM111 (~2.386
# is close, so 2.38 keeps it visible); N=4 covers the band plus one margin mode.
N_MODES = 4
EIGEN_TARGET = 2.38
CASE_TIMEOUT_S = 1800.0      # backup, not the primary fix
SIZE_FACTORS = ["1.5", "1.42", "1.58"]
#        (loop_d, loop_hw, loaded)
# 🔑 STAGED: COLD ONLY this run. The cold cases are half the mesh (44-46k vs
# 73-81k tets), they deliver the ETA REFERENCE that gates everything downstream
# (item 1a), and they label the 28x20 two-modes-in-band result. Running the
# loaded cases now would spend ~25 min producing numbers that cannot be
# interpreted until the reference exists. Loaded follows once cold lands.
CASES = [(11.0, 8.0, False), (28.0, 20.0, False)]
CASES_LOADED_NEXT = [(11.0, 8.0, True), (28.0, 20.0, True)]   # stage 2
Q_EMPTY_NO_LOOP = 44384.0    # E0, for CONTEXT only — never as the eta reference


def save(out):
    p = pathlib.Path(f"{TAG}.result.json")
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def build_mesh(tag, a, L, ld, lw, loaded, zlo, zhi, rec):
    args = (list(GEO_DESIGN) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                                "--sectors", str(SECTORS),
                                "--loop", f"{ld},{lw},{LOOP_RW},{LOOP_GAP}",
                                "--loop-cap", f"{CAP_R_FRAC * a:.4f}",
                                "--loop-phi", LOOP_PHI])
    if loaded:
        args += ["--plasma", f"{RI},{RO},{zlo:.4f},{zhi:.4f}", "--plasma-h", "1.000"]
    for sf in SIZE_FACTORS:
        r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                            "--size-factor", sf] + args,
                           capture_output=True, text=True)
        if not r.returncode and pathlib.Path(f"{tag}.msh").exists():
            rec["size_factor"] = sf
            if sf != SIZE_FACTORS[0]:
                print(f"    ⚠️ mesh needed size-factor {sf}; REPORTED", flush=True)
            return solveconf.load_meta(f"{tag}.msh")
        rec["_err"] = (r.stdout + r.stderr)[-200:]
    return None


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma_w = wall_sigma()
    w = 2.0 * math.pi * 2.45e9
    zlo, zhi = -Z_FRAC * L, Z_FRAC * L
    exact = ph.spectrum(a, L, fmax=3.2)["TE011"]
    eps_p, sig_p = drude(NE_HOT, w)
    print(f"  cavity a={a:.4f} L={L:.4f}   groove 5x10 (GEO_DESIGN)")
    print(f"  closed form TE011 = {exact:.6f} GHz   (E0's anchor)")
    print(f"  loaded case: ne={NE_HOT:.0e}, eps={eps_p:+.3f}, sigma={sig_p:.4g} S/m")
    print(f"  identify over {WINDOW}, judge the band {BAND}\n", flush=True)
    out = {"exact_te011": exact, "band": list(BAND), "ne_hot": NE_HOT,
           "q_empty_no_loop_context": Q_EMPTY_NO_LOOP, "points": []}

    for ld, lw, loaded in CASES:
        # ⚠️ "loaded", NOT "hot". HOT is a THERMAL regime (a cavity already
        # operating, no plasma); LOADED means plasma present. Using "hot" for
        # the plasma case conflated the two and propagated the confusion.
        tag = f"{TAG}_{ld:g}x{lw:g}_{'loaded' if loaded else 'cold'}".replace(".", "p")
        rec = {"ld": ld, "lw": lw, "loaded": loaded, "tag": tag}
        print(f"  --- loop {ld:g}x{lw:g}  {'LOADED' if loaded else 'COLD'}",
              flush=True)
        meta = build_mesh(tag, a, L, ld, lw, loaded, zlo, zhi, rec)
        if meta is None:
            rec["error"] = f"mesh failed: {rec.pop('_err','')[:150]}"
            print(f"    🔴 {rec['error']}\n    REPORTED.", flush=True)
            out["points"].append(rec); save(out); continue
        rec.pop("_err", None)
        # V1 — the groove must be in the MESH, not merely in the flag list
        g = (meta.get("geometry_mm") or {}).get("groove")
        if [float(x) for x in (g or [0, 0])] != [5.0, 10.0]:
            rec["error"] = (f"V1: mesh groove is {g}, not [5.0, 10.0]. Refusing "
                            f"to measure the wrong cavity.")
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        print(f"    groove in mesh: {g} ✅   tets={meta['tets']:,}", flush=True)
        attrs = meta["attributes"]
        rec["tets"] = meta["tets"]
        bins = sector_bins(meta)
        vols = sorted({v for k, v in attrs.items()
                       if isinstance(v, int) and k not in ("wall", "port")}
                      | set(attrs.get("air") or []))
        # 🔴 port_bc="pec" — GATE 4, added 2026-08-24 (CONVENTIONS §7v).
        # This rig wants the UNLOADED Q, so the port must not be a loss
        # channel. Shorting the gap makes the loop a small closed ring
        # resonant far above the band: TE011 is left essentially
        # unperturbed (P=0.9997) and Q excludes port loss.
        # ⚠️ UNASSIGNED IS PMC — an OPEN gap, which is an LC resonator
        # near 2.45 GHz that HYBRIDISES TE011 into a pair. Everything
        # this rig produced before today was measured that way.
        c = eigen_cfg(tag, meta, mesh=f"{tag}.msh", sigma=sigma_w,
                      n=N_MODES, target=EIGEN_TARGET, port_bc="pec")
        c["Solver"]["Order"] = 2
        c["Domains"]["Postprocessing"]["Energy"] = (
            [{"Index": 1, "Attributes": [attrs["bore"]]}]
            + [{"Index": 10 + i, "Attributes": [v]} for i, v in enumerate(vols)])
        if loaded:
            others = sorted(set(vols) - {attrs["plasma"]})
            c["Domains"]["Materials"] = [
                {"Attributes": others, "Permittivity": 1.0, "Permeability": 1.0},
                {"Attributes": [attrs["plasma"]], "Permittivity": eps_p,
                 "Permeability": 1.0, "Conductivity": sig_p}]
        try:
            run(tag, c, allow_lossy_eigen=True, timeout=CASE_TIMEOUT_S)
        except RuntimeError as e:
            rec["error"] = f"F4: {str(e)[:170]}"
            print(f"    🔴 {rec['error']}\n    REPORTED as envelope data.",
                  flush=True)
            out["points"].append(rec); save(out); continue

        # V2 — identify by AZIMUTHAL ORDER, and report EVERY mode in the window
        modes = eigmodes.read(tag)
        qs = {}
        for line in (pathlib.Path("postpro") / tag /
                     "eig.csv").read_text().splitlines()[1:]:
            pp = line.split(",")
            if len(pp) > 3:
                qs[round(float(pp[0]))] = float(pp[3])
        sec = read_sector_energy(tag, bins)
        found = []
        for md in modes:
            if not (WINDOW[0] < md["f"] < WINDOW[1]):
                continue
            u = sec.get(float(md["m"]))
            if u is None and sec:
                u = sec[min(sec, key=lambda x: abs(x - md["m"]))]
            m_az, conf, harm = azimuthal.order(u) if u else (None, 0, {})
            found.append({"f_ghz": md["f"], "Q": qs.get(md["m"], 0.0),
                          "m_az": m_az, "A2_A0": harm.get(2, 0.0),
                          "in_band": BAND[0] <= md["f"] <= BAND[1]})
        rec["modes"] = found
        for m in found:
            print(f"      {m['f_ghz']:.6f} GHz  Q={m['Q']:>9,.0f}  m={m['m_az']}"
                  f"  A2/A0={m['A2_A0']:.4f}"
                  + ("  ← IN BAND" if m["in_band"] else ""), flush=True)
        # 🔴 DEGRADE, DO NOT ERROR (§7l). `azimuthal.order()` returns m=None on a
        # MIXED mode, and mixing is the PHYSICS here: loaded A2/A0 = 0.32 against
        # 0.0004 for a mode the plasma does not couple to. Run 1 tested
        # `m_az == 0` and discarded two converged measurements, then skipped the
        # report entirely.
        ib = [m for m in found if m["in_band"]]
        if not ib:
            rec["error"] = "no mode at all in the LDMOS band"
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        clean = [m for m in ib if m["m_az"] == 0]
        if clean:
            pick, how = min(clean, key=lambda m: abs(m["f_ghz"] - exact)), "m=0"
        else:
            # 🔴 EXCLUDE MODES POSITIVELY LABELLED m != 0 FIRST. The first
            # version ranked ALL in-band modes by A2/A0 and selected 2.440003 —
            # which the classifier had confidently labelled **m=1**. A mode
            # identified as m=1 is definitively NOT TE011, however low its A2/A0
            # happens to be. "Uncertain" and "known to be something else" are
            # different states and must not be pooled.
            maybe = [m for m in ib if m["m_az"] is None]
            if not maybe:
                rec["error"] = ("every in-band mode is positively labelled "
                                "m != 0 — TE011 is NOT in the band")
                print(f"    🔴 {rec['error']}", flush=True)
                out["points"].append(rec); save(out); continue
            # ⚠️ NOT "nearest 2.45" (§1). Among UNLABELLED in-band modes the
            # least mixed is the best candidate — A2/A0 measures m=1 character
            # and TE011 is the m=0 member.
            pick, how = min(maybe, key=lambda m: m["A2_A0"]), "lowest A2/A0 (unlabelled only)"
            rec["identification_uncertain"] = True
        pick = dict(pick, selected_by=how)
        rec["te011"] = pick
        print(f"    TE011 candidate {pick['f_ghz']:.6f} GHz  Q={pick['Q']:,.0f}  "
              f"by {how}  A2/A0={pick['A2_A0']:.4f}"
              + ("  ⚠️ UNCERTAIN — no clean m=0 in band"
                 if how != "m=0" else ""), flush=True)
        if not loaded:
            if rec.get("identification_uncertain"):
                # 🔴 An eta reference from an UNCERTAIN identification is worse
                # than none — it looks authoritative and propagates silently.
                print(f"    🔴 NO eta reference emitted for {ld:g}x{lw:g}: the "
                      f"TE011 identification is UNCERTAIN. A reference from a "
                      f"mode that may not be TE011 is worse than none.",
                      flush=True)
            else:
                rec["q_bare_this_loop"] = pick["Q"]
                print(f"    🔑 eta REFERENCE for {ld:g}x{lw:g}: "
                      f"Q_bare = {pick['Q']:,.0f}  (NOT 44,384, NOT 29,854)",
                      flush=True)
        out["points"].append(rec); save(out)
    # 🔴 THE REPORT RUNS NO MATTER WHAT. Run 1 lost F1 — the filter check, the
    # whole point of §7i — because an earlier case errored. A verdict that only
    # appears when everything succeeded is a verdict you will not have when you
    # most need it.
    try:
        _report(out)
    except Exception as e:
        print(f"\n  🔴 _report FAILED: {type(e).__name__}: {e}")
        print("     The DATA is in the result.json and re-scoring is free (§10).")


def _report(out):
    P = {(p["ld"], p["lw"], p["loaded"]): p for p in out["points"] if "te011" in p}
    print("\n" + "=" * 78)
    print(f"  {'loop':>9}{'state':>8}{'TE011 GHz':>12}{'Q':>11}{'m':>4}"
          f"{'A2/A0':>9}{'in band':>9}")
    for p in out["points"]:
        name = "%gx%g" % (p["ld"], p["lw"])
        st = "LOADED" if p["loaded"] else "COLD"
        if "te011" not in p:
            print(f"  {name:>9}{st:>8}   🔴 " + p.get("error", "")[:44])
            continue
        t = p["te011"]
        print(f"  {name:>9}{st:>8}{t['f_ghz']:>12.6f}{t['Q']:>11,.0f}"
              f"{str(t['m_az']):>4}{t['A2_A0']:>9.4f}"
              f"{('yes' if t['in_band'] else 'NO'):>9}")
    print()
    # F1 — the filter's job
    for p in out["points"]:
        if "modes" not in p or p["loaded"]:
            continue
        ib = [m for m in p["modes"] if m["in_band"]]
        name = "%gx%g" % (p["ld"], p["lw"])
        print(f"  F1 {name} cold: {len(ib)} mode(s) in {out['band']} — "
              + ("✅ exactly one; the filter is doing its job"
                 if len(ib) == 1 else
                 f"🔴 FIRES — {len(ib)} modes: "
                 + ", ".join(f"{m['f_ghz']:.4f}(m={m['m_az']})" for m in ib)
                 + ". The filter is NOT clearing the band in this "
                   "configuration. REPORT IT; do not build selection "
                   "machinery around it (§7i)."))
    # V3 — closed form
    c0 = P.get((11.0, 8.0, False))
    if c0:
        d = (c0["te011"]["f_ghz"] - out["exact_te011"]) * 1e3
        print(f"\n  V3 11x8 cold: {c0['te011']['f_ghz']:.6f} vs closed form "
              f"{out['exact_te011']:.6f} -> {d:+.2f} MHz "
              + ("✅ (a cap loop shifts 0.37-0.44 MHz; the groove costs ~0)"
                 if abs(d) <= 2.0 else "🔴 FIRES"))
        q = c0["te011"]["Q"]
        print(f"  F2 Q_bare(11x8, grooved+looped) = {q:,.0f} "
              + ("✅ in 20,000-45,000" if 20000 <= q <= 45000 else "🔴 FIRES")
              + f"   [context: empty no-loop no-groove = "
                f"{out['q_empty_no_loop_context']:,.0f}]")
    # F3 — does loop size move the MODE?
    c1 = P.get((28.0, 20.0, False))
    if c0 and c1:
        d = (c1["te011"]["f_ghz"] - c0["te011"]["f_ghz"]) * 1e3
        print(f"  F3 cold 28x20 vs 11x8: {d:+.2f} MHz "
              + ("✅ loop size is not moving the mode"
                 if abs(d) <= 2.0 else
                 "🔴 FIRES — loop size perturbs the MODE, not just the "
                 "coupling. This would explain h3_groove's -12.80 MHz with no "
                 "groove effect at all."))
    # 🔑 PRIORS FOR THE SURROGATE (OPTIMIZER §3c/§3d), not just verdicts.
    # A number without its slice coordinates cannot be placed in the joint space.
    print("\n  📊 PRIORS — per case, with the coordinates held fixed:")
    print(f"    {'loop':>9}{'state':>7}{'tets':>8}{'outcome':>11}{'in band':>9}"
          f"{'A2/A0':>8}  fixed at")
    for p in out["points"]:
        nm = "%gx%g" % (p["ld"], p["lw"])
        st = "LOADED" if p["loaded"] else "COLD"
        fixed = (f"groove 5x10, ne={out['ne_hot']:.0e}" if p["loaded"]
                 else "groove 5x10, no plasma")
        if "modes" not in p:
            oc = "TIMEOUT" if "TIMED OUT" in p.get("error", "") else "error"
            print(f"    {nm:>9}{st:>7}{p.get('tets',0):>8,}{oc:>11}"
                  f"{'—':>9}{'—':>8}  {fixed}")
            continue
        ib = [m for m in p["modes"] if m["in_band"]]
        a2 = p.get("te011", {}).get("A2_A0")
        print(f"    {nm:>9}{st:>7}{p['tets']:>8,}{'converged':>11}"
              f"{len(ib):>9}" + (f"{a2:>8.4f}" if a2 is not None else f"{'—':>8}")
              + f"  {fixed}")
    n_ok = sum(1 for p in out["points"] if "modes" in p)
    print(f"    -> {n_ok}/{len(out['points'])} converged; the rest are MISSING "
          f"DATA, not bad scores (OPTIMIZER §3)")

    print("\n  🔑 eta REFERENCES (use these; 44,384 and 29,854 are BOTH wrong):")
    for (ld, lw, loaded), p in sorted(P.items()):
        if not loaded and "q_bare_this_loop" in p:
            print(f"     {('%gx%g' % (ld, lw)):>9}: Q_bare = "
                  f"{p['q_bare_this_loop']:,.0f}")
    print(f"\n  wrote {TAG}.result.json")


if __name__ == "__main__":
    main()
