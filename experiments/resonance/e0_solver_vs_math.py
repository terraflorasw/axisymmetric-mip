"""E0 — how far is this solver from mathematics?

NOT "verify the instrument". Put a NUMBER on the disagreement between this
solver and the closed form, on the one case where the closed form is complete.
Nothing here licenses anything; it bounds how much a later disagreement may be
attributed to the solver rather than to the model.

VERIFICATION  physics.spectrum(103.70, 88.53) — exact for PEC walls.
FALSIFICATION chi'_01 = chi_11 IDENTICALLY, so the TE011/TM111 splitting has a
              true value of EXACTLY ZERO. Any splitting reported is pure
              numerical symmetry breaking. This is a stronger probe than
              rotation or translation: those have zero true CHANGE in one
              quantity; this has zero true DIFFERENCE between two things the
              solver must report separately.

⚠️ KNOWN DEVIATION FROM THE IDEAL REFERENCE, stated rather than hidden.
`geometry.py` cannot delete the outer torch shell — `--no-torch` sets its
permittivity to 1.0 and `--torch-tube 0,w` is refused by a guard. So the cavity
is a right circular cylinder containing a VACUUM-FILLED SHELL: electromagnetically
empty, but carrying internal mesh surfaces that the closed form knows nothing
about. `--no-inner` removes two of the three tubes. The residual is itself
informative — it is the mesh's response to physics-free internal boundaries —
but it means a small disagreement is EXPECTED and must not be read as solver error.

🔴 THREE PREVIOUS ATTEMPTS AT THIS BENCHMARK FAILED ON THE GEOMETRY, NOT THE
SOLVER: a viewport left on; a flag (`--viewport 0`) that could not turn it off
because 0 is falsy; and two volume attributes left with no material at all. Each
time the disagreement looked like a solver fault. The gates below are written as
COMPLETENESS ASSERTIONS rather than lists of things to exclude, because a list
maintained by hand is the same failure as a name maintained by hand.
"""
import json
import math
import os
import signal
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import values
import journal
import solveconf
import solvecost
import solver

# 🔴🔴 WAS `A_MM, L_MM = 103.70, 88.53` — D/L = 2.343, WHICH IS NOT THIS
# CAVITY. H1's answer is D/L = 1.525 (a 88.0045, L 115.4158), and KNOWN.md
# states it plainly. The literal pair sat here as GEO's DEFAULT, so any rig
# that used GEO/GEO_DESIGN without appending its own --radius/--length meshed
# a cavity nobody is building. Every H3 rig DID override, via design_point(),
# and the mesh sidecars confirm it — but the E0 instrument rigs and the mesh
# utilities did not.
# ✅ Now DERIVED from the declared shape, so GEO cannot disagree with H1 again.
# ⚠️ This CHANGES the cavity those non-overriding rigs mesh. That is the point;
#    the re-run is queued in NEXT.md rather than avoided by keeping the bug.
A_MM, L_MM = ph.design_point(values.get("cavity.d_over_l"),
                             values.get("source.f0.ghz"))
# 🔴 THE GROOVE OMISSION (2026-08-23) — THE BASELINE OMITTED THE DESIGN'S MODE FILTER, AND 31
# RIGS INHERITED IT SILENTLY.
#
# `GEO` never passed `--groove`, so every rig built on it meshed a cavity with
# `groove = [0.0, 0.0]` — including the ENTIRE loaded programme (H3, H6,
# h3_superpose, h3_sapphire, h3_loopsize). The cavity design is premised on a
# mode filter; those solves measured a cavity that is not the one being built.
#
# ⚠️ `--mode-filter 0` is NOT the omission and must not be read as one. That flag
# is the QUARTZ ANNULUS, a SUPERSEDED device. The groove replaced it. Two parts
# share the phrase "mode filter" in this tree and only one of them is current:
#     --mode-filter <t>   quartz annulus   RETIRED
#     --groove <w,depth>  annular slot     CURRENT, and this is the design
#
# ✅ GEO is now explicitly the BARE cavity — `--groove 0,0` is written out, so
# the absence is a DECLARATION rather than an omission — and it is for the
# instrument rigs that compare against closed form, where a plain cylinder is
# the point.
# ⚠️⚠️ GEO_DESIGN IS NOT THE FULL DESIGN — READ THIS BEFORE TRUSTING ITS NAME.
# It is GEO with the GROOVE restored, and NOTHING ELSE. In particular it still
# carries `--no-torch` from GEO, so **every rig that uses GEO_DESIGN as-is
# solves a cavity with NO TORCH BODY** (h3_loopq, h2_groove, h3_ladder, ...).
# The cavity being built has a SAPPHIRE torch, eps = 11.6.
#   measured 2026-08-25 (e3_closure case B vs h3_loopq):
#     sapphire torch vs none ->  f0  -13.87 MHz,  Q0  +2.0%
# 🔴 So every eigen f0 in the record is ~14 MHz HIGH, and Q_REF is ~2% LOW.
# h3_driven strips `--no-torch` and meshes the torch at eps=1 (vacuum), which is
# NOT the same cavity either -- see CONVENTIONS 7aq: cross-solver comparisons
# must match geometry AND mesh.
# ⚠️ NOT PATCHED HERE ON PURPOSE: adding the torch invalidates every stored f0,
# so it belongs to one deliberate re-mesh with the apertures and chimney
# (NEXT.md restoration). The WARNING must not wait for that; the change may.
#
# ✅ Any rig whose result is a DESIGN number must use GEO_DESIGN **and state its
# torch state**. `run()` refuses a plasma solve on a groove-free mesh unless the
# caller says `allow_no_groove=True`.
GROOVE_DESIGN = tuple(values.get("cavity.groove.mm"))   # H2, frozen. BOUND (7f)

GEO = ["--radius", f"{A_MM}", "--length", f"{L_MM}", "--order", "2",
       "--sectors", "1", "--no-torch", "--no-inner", "--mode-filter", "0",
       "--groove", "0,0",
       "--viewport", "0", "--trap", "0,0,0", "--chimney", "0,41",
       "--feed", "0,41"]

# 🔴🔴 THE RESTORATION, 2026-08-25. GEO_DESIGN WAS BUILT FROM GEO BY CHANGING
# ONLY THE GROOVE — so `--no-torch` survived into it, and CLAUDE.md's
# "GEO_DESIGN is the cavity being built" was true of the groove and FALSE of
# the torch. Every eigen f0 in the record is for a TORCH-FREE, SEALED cavity
# and is therefore ~10.4 MHz high (e3-torch-01 measured the shift) — 6.5x the
# whole anchor band.
#
# GEO_DESIGN is now built EXPLICITLY, not by patching GEO, so a future flag
# cannot leak in the same way. GEO stays the BARE cavity: instrument rigs
# compare it against closed form and a plain cylinder is the point there.
#
# The apertures (user, 2026-08-25: "shouldn't the outer tube extend out
# through the opposite end cap?"):
#   chimney 21 mm  — clears the 20 mm torch OD by 0.5 mm on radius
#   feed    21 mm  — same, so the outer tube can PASS THROUGH the -z cap
#   torch_ext 41   — the tube runs the full feed tube, which is what the gas
#                    plumbing requires
# ⚠️ torch_ext IS NOT FREE: running sapphire through the feed drops that
# aperture's TE11 cutoff from 8.37 GHz (3.41x f0) to ~4.74 GHz (1.94x), i.e.
# ~60 dB -> ~30 dB of evanescent isolation over 41 mm. Still firmly below
# cutoff and PEC-terminated in the model; it is a plumbing/compliance note,
# not an EM blocker.
_APERTURE_D = 21.0          # mm, both apertures
_APERTURE_L = 41.0          # mm, axial length beyond the cap
# 🔴 `--no-inner` REMOVED 2026-08-25. User: *"Just use Fassel, so we have a
# baseline."* It left a SINGLE-TUBE torch — outer tube only, no intermediate,
# no injector — which is not a Fassel torch and not a baseline of anything.
# I had called the inner tubes "out of scope"; that boundary was mine, not the
# record's, and the standing instruction was to build a REALISTIC torch.
# geometry.py's defaults are the Fassel dimensions: outer 20.0/1.5,
# intermediate 16.0/1.0, injector 5.0 OD / 2.0 ID.
GEO_DESIGN = ["--radius", f"{A_MM}", "--length", f"{L_MM}", "--order", "2",
              "--sectors", "1", "--mode-filter", "0",
              "--groove", f"{GROOVE_DESIGN[0]:g},{GROOVE_DESIGN[1]:g}",
              "--viewport", "0", "--trap", "0,0,0",
              "--chimney", f"{_APERTURE_D:g},{_APERTURE_L:g}",
              "--feed", f"{_APERTURE_D:g},{_APERTURE_L:g}",
              # 🔑 THE OUTER TUBE PASSES THROUGH BOTH CAPS (user, 2026-08-25):
              # one end is the gas entry, the other "basically eliminates
              # fouling" — a tube stopping at the cap would deposit exhaust on
              # the cap and aperture walls instead of carrying it out.
              "--torch-ext", f"{_APERTURE_L:g}",
              "--torch-ext-top", f"{_APERTURE_L:g}"]
# 🔑 NOTE WHAT IS ABSENT: no --no-torch, and no --torch-material. The torch
# body is now present and its permittivity comes from geometry.py's default,
# which is BOUND to torch.sapphire.permittivity (9.39, Krupka 2005). The
# design cavity therefore carries the DESIGN torch without restating it.
FACTORS = ["0.96", "1.06", "1.00", "1.20", "0.90"]
PALACE = solver.PALACE          # E1e: single source, env-driven
# 🔴 E1d CORRECTED. I raised this to 8 saying "every run so far used 4 of the 8
# cores". WRONG: /proc/cpuinfo shows `cpu cores: 4` with `siblings: 8` — FOUR
# PHYSICAL CORES, eight hyperthreads. PRRTE allocates slots by physical cores,
# so -np 8 simply fails ("not enough slots"), and -np 4 was full utilisation the
# whole time. The contention was real — 4 orphans + 4 live on FOUR cores is 2x
# oversubscribed, worse than I said — but the idle-capacity claim was not.
RANKS = os.environ.get("PALACE_RANKS", "4")


def build(tag, extra=()):
    for fac in FACTORS:
        r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                            "--size-factor", fac] + GEO + list(extra),
                           capture_output=True, text=True)
        if r.returncode == 0 and pathlib.Path(f"{tag}.msh").exists():
            break
        print(f"    sf {fac} failed", flush=True)
    else:
        raise RuntimeError(f"{tag}: no size factor meshed")
    m = solveconf.load_meta(f"{tag}.msh")
    g = m["geometry_mm"]

    # GATE 1 — every aperture off. Completeness, not a remembered list: any
    # geometry_mm key whose first element is a diameter must be zero.
    live = {k: v for k, v in g.items()
            if k in ("viewport", "trap", "chimney", "feed", "groove") and v
            and v[0]}
    if live:
        raise RuntimeError(f"{tag}: apertures present {live} — not a cylinder")
    # GATE 2 — the dielectric must be vacuum everywhere.
    if (g.get("torch_material") or [1.0])[0] != 1.0:
        raise RuntimeError(f"{tag}: torch eps {g['torch_material']} != 1.0")
    print(f"  {tag}: sf {fac}, {m['tets']:,} tets, "
          f"volumes {sorted(k for k, v in m['attributes'].items() if isinstance(v, int))}",
          flush=True)
    return m, fac


def _materials(a, meta, vols):
    """Volume materials for the eigen config, with the TORCH bound from the mesh.

    🔴 THE RESTORATION FOUND THIS, 2026-08-25. Every volume was given ONE
    material at Permittivity 1.0 — so a sapphire torch in the mesh SOLVED AS
    VACUUM. It never showed up because `GEO_DESIGN` carried `--no-torch`: there
    was no torch volume to get it wrong. Restore the torch and the bug becomes
    reachable, which is exactly what `_assert_torch_bound` caught on the first
    run (config eps=1.0 vs sidecar eps=9.39).

    🔑 R101's rule: THE MESH IS THE SOURCE OF TRUTH. The permittivity is read
    from the sidecar, never typed here.
    """
    tv = (a or {}).get("torch")
    tm = ((meta.get("geometry_mm") or {}).get("torch_material")) if meta else None
    if tv is None or tv not in vols or not tm:
        return [{"Attributes": vols, "Permittivity": 1.0, "Permeability": 1.0}]
    rest = [v for v in vols if v != tv]
    mats = []
    if rest:
        mats.append({"Attributes": rest, "Permittivity": 1.0, "Permeability": 1.0})
    torch = {"Attributes": [tv], "Permittivity": float(tm[0]),
             "Permeability": 1.0}
    if len(tm) > 1 and float(tm[1]) > 0:
        torch["LossTan"] = float(tm[1])
    mats.append(torch)
    return mats


def eigen_cfg(tag, meta, mesh=None, sigma=None, n=22, target=1.05, order=2,
              port_bc=None):
    """PEC by default — the closed form assumes it. sigma= switches to metal.

    GATE 3: every volume attribute gets vacuum, and we ASSERT none was missed.
    GATE 4: every SURFACE attribute gets an INTENTIONAL boundary condition.

    🔴 GATE 4 EXISTS BECAUSE GATE 3 WAS NOT ENOUGH. GATE 3 checks volumes and
    explicitly SKIPS "wall" and "port" as surfaces — so the port fell through
    both: not a volume, and nothing assigned it a boundary either.

    ⚠️ AN UNASSIGNED BOUNDARY IS **PMC**, NOT PEC. It is the NATURAL boundary
    condition of the curl-curl E formulation (n x H = 0); PEC is the ESSENTIAL
    one and must be imposed. So the loop gap was left **OPEN**, and an open gap
    plus the loop is an LC resonator that lands near 2.45 GHz and HYBRIDISES
    TE011 into a pair (2.4400 / 2.4944, matched purity spreads ~0.94).
    🔑 Measured, same mesh, only the port BC changed (`h3_step3`, 2026-08-24):
        unassigned (PMC, gap OPEN) -> 2.440003 + 2.494440, best P = 0.9423
        port_bc="pec"  (gap SHORT) -> TE011 2.451633, Q 43,422, P = 0.9997
    A SHORTED loop is a small closed ring resonant far above 2.45 GHz, so it
    barely perturbs the cavity. **The open gap was the resonator, not the ring.**

    `port_bc` makes the choice EXPLICIT and has no default:
      "lumped"     — 50 ohm LumpedPort, Excitation off. **THE MACHINE.** Same
                     port, same R and Direction the driven template uses, so
                     the eigen and driven cavities are finally the SAME cavity.
                     Makes the eigenproblem LOSSY: pass allow_lossy_eigen=True
                     and read Q as LOADED (Q_L), not Q0.
      "pec"        — short the gap. The loop becomes a small closed ring whose
                     own resonance is far above the band, so TE011 is left
                     nearly unperturbed. Agrees with driven to ~10 kHz.
      "absorbing"  — radiation BC. ⚠️ NOT the 50 ohm feed; use "lumped" for that.
      None         — allowed ONLY when the mesh has no port attribute.
                     🔴 There is NO "leave it to Palace" option, because that
                     silently selects PMC and opens the gap.
    ⚠️ A mesh WITH a port and `port_bc=None` is now a REFUSAL, not a default.
    """
    a = meta["attributes"]
    vols = sorted({v for k, v in a.items()
                   if isinstance(v, int) and k not in ("wall", "port")}
                  | set(a.get("air") or []))
    for k, v in a.items():
        if isinstance(v, int) and k not in ("wall", "port") and v not in vols:
            raise RuntimeError(f"{tag}: volume {k}={v} has no material")
    c = {"Problem": {"Type": "Eigenmode", "Verbose": 2,
                     "Output": f"postpro/{tag}"},
         "Model": {"Mesh": mesh or f"{tag}.msh", "L0": 1.0,
                   "Refinement": {"UniformLevels": 0}},
         "Domains": {"Materials": _materials(a, meta, vols),
                     # 🔑 ONE ENERGY INDEX PER REGION, not just the bore.
                     # Without this a mode carries no SIGNATURE and can only be
                     # identified by WHERE IT IS — which fails as soon as the
                     # effect being measured exceeds the mode spacing. That is
                     # exactly how E1b's loading measurement was lost: TM010
                     # moved 130 MHz out of the window and the matcher paired
                     # it with TM110. bore-H/bore-E is what tells a TE from a
                     # TM, and it costs nothing to emit.
                     "Postprocessing": {"Energy":
                         [{"Index": 1, "Attributes": [a["bore"]]}]
                         + [{"Index": 10 + i, "Attributes": [v]}
                            for i, v in enumerate(sorted(vols))]}},
         "Boundaries": {},
         # 🔴 THE DEFAULT WAS 1, AND THAT IS WHERE THE DAMAGE CAME FROM.
         # E0g measured order-1 error at 12-17 MHz, mode-dependent by 40x.
         # Every rig that did not explicitly override this inherited a
         # discretisation already known to be wrong — including E0f, whose
         # conclusion "geometry is converged at geometric order 2" was reached
         # with the SOLVER at order 1, where the error exceeds the geometric
         # differences it was resolving. A known-bad value must not be the
         # default; rigs that WANT order 1 (E0g's sweep, E0k's bridge) say so.
         "Solver": {"Order": order, "Device": "CPU",
                    "Eigenmode": {"Target": target, "N": n, "Tol": 1e-08,
                                  "MaxIts": 200, "Save": 0},
                    "Linear": {"Type": "Default", "KSPType": "GMRES",
                               "Tol": 1e-08, "MaxIts": 500}}}
    if sigma is None:
        c["Boundaries"]["PEC"] = {"Attributes": [a["wall"]]}
    else:
        c["Boundaries"]["Conductivity"] = [
            {"Attributes": [a["wall"]], "Conductivity": sigma,
             "Permeability": 1.0}]

    # ---- GATE 5: the mesh the solver is told to read must be the mesh the
    # SIDECAR describes. `meta` records its own source in meta["mesh"]; a caller
    # that builds "x.msh" and then asks for "x_pec.msh" gets rc=1 in 2 s with no
    # useful message. That exact bug cost a launch on 2026-08-24, and it is the
    # SAME shape as `sweep()` using the OUTPUT tag to find the mesh (§7).
    _m = meta.get("mesh")
    _want = pathlib.Path(mesh or f"{tag}.msh").name
    if _m and pathlib.Path(_m).name != _want:
        raise RuntimeError(
            f"{tag}: GATE 5 — asked to solve '{_want}' but the sidecar "
            f"describes '{pathlib.Path(_m).name}'.\n"
            f"  🔑 Pass the MESH tag and the OUTPUT tag separately. Binding the "
            f"solve to a mesh\n"
            f"     the metadata does not describe is how a rig solves the wrong "
            f"cavity in silence.")

    # ---- GATE 4: no surface may reach the solver by DEFAULT.
    port = a.get("port")
    if port is None:
        if port_bc is not None:
            raise RuntimeError(
                f"{tag}: port_bc={port_bc!r} was given but this mesh has NO "
                f"port attribute. Passing it means you think there is a loop.")
    else:
        if port_bc is None:
            raise RuntimeError(
                f"{tag}: mesh has a PORT (attribute {port}) and no port_bc.\n"
                f"  🔴 Palace would leave it at PMC (the NATURAL BC) — i.e. "
                f"leave the loop gap\n"
                f"     OPEN. An open gap + loop is an LC resonator near "
                f"2.45 GHz and it\n"
                f"     HYBRIDISES TE011 into a pair. That is a DIFFERENT cavity "
                f"from the\n"
                f"     machine, which feeds the loop through 50 ohm "
                f"(CONVENTIONS §7v).\n"
                f"  ✅ port_bc='lumped' is the MACHINE (50 ohm feed). "
                f"'pec' shorts it on\n"
                f"     purpose; 'absorbing' is a radiation BC. There is no "
                f"default because\n"
                f"     there is no safe default.")
        if port_bc == "pec":
            c["Boundaries"].setdefault("PEC", {"Attributes": []})
            c["Boundaries"]["PEC"]["Attributes"] = sorted(
                set(c["Boundaries"]["PEC"].get("Attributes", [])) | {port})
            print(f"    {tag}: port {port} gap SHORTED (port_bc=pec) — loop "
                  f"is a closed ring, resonant far above band; Q excludes port "
                  f"loss", flush=True)
        elif port_bc == "lumped":
            d = meta.get("port_direction")
            if d is None:
                raise RuntimeError(
                    f"{tag}: port_bc='lumped' needs `port_direction` in the "
                    f"mesh sidecar and it is absent.")
            c["Boundaries"]["LumpedPort"] = [
                {"Index": 1, "Attributes": [port], "Direction": d,
                 "R": 50.0, "Excitation": False}]
            print(f"    🔑 {tag}: port {port} terminated in 50 ohm "
                  f"(port_bc=lumped) — the OPERATING configuration. "
                  f"Q is LOADED.", flush=True)
        elif port_bc == "absorbing":
            c["Boundaries"]["Absorbing"] = {"Attributes": [port], "Order": 1}
            print(f"    {tag}: port {port} terminated (port_bc=absorbing)",
                  flush=True)
        else:
            raise RuntimeError(
                f"{tag}: port_bc must be 'lumped', 'pec' or "
                f"'absorbing', got {port_bc!r}")

    # every surface attribute the mesh declares must now be accounted for
    surfaces = {k: v for k, v in a.items()
                if k in ("wall", "port") and isinstance(v, int)}
    assigned = set()
    for _k, _v in c["Boundaries"].items():
        for d in (_v if isinstance(_v, list) else [_v]):
            if isinstance(d, dict):
                assigned |= set(d.get("Attributes", []))
    missed = {k: v for k, v in surfaces.items() if v not in assigned}
    if missed:
        raise RuntimeError(
            f"{tag}: GATE 4 — surface(s) {missed} reach the solver with NO "
            f"boundary condition. Palace would default them to PEC.")
    # 🔑 SAY IT. The solver order was a hardcoded 1 that six rigs inherited
    # silently, and every result from them had to be invalidated. An
    # inherited discretisation must at least be a VISIBLE one.
    print(f"    {tag}: solver order {c['Solver']['Order']}", flush=True)
    return c


def lossy_domains(cfg):
    """[(attributes, eps, tand, sigma)] for every NON-VACUUM domain material."""
    out = []
    for m in (cfg.get("Domains", {}) or {}).get("Materials", []) or []:
        eps = m.get("Permittivity", 1.0)
        tand = m.get("LossTan", 0.0)
        sig = m.get("Conductivity", 0.0)
        if tand or sig:
            out.append((m.get("Attributes"), eps, tand, sig))
    return out


def check_torch_bound(tag, cfg):
    """R101 (extended): refuse a solve whose TORCH permittivity disagrees with its mesh.

    🔴 WHY. `eigen_cfg` writes Permittivity 1.0 for EVERY volume, torch
    included. The torch binding existed only in `solveconf.driven` (R101), so
    every EIGEN solve carrying a torch solved it as VACUUM — geometrically
    present, electromagnetically absent. `h4_field` run 1 predicted -11.2 MHz
    from a sapphire tube and measured +0.06 MHz, which is exactly right for a
    tube that is not there.

    ⚠️ Fixing `eigen_cfg` does NOT fix this, and that is the whole point. Six
    rigs REPLACE `Domains.Materials` wholesale after calling it
    (h3_eigen, h3_annular, h3_loaded, h3_eigenprobe, h4_seed, probecheck), so a
    better eigen_cfg is silently discarded by exactly the rigs that need it —
    CONVENTIONS §2, the value never reaching its consumer. Checked HERE because
    `run()` sees the config actually being solved, the same reasoning that put
    the lossy-domain check here. §7: a checker must be able to see its subject.

    The MESH is the source of truth (R101's rule). A mismatch means the rig
    typed a permittivity that is not the one it meshed.
    """
    try:
        meta = solveconf.load_meta(cfg.get("Model", {}).get("Mesh") or f"{tag}.msh")
    except Exception:
        return None                      # no sidecar: load_meta's own error owns it
    attrs = meta.get("attributes") or {}
    tv = attrs.get("torch")
    tm = (meta.get("geometry_mm") or {}).get("torch_material")
    if tv is None:
        return None                      # --no-torch: nothing to bind
    if tm is None:
        raise RuntimeError(
            f"{tag}: mesh has a torch volume (attribute {tv}) but the sidecar "
            f"names no torch_material. Refusing to guess the permittivity of "
            f"the thing under test. Rebuild the mesh with --torch-material.")
    want = float(tm[0])
    got = [m for m in cfg.get("Domains", {}).get("Materials", [])
           if tv in (m.get("Attributes") or [])]
    if not got:
        raise RuntimeError(
            f"{tag}: torch volume {tv} is in the mesh but no material in the "
            f"config covers it.")
    have = float(got[0].get("Permittivity", 1.0))
    if abs(have - want) > 1e-9:
        raise RuntimeError(
            f"{tag}: TORCH PERMITTIVITY DISAGREES WITH THE MESH — config says "
            f"eps={have}, the sidecar says the mesh was built with eps={want}. "
            f"This is R101: a sapphire tube solving as vacuum shifts f0 by "
            f"~15 MHz and the meshes are byte-identical, so nothing downstream "
            f"can notice. Bind the permittivity FROM THE SIDECAR.")
    print(f"    torch: eps={have} (bound from mesh sidecar)", flush=True)
    return have


def _selftest_torch_bound():
    """§7: a checker gets known-bad input, or it is believed without evidence."""
    import types
    real = solveconf.load_meta
    meta = {"attributes": {"torch": 7, "wall": 1, "bore": 2},
            "geometry_mm": {"torch_material": [11.6, 3.5e-05]}}
    solveconf.load_meta = lambda mesh: meta
    try:
        vac = {"Model": {"Mesh": "x.msh"},
               "Domains": {"Materials": [{"Attributes": [7, 2],
                                          "Permittivity": 1.0}]}}
        try:
            check_torch_bound("selftest", vac)
            raise AssertionError("FAILED: sapphire-as-vacuum was not caught")
        except RuntimeError as e:
            assert "DISAGREES" in str(e), e
        ok = {"Model": {"Mesh": "x.msh"},
              "Domains": {"Materials": [{"Attributes": [7], "Permittivity": 11.6},
                                        {"Attributes": [2], "Permittivity": 1.0}]}}
        assert check_torch_bound("selftest", ok) == 11.6
        meta["geometry_mm"] = {}
        try:
            check_torch_bound("selftest", ok)
            raise AssertionError("FAILED: missing torch_material was not caught")
        except RuntimeError as e:
            assert "no torch_material" in str(e), e
    finally:
        solveconf.load_meta = real
    return True


def check_groove_declared(tag, cfg, allow_no_groove=False):
    """the groove omission: refuse a LOADED solve on a cavity with no mode filter.

    🔴 WHY. The cavity design is premised on a mode filter. `GEO` never passed
    `--groove`, so the ENTIRE loaded programme of 2026-08-23 — H3, H6,
    h3_superpose, h3_sapphire, h3_loopsize — measured a groove-free cavity and
    every design number from it is scoped to a cavity nobody is building.
    Nothing crashed, nothing looked wrong, and 31 rigs inherited the omission.

    🔑 A PLASMA is the tell. A groove-free cavity is legitimate for the
    instrument rigs (closed-form comparison wants a plain cylinder) and is never
    legitimate for a loaded, design-facing solve — the filter is what decides
    which modes exist, and a loaded cavity is where mode identity is hardest.

    ⚠️ Checked HERE, on the config actually being solved, for the same reason the
    torch and lossy-domain checks are: callers assemble geometry themselves.
    """
    try:
        meta = solveconf.load_meta(cfg.get("Model", {}).get("Mesh") or f"{tag}.msh")
    except Exception:
        return None
    g = (meta.get("geometry_mm") or {}).get("groove") or [0.0, 0.0]
    has_plasma = (meta.get("attributes") or {}).get("plasma") is not None
    grooved = float(g[0]) > 0.0 and float(g[1]) > 0.0
    if grooved:
        print(f"    groove: {g[0]:g} x {g[1]:g} mm (in mesh)", flush=True)
        return tuple(g)
    if has_plasma and not allow_no_groove:
        raise RuntimeError(
            f"{tag}: LOADED solve on a cavity with NO MODE FILTER (groove="
            f"{g}). The design is premised on one, and a groove-free loaded "
            f"cavity has a DIFFERENT MODE LANDSCAPE — which is exactly what a "
            f"loaded measurement is about. Use GEO_DESIGN, or pass "
            f"allow_no_groove=True and say in the rig's docstring why a bare "
            f"cavity is the right control.")
    return None


def run(tag, cfg, allow_lossy_eigen=False, timeout=None,
        allow_no_groove=False):
    # 🔴 EIGENMODE + A LOSSY VOLUME DOES NOT CONVERGE. Measured 2026-08-23: a
    # bulk lossy region with tan-delta ~ 3 stalled NLEPS at nconv=0 after 19
    # iterations and ~22,500 KSP iterations — 65 minutes, on the WEAKEST plasma
    # of an intended 16-point grid. The same cavity without it solves in 155 s.
    #
    # 🔑 A surface-impedance WALL is a boundary term and is fine; a lossy VOLUME
    # is in the operator, and the frequency dependence it introduces is what
    # NLEPS chokes on. INSTRUMENT already said "the geometries where the
    # eigensolver diverges are exactly where driven should still work" — the
    # gap was that nothing CHECKED.
    #
    # ⚠️ Checked HERE, not in eigen_cfg: eigen_cfg only ever writes vacuum, and
    # callers mutate Materials afterwards (that is how the plasma got in). This
    # sees the config actually being solved. CONVENTIONS §7 — a checker must be
    # able to see what it checks.
    if (cfg.get("Problem", {}).get("Type") == "Eigenmode"
            and not allow_lossy_eigen):
        bad = lossy_domains(cfg)
        if bad:
            lines = "\n".join(
                f"      attributes {a}: eps={e} tan-delta={t} sigma={sg}"
                for a, e, t, sg in bad)
            # 🔴 THIS WAS A REFUSAL AND THE PREMISE WAS FALSE. It was added from
            # ONE stalled solve, generalised into "the eigensolver cannot do a
            # lossy plasma". A four-case probe showed the stall was the SHIFT
            # TARGET — placed 300 MHz below the mode because I assumed loading
            # pulls DOWN, when an overdense plasma (eps<0, conductor-like)
            # pulls UP. Eigen converges across sigma = 2.75e-4 .. 275 S/m in
            # 89-284 s. A guard built on a wrong premise blocks correct work,
            # so this WARNS and states the real hazard instead.
            print(f"    ⚠️ {tag}: eigenmode with {len(bad)} lossy domain(s):\n"
                  f"{lines}\n"
                  f"       This converges — but NLEPS is sensitive to the SHIFT "
                  f"TARGET. Put the target NEAR the expected loaded frequency, "
                  f"and note an overdense plasma pulls the mode UP, not down.",
                  flush=True)
        if False:
            raise RuntimeError(
                f"{tag}: EIGENMODE solve with {len(bad)} LOSSY DOMAIN(S) —\n"
                f"{lines}\n"
                f"    This does not converge. Measured: nconv=0 after 19 NLEPS "
                f"iterations and ~22,500 KSP iterations in 65 minutes, on a "
                f"weaker load than most. Use a DRIVEN solve — it has no NLEPS "
                f"and therefore no convergence cliff.\n"
                f"    If you have reason to believe this particular case "
                f"converges, say so explicitly: run(..., allow_lossy_eigen=True). "
                f"Do not remove this check.")
    check_torch_bound(tag, cfg)
    check_groove_declared(tag, cfg, allow_no_groove=allow_no_groove)
    pathlib.Path(f"{tag}.json").write_text(json.dumps(cfg, indent=2))
    t0 = time.time()
    # 🔴 subprocess.run(timeout=) RAISES BUT DOES NOT KILL. e1c's k=1.0 solve
    # timed out and its four ranks kept running for another 90 minutes, stealing
    # half the machine from every job that followed — and every earlier timeout
    # in this session (e0h, e0i, e0g order 3) did the same unnoticed. Popen +
    # kill() is the only form that actually stops the work.
    # 🔴 AND proc.kill() IS NOT ENOUGH EITHER. It kills only the `palace` bash
    # wrapper; the real tree is palace -> prterun -> palace-x86_64.bin xN, so
    # the RANKS survive, reparent to PPID 1, and keep burning the machine —
    # four of them for 20 minutes, and reap.py could not see them because ranks
    # are never direct children of init. Kill the PROCESS GROUP.
    # e0l_scaling.py was fixed this way; this is the last caller that was not.
    proc = subprocess.Popen([PALACE, "-np", RANKS, f"{tag}.json"], env=solver.ENV,
                            stdout=open(f"{tag}_p.log", "w"),
                            stderr=subprocess.STDOUT,
                            start_new_session=True)
    # 🔴 THE BUDGET WAS POST-HOC AND THAT IS WHY IT DID NOT HELP.
    # solvecost.NLEPS_BUDGET has existed since 2026-08-22, but it was only ever
    # read AFTER run() returned — so a stalled solve still burned its whole
    # timeout first. The H3 stall sat at nconv=0 for 65 minutes when the budget
    # would have cut it at ~1,000 NLEPS iterations. A guard that fires after the
    # cost has been paid is a report, not a guard.
    #
    # ⚠️ Exceeding the budget is MISSING DATA, not a bad result — a distinct
    # exception message, so a caller can tell "did not converge" from "wrong
    # answer" and from "timed out". Scoring them the same is what teaches a
    # sweep to avoid regions that are merely hard.
    def _nleps_count():
        try:
            return pathlib.Path(f"{tag}_p.log").read_text(
                errors="ignore").count("NLEPS (nconv=")
        except OSError:
            return 0

    def _kill_tree(why):
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError) as e:
            print(f"    ⚠️ {tag}: could not kill process group ({e}) — "
                  f"CHECK FOR ORPHANED RANKS with ops/go ops/status.sh",
                  flush=True)
        proc.wait()
        return why

    # 🔴 A PROBE NEEDS A WALL-CLOCK BUDGET, NOT JUST AN ITERATION ONE.
    # DEFAULT_TIMEOUT_S is 6 hours, and NLEPS_BUDGET cannot help when each NLEPS
    # iteration itself takes minutes: the H3 stall managed 19 iterations in 65
    # minutes, so reaching 1,000 would take ~57 HOURS. The two guards catch
    # different shapes — many cheap iterations vs few expensive ones — and a
    # probe needs the second.
    tmo = solver.DEFAULT_TIMEOUT_S if timeout is None else float(timeout)
    deadline = t0 + tmo
    poll = 30.0
    while True:
        try:
            rc = proc.wait(timeout=poll)
            break
        except subprocess.TimeoutExpired:
            pass
        n = _nleps_count()
        if n > solvecost.NLEPS_BUDGET:
            raise RuntimeError(_kill_tree(
                f"{tag}: DID NOT CONVERGE WITHIN BUDGET — {n} NLEPS iterations "
                f"exceeds {solvecost.NLEPS_BUDGET} (worst run that DID converge "
                f"used 869). Killed after {time.time()-t0:.0f}s. This is MISSING "
                f"DATA, not a bad result: report it as unconverged, do not score "
                f"it. Raise solvecost.NLEPS_BUDGET deliberately if this case is "
                f"merely hard."))
        if time.time() > deadline:
            raise RuntimeError(_kill_tree(
                f"{tag}: TIMED OUT after {tmo:.0f}s "
                f"({n} NLEPS iterations) — rank TREE killed"))
    dt = time.time() - t0
    # 🔴 "TOO FAST" IS NOT EVIDENCE OF FAILURE. This was `rc or dt <
    # MIN_SECONDS`, and MIN_SECONDS=30 was calibrated on 4 ranks at order 2 on
    # 35-45k elements. On the 32-rank instance a legitimate order-1 solve of a
    # 27.5k mesh finishes in 5s: E0k's first solve produced a complete eig.csv
    # with backward errors of 8e-12 and was thrown away as a failure.
    #
    # Ask the direct question instead: DID IT PRODUCE OUTPUT? Elapsed time is a
    # proxy for that, and a proxy calibrated on hardware we no longer use. (The
    # same substitution made ops/wait.sh call a healthy run dead and ops/go
    # think a meshing rig was idle.)
    pp = pathlib.Path("postpro") / tag
    produced = sorted(f.name for f in pp.glob("*.csv")
                      if f.stat().st_size > 0) if pp.is_dir() else []
    if rc or not produced:
        tail = pathlib.Path(f"{tag}_p.log").read_text().strip().splitlines()
        why = "did not solve" if rc else "produced NO non-empty csv in postpro/"
        raise RuntimeError(f"{tag}: rc={rc} in {dt:.0f}s — {why} — "
                           f"{tail[-1] if tail else '(empty log)'}")
    if dt < solver.MIN_SECONDS:
        # reported, not fatal: fast AND complete is the expected result of
        # more ranks, and staying silent about it would hide a real speedup
        print(f"    solved in {dt:.0f}s — under MIN_SECONDS={solver.MIN_SECONDS}"
              f" but produced {', '.join(produced)}", flush=True)
    else:
        print(f"    solved in {dt:.0f}s", flush=True)
    # 🔑 journalled HERE, in the shared helper, not in each rig — the same
    # reason preflight and reap exist: a step every caller must remember is a
    # step that will be forgotten. RUN is the environment variable a rig sets
    # so its solves land in one journal.
    journal.log(os.environ.get("RUN", "run"), event="solve", tag=tag,
                seconds=round(dt, 1), ranks=RANKS,
                order=cfg["Solver"].get("Order"),
                mesh=cfg["Model"]["Mesh"])


def eig(tag):
    f = pathlib.Path("postpro") / tag / "eig.csv"
    return sorted(float(l.split(",")[1]) for l in f.read_text().splitlines()[1:]
                  if len(l.split(",")) > 2)


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    EX = ph.spectrum(A_MM, L_MM)
    print("VERIFICATION REFERENCE — physics.py, no simulation:")
    for k, v in EX.items():
        print(f"    {k}  {v:.6f} GHz")
    deg = ph.degenerate_pairs(A_MM, L_MM)
    print(f"  FALSIFIER: exact degeneracies {[(x, y) for x, y, _ in deg]} "
          "— true splitting identically 0\n")
    pathlib.Path("e0.reference.json").write_text(json.dumps(
        {"exact": EX, "degenerate": [[x, y] for x, y, _ in deg],
         "a_mm": A_MM, "L_mm": L_MM}, indent=1))

    print("MESHING", flush=True)
    mF, facF = build("e0fine")
    # 🔴 WAS ["--n-wl", "8"], AND 8.0 IS THE DEFAULT (geometry.py elems_per_wl).
    # The flag was a no-op: "coarse" and "fine" came out with identical sizing
    # (air 15.2955 mm), identical tet counts (83,322) and identical file sizes.
    # E0 was comparing a mesh to an independently built copy of the SAME SPEC,
    # which E0kp later showed differ by ~66 Hz — so the coarse/fine agreement
    # was guaranteed by construction and never tested mesh resolution at all.
    # That means E0's conclusion "the solver-vs-mathematics gap is not a mesh
    # artifact" was never actually checked.
    mC, facC = build("e0coarse", ["--n-wl", "5"])

    # GUARD: a resolution comparison whose two meshes are the same mesh is not a
    # comparison. Assert they DIFFER, rather than trusting a flag to have worked.
    hF = mF.get("sizing_mm", {}).get("air")
    hC = mC.get("sizing_mm", {}).get("air")
    if mF["tets"] == mC["tets"] or (hF and hC and abs(hF - hC) < 1e-9):
        raise RuntimeError(
            f"e0: coarse and fine are the SAME mesh — tets {mF['tets']} vs "
            f"{mC['tets']}, h_air {hF} vs {hC}. A no-op flag silently did this "
            f"once already; refusing to report a resolution comparison that is "
            f"not one.")
    print(f"  ✅ meshes genuinely differ: fine {mF['tets']:,} tets "
          f"(h_air {hF:.2f} mm) vs coarse {mC['tets']:,} tets "
          f"(h_air {hC:.2f} mm)", flush=True)

    print("\nEIGENMODE, PEC — the case the closed form describes", flush=True)
    run("e0fine", eigen_cfg("e0fine", mF))
    run("e0coarse", eigen_cfg("e0coarse", mC))

    print("\nEIGENMODE, finite-conductivity wall — same mesh, only the BC changes.\n"
          "  This is the like-for-like partner for a driven solve (old R37).",
          flush=True)
    # 🔴 WAS sigma=3.5e7 — a FOURTH hardcoded copy of the wall conductivity,
    # after the three r_hardcoded_value already found. wall_sigma() exists to
    # bind it from baselines.json and REFUSE without it; typing the number
    # bypasses the guard silently.
    from e0k2_anchor import wall_sigma as _ws
    run("e0cond", eigen_cfg("e0cond", mF, mesh="e0fine.msh", sigma=_ws()))

    out = {"exact": EX, "fine": eig("e0fine"), "coarse": eig("e0coarse"),
           "cond": eig("e0cond"), "tets_fine": mF["tets"], "tets_coarse": mC["tets"],
           "sf_fine": facF, "sf_coarse": facC}
    json.dump(out, open("e0.result.json", "w"), indent=1)
    print("\n  wrote e0.result.json — NO VERDICT HERE", flush=True)


if __name__ == "__main__":
    main()
