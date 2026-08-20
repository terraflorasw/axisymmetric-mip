#!/usr/bin/env python3
"""SMALL TEST: is Palace's lumped-port C in SERIES or PARALLEL with R?

R62 rests on a claim recorded in the coupler section — that Palace's port R and C
are in parallel, so a series capacitor must be built geometrically. Two full
sweeps (~4 h) were spent on the geometric route, one defeated by mesh resolution
and one by a sign error in my own leg construction. Before spending a third,
test the claim itself.

🔑 THIS NEEDS NO NEW GEOMETRY AND NO RESONANCE. The two hypotheses predict very
different reflection at the SAME frequency on the SAME mesh, so a one-point band
on choff.msh answers it in minutes:

    Zc = 1/(j w C) = -331j ohm at C = 0.196 pF, 2.45 GHz

    PARALLEL:  Z = 50 || -331j  =  48.9 + 7.4j   ->  |S11| barely moves
    SERIES:    Z = 50 - 331j                     ->  |Gamma| ~ 0.96, huge change

⚠️ The cavity's own impedance is in the loop too, so neither prediction is exact.
The DISCRIMINATION does not depend on that: a parallel C is a ~2% perturbation on
50 ohm, a series C is a 331 ohm dominant term. Orders of magnitude apart, so the
structure's contribution cannot flip the verdict.
"""
import json
import math
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
import solveconf

PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
import os
HOME = pathlib.Path.home()
ENV = {**os.environ,
       "PATH": f"{HOME}/.local/share/mamba/envs/emsim/bin:{os.environ['PATH']}",
       "MAMBA_ROOT_PREFIX": str(HOME / ".local/share/mamba")}

MESH = "choff.msh"
F0 = 2.41692                      # TE011 on this mesh, so the loop is driven
C_FARAD = 1.96e-13
BAND = (F0 - 0.0004, F0 + 0.0004)  # tiny band -> few ROM samples -> fast


def run(tag, cap):
    c, meta, _ = solveconf.driven(MESH, tag, BAND, step=2e-4)
    if cap is not None:
        c["Boundaries"]["LumpedPort"][0]["C"] = cap
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    t0 = time.time()
    rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"], env=ENV,
                        stdout=open(f"{tag}_p.log", "w"),
                        stderr=subprocess.STDOUT).returncode
    dt = time.time() - t0
    if rc != 0:
        tail = pathlib.Path(f"{tag}_p.log").read_text().strip().splitlines()
        print(f"  🔴 {tag}: rc={rc} — {tail[-1] if tail else ''}", flush=True)
        return None
    recs = dq.load(tag)
    if not recs:
        return None
    m = min(recs, key=lambda r: abs(r["f"] - F0))
    print(f"  {tag}: {dt:.0f}s  f={m['f']:.5f}  |S11|={m['s_db']:8.4f} dB  "
          f"|Gamma|={m['gamma']:.5f}", flush=True)
    return m


print(__doc__)
w = 2 * math.pi * F0 * 1e9
Zc = -1.0 / (w * C_FARAD)
zp = complex(50, 0) * complex(0, Zc) / (complex(50, 0) + complex(0, Zc))
zs = complex(50, Zc)
print(f"  Zc = {Zc:.0f}j ohm")
print(f"  predicted parallel Z = {zp.real:.1f}{zp.imag:+.1f}j  ->  "
      f"|Gamma| = {abs((zp-50)/(zp+50)):.4f}")
print(f"  predicted series   Z = {zs.real:.1f}{zs.imag:+.1f}j  ->  "
      f"|Gamma| = {abs((zs-50)/(zs+50)):.4f}")
print("=" * 78, flush=True)

a = run("rig_noC", None)
b = run("rig_wC", C_FARAD)

print("\n" + "=" * 78)
if a and b:
    d = b["gamma"] - a["gamma"]
    print(f"  |Gamma| without C: {a['gamma']:.5f}")
    print(f"  |Gamma| with    C: {b['gamma']:.5f}   change {d:+.5f}")
    if abs(d) < 0.05:
        print("\n  ✅ PARALLEL confirmed — adding C barely moves the reflection.\n"
              "     The record is right: a series capacitor must be built as a\n"
              "     geometric gap, and the port C cannot stand in for it.")
    else:
        print("\n  🔴 SERIES — adding C changes the reflection substantially.\n"
              "     The record's claim is WRONG, two geometric sweeps were spent\n"
              "     on a problem that did not exist, and R62 can be answered by\n"
              "     setting C on the port.")
else:
    print("  🔴 a case failed — see the logs")
print(flush=True)
