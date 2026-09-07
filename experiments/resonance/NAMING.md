# NAMING — audit and repair plan

**One quantity, one name, and it is the `baselines.json` name.** CONVENTIONS §0
states the rule; this file is the audit behind it and the plan to finish it.

Written 2026-09-03 after `coupling.beta` was retrofitted (346 renames). The
survey below is measured, not estimated — `ops/priorart.sh` and the audit script
in this file's history produced the counts.

---

## The problem is TWO problems, and they need different treatment

| | **A — AMBIGUITY** | **B — VARIANCE** |
|---|---|---|
| what | one name, **two quantities** | one quantity, **many spellings** |
| example | `β` = Q0/Q_ext **and** `β` = pi/L | `Q₀` / `Q0` / `Q_0` |
| harm | a reader takes the **wrong number** | search misses; attention splits |
| risk | 🔴 corrupts conclusions | ⚠️ costs time |
| fix | **must** disambiguate, needs an audit first | normalise; mechanical |

🔴 **Never sweep a type-A name without auditing first.** The `coupling.beta`
retrofit would have destroyed the `mode.beta_z` derivation in KNOWN.md and
cad/README.md; the audit caught 5 instances before the edit, not after.

---

## A — AMBIGUITIES (must fix)

| symbol | meaning 1 | meaning 2 | status |
|---|---|---|---|
| **β** | `coupling.beta` = Q0/Q_ext | `mode.beta_z` = pi/L, in `mode.beta_z`/`mode.k_c` | ✅ **DONE** 2026-09-03 — 346 renamed, 5 protected |
| **σ** | `wall.conductivity.s_per_m` / `loop.conductivity.s_per_m`, **S/m** | `MOMENTUM_CROSS_SECTION_M2`, **m²** — *and* `std_dev_mhz` in evaluate.py, **MHz**. THREE meanings | ✅ **DONE** 2026-09-03 — renamed in physics.py and evaluate.py; `plasma_state` output unchanged |
| **χ / x** | `bessel.chi_prime_01` = 3.8317 | *same quantity, two LETTERS*: `χ′₀₁` (14) and `x'₀₁` (3) | 🔴 **OPEN** — strictly type B, but a letter change reads as a different symbol |
| **η** | `eta.reference`, efficiency | intrinsic impedance η₀ — **searched, NOT used here** | ✅ no collision |
| **ν** | `plasma.collision_frequency` | spectral frequency — **searched, NOT used here** | ✅ no collision, but see CONVENTIONS §0: this instrument IS a spectrometer, so it could arrive later |

## B — VARIANCE (normalise progressively)

Counts across 118 files, .md and .py:

    torch.sapphire.permittivity   eps(228)  ε(161)  permittivit(44)  9.39(26)
    wall.conductivity.s_per_m     sigma(177) σ(88)  conductivit(81)  3.5e7(24)
    eta.reference                 eta(162)  η(148)  efficiency(14)
    cavity.Q_ext                  Q_ext(529) external Q(2)  Qext(2)
    cavity.Q0.cold                Q0(352)   Q₀(279) unloaded Q(1)
    source.f0.ghz                 f0(256)   f₀(149)
    source.lambda.mm              lambda(214) λ(49)
    plasma.collision_frequency    nu(23)    ν(16)

⚠️ **These counts CONFLATE code and prose.** `sigma`/`eps` are largely Python
identifiers and are legitimate there — see the transformation rule below.

---

## The code/prose transformation

`baselines.json` keys are dotted; Python identifiers cannot be. **The rule is a
defined transformation, not a second vocabulary:**

    baselines.json   wall.conductivity.s_per_m
    Python           wall_conductivity_s_per_m        dots -> underscores
    prose/comments   `wall.conductivity.s_per_m`      the dotted form, verbatim

A local alias is allowed where it aids readability, but **it must be introduced
by assignment from the canonical name**, so the link is greppable:

    sigma_w = values.get("wall.conductivity.s_per_m")     ✅ traceable
    sigma_w = 3.5e7                                        🔴 a second source of truth

---

## Repair order — by RISK, not by count

1. ✅ **`coupling.beta`** — done.
2. 🔴 **`σ` cross-section vs conductivity.** Small (SIGMA_M and its uses in
   `physics.py`), high value: rename to `plasma.momentum_cross_section.m2` and
   add it to `baselines.json` with its ORDER-ONLY status, which the code comment
   already states.
3. ✅ **`x'₀₁` -> `χ′₀₁`** — DONE 2026-09-03, 3 instances.
4. ⚠️ **Greek -> ASCII in prose for searchability**, per quantity, highest count
   first: `ε`, `η`, `Q₀`, `f₀`, `λ`. Mechanical, but see the guardrails.
5. ⚠️ **Code aliases** — audit for `= <literal>` where a canonical value exists
   (rule 2 above). This is CONVENTIONS §2 applied to names.

---

## Guardrails, each learned by breaking it

  - 🔴 **Audit for type-A collisions BEFORE any sweep.** `β/k_c` survived only
    because it was searched for first.
  - 🔴 **Quotations are verbatim, and they SPAN LINES.** Protect on the
    ATTRIBUTION (`User:`, `>`), carried while the quote is open. A state machine
    on `*"` does NOT work: `**"text"**` matches the same opener and wedges the
    tracker, which silently under-renamed 29 OPTIMIZER rows and looked like
    success.
  - 🔴 **Dry-run, print samples, then apply.** Every stage above ends with a
    post-check that counts what should now be zero.
  - ✅ **Renaming is not rewriting.** Append-over-rewrite protects RESULTS.
    Changing what a quantity is CALLED does not change what a superseded claim
    SAID — and leaving two names for it makes that claim harder to read.
  - ⚠️ **Do not invent a name when one exists.** `cond_sigma` was invented on
    2026-09-03 while `wall.conductivity.s_per_m` was already canonical — a NEW
    inconsistency created while fixing an old one.


---

## Found BY the audit, but not a naming defect

- 🔴 **Two sources of truth for the collision frequency.** `h3_loaded.NU_M =
  1.0e11` (hardcoded, used by `drude()` for every plasma solve) versus
  `physics.plasma_state` deriving 6.295e10. 1.59x apart, moving the eps = 0
  threshold by 2.44x. See NEXT.md. This is CONVENTIONS §2, surfaced by chasing a
  name — which is the argument for doing the audit at all.

---

## Item 5 — code aliases. DONE 2026-09-03. Four defects, one of them inverted.

Method: every numeric literal in a `.py` assignment, matched against every value
in `baselines.json`. Deliberate sweep lists (`e0q_wallloss.SIGMAS`) excluded.

1. 🔴 **`geometry.py` labelled the correct value "custom" and the WRONG value
   "SAPPHIRE".** The mesh binds `torch_eps` from baselines (**9.39**, eps_PERP_c
   — the axis TE011 sees), then the printed label tested `abs(eps - 11.6) < 0.3`
   against a *literal* of eps_PARALLEL_c. So every correctly-built mesh announced
   `torch: custom`, and a mesh built on the wrong axis would have announced
   `SAPPHIRE`. **Measurement right, label inverted** — precisely the split the
   "measurement vs evaluation" rule exists for. Both label constants now bind.
   ✅ The tentative-value guard then fail-closed on `torch.quartz.permittivity`
   (TENTATIVE) at mesh time, catching a regression *inside this repair*. The
   call site now passes `allow_tentative=True` and says why: it is a LABEL, and
   is never meshed from.
2. 🔴 **`wall.conductivity.s_per_m` copied, not bound**, in `h1_aspect`,
   `h2_groove`, `h2b_groovescale`. `h1_aspect` read
   `SIGMA = 3.5e7  # aluminium, as declared in baselines.json` — **a comment
   asserting the link in place of making it**, which is the failure mode in its
   purest form. `h2_groove` binds `cavity.d_over_l` seven lines above. All three
   now bind. Numerically identical (3.5e7 IS canonical); no result moves.
3. ⚠️ **`e3_closure` wrote `plasma_state(5245.0)`** beside `T_GAS_ANCHOR_K =
   (5220, 5270)`, whose midpoint it is. Now `sum(ph.T_GAS_ANCHOR_K) / 2.0`.
4. 🔴 **`NU_M` / `drude()`** — see below; repaired without moving any number.

## Item 4 — Greek/ASCII in prose. REJECTED as specified, and the tool repaired.

**The plan was wrong on its own evidence, and the guardrail caught it.**

- 🔴 **The count that motivated the sweep was contaminated.** It read
  `lambda(214) λ(49)` and concluded ASCII wins. **168 of those 214 are Python's
  `lambda` keyword.** Genuine wavelength usage is 51 ASCII vs 54 Greek — the
  opposite direction. A sweep would have merged the wavelength into 168 lambda
  expressions and made it permanently ungreppable, *while claiming to improve
  searchability*.
- 🔎 **PRIOR ART, found before sweeping:** GLOSSARY § already diagnoses the
  alphabet ambiguity (it cost an afternoon on R4's eps-near-zero conditioning)
  and adopts a **tooling** answer — `ops/priorart.sh` transliterates both ways.
  A prose rewrite would have re-solved a solved problem, destructively.
- ➡️ **So the repair is the tool, not 758 lines of prose.** Two real defects in
  `ops/priorart.sh`, both silent:
  - **`η`, `ν`, `σ` and the `₀` subscripts were absent from the table**, so
    `eta`/`η`, `Q0`/`Q₀`, `f0`/`f₀` each returned *different* result sets.
  - **No word boundaries**: `s/chi/χ/` rewrote **`machine` → `maχne`**. A search
    for "machine" searched a string that cannot exist — the exact silent miss
    this tool was built to prevent, living inside the tool.
  - ✅ Post-check: all nine pairs (eps ε · eta η · Q0 Q₀ · f0 f₀ · lambda λ ·
    sigma σ · nu ν · beta β · chi χ) now return identical result sets.

🔑 **The transferable rule: a count that motivates a rewrite must be
decontaminated before it is trusted.** `lambda` is a keyword; `eta` hides in
`beta`/`meta`/`theta`; `chi` hides in `machine`. Bare frequency counts over a
mixed corpus are evidence about strings, not about usage.

## Also repaired: the linter was reporting a false ERROR on every run

`preflight.py` flagged `TAG_LOOP = 92` in `geometry.py` as "a geometry dimension
hardcoded" — it matched the geometry pattern on **`LOOP`** with `abs(v) > 0`,
though a gmsh physical-group id is categorically not a measurement. `TAG_GROOVE`
had hit the identical false positive and been silenced by **grandfathering** it,
which is the wrong direction for a ratchet documented as may-only-shrink, and it
left a standing 🔴 in the programme's most-read file — the reliable way to train
a reader to skim past linter output.

✅ Fixed structurally (`TAG_<NAME>` holding a small positive integer is exempt),
and the `geometry.py` grandfather row **removed** — the ratchet shrank.
Verified: still fires on a real `GROOVE_W = 5.0`, all six rules still
discriminate, **0 errors across all 91 rigs.**

## Item 4, second pass — λ/`lambda` RENAMED TO `wavelength` (user directive)

> User, 2026-09-03: *"just use wavelength instead of lambda/λ"*

This resolves what the audit had only diagnosed. The word is written out rather
than normalised to one of the two symbols, which is the right answer because the
symbol was a **three-way** collision, not a two-way one:

| sense | where | count | action |
|---|---|---:|---|
| **wavelength** | prose, comments, docstrings | 96 | ➡️ `wavelength` |
| **Python `lambda`** | live expressions | 169 | untouched |
| **eigenvalue** (shift-invert) | `INSTRUMENT.md`, `h3_ladder` | 2 | ➡️ `eigenvalue` |

**How the keyword was kept out of it.** The `.py` pass edited only `COMMENT` and
`STRING` tokens, never `NAME`, and skipped any occurrence preceded by `key=` or
followed by `<args>:` — so quoted code inside comments (`eigmodes.py:123`,
`preflight.py:618`, the regex at `preflight.py:178`) survives verbatim.

🔴 **A token filter is not enough on Python 3.12.** f-string literal text
tokenizes as `FSTRING_MIDDLE`, not `STRING`, so the first pass silently skipped
9 sites — `λ/4` inside `print(f"...")`. They were caught only because the
post-check counted what should have been zero and found 3, then 6 more. **The
post-check is what worked here, not the filter.**

Also done: identifiers (`LAMBDA`/`LAM` → `WAVELENGTH`, `over_lambda` →
`over_wavelength`, `lambda_mm` → `wavelength_mm`, 20 refs); `λ₀` →
"(free-space wavelength)", since the subscript meant free-space and a bare
rename would have dropped it; and three printed tables whose **header labels
outgrew their field widths** — header and data widths moved together, or the
columns would have sheared.

✅ `ops/priorart.sh` now treats `wavelength`/`lambda`/`λ` as one three-way group,
verified to return identical result sets. Without that, **the rename would
itself have become the search failure the tool exists to prevent**, because git
history and every prior document still carry the symbol.

⚠️ **`source.lambda.mm` was a PHANTOM key** — documented in GLOSSARY as
canonical, never present in `baselines.json`. The wavelength is *derived* from
`source.f0.ghz` (c/f0 = 122.36 mm), not anchored, so the row now says so instead
of naming a key that never existed.
