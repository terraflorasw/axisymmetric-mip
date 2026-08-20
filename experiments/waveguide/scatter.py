#!/usr/bin/env python3
"""Random scatter over loop geometry — break the axis-aligned sweep.

§12 grew the loop along ONE DIAGONAL (12x17, 20x28, 28x40, 36x52 — aspect ratio
~1.4 throughout) and found Q_ext essentially flat: 5.5x in area for 12% in Q_ext,
a log-log slope of -0.07 where geometry predicts -2. The explanation offered at
the time (loop self-reactance) was falsified by R62.

A flat 1-D sweep through a DEGENERATE DIRECTION and a genuinely flat surface look
identical from the surface. Scattering breaks that: if Q_ext depends differently
on radial depth than on half-width, points off the diagonal will show it.

Affordable only because of the narrow-band result: solves went from 15-40 min to
~30 s once the band matches the linewidth instead of exceeding it 2,600-fold.

TWO STAGES PER POINT, because the resonance MOVES with loop geometry (§12 saw
134 MHz) and a narrow band centred on a fixed frequency would simply miss it:
  1. coarse locate — wide band, only the peak POSITION is needed
  2. narrow re-solve at that position — accurate Q_ext, no linewidth bias

Kept inside the safe regime (area <= 1100 mm^2): §12 showed 1872 mm^2 destroys
the mode, 1120 survived.
"""
import json, math, os, pathlib, random, subprocess, sys, time
W = pathlib.Path(__file__).parent
sys.path.insert(0, str(W)); os.chdir(W)
import dq, modes, solveconf

PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
H = pathlib.Path.home()
ENV = {**os.environ, "PATH": f"{H}/.local/share/mamba/envs/emsim/bin:" + os.environ["PATH"],
       "MAMBA_ROOT_PREFIX": str(H / ".local/share/mamba")}
MM = H / ".local/bin/micromamba"
BASE = ["--radius", "103.70", "--length", "88.53", "--mode-filter", "3",
        "--azimuthal-bins", "1", "--order", "2", "--size-factor", "0.96"]
random.seed(20260818)


def mesh(tag, d, w, rw):
    g = subprocess.run([str(MM), "run", "-n", "emsim", "python", "geometry.py",
                        "--out", f"{tag}.msh", "--loop", f"{d},{w},{rw},0.3"] + BASE,
                       capture_output=True, text=True)
    return g.returncode == 0


def solve(tag, band, step, timeout=600, samples=None):
    c, _m, _dr = solveconf.driven(f"{tag}.msh", tag, band, step=step)
    if samples:
        # Stage 1 needs only the peak POSITION, so starve the ROM. Measured: a
        # 160 MHz band at the default 40 adaptive samples costs ~850 s, which
        # made 12 points a 3.1 h job against my 600 s guess — 18x wrong.
        c["Solver"]["Driven"]["AdaptiveMaxSamples"] = samples
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    try:
        rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"], env=ENV,
                            stdout=open(f"{tag}_p.log", "w"),
                            stderr=subprocess.STDOUT, timeout=timeout).returncode
    except subprocess.TimeoutExpired:
        return None
    return None if rc else modes.te011(modes.peaks(tag, rel=0.02))


def qext(tag, te):
    recs = dq.load(tag)
    i0 = recs.index(min(recs, key=lambda r: abs(r["f"] - te["f"])))
    half = recs[i0]["U"] / 2
    lo = next((recs[i]["f"] for i in range(i0, -1, -1) if recs[i]["U"] <= half), None)
    hi = next((recs[i]["f"] for i in range(i0, len(recs)) if recs[i]["U"] <= half), None)
    if not (lo and hi and hi > lo):
        return None
    ql = te["f"] / (hi - lo)
    return 1 / (1 / ql - 1 / te["Q0"]) if ql < te["Q0"] else None


pts = []
while len(pts) < 12:
    d = random.uniform(8.0, 30.0)
    w = random.uniform(5.0, 20.0)
    if d * 2 * w <= 1100.0:
        pts.append((round(d, 1), round(w, 1), round(random.uniform(0.6, 1.8), 2)))

print(__doc__)
print("=" * 78, flush=True)
print(f"{'d':>6}{'w':>6}{'rw':>6}{'area':>8}{'aspect':>8}{'f0':>10}{'Q0':>9}{'Q_ext':>11}", flush=True)
rows = []
for i, (d, w, rw) in enumerate(pts):
    tag = f"sc{i:02d}"
    if not mesh(tag, d, w, rw):
        print(f"{d:>6.1f}{w:>6.1f}{rw:>6.2f}   mesh failed", flush=True); continue
    te = solve(tag, (2.40, 2.47), 2e-4, samples=12)  # stage 1: locate only
    if not te:
        print(f"{d:>6.1f}{w:>6.1f}{rw:>6.2f}   no resonance located", flush=True); continue
    f0 = te["f"]
    te2 = solve(tag, (f0 - 0.0015, f0 + 0.0015), 2e-6)   # stage 2: measure
    if not te2:
        print(f"{d:>6.1f}{w:>6.1f}{rw:>6.2f}   narrow solve failed", flush=True); continue
    q = qext(tag, te2)
    a = d * 2 * w
    rows.append((d, w, rw, a, d / (2 * w), te2["f"], te2["Q0"], q))
    print(f"{d:>6.1f}{w:>6.1f}{rw:>6.2f}{a:>8.0f}{d/(2*w):>8.2f}{te2['f']:>10.5f}"
          f"{te2['Q0']:>9,.0f}{(q or float('nan')):>11,.0f}", flush=True)

json.dump(rows, open("scatter.json", "w"), indent=1)
print(f"\n  {len(rows)} usable points -> scatter.json", flush=True)
