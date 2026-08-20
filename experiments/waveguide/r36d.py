#!/usr/bin/env python3
"""R36d — the ovality ladder, rebuilt after r36c could not be meshed.

r36c asked for +/-0.01, 1, 2 and 4 mm in one sweep and got no common
size-factor: every one of the five candidates failed on SOME case (1.00 and
1.06 and 0.85 on d001, 0.96 on d400, 0.90 on d100). meshsweep refused to return
a mixed-density set, which is correct — differencing across size-factors is the
R11 error.

What that run DID establish is that 0.96 meshes d001, d100 and d200 (it built
all three before failing on d400). So the comparable ladder is those three:

    d001   +/-0.01 mm   sham reference — round to 1e-4 of the radius, but
                        carrying the same ovalised surface representation
    d100   +/-1.0 mm    5x the tolerance under consideration
    d200   +/-2.0 mm    10x it, i.e. 100x a quadratic effect

+/-4 mm is run afterwards, ALONE, at whatever factor will curve it, and is
reported as CORROBORATION ONLY — it is not size-factor-matched to the ladder
and is deliberately excluded from the fit. A trend confirmed by a point that
cannot legally be differenced is still worth seeing; a fit contaminated by one
is not.

WHAT THE RATIO MEANS. With a sham reference and two loaded points, the
discriminator is df(2mm)/df(1mm):

    ~4    quadratic — the m=0 cancellation holds and only delta^2 survives.
          Extrapolating to +/-0.2 mm divides by 100 from the 2 mm point.
    ~2    linear — the first-order cancellation is NOT holding, something is
          breaking the azimuthal symmetry argument, and the tolerance is real.
    ~1    neither — the "signal" is discretisation error, and all this bounds
          is the noise floor.
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
LADDER = [("d001", "0.01"), ("d100", "1.0"), ("d200", "2.0")]
EXTRA = ("d400", "4.0")
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


def show(tag, ov, peaks):
    ovf = float(ov)
    print(f"\n=== ovality +/-{ov} mm  (semi-axes {float(A)+ovf:.2f} / "
          f"{float(A)-ovf:.2f}, {100*ovf/float(A):.2f}% of radius)", flush=True)
    for m in peaks:
        print(f"    {m['mode']:>6}  f={m['f']:.5f}  Q0={m['Q0']:>9,.0f}  "
              f"boreE={m['pe']*100:6.3f}%  boreH={m['pm']*100:6.3f}%", flush=True)
    if not peaks:
        print("    NO PEAKS", flush=True)


print(__doc__)
print("=" * 78, flush=True)

fac, _ = meshsweep.sweep([(t, ["--ovality", ov]) for t, ov in LADDER],
                         BASE_ARGS, factors=("0.96",))
if not fac:
    sys.exit("0.96 no longer meshes the ladder — re-probe before trusting r36c's log")

res = {}
for tag, ov in LADDER:
    res[tag] = solve(tag)
    show(tag, ov, res[tag])

print("\n" + "=" * 78)
ref = {m["mode"]: m for m in res.get("d001", [])}
print(f"{'ovality':>9}{'mode':>8}{'f (GHz)':>11}{'df vs sham':>12}{'Q0':>10}"
      f"{'dQ %':>8}{'boreH %':>9}")
for tag, ov in LADDER:
    for m in res[tag]:
        b = ref.get(m["mode"])
        df = f"{(m['f']-b['f'])*1000:+.2f}" if b else "--"
        dqp = f"{100*(m['Q0']/b['Q0']-1):+.2f}" if b and m["Q0"] and b["Q0"] else "--"
        print(f"{ov:>9}{m['mode']:>8}{m['f']:>11.5f}{df:>12}{m['Q0']:>10,.0f}"
              f"{dqp:>8}{m['pm']*100:>9.3f}")

print("\nRATIO TEST  df(2mm)/df(1mm)   [~4 quadratic | ~2 linear | ~1 noise]")
NOISE = 1.0     # MHz — the scatter measured across r36/r36b at fixed geometry
for mode in ("TE011", "TM020"):
    b = ref.get(mode)
    m1 = next((x for x in res["d100"] if x["mode"] == mode), None)
    m2 = next((x for x in res["d200"] if x["mode"] == mode), None)
    if not (b and m1 and m2):
        print(f"  {mode}: missing a point — no ratio")
        continue
    d1, d2 = (m1["f"] - b["f"]) * 1000, (m2["f"] - b["f"]) * 1000
    print(f"  {mode}: 1mm {d1:+.2f} MHz   2mm {d2:+.2f} MHz", end="")
    if abs(d2) < NOISE:
        print(f"   → both inside the {NOISE:.1f} MHz floor: NO measurable "
              f"effect even at 10x the tolerance")
        continue
    r = d2 / d1 if abs(d1) > 1e-9 else float("nan")
    print(f"   ratio {r:.2f}", end="")
    if 3.0 <= r <= 5.0:
        print("  ✅ quadratic")
        for tol in (0.40, 0.20, 0.10, 0.05):
            print(f"      implied at +/-{tol:.2f} mm: "
                  f"{abs(d2)*(tol/2.0)**2:.4f} MHz")
    elif 1.5 <= r <= 2.5:
        print("  ⚠️ LINEAR — the m=0 cancellation is not holding; the tolerance "
              "is real and must be derived from this slope, not extrapolated "
              "as delta^2")
    else:
        print("  ⚠️ neither — read as discretisation scatter, not a trend")

# ---- 4 mm, alone, NOT in the fit ---------------------------------------
print("\n" + "=" * 78)
print("CORROBORATION ONLY — +/-4 mm at its own size-factor, not comparable")
tag, ov = EXTRA
# Built directly, not through sweep(): there is nothing to make common across a
# single case, and sweep() would only be a wrapper pretending otherwise.
fac4 = next((f for f in ("1.00", "0.90", "1.06", "0.85", "0.93")
             if meshsweep.build(tag, BASE_ARGS, ["--ovality", ov], f).returncode == 0),
            None)
if not fac4:
    print("  +/-4 mm will not curve at any candidate factor — skipped.")
else:
    print(f"  built at size-factor {fac4} (ladder is 0.96 — DO NOT difference)")
    p4 = solve(tag)
    show(tag, ov, p4)
    for m in p4:
        b = ref.get(m["mode"])
        if b:
            print(f"    {m['mode']}: {(m['f']-b['f'])*1000:+.2f} MHz from the "
                  f"sham — sign and rough scale only", flush=True)
print(flush=True)
