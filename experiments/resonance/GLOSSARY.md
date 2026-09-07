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
+100 K** — 🔴 **MEASURED ×0.838 on 2026-08-24 (`h3_hot`)**, which is exactly
√σ with standard aluminium α_R = 4.29e-3/K. 0.78 needs α_R = 6.44e-3/K, ~1.5×
aluminium. **Unresolved: σ is a solver INPUT, so where did 0.78 come from?**). It is the regime that decides whether the instrument restarts itself.
⚠️ **2026-08-24: read that as EMPHASIS, not a finding.** It was written to stop
HOT being dropped, and it has been over-read since. A hot cavity can be allowed
to cool, or cooled harder. **The real consequence is that the control loop needs
a cavity TEMPERATURE input** — with it, thermal detuning is a computed offset
(−5.7 MHz/100 K) rather than a search. **A parameter to read, not a barrier.**

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
| **β** | Q₀/Q_ext, coupling | not MESH-converged — see *converged* below |
| **converged** | 🔴 **SAY WHICH.** Two unrelated meanings, both live in these documents | see the split below |
| **· solver-converged** | the SOLVE reached its own tolerance: adaptive PROM under `AdaptiveTol`, GMRES under its residual, NLEPS finding modes | a property of ONE run. Its failure is an ERROR — *"Linear solver did not converge"*, rc≠0, no result |
| **· mesh-converged** | the measured VALUE stops moving as `size_factor` falls | a property of a SERIES. Its failure is a RESULT, not an error: every solve succeeded and the numbers still disagree |
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


## SYMBOLS — three disciplines, one alphabet

This programme sits on **microwave engineering**, **plasma physics** and
**Bessel-function analysis** at once, and they collide on the same letters. A
reader arriving from one of them will silently mis-read the others. What each
symbol means HERE, and what it means to someone who does not work here:

🔑 **CANONICAL NAME is the left column, and it is the `baselines.json`
identifier — CONVENTIONS §0. Use it in prose, comments and docs, not just
in code. A Greek letter alone is not a name: this record contains TWO
different betas (see the `mode.beta_z` row).

| canonical name | symbol | **HERE it means** | elsewhere it commonly means | risk |
|---|---|---|---|---|
| `mode.beta_z` | **β** | **axial propagation constant**, pi/L, in `mode.beta_z`/`mode.k_c` | — | 🔴 **an INTERNAL collision**: KNOWN.md:1400 and cad/README.md:43 write β for THIS, everything else means coupling |
| `coupling.beta` | **β** | **coupling coefficient, Q₀/Q_ext** | **plasma β** — ratio of plasma to magnetic pressure; also phase constant, or v/c | 🔴 **worst.** 71 uses. A plasma physicist reads every one of them wrong |
| `plasma.collision_frequency` | **ν** | **electron–neutral collision frequency** (rad/s) | **frequency itself** in spectroscopy (ν in Hz) — and this instrument IS a spectrometer | 🔴 severe. `ν = 6.5ω` is a ratio of two *frequencies*, not a tautology |
| `bessel.chi_prime_01` | **χ** | **Bessel root** — χ′₀₁, χ₁₁ = 3.8317 | electric **susceptibility** (and we use ε beside it) | ⚠️ real |
| `wall.conductivity.s_per_m` | **σ** | **electrical conductivity** (S/m) | **cross-section** in plasma/atomic physics; stress in mechanics | ⚠️ real |
| `torch.sapphire.permittivity` | **ε** | **relative permittivity** | numerical **tolerance**; also strain | ⚠️ 202 uses; context usually disambiguates |
| `cavity.Q0.cold` / `cavity.Q_ext.cold` | **Q** | **quality factor** (Q₀, Q_L, Q_ext) | charge; heat | low |
| *derived from* `source.f0.ghz` | **λ** | **wavelength** — c/f0 = 122.36 mm | eigenvalue in numerics | ✅ **symbol retired 2026-09-03**: prose now writes `wavelength`; λ survives only in git history |
| `eta.reference` | **η** | **efficiency**, referenced to a stated Q₀ | viscosity; intrinsic impedance η₀ | ⚠️ η₀ *is* used for the coax formula |

- ⚠️ **`size_factor` IS NOT A GEOMETRY SCALE.** It is gmsh's
  `Mesh.MeshSizeFactor`, an element-size multiplier on a FIXED cavity. The
  cavity is sized by `cavity.d_over_l`. The name misleads because it appears
  beside `--radius` and `--length` in the same argument list. *(User asked
  exactly this on 2026-09-04: "the cavity was sized according to D/L, so I'm not
  sure what we're trying to answer by scaling the size factor.")*
  🔑 **What a size_factor sweep answers:** whether a number is physics or
  discretisation. The cavity cannot change, so any movement is numerical error —
  which is how coupling.beta.loaded was found to be ~21 % mesh artefact.

🔑 **RULES**
- **Never write a bare β.** Say *coupling* β, or write Q₀/Q_ext. The saving is
  two words; the cost of the collision is a reader who trusts the wrong number.
- **Never write a bare ν.** Say *collision* ν, or ν_coll. In a document that
  also discusses emission spectra, ν alone is genuinely ambiguous.
- **State the reference with η**, which § Q AND η already requires — the same
  discipline, applied to a symbol rather than a term.
- 🔴 **Never write `λ` or `lambda` — write `wavelength`.** User, 2026-09-03:
  *"just use wavelength instead of lambda/λ"*. This symbol was a THREE-way
  collision, which is why it is the one spelled out rather than disambiguated:
  the **wavelength**, the **eigenvalue** of a shift-invert transform
  (`INSTRUMENT.md`, `h3_ladder`), and **Python's `lambda` keyword** — 169 live
  expressions in this directory, against 96 prose uses. Nothing distinguished
  them but context. The eigenvalue sites now say *eigenvalue*; the keyword is
  untouched; `wavelength` means the wavelength and nothing else.
  ⚠️ **`λ₀` became "(free-space wavelength)"**, not `wavelength_0` — the
  subscript carried meaning that a bare rename would have dropped.

⚠️ **AND THE ALPHABET ITSELF IS AMBIGUOUS.** The record writes both `ε` and
`eps`, `λ` and `lambda`, `ω` and `omega`, `χ` and `chi`. **A search for one form
misses the other.** That is not hypothetical: R4's diagnosis of eps-near-zero
conditioning stayed hidden through a whole afternoon's debugging because R4
spells it with a Greek epsilon and the search used ASCII.
➡️ `ops/priorart.sh` transliterates both ways. Use it rather than a bare grep.
✅ **Repaired 2026-09-03** — it covered only eps/lambda/omega/beta/chi, so
`eta`/`η`, `Q0`/`Q₀` and `f0`/`f₀` still returned *different* result sets, and
with no word boundaries `s/chi/χ/` turned **`machine` into `maχne`**. All nine
pairs (ε η ν σ λ ω β χ and the ₀ subscripts) now return identical sets.
