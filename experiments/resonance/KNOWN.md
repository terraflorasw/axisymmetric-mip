# KNOWN — what this programme has actually established

**One page. If it is not here, it is not established.** `FINDINGS.md` is the
append-only archive and is 5,000 lines of which most is superseded; read it only
to follow a citation. `HYPOTHESES.md` holds open questions. This file holds
answers.

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

## 🔑 KEPT FROM 2026-08-23 — instrument, not cavity

Driven replaces eigen for loaded work: **12 eigen timeouts / 3 h wasted → 0
across 17 driven cases.** Cost ∝ Q, so driven is cheapest exactly where eigen
fails. Full method in INSTRUMENT's "loaded-cavity toolkit".
⚠️ This is an inward gain. It answered no question about the machine.

---

**Next steps live in `NEXT.md`.** This file says what is known; that one says
what to do. Keeping them apart is the point — one document with both jobs is how
`FINDINGS.md` became unreadable.
