#!/usr/bin/env python3
"""R54b — did TM111 and TM020 DIE, or just leave the window?

R54 searched 2.34-2.50 GHz down to 0.1% of peak and found no TM111 in either
grooved case, and no TM020 in the λ/4 case. I reported that as "absent". That was
overclaiming: it is absent FROM THE SWEPT BAND, which is not the same thing, and
the distinction is exactly the detuning-vs-damping question that has to be
settled before any groove geometry is optimised.

The evidence already points to detuning. At 15 mm TM020 was plainly visible at
2.39376, having moved 55 MHz DOWN from its bare position of 2.44856 with its Q
halved. If that motion continues with depth, TM020 leaves the bottom of the
window at λ/4 — which is what happened. Meanwhile the m=2 doublet moved the other
way, 2.347 -> 2.45, so modes are being pushed in both directions AWAY from TE011.

This widens the sweep to 2.10-2.60 GHz to find them.

⚠️ Run at --sectors 1, not 5. Locating a mode needs its bore-energy signature
(TM020 boreE ~3-4%, TM111 boreH ~1.2% with boreE ~0.75%), not azimuthal content,
and sectors=1 solves in a third of the time. The cost is that these meshes are
NOT comparable to R54's — this run answers "where did they go", not "how much did
they move". Frequencies here should not be differenced against R54's.
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
BASE_ARGS = ["--radius", A, "--length", L, "--sectors", "1", "--order", "2",
             "--loop", "12,8.5,1,0.3", "--loop-tilt", "45", "--brake", "0"]
CASES = [("w_none", []), ("w_15", ["--groove", "3,15"]),
         ("w_31", ["--groove", "3,30.6"])]
LABEL = {"w_none": "no groove", "w_15": "groove 15mm", "w_31": "groove λ/4"}
BAND = (2.10, 2.60)


def solve(tag):
    c = json.loads(json.dumps(BASE))
    c["Model"]["Mesh"] = f"{tag}.msh"
    c["Problem"]["Output"] = f"postpro/{tag}"
    c["Domains"]["Materials"] = [m for m in c["Domains"]["Materials"]
                                 if m["Attributes"] != [8]]
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
            return []
    recs = dq.load(tag)
    return [recs[i] for i in dq.peaks(recs, rel=0.001, sep=0.0015)]


def label_of(r):
    """By signature, NOT dq.identify -- its 1% boreH cut calls TM111 a TE011."""
    if r["pm"] >= 0.018:
        return "TE011"
    if r["pe"] >= 0.020:
        return "TM020"
    if 0.008 <= r["pm"] < 0.018 and r["pe"] >= 0.004:
        return "TM111?"
    return "other"


print(__doc__)
print("=" * 78, flush=True)

fac, _ = meshsweep.sweep(CASES, BASE_ARGS,
                         factors=("0.96", "1.00", "0.93", "0.90", "1.06"))
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")

res = {}
for tag, _e in CASES:
    print(f"\n=== {LABEL[tag]}   band {BAND[0]}-{BAND[1]} GHz", flush=True)
    res[tag] = solve(tag)
    for r in res[tag]:
        print(f"   f={r['f']:.5f}  Q={r['Q0']:>9,.0f}  boreE={r['pe']*100:6.3f}%"
              f"  boreH={r['pm']*100:6.3f}%   {label_of(r)}", flush=True)
    if not res[tag]:
        print("   no peaks", flush=True)

print("\n" + "=" * 78)
print("WHERE THE TM MODES WENT")
for tag, _e in CASES:
    te = next((r for r in res[tag] if label_of(r) == "TE011"), None)
    tms = [r for r in res[tag] if label_of(r) in ("TM020", "TM111?")]
    print(f"\n  {LABEL[tag]}:")
    if te:
        print(f"    TE011 at {te['f']:.5f}, Q {te['Q0']:,.0f}")
    for r in tms:
        d = (r["f"] - te["f"]) * 1000 if te else float("nan")
        print(f"    {label_of(r):>7} at {r['f']:.5f}, Q {r['Q0']:>8,.0f}, "
              f"{d:+.1f} MHz from TE011")
    if not tms:
        print("    🔴 NO TM mode anywhere in 2.10-2.60 — it is not merely "
              "detuned out of the ISM band, and DAMPING is the remaining "
              "explanation")
print("""
Read: TM modes present but far from TE011 => DETUNING, and groove geometry goes
on the optimization pile as agreed. TM modes absent from a 500 MHz window with
their Q gone => DAMPING, and the design criterion changes from separation to
suppression ratio.""", flush=True)
