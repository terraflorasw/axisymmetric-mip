# Scope — the dimensionless torch (R88)  ·  rev 2, correcting §1/§4

**Working artifact, regenerated not appended.** `FINDINGS.md` remains the evidence
trail. Written 2026-08-19 after the custom-torch decision removed the catalogue
constraint (entry 129).

Per entry 127 the design is dimensionless with two hard anchors: ① f₀ = 2.45 GHz
±2.04% fixing λ = 122.36 mm, and ② N₂ at 0–2 atm. The torch straddles both — its
geometry is scale-free, its gas flow is not.

---

## 1. The parameters — the Fassel torch IS already modelled

🔴 **Rev 1 of this scope claimed the three-tube geometry was not modelled. That
was wrong.** `geometry.py` builds all three tubes, and its own comment records
that the single-tube model was already found insufficient and fixed:

> *"Modelling only the outer tube was wrong in two ways. The intermediate tube
> and injector displace gas — and the injector sits ON AXIS, exactly where
> TM₀₂₀'s E_z peaks. And the plasma forms DOWNSTREAM of the intermediate tube,
> in the last 20–30 mm before the tip, not uniformly along the whole length."*

✅ **Consequence: R83 and R85's deposition results already include the full
torch and stand.**

| | mm | r/a or z/L | |
|---|---:|---:|---|
| outer tube OD/2 | 10.00 | 0.0964 | |
| **outer tube ID/2** | 8.50 | **0.0820** | the bore — bounds the plasma |
| intermediate OD/2 | 8.00 | 0.0771 | |
| intermediate ID/2 | 7.00 | 0.0675 | |
| injector OD/2 | 2.50 | 0.0241 | **on axis, at TM₀₂₀'s E_z peak** |
| injector ID/2 | 1.00 | 0.0096 | sample channel |
| intermediate ends | −20.0 | **0.2741** | plasma starts here |
| injector tip | −25.0 | 0.2176 | below the intermediate, as a Fassel should be |
| *field maximum* | *0* | *0.5000* | |

Derived: **ρ = r̄_plasma/a = 0.0627** (E_φ peak at 0.4805) · τ = t/r̄ = 0.615 ·
ω = w_wall/λ = 0.0123 with ε_r 3.78 quartz / 9.4 sapphire.

🔑 **ρ is bounded by the outer tube ID, so growing it means growing all three
tubes together — a coupled change, not one parameter.** The plasma annulus
(4.5–8.5) sits between the injector and the bore wall: coolant annulus above the
intermediate tube, sample channel up the middle. Physically coherent.

## 2. The central trade — ρ

E_φ ∝ J₁(χ′₀₁·ρ), deposition ∝ |E|², gas flow ∝ annulus area.

| ρ | r̄ mm | E/E_pk | deposition | torch OD | gas* |
|---:|---:|---:|---:|---:|---:|
| **0.063** | 6.5 | 0.206 | 1.0× | 21 mm | 15 slm |
| **0.10** | 10.4 | 0.323 | **2.5×** | 30 mm | 30 slm |
| **0.15** | 15.6 | 0.474 | **5.3×** | 41 mm | 56 slm |
| 0.20 | 20.7 | 0.611 | 8.8× | 53 mm | 85 slm |
| 0.4805 | 49.8 | 1.000 | 23.6× | 115 mm | 318 slm |

\* scaled from a 15 slm baseline at the current annulus area.

🔴 **The dimensionless optimum is unreachable.** ρ = 0.4805 needs a 115 mm torch
and hundreds of slm. **Gas flow is the binding constraint and it is an anchor-②
quantity — it does not scale with λ**, so no choice of frequency escapes it.

✅ **The achievable window is ρ ≈ 0.10–0.15**, buying **2.5–5.3× deposition** at
30–56 slm against an MP-AES's ~20. Never posed before, because the torch was a
20 mm catalogue part.

## 3. Where it stops being scale-free (anchor ②)

- **gas flow** ∝ annulus area × velocity. The hard limit, and it sets the ρ ceiling.
- **pressure** — Paschen *p·d*, and *d* grows with the torch.
- **thermal load** on the tube ∝ deposited power / wall area.
- **sapphire cost** — scales steeply with diameter, not just length.

## 4. What the harness can and cannot express

| | state |
|---|---|
| `--plasma ri,ro,zlo,zhi` | ✅ ρ, τ, ζ of the conductive region directly settable |
| three-tube Fassel geometry | ✅ **MODELLED** — `inter_od/wall/end`, `inj_od/id/end`, and the plasma zone defined as the clear bore downstream of the intermediate tube |
| `torch_od`, `torch_wall`, `torch_eps`, `torch_tand`, `inter_*`, `inj_*` | ✅ **all ten now exposed** — `--torch-tube od,wall` · `--intermediate od,wall,end` · `--injector od,id,end` · `--torch-material eps,tand`, with concentricity and arity guards, and recorded in the sidecar |

⚠️ **What the model still does not carry:** gas flow, swirl, temperature and the
aerosol path. So deposition and coupling conclusions are usable; sample-transport
and plasma-stability conclusions are not available from it, and stage 5 stays
external.

## 5. Staged plan

| stage | what | cost |
|---|---|---|
| **1** | ✅ analytic ρ trade — done, §2 | free |
| **2** | ✅ **DONE** — ten parameters exposed as four grouped flags, four validation guards verified firing, sidecar now records the torch, default path byte-identical at 158,929 tets. A 1.6× torch builds and gives ρ = 0.100 | done |
| **3** | lit solves at **ρ = 0.063 / 0.10 / 0.15**, at the η minimum δ/t ≈ 1 (R86's regime, not the favourable flanks). ⚠️ **All three tubes scale together** — ρ is not independently settable. Measure **η** and **C1′ deposition non-uniformity** | 3 solve pairs |
| **4** | ζ_inj sweep at the chosen ρ — the injector is at 0.274 against a field maximum at 0.500 and has never been varied | 2–3 solves |
| **5** | gas / thermal / cost reality check | external |

## 6. What each stage-3 outcome would mean

- **deposition gain materialises AND uniformity improves** → ρ is a free win and the
  torch should grow.
- **gain materialises, uniformity worsens** → the same trade as R85's groove, and
  it waits on R87's uniformity spec.
- **gain does not materialise** → the vacuum J₁ argument does not survive plasma
  loading, which would be a genuine falsification of §2 and the more informative
  result.

⚠️ **A larger plasma is also a stronger load.** R74 measured the plasma already
taking ≥96.8% of absorbed power, so this does not buy delivered power — which is
not short. The expected payoff is in **ignition** (breakdown scales steeply with
E, and we sit at 21% of peak field) and possibly in uniformity, since a wider
annulus averages over more of the azimuth.

## 7. What could invalidate this scope

- 🔴 If R87 says the current 46% deposition non-uniformity is already unacceptable,
  the filter and coupler decisions dominate and torch radius is second-order.
- 🔴 If R82 shows an m = 5 component that 5 sectors cannot see, every uniformity
  number in §6 is provisional.
- ⚠️ Growing the injector moves it further into TM₀₂₀'s on-axis E_z peak, which
  the geometry comment flags explicitly. A larger torch may therefore couple
  TM₀₂₀ more strongly — the mode R83 needs out of the way.
- ⚠️ The gas-flow scaling in §2 assumes velocity is held constant. If plasma
  stability requires a fixed *velocity* rather than a fixed *flow*, the ceiling
  moves; if it requires fixed *residence time*, it moves the other way.
