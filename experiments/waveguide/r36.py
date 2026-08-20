#!/usr/bin/env python3
"""R36 — what does machining OVALITY do to the design point?

The gap this closes: every non-axisymmetric feature ever put into this model
(loop, viewport) is m=1. Ovality is m=2, and had never been simulated at all;
the roundness figure on the drawing rests on a two-level estimate in FINDINGS
that predicts 2.4-9.7% mixing over +/-0.05 to +/-0.20 mm.

PRE-REGISTERED PREDICTION (written before the first solve, so it can be wrong
in public). First-order cavity perturbation theory says a wall deformation
delta_a(phi) = ov*cos(2phi) shifts a mode by an integral of delta_a against
|field|^2 over phi. For an m=0 mode -- and BOTH modes we care about are m=0,
TE011 and TM020 -- |field|^2 has no phi dependence, so that integral is
    int cos(2phi) dphi = 0  exactly.
So I expect:

  * TE011 and TM020 shift only at SECOND order, i.e. hardly at all: well under
    1 MHz at ov = 0.2 mm. The FINDINGS estimate of df ~ delta*f = 4.8 MHz is a
    DOUBLET-SPLITTING formula and does not apply to either operating mode.
  * The m=+/-1 TM111 pair, which the brake exists to separate from TE011, DOES
    split at first order -- ovality couples m and m+2, so +1 and -1 mix.
  * Q0 of TE011 changes negligibly.

If TE011 moves by MHz here, the prediction is wrong and the tolerance is real.
Either way the drawing gets a measured number instead of an estimate.

Method: one common size-factor across all four cases (meshsweep, R27), driven
solves (the standing policy says eigenmode-derived values are suspect), every
peak in the band reported -- not just the two we expect -- so a mode moving in
from outside cannot hide.
"""
import json, os, pathlib, subprocess, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
import meshsweep

PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
# palace shells out to mpiexec, which lives in the emsim env and NOT on a bare
# login PATH. Without this the wrapper exits rc=1 in 0 s with "Could not locate
# MPI launcher" -- which the driver then reports as "no peaks", i.e. a solver
# that never ran looks exactly like a cavity with no resonance. Cost: one
# 4-solve sweep. recheck_queue.py carries the same block for the same reason.
HOME = pathlib.Path.home()
ENV = {**os.environ,
       "PATH": f"{HOME}/.local/share/mamba/envs/emsim/bin:{os.environ['PATH']}",
       "MAMBA_ROOT_PREFIX": str(HOME / ".local/share/mamba")}
BASE = json.loads(pathlib.Path("w890.json").read_text())

A = "103.70"           # refined design point
L = "88.53"            # quartz development length (R46)
BASE_ARGS = ["--radius", A, "--length", L, "--brake", "3", "--sectors", "1",
             "--order", "2", "--loop", "12,8.5,1,0.3", "--loop-tilt", "45"]

# peak radial deviation in mm == the roundness tolerance on the drawing
CASES = [("ov000", "0.00"), ("ov005", "0.05"), ("ov010", "0.10"),
         ("ov020", "0.20")]


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
        # A solve that returns in seconds did not solve anything. Say so here
        # rather than let an empty peak list read as a physical result.
        print(f"    🔴 {tag} DID NOT SOLVE — last line of {tag}_p.log:",
              flush=True)
        tail = pathlib.Path(f"{tag}_p.log").read_text().strip().splitlines()
        print(f"    {tail[-1] if tail else '(empty log)'}", flush=True)
        if rc != 0:
            return []
    return dq.report(tag)


print(__doc__)
print("=" * 78, flush=True)

fac, ok = meshsweep.sweep([(t, ["--ovality", ov]) for t, ov in CASES],
                          BASE_ARGS)
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")

results = {}
for tag, ov in CASES:
    print(f"\n=== ovality +/-{ov} mm  (a = {A} -> semi-axes "
          f"{float(A)+float(ov):.2f} / {float(A)-float(ov):.2f})", flush=True)
    peaks = solve(tag)
    results[tag] = peaks
    for m in peaks:
        print(f"    {m['mode']:>6}  f={m['f']:.5f}  Q0={m['Q0']:>9,.0f}  "
              f"boreE={m['pe']*100:6.3f}%  boreH={m['pm']*100:6.3f}%",
              flush=True)
    if not peaks:
        print("    NO PEAKS — check the log before reading anything into this",
              flush=True)

print("\n" + "=" * 78)
ref = {m["mode"]: m for m in results.get("ov000", [])}
print(f"{'ovality':>9}{'mode':>8}{'f (GHz)':>11}{'df (MHz)':>10}"
      f"{'Q0':>10}{'dQ %':>8}{'boreH %':>9}{'peaks':>7}")
for tag, ov in CASES:
    for m in results[tag]:
        b = ref.get(m["mode"])
        df = f"{(m['f']-b['f'])*1000:+.2f}" if b else "--"
        dq_ = f"{100*(m['Q0']/b['Q0']-1):+.2f}" if b and m["Q0"] and b["Q0"] else "--"
        print(f"{ov:>9}{m['mode']:>8}{m['f']:>11.5f}{df:>10}"
              f"{m['Q0']:>10,.0f}{dq_:>8}{m['pm']*100:>9.3f}"
              f"{len(results[tag]):>7}")
print("""
Read: df for TE011 and TM020 is the whole question. Near zero => ovality is a
second-order effect on both m=0 modes, the FINDINGS estimate was the wrong
formula, and the roundness tolerance can be a routine one. MHz-scale df, or a
peak count that changes with ovality, means a mode is being mixed or dragged in
and the tolerance is load-bearing.""", flush=True)
