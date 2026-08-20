#!/usr/bin/env python3
"""R99b — LOCATE TM020 at the sapphire point. Re-solve only; no new meshes.

R99 measured, in the (2.26, 2.48) window, at L = 88.53:

    quartz    TM020 at 2.37330, boreE 2.362%  (tm020.f_raw_order1 = 2.37546 ✓)
    sapphire  NO mode with boreE above 0.25% anywhere in the window

The predicted direction is exactly this: TM020's E_z ~ J0 is MAXIMUM on axis,
where the torch is, so it is the mode sapphire loads hardest and it moves DOWN.

🔴 BUT "ABSENT FROM A WINDOW IS NOT ABSENT." That inference has been retracted
three times in this record — R54's TM111/TM020, R77's excluded 2.3431, R59's
unlocated TM111. The mode is UNLOCATED, not "below 2.26", and the difference
between those two statements is the entire result: the primary criterion is a
CLEARANCE, and a clearance cannot be computed from an absence.

🔑 ALSO: R99's OWN NULL CONTROL IS VOID, NOT PASSED. It required s99sa and s99pr
to agree on f(TM020) — unevaluable when neither has one. Nothing about TM020 from
R99 should be read until this run finds it.

WHAT THIS RUN IS: the same three meshes, a lower window, a coarser step. LOCATE
only. Once TM020 is found, a narrow fine sweep can measure it properly.

    band  (2.05, 2.30)   250 MHz — wide enough that a shift several times the
                         quartz->sapphire TE011 shift is still captured
    step  2e-4           200 kHz = ~11 points across a 2.3 MHz linewidth. Ample
                         to locate; NOT the step to quote a linewidth from.

⚠️ s99qz is included even though its TM020 is already known. It is the control
that proves the low window is being read correctly — if a spurious boreE mode
appears down here in QUARTZ too, the identification is wrong, not the physics.
"""
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import results
import solveconf
import solver

TAGS = ["s99qzL", "s99saL", "s99prL"]
MESH = {"s99qzL": "s99qz.msh", "s99saL": "s99sa.msh", "s99prL": "s99pr.msh"}
BAND, STEP = (2.05, 2.30), 2e-4
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")


def run(tag):
    mesh = MESH[tag]
    meta = solveconf.load_meta(mesh)
    pl = meta["attributes"].get("plasma")
    c, meta, _ = solveconf.driven(
        mesh, tag, BAND, step=STEP, order=1,
        materials={pl: {"Permittivity": 1.0, "Permeability": 1.0}})
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    eps = meta["geometry_mm"]["torch_material"]
    got = [m for m in c["Domains"]["Materials"]
           if m["Attributes"] == [meta["attributes"]["torch"]]]
    assert len(got) == 1 and abs(got[0]["Permittivity"] - eps[0]) < 1e-9, (
        f"{tag}: config/mesh torch material disagree (R101)")
    print(f"  {tag}: {mesh} eps={eps[0]} L={meta['geometry_mm']['length']}",
          flush=True)
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
for t in TAGS:
    run(t)
idx, got = results.sweep(
    TAGS, "r99b",
    extra=dict(question="where is TM020 at the sapphire point?",
               purpose="LOCATE only — 200 kHz step is not a linewidth step",
               control="s99qzL must show TM020 at ~2.3733 and nothing spurious "
                       "in the low window",
               supersedes="R99's TM020 rows, which were an ABSENCE not a "
                          "measurement"))
print(f"\n  wrote {len(got)} result files + r99b.sweep.json")
print("  ⚠️ NO VERDICT HERE — mode identity is by boreE signature", flush=True)
