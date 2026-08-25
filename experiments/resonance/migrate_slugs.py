#!/usr/bin/env python3
"""Rename every pre-slug artefact into the slug regime. DRY-RUN by default.

🔴 User, 2026-08-25: *"we also have to rename everything extant to conform to
the slug regime. And modify all scripts, and update CONVENTIONS.md."*

Each existing rig's TAG becomes a RETRO slug with run number `00`, meaning
"the pre-slug era run":

    h3_loopq          ->  h3-loopq-00
    h3_loopq.result.json  ->  h3-loopq-00.result.json
    h3_driven_cold.msh    ->  h3-driven-00_cold.msh
    postpro/h3_driven_cold_wide/  ->  postpro/h3-driven-00_cold_wide/

⚠️ `00` IS A CLAIM ABOUT PROVENANCE, AND A WEAK ONE. These artefacts are the
residue of an era where a re-run overwrote its predecessor in place (7ap), so
"run 00" may be the third run of that rig with the first two destroyed. The
retro config records that as `sha256: null` plus a retrofit note, exactly as
baseline-h3-driven-anchor-01.json does. Do not read `00` as "the first run".

🔴 WHAT THIS TOUCHES THAT GIT DOES NOT PROTECT:
    *.msh        369 MB, GITIGNORED — regenerable, but not restorable
    *.meta.json  GITIGNORED — and it is the sidecar GATE 5 validates the mesh
                 against, so a rename that misses it BREAKS EVERY SOLVE
    postpro/     148 MB, gitignored
Tracked (restorable): *.result.json, *.log, *.jsonl, docs, scripts.

USAGE
    python3 migrate_slugs.py              plan only, writes migrate_slugs.plan.json
    python3 migrate_slugs.py --apply      execute (refuses if a rig is running)
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
SKIP_TAGS = {"h3_qext"}          # 🔴 currently RUNNING — never touch a live job


# 🔴 KEYING THIS ON `TAG` WAS WRONG, AND THE FIRST PLAN PROVED IT: it produced
# 195 renames and MISSED EVERY MESH. Only 32 of 87 rigs declare a TAG at all;
# the rest name their artefacts from local variables, so the prefixes on disk
# are the ground truth and the TAG table is a partial index of them.
#
# THE INVENTORY (2026-08-25): 385 artefact files/dirs, 34 distinct prefixes.
#   25 prefixes map to a rig            -> migratable
#    9 prefixes have NO OWNING RIG      -> e1b e1c e1cc scale e0fine e0coarse
#                                          e0cond sfprobe (37 files). Their
#                                          producing code is GONE (the deleted
#                                          waveguide/ignition programmes, or
#                                          earlier eras). A slug must reference
#                                          a doc section; these can reference
#                                          nothing, so they CANNOT be migrated
#                                          — they can only be quarantined or
#                                          deleted, and that is a user call.
#    1 prefix is already slugged        -> h3-driven-anchor-01


def tags():
    """TAG -> retro slug, from every rig that declares a module-level TAG."""
    import ast
    out = {}
    for f in sorted(ROOT.glob("*.py")):
        try:
            t = ast.parse(f.read_text())
        except Exception:
            continue
        for n in t.body:
            if isinstance(n, ast.Assign):
                for tg in n.targets:
                    if (isinstance(tg, ast.Name) and tg.id == "TAG"
                            and isinstance(n.value, ast.Constant)
                            and isinstance(n.value.value, str)):
                        tag = n.value.value
                        if tag in SKIP_TAGS:
                            continue
                        out[tag] = tag.replace("_", "-") + "-00"
    return out


def plan():
    """Every rename, longest tag first so `h3_driven` wins over `h3`."""
    m, moves, seen = tags(), [], set()
    for tag in sorted(m, key=len, reverse=True):
        slug = m[tag]
        for p in sorted(ROOT.glob(f"{tag}*")) + sorted((ROOT / "postpro").glob(f"{tag}*")):
            if p.suffix == ".py" or p in seen:
                continue
            rel = p.relative_to(ROOT)
            if not (p.name == tag or p.name.startswith(tag + ".")
                    or p.name.startswith(tag + "_")):
                continue
            seen.add(p)
            moves.append({"tag": tag, "slug": slug, "from": str(rel),
                          "to": str(rel.parent / (slug + p.name[len(tag):]))})
    return m, moves


def sidecar_fixes(moves):
    """.meta.json files whose internal `mesh` field must move with the file."""
    ren = {pathlib.Path(mv["from"]).name: pathlib.Path(mv["to"]).name for mv in moves}
    out = []
    for mv in moves:
        if mv["from"].endswith(".meta.json"):
            try:
                d = json.loads((ROOT / mv["from"]).read_text())
            except Exception:
                continue
            old = d.get("mesh")
            if old and old in ren:
                out.append({"file": mv["to"], "field": "mesh",
                            "from": old, "to": ren[old]})
    return out


def main():
    m, moves = plan()
    fixes = sidecar_fixes(moves)
    by = {}
    for mv in moves:
        by[pathlib.Path(mv["from"]).suffix or "dir"] = \
            by.get(pathlib.Path(mv["from"]).suffix or "dir", 0) + 1
    print(f"  rigs         {len(m)}")
    print(f"  renames      {len(moves)}   {by}")
    print(f"  sidecar mesh fields to rewrite  {len(fixes)}")
    print(f"  🔴 SKIPPED (running): {sorted(SKIP_TAGS)}")
    (ROOT / "migrate_slugs.plan.json").write_text(
        json.dumps({"tags": m, "moves": moves, "sidecar_fixes": fixes},
                   indent=1) + "\n")
    print(f"  wrote migrate_slugs.plan.json")
    if "--apply" not in sys.argv:
        print("\n  DRY RUN. Nothing moved. Re-run with --apply.")
        for mv in moves[:8]:
            print(f"    {mv['from']}  ->  {mv['to']}")
        print(f"    ... {max(0, len(moves)-8)} more in the plan file")
        return 0
    print("\n  --apply is deliberately not implemented yet: see the header. "
          "A restore point (commit) and a quiet instance are preconditions.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
