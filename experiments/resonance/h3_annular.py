"""H3 (annular) — power density vs plasma ANNULUS (r_i, r_o), at ne=1e20.

🔑 WHY THIS EXISTS. h3_eigen swept a SOLID column and found power density peaking
at R = 0.75 mm. I then reported that peak as "unreachable", reasoning that a
Fassel injector bore has radius 0.75-1.0 mm so plasma could not live there.

That was wrong twice, and both errors are worth naming because neither was a
numerical slip:

  1. GEOMETRY. The injector TIP sits at the bottom of the plasma zone; the plasma
     forms DOWNSTREAM of it. At the plasma's axial location there is no solid
     object at all — the inner radius is set by GAS FLOW, not by a tube wall.
     geometry.py has modelled this correctly the whole time.

  2. MODEL-AS-WORLD. A solid-column sweep CANNOT REPRESENT an annulus, so its
     peak location was never the physical optimum. I read a limitation of the
     rig as a fact about the plasma. `h3_loaded.INNER_R` even carried the
     comment "0 = solid column. >0 would make it annular." The capability was
     always there; I built an analytic correction instead of measuring.

## The physical claim being tested

TE011's E_phi ~ J1(chi*r/a) vanishes on axis, so a plasma CORE near r=0 sits in a
field null and can be removed almost for free. That was the argument when this
rig was aimed at r_o ~ 1 mm.

⚠️ IN THE FLOW BOX THE MECHANISM IS DIFFERENT, and weaker. Skin depth at ne=1e20
is delta = 1.80 mm, so at r_o = 5-8.5 mm we have r_o/delta = 2.8-4.7: the core is
SKIN-SHIELDED, not sitting in a null. Removing it is still nearly free — a
shielded core absorbs nothing — but the volume it frees is a small fraction of
the total. If the core absorbed exactly nothing, density would rise by
r_o^2/(r_o^2 - r_i^2):

    r_i=2.0 r_o=8.5 -> 1.06x        r_i=3.0 r_o=6.0 -> 1.33x
    r_i=2.0 r_o=5.0 -> 1.19x        r_i=1.5 r_o=6.0 -> 1.07x

So expect 5-35% here, NOT the ~1.4x the small-radius arithmetic suggested. That
estimate was computed in a box flow cannot produce and does not transfer.

🔴 EIGEN ONLY (CONVENTIONS §7c). ne=1e20 -> PI_1 = 5.58, proven convergent.

VERIFICATION
  V1  every point identifies TE011 by AZIMUTHAL ORDER (m=0), never by max-Q.
  V2  the two SOLID points (0, 2.0) and (0, 6.0) must reproduce h3_eigen's
      8.16e8 and 9.52e7 W/m^3 within 5%. A rig that cannot reproduce the sweep
      it is extending is not measuring the same thing. These are the anchors F1
      leans on: an expected 1.06-1.33x effect is only readable if they are tight.
FALSIFICATION
  🔴 F1  if hollowing does NOT raise power density above the solid column at the
         same r_o, the shielded-core argument is wrong. Say so and drop it.
         Expected gain here is only 1.06-1.33x, so F1 needs the V2 points to be
         tight or the effect is inside the noise and must be called that.
  🔴 F2  if the best r_o does NOT move outward as r_i grows, the shape claim is
         wrong even if the magnitude happened to land. ⚠️ Only r_i=1.5 and 2.0
         carry 3+ points here, so F3 is testable on those rows ONLY; r_i=2.5 and
         3.0 have two points each and no optimum may be claimed for them.
  🔴 F3  if the best r_o for any r_i sits at the EDGE of that row's sampled
         range, the range is wrong — extend it, do not report an edge.
  🔴 F4  if azimuthal order leaves m=0 the mode is not TE011; report the onset.
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
from h3_loaded import drude, Z_FRAC, EIGEN_TARGET, SECTORS

TAG = "h3_annular"
# 🔴 PER-CONFIGURATION ETA REFERENCE. CONVENTIONS §7c.
# 44,384 is the BARE cavity (no loop, no groove). This rig meshes GEO_DESIGN.
# ⚠️ Was 44384.0 until 2026-08-24, which inflates every eta below.
# 🔴 12,368 IS DISPUTED (2026-08-24) AND ITS PROVENANCE WAS WRONG HERE TOO.
#    It is NOT from `h3_ladder` (that ran bare+grooved and stopped, no step 3).
#    It is `h3_cold`'s, selected by "lowest A2/A0" on a mode labelled m_az=1,
#    and a driven sweep found NO resonance within +-3 MHz of it. See §7s.
# ✅ THE FIX IS STRUCTURAL, NOT A BETTER CONSTANT (§7t): measure the reference
#    as a CASE OF THIS RUN, on this mesh, with this solver — as `h3_driven` now
#    does with ne=0 — instead of importing one. Do that before trusting any eta
#    this rig prints.
# 🔴 CORRECTED TWICE ON 2026-08-24 — get the CONFIGURATION right, not just the
# number. This rig meshes GEO_DESIGN and **NO LOOP** (grep: zero `--loop`), so
# neither cavity I reached for first applies:
#   44,384 = bare, no groove, no loop        (E0)
#   12,368 = an OPEN-GAP ARTIFACT, never real (§7v) — what was here
#   43,523 = grooved + loop 11x8             (the DESIGN cavity, has a loop)
#   44,414 = grooved 5x10, NO loop           <- THIS rig's cavity
# 🔑 `h3_ladder` step 2, externally anchored against H2. Q0 with no port at all,
# so there is no coupling term to remove.
Q_REF = 44414.0
Q_REF_SOURCE = "h3_ladder step 2 — grooved 5x10, no loop, eigen"
P_REF = 1000.0
N_MODES = 4                 # DERIVED in h3_eigen: 4 converges where 6 stalls
TE011_WINDOW = (2.40, 2.50)
CASE_TIMEOUT_S = 900.0
# 🔴 "proved solvable" IS NOT "is the case" (§7ab). PI_1 = 5.58 is a SOLVER
# CONVERGENCE parameter; this value was chosen because eigen converges there and
# has no physical provenance. Downstream rigs then called it "the operating
# point". ⚠️ Results here are CONDITIONAL on a density nobody chose.
NE = 1.0e20                 # PI_1 = 5.58 — a CONVERGENCE choice, not physics

# (r_i, r_o) in mm — THE BOX FLOW PERMITS, not a box chosen for EM convenience.
# Continuity: area = Q*(T/300)/v. Nebulizer 0.5-1.0 slm at 3000-5000 K, 10-25 m/s
# -> r_i = 1.0-3.0 mm. Plasma+aux 15-20 slm at 5000-7000 K, 15-30 m/s -> r_o =
# 6.8-13.1 mm. Capping r_o at a standard Fassel outer tube (17 mm ID -> 8.5 mm)
# back-solves to v = 19-31 m/s, squarely in ICP practice: geometry, flows and
# tube ID close on each other.
#
# 🔴 The FIRST grid here was r_i 0-1, r_o 1-3 mm — chosen around the solid-column
# power-density peak at 0.75 mm. Flow cannot produce that plasma: 15-20 slm at
# plasma temperature has to go somewhere. Sampling it would have measured a
# geometry no torch can make. Sustaining at 1 kW in N2 is not in question either
# — MICAP and MP-AES ship it — so the open variable was always FLOW, and flow is
# what sets (r_i, r_o).
CASES = [(0.00, 2.00), (0.00, 6.00),
         (1.50, 5.00), (1.50, 6.00), (1.50, 8.50),
         (2.00, 5.00), (2.00, 6.00), (2.00, 7.00), (2.00, 8.50),
         (2.50, 6.00), (2.50, 8.50),
         (3.00, 6.00), (3.00, 8.50)]
V2_EXPECT = {2.00: 8.16e8, 6.00: 9.52e7}    # h3_eigen, ne=1e20, SOLID column
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
    zlo, zhi = -Z_FRAC * L, Z_FRAC * L
    Lp = (zhi - zlo) * 1e-3
    eps, sig = drude(NE, w)
    print(f"  cavity a={a:.4f} L={L:.4f}  Q_ref={Q_REF:,.0f}  P_ref={P_REF:.0f} W")
    print(f"  plasma z = +-{Z_FRAC}L ({Lp*1e3:.1f} mm)   "
          f"ne={NE:.0e}  eps={eps:.3f}  sigma={sig:.3g} S/m\n", flush=True)
    out = {"q_ref": Q_REF, "p_ref_w": P_REF, "plasma_len_m": Lp,
           "ne": NE, "eps": eps, "sigma": sig, "points": []}

    for ri, ro in CASES:
        tag = f"{TAG}_i{ri:g}_o{ro:g}".replace(".", "p")
        thick = ro - ri
        ph_mesh = min(1.0, max(0.30, thick / 6.0))   # resolve delta=1.8 mm
        rec = {"ri_mm": ri, "ro_mm": ro, "thick_mm": thick,
               "plasma_h": ph_mesh, "tag": tag}
        print(f"  --- ri={ri} ro={ro} mm (t={thick:.2f}, plasma_h={ph_mesh:.3f})",
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
        if attrs.get("plasma") is None:
            rec["error"] = "no plasma attribute"
            print(f"    🔴 {rec['error']}"); out["points"].append(rec)
            save(out); continue
        bins = sector_bins(m)
        # 🔴 was a local copy of the surface/volume rule. A `loop`
        # SURFACE got classified as a VOLUME (2026-08-27) and
        # Palace refused the config. One definition now.
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
        eta = 1.0 - Q / Q_REF
        vol = math.pi * ((ro * 1e-3) ** 2 - (ri * 1e-3) ** 2) * Lp
        pdens = eta * P_REF / vol

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
    print(f"  {'ri mm':>7}{'ro mm':>7}{'t mm':>7}{'Q':>9}{'lw MHz':>9}"
          f"{'power density':>16}{'|E| V/m':>11}{'eta':>8}")
    for p in pts:
        if "Q" not in p:
            print(f"  {p['ri_mm']:>7.2f}{p['ro_mm']:>7.2f}   🔴 "
                  f"{p.get('error','no result')[:48]}")
            continue
        print(f"  {p['ri_mm']:>7.2f}{p['ro_mm']:>7.2f}{p['thick_mm']:>7.2f}"
              f"{p['Q']:>9,.0f}{p['linewidth_mhz']:>9.2f}"
              f"{p['power_density_wm3']:>16.3g}"
              + (f"{p['E_peak_vm']:>11.3g}" if p.get("E_peak_vm") else f"{'—':>11}")
              + f"{p['eta']:>8.4f}")

    good = [p for p in pts if "Q" in p]
    print()
    # V2 — reproduce the solid points h3_eigen already measured
    for p in good:
        if p["ri_mm"] == 0.0 and p["ro_mm"] in V2_EXPECT:
            exp = V2_EXPECT[p["ro_mm"]]
            d = abs(p["power_density_wm3"] / exp - 1)
            print(f"  V2 solid ro={p['ro_mm']}: {p['power_density_wm3']:.3g} vs "
                  f"h3_eigen {exp:.3g} -> {100*d:.1f}% "
                  + ("✅" if d <= 0.05 else "🔴 FIRES — this rig is not "
                     "measuring what h3_eigen measured; fix before reading on"))
    # F1 — does hollowing beat the solid column at the SAME ro?
    solid = {p["ro_mm"]: p["power_density_wm3"] for p in good if p["ri_mm"] == 0.0}
    gains = [(p, p["power_density_wm3"] / solid[p["ro_mm"]])
             for p in good if p["ri_mm"] > 0 and p["ro_mm"] in solid]
    if gains:
        print()
        for p, g in gains:
            print(f"  F1 ri={p['ri_mm']} ro={p['ro_mm']}: {g:.2f}x the solid "
                  f"column " + ("✅ hollowing helps" if g > 1.0 else
                                "🔴 FIRES — hollowing does NOT help"))
    else:
        print("\n  F1 ⚠️ NOT TESTED — no hollow case shares an ro with a solid one")
    # F2/F3 — best ro per ri, and is it interior?
    print()
    best = {}
    for ri in sorted({p["ri_mm"] for p in good}):
        row = sorted([p for p in good if p["ri_mm"] == ri],
                     key=lambda p: p["ro_mm"])
        if len(row) < 3:
            print(f"  ri={ri}: only {len(row)} point(s) — F3 not testable, "
                  f"no optimum claimed")
            if row:
                best[ri] = max(row, key=lambda p: p["power_density_wm3"])["ro_mm"]
            continue
        d = [p["power_density_wm3"] for p in row]
        i = max(range(len(d)), key=lambda k: d[k])
        best[ri] = row[i]["ro_mm"]
        interior = 0 < i < len(d) - 1
        print(f"  ri={ri}: best ro={row[i]['ro_mm']} ({d[i]:.3g} W/m^3)  "
              + ("F3 ✅ interior" if interior else
                 "🔴 F3 FIRES — at the EDGE of the sampled range; extend it"))
    ris = sorted(best)
    if len(ris) >= 3:
        outward = all(best[ris[k + 1]] >= best[ris[k]] for k in range(len(ris) - 1))
        print(f"\n  F2 best ro vs ri: "
              + ", ".join(f"{r}->{best[r]}" for r in ris) + "  "
              + ("✅ moves outward as predicted" if outward else
                 "🔴 FIRES — the analytic SHAPE is wrong"))
    else:
        print("\n  F2 ⚠️ NOT TESTED — fewer than 3 usable ri rows")
    print(f"\n  wrote {TAG}.result.json")


if __name__ == "__main__":
    main()
