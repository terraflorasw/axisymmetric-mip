#!/usr/bin/env python3
"""R36b — the CONTROL that r36 needed: a sham-oval reference.

r36 found TE011 sitting ~2 MHz below the round case at EVERY ovality tested
(-2.08, -1.72, -2.18 MHz at +/-0.05, 0.10, 0.20 mm). Flat in delta is not
physics: any real perturbation of an m=0 mode must vanish as delta -> 0, and a
second-order effect would scale as delta^2, i.e. 16x between 0.05 and 0.20 mm.
It does not.

What differs between the round case and every oval case is not mesh density --
they are within 0.3% on element count -- but the SURFACE REPRESENTATION. The
round bore is an analytic OCC cylinder; an ovalised bore is a GTransform'd
surface, and the order-2 curved elements laid on it discretise slightly
differently. That is a constant offset, present at any nonzero delta.

So the round case is the wrong control. This run uses a SHAM OVAL instead:

    c001   delta = 0.01 mm    physically round to 1e-4 of the radius, but
                              carrying the identical BSpline representation
    c020   delta = 0.20 mm    the tolerance actually under consideration
    c040   delta = 0.40 mm    2x beyond it -- 4x the delta^2 effect, so if
                              anything real is happening this is where it shows

Differences WITHIN this set are physics, because the representation is common
to all three. All three are built in ONE meshsweep call, so the size-factor is
common too (R27).

Prediction stands from r36: c001 -> c020 -> c040 flat to well under 1 MHz. If
c040 moves and c020 does not, the effect is real and quadratic and the
tolerance is a genuine constraint that must go on the drawing.
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
CASES = [("c001", "0.01"), ("c020", "0.20"), ("c040", "0.40")]


def solve(tag):
    c = json.loads(json.dumps(BASE))
    c["Model"]["Mesh"] = f"{tag}.msh"
    c["Problem"]["Output"] = f"postpro/{tag}"
    c["Solver"]["Driven"]["Samples"] = [{"Type": "Linear", "MinFreq": 2.34,
                                         "MaxFreq": 2.48, "FreqStep": 2e-5}]
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
    return dq.report(tag)


print(__doc__)
print("=" * 78, flush=True)

fac, ok = meshsweep.sweep([(t, ["--ovality", ov]) for t, ov in CASES],
                          BASE_ARGS)
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")

res = {}
for tag, ov in CASES:
    print(f"\n=== ovality +/-{ov} mm", flush=True)
    res[tag] = solve(tag)
    for m in res[tag]:
        print(f"    {m['mode']:>6}  f={m['f']:.5f}  Q0={m['Q0']:>9,.0f}  "
              f"boreE={m['pe']*100:6.3f}%  boreH={m['pm']*100:6.3f}%", flush=True)

print("\n" + "=" * 78)
ref = {m["mode"]: m for m in res.get("c001", [])}
print(f"{'ovality':>9}{'mode':>8}{'f (GHz)':>11}{'df vs sham':>12}"
      f"{'Q0':>10}{'dQ %':>8}{'boreH %':>9}")
for tag, ov in CASES:
    for m in res[tag]:
        b = ref.get(m["mode"])
        df = f"{(m['f']-b['f'])*1000:+.2f}" if b else "--"
        dqp = f"{100*(m['Q0']/b['Q0']-1):+.2f}" if b and m["Q0"] and b["Q0"] else "--"
        print(f"{ov:>9}{m['mode']:>8}{m['f']:>11.5f}{df:>12}"
              f"{m['Q0']:>10,.0f}{dqp:>8}{m['pm']*100:>9.3f}")
print("""
Read against the SHAM, not against round. Flat here => ovality is negligible on
both operating modes out to twice the tolerance, and the roundness callout is
free. Quadratic growth => it is real, and c040 sets the scale.""", flush=True)
