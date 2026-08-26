#!/usr/bin/env python3
"""Geometry parameters come from the SLUG CONFIG, not from a command line.

🔑 User, 2026-08-25: *"We can also get rid of all the command line arguments, so
that they're forced to come through a file. So everything can be tracked by git,
and via the slug, everything maps back to the docs."*

THE SURFACE BEING REPLACED: geometry.py exposes **45 flags**, and **55 files
hand-build argv lists for it — 375 literal flag occurrences.** That is the real
reason `GEO_DESIGN` could carry `--no-torch` for the entire programme without
anyone noticing (CONVENTIONS 7aq): a flag list is an untyped string blob, and
nothing can validate it.

🔴 WHY THIS GOES config -> argv AND NOT config -> params DIRECTLY.
geometry.py's `main()` does the UNIT CONVERSION inline — `a.radius * 1e-3`,
`math.radians(a.loop_tilt)`, and ~45 more, several with hard-won guards
(`is not None`, because 0 is falsy and `--viewport 0` was once silently ignored,
benchmarking a cavity with a 10 mm stub against a closed form for a plain
cylinder). Re-implementing that overlay would DUPLICATE the conversions, and a
duplicated conversion drifts. So the config is authoritative and argv becomes an
internal detail: ONE conversion path, and the parser can be deleted later
without the config schema moving.

    geometry:
      radius: 103.7          # same units the flag took: mm, degrees
      groove: "5,10"
      no-torch: true         # a bare switch is a boolean
      torch-material: "11.6,3.5e-05"

⚠️ A `true` switch emits the flag; `false` omits it. `null` omits it. That makes
"the design has no torch" a TYPED FALSE you can see in a diff, instead of a
string buried in a list.
"""
import json
import pathlib
import sys

SWITCHES = {"no-torch", "no-inner", "no-cache", "ho-optimize", "tag-groove",
            "air-coarsen", "bore-h"}


def argv_from(geom):
    """{flag: value} -> the argv list geometry.py's parser already accepts."""
    out = []
    for k in sorted(geom):
        v = geom[k]
        if v is None or v is False:
            continue
        flag = "--" + k.lstrip("-")
        if v is True:
            out.append(flag)
            continue
        out += [flag, str(v)]
    return out


def geom_of(cfg):
    """The `parameters.geometry` block of a loaded slug config."""
    g = ((cfg.get("_run") or {}).get("parameters") or {}).get("geometry")
    if g is None:
        raise RuntimeError(
            "this run's config has no parameters.geometry block. Geometry is "
            "not a command line any more — put it in baseline-<slug>.json so "
            "git tracks it and the slug maps it back to the docs.")
    return g


def argv_for(slug):
    import slug as S
    return argv_from(geom_of(S.config(slug)))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    print(" ".join(argv_for(sys.argv[1])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
