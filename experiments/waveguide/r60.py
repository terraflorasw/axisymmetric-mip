#!/usr/bin/env python3
"""R60 — does the OPERATIONAL coupler excite TM020 at all?

Every driven run in this project uses a 45-degree loop tilt. That is a
DIAGNOSTIC choice, documented in geometry.py: 0 deg links H_z and shows TE011
only, 90 deg links H_phi and shows TM020 only, 45 couples to both at -3 dB so one
sweep yields both resonances. The instrument's coupler is at 0.

That matters because TM modes have H_z = 0 identically. A loop lying in the z = 0
plane has normal z-hat and links H_z flux, so at first order it is ORTHOGONAL to
TM020 and to TM111 alike. If that orthogonality survives a real, finite-sized
loop, then TM020's frequency does not matter, and "TM020 must stay below the
2.400 band floor" is a vestige of the mode-shift ignition scheme that R11/R44
surrendered.

🔢 WHAT RIDES ON IT. That constraint is what tonight's aperture budget was spent
defending: chimney 1.26 MHz (R29), feed 2.70 MHz (R49), headroom 10 -> 6 MHz,
bore tolerance +/-0.45 -> +/-0.27 mm. Drop it and the bore tolerance reverts to
what TE011 needs -- of order +/-3 mm at -12.86 MHz/mm against 42 MHz of margin.

METHOD. Same mesh recipe, one sweep, two tilts. The port Direction must rotate
with the loop or Palace aborts (learned in R47), so it is derived here rather
than copied.

    t45   45 deg, the diagnostic configuration every prior run used
    t00    0 deg, the instrument's actual coupler

Read TM020's stored-energy amplitude relative to TE011's in each. If it collapses
at 0 deg, the mode is unreachable by the drive and its position is not a design
constraint.

⚠️ WHAT THIS DOES NOT TEST. TE011 and TM020 are both m = 0 but differ in p, so an
axially asymmetric perturbation could mix them even though the port cannot drive
TM020 directly -- and the plasma column IS axially asymmetric, running from
z = -20 mm to the far cap. This run is unlit. A null here bounds the DRIVE
channel only, not the mixing channel.
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
             "--order", "2", "--loop", "12,8.5,1,0.3"]
CASES = [("t45", ["--loop-tilt", "45"]), ("t00", [])]
TILT = {"t45": 45.0, "t00": 0.0}
LABEL = {"t45": "45° (diagnostic)", "t00": "0° (instrument)"}
BAND = (2.34, 2.50)


def port_direction(tilt_deg, phi_deg=0.0):
    p, t = math.radians(phi_deg), math.radians(tilt_deg)
    return [-math.sin(p) * math.cos(t), math.cos(p) * math.cos(t), math.sin(t)]


def solve(tag):
    c = json.loads(json.dumps(BASE))
    c["Model"]["Mesh"] = f"{tag}.msh"
    c["Problem"]["Output"] = f"postpro/{tag}"
    c["Boundaries"]["LumpedPort"][0]["Direction"] = port_direction(TILT[tag])
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
    recs = dq.load(tag)
    um = max(r["U"] for r in recs)
    out = []
    for i in dq.peaks(recs, rel=0.001, sep=0.0008):
        r = recs[i]
        kind = ("TE011" if r["pm"] >= 0.018
                else "TM020" if r["pe"] >= 0.020 else "other")
        out.append(dict(f=r["f"], Q0=r["Q0"], pe=r["pe"], pm=r["pm"],
                        rel=r["U"] / um, kind=kind))
    return out


print(__doc__)
print("=" * 78, flush=True)

fac, _ = meshsweep.sweep(CASES, BASE_ARGS,
                         factors=("0.96", "1.00", "0.93", "0.90", "1.06"))
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")

res = {}
for tag, _e in CASES:
    print(f"\n=== loop tilt {LABEL[tag]}", flush=True)
    res[tag] = solve(tag)
    for m in res[tag]:
        print(f"   f={m['f']:.5f}  U/Umax={m['rel']:8.5f}  Q={m['Q0']:>9,.0f}"
              f"  boreE={m['pe']*100:6.3f}%  boreH={m['pm']*100:6.3f}%"
              f"   {m['kind']}", flush=True)
    if not res[tag]:
        print("   no peaks", flush=True)

print("\n" + "=" * 78)
print("TM020 EXCITATION vs loop tilt")
ratio = {}
for tag, _e in CASES:
    te = next((m for m in res[tag] if m["kind"] == "TE011"), None)
    tm = next((m for m in res[tag] if m["kind"] == "TM020"), None)
    if not te:
        print(f"  {LABEL[tag]}: no TE011 — cannot normalise")
        continue
    if tm:
        ratio[tag] = tm["rel"] / te["rel"]
        print(f"  {LABEL[tag]:>18}: TM020 at {tm['f']:.5f}, "
              f"{100*ratio[tag]:.2f}% of TE011's stored energy")
    else:
        ratio[tag] = 0.0
        print(f"  {LABEL[tag]:>18}: TM020 NOT DETECTED above 0.1% of peak")

if "t45" in ratio and "t00" in ratio:
    if ratio["t45"] > 0:
        supp = ratio["t00"] / ratio["t45"]
        print(f"\n  suppression at 0° vs 45°: {supp:.4f}  "
              f"({-10*math.log10(supp):.1f} dB)" if supp > 0
              else "\n  TM020 vanishes entirely at 0°")
    print("""
Read: TM020 collapsing at 0 deg means the instrument's coupler cannot reach it,
its frequency is not a design constraint, and the aperture budget spent defending
the 2.400 floor (R29 1.26 MHz, R49 2.70 MHz, bore tolerance +/-0.45 -> +/-0.27 mm)
is recoverable. TM020 surviving at 0 deg means the finite loop breaks the
orthogonality and the floor constraint stands as written.""", flush=True)
