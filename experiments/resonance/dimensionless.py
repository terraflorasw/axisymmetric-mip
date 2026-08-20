#!/usr/bin/env python3
"""The design in dimensionless form — DERIVED from baselines.json, never stored.

🔑 Maxwell's equations are scale-invariant: scale every length by k and the
wavelength by k and the solution is identical. So the cavity electromagnetics is
determined entirely by RATIOS, and millimetres are a presentation choice. This
project has been sweeping millimetres and matching absolute values taken from one
configuration onto another — which is how C1 came to reject ten geometries
against quartz's own number (FINDINGS entry 126).

TWO HARD ANCHORS. Everything else is dimensionless or reduces to it.

  ① f0 = 2.45 GHz, band 2.400-2.500 = ±2.04% FRACTIONAL.
     A REGULATORY anchor (ISM allocation, LDMOS availability), not a physical
     one. Fixes lambda = 122.36 mm; every length becomes a ratio to it.

  ② N2 at 0-2 atm.
     The only place scale-invariance genuinely fails. Paschen is p·d, Townsend
     is E/N, and the N2 vibrational bootstrap is absolute. Produces the plasma
     sigma, which re-enters the electromagnetics ONLY as delta/t or delta/lambda.

Two that LOOK like hard units and are not:
  wall conductivity -> delta_wall/lambda = 1.05e-5, a fixed dimensionless number
  thermal drift     -> df/f = -alpha*dT = -23.6 ppm/K, scale-free. Only the
                       absolute temperature RISE needs units, and that is a
                       cooling question, not an electromagnetic one.

⚠️ THIS FILE DERIVES, IT DOES NOT STORE. baselines.json stays in millimetres
because that is what geometry.py consumes. A hand-maintained second copy in
lambda would become the next thing to drift out of step — which is the failure
that let a dropped mode filter keep being simulated for a day.
"""
import json
import math
import pathlib
import sys

C_MM_GHZ = 299.792458          # mm·GHz
F0 = 2.45                      # GHz — anchor ①
BAND = (2.400, 2.500)
LAMBDA = C_MM_GHZ / F0
MU0 = 4e-7 * math.pi
EPS0 = 8.8541878128e-12


def skin_mm(sigma, f_ghz=F0):
    """RF skin depth in mm. NOT scale-invariant — this is anchor ② leaking in."""
    return 1e3 * math.sqrt(2.0 / (2 * math.pi * f_ghz * 1e9 * MU0 * sigma))


def view(path="baselines.json"):
    """Every length as a fraction of lambda, every frequency as a fraction of f0."""
    d = json.loads(pathlib.Path(path).read_text())
    out = {}
    for k, v in d.items():
        if k == "_meta":
            continue
        u, val = (v.get("unit") or "").strip(), v.get("value")
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            if u.startswith("mm"):
                out[k] = dict(kind="length", mm=val, over_lambda=val / LAMBDA)
            elif u == "GHz":
                out[k] = dict(kind="freq", ghz=val, frac_of_f0=val / F0,
                              detune_pct=100 * (val - F0) / F0,
                              frame=v.get("frame"))
            elif u == "MHz":
                out[k] = dict(kind="freq_delta", mhz=val,
                              frac=val / (1e3 * F0), ppm=1e6 * val / (1e3 * F0),
                              frame=v.get("frame"))
        elif isinstance(val, list) and u.startswith("mm"):
            out[k] = dict(kind="length_list", mm=val,
                          over_lambda=[x / LAMBDA for x in val])
    return out


def check(path="baselines.json"):
    """Every GHz/MHz entry must carry a frame, and raw+offset must equal converged.

    The file carried raw and corrected frequencies unmarked until 2026-08-19, and
    the offsets are mode-dependent — worth a quarter of the 2.400-2.500 band.
    This makes a future unframed entry fail loudly instead of being silently
    mis-read.
    """
    d = json.loads(pathlib.Path(path).read_text())
    bad = [k for k, v in d.items()
           if k != "_meta" and (v.get("unit") or "") in ("GHz", "MHz")
           and not v.get("frame")]
    errs = [f"unframed frequency entries: {bad}"] if bad else []
    for m, off in (("te011", 24.54e-3), ("tm020", 20.06e-3)):
        r, c = d.get(f"{m}.f_raw_order1"), d.get(f"{m}.f_converged")
        if r and c and r.get("value") and c.get("value"):
            gap = abs(r["value"] + off - c["value"])
            if gap > 5e-5:
                errs.append(f"{m}: raw+offset != converged by {1e3*gap:.2f} MHz")
    return errs


if __name__ == "__main__":
    for e in check():
        print(f"  🔴 {e}")
        sys.exit(1)
    v = view()
    print(f"ANCHOR ①  f0 = {F0} GHz -> lambda = {LAMBDA:.2f} mm")
    print(f"          band {BAND[0]}-{BAND[1]} GHz = ±"
          f"{100 * (BAND[1] - BAND[0]) / 2 / F0:.2f}% fractional")
    print(f"ANCHOR ②  N2, 0-2 atm — kinetics, does not scale\n")
    print("LENGTHS (× lambda)")
    for k, e in sorted(v.items()):
        if e["kind"] == "length":
            near = ""
            for n in (2, 3, 4, 5, 6, 8, 10, 12, 16):
                if abs(e["over_lambda"] - 1.0 / n) < 0.006:
                    near = f"  ~ lambda/{n}"
            print(f"  {k:>34}{e['mm']:>9.2f} mm{e['over_lambda']:>9.4f}{near}")
        elif e["kind"] == "length_list":
            print(f"  {k:>34}{str(e['mm']):>13}"
                  f"   {[round(x, 4) for x in e['over_lambda']]}")
    print("\nABSOLUTE FREQUENCIES — band placement, frame-aware")
    print("  offsets are MODE-dependent: TE011 +24.54 MHz, TM020 +20.06, "
          "others UNMEASURED")
    d = json.loads(pathlib.Path("baselines.json").read_text())
    OFF = {"te011": 24.54e-3, "tm020": 20.06e-3}
    for k, e in sorted(v.items()):
        if e["kind"] != "freq":
            continue
        fr = e.get("frame")
        if fr == "converged":
            fc, note = e["ghz"], "converged"
        elif fr == "raw-order1":
            mode = next((m for m in OFF if k.startswith(m)), None)
            if mode is None:
                print(f"  {k:>34}{e['ghz']:>9.4f} GHz   🔴 RAW, offset "
                      f"UNMEASURED for this mode — NO placement claim possible")
                continue
            fc, note = e["ghz"] + OFF[mode], f"raw {e['ghz']:.4f} +{mode}"
        else:
            continue
        inband = BAND[0] < fc < BAND[1]
        print(f"  {k:>34}{fc:>9.4f} GHz{100 * (fc - F0) / F0:>+8.2f}%"
              f"   {'IN band' if inband else 'OUT of band':<11} [{note}]")

    print("\nDIFFERENCES — frame-independent, no offset applies")
    for k, e in sorted(v.items()):
        if e["kind"] == "freq_delta" and e.get("frame") in ("delta", "offset"):
            print(f"  {k:>34}{e['mhz']:>9.2f} MHz{e['ppm']:>9.0f} ppm of f0"
                  f"   [{e['frame']}]")

    print(f"\nANCHOR ② leaking in: skin depth over plasma thickness (t = 4 mm)")
    print(f"  {'sigma':>8}{'delta mm':>11}{'delta/t':>9}{'delta/lambda':>14}")
    for s in (0.3, 1, 3, 10, 30, 100, 300):
        dl = skin_mm(s)
        print(f"  {s:>8g}{dl:>11.2f}{dl / 4.0:>9.2f}{dl / LAMBDA:>14.4f}")
