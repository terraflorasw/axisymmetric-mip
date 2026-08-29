# CLAUDE.md — read before doing anything

This repo is **`axisymmetric-mip`**. The live work is the AMIP cavity, in
**`experiments/resonance/`**.

## ⚠️ The working directory is the repo's PARENT, on purpose

Sessions run from **one level above this repo**, because `aws.pem` lives there
and **must never enter version control**. So:

    regenerative-soil-testing/     <- cwd. NOT a repo. holds aws.pem, rsync.sh
      axisymmetric-mip/            <- THIS repo (git root)
        experiments/resonance/     <- THE LIVE PROGRAMME (the cavity)
        experiments/control-loop/  <- the SOURCE side: LDMOS, match, control.
                                      ⏸️ PARKED, opened 2026-08-24
        experiments/spectroscopy/  <- WHY any of it exists: the analytical
                                      measurement. Opened 2026-08-24.
                                      🔴 resonance is BLOCKED on one answer
                                      from here: the required GAS TEMPERATURE
        experiments/ignition-options/ <- HOW the plasma starts. Opened
                                      2026-08-25. 🔴 HOLDS A LIVE BLOCKER:
                                      resonance item 7's loop TARGET flips
                                      on the answer. NOT the removed
                                      `ignition/`, which was TM-specific
        experiments/torch-geometry/ <- where EM, residency/LOD and the NITROGEN
                                      GENERATOR collide. Opened 2026-08-25.
                                      🔑 gas flow is a PRODUCT constraint:
                                      10-12 L/min = quiet bench compressor,
                                      20+ = utility room. The programme
                                      assumes 20. ⏸️ No modelling: the
                                      standing decision is standard Fassel
      soil-testing/  amip/         <- sibling programmes, not this repo

⚠️ **`experiments/waveguide/` and `experiments/ignition/` were REMOVED**
(commit `2db1d59`, 2026-08-24) — superseded by resonance. Their numbers come
from earlier cavity designs and **do not transfer**; retrieve only to follow a
citation, the way `FINDINGS.md` is handled:

    git show 2db1d59^:experiments/waveguide/FINDINGS.md

⚠️ Untracked solver artefacts (csv/msh/log/vtu) may still sit in those paths on
a given machine. **They are data with no surviving documents — do not read them
as results.**

Consequences worth knowing:
- `git` commands need `-C axisymmetric-mip`, or run them from inside the repo.
- `ops/*.sh` derive the key as `../../../../aws.pem` from `ops/` — that is the
  parent, and it is correct.
- Anything written to the parent directory is **NOT version controlled** and
  will not reach another machine.

## Start here, in this order

1. **`experiments/resonance/KNOWN.md`** — one page. Everything
   this programme has established, what is explicitly NOT established, and an
   index of all ten documents. **If it is not in KNOWN.md, it is not known.**
2. **`experiments/resonance/GLOSSARY.md`** — say exactly this, mean exactly
   this. Short. **Every entry in it caused a real error**, and several cost a
   day: `hot` is a THERMAL regime not a plasma density; two different parts are
   called "mode filter"; a Q is meaningless without saying which cavity.
3. **`experiments/resonance/PLAN.md`** — the FIXED experiment list, **E0–E4**.
4. **`experiments/resonance/CONVENTIONS.md`** — the recurring errors. Long, and every
   entry is a mistake actually made here, several of them twice.

⚠️ **`FINDINGS.md` is NOT in the working tree.** It was removed 2026-08-23
because 5,300 lines across three invalidated eras confused more than it helped.
Retrieve it only to follow a citation:

    git show ba740d6:experiments/resonance/FINDINGS.md

(Run from inside this repo, or add `-C axisymmetric-mip` from the parent.)

## Non-negotiable, and each one was learned expensively

- 🔴 **THE CAVITY HAS A MODE FILTER.** An annular groove, **baseline 5 × 10 mm**
  (H2). Use **`GEO_DESIGN`**, not `GEO` — `GEO` is the BARE cavity and exists
  only for instrument rigs comparing against closed form.
  ⚠️ **BASELINE, not frozen.** H2 validated it COLD against the LDMOS range.
  Loading moves every mode, so refining the groove size under load is **H3's
  job**. Do not treat 5 × 10 as immutable.
  `run()` refuses a plasma solve on a groove-free mesh.
  *A context reset once dropped this fact while leaving every downstream number
  intact and plausible; 31 rigs then measured a cavity nobody is building.*
- 🔴 **ANYTHING MEASURED WITHOUT THE GROOVE, AFTER H1, IS DISCARDED.** H1 fixed
  the cavity; a groove-free mesh after that is a different cavity and its mode
  landscape is not the design's. **The one exception is instrument rigs
  comparing against CLOSED FORM** — a plain cylinder is the point there, and
  `GEO` exists for it. Audited by mesh sidecar (`geometry_mm.groove`), this
  discards **all of h4** and **66 of 72 h3 meshes**. See `KNOWN.md` § THE FILTER.
- 🔴 **A competing IN-BAND mode is an ALARM, not a puzzle.** A filtered cavity
  has ONE resonance in the source's tuning band. If you find yourself building
  cleverer mode-selection logic, suspect the geometry first (§7i).
- 🔴 **THE EXPERIMENT LIST DOES NOT GROW.** Surprises go in PLAN's *Parked*
  section — recorded so they are not lost, and **they do not spawn runs**. Do
  not invent hypotheses; find which of E0–E4 the question belongs to (§7k).
- 🔴 **NEVER MINT AN R-NUMBER.** They are `geometry.py` code revisions with an
  owner and a chain. Cite findings by DATE and DESCRIPTION. The previous
  programme was abandoned because its R-register "grew by generating its own
  questions — an inward-facing loop with no external anchor can only expand"
  (`README.md`).
- 🔴 **NAME THE EXTERNAL ANCHOR before starting work.** Closed form, a measured
  datum, a hardware constraint, or a person. Provenance descends from **E0**
  (instrument, vs closed form), **H1** (cavity D/L, vs an analytic max-min) and
  **H2** (the groove, vs the LDMOS tuning range). A result supported only by
  another result of this programme is not evidence.
- 🔴 **SEARCH FOR PRIOR ART BEFORE DERIVING SETTINGS OR METHOD.**
  `KNOWN.md` § PRIOR ART lists which rig already solved what — grooved-cavity
  eigen settings, coupling-branch resolution, Q₀ extraction, the η reference
  trap. On 2026-08-23 I derived my own four times and was wrong four times, each
  in a way the existing solution had already handled. **This is a search
  failure, not a reasoning failure**, and it is the most repeated error in the
  record.
- ⚠️ **Land conclusions in a document before starting the next rig.** A rig is
  done when the conclusion is written, not when it exits 0 (§8b).

## Operations

- Instance address lives in `ops/env.sh` — one line. Never hardcode it.
- `ops/go <script>` is the only way to run things; it lints and syncs first.
- `ops/go ops/remote.sh <rig.py> 32 <slug>` — **pass the slug.** Without one the
  log is named for the RIG, so a re-run overwrites it, and there is nothing to
  watch by name.
- Long solves: **`ops/watch.sh <slug>`** — watch, do not poll. The rig appends
  `EXIT=` when done.
  🔴 **Do NOT pipe it into `tail`/`head`/anything buffering** — they hold their
  input until EOF, so a live watch emits nothing until the run ends. It is
  survivable (every line is mirrored to `<slug>.watch.log`) but the point of a
  watch is to watch. `ops/status.sh` is a SNAPSHOT, not a watch. See §7bq — the
  watcher has failed four times, never the same way twice.
