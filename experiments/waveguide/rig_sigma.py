#!/usr/bin/env python3
"""R74 — does R73's answer survive sigma? eta(sigma) on ONE frozen mesh.

R73 measured 78.8% of input power into the plasma and dissolved the "coupling
crisis". It closed with its own warning, which is now the register:

    sigma = 30 S/m is still the bare literal at r12.py:26, error null (R67).
    eta scales with it. The RATIOS between cases are safe; 78.8% is not.

R67 named the fixed point that was never solved for -- sigma, Q and P_abs are
mutually determined -- and could not test it, because Q is undefined where the
lit cavity lives. eta has no denominator, so the test is now posable: hold the
geometry fixed, move the one unmeasured literal, and read delivered power.

WHAT THE SAMPLE SET BUYS: THE SHAPE OF eta(sigma), NOT A BETTER VALUE.

This is falsification, not optimisation. Nothing here picks a design; it asks
whether the design's headline number depends on a guess. Seven points, one per
half-decade-ish, spanning the plausible plasma range end to end:

    0.3   1   3   10   30   100   300  S/m

  0.3-3    MP-AES class, n_e ~ 1e13 cm^-3. R67: at ~0.3 the ALREADY-MEASURED
           bare loop is critically coupled, i.e. the crisis was manufactured.
  10-30    the assumed value and its neighbourhood.
  100-300  ICP class, n_e ~ 1e15. R68 walked R67 back to here being defensible.

eta(sigma) MUST be non-monotonic, and that is the whole point. At sigma -> 0
there is no absorber and the power comes back; at sigma -> inf the plasma is a
mirror with no skin depth and the power comes back. Somewhere between is a
match. THE QUESTION IS WHERE 30 SITS ON THAT CURVE:

  - on a broad plateau  -> 78.8% is robust and R67 stops being load-bearing;
  - on a narrow peak    -> 78.8% is a best case, any real plasma is worse, and
                           sigma must be measured before anything is built;
  - on a steep flank    -> the design is a tuning problem, not a geometry one.

METHOD, and what it deliberately does NOT do:

  ONE MESH, FROZEN. Every case is the SAME wbarrel.msh that produced R73's
  78.8%, hash-pinned below. No remeshing, so the two silent no-ops that have
  faked results here (MeshSizeExtendFromBoundary, MeshSizeMin) cannot occur --
  not because they were checked, but because nothing is rebuilt. Only the
  material conductivity on the plasma attribute changes between cases.

  A KNOWN-ANSWER CASE INSIDE THE SWEEP. sigma = 30 must reproduce R73 exactly:
  eta_total = 79.3% at f = 2.4102. The band is wider here (2.38-2.48 vs
  2.40-2.46) but the grid is the same 2e-4 step and contains 2.4102, so a
  mismatch means the harness moved, and nothing else in the run is believable.

  NO PEAK-FINDING, NO MODE ID, NO Q -- as R73. eta is the max of 1-|Gamma|^2
  over the band.

  BRACKETING IS CHECKED. A maximum at a window edge is not a maximum; that
  exact failure once reported a resonance for a mode that had left the band.
  Any case whose f@max lands within 3 samples of an edge is flagged UNBRACKETED
  and its eta is a lower bound, not a measurement.

DECOMPOSITION (verified against R73's numbers before this was written):

    eta_wall   = Phi_pow[1] / (2 * P_inc)        entry 107's 2x convention
    eta_plasma = (sigma/eps0) * E_elec[90] / P_inc
    residual   = eta_total - eta_wall - eta_plasma   -> dielectric

  On R73's barrel: 0.501% + 78.59% = 79.09% against eta_total 79.31%, closing
  to 0.22 points. If a case fails to close, only eta_total is quoted for it.

  eta_plasma is computed INDEPENDENTLY from the plasma-region field energy, not
  by subtracting the wall from the total. That is what makes closure a test
  rather than a definition.

DIAGNOSTIC, NOT A GATE: bore magnetic fraction p_mag[1] at f@max is printed so
the mode's character can be tracked across sigma. R73's barrel sat at 0.00433.
A collapse would say the heated mode is no longer the intended geometry -- an
analytical-performance question, not a power one, and it does not invalidate a
watt.

VERDICTS: this driver reports one of PLATEAU / PEAK / FLANK, and says what each
means for R67. It does not propose a geometry change either way.
"""
import csv
import hashlib
import math
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
import solveconf
import solver

EPS0 = 8.8541878128e-12
MESH = "wbarrel.msh"
# Pinned to the exact mesh that produced R73. A different hash is a hard stop:
# comparing eta across sigma is only meaningful on one geometry at one density.
MESH_MD5 = "ca8ca50311b9b80ccebdc4546a8719e3"
SIGMAS = [0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0]
BAND = (2.38, 2.48)
STEP = 2e-4
EDGE_SAMPLES = 3
# R73's measured point, which sigma = 30 has to land on again.
KNOWN = dict(sigma=30.0, f=2.4102, eta=0.7931, f_tol=5e-4, eta_tol=0.005)
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
# --replay re-runs only the ANALYSIS over postpro/ already on disk.
REPLAY = "--replay" in sys.argv


def tag_for(sig):
    return "s" + f"{sig:g}".replace(".", "p")


def build_cfg(mesh, tag, sigma):
    meta = solveconf.load_meta(mesh)
    pl = meta["attributes"].get("plasma")
    if pl is None:
        raise RuntimeError(f"{mesh}: no plasma attribute in the sidecar")
    c, meta, dropped = solveconf.driven(
        mesh, tag, BAND, step=STEP, order=1,
        materials={pl: {"Permittivity": 1.0, "Permeability": 1.0,
                        "Conductivity": sigma}})
    for d in dropped:
        print(f"    dropped: {d}", flush=True)
    c["Domains"]["Postprocessing"]["Energy"].append(
        {"Index": 90, "Attributes": [pl]})
    c["Boundaries"].setdefault("Postprocessing", {})["SurfaceFlux"] = [
        {"Index": 1, "Attributes": [meta["attributes"]["pec"]], "Type": "Power"}]
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    # Read the conductivity back OUT of the written config. A material silently
    # dropped onto an absent attribute is the R50 failure this guards.
    wrote = [m for m in json.loads(pathlib.Path(f"{tag}.json").read_text())
             ["Domains"]["Materials"] if m.get("Conductivity") == sigma]
    if not wrote:
        raise RuntimeError(f"{tag}: sigma={sigma} is not in the written config")
    return meta


def _col(rows, i, name):
    for k, v in rows[i].items():
        if k and name.lower() in k.lower():
            return float(v)
    return None


def decompose(tag, sigma, idx):
    """eta_wall and eta_plasma at sample `idx`, each measured independently."""
    d = pathlib.Path("postpro") / tag
    V = list(csv.DictReader(open(d / "port-V.csv")))
    I = list(csv.DictReader(open(d / "port-I.csv")))
    pinc = 0.5 * _col(V, 0, "V_inc") * _col(I, 0, "I_inc")
    en = list(csv.DictReader(open(d / "domain-E.csv")))
    sf = list(csv.DictReader(open(d / "surface-F.csv")))
    wall = _col(sf, idx, "pow") / (2.0 * pinc)
    plasma = (sigma / EPS0) * _col(en, idx, "E_elec[90]") / pinc
    return wall, plasma


print(__doc__)
print("=" * 78, flush=True)

h = hashlib.md5(pathlib.Path(MESH).read_bytes()).hexdigest()
if h != MESH_MD5:
    sys.exit(f"🔴 {MESH} hash {h} != pinned {MESH_MD5}. The mesh moved since "
             "R73; re-pin deliberately or rebuild, but do not compare across it.")
meta0 = solveconf.load_meta(MESH)
print(f"  mesh FROZEN: {MESH}  {meta0['tets']:,} tets  "
      f"size-factor {meta0['size_factor']}  md5 {h[:8]}")
print(f"  band {BAND[0]}-{BAND[1]} GHz, step {STEP} "
      f"({int(round((BAND[1]-BAND[0])/STEP))+1} samples), order 1\n", flush=True)

rows = []
for sigma in SIGMAS:
    tag = tag_for(sigma)
    try:
        build_cfg(MESH, tag, sigma)
    except Exception as e:
        print(f"  🔴 sigma={sigma}: {e}", flush=True)
        continue
    t0 = time.time()
    if REPLAY and (pathlib.Path("postpro") / tag / "port-S.csv").exists():
        # Re-analyse an existing solve. Only ever skips work that is already on
        # disk; a missing case still solves, so a replay is never a subset of
        # the sweep without saying so.
        print(f"  replay sigma={sigma:g} from postpro/{tag}", flush=True)
        rc, dt = 0, solver.MIN_SECONDS + 1
    else:
        rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"], env=solver.ENV,
                            stdout=open(f"{tag}_p.log", "w"),
                            stderr=subprocess.STDOUT,
                            timeout=solver.DEFAULT_TIMEOUT_S).returncode
        dt = time.time() - t0
    if rc or dt < solver.MIN_SECONDS:
        tail = pathlib.Path(f"{tag}_p.log").read_text().strip().splitlines()
        print(f"  🔴 sigma={sigma}: rc={rc} in {dt:.0f}s — "
              f"{tail[-1] if tail else '(empty log)'}", flush=True)
        continue
    recs = dq.load(tag)
    if not recs:
        print(f"  ⚠️ sigma={sigma}: no records", flush=True)
        continue
    idx = max(range(len(recs)),
              key=lambda i: (1.0 - recs[i]["gamma"] ** 2)
              if recs[i].get("gamma") is not None else -1)
    eta = 1.0 - recs[idx]["gamma"] ** 2
    wall, plasma = decompose(tag, sigma, idx)
    edge = idx < EDGE_SAMPLES or idx >= len(recs) - EDGE_SAMPLES
    # eta = 4b/(1+b)^2 has TWO roots. Keep both; the branch test below picks
    # one, using the fact that Q_ext is a coupler property and Q0 is not.
    d = 2.0 * math.sqrt(max(0.0, 1.0 - eta))
    rows.append(dict(sigma=sigma, tag=tag, f=recs[idx]["f"], eta=eta,
                     wall=wall, plasma=plasma,
                     resid=eta - wall - plasma, pm=recs[idx]["pm"],
                     q0=recs[idx]["Q0"], blo=(2 - eta - d) / eta,
                     bhi=(2 - eta + d) / eta,
                     edge=edge, dt=dt))
    flag = "  🔴 UNBRACKETED (max at band edge — lower bound only)" if edge else ""
    print(f"  sigma={sigma:>6g}  {dt:>4.0f}s  f@max={recs[idx]['f']:.5f}  "
          f"eta={100*eta:>5.1f}%  (wall {100*wall:>4.1f}%, plasma "
          f"{100*plasma:>5.1f}%, resid {100*(eta-wall-plasma):>+5.1f})"
          f"  bore-H {recs[idx]['pm']:.5f}{flag}", flush=True)

print("\n" + "=" * 78)
if not rows:
    sys.exit("no usable cases — read the logs, do not interpret this as a null")

print(f"{'sigma':>8}{'f@max':>11}{'eta_tot':>10}{'eta_wall':>10}"
      f"{'eta_plasma':>12}{'resid':>8}{'bore-H':>9}")
for r in rows:
    print(f"{r['sigma']:>8g}{r['f']:>11.5f}{100*r['eta']:>9.1f}%"
          f"{100*r['wall']:>9.1f}%{100*r['plasma']:>11.1f}%"
          f"{100*r['resid']:>+8.1f}{r['pm']:>9.5f}"
          + ("  🔴edge" if r["edge"] else ""))

print("\nCLOSURE")
bad = [r for r in rows if abs(r["resid"]) > 0.05]
if bad:
    print("  ⚠️ decomposition does NOT close for "
          + ", ".join(f"sigma={r['sigma']:g} ({100*r['resid']:+.1f} pts)"
                      for r in bad)
          + "\n     -> quote eta_total ONLY for those. The split is wrong, "
            "not the total.")
else:
    print(f"  ✅ closes within {100*max(abs(r['resid']) for r in rows):.1f} "
          "points everywhere — the split is real, not a subtraction.")

print("\nKNOWN-ANSWER CHECK (sigma = 30 must reproduce R73)")
k = next((r for r in rows if r["sigma"] == KNOWN["sigma"]), None)
if k is None:
    print("  🔴 the sigma = 30 case did not run. Nothing here is validated.")
elif (abs(k["f"] - KNOWN["f"]) > KNOWN["f_tol"]
      or abs(k["eta"] - KNOWN["eta"]) > KNOWN["eta_tol"]):
    print(f"  🔴 REGRESSION: got f={k['f']:.5f} eta={100*k['eta']:.1f}%, "
          f"R73 measured f={KNOWN['f']:.4f} eta={100*KNOWN['eta']:.1f}%.")
    print("     The harness moved. Do not read the sigma trend until this is "
          "explained.")
else:
    print(f"  ✅ f={k['f']:.5f} eta={100*k['eta']:.1f}% reproduces R73 "
          f"({KNOWN['f']:.4f}, {100*KNOWN['eta']:.1f}%). The wider band and the "
          "re-run agree.")

print("\nVERDICT — the SHAPE of eta(sigma), and the FLOOR")
# 🔴 The first version of this block looked for a plateau around a single
# maximum and reported "FLANK, peak at 300" for a curve that is U-SHAPED, with
# maxima at BOTH ends and a minimum in the middle. A unimodal detector on a
# bimodal curve is R71's error again: it returns an answer rather than saying
# the model does not fit. Classify the shape first, and lead with the FLOOR,
# which is well defined whatever the shape.
usable = [r for r in rows if not r["edge"]]
if k is None or len(usable) < 3:
    print("  insufficient bracketed cases to characterise the curve")
else:
    o = sorted(usable, key=lambda r: r["sigma"])
    e = [r["eta"] for r in o]
    lo = min(o, key=lambda r: r["eta"])
    hi = max(o, key=lambda r: r["eta"])
    i_lo, i_hi = e.index(lo["eta"]), e.index(hi["eta"])
    interior_min = 0 < i_lo < len(e) - 1
    interior_max = 0 < i_hi < len(e) - 1
    shape = ("U-SHAPED (matched at both ends, worst in the middle)"
             if interior_min and not interior_max else
             "PEAKED (one interior maximum)" if interior_max and not interior_min
             else "MONOTONIC over the sampled range" if not interior_min
             and not interior_max else "NEITHER — more than one turning point")
    print(f"  shape: {shape}")
    print(f"  🔑 FLOOR = {100*lo['eta']:.1f}% at sigma = {lo['sigma']:g}, over "
          f"sigma = {o[0]['sigma']:g} to {o[-1]['sigma']:g} "
          f"({o[-1]['sigma']/o[0]['sigma']:.0f}x)")
    print(f"  peak  = {100*hi['eta']:.1f}% at sigma = {hi['sigma']:g}; "
          f"sigma = 30 delivers {100*k['eta']:.1f}%")

    # eta cannot say which side of critical coupling we are on: it is symmetric
    # in beta <-> 1/beta. Q_ext = Q0/beta CAN, because it must be a property of
    # the COUPLER and not of the load. The branch whose Q_ext is constant across
    # sigma is the real one.
    print("\n  BRANCH TEST — Q_ext must not depend on the load")
    for name, key in (("beta<1 (undercoupled)", "blo"),
                      ("beta>1 (overcoupled)", "bhi")):
        qs = [r["q0"] / r[key] for r in o if r.get("q0") and r[key] > 0]
        if len(qs) >= 3:
            print(f"    {name:>22}: Q_ext {min(qs):>6.0f}-{max(qs):>6.0f} "
                  f"({max(qs)/min(qs):.1f}x spread)")
    qlo = [r["q0"] / r["blo"] for r in o if r.get("q0") and r["blo"] > 0]
    qhi = [r["q0"] / r["bhi"] for r in o if r.get("q0") and r["bhi"] > 0]
    if len(qlo) >= 3 and len(qhi) >= 3:
        slo, shi = max(qlo) / min(qlo), max(qhi) / min(qhi)
        if slo < shi / 2:
            print("    ✅ UNDERCOUPLED at every sampled sigma — the beta<1 "
                  "branch holds Q_ext\n       roughly constant while beta>1 "
                  "makes it a function of the plasma.")
        elif shi < slo / 2:
            print("    ✅ OVERCOUPLED at every sampled sigma, by the same test.")
        else:
            print("    ⚠️ the test does not separate the branches here — "
                  "neither Q_ext is constant.\n       Do not assign a branch.")

    print("\n  WHERE THE LOSS IS")
    print(f"    eta_plasma / eta_total = "
          + ", ".join(f"{100*r['plasma']/r['eta']:.0f}%" for r in o)
          + f"  (wall never above {100*max(r['wall'] for r in o):.1f}%)")
    if min(r["plasma"] / r["eta"] for r in o) > 0.95:
        print("    🔑 Whatever enters the cavity reaches the plasma at EVERY "
              "sigma. eta is not\n       measuring absorption — it is "
              "measuring the MATCH.")

    print("\n  WHAT THIS DOES TO R67")
    if lo["eta"] >= 0.50:
        print(f"    🔽 DEMOTED as a design gate: delivered power never falls "
              f"below {100*lo['eta']:.1f}%\n       across "
              f"{o[-1]['sigma']/o[0]['sigma']:.0f}x in sigma, so no plausible "
              "plasma produces a coupling crisis.")
        print("    🔼 STILL BINDING on any quoted number — QUOTE THE FLOOR, "
              "NOT THE POINT,\n       until sigma is pinned (audit A5).")
    else:
        print(f"    🔴 BLOCKING: eta falls to {100*lo['eta']:.1f}% at sigma = "
              f"{lo['sigma']:g}. sigma must be pinned\n       before any "
              "number here is quotable.")
    if interior_min:
        print(f"    ⚠️ The worst case (sigma = {lo['sigma']:g}) is in the "
              "MIDDLE of the plausible range,\n       not at an unphysical "
              "extreme. It cannot be dismissed.")

print("\n⚠️ What this still does NOT establish: one geometry (sc06 on the "
      "barrel), one\n   mesh density, order 1, and a plasma region whose SHAPE "
      "(baselines plasma.region)\n   is as assumed as its conductivity was. "
      "This sweep moves sigma and nothing else.")
print(flush=True)
