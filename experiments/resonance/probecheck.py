"""Do Palace point probes work, and do they read the field INSIDE a lossy plasma?

🔴 WHY ASK RATHER THAN ASSUME. The sustaining question needs E/N inside the
plasma. Stored energy CANNOT give it there: electric energy is ~ eps|E|^2, and
eps_eff is NEGATIVE in the metal-like regime, so the energy goes negative
(measured: p_elec = -3e-5). Probes are the only route to a field value in that
regime — IF they work.

⚠️ And a flag doing what it says has a poor record in this project:
`--tag-groove` defaulted OFF through two rigs, `--no-torch` leaves the torch
REGION in place, and the lumped port meshed with 2 elements for the whole life
of the driven programme. So: one cheap solve, look at what actually appears.

## The geometry is chosen so the answer is KNOWN in advance

TE011's E_phi ~ J1(chi'01 r/a) * sin(pi(z+L/2)/L):
  * EXACTLY ZERO on the axis
  * grows LINEARLY away from it
  * peaks at r = 0.4805a = 42.3 mm
  * zero again at the wall (J1(chi'01) = 0)

Probes on the +x axis at the mid-plane read E_phi as their **y** component.

Plasma: R = 4 mm at ne = 1e20, so delta = 1.80 mm and PI_2 = 2.2 — past the
penetration transition, so the field SHOULD decay measurably from the plasma
surface inward. That is the effect the whole sweep depends on being able to see.

VERIFICATION
  V1  a probe file must appear at all, with one row per probe
  V2  |E| near the axis must be ~0 and rise with r — TE011's own shape. If it
      does not, the probe is not reading the field we think it is.
  V3  |E| must PEAK near r = 42.3 mm (vacuum, outside the plasma) — a known
      landmark that needs no plasma physics to predict
FALSIFICATION
  🔴 F1  if probes inside the plasma return the same value as their vacuum
         neighbours, they are interpolating across the boundary and are USELESS
         for this measurement
  🔴 F2  if |E| does not decay from the plasma surface inward at PI_2 = 2.2,
         either the probe or the shielding physics is not what is assumed —
         and the sweep cannot be built on it either way
"""
import json
import math
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import solveconf
from e0_solver_vs_math import GEO, eigen_cfg, run, volume_attrs
from e0k2_anchor import design_point, wall_sigma
from h3_loaded import drude, SECTORS, Z_FRAC, INNER_R, PLASMA_H, EIGEN_TARGET

TAG = "probecheck"
R_MM = 4.0
NE = 1.0e20          # metal-like and solvable: PI_1 = 5.58
N_MODES = 4
# radii in mm: inside the 4 mm plasma, then vacuum, then the known field peak
PROBE_R = [0.1, 0.5, 1.0, 2.0, 3.0, 3.9, 5.0, 8.0, 15.0, 42.3, 80.0]


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma_w = wall_sigma()
    w = 2.0 * math.pi * 2.45e9
    eps, sig = drude(NE, w)
    delta = math.sqrt(2.0 / (w * 4e-7 * math.pi * sig)) * 1e3
    print(f"  plasma R={R_MM} mm, ne={NE:.0e}: eps={eps:.2f}, sigma={sig:.2f} S/m")
    print(f"  skin depth {delta:.2f} mm  ->  PI_2 = R/delta = {R_MM/delta:.2f}")
    print(f"  field peak (vacuum) at 0.4805a = {0.4805*a:.1f} mm\n", flush=True)

    zlo, zhi = -Z_FRAC * L, Z_FRAC * L
    args = (list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                         "--sectors", str(SECTORS),
                         "--plasma", f"{INNER_R},{R_MM},{zlo:.4f},{zhi:.4f}",
                         "--plasma-h", f"{PLASMA_H:.3f}"])
    r = subprocess.run([sys.executable, "geometry.py", "--out", f"{TAG}.msh",
                        "--size-factor", "1.5"] + args,
                       capture_output=True, text=True)
    if r.returncode or not pathlib.Path(f"{TAG}.msh").exists():
        sys.exit(f"🔴 mesh failed: {(r.stdout + r.stderr)[-300:]}")
    m = solveconf.load_meta(f"{TAG}.msh")
    attrs = m["attributes"]
    print(f"  {m['tets']:,} tets, plasma attr {attrs.get('plasma')}", flush=True)

    # 🔴 was a local copy of the surface/volume rule. A `loop`
    # SURFACE got classified as a VOLUME (2026-08-27) and
    # Palace refused the config. One definition now.
    vols = volume_attrs(m)
    c = eigen_cfg(TAG, m, mesh=f"{TAG}.msh", sigma=sigma_w, n=N_MODES,
                  target=EIGEN_TARGET)
    c["Solver"]["Order"] = 2
    others = sorted(set(vols) - {attrs["plasma"]})
    c["Domains"]["Materials"] = [
        {"Attributes": others, "Permittivity": 1.0, "Permeability": 1.0},
        {"Attributes": [attrs["plasma"]], "Permittivity": eps,
         "Permeability": 1.0, "Conductivity": sig}]
    # 🔑 probes on the +x axis at the MID-PLANE (z=0), where TE011's E_phi peaks
    # in z. Center is in METRES, matching the mesh (Model.L0 = 1.0).
    c["Domains"]["Postprocessing"]["Probe"] = [
        {"Index": i + 1, "Center": [rr * 1e-3, 0.0, 0.0]}
        for i, rr in enumerate(PROBE_R)]
    print(f"  {len(PROBE_R)} probes on the +x axis at z=0: "
          f"{PROBE_R} mm\n", flush=True)

    before = set(p.name for p in (pathlib.Path("postpro") / TAG).glob("*")) \
        if (pathlib.Path("postpro") / TAG).is_dir() else set()
    run(TAG, c, allow_lossy_eigen=True, timeout=900.0)
    after = set(p.name for p in (pathlib.Path("postpro") / TAG).glob("*"))

    print(f"\n  files in postpro/{TAG}/:")
    for f in sorted(after):
        n = len((pathlib.Path("postpro") / TAG / f).read_text(
            errors="ignore").splitlines())
        mark = "   <-- NEW" if f not in before else ""
        print(f"    {f:<28}{n:>6} lines{mark}")
    probe_files = [f for f in after if "probe" in f.lower()]
    print(f"\n  V1 probe file present: "
          + (f"✅ {probe_files}" if probe_files else "🔴 NONE — probes produced nothing"))
    if not probe_files:
        return
    pf = pathlib.Path("postpro") / TAG / probe_files[0]
    txt = pf.read_text().splitlines()
    print(f"\n  header: {txt[0][:200]}")
    for line in txt[1:3]:
        print(f"  row:    {line[:200]}")


if __name__ == "__main__":
    main()
