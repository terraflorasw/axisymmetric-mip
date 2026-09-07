# VERIFY.md — re-verification from E0 under the current conventions

> User, 2026-09-03: *"We have to basically re-verify from e0 with the updated
> methodology and conventions"*

## The defect class, stated precisely

Every error found on 2026-09-03 was in the **evaluation layer**, not the
measurement layer. The solves were fine. What was wrong:

| defect | shape |
|---|---|
| `h3_driven` Q0 from `Q_EXT_EST` | a CONSTANT stood in for the measured quantity |
| `geometry.py` torch label | a LABEL keyed on a literal contradicted the bound value |
| `SIGMA = 3.5e7` in three rigs | a value COPIED instead of bound |
| `cavity.Q_ext` | a NAME without the state it was measured in |
| `h3_driven:316` torch | a hardcoded literal inside a CLI arg list |
| cold branch | the RESOLUTION lived in the log, not the artefact |

🔑 **So the re-verification is mostly NOT a re-solve.** The raw measurements —
f0, linewidths, Q_L, eigen Q pairs, mode purity — are in the artefacts. What
must be redone is what was *computed* from them, and that is free.

⚠️ This is the programme's own rule turned on itself: *drivers emit data with
provenance; labels and verdicts live in a re-runnable layer, because that layer
is the one that keeps being wrong.* The layer was re-runnable. Nobody re-ran it.

## Phase 0 — identity audit ✅ DONE 2026-09-03

`verify_identities.py`. Checks what the numbers must satisfy regardless of
physics <!-- q:ok identities, not values -->: `Q0 = Q_L(1+beta)`, `Q_ext = Q0/beta`, and `Q0_looped <= Q0_bare`.

**Result over 90 files, 188 checks: 10 failures in 3 files, ONE signature.**
Every failure reverse-solves to an implied `cavity.Q_ext.cold` = 9,231 (no_torch, eigen_pair) — the plain 11x8 CAP
loop's cold external Q, applied to cavities that are not it.

| file | worst error | cited in KNOWN.md? |
|---|---|---|
| `h3-azimload-01` | Q0 **+397 %**, and 70,353 > the bare cavity — impossible | no |
| `h3-gap2load-01` (vacuum torch, barrel + gap2 2.25, loaded) | Q0 −24 %, Q_ext 264 -> **343** | no (NEXT only) |
| `h3-lambda4-02` (vacuum torch, cap loop, COLD) | Q0 +20 %, Q_ext up to −11 % | **YES** — the wavelength/4 finding |

✅ **PILOT RE-DERIVATION: the wavelength/4 finding SURVIVES.** Corrected Q_ext
`40,861 / 33,704 / 39,982 / 40,087` still has its interior minimum at ld = 8.0.
**The conclusion stands; its numbers move by up to 17 %.** That is the expected
shape of this whole exercise — and it is why the exercise is worth doing rather
than assuming either that everything is fine or that everything is void.

## Phase 1 — extend the audit (no solver)

**120 points are currently NOT CHECKABLE** — mostly eigen results with no beta.
They need their own identities:

- eigen pair <!-- q:ok identity -->: `Q_ext = 1/(1/Q_lumped - 1/Q_pec)`, and `Q_lumped < Q_pec` always
- **mode purity present on every eigen result** — already a standing requirement;
  audit whether it is actually there, since a Q with no purity cannot be
  attributed to a mode (§ never identify TE011 by m=0 alone)
- **mesh sidecar matches the request** — groove, loop, mount, gap2, torch. The
  sidecar is the only record of what was actually built; today it is what proved
  `loop_gap2 = 2.25` was really in the mesh
- f0 grid vs interpolated, where both exist (§7bh quantisation)

## Phase 2 — repair the derivation layer, then re-run Phase 0/1

1. 🔴 `h3_driven`: derive Q0 from its OWN fitted beta, or refuse. A constant from
   another geometry standing in for the measured quantity is §2 inside the
   evaluation layer.
2. 🔴 Write the **resolved branch** into the artefact. Today `points[0].beta` is
   the undercoupled root while the summary says overcoupled; a reader taking
   `beta` from the JSON gets the wrong number.
3. ⚠️ `h3_driven:316` hardcodes `--torch-material 1.0,3.5e-05`. The design torch
   is unreachable from this rig, and preflight cannot see a literal in an args
   list. Bind it, and extend `r_hardcoded_value` to string literals in arg lists.
4. Gate on `verify_identities.py` — it exits 1, so it can refuse a workflow.

## Phase 3 — the claims ledger

For every ✅ claim in `KNOWN.md`: name its artefact, re-derive from raw stored
quantities, mark **SURVIVES / NUMBERS CHANGE / VOID**, and record which. A claim
whose artefact is missing is VOID by default — not "probably fine".

⚠️ **This is where the shorthand bites.** 174 of 236 `Q0` mentions in the record
do not say which cavity. The ledger must resolve each to a canonical key
(`cavity.Q0.cold`, `cavity.Q0.loaded`, ...) with its context, or mark it
unresolvable. That is per-site work, not a sweep.

## Phase 4 — re-solve ONLY what cannot be recovered

Expected to be small. A re-solve is justified when the raw data is missing, the
mesh was wrong (§ THE FILTER discards), or the mode attribution has no purity.
**Not** merely because a derived number changed — that is Phase 3's job, for free.

## Phase 5 — E0, the instrument, against closed form

The actual "from E0". E0 compares the solver to analytic results on a bare
cylinder, which is the only external anchor that does not descend from this
programme. Re-run it under current code and confirm the instrument still reads
true before trusting anything built on it.

---

## The rule this leaves behind

🔑 **A derived quantity must be reconstructible from the raw measurements in the
same artefact.** If `Q0` cannot be rebuilt from `Q_L` and `beta` stored beside
it, the artefact is not a measurement — it is a measurement plus an assumption,
and the assumption is invisible.

🔑 **And identity checks are free.** None of the 10 failures needed a solver, a
cluster, or an instance that survives 18 minutes. They needed one page of
arithmetic that nobody had written.
