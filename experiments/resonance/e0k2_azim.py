"""E0k2-azim — does the azimuthal-order discriminator work on REAL solves?

🔴 THE PROBLEM. Driven-only mode identification currently rests on matching an
energy fingerprint to a reference library. Measured margin over the best
alternative: 58.8x, 33.5x, 26.0x, and **4.5x at the weakest coupling** — and weak
coupling is the regime we want. The threshold was calibrated on the easy case
(mode absent) and silently accepted a false match at 0.00397 while set to 0.010.
Unattended, that is how an optimiser scores the wrong mode and never notices.

🔑 THE FIX IS A SYMMETRY TEST, NOT A BETTER THRESHOLD. TE011 is m=0; TM111 is
m=1. Energy goes as cos^2(m*phi), so per-sector energies are FLAT for m=0 and a
pure cos(2phi) for m=1. No reference library, no threshold from four points, and
computable from a DRIVEN solve alone.

⚠️ `geometry.py --sectors` already does this — its own help says "5 resolves
m=1..4" — and GEO sets `--sectors 1`, so NO solve in the record has azimuthal
bins. This rig turns it on.

TWO CASES, because a discriminator must be tested where the answer is known
BEFORE it is trusted where it is not:

  bare   no loop. TE011 (Q 44,384) and the TM111 pair (Q ~20,256) are already
         identified by Q, unambiguously. The discriminator must AGREE.
  loop   the 176 mm^2 cap loop, driven AND eigen. The eigen solve gives truth;
         the DRIVEN solve is where the discriminator has to stand alone.

VERIFICATION
  V1  bare: TE011 reads m=0, both TM111 polarisations read m=1.
  V2  loop/eigen: same, with the loop present.
  V3  loop/DRIVEN: the discriminator, applied to the driven field at the dip,
      returns the same m as the eigen mode it matches by signature.

FALSIFICATION
  🔴 F1  if TE011 does not read m=0 on the BARE cavity, the discriminator is
         broken and nothing downstream of it is worth running.
  🔴 F2  if A2/A0 for m=0 and m=1 are not separated by at least 10x, the
         symmetry test is no better than the fingerprint it replaces.
  🔴 F3  if the driven answer disagrees with the eigen answer, driven-only
         identification does NOT work and eigen stays mandatory per evaluation.
"""
import json
import csv
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import eigmodes
import solveconf
import azimuthal
from e0_solver_vs_math import GEO, eigen_cfg, run
from e0k2_anchor import (design_point, wall_sigma, CAP_R_FRAC, LOOP_PHI,
                         LOOP_RW, LOOP_GAP, N_MODES, FREQ_STEP,
                         BAND_HALFWIDTH_MHZ)

TAG = "e0k2_azim"
SECTORS = 5
LOOP_LD, LOOP_LW = 11.0, 8.0      # the 176 mm^2 case: reads TE011, beta 0.560


def sector_bins(meta):
    """Energy Index -> attribute, for the AIR sectors only, in azimuthal order.

    🔑 The air sectors ARE the azimuthal bins. eigen_cfg numbers volumes 10+i
    over sorted(vols), so the sector attributes must be located in that order.
    """
    attrs = meta["attributes"]
    air = sorted(attrs.get("air") or [])
    vols = sorted({v for k, v in attrs.items()
                   if isinstance(v, int) and k not in ("wall", "port")}
                  | set(air))
    return [(10 + vols.index(a), a) for a in air]


def read_sector_energy(tag, bins, row_key=None):
    """Per-sector p_elec for each mode (eigen) or the nearest f (driven)."""
    p = pathlib.Path("postpro") / tag / "domain-E.csv"
    rows = list(csv.reader(p.read_text().splitlines()))
    head = [h.strip() for h in rows[0]]
    cols = []
    for idx, _a in bins:
        try:
            cols.append(head.index(f"p_elec[{idx}]"))
        except ValueError:
            raise RuntimeError(f"{tag}: no p_elec[{idx}] column — the mesh has "
                               f"no azimuthal sectors. Built with --sectors 1?")
    out = {}
    for r in rows[1:]:
        try:
            key = float(r[0])
        except (ValueError, IndexError):
            continue
        out[key] = [float(r[c]) for c in cols]
    if row_key is None:
        return out
    k = min(out, key=lambda x: abs(x - row_key))
    return out[k]


def build(tag, a, L, loop):
    geo = list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                       "--sectors", str(SECTORS)]
    r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                        "--size-factor", "1.5"] + geo + loop,
                       capture_output=True, text=True)
    if r.returncode or not pathlib.Path(f"{tag}.msh").exists():
        raise RuntimeError(f"{tag}: mesh failed — {(r.stdout + r.stderr)[-300:]}")
    return solveconf.load_meta(f"{tag}.msh")


def solve_eigen(tag, m, sigma, fmin, energy):
    c = eigen_cfg(tag, m, mesh=f"{tag}.msh", sigma=sigma, n=N_MODES, target=fmin)
    c["Solver"]["Order"] = 2
    c["Domains"]["Postprocessing"]["Energy"] = energy
    if m["attributes"].get("port") is not None:
        c["Boundaries"]["PEC"] = {"Attributes": [m["attributes"]["port"]]}
    for mat in c["Domains"]["Materials"]:
        for k, want in (("Permittivity", 1.0), ("LossTan", 0.0),
                        ("Conductivity", 0.0)):
            if k in mat and mat[k] != want:
                mat[k] = want
    run(tag, c)


def energy_list(meta, bins):
    attrs = meta["attributes"]
    vols = sorted({v for k, v in attrs.items()
                   if isinstance(v, int) and k not in ("wall", "port")}
                  | set(attrs.get("air") or []))
    return ([{"Index": 1, "Attributes": [attrs["bore"]]}]
            + [{"Index": 10 + i, "Attributes": [v]} for i, v in enumerate(vols)])


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma = wall_sigma()
    cap_r = CAP_R_FRAC * a
    EX = ph.spectrum(a, L, fmax=3.2)
    exact = EX["TE011"]
    fmin = exact - 0.20
    out = {"sectors": SECTORS, "cases": {}}

    # ---------------- CASE 1: bare, where the answer is known ----------------
    print(f"\n{'='*78}\n  CASE 1 — BARE cavity, {SECTORS} sectors. "
          f"TE011 and TM111 already identified by Q.\n", flush=True)
    tb = f"{TAG}_bare"
    mb = build(tb, a, L, [])
    bins = sector_bins(mb)
    print(f"    {mb['tets']:,} tets, air sectors {[b[1] for b in bins]} "
          f"-> energy indices {[b[0] for b in bins]}", flush=True)
    if len(bins) < 3:
        raise RuntimeError(f"only {len(bins)} air sector(s) — --sectors did not "
                           f"take effect, and the discriminator needs >= 3.")
    solve_eigen(tb, mb, sigma, fmin, energy_list(mb, bins))
    modes = eigmodes.read(tb)
    qs = {}
    for line in (pathlib.Path("postpro") / tb /
                 "eig.csv").read_text().splitlines()[1:]:
        p_ = line.split(",")
        if len(p_) > 3:
            qs[round(float(p_[0]))] = float(p_[3])
    sec = read_sector_energy(tb, bins)
    rows = []
    print(f"\n    {'f (GHz)':>10}{'Q':>10}{'A2/A0':>9}{'m':>4}{'conf':>8}  sectors")
    for md in modes:
        u = sec.get(float(md["m"])) or sec[min(sec, key=lambda x: abs(x - md["m"]))]
        m_, conf, h = azimuthal.order(u)
        rows.append({"f": md["f"], "Q": qs.get(md["m"]), "A2_A0": h.get(2),
                     "m": m_, "conf": conf, "sectors": u})
        print(f"    {md['f']:>10.6f}{qs.get(md['m'],0):>10,.0f}"
              f"{h.get(2,0):>9.4f}{str(m_):>4}{conf:>8.1f}  "
              f"{[round(x,4) for x in u]}", flush=True)
    out["cases"]["bare"] = rows

    te = max(rows, key=lambda r: r["Q"] or 0)
    tms = [r for r in rows if r is not te and 2.4 < r["f"] < 2.5]
    print(f"\n    V1  TE011 (Q={te['Q']:,.0f}) reads m={te['m']} "
          + ("✅" if te["m"] == 0 else "🔴 F1 FIRES — discriminator broken"))
    for r in tms:
        print(f"        TM111 (Q={r['Q']:,.0f}) reads m={r['m']} "
              + ("✅" if r["m"] == 1 else "🔴"))
    if tms and te["A2_A0"] is not None:
        sep = min(r["A2_A0"] for r in tms) / max(te["A2_A0"], 1e-9)
        print(f"    V2  separation A2/A0: {sep:.0f}x "
              + ("✅" if sep >= 10 else "🔴 F2 FIRES — no better than fingerprints"))
        out["separation"] = sep

    # ---------------- CASE 2: with the loop, driven AND eigen ----------------
    print(f"\n{'='*78}\n  CASE 2 — {LOOP_LD}x{LOOP_LW} mm cap loop, "
          f"{SECTORS} sectors. Eigen = truth, DRIVEN = the real test.\n",
          flush=True)
    tl = f"{TAG}_loop"
    loop = ["--loop", f"{LOOP_LD},{LOOP_LW},{LOOP_RW},{LOOP_GAP}",
            "--loop-cap", f"{cap_r:.4f}", "--loop-phi", LOOP_PHI]
    ml = build(tl, a, L, loop)
    binsl = sector_bins(ml)
    en = energy_list(ml, binsl)
    print(f"    {ml['tets']:,} tets, {len(binsl)} air sectors", flush=True)
    solve_eigen(tl, ml, sigma, fmin, en)
    modes_l = eigmodes.read(tl)
    qsl = {}
    for line in (pathlib.Path("postpro") / tl /
                 "eig.csv").read_text().splitlines()[1:]:
        p_ = line.split(",")
        if len(p_) > 3:
            qsl[round(float(p_[0]))] = float(p_[3])
    secl = read_sector_energy(tl, binsl)
    erows = []
    print(f"\n    EIGEN {'f (GHz)':>10}{'Q':>10}{'A2/A0':>9}{'m':>4}{'conf':>8}")
    for md in modes_l:
        u = secl.get(float(md["m"])) or secl[min(secl, key=lambda x: abs(x - md["m"]))]
        m_, conf, h = azimuthal.order(u)
        erows.append({"f": md["f"], "Q": qsl.get(md["m"]), "A2_A0": h.get(2),
                      "m": m_, "conf": conf})
        print(f"    {'':>5}{md['f']:>10.6f}{qsl.get(md['m'],0):>10,.0f}"
              f"{h.get(2,0):>9.4f}{str(m_):>4}{conf:>8.1f}", flush=True)
    out["cases"]["loop_eigen"] = erows

    band = (exact - BAND_HALFWIDTH_MHZ / 1e3, exact + BAND_HALFWIDTH_MHZ / 1e3)
    td = f"{tl}_drv"
    cd, _meta, dropped = solveconf.driven(f"{tl}.msh", td, band,
                                          step=FREQ_STEP, order=2)
    cd["Domains"]["Postprocessing"]["Energy"] = en
    for mat in cd["Domains"]["Materials"]:
        for k, want in (("Permittivity", 1.0), ("LossTan", 0.0),
                        ("Conductivity", 0.0)):
            if k in mat and mat[k] != want:
                mat[k] = want
    pathlib.Path(f"{td}.json").write_text(json.dumps(cd, indent=2))
    print(f"\n    driven {band[0]:.4f}-{band[1]:.4f} GHz", flush=True)
    run(td, cd)

    import qfit
    r = qfit.analyse(td)
    if "error" in r:
        print(f"    🔴 {r['error']}")
        json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
        return
    ud = read_sector_energy(td, binsl, row_key=r["f0"])
    md_, confd, hd = azimuthal.order(ud)
    near = min(erows, key=lambda e: abs(e["f"] - r["f0"]))
    out["driven"] = {"f0": r["f0"], "beta": r["beta"], "Q_L": r["Q_L"],
                     "A2_A0": hd.get(2), "m": md_, "conf": confd,
                     "nearest_eigen_f": near["f"], "eigen_m": near["m"]}
    print(f"\n    DRIVEN f0={r['f0']:.6f}  beta={r['beta']:.4f}  "
          f"A2/A0={hd.get(2,0):.4f}  m={md_}  conf={confd:.1f}")
    print(f"    nearest eigen mode {near['f']:.6f} (Q={near['Q']:,.0f}) "
          f"reads m={near['m']}")
    v3 = md_ is not None and md_ == near["m"]
    print(f"\n    V3  driven m == eigen m: {md_} vs {near['m']} "
          + ("✅ DRIVEN-ONLY IDENTIFICATION WORKS" if v3 else
             "🔴 F3 FIRES — eigen stays mandatory per evaluation"))
    out["v3_pass"] = bool(v3)
    json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
    print(f"\n  wrote {TAG}.result.json", flush=True)


if __name__ == "__main__":
    main()
