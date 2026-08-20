#!/usr/bin/env python3
"""R77b — FALSIFICATION: is R47's TM111 still down at 2.351, below R77's band?

R77 fingerprinted the interloper at 2.4382 as chi = 3.846, p = 1, which admits
only TE011 (m=0) and TM111 (m=1) — and TE011 is separately identified, so TM111
by elimination.

🔴 BUT R77's BAND STARTED AT 2.360, AND R47 PUT TM111 AT 2.35094 — BELOW IT.
R47 measured TM111 64.3 MHz BELOW TE011 with the same 3 mm filter; R77's
candidate is 42.3 MHz ABOVE. Both cannot be TM111. Either sc06's loop moved it
+107 MHz relative to TE011, or R77 identified a different mode and the real TM111
was simply outside the window.

An identification whose leading alternative was never in the band is not an
identification. This looks in the band R77 skipped, on the SAME idref mesh, with
the same sector machinery.

THE TEST IS THE AZIMUTHAL SIGNATURE, not the frequency. R47's TM111 showed DFT
bin 2 at 57.7x the m=0 floor. R77's candidate shows 10.8x. If a mode with a
STRONG m=1 signature sits near 2.351, it is R47's TM111 and R77's assignment is
wrong. If nothing is there, R77's elimination argument survives.
"""
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
import modes
import solveconf
import solver

MESH, TAG, BAND, STEP = "idref.msh", "idlow", (2.315, 2.365), 2.5e-5
AZ_FLOOR = 0.0046
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")

print(__doc__)
print("=" * 78, flush=True)
meta = solveconf.load_meta(MESH)
pl = meta["attributes"].get("plasma")
c, meta, dropped = solveconf.driven(
    MESH, TAG, BAND, step=STEP, order=1,
    materials={pl: {"Permittivity": 1.0, "Permeability": 1.0}})
for d in dropped:
    print(f"  dropped: {d}")
for m in c["Domains"]["Materials"]:
    if m["Attributes"] == [pl] and "Conductivity" in m:
        raise SystemExit("plasma still conducting — not a cold run")
pathlib.Path(f"{TAG}.json").write_text(json.dumps(c, indent=2))
print(f"  {MESH}, band {BAND[0]}-{BAND[1]} GHz at 25 kHz "
      f"({int((BAND[1]-BAND[0])/STEP)+1} pts) — the window R77 skipped",
      flush=True)

t0 = time.time()
rc = subprocess.run([PALACE, "-np", "4", f"{TAG}.json"], env=solver.ENV,
                    stdout=open(f"{TAG}_p.log", "w"), stderr=subprocess.STDOUT,
                    timeout=solver.DEFAULT_TIMEOUT_S).returncode
dt = time.time() - t0
if rc or dt < solver.MIN_SECONDS:
    tail = pathlib.Path(f"{TAG}_p.log").read_text().strip().splitlines()
    sys.exit(f"🔴 rc={rc} in {dt:.0f}s — {tail[-1] if tail else '(empty)'}")

recs = dq.load(TAG)
sect = modes.sector_energy(TAG)
if sect is None:
    sys.exit("🔴 no sector data — m cannot be measured and this test is void")
U = [r["U"] for r in recs]
um = max(U)
print(f"\n  {dt:.0f}s. Resonances in 2.315-2.365:")
print(f"    {'f GHz':>9}{'rel':>8}{'bore-H':>9}{'bore-E':>10}{'Q0':>8}{'eta':>7}"
      f"{'b1(m2)':>9}{'b2(m1)':>9}{'b2/floor':>10}")
found = []
for i in range(2, len(U) - 2):
    if U[i] == max(U[i - 2:i + 3]) and U[i] > 0.005 * um:
        b1, b2 = modes.azimuthal(sect[i])
        r = recs[i]
        found.append((r["f"], b1, b2, r["pm"], r["pe"]))
        print(f"    {r['f']:>9.4f}{U[i]/um:>8.3f}{r['pm']:>9.5f}{r['pe']:>10.6f}"
              f"{r['Q0']:>8.0f}{100*(1-r['gamma']**2):>6.1f}%{b1:>9.4f}"
              f"{b2:>9.4f}{b2/AZ_FLOOR:>10.1f}")
if not found:
    print("    (none above 0.5% of the window maximum)")

print("\nVERDICT")
strong = [f for f in found if f[2] / AZ_FLOOR > 20.0]
if strong:
    print(f"  🔴 R77's IDENTIFICATION IS WRONG. A strong m=1 mode sits at "
          f"{strong[0][0]:.4f} GHz\n     (bin2 = {strong[0][2]:.4f} = "
          f"{strong[0][2]/AZ_FLOOR:.0f}x the floor, against R47's 57.7x for "
          "TM111).\n     That is R47's TM111, below the band R77 searched, and "
          "the 2.4382 mode is\n     something else that must be identified "
          "again.")
else:
    print("  ✅ NO strong m=1 mode in 2.315-2.365. The band R77 skipped is "
          "empty of the\n     leading alternative, so R47's TM111 is NOT still "
          "sitting there — it moved,\n     and R77's elimination argument "
          "survives this test.")
    if found:
        print(f"     (strongest m=1 content here: bin2 "
              f"{max(f[2] for f in found):.4f} = "
              f"{max(f[2] for f in found)/AZ_FLOOR:.1f}x floor)")
print("\n⚠️ This tests ONE alternative — that TM111 stayed where R47 found it. It "
      "does not\n   prove the 2.4382 mode is TM111; that rests on the chi/p "
      "fingerprint and the\n   degeneracy argument in R77.")
print(flush=True)
