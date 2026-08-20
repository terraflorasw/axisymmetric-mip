#!/usr/bin/env python3
"""R54 — can a GEOMETRIC mode filter replace the quartz annulus?

The quartz annulus works, and R47 finally measured it on the right mode: it puts
TM111 64.3 MHz below TE011 instead of 19.5, and keeps TE011's azimuthal content
at the harness floor. What it costs is 5.6% of Q, 442 g of custom optical parts
(two 207.4 x 3 mm annuli with 20 mm bores), and a mounting problem needing 0.23 mm
of compliant radial float (R53).

The geometric alternative is a circumferential groove at each cap/barrel corner.
It works on a completely different principle:

    quartz annulus   DETUNES TM by dielectric loading at the E_z maximum
    corner groove    interrupts TM111's RADIAL cap current

🔢 The corner is where discrimination is perfect, and this is not a citation but
the field structure:

    TE011 cap current  ~ J1(chi'01 r/a)   -> ZERO at r = a, by the BC itself
    TM111 cap current  ~ J1'(chi11 r/a)   -> 0.40 of maximum at r = a

At mid-radius it INVERTS (J1' = 0 at r = 49.8 mm, where TE011's cap current
peaks), so a groove there would cut the mode we want and spare the one we do not.
Hence: at the corner, or not at all.

PRE-REGISTERED PREDICTIONS, and I am separating the ones I am confident in from
the ones I am not.

  ✅ CONFIDENT — TE011 f and Q barely move. The groove sits in a null of its cap
     current. This is the same argument that made R29's chimney null hold, and
     that one was measured right.
  ⚠️ UNSURE OF SIGN — TM111 shifts. A lambda/4 groove transforms the short at its
     bottom into an open at the cap face, which should act like moving the cap
     outward, i.e. DOWNWARD in frequency. My sign predictions are poor tonight
     (0 for 2 on TM020), so this is stated to be checked, not believed.
  ⚠️ MECHANISM UNKNOWN — the groove may SEPARATE (shift TM111 away) or SUPPRESS
     (spoil its Q) or both. Either is a valid filter, so this run reports BOTH
     the separation and TM111's Q, and the pass criterion accepts either.
  🔴 NAMED FAILURE MODE — a lambda/4 groove is RESONANT at 2.45 GHz by
     construction. TE011's E_phi is not quite zero at the groove's inner radius:
     J1(chi'01 * 100.7/103.7) is 5.9% of peak. If the resonant groove couples to
     that, it will spoil TE011's Q — and the deep case is where it would show.

    q_filter   quartz 3 mm, no groove   the incumbent, rebuilt in-sweep
    g_none     neither                  the degenerate baseline
    g_15       groove 3 x 15 mm         partial depth
    g_31       groove 3 x 30.6 mm       lambda/4 at 2.45 GHz
"""
import cmath, csv, json, math, os, pathlib, subprocess, sys, time

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
NSEC, SECT_ATTRS = 5, [3, 4, 5, 6, 7]
LOOP_PHI_DEG, LOOP_TILT_DEG = 36.0, 45.0
BASE_ARGS = ["--radius", A, "--length", L, "--sectors", str(NSEC),
             "--loop-phi", str(LOOP_PHI_DEG), "--order", "2",
             "--loop", "12,8.5,1,0.3", "--loop-tilt", str(LOOP_TILT_DEG)]
CASES = [("q_filter", ["--brake", "3"]),
         ("g_none", ["--brake", "0"]),
         ("g_15", ["--brake", "0", "--groove", "3,15"]),
         ("g_31", ["--brake", "0", "--groove", "3,30.6"])]
LABEL = {"q_filter": "quartz 3mm", "g_none": "neither",
         "g_15": "groove 15mm", "g_31": "groove λ/4"}
BAND = (2.34, 2.50)


def port_direction(phi_deg, tilt_deg):
    p, t = math.radians(phi_deg), math.radians(tilt_deg)
    return [-math.sin(p) * math.cos(t), math.cos(p) * math.cos(t), math.sin(t)]


def make_cfg(tag, has_brake):
    c = json.loads(json.dumps(BASE))
    c["Model"]["Mesh"] = f"{tag}.msh"
    c["Problem"]["Output"] = f"postpro/{tag}"
    c["Boundaries"]["LumpedPort"][0]["Direction"] = port_direction(
        LOOP_PHI_DEG, LOOP_TILT_DEG)
    mats = []
    for m in c["Domains"]["Materials"]:
        if m["Attributes"] == [3]:
            m = dict(m, Attributes=SECT_ATTRS)
        if m["Attributes"] == [8] and not has_brake:
            continue
        mats.append(m)
    c["Domains"]["Materials"] = mats
    c["Domains"]["Postprocessing"]["Energy"] = (
        [{"Index": 1, "Attributes": [1]}]
        + [{"Index": 2 + i, "Attributes": [a]} for i, a in enumerate(SECT_ATTRS)])
    c["Solver"]["Driven"]["Samples"] = [{"Type": "Linear", "MinFreq": BAND[0],
                                         "MaxFreq": BAND[1], "FreqStep": 2e-5}]
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))


def sector_rows(tag):
    p = pathlib.Path("postpro") / tag / "domain-E.csv"
    with open(p) as fh:
        rows = [{k.strip(): v.strip() for k, v in r.items() if k}
                for r in csv.DictReader(fh)]
    out = []
    for r in rows:
        vals = []
        for i in range(2, 2 + NSEC):
            e = m = 0.0
            for k, v in r.items():
                if f"p_elec[{i}]" in k:
                    e = float(v)
                elif f"p_mag[{i}]" in k:
                    m = float(v)
            vals.append(e + m)
        out.append(vals)
    return out


def azimuthal(U):
    n = len(U)
    a0 = sum(U) / n
    if a0 <= 0:
        return 0.0, 0.0
    return tuple(abs(sum(U[k] * cmath.exp(-2j * math.pi * b * k / n)
                         for k in range(n))) / n / a0 for b in (1, 2))


def solve(tag, has_brake):
    make_cfg(tag, has_brake)
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
    recs, sect = dq.load(tag), sector_rows(tag)
    if len(sect) < len(recs):
        print("    🔴 sector columns missing — Energy blocks did not take effect",
              flush=True)
        return []
    out = []
    for i in dq.peaks(recs, rel=0.01, sep=0.0008):
        r = recs[i]
        b1, b2 = azimuthal(sect[i])
        out.append(dict(f=r["f"], Q0=r["Q0"], pe=r["pe"], pm=r["pm"],
                        b1=b1, b2=b2))
    return out


# TE011 is the mode with the TE011 bore-H signature, ~2.08%. TM111 carries ~1.2%.
# NOT dq.identify: its te_h = 1% cut labels TM111 as TE011, which has now misfired
# three times (R36, R39, R47). Deferred to R50 there; worked around here.
def pick(peaks, lo, hi):
    c = [m for m in peaks if lo <= m["pm"] < hi]
    return max(c, key=lambda m: m["U"] if "U" in m else m["Q0"]) if c else None


print(__doc__)
print("=" * 78, flush=True)

fac, _ = meshsweep.sweep(CASES, BASE_ARGS,
                         factors=("0.96", "1.00", "0.93", "0.90", "1.06"))
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")
sizes = {t: pathlib.Path(f"{t}.msh").stat().st_size for t, _e in CASES}
if len(set(sizes.values())) != len(sizes):
    sys.exit("🔴 two cases produced identically sized meshes — an argument did "
             "not take effect. Do not read results from this.")

res = {}
for tag, extra in CASES:
    print(f"\n=== {LABEL[tag]}", flush=True)
    res[tag] = solve(tag, "--brake" in extra and extra[extra.index("--brake") + 1] != "0")
    print(f"  {'f (GHz)':>9}{'Q0':>9}{'boreH %':>9}{'bin1':>9}{'bin2':>9}",
          flush=True)
    for m in res[tag]:
        print(f"  {m['f']:>9.5f}{m['Q0']:>9,.0f}{m['pm']*100:>9.3f}"
              f"{m['b1']:>9.4f}{m['b2']:>9.4f}", flush=True)

print("\n" + "=" * 78)
print(f"{'case':>12}{'TE011 f':>10}{'TE011 Q':>10}{'purity b1':>11}"
      f"{'TM111 f':>10}{'TM111 Q':>9}{'sep MHz':>9}")
summary = {}
for tag, _e in CASES:
    te = pick(res[tag], 0.018, 0.10)
    tm = pick(res[tag], 0.008, 0.018)
    if not te:
        print(f"{LABEL[tag]:>12}   no TE011-signature mode found")
        continue
    sep = (te["f"] - tm["f"]) * 1000 if tm else float("nan")
    summary[tag] = (te, tm, sep)
    print(f"{LABEL[tag]:>12}{te['f']:>10.5f}{te['Q0']:>10,.0f}{te['b1']:>11.4f}"
          + (f"{tm['f']:>10.5f}{tm['Q0']:>9,.0f}{sep:>9.1f}" if tm
             else f"{'--':>10}{'--':>9}{'--':>9}"))

print("\nVERDICT — a geometric filter must do all four")
q = summary.get("q_filter")
n = summary.get("g_none")
for tag in ("g_15", "g_31"):
    s = summary.get(tag)
    if not (s and q and n):
        print(f"  {LABEL[tag]}: incomplete")
        continue
    te, tm, sep = s
    dq_te = 100 * (te["Q0"] / n[0]["Q0"] - 1)
    pur = te["b1"] / q[0]["b1"] if q[0]["b1"] > 0 else float("inf")
    supp = tm["Q0"] / n[1]["Q0"] if (tm and n[1] and n[1]["Q0"]) else float("nan")
    print(f"\n  {LABEL[tag]}:")
    print(f"    1. TE011 Q vs no-filter      {dq_te:+6.2f}%   "
          + ("✅" if abs(dq_te) < 2 else "🔴 the groove is costing the mode it must not touch"))
    print(f"    2. TE011 purity vs quartz    {pur:6.2f}x   "
          + ("✅" if pur < 3 else "🔴 azimuthal contamination remains"))
    print(f"    3. TE011-TM111 separation    {sep:6.1f} MHz (quartz {q[2]:.1f}, "
          f"bare {n[2]:.1f})   "
          + ("✅" if abs(sep) > 40 else "⚠️ not separating"))
    print(f"    4. TM111 Q vs bare           {supp:6.2f}x   "
          + ("✅ suppressed" if supp < 0.5 else "— not suppressing"))
    ok_sep, ok_sup = abs(sep) > 40, supp < 0.5
    print("    => " + ("✅ VIABLE — " + ("separates" if ok_sep else "") +
                       ("+suppresses" if ok_sep and ok_sup else
                        "suppresses" if ok_sup else "")
                       if (ok_sep or ok_sup) and abs(dq_te) < 2 and pur < 3
                       else "🔴 NOT viable as drawn — the quartz annulus stays"))
print(flush=True)
