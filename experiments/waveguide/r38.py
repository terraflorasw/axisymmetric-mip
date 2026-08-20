#!/usr/bin/env python3
"""R38 — re-confirm the +31.6 MHz order-1 → converged offset, driven, at the
current design point.

This is the most load-bearing eigenmode-derived number left in the project.
EVERY "converged" frequency in FINDINGS is a raw order-1 value plus this offset,
including the TM020 band-floor margins written tonight in R39 and R29. The mesh
is sized at 8 elements per wavelength FOR ORDER 2, so an order-1 solve on it is
knowingly under-resolved and the offset is the correction for that.

The first attempt at R38 never answered the question: at L = 90.4 the order-2
solve returned a SINGLE hybridised peak, which is how the TE011/TM020 crossing
was discovered. That crossing was fixed by R44's design point, where the two
modes sit 41.5 MHz apart raw. The question is cleanly askable again.

METHOD — the only thing that varies is Solver.Order.

    o1     order 1, choff.msh          the mesh R29 already solved at order 1
    o2     order 2, choff.msh          SAME MESH, same band, same everything
    o2f    order 2, finer mesh (0.85)  is order 2 itself converged?

Same mesh for o1/o2 matters: R36 showed that separately built meshes carry 1-3
MHz of systematic scatter, which is 10% of the quantity being measured here.
Using one mesh removes that term entirely.

o2f is the check the original offset never had. An offset is only meaningful if
the thing it extrapolates TO is converged. If o2 on a 0.85 mesh lands on o2 at
0.96, order 2 is resolved and the offset is a real correction; if they differ by
MHz, order 2 is not converged either and the offset is extrapolating to a moving
target.

⚠️ Order-2 driven is expensive in memory as well as time — roughly 4x the DOFs.
If a solve dies, the log line says so rather than reporting an empty peak list
as a physical result.
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
# Wide enough to hold both modes at BOTH orders: order 2 is expected to move
# them up by ~30 MHz, and a mode that leaves the window reads as "no peak".
BAND = (2.35, 2.49)
RECORDED_OFFSET = 31.6      # MHz, the number under test


def solve(tag, mesh, order):
    c = json.loads(json.dumps(BASE))
    c["Model"]["Mesh"] = mesh
    c["Problem"]["Output"] = f"postpro/{tag}"
    c["Solver"]["Order"] = order
    c["Solver"]["Driven"]["Samples"] = [{"Type": "Linear", "MinFreq": BAND[0],
                                         "MaxFreq": BAND[1], "FreqStep": 2e-5}]
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    t0 = time.time()
    rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"], env=ENV,
                        stdout=open(f"{tag}_p.log", "w"),
                        stderr=subprocess.STDOUT).returncode
    dt = time.time() - t0
    print(f"  {tag}: order {order} on {mesh}, rc={rc} in {dt:.0f}s", flush=True)
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
    if len(out) < 2:
        print("     ⚠️ fewer than two modes found — check for hybridisation "
              "before differencing anything (this is how R38 failed last time)",
              flush=True)
    return out


print(__doc__)
print("=" * 78, flush=True)

if not pathlib.Path("choff.msh").exists():
    sys.exit("choff.msh missing — rebuild it with r29.py's base args first")

print("\n=== o1: order 1, choff.msh (size-factor 0.96)")
o1 = solve("r38o1", "choff.msh", 1)

print("\n=== o2: order 2, SAME MESH")
o2 = solve("r38o2", "choff.msh", 2)

print("\n=== o2f: order 2, finer mesh — is order 2 itself converged?")
o2f = []
g = meshsweep.build("r38fine", BASE_ARGS, [], "0.85")
if g.returncode != 0:
    for line in (g.stderr or g.stdout or "").strip().splitlines()[-3:]:
        print(f"    {line}")
    print("  finer mesh would not build — convergence check SKIPPED, and the "
          "offset below is therefore unchecked against mesh density", flush=True)
else:
    o2f = solve("r38o2f", "r38fine.msh", 2)

print("\n" + "=" * 78)
d1 = {m["mode"]: m for m in o1}
d2 = {m["mode"]: m for m in o2}
d2f = {m["mode"]: m for m in o2f}
print(f"{'mode':>7}{'order 1':>11}{'order 2':>11}{'OFFSET':>10}"
      f"{'order2 fine':>13}{'o2 drift':>10}")
for mode in ("TE011", "TM020"):
    a_, b_ = d1.get(mode), d2.get(mode)
    if not (a_ and b_):
        print(f"{mode:>7}   missing from one of the solves — no offset")
        continue
    off = (b_["f"] - a_["f"]) * 1000
    c_ = d2f.get(mode)
    fine = f"{c_['f']:.5f}" if c_ else "--"
    drift = f"{(c_['f']-b_['f'])*1000:+.2f}" if c_ else "--"
    print(f"{mode:>7}{a_['f']:>11.5f}{b_['f']:>11.5f}{off:>+10.2f}"
          f"{fine:>13}{drift:>10}")

te = (d1.get("TE011"), d2.get("TE011"))
if all(te):
    off = (te[1]["f"] - te[0]["f"]) * 1000
    err = off - RECORDED_OFFSET
    print(f"\nTE011 offset measured {off:+.2f} MHz vs the recorded "
          f"{RECORDED_OFFSET:+.1f} MHz → {err:+.2f} MHz")
    if abs(err) <= 2.0:
        print("  ✅ the recorded offset is confirmed at the current geometry")
    else:
        print("  🔴 the recorded offset is WRONG at the current geometry. Every "
              "converged frequency in FINDINGS inherits this error, including "
              "the TM020 band-floor margins.")
tm = (d1.get("TM020"), d2.get("TM020"))
if all(tm):
    print(f"TM020 offset measured {(tm[1]['f']-tm[0]['f'])*1000:+.2f} MHz "
          f"(19.7 was assumed in R39/R29 — it was never measured)")
if d2f:
    ok = all(abs(d2f[m]["f"] - d2[m]["f"]) * 1000 < 1.0
             for m in d2f if m in d2)
    print("\n" + ("  ✅ order 2 is converged: the finer mesh agrees within 1 MHz"
                  if ok else
                  "  🔴 order 2 is NOT converged — the offset extrapolates to a "
                  "moving target and needs a Richardson treatment, not a "
                  "single number"))
print(flush=True)
