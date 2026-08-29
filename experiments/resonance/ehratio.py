"""rho = |E| / (c|B|) at the probes — the ELECTRIC-vs-MAGNETIC character of a mode.

🔑 WHY THIS EXISTS. Everything this programme measures is E-FIELD ONLY. Purity
is P = |E_phi|^2/(|E_r|^2+|E_phi|^2+|E_z|^2) — the mode's POLARISATION, not the
coupling MECHANISM. It cannot distinguish an inductive coupler from a capacitive
one, which is the question item 7 turned into.

🔑 AND THE DATA WAS ALREADY THERE. Palace writes `probe-B.csv` beside
`probe-E.csv` in every postpro directory — 111 of each on 2026-08-27 — and
nothing had ever opened one. No solve was needed to produce the first
electric-vs-magnetic measurement in this programme.

🔑 EVALUATION LAYER, DELIBERATELY SEPARATE FROM THE RIG (§10, and the
   separate-measurement-from-evaluation rule), the same way `fieldcheck.py` is.
   The rigs emit probe fields; every judgement here is applied afterwards and
   can be re-run without re-solving.

## The external anchor

For TE011 at the MID-PLANE (z = 0, where sin(pi*zeta) = 1 and cos = 0, so
H_r vanishes and only E_phi and H_z survive):

    E_phi ~ (w*mu*a/chi) H0 J1(x)        H_z ~ H0 J0(x)      x = chi * r/a

    rho = |E|/(c|B|) = (k/k_c) * |J1(x)/J0(x)|,     k_c = chi/a, chi = 3.8317

**Amplitude-free and geometry-only** — it does not depend on how the mode is
normalised, which is what makes it usable as a check on an eigenmode.

⚠️ EXACT ONLY FOR A BARE CYLINDER. With the groove present it is approximate;
measured, grooved-no-loop sits 0.6 MHz off analytic TE011 and rho agrees to
under 1 %. Quote it as a sanity anchor, NOT as a proof.

⚠️ AND A BARE CYLINDER CANNOT SUPPLY A CLEAN TE011 ANYWAY: chi'_01 = chi_11 =
3.8317 because J0' = -J1, so TE011 and TM111 are EXACTLY degenerate at every
aspect ratio and an eigensolve returns an arbitrary mixture. The groove is what
lifts it. So closed form is the instrument's anchor in the cavity BODY; a NULL
FLOOR must come from a no-loop control, not from theory.

## Reading the result

🔴 `pec` SHORTS THE LOOP and lets it resonate (KNOWN.md PRIOR ART), which
inflates rho. `lumped` (50 ohm) is the machine. Compare like with like.

    python3 ehratio.py --slug h3-loop-gap2-02
"""
import csv
import json
import math
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import slug as S

C_M_S = 299792458.0
CHI = 3.831705970207512          # chi'_01 = chi_11 — the degeneracy, in one constant
UNIT = {"E": "(V/m)", "B": "(Wb/m²)"}


def _bessel(order, x):
    """J0/J1 by series. Adequate for x < 8; the probes never exceed chi = 3.83."""
    if x > 8.0:
        raise ValueError(f"series not valid at x={x}; probes should be inside chi")
    if order == 0:
        return sum((-1) ** m / (math.factorial(m) ** 2) * (x / 2) ** (2 * m)
                   for m in range(30))
    return sum((-1) ** m / (math.factorial(m) * math.factorial(m + 1))
               * (x / 2) ** (2 * m + 1) for m in range(30))


def te011_rho_midplane(r_frac, f_ghz, a_mm):
    """Closed-form rho for TE011 at z = 0. Amplitude-free."""
    k = 2.0 * math.pi * f_ghz * 1e9 / C_M_S
    k_c = CHI / (a_mm * 1e-3)
    x = CHI * r_frac
    return (k / k_c) * abs(_bessel(1, x) / _bessel(0, x))


def read_probe(tag, kind, mode_index, n_pts):
    """The complex vector at each probe for one mode, or None."""
    f = pathlib.Path("postpro") / tag / f"probe-{kind}.csv"
    if not f.exists():
        return None
    rows = list(csv.reader(f.read_text().splitlines()))
    head = [x.strip() for x in rows[0]]
    row = next((r for r in rows[1:]
                if r and round(float(r[0])) == mode_index), None)
    if row is None:
        return None
    out = []
    for i in range(1, n_pts + 1):
        try:
            out.append([complex(
                float(row[head.index(f"Re{{{kind}_{ax}[{i}]}} {UNIT[kind]}")]),
                float(row[head.index(f"Im{{{kind}_{ax}[{i}]}} {UNIT[kind]}")]))
                for ax in "xyz"])
        except (ValueError, IndexError):
            return None
    return out


def to_cyl(v, phi_deg):
    """Cartesian -> cylindrical. ⚠️ At phi != 0 these are a ROTATION of E_x/E_y,
    not E_x/E_y directly — the error `h3_ladder.purity` documents."""
    ph = math.radians(phi_deg)
    vx, vy, vz = v
    return (vx * math.cos(ph) + vy * math.sin(ph),
            -vx * math.sin(ph) + vy * math.cos(ph), vz)


def _mag(v):
    return math.sqrt(sum(abs(c) ** 2 for c in v))


def analyse(tag, mode_index, pts, f_ghz, a_mm):
    """rho at every probe, plus purity recomputed as a SELF-CHECK.

    🔑 THE PURITY RECOMPUTE IS THE POINT OF TRUST. This reader must reproduce
    the P_min/spread the rig already recorded before any of its B numbers are
    believed — verify with the consumer, not with the thing you just wrote.
    """
    E = read_probe(tag, "E", mode_index, len(pts))
    B = read_probe(tag, "B", mode_index, len(pts))
    if E is None or B is None:
        return None
    out = []
    for e, b, pt in zip(E, B, pts):
        er, ep, ez = to_cyl(e, pt["phi_deg"])
        tot = abs(er) ** 2 + abs(ep) ** 2 + abs(ez) ** 2
        eM, bM = _mag(e), _mag(b)
        rf = pt["r_mm"] / a_mm
        out.append({
            "r_mm": pt["r_mm"], "r_frac": rf, "phi_deg": pt["phi_deg"],
            "name": pt.get("name"),
            "rho": (eM / (C_M_S * bM)) if bM else None,
            "rho_closed_form": (te011_rho_midplane(rf, f_ghz, a_mm)
                                if 0 < rf < 1 else None),
            "P": (abs(ep) ** 2 / tot) if tot > 0 else None,
            "E_mag": eM, "B_mag": bM,
        })
    return out


def probe_points(rec, a_mm):
    """The probe list in PALACE'S INDEX ORDER, or None if it cannot be trusted.

    🔴 NO RIG RECORDS THE FULL LIST. `h3_loopq` records `probe_names` and
    `probe_named_mm` but never the six purity coordinates, and both gap sweeps
    predate even that. So the first six are rebuilt from `h3_ladder`'s own
    constants — the module the rig itself imports, not a copy — and the named
    ones are read from the record.

    🔑 AND THE REBUILD IS CHECKED AGAINST THE CSV, NOT ASSUMED. The probe count
    must equal the number of `Re{E_x[i]}` columns Palace actually wrote. A
    reconstruction that silently disagrees with the file would mis-address every
    probe and still print a full table.
    """
    from h3_ladder import PROBE_PHI_DEG, PROBE_R_FRAC
    pts = [{"r_mm": rf * a_mm, "phi_deg": pd, "name": None}
           for rf in PROBE_R_FRAC for pd in PROBE_PHI_DEG]
    for nm, (x, y, _z) in (rec.get("probe_named_mm") or {}).items():
        pts.append({"r_mm": math.hypot(x, y),
                    "phi_deg": math.degrees(math.atan2(y, x)), "name": nm})
    return pts


def n_probes_in_file(tag):
    """How many probes Palace actually wrote. The ground truth for the count."""
    f = pathlib.Path("postpro") / tag / "probe-E.csv"
    if not f.exists():
        return None
    head = f.read_text().split("\n", 1)[0]
    return len(re.findall(r"Re\{E_x\[\d+\]\}", head))


def report(tag, mode_index, pts, f_ghz, a_mm, recorded_pmin=None):
    n = n_probes_in_file(tag)
    if n is None:
        print(f"    🔴 no probe-E.csv for {tag}")
        return
    if n != len(pts):
        print(f"    🔴 PROBE COUNT MISMATCH — the file has {n}, the record "
              f"implies {len(pts)}. Indices cannot be trusted; refusing to "
              f"report rather than mis-address every probe.")
        return
    rows = analyse(tag, mode_index, pts, f_ghz, a_mm)
    if rows is None:
        print(f"    🔴 no probe pair on disk for {tag}")
        return
    # 🔴 SELF-CHECK FIRST — reproduce the purity the RIG recorded, from the same
    # file, before any B number here is believed (verify with the consumer).
    ps = [r["P"] for r in rows[:6] if r["P"] is not None]
    if ps and recorded_pmin is not None:
        ok = abs(min(ps) - recorded_pmin) < 1e-4
        print(f"    self-check P_min {min(ps):.6f} vs recorded "
              f"{recorded_pmin:.6f}  "
              + ("✅" if ok else "🔴 READER DISAGREES — rho below is NOT quotable"))
        if not ok:
            return
    print(f"    {'probe':<12}{'r/a':>8}{'phi':>7}{'rho':>10}"
          f"{'TE011':>9}{'ratio':>9}")
    for r in rows:
        cf = r["rho_closed_form"]
        rat = f"{r['rho'] / cf:>8.2f}x" if cf else f"{'—':>9}"
        print(f"    {(r['name'] or 'purity'):<12}{r['r_frac']:>8.4f}"
              f"{r['phi_deg']:>7.1f}{r['rho']:>10.4f}"
              f"{(cf if cf else float('nan')):>9.4f}{rat}")


def main():
    sl = S.parse()
    res = next(iter(sorted(pathlib.Path(".").glob(f"{sl}.*.result.json"))), None)
    if res is None:
        raise SystemExit(f"🔴 no result file for {sl}")
    d = json.loads(res.read_text())
    print(__doc__)
    print("=" * 78)
    for rec in (d.get("points") or d.get("loops") or []):
        a_mm = rec.get("_a")
        if a_mm is None:
            print(f"  🔴 {rec.get('name')}: no cavity radius in the record")
            continue
        pts = probe_points(rec, a_mm)
        for bc in ("pec", "lumped"):
            t = rec.get(f"te011_{bc}")
            if not t or t.get("mode_index") is None:
                continue
            print(f"\n  {rec.get('name')} / {bc}   f0={t['f_ghz']:.5f} GHz")
            report(f"{S.out(sl)}_{rec['name']}_{bc}", t["mode_index"],
                   pts, t["f_ghz"], a_mm, t.get("P_min"))


if __name__ == "__main__":
    main()
