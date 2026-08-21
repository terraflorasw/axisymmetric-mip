"""Does a generated solver config actually carry the declared wall metal?

The binding failed silently for the whole programme: baselines.json starts empty
by design, so solveconf fell through to the template's SILVER (6.3e7) on every
solve while printing a warning nobody acted on.

VERIFICATION   a config built by solveconf carries baselines' wall.conductivity.
FALSIFICATION  it carries the template value, or any other number; or a missing
               declaration fails to stop the solve.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import solveconf


def main():
    base = json.loads(pathlib.Path("baselines.json").read_text())
    want = base["wall.conductivity"]["value"]
    tmpl = json.loads(pathlib.Path(solveconf.TEMPLATE).read_text())
    tval = tmpl["Boundaries"]["Conductivity"][0]["Conductivity"]
    print(__doc__)
    print(f"  declared in baselines : {want:.4g} S/m "
          f"({base['wall.conductivity']['material']})")
    print(f"  template  {solveconf.TEMPLATE:<12}: {tval:.4g} S/m  <- must NOT win")

    # a DRIVEN config needs a coupling loop, so pick a mesh whose sidecar has a
    # port direction rather than whichever sorts first
    meshes = []
    for mp in sorted(pathlib.Path(".").glob("*.msh")):
        side = mp.with_suffix(".meta.json")
        if not side.exists():
            continue
        if json.loads(side.read_text()).get("port_direction"):
            meshes.append(mp)
    if not meshes:
        print("  ⚠️ no mesh WITH A LOOP present — cannot build a driven config "
              "here. REPORTED, not passed.")
        return 2
    m = str(meshes[0])
    c, _meta, _dropped = solveconf.driven(m, "_condcheck", (2.44, 2.45),
                                          step=1e-3, order=2)
    got = c["Boundaries"]["Conductivity"][0]["Conductivity"]
    print(f"  config built from {m}: {got:.4g} S/m")
    ok = abs(got - want) / want < 1e-9
    print(f"  {'✅ config carries the declared metal' if ok else '🔴 MISMATCH'}")
    if abs(got - tval) / tval < 1e-9 and abs(tval - want) / want > 1e-9:
        print("  🔴 it is the TEMPLATE value — the binding is not working")
        ok = False

    # the refusal must also work: a missing declaration must STOP a solve
    bp = pathlib.Path("baselines.json")
    orig = bp.read_text()
    try:
        d = json.loads(orig)
        d.pop("wall.conductivity")
        bp.write_text(json.dumps(d, indent=1) + "\n")
        try:
            solveconf.driven(m, "_condcheck2", (2.44, 2.45), step=1e-3, order=2)
        except RuntimeError:
            print("  ✅ a missing declaration REFUSES to solve")
        else:
            print("  🔴 a missing declaration still solved — silent fallback lives")
            ok = False
    finally:
        bp.write_text(orig)

    for f in pathlib.Path(".").glob("_condcheck*"):
        f.unlink(missing_ok=True)
    print(f"\n  {'✅ ALL PASS' if ok else '🔴 FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
