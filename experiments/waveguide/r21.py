#!/usr/bin/env python3
"""R21 — capacitive ignition electrode: what does the band cost TE011?

A conducting band around the torch OD is a SHORTED TURN to TE011's azimuthal E.
Analytically it sees 31.9% of peak E_phi at mid-plane and 5.7% at 5 mm from an
end cap, so position should decide between harmless and fatal. This measures it
the same way R6 measured the viewport: add the feature, sweep, read dQ and df.

Baseline is a NO-ELECTRODE run built by this same helper, so every comparison
shares a size-factor. Both of yesterday's comparability failures — the missing
--sectors 1 that silently killed the port, and the silent size-factor fallback
that made two runs non-differenceable — are handled here rather than trusted to
memory.
"""
import json, pathlib, subprocess, sys, time
import dq

MM = pathlib.Path.home() / ".local/bin/micromamba"
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
BASE = json.loads(pathlib.Path("driven-tilt45.json").read_text())

Z0 = 43.8 - 87.67          # upstream end cap
CASES = [
    ("elnone", None,             "no electrode — matched baseline"),
    ("el05",   (Z0 + 5,  5, 1),  "5 mm from upstream end cap"),
    ("el10",   (Z0 + 10, 5, 1),  "10 mm from end cap"),
    ("el20",   (Z0 + 20, 5, 1),  "20 mm from end cap"),
    ("elmid",  (0.0,     5, 1),  "mid-plane — the worst case"),
]


def mesh(tag, el):
    # "=" form is REQUIRED: a bare "--electrode -33.87,..." has argparse read the
    # leading minus as an option flag. Every negative-z case failed on this and
    # was reported as a mesh failure.
    extra = ["--electrode=" + ",".join(str(v) for v in el)] if el else []
    for fac in ("1.00", "0.96", "1.06", "0.90", "0.85"):
        g = subprocess.run([str(MM), "run", "-n", "emsim", "python", "geometry.py",
                            "--out", f"{tag}.msh", "--radius", "101.43",
                            "--length", "87.67", "--brake", "3", "--sectors", "1",
                            "--order", "2", "--size-factor", fac,
                            "--loop", "12,8.5,1,0.3", "--loop-tilt", "45"] + extra,
                           capture_output=True, text=True)
        if g.returncode == 0:
            return fac
    # Never report a generic failure while holding the actual message: that is
    # what turned an argparse error into a phantom meshing problem.
    print(f"  {tag}: MESH FAIL at every size factor. Last stderr:")
    for line in (g.stderr or g.stdout or "").strip().splitlines()[-6:]:
        print(f"      {line}")
    return None


rows = []
for tag, el, desc in CASES:
    fac = mesh(tag, el)
    if not fac:
        continue
    c = json.loads(json.dumps(BASE))
    c["Model"]["Mesh"] = f"{tag}.msh"
    c["Problem"]["Output"] = f"postpro/{tag}"
    c["Solver"]["Driven"]["Samples"] = [{"Type": "Linear", "MinFreq": 2.36,
                                         "MaxFreq": 2.56, "FreqStep": 5e-5}]
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    t0 = time.time()
    rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"],
                        stdout=open(f"{tag}.log", "w"),
                        stderr=subprocess.STDOUT).returncode
    got = {m["mode"]: m for m in dq.report(tag)} if rc == 0 else {}
    te, tm = got.get("TE011"), got.get("TM020")
    rows.append((tag, desc, fac, te, tm))
    print(f"\n=== {tag} ({desc})  size-factor {fac}, {time.time()-t0:.0f}s", flush=True)
    for n, m in (("TE011", te), ("TM020", tm)):
        print(f"    {n}: " + (f"f={m['f']:.5f}  Q0={m['Q0']:,.0f}" if m else "not found"),
              flush=True)

print("\n" + "=" * 76)
base = next((r for r in rows if r[0] == "elnone"), None)
if not base or not base[3]:
    print("no baseline — cannot report deltas"); raise SystemExit
bte = base[3]
print(f"{'case':<8}{'size-f':>8}{'TE011 f':>10}{'df':>9}{'TE011 Q0':>11}{'dQ':>9}")
for tag, desc, fac, te, tm in rows:
    if not te:
        print(f"{tag:<8}{fac:>8}   TE011 not found"); continue
    print(f"{tag:<8}{fac:>8}{te['f']:>10.5f}{(te['f']-bte['f'])*1000:>+8.1f}M"
          f"{te['Q0']:>11,.0f}{(te['Q0']/bte['Q0']-1)*100:>+8.1f}%")
print("""
Predicted from E_phi ~ J1(chi r/a) sin(pi z/L): the band sees 5.7% of peak at
5 mm, 11.2% at 10 mm, and 31.9% at mid-plane. If dQ tracks that ordering the
short is real and placement fixes it; if even mid-plane is cheap, the band is
not the problem the analysis suggests and it can go anywhere convenient.""")
