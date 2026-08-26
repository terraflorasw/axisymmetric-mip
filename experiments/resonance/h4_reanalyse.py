"""Re-score h4_field's SAVED raw data with the current analysis layer.

CONVENTIONS §10: drivers emit data with provenance, verdicts live in a
re-runnable layer. h4_field's run-2 solves (2026-08-23 13:33) are sound — four
cases converged, V2-Q passed — but the log they printed was scored by an
analysis layer carrying two arithmetic bugs, both fixed in h4_field.py at 13:35
and never re-run:

  1. j1(chi * r_mm*1e-3 / a_mm)  — r in metres, a in millimetres. 1000x wrong
     Bessel argument; V2 E0 reported 1.486e9 against 1.691e6 and "FIRED" at
     87,800%. It was a unit error in the CHECK, not a bad field.
  2. the argon contour compared prof[i]/sqrt(2) against the threshold when
     prof is ALREADY rms — every contour pushed ~1.41x too far out, which is
     what produced "🔴 will not light" for cases that do.

Also: R_RESOLVED is no longer the asserted 1.0 mm. It is CALIBRATED per run from
the no-torch rake against J1 — exact for an empty cavity — scanning inward from
the mode peak. F2's 56-65% "departure" was read off the r = 0.5 mm probe, and
after the first fix off r = 1.0 mm, which was still the first included point.

No solving. Reads h4_field.result.json, calls the same _report the rig calls.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import h4_field
from e0k2_anchor import design_point

# 🔴 GUARDED 2026-08-24 — BUT ONLY HALFWAY, AND THE COMMENT SAID OTHERWISE.
# The note below claimed this no longer ran on import. Only the final
# `_report` call was ever moved behind the guard: the file READ, the
# design_point() solve and three prints all still executed at import time, so
# `import h4_reanalyse` still did work and still printed. Fixed properly
# 2026-08-25 — a correction applied to one of two adjacent sites reads as done
# (CONVENTIONS 7bl), and a comment asserting the fix makes it worse.
#
# The original hazard, unchanged: any module that did `import h4_reanalyse`
# re-ran the whole analysis and REWROTE h4_field.result.json as a side effect.
# A rig must not act when it is merely read.
#
# ⚠️ DEBT, not fixed here: this still takes a positional argv and defaults to
# an UNSLUGGED "h4_field.result.json". H4 is PARKED (NEXT.md item 6), so it is
# left alone rather than half-migrated; when H4 restarts it takes --slug like
# every other rig.
def main():
    src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                       else "h4_field.result.json")
    out = json.loads(src.read_text())
    a, L = design_point()
    exact = ph.spectrum(a, L, fmax=3.2)["TE011"]

    print(f"  re-scoring {src} with the 13:35 analysis layer")
    print(f"  cavity a={a:.4f} L={L:.4f}  analytic TE011 {exact:.6f} GHz")
    print(f"  RESOLVE_TOL = {h4_field.RESOLVE_TOL} "
          f"(R_RESOLVED is now calibrated per-run from the no-torch rake)")
    h4_field._report(out, exact)


if __name__ == "__main__":
    main()
