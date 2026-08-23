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

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "h4_field.result.json")
out = json.loads(src.read_text())
a, L = design_point()
exact = ph.spectrum(a, L, fmax=3.2)["TE011"]

print(f"  re-scoring {src} with the 13:35 analysis layer")
print(f"  cavity a={a:.4f} L={L:.4f}  analytic TE011 {exact:.6f} GHz")
print(f"  RESOLVE_TOL = {h4_field.RESOLVE_TOL} "
      f"(R_RESOLVED is now calibrated per-run from the no-torch rake)")
h4_field._report(out, exact)
