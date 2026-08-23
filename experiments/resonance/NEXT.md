# Next

Read **`KNOWN.md`** first — one page, everything established, and the index of
every document. Then **`PLAN.md`** — the FIXED experiment list (E0–E4), which
**does not grow**, and whose *Parked* section is where surprises go: they are
recorded so they are not lost, and **they do not spawn runs**. Then
`CONVENTIONS.md`, then `INSTRUMENT.md` / `HYPOTHESES.md` / `OPTIMIZER.md`.
**This file is the queue only** — it holds no measurements.
⚠️ `FINDINGS.md` is the ARCHIVE. Do not read it to find out what is known.

🔴 **THIS FILE WENT STALE FOR A DAY (fixed 2026-08-23).** It sat at 2026-08-22
saying the instance was shut down and *"H3 — THE SOLE GATE, and the whole queue
now"* while H3 and H6 were both being answered. It is a FIFTH working document
and the memory index listed only four, so no session opened it. **If you add a
doc, add it to the index, or it becomes a trap.** See CONVENTIONS §8b.

## Instance

**UP.** Address in `ops/env.sh` (one line — it was hardcoded in 29 places once).
`ops/go ops/status.sh` for state; `ops/go ops/remote.sh <rig.py> 32` to launch.

**After a spot reclamation:** launch `c7a.8xlarge` **in the volume's AZ** (EBS is
AZ-scoped — the easy mistake), attach, set the address in `ops/env.sh`, then
`NOSYNC=1 ops/go ops/mount.sh`. Exercised four times.
⚠️ `mount.sh` also checks that **pyflakes is in the env** — it lives on
`/opt/amip/envs/emsim`, NOT the root filesystem, because root is wiped by every
reclamation. Without it `preflight` silently stops checking undefined names.

## WHERE 2026-08-23 LANDED

✅ **H3 ANSWERED.** TE011 sustains: η = 0.95–0.995 at the operating point.
Loaded pull **+31.6 MHz** (up), Q 44,384 → 163, linewidth 15.2 MHz, loaded
f₀ = 2.4815 GHz — in band. Third leg killing the in-band TM companion.
✅ **H6 ANSWERED (EM half)** — user-raised, and the premise I opened it on was
wrong. **η ≥ 99.1% across TWO DECADES of ne** (1e18–1e20). Mass loading is NOT a
hard EM constraint. The "collapse to 0.185" was a 2 mm SOLID-COLUMN artifact;
the annulus is 17× the plasma and does not collapse.
✅ **H4 field** — Slater holds at ε=11.6 (predicted −15.3, measured −15.00).
H1's design point survives the torch AND the plasma together.
✅ **Superposition FAILS**: the plasma SUPPRESSES a dielectric's shift by **78%**,
constant over ε 2–6, because it cuts E_elec at the tube ~75% material-independently.
✅ **Power density is a DEFINITION** (η·P/V), not a measurement — no optimum to
find; it is a FLOW question. H3's last "open" item closed with arithmetic.

## Queued, in order

🔴 **H3 IS THE PROGRAMME. It has three regimes and one cavity — H2's, with the
groove.** There is no groove-free variant; everything measured that way on
2026-08-23 is discarded, not pending.

### State of the tree (2026-08-23 cleanup)

- ✅ Design rigs now import **`GEO_DESIGN`** (groove 5×10): `h3_driven`,
  `h3_superpose`, `h3_sapphire`, `h3_loopsize`, `h3_eigen`, `h3_annular`.
  `h3_groove` deliberately keeps bare `GEO` — it toggles the groove itself.
- ✅ Groove-free results moved to **`discarded-2026-08-23-no-groove/`** with a
  README saying why. Nothing in there may be quoted.
- ✅ `FINDINGS.md` removed to git; `KNOWN.md` is the authority and indexes all
  ten documents. `METHODOLOGY.md`'s "FINDINGS wins" line updated to point at
  KNOWN.
- ✅ `CLAUDE.md` created at the REPO ROOT so a fresh session on any machine gets
  the orientation.
- ⚠️ **`loopbranch.py` is written and UNRUN** — resolves the coupling branch from
  phase. Needed before any β is quoted (item 1b).

0. ✅ **DONE — `h3_groove`.** The filter makes TE011 the mode the tuner locks to,
   at both loop sizes. Without it the tuner takes a TM-like mode at 2.44 GHz,
   which the groove moves −63.6 MHz (H2 cold: TM111 −64 MHz).
   🔴 **Unresolved**: at 28×20 TE011 moved −12.80 MHz vs +0.00 at 11×8. Either
   the groove differs under load or that mode is misidentified. Settle it in 1.

1. 🔴 **MEASUREMENT HYGIENE — before any loaded number is quoted again.**
   a. **MEASURE the η reference on the GROOVED, LOOPED mesh — PER LOOP SIZE.**
      Every loaded η on 2026-08-23 used `Q_BARE = 44,384`, the no-loop,
      no-groove value, while every driven mesh had a loop.
      🔴 **CORRECTION (caught by a fresh session, 2026-08-23): 29,854 is NOT the
      substitute.** I wrote it as though §7c's with-loop figure were the answer.
      It is itself **groove-free AND from a different loop geometry**, so it is
      wrong on both axes. There is no number to look up — **Q_bare must be
      SOLVED for each loop size on the grooved, looped mesh.**
      ⚠️ That makes 1a a solve, not a re-score, and it is why nothing else can
      be re-run first.
   b. **Resolve the coupling branch from PHASE** before reporting β.
      |S11| cannot tell β from 1/β: −11.46 dB is 0.578 OR 1.730.
      `loopbranch.py` is written and unrun.
   c. **Fix mode identification under the groove** — settle 0's −12.80 MHz.
   d. 🔑 **CLOSE THE ENERGY BALANCE — `PLAN.md` E3 declared this falsifier
      before any of this was built and it was never run:**
      **η_total = η_plasma + η_wall + η_dielectric.** If the split does not sum
      to η_total within a few percent, **the decomposition is wrong and ONLY
      η_total may be quoted.** Every "into the plasma" figure I produced was an
      undecomposed η_total wearing a decomposition's name. PLAN notes this
      already caught a factor-of-2 convention error once.
   e. Only then may delivered-power figures be quoted at all.

2. 🔑 **H3 COLD** — no discharge, gas fill. f₀, Q₀, and what a tuner sees before
   ignition. This is the acquisition point for the whole ignition sequence and
   it has never been measured with the groove.

3. 🔑 **H3 LOADED** — full plasma, in the grooved cavity. Sustained f₀, Q₀,
   delivered power at the operating point.

4. 🔑 **H3 HOT** — the trajectory between cold and loaded. Where the tuner must
   track and whether coupling holds through it. ⚠️ The groove-free data hinted
   at a coupling minimum mid-trajectory; that hint is discarded with the rest
   and the question stands on its own merits, not on that evidence.

5. **H3 LOADED + SAMPLE** — a real high-TDS matrix. The sample travels up the
   central channel (r < 2 mm), which is TE011's field null.
   ⚠️ What ne a sample actually produces is CHEMISTRY (aerosol transport,
   desolvation, atomisation) and is an H5 external input, not an EM question.

6. **P_required(ne)** — the plasma power balance. Without it the operating point
   cannot be closed: P_delivered alone does not say whether the discharge holds.

7. **H4 — ignition.** TM ignition is discarded; auxiliary/thermal-kernel is the
   adopted route. Needs H3 COLD first (the acquisition point).

8. **H5 — the optical path to LOD. TERMINAL.** Blocked on external inputs
   (spectrometer f-number, uniformity spec, coolant interlock), not simulation.

## Retired / not on the path

- **H2 (the groove)** — RETIRED `premature` 2026-08-23. Frozen at 5×10 mm; its
  variables have left the design space. What remains is MODEL VALIDATION (does
  Slater predict the shift?), a free by-product of any future grooved solve with
  `--tag-groove`. Not a hypothesis, not on the path.
- **The loop sizing sweep** — VOID. β is not mesh-converged (43% for a 1.25×
  refinement) and the sweep was built on it. Supersede with item 2, which sizes
  against a loaded Q₀ that now exists.

## Still open, recorded and not narrated

- **TE011's Q is non-monotonic in loop area** (37,525 / 29,073 / 30,020 /
  31,665, minimum near 82 mm²) while `pair_q_ratio` degrades 1.000 → 1.364. The
  loop MIXES the triplet rather than merely shifting it. May be explained by the
  port fix; check after item 1.
- **The 100–150 Td avalanche threshold is a literature figure.** Microwave
  breakdown at 1 atm is diffusion-loss and therefore geometry dependent. Verify
  before leaning on the ignition conclusion.
- **Three inherited assumptions are now marked ASSUMED in OPTIMIZER.md** and
  must not be used as priors: the 8.5 mm bore (from order-1 solving), the 20 slm
  N₂ ceiling (from MP-AES/MICAP, not optimised), and the Fassel torch geometry
  (Argon-optimised; there is no N₂ equivalent).


