#!/usr/bin/env python3
"""R99 — re-take the mode landscape at the SAPPHIRE point.

Every mesh in this record runs torch_eps = 3.78. That is QUARTZ, and the design
point (R44) is sapphire. The gap was legitimate while the shim made the two builds
one cavity; R99 (the torch is a PERMANENT all-sapphire feature) deleted the shim,
and with it the justification. The development build is now a DIFFERENT RESONATOR
from the product.

🔑 AND THE DIFFERENCE IS NOT UNIFORM ACROSS MODES. The torch sits ON AXIS:

    TM020   E_z ~ J0(chi02 r/a)      MAXIMUM on axis   -> loaded hardest
    TM111   E_z ~ J1(chi11 r/a) = 0  ZERO on axis      -> barely loaded
    TE011   E_phi ~ J1(chi'01 r/a)=0 ZERO on axis      -> barely loaded

So torch permittivity is a DIFFERENTIAL mode-mover: it changes mode SEPARATIONS,
not just f(TE011). Sweeping it is not a retune, it is a different mode landscape.

CASES — three, because two effects must be separated:

    A  s99qz   eps 3.78   L 88.53   the development build (CONTROL, ties to record)
    C  s99sa   eps 11.6   L 88.53   material effect ALONE, at fixed length
    B  s99pr   eps 11.6   L 87.97   the product

🔑 dTM020/dL = 0 IDENTICALLY (R46 measured 2.392-2.393 across three lengths), so
TM020's entire shift is A->C and B adds nothing to it. That makes C the
load-bearing case for the headline question -- and makes B vs C a FREE NULL
CONTROL (below).

════════════════════════════════════════════════════════════════════════════════
CRITERIA, DECLARED BEFORE THE RUN. Labels live in evaluate.py; this file and
results.py emit measurements only.
════════════════════════════════════════════════════════════════════════════════

1. PRIMARY -- does TM020 keep enough clearance below the 2.400 GHz band floor?

   THRESHOLD 4.4 MHz, and it is not arbitrary: dTM020/da = -22 MHz/mm against the
   +/-0.2 mm radius callout is +/-4.4 MHz. Below that, MACHINING ALONE can push
   TM020 into the amplifier's reach, and "TM020 is unreachable" stops being an
   unconditional guarantee. Recorded headroom today is 5.7-6.0 MHz -- already
   tight, which is why this is the headline.

   ⚠️ FRAME. Order-1 raw sits ~20 MHz below converged (tm020: 2.37546 raw vs
   2.39552 converged). Do NOT compare a raw number to a 2.400 absolute. Use the
   DIFFERENTIAL, which cancels the frame offset to first order:

       f_conv(C) = tm020.f_converged + [ f_raw(C) - f_raw(A) ]

   A exists in this run precisely so that subtraction is available.

2. NULL CONTROL -- B and C differ ONLY in length, and dTM020/dL = 0. So
   f(TM020) must agree between B and C to within the frequency step (0.05 MHz).
   🔴 IF IT DOES NOT, the mode identification or the measurement is wrong and
   NOTHING ELSE IN THIS RUN SHOULD BE READ. R89's null control failed and
   invalidated a day of rankings; this one is free, so there is no excuse.

3. PREDICTIONS, stated so they can be falsified rather than confirmed:
     TM020  largest downward shift (E_z max on axis)
     TM111  nearly unmoved (E_z = 0 on axis)
     TE011  ~9.25 MHz  (entry 64, DRIVEN)
   🔴 DO NOT quote entry 60's -33.9 MHz. That is the EIGENMODE number, and entry
   64 recorded eigenmode and driven disagreeing 3.7x with DRIVEN defining the
   design. Reusing it here would repeat the standing error of this record: an
   inherited number quoted outside the context of its own description.

4. REACHABILITY before ranking. The amplifier is 2.400-2.500 GHz. A mode outside
   that is unreachable whatever its Q, and must not be ranked as a rival.

⚠️ The mode filter stays QUARTZ (--mode-filter 3). It is a cavity annulus, not a
   torch tube: the Mehlich-3 aerosol never reaches it, so the fluoride argument
   that eliminated quartz for the torch does not apply to it (R85 kept it).

⚠️ MESH FAMILY. These three are built together at a common size factor and with
   the current defaults (viewport and trap ON at 10 mm). They are comparable to
   EACH OTHER. They are NOT comparable to pre-2026-08-19 meshes, which have
   neither. A is the control that ties this family back to the record.
"""
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import meshsweep
import results
import solveconf
import solver

BASE = ["--radius", "103.70", "--order", "2", "--sectors", "1",
        "--loop", "25.8,19.4,1.5,0.3", "--loop-phi", "36",
        "--plasma", "4.5,8.5,-20,10", "--plasma-h", "1.0", "--mode-filter", "3"]
CASES = [("s99qz", ["--length", "88.53", "--torch-material", "3.78,1e-4"]),
         ("s99sa", ["--length", "88.53"]),
         ("s99pr", ["--length", "87.97"])]
# Widened at the BOTTOM vs R89's (2.30, 2.48): sapphire pushes TM020 DOWN and the
# shift is the unknown being measured. A band that clips the mode we came to find
# would report "not present" for "outside the window".
BAND, STEP = (2.26, 2.48), 5e-5
REPLAY = "--replay" in sys.argv
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")


def run(tag):
    mesh = f"{tag}.msh"
    meta = solveconf.load_meta(mesh)
    pl = meta["attributes"].get("plasma")
    c, meta, _ = solveconf.driven(
        mesh, tag, BAND, step=STEP, order=1,
        materials={pl: {"Permittivity": 1.0, "Permeability": 1.0}})
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    eps = meta["geometry_mm"]["torch_material"]
    # R101 guard. The first attempt at this run would have compared sapphire to
    # quartz on BYTE-IDENTICAL meshes with an identical template permittivity,
    # and reported "the material does not matter". Assert the config carries the
    # mesh's material — a check that can pass, and that fails loudly if the
    # binding regresses.
    got = [m for m in c["Domains"]["Materials"]
           if m["Attributes"] == [meta["attributes"]["torch"]]]
    assert len(got) == 1, f"{tag}: {len(got)} torch materials in the config"
    assert abs(got[0]["Permittivity"] - eps[0]) < 1e-9, (
        f"{tag}: config eps {got[0]['Permittivity']} != mesh eps {eps[0]}")
    print(f"  {tag}: torch eps={eps[0]} tand={eps[1]}, "
          f"L={meta['geometry_mm']['length']}, {meta['tets']:,} tets, "
          f"sf {meta['size_factor']}", flush=True)
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
    print(f"    solved in {dt:.0f}s", flush=True)


print(__doc__)
print("=" * 78, flush=True)
if not REPLAY:
    fac, _ = meshsweep.sweep(CASES, BASE)
    if not fac:
        sys.exit("mesh sweep failed — a size-factor confound must be removed by "
                 "construction, not argued away")
    print(f"  ✅ all 3 cases at a COMMON size-factor {fac}", flush=True)

for tag, _e in CASES:
    if not (REPLAY and (pathlib.Path("postpro") / tag / "port-S.csv").exists()):
        run(tag)

idx, got = results.sweep(
    [t for t, _e in CASES], "r99",
    extra=dict(question="does TM020 keep >=4.4 MHz clearance below 2.400 GHz "
                        "when the torch becomes sapphire?",
               threshold_mhz=4.4,
               threshold_basis="dTM020/da = -22 MHz/mm x the +/-0.2 mm radius "
                               "callout; below this, machining alone can make "
                               "TM020 reachable",
               frame="raw-order1; convert via the A->C differential against "
                     "tm020.f_converged, never by comparing raw to 2.400",
               null_control="dTM020/dL = 0 (R46), so s99pr and s99sa must agree "
                            "on f(TM020) to within the 0.05 MHz step. If they "
                            "do not, discard the run."))
print(f"\n  wrote {len(got)} result files + r99.sweep.json")
print("  ⚠️ NO VERDICT HERE — run evaluate.py --sweep r99", flush=True)
