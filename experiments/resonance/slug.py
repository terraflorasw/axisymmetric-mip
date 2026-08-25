#!/usr/bin/env python3
"""One RUN = one SLUG = one config = one namespace for every file it writes.

🔴 User, 2026-08-25: *"characterize everything by config file, found by a
`--slug` parameter that contains the provenance from the docs ... Any output
files have to contain the slug as well, so that we don't have the results.json
collision from before."*

WHAT THIS PREVENTS, all of which happened:

  🔴 THE COLLISION (CONVENTIONS 7ap). `h3_driven` wrote `h3_driven.result.json`
     — named for the RIG, not the RUN. Re-running overwrote the previous run's
     numbers, and then an `ops/go` rsync pushed a day-old local copy back over
     the fresh remote one. `rsync -a` preserves mtime, so the clobber was
     invisible: the file looked like it was simply old.
  🔴 THE LOST BASELINE (7ao). Nothing archives a `.result.json`; the `.jsonl`
     journal holds solve METADATA only. Once overwritten, gone.
  🔴 THE CONTEXT COLLAPSE (7au). `Q_ext` meant 9,231 / 9,117 / 8,462 depending
     on mesh and extraction, and rigs hardcoded whichever they met first.
  🔴 THE PROVENANCE GAP (7s). "Which run produced this number?" had no answer
     that did not require reading a rig's source and guessing its era.

THE RULE: a slug names a CHARACTERISATION, not a program. `h3_driven` is a
program that has been run against several cavities at several densities; each of
those is a different characterisation and deserves its own slug, its own config,
and its own output namespace.

    ops/go ops/remote.sh h3_driven.py 32 --slug h3-driven-anchor-01

      reads   baseline-h3-driven-anchor-01.json     REQUIRED. No default.
      writes  h3-driven-anchor-01.result.json
              h3-driven-anchor-01.log
              h3-driven-anchor-01_<case>.msh
              postpro/h3-driven-anchor-01_<case>/

⚠️ THE SLUG CARRIES PROVENANCE, so it is not a serial number. `h3-driven-anchor-01`
says: hypothesis H3, the driven rig, the anchored-density characterisation, first
run. A second run that changes anything measurable gets `.02` and the first stays
on disk. THAT is the archive; there is no other.

🔑 Same shape as GATE 4 (`port_bc` has no default) and `wall_sigma()` (bind or
refuse). A thing that must be chosen must not be defaultable.
"""
import json
import pathlib
import re
import sys

# 🔑 THE SLUG CAN BE ANYTHING. Its only contract is that it determines BOTH
# filenames — the input config and every output file:
#
#     --slug X   reads  baseline-X.json      writes  X.result.json, X.log,
#                                                    X_<case>.msh, postpro/X_*
#
# So validation enforces exactly one thing: that it is safe as a filename
# component. No path separators, no whitespace, not starting with '.' or '-'.
# 🔑 STRUCTURE IS ADVICE, NOT A RULE. Carrying provenance in the slug
# (h3-eNxyz: hypothesis H3, experiment eNxyz) is what makes a directory listing
# readable a month later, and case is preserved because doc identifiers are
# case-bearing. But that is a convention for humans; the gate only cares that
# input and output cannot drift apart.
SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

CONFIG_FMT = "baseline-{slug}.json"


class SlugError(RuntimeError):
    pass


def parse(argv=None):
    """The slug from `--slug X`. REFUSES if absent or malformed."""
    a = list(argv if argv is not None else sys.argv[1:])
    if "--slug" not in a:
        raise SlugError(
            "no --slug. Every run must name its characterisation, because the "
            "output filenames are built from it and a rig-named output is what "
            "let one run silently overwrite another (CONVENTIONS 7ap).\n"
            "  e.g. --slug h3-driven-anchor-01")
    i = a.index("--slug")
    if i + 1 >= len(a):
        raise SlugError("--slug given with no value")
    s = a[i + 1]
    if not SLUG_RE.match(s):
        raise SlugError(
            f"slug {s!r} cannot be a filename component. It may not contain "
            f"path separators or whitespace, or start with '.' or '-'. "
            f"Anything else is allowed — but carry the provenance if you can, "
            f"e.g. h3-eNxyz or h3-driven-anchor-01.")
    return s


def config_path(slug):
    return pathlib.Path(__file__).with_name(CONFIG_FMT.format(slug=slug))


def config(slug):
    """The run's config. REFUSES if missing — never invents defaults."""
    p = config_path(slug)
    if not p.exists():
        raise SlugError(
            f"{p.name} does not exist. The config IS the characterisation: "
            f"which cavity, which solver, which operating point, and which "
            f"canonical values it binds. Write it before running.\n"
            f"  🔑 template: python3 slug.py --new {slug}")
    d = json.loads(p.read_text())
    if d.get("slug") != slug:
        raise SlugError(
            f"{p.name} declares slug {d.get('slug')!r} but was loaded as "
            f"{slug!r}. A config copied and not renamed is how a run silently "
            f"inherits another's provenance.")
    if "_run" not in d:
        raise SlugError(
            f"{p.name} has no '_run' block. A run config is a COPY of "
            f"baselines.json plus `_run`; write it with slug.derive().")
    for k in ("provenance", "binds", "parameters"):
        if k not in d["_run"]:
            raise SlugError(f"{p.name}: _run has no '{k}' section")
    return d


def out(slug, *parts):
    """A TAG guaranteed to carry the slug:  slug_part_part.

    For per-case artefacts — meshes, Palace output dirs, solve tags.
        out("h3-driven-anchor-01", "n18p90")  -> h3-driven-anchor-01_n18p90
    """
    tail = "_".join(str(p) for p in parts if p not in (None, ""))
    return f"{slug}_{tail}" if tail else slug


def outfile(slug, suffix):
    """A FILE NAME guaranteed to carry the slug:  slug.suffix

        outfile("h3-driven-anchor-01", "result.json")
            -> h3-driven-anchor-01.result.json

    🔴 This is the one that stops CONVENTIONS 7ap. The clobbered file was
    `h3_driven.result.json` — named for the PROGRAM, so every run of that
    program aimed at the same path.
    """
    return f"{slug}.{suffix.lstrip('.')}"


def bind(slug, name):
    """Resolve a canonical name through THIS run's declared context.

    🔑 The config says which context this characterisation is in; values.py
    holds what was measured there. Neither alone is enough, and a rig that
    hardcodes the number has thrown both away.
    """
    import values
    d = config(slug)
    if name not in d["_run"]["binds"]:
        raise SlugError(
            f"{slug} does not declare a binding for {name!r}. Add it to the "
            f"config's `binds` with the context it applies in — do not reach "
            f"for values.get() directly from a rig, or the run's record will "
            f"not say which value it used.")
    # 🔑 resolved against THIS RUN'S store, not the global.
    return values.get(name, store=config_path(slug),
                      **d["_run"]["binds"][name])



# ---------------------------------------------------------------------------
# 🔑 User, 2026-08-25: *"ideally, we should use slugs that reference the docs so
# that we get round-trips between code and prose."*
#
# A slug is only provenance if the reference RESOLVES. `provenance.document`
# names a file and a section; this checks the section text actually exists
# there, and — the other direction — that every slug a document cites has a
# config on disk. Both directions matter:
#
#   forward orphan  a run claiming a doc section nobody wrote
#   reverse orphan  a document citing a run whose config is gone
#
# ⚠️ Prose drifts silently; that is the whole reason CONVENTIONS exists. A
# reference that is CHECKED is the only kind that stays true.
DOC_SEP = "§"


def doc_ref(cfg):
    """(path, anchor) from `provenance.document` = 'FILE.md § SECTION TEXT'."""
    raw = ((cfg.get("_run") or {}).get("provenance") or {}).get("document") or ""
    if DOC_SEP not in raw:
        return None, None
    f, anchor = raw.split(DOC_SEP, 1)
    return f.strip(), anchor.strip()


def check_roundtrip(root=None):
    """Findings as (severity, message). Empty means both directions resolve."""
    root = pathlib.Path(root or pathlib.Path(__file__).parent)
    out, slugs = [], {}
    for c in sorted(root.glob("baseline-*.json")):
        slug = c.name[len("baseline-"):-len(".json")]
        try:
            cfg = json.loads(c.read_text())
        except Exception as e:
            out.append(("ERROR", f"{c.name}: unreadable ({e})"));  continue
        slugs[slug] = cfg
        f, anchor = doc_ref(cfg)
        if not f:
            out.append(("ERROR", f"{c.name}: provenance.document has no "
                                 f"'FILE.md {DOC_SEP} SECTION' reference"))
            continue
        d = root / f
        if not d.exists():
            out.append(("ERROR", f"{c.name}: cites {f}, which does not exist"))
        elif anchor and anchor not in d.read_text():
            out.append(("ERROR", f"{c.name}: cites {f} {DOC_SEP} {anchor!r}, "
                                 f"which is not in that file — prose moved or "
                                 f"the reference was never true"))
    # 🔑 A slug's LEADING SEGMENT is a doc identifier (h3, e3, h2b). It is
    # pinned by every artefact on disk that carries the slug, so it must agree
    # with the hypothesis the run declares. See CONVENTIONS 7ay / 7j: the H2<->H3
    # swap moved status labels across content and cost 31 rigs.
    for slug, cfg in slugs.items():
        head = re.split(r"[-._]", slug)[0].lower()
        hyp = ((cfg.get("_run") or {}).get("provenance") or {}).get("hypothesis") or ""
        toks = {t.lower().rstrip(":,") for t in re.split(r"[\s/]+", hyp)}
        if head and not any(t.startswith(head) or head.startswith(t)
                            for t in toks if t):
            out.append(("ERROR",
                        f"baseline-{slug}.json: slug starts {head!r} but "
                        f"declares hypothesis {hyp!r} — the leading segment is "
                        f"a doc identifier and every artefact on disk carries "
                        f"it. Rename the run, never the identifier (7ay)."))

    for d in sorted(root.glob("*.md")):
        text = d.read_text()
        for m in re.finditer(r"baseline-([A-Za-z0-9][A-Za-z0-9._-]*)\.json", text):
            if m.group(1) not in slugs:
                out.append(("ERROR", f"{d.name} cites baseline-{m.group(1)}"
                                     f".json, which does not exist"))
    return out



# ---------------------------------------------------------------------------
# 🔑 User, 2026-08-25: *"we can keep a global baselines.json, and then mutate it
# to an appropriate slug version depending on case, run the sweeps or whatever
# against it, and then either land the values back into the global
# baselines.json or if they're not definitive, sideline them as tentative
# pending further investigation."*
#
#     baselines.json  ──derive──▶  baseline-<slug>.json  ──run──▶  <slug>.result.json
#          ▲                        (FROZEN inputs)                      │
#          └──────────── promote(definitive) ◀── or ── sideline(tentative)
#
# WHY EACH ARROW EXISTS, from failures already in this record:
#
#   derive   freezes the inputs a run actually used, with a HASH of the global
#            it forked from. "Which baseline did this run use?" stopped being
#            answerable the moment anyone edited a constant mid-programme —
#            which is how eta.reference was wrong four times (7c) without any
#            single run looking wrong.
#   promote  lands a measurement back under a canonical name WITH the slug that
#            produced it, so the value carries its own provenance forever.
#   sideline is the half that was always missing. Values were previously either
#            asserted or absent; a number that is measured but NOT yet
#            trustworthy had nowhere to live, so it got asserted. `tentative`
#            entries are recorded, are visible, and are NOT returned by
#            values.get() unless explicitly requested.
import hashlib


def _sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()[:16]


def derive(slug, provenance=None, binds=None, parameters=None):
    """COPY the whole global store into this run's own baselines.

    🔑 User, 2026-08-25: *"I don't mean we edit baselines.json for every
    question, we copy it with an appropriate slug, then run against that, then
    decide what to do with the output."*

    So `baseline-<slug>.json` IS a baselines.json — the same schema, every
    entry — plus a `_run` block. The rig reads its values from ITS OWN copy and
    never touches the global at run time. That means:

      - the global can move mid-run without changing what the run used;
      - "which baselines did this produce against?" is the file next to the
        result, not a reconstruction from dates;
      - mutating an input for one question is a local edit to a copy, not a
        change everyone else silently inherits — which is how `eta.reference`
        was wrong four times without any single run looking wrong (7c).
    """
    p = config_path(slug)
    if p.exists():
        raise SlugError(f"{p.name} exists — a run's config is immutable once "
                        f"written. Take the next run number.")
    g = pathlib.Path(__file__).with_name("baselines.json")
    cfg = json.loads(g.read_text())          # ← the WHOLE store, copied
    cfg["_run"] = {
        "slug": slug,
        "derived_from": {"file": g.name, "sha256_16": _sha(g)},
        "provenance": provenance or dict(TEMPLATE["provenance"]),
        "binds": dict(binds or {}),
        "parameters": dict(parameters or {}),
        "note": "Copied from the global store, then mutated for this run. "
                "Edit THIS file, never the global, to change an input for one "
                "question. Land results back with slug.promote().",
    }
    cfg["slug"] = slug
    p.write_text(json.dumps(cfg, indent=1) + "\n")
    return p


def promote(slug, name, value, context, status="definitive",
            verification=None, falsification=None, note=None, date=None):
    """Land a measured value into the GLOBAL store under a canonical name.

    status="tentative" is the sideline: recorded, visible, and NOT returned by
    values.get() unless the caller asks for tentative explicitly.
    """
    if status not in ("definitive", "tentative"):
        raise SlugError("status must be 'definitive' or 'tentative'")
    if status == "definitive" and not verification:
        raise SlugError(
            f"refusing to promote {name} as definitive with no `verification`. "
            f"baselines.json's own _meta rule requires it. If you cannot say "
            f"what outside this rig it agrees with, it is TENTATIVE.")
    g = pathlib.Path(__file__).with_name("baselines.json")
    d = json.loads(g.read_text())
    e = d.setdefault(name, {"kind": "result", "unit": "1",
                            "description": f"(promoted from {slug})",
                            "contexts": []})
    # 🔴 date is PASSED, never generated: scripts here must not call
    # datetime.now() (the journal/resume contract), and an undated
    # result is one you cannot order against a retraction.
    if not date:
        raise SlugError("promote() needs an explicit date=YYYY-MM-DD")
    row = {"value": value, "context": dict(context), "rig": slug,
           "date": date, "status": status,
           "verification": verification, "falsification": falsification}
    if note:
        row["note"] = note
    for i, r in enumerate(e["contexts"]):
        if r.get("context") == row["context"]:
            row["supersedes"] = r["value"]
            e["contexts"][i] = row
            break
    else:
        e["contexts"].append(row)
    g.write_text(json.dumps(d, indent=1) + "\n")
    return row


TEMPLATE = {
    "slug": None,
    "provenance": {
        "hypothesis": "H?  — which hypothesis or PLAN experiment this serves",
        "document": "KNOWN.md § ...  — where the question is stated",
        "question": "the one sentence this run answers",
        "supersedes": None,
        "date": None,
    },
    "binds": {},
    "parameters": {},
}


def _new(slug):
    p = config_path(slug)
    if p.exists():
        raise SlugError(f"{p.name} already exists — pick the next run number")
    d = dict(TEMPLATE)
    d["slug"] = slug
    p.write_text(json.dumps(d, indent=1) + "\n")
    return p


def main():
    if "--check" in sys.argv:
        fs = check_roundtrip()
        for lvl, msg in fs:
            print(f"  🔴 {msg}")
        print(f"  {'✅ code and prose round-trip' if not fs else f'🔴 {len(fs)} broken reference(s)'}")
        return 1 if fs else 0
    if "--new" in sys.argv:
        s = sys.argv[sys.argv.index("--new") + 1]
        if not SLUG_RE.match(s):
            raise SlugError(f"malformed slug {s!r}")
        print(f"wrote {_new(s).name}")
        return 0
    s = parse()
    d = config(s)
    print(json.dumps(d, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
