# Provenance audit — 2026-08-17

**Question asked of every fixed parameter:** which finding set it, is that finding
still standing, and does the parameter survive?

Scope: all 57 entries of `baselines.json`, plus the design table in
`amip/README.md`. Method: each entry carries a provenance string naming its
source finding; that finding was checked against the current state of the record.

**This is a working artifact, not a findings entry.** It is regenerated, not
appended to. `FINDINGS.md` remains the evidence trail.

## Verdicts used

| | |
|---|---|
| ✅ **VALID** | measurement sound, justification intact |
| 🔶 **WEAKENED** | the number is right; the *reason it was chosen* has been undercut |
| ⚠️ **PROVISIONAL** | contingent on an open question, most often R62 |
| 🔴 **ORPHANED** | the argument that created it has been withdrawn |
| 🔁 **RE-DERIVE** | needs re-measurement before use |

---

## 1. The headline

🔴 **The design point's frequency target was computed with an offset that was
7.06 MHz wrong.** `cav.length_sapphire` and `cav.length_quartz` were chosen to
place TE₀₁₁ at 2.4487 GHz using the **+31.6 MHz** order-1 offset. R38 measured
that offset at **+24.54**. The lengths are still what they are and entry 79
concluded no retune is *needed* — both binding constraints still hold — but
**the lengths were selected against a target that was never where it was thought
to be.** They are not wrong; they are unjustified at their stated precision.

⚠️ **R62 makes most of the geometry provisional.** R56 showed the lit cavity
absorbs 5–6% and the deficit is coupler strength (52×), not size. If the feed
architecture changes, the design point moves and every geometric parameter is
re-opened. **34 of 57 entries are contingent on R62.**

🔶 **The TM₀₂₀ band-floor constraint is a second layer, not a primary one.** R60
measured 18.3 dB of suppression at the operational tilt. Everything whose
*justification* is "protect TM₀₂₀'s headroom" is weakened — including the
tightest number on the drawing.

---

## 2. Parameters whose justification changed

| parameter | set by | what happened | verdict |
|---|---|---|---|
| `cav.length_sapphire` 88.12 | R44/R46 | target frequency used the **wrong +31.6 offset** | 🔶 value stands, target did not exist |
| `cav.length_quartz` 88.53 | R46 | same | 🔶 same |
| `cav.radius` 103.70 **±0.2** | R44, entry 74 | tolerance set by **TM₀₂₀ headroom**, which R60 downgraded to a second layer | 🔶 value ✅, tolerance over-tight |
| `tm020.headroom` 6.0 MHz | R29+R49 arithmetic | built on the floor being binding | 🔶 |
| `effect.chimney_tm020` 1.26 | R29 | measurement ✅; its *significance* depends on the floor | ✅ measured, 🔶 in use |
| `effect.feed_tm020` 2.70 | R49 | same | ✅ measured, 🔶 in use |
| `chimney.length` 41 mm | entry 53 | sized for 60 dB from a **TE₁₁ decay rate that R48 showed is not the coupling channel**; leakage never measured | 🔶 basis unverified |
| `feed.length` 41 mm | R49 | isolation **bounded, not measured** — the 10 mm control failed to move | 🔶 (R51) |
| `brake.thickness` 3.0 | R39 | R54 says a groove beats it on every measure; R54 itself provisional | ⚠️ |
| `wall.conductivity` 6.3e7 | Q optimisation | R58: Q is 0.7% of lit dissipation; **optics should decide the surface** | ⚠️ |
| `wall.q_derate_roughness` 0.82 | Hammerstad + silver | falls with the material decision | ⚠️ |
| `plasma.sigma` 30 | `r12.py` | a **model value never validated** against a real N₂ MIP; R56 shows conclusions depend strongly on it | 🔶 assumption |
| `plasma.region` toroid | `r12.py` | assumed shape, never validated | 🔶 assumption |
| `plasma.q_loaded` 320 | R15 | converged ✅ but measured at the **45° diagnostic tilt**; no 0° value exists at σ=30 | 🔶 tilt-unmeasured |
| `groove.*` (4 entries) | R54/R54b | verdict provisional pending R62 | ⚠️ |

## 3. Parameters that survive unchanged

✅ `cav.shim` 0.41 (both lengths move together) · `cav.roundness` 0.5 (R36; even
freer if the floor is not binding) · `chimney.diameter` 21 · `torch.od` 20 ·
`mesh.size_factor` · `mesh.order` · `offset.te011` **+24.54** and `offset.tm020`
**+20.06** (for *this* geometry — R38 flags them geometry-dependent) · the six
`te011/tm020` f and Q entries (pinned to `choff.msh`) · all four `sens.*` ·
`effect.chimney_te011` · `effect.feed_te011_q` · `te011.q_ext` 16,568 ·
`tm111.f_filtered` / `f_unfiltered` / `identification` ·
`effect.filter_te011_tm111_separation` 45 MHz · `te011.azimuthal_floor` ·
`te011.m2_contamination_unfiltered` 8.5 · `loop.tilt_operational` ·
`effect.tm020_tilt_suppression` 18.3 · `match.*` · all five `reproducibility.*` ·
the two honest nulls (`plasma.f_loaded`, `effect.tm111_tilt_anomaly`,
`groove.pole_depth`).

🔑 **The measurement layer is in good shape. The justification layer is not.**
Almost every ✅ is a *measured* quantity; almost every 🔶 is a *chosen* one.

## 4. Nothing is fully orphaned — but one comes close

`brake.thickness` exists to keep TM₀₂₀ out of band (R39's stated decisive job).
With the floor downgraded to a second layer *and* a groove that outperforms it,
its remaining justification is the **TE₀₁₁/TM₁₁₁ separation** measured in R47 —
which is a different argument from the one that put it on the drawing.

## 5. Work list

| | action | blocked by |
|---|---|---|
| **A1** | Re-derive `cav.length_*` against the corrected +24.54 offset, or record explicitly that the length is retained and the target restated | — |
| **A2** | Re-derive `cav.radius` tolerance with TM₀₂₀ as a second layer. Current ±0.2 may be several times tighter than needed | — |
| **A3** | Restate `brake.thickness`'s justification as TE₀₁₁/TM₁₁₁ separation, not TM₀₂₀ position | — |
| **A4** | Measure `plasma.q_loaded` at 0° tilt at σ=30 | harness |
| **A5** | Validate `plasma.sigma` and `plasma.region` against literature for an atmospheric N₂ MIP — the only assumptions in the file with no measurement behind them | external |
| **A6** | Measure chimney and feed **leakage** with a port, replacing the unverified 60 dB basis | harness |
| **A7** | Hold all ⚠️ pending **R62** | R62 |

## 6. What this means for the refactor

- **The regression suite should be built from the ✅ set only.** Pinning a 🔶 or ⚠️
  value makes a contingent choice look authoritative — the failure this audit
  exists to prevent.
- **`offset.*` must be a first-class, re-measurable quantity**, not a constant.
  It is geometry-dependent, it was wrong for the life of the project, and it is
  the single most load-bearing number in the file.
- **Dead-code check before porting — CHECKED 2026-08-17, and the first draft of
  this line was half wrong:**
  - `--striker` is **genuinely dead**, but on *measurement*, not architecture:
    ~1.00× enhancement on three geometries, because the enhancement decays over
    ~r_tip and the torch wall holds metal 4 mm away. It is in the README's
    do-not-re-attempt list and only `striker-ab.py` — the driver that killed it —
    references it. **Do not port.**
  - `--electrode` is **LIVE**. It is the design's current ignition mechanism
    (README: "capacitive electrode recessed at an end cap, −0.41% of Q"). R21
    showed it is a shorted turn to TE₀₁₁'s azimuthal E, so recessing it where
    E_φ → 0 makes it nearly free. It never depended on TM₀₂₀, so mode-shift's
    surrender does not touch it. **Port it.**
- **Every ⚠️ is a case-file input, not a hardcoded default** — the whole point of
  the JSON-driven design, and R62 is the reason it matters.
