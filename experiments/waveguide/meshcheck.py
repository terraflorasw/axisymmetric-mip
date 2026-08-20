#!/usr/bin/env python3
"""Postconditions on a mesh sweep: did the thing you asked for actually happen?

R50. Two silent no-ops in one night, both of which produced a confident verdict
from meshes that were never modified:

  set_pts        A plasma size prescribed through boundary POINTS, with
                 Mesh.MeshSizeExtendFromBoundary = 0, never reaches the volume
                 interior. Changed the mesh by 795 tets where ~29,000 were
                 expected.
  MeshSizeMin    A hard floor at 1.2 mm silently clamped requested plasma meshes
                 of 1.0 and 0.6 mm to the same value. Both came back as the SAME
                 mesh — 14,703 vs 14,586 tets — and the run reported
                 "39.5% apart, NOT CONVERGED" while comparing a mesh against
                 itself.

Neither raises an error. Both were caught only by counting elements by hand
afterwards. This makes that check mechanical.

🔑 THE DISTINCTION THAT MATTERS: a **sizing** parameter MUST change the element
count — that is what it is for. A **shape** parameter need not: ovality changed
the mesh by 0.4% and was still perfectly applied. Blanket "meshes must differ"
would be wrong and would cry wolf on every geometry sweep.
"""
import json
import pathlib
import sys

# Parameters whose entire purpose is to change mesh density. If one of these
# differs between two cases and the element count does not, it did not take.
SIZING = ("plasma_h",)
# Flags that BREAK A CONDUCTOR. If one is on, the exterior-surface count must
# rise: new faces appear where the conductor was cut. R62's second gap
# overlapped by 14 mm instead of separating, leaving 23 PEC surfaces either way,
# and Q_ext stayed flat across every gap while two sweeps were spent on it.
BREAKING = ("loop_gap2",)
MIN_REL_CHANGE = 0.02          # 2%; the two real no-ops both sat at 0.8%


class NoOp(RuntimeError):
    pass


def meta(tag):
    p = pathlib.Path(f"{tag}.meta.json")
    if not p.exists():
        raise FileNotFoundError(f"{p.name} missing — rebuild through geometry.py")
    return json.loads(p.read_text())


def check(tags, strict=True):
    """Verify a sweep's meshes differ where they were asked to differ."""
    ms = {t: meta(t) for t in tags}
    problems = []

    for t, m in ms.items():
        s = m.get("sizing_mm", {})
        if s.get("plasma_clamped"):
            problems.append(
                f"{t}: plasma_h {s['plasma_requested']:.2f} mm is BELOW the "
                f"{s['min']:.2f} mm MeshSizeMin floor and was clamped — the "
                f"refinement you asked for did not happen")

    base = [m for m in ms.values()
            if not any(m["geometry_mm"].get(k) for k in BREAKING)]
    for t, m in ms.items():
        on = [k for k in BREAKING if m["geometry_mm"].get(k)]
        if on and base and "pec_surfaces" in m and "pec_surfaces" in base[0]:
            if m["pec_surfaces"] <= base[0]["pec_surfaces"]:
                problems.append(
                    f"{t}: {'/'.join(on)} is set but the exterior-surface count "
                    f"({m['pec_surfaces']}) did not rise above the unbroken case "
                    f"({base[0]['pec_surfaces']}) — the conductor was NOT broken")

    facs = {t: m["size_factor"] for t, m in ms.items()}
    if len(set(facs.values())) > 1:
        problems.append("cases do not share a size-factor, so they are not "
                        "comparable: " + ", ".join(f"{t}={f}" for t, f in facs.items()))

    seen = list(ms.items())
    for i in range(len(seen)):
        for j in range(i + 1, len(seen)):
            (ta, ma), (tb, mb) = seen[i], seen[j]
            ga, gb = ma["geometry_mm"], mb["geometry_mm"]
            differing = [k for k in SIZING if ga.get(k) != gb.get(k)]
            if not differing:
                continue
            na, nb = ma["tets"], mb["tets"]
            rel = abs(na - nb) / max(na, nb)
            if rel < MIN_REL_CHANGE:
                problems.append(
                    f"{ta} vs {tb}: {'/'.join(differing)} differ "
                    f"({[ga.get(k) for k in differing]} vs "
                    f"{[gb.get(k) for k in differing]}) but element counts are "
                    f"{na:,} vs {nb:,} — {100*rel:.1f}% apart. The refinement "
                    f"did not take effect; do NOT read results from this.")

    if problems:
        msg = "🔴 mesh postcondition failed:\n  " + "\n  ".join(problems)
        if strict:
            raise NoOp(msg)
        print(msg, flush=True)
        return False
    print(f"  ✅ mesh postconditions pass for {len(tags)} case(s): "
          f"shared size-factor, no clamped refinements, sizing changes took "
          f"effect", flush=True)
    return True


if __name__ == "__main__":
    sys.exit(0 if check(sys.argv[1:], strict=False) else 1)
