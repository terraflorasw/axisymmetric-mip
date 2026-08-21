"""E0f2 — E0f re-run at SOLVER ORDER 2, testing an ANALYTIC faceting prediction.

E0f held the solver at order 1 throughout, "so that only the geometry varies".
E0g then showed order-1 solver error is 12-17 MHz and MODE-DEPENDENT BY 40x —
larger than the geometric effect E0f was resolving, and varying between the modes
it compared. Two of E0f's conclusions rest on that contaminated baseline:

    "geometric order 2->3 changes nothing (0.01 MHz)"   -> plateau, or masked?
    "an inscribed polygon would read high (signs were   -> mixed signs are
     mixed)"                                               exactly what a
                                                           mode-dependent 12-17
                                                           MHz error produces

Neither is refuted. Neither is established. This re-runs the same representation
study with the field basis no longer the dominant error.

🔑 AND IT NOW HAS A NUMBER TO HIT, not just a direction. physics.faceting_shift_mhz
predicts the geometric-order-1 error with NO SIMULATION IN IT: a straight-sided
mesh inscribes the true cylinder, the equal-area radius of an N-gon is
sqrt((N/2pi) sin(2pi/N)), and frequency responds only through the radial share of
f^2. The prediction is computed HERE from each mesh's ACTUAL applied element size
(meta sizing_mm.air), not from a nominal one.

PREDICTION, DECLARED BEFORE THE RUN
    geometric order 1   Δ POSITIVE, and within ~50% of faceting_shift_mhz
                        per mode. TM020 should move ~2x TE011, because TE011's
                        radial share is 0.52 and TM020's is 1.0.
    geometric order 2   |Δ| far smaller
    geometric order 3   no further improvement (E0f's plateau, now uncontaminated)

🔴 FALSIFIERS
    1. order-1 Δ NEGATIVE on the low modes -> the inscribed-polygon model is
       wrong, and E0f's "signs were mixed" was not contamination after all.
    2. order-1 Δ positive but off by >3x -> the model has the right sign and the
       wrong magnitude; the equal-area assumption is the first suspect.
    3. order 2 and 3 differing by more than the 8 kHz mesher floor (E0kp) ->
       geometric order 2 is NOT converged and E0f's plateau was real but
       misread.

⚠️ Geometric order 1 meshes are BIT-REPRODUCIBLE (E0m), so that side of this
comparison carries zero mesher jitter. Orders 2 and 3 carry the ~8 kHz floor
E0kp measured — negligible against everything here.

VERIFICATION   physics.spectrum(), exact, plus the faceting prediction above.
FALSIFICATION  the exactly-degenerate TE011/TM111 splitting, true value 0.
"""
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import eigmodes
import physics as ph
from e0_solver_vs_math import A_MM, L_MM, build, eigen_cfg, run, eig

ORDERS = [1, 2, 3]
CASES = [(f"e0f2_o{o}", ["--order", str(o)]) for o in ORDERS]
SOLVER_ORDER = 2
DEG = [("TE011", "TM111")]
# (kind, m, n, p) for the modes the faceting model covers analytically
MODEL = {"TE011": ("TE", 0, 1, 1), "TM010": ("TM", 0, 1, 0),
         "TM020": ("TM", 0, 2, 0), "TM011": ("TM", 0, 1, 1),
         "TM110": ("TM", 1, 1, 0), "TE111": ("TE", 1, 1, 1)}


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    EX = ph.spectrum(A_MM, L_MM)

    info = {}
    for tag, extra in CASES:
        m, fac = build(tag, extra)
        h = hashlib.sha256(pathlib.Path(f"{tag}.msh").read_bytes()).hexdigest()[:12]
        info[tag] = (m, h, fac)
        print(f"    sha {h}  mesh_order {m.get('mesh_order')}  "
              f"h_air {m.get('sizing_mm', {}).get('air', float('nan')):.2f} mm",
              flush=True)

    hs = {t: h for t, (_m, h, _f) in info.items()}
    if len(set(hs.values())) != len(CASES):
        sys.exit("🔴 identical meshes across geometric orders — NOT solving.")
    print(f"  ✅ {len(CASES)} distinct meshes\n", flush=True)

    # the prediction, from the ORDER-1 mesh's actual element size
    h_air = info[CASES[0][0]][0].get("sizing_mm", {}).get("air")
    pred = {}
    if h_air:
        for k, (kind, m_, n_, p_) in MODEL.items():
            pred[k] = ph.faceting_shift_mhz(kind, m_, n_, p_, A_MM, L_MM, h_air)
        import math
        print(f"  ANALYTIC PREDICTION for geometric order 1, from h_air="
              f"{h_air:.2f} mm (N≈{2*math.pi*A_MM/h_air:.1f} facets):")
        for k in sorted(pred, key=lambda x: EX.get(x, 0)):
            print(f"    {k:>7}  {pred[k]:+8.2f} MHz  "
                  f"(radial share {ph.radial_share(*MODEL[k], A_MM, L_MM):.3f})")
        print(flush=True)

    for tag, _e in CASES:
        c = eigen_cfg(tag, info[tag][0])
        c["Solver"]["Order"] = SOLVER_ORDER          # EXPLICIT, never inherited
        assert c["Solver"]["Order"] == SOLVER_ORDER
        print(f"  {tag}: solver order {SOLVER_ORDER}", flush=True)
        run(tag, c)
    res = {t: eig(t) for t, _e in CASES}

    print(f"\nΔ from EXACT, MHz — SOLVER ORDER {SOLVER_ORDER}, size factor fixed\n")
    hdr = f"{'mode':>7}{'exact':>11}" + "".join(f"{'geom ' + str(o):>11}"
                                                for o in ORDERS)
    print(hdr + f"{'predicted':>12}{'o1/pred':>9}")
    rows = {}
    for k, fx in sorted(EX.items(), key=lambda kv: kv[1]):
        row, vals = [], {}
        for t, _e in CASES:
            p, _r = ph.match_exact(EX, res[t], DEG)
            if k in p:
                d = 1e3 * (p[k] - fx)
                vals[t] = d
                row.append(f"{d:>11.3f}")
            else:
                row.append(f"{'—':>11}")
        pr = pred.get(k)
        o1 = vals.get(CASES[0][0])
        ratio = (f"{o1/pr:>9.2f}" if (pr and o1 is not None and abs(pr) > 1e-9)
                 else f"{'—':>9}")
        print(f"{k:>7}{fx:>11.5f}" + "".join(row)
              + (f"{pr:>12.2f}" if pr is not None else f"{'—':>12}") + ratio)
        rows[k] = {"exact": fx, "delta": vals, "predicted": pr}

    print(f"\n{'':>18}" + "".join(f"{info[t][0]['tets']:>11,}" for t, _e in CASES)
          + "   elements")
    print(f"\n  🔑 TE011/TM111 splitting, true value EXACTLY 0:")
    split = {}
    for t, _e in CASES:
        # 🔴 was sorted(...)[:2] — the two NEAREST, which are BOTH TM111
        # polarisations (m=1 is doubly degenerate). That reported TM111's
        # internal splitting, not TE011<->TM111. See eigmodes.te011_tm111.
        _d = eigmodes.te011_tm111(res[t], EX["TE011"])
        n = [_d['tm111'], _d['te011']] if _d else sorted(res[t], key=lambda x: abs(x - EX["TE011"]))[:2]
        split[t] = 1e3 * abs(n[1] - n[0])
        print(f"    geometric order {t[-1]}:  {split[t]:8.3f} MHz")

    o2, o3 = CASES[1][0], CASES[2][0]
    d23 = {k: abs(rows[k]["delta"].get(o2, 0) - rows[k]["delta"].get(o3, 0))
           for k in rows if o2 in rows[k]["delta"] and o3 in rows[k]["delta"]}
    if d23:
        worst = max(d23.values())
        print(f"\n  geometric order 2 vs 3: worst |Δ| = {worst*1e3:.1f} kHz "
              f"(mesher floor is 8 kHz, E0kp)")

    json.dump({"exact": EX, "solver_order": SOLVER_ORDER, "orders": ORDERS,
               "sha": hs, "h_air_mm": h_air, "prediction_mhz": pred,
               "rows": rows, "splitting_mhz": split,
               "modes": {t: sorted(res[t]) for t, _e in CASES},
               "tets": {t: info[t][0]["tets"] for t, _e in CASES}},
              open("e0f2.result.json", "w"), indent=1)
    print("\n  wrote e0f2.result.json — NO VERDICT HERE", flush=True)


if __name__ == "__main__":
    main()
