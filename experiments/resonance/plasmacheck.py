"""Does --plasma actually build a plasma region? One mesh, before 16 solves.

🔴 WHY BOTHER. `--tag-groove` defaulted OFF and nobody noticed for two rigs;
`--no-torch` leaves the torch REGION in place; the port meshed with 2 elements
for the whole life of the driven programme. Assuming a geometry flag did what it
says is how all three of those survived. Ask the mesh.
"""
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import solveconf
import meshattrs
from e0_solver_vs_math import GEO
from e0k2_anchor import design_point
from h3_loaded import SECTORS, INNER_R, Z_FRAC

R = 4.0


def main():
    a, L = design_point()
    zlo, zhi = -Z_FRAC * L, Z_FRAC * L
    tag = "plasmacheck"
    args = (list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                         "--sectors", str(SECTORS),
                         "--plasma", f"{INNER_R},{R},{zlo:.4f},{zhi:.4f}",
                         "--plasma-h", f"{max(0.4, R/6.0):.3f}"])
    print(f"  --plasma {INNER_R},{R},{zlo:.4f},{zhi:.4f}", flush=True)
    r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                        "--size-factor", "1.5"] + args,
                       capture_output=True, text=True)
    if r.returncode or not pathlib.Path(f"{tag}.msh").exists():
        raise SystemExit(f"🔴 mesh failed:\n{(r.stdout + r.stderr)[-800:]}")
    m = solveconf.load_meta(f"{tag}.msh")
    attrs = m["attributes"]
    print(f"  {m['tets']:,} tets")
    print(f"  plasma attribute: {attrs.get('plasma')}")
    print(f"  bore attribute:   {attrs.get('bore')}")
    c = meshattrs.counts(f"{tag}.msh")
    ok = True
    for (dim, t, nm), n in sorted(c.items()):
        if dim != 3:
            continue
        mark = ""
        if nm == "plasma":
            mark = ("   ✅ plasma region present"
                    if n > 200 else f"   🔴 ONLY {n} ELEMENTS — under-resolved")
            ok &= n > 200
        print(f"    attr {t:>3}  {nm or '(unnamed)':<12}{n:>9,} elements{mark}")
    if attrs.get("plasma") is None:
        print("  🔴 NO plasma attribute — --plasma did not take effect")
        ok = False
    print(f"\n  {'✅ READY for the sweep' if ok else '🔴 DO NOT RUN THE SWEEP'}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
