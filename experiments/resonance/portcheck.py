"""Does the mesh actually RESOLVE the lumped port? Build one and count.

🔴 WHY. The port surface came back with **2 elements** on a 1.8 x 0.30 mm
rectangle against a 1.2 mm mesh floor. The port IS the drive point, so beta rode
on how those two triangles happened to fall: the SAME geometry at 1 and 5
azimuthal sectors gave beta 0.5598 and 0.3411 — 39% apart — and the loop-area
sizing sweep came back non-monotonic for the same reason.

R62 diagnosed exactly this for the SERIES capacitor gap and fixed it there only.
The PRIMARY port gap was left below the floor for the whole life of the driven
programme.

VERIFICATION
  V1  the port surface must carry >= 20 elements. Two triangles cannot
      represent a drive point.
  V2  the mesh floor must be below the gap, not above it.
FALSIFICATION
  🔴 F1  if the element count does not rise, the field is not reaching the port
         and lowering the floor achieved nothing — which is precisely R15's
         warning that a floor does not refine anything on its own.
  🔴 F2  if the tet count explodes (> 3x), the refinement is not local and the
         Ball radius is wrong.
"""
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import solveconf
import meshattrs
from e0_solver_vs_math import GEO
from e0k2_anchor import design_point, CAP_R_FRAC, LOOP_PHI, LOOP_RW, LOOP_GAP


def build(tag, a, L, ld, lw, cap_r, extra):
    args = (list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}"]
            + ["--loop", f"{ld},{lw},{LOOP_RW},{LOOP_GAP}",
               "--loop-cap", f"{cap_r:.4f}", "--loop-phi", LOOP_PHI] + extra)
    r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                        "--size-factor", "1.5"] + args,
                       capture_output=True, text=True)
    out = r.stdout + r.stderr
    for line in out.splitlines():
        if "PORT refinement" in line or "floor" in line.lower():
            print(f"      {line.strip()}")
    if r.returncode or not pathlib.Path(f"{tag}.msh").exists():
        raise RuntimeError(f"{tag}: mesh failed — {out[-400:]}")
    return solveconf.load_meta(f"{tag}.msh")


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    cap_r = CAP_R_FRAC * a
    rows = []
    for label, extra in (("1 sector", []), ("5 sectors", ["--sectors", "5"])):
        tag = f"portcheck_{label.split()[0]}s"
        print(f"\n  --- {label}", flush=True)
        m = build(tag, a, L, 11.0, 8.0, cap_r, extra)
        c = meshattrs.counts(f"{tag}.msh")
        port = next((n for (d, t, nm), n in c.items() if d == 2 and nm == "port"), None)
        tets = sum(n for (d, _t, _nm), n in c.items() if d == 3)
        floor = (m.get("sizing_mm") or {}).get("min")
        rows.append((label, port, tets, floor))
        print(f"      port surface: {port} elements   tets {tets:,}   "
              f"floor {floor:.3f} mm", flush=True)

    print("\n" + "=" * 78)
    print(f"  {'mesh':<12}{'port elts':>11}{'tets':>10}{'floor mm':>10}   before")
    BEFORE = {"1 sector": (2, 33608, 1.2), "5 sectors": (2, 35738, 1.2)}
    ok = True
    for label, port, tets, floor in rows:
        b = BEFORE[label]
        v1 = port is not None and port >= 20
        v2 = floor is not None and floor < LOOP_GAP
        f2 = tets > 3 * b[1]
        ok &= v1 and v2 and not f2
        print(f"  {label:<12}{port:>11}{tets:>10,}{floor:>10.3f}   "
              f"was {b[0]} elts / {b[1]:,} tets / {b[2]:.1f} mm")
        print(f"      V1 port >= 20 elements: {'✅' if v1 else '🔴 F1 — the field is not reaching the port'}")
        print(f"      V2 floor < {LOOP_GAP} mm gap: {'✅' if v2 else '🔴'}")
        if f2:
            print(f"      🔴 F2 FIRES: tets grew {tets/b[1]:.1f}x — refinement is not local")
    print(f"\n  {'✅ PORT RESOLVED' if ok else '🔴 SEE FAILURES ABOVE'}")


if __name__ == "__main__":
    main()
