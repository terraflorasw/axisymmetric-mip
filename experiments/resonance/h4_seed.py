"""H4 (seed) — can the field GRAB a thermal kernel, and does its PLACEMENT decide it?

🔑 H4 IS ALREADY OPEN. TM ignition was discarded 2026-08-22 on two measured legs
and AUXILIARY IGNITION was adopted; the mechanism died, the question did not.
This rig addresses H4 "Still to check" item 2 — does a conductor perturb TE011,
and where must it sit — and adds the part H4 did not have: a RADIUS-RESOLVED
answer.

⚠️ H4 ALREADY SETTLES ONE THING I GOT LOOSE. It records that seeding "does NOT
lower the field required for net ionisation, which is set by E/N" — seeds remove
the statistical delay only. So for N2 the mechanism is the THERMAL KERNEL (hot
channel -> N falls -> E/N rises), not seed electrons. Argon is different because
its THRESHOLD is lower, not because seeding helps.

🔴 AND IT PUTS ONE H4 SENTENCE UNDER TENSION. H4 argues an on-axis igniter is
"nearly invisible" to TE011 (0.079% of mode energy on axis) and calls this the
geometry inverting in our favour. True for the ELECTRODE. But the KERNEL inherits
the electrode's position, and a kernel in the field null is one the mode cannot
grab — measured coupling ratio wall:axis is predicted at 279x. H4's adopted
answer (external spark through the quartz, as ICP does) already puts the kernel
at large r, so the CONCLUSION stands; the REASON needs to be coupling, not just
electrode erosion. This rig measures that ratio.

N2 arc ignition matters because it removes an argon line from a field instrument.
Breakdown is NOT the obstacle: a 1 atm N2 spark reaches 10-20 kK, where E/N is
106-593 Td across r=3-8.5 mm against a ~100-150 Td threshold. The open question
is HANDOVER — when the arc stops, can the 2.45 GHz field deposit power fast
enough to hold the channel before it recombines?

## Why placement should dominate

Absorbed power goes as integral of sigma|E|^2, and TE011's E_phi VANISHES ON
AXIS. Relative to a seed at r=0.5 mm, the same seed absorbs:

    r=2 mm   16x        r=6 mm  142x
    r=4 mm   64x        r=7 mm  192x        r=8.5 mm  279x

If that holds, the igniter electrode must sit near the OUTER TUBE. An on-axis
seed sits in the field null and cannot be grabbed however hot the spark is.

⚠️ THOSE ARE RATIOS OF AN ANALYTIC MODE PROFILE, NOT MEASUREMENTS. Extrapolating
h3_eigen's eta=0.078 (0.5 mm on-axis column) across two decades of coupling is
exactly the arithmetic-instead-of-simulation shortcut that produced two
retractions today. This rig measures the ratio instead.

## What the instrument can and cannot say (CONVENTIONS §6c)

Palace's domain-E.csv reports per-domain ENERGY, not dissipated power, so eta
comes from the Q difference: eta = 1 - Q/Q_BARE. Measured Q reproducibility is
0.13-1.7%, so **eta below ~2% is not resolvable** and must be reported as "below
the floor", never as a value.

At the other end eta SATURATES at 1. A wall-adjacent seed at ne=1e20 is predicted
to saturate, which is itself the handover answer (it grabs essentially all the
power) but makes the RATIO unmeasurable there. So the weak-seed row at ne=1e18
exists to put both members of a matched pair inside the resolvable band.

VERIFICATION
  V1  every point identifies TE011 by AZIMUTHAL ORDER (m=0), never by max-Q.
  V2  Q_BARE is h3_eigen's 44,384, reproduced twice. Any point whose Q EXCEEDS
      Q_BARE is unphysical (negative absorption) and is reported as a failure,
      not clipped to zero.
FALSIFICATION
  🔴 F1  if a WALL seed does not couple far more than an AXIS seed of the same
         volume and density, the placement argument is wrong and the igniter
         electrode position does not matter. This is the whole point.
  🔴 F2  if BOTH members of a matched pair saturate (eta > 0.98) or BOTH sit
         below the 2% floor, that pair measures nothing — report it as
         uninformative rather than quoting a ratio built from two blurs.
  🔴 F3  if azimuthal order leaves m=0 the mode is not TE011; report the onset.
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
from e0_solver_vs_math import GEO, eigen_cfg, run
from e0k2_anchor import design_point, wall_sigma
from e0k2_azim import sector_bins, read_sector_energy
from h3_loaded import drude, Z_FRAC, EIGEN_TARGET, SECTORS

TAG = "h4_seed"
Q_BARE = 44384.0
P_REF = 1000.0
N_MODES = 4                 # DERIVED in h3_eigen: 4 converges where 6 stalls
TE011_WINDOW = (2.40, 2.50)
CASE_TIMEOUT_S = 900.0

# (r_i, r_o, z_half_mm, ne) — MATCHED PAIRS. Each wall shell is paired with an
# axis column of comparable volume at the same density, so F1 compares like with
# like. Volumes are matched to ~2x, not exactly: an axis column cannot be made
# thin enough to match a wall shell without falling below the mesh floor that
# killed a 0.25 mm annulus earlier today.
TETS_MAX = 150000           # between 36,967 (solved) and 252,068 (timed out)
ETA_FLOOR = 0.02            # Q reproducibility 0.13-1.7% -> below this is noise
ETA_SAT = 0.98              # above this the ratio is unmeasurable, not 1.0
CASES = [("axis-strong", 0.00, 1.00, 5.0, 1.0e20),
         ("wall-strong", 6.00, 8.50, 5.0, 1.0e20),
         ("axis-weak",   0.00, 2.00, 5.0, 1.0e20),
         ("wall-weak",   7.00, 8.50, 5.0, 1.0e18),
         ("wall-tiny",   6.00, 8.50, 2.0, 1.0e20),
         ("axis-tiny",   0.00, 1.00, 2.0, 1.0e20)]
PAIRS = [("axis-strong", "wall-strong"), ("axis-weak", "wall-weak"),
         ("axis-tiny", "wall-tiny")]
SIZE_FACTORS = ["1.5", "1.42", "1.58"]      # retry perturbs to dodge ScaledJac


def save(out):
    p = pathlib.Path(f"{TAG}.result.json")
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma_w = wall_sigma()
    w = 2.0 * math.pi * 2.45e9
    exact = ph.spectrum(a, L, fmax=3.2)["TE011"]
    print(f"  cavity a={a:.4f} L={L:.4f}  Q_bare={Q_BARE:,.0f}  P_ref={P_REF:.0f} W")
    print(f"  eta floor {ETA_FLOOR:.2f} (Q reproducibility), saturation "
          f"{ETA_SAT:.2f}\n", flush=True)
    out = {"q_bare": Q_BARE, "p_ref_w": P_REF, "eta_floor": ETA_FLOOR,
           "eta_sat": ETA_SAT, "points": []}

    for name, ri, ro, zh, ne in CASES:
        tag = f"{TAG}_{name}".replace("-", "_")
        thick = ro - ri
        zlo, zhi = -zh, zh
        Lp = 2.0 * zh * 1e-3
        eps, sig = drude(ne, w)
        # 🔴 FIRST ATTEMPT FAILED HERE. A 0.5 mm shell at r=8.25 mm has ~52 mm
        # of circumference; at plasma_h=0.30 that meshed to 252,068 tets vs
        # 36,967 for an axis column, and ALL THREE wall cases timed out at 0-2
        # NLEPS iterations. Mesh cost for a shell scales with its SURFACE, not
        # its volume — so thickness must set the element size, and thin shells
        # are simply not affordable here.
        ph_mesh = max(0.40, min(thick, 2.0 * zh) / 4.0)
        # 🔴 DO NOT PREDICT THE MESH BURDEN FROM THE SHELL'S VOLUME. I wrote such
        # an estimator and it said 4,050 elements for the case that actually
        # meshed to 252,068 — wrong by 50x, because gmsh's size field grows
        # gradually and the refinement bleeds into the surrounding cavity. The
        # shell added ~215k tets OUTSIDE itself. Use the MEASURED count from the
        # sidecar instead (guard below, after load_meta).
        rec = {"case": name, "ri_mm": ri, "ro_mm": ro, "thick_mm": thick,
               "z_half_mm": zh, "ne": ne, "eps": eps, "sigma": sig,
               "plasma_len_m": Lp, "plasma_h": ph_mesh, "tag": tag}
        print(f"  --- {name}: ri={ri} ro={ro} mm, z=+-{zh} mm, ne={ne:.0e} "
              f"(eps={eps:.3f} sigma={sig:.3g}, plasma_h={ph_mesh:.3f})",
              flush=True)
        args = (list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                             "--sectors", str(SECTORS),
                             "--plasma", f"{ri},{ro},{zlo:.4f},{zhi:.4f}",
                             "--plasma-h", f"{ph_mesh:.3f}"])
        # R=1.0 died on ScaledJac in h3_eigen with no retry. Perturbing the size
        # factor is geometry.py's own documented dodge for a curving failure.
        ok, last = False, ""
        for sf in SIZE_FACTORS:
            r = subprocess.run([sys.executable, "geometry.py", "--out",
                                f"{tag}.msh", "--size-factor", sf] + args,
                               capture_output=True, text=True)
            if not r.returncode and pathlib.Path(f"{tag}.msh").exists():
                ok = True
                rec["size_factor"] = sf
                if sf != SIZE_FACTORS[0]:
                    print(f"    ⚠️ mesh needed size-factor {sf}; REPORTED",
                          flush=True)
                break
            last = (r.stdout + r.stderr)[-200:]
        if not ok:
            rec["error"] = f"mesh failed at all size factors: {last}"
            print(f"    🔴 {rec['error'][:150]}\n    REPORTED.", flush=True)
            out["points"].append(rec); save(out); continue

        m = solveconf.load_meta(f"{tag}.msh")
        attrs = m["attributes"]
        # measured, not predicted: 36,967 tets solved in 135 s; 252,068 timed out
        # at 0-2 NLEPS iterations. Refuse rather than burn CASE_TIMEOUT_S.
        if m["tets"] > TETS_MAX:
            rec["tets"] = m["tets"]
            rec["error"] = (f"mesh {m['tets']:,} tets exceeds TETS_MAX "
                            f"{TETS_MAX:,} — 252,068 timed out; not attempted")
            print(f"    🔴 {rec['error']}\n    REPORTED.", flush=True)
            out["points"].append(rec); save(out); continue
        if attrs.get("plasma") is None:
            rec["error"] = "no plasma attribute"
            print(f"    🔴 {rec['error']}"); out["points"].append(rec)
            save(out); continue
        bins = sector_bins(m)
        vols = sorted({v for k, v in attrs.items()
                       if isinstance(v, int) and k not in ("wall", "port")}
                      | set(attrs.get("air") or []))
        energy = ([{"Index": 1, "Attributes": [attrs["bore"]]}]
                  + [{"Index": 10 + i, "Attributes": [v]}
                     for i, v in enumerate(vols)])
        c = eigen_cfg(tag, m, mesh=f"{tag}.msh", sigma=sigma_w,
                      n=N_MODES, target=EIGEN_TARGET)
        c["Solver"]["Order"] = 2
        c["Domains"]["Postprocessing"]["Energy"] = energy
        others = sorted(set(vols) - {attrs["plasma"]})
        c["Domains"]["Materials"] = [
            {"Attributes": others, "Permittivity": 1.0, "Permeability": 1.0},
            {"Attributes": [attrs["plasma"]], "Permittivity": eps,
             "Permeability": 1.0, "Conductivity": sig}]
        # probes ACROSS THE ANNULUS (ri..ro), plus the vacuum landmark
        pr = [ri + f * thick for f in (0.02, 0.25, 0.5, 0.75, 0.98)]
        pr += [1.5 * ro, 0.4805 * a]
        c["Domains"]["Postprocessing"]["Probe"] = [
            {"Index": i + 1, "Center": [x * 1e-3, 0.0, 0.0]}
            for i, x in enumerate(pr)]
        rec["probe_r_mm"] = pr
        rec["tets"] = m["tets"]
        try:
            run(tag, c, allow_lossy_eigen=True, timeout=CASE_TIMEOUT_S)
        except RuntimeError as e:
            rec["error"] = str(e)[:200]
            print(f"    🔴 {str(e)[:170]}\n    REPORTED.", flush=True)
            out["points"].append(rec); save(out); continue

        modes = eigmodes.read(tag)
        qs, emag = {}, {}
        for line in (pathlib.Path("postpro") / tag /
                     "eig.csv").read_text().splitlines()[1:]:
            pp = line.split(",")
            if len(pp) > 3:
                qs[round(float(pp[0]))] = float(pp[3])
        drows = list(csv.reader((pathlib.Path("postpro") / tag /
                                 "domain-E.csv").read_text().splitlines()))
        dh = [x.strip() for x in drows[0]]
        im_ = next((i for i, h in enumerate(dh) if h.startswith("E_mag (")), None)
        for rr in drows[1:]:
            try:
                emag[round(float(rr[0]))] = float(rr[im_])
            except (ValueError, IndexError, TypeError):
                pass
        sec = read_sector_energy(tag, bins)
        cands = []
        for md in modes:
            u = sec.get(float(md["m"]))
            if u is None and sec:
                u = sec[min(sec, key=lambda x: abs(x - md["m"]))]
            m_az, conf, harm = azimuthal.order(u) if u else (None, 0, {})
            if m_az == 0 and TE011_WINDOW[0] < md["f"] < TE011_WINDOW[1]:
                cands.append((md, harm))
        if not cands:
            rec["error"] = (f"F4: no m=0 mode in {TE011_WINDOW}; modes "
                            f"{[round(md['f'],5) for md in modes]}")
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        if len(cands) > 1:
            rec["ambiguous"] = [round(cc[0]["f"], 6) for cc in cands]
            print(f"    ⚠️ {len(cands)} m=0 candidates {rec['ambiguous']} — "
                  f"taking nearest 2.45 and saying so", flush=True)
        pick, harm = min(cands, key=lambda cc: abs(cc[0]["f"] - exact))
        Q = qs.get(pick["m"], 0.0)
        eta = 1.0 - Q / Q_BARE
        vol = math.pi * ((ro * 1e-3) ** 2 - (ri * 1e-3) ** 2) * Lp
        pdens = eta * P_REF / vol
        # V2: absorption cannot be negative. Q > Q_BARE means the solve is not
        # measuring what it claims — report, never clip.
        if eta < 0:
            rec["error"] = (f"V2: Q={Q:,.0f} EXCEEDS Q_bare={Q_BARE:,.0f} "
                            f"(eta={eta:+.4f}) — unphysical, not clipped")
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        rec["band"] = ("below-floor" if eta < ETA_FLOOR else
                       "saturated" if eta > ETA_SAT else "resolvable")

        Wt = P_REF * Q / w
        Ws = 2.0 * emag.get(pick["m"], 0.0)
        scale = math.sqrt(Wt / Ws) if Ws > 0 else None
        Epk = None
        pe = pathlib.Path("postpro") / tag / "probe-E.csv"
        if scale and pe.exists():
            prows = list(csv.reader(pe.read_text().splitlines()))
            ph_ = [x.strip() for x in prows[0]]
            vals = []
            for i in range(len(pr)):
                ci = next((k for k, h in enumerate(ph_)
                           if h.startswith(f"Re{{E_y[{i+1}]}}")), None)
                if ci is None:
                    continue
                rowm = next((rr for rr in prows[1:]
                             if rr and round(float(rr[0])) == pick["m"]), None)
                if rowm:
                    vals.append(math.hypot(float(rowm[ci]),
                                           float(rowm[ci + 1])) * scale)
            if vals:
                Epk = max(vals[:5])
                rec["E_profile_vm"] = vals
        rec.update(f_ghz=pick["f"], Q=Q, eta=eta, power_density_wm3=pdens,
                   linewidth_mhz=pick["f"] * 1e3 / Q, A2_A0=harm.get(2),
                   pull_mhz=1e3 * (pick["f"] - exact), E_peak_vm=Epk,
                   plasma_vol_m3=vol)
        out["points"].append(rec); save(out)
        print(f"    f={pick['f']:.6f} ({rec['pull_mhz']:+.2f} MHz)  "
              f"Q={Q:,.0f}  lw={rec['linewidth_mhz']:.2f} MHz")
        print(f"    power density {pdens:.3g} W/m^3   "
              + (f"|E|peak {Epk:.3g} V/m   " if Epk else "")
              + f"eta={eta:.4f}  A2/A0={harm.get(2,0):.4f}", flush=True)
    _report(out)


def _report(out):
    pts = out["points"]
    print("\n" + "=" * 78)
    print(f"  {'case':>13}{'ri':>6}{'ro':>6}{'z+-':>6}{'ne':>9}{'Q':>9}"
          f"{'eta':>9}{'band':>13}{'W/m^3':>11}")
    by = {}
    for p in pts:
        if "Q" not in p:
            print(f"  {p['case']:>13}   🔴 {p.get('error','no result')[:52]}")
            continue
        by[p["case"]] = p
        print(f"  {p['case']:>13}{p['ri_mm']:>6.1f}{p['ro_mm']:>6.1f}"
              f"{p['z_half_mm']:>6.1f}{p['ne']:>9.0e}{p['Q']:>9,.0f}"
              f"{p['eta']:>9.4f}{p['band']:>13}{p['power_density_wm3']:>11.3g}")
    print()
    # F1 — does placement decide coupling? Compare matched pairs.
    any_ok = False
    for axis, wall in PAIRS:
        pa, pw = by.get(axis), by.get(wall)
        if not pa or not pw:
            print(f"  F1 {axis} vs {wall}: ⚠️ NOT TESTED — a member is missing")
            continue
        # F2 — a pair of two blurs measures nothing
        if pa["band"] == pw["band"] and pa["band"] != "resolvable":
            print(f"  🔴 F2 {axis} vs {wall}: BOTH {pa['band']} "
                  f"(eta {pa['eta']:.4f}, {pw['eta']:.4f}) — uninformative, "
                  f"no ratio quoted")
            continue
        va = math.pi * ((pa['ro_mm']*1e-3)**2 - (pa['ri_mm']*1e-3)**2) * pa['plasma_len_m']
        vw = math.pi * ((pw['ro_mm']*1e-3)**2 - (pw['ri_mm']*1e-3)**2) * pw['plasma_len_m']
        # normalise the ratio by volume so placement is what is being compared
        r = (pw["eta"] / vw) / (pa["eta"] / va) if pa["eta"] > 0 else None
        if r is None:
            print(f"  F1 {axis} vs {wall}: axis eta is zero — no ratio")
            continue
        # 🔴 A SATURATED MEMBER CANNOT FALSIFY ANYTHING. eta is capped at 1, so
        # eta/V for a saturated case is set by 1/V — by its VOLUME, not by its
        # coupling strength. The first version of this printed "wall couples 0x"
        # (a {:,.0f} format bug on a ratio of 0.124) and then fired F1 on it.
        # Both wrong: the ratio is a LOWER BOUND and F1 is untestable.
        if pw["band"] == "saturated" or pa["band"] == "saturated":
            who = wall if pw["band"] == "saturated" else axis
            print(f"  F1 {axis} vs {wall}: ratio {r:.3g}x per unit volume, but "
                  f"{who} is SATURATED (eta={by[who]['eta']:.4f})")
            print(f"     ⚠️ NOT TESTABLE — a saturated member's eta/V is set by "
                  f"its volume, not its coupling. Lower bound only; F1 neither "
                  f"passes nor fires. Re-pick ne/size to unsaturate {who}.")
            continue
        any_ok = True
        print(f"  F1 {axis} vs {wall}: wall couples {r:.3g}x per unit volume")
        if r > 10:
            print("     ✅ placement DECIDES coupling")
        else:
            print("     🔴 F1 FIRES — placement does NOT decide coupling; the "
                  "igniter position argument is wrong")
    if not any_ok:
        print("\n  🔴 NO PAIR WAS INFORMATIVE. Nothing is claimed about "
              "placement. Re-pick ne/geometry so both members land in the "
              "resolvable band.")
    print(f"\n  wrote {TAG}.result.json")


if __name__ == "__main__":
    main()
