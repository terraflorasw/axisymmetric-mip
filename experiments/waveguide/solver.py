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

PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
HOME = pathlib.Path.home()
ENV = {**os.environ,
       "PATH": f"{HOME}/.local/share/mamba/envs/emsim/bin:{os.environ['PATH']}",
       "MAMBA_ROOT_PREFIX": str(HOME / ".local/share/mamba")}
MIN_SECONDS = 30
# Every solve carries a CEILING as well as a floor. A wave-port case ran 4 ranks
# at 99.9% CPU for 50 minutes on 37k unknowns without converging, and an earlier
# one burned 3h51m on a band 1,227 linewidths wide. Neither was detected until
# someone looked. Rule of thumb from the user: bound at ~3x what you expect, so a
# hang self-terminates instead of being discovered hours later.
DEFAULT_TIMEOUT_S = 3600


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
    try:
        rc = subprocess.run([PALACE, "-np", str(ranks), f"{tag}.json"], env=ENV,
                            stdout=open(f"{tag}_p.log", "w"),
                            stderr=subprocess.STDOUT,
                            timeout=timeout_s).returncode
    except subprocess.TimeoutExpired:
        dt = time.time() - t0
        msg = (f"{tag}: exceeded {timeout_s}s and was killed. Not a slow solve — "
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
