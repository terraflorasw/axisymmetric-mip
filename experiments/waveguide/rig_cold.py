#!/usr/bin/env python3
"""The COLD resonance of the R74 geometry, coarse then fine.

R75 flagged this as the missing number: every lit result sits on wbarrel.msh, but
the UNLIT resonance of that same geometry has never been measured, so the
cold -> lit excursion the amplifier must cross is unknown for the thing we
actually simulated. R10's +16-24 MHz is a DIFFERENT geometry.

⚠️ THE TRAP THIS IS BUILT AROUND. R74 swept at 0.2 MHz. A high-Q cold resonance
can be narrower than one step, and a sweep that steps over a resonance does not
report a small peak -- it reports NO peak, or a peak at whatever sample happened
to land nearest. That is reproducibility.linewidth_step_bias, which already cost
this project a Q measurement (9,785-16,568 wide-band vs 31,304 at 2 kHz on the
SAME mesh). So: locate coarse, then resolve fine, and MEASURE THE BIAS BETWEEN
THEM rather than assuming the fine one is right.

🔑 HOW WIDE IS THE COLD RESONANCE, ACTUALLY? Worth predicting before measuring,
because it sets the step and a wrong guess wastes the run:

    design coupler   Q0 45,728, beta 1.46  -> Q_L 18,600 -> linewidth 0.13 MHz
    sc06 (THIS mesh) Q0 ~36,000 (R70: -21%), Q_ext 1,084 -> beta ~33
                                          -> Q_L ~1,060  -> linewidth ~2.3 MHz

R75 quoted 0.13 MHz, which is right for the DESIGN loop and wrong for this mesh:
sc06 is badly overcoupled unlit (R70), and overcoupling BROADENS the loaded
resonance. Predicting ~2.3 MHz here. The coarse step is 0.05 MHz so that the
prediction being wrong by 4x still leaves the peak resolved, and the driver
refuses to report a linewidth it did not resolve.

ONE MESH, and ONE key different from the lit runs. Same hash-pinned wbarrel.msh,
same config builder, same order. The plasma attribute gets air instead of a
conductor -- literally the lit material with "Conductivity" removed. Nothing else
changes, so the cold-lit difference cannot be a configuration difference.

STAGE 1  COARSE  2.36-2.46 GHz at 0.05 MHz (2001 points) -> locate, and measure
                 the linewidth well enough to CHOOSE the fine step.
STAGE 2  FINE    peak +/- 3 linewidths at linewidth/25 -> resolve.

Q is taken two independent ways at each stage, which is what makes the pair a
check rather than a repetition:
    Q0  = omega*U/P_abs      an ENERGY ratio. No linewidth, no peak-finding.
    Q_L = f/FWHM(U)          a LINEWIDTH. No energy.
    beta = Q0/Q_L - 1        their ratio, so no reciprocal difference anywhere.
Q0 is immune to step bias and Q_L is not, so disagreement between them across the
two stages localises the error instead of averaging it away.
"""
import hashlib
import json
import math
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
import solveconf
import solver

MESH = "wbarrel.msh"
MESH_MD5 = "ca8ca503 11b9b80ccebdc4546a8719e3".replace(" ", "")
COARSE_BAND, COARSE_STEP = (2.36, 2.46), 5e-5
FINE_HALFWIDTHS, FINE_PTS_PER_LW, FINE_MAX_PTS = 3.0, 25.0, 800
MIN_PTS_ACROSS_FWHM = 5
MIN_CONTRAST = 5.0
LIT_F30, LIT_ETA30 = 2.41020, 0.7931     # R74 sigma = 30, same mesh
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
# --replay re-runs only the ANALYSIS over postpro/ already on disk. The FINE
# stage always solves: its window is chosen from the coarse result, so a
# replayed fine stage could be a window computed for a different peak.
REPLAY = "--replay" in sys.argv


def build(tag, band, step):
    """The LIT config with 'Conductivity' removed. That is the whole difference."""
    meta = solveconf.load_meta(MESH)
    pl = meta["attributes"].get("plasma")
    if pl is None:
        raise RuntimeError(f"{MESH}: no plasma attribute in the sidecar")
    c, meta, dropped = solveconf.driven(
        MESH, tag, band, step=step, order=1,
        materials={pl: {"Permittivity": 1.0, "Permeability": 1.0}})
    for d in dropped:
        print(f"    dropped: {d}", flush=True)
    c["Domains"]["Postprocessing"]["Energy"].append(
        {"Index": 90, "Attributes": [pl]})
    c["Boundaries"].setdefault("Postprocessing", {})["SurfaceFlux"] = [
        {"Index": 1, "Attributes": [meta["attributes"]["pec"]], "Type": "Power"}]
    # Prove the cavity is COLD: a stray Conductivity here would silently make
    # this another lit run, and it would look entirely plausible.
    for m in c["Domains"]["Materials"]:
        if m["Attributes"] == [pl] and "Conductivity" in m:
            raise RuntimeError("plasma attribute still carries a Conductivity — "
                               "this is not a cold run")
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    return meta


def run(tag, band, step, label):
    n = int(round((band[1] - band[0]) / step)) + 1
    print(f"\n{label}: {band[0]:.5f}-{band[1]:.5f} GHz, step {1e6*step:.4g} kHz, "
          f"{n} points", flush=True)
    if REPLAY and tag == "cold_c" and (pathlib.Path("postpro") / tag /
                                       "port-S.csv").exists():
        recs = dq.load(tag)
        print(f"  replay from postpro/{tag}: {len(recs)} samples", flush=True)
        return recs
    build(tag, band, step)
    t0 = time.time()
    rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"], env=solver.ENV,
                        stdout=open(f"{tag}_p.log", "w"),
                        stderr=subprocess.STDOUT,
                        timeout=solver.DEFAULT_TIMEOUT_S).returncode
    dt = time.time() - t0
    if rc or dt < solver.MIN_SECONDS:
        tail = pathlib.Path(f"{tag}_p.log").read_text().strip().splitlines()
        raise RuntimeError(f"{tag}: rc={rc} in {dt:.0f}s — "
                           f"{tail[-1] if tail else '(empty log)'}")
    recs = dq.load(tag)
    if not recs:
        raise RuntimeError(f"{tag}: solved in {dt:.0f}s but produced no records")
    print(f"  {dt:.0f}s, {len(recs)} samples", flush=True)
    return recs


def candidates(recs, rel=0.02):
    """Every resonance in the window: local maxima of STORED ENERGY."""
    U = [r["U"] for r in recs]
    um = max(U)
    return [i for i in range(2, len(U) - 2)
            if U[i] == max(U[i - 2:i + 3]) and U[i] > rel * um]


def pick_te011(recs, cands):
    """🔴 argmax(U) IS NOT A MODE IDENTIFIER, and the first version of this file
    used it. It selected the resonance with the most stored energy, which is the
    one the LOOP COUPLES BEST TO — here a third mode at 2.4304 with eta 46.5%,
    not TE011 at 2.3975 with eta 11.1%. It then reported that mode's beta (0.17)
    and a cold->lit excursion of the wrong sign.

    This is the project's own standing rule broken in a new spelling: identify a
    mode by WHERE ITS ENERGY IS, never by a global scalar that coupling strength
    also drives. argmin|S11| and argmax(U) are the same error.

    TE011's signature is BORE MAGNETIC fraction: it is the mode whose H fills the
    torch bore. TM020 is bore-ELECTRIC and separates 15x the other way.
    """
    return max(cands, key=lambda i: recs[i]["pm"])


def analyse(recs, stage, i=None):
    """FWHM by interpolation about sample `i` (the identified TE011 peak)."""
    U = [r["U"] for r in recs]
    f = [r["f"] for r in recs]
    if i is None:
        c = candidates(recs)
        i = pick_te011(recs, c) if c else max(range(len(U)), key=lambda j: U[j])
    contrast = U[i] / min(U) if min(U) > 0 else float("inf")
    edge = i < 3 or i >= len(U) - 3
    half = U[i] / 2.0

    def cross(rng):
        prev = i
        for j in rng:
            if U[j] < half:
                # linear interpolation between the bracketing samples
                t = (U[prev] - half) / (U[prev] - U[j])
                return f[prev] + t * (f[j] - f[prev]), True
            prev = j
        return None, False

    lo, ok_lo = cross(range(i - 1, -1, -1))
    hi, ok_hi = cross(range(i + 1, len(U)))
    fwhm = (hi - lo) if (ok_lo and ok_hi) else None
    ql = (f[i] / fwhm) if fwhm else None
    npts = (fwhm / (f[1] - f[0])) if fwhm else 0.0
    eta = 1.0 - recs[i]["gamma"] ** 2
    q0 = recs[i]["Q0"]
    beta = (q0 / ql - 1.0) if ql else None
    return dict(stage=stage, i=i, f=f[i], U=U[i], eta=eta, q0=q0, ql=ql,
                fwhm=fwhm, beta=beta, npts=npts, contrast=contrast, edge=edge,
                pm=recs[i]["pm"], s_db=recs[i]["s_db"],
                span=(f[0], f[-1]))


def report(a):
    print(f"  peak (stored energy) at {a['f']:.6f} GHz   contrast "
          f"{a['contrast']:.0f}x   |S11| {a['s_db']:.2f} dB   eta "
          f"{100*a['eta']:.1f}%")
    if a["fwhm"]:
        print(f"  FWHM {1e3*a['fwhm']:.3f} MHz over {a['npts']:.1f} samples   "
              f"Q_L {a['ql']:,.0f}   Q0 {a['q0']:,.0f}   beta {a['beta']:.2f}")
    else:
        print("  🔴 FWHM NOT BRACKETED inside the window — cannot quote a "
              "linewidth")
    print(f"  bore-H {a['pm']:.5f}")
    bad = []
    if a["edge"]:
        bad.append("peak within 3 samples of a window edge — it may be outside")
    if a["contrast"] < MIN_CONTRAST:
        bad.append(f"contrast only {a['contrast']:.1f}x — this window may hold "
                   "no resonance at all")
    if a["fwhm"] and a["npts"] < MIN_PTS_ACROSS_FWHM:
        bad.append(f"only {a['npts']:.1f} samples across the FWHM — the "
                   "linewidth is STEP-LIMITED, not measured")
    for b in bad:
        print(f"  🔴 {b}")
    return not bad


print(__doc__)
print("=" * 78, flush=True)
h = hashlib.md5(pathlib.Path(MESH).read_bytes()).hexdigest()
if h != MESH_MD5:
    sys.exit(f"🔴 {MESH} hash {h} != pinned {MESH_MD5} — not the R74 geometry.")
m = solveconf.load_meta(MESH)
print(f"  mesh FROZEN: {MESH}  {m['tets']:,} tets  size-factor {m['size_factor']}"
      f"  md5 {h[:8]}   (same mesh as R73/R74)")

recs_c = run("cold_c", COARSE_BAND, COARSE_STEP, "STAGE 1  COARSE")
cands = candidates(recs_c)
print(f"\n  {len(cands)} resonance(s) in the band — TE011 is picked by BORE-H, "
      f"not by size:")
print(f"    {'f (GHz)':>10}{'U/Umax':>9}{'bore-H':>9}{'bore-E':>10}{'eta':>8}"
      f"{'Q0':>9}")
um = max(r["U"] for r in recs_c)
te = pick_te011(recs_c, cands) if cands else None
for i in cands:
    r = recs_c[i]
    print(f"    {r['f']:>10.4f}{r['U']/um:>9.2f}{r['pm']:>9.5f}{r['pe']:>10.6f}"
          f"{100*(1-r['gamma']**2):>7.1f}%{r['Q0']:>9.0f}"
          + ("   <- TE011 (max bore-H)" if i == te else ""))
if te is not None and recs_c[te]["U"] < 0.9 * um:
    print("  ⚠️ TE011 is NOT the largest peak here. argmax(U) would have picked "
          "a different\n     mode — which is exactly the bug this selection "
          "replaces.")
co = analyse(recs_c, "coarse", te)
print("\nSTAGE 1 RESULT"); ok = report(co)
if co["edge"] or co["contrast"] < MIN_CONTRAST:
    sys.exit("\n🔴 the coarse stage did not find a usable resonance. Widen the "
             "band or reduce the step; do NOT read a fine sweep placed from this.")
if not co["fwhm"]:
    sys.exit("\n🔴 no bracketed FWHM, so there is no linewidth to size the fine "
             "step from. Refusing to guess.")

lw = co["fwhm"]
step = max(1e-6, lw / FINE_PTS_PER_LW)
half = FINE_HALFWIDTHS * lw
if 2 * half / step > FINE_MAX_PTS:
    step = 2 * half / FINE_MAX_PTS
band = (co["f"] - half, co["f"] + half)
print(f"\n  fine window from the MEASURED coarse linewidth: "
      f"{co['f']:.5f} +/- {1e3*half:.3f} MHz at {1e6*step:.1f} kHz")
fi = analyse(run("cold_f", band, step, "STAGE 2  FINE"), "fine")
print("\nSTAGE 2 RESULT"); ok_f = report(fi)

print("\n" + "=" * 78)
print("STEP BIAS — the reason for doing this twice")
print(f"{'':>10}{'f (GHz)':>13}{'FWHM MHz':>11}{'Q_L':>10}{'Q0':>10}{'beta':>8}"
      f"{'pts/FWHM':>10}")
for a in (co, fi):
    print(f"{a['stage']:>10}{a['f']:>13.6f}"
          f"{(1e3*a['fwhm'] if a['fwhm'] else float('nan')):>11.3f}"
          f"{(a['ql'] or float('nan')):>10,.0f}{a['q0']:>10,.0f}"
          f"{(a['beta'] or float('nan')):>8.2f}{a['npts']:>10.1f}")
if co["ql"] and fi["ql"]:
    bias = fi["ql"] / co["ql"]
    dq0 = fi["q0"] / co["q0"]
    print(f"\n  Q_L fine/coarse = {bias:.3f}   Q0 fine/coarse = {dq0:.3f}")
    if abs(bias - 1) < 0.05:
        print("  ✅ NO STEP BIAS: the coarse sweep already resolved this "
              "resonance. Q_L is real.")
    else:
        print(f"  ⚠️ the coarse linewidth was biased {1/bias:.2f}x — as "
              "expected when a step\n     is a significant fraction of the "
              "FWHM. THE FINE VALUE IS THE MEASUREMENT.")
    if abs(dq0 - 1) > 0.05:
        print(f"  🔴 Q0 ALSO MOVED by {dq0:.2f}x. Q0 is an energy ratio and "
              "should NOT depend on\n     the step. If it did, the two stages "
              "are not on the same resonance.")
    else:
        print("  ✅ Q0 is step-independent, as an energy ratio must be — the "
              "two stages agree\n     on WHICH resonance this is.")

print("\nMODE CHECK")
print(f"  bore-H fraction {fi['pm']:.5f}   (R70's unlit TE011 discriminator: "
      "0.019-0.021)")
print("  ⚠️ diagnostic only. R70's range was measured on OTHER unlit meshes; "
      "sc06 perturbs\n     the mode hard (Q0 -21%, 17.2 MHz pull), so a "
      "mismatch is not by itself\n     a misidentification.")

print("\n🔑 THE NUMBER R75 ASKED FOR — the cold -> lit excursion of THIS geometry")
d = 1e3 * (LIT_F30 - fi["f"])
print(f"  cold  {fi['f']:.5f} GHz   Q_L {fi['ql']:,.0f}   FWHM "
      f"{1e3*fi['fwhm']:.3f} MHz   |S11| {fi['s_db']:.2f} dB")
print(f"  lit   {LIT_F30:.5f} GHz   (R74, sigma = 30, same mesh, "
      f"eta {100*LIT_ETA30:.1f}%)")
print(f"  🔢 EXCURSION {d:+.1f} MHz = {abs(d)/(1e3*fi['fwhm']):.1f} COLD "
      f"linewidths, {abs(d)/11.0:.1f} lit linewidths")
print("\n  What the amplifier must do, in one line: acquire a "
      f"{1e3*fi['fwhm']:.2f} MHz target,\n  then follow it {abs(d):.1f} MHz "
      "while it broadens to ~11 MHz.")
print("\n⚠️ Order 1, one mesh density, sc06's loop. The cold frequency is "
      "order-1 RAW —\n   add offset.te011 (+24.54 MHz, geometry-dependent) "
      "before any band-placement claim.")
print(flush=True)
