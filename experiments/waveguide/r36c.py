#!/usr/bin/env python3
"""R36c — AMPLIFICATION LADDER: force the ovality effect above the noise floor.

r36 and r36b both look for an effect at the tolerance itself (0.05-0.40 mm),
where perturbation theory says it is second order in delta and therefore tiny.
Measuring "nothing" there bounds the effect only as well as the mesh noise
floor, which is ~0.5 MHz.

This instead drives ovality FAR past anything a machine shop would produce --
+/-1, 2 and 4 mm on a 103.70 mm radius -- to make the effect big enough to
measure, and then measures its EXPONENT. That is the number that licenses
extrapolation back down:

    if  df ~ delta^2  over 1 -> 4 mm (a 16x span), then a value measured at
    4 mm divides by 400 to reach +/-0.20 mm, and by 1600 to reach +/-0.10 mm.

+/-4 mm is also a real-world case in its own right, not just an amplifier: it
is roughly what a hand-finished bore -- a skilled operator with a Dremel and a
guide -- would hold. If TE011 survives that, a crude prototype body is viable
and the tolerance never needs to be tight.

⚠️ THE EXPONENT IS THE POINT, NOT THE MAGNITUDE. At 4 mm the perturbation is
3.9% of the radius and no longer small. If ovality mixes TE011 with an m=2 mode
that happens to lie nearby, the response stops being quadratic and an
extrapolation from it would be worthless. A fitted slope of ~2.0 says the
mechanism is still second-order and the extrapolation holds; anything else says
read the ladder as a direct measurement only, and do not extrapolate.

The sham (+/-0.01 mm) is repeated HERE so the whole ladder shares one mesh
representation and one size-factor. Comparing across sweeps is what R11 did
wrong.
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
BASE_ARGS = ["--radius", A, "--length", L, "--brake", "3", "--sectors", "1",
             "--order", "2", "--loop", "12,8.5,1,0.3", "--loop-tilt", "45"]
CASES = [("d001", "0.01"), ("d100", "1.0"), ("d200", "2.0"), ("d400", "4.0")]

# The band is widened well below the r36 window: at 4 mm the modes may move
# tens of MHz, and a mode that walks out of the window reads as "no peak",
# which is indistinguishable from a solver that never ran.
BAND = (2.28, 2.50)


def solve(tag):
    c = json.loads(json.dumps(BASE))
    c["Model"]["Mesh"] = f"{tag}.msh"
    c["Problem"]["Output"] = f"postpro/{tag}"
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
    return dq.report(tag)


print(__doc__)
print("=" * 78, flush=True)

fac, ok = meshsweep.sweep([(t, ["--ovality", ov]) for t, ov in CASES],
                          BASE_ARGS)
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")

res = {}
for tag, ov in CASES:
    ov_f = float(ov)
    print(f"\n=== ovality +/-{ov} mm  (semi-axes {float(A)+ov_f:.2f} / "
          f"{float(A)-ov_f:.2f}, {100*ov_f/float(A):.2f}% of radius)", flush=True)
    res[tag] = solve(tag)
    for m in res[tag]:
        print(f"    {m['mode']:>6}  f={m['f']:.5f}  Q0={m['Q0']:>9,.0f}  "
              f"boreE={m['pe']*100:6.3f}%  boreH={m['pm']*100:6.3f}%", flush=True)
    if len(res[tag]) != len(res[CASES[0][0]]):
        print(f"    ⚠️  peak COUNT changed vs the sham ({len(res[CASES[0][0]])}"
              f" -> {len(res[tag])}) — a mode has moved, split, or left the band",
              flush=True)

print("\n" + "=" * 78)
ref = {m["mode"]: m for m in res.get("d001", [])}
print(f"{'ovality':>9}{'mode':>8}{'f (GHz)':>11}{'df vs sham':>12}{'Q0':>10}"
      f"{'dQ %':>8}{'boreH %':>9}")
for tag, ov in CASES:
    for m in res[tag]:
        b = ref.get(m["mode"])
        df = f"{(m['f']-b['f'])*1000:+.2f}" if b else "--"
        dqp = f"{100*(m['Q0']/b['Q0']-1):+.2f}" if b and m["Q0"] and b["Q0"] else "--"
        print(f"{ov:>9}{m['mode']:>8}{m['f']:>11.5f}{df:>12}{m['Q0']:>10,.0f}"
              f"{dqp:>8}{m['pm']*100:>9.3f}")

# ---- exponent fit, the whole reason for the ladder -----------------------
print("\nEXPONENT: log-log slope of |df| vs ovality, fitted on 1/2/4 mm")
for mode in ("TE011", "TM020"):
    pts = []
    for tag, ov in CASES[1:]:
        m = next((x for x in res[tag] if x["mode"] == mode), None)
        b = ref.get(mode)
        if m and b:
            d = abs(m["f"] - b["f"]) * 1000
            if d > 0:
                pts.append((math.log(float(ov)), math.log(d), float(ov), d))
    if len(pts) < 2:
        print(f"  {mode}: too few usable points to fit")
        continue
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    den = sum((p[0] - mx) ** 2 for p in pts)
    slope = sum((p[0] - mx) * (p[1] - my) for p in pts) / den if den else float("nan")
    print(f"  {mode}: " + "  ".join(f"{p[2]}mm->{p[3]:.2f}MHz" for p in pts))
    print(f"  {mode}: slope = {slope:.2f}"
          + ("  ✅ quadratic — extrapolation is licensed" if 1.7 <= slope <= 2.3
             else "  ⚠️ NOT quadratic — do NOT extrapolate from this ladder"))
    if 1.7 <= slope <= 2.3:
        big = pts[-1]
        for tol in (0.40, 0.20, 0.10, 0.05):
            print(f"      implied at +/-{tol:.2f} mm: "
                  f"{big[3]*(tol/big[2])**2:.4f} MHz")
print(flush=True)
