# Conventions

**Read this at the start of every session.** These are not style preferences.
Each one is a mistake that was actually made here, usually more than once, and
several were made again within hours of being written down.

Sorted by pattern, because the same shapes keep recurring in new clothes.

---

## 1. Never infer state from a proxy. Ask the direct question.

This is the single most repeated error. Four instances in one session:

| proxy used | what it got wrong | direct question |
|---|---|---|
| Palace ranks = "busy" | `ops/go` nearly synced code into a live meshing run — rigs spend most of their life meshing with **zero** ranks | is the RIG process alive? |
| log growing = "alive" | the waiter declared a healthy E1b dead; gmsh meshes silently for minutes | is the rig's own `python3` running? |
| elapsed time = "solved" | `MIN_SECONDS=30` discarded a correct 5 s solve; the threshold was calibrated on hardware we no longer use | did it PRODUCE non-empty output? |
| frequency proximity = "which mode" | E1b failed three times; then H2b rebuilt the identical bug hours after the lesson was written | match by Q, multiplicity, or continuation |

🔑 **The sharpest form of this: a nearest-neighbour answer is only trustworthy
if what it found is NEARER than the edge of the region that was searched.**
Otherwise "nearest" is an artifact of where you stopped looking. H2b asked for
the mode nearest 2.45 GHz in a solve whose window began at 2.40, while the groove
had pushed that mode down to 2.387 — outside. The function returned a confident
2.606, a real mode of a different kind that even had a plausible Q ratio (0.472
against TM111's 0.456). Every guard passed. H2 had measured the same geometry
correctly, months of reasoning apart, only because it searched from 1.05.

And it is a BALL, not a side: the false candidate sat 156 MHz ABOVE the target
where the window ran 343 MHz, while the real mode was 63 MHz BELOW where it ran
only 50. Checking the side the candidate happens to lie on passes the bad case.

**And do not re-derive what something already knows.** `h1_aspect` re-searched
for the TM111 pair by frequency after `te011_tm111` had already identified them;
it returned empty whenever the pair split more than 100 kHz. Return the indices.

## 2. A value must reach the thing that consumes it

*"A baseline nobody reads is a claim, not a fact."*

- **R101** — `--torch-material` fed mesh sizing and the sidecar, never the
  solver. Two meshes with identical byte counts were the only tell.
- **R110** — aluminium adopted and written to `baselines.json`; the template
  kept **silver**, so every absolute Q in the record was 34% high.
- **solver order** — `eigen_cfg` hardcoded `Order: 1`; six rigs inherited it
  silently and all their conclusions had to be invalidated.
- **E0l** — `PRIOR` merged AFTER the summary table, so every speedup printed
  `NaN`.

✅ Bind from the source of truth, **announce the value in the log**, and make a
missing declaration **refuse to run** rather than substitute a default.

⚠️ A flag set to its own default is invisible. `--n-wl 8` where 8 is the default
made E0's "coarse" mesh identical to its "fine" one, so its resolution check was
vacuous for the programme's whole life. `noopflags.py` scans for these.

## 3. Nothing is silently dropped

*"A script that drops a row makes its own criterion invisible."*

- E1b's analysis sat one indent outside the shape loop: shape A was meshed and
  solved twice, then discarded, while the run printed a confident summary.
- H2b's Q guard excluded points from a fit without saying so — written into a
  file whose own docstring claims nothing is dropped.

✅ Report the failure, the count, and the reason. Where an exclusion feeds a
derived number, print that number **both with and without**.

## 4. Killing a process means killing its tree

- `pkill -f` matched the calling shell's own argv and **killed the shell three
  times**. Never use it. Select by exact executable name, kill by PID.
- `proc.kill()` kills only the bash wrapper. The real tree is
  **`palace` (wrapper) → `prterun` → `palace-x86_64.bin` ×N**, so the ranks are
  orphaned to PPID 1 and keep running — four of them for 20 minutes.
- `reap.py` looked for ranks whose OWN parent was init and reported "no orphans"
  throughout that leak, because ranks are **never** direct children.

✅ `start_new_session=True` + `os.killpg`. `ops/stoprig.sh` does rig + tree.

## 4b. A quantity measured in another epoch was measured on another machine

Two numbers from this programme are only comparable if the thing between them
did not change. Three times now the "surprising discrepancy" was bookkeeping:

| looked like | actually was |
|---|---|
| solve cost varying 95× at fixed tet count | **4 ranks on the laptop vs 32 on the instance** |
| driven and eigen disagreeing 3.7× on frequency | **solver order 1 vs 2** |
| one loop giving β = 0.067 then β = 27.5 | **two different cavity DESIGNS** — E0k predates H1 and ran D/L 2.343, the candidate H1 rejected |

🔴 In the last of these I described it as "a factor of 410 for a 15% change in
radius" — quoting the one dimension that had moved least (the length changed
30%, the aspect ratio 35%) and thereby making a different design look like a
perturbed one. Then I set it up as a mystery to be solved before work could
continue. It was not a mystery; it was two machines.

✅ Before calling a difference surprising, list what else changed — epoch,
geometry, ranks, order, wall material, solver type — and say which of them you
have held fixed. If the answer is "none", the comparison is not a measurement.

## 5. Measure the magnitude before drawing the consequence

*"Measure the outcome, not the mechanism."*

- E0m found the mesher non-deterministic (46 µm of node motion). I wrote three
  consequences into the record — an invalidation, a repo-policy reversal, and a
  promotion of the cache to "infrastructure" — **before** measuring that it
  costs **66 Hz**. All three had to be withdrawn. The measurement took 8 minutes.
- Q_ext once turned a 21-point power gap into a "98× deficit".

## 6. Do not reuse a parameter without re-deriving it for the case

- `sf 0.96` and `target 1.05`, copied from the E0 rigs into H1, gave 110–120k
  elements and a shift-invert spanning 1.05→2.6 GHz: **over an hour per point**.
  Retargeted, the same measurement took ~2 minutes.
- **E0l's original scaling curve used a 10.7 s toy**; production solves are 106
  minutes at 1 rank. The toy said 32 ranks were 37% efficient and fan-out was
  worth 1.8×. Reality: **87% and 4%**. A benchmark 600× too small does not lose
  precision, it **inverts the answer**.
- λ/4 was predicted as the optimal groove depth. It is where the slot resonates
  and therefore the depth to **avoid** — right physics, wrong design goal.

## 7. A checker must be able to see what it checks

Three versions of one scanner, in order:

1. regex over raw text — flagged **the comment documenting the bug** as the bug
2. `preflight.code_only()` — blanks strings, and the flags ARE strings, so it
   found nothing and **printed a clean bill of health**
3. AST walk over list literals — correct

Version 2 is the dangerous one: it passed. **A checker that cannot see its
subject is worse than none, because it is believed.** Give checkers self-tests
with known-bad input — `physics.py`'s caught two hand-typed constants, and
`eigmodes.py`'s caught the Q discriminator firing on PEC noise (Q ~1e15 passes a
ratio test happily).

## 8. Land results in files, immediately

A spot reclamation killed the instance mid-run. H1, H2 and H2b wrote their result
files only after the last case, so an interrupt lost every completed case.

✅ **Checkpoint after every case**, atomically (temp file + `os.replace`), so an
interrupt during the write leaves the previous complete file.
✅ Write conclusions to FINDINGS **as they are obtained**, not at session end.
H2's table survived only because it was transcribed by hand from a log on a
machine that no longer existed.

## 9. Declare verification AND falsification before the run

This is what actually caught things. Every retraction this session came from a
criterion fixed in advance, where it could not be quietly reinterpreted:

- E1b's **sign test** caught the mode pairing twice
- E0kp's *"if the spread is comparable to 1.3–3.3 MHz"* forced a retraction I had
  already written into FINDINGS — it came back at 0.0001× the threshold
- H2's *"TE011 must barely move"* caught the λ/4 hybridisation

Prefer a falsifier that tests the **identification**, not only the physics: H1's
"TE011 Q must exceed TM111 Q" guards the tool that does the picking.

## 10. Separate the driver from the analysis

*"Drivers emit data with provenance; labels and verdicts live in a re-runnable
layer, because that layer is the one that keeps being wrong."*

Every E1b failure was in analysis, and each cost solver hours only because the
two were welded. After splitting, shape A was recovered in **0.334 s** instead of
9 minutes of re-solving, and `resplit.py` later re-scored **nine rigs** offline
after a shared bug — no re-solving either time.

✅ Rigs emit raw data + a manifest with provenance (mesh SHA, seconds, settings).
Analysis reads it. **When a result looks wrong, re-analyse before re-running.**

## 11. Two points cannot establish a scaling law

The groove's depth dependence had two points. `Z₀·tan(βd)` predicts 2.93×,
volume fraction 2.00×, measured 1.72× — below both. Two competing derivations
agreed with each other and disagreed with the data, which is only visible with
enough points to fit an exponent.

## 12. Housekeeping that has bitten

- **`.gitignore` trailing comments do nothing.** `*.msh  # 4.8 GB` is a literal
  pattern matching nothing. Verify with `git check-ignore` against real paths.
- **`grep -c` exits 1 on zero**, so `cmd || echo 0` prints twice.
- **Numeric flags: guard on `is not None`.** `if a.viewport:` made
  `--viewport 0` silently impossible once the default changed.
- **The instance address lives in `ops/env.sh`.** It was hardcoded in 29 places
  when a spot reclamation changed it.
- **Apertures default ON.** `--viewport` and `--trap` were live in E1b because
  R98 changed a default. Gate them explicitly, as `e0_solver_vs_math` does.
