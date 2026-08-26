#!/usr/bin/env python3
"""Rename pre-slug artefacts into the slug regime. Self-contained; DRY-RUN default.

🔴 User, 2026-08-25: *"we also have to rename everything extant to conform to the
slug regime."*

Each rig's artefacts move to a RETRO slug `<rig-with-hyphens>-00`, meaning "the
pre-slug era run":

    h3_driven_n18p90.msh  ->  h3-driven-00_n18p90.msh
    postpro/h2_d10/       ->  postpro/h2-groove-00_d10/

⚠️ `00` IS A WEAK CLAIM. These are the residue of an era where a re-run
overwrote its predecessor in place (CONVENTIONS 7ap), so "run 00" may be the
third run with the first two destroyed.

🔴 THREE THINGS THIS GOT WRONG BEFORE, ALL CAUGHT BY CHECKS RATHER THAN CARE:
  1. KEYING ON `TAG`. Only 32 of 87 rigs declare one; the first plan produced
     195 renames and MISSED EVERY MESH. Ownership is now found by GREPPING each
     artefact prefix in the rig sources — the prefixes on disk are ground truth.
  2. LOSING THE CASE LABEL. The plain rule `slug + rest` collapsed
     e0fine_p.log / e0coarse_p.log / e0cond_p.log onto one name, because there
     the HEAD is the distinguishing part. Collisions are now detected and the
     head is restored for exactly those.
  3. FORGETTING THE SIDECAR. `.meta.json` carries `mesh`, which GATE 5 compares
     against what a solve is told to read. A rename that misses it BREAKS EVERY
     SOLVE. The field is rewritten and then verified.

⚠️ RUN IT WHEREVER THE ARTEFACTS ARE. The instance holds ~182 meshes; a laptop
checkout holds a subset. It plans from the directory it is in.

    python3 migrate_slugs.py            plan only
    python3 migrate_slugs.py --apply    execute, then verify
"""
import collections
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
PATTERNS = ("*.msh", "*.meta.json", "*.result.json", "*.log", "*.jsonl",
            "*.sweep.json", "*.criteria.json", "*.json")
# 🔴 baselines.json IS THE GLOBAL STORE, not an artefact. It matched "*.json"
# and was planned for renaming — the refusal caught it. Repo fixtures are
# excluded by name, not by pattern luck.
FIXTURES = {"baselines.json", "migrate_slugs.plan.json"}
SKIP = re.compile(r"^(baseline-|orphaned-|migrate_slugs)")
TOOLS = {"migrate_slugs.py", "preflight.py", "hardcoded_audit.py",
         "values.py", "slug.py", "geomcfg.py"}


def sources():
    return {f.name: f.read_text() for f in ROOT.glob("*.py")
            if f.name not in TOOLS}


def artefacts():
    out = []
    for pat in PATTERNS:
        out += [p for p in ROOT.glob(pat)
                if not SKIP.match(p.name) and p.name not in FIXTURES]
    out += [p for p in (ROOT / "postpro").glob("*")
            if p.is_dir() and not SKIP.match(p.name)]
    return sorted(set(out))


def heads(name):
    n = re.sub(r"\.(msh|log|jsonl|json)$", "", name)
    n = re.sub(r"\.(meta|result|sweep|criteria)$", "", n)
    parts = n.split("_")
    # 🔴 LONGEST FIRST. Shortest-first meant that once `h3` resolved, EVERY
    # h3_* artefact from 18 different rigs collapsed onto one slug. The
    # most specific prefix is the one that identifies the producing rig.
    return ["_".join(parts[:i]) for i in range(len(parts), 0, -1)]


AMBIG = {}


def owners():
    """artefact prefix -> rig file, by finding the prefix literal in a rig."""
    src, own = sources(), {}
    for p in artefacts():
        for h in heads(p.name):
            if h in own:
                break
            # 🔴 PRIORITY, NOT POPULARITY. Two failures got here:
            #   1. a MENTION counted as a write — `e0.result.json` was
            #      attributed to e0v_reverify.py, which only names "e0" in a
            #      cross-reference table describing what ANOTHER rig writes.
            #   2. SUMMING matches let a file that references a prefix often
            #      outrank the file that DECLARES it: `e0k2` is owned by
            #      e0k2_anchor.py via `TAG = "e0k2"`, and that rig did not even
            #      make the candidate list because two others mention `e0k2_`
            #      more times.
            # Ownership is a hierarchy of evidence. First tier that yields
            # exactly one rig wins; a tier with several is AMBIGUOUS and the
            # migration refuses rather than guessing.
            # ⚠️ READERS LOOK LIKE WRITERS. `open("e0.result.json")` and
            # `open("e0.result.json","w")` both contain the literal, so e0read.py
            # tied with the rig that produces it. An explicit write outranks any
            # mention of the same name.
            tiers = [
                r'TAG\s*=\s*["\']%s["\']' % re.escape(h),          # declares it
                None,                                                # stem == head
                r'["\']%s\.[a-z.]*["\']\s*,\s*["\']w' % re.escape(h),   # open(..,"w")
                r'["\']%s\.[a-z.]*["\']\)\s*\.write_text' % re.escape(h),
                # 🔴 PRODUCTION BEFORE REFERENCE. `build("e0fine")` says a rig
                # MAKES it; `"e0fine.msh"` only says a rig NAMES it. With the
                # mention tier first, e0_solver_vs_math.py (which builds it) tied
                # with e0l_scaling.py (which reads `CFG = "e0fine.json"`).
                r'\b(?:build|run|solve_one|eigen_cfg)\(\s*["\']%s["\']'
                % re.escape(h),                                      # build("<h>")
                # 🔴 F-STRING-BUILT NAMES. `f"scale_{n}.log"` and
                # `f"e0h_r{a}"` construct the filename, so no literal
                # "scale.json" or TAG ever appears — both artefact sets were
                # MISSED by the migration and only turned up in the leftovers.
                # An f-string that OPENS with the head is a production signal.
                r'f["\']%s' % re.escape(h),                          # f"<h>_{...}"
                r'["\']%s\.[a-z]' % re.escape(h),                    # bare mention
                # 🔴 a bare `"<h>_..."` mention tier was REMOVED: it matched
                # cross-references in 18 rigs and could never identify an owner.
            ]
            picked = None
            for ti, pat in enumerate(tiers):
                if pat is None:
                    hits = [f for f in src if f[:-3] == h]
                else:
                    hits = [f for f, t in src.items() if re.search(pat, t)]
                if not hits:
                    continue
                if len(hits) > 1:
                    AMBIG.setdefault(h, sorted(hits))
                picked = sorted(hits)[0]
                break
            if picked:
                own[h] = picked
                break
    return own


def slug_of(rig):
    return rig[:-3].replace("_", "-") + "-00"


def plan():
    own = owners()
    def head_of(n):
        for h in heads(n):
            if h in own:
                return h
        return None
    raw = []
    for p in artefacts():
        if re.search(r"-00[_.]|^h3-", p.name):
            continue                              # already migrated
        h = head_of(p.name)
        if not h:
            continue
        raw.append({"from": str(p.relative_to(ROOT)),
                    "rel": str(p.relative_to(ROOT).parent),
                    "head": h, "slug": slug_of(own[h]),
                    "rest": p.name[len(h):]})

    def target(m, keep):
        r = m["rest"]
        if keep or not r.startswith("_"):
            return f"{m['slug']}_{m['head']}{r}"
        return f"{m['slug']}{r}"

    keep = set()
    for _ in range(4):
        seen = collections.defaultdict(list)
        for m in raw:
            seen[(m["rel"], target(m, m["head"] in keep))].append(m)
        bad = [v for v in seen.values() if len(v) > 1]
        if not bad:
            break
        for grp in bad:
            for m in grp:
                keep.add(m["head"])
    for m in raw:
        m["to"] = str(pathlib.Path(m["rel"]) / target(m, m["head"] in keep))
    return raw, own


def verify():
    bad = []
    for p in sorted(ROOT.glob("*.meta.json")):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        want = p.name[:-len(".meta.json")] + ".msh"
        if d.get("mesh") != want:
            bad.append(f"{p.name}: mesh={d.get('mesh')!r} expected {want!r}")
        elif not (ROOT / want).exists():
            bad.append(f"{p.name}: names a mesh that does not exist")
    return bad


def main():
    moves, own = plan()
    tgt = collections.Counter(m["to"] for m in moves)
    clash = {t: c for t, c in tgt.items() if c > 1}
    print(f"  artefact prefixes owned : {len(own)}")
    if AMBIG:
        print(f"  🔴 AMBIGUOUS ownership   : {len(AMBIG)} — resolve before applying")
        for h, t in list(AMBIG.items())[:5]:
            print(f"     {h!r} could be {t}")
    print(f"  renames planned         : {len(moves)}")
    print(f"  distinct retro slugs    : {len({m['slug'] for m in moves})}")
    print(f"  collisions              : {len(clash)}")
    for t in list(clash)[:5]:
        print(f"     🔴 {t}")
    if clash or AMBIG:
        print("  refusing: collisions and ambiguous ownership must both be zero")
        return 1
    if "--apply" not in sys.argv:
        for m in moves[:6]:
            print(f"    {m['from']}  ->  {m['to']}")
        print(f"    ... {max(0, len(moves) - 6)} more")
        print("\n  DRY RUN. Re-run with --apply.")
        return 0
    for m in moves:
        if (ROOT / m["to"]).exists():
            print(f"  🔴 target exists: {m['to']}")
            return 1
    ren = {}
    for m in moves:
        os.rename(ROOT / m["from"], ROOT / m["to"])
        ren[pathlib.Path(m["from"]).name] = pathlib.Path(m["to"]).name
    print(f"  ✅ renamed {len(moves)}")
    fixed = 0
    for p in sorted(ROOT.glob("*.meta.json")):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        if d.get("mesh") in ren:
            d["mesh"] = ren[d["mesh"]]
            p.write_text(json.dumps(d, indent=1) + "\n")
            fixed += 1
    print(f"  ✅ rewrote mesh field in {fixed} sidecar(s)")
    bad = verify()
    print("  ✅ sidecar<->mesh linkage verified" if not bad
          else f"  🔴 {len(bad)} BROKEN: {bad[:3]}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
