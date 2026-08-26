"""Measure the ACTUAL faceting deficit of the geometric-order-1 mesh.

E0f2: the analytic faceting model reproduced the per-mode STRUCTURE to 2.5% but
came out 1.36x too large. Suspected cause is MY input, not the model: I estimated
facets as N = 2*pi*a/h_air, while geometry.py sets MeshSizeFromCurvature=12,
which refines the curved wall BELOW the nominal air size. Shift goes as 1/N^2, so
a true N about 1.17x larger would account for the whole discrepancy.

Two independent measurements, neither using h_air:

  1. VOLUME. The order-1 mesh is straight-sided tets, so its volume is EXACT and
     is precisely the quantity the equal-area model is about:
         a_eff = sqrt(V_mesh / (pi L))      -> deficit with no N in it at all
  2. EDGES. Mean azimuthal chord length on the barrel -> N = 2 pi a / chord.

VERIFICATION   the two must agree on N. They measure the same faceting by
               different routes (volume vs perimeter).
FALSIFICATION  if the measured deficit still predicts shifts 1.36x too large,
               the error is in the MODEL (the equal-area assumption), not in my
               estimate of N — and the constant ratio needs a physical
               explanation instead.
"""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph

MESH = "e0f2_o1.msh"
# 🔴 LEGACY CAVITY, DELIBERATELY NOT BOUND. 103.70/88.53 is D/L = 2.343 —
# candidate A, which H1 REJECTED. This script ANALYSES data meshed at those
# dimensions, so the closed form here must use them or the comparison is
# meaningless. Binding it to cavity.d_over_l would silently break that.
# ⚠️ THEREFORE NOTHING HERE IS A DESIGN NUMBER. Re-run on H1's cavity is
# queued in NEXT.md § THE GEO RE-RUN LIST (2026-08-25).
A_MM, L_MM = 103.70, 88.53   # LEGACY — see above
MODEL = {"TE011": ("TE", 0, 1, 1), "TM010": ("TM", 0, 1, 0),
         "TM020": ("TM", 0, 2, 0), "TM011": ("TM", 0, 1, 1),
         "TM110": ("TM", 1, 1, 0), "TE111": ("TE", 1, 1, 1)}


def read_msh(path):
    nodes, tets, tris = {}, [], []
    it = iter(open(path))
    for line in it:
        s = line.strip()
        if s == "$Nodes":
            for _ in range(int(next(it))):
                p = next(it).split()
                nodes[int(p[0])] = (float(p[1]), float(p[2]), float(p[3]))
        elif s == "$Elements":
            for _ in range(int(next(it))):
                p = [int(x) for x in next(it).split()]
                etype, ntags = p[1], p[2]
                ids = p[3 + ntags:]
                if etype == 4:
                    tets.append(ids[:4])
                elif etype == 2:
                    tris.append(ids[:3])
    return nodes, tets, tris


def tet_volume(a, b, c, d):
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    w = [d[i] - a[i] for i in range(3)]
    return abs(u[0] * (v[1] * w[2] - v[2] * w[1])
               - u[1] * (v[0] * w[2] - v[2] * w[0])
               + u[2] * (v[0] * w[1] - v[1] * w[0])) / 6.0


def n_from_ratio(ratio):
    """Invert facet_radius_ratio numerically: which N gives this deficit?"""
    lo, hi = 3.0, 100000.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if ph.facet_radius_ratio(mid) < ratio:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main():
    p = pathlib.Path(MESH)
    if not p.exists():
        sys.exit(f"ERROR: {MESH} not found (it lives on the instance)")
    nodes, tets, tris = read_msh(MESH)
    print(__doc__)
    print("=" * 78)
    print(f"  {len(nodes):,} nodes, {len(tets):,} tets, {len(tris):,} triangles")

    zs = [n[2] for n in nodes.values()]
    L = (max(zs) - min(zs)) * 1e3
    rs = [math.hypot(n[0], n[1]) for n in nodes.values()]
    a_nom = max(rs) * 1e3
    print(f"  from the mesh: L = {L:.3f} mm, max r = {a_nom:.4f} mm "
          f"(nominal a = {A_MM})")

    V = sum(tet_volume(*[nodes[i] for i in t]) for t in tets)
    V_true = math.pi * (A_MM * 1e-3) ** 2 * (L_MM * 1e-3)
    a_eff = math.sqrt(V / (math.pi * (L_MM * 1e-3))) * 1e3
    ratio_vol = a_eff / A_MM
    print(f"\n  1. VOLUME")
    print(f"     mesh volume  {V*1e6:12.4f} cm^3")
    print(f"     true cylinder{V_true*1e6:12.4f} cm^3   deficit "
          f"{100*(1-V/V_true):.4f}%")
    print(f"     a_eff = {a_eff:.5f} mm   a_eff/a = {ratio_vol:.8f}")
    print(f"     -> N_eff = {n_from_ratio(ratio_vol):.1f} facets")

    # 2. barrel edges: nodes essentially on the wall
    rmax = max(rs)
    wall = {i for i, n in nodes.items()
            if math.hypot(n[0], n[1]) > 0.999 * rmax}
    edges = set()
    for t in tris:
        if all(i in wall for i in t):
            for x, y in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                edges.add((min(x, y), max(x, y)))
    chords = []
    for x, y in edges:
        px, py = nodes[x], nodes[y]
        dth = abs(math.atan2(py[1], py[0]) - math.atan2(px[1], px[0]))
        dth = min(dth, 2 * math.pi - dth)
        if dth > 1e-9:
            chords.append(dth)
    print(f"\n  2. EDGES")
    print(f"     wall nodes {len(wall):,}, wall edges {len(edges):,}, "
          f"azimuthal edges {len(chords):,}")
    if chords:
        chords.sort()
        med = chords[len(chords) // 2]
        print(f"     median azimuthal step {math.degrees(med):.4f} deg"
              f"  -> N = {2*math.pi/med:.1f} facets")

    # 🔴 The median azimuthal STEP over triangle edges is not the facet count:
    # on an unstructured surface mesh most edges run diagonally, spanning less
    # theta than a full facet, which biases N high. Count the distinct
    # azimuthal POSITIONS instead — that is the polygon's actual vertex count.
    ths = sorted(math.atan2(nodes[i][1], nodes[i][0]) % (2 * math.pi)
                 for i in wall)
    tol = math.radians(0.5)
    distinct = 1
    for x, y in zip(ths, ths[1:]):
        if y - x > tol:
            distinct += 1
    if (ths[0] + 2 * math.pi) - ths[-1] <= tol:
        distinct -= 1
    print(f"     distinct azimuthal positions among wall nodes: {distinct}")
    if distinct:
        print(f"     -> {len(wall)/distinct:.1f} nodes per azimuthal position "
              f"(z-levels), N = {distinct} facets")

    h_air = None
    side = pathlib.Path(MESH).with_suffix(".meta.json")
    if side.exists():
        h_air = json.loads(side.read_text()).get("sizing_mm", {}).get("air")
        if h_air:
            print(f"\n  for comparison, MY ESTIMATE was N = 2*pi*a/h_air = "
                  f"{2*math.pi*A_MM/h_air:.1f}  (h_air {h_air:.2f} mm)")

    print(f"\n  RE-PREDICTED SHIFTS using the MEASURED volume deficit:")
    print(f"    {'mode':>7}{'predicted':>11}{'measured':>10}{'ratio':>8}")
    res = json.loads(pathlib.Path("e0f2.result.json").read_text())
    rows = res["rows"]
    rats = []
    for k, (kind, m_, n_, p_) in sorted(MODEL.items(),
                                        key=lambda kv: rows[kv[0]]["exact"]):
        share = ph.radial_share(kind, m_, n_, p_, A_MM, L_MM)
        f0 = ph.f_mnp(kind, m_, n_, p_, A_MM, L_MM)
        pred = -share * (ratio_vol - 1.0) * f0 * 1e3
        meas = rows[k]["delta"].get("e0f2_o1")
        if meas is None:
            continue
        r = meas / pred if pred else float("nan")
        rats.append(r)
        print(f"    {k:>7}{pred:>11.3f}{meas:>10.3f}{r:>8.3f}")
    if rats:
        mean = sum(rats) / len(rats)
        sd = (sum((x - mean) ** 2 for x in rats) / len(rats)) ** 0.5
        print(f"\n    ratio mean {mean:.4f}  sd {sd:.4f}")
        print(f"    (was 0.736 using the h_air estimate of N)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
