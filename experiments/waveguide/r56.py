#!/usr/bin/env python3
"""R56 — what matches the LIT cavity, and what does that do to sample loading?

With fixed coupling and no tuner, the cavity cannot follow the plasma. Unlit it
is over-coupled (beta = 2.76, Q0 = 45,728, so Q_ext = 16,568); lit at sigma = 30
its Q0 collapses to 320 (R15), giving beta = 0.019 and |Gamma|^2 ~ 0.93. One
state is always badly mismatched, and "no tuner, no moving parts" is an explicit
design commitment.

🔑 WHY THIS IS AN ANALYTICAL CONSTRAINT, NOT JUST AN RF ONE. Plasma conductivity
depends on what is in the plasma: solvent uptake and dissolved solids change
electron density and the energy balance, so sigma is a function of sample feed
rate. Only a window of sigma gives an acceptable match, so **the match window
sets a tolerable aerosol loading, which sets an uptake rate and a dissolved-
solids ceiling.** Mehlich-3 is a salty extractant (NH4NO3, NH4F, HNO3, EDTA,
acetic acid), i.e. the high-TDS case.

METHOD. Sweep sigma DOWNWARD from the nominal 30 and read the match directly.
The crossing where beta = 1 is at LIGHT loading, not heavy — see the SIGMAS note.

🔢 |Gamma| IS MEASURED, NOT DERIVED. Palace reports S11 per frequency, so the
reflection at resonance is read straight off the sweep. The beta chain
(Q0 -> beta = Q0/Q_ext -> |Gamma| = |1-beta|/(1+beta)) is computed alongside as a
CROSS-CHECK. If the two disagree, the beta model is wrong, not the measurement —
Q_ext is assumed constant and that assumption is exactly what heavy loading might
break.

🔢 MESH RESOLUTION IS PER-CASE, and this is deliberate. The skin depth in the
plasma is delta = sqrt(2/(omega mu sigma)), which GROWS as sigma falls:

    sigma    0.3     1     3    10    30
    delta mm 18.6  10.2  5.87  3.22  1.86
    mesh mm  5.00  3.39  1.96  1.07  0.62   (delta/3, R15's converged criterion,
                                             capped at the 5 mm bore mesh)

R15 showed loaded Q is unstable at the ~40% level when the skin depth is
under-resolved, and CONVERGED at 0.3% once it is resolved at ~3 elements. A
single mesh across this sweep would be adequate at sigma = 3 and badly
under-resolved at sigma = 100. **The common quantity here is the RESOLUTION
CRITERION, not the element size** — which is the right invariant when the physics
length scale is itself the swept variable.

⚠️ Run at the OPERATIONAL 0 deg loop tilt (R60/R61), not the 45 deg diagnostic
every earlier plasma run used. The sigma = 30 case therefore doubles as a check
on whether tilt affects loaded Q at all: R15 measured 320 at 45 deg.
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
PLASMA = "4.5,8.5,-20.0,10.0"          # R12's realistic toroid
Q_EXT = 16568.0                        # from unlit beta = 2.76, Q0 = 45,728
BASE_ARGS = ["--radius", A, "--length", L, "--brake", "3", "--sectors", "1",
             "--order", "2", "--loop", "12,8.5,1,0.3", "--plasma", PLASMA]
BAND = (2.30, 2.52)
MU0 = 4e-7 * math.pi
W = 2 * math.pi * 2.45e9


def skin_mm(sigma):
    return math.sqrt(2 / (W * MU0 * sigma)) * 1e3


# 🔑 THE SWEEP RUNS DOWNWARD, and getting this backwards was my first mistake.
# Matching needs Q0 = Q_ext = 16,568. Unlit Q0 is 45,728 (over-coupled, beta 2.76)
# and at sigma = 30 it is 320 (badly under-coupled, beta 0.019). **The crossing is
# therefore at LOW sigma**, i.e. light loading — raising sigma walks AWAY from the
# match. It is also the affordable direction: delta grows as sigma falls, so the
# mesh gets coarser, not finer. A probe at sigma = 100 needed 0.35 mm, giving
# 1.7M tets and 2.25M nodes — impractical for an order-2 driven solve, and
# pointing the wrong way besides.
SIGMAS = [("s0p3", 0.3), ("s001", 1.0), ("s003", 3.0), ("s010", 10.0),
          ("s030", 30.0)]
# No point resolving finer than the bore mesh itself (5 mm) at the light-loading
# end, where the skin depth exceeds the plasma region.
FLOOR_MM = 0.45
CEIL_MM = 5.0


def solve(tag, sigma):
    c = json.loads(json.dumps(BASE))
    c["Model"]["Mesh"] = f"{tag}.msh"
    c["Problem"]["Output"] = f"postpro/{tag}"
    c["Boundaries"]["LumpedPort"][0]["Direction"] = [0.0, 1.0, 0.0]   # 0 deg tilt
    c["Domains"]["Materials"].append(
        {"Attributes": [12], "Permittivity": 1.0, "Permeability": 1.0,
         "Conductivity": sigma})
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
    recs = dq.load(tag)
    if not recs:
        return None
    idx = dq.peaks(recs, rel=0.05, sep=0.002)
    if not idx:
        print("    ⚠️ no peak — a heavily loaded resonance is broad and "
              "low-contrast; check the log before reading anything into this",
              flush=True)
        return None
    # The loaded resonance is the largest stored-energy maximum in band.
    best = max((recs[i] for i in idx), key=lambda r: r["U"])
    # Deepest |S11| anywhere in band, which is what a VNA would see.
    dip = min(recs, key=lambda r: r["s_db"])
    return dict(f=best["f"], Q0=best["Q0"], pe=best["pe"], pm=best["pm"],
                s_at_peak=best["s_db"], g_at_peak=best["gamma"],
                f_dip=dip["f"], s_dip=dip["s_db"], g_dip=dip["gamma"])


print(__doc__)
print("=" * 78, flush=True)
print(f"{'sigma':>8}{'skin mm':>10}{'mesh mm':>10}   resolution")
cases = []
for tag, s in SIGMAS:
    d = skin_mm(s)
    h = min(max(d / 3.0, FLOOR_MM), CEIL_MM)
    n = d / h
    flag = ("✅" if n >= 2.5 else
            "✅ skin depth exceeds the plasma region — bulk heating, not a skin"
            if d > 8.5 else
            "⚠️ UNDER-RESOLVED, R15 says Q is unstable here")
    print(f"{s:>8.1f}{d:>10.2f}{h:>10.2f}   {n:.1f} elements/skin depth {flag}")
    cases.append((tag, ["--plasma-h", f"{h:.3f}"]))
print(flush=True)

fac, _ = meshsweep.sweep(cases, BASE_ARGS,
                         factors=("0.96", "1.00", "0.93", "0.90", "1.06"))
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")
sizes = {t: pathlib.Path(f"{t}.msh").stat().st_size for t, _e in cases}
if len(set(sizes.values())) != len(sizes):
    sys.exit("🔴 two cases produced identically sized meshes — --plasma-h did "
             "not take effect. Do not read results from this.")

res = {}
for (tag, sigma), (_t, extra) in zip(SIGMAS, cases):
    print(f"\n=== sigma = {sigma} S/m   plasma mesh {extra[1]} mm", flush=True)
    res[tag] = solve(tag, sigma)
    m = res[tag]
    if m:
        print(f"   peak f={m['f']:.5f}  Q0={m['Q0']:>8,.0f}  "
              f"boreE={m['pe']*100:6.3f}%  boreH={m['pm']*100:6.3f}%", flush=True)
        print(f"   |S11| at peak {m['s_at_peak']:7.3f} dB   "
              f"deepest dip {m['s_dip']:7.3f} dB at {m['f_dip']:.5f}", flush=True)

print("\n" + "=" * 78)
print(f"{'sigma':>7}{'Q0':>9}{'beta':>9}{'|G|^2 meas':>12}{'|G|^2 beta':>12}"
      f"{'absorbed':>10}")
rows = []
for tag, sigma in SIGMAS:
    m = res.get(tag)
    if not m:
        print(f"{sigma:>7.1f}   no usable peak")
        continue
    beta = m["Q0"] / Q_EXT
    g2_beta = ((1 - beta) / (1 + beta)) ** 2
    g2_meas = m["g_at_peak"] ** 2
    rows.append((sigma, m["Q0"], beta, g2_meas, g2_beta))
    print(f"{sigma:>7.1f}{m['Q0']:>9,.0f}{beta:>9.3f}{g2_meas:>12.3f}"
          f"{g2_beta:>12.3f}{100*(1-g2_meas):>9.1f}%")

print("\nMATCH WINDOW")
if rows:
    best = min(rows, key=lambda r: r[3])
    print(f"  best match in this sweep: sigma = {best[0]}, "
          f"|Gamma|^2 = {best[3]:.3f}, {100*(1-best[3]):.0f}% absorbed")
    ok = [r for r in rows if r[3] <= 0.50]
    if ok:
        print(f"  sigma giving >=50% absorbed: "
              f"{', '.join(f'{r[0]}' for r in ok)}")
    else:
        print("  🔴 NO sigma in this sweep absorbs even 50% — with fixed "
              "coupling and no tuner, the lit cavity is mismatched across the "
              "whole plausible range, and the coupling design needs revisiting "
              "before sample loading can be specified.")
    d = [r for r in rows if abs(r[2] - 1.0) < 0.5]
    if d:
        print(f"  ⚠️ beta ~ 1 near sigma = {d[0][0]} — the match is a "
              f"critically-coupled point, so the ACCEPTABLE WINDOW is set by how "
              f"far sigma can drift either side of it")
print("""
Read: |Gamma|^2 measured vs beta-derived should agree. If they diverge, Q_ext is
NOT constant under load and the beta model — which every coupling number in this
project rests on — is the thing that broke, not the measurement.

Then: whichever sigma range absorbs acceptably IS the allowed aerosol loading,
and it converts to an uptake rate and a dissolved-solids ceiling.""", flush=True)
