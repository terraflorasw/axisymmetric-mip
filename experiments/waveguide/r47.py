#!/usr/bin/env python3
"""R47 — identify the modes AZIMUTHALLY, and find out whether TM111 is really there.

R47 was filed as low priority when its only job was corroborating R36's ovality
result by a second observable. Its purpose has changed. Entry 86: the mode
filter's entire justification is the TE011/TM111 degeneracy, and **TM111 has
never been positively identified in this project**. Every measured number is
TM020. The one piece of TM111-shaped evidence is a mode that appears +3.2 MHz
from TE011 when the filter is removed (R39, b00), carrying boreH 1.25% — and at
--sectors 1 there is no azimuthal information to identify it with.

That matters now because R54, the geometric mode filter, targets TM111
specifically. Evaluating a filter aimed at a mode we cannot see is not a test.

WHAT UNBLOCKED IT: geometry.py gained --loop-phi. At --sectors 5 the sector
planes lie at 0/72/144/216/288 degrees, and the loop at phi=0 straddled one,
splitting the port face so it drove nothing — the failure r12.py documented as
"--sectors 1 is not optional". Putting the loop at a sector CENTRE (36 deg)
clears the planes: verified, single port face, air sectors 3..7.

HOW m IS IDENTIFIED. A mode with azimuthal index m has energy density going as
cos^2(m phi) = (1 + cos(2 m phi))/2, so its energy per sector varies at spatial
frequency 2m around the ring. Taking the DFT of the 5 sector energies:

    m = 0   ->  bin 0 only (uniform)
    m = 1   ->  frequency 2  ->  BIN 2
    m = 2   ->  frequency 4  ->  aliases to BIN 1 at N=5

so bin 2 dominant means m=1, bin 1 dominant means m=2. This is a genuine
identification, not the CV scalar the file used before -- CV says "not
axisymmetric" without saying in what way, and at N=4 it was exactly blind to m=2.

⚠️ THE LOOP IS ITSELF AN m-BREAKING PERTURBATION, so every mode will show some
bin-1 and bin-2 content. TE011 is the calibration: it is KNOWN to be m=0, so
whatever it shows is this harness's floor, and only excess above that floor
counts as a signal. Same discipline as R29's contrast test.

    s5_mf     mode filter present (brake 3) -- the design point
    s5_nomf   filter removed (brake 0)      -- where the +3.2 MHz neighbour lives
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
NSEC = 5
BASE_ARGS = ["--radius", A, "--length", L, "--sectors", str(NSEC),
             "--loop-phi", "36", "--order", "2",
             "--loop", "12,8.5,1,0.3", "--loop-tilt", "45"]
CASES = [("s5_mf", ["--brake", "3"]), ("s5_nomf", ["--brake", "0"])]
LABEL = {"s5_mf": "filter 3 mm", "s5_nomf": "no filter"}
BAND = (2.34, 2.50)
SECT_ATTRS = [3, 4, 5, 6, 7]


LOOP_PHI_DEG, LOOP_TILT_DEG = 36.0, 45.0


def port_direction(phi_deg, tilt_deg):
    """The port direction rotates WITH the loop. Getting this wrong is a hard
    abort, not a wrong answer: Palace refuses a direction that does not align
    with the port face's bounding box, and the first run of R47 died in 7 s
    because the loop moved to 36 deg while Direction stayed at phi = 0.

    dir = Rz(phi) . (0, cos tilt, sin tilt)
    """
    p, t = math.radians(phi_deg), math.radians(tilt_deg)
    return [-math.sin(p) * math.cos(t), math.cos(p) * math.cos(t), math.sin(t)]


def make_cfg(tag, brake):
    c = json.loads(json.dumps(BASE))
    c["Model"]["Mesh"] = f"{tag}.msh"
    c["Problem"]["Output"] = f"postpro/{tag}"
    c["Boundaries"]["LumpedPort"][0]["Direction"] = port_direction(
        LOOP_PHI_DEG, LOOP_TILT_DEG)
    mats = []
    for m in c["Domains"]["Materials"]:
        if m["Attributes"] == [3]:
            m = dict(m, Attributes=SECT_ATTRS)      # all five air sectors
        if m["Attributes"] == [8] and float(brake) == 0.0:
            continue                                 # attribute absent from mesh
        mats.append(m)
    c["Domains"]["Materials"] = mats
    # Index 1 stays the bore, so dq.py keeps working; 2..6 are the sectors.
    c["Domains"]["Postprocessing"]["Energy"] = (
        [{"Index": 1, "Attributes": [1]}]
        + [{"Index": 2 + i, "Attributes": [a]} for i, a in enumerate(SECT_ATTRS)])
    c["Solver"]["Driven"]["Samples"] = [{"Type": "Linear", "MinFreq": BAND[0],
                                         "MaxFreq": BAND[1], "FreqStep": 2e-5}]
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))


def sector_rows(tag):
    """Per-frequency sector energy fractions, aligned with dq.load's rows."""
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
    """Return (bin1, bin2) as fractions of the mean, from the 5-sector DFT."""
    n = len(U)
    a0 = sum(U) / n
    if a0 <= 0:
        return None
    amp = []
    for b in (1, 2):
        s = sum(U[k] * cmath.exp(-2j * math.pi * b * k / n) for k in range(n))
        amp.append(abs(s) / n / a0)
    return amp[0], amp[1]


def solve(tag, brake):
    make_cfg(tag, brake)
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
    recs = dq.load(tag)
    sect = sector_rows(tag)
    if len(sect) < len(recs):
        print(f"    🔴 sector columns missing ({len(sect)} rows vs {len(recs)}) "
              f"— the Energy postprocessing blocks did not take effect",
              flush=True)
        return []
    out = []
    for i in dq.peaks(recs, rel=0.01, sep=0.0008):
        r = recs[i]
        az = azimuthal(sect[i])
        if az is None:
            continue
        out.append(dict(f=r["f"], Q0=r["Q0"], pe=r["pe"], pm=r["pm"],
                        b1=az[0], b2=az[1], U=r["U"],
                        sect=sect[i], label=dq.identify(r)))
    return out


print(__doc__)
print("=" * 78, flush=True)

fac, _ = meshsweep.sweep(CASES, BASE_ARGS,
                         factors=("0.96", "1.00", "0.93", "0.90", "1.06"))
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")

res = {}
for tag, extra in CASES:
    print(f"\n=== {LABEL[tag]}", flush=True)
    res[tag] = solve(tag, extra[1])
    print(f"  {'f (GHz)':>9}{'Q0':>9}{'boreH %':>9}{'bin1 (m=2)':>12}"
          f"{'bin2 (m=1)':>12}   verdict", flush=True)
    for m in res[tag]:
        print(f"  {m['f']:>9.5f}{m['Q0']:>9,.0f}{m['pm']*100:>9.3f}"
              f"{m['b1']:>12.4f}{m['b2']:>12.4f}   {m['label']}", flush=True)

print("\n" + "=" * 78)
# TE011 is a KNOWN m=0 mode. Its bins are the floor set by the loop itself.
floor = None
for m in res.get("s5_mf", []):
    if m["label"] == "TE011":
        floor = (m["b1"], m["b2"])
        print(f"CALIBRATION — TE011 (known m=0) with the filter in place:")
        print(f"  bin1 {m['b1']:.4f}   bin2 {m['b2']:.4f}   <- the harness floor,"
              f" set by the loop's own asymmetry")
if floor is None:
    print("🔴 no TE011 found in the filtered case — cannot calibrate, and every "
          "azimuthal number below is unanchored.")
else:
    print("\nMODES ABOVE THE FLOOR (3x), i.e. genuinely non-axisymmetric:")
    for tag, _e in CASES:
        for m in res[tag]:
            r1 = m["b1"] / floor[0] if floor[0] > 0 else 0
            r2 = m["b2"] / floor[1] if floor[1] > 0 else 0
            if max(r1, r2) < 3:
                continue
            kind = ("m=1" if r2 > r1 else "m=2")
            print(f"  {LABEL[tag]:>12}  f={m['f']:.5f}  Q={m['Q0']:>8,.0f}  "
                  f"boreH={m['pm']*100:5.2f}%  bin1 {r1:5.1f}x  bin2 {r2:5.1f}x"
                  f"   -> {kind}")
    print("""
Read: a mode near TE011 in the UNFILTERED case with bin2 well above the floor is
TM111, and the degeneracy story is confirmed by direct observation for the first
time. If nothing shows m=1, the +3.2 MHz neighbour is something else and the
mode filter's justification needs restating before R54 designs a replacement for
it.""")
print(flush=True)
