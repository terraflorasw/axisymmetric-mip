#!/usr/bin/env python3
"""R15 — is the plasma-loaded Q converged, or is it a mesh artefact?

R10 already showed the plasma-induced *frequency shift* is robust (+21.11 vs
+21.10 MHz across solver orders). What was never checked is the loaded **Q**,
which collapses to 138-321 and is what sets the amplifier's tracking and
impedance spec. Q is the quantity that depends on resolving the field INSIDE the
conductor, and that is exactly what a coarse mesh cannot do.

🔢 The length that has to be resolved is the RF skin depth in the plasma:

    delta = sqrt(2/(omega mu sigma)) = 1.86 mm at sigma = 30 S/m, 2.45 GHz

and the R12 sub-region was being meshed at 1.5 mm near the quartz wall growing
to 15 mm in the interior — roughly ONE element per skin depth at best.

⚠️ A BUG FOUND WHILE SETTING THIS UP. The first attempt prescribed the plasma
mesh size through `set_pts`, the same helper the bore uses. It changed the mesh
by 795 tets where ~29,000 were expected: this model runs with
Mesh.MeshSizeExtendFromBoundary = 0, so a size prescribed at boundary POINTS
never propagates into the volume interior. Silently ignored, and it would have
produced four "different" densities that were all the same mesh — a null result
with nothing behind it. geometry.py now refines the region with a Cylinder FIELD
combined by Min against the torch-wall threshold.

🔴 A SECOND SILENT CLAMP, found by checking element counts after the first run.
Mesh.MeshSizeMin was h_qtz*0.8 = 1.2 mm, and gmsh clamps EVERY requested size to
that floor — including one asked for by a field. So the 1.0 mm and 0.6 mm cases
both came back as the same 1.2 mm mesh: 14,703 vs 14,586 tets in the plasma. The
run reported "39.5% apart, NOT CONVERGED" while comparing a mesh against itself.

That first run is not wasted, though. Two meshes differing by 0.8% in element
count returned Q = 149 and Q = 208. **Loaded Q is unstable at the ~40% level
against a trivial mesh change**, which is a noise floor this study has to clear
before any convergence claim means anything.

Densities now actually achievable, loaded only. The unloaded reference is not
re-solved: R10 settled the shift, and the question here is Q.

    1.2     0.6 per skin depth — the floor the previous run was stuck at
    0.8     2.3 per skin depth
    0.6     3.1 per skin depth, R15's stated target

⚠️ The verdict is sigma-specific. delta scales as 1/sqrt(sigma), so a denser
plasma needs a finer mesh than whatever passes here.
"""
import json, math, os, pathlib, subprocess, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
import meshsweep

PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
HOME = pathlib.Path.home()
ENV = {**os.environ,
       "PATH": f"{HOME}/.local/share/mamba/envs/emsim/bin:{os.environ['PATH']}",
       "MAMBA_ROOT_PREFIX": str(HOME / ".local/share/mamba")}
BASE = json.loads(pathlib.Path("w890.json").read_text())

A, L = "103.70", "88.53"
SIGMA = 30.0
PLASMA = "4.5,8.5,-20.0,10.0"        # R12's realistic toroid
BASE_ARGS = ["--radius", A, "--length", L, "--brake", "3", "--sectors", "1",
             "--order", "2", "--loop", "12,8.5,1,0.3", "--loop-tilt", "45",
             "--plasma", PLASMA]
CASES = [("p_12", ["--plasma-h", "1.2"]), ("p_08", ["--plasma-h", "0.8"]),
         ("p_06", ["--plasma-h", "0.6"])]
LABEL = {"p_12": "1.2 mm", "p_08": "0.8 mm", "p_06": "0.6 mm"}
BAND = (2.36, 2.50)
DELTA = math.sqrt(2 / (2 * math.pi * 2.45e9 * 4e-7 * math.pi * SIGMA)) * 1e3


def solve(tag):
    c = json.loads(json.dumps(BASE))
    c["Model"]["Mesh"] = f"{tag}.msh"
    c["Problem"]["Output"] = f"postpro/{tag}"
    c["Domains"]["Materials"].append(
        {"Attributes": [12], "Permittivity": 1.0, "Permeability": 1.0,
         "Conductivity": SIGMA})
    c["Solver"]["Driven"]["Samples"] = [{"Type": "Linear", "MinFreq": BAND[0],
                                         "MaxFreq": BAND[1], "FreqStep": 5e-5}]
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    t0 = time.time()
    rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"], env=ENV,
                        stdout=open(f"{tag}_p.log", "w"),
                        stderr=subprocess.STDOUT).returncode
    dt = time.time() - t0
    print(f"  {tag}: rc={rc} in {dt:.0f}s", flush=True)
    if rc != 0 or dt < 30:
        tail = pathlib.Path(f"{tag}_p.log").read_text().strip().splitlines()
        print(f"    🔴 {tag} DID NOT SOLVE — {tail[-1] if tail else '(empty)'}",
              flush=True)
        if rc != 0:
            return None
    # A loaded resonance is broad and low-contrast, and dq.identify's thresholds
    # were calibrated on UNLOADED modes — so take the largest stored-energy peak
    # and print its signature rather than trusting the label.
    recs = dq.load(tag)
    if not recs:
        return None
    idx = dq.peaks(recs, rel=0.05, sep=0.002)
    if not idx:
        print("    ⚠️ no peak found in band — loaded resonance may be broader "
              "than the window or below the contrast guard", flush=True)
        return None
    best = max((recs[i] for i in idx), key=lambda r: r["U"])
    for i in idx:
        r = recs[i]
        mark = " <-" if r is best else ""
        print(f"     f={r['f']:.5f}  Q0={r['Q0']:>8,.0f}  boreE={r['pe']*100:6.3f}%"
              f"  boreH={r['pm']*100:6.3f}%  {dq.identify(r):>5}{mark}", flush=True)
    return best


print(__doc__)
print(f"skin depth at sigma={SIGMA}: {DELTA:.2f} mm")
print("=" * 78, flush=True)

fac, _ = meshsweep.sweep(CASES, BASE_ARGS,
                         factors=("0.96", "1.00", "0.93", "0.90", "1.06"))
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")

res = {}
for tag, _e in CASES:
    print(f"\n=== plasma mesh {LABEL[tag]}"
          + f"  ({DELTA/float(LABEL[tag].split()[0]):.1f} elements per skin depth)",
          flush=True)
    res[tag] = solve(tag)

print("\n" + "=" * 78)
print(f"{'plasma mesh':>13}{'f (GHz)':>10}{'Q0':>9}{'ΔQ vs finest':>14}"
      f"{'boreE %':>9}{'boreH %':>9}")
fine = res.get("p_06")
for tag, _e in CASES:
    m = res[tag]
    if not m:
        print(f"{LABEL[tag]:>13}   no usable peak")
        continue
    d = f"{100*(m['Q0']/fine['Q0']-1):+.1f}%" if fine and fine["Q0"] else "--"
    print(f"{LABEL[tag]:>13}{m['f']:>10.5f}{m['Q0']:>9,.0f}{d:>14}"
          f"{m['pe']*100:>9.3f}{m['pm']*100:>9.3f}")

qs = [(LABEL[t], res[t]["Q0"]) for t, _e in CASES if res[t] and res[t]["Q0"]]
if len(qs) >= 2:
    last2 = abs(qs[-1][1] / qs[-2][1] - 1) * 100
    print(f"\nfinest two densities differ by {last2:.1f}% in Q")
    if last2 < 5:
        print("  ✅ CONVERGED — loaded Q is a physical number at this sigma, and "
              "the amplifier spec derived from it stands")
    else:
        print("  🔴 NOT CONVERGED — loaded Q is still moving with mesh density. "
              "Every quantitative plasma-loading claim, including the impedance "
              "collapse the control loop is specified against, is unresolved.")
    print("  ⚠️ prior run measured Q = 149 and 208 on two meshes that were "
          "IDENTICAL in density (both clamped to 1.2 mm) — treat anything under "
          "~40% as indistinguishable from extraction noise on a broad peak.")
print(flush=True)
