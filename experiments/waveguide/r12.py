#!/usr/bin/env python3
"""R12 — how much of the +21.1 MHz plasma shift is an artefact of filling factor?

The shift that R11's whole retune is sized by came from a uniform conductivity
filling the ENTIRE plasma zone: r <= 8.5 mm, z = -20.0 .. +43.8 mm, 14,438 mm^3.
A real discharge is smaller in both directions — annular, with a cool central
channel where the sample flows, and axially concentrated rather than running the
full length.

If the shift scales with plasma VOLUME, a realistic torus at ~34% of that volume
shifts ~7 MHz and the retune is oversized by 3x. If it scales with where the
FIELD is, the outer annulus carries most of it (E_phi ~ r inside the bore, so the
outer shell is where the coupling happens) and the shift barely moves. Those two
predictions differ by enough to change the design, which is why this blocks R11.

Every mesh here is built through one helper carrying --sectors 1 (whose omission
silently killed the port in R11) and a recorded size-factor (whose silent
fallback made two R11 runs non-comparable).
"""
import json, math, pathlib, subprocess, sys, time
import dq

MM = pathlib.Path.home() / ".local/bin/micromamba"
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
BASE = json.loads(pathlib.Path("driven-tilt45.json").read_text())
SIGMA = 30.0
# The unloaded reference is solved HERE, on a mesh built by the same helper, so
# every number below shares a size-factor. Taking it from tilt45.msh would repeat
# the R11 mistake of differencing across an unknown mesh density.
UNLOADED = None

# ri, ro, zlo, zhi (mm) — the bore is r<=8.5, z -20.0..43.8
CASES = [
    ("none",    None,                    "NO plasma — matched unloaded reference"),
    ("full",    None,                    "uniform bore (the current model)"),
    ("annular", (4.5, 8.5, -20.0, 43.8), "hollow centre: cool sample channel"),
    ("short",   (0.0, 8.5, -20.0, 10.0), "axially concentrated, full radius"),
    ("toroid",  (4.5, 8.5, -20.0, 10.0), "both: the realistic shape"),
]


def mesh(tag, plasma):
    """Build through ONE helper. --sectors 1 is not optional: without it the
    port face splits and drives nothing, with no error raised."""
    extra = ["--plasma", ",".join(str(v) for v in plasma)] if plasma else []
    for fac in ("1.00", "0.96", "1.06", "0.90"):
        g = subprocess.run([str(MM), "run", "-n", "emsim", "python", "geometry.py",
                            "--out", f"{tag}.msh", "--radius", "101.43",
                            "--length", "87.67", "--brake", "3", "--sectors", "1",
                            "--order", "2", "--size-factor", fac,
                            "--loop", "12,8.5,1,0.3", "--loop-tilt", "45"] + extra,
                           capture_output=True, text=True)
        if g.returncode == 0:
            return fac
    print(f"  {tag}: MESH FAIL at every size factor"); return None


def volume(tag, attr):
    import gmsh
    gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0)
    gmsh.merge(f"{tag}.msh")
    tot = 0.0
    try:
        for e in gmsh.model.getEntitiesForPhysicalGroup(3, attr):
            for et in gmsh.model.mesh.getElementTypes(3, e):
                t, _ = gmsh.model.mesh.getElementsByType(et, e)
                tot += sum(gmsh.model.mesh.getElementQualities(list(t), "volume"))
    except Exception:
        pass
    gmsh.finalize()
    return tot * 1e9


rows = []
for tag, plasma, desc in CASES:
    if tag == "none":
        pass
    fac = mesh(tag, plasma)
    if not fac:
        continue
    attr = 12 if plasma else 1          # TAG_PLASMA when carved, else whole bore
    vol = volume(tag, attr)
    c = json.loads(json.dumps(BASE))
    c["Model"]["Mesh"] = f"{tag}.msh"
    c["Problem"]["Output"] = f"postpro/r12{tag}"
    if tag == "none":
        pass                              # no conductivity anywhere
    elif plasma:
        c["Domains"]["Materials"].append(
            {"Attributes": [12], "Permittivity": 1.0, "Permeability": 1.0,
             "Conductivity": SIGMA})
    else:
        for m in c["Domains"]["Materials"]:
            if m["Attributes"] == [1]:
                m["Conductivity"] = SIGMA
    c["Solver"]["Driven"]["Samples"] = [{"Type": "Linear", "MinFreq": 2.44,
                                         "MaxFreq": 2.50, "FreqStep": 5e-5}]
    pathlib.Path(f"r12{tag}.json").write_text(json.dumps(c, indent=2))
    t0 = time.time()
    rc = subprocess.run([PALACE, "-np", "4", f"r12{tag}.json"],
                        stdout=open(f"r12{tag}.log", "w"),
                        stderr=subprocess.STDOUT).returncode
    got = [m for m in dq.report(f"r12{tag}") if m["mode"] == "TE011"] if rc == 0 else []
    f = got[0]["f"] if got else None
    if tag == "none" and f:
        globals()["UNLOADED"] = f
    rows.append((tag, desc, fac, vol, f, got[0]["Q0"] if got else None))
    print(f"\n=== {tag} ({desc})  size-factor {fac}, {time.time()-t0:.0f}s")
    if f:
        sh = f"{(f-UNLOADED)*1000:+.1f} MHz" if UNLOADED else "reference"
        print(f"    vol {vol:,.0f} mm^3   f={f:.5f}   shift {sh}"
              f"   Q0={got[0]['Q0']:,.0f}", flush=True)
    else:
        print(f"    no resonance (rc={rc})", flush=True)

print("\n" + "=" * 78)
full = next((r for r in rows if r[0] == "full" and r[4]), None)
if not UNLOADED:
    print("no unloaded reference — cannot report shifts"); raise SystemExit
print(f"{'case':<9}{'size-f':>8}{'volume':>11}{'vol %':>7}{'f':>10}{'shift':>9}{'shift %':>9}")
for tag, desc, fac, vol, f, q in rows:
    if not f or tag == "none":
        continue
    sh = (f - UNLOADED) * 1000
    vp = vol / full[3] * 100 if full and full[3] else float("nan")
    sp = sh / ((full[4] - UNLOADED) * 1000) * 100 if full else float("nan")
    print(f"{tag:<9}{fac:>8}{vol:>10,.0f}{vp:>7.0f}%{f:>10.5f}{sh:>+8.1f}M{sp:>8.0f}%")
print("""
Read: if shift % tracks vol %, the shift is a volume effect and the R11 retune is
oversized. If shift % stays high while vol % falls, the outer annulus dominates
because that is where E_phi lives, and the retune target survives.""")
