"""E0k2-bare — TE011's Q with NO coupling loop, so the probe's cost is measurable.

🔴 WHY. E0k2 measured Q0 ~ 29,000 for the cavity WITH an 11x8 mm cap loop, and
two independent routes (driven linewidth, eigenvalue) agreed on it to 5.4%. But
the bare-cavity TE011 Q0 in the record is 44,384 — so the loop appears to cost
~32% of Q while shifting the frequency only 0.40 MHz.

🔑 THAT IS NOT A CONTRADICTION, IT IS A DISTINCTION NOBODY HAD MEASURED.
Frequency is a VOLUME integral; Q is a SURFACE-CURRENT integral. An obstacle at
a current maximum can be negligible in the first and dominant in the second. The
cap loop sits at r = 0.4805a, exactly where TE011's H_r — and therefore its cap
current — peaks. V3 tested the frequency perturbation and passing it said
NOTHING about the quantity being anchored.

⚠️ The loop is PEC in the eigenmode solve, so whatever it costs is NOT its own
conductor loss. It is the loop distorting the mode and crowding current onto the
finite-conductivity wall beside it.

This rig removes the loop and changes nothing else: same geometry flags, same
wall from baselines.json, same solver order, same window. The difference IS the
probe's cost.

VERIFICATION
  V1  TE011 must be identified by Q, not by frequency. Without a loop the
      cavity is axisymmetric and TE011/TM111 are EXACTLY degenerate, so
      frequency cannot separate them and Q is the only discriminator that works.
  V2  TE011 Q must EXCEED TM111 Q (H1's falsifier), and the TM111 pair's two
      polarisations must have near-equal Q — they are one mode in two
      orientations.
  V3  TE011 must land within a few hundred kHz of 2.45 GHz. This geometry is
      constructed to put it there, so a miss means the mesh or the flags, not
      the physics.

FALSIFICATION
  🔴 F1  if bare Q0 comes back near 29,000 rather than ~44,000, the loop is NOT
         what depressed it and the 44,384 in the record is wrong for this
         geometry. Either way the anchor's interpretation changes, and this
         number is the one that decides which.
  🔴 F2  if TE011 Q < TM111 Q the identification is inverted and NO Q is
         reported — the same guard that fired on the cap-loop solve.
"""
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import eigmodes
import solveconf
from e0_solver_vs_math import GEO, eigen_cfg, run
from e0k2_anchor import design_point, wall_sigma, shared_energy_list, N_MODES

TAG = "e0k2_bare"


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma = wall_sigma()
    print(f"  design point (H1, DERIVED): a={a:.4f} mm  L={L:.4f} mm")
    print(f"  wall: {sigma:.3g} S/m from baselines.json")
    print(f"  NO loop, NO groove — the only difference from e0k2\n", flush=True)

    geo = list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}"]
    r = subprocess.run([sys.executable, "geometry.py", "--out", f"{TAG}.msh",
                        "--size-factor", "1.5"] + geo,
                       capture_output=True, text=True)
    if r.returncode or not pathlib.Path(f"{TAG}.msh").exists():
        sys.exit(f"mesh failed: {(r.stdout + r.stderr)[-300:]}")
    m = solveconf.load_meta(f"{TAG}.msh")
    attrs = m["attributes"]
    print(f"  {m['tets']:,} tets, {m.get('sectors')} sector(s), "
          f"port attr {attrs.get('port')} (expect None — no loop)", flush=True)

    EX = ph.spectrum(a, L, fmax=3.2)
    exact = EX["TE011"]
    fmin = exact - 0.20
    c = eigen_cfg(TAG, m, mesh=f"{TAG}.msh", sigma=sigma, n=N_MODES, target=fmin)
    c["Solver"]["Order"] = 2
    c["Domains"]["Postprocessing"]["Energy"] = shared_energy_list(m)
    # 🔴 no loop means no port attribute to short. Asserting it rather than
    # silently skipping: a port here would mean the mesh is not what we asked for.
    if attrs.get("port") is not None:
        raise RuntimeError(f"{TAG}: mesh has port attribute {attrs['port']} — "
                           f"a loop got built. This rig measures the BARE cavity.")
    for mat in c["Domains"]["Materials"]:
        for k, want in (("Permittivity", 1.0), ("LossTan", 0.0),
                        ("Conductivity", 0.0)):
            if k in mat and mat[k] != want:
                print(f"    🔧 {mat.get('Attributes')}: {k} {mat[k]} -> {want}")
                mat[k] = want
    run(TAG, c)

    modes = eigmodes.read(TAG)
    qs = {}
    for line in (pathlib.Path("postpro") / TAG / "eig.csv").read_text().splitlines()[1:]:
        p_ = line.split(",")
        if len(p_) > 3:
            qs[round(float(p_[0]))] = float(p_[3])
    print(f"\n  {len(modes)} modes:", flush=True)
    for md in modes:
        print(f"    f={md['f']:.6f}  Q={qs.get(md['m'], 0):,.0f}", flush=True)

    fs = [md["f"] for md in modes]
    ql = [qs.get(md["m"], 0.0) for md in modes]
    pair = eigmodes.te011_tm111(fs, exact, ql, fmin=fmin)
    out = {"a_mm": a, "L_mm": L, "sigma": sigma, "tets": m["tets"],
           "exact_te011": exact,
           "modes": [{"f": md["f"], "Q": qs.get(md["m"])} for md in modes]}
    if not pair:
        print("\n  🔴 te011_tm111 REFUSED — no Q reported.")
        json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
        return

    q_te = ql[pair["te011_index"]]
    q_tm = sum(ql[i] for i in pair["tm111_indices"]) / 2.0
    print(f"\n  TE011 = {pair['te011']:.6f} GHz   Q = {q_te:,.0f}   "
          f"(how={pair['how']})")
    print(f"  TM111 = {pair['tm111']:.6f} GHz   Q = {q_tm:,.0f}")
    print(f"  degeneracy split {pair['splitting_mhz']:.4f} MHz "
          f"(closed form: EXACTLY 0)")
    print(f"  pair polarisation split {pair['tm111_pair_mhz']:.4f} MHz")

    print(f"\n  DECLARED CRITERIA")
    v2 = q_te > q_tm
    print(f"    V2 TE011 Q > TM111 Q: {q_te:,.0f} vs {q_tm:,.0f} "
          + ("✅" if v2 else "🔴 F2 FIRES — inverted, no Q reported"))
    print(f"       q_margin {pair['q_margin']:.3f}  "
          f"pair_q_ratio {pair['pair_q_ratio']:.3f} (want ~1: one mode, two "
          f"orientations)")
    v3 = abs(1e3 * (pair["te011"] - exact))
    print(f"    V3 TE011 within {v3:.3f} MHz of {exact:.5f} "
          + ("✅" if v3 < 0.5 else "🔴 check the mesh and the flags"))
    if not v2:
        json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
        return
    out.update(q_te011=q_te, q_tm111=q_tm, f_te011=pair["te011"],
               q_margin=pair["q_margin"])

    print(f"\n  {'='*70}")
    print(f"  BARE TE011 Q0 = {q_te:,.0f}")
    print(f"    record (INSTRUMENT, this geometry) : 44,384")
    print(f"    with the 11x8 cap loop (e0k2)      : 30,020")
    print(f"    -> the loop costs {100*(1-30020.0/q_te):+.1f}% of Q")
    print(f"       F1: if that is small, the loop is NOT what depressed Q and")
    print(f"       the 44,384 in the record does not describe this geometry.")
    json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
    print(f"\n  wrote {TAG}.result.json", flush=True)


if __name__ == "__main__":
    main()
