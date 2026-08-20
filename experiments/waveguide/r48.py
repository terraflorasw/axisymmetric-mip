#!/usr/bin/env python3
"""R48 — is the chimney's TM020 shift independent of LENGTH?

R29 measured the 21 x 41 mm exhaust chimney as free for TE011 and +1.26 MHz on
TM020. I explained the upward sign — I had predicted downward — by guessing that
a PEC-terminated below-cutoff tube is not "added volume" but a SHORTED EVANESCENT
STUB, loading the aperture inductively. That was post-hoc and untested.

It makes a checkable prediction. Whatever the mechanism, if the tube is truly
below cutoff the resonance cannot see its far end, so the shift must SATURATE
with length. And in the limit L -> 0 a PEC-terminated tube is just a dimple in
the cap, so the shift must go to zero. Between those, the approach to saturation
measures the evanescent decay length directly.

🔢 From alpha = (2*pi/c)*sqrt(fc^2 - f^2) with fc = 1.8412c/(pi*d) = 8.37 GHz for
a 21 mm air bore: alpha = 0.168 Np/mm, i.e. 1.457 dB/mm (reproducing entry 53's
1.46) and a DECAY LENGTH of 5.96 mm.

PRE-REGISTERED PREDICTION. Field amplitude at the far end falls as exp(-L/5.96),
and its effect on the resonance goes as the round trip, exp(-2L/5.96). So the
shift should approach saturation as 1 - exp(-2L/5.96):

    L = 2 mm    ~49% of saturation   ~0.6 MHz
    L = 6 mm    ~87%                 ~1.1 MHz
    L = 41 mm   ~100%                ~1.26 MHz

Monotone, no sign change. TE011 stays at zero throughout — it does not couple to
a near-axis cap aperture at all (R29, and the corrected reasoning in entry 80).

⚠️ LEARNED FROM R49, WHICH FAILED THIS WAY. There the 10 mm "positive control"
was already ~3 decay lengths long, so it did not move, and the run could not
separate "isolated" from "test too blunt". Here the control is 2 mm — a third of
one decay length — so it MUST move if the method works at all.

🔴 WHAT THIS DOES NOT MEASURE: leakage. Saturation of the near-field perturbation
says the resonance stops seeing the tube's end; it says nothing about how much
power escapes through it. The 60 dB isolation target still rests on length x
dB/mm and needs a port at the exit to measure properly. **A saturating shift is
NOT a licence to shorten the chimney.**
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
CASES = [("cl_ref", []), ("cl_02", ["--chimney", "21,2"]),
         ("cl_06", ["--chimney", "21,6"]), ("cl_41", ["--chimney", "21,41"])]
LABEL = {"cl_ref": "none", "cl_02": "2 mm", "cl_06": "6 mm", "cl_41": "41 mm"}
LENGTH = {"cl_02": 2.0, "cl_06": 6.0, "cl_41": 41.0}
BAND = (2.34, 2.50)
DECAY = 5.96      # mm, computed above


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

sizes = {t: pathlib.Path(f"{t}.msh").stat().st_size for t, _e in CASES}
for t, _e in CASES:
    print(f"  {LABEL[t]:>6}: mesh {sizes[t]/1e6:.2f} MB", flush=True)
if len(set(sizes.values())) != len(sizes):
    sys.exit("🔴 two cases produced identically sized meshes — the chimney "
             "argument did not take effect. Do not read results from this.")

res = {}
for tag, _e in CASES:
    print(f"\n=== chimney {LABEL[tag]}", flush=True)
    res[tag] = solve(tag)

print("\n" + "=" * 78)
ref = {m["mode"]: m for m in res.get("cl_ref", [])}
print(f"{'chimney':>8}{'mode':>8}{'f (GHz)':>11}{'df vs none':>12}{'Q0':>10}"
      f"{'dQ %':>8}")
for tag, _e in CASES:
    for m in res[tag]:
        b = ref.get(m["mode"])
        df = f"{(m['f']-b['f'])*1000:+.2f}" if b else "--"
        dqp = f"{100*(m['Q0']/b['Q0']-1):+.2f}" if b and m["Q0"] and b["Q0"] else "--"
        print(f"{LABEL[tag]:>8}{m['mode']:>8}{m['f']:>11.5f}{df:>12}"
              f"{m['Q0']:>10,.0f}{dqp:>8}")

print(f"\nSATURATION vs the evanescent model, decay length {DECAY:.2f} mm")
sat = None
for mode in ("TM020", "TE011"):
    b = ref.get(mode)
    m41 = next((x for x in res["cl_41"] if x["mode"] == mode), None)
    if not (b and m41):
        continue
    full = (m41["f"] - b["f"]) * 1000
    print(f"  {mode}: saturated shift {full:+.2f} MHz")
    if abs(full) < 0.5:
        print("    (too small to resolve a saturation curve — expected for TE011)")
        continue
    sat = full
    for tag in ("cl_02", "cl_06", "cl_41"):
        m = next((x for x in res[tag] if x["mode"] == mode), None)
        if not m:
            continue
        d = (m["f"] - b["f"]) * 1000
        pred = 1 - math.exp(-2 * LENGTH[tag] / DECAY)
        print(f"    {LENGTH[tag]:>5.0f} mm: {d:+.2f} MHz = {100*d/full:5.1f}% of "
              f"saturation   (evanescent model predicts {100*pred:5.1f}%)")
    d2 = next(((x["f"] - b["f"]) * 1000 for x in res["cl_02"]
               if x["mode"] == mode), None)
    if d2 is not None:
        if abs(d2 / full) > 0.9:
            print("    🔴 the 2 mm case is ALREADY saturated — the shift is not "
                  "an evanescent-tube effect at all; it is the aperture opening, "
                  "and the shorted-stub explanation is dead.")
        elif abs(d2 / full) < 0.15:
            print("    ⚠️ 2 mm gives almost nothing — slower onset than the "
                  "evanescent model; the tube is doing more than decay.")
        else:
            print("    ✅ partial at 2 mm and saturated by 41 — consistent with "
                  "an evanescent stub, and the decay length is measurable here.")
print("""
⚠️ REMINDER: this is near-field saturation, NOT leakage. It does not license a
shorter chimney; the 60 dB isolation target needs a port at the exit.""",
      flush=True)
