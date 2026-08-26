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


def _require_slug(slug):
    """A slug is a short string. Passing a config DICT built a 6 KB filename
    and raised deep in pathlib instead of here (2026-08-25)."""
    if not isinstance(slug, str):
        raise TypeError(
            f"slug must be a str, got {type(slug).__name__}. "
            f"config() returns the CONFIG; stamp()/out()/config() all take the "
            f"SLUG. You probably wrote stamp(config(slug)) for stamp(slug).")
    if not slug or len(slug) > 64 or "/" in slug or "\n" in slug:
        raise ValueError(f"implausible slug {slug[:40]!r}")
    return slug


def config_path(slug):
    _require_slug(slug)
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


# ---------------------------------------------------------------------------
# 🔑 User, 2026-08-25: *"intermediate files and outputs include the hash of
# their input baselines, up to 8 characters, say. So if the input file changes
# without the slug changing, we can see if they differ."*
#
# The slug pins WHICH question. The STAMP pins WHICH INPUTS answered it.
#
#     h3-qext-01.4f2a9c31.result.json
#     h3-qext-01.4f2a9c31_n18p90.msh
#     ^---------^ ^------^
#      question    the exact bytes of baseline-h3-qext-01.json
#
# 🔴 WHAT IT CATCHES THAT THE SLUG ALONE CANNOT: a config edited between two
# runs of the same slug. Without the stamp the second run overwrites the first
# and the difference is invisible — which is CONVENTIONS 7ap with extra steps.
# With it, the outputs land at DIFFERENT NAMES and the divergence is a directory
# listing.
#
# ✅ AND IT CONVERTS IDEMPOTENCE FROM A HOPE INTO A CHECK (7bc): same slug +
# same stamp must mean same output. If it does not, the non-determinism is in
# the SOLVER, not the inputs — and that is now a separable question.
#
# ⚠️ The config itself is NOT stamped: it cannot contain its own hash. Only
# what it produces carries it.
def stamp(slug):
    """First 8 hex of sha256(baseline-<slug>.json) — the input fingerprint."""
    return _sha(config_path(slug))[:8]


def out(slug, *parts):
    """A stamped TAG:  slug.stamp_part_part  — meshes, postpro dirs, solves."""
    tail = "_".join(str(p) for p in parts if p not in (None, ""))
    base = f"{slug}.{stamp(slug)}"
    return f"{base}_{tail}" if tail else base


def outfile(slug, suffix):
    """A stamped FILE NAME:  slug.stamp.suffix

    🔴 This is what stops 7ap AND its subtler cousin. `h3_driven.result.json`
    was named for the PROGRAM, so every run collided. `<slug>.result.json` fixes
    that across questions; `<slug>.<stamp>.result.json` fixes it across INPUT
    REVISIONS of the same question.
    """
    # 🔴 "result.json is not a valid filename" — user, 2026-08-25. The suffix is
    # a SUFFIX, not a path: a caller passing an absolute/relative path, or a
    # name already carrying a stamp, would produce something that reads like a
    # qualified artefact but is not one.
    suffix = suffix.lstrip(".")
    if "/" in suffix or suffix.startswith("baseline-"):
        raise SlugError(f"outfile suffix {suffix!r} is a PATH or a config name, "
                        f"not a suffix. Pass e.g. 'result.json'.")
    if stamp_of_artefact(f"x.{suffix}"):
        raise SlugError(f"outfile suffix {suffix!r} already carries a stamp — "
                        f"the result would be double-stamped.")
    return f"{slug}.{stamp(slug)}.{suffix}"


def stamp_of_artefact(name):
    """The stamp embedded in an artefact name, or None."""
    m = re.match(r"^(?P<slug>.+?)\.(?P<stamp>[0-9a-f]{8})[._]", name)
    return (m.group("slug"), m.group("stamp")) if m else None


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



def check_stamps(root=None):
    """Do the artefacts on disk still match the config that claims to describe them?

    🔴 THIS IS THE DETECTION THE STAMP EXISTS FOR. An artefact carries the hash
    of the inputs that produced it. If the config has been edited since, the
    stamps disagree — and the config no longer describes the result sitting next
    to it. Without this the edit is invisible and the result silently acquires a
    provenance it never had (CONVENTIONS 7s).
    """
    root = pathlib.Path(root or pathlib.Path(__file__).parent)
    known = {p.name[len("baseline-"):-len(".json")] for p in root.glob("baseline-*.json")}
    out, seen = [], {}
    for p in sorted(root.glob("*")) + sorted((root / "postpro").glob("*")):
        got = stamp_of_artefact(p.name)
        if not got:
            continue
        sl, st = got
        if sl not in known:
            continue
        seen.setdefault(sl, set()).add(st)
    for sl, stamps in sorted(seen.items()):
        cur = stamp(sl)
        stale = sorted(stamps - {cur})
        if stale:
            out.append(("ERROR",
                        f"{sl}: artefacts carry stamp(s) {stale} but "
                        f"baseline-{sl}.json now hashes to {cur} — THE CONFIG "
                        f"WAS EDITED AFTER THE RUN. Those results were produced "
                        f"by inputs that no longer exist. Either restore the "
                        f"config or re-run under a new slug."))
    # 🔴 THIS SWEEP WAS KNOWN-SLUG-DRIVEN AND THEREFORE NEARLY BLIND.
    # It only looked at slugs that HAVE a baseline-*.json, so every artefact
    # whose slug never got a config was invisible: 30 of 32 *.result.json files
    # carried no stamp and the check reported ONE. An audit that can only see
    # the things already registered is not an audit (7d).
    # ✅ Now driven by what is ON DISK.
    unstamped = [p.name for p in sorted(root.glob("*.result.json"))
                 if not stamp_of_artefact(p.name)]
    if unstamped:
        out.append(("WARN",
                    f"{len(unstamped)} result file(s) carry NO stamp, so the "
                    f"inputs that produced them cannot be verified "
                    f"(e.g. {unstamped[:3]}). These predate the stamp regime. "
                    f"Under CONVENTIONS 7bm they are NOT citable as current "
                    f"results without a re-run; see NEXT.md."))
    return out


def unstamped_artefacts(root=None):
    """Every result file on disk with no stamp, so the burn-down is countable."""
    root = pathlib.Path(root or pathlib.Path(__file__).parent)
    return sorted(p.name for p in root.glob("*.result.json")
                  if not stamp_of_artefact(p.name))


def check_roundtrip(root=None):
    """Findings as (severity, message). Empty means both directions resolve."""
    root = pathlib.Path(root or pathlib.Path(__file__).parent)
    out, slugs = list(check_all_unique(root)) + list(check_stamps(root)), {}
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
    check_unique(slug)          # 🔑 uniqueness is a PRECONDITION, not a hope
    p = config_path(slug)
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



def retro(slug, provenance=None, root=None):
    """Write a config for an artefact set that ALREADY EXISTS, honestly marked.

    🔴 THE MIGRATION CREATED 50 RETRO SLUGS WITH ARTEFACTS AND NO CONFIG — the
    exact state this whole regime exists to eliminate: results on disk with no
    record of what produced them. But `derive()` REFUSES over existing artefacts
    (check_unique 4), and rightly: a normal run must never adopt files it did
    not write.

    ⚠️ SO A RETRO CONFIG IS A DIFFERENT OBJECT AND SAYS SO. It carries
    `retrofit: true` and `derived_from.sha256_16: null`, because the global it
    ran against was never snapshotted and CANNOT be recovered. It documents what
    the artefacts are; it does NOT claim to reproduce them.
    """
    root = pathlib.Path(root or pathlib.Path(__file__).parent)
    p = config_path(slug)
    if p.exists():
        raise SlugError(f"{p.name} exists")
    found = sorted({q.name for q in root.glob(f"{slug}*")}
                   | {q.name for q in (root / "postpro").glob(f"{slug}*")})
    if not found:
        raise SlugError(f"no artefacts named {slug}* — use derive() for a new run")
    g = root / "baselines.json"
    cfg = json.loads(g.read_text())
    cfg["slug"] = slug
    cfg["_run"] = {
        "slug": slug,
        "retrofit": True,
        "derived_from": {"file": g.name, "sha256_16": None,
                         "note": "🔴 UNRECOVERABLE. This run predates the "
                                 "copy-per-slug workflow, so the global it used "
                                 "was never snapshotted. The entries in this "
                                 "file are the CURRENT global, not what the run "
                                 "saw."},
        "provenance": provenance or dict(TEMPLATE["provenance"]),
        "binds": {},
        "parameters": {},
        "artefacts": found[:200],
        "note": "🔴 RETROFIT, NOT A RECORD. Written after the fact to give an "
                "existing artefact set a name and a doc reference. It documents "
                "what these files are; it does NOT claim to reproduce them.",
    }
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



# ---------------------------------------------------------------------------
# 🔑 User, 2026-08-25: *"all slugs must be unique. No collisions."*
#
# "The config does not exist yet" is NOT uniqueness. Four ways two runs can
# still collide, all of which the slug regime is supposed to prevent:
#
#   1. ARTEFACTS WITHOUT A CONFIG. A slug whose baseline-*.json was never
#      written, or was deleted, silently adopts whatever `<slug>*` is already
#      on disk — inheriting another run's meshes and postpro dirs.
#   2. CASE. `H3-Qext-01` and `h3-qext-01` are different slugs and the SAME
#      file on a case-insensitive filesystem. Case is preserved deliberately
#      (doc identifiers bear it), so it must be checked explicitly.
#   3. PREFIX. `h3-qext-01` and `h3-qext-01b` never collide exactly, but every
#      glob in ops/ is `<slug>*` — fetch, cleanup and status would sweep both.
#      That is a collision in every tool that matters.
#   4. REUSE AFTER DELETION. Deleting a config does not delete its artefacts,
#      so the name is NOT free again. It is retired.
def check_unique(slug, root=None):
    """Raise unless `slug` can own its whole filename namespace. """
    root = pathlib.Path(root or pathlib.Path(__file__).parent)
    if config_path(slug).exists():
        raise SlugError(f"baseline-{slug}.json already exists — a run config is "
                        f"immutable. Take the next run number.")
    known = [p.name[len("baseline-"):-len(".json")]
             for p in root.glob("baseline-*.json")]
    low = slug.lower()
    for k in known:
        if k.lower() == low:
            raise SlugError(
                f"{slug!r} collides with {k!r} by CASE. They are different "
                f"slugs and the same file on a case-insensitive filesystem.")
        if low.startswith(k.lower()) or k.lower().startswith(low):
            raise SlugError(
                f"{slug!r} and the existing {k!r} are PREFIXES of one another. "
                f"Every glob in ops/ is `<slug>*`, so fetch, cleanup and status "
                f"would sweep both runs. Pick a name that is not a prefix.")
    stray = sorted({p.name for p in root.glob(f"{slug}*")}
                   | {p.name for p in (root / "postpro").glob(f"{slug}*")})
    if stray:
        raise SlugError(
            f"{slug!r} has {len(stray)} artefact(s) on disk already "
            f"(e.g. {stray[:3]}). A deleted config does NOT free the name — "
            f"the artefacts still carry it. That name is RETIRED.")
    return True


def check_all_unique(root=None):
    """Findings for every existing slug pair. Used by --check."""
    root = pathlib.Path(root or pathlib.Path(__file__).parent)
    names = sorted(p.name[len("baseline-"):-len(".json")]
                   for p in root.glob("baseline-*.json"))
    out = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if a.lower() == b.lower():
                out.append(("ERROR", f"slugs {a!r} and {b!r} differ only by CASE"))
            elif a.lower().startswith(b.lower()) or b.lower().startswith(a.lower()):
                out.append(("ERROR", f"slugs {a!r} and {b!r} are PREFIXES of one "
                                     f"another — `<slug>*` globs sweep both"))
    return out


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
            print(f"  {'🔴' if lvl == 'ERROR' else '⚠️ '} {msg}")
        errs = [f for f in fs if f[0] == 'ERROR']
        print(f"  {'✅ slugs, stamps and prose all agree' if not errs else f'🔴 {len(errs)} error(s)'}")
        return 1 if errs else 0
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
