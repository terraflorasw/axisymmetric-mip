# ignition-options — how does the plasma actually start?

**Opened 2026-08-25.** ⚠️ **NOT the old `experiments/ignition/`**, which was
removed in `2db1d59` and was specifically about **TM-mode ignition**. This
programme is broader and starts empty: *what are the options, and which does
this instrument use?*

🔴 **NOTHING IS MEASURED HERE.** Every line is **STATED** (from the user) ·
**DERIVED** (a consequence of measurements made elsewhere) · **ASSUMED**.

---

## Why it was opened: it became a BLOCKER, not a someday item

`../resonance/` item 7 measured the coupling loop across 9 designs and drove
Q_ext from 8,716 to 322 — a 27× lever. Then the user asked:

> ***"Is it even worth getting VSWR to 1, given the difference between cold and
> loaded coupling?"***

🔑 **That question cannot be answered without knowing how ignition happens**, and
the answer flips the loop's design target:

| | if ignition goes THROUGH the cavity | if a STRIKER lights it |
|---|---|---|
| cold coupling | 🔴 **hard constraint** | not constraining |
| right target | **minimax**, Q_ext ≈ 1,700–2,100, VSWR ~16 both states | **β = 1 loaded**, Q_ext ≈ 105 |
| steps 2b/2c | pointed the WRONG way | pointed the right way |

**DERIVED — the numbers that make it a blocker.** Cold power into the cavity at
1 kW, from measured Q₀ and Q_ext:

| loop design | VSWR cold | **cold P_in** |
|---|---:|---:|
| as built (no capacitor) | 5.0 | **556 W** |
| minimax | 16.3 | 218 W |
| gap 2.25 mm (measured) | 86.5 | 45 W |
| β = 1 loaded | 265 | 🔴 **15 W** |

🔑 **Optimising the loaded match costs 37× of the ignition power.** Whether that
matters depends entirely on whether ignition needs the cavity at all.

## The options — none evaluated, listed so the space is visible

| | option | notes |
|---|---|---|
| 1 | **Cavity-only** — drive cold and let the field break the gas down | needs the cold match to be decent, i.e. the minimax loop. **The E-field required for N₂ breakdown at 1 atm has not been computed** and may be unreachable at any VSWR |
| 2 | **Mechanical striker** — a retractable electrode | `geometry.py` already has `--striker h,r_tip,r_ring`, so the EM effect IS modellable. Moving parts near the torch |
| 3 | **Tesla coil / HV spark**, external | standard on ICP; adds an HV supply and its EMI |
| 4 | **Seed gas / easier-ionised species** at start | changes the plasma chemistry `../spectroscopy/` cares about |
| 5 | **Reduced pressure at start** | Paschen minimum is far easier; needs a pump and a pressure ramp |
| 6 | **Tuner-assisted** — re-match cold, then track to loaded | ⚠️ **this is the 400× swing `../control-loop/` already calls its hardest problem**, not a free option |
| **7** | 🔑 **TWO LOOPS** — one sized for cold, one for loaded | **STATED by the user 2026-08-25.** Breaks the constraint instead of trading against it. See below — the most promising option listed, and the only one that gives β = 1 in **both** states |

## 🔑 OPTION 7 — TWO LOOPS. The bimodal problem dissolves

**User, 2026-08-25: *"There's another option: two loops, optimized for loaded
and unloaded."*** 🔑 Every other option accepts that ONE Q_ext must serve two
states whose Q₀ differ 265×. **This one refuses the premise.**

| state | driven | idle loop | β | **VSWR** |
|---|---|---|---:|---:|
| cold | **A** (Q_ext = 27,863) | open/shorted | 1.00 | **1.0** |
| loaded | **B** (Q_ext = 105) | open/shorted | 1.00 | **1.0** |

✅ **β = 1 in BOTH states.** No tuner swing, no compromise point, no 37× loss of
ignition power. Compare the best single-loop options: minimax gives VSWR ~16 in
both, β=1-loaded gives 1.0 loaded but **265 cold**.

### 🔴 The idle port decides it — and it is a REAL failure mode

| cold, driving A, loop B... | Q₀ effective | VSWR |
|---|---:|---:|
| open or shorted | 27,863 | **1.0** |
| 🔴 **terminated in 50 Ω** | **105** | **266** |

**A terminated idle loop drains the cold cavity as fast as loop A fills it** —
worse than any single-loop design. ✅ The record already knows a shorted loop is
benign: *"a small closed ring resonant far above 2.45 GHz"*
(`../resonance/e0_solver_vs_math`).
🔑 **SO THE SWITCH IS THE COMPONENT BEING PROPOSED, not the second loop.**

⚠️ **But asymmetrically so, which helps:** during LOADED running, leaving loop A
terminated is harmless (β = 0.9962, VSWR 1.0) — its Q_ext is huge, so it drains
slowly. **Only loop B needs isolating, and only during ignition.**
🔑 **And it need never switch under power:** ignite on A → drop power → close
B → raise power. A cold-switched 1 kW coax relay is an ordinary part; a
hot-switching magnitude tuner at 40 A is not.

### ✅ SIZING — from MEASURED data, no new solve

Single-loop Q_ext vs area (`e3-closure-00_loopq`, cap mount):

| area mm² | 35 | 82 | 176 | 384 |
|---|---:|---:|---:|---:|
| **Q_ext** | 19,633 | 11,202 | **9,231** | 13,333 |

🔑 **Q_ext has a MINIMUM at 176 mm² and rises both ways** — area alone cannot go
below ~9,231, which is precisely why the series capacitor mattered.

- **Loop A (ignition), wants 27,863** — weaker than anything measured, and the
  curve rises as area falls: **~20–25 mm² should reach it.** ✅ **A small PLAIN
  loop — no series gap, no capacitor, no arcing risk.** The easy one.
- **Loop B (running), wants 105** — measured 322 at gap 2.25 mm; needs a further
  3.1×. ⚠️ The hard one, and it carries the unquantified gap field.

🔑 **The asymmetry is the point:** splitting the job lets each loop be SIMPLE in
its own regime, instead of one loop being a compromise in both.

### 🔴 What is NOT established

- **NOT BUILDABLE TODAY.** `geometry.py` has **no second loop** (0 matches) and
  `solveconf` writes exactly one `LumpedPort[0]`. This is **new OCC geometry
  plus a solver change** — the same class as "turns is not buildable" (item 7
  step 1), not a rig parameter.
- 🔴 **MODE PERTURBATION IS UNMEASURED.** Two loops at different azimuths break
  the symmetry a single loop preserves. Purity held beautifully through every
  single-loop sweep (`spread ≤ 0.0046`); **there is no evidence it survives a
  second loop**, and F2 exists for exactly this.
- ⚠️ **Two obstacles, not one.** One 176 mm² loop costs Q₀ −2.1 %; two is
  presumably ~−4 %, but that is arithmetic, not measurement.
- ⚠️ **The two-port behaviour above is DERIVED by superposition**
  (1/Q_L = 1/Q₀ + 1/Q_A + 1/Q_B). Sound, standard, and **not measured here.**

### The passive variant, noted and not analysed

Each loop is severely mismatched in the other's state (VSWR ~265 both ways), so
a splitter feeding both would route power to whichever is matched — **self
switching, no active part.** ⚠️ Costs 3 dB and the mismatched arm reflects into
the splitter. **Not analysed; recorded so it is not lost.**

⚠️ **Option 6 deserves care.** It looks like it dissolves the trade, but the
tuner is exactly what item 7 was trying to make unnecessary. Using it to fix
ignition re-imposes the component the loop work was removing.

## What's needed

| | | blocks |
|---|---|---|
| **1** | **Which option is the instrument's?** | 🔴 `../resonance/` item 7's TARGET. The measurement is done; the CHOICE is not |
| 2 | E-field for N₂ breakdown at 1 atm in the torch bore, vs what the cavity can produce cold | decides whether option 1 exists at all |
| 3 | Does ignition happen once per run, or per sample? | if per-sample, ignition reliability outranks loaded efficiency |
| 4 | Time budget for ignition | a slow ramp tolerates a poor cold match; a fast one does not |

## Rules

Inherits `../resonance/CONVENTIONS.md`.

- **§7ab** — a value chosen for convenience must never become "the operating
  point". **The loop's Q_ext is at that fork right now**: 322 was reached by
  minimising one number, and only a stated ignition strategy makes it right or
  wrong.
- **§7ac** — never mix a verified analysis with an unverified suggestion. The
  cold-power table is DERIVED from measurement; the option list is **not
  evaluated at all** and must not be read as ranked.
- **§7bm** — a bug fix that could invalidate a result means the result is
  invalid until proven otherwise. **The same applies to a changed objective:**
  steps 2b/2c are not wrong, but what they were FOR is now open.

⚠️ **Opening a directory is not a commitment to work it now** — but this one
holds a live blocker, which the other two programmes did not when they opened.
