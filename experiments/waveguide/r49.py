#!/usr/bin/env python3
"""R49 — the gas-feed feedthrough on the -z cap, which was never in the model.

The torch has to penetrate the -z end cap to reach its plumbing. geometry.py
ended the tube flush against solid metal, so that aperture did not exist: every
number measured on this design was taken on a cavity with one hole (the exhaust
chimney) when the real object has two.

It is also the harder of the two, because it is DIELECTRIC-LOADED. A below-cutoff
tube gets its isolation from being far above the operating frequency, and a
dielectric drops the cutoff by ~sqrt(eps_eff):

    21 mm bore, air                 TE11 cutoff 8.37 GHz    1.46 dB/mm
    21 mm bore, ~25% quartz by area   est. ~5-6 GHz         est. ~1.0-1.2 dB/mm
    21 mm bore, sapphire-FILLED       bound: 2.46 GHz       🔴 AT the operating
                                                               frequency

The filled row is a bound, not this geometry — the tube is an annulus, not a rod.
But it shows how little headroom the argument has, and nobody has checked where
between those rows the real part sits.

METHOD — length-independence as the isolation criterion, which needs no port.
If the feed tube is genuinely below cutoff, the resonance cannot see its far end,
so f and Q must stop changing once the tube is a few decay constants long. If
they keep moving with length, the field is reaching the termination and the
"below cutoff" claim is false for the LOADED aperture whatever it is for an air
one.

    ref    no feedthrough — the model as it has been all along
    L10    10 mm, ~10-15 dB. The POSITIVE CONTROL: too short to isolate, so it
           SHOULD move. If it does not, this method has no sensitivity and a null
           at 41 mm proves nothing.
    L20    20 mm
    L41    41 mm, the same length as the exhaust chimney

Every case extends the torch the full length of its tube, which is the loaded
case that matters.

PRE-REGISTERED PREDICTION:
  * ref -> L41 perturbs TM020 upward by roughly the chimney's +1.26 MHz. TM020
    has p = 0 and no z dependence, so both caps are equivalent to it, and the
    aperture is the same diameter.
  * TE011 barely moves: the hole is near the axis where its cap current
    J1(chi'01 r/a) vanishes.
  * ⚠️ TWO COMPETING EFFECTS on TM020 and I do not know which wins: the aperture
    pushes it UP (R29), while the extra dielectric sitting in that aperture --
    exactly where TM020's E_z is maximal -- pulls it DOWN. The net sign is a
    genuine prediction failure risk, and my TM020 sign predictions are 0 for 2
    tonight.
  * Length: L20 and L41 agree; L10 differs.
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
CASES = [("fd_ref", []),
         ("fd_10", ["--feed", "21,10", "--torch-ext", "10"]),
         ("fd_20", ["--feed", "21,20", "--torch-ext", "20"]),
         ("fd_41", ["--feed", "21,41", "--torch-ext", "41"])]
LABEL = {"fd_ref": "no feed", "fd_10": "21x10 mm", "fd_20": "21x20 mm",
         "fd_41": "21x41 mm"}
BAND = (2.34, 2.50)


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
    out = dq.report(tag)
    for m in out:
        print(f"     {m['mode']:>6}  f={m['f']:.5f}  Q0={m['Q0']:>9,.0f}  "
              f"boreE={m['pe']*100:6.3f}%  boreH={m['pm']*100:6.3f}%", flush=True)
    return out


print(__doc__)
print("=" * 78, flush=True)

fac, _ = meshsweep.sweep(CASES, BASE_ARGS,
                         factors=("0.96", "1.00", "0.93", "0.90", "1.06"))
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")

# R50 in miniature: assert the geometry actually changed, because two silent
# no-ops today produced verdicts from meshes that were never modified.
import re
sizes = {}
for tag, _e in CASES:
    n = pathlib.Path(f"{tag}.msh").stat().st_size
    sizes[tag] = n
    print(f"  {LABEL[tag]:>10}: mesh file {n/1e6:.1f} MB", flush=True)
if len(set(sizes.values())) != len(sizes):
    sys.exit("🔴 two cases produced identically sized meshes — the feed "
             "argument did not take effect. Do not read results from this.")

res = {}
for tag, _e in CASES:
    print(f"\n=== {LABEL[tag]}", flush=True)
    res[tag] = solve(tag)

print("\n" + "=" * 78)
ref = {m["mode"]: m for m in res.get("fd_ref", [])}
print(f"{'case':>10}{'mode':>8}{'f (GHz)':>11}{'df vs ref':>11}{'Q0':>10}"
      f"{'dQ %':>8}{'boreH %':>9}")
for tag, _e in CASES:
    for m in res[tag]:
        b = ref.get(m["mode"])
        df = f"{(m['f']-b['f'])*1000:+.2f}" if b else "--"
        dqp = f"{100*(m['Q0']/b['Q0']-1):+.2f}" if b and m["Q0"] and b["Q0"] else "--"
        print(f"{LABEL[tag]:>10}{m['mode']:>8}{m['f']:>11.5f}{df:>11}"
              f"{m['Q0']:>10,.0f}{dqp:>8}{m['pm']*100:>9.3f}")

print("\nISOLATION TEST — does the resonance still see the tube's far end?")
for mode in ("TE011", "TM020"):
    got = {}
    for tag, _e in CASES[1:]:
        m = next((x for x in res[tag] if x["mode"] == mode), None)
        if m:
            got[LABEL[tag]] = m["f"]
    if len(got) < 3:
        print(f"  {mode}: missing a case — read the tables above")
        continue
    v = list(got.values())
    d_10_20 = (v[1] - v[0]) * 1000
    d_20_41 = (v[2] - v[1]) * 1000
    print(f"  {mode}: 10->20 mm {d_10_20:+.2f} MHz   20->41 mm {d_20_41:+.2f} MHz")
    if abs(d_20_41) < 0.5 and abs(d_10_20) >= 0.5:
        print("    ✅ saturated by 20 mm, and the 10 mm control DID move — the "
              "loaded feedthrough is genuinely below cutoff and 41 mm is ample")
    elif abs(d_20_41) < 0.5 and abs(d_10_20) < 0.5:
        print("    ⚠️ flat everywhere INCLUDING the 10 mm control — this test "
              "has no demonstrated sensitivity, so the null is weak evidence")
    else:
        print("    🔴 still moving at 41 mm — the resonance reaches the "
              "termination, and the below-cutoff argument does not hold for the "
              "DIELECTRIC-LOADED aperture. The feed tube needs lengthening or "
              "the aperture needs shrinking toward the tube OD.")
print(flush=True)
