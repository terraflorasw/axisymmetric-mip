#!/usr/bin/env python3
"""R38b — is ORDER 2 itself converged? The check r38 could not build.

r38 measured the order-1 → order-2 offset at the design point as +24.54 MHz on
TE011, against the +31.6 MHz the whole file has been applying. That correction
only means anything if order 2 is the converged answer. r38's convergence probe
never ran: the 0.85 mesh would not curve.

This retries the probe across several densities and solves the first one that
builds. Two independent knobs, because they fail independently:

    size-factor   scales every mesh size (0.90, 0.93, 0.80)
    --n-wl        elements per wavelength, 8 by default -> 10

A pass means the finer solve lands within ~1 MHz of order 2 at 0.96, order 2 is
resolved, and +24.54 is a real correction to a fixed target. A fail means the
offset is extrapolating to something still moving, and it needs a Richardson
treatment over at least three densities rather than a single number — which is
exactly the criticism the ORIGINAL +31.6 never had to answer.
"""
import json, os, pathlib, subprocess, sys, time

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
BASE_ARGS = ["--radius", A, "--length", L, "--brake", "3", "--sectors", "1",
             "--order", "2", "--loop", "12,8.5,1,0.3", "--loop-tilt", "45"]
BAND = (2.35, 2.49)
# r38's order-2 result on choff.msh (size-factor 0.96), the target to land on
O2_COARSE = {"TE011": 2.44146, "TM020": 2.39552}
# (label, extra args, size-factor)
PROBES = [("f090", [], "0.90"),
          ("f093", [], "0.93"),
          ("f080", [], "0.80"),
          ("nwl10", ["--n-wl", "10"], "1.00"),
          ("nwl10b", ["--n-wl", "10"], "0.96")]


def solve(tag, mesh):
    c = json.loads(json.dumps(BASE))
    c["Model"]["Mesh"] = mesh
    c["Problem"]["Output"] = f"postpro/{tag}"
    c["Solver"]["Order"] = 2
    c["Solver"]["Driven"]["Samples"] = [{"Type": "Linear", "MinFreq": BAND[0],
                                         "MaxFreq": BAND[1], "FreqStep": 2e-5}]
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
            return []
    out = dq.report(tag)
    for m in out:
        print(f"     {m['mode']:>6}  f={m['f']:.5f}  Q0={m['Q0']:>9,.0f}  "
              f"boreE={m['pe']*100:6.3f}%  boreH={m['pm']*100:6.3f}%", flush=True)
    return out


print(__doc__)
print("=" * 78, flush=True)

built = None
for tag, extra, fac in PROBES:
    g = meshsweep.build(tag, BASE_ARGS, extra, fac)
    if g.returncode == 0:
        print(f"  ✅ {tag} built (size-factor {fac}"
              + (f", {' '.join(extra)}" if extra else "") + ")", flush=True)
        built = (tag, extra, fac)
        break
    print(f"  {tag} failed at size-factor {fac}"
          + (f" with {' '.join(extra)}" if extra else ""), flush=True)
    for line in (g.stderr or g.stdout or "").strip().splitlines()[-2:]:
        print(f"      {line}", flush=True)

if not built:
    sys.exit("no finer mesh will curve — order 2 stays unverified against mesh "
             "density, and that limitation must stay on the R38 result")

tag, extra, fac = built
print(f"\n=== order 2 on the finer mesh ({tag})", flush=True)
fine = {m["mode"]: m for m in solve(f"r38{tag}", f"{tag}.msh")}

print("\n" + "=" * 78)
print(f"{'mode':>7}{'o2 @0.96':>11}{'o2 finer':>11}{'drift':>9}")
ok = True
for mode in ("TE011", "TM020"):
    if mode not in fine:
        print(f"{mode:>7}   missing from the finer solve")
        ok = False
        continue
    d = (fine[mode]["f"] - O2_COARSE[mode]) * 1000
    ok &= abs(d) < 1.0
    print(f"{mode:>7}{O2_COARSE[mode]:>11.5f}{fine[mode]['f']:>11.5f}{d:>+9.2f}")
print()
if ok:
    print("✅ ORDER 2 IS CONVERGED — both modes within 1 MHz across mesh "
          "densities. The +24.54 MHz TE011 offset is a correction to a fixed\n"
          "   target, and supersedes +31.6.")
else:
    print("🔴 ORDER 2 IS NOT CONVERGED at this density. A single offset number "
          "is the wrong instrument; this needs Richardson extrapolation over\n"
          "   three densities. Note the ORIGINAL +31.6 was never held to this "
          "standard either.")
print(flush=True)
