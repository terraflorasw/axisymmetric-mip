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
import journal
import solveconf
import solver

A_MM, L_MM = 103.70, 88.53
GEO = ["--radius", f"{A_MM}", "--length", f"{L_MM}", "--order", "2",
       "--sectors", "1", "--no-torch", "--no-inner", "--mode-filter", "0",
       "--viewport", "0", "--trap", "0,0,0", "--chimney", "0,41",
       "--feed", "0,41"]
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


def eigen_cfg(tag, meta, mesh=None, sigma=None, n=22, target=1.05, order=2):
    """PEC by default — the closed form assumes it. sigma= switches to metal.

    GATE 3: every volume attribute gets vacuum, and we ASSERT none was missed.
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
         "Domains": {"Materials": [{"Attributes": vols, "Permittivity": 1.0,
                                    "Permeability": 1.0}],
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
    # 🔑 SAY IT. The solver order was a hardcoded 1 that six rigs inherited
    # silently, and every result from them had to be invalidated. An
    # inherited discretisation must at least be a VISIBLE one.
    print(f"    {tag}: solver order {c['Solver']['Order']}", flush=True)
    return c


def run(tag, cfg):
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
    try:
        rc = proc.wait(timeout=solver.DEFAULT_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError) as e:
            print(f"    ⚠️ {tag}: could not kill process group ({e}) — "
                  f"CHECK FOR ORPHANED RANKS with ops/go ops/status.sh",
                  flush=True)
        proc.wait()
        raise RuntimeError(f"{tag}: TIMED OUT after "
                           f"{solver.DEFAULT_TIMEOUT_S:.0f}s — rank TREE killed")
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
    run("e0cond", eigen_cfg("e0cond", mF, mesh="e0fine.msh", sigma=3.5e7))

    out = {"exact": EX, "fine": eig("e0fine"), "coarse": eig("e0coarse"),
           "cond": eig("e0cond"), "tets_fine": mF["tets"], "tets_coarse": mC["tets"],
           "sf_fine": facF, "sf_coarse": facC}
    json.dump(out, open("e0.result.json", "w"), indent=1)
    print("\n  wrote e0.result.json — NO VERDICT HERE", flush=True)


if __name__ == "__main__":
    main()
