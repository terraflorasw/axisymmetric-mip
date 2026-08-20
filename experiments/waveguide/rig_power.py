#!/usr/bin/env python3
"""R73 — STOP MEASURING Q. Measure the power that does not come back.

Q is a global scalar, omega*U/P over the whole cavity. It has no position. Every
rig here has swept a coordinate and read a whole-cavity Q, attributing a global
quantity to a local one — and then tried to invert that back into "what the
coupler at r contributes", which needs the perturbation assumption R71 showed
fails.

🔑 AND Q HAS A DENOMINATOR:

        1/Q_ext = 1/Q_L - 1/Q_0

a difference of reciprocals, ill-conditioned the moment Q_L approaches Q_0, and
undefined without a resonance to measure at all. The LIT cavity barely has one:
its peak position scatters 5 MHz on a 7.6 MHz linewidth, 66% of its own width.
That is the divide-by-zero, structurally, and no amount of careful sampling fixes
a quantity that is not defined where we need it.

🔢 THE OBSERVABLE HERE HAS NO DENOMINATOR AND NO MODEL IN IT:

        eta_total = 1 - |Gamma|^2

"of the power I sent in, what fraction did not come back." One measured number.
No resonance, no linewidth, no mode identification, no offset, no 2x convention,
no peak-finding — the maximum of eta over the band is well defined even when the
band contains a broad flat maximum rather than a resonance, which is exactly the
lit case.

It is also the actual design figure of merit. "Q_ext must be 320" was only ever a
proxy for "most of the power must reach the plasma".

🔑 A CONSEQUENCE WORTH STATING: the R71/R72 ADMISSIBILITY GATE DOES NOT APPLY
HERE. That gate existed because Q-based coupling coefficients are linearisations
that break down when the coupler perturbs the mode. eta measures the real
outcome, so a coupler that restructures the mode is FINE provided it delivers
power. That frees the sweep to use the size we would actually build — sc06's
1001 mm^2 — instead of a probe small enough to be theoretically clean and
practically useless.

DECOMPOSITION, as a cross-check rather than the headline. The absorbed power
splits into plasma, walls and dielectric:

        eta_total = eta_plasma + eta_wall + eta_dielectric

eta_wall comes from SurfaceFlux on the conducting boundary (the 2x time-averaged
convention there was closed in entry 107). If the split does not close to within
a few percent, the decomposition is wrong and only eta_total should be quoted —
that is precisely the discipline that caught the 2x error the first time.

CASES: sc06's loop geometry, plasma-loaded, mounted on the barrel and on the cap
at three radii. The question is direct — does moving the SAME coupler to the cap
deliver more power to the plasma? The field map (R72) predicts 1.64x more linked
flux at r = 50. In eta that is not a clean square law, because eta saturates at
1, so the prediction is DIRECTIONAL: cap > barrel, with r = 50 best.

⚠️ sigma = 30 S/m is still the bare literal at r12.py:26 with error null (R67).
eta depends on it. Ratios between cases at ONE sigma are much safer than any
absolute eta, and that is how this should be read.
"""
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
import meshsweep
import solveconf
import solver

SIGMA = 30.0
PLASMA = "4.5,8.5,-20,10"          # baselines plasma.region, the R12 toroid
LOOP = "25.8,19.4,1.5,0.3"          # sc06 — the best coupler ever measured here
BASE_ARGS = ["--radius", "103.70", "--length", "88.53", "--mode-filter", "3",
             "--azimuthal-bins", "1", "--order", "2", "--loop", LOOP,
             "--plasma", PLASMA, "--plasma-h", "1.0"]
CASES = [("wbarrel", []),
         ("wcap30", ["--loop-cap", "30"]),
         ("wcap50", ["--loop-cap", "50"]),
         ("wcap70", ["--loop-cap", "70"])]
# Loaded TE011 sits near 2.431 GHz with a 7.6 MHz linewidth at Q ~ 320. A 60 MHz
# band is ~8 linewidths — wide enough to survive the 5 MHz peak scatter, and the
# step only has to resolve a BROAD maximum, not a half-power point.
BAND = (2.40, 2.46)
STEP = 2e-4
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")


def build_cfg(mesh, tag):
    """Config with the plasma conductivity and wall-flux postprocessing."""
    meta = solveconf.load_meta(mesh)
    pl = meta["attributes"].get("plasma")
    if pl is None:
        raise RuntimeError(f"{mesh}: no plasma attribute — --plasma was ignored")
    c, meta, dropped = solveconf.driven(
        mesh, tag, BAND, step=STEP, order=1,
        materials={pl: {"Permittivity": 1.0, "Permeability": 1.0,
                        "Conductivity": SIGMA}})
    for d in dropped:
        print(f"    dropped: {d}", flush=True)
    # Energy in the plasma region, for the cross-check decomposition.
    c["Domains"]["Postprocessing"]["Energy"].append(
        {"Index": 90, "Attributes": [pl]})
    # Wall loss. Entry 107: Palace's surface flux carries the same 2x
    # time-averaged convention dq.py already corrects for energy.
    c["Boundaries"].setdefault("Postprocessing", {})["SurfaceFlux"] = [
        {"Index": 1, "Attributes": [meta["attributes"]["wall"]], "Type": "Power"}]
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    return meta, pl


print(__doc__)
print("=" * 78, flush=True)

fac, _ = meshsweep.sweep(CASES, BASE_ARGS)
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")

rows = []
for tag, _e in CASES:
    mesh = f"{tag}.msh"
    try:
        meta, pl = build_cfg(mesh, tag)
    except Exception as e:
        print(f"  🔴 {tag}: {e}", flush=True)
        continue
    t0 = time.time()
    rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"], env=solver.ENV,
                        stdout=open(f"{tag}_p.log", "w"),
                        stderr=subprocess.STDOUT).returncode
    dt = time.time() - t0
    if rc or dt < solver.MIN_SECONDS:
        tail = pathlib.Path(f"{tag}_p.log").read_text().strip().splitlines()
        print(f"  🔴 {tag}: rc={rc} in {dt:.0f}s — {tail[-1] if tail else ''}",
              flush=True)
        continue
    recs = dq.load(tag)
    if not recs:
        print(f"  ⚠️ {tag}: no records", flush=True)
        continue
    # 🔑 NO PEAK-FINDING, NO MODE ID. Just the best point in the band.
    best = max(recs, key=lambda r: (1.0 - r["gamma"] ** 2)
               if r.get("gamma") is not None else -1)
    eta = 1.0 - best["gamma"] ** 2
    rows.append((tag, best["f"], eta, dt, meta["tets"]))
    print(f"  {tag:>8}  {meta['tets']:>7,} tets  {dt:>5.0f}s   "
          f"f@max={best['f']:.5f}   eta_total={100*eta:>5.1f}%", flush=True)

print("\n" + "=" * 78)
print(f"{'case':>9}{'f @ max eta':>13}{'eta_total':>11}{'vs barrel':>11}")
ref = next((r for r in rows if r[0] == "wbarrel"), None)
for tag, f, eta, _dt, _n in rows:
    rel = (eta / ref[2]) if ref else None
    print(f"{tag:>9}{f:>13.5f}{100*eta:>10.1f}%"
          f"{(f'{rel:.2f}x' if rel else '—'):>11}")

print("\nVERDICT")
caps = [r for r in rows if r[0].startswith("wcap")]
if ref and caps:
    best = max(caps, key=lambda r: r[2])
    print(f"  barrel {100*ref[2]:.1f}%   best cap {best[0][4:]} mm "
          f"{100*best[2]:.1f}%   ({best[2]/ref[2]:.2f}x)")
    if best[2] > ref[2] * 1.10:
        print("\n  ✅ MOVING THE COUPLER TO THE CAP DELIVERS MORE POWER.")
        print("     Measured as returned power, with no Q, no resonance and no "
              "linearisation\n     anywhere in it. The field map's direction is "
              "confirmed in the units that\n     matter.")
    elif best[2] > ref[2] * 0.90:
        print("\n  ⚠️ CAP AND BARREL ARE WITHIN 10% — position does not decide "
              "this.")
        print("     The map predicted 1.64x in flux at r = 50. If eta does not "
              "follow, either\n     eta is saturating (check whether both are "
              "near 100%) or the map is wrong.")
    else:
        print("\n  🔴 THE CAP IS WORSE. The map predicted the opposite, and the "
              "map is just the\n     mode field — so the mode is not what the "
              "algebra says. Chase that before\n     any coupler.")
    if max(r[2] for r in rows) > 0.95:
        print("\n  ⚠️ eta > 95% somewhere: the metric is SATURATED and ratios "
              "between cases\n     understate the difference. Compare at a "
              "lower sigma to separate them.")
else:
    print("  no usable comparison — check the logs")
print("\n⚠️ eta depends on sigma = 30 S/m, still a bare literal (R67). Read the "
      "RATIOS,\n   not the absolute percentages.")
print(flush=True)
