"""H3 (eigen) — power density and loaded Q vs plasma radius. The torch spec sheet.

🔑 WHAT CHANGED, AND WHY. Earlier versions reported **eta**, the fraction of
dissipated power reaching the plasma. Measured at ne=1e20: eta = 0.947 at R=2 mm
and 0.991 at R=4 mm — 4.6% apart. **eta does not discriminate.** Over that same
2x in radius:

    power density   4.0x LOWER at 4 mm   -> sets TEMPERATURE, hence n_e
    loaded Q        5.7x LOWER at 4 mm   -> sets the TUNING-LOOP bandwidth
                                            (linewidth 1.03 -> 5.90 MHz)

So the torch is NOT moot; eta was simply the wrong readout. This rig reports
power density and loaded Q as PRIMARY, with eta demoted to a sanity check.

⚠️ eta is only ~1 in the METAL-LIKE regime. At ne=1e18, R=2 mm it was 0.185, so
in the marginal regime — exactly where sustaining is decided — it still
discriminates. Both rows below are run for that reason.

## Why a FINE sweep in R, not brackets

Power density = eta * P / volume, and volume ~ R^2:
  * small R: eta ~ R^4 (TE011's field grows linearly from the axis) -> ~ R^2, RISING
  * large R: eta saturates near 1                                   -> ~ 1/R^2, FALLING

**There is a maximum**, and a bracket cannot find a maximum. Measurement already
shows it lies BELOW 4 mm — smaller than a crude analytic sketch suggested, which
is why it is being measured.

## Sampling: dimensionless, and clear of the unusable band

CONVENTIONS §6d. PI_1 = wp/sqrt(w^2+nu^2) = sqrt(1 - Re eps_eff), transition at 1
by construction. Measured eigen behaviour:

    PI_1 = 0.02 .. 0.56   converges
    PI_1 = 1.76           🔴 FAILS — the div-free projection runs on PCG, which
                          needs a POSITIVE-DEFINITE operator, and eps_eff is
                          indefinite near the crossing
    PI_1 = 5.58 .. 17.6   converges

So the two rows sit at **PI_1 = 0.56 (gas-like)** and **5.58 (metal-like)**,
either side of a transition whose location the equations already give us. We do
not need to FIND PI_1 = 1; we need behaviour on each side.

🔴 EIGEN ONLY (CONVENTIONS §7c). The indefinite band needs driven, and that is a
SEPARATE rig. Converting one file between solvers cost three failed launches and
two silently wrong values.

## What is measured

    power density   eta * P_REF / V_plasma, at a stated reference input power
    Q_loaded        and the linewidth it implies — the tuning-loop requirement
    |E| in plasma   from POINT PROBES, renormalised to P_REF. Probes are the
                    only route to field here: stored electric energy is ~eps|E|^2
                    and goes NEGATIVE where eps_eff < 0 (measured: -3e-5)
    eta             sanity check, not the answer
    A2/A0           azimuthal order — is it still TE011 (m=0)?

⚠️ NORMALISATION. Eigenmode fields carry arbitrary scale. Physical field comes
from Q = w*W/P_diss, so W_target = P_REF*Q/w, and E scales as sqrt(W). W is taken
as **2 x E_mag_total**, NOT E_elec + E_mag: magnetic energy is positive
everywhere (mu is real), while electric energy is ill-defined in sign where
eps_eff < 0.

🔴 WHAT THIS DOES NOT DO. It does not close the loop from power density to
temperature to n_e — that needs a thermal balance Palace does not have. It hands
over W/m^3 and stops. Producing a temperature here would be the cold-cavity error
again.

VERIFICATION
  V1  every point identifies TE011 by AZIMUTHAL ORDER (m=0) in 2.40-2.50, never
      by max-Q: max-Q selects the 2.62 mode, which has almost no bore field and
      came back IDENTICAL across a 10x density change.
  V2  the R=2 mm, ne=1e20 point must reproduce Q = 2,369 (already measured
      twice). A rebuilt rig that cannot reproduce a known point is not measuring.
FALSIFICATION
  🔴 F1  if power density is MONOTONIC across the whole R range, there is no
         interior maximum and the range is wrong — extend it rather than
         reporting an edge as an optimum.
  🔴 F2  if azimuthal order leaves m=0, the mode is not TE011 and numbers past
         that point describe something else. Report the onset.
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
# 🔴 GEO_DESIGN, not GEO. GEO is the BARE cavity (groove 0,0) and exists
# for instrument rigs comparing against closed form. This rig produces
# DESIGN numbers, so it needs the cavity being built — groove 5x10 (H2).
# Every result this rig produced before 2026-08-23 was groove-free and is
# DISCARDED; see CONVENTIONS §7f.
from e0_solver_vs_math import GEO_DESIGN as GEO, eigen_cfg, run, volume_attrs
from e0k2_anchor import design_point, wall_sigma
from e0k2_azim import sector_bins, read_sector_energy
from h3_loaded import drude, Z_FRAC, INNER_R, EIGEN_TARGET, SECTORS

TAG = "h3_eigen"
Q_BARE = 44384.0
P_REF = 1000.0              # W — a stated reference, not a design point
N_MODES = 4                 # DERIVED: 4 converges where 6 stalls (CONVENTIONS §6)
TE011_WINDOW = (2.40, 2.50)
CASE_TIMEOUT_S = 900.0

# two rows, either side of the transition, both at PI_1 values proven solvable
ROWS = [("metal-like", 1.0e20, [0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]),
        ("gas-like",   1.0e18, [1.0, 2.0, 4.0, 8.0, 16.0])]


def pi1(ne, w, nu=1.0e11):
    eps0, e, me = 8.8541878128e-12, 1.602176634e-19, 9.1093837015e-31
    return math.sqrt(ne * e * e / (eps0 * me) / (w * w + nu * nu))


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
    zlo, zhi = -Z_FRAC * L, Z_FRAC * L
    Lp = (zhi - zlo) * 1e-3
    print(f"  cavity a={a:.4f} L={L:.4f}  Q_bare={Q_BARE:,.0f}  P_ref={P_REF:.0f} W")
    print(f"  plasma column length {Lp*1e3:.1f} mm (z = +-{Z_FRAC}L)\n", flush=True)
    out = {"q_bare": Q_BARE, "p_ref_w": P_REF, "plasma_len_m": Lp, "points": []}

    for label, ne, radii in ROWS:
        eps, sig = drude(ne, w)
        print(f"\n{'='*78}\n  ROW: {label}  ne={ne:.0e}  PI_1={pi1(ne,w):.2f}  "
              f"eps={eps:.3f}  sigma={sig:.3g} S/m\n", flush=True)
        for R in radii:
            tag = f"{TAG}_{label[:5]}_r{R:g}".replace(".", "p")
            ph_mesh = max(0.25, R / 3.0)
            rec = {"row": label, "R_mm": R, "ne": ne, "eps": eps, "sigma": sig,
                   "pi1": pi1(ne, w), "plasma_h": ph_mesh, "tag": tag}
            print(f"  --- R={R} mm (plasma_h={ph_mesh:.2f})", flush=True)
            args = (list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                                 "--sectors", str(SECTORS),
                                 "--plasma", f"{INNER_R},{R},{zlo:.4f},{zhi:.4f}",
                                 "--plasma-h", f"{ph_mesh:.3f}"])
            r = subprocess.run([sys.executable, "geometry.py", "--out",
                                f"{tag}.msh", "--size-factor", "1.5"] + args,
                               capture_output=True, text=True)
            if r.returncode or not pathlib.Path(f"{tag}.msh").exists():
                rec["error"] = f"mesh failed: {(r.stdout + r.stderr)[-200:]}"
                print(f"    🔴 {rec['error'][:130]}\n    REPORTED.", flush=True)
                out["points"].append(rec); save(out); continue
            m = solveconf.load_meta(f"{tag}.msh")
            attrs = m["attributes"]
            if attrs.get("plasma") is None:
                rec["error"] = "no plasma attribute"
                print(f"    🔴 {rec['error']}"); out["points"].append(rec)
                save(out); continue
            bins = sector_bins(m)
            # 🔴 was a local copy of the surface/volume rule — one of
            # NINE. A `loop` SURFACE got classified as a VOLUME and
            # Palace refused the config (2026-08-27). One definition.
            vols = volume_attrs(m)
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
            # probes across the plasma, plus the vacuum landmark at 0.4805a
            pr = [0.02 * R, 0.25 * R, 0.5 * R, 0.75 * R, 0.98 * R,
                  1.5 * R, 0.4805 * a]
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
            # V1: identify by AZIMUTHAL ORDER, never by max-Q
            cands = []
            for md in modes:
                u = sec.get(float(md["m"]))
                if u is None and sec:
                    u = sec[min(sec, key=lambda x: abs(x - md["m"]))]
                m_az, conf, harm = azimuthal.order(u) if u else (None, 0, {})
                if m_az == 0 and TE011_WINDOW[0] < md["f"] < TE011_WINDOW[1]:
                    cands.append((md, harm))
            if not cands:
                rec["error"] = (f"no m=0 mode in {TE011_WINDOW}; modes "
                                f"{[round(md['f'],5) for md in modes]}")
                print(f"    🔴 F2: {rec['error']}", flush=True)
                out["points"].append(rec); save(out); continue
            if len(cands) > 1:
                rec["ambiguous"] = [round(cc[0]["f"], 6) for cc in cands]
                print(f"    ⚠️ {len(cands)} m=0 candidates {rec['ambiguous']} — "
                      f"taking nearest 2.45 and saying so", flush=True)
            pick, harm = min(cands, key=lambda cc: abs(cc[0]["f"] - exact))
            Q = qs.get(pick["m"], 0.0)
            eta = 1.0 - Q / Q_BARE
            vol = math.pi * (R * 1e-3) ** 2 * Lp
            pdens = eta * P_REF / vol

            # physical field: W_target = P*Q/w, and W = 2*E_mag (positive-definite)
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
                    Epk = max(vals[:5])          # peak within the plasma
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
    print("\n" + "=" * 78)
    print(f"  {'row':>11}{'R mm':>7}{'Q':>9}{'lw MHz':>9}"
          f"{'power density':>16}{'|E| V/m':>11}{'eta':>8}")
    for p in out["points"]:
        if "Q" not in p:
            print(f"  {p['row']:>11}{p['R_mm']:>7.2f}   🔴 "
                  f"{p.get('error','no result')[:44]}")
            continue
        print(f"  {p['row']:>11}{p['R_mm']:>7.2f}{p['Q']:>9,.0f}"
              f"{p['linewidth_mhz']:>9.2f}{p['power_density_wm3']:>16.3g}"
              + (f"{p['E_peak_vm']:>11.3g}" if p.get("E_peak_vm") else f"{'—':>11}")
              + f"{p['eta']:>8.4f}")
    for row in ("metal-like", "gas-like"):
        pts = [p for p in out["points"] if p.get("row") == row and "Q" in p]
        if len(pts) < 3:
            continue
        pts.sort(key=lambda p: p["R_mm"])
        d = [p["power_density_wm3"] for p in pts]
        i = max(range(len(d)), key=lambda k: d[k])
        interior = 0 < i < len(d) - 1
        print(f"\n  {row}: power density peaks at R = {pts[i]['R_mm']} mm "
              f"({d[i]:.3g} W/m^3)")
        print(f"    F1 interior maximum: "
              + ("✅ found — the range brackets it"
                 if interior else
                 "🔴 FIRES — the peak is at the EDGE of the range. Extend it; "
                 "do NOT report an edge as an optimum."))
        print(f"    loaded linewidth spans {min(p['linewidth_mhz'] for p in pts):.2f}"
              f" to {max(p['linewidth_mhz'] for p in pts):.2f} MHz "
              f"— the tuning-loop requirement across this range")
    save(out)
    print(f"\n  wrote {TAG}.result.json", flush=True)


if __name__ == "__main__":
    main()
