#!/usr/bin/env python3
"""R29 — does the below-cutoff exhaust chimney perturb TE011?

Entry 53 sized the end-cap aperture as a chimney rather than a hole: 21 mm bore,
41 mm long, 1.46 dB/mm below cutoff for 60 dB of isolation, doing thermal and
pressure duty at the same time. R29 was opened because the radial viewport was
also "obviously fine" until it was measured and cost 0.9% of Q.

`geometry.py` gained `--chimney D,LEN`: air continuing past the +z end cap,
terminated PEC at its far end, exactly as the radial viewport stub is.

PRE-REGISTERED PREDICTION. An aperture couples through the TANGENTIAL H and the
NORMAL E on the wall it pierces. At a TE011 cavity's end cap:

    E is purely azimuthal and ~ sin(pi z/L)  -> ZERO at both caps
    H_r, the tangential component,  ~ sin(pi z/L)  -> ZERO at both caps
    H_z is normal to the cap, and normal H does not drive aperture coupling

Both drivers vanish. This is the same property that makes TE011 tolerate a gap
at the cap-wall joint and is why it is the classic high-Q mode. So I expect the
chimney to be FREE for TE011 — no measurable df, no measurable dQ — and to stay
free as the hole is opened out to 25 mm.

🔴 CORRECTED 2026-08-16, AFTER THE RUN — the prediction above is left verbatim
because it is a pre-registration, but its H claim is WRONG. H_r ~ cos(pi z/L) is
MAXIMAL at the caps, not zero; that is why the caps carry azimuthal current and
dissipate at all. The measured null stands, for a narrower reason: TE011 has no
normal E on the cap (exactly zero), and its magnetic coupling is weak only
because H_r ~ J1(r) vanishes ON AXIS and small-hole coupling goes as (d/lambda)^3.
Cap current peaks at r = 49.8 mm, so a cap aperture is free only NEAR THE AXIS —
a mid-radius port would couple strongly. See the correction entry in FINDINGS.

TM020 is the opposite case: its E_z is NORMAL to the cap and MAXIMUM on axis,
which is exactly where the hole is. It should shift measurably, and downward,
since the chimney adds volume for that field to store energy in.

🔑 THAT CONTRAST IS THE CONTROL. R36 showed that comparing across separately
built meshes carries ~1-3 MHz of systematic discretisation scatter, which could
swamp a small real effect on TE011. But mesh scatter does not know which mode is
which: if TM020 moves monotonically with hole diameter in the SAME meshes where
TE011 does not move at all, the null on TE011 is a physical null and not a
measurement that was too coarse to see anything.

    off      no chimney — the design point as solved everywhere else
    c2141    21 x 41 mm, the sizing from entry 53
    c2541    25 x 41 mm, opened out — still below cutoff (TE11 at 7.0 GHz)
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
CASES = [("choff", []), ("c2141", ["--chimney", "21,41"]),
         ("c2541", ["--chimney", "25,41"])]
LABEL = {"choff": "no chimney", "c2141": "21 x 41 mm", "c2541": "25 x 41 mm"}
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
    return dq.report(tag)


print(__doc__)
print("=" * 78, flush=True)

fac, _ = meshsweep.sweep(CASES, BASE_ARGS,
                         factors=("0.96", "1.00", "0.93", "0.90", "1.06"))
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")

res = {}
for tag, _extra in CASES:
    print(f"\n=== {LABEL[tag]}", flush=True)
    res[tag] = solve(tag)
    for m in res[tag]:
        print(f"    {m['mode']:>6}  f={m['f']:.5f}  Q0={m['Q0']:>9,.0f}  "
              f"boreE={m['pe']*100:6.3f}%  boreH={m['pm']*100:6.3f}%", flush=True)

print("\n" + "=" * 78)
ref = {m["mode"]: m for m in res.get("choff", [])}
print(f"{'case':>12}{'mode':>8}{'f (GHz)':>11}{'df (MHz)':>10}{'Q0':>10}"
      f"{'dQ %':>8}{'boreH %':>9}")
for tag, _e in CASES:
    for m in res[tag]:
        b = ref.get(m["mode"])
        df = f"{(m['f']-b['f'])*1000:+.2f}" if b else "--"
        dqp = f"{100*(m['Q0']/b['Q0']-1):+.2f}" if b and m["Q0"] and b["Q0"] else "--"
        print(f"{LABEL[tag]:>12}{m['mode']:>8}{m['f']:>11.5f}{df:>10}"
              f"{m['Q0']:>10,.0f}{dqp:>8}{m['pm']*100:>9.3f}")

print("\nCONTRAST TEST — does the mode that SHOULD move, move?")
for mode in ("TE011", "TM020"):
    b = ref.get(mode)
    row = []
    for tag, _e in CASES[1:]:
        m = next((x for x in res[tag] if x["mode"] == mode), None)
        row.append((LABEL[tag], (m["f"] - b["f"]) * 1000 if (m and b) else None,
                    100 * (m["Q0"] / b["Q0"] - 1) if (m and b and m["Q0"]) else None))
    if any(r[1] is None for r in row):
        print(f"  {mode}: a case is missing this mode — read the peak lists")
        continue
    print(f"  {mode}: " + "   ".join(f"{n} {d:+.2f} MHz ({q:+.2f}% Q)"
                                     for n, d, q in row))
    big = max(abs(d) for _n, d, _q in row)
    mono = abs(row[1][1]) > abs(row[0][1])
    print(f"        max |df| {big:.2f} MHz, "
          + ("grows with hole diameter" if mono else "does NOT grow with diameter"))
print("""
Read: TE011 flat AND TM020 moving monotonically with diameter => the null on
TE011 is physical, the aperture theory holds, and the chimney is free for the
operating mode. Both flat => the run is only as good as its ~1-3 MHz scatter and
proves nothing. TE011 moving => entry 53's chimney needs a redesign or a
recessed cap.""", flush=True)
