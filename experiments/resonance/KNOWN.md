# KNOWN — what this programme has actually established

**One page. If it is not here, it is not established.**

### 📁 THE DOCUMENT SET — all of it, so none is missed again

| file | what it is | status |
|---|---|---|
| **`KNOWN.md`** | this — what is established | **read first** |
| **`PLAN.md`** | 🔑 **the FIXED experiment list, E0–E4. "It does not grow."** Each with V and F declared before any driver. Has a *Parked* section for surprises that **do not spawn runs** | **authority on what experiments EXIST**; some status lines stale (E1 was deleted 2026-08-21) |
| `NEXT.md` | the queue only, no measurements | current |
| `CONVENTIONS.md` | recurring errors + corrected approach | current |
| `HYPOTHESES.md` | H0–H5, the working question set | current |
| `INSTRUMENT.md` | what gmsh+Palace can and cannot tell us | current |
| `OPTIMIZER.md` | priors for the eventual multi-variable optimisation | current |
| `METHODOLOGY.md` | tool-specific lessons, each paid for with a wrong answer | rev 4, 2026-08-20 |
| `DEPLOY.md` | running the programme on a rented machine | 2026-08-21 |
| `README.md` | the rules, and why the previous programme was abandoned | 2026-08-20 |

⚠️ **`FINDINGS.md` was REMOVED from the working tree 2026-08-23** so it stops
confusing sessions. It is in git and retrievable:

    git -C axisymmetric-mip show ba740d6:experiments/resonance/FINDINGS.md

Retrieve it only to follow a citation. It is 5,300 lines, three invalidated
eras, and it is not where you find out what is true.

⚠️ **Two numbering systems.** `PLAN.md` uses **E0–E4** (experiments, fixed).
`HYPOTHESES.md` uses **H0–H5** (questions, evolving). They are not the same
axis and neither supersedes the other.

Every entry names **what it is anchored to outside the programme.** A result
supported only by another result of this programme is not listed — that is the
inward-facing loop that ended the previous programme (`README.md`).

---

## ✅ E0 — the instrument
**Anchor: closed-form cavity mathematics.**

- Geometric order 2 **and** solver order 2. They are different discretisations;
  conflating them cost a full invalidation.
- TE011 within **0.058 MHz** of closed form. Differential work ~20 kHz; mesher
  jitter 8 kHz.
- **Q ∝ σ^0.5** to four decimals, across a decade of σ, all 14 modes.
- Bare TE011 **Q₀ = 44,384** at aluminium 3.5e7 (empty, **no loop, no groove**).
  ⚠️ With a coupling loop the reference is **29,854**, not 44,384.
- Cost model `t ≈ 454 ns × ND_dofs × KSP_its`, ±15%, at 32 ranks / order 2.

## ✅ H1 — the cavity
**Anchor: an analytic max-min optimum over D/L.**

- **D/L = 1.525, a = 88.0045 mm, L = 115.4158 mm.**
- Nearest rival TE112 at **332.7 MHz** — a stationary point of the max-min, so
  tolerance-insensitive. Neither original candidate.
- ⚠️ **Poles to avoid**: TM012 crosses TE011 at D/L = 1.096440.

## ✅ H2 — the mode filter · **ANSWERED**
**Anchor: the LDMOS tuning range — a hardware constraint outside the programme.**

- **Annular groove, frozen at 5 × 10 mm** (width × depth), both end caps.
- Mechanism: TE011's cap current is **azimuthal** and runs parallel to the slot;
  every TM mode has a **radial** component the slot cuts.
- Cold, measured: TM111 **−64.25 MHz**, TE011 moves **14 kHz**, Q cost **0.3%**.
- 🔑 **SUFFICIENCY IS ESTABLISHED, not deferred:** 64.25 MHz **clears the 50 MHz
  LDMOS band**. That is why the dimensions were not optimised further — 5 × 10
  puts every competitor out of the tuner's reach, so refining it buys nothing.
- 🔴 **λ/4 = 30.59 mm is the depth to AVOID** — the slot resonates and Q
  collapses to ~3,000.
- ⚠️ An annular filter is **blind to m**.

## ✅ TE011's field structure
**Anchor: closed form, and it reproduces a ratio the code independently uses.**

- E is a **torus at r = 0.4805a**, zero on axis and zero at the wall.
- H_z max at mid-plane, zero at the caps; H_r max at the caps, zero at
  mid-plane, peaking radially at 0.4805a.
- Only ~0.1% of TE011's energy sits in an 8.5 mm bore.

---

## 🔴 NOT ESTABLISHED — do not quote

- **All non-groove H3/H6 work (2026-08-23).** η(ne), the +31.6 MHz loaded pull,
  loaded Q₀, the 78% suppression law, sapphire's loaded point, β vs loop area.
  Measured on a cavity with **no mode filter**; the design has one. The cavity
  was wrong, so the mode landscape was wrong, and every one of those results is
  *about* the mode landscape.
- **"Net into plasma" figures.** A product of a β whose coupling branch is
  unresolved (|S11| cannot distinguish β from 1/β), an η referenced to the
  **no-loop** 44,384 instead of the with-loop 29,854, one-sided linewidths, and
  in places a mode whose identity the rig itself flagged. **Stop quoting these.**
- **β and Q_ext.** β is not mesh-converged (43% for a 1.25× refinement); Q_ext
  is not transferable between meshes.
- **The 2.44 GHz TM-like mode.** Real in the ungrooved cavity and removed by the
  groove — but characterised only in the wrong cavity.

## 🔑 KEPT FROM 2026-08-23 — and only the part that is not cavity-dependent

⚠️ **Even the instrument gains need splitting.** A method claim and a cavity
claim often sit in one sentence. INSTRUMENT now marks which is which; five of
its sections carry a GROOVE-FREE re-check banner.

**Survives** (arithmetic or circuit theory, independent of which modes exist):
driven sweep cost ∝ Q; η robust where Q₀ is not; |S11| cannot distinguish β from
1/β; band-vs-step sizing; continuation needs a seed measured in-regime; a guard
on fit QUALITY cannot detect a fit of the WRONG THING.

**Does NOT survive without re-checking** (claims about mode behaviour in a cavity
whose modes the filter changes): the ~176 mm² mode-identity threshold — its
source rig `e0k2_sizeq` was groove-free and TE011/TM111 are EXACTLY degenerate
ungrooved, so it may be an artifact of a degeneracy the design removes; the
ε-contrast convergence envelope; the 2.6232 GHz competitor; the 12→0 eigen/driven
timeout comparison; every β, Q_ext and delivered-power figure; `h4_field`'s
dielectric shifts.

## 🔑 The old note, kept for the numbers

Driven replaces eigen for loaded work: **12 eigen timeouts / 3 h wasted → 0
across 17 driven cases.** Cost ∝ Q, so driven is cheapest exactly where eigen
fails. Full method in INSTRUMENT's "loaded-cavity toolkit".
⚠️ This is an inward gain. It answered no question about the machine.

---

**Next steps live in `NEXT.md`.** This file says what is known; that one says
what to do. Keeping them apart is the point — one document with both jobs is how
`FINDINGS.md` became unreadable.
