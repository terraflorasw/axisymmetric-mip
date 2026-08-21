"""Recompute the TE011/TM111 splitting from SAVED results. No solver.

Nine rigs reported the two-nearest gap, which is TM111's internal polarisation
splitting, not TE011<->TM111. The fix is in eigmodes.te011_tm111 — and because
every rig saved its full mode list, the corrected number comes out of the
existing data. Re-analysis, not re-solving: the split that E1b was refactored
for, paying off on an unrelated bug.
"""
import glob
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import eigmodes
import physics as ph

A_MM, L_MM = 103.70, 88.53
EXACT = ph.spectrum(A_MM, L_MM)["TE011"]


def main():
    print(__doc__)
    print(f"  exact TE011 = {EXACT:.6f} GHz\n")
    print(f"  {'result file':<22}{'case':<16}{'OLD (TM111 pair)':>18}"
          f"{'CORRECTED':>12}{'ratio':>8}")
    for f in sorted(glob.glob("e0*.result.json")):
        try:
            d = json.load(open(f))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(d, dict):     # e0l writes a list of timings
            continue
        for k, v in d.items():
            # a case is any key whose value is a plain list of frequencies
            if not (isinstance(v, list) and len(v) >= 3
                    and all(isinstance(x, (int, float)) for x in v)):
                continue
            near = sorted(v, key=lambda x: abs(x - EXACT))
            if abs(near[0] - EXACT) > 0.05:      # no triplet here
                continue
            old = 1e3 * abs(near[1] - near[0])
            r = eigmodes.te011_tm111(v, EXACT)
            if not r:
                continue
            new = r["splitting_mhz"]
            print(f"  {f:<22}{k:<16}{old:>18.4f}{new:>12.4f}"
                  f"{(new/old if old else float('nan')):>8.1f}x")
    print("\n  OLD = gap between the two nearest = TM111's two polarisations")
    print("  CORRECTED = TE011 to the TM111 pair mean, true value EXACTLY 0")


if __name__ == "__main__":
    main()
