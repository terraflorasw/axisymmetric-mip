#!/usr/bin/env python3
"""R39 — re-do the brake-essential test DRIVEN, at the current design point.

The standing result is that the 3 mm quartz annulus per end cap is doing
essentially all of the degeneracy breaking: with it, the nearest m!=0 mode is
+59 MHz away and sector CV is 0.0075; without it, +0.8 MHz and CV 0.0498. That
is a load-bearing claim — the brake is a part on the drawing — and it was
measured with an EIGENSOLVE on 4 SECTORS, both of which the R37 policy now
treats as provisional, and 4 sectors is additionally blind to m=2.

This re-asks it driven, at a = 103.70 / L = 88.53, and adds a half-thickness
case that the original never ran:

    b30   3.0 mm   the design as drawn
    b15   1.5 mm   is the brake oversized, or is 3 mm doing real work?
    b00   0.0 mm   deleted

WHAT A DRIVEN SOLVE CAN AND CANNOT SEE HERE. With --sectors 1 there is no
sector-CV metric, so this cannot reproduce the original's axisymmetry number.
It does not need to. R36 established a sharper signature for exactly this
failure, and validated it against a case where the mode was known to be
destroyed (+/-4 mm ovality):

    an intact TE011      ONE peak, boreH ~2.08%, boreE ~0.05%, Q ~45,800
    a hybridised TE011   TWO peaks sharing the bore-H between them (1.16% and
                         1.26% at 4 mm ovality), boreE up ~15x, Q roughly HALVED

So the read is: does deleting the brake split TE011's signature and collapse its
Q? That is the same question the CV metric was asking, measured through the
instrument's own filter rather than through a classifier that has failed 3x.

⚠️ Frequencies are NOT differenced against the design point: removing the brake
moves TE011 by ~+13 MHz and TM020 by far more (the brake and torch together load
TM020 by 154 MHz). The band below is wide enough to hold TE011 in all three
cases; TM020 is expected to leave it in the b00 case and its absence there means
nothing.
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
BASE_ARGS = ["--radius", A, "--length", L, "--sectors", "1", "--order", "2",
             "--loop", "12,8.5,1,0.3", "--loop-tilt", "45"]
CASES = [("b30", "3"), ("b15", "1.5"), ("b00", "0")]
BAND = (2.34, 2.56)
BRAKE_ATTR = 8


def solve(tag, brake):
    c = json.loads(json.dumps(BASE))
    c["Model"]["Mesh"] = f"{tag}.msh"
    c["Problem"]["Output"] = f"postpro/{tag}"
    if float(brake) == 0.0:
        # No brake means attribute 8 is absent from the mesh. Leaving a material
        # bound to a non-existent attribute is how a config silently stops
        # describing the model it is solving.
        c["Domains"]["Materials"] = [m for m in c["Domains"]["Materials"]
                                     if m["Attributes"] != [BRAKE_ATTR]]
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

fac, _ = meshsweep.sweep([(t, ["--brake", b]) for t, b in CASES], BASE_ARGS,
                         factors=("0.96", "1.00", "0.93", "0.90", "1.06"))
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")

res = {}
for tag, b in CASES:
    print(f"\n=== brake {b} mm per end cap", flush=True)
    res[tag] = solve(tag, b)
    for m in res[tag]:
        print(f"    {m['mode']:>6}  f={m['f']:.5f}  Q0={m['Q0']:>9,.0f}  "
              f"boreE={m['pe']*100:6.3f}%  boreH={m['pm']*100:6.3f}%", flush=True)

# ---- the signature test, run at 1% of peak so weak neighbours show ------
print("\n" + "=" * 78)
print("EVERY resonance above 1% of peak stored energy, and the bore-H it carries")
for tag, b in CASES:
    recs = dq.load(tag)
    if not recs:
        print(f"  brake {b} mm: no output"); continue
    um = max(r["U"] for r in recs)
    idx = dq.peaks(recs, rel=0.01, sep=0.0008)
    tot_h = sum(recs[i]["pm"] for i in idx)
    print(f"\n  brake {b:>3} mm — {len(idx)} peaks, total bore-H {tot_h*100:.3f}%")
    for i in idx:
        r = recs[i]
        print(f"     f={r['f']:.5f}  U/Umax={r['U']/um:7.4f}  Q0={r['Q0']:>9,.0f}"
              f"  boreE={r['pe']*100:6.3f}%  boreH={r['pm']*100:6.3f}%")
    # 1.8%, NOT 1.0%. A persistent mode family carrying boreH ~1.21% exists in
    # EVERY case including the design point, so a 1% cut fired "hybridised" on
    # all three runs including the known-good one. The signature being tested is
    # TE011's own 2.08%, and hybridisation means that 2.08% SPLITS — so the cut
    # has to sit above the resident family, not below it.
    strong = [recs[i] for i in idx if recs[i]["pm"] >= 0.018]
    if len(strong) == 1:
        s = strong[0]
        others = [recs[i]["f"] for i in idx if recs[i] is not s]
        near = min((abs(o - s["f"]) * 1000 for o in others), default=None)
        print(f"     ✅ ONE mode carries the TE011 signature (boreH "
              f"{s['pm']*100:.3f}%, Q {s['Q0']:,.0f})"
              + (f"; nearest other resonance {near:.1f} MHz away"
                 if near is not None else "; nothing else in band"))
    elif len(strong) > 1:
        print(f"     🔴 {len(strong)} modes share the bore-H — TE011 is "
              f"HYBRIDISED, the R36 signature of a destroyed mode")
    else:
        print("     ⚠️ nothing carries a TE011-like bore-H — mode has left the "
              "band or the solve is not describing the model")
print("""
Read: if b00 shows one clean TE011 with a distant neighbour and undegraded Q,
the brake is deletable and a part comes off the drawing. If b00 splits the
bore-H or halves Q, the standing result survives its method being replaced. b15
says whether 3 mm is doing real work or is just the stock thickness.""",
      flush=True)
