"""Bind each point of `h3-lambda4-02` to its ld by ARTEFACT, not by array order.

🔴 WHY THIS EXISTS. `h3_driven`'s loop axis built every case's tag without the
swept variable, so all four cases wrote to ONE mesh, ONE .meta.json and ONE
postpro directory, and `ld` was recorded in no field of the result. The four
points are therefore distinguishable only by their position in the array —
which is an ARGUMENT (the SWEEP is built in `loop_grid` order and appended in
loop order), and §7bm is explicit that an argument does not discharge the
burden a bug creates. The GEO debt was discharged by artefact — the mesh
sidecar's own record of what it meshed — and this needs the same.

🔑 THE ARTEFACT AVAILABLE IS THE TET COUNT. Each point carries `tets` from its
own `load_meta`, taken at solve time. Re-meshing each ld through the SAME
`build_mesh` and comparing reproduces that number for the right ld and no
other, provided the counts are distinct (they are: 125,853 / 123,949 / 123,987
/ 124,438 — but two differ by 38, so the match must be EXACT, not near).

⚠️ THIS RE-MESHES ONLY. No solve, no overwrite of the surviving run artefacts:
the tags below are this script's own and share no name with the run's.

    ops/go ops/runthere.sh verify_ld_tets.py --slug h3-lambda4-02
"""
import math
import sys

import h3_driven as H

# the tets each point recorded at solve time, in the order they were appended
OBSERVED = [125853, 123949, 123987, 124438]
LD_GRID = [float(v) for v in H.PRM["loop_grid"]]


def main():
    if len(LD_GRID) != len(OBSERVED):
        raise SystemExit(f"🔴 loop_grid has {len(LD_GRID)} entries, "
                         f"{len(OBSERVED)} observed tet counts")
    if len(set(OBSERVED)) != len(OBSERVED):
        raise SystemExit("🔴 the observed tet counts are NOT distinct — this "
                         "fingerprint cannot bind anything. Re-run instead.")
    a, L = H.design_point()
    w = 2.0 * math.pi * 2.45e9
    zlo, zhi = -H.Z_FRAC * L, H.Z_FRAC * L
    eps_p, sig_p = H.drude(float(H.PRM.get("ne_fixed", 0.0)), w)
    print(f"  cavity a={a:.6f} L={L:.6f}  bore {H.RI:g}-{H.RO:g} mm  "
          f"ne={float(H.PRM.get('ne_fixed', 0.0)):.1e}", flush=True)

    got = {}
    for ld in LD_GRID:
        rec = {}
        meta = H.build_mesh(f"ldverify_ld{ld:g}".replace(".", "p"),
                            a, L, zlo, zhi, eps_p, sig_p, rec,
                            H.RI, H.RO, _ld_override=ld)
        if meta is None:
            print(f"  🔴 ld={ld:g} FAILED TO MESH: "
                  f"{rec.get('_last_mesh_err', '')[:150]}", flush=True)
            continue
        got[ld] = meta["tets"]
        print(f"  ld={ld:>5g}  tets={meta['tets']:>9,}  "
              f"size-factor {rec.get('size_factor')}", flush=True)

    print("\n" + "=" * 70)
    ok = True
    for i, (ld, obs) in enumerate(zip(LD_GRID, OBSERVED)):
        t = got.get(ld)
        hit = (t == obs)
        ok &= hit
        print(f"  point[{i}] tets={obs:>9,}  vs ld={ld:<5g} re-mesh "
              f"{t if t is None else format(t, ','):>9}  "
              + ("✅ BOUND" if hit else "🔴 MISMATCH"))
    # 🔑 A UNIQUE match matters as much as a match: if a re-meshed ld reproduces
    # a DIFFERENT point's count too, the fingerprint does not identify anything.
    for ld, t in got.items():
        n = OBSERVED.count(t)
        if n > 1:
            print(f"  🔴 ld={ld:g}'s count {t:,} matches {n} points — "
                  f"NOT a unique fingerprint.")
            ok = False
    print()
    if ok:
        print("  ✅ ALL FOUR POINTS BOUND BY ARTEFACT. The order mapping is "
              "confirmed by re-meshing,\n     not assumed. ld may be attached "
              "to the record.")
    else:
        print("  🔴 NOT BOUND. Do NOT attach ld by order — re-run the sweep "
              "with the fixed tagging.")
        sys.exit(1)


if __name__ == "__main__":
    main()
