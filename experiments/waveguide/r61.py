#!/usr/bin/env python3
"""R61 — re-take R47's azimuthal identification at the INSTRUMENT's 0° loop tilt.

R60 found TM020 suppressed 18.3 dB at 0° tilt, as the H_z orthogonality argument
predicts — but TM111's relative excitation TRIPLED, going the opposite way,
despite TM111 also having H_z = 0. That inverts an assumption several conclusions
rest on, and it matters because **every TM111 result in this project was measured
at 45°**, which geometry.py documents as a DIAGNOSTIC setting, not the operating
one: R47's identification, R54's assessment of the geometric mode filter, R39's
brake-essential test.

This repeats R47 exactly — `--sectors 5 --loop-phi 36`, filter present and
absent, m by DFT of the five sector energies — with the single change of
`--loop-tilt 0`.

    bin 2 -> m = 1        bin 1 -> m = 2 (aliased at N = 5)

TWO QUESTIONS, and they are separable:

  1. **Does the identification survive?** TM111 was identified at 45° by bin2 at
     57.7x the TE011 floor. If it still reads m = 1 at 0°, R47's identification
     stands regardless of amplitude, and the mode filter's justification is
     intact.
  2. **Is the anomaly real?** R60 saw it in a single sectors=1 pair. If TM111's
     amplitude relative to TE011 again rises at 0°, it reproduces on an
     independent mesh family and needs a mechanism. If it does not, R60's
     observation was a peak-extraction artefact and the 45° results stand.

⚠️ The TE011 floor must be RE-MEASURED here, not carried from R47. The floor is
set by the loop's own symmetry breaking, and the loop's geometry is what changed.

⚠️ These meshes are not the 45° meshes — tilt changes the loop solid. Compare
RATIOS within each run, not absolute frequencies across runs.
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
LOOP_PHI_DEG, LOOP_TILT_DEG = 36.0, 0.0          # <-- the one change from R47
BASE_ARGS = ["--radius", A, "--length", L, "--sectors", str(NSEC),
             "--loop-phi", str(LOOP_PHI_DEG), "--order", "2",
             "--loop", "12,8.5,1,0.3"]
CASES = [("z0_mf", ["--brake", "3"]), ("z0_nomf", ["--brake", "0"])]
LABEL = {"z0_mf": "filter 3 mm", "z0_nomf": "no filter"}
BAND = (2.34, 2.50)

# R47's numbers at 45 deg, for the comparison this run exists to make.
R47 = {"z0_mf": {"te_b1": 0.0046, "te_b2": 0.0035, "tm111_rel": 0.0970},
       "z0_nomf": {"te_b1": 0.1061, "te_b2": 0.0092, "tm111_rel": 0.3378}}


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
                         for k in range(n))) / n / a0
                 for b in (1, 2))


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
        print("    🔴 sector columns missing", flush=True)
        return []
    um = max(r["U"] for r in recs)
    out = []
    for i in dq.peaks(recs, rel=0.005, sep=0.0008):
        r = recs[i]
        b1, b2 = azimuthal(sect[i])
        out.append(dict(f=r["f"], Q0=r["Q0"], pe=r["pe"], pm=r["pm"],
                        rel=r["U"] / um, b1=b1, b2=b2))
    return out


# Pick by bore-energy SIGNATURE, never dq.identify -- its 1% boreH cut calls
# TM111 a TE011 and has misfired three times (R36, R39, R47).
def te011(ms):
    c = [m for m in ms if m["pm"] >= 0.018]
    return max(c, key=lambda m: m["rel"]) if c else None


def tm111(ms):
    c = [m for m in ms if 0.008 <= m["pm"] < 0.018 and m["pe"] >= 0.004]
    return max(c, key=lambda m: m["rel"]) if c else None


print(__doc__)
print("=" * 78, flush=True)

fac, _ = meshsweep.sweep(CASES, BASE_ARGS,
                         factors=("0.96", "1.00", "0.93", "0.90", "1.06"))
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")

res = {}
for tag, extra in CASES:
    print(f"\n=== {LABEL[tag]}   loop tilt 0°", flush=True)
    res[tag] = solve(tag, extra[1] != "0")
    print(f"  {'f (GHz)':>9}{'U/Umax':>9}{'Q0':>9}{'boreH %':>9}"
          f"{'bin1':>9}{'bin2':>9}", flush=True)
    for m in res[tag]:
        print(f"  {m['f']:>9.5f}{m['rel']:>9.4f}{m['Q0']:>9,.0f}"
              f"{m['pm']*100:>9.3f}{m['b1']:>9.4f}{m['b2']:>9.4f}", flush=True)

print("\n" + "=" * 78)
print("Q1 — DOES THE m=1 IDENTIFICATION SURVIVE AT 0°?")
for tag, _e in CASES:
    te, tm = te011(res[tag]), tm111(res[tag])
    if not te:
        print(f"  {LABEL[tag]}: no TE011 — cannot calibrate")
        continue
    print(f"  {LABEL[tag]}: TE011 floor bin1 {te['b1']:.4f} / bin2 {te['b2']:.4f}"
          f"   (R47 at 45°: {R47[tag]['te_b1']:.4f} / {R47[tag]['te_b2']:.4f})")
    if not tm:
        print("    🔴 no TM111-signature mode found at all")
        continue
    r2 = tm["b2"] / te["b2"] if te["b2"] > 0 else float("inf")
    r1 = tm["b1"] / te["b1"] if te["b1"] > 0 else float("inf")
    print(f"    TM111 at {tm['f']:.5f}: bin2 {r2:>6.1f}x floor, "
          f"bin1 {r1:>6.1f}x   -> " + ("✅ still m=1" if r2 > 3 * max(r1, 1)
                                       else "🔴 no longer reads m=1"))

print("\nQ2 — DOES THE AMPLITUDE ANOMALY REPRODUCE?")
for tag, _e in CASES:
    tm = tm111(res[tag])
    if not tm:
        print(f"  {LABEL[tag]}: no TM111 to compare")
        continue
    was = R47[tag]["tm111_rel"]
    print(f"  {LABEL[tag]}: TM111/TE011 energy {tm['rel']:.4f} at 0°, "
          f"{was:.4f} at 45°  ->  {tm['rel']/was:.2f}x")
print("""
Read: ratios above ~1 reproduce R60's anomaly on an independent mesh family and
it needs a mechanism — plus every 45° TM111 result understates the hazard. Ratios
below 1 mean TM111 IS suppressed at the operational tilt as orthogonality says,
R60 was a peak-extraction artefact, and the 45° results stand as measured.""",
      flush=True)
