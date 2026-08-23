# CLAUDE.md — read before doing anything

This repo is **`axisymmetric-mip`**. The live work is the AMIP cavity, in
**`experiments/resonance/`**.

## ⚠️ The working directory is the repo's PARENT, on purpose

Sessions run from **one level above this repo**, because `aws.pem` lives there
and **must never enter version control**. So:

    regenerative-soil-testing/     <- cwd. NOT a repo. holds aws.pem, rsync.sh
      axisymmetric-mip/            <- THIS repo (git root)
        experiments/resonance/     <- the live programme
      soil-testing/  amip/         <- sibling programmes, not this repo

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
2. **`experiments/resonance/PLAN.md`** — the FIXED experiment list, **E0–E4**.
3. **`experiments/resonance/CONVENTIONS.md`** — the recurring errors. Long, and every
   entry is a mistake actually made here, several of them twice.

⚠️ **`FINDINGS.md` is NOT in the working tree.** It was removed 2026-08-23
because 5,300 lines across three invalidated eras confused more than it helped.
Retrieve it only to follow a citation:

    git show ba740d6:experiments/resonance/FINDINGS.md

(Run from inside this repo, or add `-C axisymmetric-mip` from the parent.)

## Non-negotiable, and each one was learned expensively

- 🔴 **THE CAVITY HAS A MODE FILTER.** An annular groove, frozen at **5 × 10 mm**
  (H2). It is the design. Use **`GEO_DESIGN`**, not `GEO` — `GEO` is the BARE
  cavity and exists only for instrument rigs comparing against closed form.
  `run()` refuses a plasma solve on a groove-free mesh.
  *A context reset once dropped this fact while leaving every downstream number
  intact and plausible; 31 rigs then measured a cavity nobody is building.*
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
- ⚠️ **Land conclusions in a document before starting the next rig.** A rig is
  done when the conclusion is written, not when it exits 0 (§8b).

## Operations

- Instance address lives in `ops/env.sh` — one line. Never hardcode it.
- `ops/go <script>` is the only way to run things; it lints and syncs first.
- `ops/go ops/remote.sh <rig.py> 32` launches a rig on the instance.
- Long solves: watch, do not poll. The rig appends `EXIT=` when done.
