#!/usr/bin/env python3
"""Run one Palace case. ONE implementation, so its failure modes happen once.

R50. Eighteen drivers here carry a near-identical `def solve`, and each copy had
to independently get right things that were only learned by getting them wrong:

  ENV        `palace` shells out to `mpiexec`, which is not on a bare login PATH.
             Without it: rc=1 in 0 s, "Could not locate MPI launcher" — and a
             driver that reports "no peaks" makes a solver that never ran look
             exactly like a cavity with no resonance. Cost one full sweep.
  0-s guard  Any solve returning in under ~30 s did not solve. Report it as a
             failure and print the log's last line, never as an empty result.
  progress   A 4-case sweep is 2-3 h. Emitting per solve is what lets a problem
             surface in minutes instead of at the end.
  config     Derived from the mesh's sidecar (solveconf), never hand-assembled.

Nothing here is new physics. It is the accumulated cost of the night, in one
place, so the nineteenth driver does not pay it again.
"""
import os
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import meshcheck
import modes
import solveconf

# E1e: PATHS COME FROM THE ENVIRONMENT. These were hardcoded to this laptop's
# layout (~/.local/opt/palace, ~/.local/share/mamba), which is wrong on any
# other machine — on EC2 the toolchain lives at /opt/amip so every solve would
# have failed with a confusing "returned in 0 s" rather than "not found".
# `bootstrap.sh` writes /opt/amip/env.sh which sets these; the defaults keep
# this laptop working unchanged.
PALACE = os.environ.get(
    "PALACE_BIN", str(pathlib.Path.home() / ".local/opt/palace/bin/palace"))
CONDA_ENV = os.environ.get(
    "CONDA_ENV", str(pathlib.Path.home() / ".local/share/mamba/envs/emsim"))
MAMBA_ROOT = os.environ.get(
    "MAMBA_ROOT_PREFIX", str(pathlib.Path.home() / ".local/share/mamba"))
HOME = pathlib.Path.home()
ENV = {**os.environ,
       "PATH": f"{CONDA_ENV}/bin:{os.environ['PATH']}",
       "MAMBA_ROOT_PREFIX": MAMBA_ROOT}
MIN_SECONDS = 30
# Every solve carries a CEILING as well as a floor. A wave-port case ran 4 ranks
# at 99.9% CPU for 50 minutes on 37k unknowns without converging, and an earlier
# one burned 3h51m on a band 1,227 linewidths wide. Neither was detected until
# someone looked. Rule of thumb from the user: bound at ~3x what you expect, so a
# hang self-terminates instead of being discovered hours later.
# E1d: raised from 3600. 🔴 One hour was an arbitrary config value that I then
# quoted as a "hard practical ceiling" on mesh size. It is neither hard nor
# physical — and every timing behind that claim was measured while ORPHANED
# ranks from a previous timeout were still running, on 8 cores with every job
# pinned to -np 4. Nothing about 92k elements is out of reach.
DEFAULT_TIMEOUT_S = 21600


class SolveFailed(RuntimeError):
    pass


def solve(mesh, tag, band, ranks=4, strict=True, timeout_s=DEFAULT_TIMEOUT_S,
          **cfg):
    """Solve `mesh` as `tag` over `band`. Returns modes.peaks(tag).

    strict=True raises on failure rather than returning an empty list, because
    an empty list is indistinguishable from a physical null and that ambiguity
    has produced two wrong verdicts here.
    """
    meta = solveconf.write(mesh, tag, band, **cfg)
    t0 = time.time()
    # 🔴 E1d: this used subprocess.run(timeout=…), which RAISES BUT DOES NOT
    # KILL — and the message below claimed "was killed", which was never true.
    # Four runs in one session leaked four ranks each; one ran 90 minutes past
    # its timeout and twelve concurrent processes thrashed the machine. Popen +
    # kill() is the only form that stops the work. `reap.py` cleans up leaks
    # from any OTHER cause (never `pkill -f`: it matches the harness wrapper's
    # argv and kills the calling shell — observed three times here).
    proc = subprocess.Popen([PALACE, "-np", str(ranks), f"{tag}.json"], env=ENV,
                            stdout=open(f"{tag}_p.log", "w"),
                            stderr=subprocess.STDOUT)
    try:
        rc = proc.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        dt = time.time() - t0
        msg = (f"{tag}: exceeded {timeout_s}s; ranks KILLED. Not a slow solve — "
               f"a non-converging one. Check the tail of {tag}_p.log: a frozen "
               f"log with ranks at 100% CPU means the linear solve is not "
               f"converging, not that it needs longer.")
        print(f"  🔴 {msg}", flush=True)
        if strict:
            raise SolveFailed(msg)
        return []
    dt = time.time() - t0

    if rc != 0 or dt < MIN_SECONDS:
        tail = pathlib.Path(f"{tag}_p.log").read_text().strip().splitlines()
        why = tail[-1] if tail else "(empty log)"
        msg = (f"{tag}: rc={rc} in {dt:.0f}s — "
               + ("did not solve" if rc else f"returned in under {MIN_SECONDS}s")
               + f". Last log line: {why}")
        print(f"  🔴 {msg}", flush=True)
        if strict:
            raise SolveFailed(msg)
        return []

    ms = modes.peaks(tag)
    print(f"  ✅ {tag}: {dt:.0f}s, {len(ms)} resonance(s)"
          f"  [{meta['tets']:,} tets, size-factor {meta['size_factor']}]",
          flush=True)
    return ms


def sweep(cases, band, **kw):
    """cases: [(mesh, tag)]. Runs each, reporting as it goes.

    ⚠️ Meshes must already share a size-factor — build them through
    meshsweep.sweep(), which is what guarantees comparability (R27). This
    function checks and refuses otherwise rather than differencing a
    mixed-density set.
    """
    # Postconditions BEFORE any solve: a shared size-factor, no silently
    # clamped refinements, and sizing changes that actually changed the mesh.
    # Two no-ops produced confident verdicts here before this existed.
    meshcheck.check([pathlib.Path(m).stem for m, _t in cases])
    return {tag: solve(mesh, tag, band, **kw) for mesh, tag in cases}
