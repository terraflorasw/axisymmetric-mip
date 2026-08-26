"""H3's HOT leg — the cavity at operating wall temperature, NO plasma.

🔴 WHY THIS EXISTS. H3 asks for sustainment across **COLD / HOT / LOADED**. Cold
and loaded are measured; **HOT never has been.** Nothing in the tree scales
dimensions for temperature, and the only "hot" string in a result file is a
mislabelled plasma density — the exact confusion GLOSSARY was written to stop.

🔑 GLOSSARY: **HOT is THERMAL, not a plasma density.** Cavity already operating —
hot walls, hot gas, **NO PLASMA**. It is the RE-IGNITION state.
⚠️ **Do NOT restate GLOSSARY's "the regime that decides whether the instrument
restarts itself".** That is emphasis, not a finding — a hot cavity can be allowed
to cool, or cooled harder. **The real consequence is that the control loop needs
a temperature input**, which turns thermal detuning into a computed offset.

## What changes with wall temperature, and it splits cleanly

  FREQUENCY — every state. Pure geometry: aluminium expands, f ~ 1/length, so
              df/f = -alpha*dT exactly. This rig TESTS that the mesher and
              solver reproduce it; it is not new physics.
  MATCH     — UNLOADED ONLY. Wall sigma falls with T, so Q0 and beta fall.
              ⚠️ LOADED, the plasma is 275x the wall loss: Q0 158.0 -> 157.8 at
              +100 K. Loaded beta belongs to the plasma. **That is why this rig
              has NO plasma** — the hot effect on the match lives entirely here.

🔴 A DISCREPANCY THIS RIG CANNOT SETTLE, SO IT REPORTS BOTH.
GLOSSARY states **Q x 0.78 at +100 K**. E0 validated **Q ~ sqrt(sigma)** to four
decimals, and standard aluminium (alpha_R = 4.29e-3 /K) gives sigma x0.700 ->
**Q x0.837**. The record's 0.78 requires alpha_R = 6.44e-3 /K, **~1.5x
aluminium**. **sigma is an INPUT here, so the solve cannot arbitrate** — it can
only confirm Q follows sqrt(sigma) from whatever sigma it is given.
✅ This rig uses the defensible **4.29e-3** and prints both predictions.
**Someone must decide where 0.78 came from.**

🔴 EIGEN ONLY (§7c). Eigen PAIRS per temperature — port_bc "pec" for Q0 (no port
loss) and "lumped" for Q_L — so beta comes from
1/Q_ext = 1/Q_L - 1/Q0 with **no |S11|, no fit, no branch decision** (§7x).

VERIFICATION
  V1  🔑 dT = 0 MUST reproduce `h3_loopq`'s 11x8 cell: Q0 43,422, Q_ext 9,231,
      beta 4.704, f0 2.451633. Same mesh style, same settings. **If dT=0 does
      not reproduce, nothing else in the sweep means anything.**
  V2  df/f must equal **-alpha*dT** (alpha = 23.1e-6/K) to within mesh jitter.
      This is a GEOMETRY identity — it tests that scaling reached the mesh, not
      the physics. -5.65 MHz at +100 K, -11.27 at +200 K.
  V3  Q0 ratio must equal **sqrt(sigma ratio)** — E0's validated law. x0.837 at
      +100 K, x0.734 at +200 K.
  V4  purity must stay high. Thermal scaling is uniform, so the mode shape
      should be untouched; a purity change would mean the scaling broke
      something.
FALSIFICATION
  🔴 F1  if df/f != -alpha*dT, the dimensions did not scale as intended and
         every row is suspect. **Check the mesh sidecar before believing any Q.**
  🔴 F2  if Q0 does not follow sqrt(sigma), either E0's law fails here or sigma
         did not reach the solver. Both are instrument faults, not findings.
  🔴 F3  if beta moves less than Q0 does, Q_ext is scaling too — the loop
         expands with the cavity. Report Q_ext(dT); do not assume it is fixed.
         ⚠️ ASSUMPTION: that Q_ext is dominated by geometry that scales
         uniformly. The loop, the gap and the cavity all expand together, so
         first order this should nearly cancel in beta. **Measured, not assumed.**
"""
import json
import values
import math
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import solveconf
import eigmodes
from e0_solver_vs_math import GEO, eigen_cfg, run
from e0k2_anchor import design_point, wall_sigma, LOOP_PHI, LOOP_RW, LOOP_GAP
from h3_loaded import SECTORS, CAP_R_FRAC
from azimuthal import order as az_order
from e0k2_azim import sector_bins, read_sector_energy
from h3_ladder import purity, PROBE_PHI_DEG, PROBE_R_FRAC

TAG = "h3_hot"

# 🔑 aluminium. alpha is the record's; alpha_R is the standard value, NOT the
# one GLOSSARY's "Q x 0.78" implies — see the docstring.
ALPHA = 23.1e-6                 # linear expansion, /K
ALPHA_R = 4.29e-3               # resistivity temperature coefficient, /K
ALPHA_R_IMPLIED = 6.44e-3       # what GLOSSARY's 0.78 would require

# 🔴 THE COLD BASELINE IS AN ASSUMPTION AND IT WAS NEVER WRITTEN DOWN.
# `baselines.json` gives wall sigma = 3.5e7 S/m for "bare electropolished
# aluminium 6061" with **no reference temperature**, and GLOSSARY defines COLD
# only as "cavity at ambient". alpha_R is itself quoted at 20 C, so the
# linearisation needs an origin. **Stated here so it can be argued with.**
T_COLD_K = 293.15               # 20 C — ASSUMED, not sourced
T_WALL_K = [293.15, 393.15, 493.15]   # absolute wall temperature
DELTA_T = [t - T_COLD_K for t in T_WALL_K]
GROOVE_W, GROOVE_D = values.get("cavity.groove.mm")  # at dT=0; scaled w/ cavity
LOOP_LD, LOOP_LW = values.get("loop.size.mm")

N_MODES = 8
EIGEN_TARGET = 2.38
CASE_TIMEOUT_S = 2700.0
WINDOW = (2.30, 2.65)           # widened: f0 falls with temperature

V1 = {"f0": 2.451633, "Q0": 43422.0, "Q_ext": 9231.0, "beta": 4.704}
V1_TOL = 0.05
V2_TOL_MHZ = 0.20               # mesh jitter is ~8 kHz; 200 kHz is generous
V3_TOL = 0.03
CONT_MAX_MHZ = 30.0             # f0 moves -11 MHz by +200 K


def save(out):
    p = pathlib.Path(f"{TAG}.result.json")
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def geo_scaled(gw, gd):
    g = list(GEO)
    g[g.index("--groove") + 1] = f"{gw:.6f},{gd:.6f}"
    return g


def build(tag, dT, a0, L0, rec):
    """🔑 EVERYTHING scales — cavity, groove, loop, wire, gap.

    A partial scaling would be worse than none: it would produce a cavity that
    is neither cold nor hot, and V2 would still pass because it only checks the
    frequency, which the barrel and length dominate.
    """
    s = 1.0 + ALPHA * dT
    a, L = a0 * s, L0 * s
    gw, gd = GROOVE_W * s, GROOVE_D * s
    ld, lw = LOOP_LD * s, LOOP_LW * s
    rw, gp = LOOP_RW * s, LOOP_GAP * s
    rec.update(scale=s, a_mm=a, L_mm=L, groove_req=[gw, gd],
               loop_req=[ld, lw], sigma=wall_sigma() / (1.0 + ALPHA_R * dT))
    args = (geo_scaled(gw, gd)
            + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
               "--sectors", str(SECTORS),
               "--loop", f"{ld:.6f},{lw:.6f},{rw:.6f},{gp:.6f}",
               "--loop-cap", f"{CAP_R_FRAC * a:.4f}",
               "--loop-phi", LOOP_PHI])
    for sf in ("1.5", "1.42", "1.58"):
        r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                            "--size-factor", sf] + args,
                           capture_output=True, text=True)
        if not r.returncode and pathlib.Path(f"{tag}.msh").exists():
            rec["size_factor"] = sf
            if sf != "1.5":
                print(f"      ⚠️ mesh needed size-factor {sf}; REPORTED",
                      flush=True)
            return solveconf.load_meta(f"{tag}.msh")
        rec["_err"] = (r.stdout + r.stderr)[-200:]
    return None


def solve(mesh_tag, out_tag, meta, sigma, port_bc, a, seed, rec):
    attrs = meta["attributes"]
    bins = sector_bins(meta)
    vols = sorted({v for k, v in attrs.items()
                   if isinstance(v, int) and k not in ("wall", "port")}
                  | set(attrs.get("air") or []))
    # 🔴 MESH tag and OUTPUT tag are SEPARATE. One mesh per temperature is
    # solved TWICE (pec, lumped), so the output tag must differ while the mesh
    # tag must not. Conflating them cost a launch: build wrote h3_hot_0.msh,
    # solve asked for h3_hot_0_pec.msh, Palace returned rc=1 in 2 s.
    c = eigen_cfg(out_tag, meta, mesh=f"{mesh_tag}.msh", sigma=sigma,
                  n=N_MODES, target=EIGEN_TARGET, port_bc=port_bc)
    c["Solver"]["Order"] = 2
    c["Domains"]["Postprocessing"]["Energy"] = (
        [{"Index": 1, "Attributes": [attrs["bore"]]}]
        + [{"Index": 10 + i, "Attributes": [v]} for i, v in enumerate(vols)])
    pts = [(rf * a, math.radians(pd))
           for rf in PROBE_R_FRAC for pd in PROBE_PHI_DEG]
    probe_pts = [{"r_mm": r, "phi_deg": math.degrees(p_)} for r, p_ in pts]
    c["Domains"]["Postprocessing"]["Probe"] = [
        {"Index": i + 1,
         "Center": [r * 1e-3 * math.cos(p_), r * 1e-3 * math.sin(p_), 0.0]}
        for i, (r, p_) in enumerate(pts)]
    try:
        run(out_tag, c, allow_lossy_eigen=True, timeout=CASE_TIMEOUT_S)
    except RuntimeError as e:
        print(f"      🔴 {str(e)[:150]}", flush=True)
        return None
    modes = eigmodes.read(out_tag)
    qs = {}
    for line in (pathlib.Path("postpro") / out_tag /
                 "eig.csv").read_text().splitlines()[1:]:
        pp = line.split(",")
        if len(pp) > 3:
            qs[round(float(pp[0]))] = float(pp[3])
    sec = read_sector_energy(out_tag, bins)
    found = []
    for md in modes:
        if not (WINDOW[0] < md["f"] < WINDOW[1]):
            continue
        u = sec.get(float(md["m"]))
        if u is None and sec:
            u = sec[min(sec, key=lambda x: abs(x - md["m"]))]
        m_az, conf, harm = az_order(u) if u else (None, 0, {})
        idx = round(float(md["m"]))
        pu = purity(out_tag, idx, probe_pts)
        found.append({"f_ghz": md["f"], "Q": qs.get(idx), "mode_index": idx,
                      "m_az": m_az, "A2_A0": harm.get(2, 0.0),
                      "P_min": (pu or {}).get("P_min"),
                      "spread": (pu or {}).get("spread")})
    # 🔴 SAVE BEFORE LABELLING (§7q)
    rec[f"modes_{port_bc}"] = found
    if not found:
        return None
    te = min(found, key=lambda f: abs(f["f_ghz"] - seed))
    d = (te["f_ghz"] - seed) * 1e3
    if abs(d) > CONT_MAX_MHZ:
        rec[f"identification_failed_{port_bc}"] = (
            f"continuation BROKE: nearest is {d:+.2f} MHz from {seed:.6f}")
        return None
    te = dict(te, selected_by=f"continuation {d:+.3f} MHz")
    return te


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a0, L0 = design_point()
    sig0 = wall_sigma()
    print(f"  cold baseline: a={a0:.4f} L={L0:.4f}  sigma={sig0:.3g} S/m")
    print(f"  alpha={ALPHA:.3g}/K (expansion)   alpha_R={ALPHA_R:.3g}/K "
          f"(resistivity)")
    print(f"  ⚠️ GLOSSARY's 'Q x0.78 at +100 K' needs alpha_R={ALPHA_R_IMPLIED:.3g}"
          f"/K — ~1.5x aluminium. Using the standard value and reporting both.\n",
          flush=True)

    out = {"alpha": ALPHA, "alpha_R": ALPHA_R,
           "T_cold_K": T_COLD_K, "T_cold_source": "ASSUMED 20 C — baselines.json states no reference temperature for wall sigma",
           "T_wall_K": T_WALL_K,
           "alpha_R_implied_by_record": ALPHA_R_IMPLIED,
           "v1_anchor": V1, "cold": {"a_mm": a0, "L_mm": L0, "sigma": sig0},
           "points": []}

    for dT in DELTA_T:
        rec = {"dT": dT, "T_wall_K": T_COLD_K + dT}
        out["points"].append(rec)
        print(f"  --- wall T = {T_COLD_K + dT:.1f} K "
              f"({T_COLD_K + dT - 273.15:.0f} C), i.e. dT = {dT:+.0f} K"
              + ("   🔑 V1 ANCHOR (must reproduce h3_loopq)" if dT == 0 else ""),
              flush=True)
        meta = build(f"{TAG}_{int(dT)}", dT, a0, L0, rec)
        if meta is None:
            rec["error"] = f"mesh failed: {rec.pop('_err','')[:140]}"
            print(f"    🔴 {rec['error']}", flush=True)
            save(out); continue
        rec.pop("_err", None)
        g = (meta.get("geometry_mm") or {}).get("groove") or [0, 0]
        rec["groove_meshed"] = list(map(float, g))
        rec["tets"] = meta["tets"]
        # 🔴 F1's first line of defence: did the SCALING reach the mesh?
        want = rec["groove_req"]
        if max(abs(x - y) for x, y in zip(map(float, g), want)) > 0.01:
            rec["error"] = (f"scaling did NOT reach the mesh: groove {g} vs "
                            f"requested {[round(x,4) for x in want]}")
            print(f"    🔴 {rec['error']}", flush=True)
            save(out); continue
        print(f"    a={rec['a_mm']:.4f} L={rec['L_mm']:.4f}  groove {g}  "
              f"sigma={rec['sigma']:.4g}  tets={meta['tets']:,}", flush=True)

        seed = V1["f0"] / (1.0 + ALPHA * dT)
        per = {}
        for bc in ("pec", "lumped"):
            te = solve(f"{TAG}_{int(dT)}", f"{TAG}_{int(dT)}_{bc}",
                       meta, rec["sigma"], bc, rec["a_mm"], seed, rec)
            save(out)
            if te is None:
                rec["error"] = rec.get(f"identification_failed_{bc}",
                                       f"{bc}: no modes in {WINDOW}")
                print(f"    🔴 {rec['error']}", flush=True)
                break
            per[bc] = te
            rec[f"te011_{bc}"] = te
            print(f"    {bc:>6}: {te['f_ghz']:.6f}  Q={te['Q']:>9,.0f}  "
                  f"P>={te['P_min']:.4f} spread={te['spread']:.4f}  "
                  f"({te['selected_by']})", flush=True)
        if len(per) == 2:
            q0, ql = per["pec"]["Q"], per["lumped"]["Q"]
            if ql < q0:
                qext = 1.0 / (1.0 / ql - 1.0 / q0)
                rec.update(f0=per["pec"]["f_ghz"], Q0=q0, Q_L=ql, Q_ext=qext,
                           beta=q0 / qext)
                print(f"    -> f0={rec['f0']:.6f}  Q0={q0:>9,.0f}  "
                      f"Q_ext={qext:>9,.0f}  beta={rec['beta']:.3f}", flush=True)
            else:
                rec["error"] = f"Q_L={ql:,.0f} >= Q0={q0:,.0f} — impossible"
                print(f"    🔴 {rec['error']}", flush=True)
        save(out)

    # ---------------- V1 gates everything
    print("\n" + "=" * 78)
    base = next((p for p in out["points"] if p["dT"] == 0 and p.get("Q0")), None)
    if base is None:
        print("  🔴 V1 CANNOT BE CHECKED — the dT=0 anchor did not complete.\n"
              "     NOTHING IN THIS SWEEP IS QUOTABLE.")
        out["v1"] = "not checked"
    else:
        bad = []
        for k in ("f0", "Q0", "Q_ext", "beta"):
            off = abs(base[k] - V1[k]) / V1[k]
            print(f"  V1 {k:<6} {base[k]:>12,.4f} vs h3_loopq {V1[k]:>12,.4f}"
                  f"  -> {off*100:>5.2f}% " + ("✅" if off <= V1_TOL else "🔴"))
            if off > V1_TOL:
                bad.append(k)
        out["v1"] = "pass" if not bad else f"FIRES on {bad}"
        if bad:
            print("  🔴 THE ANCHOR DOES NOT REPRODUCE — treat every row as "
                  "SUSPECT.")

    ok = [p for p in out["points"] if p.get("Q0")]
    if len(ok) >= 2:
        print(f"\n  {'dT':>6}{'f0 GHz':>11}{'df MHz':>9}{'Q0':>10}{'Q_ext':>9}"
              f"{'beta':>8}{'VSWR':>8}{'P_min':>9}")
        for p in ok:
            df = (p["f0"] - base["f0"]) * 1e3 if base else float("nan")
            b = p["beta"]
            print(f"  {p['dT']:>+6.0f}{p['f0']:>11.6f}{df:>9.2f}{p['Q0']:>10,.0f}"
                  f"{p['Q_ext']:>9,.0f}{b:>8.3f}{(1/b if b<1 else b):>8.1f}"
                  f"{p['te011_pec']['P_min']:>9.4f}")

        print()
        for p in ok:
            if p["dT"] == 0:
                continue
            # V2 — geometry identity
            pred_df = -V1["f0"] * ALPHA * p["dT"] * 1e3
            got_df = (p["f0"] - base["f0"]) * 1e3
            e2 = abs(got_df - pred_df)
            print(f"  V2 dT{p['dT']:+.0f}: df {got_df:+.2f} vs -alpha*dT "
                  f"{pred_df:+.2f} MHz -> {e2:.3f} "
                  + ("✅" if e2 <= V2_TOL_MHZ else "🔴 F1 FIRES — the scaling "
                     "did not reach the solve"))
            # V3 — E0's sqrt(sigma) law
            pred_q = math.sqrt(1.0 / (1.0 + ALPHA_R * p["dT"]))
            got_q = p["Q0"] / base["Q0"]
            e3 = abs(got_q - pred_q) / pred_q
            alt = math.sqrt(1.0 / (1.0 + ALPHA_R_IMPLIED * p["dT"]))
            print(f"  V3 dT{p['dT']:+.0f}: Q0 x{got_q:.4f} vs sqrt(sigma) "
                  f"x{pred_q:.4f} -> {e3*100:.2f}% "
                  + ("✅" if e3 <= V3_TOL else "🔴 F2 FIRES"))
            print(f"     ⚠️ the record's 0.78-at-100K would predict x{alt:.4f} "
                  f"— UNRESOLVED, sigma is an input")
            # F3 — does Q_ext scale too?
            rq = p["Q_ext"] / base["Q_ext"]
            print(f"  F3 dT{p['dT']:+.0f}: Q_ext x{rq:.4f}, Q0 x{got_q:.4f} "
                  f"-> beta x{p['beta']/base['beta']:.4f}"
                  + ("   (Q_ext nearly fixed)" if abs(rq - 1) < 0.02
                     else "   🔑 Q_ext SCALES — the loop expands too"))
        # V4 — uniform scaling must not change the mode shape
        worst = max(ok, key=lambda p: p["te011_pec"]["spread"])
        w = worst["te011_pec"]["spread"]
        if w <= 0.02:
            print(f"\n  V4 worst purity spread {w:.4f} at dT"
                  f"{worst['dT']:+.0f} ✅ thermal scaling leaves the mode "
                  f"shape alone")
        else:
            print(f"\n  V4 🔴 purity degraded to {w:.4f} at dT"
                  f"{worst['dT']:+.0f} — UNIFORM scaling should not do that. "
                  f"Suspect the mesh, not the physics.")
    save(out)
    print(f"\n  result -> {TAG}.result.json", flush=True)


if __name__ == "__main__":
    main()
