# GLOSSARY — say exactly this, mean exactly this

**Every entry here caused a real error.** A term that can be read two ways will
be, and the wrong reading survives because nothing crashes.

---

## The three OPERATING REGIMES — H3's axis

| term | means | does NOT mean |
|---|---|---|
| **COLD** | cavity at ambient, never operated or fully cooled. **First ignition.** | "no plasma" in general |
| **HOT** | cavity **already operating** — hot walls, hot gas, **NO plasma**. **RE-ignition.** | weakly ionised, or "part-way to loaded" |
| **LOADED** | plasma present and running | "hot" |

🔴 **HOT is THERMAL, not a plasma density.** I read it as a density slice and
built a rig that tagged the plasma cases "hot", propagating the confusion.
Hot differs from cold by: dimensions (α = 23.1e-6/K → **−5.7 MHz at +100 K**),
gas density (n ∝ 1/T → **E/N 10× higher at 3000 K**), wall σ (**Q × 0.78 at
+100 K**). It is the regime that decides whether the instrument restarts itself.

## The MODE FILTER — two devices, one name

| flag | part | status |
|---|---|---|
| `--groove w,depth` | **annular slot** at the cap/barrel corner, both caps | ✅ **CURRENT.** This is the design |
| `--mode-filter <t>` | **quartz annulus** | 🔴 **RETIRED**, superseded by the groove |

🔴 Checking "is the mode filter on?" finds `--mode-filter 0`, reads it as a
deliberate choice, and stops. **The current device has a different flag**, and it
was absent from `GEO` for the whole loaded programme.

## The CAVITY VARIANTS — say which one

| term | groove | loop | torch | plasma |
|---|---|---|---|---|
| **bare** | ✗ | ✗ | ✗ | ✗ |
| **grooved** | ✅ 5×10 | ✗ | ✗ | ✗ |
| **design cavity, COLD** | ✅ | ✅ | ✅ | ✗ |
| **design cavity, LOADED** | ✅ | ✅ | ✅ | ✅ |

⚠️ **"Empty" and "bare" are not synonyms for each other or for anything else.**
Name the four flags or do not use the word.
🔑 `GEO` = **bare** (instrument rigs, closed-form comparison only).
`GEO_DESIGN` = **grooved**. Neither carries a loop or plasma; rigs add those.

## Q AND η — the reference is part of the number

| symbol | means | ⚠️ |
|---|---|---|
| **Q₀** | unloaded-by-the-port Q of a given cavity | **meaningless without saying WHICH cavity** |
| **Q_bare = 44,384** | E0's **bare** cavity: no groove, no loop, no torch | 🔴 **NOT the η reference for anything else** |
| **29,854** | with a loop, **no groove**, and a *different* loop | 🔴 also not a substitute |
| **η** | 1 − Q₀/Q_ref — the fraction of DISSIPATED power not going to the walls | 🔴 **NOT "power into the plasma"** until the E3 closure runs |
| **β** | Q₀/Q_ext, coupling | not mesh-converged (43% for 1.25× refinement) |
| **delivered / net power** | (1−|S11|²)·η | needs β's BRANCH resolved and the closure — see PLAN E3 |

🔑 **There is no η reference to look up for the design cavity. It must be
SOLVED, per loop size, on the grooved looped mesh.**

## "THE FILTER WORKS" — two different claims

| claim | status |
|---|---|
| the groove makes TE011 **the mode the tuner locks to** | ✅ measured (driven, `h3_groove`) |
| the groove **clears the band** (exactly one mode in 2.40–2.50) | 🔴 **FIRES** in eigen at both loop sizes |

🔑 **A driven sweep shows what the PORT COUPLES TO, not what EXISTS.** One dip
does not mean one mode. Pair driven with eigen before saying "the filter works".

## LOOP GEOMETRY

`--loop d,w,rw,gap` — **`w` is a HALF-width.** Area = **d × 2w**.
11×8 → **176 mm²** (not 88). Verified against INSTRUMENT's own table
(5×3.5→35, 7.5×5.5→82, 11×8→176, 16×12→384).

## NUMBERING — two axes, neither supersedes the other

| | |
|---|---|
| **E0–E4** | `PLAN.md`, the **fixed experiment list**. It does not grow |
| **H0–H5** | `HYPOTHESES.md`, the **question set**. Evolves |
| **R-numbers** | `geometry.py` **code revisions**, with an owner and a chain. 🔴 **NEVER MINT ONE** — cite findings by DATE and DESCRIPTION |

## STATUS WORDS — they are not interchangeable

| word | means |
|---|---|
| **baseline** | validated, and **open to refinement** (the groove's 5×10) |
| **frozen** | 🔴 avoid. It has meant both "settled" and "removed from the geometry", and that ambiguity cost a day |
| **retired** | the QUESTION is closed. **Says nothing about whether the RESULT is live** |
| **discarded** | the measurement is of the wrong thing. Do not quote, do not salvage |
| **scope-invalid** | 🔴 avoid — too soft. Say **discarded** |
| **missing data** | an evaluation that did not converge. **NOT a bad score** (OPTIMIZER §3) |
