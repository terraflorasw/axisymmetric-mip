# FINDINGS — resonance

Append-only, newest at the bottom, dated UTC. Every entry carries a
**verification** and a **falsification**. See `README.md` for the rules.

---

## 🔴 READ `KNOWN.md` INSTEAD

**`KNOWN.md` is one page and holds everything this programme has established:
E0 (the instrument), H1 (the cavity), H2 (the groove), and what is NOT
established.** This file is the append-only ARCHIVE — 5,000 lines, most of it
superseded. **Come here only to follow a citation**, never to find out what is
known.

## 🔴 STATUS INDEX — READ BEFORE QUOTING ANY NUMBER FROM THIS FILE

### 🔑 LIVE PROVENANCE: **E0 and H1.** Everything else descends from them.

Those are the only two results anchored OUTSIDE the programme — **E0 against
closed-form mathematics, H1 against an analytic max-min optimum.** A finding
whose only support is another finding in this file is not independently
evidenced, however many entries cite it.

⚠️ Judge every entry below by asking **what external thing it touches**, not by
how much of this file it agrees with. Internal agreement is what an inward-facing
loop produces (see CONVENTIONS §7g and `README.md` on why the previous programme
was abandoned).


5,275 lines, 76 entries, and **three separate invalidation eras**. An entry being
here does not make it live. Check which era it belongs to first.

| lines | era | status |
|---|---|---|
| 1–328 | **ORDER-1 SOLVER** (5 entries, all 2026-08-20) | 🔴 **DEAD.** The instrument ran at solver order 1; errors up to 27.6 MHz are order-1 artifacts, not physics. Entry 5 (E0g, L303) is the fix and IS live. Kept because the invalidations only make sense against the numbers they replaced. |
| 328–~3100 | **E0 / H1 / H2 — instrument and cold cavity** | ✅ **LIVE**, with exceptions noted inline. Solver order 2, geometric order 2. This is where the design point, the Q anchor and the instrument characterisation come from. |
| — | **E1 series** | 🔴 **DELETED 2026-08-21**, ~64 MB. Methodologically poisoned: it moved torch and filter permittivity together, so no shift was attributable. Its one durable lesson survives — mode identity across a large perturbation needs CONTINUATION. |
| ~3100–end | **2026-08-23 LOADED PROGRAMME** (H3, H6, superpose, sapphire, loopsize) | 🔴 **SCOPE-INVALID (the groove omission).** Ran on a cavity with NO MODE FILTER — `GEO` never passed `--groove` while the design is frozen at 5×10 mm. Solver and geometry are fine (order 2 throughout); the CAVITY is wrong. **Design numbers must not be quoted.** METHOD findings from this era stand and are consolidated in INSTRUMENT's "loaded-cavity toolkit". |

⚠️ **Geometric order has been 2 for the whole life of this file** — E0f tested
2→3 and found 0.01 MHz. The "entire record is order-1" line at L341 refers to
the **waveguide/ignition programme that PRECEDED this one**, not to FINDINGS.

🔑 **Why nothing is deleted:** several invalidations are only comprehensible
against the wrong numbers they replaced, and CONVENTIONS keeps citations intact
("gaps beat broken citations"). The cost of that policy is this index — without
it the file is 5,000 lines with no way to tell live from dead, which is a fair
reason to distrust the whole thing.

✅ **When you invalidate an era, add a row here in the same edit.** That is the
same rule as CONVENTIONS §7f (a frozen parameter must enter the baseline) and
§8b (a doc not in the index is never read), applied to this file.

---

## 2026-08-20 — E0: the solver disagrees with mathematics by up to 27.6 MHz, ~8× its own noise floor

**V** — `physics.spectrum(103.70, 88.53)`, exact for PEC walls.
**F** — χ′₀₁ = χ₁₁ identically, so the TE₀₁₁/TM₁₁₁ splitting has a true value of
**exactly zero**; anything reported is pure artifact.

Eigenmode, PEC walls, order-1 solver on an order-2 mesh, 83,322 tets.

| mode | exact GHz | solved GHz | Δ MHz | ppm |
|---|---:|---:|---:|---:|
| TM₀₁₀ | 1.106485 | 1.102772 | −3.714 | −3356 |
| TM₁₁₀ | 1.763008 | 1.758425 | −4.583 | −2599 |
| TE₁₁₁ | 1.893272 | 1.890331 | −2.941 | −1554 |
| **TM₀₁₁** | 2.022654 | 2.022231 | **−0.424** | −209 |
| **TE₂₁₁** | 2.200375 | 2.199920 | **−0.455** | −207 |
| TM₂₁₀ | 2.362953 | 2.346328 | −16.625 | −7036 |
| **TE₀₁₁** | 2.444385 | 2.432387 | **−11.998** | −4908 |
| **TM₁₁₁** | 2.444385 | 2.432387 | −11.998 | −4908 |
| TM₀₂₀ | 2.539846 | 2.525423 | −14.423 | −5679 |
| TE₁₂₁ | 2.980652 | 2.953088 | **−27.564** | −9248 |

> 🔑 **mean −8.8 MHz, max |Δ| 27.6 MHz — against a mesh-noise floor of
> 1.3–3.3 MHz.** The instrument's SYSTEMATIC disagreement with physics is roughly
> **eight times its own random scatter**, and this is the first time it has been
> measurable at all. Every frequency in the previous programme inherits an
> unquantified error of this order.

⚠️ **Every Δ is NEGATIVE**, and the size is mode-dependent rather than a smooth
function of frequency — TM₀₁₁ and TE₂₁₁ land within 0.5 MHz while TM₂₁₀ and TE₁₂₁
are 17–28 MHz low. A uniform offset would be a scale or units error; this is not
uniform, so it is a **discretisation signature that depends on the field pattern**.
It cannot be absorbed by a single constant — which is exactly what the old
`offset.te011 = +24.54 MHz` tried to do.

### 🔑 The falsifier fired

| | |
|---|---|
| TE₀₁₁ / TM₁₁₁ solved | 2.432387 and 2.431187 |
| **splitting** | **1.199 MHz** |
| **true splitting** | **exactly 0** |

✅ **So the solver breaks an exact degeneracy by 1.2 MHz.** That is a hard bound
on every claim made near that degeneracy — including any hybridisation result,
and the mode filter's entire justification, which is a statement about two modes
that the instrument cannot place closer than ~1.2 MHz apart.

### 🔴 What is NOT established, stated plainly

1. **The convergence arm is VOID.** `e0fine` and `e0coarse` came out
   **byte-identical** (`md5sum` → one hash, 83,322 tets each): `--n-wl 8` did not
   coarsen the mesh, because the torch-shell wall clamps the element size. ⚠️ **My
   gates checked apertures, dielectric and material completeness but never
   asserted that the two meshes DIFFER** — the same class of omission for the
   fourth time today. No convergence claim may be read from this run.
2. **The cavity is not ideally empty.** `geometry.py` cannot delete the outer
   torch shell, so a vacuum-filled shell with internal mesh surfaces is present.
   Some unknown share of the 27.6 MHz belongs to that, not to the solver.
3. **Order-1 solver only.** The disagreement should shrink at order 2; that was
   not run.

🔑 **None of those weaken the falsifier.** The degeneracy splitting is a
difference between two modes of the SAME solve on the SAME mesh, so the shell,
the mesh density and the solver order all cancel. **1.199 MHz stands.**

### What this licenses

Nothing, by design. It bounds how much of a future disagreement may be
attributed to the solver rather than to the model — and it says that bound is
**large**: up to 27.6 MHz systematic, plus 1.2 MHz of symmetry breaking, against
a 1.3–3.3 MHz random floor.

| next | |
|---|---|
| E0b | a genuinely empty cylinder (needs a `geometry.py` change to drop the shell) and a REAL convergence ladder, with a differ-assertion on the meshes |
| E0c | order 2, to see how much of the 27.6 MHz is solver order |

---

## 2026-08-20 — E0b: a +256 mm rigid offset. TE₀₁₁ is stable; the DEGENERACY GETS 6× WORSE off-origin

**V** — the same exact spectrum. **F** — a rigid translation is an exact symmetry
of Maxwell, so **every frequency must be identical**. Anything that moves is pure
instrument. ✅ Meshes asserted distinct before solving (83,322 vs 83,809 tets,
0.58% apart) — the assertion E0 was missing.

| mode | Δ at origin | Δ at +256 mm | **shift** |
|---|---:|---:|---:|
| TM₀₁₀ | −3.714 | −4.019 | −0.306 |
| TM₁₁₀ | −4.583 | −5.259 | −0.677 |
| TE₁₁₁ | −2.941 | −3.326 | −0.385 |
| TM₀₁₁ | −0.424 | −0.675 | −0.251 |
| TE₂₁₁ | −0.455 | −0.827 | −0.372 |
| TM₂₁₀ | −16.625 | −18.478 | −1.853 |
| **TE₀₁₁** | **−11.998** | **−12.146** | **−0.148** |
| TM₁₁₁ | −11.998 | −12.146 | −0.148 |
| TM₀₂₀ | −14.423 | −18.496 | −4.074 |
| TM₂₁₁ | −2.463 | −5.482 | −3.019 |
| **TE₁₂₁** | **−27.564** | **−13.037** | **+14.527** |

### ✅ TE₀₁₁'s error is STRUCTURAL, not a coordinate artifact

Our operating mode moves **0.148 MHz** under a translation that is an exact
symmetry — below the mesh floor. **So its −12 MHz disagreement with the closed
form is real discretisation error (or the vacuum shell), not something an origin
choice created.** That is worth knowing: it is a correctable, characterisable
error rather than a coincidence.

### 🔴 But the "systematic" is NOT one number

**TE₁₂₁'s disagreement HALVED** — −27.6 → −13.0 — under a transformation that
changed no physics. So E0's worst-case 27.6 MHz was itself **half coordinate
artifact**. Different modes carry different mixtures of structural and
coordinate-dependent error, which is another way of saying **a single offset
constant cannot correct this instrument.** The old programme's
`offset.te011 = +24.54` was trying to do exactly that.

### 🔑 THE ORIGIN IS THE BEST OPERATING POINT — and this was the surprise

| | splitting of an EXACTLY degenerate pair |
|---|---:|
| at the origin | **1.199 MHz** |
| at +256 mm | **7.052 MHz** |

> 🔴 **Offsetting makes it nearly 6× worse.** The reasoning that motivated the
> test — that x = y = 0 forces geometric predicates through exact zeros where
> degenerate tie-breaking lives — is correct about the mechanism and **backwards
> about the sign.** Those exact coincidences are what let the mesh REPRESENT the
> cavity's azimuthal symmetry. The physics has that symmetry; putting the axis on
> the coordinate axis lets the discretisation inherit it. Moving off-axis
> destroys it, and an exact degeneracy splits 6× further apart.

✅ **So: build models at the origin.** An offset remains an excellent *probe* —
it separates structural error from coordinate error, which is exactly what it did
here — but it is a bad place to compute.

⚠️ And it re-bounds the falsifier: **1.199 MHz is the BEST case, not a typical
one.** Any claim about two modes closer than that is unresolvable, and a model
built off-axis would need 7 MHz of clearance instead.

| | |
|---|---|
| translation invariance violated by | **up to 14.5 MHz** |
| TE₀₁₁ structural error | **−12.0 MHz**, stable |
| degeneracy floor, on-axis | **1.2 MHz** |
| degeneracy floor, off-axis | **7.1 MHz** |

---

## 2026-08-20 — 🔴 CORRECTION to E0 and E0b: my matcher fabricated the two largest numbers

Prompted by the user calling the translation result "a massive concern on its own"
— which it partly is, but I had **overstated both headline numbers**, and the
cause was mine, not the solver's.

### The bug

I paired each exact mode to the **nearest solved eigenvalue**. That cannot see
two things:

| | |
|---|---|
| 🔴 an exact mode **above the solved ceiling** | the at-origin run returned **22 modes topping out at 2.95309 GHz**. **TE₁₂₁ sits at 2.98065 — it was never solved at all.** The matcher paired it with a lower mode |
| 🔴 a solved value **already claimed** | TE₀₁₁ and TM₁₁₁ are degenerate, so both matched the same eigenvalue |

The offset run returned **27** modes (ceiling 3.194) and *did* contain TE₁₂₁. So
the reported "+14.527 MHz shift" was **two different modes compared to each
other.**

### Corrected numbers — one-to-one, ceiling-checked

| mode | Δ at origin | Δ at +256 mm | shift |
|---|---:|---:|---:|
| TM₀₁₀ | −3.714 | −4.019 | −0.306 |
| TM₁₁₀ | −4.583 | −5.259 | −0.677 |
| TE₁₁₁ | −2.941 | −3.326 | −0.385 |
| TM₀₁₁ | −0.424 | −0.675 | −0.251 |
| TE₂₁₁ | −0.455 | −0.827 | −0.372 |
| **TM₂₁₀** | **−16.625** | −18.478 | −1.853 |
| **TE₀₁₁** | **−11.998** | −12.146 | **−0.148** |
| TM₀₂₀ | −14.423 | −18.496 | **−4.074** |
| TM₂₁₁ | −2.463 | −5.482 | −3.019 |

| claim | I said | **actually** |
|---|---:|---:|
| solver vs mathematics, worst mode | 27.6 MHz | **16.6 MHz** (TM₂₁₀) |
| shift under a rigid translation | 14.5 MHz | **4.1 MHz** (TM₀₂₀) |
| by index across the whole spectrum | — | 6.0 MHz, and that is a degenerate partner |

### ✅ What survives unchanged, and it is still the headline

| | |
|---|---:|
| **degeneracy splitting, on-axis** | **1.199 MHz** |
| **degeneracy splitting, +256 mm** | **7.052 MHz** |

🔑 **Untouched by the matcher bug** — a splitting is measured *within* one solve
between two adjacent eigenvalues, so no cross-run pairing is involved. **A rigid
translation, which is an exact symmetry of Maxwell, degrades an exact degeneracy
by 5.9×.** That remains the strongest statement E0b makes.

And **TE₀₁₁ is still the most translation-stable mode in the spectrum**
(0.148 MHz), so its −12.0 MHz disagreement is structural, not coordinate.

### 🔑 The lesson, which is already in METHODOLOGY and I did it anyway

> *"Never track a mode by 'largest of its type'"* — R59's tracker re-identified
> its target at every depth and drew a clean curve through three different modes.

**I wrote that rule down and then matched by nearest value.** `physics.match_exact()`
now refuses three cases: above the ceiling, already-claimed, and degenerate
partners (which are handled by splitting, never by pairing). It reports what it
refused rather than silently returning a number.

⚠️ **The solved spectrum being TRUNCATED is the deeper trap.** Requesting N modes
returns whatever the eigensolver converged — 22 in one case, 27 in another, for
the same request. **Any comparison against a reference list must check the
ceiling first**, or it will confidently report a value for a mode that was never
computed.

---

## 2026-08-20 — ✅ E0e: the SOLVER is exactly translation-invariant. 100% of the shift is the MESHER

The user, twice, and correctly: *"you're just gormlessly accepting the result
again. The fact that there is a massive difference under translation means the
tooling is suspect."* Grading a failed exact test as "about one noise floor" is
normalising it. **The correct answer is zero.** So: find the mechanism.

### The separation

Two candidates, and they can be split exactly. Instead of re-meshing a moved
solid, **translate the MESH ITSELF** — take the mesh already solved at the origin
and add 256 mm to every node. Identical topology, connectivity, element shapes and
quality; only the absolute coordinates differ.

| gate | |
|---|---|
| nodes | 113,647 → 113,647 |
| order-2 tets | 83,322 → 83,322 |
| every node delta | exactly 0.256000000 m |

### The result

| | |
|---|---:|
| **max \|Δ\| across all 22 eigenvalues** | **0.000000 MHz** |
| degeneracy splitting, origin | 1.199310 MHz |
| degeneracy splitting, nodes +256 mm | **1.199310 MHz** |

> ✅ **PALACE/MFEM IS EXACTLY TRANSLATION-INVARIANT — to seven decimal places on
> every mode.** The solver has no coordinate dependence whatsoever. This is the
> first component of this pipeline to be EXONERATED by an exact test rather than
> assumed correct.

🔑 **Therefore 100% of E0b's shift is gmsh re-meshing.** Not floating point, not
Palace's nondimensionalisation (`Lc` was identical at 2.074e-01 m in both), not
the geometry kernel misplacing anything (the bounding box translated exactly).
**The mesher, handed a rigidly moved solid, produces a genuinely different
discretisation, and that discretisation carries a different error.**

### 🔴 What that actually means, and it is worse than a bug would be

A bug could be fixed. This cannot:

| | |
|---|---|
| frequency error from mesh realisation | **up to ~4 MHz**, irreducible by care |
| the exactly-degenerate splitting | **1.199 MHz on one mesh, 7.052 on another of the same solid** |

🔴 **The 1.199 MHz degeneracy floor is a property of ONE MESH, not of the
instrument.** It varies almost 6× across realisations of the same geometry. Any
statement of the form "this instrument can resolve modes X MHz apart" is
therefore mesh-specific and cannot be quoted as a general bound.

🔑 **AND THE FIX IS NOT CARE — IT IS REFINEMENT OR ENSEMBLES.** No amount of
checking the setup reduces realisation error; it is not a mistake, it is a
property of which mesh you happened to get. Reducing it requires either refining
until the realisation dependence shrinks, or averaging over an ensemble of
meshes. **This project has never done either**, and every result to date is a
single draw from that distribution.

| component | status |
|---|---|
| Palace / MFEM solver | ✅ **exact** under translation, 0.000000 MHz |
| Palace nondimensionalisation | ✅ identical Lc |
| OCC geometry kernel | ✅ bounding box translated exactly |
| **gmsh mesh generation** | 🔴 **the entire source**, ~4 MHz, irreducible without refinement or ensembles |

⚠️ Incidental: `gmsh.write` defaults to MSH 4.1 while `geometry.py` writes 2.2,
and MFEM aborts on 4.1 with *"vertex index doesn't exist"*. Match the parent
format when rewriting a mesh.

---

## 2026-08-20 — ✅✅ E0g: AT SOLVER ORDER 2 THE INSTRUMENT IS ESSENTIALLY EXACT. The error was never the mesh

One mesh, geometric order 2, solver order varied — a **same-mesh** comparison, so
mesh-realisation error cancels exactly.

| mode | exact | **solver 1** | **solver 2** |
|---|---:|---:|---:|
| TM₀₁₀ | 1.10649 | −3.714 | **+0.005** |
| TM₁₁₀ | 1.76301 | −4.583 | **+0.022** |
| TE₁₁₁ | 1.89327 | −2.941 | +0.065 |
| TM₀₁₁ | 2.02265 | −0.424 | +0.073 |
| TE₂₁₁ | 2.20037 | −0.455 | +0.134 |
| TM₂₁₀ | 2.36295 | **−16.625** | **+0.095** |
| **TE₀₁₁** | 2.44438 | **−11.998** | **+0.058** |
| TM₀₂₀ | 2.53985 | −14.423 | +0.223 |
| TM₂₁₁ | 2.90695 | −2.463 | +0.143 |
| TE₁₂₁ | 2.98065 | (above ceiling) | +0.361 |

| | solver 1 | solver 2 | |
|---|---:|---:|---|
| **max \|Δ\| from exact** | 16.625 MHz | **0.361 MHz** | **46× better** |
| **degenerate splitting** (true value 0) | 1.199 MHz | **0.014 MHz** | **86× better** |

> ✅ **PALACE REPRODUCES THE EXACT SPECTRUM OF A CYLINDRICAL CAVITY TO BETTER
> THAN 0.4 MHz ON EVERY MODE, AND PRESERVES AN EXACT DEGENERACY TO 14 kHz.**
> The instrument is not suspect. **We were running it at solver order 1.**

### 🔴 What this retro-invalidates

1. **The whole "tooling is suspect" line of enquiry was measured at order 1.**
   E0b's 4 MHz translation shifts, E0c's 1.2→7.1 MHz splitting spread, E0's
   16.6 MHz systematic — all of it is order-1 behaviour. At order 2 the
   discretisation error is 46× smaller, so the realisation scatter should
   collapse with it. **E0h is now running the ensemble at order 2 to check.**
2. **`offset.te011 = +24.54 MHz` was never correctable as a constant.** At order 1
   the error runs from −0.42 MHz (TM₀₁₁) to −16.6 MHz (TM₂₁₀) — **mode-dependent
   by 40×.** A single additive offset applied to all modes corrupts every mode
   SEPARATION it touches, which is most of the old programme's mode-landscape work.
3. **The old programme's entire record is order-1 driven.** Its frequencies carry
   a mode-dependent error of up to ~17 MHz that no constant removes.

### 🔑 The sequence that got here, because the method is the finding

| | |
|---|---|
| E0 | solver disagrees with mathematics by up to 27.6 MHz | *(later corrected to 16.6 — my matcher)* |
| E0b/E0c | rigid motions move it by ~4 MHz; exact degeneracy splits 6× | tooling suspected |
| E0e | **solver is exactly translation-invariant, 0.000000 MHz** | solver exonerated, mesher blamed |
| E0f | geometric order 2→3 changes **nothing** (0.01 MHz) | **falsifier fired** — not the geometry |
| **E0g** | **solver order 1→2 fixes everything** | it was the field basis all along |

⚠️ **Three of my own predictions were wrong and each wrong one was informative**:
geometric order 3 would collapse the error (it plateaued, which located the fault);
an inscribed polygon would read high (signs were mixed); and 4 MHz under
translation was "about one noise floor" (it was order-1 error, and the user was
right to refuse that framing twice).

🔑 **None of this was reachable by internal consistency.** Every check the old
programme ran compared the instrument to itself. The closed form is what made the
order-1 error visible at all — which is the entire argument for `physics.py`.

⚠️ Solver order 3 timed out at the 3600 s ceiling and was not measured.
Unnecessary: order 2 already lands inside the 0.4 MHz that any physical
tolerance cares about.

---

## 2026-08-20 — ✅ E0j: the working recipe. Order 2 on a COARSE mesh, and my "two minutes" prediction was wrong

| size factor | elements | seconds | TE₀₁₁ | **max\|Δ\|** | splitting |
|---:|---:|---:|---:|---:|---:|
| 3.0 | 5,199 | 648 | +0.264 | **10.593** | 5.423 |
| **2.5** | **7,739** | **588** | **−0.252** | **1.751** | 0.490 |
| 2.0 | 13,013 | 943 | +0.128 | 1.709 | 0.870 |
| 1.5 | 25,982 | 1879 | +0.197 | 1.957 | 0.014 |
| *0.96 (E0g)* | *83,322* | *3007* | *+0.058* | *0.361* | *0.014* |
| *0.96, **solver 1*** | *83,322* | *89* | *−11.998* | *16.625* | *1.199* |

### 🔴 TE₀₁₁ ALONE IS THE WRONG METRIC, and the coarsest row proves it

At sf 3.0, TE₀₁₁ is accurate to **0.264 MHz** — and **max\|Δ\| across the spectrum
is 10.6 MHz** with the exact degeneracy split by **5.4 MHz**. A 5,199-element mesh
gets the operating mode nearly right and the *mode landscape* badly wrong.

🔑 **Since most of this design rests on mode SEPARATIONS — TM₀₂₀'s clearance,
TE₀₁₁/TM₁₁₁, which rival sits nearest the drive — `max|Δ|` is the metric that
governs, not the accuracy of the mode we care about.** Reporting TE₀₁₁ alone
would have licensed a setting that corrupts everything else.

### 🔴 My prediction was wrong: cost is NOT proportional to elements

I predicted "under two minutes" on a 10–15k mesh. It is **588–943 s**. Elements
fell **11×** (83k → 7.7k) while cost fell only **5×** — and below sf 2.5 cost
goes back UP (5,199 elements took 648 s, *longer* than 7,739 at 588 s) while
accuracy collapses. There is a **floor**, and the coarse end is worse on both axes.

⚠️ So E0j's declared falsifier partly fired: the frontier is flatter than assumed.
The order-2 advantage is real but it does **not** buy an order-of-magnitude
cheaper instrument — a large fixed cost (setup and the shift-invert
factorisation) dominates once the mesh is small.

### ✅ THE STANDING RECIPE

| | |
|---|---|
| geometric order | **2** (order 3 changes nothing — E0f) |
| **solver order** | **2** (order 1 is never worth it — E0g) |
| size factor | **2.0–2.5**, ~8–13k elements, ~10–16 min |
| expected accuracy | TE₀₁₁ ~0.2 MHz, **all modes within ~1.8 MHz** |
| when sub-0.4 MHz is needed | sf 0.96, 83k elements, 50 min |

🔴 **Solver order 1 is never the right choice at any mesh size.** It costs 89 s to
be 12 MHz wrong on TE₀₁₁ and 16.6 MHz wrong on TM₂₁₀ — worse than order 2 on a
mesh **11× coarser**, which is both cheaper per unit accuracy and 48× more
accurate. **The old programme ran every solve in the worst corner of this trade**,
paying for a fine mesh whose resolution a poor basis threw away.

### E0 closes here

| | |
|---|---|
| solver, translation invariance | ✅ **exact**, 0.000000 MHz (E0e) |
| geometry representation | ✅ converged at order 2 (E0f) |
| field basis | 🔑 **was the entire error** (E0g) |
| absolute accuracy, working recipe | ✅ **≤1.8 MHz all modes**, 0.2 MHz on TE₀₁₁ |
| exact degeneracy preserved to | ✅ **0.014–0.49 MHz** depending on mesh |
| against physical tolerances | 2.34 MHz linewidth, 23 MHz tuner, 195 MHz clearance |

✅ **The instrument is fit for purpose, and now it is known to be, against
mathematics rather than against itself.** That was the whole point of E0.

---

## 2026-08-20 — 🔑 E1a: the design point is ANALYTIC. No solver, and three results fall out for free

Once E0 established the closed form to ≤1.8 MHz, the empty-cavity design point
needs no simulation at all. Fix f(TE₀₁₁) = 2.4500 GHz and one free parameter
remains — the aspect ratio. Every member of that family resonates on target; the
choice among them is made by the rest of the spectrum, which is equally analytic.

| L mm | a mm | D/L | TM₀₂₀ | TM₂₁₀ | nearest rival |
|---:|---:|---:|---:|---:|---:|
| 70.00 | 153.584 | 4.388 | 1.7149 | 1.5955 | TE₂₁₁ −108 MHz |
| 80.00 | 115.820 | 2.895 | 2.2741 | 2.1157 | TM₀₂₀ −176 |
| **88.53** | **103.245** | **2.332** | 2.5510 | 2.3734 | **TM₂₁₀ −77** ← inherited |
| 95.00 | 97.544 | 2.054 | 2.7001 | 2.5121 | TM₂₁₀ +62 |
| 105.00 | 91.820 | 1.749 | 2.8685 | 2.6687 | TM₂₁₀ +219 |
| **120.00** | **86.743** | **1.446** | 3.0363 | 2.8249 | **TE₁₁₂ +246** ← widest |

### 🔑 Three results, none of which required a solve

**1. The mode filter is mandatory, and that is a THEOREM.** χ′₀₁ = χ₁₁ =
3.8317059702 identically, so TM₁₁₁ is degenerate with TE₀₁₁ **at every aspect
ratio**. No cavity shape separates them. The old programme reached this
empirically; it is provable in one line and could never have been otherwise.

**2. TM₀₂₀ is a function of RADIUS ALONE** — p = 0 means no length dependence at
all, so f = c·χ₀₂/(2πa) exactly. ✅ The old programme's "TM₀₂₀ headroom sets the
radius tolerance" was therefore structurally right, even though its numbers were
order-1.

**3. NO in-band rivals at any aspect ratio** — for an empty cavity, nothing but
TE₀₁₁/TM₁₁₁ lands in 2.400–2.500 GHz anywhere on the family.

### 🔴 But (3) does NOT transfer to the loaded cavity, and the reason is large

| mode | empty (exact) | old LOADED value | loading shift |
|---|---:|---:|---:|
| TE₀₁₁ | 2.444385 | 2.44146 | **−2.9 MHz** |
| TM₀₂₀ | 2.539846 | 2.39552 | **−144.3 MHz** |

🔑 **Loading moves TM₀₂₀ FIFTY TIMES further than TE₀₁₁** — because TM₀₂₀'s E_z
peaks on axis where the torch sits, while TE₀₁₁'s E_φ vanishes there. So an empty
cavity with no in-band rivals can acquire one purely through loading, and the
whole point of E1b is to compute that. **The analytic result is necessary and not
sufficient**, and the old programme's TM₀₂₀ work was measuring a real effect even
where its numbers were wrong.

### ⚠️ The inherited aspect ratio is not the separation optimum

| | |
|---|---|
| inherited D/L = 2.332 | nearest rival TM₂₁₀ at **−77 MHz** |
| D/L = 1.446 | nearest rival TE₁₁₂ at **+246 MHz** — 3.2× wider |

⚠️ **Not a recommendation.** D/L also sets plasma volume, the field at the torch,
the optical chord and wall Q, and a = 86.7 mm is a substantially different
machine. It is recorded because it was free and because **the inherited value was
never chosen against this criterion.**

⚠️ Also: the inherited point puts the EMPTY TE₀₁₁ at 2.444385 — **5.6 MHz below
the 2.45 target before any loading**, and loading pushes it a further 2.9 MHz
down. Whether 2.45 is the right target at all is a separate question (the band is
2.400–2.500 and the tuner spans 23 MHz), but the offset should be deliberate
rather than inherited.

---

## 2026-08-20 — 🔴 CORRECTION: every TIMING in this record is contaminated, and "hard practical ceiling" was wrong

I wrote that solver order 2 above ~85k elements was "off the table" and called a
one-hour timeout a **hard practical ceiling**. Both claims are withdrawn.

### The defect

`subprocess.run(timeout=…)` **raises but does not kill the child.** Every timeout
in this session left four Palace ranks running:

| run | what timed out | orphan lifetime |
|---|---|---|
| e0g | solver order 3 | ran on through E0j |
| e0h | ensemble member 1 | ran on |
| e0i | first case | ran on |
| **e1c** | k = 1.0, 92,596 el | **90 minutes past its own timeout**, caught only because the user asked how the runs were doing |

🔴 **So E0j's cost column measured MY CONTENTION, not the solver.** Its 588–3007 s
figures were taken on an 8-core box while a forgotten job held four of those
cores, with every run pinned to `-np 4`. **The "10–16 min" in the standing recipe
is not a measurement of anything.**

✅ **The ACCURACY columns stand** — E0e proved the pipeline is bit-exact
reproducible, so contention changes wall-clock and nothing else. Every Δ, every
splitting, every convergence conclusion is unaffected. **It is only the cost model
that was wrong**, and cost is what I used to justify shrinking the ensemble and
declaring a ceiling.

### Three things were arbitrary and got treated as physical

| | was | now |
|---|---|---|
| timeout | 3600 s, a config default | **21600 s** |
| ranks | `-np 4` | **`-np 8`**, one job at a time |
| memory | judged from `free`, which reports the HOST | cgroup shows 3 GB of 32 used |

🔑 **I built a cost model out of three of my own configuration choices and then
let it decide the science** — it shrank the ensemble from 8 members to none, and
produced a "ceiling" that ruled out the fine-mesh end of the frontier.

### What has to be re-measured

- **E0j's frontier**, uncontended, at `-np 8`. The accuracy/element curve is
  correct; the seconds/element curve must be re-taken.
- **The standing recipe's cost claim.** Its ACCURACY basis (order 2, sf floor set
  by the thinnest feature) is unaffected.
- ⚠️ `solver.py` still exposes `ranks=4` in its own `solve()` signature, used by
  the carried-over drivers. Not yet touched.

⚠️ **And the ceiling claim had a second error**: I generalised from the loaded
geometry's 92k-element timeout to solver order 2 in general, when E0g had already
run 83k elements to completion. One data point, taken under contention, against a
counter-example I had myself produced an hour earlier.

---

## 2026-08-20 — 🔴 E1c CLOSED by counting: graded meshing is not worthwhile. And the harness leaked until it thrashed the user's machine

### The answer needed no solves at all

| strategy | elements | reduction |
|---|---:|---:|
| **graded** — air ×2, walls fine | 75,526 | 18% |
| **graded** — air ×3, walls fine | 72,215 | **22%** |
| **uniform** — sf 1.5 | 35,487 | 62% |
| **uniform** — sf 2.0 | **19,346** | **79%** |

🔑 **Coarsening the air threefold removes 22% of the elements, and it
asymptotes.** The air was never the budget — the count is dominated by the thin
walls, and only a uniform coarsening, which lets them relax toward the
`MeshSizeMin` floor, touches it. **The declared falsifier fired: grading is a
coarser mesh with extra steps.**

⚠️ **The mesh counts were on screen before the first solve was launched.** Three
order-2 solves at 72–92k elements were spent on a question already answered by
`ls`-level information. **`--air-coarsen` is to be removed** rather than left as a
knob whose only use is a way to be wrong.

### 🔴 The harness defect, and what it cost

`subprocess.run(timeout=…)` **raises but does not kill the child.** Every timeout
this session leaked four ranks:

| run | leaked | noticed |
|---|---|---|
| e0g order 3 | 4 ranks | never — ran through E0j |
| e0h, e0i | 4 ranks each | never |
| e1c k=1.0 | 4 ranks | **90 min later**, only because the user asked |
| e1c k=2.0 | 4 ranks | on the next check |

🔴 **Twelve concurrent Palace processes on 8 cores thrashed the user's machine and
they had to stop the session during their standup.** That is the real cost, and it
was mine.

⚠️ **`solver.py` carried the same bug AND a false message** — it printed *"exceeded
Ns and was killed"* when nothing was killed. A log line that asserts an action the
code does not take is worse than silence.

### Fixes

| | |
|---|---|
| both drivers | `Popen` + `wait(timeout)` + **`kill()`** |
| `reap.py` | finds ranks whose **parent is gone (PPID 1)** by exact executable name and kills by PID. 🔴 **Never `pkill -f`** — it matches the harness wrapper's argv and kills the calling shell (exit 144, three times in this project, twice today) |
| timeout | 3600 → 21600 s; one hour was a config default I had quoted as a physical ceiling |
| ranks | 4 → 8, one job at a time |

### 🔑 The pattern worth keeping

**Both of today's self-inflicted failures were documented lessons I had written
down myself** — `subprocess.run` not killing children, and `pkill -f` killing the
caller. Writing them down was not sufficient. What they have in common is that
**the unsafe form is shorter than the safe one**, so the fix has to be a
FUNCTION THAT EXISTS (`reap.py`, `Popen`+`kill` inside the shared `run`), not a
rule to remember at the moment of typing.

---

## 2026-08-20 — 🔴 E1b: the MEASUREMENT IS NOT RECOVERABLE from this data. Mode pairing needs field signatures

Four solves, both shapes, ~3.6 hours. **The meshes are good and the solves are
good; the pairing between them is not.**

| | shape A (D/L 2.332) | shape B (D/L 1.446) |
|---|---|---|
| elements | 35,487 | 45,066 |
| solve time | 2141 s / 2238 s | **4208 s / 4299 s** |
| ✅ mesh check vs exact | **1.753 MHz** | **1.859 MHz** |
| 🔴 falsifier | TM₀₁₀ **+607.60 MHz** | TE₁₁₂ **+55.09**, TM₂₁₁ +14.68 |

✅ **The declared sign falsifier fired on both.** Adding dielectric cannot raise a
resonance, so any positive shift condemns the setup — and it did, immediately,
before any conclusion was drawn from the numbers.

### Why, precisely

Each solve was matched INDEPENDENTLY against the **empty** exact spectrum. That
works only while the effect being measured is smaller than the mode spacing:

| | |
|---|---:|
| loading moves TM₀₂₀ by | ~144 MHz |
| loading moves TM₀₁₀ by | ~130 MHz |
| **mode spacing** | **50–100 MHz** |

🔑 **So "nearest to the empty value" is guaranteed to find the wrong mode.**
TM₀₁₀ drops out of the eigensolver's window entirely and the matcher pairs it
with TM₁₁₀, and the mispairing cascades.

⚠️ `physics.match_exact()` did not help, and could not: it enforces one-to-one
and a ceiling check **within one solve**. Nothing in it relates two solves to
each other.

### 🔴 What is needed, and it is not an analysis fix

Modes must be paired **transparent ↔ loaded by what they ARE, not where they
are** — bore-H and bore-E energy fractions, the discriminator that has worked
everywhere else in this project. 🔴 **The eigenmode configs emit only Energy
index 1 (bore), so the modes carry no signature to match on.** `results.py` has
done this for driven solves since the old programme; the eigenmode path never
got it.

**So this needs a re-solve, not a re-analysis.** That is the opposite of the
three-layer split's usual promise, and worth stating plainly: the split saves you
when the VERDICT is wrong, not when the MEASUREMENT lacks the field needed to
interpret it.

### What survives

| | |
|---|---|
| ✅ mesh quality, both shapes | 1.75 / 1.86 MHz vs exact — the meshes are fine |
| ✅ the empty spectra | both reproduce closed form at sf 1.5, order 2 |
| ✅ solve timings, uncontended | 2141–4299 s at 4 ranks |
| 🔴 every loading shift | **withdrawn** |
| 🔴 the A vs B comparison | **not made** |

⚠️ **Cost note for the rental case**: shape B took **4208 s and 4299 s** on
45,066 elements — 2× shape A's time for 1.27× the elements. Four solves is 3.6
hours here. At 8 concurrent on 32 cores it is ~70 minutes, and the re-run with
signatures is the natural first job for that machine.

---

## 2026-08-20 — 🔴 E1b RE-RUN: signatures did not fix the pairing, and the experiment changes TWO materials at once

Re-ran E1b on the instance at 32 ranks with signature-based pairing. The mesh
verification passed; the measurement is still not recoverable, for a reason the
first failure hid.

### What passed

| | |
|---|---|
| ✅ mesh check, shape B | transparent vs closed form, max\|Δ\| = **1.859 MHz** |
| ✅ TE011 shift, B | **−102.83 MHz** — identical under every pairing tried, so this one is real |
| ✅ solver/rank invariance | unchanged from E0l; 32 ranks is not a variable |

### What failed, and it is not the same failure as last time

Signature pairing produced physically impossible assignments: TM010 **+1781 MHz**
and TM020 **−1847 MHz**, i.e. it swapped them. The declared sign falsifier caught
it, as designed.

The fingerprints are **not invariant under loading** — that was the assumption
the whole approach rested on. Sapphire at ε=11.6 sits on axis, exactly where
TM0n0 modes keep their energy, so loading *changes the very quantity* being used
as the identity. TM010 and TM020 have similar bore/torch energy fractions to
begin with, and the Hungarian assignment minimised total distance by swapping
them. `sig dist` was 0.07–0.19 on the doubtful pairs against 0.002–0.018 on the
trustworthy ones — the rig flagged them, and the flags were right.

An order-preserving pairing was also tried offline: it fixes 11 of 12 signs but
gives TM020 = −31 MHz and a ratio of **0.3×** against a predicted 43–53×. It
assumes no crossings, and crossings are precisely what a 150 MHz shift through
50–100 MHz spacing must produce. **All three static methods fail for the same
structural reason**: frequency, energy-fraction signature, and ordering are each
destroyed by a perturbation this large.

### 🔑 The finding under the finding: two variables move together

The rig switches torch ε 1→11.6 **and** filter ε 1→3.78 in a single step, so no
result from it can attribute a shift to either. That is why the prediction missed
by more than the pairing explains:

- predicted TE011 shift ≈ **−3 MHz**, from Bessel integrals over the **torch tube
  walls only**
- measured TE011 shift = **−102.83 MHz**, stable under every pairing

TE011's E is azimuthal and vanishes on axis, so the on-axis torch *cannot* move
it 100 MHz. The quartz mode filter can: it sits where E_φ is strong, and R107
established the filter is what makes TE011 exist as a clean mode at all. The
prediction covered one perturbation and the experiment performed two. **The 43–53×
ratio was never testable by this rig.**

### 🔴 Harness defect, mine, introduced in the signature rewrite

The per-case analysis block sat **outside** the `for nm, a, L in SHAPES:` loop.
Both shapes were meshed and solved; the analysis then ran once on whichever `tag`
survived the loop. **Shape A was meshed (5.2 min) and solved twice (137 s + 120 s)
and silently discarded** — no mesh check, no table, no entry in the result file —
while the run printed a confident summary for half the experiment. Fixed, and the
fix verified by AST rather than by reading. Prior entries carry A's mesh check
(1.75 MHz), which is how the loss was visible at all.

### Next

Mode identity must come from **continuation**, not from a static comparison of two
solves: sweep ε in steps small enough that each step's shift is far below mode
spacing, and follow modes through crossings by continuity. Separate the torch and
filter perturbations while doing it. Both are now affordable — see the mesh-cache
entry: the mesh is built once and every step reuses it byte-identically, which is
the same-mesh rule enforced rather than re-derived.

---

## 2026-08-20 — ✅ MESH CACHE: meshing became the critical path, and reuse is provably identical

At 4 ranks the solves dominated and meshing was noise. At 32 ranks that inverted:

| E1b shape | mesh | both solves |
|---|---:|---:|
| A, 35,487 elem | 5.2 min | 4.3 min |
| B, 45,066 elem | **10.6 min** | 9.4 min |

**Meshing is ~53% of the run**, and it grew faster with element count than the
solve did. Every re-run rebuilt byte-identical meshes from scratch.

`geometry.py` now caches meshes, keyed on the resolved parameter dict **plus the
SHA-256 of `geometry.py` itself**. Hashing resolved parameters means `--sectors 1`
and `--azimuthal-bins 1` share an entry and flag order is irrelevant; hashing the
source means any edit to the geometry code invalidates every entry, which is the
property that makes it safe to leave on by default. Entries store their mesh hash
and are verified before use; a corrupt entry is a loud miss. Writes are atomic
(temp dir + `os.replace`), and a store failure can never fail a run.

`cachetest.py` proves the claim rather than the code path:

```
cold build :   282.1s  8fe2754decf8a60f  stored
cache hit  :     0.2s  8fe2754decf8a60f  HIT
✅ byte-identical   ✅ 1582x   ✅ edit invalidates   ✅ --no-cache bypasses
```

⚠️ This is **reuse, not approximation**. It does not weaken METHODOLOGY §2b — it
strengthens it: a rebuild is identical only if nothing drifted, a hit is identical
by construction and checked by hash.

### Two near-misses this created

1. I edited `geometry.py` while the mesh-determinism rig was mid-flight. Its
   second repeat would have been served a **cache copy in 0.2 s with a trivially
   identical hash**, and the rig would have reported "REPRODUCIBLE" having meshed
   nothing. `meshdet.py` now forces `--no-cache` itself and *refuses* to be passed
   it — the guarantee belongs in the rig, not in remembering.
2. `ops/go` gated its auto-sync on **Palace ranks**, and a rig spends most of its
   life meshing with zero ranks alive (5.2 min, then 10.6 min in this very run).
   The guard read 0 and would have synced modified code into a running
   experiment, between its two cases. It now counts rig and mesh processes too.

Both are the same error as `ops/wait.sh` declaring a healthy run dead: **inferring
state from a downstream symptom instead of asking directly**. Meshing is now long
enough that "no ranks" and "not running" are wholly different statements.

### gmsh threading, measured not assumed

`General.NumThreads` is **live** here — OpenMP is in `General.BuildOptions` — and
defaults to 1, so all meshing to date has been serial. `Mesh.Algorithm3D` is 1
(Delaunay, largely serial); the parallel mesher is HXT (`=10`), which is compiled
in but **produces a different mesh** and so cannot be adopted without
re-baselining. `geometry.py --threads` now exists, **defaulting to 1** so every
existing mesh still reproduces, and the thread count is recorded in the sidecar.
Adoption is gated on `meshdet.py` showing byte-identical output across repeats
**and** against the serial mesh — untested as of this entry.

---

## 2026-08-20 — 🔑 E1b SPLIT into driver and analysis. Shape A recovered in 0.33 s, no solver

Correction to the entry above: shape A's data was **not lost**. All four solves'
output sat intact in `postpro/` the whole time. Only the analysis skipped it, and
because analysis lived inside the solver script, a skipped analysis was
indistinguishable from lost data.

E1b is now two files:

| | |
|---|---|
| `e1b_drive.py` | meshes, solves, writes `e1b.manifest.json`. **May not** name a mode, pair anything, compute a shift, or emit a verdict. |
| `e1b_analyse.py` | reads the manifest + `postpro/`, does all naming, pairing, checks. Solves nothing. |

`e1b_loaded.py` is deleted — two paths doing one job is how they drift.

**The split paid for itself immediately.** Reconstructing the manifest for the
completed run and re-analysing recovered shape A in **0.334 s**, against the ~9
minutes of solving it would otherwise have cost. Every past E1b failure was in
the analysis layer; each one previously cost solver hours purely because the two
were welded together.

The driver now also records the **mesh SHA-256 per case**, so the analysis layer
CHECKS the same-mesh rule instead of assuming it, and writes the manifest after
every case so a death in case 2 cannot take case 1 down with it.

### What shape A adds — and it changes the reading

| | shape A (D/L 2.332) | shape B (D/L 1.446) |
|---|---:|---:|
| mesh check vs closed form | 1.753 MHz ✅ | 1.859 MHz ✅ |
| **TE011 shift** | **−95.76 MHz** | **−102.83 MHz** |
| TM020 shift | −351.96 MHz | −1846.82 MHz |

**TE011 agrees to 7% across two very different aspect ratios; TM020 disagrees by
5×.** That asymmetry is the finding. TM020's pairing is junk in both shapes, as
already established — but TE011's ≈ **−100 MHz** now looks like a real
measurement, reproduced on two independent geometries and stable under every
pairing method tried.

It is ~30× the **−3 MHz** predicted from the torch tube walls, and it is very
nearly **shape-independent** — which is what a perturbation from the **3 mm mode
filter** (identical in both shapes) produces, and not what an on-axis torch
produces for a mode whose E vanishes on axis. Combined with R107 (the filter is
what makes TE011 a clean mode at all), the torch is now the *unlikely* cause of
TE011's shift.

⚠️ Still not attributable: the rig moves torch and filter ε together, so
"−100 MHz is the filter" remains inference, not measurement. Separating them is
two more solves per shape on the **cached** mesh — the first experiment the split
and the cache were built to make cheap.

Shape A also reported `TM010 — no signature match`, which the old code never
printed at all.

---

## 2026-08-20 — 🔴🔴 INVALIDATION: the solver-order default was 1, and most of this programme inherited it

E0k settled the driven-vs-eigenmode question, and in doing so exposed something
larger than the question it answered.

### E0k's result first

One mesh, one loop, four solves:

| order 2, same mesh | f (GHz) | vs exact |
|---|---:|---:|
| eigenmode | 2.44648 | +2.09 MHz |
| driven | 2.44670 | +2.32 MHz |
| **driven − eigenmode** | | **+0.225 MHz** |

| order 1 | | |
|---|---:|---:|
| eigenmode | 2.46786 | +23.5 MHz |
| driven | 2.44136 | −3.0 MHz |
| **apart** | | **26.5 MHz** |

**The two problem types agree to 0.225 MHz at order 2 and disagree by 26.5 MHz at
order 1.** METHODOLOGY's 3.7× driven-vs-eigenmode disagreement was an **order-1
artifact**, consistent with the note that the old programme's record is entirely
order-1 driven and with E0g's finding that order-1 error varies 40× by mode. The
declared falsifier's premise dissolves rather than resolving: the gap is not a
property of the two solvers.

### 🔴 The invalidation

`eigen_cfg` in `e0_solver_vs_math.py` hardcoded **`"Order": 1`**, and both
templates (`w890.json`, `e0cond.json`) default to `Order: 1`. Any rig that did not
explicitly override it ran at a discretisation **already known to be wrong**.

| ran at solver order 1 | ran at order 2 (explicit) |
|---|---|
| `e0b_offset`, `e0c_rigid`, `e0d_transverse`, `e0e_nodeshift`, **`e0f_geomorder`** | `e0g` (sweeps), `e0h` (default 2), `e0i`, `e0j`, `e0k`, `e1b_drive` |

Plus the **entire old programme**, already recorded as order-1 driven.

**The most consequential is E0f.** Its conclusion — *"geometry is converged at
geometric order 2"* — was reached with the SOLVER at order 1, where the error is
12–17 MHz and mode-dependent by 40×, i.e. **larger than the geometric-order
differences it was resolving**. That conclusion is load-bearing: it is why every
mesh since is built at geometric order 2. It is not refuted, but it is **not
established**, and it must be re-run at solver order 2.

⚠️ Differential vs absolute. Claims resting on a difference between two solves at
the SAME order may survive, because the order-1 error largely cancels — E0e
(translation invariance), E0b/c/d (rigid motion), E0l (rank invariance) are in
this class. Claims about an ABSOLUTE frequency do not survive. **Each needs
re-checking individually; "differential" is a reason to re-examine, not a pass.**

### The fix, and why it is the default that mattered

`eigen_cfg` now defaults to **Order 2**. A known-bad value must never be the
default — rigs that genuinely want order 1 (E0g's sweep, E0k's historical bridge)
set it explicitly. This is the same shape as the wall-conductivity bug below: the
right value existed, and the thing that consumed it never asked.

## 2026-08-20 — 🔴 Every Q in this programme is ~34% high: the wall was SILVER

`solveconf` binds wall conductivity from `baselines.json` (R110). This programme's
`baselines.json` **starts empty by design** — "nothing is inherited from
../waveguide without re-derivation" — so the lookup raised on **every solve**, and
the code fell back to the template while printing a warning:

```
⚠️ wall conductivity from TEMPLATE — baselines unreadable ('wall.conductivity')
```

`w890.json` carries **6.3e7 S/m — silver**. R58 adopted bare electropolished
aluminium at 3.5e7 on optical grounds. So every absolute Q in the resonance record
is high by √(6.3/3.5) = **1.34×**. Frequencies are unaffected, so E0k's result and
E1b's mesh checks stand.

R110 fixed precisely this bug in the old programme, and the new programme's
"start empty" policy silently undid it. **A warning that does not stop anything is
a warning nobody acts on.**

Fixed both ways: `wall.conductivity` is now declared in `baselines.json`
(kind=input, with source, and noting the handbook value is an UPPER bound on a
real electropolished surface), and a missing declaration now **refuses to solve**
instead of substituting silver. `condcheck.py` verifies both on the instance:
config carries 3.5e7, and removing the declaration raises.

---

## 2026-08-20 — 🔴🔴🔴 E0m: gmsh IS NOT DETERMINISTIC. Meshes are not regenerable, and never were

Ran to validate PARALLEL meshing before adopting it. The parallel question turned
out to be the less important one.

### Two identical SERIAL commands produce different meshes

| threads | best s | speedup | reproducible | same as serial |
|---:|---:|---:|---|---|
| 1 | 4.6 | 1.00× | **NO** | — |
| 8 | 5.0 | 0.92× | **NO** | NO |
| 32 | 4.7 | 0.96× | **NO** | NO |

`threads=1` — the setting every mesh in this programme has ever used — is **not
reproducible**. Verified as real, not a header artifact: `meshdiff.py` found
2,540 differing lines, **all inside `$Nodes`**, with `$Elements` byte-identical.
Topology is fixed; node POSITIONS move.

### How much, and which nodes

| | |
|---|---:|
| nodes moved | 2,542 of 38,832 (6.5%) |
| max displacement | **46.5 µm** |
| p99 / median / rms | 28.2 / 4.95 / **8.8 µm** |
| corner (vertex) nodes among the movers | **816** (max 11.9 µm, median 1.0 µm) |
| mid-edge nodes among the movers | 1,724 |
| movers in the bulk (r < 80 mm) | 892 of 2,542 |

8.8 µm rms on a 103.7 mm radius is **8.5e-5 relative — about 11 orders of
magnitude above double-precision roundoff**. This is an algorithmic instability,
not numerical drift, which is why the E0b/E0e hunt (translating the cavity 256 mm
to expose floating-point error) could never have found it. 46 µm is also real
machining tolerance, so the scale is physically meaningful, not academic.

⚠️ **Corner nodes move.** So this is not only the high-order projection: the
LINEAR tet mesh is position-unstable while topologically identical. Consistent
with `--ho-optimize 0` changing nothing.

Localisation, by geometric order:

| | reproducible | time |
|---|---|---:|
| geometric order 1 | ✅ bit-identical | 0.9 s |
| order 2, ho-opt 2 (current) | 🔴 varies | 4.8 s |
| order 2, ho-opt 0 | 🔴 varies | 4.6 s |
| order 2, ho-opt 1 | 🔴 varies | 5.4 s |

Disabling `HighOrderOptimize` neither restores determinism nor saves time. **Not
reachable by a flag.**

### What this invalidates

**`.gitignore`'s central claim is false.** It reads: *"Meshes are a pure function
of geometry.py and its arguments, and gmsh is deterministic — E0e and E1c both
confirmed identical inputs give a byte-identical mesh."* They are not. Every
order-2 mesh backing a result is an **irreplaceable artifact**; deleting one
destroys exact reproducibility of whatever rests on it. The tracking policy
("track what cannot be regenerated") therefore now points the other way for
meshes, and needs a decision.

**The mesh cache stopped being an optimisation.** It is the only mechanism that
makes "the same mesh" mean anything across runs, which is why it verifies by
hash rather than trusting its key.

**The recorded "1.3–3.3 MHz cross-mesh error" may be misattributed.** It has been
read as the cost of changing mesh PARAMETERS. If two identical commands span a
comparable range, it is irreducible mesher noise carried by every cross-mesh
comparison in the record. E0kp measures exactly this.

⚠️ **E0e needs re-reading in this light.** It concluded "the SOLVER is exactly
translation-invariant; 100% of the shift is the MESHER" — correct, but it could
not separate *translation* from *irreproducibility* unless it ran a same-position
rebuild as a null control. That control has to be checked before E0e's
attribution stands.

### Threading: do not adopt (yet)

No speedup — 0.92× at 8 threads, 0.96× at 32 — and it adds topology variation
(tet counts moved to 27,608 / 27,626 / 27,708 / 27,557) on top of the node
jitter serial already has. ⚠️ But this geometry meshes in **4.6 s**, which is not
the regime where meshing hurts: E1b's shapes took **5.2 and 10.6 minutes**
because of the 1.0–1.5 mm torch walls. The speedup question is unanswered where
it matters and must be re-tested there before being closed.

### Caveat on the corner/mid-edge split

It assumes gmsh numbers vertices first and that the order-2 build's vertex count
equals the order-1 build's 5,105. Both plausible (same tet count, identical
topology); neither verified. The order-1-vs-order-2 node comparison attempted in
`nodejitter.py` is MEANINGLESS — node ids do not correspond across separate
builds — and was discarded.

---

## 2026-08-20 — ✅ E0kp: the mesher's jitter costs 66 Hz. 🔴 CORRECTION to the entry above

E0m found the mesher non-deterministic and I drew conclusions from that before
measuring what it cost. E0kp measured it. **My hypothesis was wrong.**

Three meshes from the identical command, solved identically at solver order 2:

| mesh | sha | TE011 |
|---|---|---|
| 0 | `0fc68a3e…` | 2.446475343 GHz |
| 1 | `37e7143c…` | 2.446475277 GHz |
| 2 | `bd558c84…` | 2.446475332 GHz |

**Spread = 66 Hz.** Worst across all 8 solved modes = **8 kHz**. Topology was
identical in all three (27,578 tets), and the hashes genuinely differ.

### What this withdraws

🔴 **"The 1.3–3.3 MHz cross-mesh error may be misattributed"** — **WITHDRAWN**.
The jitter is 160× smaller than the *smallest* recorded cross-mesh error. That
error is about changing mesh PARAMETERS, exactly as originally attributed. The
falsifier declared in E0kp was "if the spread is comparable to 1.3–3.3 MHz"; it
came in at 0.0001× that, so the original attribution stands.

🔴 **"Meshes are irreplaceable artifacts" / "`.gitignore`'s claim is false"** —
**OVERSTATED, corrected**. The BYTE-level claim ("gmsh is deterministic … a
byte-identical mesh") is indeed false. But the claim the policy actually rests on
— that a mesh can be regenerated and reproduce the result — **holds to 8 kHz**,
far inside any tolerance this instrument cares about (E0j quotes 0.2 MHz on
TE011, 1.8 MHz across modes). Meshes remain safe to treat as regenerable and safe
to leave untracked. The `.gitignore` rationale needs its *reason* corrected, not
its *decision*.

🔻 **"The mesh cache stopped being an optimisation"** — **downgraded**. It is an
optimisation, and a good one (saves 5–10 min per E1b re-run). It is not required
for correctness, because rebuilding reproduces the physics to 8 kHz.

### What stands

- gmsh is genuinely non-deterministic in node POSITION at geometric order 2:
  2,540 nodes move, up to 46.5 µm, 8.8 µm rms, and 816 of them are corner nodes.
- It is deterministic in TOPOLOGY, and the resonance is set by topology plus the
  overall shape, not by where individual nodes sit inside the volume.
- Geometric order 1 is bit-identical; the instability enters with order 2.

🔑 **The lesson is about my sequencing, not the mesher.** A 46 µm geometric
instability sounds alarming and is, in frequency, 66 Hz. I wrote three
consequences into the record — one invalidation, one policy reversal, one
"infrastructure not optimisation" — from the *existence* of an effect before its
*magnitude* was known. The measurement took one rig and eight minutes. This is
the same error as Q_ext turning a 21-point power gap into a "98× deficit":
measure the outcome, not the mechanism.

---

## 2026-08-21 — ✅✅ E0f2: geometric error is now PREDICTABLE from closed form, to 5%

E0f held the solver at order 1, where E0g later measured 12–17 MHz of
mode-dependent error — larger than the geometric effect it was resolving. Re-run
at solver order 2, with an analytic prediction declared before the run.

### E0f's conclusion is rehabilitated, and sharper than it looked

At **solver order 2**, Δ from the closed form across 11 modes:

| geometric order | worst Δ | TE011 | median \|Δ\| |
|---|---:|---:|---:|
| 1 | 3.570 MHz | 1.664 | — |
| **2** | **0.361 MHz** | **0.058** | **0.084 MHz** |
| 3 | 0.370 MHz | 0.059 | 0.086 MHz |

Geometric order 2 is the right choice — now established rather than assumed. The
exactly-degenerate TE011/TM111 splitting (true value 0) reproduces to 14 kHz.

🔴 **Falsifier 3 fired**: order 2 vs 3 differ by **25.9 kHz**, above the 8 kHz
mesher floor (E0kp). So E0f's "order 2→3 changes nothing" was slightly too
strong — the residual is real, not noise. It is also 0.026 MHz, negligible
against the 0.2–1.8 MHz working accuracy. Real and irrelevant.

### 🔑 The faceting model works

`physics.faceting_shift_mhz` — inscribed N-gon, equal-area radius
`sqrt((N/2pi) sin(2pi/N))`, frequency responding only through the radial share of
f² — predicts the geometric-order-1 error with no simulation in it.

Using the mesh's **measured volume deficit** (0.2534%, a_eff/a = 0.99873214):

| mode | predicted | measured | ratio |
|---|---:|---:|---:|
| TM010 | 1.403 | 1.455 | 1.037 |
| TM110 | 2.235 | 2.309 | 1.033 |
| TE111 | 0.481 | 0.504 | 1.050 |
| TM011 | 0.767 | 0.811 | 1.057 |
| TE011 | 1.612 | 1.664 | 1.032 |
| TM020 | 3.220 | 3.570 | 1.109 |

**mean 1.053, sd 0.027.** Scale-free check, independent of any calibration:
measured TM020/TE011 = 2.146 against predicted 1.997 (radial shares 1.000 /
0.520).

⚠️ **First pass was 1.36× off, and the fault was MY INPUT, not the model.** I
estimated N = 2πa/h_air = 42.6; `geometry.py` sets `MeshSizeFromCurvature = 12`,
which refines the curved wall below the nominal air size. Measured N_eff = 50.9 —
**1.19×**, against the 1.17× predicted from that hypothesis before measuring.

### 🔴 "Count the boundary edges" is not well-defined, and that matters

| method | N |
|---|---:|
| volume deficit | **50.9** |
| median azimuthal edge step | 86.9 |
| distinct azimuthal node positions | 157 |

157 distinct θ among 365 wall nodes = **2.3 nodes per position**. The barrel is
an unstructured triangulation, not a prism: nearly every node has its own angle,
and there is no regular polygon to count. The edge-based numbers measure edge
obliquity and scatter, not faceting. **Volume is the only instrument that
measures the quantity the model is about**, which is why it is the one that
agrees.

### Residuals, unexplained

- systematically **5% low**, not scattered about 1.0 — something small is
  unmodelled; equal-area treats the deficit as a uniform radius change when it is
  concentrated between nodes.
- TM020 at 1.109 against 1.03–1.06 for the rest: a slight trend with radial order.
- **TE121 is −2.345 MHz at geometric order 1** — the only negative of 11 modes,
  and outside the six the model covers. Either a mode mis-assignment at order 1
  or something the inscribed-polygon picture misses. Unexplained; E0f's original
  "signs were mixed" may have been partly this and partly solver contamination.

### What this buys

Geometric order-1 error is **predictable before meshing**. Mesh sizing for a
target accuracy becomes a calculation instead of a sweep — and it is a closed
round trip: known physics → simulation → back to known physics, which is the
check the old programme never had.

---

## 2026-08-21 — 🔻 E1 RETIRED. The design point survives as a calculation, not a result

E1 and everything after it is removed: `e1_design_analytic.py`, `e1b_drive.py`,
`e1b_analyse.py`, `recover_e1b_manifest.py`, all E1 configs, meshes, sidecars,
results and postpro. 64 MB. The rig logs are kept — they carry criteria declared
before each run, which a re-run cannot reproduce.

**Nothing was lost, because the only durable output was analytic.** The two
aspect-ratio candidates are a three-line calculation against `physics.py`, not an
experimental finding — solving TE011 = 2.45 GHz gives

| L (mm) | a (mm) | D/L |
|---:|---:|---:|
| 88.53 | 103.244558 | 2.3324 |
| 120.00 | 86.743283 | 1.4457 |

both landing on 2.450000000 GHz. E1a recorded 103.245 and 86.743. Regenerable in
seconds, forever, with no solver.

⚠️ **Carry a and L ONLY.** The E1b rig's geometry is NOT carried: it had
`viewport = [10.0, 25.0, 108.0]` and `trap = [10.0, 25.0, 288.0]` live by
default, breaking axisymmetry, which nobody asked for and which arrived when R98
changed a default. Any new geometry switches apertures on deliberately, behind a
gate like E0's.

### What E1 established, collapsed to its conclusions

- 🔴 **Endpoint pairing cannot track a mode across a large perturbation.**
  Frequency, energy-fraction signature, and ordering all fail for one structural
  reason: TM020 moves ~150–790 MHz through 50–100 MHz spacing, so modes must
  cross. Mode identity across a material change needs CONTINUATION — small steps
  where each shift is far below spacing — not a comparison of two endpoints.
- 🔴 **The rig changed two materials at once** (torch 1→11.6 AND filter 1→3.78),
  so no shift it produced was attributable. The prediction covered the torch
  only. A loading experiment must move one dielectric at a time.
- 🔑 **TM020 is not perturbed by the torch, it is rebuilt.** 3.6–4.9% of its E
  energy sits in the tubes; first-order theory predicts −486 to −786 MHz, i.e.
  19–26% of f0 — far outside the regime where the perturbation ratio it was being
  tested against is even defined.
- 🔑 **A dielectric end-cap filter may be the wrong mechanism.** It is what made
  the measurement two-variable. A circumferential GROOVE at the barrel/end-cap
  seam separates TE011 from TM111 geometrically — it interrupts the axial wall
  currents TM111 needs while TE011's are purely azimuthal there — and adds no
  dielectric loading or loss. Worth trying before reintroducing a material filter.

---

## 2026-08-21 — 🔴 CORRECTION: nine rigs measured the WRONG degeneracy, and Q is a mode fingerprint

E0q solved with a lossy wall and 14 modes, which put three modes at 2.444 GHz
with their Q values:

| f (GHz) | Q at Al | |
|---:|---:|---|
| 2.44432 | 18,034 | TM111 (a) |
| 2.44433 | 18,031 | TM111 (b) |
| **2.44446** | **36,548** | **TE011** |

**TM111 is m=1 and therefore DOUBLY degenerate** — cos φ and sin φ. Every rig
computed the splitting as the gap between the two modes NEAREST the exact TE011
frequency, and both of those are TM111 polarisations. Nine rigs, identical line,
copy-pasted:

```python
n = sorted(res[t], key=lambda x: abs(x - EX["TE011"]))[:2]
```

So "TE011/TM111 splitting" in this record has always meant **TM111's internal
polarisation splitting**.

### Corrected, from SAVED data — no re-solving

| | reported | corrected | |
|---|---:|---:|---|
| solver order 1 | 1.20 MHz | **12.19 MHz** | 10.1× |
| order 2, fine | 0.0145 | **0.0697** | 4.8× |
| order 2, translation/rotation | 0.001–0.021 | **0.050–0.082** | up to 60× |
| order 2, coarse mesh | 0.042 | **0.539** | 12.8× |

Every rig saved its full mode list, so `resplit.py` recomputed all of it offline
in under a second. **The driver/analysis split, built for E1b, paid off on an
unrelated bug in nine other rigs.**

⚠️ **No conclusion changes.** Order 2 still beats order 1 — by 175× now, not
86×. E0e's translation invariance is untouched (origin and shifted both give
0.0697 exactly). The instrument is slightly worse than the spec claimed and still
far inside anything that matters. What was wrong was a labelled number, in the
flattering direction.

### 🔑 Q is a mode fingerprint, and a better one than energy fractions

TE011 has **2.03× the Q of TM111** — no axial wall currents. That separates a
pair which is EXACTLY degenerate in frequency (χ′₀₁ = χ₁₁) and which no
frequency measurement can ever resolve. It is already in `eig.csv`, free with
every lossy solve. E1b's signature matching failed because energy fractions move
under the perturbation being measured; Q is a property of the mode's current
distribution and is far more stable.

`eigmodes.te011_tm111()` now does this with two discriminators:
- **Q**, when the wall is lossy and the values are physically plausible
- **multiplicity**, always — m=1 comes in pairs, m=0 does not, so the two modes
  closest TO EACH OTHER are TM111

⚠️ The plausibility guard exists because the self-test caught the Q branch
firing on PEC noise: a PEC solve reports Q ~1e12–1e15, and the ratio test passes
happily on garbage (6.1e15 > 1.5 × 7.3e13) and then picks the wrong mode. Real
wall Q here is ~1e4; anything outside 1e2–1e7 is rejected.

### The meta-lesson

Nine rigs shared one bug because they shared one copy-pasted line, and it took an
unrelated experiment — measuring Q — to expose it. The fix is now in ONE place
that has its own self-test. A pattern repeated nine times is nine chances to be
wrong identically and no chance to notice.

---

## 2026-08-21 — ✅ E0l AT PRODUCTION SIZE: 27.7x at 32 ranks. The fan-out plan is dead

The original E0l measured a **10.7 s** solve. Real solves are **106 minutes at
1 rank** — roughly 600x the work — and the scaling is completely different.

| ranks | seconds | speedup | efficiency | TOY efficiency |
|---:|---:|---:|---:|---:|
| 1 | 6385.9 | — | — | — |
| 2 | 3301.3 | 1.93× | 97% | 92% |
| 4 | 1665.8 | 3.83× | 96% | 82% |
| 8 | 881.0 | 7.25× | 91% | 66% |
| 16 | 438.9 | 14.55× | 91% | 55% |
| **32** | **230.3** | **27.73×** | **87%** | **37%** |

Throughput on 32 cores, with the measured 10 GB/solve memory ceiling applied:

| | solves/hr | |
|---|---:|---|
| **1 × 32 ranks** | **15.6** | simple, no scheduler |
| 2 × 16 | 16.4 | +5% |
| 4 × 8 | 16.3 | +4% |
| 32 × 1 | 18.0 | **impossible** — 320 GB |

🔑 **DECISION: one solve at 32 ranks.** Fan-out buys 4–5% for a scheduler, a
memory guard, and a new failure mode.

⚠️ **This reverses a conclusion I argued for hours.** On the toy numbers, 32
ranks looked 37% efficient and fan-out looked like a 1.8× win worth building
machinery for. The whole difference is problem size. **Measure the scaling of the
work you actually run** — a benchmark 600× too small does not merely lose
precision, it inverts the answer.

✅ **TE011 = 2.4444433 at every rank count, spread 0.0000 MHz.** Rank count is not
a hidden variable, now confirmed at solver order 2.

### Two defects found in the re-run

🔴 **`proc.kill()` kills only the bash wrapper.** The launch tree is
`palace (wrapper) → prterun → palace-x86_64.bin ×N`, so killing the rig orphans
`prterun` and every rank to PPID 1. Four ranks ran 20 minutes after E0v killed
this rig, and `reap.py` printed "no orphaned palace ranks" throughout because it
only looked for ranks whose OWN parent was init. Fixed with
`start_new_session=True` + `os.killpg`; `reap.py` now walks the full ancestry.

🔴 **The PRIOR merge happened after the summary table**, so every speedup and
efficiency cell printed `NaN` — the -np 1 reference was not in `rows` when the
table was built. Same shape as R110 (a baseline nobody reads) and R101 (a flag
that never reaches the solver): a value that arrives after the thing that
consumes it.

---

## 2026-08-21 — ✅ H1 RESOLVED: D/L = 1.525, a = 88.00 mm, L = 115.42 mm

Neither original candidate. Four axes, three analytic and one measured.

| D/L | a mm | L mm | TE011 Q | TM111 Q | ratio | rival sep | bore coupling (R=12) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.200 | 83.16 | 138.60 | 46,220 | 21,961 | 2.10 | 42.9 | 0.466% |
| 1.350 | 85.29 | 126.35 | 45,547 | 21,081 | 2.16 | 136.6 | 0.423% |
| 1.446 (B) | 86.75 | 119.98 | 44,993 | 20,602 | 2.18 | 246.1 | 0.395% |
| **1.525** | **88.00** | **115.42** | 44,384 | 20,256 | 2.19 | **332.7** | 0.374% |
| 1.700 | 90.96 | 107.01 | 42,823 | 19,586 | 2.19 | 244.0 | 0.328% |
| 2.000 | 96.50 | 96.50 | 39,736 | 18,713 | 2.12 | 89.3 | 0.261% |
| 2.332 (A) | 103.24 | 88.54 | 36,308 | 18,037 | 2.01 | 76.4 | 0.200% |

**Why 1.525 over B (1.446)**: separation +35%, Q −1.4%, coupling −5%. Separation
dominates by an order of magnitude, and 1.525 is the max-min **stationary point**,
so it is first-order insensitive to machining tolerance on a and L.

**Why not lower**: 1.350 buys +2.6% Q and +13% coupling for **−59% separation**.

🔴 **Candidate A is beaten on every axis** — 23% of optimal separation, lowest Q
(36,308), half the bore coupling, and sitting on the shoulder of a TM210 pole
(11.5 MHz at D/L 2.20), so tolerance-sensitive as well.

### The cross-check is what makes this trustworthy

The sweep ran at **sf 1.5 (~26k elements)** because Q is used in RATIO. That
choice was **under test, not assumed**: the D/L 2.332 point had to reproduce
E0q's fine-mesh (83k) TE011 Q of 36,548. It returned **36,308 — −0.7%**. A
26k-element mesh reproduced an 83k-element Q to under a percent.

✅ **Falsifier passed**: TE011 Q exceeds TM111 Q at every point (2.01–2.19×). The
mode identification held across the whole sweep, which matters because
`eigmodes.te011_tm111` used Q as its discriminator here.

### Two axes that came out of the analysis, not the solves

**Bore coupling.** TE011's E is a torus at r = 0.4805a, zero on axis AND zero at
the wall (J₁(χ′₀₁) = J₁(χ₁₁) = 0 — the same Bessel coincidence that creates the
TM111 degeneracy). Lower D/L means smaller a, so the torus sits closer to the
axis and any given bore captures more.

🔑 **But bore RADIUS is the dominant lever, not aspect ratio.** D/L moves coupling
2× across its usable range; bore radius moves it **30×** (0.10% at R=8.5 mm to
2.8% at R=20 mm). Gas flow scales as R², so the constraint chain is
**slm ceiling → bore radius → coupling → required input power**, with aspect
ratio a second-order correction. ⚠️ The 8.5 mm bore is inherited from the
suspect record and is a DESIGN VARIABLE, not a boundary condition.

### 🔴 My configuration error, and what it cost

First launch used `sf 0.96` and `target 1.05` with n=12–14 — copied from the E0
rigs without checking their cost for THIS geometry. The longer, narrower shapes
mesh to 110–120k elements (not E0's 83k), and a shift-invert spanning 1.05→2.6
GHz solves a dozen eigenvalues when three are wanted. **Over an hour per point**;
killed at 89 minutes on point 2 of 7. Retargeted to `target 2.40, n=8, sf 1.5`:
the same measurement in **~2 minutes a point**, and the cross-check proves it
lost nothing.

---

## 2026-08-21 — ✅ H2: the groove works, and λ/4 is the depth to AVOID

⚠️ **Transcribed from the run log, not from a result file.** The rig was stopped
before it wrote `h2.result.json`, and the instance was lost to what looks like a
spot reclamation shortly after. These numbers exist here and in
`postpro/h2_*/eig.csv` on the EBS volume. Landing them here first.

Bare cavity at H1's D/L 1.525 (a=88.00, L=115.42), groove width 5 mm, σ=3.5e7,
solver order 2, sf 1.5. Each row against the gd=0 control.

| depth mm | d/λ | TE011 GHz | TM111 GHz | splitting | Q_TE011 |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 2.45086 | 2.45013 | 0.72 MHz | 44,383 |
| **10** | 0.082 | **2.45100** | 2.38675 | **64.25 MHz** | **44,256** |
| **20** | 0.163 | **2.45084** | 2.34006 | **110.77 MHz** | **44,364** |
| 27 | 0.221 | 2.29947 | 2.07661 | 222.86 | 3,295 |
| 30.59 (λ/4) | 0.250 | 2.17077 | 1.98874 | 182.03 | 2,985 |
| 34 | 0.278 | 2.06306 | 1.94158 | 121.48 | 2,828 |
| 42 | 0.343 | 2.01335 | 1.86270 | 150.65 | 8,730 |

### The shallow regime works, and it is enough

At **10 mm**: TM111 pushed **64.25 MHz** — clears the 50 MHz LDMOS band — while
TE011 moves **14 kHz** and Q costs **0.3%**. At 20 mm: 110.77 MHz for **0.04%**.

✅ The two-sided verification passes: the groove attacks a current TE011 does not
have (no end-cap surface current, since H at the cap is purely axial so n×H = 0).

### 🔴 My λ/4 prediction was right about the physics and wrong about the goal

λ/4 IS where the stub resonates. That is exactly why it is the depth to AVOID: at
resonance the slot stores maximum energy and **hybridises with the cavity** —
Q collapses 44,000 → ~3,000 and TE011 drops 280 MHz. The useful regime is the
shallow, non-resonant one where the slot interrupts current without storing
energy. **Minimum that clears the band, not maximum splitting.**

### 🔴 The deep rows are MIS-IDENTIFIED, and Q is the tell

A mode with Q = 3,295 cannot be TE011, which has Q ≈ 44,000. Those rows track
lossy slot resonances that appeared in the solver window, so their splittings are
not cavity-mode splittings at all.

### 🔴 And H2b rebuilt E1b's bug

`eigmodes.te011_tm111` takes the three modes nearest the EXACT TE011 frequency.
Once the groove moves TM111 by 64 MHz it is no longer in that triplet, so the
function paired two unrelated modes ABOVE TE011 and returned a confident 2.60631
where H2 had measured 2.38675 for the identical geometry. TE011 was still correct
(Q 44,256), so the Q guard did not fire — it was watching the right mode while
the wrong one was misassigned.

**This is exactly what E1b died of**, rebuilt hours after writing the lesson down:
tracking a mode across a perturbation large enough to move it out of the window
being searched. Fix: identify TM111 by its Q ratio (~0.456× TE011) across the
WHOLE solved window, and refuse to guess when no mode has the right ratio.

### Scaling: two derivations agree with each other and disagree with the data

The slot is a shorted coaxial line, Z₀ = (η/2π)·ln(a/(a−gw)) — 1.4 Ω at gw=2 mm,
3.5 Ω at 5 mm, i.e. strongly capacitive. For a short line
Z_in = jZ₀tan(βd) → jZ₀βd ∝ **gw·gd**, which is the same product the slot VOLUME
FRACTION η = 4·gw·gd/(a·L) predicts. Two independent derivations, same law.

🔴 Both are contradicted by the measurement. gd 10→20 at gw=5:

| | ratio |
|---|---:|
| Z₀·tan(βd) predicts | 2.93× |
| volume fraction predicts | 2.00× |
| **measured** | **1.72×** |

Below both — something saturates, plausibly first-order perturbation failing once
the shift reaches tens of MHz and the mode redistributes into the slot. **Two
points cannot pin an exponent**; the four-point sweep to settle it was in flight
when the instance was lost.

⚠️ A 2 mm × 25 mm slot is not a small-η version of the same thing: βd = 1.284 rad
(73.6°), where tan/βd = 2.64. It is in a different regime, and it cost 58,303
tets against ~33,000 and stalled the linear solve past 248 KSP iterations.

## 2026-08-21 — 🔴 H2b: TM111 was never IN the window. Three of five cases cannot be re-analysed

Follows the mis-pairing note above. Re-analysing the five surviving cases offline
(`postpro/` was the only record — that run predates the checkpoint fix, so no
`h2b.result.json` exists) shows the mis-pairing was a SYMPTOM. The cause is worse.

### Palace returns N modes ABOVE Target. The groove moves TM111 DOWN.

`eigen_cfg(..., n=8, target=2.40)`. The groove pushes TM111 **downward** — that is
the whole point, it clears the 2.40–2.50 LDMOS band — so past about 8 mm of depth
TM111 leaves the solved window through the FLOOR and the solve never contains it.

Measured against the control's TM111 signature, which is certain (gd=0, exactly
degenerate, Q ratio 0.456):

| case | gd (mm) | nearest signature distance | at | verdict |
|---|---:|---:|---:|---|
| exp-eta1 | 5 | **0.0007** | 2.42315 | TM111 present, −27.1 MHz |
| anchor | 10 | 0.0261 | 2.75016 | **absent** |
| exp-eta3 | 15 | 0.0306 | 2.70011 | **absent** |
| exp-eta4 | 20 | 0.0344 | 2.45084 | **absent** (that is TE011) |

A 40× gap between the true match and the best non-match. For the anchor this is
independently confirmed: H2 measured TM111 at **2.38675** for the identical
geometry, and the anchor solve's lowest returned mode is **2.45100**. The mode is
63 MHz below the floor of its own window.

🔴 **`te011_tm111` did not merely mis-pair — it INVENTED a mode that was not in
the file.** It reported 2.60631 because a degenerate pair happens to sit there
with Q ratio 0.472. A function asked for something absent must say so.

### The proposed Q-ratio fix is NOT sufficient on its own

The ratio band around TM111's 0.456 is crowded with unrelated degenerate pairs —
0.472, 0.518, 0.548, 0.582, 0.652 appear in these very solves. The anchor's false
TM111 at 2.6062 has ratio **0.472**, which is *closer* to 0.456 than several true
identifications are. Q ratio narrows the field; it does not decide.

✅ **The signature decides.** TE011 is matched to d ≤ 4e-5 in every case (its
fingerprint is bit-identical across all five, and its Q holds 44,256–44,384, a
0.3% spread across a 20 mm depth sweep). Use `eigmodes.match()` continuation from
the gd=0 control, with Q ratio as a cross-check, and REFUSE when the best distance
exceeds the non-match floor.

### Window sizing is a calculation, not a guess

Closed form at D/L 1.525, a 88.005, L 115.416 — the neighbourhood is EMPTY below
the degenerate pair:

    TE211  2.10447   <- next mode down
    TE011  2.45000
    TM111  2.45000
    TE112  2.78271

**Target 2.25 buys 200 MHz of downward headroom at the cost of zero extra cavity
modes.** Every grooved case should have been solved there.

### 🔴 The 3 mm slot stalls too — the prod-narrow fix did not work

`prod-narrow` was retargeted from 2.0×25.0 to 3.0×16.667 specifically because the
2 mm slot stalled the linear solve. It stalls at 3 mm as well. The case that was
in flight at the reclamation had reached **KSP residual 4.99e-2 after 400
iterations** against `Tol 1e-8` and `MaxIts 500`, and was crawling — 5.02e-2 to
4.99e-2 over its last 8 iterations. It would have hit MaxIts and failed.

The PRODUCT test needs equal η at genuinely different widths, and narrow is where
the conditioning dies. This needs a preconditioner or a different pair of widths,
not a third guess at the width.

**Consequence for the queue**: `control-1.525` and `exp-eta1` are sound and can be
re-analysed. `anchor`, `exp-eta3` and `exp-eta4` must be **re-solved** at
target 2.25 — they are not recoverable from `postpro/`. That is 3 re-solves added
to the 6 already queued, and `prod-narrow` is unresolved independently of both.

## 2026-08-21 — ✅ A COST MODEL for the solver, and a correction to the entry above

### 🔴 Correction: prod-narrow's failure is NLEPS divergence, not a linear stall

The entry above says the 3 mm case "stalled the linear solve" and "would have hit
MaxIts and failed". The conclusion is right and the mechanism is wrong, and the
mechanism is what decides the fix.

Reading the tail of a log is inferring state from a proxy — CONVENTIONS §1, in
the same session that extended §1. The iteration-per-solve distribution says
something else: **4,205 GMRES solves at a median of 1 iteration**, entirely
healthy for 90% of the run, against anchor's 680 solves at median 1. The linear
solver was fine.

What actually failed is the **nonlinear** eigenvalue iteration:

    80 NLEPS (nconv=4, restart=1) residual norm 1.237526e-01
       NLEPS Armijo backtracks=9, alpha=1.953e-03

Four of eight eigenvalues converged, then the residual began **increasing**
(1.2289 → 1.2300 → 1.2315 → 1.2332 → 1.2352 → 1.2375) with the Armijo line
search collapsed to α ≈ 2e-3. The 501-iteration linear solve at the very end is a
SYMPTOM — a garbage Newton step being handed to GMRES — not the cause. Anchor's
equivalent line reads *"Eigenvalue 7, Quasi-Newton converged in 3 iterations"*.

⚠️ **Letting it run longer would not have finished it.** It was diverging.

✅ Consequence for the fix: **do not swap the linear solver.** A direct solve for
one case and GMRES for the rest would compare two instruments, not two geometries
— and it would not address a nonlinear-iteration failure anyway. The lever that
preserves comparability is the **mode count**: converged eigenvalues do not depend
on how many were requested, so asking for fewer modes cannot change the ones that
do converge, unlike changing the solver. Try target 2.25 with n cut to what the
measurement needs. If NLEPS still diverges, that geometry is outside the
instrument's envelope and belongs out of the design, not forced through.

### The instrument has a cost model, good to ±15%

68 Palace logs harvested. Cost is dominated by ONE line of the timing tree:

| | share of total |
|---|---:|
| **Preconditioner** | **75% median** (68–84% across all 68) |
| Eigenvalue Solve | 0.1–19% |
| Linear Solve proper | 1.6–5.5% |
| Div.-free projection | 0.3–9.5% |

One multigrid setup per run, so this is per-APPLICATION cost: it scales with the
number of KSP iterations, not with setup.

🔑 **t ≈ 454 ns × ND_dofs × total_KSP_iterations** (32 ranks, solver order 2).
Across 53 instance solves the preconditioner term is **338.8 ns/dof/it with only
1.3× spread** (308–414). Predicted vs actual on the largest runs: h2_d34 +5%,
e0cond 0%, e0q_s4e07 −1%, e0q_s2e07 −2%, e0q_s1e07 −4%, h2b_exp_eta3 −5%,
h2b_anchor −10%, e0q_s1e08 −15%. Out-of-sample on prod-narrow, a case it was not
fitted to and which failed: predicted **51 min** for the work done against ~53 min
actual, **4%**.

**ND ≈ 6.44 × tets at order 2** (6.42–6.46 across every solve), so problem size is
known from the mesh. Everything in the model is predictable in advance EXCEPT the
KSP iteration count — and that is exactly the conditioning term.

### 🔴 "Cost varies independently of tets" — resolved, and it was mostly bookkeeping

Same 83,322 tets ranged from 227 s to 21,462 s, a 95× spread, which looked like
the solver being capricious. Decomposed:

1. **Machine and rank count.** The expensive population ran **4 ranks on the
   laptop** (`/home/tanderson/.local/...`); the cheap one **32 ranks on the
   instance** (`/opt/amip/...`). ~25×, and it is pure bookkeeping — the logs say
   so on their first line. Normalised per rank-set, the scatter collapses from
   95× to 1.3×.
2. **Solver order.** p=3 gives 1,556,667 ND dofs against p=2's 534,810 on the
   identical mesh — 2.9×, and the preconditioner cost rides on it.
3. **KSP iterations.** The only genuinely unpredictable term.

⚠️ Comparing wall times across the laptop and the instance was never meaningful,
and the E0l scaling lesson (a benchmark 600× too small INVERTS the answer) is the
same error in a different coat.

✅ **What this buys: a case can be costed before it is queued, and a rig can
refuse.** A case whose KSP total implies hours should say so and stop, rather
than discovering it by reclamation. NLEPS divergence is separately detectable —
`nconv` stops rising while the residual increases — and is worth a guard, because
that failure burned 53 minutes and produced nothing.

## 2026-08-21 — 🔴 NO, convergence cannot be predicted. Three guards tested, three failed

Follows the cost model. Costing a solve turned out to be easy; predicting whether
it will converge is not, and the negative results are worth more than the one
positive.

### Not from geometry

Two failures in thirteen grooved cases, at **opposite extremes** of the parameter
space — `h2_d52` (deepest, 52 mm) and `h2b_prod_narrow` (narrowest, 3 mm) — with
successes interleaved between them: gd=42 converges, gd=52 does not; gw=5
converges, gw=3 does not. Ungrooved cases never struggle (h1 ×7, h2_d0,
h2b_control, exp-eta1 at gd=5: **zero** Armijo backtracks). Grooves deeper than
~10 mm always struggle (196–4,016 backtracks) but usually still converge.

So the groove is what makes the nonlinear eigenproblem hard — mechanistically
plausible, since the slot introduces near-degenerate slot/cavity pairs and a
Newton step across a near-degeneracy is exactly what a line search chokes on. But
"hard" and "fails" are not the same thing, and **two failures at opposite corners
cannot fix a boundary between them**. CONVENTIONS §11, one worse: two points in a
two-dimensional space.

### Not from the solver trace either — and the plausible guards are all wrong

| candidate guard | why it fails |
|---|---|
| nconv stalls for N iterations | `h2b_exp_eta3` **succeeded** with a 604-iteration stall; `h2_d52` **failed** with 614. Overlapping. |
| residual rising K in a row | 146 such windows in `h2b_anchor`, 381 in `h2_d34` — **both converged**. |
| residual ≫ best for the CURRENT eigenvalue | healthy runs legitimately swing **1e6–1e8** within one eigenvalue's work; the failures sit in the same range. 8 false positives of 11 at every threshold. |

⚠️ The third is the one that looks most principled and is the most dangerous:
resetting the baseline at each `nconv` advance is the physically right framing,
and it still cannot separate the populations.

🔴 **A correction to `solvecost.diagnose()` as first written.** Its
rising-residual check is valid **post-hoc**, reading the end of a finished log
where a healthy run has converged and stopped — end-residual / best-residual is
≤6.1 for all 11 healthy runs and ≥1,152 for both failures, a 190× separation.
Measured **online** the same rule fires constantly on healthy runs. The tool now
says so. A criterion that is sound at one point in a run and nonsense at another
is exactly the kind that gets adopted because it was only ever tested where it
works.

### What DOES work is a budget, and it is a different kind of object

25 converged runs used at most **869** NLEPS iterations. The 2 failures used
**1,445** and **4,114**. A cap of **1,000** catches both with **zero** false
positives across the whole record.

✅ Adopted as `solvecost.NLEPS_BUDGET`, and adopted as a **budget, not a
predictor**: exceeding it is REPORTED as "did not converge within budget", never
a silent drop and never a claim the geometry is unsolvable (§3). ⚠️ The margin is
**1.66×** on **two** failures, so it will eventually be wrong — which is
survivable for a budget and would not be for a predictor.

**Practical effect**: prod-narrow would have been cut at 24% of the run, saving
~40 of its 53 wasted minutes; h2_d52 at 69%. Combined with the cost model, a case
can now be given a wall-clock derived from ND × expected iterations and stopped
when it exceeds it — which is what makes the queue schedulable without being able
to predict convergence at all.

## 2026-08-21 — 🔴 E0k is the only driven data in the record, and all four of its legs are wrong

Prompted by "prior to H2, is there anything that should be re-run driven?".
Surveyed all 69 solves. **Two are driven — `e0k_drv1` and `e0k_drv2` — and
nothing else in the programme has ever had a port.**

### Its S11 was never analysed at all

`postpro/e0k_drv2/port-S.csv` holds a fully resolved resonance, 2,001 points, and
only its centre frequency was ever read. Extracted now:

| | |
|---|---:|
| f₀ | 2.446420 GHz |
| \|S11\| at resonance | −1.170 dB |
| absorbed-power 3 dB width | **97.6 kHz** |
| **Q_L** | **25,060** |
| **β** (undercoupled branch) | **0.0673** |
| Q₀ = Q_L(1+β) | 26,746 |

These are the **first coupling numbers this programme has produced**. INSTRUMENT
lists β, Q_ext and S11 as unmeasured; they were sitting in a CSV.

### But every leg of the measurement is wrong

1. 🔴 **Silver.** Both driven solves used `Conductivity: 6.3e7` — the R110
   template default — while `baselines.json` says aluminium 3.5e7. The other
   non-aluminium solves in the record are E0q's deliberate σ sweep; these are the
   bug. Absolute Q from them is ~34% high.
2. 🔴 **Its eigen counterpart was PEC.** `e0k_eig2` reports Q ≈ 2.1e9 — numerical
   noise, exactly what `eigmodes`' Q discriminator was hardened against. So E0k
   **could not** have compared Q or coupling: *"compared only the resonant
   frequency"* was forced by the configuration, not a scoping decision. There is
   no driven-vs-eigen comparison of Q or coupling anywhere in the record.
3. 🔴 **The rejected geometry.** E0k ran a = 103.70 mm, L = 88.53 mm,
   **D/L = 2.343** — candidate A, which H1 rejected. Every driven number in the
   record describes a cavity that is not the design.
4. ⚠️ **Mode identity unknown.** The loop couples to what it couples to, and
   TE011/TM111 are exactly degenerate at 2.444385 for this geometry. A driven
   solve returns an |S11| dip, not a labelled mode. Which of the pair produced
   this resonance is not established.

### What a re-run buys: the anchor INSTRUMENT says does not exist

INSTRUMENT: *"Absolute Q has no external anchor — only its scaling law. A Q
number is trustworthy in ratio, not in absolute value."*

🔑 **Q₀ from a driven linewidth is a completely different measurement route** from
the eigenvalue's imaginary part — the 3 dB width of the absorbed-power curve with
β from the dip depth, against a complex eigenvalue. Agreement would anchor
absolute Q for the first time. Disagreement would be a major finding. At 54 s per
driven solve this is ~2 minutes of compute to remove a stated limitation.

⚠️ **And there is a factor-of-two flag, stated carefully.** Scaling the measured
Q₀ = 26,746 from silver to aluminium through the verified σ^0.5 law gives
**~19,900**, against the eigen record's 36,548–44,384. This is **NOT yet a
discrepancy**: different geometry, a loop that both perturbs and adds loss, and an
unidentified mode. It is a factor of two that is unresolved *because the two were
never measured on the same footing* — which is the whole reason to put them on
one.

### Nothing else pre-H2 needs driven

The other 67 solves are PEC (40) or aluminium eigen (23). PEC is correct for the
geometry and discretisation studies, since the closed form assumes it. E0q's
σ^0.5 law does not need a driven check — it needs the absolute anchor, which E0k
supplies.

⚠️ One flag, not a re-run: **H1's "bore coupling" is an eigen energy-fraction
proxy for a driven quantity**, and the constraint chain it sits in ends in input
power. It is applied differentially across D/L, which is what this instrument is
good at, and the real load is the plasma (H3), so the comparison is probably
sound. But the word "coupling" is doing work that only a port can do.

## 2026-08-21 — E0k2 ran. F3 FIRED: the anchor is NOT established, and the loop is why

First driven+eigen pair on ONE mesh, ONE wall, at the H1 design point
(a = 88.0045, L = 115.4158, aluminium 3.5e7, order 2, 34,118 tets). Eigen 251 s,
driven 98 s.

### The headline number, and why it does not stand up

| | |
|---|---:|
| Q₀ from the driven LINEWIDTH | **28,208** |
| Q₀ from the EIGENVALUE | **27,214** |
| ratio | **1.037** |

F1's stated threshold was 20% and this is 3.7%. **It still does not anchor
anything**, because two of the three verification criteria failed:

- 🔴 **F3 FIRED: β = 27.52.** The declared limit was 0.5. The loop is not a
  diagnostic probe, it dominates the cavity.
- 🔴 **V3 FAILED: the loop moves the mode 17.60 MHz** from closed form. The
  "the loop is in both solves so it cancels" argument needs a perturbation;
  17.6 MHz is a redesign.

⚠️ **And β does 96.5% of the work in Q₀ = Q_L(1+β)** — Q_L is only 989. So the
agreement is an agreement about the coupling model, not independently about Q.

### The branch was decided by 0.2 degrees

|S11| cannot separate β from 1/β — the dip depth is identical, −0.631 dB for
both β = 27.52 and β = 0.0363. The phase test is what decides, and it returned a
swing of **180.24° against a 180° boundary**.

The measured Q_L does support the overcoupled branch decisively:

    measured Q_L                       989
    Q0_eigen/(1+beta), overcoupled     954    ratio 1.037
    Q0_eigen/(1+beta), undercoupled 26,260    ratio 0.038

⚠️ **But that check uses Q₀_eigen**, so it is self-consistency, not
independence. Two routes agreeing when one of them was resolved using the other
is not an anchor. 🔴 The rig reported "overcoupled" as decided when the
measurement was 0.2° from ambiguous; it now reports AMBIGUOUS in a band around
180° instead of picking a side.

### The mode identification is not trustworthy either, and says so

The loop coupled to **TM111**, at 2.432397 with Q 27,214 — identified by
SIGNATURE against the eigenmodes with distance 0.00035 and a **36.2× margin**,
which is the one part of this that worked cleanly.

🔴 But `te011_tm111` fell back to `how=multiplicity` and returned **TE011 at
2.497500 with Q 15,414 — LOWER than TM111's 27,214.** That inverts the physics
(TE011 has ~2× TM111's Q, no axial wall current) and would fail H1's own
falsifier. The cause is the same 17.6 MHz loop perturbation: it split the
degenerate pair by ~19.5 MHz, so "the two modes closest to each other" no longer
picks a polarisation pair at all. The multiplicity discriminator is only valid
while the splitting is small compared with the mode spacing.

### What this actually establishes

✅ **The rig works, and every declared criterion did its job** — F3 and V3 caught
the defect before a number entered the record, and the signature identification
of a driven dip against eigenmodes is validated at 36× margin.
✅ Driven and eigen CAN be run on one mesh with one wall and compared. E0k could
not do this at all.
🔴 **Absolute Q remains unanchored.** INSTRUMENT's limitation stands.

**Next: re-derive the loop for a = 88.00 mm.** This is CONVENTIONS §6 coming due
exactly where it was flagged and deliberately deferred — 25.8×19.4 mm was sized
where H_r peaks at 0.4805a = 49.83 mm, and here that radius is 42.29 mm. The
same loop gave β = 0.067 at a = 103.70 and β = 27.5 here, a factor of **410**,
which is far too large for a 15% change in radius and is itself worth
understanding before simply shrinking the loop. Target β ≈ 0.1–1, which also
brings the phase swing away from the 180° boundary.

### 🔴 Separately: driven and eigen were describing DIFFERENT cavities

`solveconf.driven` binds the torch material from the mesh sidecar (the R101
fix), and with `--no-torch` that sidecar records **`torch_material = [1.0,
3.5e-05]`** — a vacuum permittivity paired with a LOSS TANGENT, which is
incoherent. `eigen_cfg` assigns plain vacuum to every volume. So the driven
solve carried a loss term the eigen solve did not, on a region holding **9,479
elements, 28% of the mesh** (`--no-torch` removes the torch, not the torch
REGION — confirmed with the new `meshattrs.py`, since the sidecar's attribute
table lists `torch: 2` whether or not anything is there).

For a rig anchoring Q, a stray loss tangent lands directly on the quantity being
measured. E0k2 normalises the driven domains to vacuum and prints every change;
⚠️ the general fix belongs in `solveconf` — its own rule is that a material
bound to something the mesh does not have "describes a model it is not solving",
and vacuum-with-loss is the same class of claim — but that touches every driven
rig and was not this measurement's job.

## 2026-08-21 — 🔑 THE BARREL LOOP SITS ON TE011's H_z NODE. It cannot couple to TE011.

Chasing why one loop gave β = 0.067 at a = 103.70 and β = 27.5 at a = 88.00.

🔴 **First, a misunderstanding to retire.** I called that "a factor of 410 for a
15% change in radius" and set it up as a mystery needing explanation before the
loop could be re-derived. Wrong on both counts, as the user pointed out:

- **E0k predates H1.** They are not two versions of one cavity. E0k ran
  a = 103.70 / L = 88.53 (**D/L 2.343 — the candidate H1 REJECTED**); E0k2 runs
  the H1 answer, a = 88.00 / L = 115.42 (D/L 1.525). The LENGTH changed 30% and
  the aspect ratio 35%. Quoting the radius alone picked the one dimension that
  moved least and made a different design look like a perturbed one.
- ⚠️ **Comparing a measured quantity across two programme epochs is comparing
  two machines.** The rule already exists for wall times (laptop vs instance)
  and for solver order; it applies to coupling too.

### The actual geometry, and it is decisive

`geometry.py` builds every barrel-loop cylinder at **z = 0**, and `z0 = -L/2`,
so the loop lies in the **cavity mid-plane**. Its legs run radially (x from
a+2 mm to a−ld) and its crossbar along y, so the loop lies in the x–y plane, its
normal is **ẑ**, and it links **H_z**.

TE011's H_z ∝ J₀(χ′₀₁·r/a)·cos(π(z+L/2)/L). At z = 0 that cosine is **exactly
zero**:

| loop z (fraction of L from mid-plane) | H_z factor |
|---|---:|
| **0% — where the loop actually is** | **0.0000** |
| 5% | 0.1564 |
| 15% | 0.4540 |
| 25% | 0.7071 |
| 40% | 0.9511 |

🔑 **The flux is identically zero regardless of loop size, width or depth.** The
same is true of the wall current: TE011's barrel current K ∝ cos(π(z+L/2)/L) is
also zero at mid-plane. The loop sits where TE011 has neither tangential H nor
surface current — the worst possible place to couple to it.

✅ **This is geometry-independent** — true for E0k and E0k2 alike — so whatever
either loop coupled to was a residual, and a residual near a node is precisely
the kind of quantity that swings orders of magnitude between designs. **The 410×
needs no further explanation.**

⚠️ It also means E0k's β = 0.067 was never a measurement of TE011 coupling, and
E0k2's β = 27.5 is coupling to something else — consistent with the mode
identification having been untrustworthy in that run.

⚠️ The R69 comment *"1.39× the |H_z| a barrel loop sees at the wall"* compares
PEAK values; it is not the field at the loop's own plane. Read as a statement
about the barrel loop as built, it is misleading.

### Consequence: use the CAP loop, do not shrink the barrel loop

R69 already built the right instrument and its own comment says why: *"Linking
H_r rather than H_z is the point. On the cap H_r peaks at r = 0.4805a ... more
importantly the RADIUS is free, which it never is on the barrel."* For TE011
H_r ∝ sin(π(z+L/2)/L), which is MAXIMUM at mid-plane, and `--loop-cap r` makes
the radius a continuous coupling knob — exactly what is needed to place β in the
0.1–1 window the anchor requires.

The alternative, moving the barrel loop off mid-plane in z, is not currently
expressible: the z = 0 placement is hard-coded, not a flag.

## 2026-08-21 — E1 deletion completed, and the cost model does not depend on it

The record said the E1 series was deleted on 2026-08-21, but only the two
drivers had gone: 24 items and ~0.9 MB of `e1b*`, `e1c*`, `e1cc*` results, rig
logs, Palace logs and `postpro/` remained tracked. The tree and the record
disagreed, and that is the kind of drift that gets rediscovered. Removed in
full; nothing references them except `ops/cleanremote.sh`, which deletes them by
design.

⚠️ **They were load-bearing for one thing**, so it was checked rather than
assumed: `e1b_B_load`, `e1b_B_tran` and `e1cc_sf2p0` were among the logs behind
the solver cost model. Re-derived after deletion:

| | before (53 solves) | after (51 solves) |
|---|---:|---:|
| preconditioner | 338.8 ns/dof/it | **339.9** |
| total | 454.5 ns/dof/it | **456.3** |

**0.4%.** `solvecost.NS_PER_DOF_ITER = 454.5` is left as it stands — re-fitting
for 0.4% would be churn, and the constant's stated spread is 1.3×.

⚠️ The TOTAL spread widened from 2.5× to 4.5×, which is the E0k2 solves
ENTERING the set, not the E1 ones leaving: a DRIVEN solve does different work
(no NLEPS, 8 adaptive frequency samples) and does not belong in a fit calibrated
on eigenmode solves. The harvest should separate them by problem type before the
constant is quoted again.

## 2026-08-21 — 🔴 RETRACTION: the barrel loop is at the H_z MAXIMUM, not a node

The entry above — *"THE BARREL LOOP SITS ON TE011's H_z NODE"* — **is wrong.** I
had TE011's axial dependence inverted. Retracted in full.

### The correct fields

TE011 with caps at z = 0, L. Generating component E_φ ∝ J₁(χ′₀₁r/a)·sin(πz/L):

    H_z ∝ J₀(χ′₀₁ r/a) · sin(πz/L)    ZERO at the caps, MAXIMUM at mid-plane
    H_r ∝ J₁(χ′₀₁ r/a) · cos(πz/L)    MAXIMUM at the caps, ZERO at mid-plane

Boundary conditions confirm the assignment: H_z is normal at the caps and its
sin() vanishes there; H_r is normal at the barrel and J₁(χ′₀₁) = 0 by the
definition of χ′₀₁. I had written sin and cos the other way round, which
satisfies neither.

🔑 **Independent check, and it is exact.** R69's comment says H_r *"peaks at
r = 0.4805a and is 1.39× the |H_z| a barrel loop sees at the wall"*. From the
forms above, H_r peaks where J₁ does (1.8412/χ′₀₁ = **0.4805**), and

    |H_r|cap,peak / |H_z|barrel,mid = [(π/L)J₁(1.8412)] / [(χ′₀₁/a)|J₀(χ′₀₁)|]
                                    = 1.3875  at a = 103.70, L = 88.53

against the quoted **1.39**. The comment was correct and I misread it as a claim
about the field at the barrel loop's own plane.

⚠️ **So the barrel loop at z = 0 sits at TE011's H_z MAXIMUM** — a well-chosen
placement, not a defect. Its β = 27.5 is a big loop coupling strongly at a field
maximum, which is exactly what it looks like.

### What that leaves of the 410×

Nothing needing a mechanism. Per CONVENTIONS §4b, E0k and E0k2 are different
cavity DESIGNS, and beyond that **there is no reliable β pair to compare**:
E0k2's β came from a run whose coupling branch was ambiguous (phase swing 180.24°
against a 180° boundary) and whose mode label was untrustworthy. Two numbers, one
of them not trustworthy, from two different machines.

### 🔴 And a correction to H2's stated rationale

HYPOTHESES says *"TE011 has NO end-cap surface current (H is purely axial there,
so n×H = 0)"*. **At the cap H_z = 0 and H_r is maximum**, so H is purely RADIAL
there, and the cap current K = ẑ × H_r r̂ = H_r φ̂ is nonzero and **AZIMUTHAL**.

The groove still works, and the measurement stands (TM111 +64 MHz, TE011 14 kHz)
— but the mechanism is not "TE011 has no cap current". It is that an ANNULAR
groove runs PARALLEL to TE011's azimuthal cap current and does not cut it, while
TM111's RADIAL cap current must cross it. Same discriminator, different reason,
and the corrected version also explains why TE011 moves 14 kHz rather than zero.

## 2026-08-22 — 🔑 SLATER is the missing model for H2, and the measurement was never taken

Prompted by the user's reading on groove perturbation theory. It resolves why
both of H2's candidate scaling laws failed, and the test costs no extra compute.

### Why both models missed, and in a predictable direction

`Z₀·tan(βd)` predicted **2.93×**, slot volume fraction **2.00×**, measured
**1.72×**. Both reduce to the PRODUCT `gw·gd`, and both therefore assume the
field is **UNIFORM across the slot**. It is not: the far end of a deep slot
carries less field, so a field-weighted integral grows **sub-linearly** in depth.
That is the right sign for a measurement that came in BELOW both — the
"something saturates" noted when the discrepancy was first recorded.

### Slater gives a parameter-free prediction, computable per solve

For a small wall deformation of volume ΔV,

    Δf/f₀ = -(1/W) ∫_ΔV (μ|H₀|² - ε|E₀|²)/2 dV

At resonance U_mag = U_elec = W/2, so in Palace's normalised energy bins this
collapses to **one number per mode per solve**:

    Δf/f₀ = -( p_mag[groove] - p_elec[groove] ) / 2

No fitted constant, no free parameter. And it is falsifiable against what H2 has
already measured — the anchor groove, 5.0 × 10.0 mm at D/L 1.525, η = 0.0197:

| mode | measured shift | Slater then REQUIRES (p_mag − p_elec)_groove |
|---|---:|---:|
| TM111 | −63.3 MHz | +5.167e-02 — **2.62× the volume share** |
| TE011 | −0.014 MHz | +1.14e-05 — **magnetic and electric CANCEL to 1e-5** |

Two sharp predictions. TM111's groove energy must exceed its volume share
because the slot sits at the cap corner where TM111's radial current is strong;
TE011's two terms must cancel almost exactly, which is the same physics as its
14 kHz immunity stated in energy rather than in current.

### 🔴 The measurement exists as a flag and was never switched on

`geometry.py --tag-groove` makes the slot its own volume (attribute 13). R81
built it precisely for this — *"the fraction of a mode's energy inside the slot
separates 'cavity mode the groove perturbs' from 'mode the groove created'"* —
and it **defaults to False**. Neither H2 nor H2b passed it, so no grooved solve
in the record carries a groove energy bin, and the depth law is still open after
two rigs and eleven cases.

⚠️ Note `eigen_cfg` builds its own Energy list from the mesh's volume
attributes, so it picks the groove up AUTOMATICALLY once tagged — the gap was
only ever the missing flag. (`solveconf.driven` hardcodes index 80 for it; the
two number their bins differently, which is why `e0k2_anchor` forces one shared
list on both configs.)

✅ **Added to `h2b_groovescale.py`**, with `groove_slater()` returning the
predicted Δf/f₀ per mode alongside the measured one. Costs nothing: same mesh,
same solve, one more energy bin.

### What this does and does not buy

✅ A **forward predictor good in one solve**, replacing a 2-point power law that
CONVENTIONS §11 says cannot establish an exponent anyway.
✅ A measurement of **where the perturbation picture breaks** — Slater is the
small-groove limit, so the depth at which it starts to fail IS the boundary
between "slot as perturbation" and "slot as resonator". H2 found that boundary
the hard way at λ/4 = 30.6 mm, where Q collapsed to ~3,000.
🔴 It does **not** invert. Solving for (w, d) given a target Δf remains a root
of a transcendental determinant, so the sweep stays a sweep. What changes is
that each point now reports a model prediction beside its measurement, so the
sweep tests a law instead of just fitting one.

## 2026-08-22 — 🔑 The anchor needs the GROOVE: a degenerate pair cannot be fitted as one resonance

From the user, on seeing the cap-loop candidates return Q₀ ≈ 20–25k against a
bare-cavity TE011 Q₀ of 44,384.

### The stated direction is wrong, and H2 already measured it

*"Q should drop by ~half once we detune TM111"* — no. **Detuning TM111 costs
TE011 0.3% of its Q**, measured directly by H2 at the 5 × 10 mm groove: TM111
moves 64 MHz, TE011 moves 14 kHz, Q cost 0.3%. TE011's Q is set by its own wall
currents and moving its degenerate partner away does not touch them. The
measured Q should if anything go **UP** once TM111 leaves the band, because the
probe then sees TE011 alone.

The factor of ~half is about WHICH MODE, not about anything changing:
TE011 Q = 36,548, TM111 = 18,032. A loop-coupled mode at 20–25k is TM111-shaped
from the start.

### 🔴 But the underlying observation is right, and it invalidates the rig as built

TE011 and TM111 are **EXACTLY degenerate** at 2.45000 in an ungrooved cavity —
χ′₀₁ = χ₁₁, identically, at every D/L. The cap loop shifts the resonance only
**0.37–0.44 MHz** from closed form, so it is a weak perturbation and splits the
pair by well under a MHz. Against measured loaded linewidths of **184–306 kHz**
that is at best a few linewidths and possibly less than one.

**So the driven dip is plausibly TWO OVERLAPPING LORENTZIANS, and a
single-resonance 3 dB fit returns neither Q** — a systematic sitting directly on
the quantity the anchor exists to measure. It would also explain a Q that
matches neither 36,548 nor 18,032 cleanly.

✅ **Fix: run the anchor WITH the groove.** H2's validated 5 × 10 mm gives
200–300 linewidths of separation for a 0.3% Q cost on the mode being measured.
Added to `e0k2_anchor.py`, along with **V4**: the splitting must exceed 10 loaded
linewidths or the anchor is declared contaminated rather than reported. The
eigen solve measures that splitting directly, so V4 is checked, not assumed.

🔑 `--tag-groove` rides along free, making Slater's numerator a by-product.

### The general rule this exposes

⚠️ **Design variables can be separable while their MEASUREMENTS are not.**

The groove (cap corner, r near a) and the coupling loop (r = 0.4805a) barely
interact physically — by the Slater superposition argument they are independent
design choices. But the groove is a **precondition for the loop's reading to be
interpretable at all**. Separability of the design and separability of the
measurement are different questions, and only the first is answered by disjoint
support.

Practical consequence for sequencing: this argues for FREEZING the groove at
H2's validated 5 × 10 mm and building everything downstream on top of it, rather
than leaving it open as a parameter still being optimised. Its remaining
question — the depth exponent — is a by-product of Slater now, not a blocker.

## 2026-08-22 — 🔴 H2b's gd=0 controls were never a control for the groove

From the user. Correct, and quantifiably so.

### The reference is analytic, not measurable

χ′₀₁ and χ₁₁ are **the same Bessel zero**, 3.831706 — so TE011 and TM111 are
exactly degenerate at every D/L, and `shape(dl)` solves each geometry to put
TE011 at 2.45. **The ungrooved TM111 is at 2.45000 by construction.** Solving for
it measures nothing about the groove.

| | |
|---|---:|
| effect being measured | 27–63 MHz |
| absolute accuracy, worst mode | 0.361 MHz → **under 1.4% of the effect** |
| differential accuracy | 0.020 MHz → 0.07% |
| price of the controls | **3 of 11 cases, 27% of the sweep** |

⚠️ **And it can be WORSE than the analytic value, not merely redundant.** In the
ungrooved case the pair is degenerate to within mesh asymmetry (~0.070 MHz), so
`te011_tm111` must separate two near-identical modes by Q — and that assignment
error propagates into every shift referenced to it. The control spends its
differential precision resolving a degeneracy the closed form gives as exactly
zero, in the single configuration where mode identification is hardest.

✅ Replaced by `REFERENCE_GHZ = 2.45`. One analytic reference serves all three
aspect ratios, since every geometry is built to put TE011 there — which also
makes the transfer test cleaner.

### The freed cases go to depth, and the old fit was doomed for a deeper reason

Same 11-case budget, now **7 depth points (2.5–20 mm) instead of 4, no controls**.

🔑 The existing measurements already show why two points could never have settled
the scaling — **it is not a power law at all**:

| | ratio | implied exponent |
|---|---:|---:|
| gd 5 → 10 | 2.34× | **n = 1.22** |
| gd 10 → 20 | 1.72× | **n = 0.78** |

The exponent FALLS across the range. There is no single n to fit. That is
precisely the signature of a field-weighted integral saturating as the far end
of a deeper slot contributes less — Slater's behaviour, and the mechanism behind
"something saturates" recorded when the discrepancy was first found.

⚠️ CONVENTIONS §11 says two points cannot establish a scaling law. This case is
sharper than that: two points cannot establish a law that **does not exist**, and
fitting an exponent to them produced a number (1.72×) that was then compared
against two models predicting a constant exponent. All three were answering the
wrong question.

## 2026-08-22 — E0k2 with a cap loop: two routes agree to 5.4%, and a new systematic

Cap loop 11.0 × 8.0 mm at r = 0.4805a, no groove, H1 design point, aluminium.
Sizing sweep of four loop areas, then eigen on the chosen one.

| | |
|---|---:|
| β | **0.560** (target window 0.1–1) |
| V3 loop frequency perturbation | **0.40 MHz** (barrel loop: 17.6) |
| branch | undercoupled, phase swing 13.9° — unambiguous |
| signature identification margin | **26×** |
| V4 separation from nearest mode | **26 linewidths** |
| Q₀ from the driven LINEWIDTH | **28,387** |
| Q₀ from the EIGENVALUE | **30,020** |
| **agreement** | **5.4%** |

✅ **Two independent measurement routes to Q₀ agree to 5.4%** — the first time
this programme has had that. The method is validated even though the mode label
is not (below).

### 🔴 RETRACTION: the degenerate-pair BLEND hypothesis was wrong

I argued that the ungrooved cavity's exact TE011/TM111 degeneracy made the
driven dip a blend of two overlapping resonances, and that this explained three
phase-1 anomalies at once. **V4 refutes it**: the dip sits 26 linewidths clear of
its nearest neighbour.

🔑 The mechanism I missed: **the loop splits the degenerate pair at FIRST ORDER
while barely moving its centroid.** It shifts the mode 0.40 MHz from closed form
but splits 2.450399 / 2.453905 by **3.5 MHz** — standard degenerate perturbation
theory, where any symmetry-breaking perturbation splits a degenerate pair at
first order. The loop does its own separating; the groove is not required for it.

⚠️ So the three phase-1 anomalies — β non-monotonic in area (1.50, 0.87, 0.56,
1.85), derived Q₀ climbing 20.0k→30.1k, and none of them near either 36,548 or
18,032 — remain UNEXPLAINED. Do not attach them to the blend story.

### 🔴 NEW: a probe can be weak in FREQUENCY and strong in Q

Q₀ ≈ 29,000 here against a bare-cavity TE011 Q₀ of **44,384** — the loop costs
**~32% of Q** while moving the frequency only 0.40 MHz.

And it is **lossless**: the loop is PEC in the eigen solve, so this is not
conductor loss in the loop. It is the loop distorting the mode and crowding
current onto the finite-conductivity wall near it — the cap loop sits at
r = 0.4805a, which is exactly where H_r peaks and therefore where cap current is
strongest.

🔑 **V3 tested the frequency perturbation and passing it said NOTHING about Q**,
which is the quantity being anchored. Frequency depends on a volume integral; Q
depends on surface currents, and a small obstacle at a current maximum can
concentrate current far out of proportion to its effect on the volume integral.

✅ Consequence: this anchors **"cavity + loop"**, not the bare cavity. The two
routes agreeing validates the METHOD; it does not yet transfer absolute Q to the
design cavity. Needs a **V5: the loop's Q cost, measured directly** by one
loop-free eigen solve at the same geometry (~250 s) and subtraction.

### The mode label is still not trustworthy

`te011_tm111` fell back to `how=multiplicity` and assigned TE011 to
**2.423178, Q = 18,411 — the LOWEST-Q mode of the three** — while calling the
2.450399/2.453905 pair TM111. Its own declared falsifier (TE011 Q > TM111 Q)
fired and the result is labelled suspect, which is the guard working.

The driven dip is the **highest-Q** mode (30,020) and is TE011 by every other
indicator. The multiplicity discriminator fails here for the same reason it
failed in H2b: it assumes the degenerate pair are the two modes closest TO EACH
OTHER, which stops being true once a perturbation splits them by more than the
spacing to their neighbours.

## 2026-08-22 — ✅ V5 ANSWERED: the coupling loop costs 32.4% of Q, and bare Q₀ reproduces exactly

`e0k2_bare.py` — identical geometry, wall and solver to the cap-loop run, loop
removed. 32,531 tets, 164 s.

| | |
|---|---:|
| **bare TE011 Q₀** | **44,384** |
| record (INSTRUMENT, same geometry) | **44,384** |
| TM111 Q | 20,256 |
| q_margin TE011/TM111 | **2.191** (expected ~2×) |
| pair_q_ratio | **1.000** |
| bore-induced degeneracy split | **0.7235 MHz** |
| TM111 polarisation split | 0.0357 MHz |
| **→ 11×8 cap loop costs** | **32.4% of Q** |

✅ **An exact reproduction of the recorded 44,384.** Independent solve, this
session's toolchain, on a number that predates it — the strongest instrument
check in the record.

✅ The repaired `te011_tm111` handled its hardest case: frequencies degenerate to
0.72 MHz, so frequency cannot separate them, and `how=Q` picked TE011 cleanly
with `pair_q_ratio = 1.000` — precisely what two orientations of one mode must
give.

### 🔑 A probe weak in FREQUENCY can be strong in Q — now measured, not argued

The loop shifts TE011 by **0.40 MHz** and costs **32.4% of its Q**. It is PEC in
the eigen solve, so this is not the loop's own loss: it distorts the mode and
crowds current onto the finite-conductivity wall, sitting at r = 0.4805a where
TE011's cap current peaks.

⚠️ **V3 (frequency perturbation) passing said nothing about this**, and V3 was
the only probe-strength check the anchor had. Frequency is a volume integral, Q
a surface-current one.

**Consequence: E0k2 anchored "cavity + loop", not the design cavity.** The 5.4%
agreement between the driven linewidth and the eigenvalue validates the METHOD;
it does not transfer absolute Q to the bare cavity, because the probe moved the
thing being measured by a third.

⚠️ This is a real tension, not a bug: **Q cannot be measured by linewidth without
a probe, and the probe changes Q.** The escape is a weaker probe, but weaker
means a shallower dip and a worse-conditioned β — a trade to be measured, not
assumed.

### 🔴 The sizing-sweep anomaly is now sharper, and still unexplained

With bare Q₀ no longer in doubt:

| loop area | driven Q₀ | fraction of bare Q lost |
|---:|---:|---:|
| 35 mm² | 20,005 | **54.9%** |
| 82 mm² | 24,920 | 43.9% |
| 176 mm² | 28,387 | 36.0% |
| 384 mm² | 30,112 | 32.2% |

**Smaller loops appear to cost MORE Q, monotonically.** That is backwards and it
is not explained.

⚠️ The blend hypothesis is back in play for the SMALL loops only — and this time
with the bare split measured rather than assumed. The bare cavity already splits
the pair by 0.7235 MHz (the bore), and the loop adds splitting with its
asymmetry:

| loop area | est. splitting | vs loaded linewidth |
|---:|---:|---:|
| 35 mm² | ~1.4 MHz | **4.6 linewidths — marginal** |
| 82 mm² | ~2.4 MHz | 12.8 ✅ |
| 176 mm² | 4.2 MHz | 31.4 ✅ (V4 measured 26.0) |

So blending is refuted for the chosen candidate and remains PLAUSIBLE for the
smallest. ⚠️ Plausible is not measured — one eigen solve on the 35 mm² mesh,
which already exists, settles it for ~250 s. Do not adopt the explanation before
running it; that is the mistake this entry's predecessor made.

## 2026-08-22 — ✅ THE "BACKWARDS Q" ANOMALY IS RESOLVED: the loop changes WHICH MODE it couples to

Pressed on the one thing that could not be explained. It was an error in the
comparison, not in the measurement, and fixing it produces a much stronger
result than the one originally sought.

### The resolution

`e0k2_sizeq.py` ran an eigenmode solve on each of the four loop meshes — no
fitting, no coupling model, no branch decision. Matching each DRIVEN measurement
to the mode it actually coupled to:

| loop area | driven f₀ | mode coupled to | its eigen Q | driven-derived Q₀ | agree |
|---:|---:|---|---:|---:|---:|
| 35 mm² | 2.450370 | **TM111** | 21,925 | 20,004 | **8.8%** |
| 82 mm² | 2.450435 | **TM111** | 26,201 | 24,919 | **4.9%** |
| 176 mm² | 2.450405 | **TE011** | 30,020 | 28,387 | **5.4%** |
| 384 mm² | 2.449475 | **TE011** | 31,665 | 30,111 | **4.9%** |

🔑 **A small cap loop couples preferentially to a TM111 polarisation; TE011 only
dominates above ~176 mm².** The driven Q₀ matches the Q of whichever mode was
actually excited, in every case, to 4.9–8.8%.

🔴 **The "backwards trend" was mine**: I compared all four derived Q₀ against
TE011's bare 44,384 when two of them were measuring TM111. Nothing was
backwards; the reference was wrong for half the points. The earlier
single-Lorentzian fit-quality correlation (19.3% → 1.1% rms) is real but is a
SECOND effect, not the cause.

⚠️ The mistake was possible because **phase 1 ran driven solves ONLY**. With no
eigen solve there was no signature match, so nothing identified which mode each
dip belonged to — the rig's own identification machinery existed and was not
reached until phase 2. A driven solve returns an |S11| dip, not a labelled mode;
that was written down and then not applied.

### ✅ Absolute Q is anchored — by four comparisons, not one

**Four independent driven/eigen agreements at 4.9–8.8%, across TWO different
modes and an 11× range of loop area.** The loop's Q cost is irrelevant to this
check: both routes see the same cavity, so it cancels.

Combined with `e0k2_bare` reproducing the recorded **44,384 exactly**, the chain
is complete: the eigenvalue's Q is validated against an independent
frequency-domain extraction, and the bare-cavity number is a direct eigen
measurement.

⚠️ **What this does NOT anchor.** Both routes share one mesh, one wall
conductivity and one solver, so they share any systematic in the WALL-LOSS
MODEL. What is validated is the EXTRACTION of Q, not the surface-impedance
physics behind it. An external anchor still needs a measured cavity, and
INSTRUMENT should say so rather than claiming absolute Q is settled outright.

### Still open, and smaller

TE011's own Q is non-monotonic in loop area — 37,525 / 29,073 / 30,020 / 31,665
for 35 / 82 / 176 / 384 mm², a minimum near 82 mm². The spacing from TE011 to
its nearest TM111 polarisation grows monotonically (0.68 / 1.48 / 3.51 /
9.39 MHz) and `pair_q_ratio` degrades from 1.087 to 1.364, so the loop is MIXING
the triplet rather than merely shifting it.

⚠️ That is a ~9% wobble on a separate question, and it is NOT the anomaly that
was being chased. Reported, not narrated — the rig's own guard said "report the
numbers and investigate, do not narrate" and that stands.

### For the anchor: 176 mm² is the right loop, and why

- couples to **TE011**, not TM111 (needs ≥ 176 mm²)
- **β = 0.560**, inside the [0.1, 1] window (384 mm² gives 1.848, outside)
- Q cost 32.4% — fails V5's 10% threshold, so it still measures cavity+loop

✅ But V5 failing no longer blocks the anchor, because the anchor no longer
depends on the probe being weak: the four-point agreement validates the method
regardless of how much the loop loads the cavity, and the bare Q is measured
separately without any probe at all.

## 2026-08-22 — 🔴 Where driven-only mode identification is NOT nailed down

Asked because a silent mode-swap would be disastrous in an unattended optimiser,
and because eigen-per-evaluation is not affordable forever. Four regimes, one of
them an outright bug.

### 🔴 1. The threshold was wrong and would have accepted a false match

`eigmodes.follow`'s `reject_at = 0.010`, recalibrated against four
driven-vs-eigen identifications where the answer is independently known:

| | distance |
|---|---:|
| true matches (4) | 0.00016 – **0.00088** |
| nearest FALSE match (4) | **0.00397** – 0.01169 |

**0.010 sits BELOW the nearest false match at 0.00397** — it would have accepted
a wrong mode silently. The original value was calibrated on ONE true match
against non-matches from solves where the sought mode was ABSENT, which is a far
easier discrimination than telling two PRESENT modes apart. The real separation
is **4.5×**, not the 40× claimed.

✅ Now **0.002** — the geometric centre, 2.3× above the worst true match and
2.0× below the nearest false one. `follow()` now also returns the **margin over
the best alternative**, because an absolute distance says nothing if a second
mode sits equally close, and an unattended caller must gate on the margin.

### 🔴 2. Weak coupling — and it is the regime we want

| loop area | reads | identification margin |
|---:|---|---:|
| 384 mm² | TE011 | 58.8× |
| 176 mm² | TE011 | 26.0× |
| 82 mm² | TM111 | 33.5× |
| **35 mm²** | TM111 | **4.5×** |

A weakly driven field is less dominated by its resonant mode, so its fingerprint
picks up off-resonant background. **The probe regime we WANT — non-perturbing,
low Q cost — is the one where identification is least reliable.** That is a real
design tension, not a solvable bug.

### 🔴 3. The mode-swap crossover, 82–176 mm², is UNMEASURED

Coupling swaps from TM111 to TE011 somewhere in that interval and **nobody has
looked there.** Near the crossover both modes are excited comparably, so the
driven fingerprint is a superposition matching NEITHER reference well. That is
simultaneously where identification is hardest and where an optimiser exploring
loop geometry would spend time.

✅ It should fail LOUDLY there — a blended signature raises the distance and
collapses the margin, which is exactly what the recalibrated threshold now
catches. ⚠️ But that is a prediction, not a measurement. One driven+eigen pair at
~120 mm² would test it.

### 🔴 4. New region topology and strong loads

The signature is a vector of per-region energy fractions, so a reference library
is valid only within ONE region topology. Adding a groove or a torch changes what
the vector MEANS, not merely its length — `_dist` now refuses on a length
mismatch, but same-length-different-meaning would pass. And under a plasma (H3)
the energy redistribution IS the effect being measured, so an empty-cavity
reference may not transfer at all. Untested.

### What this means for the eventual optimiser

🔑 **Eigen is needed ONCE per region topology, not per evaluation** — to build
the reference fingerprints. Every driven solve afterwards can be identified
against them, which is what makes driven-only operation affordable.

🔑 **The objective must carry the identification margin and REFUSE to score a
point whose margin is poor.** Scoring an unidentified mode is precisely the
silent mislabelling that produced a confident, entirely spurious "smaller loops
cost more Q" trend here — with a human watching. Unattended, it would have been
optimised against.

## 2026-08-22 — Addressing driven-only mode ID: a SYMMETRY test, and how many bins it needs

The fingerprint-matching identifier is a similarity score with a threshold, and
its margin collapses to 4.5× exactly where we want to operate (weak coupling).
A better threshold does not fix that — the fix is to stop measuring similarity
and start measuring **symmetry**.

### The discriminator

TE011 is m=0; TM111 is m=1. Energy goes as cos²(mφ), so per-sector azimuthal
energies are **flat for m=0** and a **pure cos(2φ) for m=1**. That is structural,
needs no reference library, no threshold fitted to four points, and — crucially —
is computable from a **DRIVEN solve alone**, because Palace emits per-region
energy at every frequency sample.

`azimuthal.py` implements it: angular harmonics of the sector energies, with
`order()` returning `m`, a confidence, and the full harmonic set. Synthetic
self-test: **A2/A0 = 0.0000 for m=0 against 0.3784 for m=1** (below the ideal 0.5
because integrating over a 72° sector smears the pattern), and it REFUSES rather
than guessing on a 50/50 blend.

⚠️ `geometry.py --sectors` already did this. GEO sets `--sectors 1`, so **no
solve in the record has azimuthal bins.** The capability was built and disabled.

### 🔴 Choosing the bin count is a LOOKUP, and the docs were wrong

Mode m lands on angular harmonic **k = 2m**, folding under N sectors to
`min(k%N, N-k%N)`:

| N | m=0 | m=1 | m=2 | m=3 | m=4 | m=5 | resolves |
|---:|---:|---:|---:|---:|---:|---:|---|
| 3, 4, 6 | | | | | | | 🔴 collide among m=0,1,2 |
| **5** | 0 | 2 | 1 | 1 | **2** | **0** | m=0,1,2 only — **m=4 ≡ m=1, m=5 ≡ m=0** |
| 7, 8, 10, 12 | | | | | | | m=0,1,2 |
| **9, 11, 13** | 0 | 2 | 4 | 3 | 1 | | ✅ m=0..4 |

🔴 **`geometry.py`'s help claimed "5 resolves m=1..4". It does not** — at N=5,
m=4 aliases onto m=1 and m=5 onto m=0. Corrected in place. This is the
confounding the user remembered, one bin-count away from being live.

✅ **The procedure**: ask `physics.spectrum()` which modes are in the solve
window and take their m. For the H1 cavity over 2.25–2.80 GHz that is TE011
(m=0), TM111 (m=1), TE112 (m=1), TM210 (m=2) — so m ∈ {0,1,2}, and **N=5
suffices**. Then add margin, because slot resonances, loop resonances and
hybrids are NOT in the closed form and can carry high m. **N=9 is the smallest
that separates m=0..4** and costs only mesh regions, not solve time.

⚠️ N ≥ 3 also keeps the m=1 pair degenerate: a C_n mesh partition with n ≥ 3 has
a 2-D irreducible representation for m=1, so it does not split the polarisations.

### What still has to be shown

`e0k2_azim.py` tests it where the answer is known before trusting it where it is
not: the BARE cavity (TE011 and the TM111 pair already identified by Q,
unambiguously), then the 176 mm² loop with BOTH eigen and driven. Declared
falsifiers: F1 if TE011 does not read m=0 bare; F2 if the m=0/m=1 separation is
under 10×, in which case it is no better than the fingerprint it replaces; F3 if
the driven answer disagrees with the eigen one, in which case eigen stays
mandatory per evaluation and driven-only operation is off the table.

## 2026-08-22 — ✅ The azimuthal test works (134×), and it reframes the question

`e0k2_azim.py`, 5 sectors, bare cavity and 176 mm² cap loop.

### V1/V2 pass decisively on the bare cavity

| mode | Q | A2/A0 | m |
|---|---:|---:|---:|
| 2.450086 | 20,313 | **0.3055** | **1** ✅ |
| 2.450467 | 44,057 | **0.0023** | **0** ✅ |
| 2.783510 (TE112) | 29,002 | 0.1511 | 1 ✅ |
| 2.784914 (TM210, m=2) | 30,794 | 0.0004 | **None** — refuses, correctly |

**Separation 134×**, against the fingerprint identifier's **4.5×** at weak
coupling. It also correctly REFUSES on TM210, whose m=2 aliases to harmonic 1 at
N=5, rather than returning a wrong label.

### 🔑 With the loop, it refuses — and that is the RESULT, not a failure

| mode | Q | A2/A0 | m |
|---|---:|---:|---|
| 2.423706 | 18,457 | 0.3446 | 1 (clean) |
| 2.450241 | 31,154 | **0.1087** | **refused** |
| 2.453721 | 24,411 | **0.1975** | **refused** |

Both modes near 2.45 sit BETWEEN pure m=0 (0.0023) and pure m=1 (0.3055).
**A probe at one azimuth breaks the axisymmetry that DEFINES m**, so with a loop
present there IS no pure TE011 — the mode is a hybrid, and asking "which mode is
this" has no exact answer.

Reading A2/A0 as an admixture fraction instead:

| mode | m=1 fraction | Q predicted | Q measured | error |
|---|---:|---:|---:|---:|
| 2.450241 | **35%** | 31,242 | 31,154 | **0.3%** |
| 2.453721 | **64%** | 25,139 | 24,411 | 3.0% |

using **linear mixing of 1/Q** (loss per cycle mixes, Q does not) between the
bare TE011 and TM111 values.

🔴 **So "the loop costs 32.4% of Q" was the wrong description.** The loop adds no
loss — it is PEC. The mode simply becomes 35% TM111 and inherits 35% of TM111's
much larger loss. Predicted to **0.3%**.

⚠️ This supersedes the earlier interpretation that the loop "distorts the mode
and crowds current onto the wall". That was a guess; this is measured, and it
also removes the need for a separate explanation of the non-monotonic Q across
loop sizes — different loop areas simply produce different admixtures.

### What this changes about the plan

✅ **A2/A0 is better than a label.** It is continuous, physically meaningful,
computable from a driven solve, and it PREDICTS Q to 0.3%. For an unattended
optimiser it should be a first-class objective term, not a classification step:
a geometry that reaches its target frequency shift by hybridising TE011 with
TM111 is NOT the design wanted, and A2/A0 detects that directly where a binary
label would have said "TE011" and moved on.

⚠️ Still open: **V3 — whether the DRIVEN solve alone recovers the same answer as
its eigen counterpart.** That is the claim that makes eigen-per-evaluation
unnecessary, and it is still solving.

## 2026-08-22 — 🔴 THE GROOVE IS INCOMPATIBLE WITH IN-BAND TM IGNITION (measured, H2 data)

From the user: TM111 suppression is a moving target — we can reject it outright
mechanically, but chasing TM ignition means rejecting TM111 while ACCEPTING
TE011 **and** TM020 or TM012 in the same ~100 MHz band around 2.45 GHz.

That requirement cannot be met by the annular groove, and H2's own data says so.

### The groove discriminates by CAP-CURRENT DIRECTION, not by mode name

Cap surface current K = ẑ × H, at the end cap:

| family | H at the cap | cap current | annular groove |
|---|---|---|---|
| **TE0np** | H_z = 0 there, H_φ = 0 (m=0), H_r ≠ 0 | **purely AZIMUTHAL** | runs PARALLEL — unaffected ✅ |
| **TM0np** | H_r = 0 (m=0), H_φ ≠ 0 | **purely RADIAL** | CUTS it — strongly affected 🔴 |
| TM1np | mixed, radial component present | partly radial | affected (this is the intent) |

🔴 **TM020 and TM012 are m=0 TM modes.** Their cap current is purely radial, so
the groove suppresses them at least as hard as TM111.

### Measured, by signature matching h2_d0 → h2_d20 (20 mm groove)

| mode | f (bare) | Q | f (gd=20) | Q | shift | ΔQ | match dist |
|---|---:|---:|---:|---:|---:|---:|---:|
| **TE011** | 2.45086 | 44,383 | 2.45084 | 44,364 | **−0.0 MHz** | **−0%** | **0.0000** |
| TM111 pair | 2.45011 | 20,258 | 2.24548 | 6,079 | −204.6 | −70% | 0.0110 |
| **TM010** | 1.30386 | 21,186 | 1.27110 | 12,680 | **−32.8** | **−40%** | 0.0037 |
| **TM011** | 1.84031 | 17,567 | 1.72652 | 7,289 | **−113.8** | **−59%** | 0.0078 |
| TM110 | 2.07766 | 26,687 | 1.99587 | 9,869 | −81.8 | −63% | 0.0076 |
| TE111 | 1.63815 | 23,926 | 1.61222 | 15,578 | −25.9 | −35% | 0.0050 |

**TE011 is the ONLY mode the groove spares.** Everything else moves 26–205 MHz
and loses 35–70% of its Q. The m=0 TM family — TM010, TM011, and therefore TM012
and TM020 — is hit hard.

⚠️ This was in `postpro/h2_d*` since H2 and was never looked at: H2 asked only
"did TM111 move and did TE011 stay put", and both answers were yes, so nothing
prompted a look at the rest of the spectrum. **A rig that measures its declared
question and nothing else will not see a conflict with a hypothesis it was not
asked about.**

### Consequence for H4

🔴 **The groove and in-band TM ignition are mutually exclusive as currently
conceived.** Either:

1. **Drop in-band TM ignition** — take the second-source route (TM010 at
   1.32 GHz, TM011 at 1.82 GHz), which is cost and architecture, not physics; or
2. **Find a mode filter that discriminates by AZIMUTHAL ORDER, not current
   direction.** TM111 is m=1; TM012 and TM020 are m=0. The unique property
   separating what we want to keep from what we want to reject is **m**, and an
   annular (axisymmetric) filter is blind to m by construction — it cannot
   distinguish them, which is exactly what the table above shows.

🔑 The corollary is sharp: **any axisymmetric filter is blind to m.** Rejecting
TM111 while sparing TM0n REQUIRES an azimuthally structured perturbation. That
is a different device, not a tuned version of this one.

⚠️ Not yet designed, and not to be guessed at. Note also that TE011's own
survival depends on the filter staying parallel to its azimuthal cap current, so
an azimuthally structured filter risks the very mode it must protect.

## 2026-08-22 — 🔴 H4's PREMISE FAILS: no mode in this cavity cold-ignites

From the user, questioning whether TM is needed for ignition at all, then
sharpening it to the right mechanism: **Townsend avalanche in a TE regime.**

### The mechanism, correctly stated

⚠️ First correction, to my own framing: **seeding electrons does NOT lower the
field needed for net ionisation.** It removes the statistical delay in waiting
for an initiatory electron; the avalanche still has to grow, and that is set by
the reduced field **E/N**, not E.

Microwave caveat, which happens to help: E_eff = E_rms/√(1+(ω/ν_c)²), and at
1 atm ν_c ≈ 1e12/s against ω ≈ 1.54e10/s, so ω/ν_c ≈ 0.015 and **E_eff ≈ E_rms**
— collisions randomise the electron motion fast enough that the RF field is
nearly as effective as DC.

### Measured, from `p_elec[bore]` in h2_d0 — data already on disk

| mode | bore energy fraction | × TE011 | E/N @ 1 kW | E/N @ 3 kW |
|---|---:|---:|---:|---:|
| TE011 | **0.079%** | 1.0× | 4.1 Td | 7.0 Td |
| TM111 | 0.674% | 8.5× | 8.0 Td | 13.8 Td |
| TM011 | 0.921% | 11.7× | 10.0 Td | 17.4 Td |
| **TM010** | **2.300%** | **29.1×** | **20.7 Td** | **35.9 Td** |

against an N₂ avalanche threshold of roughly **100–150 Td**.

✅ TE011's measured 0.079% confirms the "~0.1% in an 8.5 mm bore" in the record.

🔴 **No mode cold-ignites.** The best available, TM010 with 29× TE011's bore
energy, reaches only ~36 Td at 3 kW — **3–4× short**. The gap is large enough
that substantial error in the threshold does not close it.

### 🔑 Consequence: the TM companion was solving a problem it could not solve

H4 assumed the OPERATING mode must also break down the gas, found TE011 could
not, and reached for an in-band TM companion. But **a TM companion cannot break
it down either.** Auxiliary ignition was always required, and the choice of
operating mode was never the ignition question.

**What ignition actually needs is a THERMAL KERNEL, not seed electrons.** At
3000–5000 K the neutral density falls 10–17×, so the SAME cold field lands at
45–130 Td — into the ionising range. A spark or Tesla discharge provides exactly
that: a hot conductive filament, not merely free electrons. ICP torches apply it
EXTERNALLY through the quartz, which also avoids in-plasma electrode erosion —
a real concern for a spectroscopy instrument.

🔑 **And the geometry inverts in our favour**: TE011's on-axis field null — the
exact reason it cannot ignite — is what makes an on-axis or near-axis igniter
nearly invisible to it (0.079% of its energy is there). The converse reinforces
it: an axial conductor strongly perturbs TM0n, whose E_z peaks on axis, which is
the same physics as the TDS-shorting objection that already rules TM out for
OPERATION.

### What this collapses

- the groove / TM-ignition conflict **evaporates** — the mode filter returns to
  the TE-only case, which is SOLVED at 5×10 mm
- **D/L stays at H1's optimum 1.525**, instead of being dragged to 1.141 or
  2.431 to place a companion in band
- no in-band companion → no 50 MHz near-rival → **no tuning plunger**
- the ~100 MHz band constraint disappears
- 🔑 **H3 becomes the sole gate**: can TE011 SUSTAIN a discharge once a thermal
  kernel exists? Not one question among several — the one the architecture
  turns on.

### ⚠️ What must be checked before this is adopted

1. **The 100–150 Td threshold is a literature figure**, and this programme has
   been burned by a formula quoted outside its domain before. Microwave
   breakdown at atmospheric pressure is diffusion-loss dependent and therefore
   geometry dependent. Verify.
2. **TM012 and TM020 bore fractions are not measured** — they are above this
   window. TM010's 2.3% is the proxy used here.
3. **Does an on-axis conductor perturb TE011?** One eigen solve, ~165 s.
4. **What do comparable instruments actually use to ignite?** External and
   verifiable. ⚠️ Verify, do not inherit — MP-AES/MICAP numbers have already
   entered this record unexamined (the 20 slm ceiling).

## 2026-08-22 — V3: driven-only azimuthal measurement WORKS to 2%; the criterion was mis-specified

`e0k2_azim.py` CASE 2, driven solve, 2530 s.

| | A2/A0 | as hybridisation fraction |
|---|---:|---:|
| **DRIVEN** (f₀ 2.450245) | **0.1066** | 34.4% |
| **EIGEN** (f 2.450241, Q 31,154) | **0.1087** | 35.1% |
| agreement | **1.9%** | 0.7 percentage points |

✅ **A driven solve recovers the eigen solve's azimuthal content to 2%.** That is
the substantive claim — driven-only azimuthal measurement works, and eigen is
needed once per region topology to establish the pure-m endpoints, not per
evaluation.

### 🔴 But F3 fired as written, and that is recorded, not explained away

V3 was declared as *"the driven answer returns the same m as the eigen mode it
matches"*, and coded as `m is not None and m == eigen_m`. Both returned
**m=None**, so it fired.

**None == None is agreement.** The criterion tested equality of a DISCRETE LABEL
when the physics says the quantity is CONTINUOUS — with a loop present neither
mode is a pure m state, so neither has a label to agree on. The test asked a
question the system cannot answer and scored the correct answer as a failure.

⚠️ The reinterpretation is not post-hoc: *"A2/A0 is better than a label — it is
continuous, physically meaningful, computable from a driven solve, and it
predicts Q to 0.3%"* was written into FINDINGS after the BARE-cavity case and
BEFORE this driven solve returned. The criterion was simply written earlier than
the understanding, and not revised when it changed.

🔑 **Lesson: a declared criterion has to be re-read when the model underneath it
changes.** V3 was written when "which mode is this" still looked like a
well-posed question. It stopped being well-posed two results later, and nothing
prompted a re-read of the criterion that depended on it. Declaring criteria in
advance protects against moving the goalposts; it does not protect against the
goalposts becoming the wrong shape.

✅ **Restated**: the driven solve must recover the eigen solve's **A2/A0** —
a continuous quantity — to within a stated tolerance. Measured: **1.9%**.

### ⚠️ Open, and not investigated

**β = 0.3411 on the 5-sector mesh against 0.5598 on the 1-sector mesh, for the
same 11×8 loop — 39% apart.** Sectoring changes the mesh (internal surfaces, a
different partition) and β is evidently sensitive to it. f₀ also shifts 160 kHz,
against a mesh-to-mesh figure of ≤21 kHz in INSTRUMENT — but those are the same
geometry re-meshed, and this is a different partition, so the comparison is not
like-for-like. Flagged, not explained.

## 2026-08-22 — 🔴 ROOT CAUSE: the lumped port meshed with TWO elements

Chasing the 39% β discrepancy between two meshes of identical geometry, as
instructed: find out why first.

### It is not the geometry, and both extractions were self-consistent

Sidecars are identical — same radius, length, `loop_cap_r`, `loop_phi`,
`port_direction`, sizing. `pec_surfaces` 17 → 29 is only the wall being
subdivided into 5 patches per surface (+4 barrel, +4 per cap), not new conductor.

And each driven solve agreed with its OWN eigen solve: 5.4% (1-sector) and 6.6%
(5-sector). Neither extraction is broken. The difference is in the raw
measurement — |S11|min **−10.989 dB vs −6.173 dB**, a 4.8 dB shallower dip, so
the coupling itself differed.

### 🔴 The port surface has TWO elements

    2D attr 91  port    2 elements

The lumped port is a **1.8 × 0.30 mm** rectangle and the mesh floor
(`sizing_mm.min`) is **1.2 mm** — the gap sits **4× below the floor**. The port
IS the drive point, so β rode on how those two triangles happened to fall, and
any perturbation of the surrounding mesh reshaped them.

**This explains both outstanding anomalies at once:**
1. the 39% β spread between identical geometries;
2. the non-monotonic β across the loop-area sizing sweep (1.50, 0.87, 0.56,
   1.85), which no coupling model accounted for — port noise of this scale on
   top of a monotonic trend produces exactly that.

### 🔑 R62 diagnosed this exact failure ONE GAP OVER

`geometry.py`'s own comment:

> *"R62: the series-capacitor gap is a sub-millimetre void that must be RESOLVED,
> not merely present. A first attempt left it below the mesh floor and Q_ext came
> back identical to 4 significant figures across gaps of 0, 0.15, 0.30 and
> 0.60 mm — the geometry differed (checksums), the discretisation did not, and
> the capacitor contributed nothing."*

R62 found it, fixed it for `loop_gap2`, and **left the primary port gap
unfixed** — floor logic and Ball refinement both. The driven programme has run
its whole life on a 2-element port.

### ✅ What the anchor survives

Q₀ = Q_L(1+β) is **insensitive** to this: Q_L and β come from the same S11 curve
and both track whatever the actual coupling was, so they move together. That is
why four driven-vs-eigen comparisons agreed to 4.9–8.8% throughout.

🔴 What was never trustworthy is **β as a DESIGN quantity** — "what coupling will
this loop geometry give?" Every β in the record is suspect: the sizing sweep, the
anchor's 0.560, and E0k's 0.0673.

### The fix (R112) and its verification

Mirrors R62 exactly: let the primary gap lower the floor, AND add a Ball
refinement at the port centre — because lowering the floor alone refines nothing
(R15: the floor only stops a deliberate request being overridden).

| | before | after |
|---|---:|---:|
| port surface elements | **2** | **42** |
| tets (1 sector) | 33,608 | 41,183 (1.23×) |
| tets (5 sectors) | 35,738 | 43,491 (1.22×) |
| mesh floor | 1.200 mm | 0.096 mm |

Refinement stayed local, well inside the declared 3× failure threshold. 🔑 And
**both meshes now give the SAME 42 elements**, where before both gave 2 shaped
differently — the port is now determined by the refinement field rather than by
mesh happenstance.

⚠️ `portcheck.py` is the standing test. **The remaining question — does β now
AGREE between the two meshes — needs driven solves and is running** as
`e0k2_portfix.py`, with V1 declared at 10% and F1 stating plainly that if β still
differs by tens of percent the port was NOT the cause and the answer is
elsewhere.

## 2026-08-22 — 🔴 F1 FIRES: the port was NOT the (whole) cause of the β spread

`e0k2_portfix.py`, both meshes rebuilt with the port resolved (2 → 42 elements).

| | β before | β after |
|---|---:|---:|
| 1 sector | 0.5598 | **0.5887** |
| 5 sectors | 0.3411 | **0.4081** |
| **spread** | **64.1%** | **44.2%** |

**V1 required 10%. Measured 44.2%. F1 fires: the port was not the cause, and
per the declared criterion the answer is elsewhere — this is recorded, not
re-fitted.**

### What the fix DID buy, measured

| | Q₀ driven vs eigen, before | after |
|---|---:|---:|
| 1 sector | 5.4% | **1.1%** |
| 5 sectors | 6.6% | **4.9%** |

✅ V2 passes on both, and the anchor got materially better — 1.1% agreement
between two independent routes to Q₀ is the best this programme has produced.
So R112 is a real fix and stays: a 2-element drive point was indefensible
regardless of whether it explained this particular spread.

🔴 But it explains at most a third of it (64.1% → 44.2%), and **β remains
mesh-dependent at 44% for identical geometry.** Every β in the record stays
suspect, and the loop sizing sweep still cannot be trusted.

### Candidates for the morning — NOT asserted, and not to be adopted before measuring

⚠️ This programme has twice adopted a plausible mechanism before measuring it
(the degenerate-pair blend, the loop "crowding current onto the wall"). Both were
wrong. What follows is a list of things to TEST, not an explanation.

1. **The sector partition imposes C5 symmetry on the mesh; the unpartitioned
   mesh imposes none.** That is a genuine symmetry difference, not merely a
   different discretisation. The mode is 35% hybridised TE011/TM111, and
   hybridisation is driven by symmetry breaking — so the two meshes may be
   producing genuinely different mixtures. Supporting: eigen Q differs by 3.4%
   (29,854 vs 30,878) for the same nominal mode.
2. 🔴 **The diagnostic requires the feature under suspicion.** A2/A0 can only be
   measured on a SECTORED mesh, so the hybridisation of the 1-sector case cannot
   be compared directly. Any test has to get around that — e.g. compare 5 vs 9
   sectors, where both carry bins and the symmetry differs (C5 vs C9).
3. **β may simply not be mesh-converged at sf=1.5.** No convergence study has
   ever been done for β; INSTRUMENT's mesh figures are all for FREQUENCY. A
   size-factor sweep on ONE mesh topology would settle whether 44% is symmetry
   or just resolution.

🔑 Cheapest decisive test: **5 vs 9 sectors**, both with azimuthal bins, both
with the port resolved. If β agrees there but not against 1-sector, the sector
partition is the variable. If it disagrees there too, it is convergence.

## 2026-08-23 — ✅ ANSWERED: β is not mesh-converged. Q₀ is, to 0.12%.

`e0k2_betacause.py`. The 9-sector arm failed (below); the resolution arm settles
the question by itself.

### Same partition, same port refinement, only RESOLUTION changed

| | β | Q_L | **Q₀ = Q_L(1+β)** | A2/A0 (eigen) | Q eigen |
|---|---:|---:|---:|---:|---:|
| 5 sec @ sf 1.5 | 0.4081 | 20,864 | **29,379** | 0.1087 | 30,878 |
| 5 sec @ sf 1.2 | 0.2320 | 23,817 | **29,344** | 0.1014 | 31,832 |
| change | **43.1%** | 14.2% | **0.12%** | 6.7% | 3.1% |

🔴 **β moves 43% for a 1.25× linear refinement.** That is essentially the whole
44% previously seen between partitions, so **CONVERGENCE, not symmetry**, and the
hybridisation fraction barely moves (6.7%), which independently argues against
the symmetry story.

🔑 **Q_L and β compensate almost exactly, so Q₀ is converged to 0.12% while β is
not converged at all.** This is why four driven-vs-eigen anchor comparisons held
at 4.9–8.8% while every β in the record was unreliable: the anchor never required
β to be right, only β and Q_L to be wrong TOGETHER.

⚠️ Note the eigen Q is itself still moving (3.1%), so it is not fully converged
either — but the driven Q₀ is an order of magnitude more stable than either
input that produces it.

### Consequences

✅ **The anchor stands, and is strengthened.** Absolute Q extraction is validated
by a quantity that is converged to 0.12% across a mesh refinement.
🔴 **β cannot be used as a design quantity.** The loop sizing sweep is void, and
so is any claim of the form "this loop geometry gives that coupling". Resolving
the port (R112, 2 → 42 elements) was necessary but not sufficient.
🔴 **β is not converged at sf 1.2 either** — it is still moving. 0.4081 → 0.2320
is monotonically decreasing with refinement and nothing yet establishes where it
lands. A proper series (sf 1.5 / 1.2 / 1.0 / 0.8) is needed before any β is
quoted, and it is expensive: sf 1.2 already cost 74,297 tets and 2,867 s driven.
⚠️ INSTRUMENT's mesh figures are ALL for frequency (mesh-to-mesh ≤ 21 kHz). They
say nothing about β, and were never claimed to — but they have been implicitly
relied on.

### 🔴 Separately: N ≥ 9 azimuthal sectors CANNOT be built

    Exception: Physical volume 11 already exists

Air sectors are numbered from attribute 3, so 9 sectors reaches 11 — which is
`TAG_UPSTREAM`. **Any N ≥ 9 collides**, and the mesh fails outright rather than
silently mis-tagging, which is the right failure.

🔴 This invalidates the recommendation written into OPTIMIZER.md yesterday:
"N=9 is the smallest that separates m=0..4". N=9 is unbuildable. The achievable
maximum is **N=8**, which resolves only m=0,1,2 (m=3 aliases onto m=1, m=4 onto
m=0) — the same coverage as N=5. So **no currently buildable sector count
separates m=0..4**, and doing so requires renumbering the reserved attributes.

⚠️ For the modes actually in the 2.25–2.80 GHz window (m ∈ {0,1,2}) N=5 remains
sufficient, so nothing measured so far is affected. What is lost is the margin
against unexpected high-m modes — slot, loop and hybrid resonances are not in the
closed form and can carry high m.

## 2026-08-23 — 🔑 β has no consumer. The coupling design quantity is Q_ext, and it waits on H3

Prompted by the user asking what β is even supposed to mean here — a fair
question, and the confusion is largely my doing.

### What β is

**β = Q₀/Q_ext** — power lost out the port versus power lost inside the cavity.
β<1 undercoupled, β=1 critically coupled (matched, zero reflection), β>1
overcoupled. β ≈ 1 at the operating point is a genuine instrument requirement.

### Why the EMPTY-cavity value does not transfer

The plasma is a loss INSIDE the cavity, so it changes Q₀, which changes β:

| Q₀ | β at fixed Q_ext = 71,990 | |
|---:|---:|---|
| 29,379 | 0.408 | empty, measured |
| 5,000 | 0.070 | lit, optimistic |
| 1,000 | 0.014 | lit, likely |
| 300 | 0.004 | lit, heavy |

🔴 **A loop tuned to β = 1 empty is 10–100× undercoupled once lit.**

### 🔴 Why β was in these rigs at all — a framing error

β entered ONLY as an intermediate in Q₀ = Q_L(1+β). The [0.1, 1] window was
MEASUREMENT HYGIENE — keeping β modest so it would not dominate that sum, as it
did at β = 27.5 where it supplied 96.5% of Q₀. Putting it into the rig's declared
criteria (V2/F3) made it look like a design target. It never was.

⚠️ And even the hygiene role is now moot: Q₀ is robust to β being wrong (0.12%
against β's 43%), and the anchor returned the right Q₀ at β = 27.5 too.

### The real coupling quantity, and why it also waits

**Q_ext** is the loop's own property, independent of cavity contents — and it is
equally unconverged:

| | Q_ext = Q₀/β |
|---|---:|
| sf 1.5 | 71,990 |
| sf 1.2 | 126,483 |
| | **76% apart** |

Q_ext IS the design quantity: size the loop so **Q_ext ≈ Q₀ LOADED**. But Q₀
loaded is unknown, so there is nothing to match to.

✅ **DECISION: do not run the β convergence series.** 4 h floor, realistically
8–12 h, to converge a number with no consumer against a load that will change it
by two orders of magnitude. β and Q_ext stay marked UNUSABLE in OPTIMIZER.md and
are re-derived AFTER H3, when there is a Q₀ to match.

🔑 This is CONVENTIONS §6 in a new place: *do not reuse a parameter without
re-deriving it for the case.* The case here is the LOADED cavity, and no
empty-cavity coupling number survives the transition.

## 2026-08-23 — 🔴 The EIGENMODE solver cannot handle a bulk lossy plasma

First H3 point, R=2 mm, ne=1e18 — the WEAKEST plasma on the grid. Stopped after
65 minutes with **nconv = 0**.

| | |
|---|---:|
| mesh | 59,480 tets, **380,956 ND dofs** |
| KSP residual after 38 its | 1.2e-4 against a 1e-8 tolerance, improving ~5%/it |
| NLEPS | **nconv = 0 after 19 iterations**, residual FLAT and creeping UP (3.039106e-5 → 3.039199e-5) |
| implied KSP iterations (cost model) | **~22,500** and not converged |

Compare: the bare cavity at 32,531 tets solved in **155 s**. The mesh is only
1.7× larger, so this is conditioning, not size.

### Why

    tan δ = σ/(ω ε₀ ε_r) = 0.28/(1.539e10 × 8.854e-12 × 0.689) ≈ 3

A **bulk lossy VOLUME** with tan δ ≈ 3 makes the complex permittivity strongly
frequency-dependent, so the eigenproblem is far more nonlinear than the
surface-impedance wall ever was. The wall's Robin BC is a boundary term; a lossy
volume is in the operator. NLEPS is not slow here, it is stuck.

⚠️ And this was the WEAKEST point on the grid. σ rises to 275 S/m at ne=1e21,
so it can only get worse.

### 🔑 The record already said so, and I did not apply it

INSTRUMENT, written earlier in this same programme:

> *"Driven has no NLEPS, therefore no convergence cliff. The geometries where the
> eigensolver diverges are exactly where driven should still work."*

H3 was built as eigenmode because eigen is cheap (155–882 s) and yields Q
directly, which makes η = 1 − Q_loaded/Q_bare a one-solve measurement. That
reasoning was about COST and ignored a limitation already recorded about
CAPABILITY.

🔑 The general form, worth keeping: **a cheap instrument that cannot answer the
question is not cheap.** The cost model (`solvecost`) predicts time for solves
that converge; it says nothing about which solves converge at all, and those are
different questions. `NLEPS_BUDGET` exists precisely for this and would have cut
the run at ~1,000 NLEPS iterations rather than 19 — ⚠️ but the budget is checked
AFTER `run()` returns, so a stalled solve still burns its full timeout first.
That is a gap: the guard is post-hoc when it needs to be live.

### Consequence for H3

The loaded cavity must be solved **DRIVEN**. That costs ~2,500–2,900 s per point
against eigen's 155–882 s, so the 16-point grid becomes 11–13 hours and needs
re-planning rather than a re-launch.

⚠️ Driven also requires a PORT, so the coupling loop is present and contributes
its own perturbation — measured at 32% of Q. That is not fatal: the real
instrument has a loop, and η must be referenced to the bare cavity **with the
same loop** (29,854 measured, port-resolved) rather than to the 44,384 empty
figure. But it means H3's answer includes the probe, and that has to be stated.

## 2026-08-23 — 🔴 RETRACTION ×2, and H3's first real numbers

The user objected that switching eigen→driven after one failure was reactive.
The probe they asked for retracts two of my claims and produces the first
loaded-cavity measurements this programme has.

### 🔴 RETRACTION 1: "the eigensolver cannot handle a bulk lossy plasma"

Written into INSTRUMENT as measured fact **from n = 1**. Four cases, one variable
each, at the configuration that failed:

| plasma_h | target | outcome | NLEPS | nconv |
|---:|---:|---|---:|---:|
| 0.4 | 2.15 | stalled 600 s | 6 | 0 |
| 1.0 | 2.15 | stalled 600 s | 51 | 0 |
| 0.4 | **2.40** | **converged 573 s** | 16 | 3 |
| 1.0 | **2.40** | **converged 284 s** | 16 | 3 |

**It was the SHIFT TARGET.** Not the mesh (the leading suspect — the 47× size
ratio — made no difference at target 2.15), and not Palace. Eigen then converged
at σ = 2.75e-4 through 275 S/m, the whole intended H3 range, in 89–284 s.

### 🔴 RETRACTION 2: "loading pulls the frequency DOWN and hard"

That assumption is what set the bad target (300 MHz below the mode). It is
backwards. **An overdense plasma has ε_eff < 0**, behaves like a conductor,
EXCLUDES field, shrinks the effective volume and therefore pulls the frequency
**UP**. Measured: +1.26 MHz at σ = 275 S/m. I had reasoned from ε > 1 dielectric
loading, which is the wrong regime — and the Drude numbers showing ε_eff = −310
were already in the rig's own docstring.

⚠️ The sequence was: **choose on cost → fail → generalise the failure into a
capability limit.** n = 1 in both directions. `run()`'s refusal is downgraded to
a warning that states the real hazard (target placement), since the premise it
enforced was false.

### ✅ H3's first numbers — R = 2 mm, the SMALLEST radius

TE011 identified by AZIMUTHAL ORDER (m=0 at A2/A0 ≈ 0.0001; the TM111 pair sits
at 0.308, matching the bare cavity's 0.3055):

| σ (S/m) | ne | TE011 f | Q | **η** |
|---:|---:|---:|---:|---:|
| bare | — | 2.450856 | 44,383 | — |
| 0.275 | 1e18 | 2.450554 | 36,186 | **0.185** |
| 27.5 | 1e20 | 2.450801 | 2,369 | **0.947** |
| 275 | 1e21 | 2.452113 | 1,971 | **0.956** |

🔑 **F2 does not fire.** TE011 delivers **95%** of its dissipated power to the
plasma once σ ≳ 27 S/m — at the smallest radius on the grid, where R⁴ scaling
makes coupling weakest.

🔑 **The frequency pull is ~1.26 MHz ≈ one loaded linewidth** (Q=1,971 → 1.24 MHz).
Good news for the tuning loop: the source must track about one linewidth, not
tens.

⚠️ The plasma's own `p_elec` is ~1e-4 and goes NEGATIVE at high σ. That is not a
bug: stored electric energy ½εE² is negative where ε_eff < 0. It means p_elec is
not a usable "energy fraction" for a plasma region, and η must come from Q.

### 🔴 Two things still wrong, both mine

1. **The mode pick.** The probe reported "highest-Q mode" and that selected
   2.622862 — a mode with almost no field in the bore, IDENTICAL across a 10×
   change in density. `max(Q)` picks the mode that does NOT couple. H3 must
   identify by azimuthal order, not Q.
2. **ne=1e19 (σ=2.75) did not converge** — 600 s, **0 NLEPS iterations**,
   nconv=None, an isolated hole between two converging points either side. It
   never reached the eigensolver at all, which is a different failure from the
   target stall. Unexplained; reported.

## 2026-08-23 — ✅ preflight now catches undefined names, and it immediately found one

Two launches in a row died seconds in on a `NameError` — `eigen_cfg` both times,
dropped when h3_loaded was converted eigen→driven and not restored on the way
back. `ast.parse` cannot see it: the syntax is valid and the name is only looked
up when the function runs. So the failure surfaces on the INSTANCE, after mesh
generation, with the rig already launched.

✅ **`r_undefined_name` added**, delegating to **pyflakes** rather than
hand-rolling scope analysis. ⚠️ Deliberate: a hand-rolled version has to get
comprehensions, walrus, `global`/`nonlocal` and star-imports right, and
CONVENTIONS §7 is explicit that a checker which cannot see its subject is worse
than none — this project already shipped one scanner that printed a clean bill of
health because it was blanking the very strings it was meant to read.

Reported as an ERROR, not a warning: an undefined name is not a style opinion.

🔑 **It paid for itself on the first run.** Fixing `eigen_cfg` exposed a SECOND
dropped import, `N_MODES`, at a line the earlier crash had not yet reached —
which would have produced a third failed launch. Both came from the same
refactor, and neither was visible to any check the project had.

⚠️ Note it needs the RAW source, not `code_only()` — pyflakes must see real
strings. Added to `RAW` alongside `r_help_percent`.

## 2026-08-23 — 🔴 THIRD instance of §6: N_MODES imported instead of derived

H3's grid failed at ne=1e18 at BOTH radii — 900 s timeouts — while ne=1e20 and
1e21 converged in 131–171 s and reproduced the probe's numbers exactly
(η = 0.947, 0.956). ε at ne=1e18 is **+0.689**, the regime classified as SAFE.

**The difference was the mode count.**

| | N_MODES | ne=1e18 |
|---|---:|---|
| `h3_eigenprobe` | **4** | converged, 284 s |
| `h3_loaded` | **6** | timed out, 900 s, 122 NLEPS |

Same mesh (38,791 tets), same target (2.40), same `plasma_h` (1.0), same sectors.
The rig imported `N_MODES` from `e0k2_anchor` (=6); the probe had validated 4.

🔑 Physically coherent: with a WEAK plasma the TE011/TM111 cluster is nearly
degenerate, so 6 modes means resolving closely-spaced eigenvalues. With a STRONG
plasma they are damped and spread apart — which is exactly why ne=1e20 and 1e21
converged at 6 and ne=1e18 did not. The failure is about MODE SPACING, not about
ε being negative.

⚠️ **So the ε-based dispatch rule is at best incomplete.** It predicted ne=1e18
(ε>0) would be fine and it was not — at N_MODES=6. At N_MODES=4 the probe's data
is consistent with it (1e15..1e18 converge, 1e19 fails, 1e20..1e21 converge), so
the rule survives *at the validated mode count* and nowhere else. It is a rule
about one configuration, not about ε.

### The pattern, third time in this file

CONVENTIONS §6 — *do not reuse a parameter without re-deriving it for the case*:

1. the **shift target** (2.15, from "loading pulls DOWN") — 65-minute stall
2. `Q_BARE` / `V1`'s reference — wrong bare cavity for a driven solve
3. **`N_MODES` = 6, imported** — two 900 s timeouts

All three were parameters inherited from a rig built for a different problem, and
all three were in `h3_loaded.py` — the file that was converted between solvers
twice. That is CONVENTIONS §7c's evidence, arriving after §7c was written.

⚠️ **R = 8.5 mm remains UNTESTED at any mode count** — the probe only ran R=2.
The plasma there is 18× the volume. If it still fails at N_MODES=4, that is
reported, not explained.

## 2026-08-22 — 🔴 RETRACTION: "the power-density peak is unreachable". It is not.

`h3_eigen` swept a SOLID plasma column at ne=1e20 and found power density peaking
at **R = 0.75 mm (1.82e9 W/m³)**, an interior maximum (F1 did not fire). Two
verifications passed on the way: R=2 mm returned **Q = 2,373 against 2,369
measured twice before (0.17%)**, and the range brackets the peak.

I then reported that peak as **unreachable**, on the grounds that a standard
Fassel injector has a tip bore of 1.5–2.0 mm — radius 0.75–1.0 mm — so the
optimum "coincides with the sample channel". The user rejected this: *"You keep
saying the peak is unreachable, but it isn't. The solver can't see it, that
doesn't mean it doesn't exist."* They were right, and the claim is withdrawn.

### Two errors, neither numerical

**1. Geometry.** The injector TIP sits at the BOTTOM of the plasma zone; the
plasma forms DOWNSTREAM of it. At the plasma's axial location there is no solid
object — the inner radius is set by GAS FLOW, not a tube wall. `geometry.py` has
had this right since the torch assembly was built: its own comment reads *"the
plasma forms DOWNSTREAM of the intermediate tube, in the last 20-30 mm before the
tip"*. I also told the user "there is no torch geometry currently" while
`--inj-od` / `--inj-id` / `--inter-od` were all present and modelled.

**2. Model-as-world — the one that generalises.** A solid-column sweep *cannot
represent* an annulus, so its peak location was never the physical optimum. I
read a limitation of the RIG as a fact about the PLASMA. The tell was in the
source the whole time:

    INNER_R = 0.0       # 0 = solid column. >0 would make it annular.

`geometry.py --plasma` has always taken `ri,ro,zlo,zhi`. The capability existed;
I built an analytic correction for something the rig could measure directly.

### Why hollowing should HELP (the claim now under test)

TE011's E_φ ∝ J₁(χr/a) **vanishes on axis**; near the axis J₁ ~ r, so field-energy
weight goes as r³. The plasma CORE sits in a field null — it contributes volume
but almost no absorption, so removing it should RAISE η·P/V.

Skin depth confirms this is null-vacating and not skin-shielding: at ne=1e20,
δ = 1.80 mm, so r/δ = 0.42–0.83 across 0.75–1.5 mm — the field FILLS the column.
(Where r/δ >> 1 the core would be shielded and removal nearly free. Different
mechanism, not the one claimed.)

⚠️ **Analytic estimate only, NOT simulated**: measured η curve × a null-vacating
factor gives hollow beating solid by ~1.4×, with the optimum rₒ moving OUTWARD as
rᵢ grows (0→0.75, 0.5→0.75, 0.75→1.00, 1.0→1.25, 1.5→2.00 mm). `h3_annular.py`
exists to falsify exactly this, and the numbers above must not be quoted as
measurements — the same arithmetic-instead-of-simulation shortcut this entry is
about.

### Also corrected: the tuning claim

I wrote *"linewidth 1.03 → 5.90 MHz, the LDMOS has to track 5.7× more."*
**Backwards.** A wider linewidth is a BIGGER target, easier to hold. The real
quantity is ignition shift ÷ linewidth, and measured it is **0.61–1.36 for
rₒ ≥ 1.5 mm** (6.8–9.2 only at rₒ = 0.5–0.75 mm). ~One linewidth of retune across
the whole reachable range — mild, and nearly radius-independent.

### What the sweep did NOT deliver

The **gas-like row (ne=1e18) is inconclusive**: R=1 mm failed to mesh
(`ScaledJac`), R=8 and R=16 mm BOTH timed out at 900 s (7 and 33 NLEPS
iterations). Two usable points remain, R=2 and R=4 mm, at 1.65e8 and 1.67e8 W/m³
— flat, and two points cannot bracket a maximum. That is the row where sustaining
is decided, so **the marginal regime is still unmeasured**. Metal-like is the
only row that is settled.

⚠️ Thin annuli mesh badly: a 0.25 mm shell at order 2 dies with *"3 elements still
degenerate (worst minSICN 1.57e-04)"*. `h3_annular` retries with perturbed size
factors and floors the thickness; anything thinner than ~0.5 mm is not currently
measurable and must be reported as such rather than skipped silently.

## 2026-08-22 — 🔑 THE FLOW SPEC IS THE POWER-DENSITY SPEC. Cooling flow is the lever.

Sustaining a 1 kW N₂ plasma at 2.45 GHz is **not an open question** — MICAP and
MP-AES ship it. So the gas-like row of `h3_eigen` being inconclusive (R=1 mm mesh
failure, R=8 and R=16 mm both timed out) blocks nothing. What was actually
missing was **flow rates**, and there are three of them, not one.

### The three flows, stacked radially by continuity

Each stream occupies area A = Q·(T/300)/v. Stacking from the axis outward:

    stream     slm    T K   v m/s    r_in   r_out    band
    sample    0.75   4000      15    0.00    1.88   1.88 mm
    body      1.00   5000      20    1.88    2.82   0.94 mm
    cooling  15.00   6000      25    2.82    8.46   5.64 mm

**rₒ = 8.46 mm against a 17 mm-ID Fassel tube's 8.50 mm** — the three flows, the
temperatures, plausible ICP velocities and the tube ID close on each other to
0.5%. Nothing is being forced to fit.

Across the plausible range (sample 0.5–1.0, body 0.5–1.5, cooling 12–18 slm):
**rᵢ = 1.0–3.0 mm, rₒ = 6.7–10.6 mm.**

⚠️ My earlier single-flow version lumped "plasma + auxiliary" together. It got a
similar rₒ by luck, but it hid the structure that matters: **cooling is 88–92% of
the total gas and sets rₒ almost single-handedly.** Sample flow sets rᵢ; body
flow occupies ~1 mm and moves neither appreciably.

### Why that settles power density

η is **already pinned at ~0.995** in this box (measured: 0.9946 at rₒ=6 mm, and
rising with rₒ). When η ≈ 1, power density = P/V exactly — a **geometric**
quantity. And V is set by rₒ, which is set by cooling flow:

    12 slm cooling ->  2.88e8 W/m^3     1.54x nominal
    15 slm cooling ->  1.87e8 W/m^3     1.00x
    18 slm cooling ->  1.22e8 W/m^3     0.65x

(at 1 kW, 25 mm plasma length. **NOT** the 76.8 mm the sweep used — sweep
densities are ~3x lower for that reason alone and are not comparable to these.)

**Cooling flow alone moves power density 2.4× across its normal range.**

### 🔴 What this means for the EM programme

**Coupling is not the design lever in the flow-accessible box.** η cannot
usefully exceed 0.995, so no EM improvement buys more than 0.5%. The lever is
VOLUME, the volume is set by cooling flow, and how low cooling flow can go is set
by **whether the quartz survives** — a thermal question Palace cannot answer.

This also demotes `h3_annular`, launched an hour earlier. Its F1 (does hollowing
raise density?) is near-arithmetic when η≈1: the predicted 1.06–1.33× is just
rₒ²/(rₒ²−rᵢ²). Its remaining value is **verifying that η stays ≈1 across the
whole box**, which is the assumption this entire closure rests on. It should be
read as a check on that premise, not as an optimisation.

V2 anchors both reproduced h3_eigen exactly: solid rₒ=2 mm -> 8.16e8 W/m³
(Q=2,376 vs 2,373, 0.13%); solid rₒ=6 mm -> 9.52e7 W/m³ (Q=242 vs 238, 1.7%,
but η identical so density is unaffected).

⚠️ **The velocities are assumed** (10–30 m/s, from ICP practice), not derived,
and they enter as 1/√v on every radius. They are the weakest input in the chain
and the first thing to replace with measured MP-AES/MICAP operating data.

### ⚠️ Correction to the entry above (same session): plasma length is 92.3 mm

I wrote "NOT the 76.8 mm the sweep used". Wrong number — I had carried L = 96 mm
over from a scratch mesh command. The rig prints **L = 115.4158 mm**, so
Lₚ = 0.8·L = **92.3 mm**. The comparison stands but the factor changes: sweep
densities are **~3.7× lower** than the 25 mm-plasma figures, not ~3×.

Verified against a measured point rather than re-asserted: (rᵢ=1.5, rₒ=5.0) has
V = π(5.0² − 1.5²)·10⁻⁶ · 0.0923 = 6.599e-6 m³, so η·P/V = 0.9932·1000/6.599e-6 =
**1.505e8 W/m³** against 1.51e8 reported. The rig's volume and η are consistent
to 3 figures; the error was mine alone.

## 2026-08-23 — 🔴 EIGEN SOLVES HAVE BEEN SOLVING THE TORCH AS VACUUM

`h4_field` was built to replace the analytic J₁ field map with a measured one
that includes the torch dielectric, because every ignition number in H4 rests on
a field computed with `--no-torch --no-inner`. Committed prediction before the
run (Slater): **−15.3 MHz** for three sapphire tubes, −11.2 MHz for the outer
tube alone.

Measured for the outer sapphire tube: **+0.06 MHz** — 23 ppm, i.e. mesh noise,
and the wrong sign. A 180× miss is not a bad approximation; it is a null result.

### Cause

`e0_solver_vs_math.eigen_cfg` declares:

```python
"Domains": {"Materials": [{"Attributes": vols, "Permittivity": 1.0, ...}]}
```

**Every volume gets ε = 1.0, the torch included.** The torch-material binding
exists only in `solveconf.driven` (R101), which reads it from the mesh sidecar.
So the tube was geometrically present and electromagnetically absent, and the
measured ~zero shift is exactly right for a vacuum tube.

⚠️ **This is R101 recurring in the other solver.** R101's own comment records the
identical failure on the driven path — *"A sapphire mesh therefore solved as
quartz, and the two meshes were BYTE-IDENTICAL, so nothing downstream could
notice"* — and notes it stayed latent because no rig had passed
`--torch-material`. The fix was applied to `driven` and never to `eigen`. The
same value, maintained in two places, went wrong in the second one.

🔑 **Scope: every eigen solve in this programme that contained a torch.** Most
carried `--no-torch`, so they are unaffected — but any that did not were solving
quartz/sapphire as air, and their frequencies are wrong by roughly the shift
computed above. Q is much less affected (the tubes are low-loss).

### Fix

`h4_field` now builds `Materials` itself, binding the torch permittivity from
`meta["geometry_mm"]["torch_material"]` — the same source `driven` uses — and
**refuses the case** if the sidecar cannot name it, rather than guessing the
permittivity of the thing under test. Added as **V2b**: every torch case must
print the ε it actually solved with.

🔴 The general fix belongs in `eigen_cfg`, not in one rig. Until that lands, any
eigen rig with a torch must bind the material itself or it silently solves air.

### Also from run 1: the bore field was under-resolved

The no-torch mesh was 35,182 tets in 2,808 cm³ — characteristic element **~8 mm,
larger than the 8.5 mm bore**. Probes at r = 0.5–8.2 mm were interpolated inside
one or two elements where E ∝ J₁ ∝ r is small. Measured/analytic came back 25%
low at r = 5 mm, 15% at 8.2, 11% at 10.5, 3% at 42.3 — worst where the field is
smallest, vanishing at the mode peak, which is the signature of a resolution
artifact rather than physics. Fixed with a vacuum refinement region (ε = 1,
σ = 0) spanning r < 8.5 mm, z = ±10 mm at 1 mm elements, applied identically in
every case.

✅ V2 on Q passed: no-torch gave 44,057 vs 44,384 (0.74%). f₀ and Q are global
integrals and did not suffer the probe-interpolation error.

---

## 2026-08-23 — ✅ H4 field, run 2: SLATER HOLDS AT ε=11.6, H1's DESIGN POINT SURVIVES THE TORCH

Run 2 of `h4_field` completed on the instance at 13:33 (four cases, 327/84/105/136 s).
V2b did its job: every torch case named the permittivity it actually solved with,
read from the mesh sidecar, so the R101-in-eigen bug that voided run 1 cannot recur
silently.

🔴 **The log that run printed is NOT the result.** It was scored by an analysis
layer carrying two arithmetic bugs, both already fixed in `h4_field.py` at 13:35
and never re-run against the data. Re-scored offline via `h4_reanalyse.py` — **no
solving, §10**. What the two layers say:

| check | 13:33 log | re-scored | what changed |
|---|---|---|---|
| V2 E0 | 1.486e9 vs 1.691e6, **87,800% 🔴** | 4.7% ✅ | `j1(chi*r_mm*1e-3/a_mm)` — r in metres, a in mm. A 1000× wrong Bessel argument in the CHECK, not a bad field |
| Ar 2.1 kV/cm | r ≥ 10.5 mm 🔴 **"will not light"** | r ≥ 7.4 mm ✅ inside the bore | `prof/sqrt(2)` against the threshold when `prof` is ALREADY rms — every contour pushed 1.41× too far out |
| F2 worst | 56.8–64.9% at r=0.5 mm | 10.5–12.2% at r=5–9 mm | r=0.5 mm is below the mesh's resolved floor |

⚠️ **Two of the three headline verdicts in that log were wrong, and both were unit
errors in the SCORING.** The solves were fine. This is §10 paying for itself a
third time: the correction cost one re-analysis, not four re-solves.

### ✅ The committed prediction was met

Stated BEFORE the solve (Slater, unperturbed field), against measurement:

| case | predicted | measured | |
|---|---:|---:|---|
| outer tube only | −11.2 MHz | **−13.71 MHz** | 22% |
| all three tubes | −15.3 MHz | **−15.00 MHz** | **2%** |

🔑 **Slater survives ε = 11.6.** The docstring warned this was "an order of
magnitude to TEST, not a value to confirm" because ε=11.6 is not a small
perturbation. It came back at 2% on the full torch. Q moved 0.3% (44,245 →
44,215), consistent with low-loss tubes.

✅ **F1 PASSES on all three torch cases** — 2.4368 / 2.4355 / 2.4471 GHz, all
inside 2.40–2.50. **H1's design point (a=88.0045, L=115.4158), chosen with
`--no-torch`, holds with the torch present.** The cavity that was dimensioned is
a cavity that can be built. Quartz lands closest to 2.45 (−3.36 MHz); sapphire
costs 15 MHz, which is 4.5% of the 332.7 MHz rival separation — it does not
threaten H1's mode ordering.

### 🔑 The instrument's resolved floor is r ≈ 4–5 mm, NOT the assumed 1.0 mm

The no-torch case has an **exact** analytic answer — an empty cavity is E ∝
J₁(χ′₀₁r/a) with no dielectric to perturb it — so measured/J₁ is a **prior-free
calibration of the probe rake against itself**. Fitting E₀ on r ≥ 15 mm only:

| r mm | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 | 5.0 | 8.45 | 10.5 | 15 | 20 | 30 | 42.3 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| meas/J₁ | 2.82 | 1.89 | 1.42 | 1.26 | 1.19 | 1.14 | 1.06 | 1.04 | 1.02 | 1.00 | 0.99 | 0.99 |

Monotonic divergence inward, exactly the signature run 1 identified: worst where
the field is smallest, vanishing at the mode peak. `R_RESOLVED = 1.0` puts the
cutoff **inside** the artifact zone, and F2 then read its "worst departure" off
the first included point — the one the instrument is worst at. That is
CONVENTIONS §1 in a new suit: *the answer sat at the edge of the region searched.*

✅ **E₀ fitted on the resolved region: 1.251e6 vs analytic rms 1.196e6 → 4.7%**,
which passes the **declared** V2 gate of 5%.
⚠️ The code enforces **20%**, not the 5% its own docstring declares, with a
comment justifying the relaxation. The relaxation was never needed — it was
compensating for the unit bug. **A gate widened to accommodate a broken check is
§9 running backwards.** Restore it to 5% on the resolved region.

### F2 — the J₁ map, honestly scored

In the region where the instrument is trustworthy (r ≥ 4 mm), departure from the
no-torch (≡ J₁) map:

| r mm | 4.0 | 5.0 | 6.6 | 8.2 | 8.45 | 9.2 | 10.5 | 15 | 20 | 42.3 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| sapphire | −0.5% | +3.5% | +7.7% | +10.4% | **+10.7%** | **+11.0%** | +8.4% | +2.3% | −0.5% | −2.7% |
| quartz | −15.7% | **−12.2%** | −8.5% | −6.1% | −5.7% | −5.2% | −5.0% | −4.4% | −4.1% | −1.5% |

🔴 **F2 FIRES, but marginally and for a physical reason** — not the 37–65% the
log claimed. Sapphire **concentrates** the field, peaking at **+10.9% at r =
8.45–9.2 mm**, which is the outer tube's own wall (8.5–10.0 mm), and decays to
zero by r = 20 mm. Quartz **dilutes** it, −12% at r = 5 mm. Opposite signs,
both localised at the tubes: this is a dielectric doing what a dielectric does,
not a map failure.

🔑 **The correct conclusion is narrower than "the J₁ map is RETIRED".** The map
is good to ~3% outside r = 15 mm and wrong by 10–12% *in the bore*, in a
direction that depends on tube material. For ignition work — which lives entirely
in the bore — it must be replaced by the measured profile. For anything that
lives at the mode peak (coupling, Q, stored energy) J₁ is fine.

### ✅ Argon lights, in sapphire

With the sqrt(2) double-count removed, the contours land **inside the 8.5 mm bore**:

| threshold | sapphire | quartz |
|---|---|---|
| 1.7 kV/cm | r ≥ 6.0 mm ✅ | r ≥ 6.6 mm ✅ |
| 2.1 kV/cm | r ≥ 7.4 mm ✅ | r ≥ 8.2 mm ✅ |
| 2.5 kV/cm | r ≥ 8.2 mm ✅ | r ≥ 10.5 mm 🔴 outside |

⚠️ Sapphire's field concentration is what buys this: it is the +10.9% at r≈8.5 mm
that pulls the 2.5 kV/cm contour back inside the bore. **The dielectric that
breaks the J₁ map is the same dielectric that makes the margin.** Quartz, which
dilutes, loses the top threshold.

🔑 This does NOT reopen cold ignition. These are ARGON breakdown fields at a
2.5 kV/cm ceiling; the N₂ avalanche threshold that killed cold ignition is
~100–150 Td and is untouched by a 10% field change. The thermal-kernel
conclusion stands.

### ✅ A genuinely controlled differential

`no_torch` and `outer_sap` have an **identical mesh SHA** (79eeb7eb8c70, byte-identical,
44,788 tets) and differ only in the permittivity bound from the sidecar. The
−13.71 MHz is therefore a pure ε effect with mesh, partition and solver held
exactly fixed — §4b satisfied by construction rather than by argument. `full_sap`
and `full_quartz` share their own mesh pair at 51,960 tets.

⚠️ Note "no-torch" here means **torch volume present at ε = 1**, not absent
geometry — which is why it is a valid control and why V2-Q reproduced the
`--no-torch --no-inner` Q_bare to 0.31% (44,245 vs 44,384).

### Verified, not assumed: the meshed geometry IS the predicted geometry

`--torch-tube od,wall = 20,1.5` → r 8.5–10.0 mm; `--intermediate od,wall = 16,1.0`
→ r 7.0–8.0 mm; `--injector od,id = 5,2` → r 1.0–2.5 mm. The sidecar tuples are
DIAMETERS, and read as radii they look like a completely different torch — checked
against `geometry.py`'s own help text before drawing any conclusion, per §4b.
⚠️ One docstring slip: the injector is r 1.0–**2.5** mm, not 1.0–1.5. Its Slater
contribution is −0.0 MHz either way.

### ⚠️ Correction to the entry above (same session): the floor is 6.6 mm, and quartz PASSES F2

The entry above scored F2 on "r ≥ 4 mm", a floor I picked by eye off the
calibration table before implementing the calibrator. Implemented properly —
scan inward from the mode peak, accept while no-torch meas/J₁ is within 10% —
the floor is **6.6 mm**, and seven probes (0.5, 1, 2, 3, 4, 5, 6) fall below it.
Corrected verdicts:

| case | worst in-bore departure | |
|---|---|---|
| outer-sap | +10.7% at r=8.45 mm | 🔴 fires, marginally |
| full-sap | +10.9% at r=8.45 mm | 🔴 fires, marginally |
| full-quartz | −8.5% at r=6.6 mm | ✅ **survives within 10%** |

**Quartz does not fire.** The −12.2% I quoted for it sat at r = 5 mm, below the
calibrated floor. The physical reading is unchanged and now cleaner: sapphire
concentrates the bore field ~11% and breaks the map marginally; quartz dilutes
it ~8% and the map holds.

🔑 **And separating two floors that I had conflated.** E₀ is a single scalar
NORMALISATION and must be fitted where the rake is flat (r ≥ 15 mm, ratio flat to
2%); F2 is a PER-RADIUS COMPARISON of two profiles on the same mesh, where the
shared artifact largely divides out, so it can use the wider 10% region. Fitting
E₀ out to 6.6 mm drags in radii still reading 1.04–1.06× and biases it high:
**8.8% against the gate, versus 4.7% on the flat region.** Both are now printed
(§3) so the choice is visible rather than assumed.

✅ **With that separated, V2 passes at 4.7% against the DECLARED 5%** — the 20%
gate is removed. Every falsifier now runs at the width the docstring committed to
before the solve.

## 2026-08-23 — 🔴 `ops/go`'s "is a rig running" guard has been BLIND to the entire H programme

`ops/go` refuses to rsync while a rig is running, because overwriting files a
live solve reads cost 6 of 16 grid points once. Its own comment records the
first version of the bug: it counted only palace ranks, missing the long
meshing window with zero ranks alive. Fixed then. But the rig-counting line it
was fixed INTO reads:

```sh
grep -c "^python3 -u e[0-9]"
```

**`e[0-9]`.** Written when every rig was e-series. `h1_aspect`, `h2_filter`,
`h3_eigen`, `h4_field` — every rig of the current programme — match none of it.
The guard has returned 0 for the whole H programme and would have cheerfully
synced modified code into a live solve. It never fired because nothing happened
to sync during one; that is luck, not safety.

✅ Now `^python3 -u [a-z]`, in `ops/go` and `ops/cleanremote.sh`. It OVER-matches
deliberately: a false "busy" costs one `NOSYNC=1` re-run, a false "idle"
corrupts a solve. **Fail closed.**

🔑 The shape is CONVENTIONS §7 — *a checker must be able to see what it checks* —
crossed with §2: the guard was maintained, tested and believed, while the thing
it names moved out from under it. A pattern hard-coded to the names that existed
when it was written is a value that stopped reaching its consumer. Prefer a
predicate that fails closed over one that enumerates what it knows about.

---

## 2026-08-23 — ✅ H3 IS ANSWERED, POSITIVELY — and it had been sitting on the instance since 08-22

🔴 **A LANDING FAILURE, NOT A MEASUREMENT FAILURE.** `h3_eigen` finished
**2026-08-22 21:37** and `h3_annular` **2026-08-22 23:30**. Both wrote complete
`result.json` files. **Neither was ever fetched to the repo**, and neither
produced a FINDINGS entry. `HYPOTHESES.md` still read *"H3 — NOT STARTED · THE
SOLE GATE"*, so every subsequent session — including this one, out loud —
repeated that H3 was unmeasured while ~20 converged solves answering it sat on
the volume.

⚠️ CONVENTIONS §8 says *"write conclusions to FINDINGS as they are obtained, not
at session end."* The failure mode it was written for is an interrupt losing
data. This is the **other** half: the data survived perfectly (persistent EBS)
and the CONCLUSION was lost, because a result that exists only as a remote JSON
is not a finding. **`ops/fetch.sh` is not optional, and a rig is not done when it
exits 0.**

### ✅ The answer: TE011 SUSTAINS, emphatically

η = 1 − Q_loaded/Q_bare, the fraction of dissipated power reaching the plasma
rather than the walls. `h3_eigen`, solid column, metal-like row (ne=1e20):

| R mm | 0.5 | 0.75 | 1.5 | 2.0 | 3.0 | 4.0 | 6.0 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q | 40,915 | 31,170 | 6,094 | 2,373 | 736 | 412 | 238 |
| **η** | 0.078 | 0.298 | 0.863 | **0.947** | **0.983** | **0.991** | **0.995** |

🔑 **At any plasma radius the flow box can actually produce (R ≳ 2 mm), TE011
delivers 95–99.5% of its dissipated power into the plasma.** H3's question —
*can TE011 sustain a discharge once a thermal kernel exists?* — is answered
**yes, with margin**, and the margin is not marginal. The wall is a rounding
error once the discharge exists.

⚠️ The gas-like row (lower ne) is weaker — η = 0.19 at R=2, 0.78 at R=4 — and
two of its points timed out. Sustaining is a function of density; the metal-like
row is the operating regime.

### The loading perturbation, which is what BLOCKED everything else

**The pull is UP and it is ~31 MHz, not ~1 MHz.** The earlier R=2 mm probe
reported +1.26 MHz and I generalised "about one linewidth" from it. At the
operating radius it is **+31.57 MHz** (r_i=2.0, r_o=8.5):

| r_o mm | 2.0 | 5.0 | 6.0 | 7.0 | 8.5 |
|---|---:|---:|---:|---:|---:|
| Δf MHz | +0.80 | +8.93 | +14.01 | +20.22 | **+31.57** |
| Q | 2,376 | 299 | 242 | 203 | **163** |
| loaded lw MHz | 1.03 | 8.23 | 10.17 | 12.17 | **15.22** |

✅ **The collapses hold.** 31.6 MHz is 9.5% of H1's 332.7 MHz rival separation,
and the loaded mode lands at **2.4815 GHz — still inside the 2.40–2.50 LDMOS
band**. H1's design point survives ignition as well as it survived the torch.

🔴 **But 31.6 MHz kills the in-band companion for good.** H4's TM-ignition
fallback wanted a companion at 2.500 GHz, 50 MHz away. A +31.6 MHz pull eats 63%
of that margin, and the loaded linewidth is 15.2 MHz — the two resonances
overlap. That route was already discarded on two independent legs; this is a
third, and it is the one H4 said it was waiting for.

🔑 **The tuning-loop requirement is now specified**: track **+31.6 MHz** with a
loaded linewidth of **15.2 MHz** — about two linewidths, not tens. Q falls
44,384 → 163, a factor of 272.

### ✅ The hollow-core prediction was met almost exactly

`h3_annular` tested whether removing a skin-shielded core raises power density.
Committed before the run: gain = r_o²/(r_o²−r_i²) if the core absorbs *nothing*.

| r_i, r_o | predicted | measured |
|---|---:|---:|
| 1.5, 6.0 | 1.067× | **1.07×** |
| 2.0, 6.0 | 1.125× | **1.12×** |

🔑 **And the mechanism is confirmed by a degeneracy the table makes obvious:**
Q, linewidth and η are *identical* across every r_i at fixed r_o — 163/15.2/0.9963
for r_i = 1.5, 2.0, 2.5 and 3.0 at r_o = 8.5; 242/10.17/0.9945 for both r_i at
r_o = 6.0. **The inner radius has no electromagnetic effect whatsoever.** The
core is fully skin-shielded (δ = 1.80 mm at ne=1e20), absorbs nothing, and
hollowing buys exactly the volume bookkeeping and not one percent more.

⚠️ This retires the earlier "~1.4× from hollowing" estimate, which was computed
at small radii in a box gas flow cannot produce.

### 🔴 What is NOT settled: the power-density optimum. F3 fired.

`h3_annular`'s own falsifier caught it:

```
ri=1.5: best ro=5.0  🔴 F3 FIRES — at the EDGE of the sampled range
ri=2.0: best ro=5.0  🔴 F3 FIRES — at the EDGE of the sampled range
```

r_o = 5.0 mm is the **smallest r_o sampled** in both rows. CONVENTIONS §1: *a
nearest-neighbour answer is only trustworthy if what it found is nearer than the
edge of the region searched.* **No optimum is claimed.** The row must be extended
to r_o = 3.0–4.5 mm before any power-density optimum is reported.

⚠️ Also unconverged and reported, not dropped (§3): `i2p5_o6` and `i3_o6` timed
out at 900 s (113 and 61 NLEPS); `h3_eigen` lost R=1.0 to a mesh Jacobian failure
and gas-like R=8, 16 to timeouts; `h3_loaded` lost r2_n19 to the same mesh
failure and r8p5_n18 to a timeout. **The sustaining conclusion does not depend on
any of them** — it rests on six converged metal-like points spanning R = 0.5–6.0.

### ⚠️ One caveat that H4 made visible only today

Every H3 solve carries `torch_material [1.0, 3.5e-05]` — **the torch tube is
geometrically present and electromagnetically vacuum**, the exact R101-in-eigen
bug `h4_field` diagnosed this morning. So:

- **η is unaffected.** It is a Q ratio, and H4 measured the torch's own Q cost at
  0.3%. The sustaining answer stands as measured.
- 🔴 **The absolute loaded frequency is not the built cavity's.** 2.4815 GHz is
  for a vacuum tube. Sapphire is worth −15.0 MHz (H4), so the real loaded point
  is ≈ **2.4665 GHz** — still comfortably in band, but this is an ESTIMATE from
  two perturbations measured on different configurations, and §4b says a sum of
  two epochs is not a measurement. **One solve with plasma AND sapphire together
  settles it**; until then the number carries its provenance.

---

## 2026-08-23 — 🔴 H3's POWER DENSITY IS A DEFINITION, NOT A MEASUREMENT. F3 cannot be answered by more solving.

I closed the last entry by saying `h3_annular`'s rows should be extended to
r_o = 3.0–4.5 mm to resolve F3. **That would have been wrong twice over**, and
the reason is one line of the rig:

```python
pdens = eta * P_REF / vol          # h3_annular.py:239
```

**Power density is computed, not measured.** It is η·P/V by construction. Checked
against every converged case — `pd × V` reproduces `η × P` to the last printed
digit, all eleven of them. So the 13-case sweep (~50 min of solver time, two
900 s timeouts) measured exactly **one** independent electromagnetic quantity —
**η** — and everything else in its table is arithmetic on η and πL(r_o²−r_i²).

### 🔴 Consequence 1: F3 fires forever, and extending the grid cannot stop it

η is pinned in **0.9932–0.9963** across every case with r_o ≥ 5 mm. With η
effectively constant, pd ∝ **1/V** — strictly monotonic in r_o. **There is no
interior optimum to find.** "Best r_o" will equal the smallest r_o sampled at
every future grid, so F3 will fire at every future grid, and each extension will
produce a new edge. The falsifier is sound; the swept quantity is degenerate.

### 🔴 Consequence 2: extending DOWNWARD repeats the error the rig documents

r_o = 5.0 mm is already below what flow permits. The rig's own docstring:
*"Plasma+aux 15–20 slm at 5000–7000 K, 15–30 m/s → r_o = 6.8–13.1 mm"* — and it
records that the FIRST grid, r_o 1–3 mm, was scrapped precisely because *"flow
cannot produce that plasma… sampling it would have measured a geometry no torch
can make."* My proposed 3.0–4.5 mm extension was that same box, re-entered by the
back door, chasing a monotone into a region the hardware cannot reach.

🔑 **The optimum is not an EM question.** Power density = η·P/V with η ≈ 0.995,
so it is set by the smallest volume **flow** permits. At the flow floor
(r_o ≈ 6.8 mm, r_i ≈ 2 mm): V ≈ 12,200 mm³ → **≈ 8.1e7 W/m³**. That number needs
no solver. **H3's last open item is closed analytically. No further solves.**

### 🔴 CORRECTION to this morning's entry: my hollowing evidence was CIRCULAR

I wrote that hollowing *"behaves exactly as predicted — predicted 1.067×/1.125×,
measured 1.07×/1.12×"* and called it a hit on a committed prediction. It was not
a test. The prediction was r_o²/(r_o²−r_i²) — a **volume ratio** — and pd is
*defined* as inversely proportional to volume. The moment η failed to move, that
agreement was guaranteed by arithmetic. **A prediction that the rig's own
definition forces cannot be evidence for the mechanism it was meant to test.**

✅ **The mechanism is still right; here is the non-circular evidence.** Use the
frequency perturbation, which measures field exclusion and is not defined in
terms of volume:

| r_o mm | r_i mm | volume removed | Δf MHz | change in Δf |
|---:|---:|---:|---:|---:|
| 6.0 | 0.0 | 0.0% | 13.12 | — |
| 6.0 | 1.5 | 6.2% | 13.18 | +0.5% |
| 6.0 | 2.0 | **11.1%** | 13.15 | +0.2% |
| 8.5 | 1.5 | 3.1% | 30.65 | — |
| 8.5 | 2.0 | 5.5% | 30.71 | +0.2% |
| 8.5 | 2.5 | 8.7% | 30.60 | −0.1% |
| 8.5 | 3.0 | **12.5%** | 30.67 | +0.1% |

**Removing up to 12.5% of the plasma volume changes the perturbation by ≤0.5%,
non-monotonically — i.e. within mesh noise.** The core contributes essentially
nothing to field exclusion while occupying an eighth of the volume. *That* is
skin shielding measured (δ = 1.80 mm at ne=1e20), and it is independent of any
volume bookkeeping.

⚠️ Note η is a weak test of the same thing and I should not lean on it either:
η ≈ 0.995 is **saturated against the wall**, so it cannot fall much no matter
what the core does. When a quantity is pinned at its ceiling, its invariance is
not evidence.

🔑 **The general rule, and it is [[measure-the-outcome-not-the-coefficient]]
inverted:** *before sweeping a derived quantity, check whether the rig computes
it from the solve or from the inputs.* `pdens = eta * P_REF / vol` reads like a
measurement in every table it appears in. Grep the assignment. If the swept
variable appears on the right-hand side, the sweep is plotting a formula and the
solver is only supplying a constant.

---

## 2026-08-23 — 🔴 R101-extended: I rebuilt the torch-as-vacuum bug TWO HOURS after writing it up

`h3_superpose` was written to close H3's one remaining caveat by measuring plasma
and sapphire **together** instead of adding two numbers from different epochs.
Its first launch meshed all four cases with `torch_material = 1.0`. `sap_bare`
printed `torch: eps=1.0` and would have measured the sapphire shift of a **vacuum
tube** — i.e. zero — which is `h4_field` run 1's bug, reproduced by me, two hours
after I wrote its post-mortem into this file.

### Cause: `GEO` carries `--no-torch`, and it wins

```python
GEO = [..., "--no-torch", "--no-inner", ...]
```

I wrote `list(GEO) + ["--torch-material", "11.6,3.5e-05"]`. **`--no-torch` does
not remove the tube** — the sidecar still records `torch [20.0, 1.5]`. It pins the
MATERIAL to vacuum, and it wins over a later `--torch-material`. `h4_field`
strips the flag (its lines 161–163); I copied the geometry call from
`h3_annular`, which is a rig that *wants* a vacuum tube, and inherited its flag
list along with it.

🔑 **Copying a working geometry call from a rig with a different intent imports
that intent.** h3_annular is correct — it deliberately runs a vacuum tube. The
line was right there and right for it, and wrong for me.

### 🔴 And my own new guard was BLIND to it

I had just added `check_torch_bound` to `run()` (R101-extended, below) precisely to stop
this. It let all four cases through. The reason is worth stating because it is a
general trap:

> **The guard compares the CONFIG against the SIDECAR. This rig binds the config
> FROM the sidecar. Two values read from one source cannot disagree.**

The guard verifies *consistency*, which is exactly the wrong invariant when the
question is *"did the mesh honour what I asked for?"* — a question that needs a
third value, the REQUEST, which the guard never saw.

✅ Fixed by comparing **requested vs meshed** in the rig, where the request
exists:

```python
if abs(float(tm[0]) - tmat[0]) > 1e-9:
    rec["error"] = f"mesh ignored the request: asked eps={tmat[0]}, sidecar says {tm[0]}"
```

🔑 **The general rule: a consistency check between two values derived from one
source proves nothing.** CONVENTIONS §7 says a checker must be able to see what
it checks; this is the sharper form — *it must see a value the thing under test
did not supply.* R101 said "bind from the mesh"; that is necessary and it is not
sufficient, because binding from the mesh makes you agree with a mesh that is
wrong. Bind from the mesh, then **assert the mesh is what you ordered**.

### ✅ R101-extended, the guard itself (kept — it catches the OTHER direction)

`run()` now refuses any solve whose torch permittivity disagrees with its mesh
sidecar, and refuses a torch volume whose sidecar names no `torch_material`
rather than guessing. It has a self-test with known-bad input (§7) covering
sapphire-solved-as-vacuum and a missing declaration.

⚠️ **Deliberately in `run()`, not `eigen_cfg`.** Six rigs — h3_eigen, h3_annular,
h3_loaded, h3_eigenprobe, h4_seed, probecheck — **replace `Domains.Materials`
wholesale** after calling `eigen_cfg`, so a fixed `eigen_cfg` would be silently
discarded by exactly the rigs that need it (§2, the value never reaching its
consumer). `run()` sees the config actually being solved. Same reasoning that put
the lossy-domain check there.

✅ Existing rigs are unaffected: they group the torch into their "everything
else" material at ε=1.0 and their sidecars say 1.0, so the guard passes and now
prints the bound value.

### ⚠️ Unrelated gap found while launching: no pyflakes on the instance

`preflight` on the instance reports *"pyflakes not installed — undefined names
are NOT being checked."* The local gate has it; the remote one does not, and the
remote one is the last check before a rig burns solver time. `pip`/`pip3` are
absent and `apt-get install python3-pyflakes` finds no candidate. **Not fixed.**
Until it is, the instance-side lint is strictly weaker than the local one — and
§7b's failure mode (a `NameError` at call time, after meshing) is exactly what
pyflakes was added to catch.

---

## 2026-08-23 — ✅ h3_superpose: three cases clean, and the "0 NLEPS" failure is IDENTIFIED

`h3_superpose` measures the sapphire and plasma shifts **together**, to replace
HYPOTHESES' added estimate (§4b: a sum of two epochs is not a measurement).
Four cases, two meshes, each pair differing only in the permittivity bound from
the sidecar.

| case | torch ε | plasma | f GHz | df MHz | Q |
|---|---:|---|---:|---:|---:|
| vac_bare | 1.0 | no | 2.450467 | 0.00 | 43,997 |
| sap_bare | 11.6 | no | 2.436757 | **−13.71** | 44,287 |
| vac_hot | 1.0 | yes | 2.481566 | **+31.10** | 163 |
| sap_hot | 11.6 | yes | 🔴 timed out, 0 NLEPS | — | — |

✅ **V2 passes on both legs, on independently built meshes.** df_torch = −13.71
reproduces `h4_field`'s outer-tube −13.71 **exactly**; df_plasma = +31.10
reproduces `h3_annular`'s +31.57 to **1.5%**. The two rigs being combined are
reproduced before anything is claimed about their combination.

🔴 **F1/F2 CANNOT BE EVALUATED. Nothing is claimed about superposition.** The
additive estimate for the built cavity (−13.71 + 31.10 = +17.39 MHz →
**2.46786 GHz**) remains an ESTIMATE, exactly as flagged, and it is still not a
measurement.

### 🔑 The "0 NLEPS iterations" failure is the DIV-FREE PCG DIVERGING

`h3_loaded`'s r2_n19 hole was logged as *"600 s, 0 NLEPS iterations, nconv=None,
an isolated hole between two converging points either side… Unexplained;
reported."* This is the second instance, and the palace log names it:

```
PCG solver did NOT converge in 1000 iterations (avg. reduction factor: 1.005e+00)
Linear solver did not converge, norm(Ax-b)/norm(b) = 1.573e+02
```

**Reduction factor > 1 — it is DIVERGING, not merely slow.** 0 NLEPS iterations
because it never leaves the divergence-free projection to reach the eigensolver
at all. This is a different animal from the shift-target stall (which reaches
NLEPS and sits there) and from prod-narrow's NLEPS divergence.

🔑 **The trigger is PERMITTIVITY CONTRAST ACROSS ZERO, and the isolation is
clean:**

| case | ε values present | outcome |
|---|---|---|
| sap_bare | +11.6, +1 | ✅ 66 s |
| vac_hot | +1, **−30.09** | ✅ 238 s |
| sap_hot | **+11.6, −30.09** | 🔴 diverges |

Neither ingredient alone is a problem. A strong POSITIVE dielectric adjacent to a
strong NEGATIVE-ε plasma is, and the auxiliary-space projection is where it
shows. CONVENTIONS §6d already predicted the neighbourhood — *"PI_1… is precisely
where eps changes sign, where the div-free PCG fails"* — but as a property of the
plasma alone. It is the **contrast**, and a dielectric can supply half of it.

✅ **This retro-explains r2_n19.** At ne=1e19 the Drude ε is ≈ −2, i.e. near the
sign change, where the same projection is worst conditioned. It was never an
isolated hole: it was the same mechanism at the other end of the contrast.

⚠️ **This is NOT the case for swapping the linear solver.** That warning
(prod-narrow) was about a NONLINEAR failure being misdiagnosed as a linear stall.
Here the failure IS linear and IS in the preconditioner, so the warning does not
apply — but n = 2 is not a licence to redesign the solver either. The next step
is one cheap decisive test, not a solver change.

### Next: lower the contrast

Quartz is ε = 3.78 — a real candidate material `h4_field` already measured, and
**one third of sapphire's contrast**. If quartz+plasma converges it (a) supports
the contrast mechanism, (b) bounds where the instrument works, and (c) yields a
genuine superposition test at a material we may actually build with. One solve.

## 2026-08-23 — ✅ pyflakes installed on the instance; the remote gate was silently weaker than the local one

`preflight` on the instance had been reporting *"pyflakes not installed —
undefined names are NOT being checked"* — and **exiting 0**. So the last gate
before a rig spends solver time was strictly weaker than the local one, and the
failure it stops (§7b: a `NameError` at call time, after meshing, which cost two
launches) was going unchecked exactly where it bites.

🔴 **The first three attempts to fix it all failed misleadingly:** `pip` and
`pip3` are absent, `python3 -m ensurepip` is absent, and
`apt-get install python3-pyflakes` reported **"Unable to locate package"**. That
last one reads like "not available for this image" and is not — the package list
was simply stale. `apt-get update` first, and it installs: **pyflakes 3.2.0**.
Remote `preflight` now reports the same 2 warnings as local, with the
not-installed line gone.

✅ Added to `bootstrap.sh` (with `update` in the same command, and a comment
saying why), because **pyflakes lives on the ROOT filesystem, not the persistent
volume — every spot reclamation loses it** while `/opt/amip` survives intact.
✅ Added to `ops/mount.sh`'s verification block, so a replacement instance
REPORTS the gap at the moment it is being certified rather than degrading
quietly weeks later.

🔑 **A degraded checker that exits 0 is the §7 failure with a warning attached.**
The warning was printed on every remote launch in this session and read past
every time, because it sat among two others that are permanent and expected.
A check that cannot run should be visible where the environment is *certified*,
not only where it is *used*.

⚠️ Also fixed here: `ops/mount.sh` carried a THIRD copy of the rig-liveness
pattern, `^python3 -u [eh][0-9]` — narrower than the `[a-z]` that `ops/go` and
`ops/cleanremote.sh` were corrected to earlier today. Three copies of one
predicate, two of them wrong at different times.

### 🔴 CORRECTION (same session, user-caught): I installed it in the wrong interpreter AND the wrong filesystem

The entry above is wrong about the fix. `sudo apt-get install python3-pyflakes`
puts pyflakes in **`/usr/bin/python3`**. Rigs do not run that. `ops/remote.sh`
launches with

```sh
source /opt/amip/env.sh && ... python3 -u $RIG      # -> /opt/amip/envs/emsim/bin/python3 (3.12)
```

so the rig's interpreter is the **env on the persistent volume**, a different
Python with a different package set. Two things were wrong at once:

1. **Wrong filesystem.** The root fs is wiped by every spot reclamation; the env
   lives on `/opt/amip`, which survives. Putting a tool in `bootstrap.sh`'s apt
   line guarantees re-losing it — which is what `bootstrap.sh` exists to prevent.
2. **Wrong interpreter.** Even on this instance it would never have been seen by
   a rig.

🔴 **And my verification was circular in the same way the R101-extended guard was.** I
checked with `ssh "python3 preflight.py"` — a bare login shell, which is
`/usr/bin/python3`, the very interpreter apt had just fixed. **I tested the
thing I had changed, not the thing that runs.** The warning disappeared and
proved nothing.

### 🔑 The real bug underneath, which the pyflakes hunt exposed

`ops/remote.sh` and `ops/remote_env.sh` **lint and launch under different
interpreters**:

```sh
ssh "cd $R && python3 preflight.py $RIG"                       # /usr/bin/python3
ssh "... source /opt/amip/env.sh && python3 -u $RIG ..."       # envs/emsim/bin/python3
```

The gate has been certifying an environment the rig never executes in — for the
whole life of these scripts. Every import-visibility check preflight makes was
answered by the wrong Python. That is CONVENTIONS §7 at the level of the
harness: *a checker must be able to see what it checks*, and this one was
looking at a different machine's worth of packages.

✅ Both scripts now `source /opt/amip/env.sh` before linting.
✅ `pip install --no-deps pyflakes` into `/opt/amip/envs/emsim` — **3.4.0**,
verified by running preflight exactly as `remote.sh` now does. `--no-deps`
because a solve was live in that env.
✅ `bootstrap.sh`'s apt line reverted; the install moved to the env-creation
step, next to the gmsh import check, with the reasoning recorded.
✅ `ops/mount.sh` now probes `$PREFIX/envs/emsim/bin/python3`, not the login
python, and tells you the pip command rather than the apt one.

⚠️ The root-level apt package is left installed. It is harmless, it will vanish
at the next reclamation, and nothing depends on it.

🔑 **The rule this is the third instance of today:** *verify with the thing that
consumes the value, not the thing you just changed.* R101-extended bound the config from
the sidecar and compared it to the sidecar. Here I fixed the login python and
tested the login python. Both times the check passed and the system was broken.

---

## 2026-08-23 — 🔑 SUPERPOSITION FAILS: dielectric and plasma REINFORCE by 8.6%

`h3_superpose`, quartz row. All four cases below share their meshes pairwise —
`vac_bare`/`qtz_bare` on one, `vac_hot`/`qtz_hot` on another — differing **only**
in the permittivity bound from the sidecar, so every difference is a pure ε
effect at fixed mesh, partition and solver (§4b satisfied by construction).

| case | torch ε | plasma | f GHz | df MHz | Q |
|---|---:|---|---:|---:|---:|
| vac_bare | 1.0 | no | 2.450467 | 0.000 | 43,997 |
| qtz_bare | 3.78 | no | 2.447363 | **−3.104** | 43,943 |
| vac_hot | 1.0 | yes | 2.481566 | **+31.099** | 163 |
| qtz_hot | 3.78 | yes | 2.480882 | **+30.415** | 156 |

```
df_torch + df_plasma  =  -3.104 + 31.099  =  +27.995 MHz
MEASURED together                          =  +30.415 MHz
residual                                   =   +2.420 MHz   (+8.6% of the sum)
```

🔑 **The two perturbations DO NOT ADD.** The residual is **302× the mesher
jitter** (8 kHz) and 121× the differential-work floor (20 kHz), so it is a
measurement, not noise. Equivalently: the plasma pull is **+31.10 MHz alone but
+33.52 MHz with quartz present, a 7.8% amplification.**

✅ **F1 does not fire** (|residual| = 2.42 > 2 MHz) and **F2 does not fire**
(residual > 0). The committed prediction — *"I predict superposition FAILS, and
in the direction of reinforcement"* — is met, in sign and roughly in magnitude
(predicted 10–20%, measured 8.6%).

🔴 **Consequence: HYPOTHESES' added estimate was WRONG, and wrong in the safe
direction.** Adding two epochs underestimates the loaded frequency. It is not a
large error here, but it is systematic, one-sided, and it grows with ε — sapphire
is 3× quartz's contrast.

### ⚠️ The MECHANISM I proposed is NOT established, and one measurement contradicts it

I predicted reinforcement from field concentration: the dielectric raises E in
the annulus the plasma occupies, energy goes as E², so the plasma perturbs more.
**The sign came out right and that is not evidence the reason is right.**

`h4_field` measured quartz **DILUTING** the bore field — −5.7% at r=8.45 mm,
−6.1% at 8.2 mm, against no-torch. A weaker field where the plasma sits predicts
*anti*-reinforcement, the opposite of what was measured.

⚠️ Those are not strictly comparable: h4_field's quartz case is `full-quartz`,
carrying the intermediate (r 7.0–8.0 mm) and injector (r 1.0–2.5 mm) tubes, while
`h3_superpose` runs `--no-inner` — outer tube only. The profiles come from
different dielectric geometries. **But that is exactly the point: I do not have a
bore field profile for the geometry actually measured here**, because
`h3_superpose` declares no probe rake.

🔑 **What is settled: the cross-term is real, positive, and ~8.6%.** What is not
settled is why. A second-order cross-term is expected whenever two perturbations
sit in overlapping regions — each reshapes the field the other sees — and that
requires no claim about the sign of the field change. **The concentration story
is one candidate and currently the weaker one.** Settling it needs a probe rake
on these same meshes, which is cheap (re-solve, not re-derive) and belongs to
whoever next touches this rig. Until then the mechanism is UNRESOLVED and should
not be repeated as fact.

### ✅ F3 — the built cavity, operating

**f₀ = 2.480882 GHz, Q = 156**, comfortably inside 2.40–2.50. **H1's design point
survives the torch AND the plasma together**, measured rather than estimated, for
a quartz torch.

### 🔴 CORRECTION: the sapphire failure is PCG STAGNATION, and "0 NLEPS" was run-specific

I characterised `sap_hot` as *"the div-free PCG DIVERGING… 0 NLEPS iterations
because it never leaves the divergence-free projection to reach the eigensolver
at all."* The re-run falsifies the specific claim while confirming the general
one:

| run | NLEPS reached | PCG reduction factors |
|---|---:|---|
| 1 | **0** | 1.005 (>1, diverging) |
| 2 | **49** | 0.9988 – 0.9999 (77 non-convergences) |

**Both timed out at 900 s; neither converged.** But the mode is **stagnation, not
divergence** — a reduction factor of 0.999 per iteration means each linear solve
exhausts its 1000-iteration cap having reduced the residual by ~35%, so the outer
eigensolve crawls. Run 1's 1.005 was the tail of the same behaviour, not a
different one.

⚠️ **"0 NLEPS iterations" is therefore NOT the signature I said it was.** It is
just how many outer iterations happened to fit in the timeout, and it varies
between identical runs. I built a diagnostic category on n=1 — the same shape as
the retraction in §6c, where one stall became "the eigensolver cannot do a lossy
plasma". **A count that varies run to run cannot be a signature.**

✅ **What survives, and it is the useful part:** the trigger is still
permittivity contrast across zero, and the isolation still holds — `sap_bare`
(+11.6, +1) solves in 66 s, `vac_hot` (+1, −30.09) in 238 s, `qtz_hot` (+3.78,
−30.09) in ~300 s, and only `sap_hot` (+11.6, −30.09) fails. **Quartz converging
is the new evidence**: it sits at a third of sapphire's contrast and solves
fine, which is what the contrast hypothesis predicts and what a "sapphire is
special" story would not.

🔑 The correct statement: **the auxiliary-space preconditioner degrades as the
positive-to-negative permittivity ratio grows, and somewhere between 3.78 and
11.6 (against ε = −30.09) it stops being usable within a 900 s budget.** That is
a bound, not a cliff, and it is stated as one.

⚠️ **r2_n19 is NOT explained by this after all** — or at least not shown to be.
I claimed it was "the same mechanism at the other end of the contrast" (ε ≈ −2,
near the sign change). That remains plausible and is now **unverified**, because
the signature I linked them by ("0 NLEPS") turns out not to be a signature.
Someone should check r2_n19's palace log for the same stagnation before the two
are joined.

### ✅ r2_n19 IS the same failure — and the mechanism is ε NEAR ZERO, exactly as §6d predicted

I said the r2_n19 link was now unverified and someone should check the log. It
took one grep. `h3_eigenprobe`, same rig, same machine, adjacent densities:

| ne | Drude ε | σ S/m | PCG behaviour |
|---:|---:|---:|---|
| 1e18 | **+0.689** | 0.275 | (solves — r2_n18, 281 s) |
| 1e19 | **−2.109** | 2.75 | 🔴 **92 non-convergences, worst factor 1.007** |
| 1e20 | −30.089 | 27.5 | ✅ **0 non-convergences, factor 0.814** |
| 1e21 | −309.9 | 275 | (solves — r2_n21, 100 s) |

**The failure is not at large negative ε — ε = −30 and ε = −310 are both
healthy. It is at SMALL |ε|, straddling the sign change**, which happens between
ne=1e18 (+0.689) and ne=1e19 (−2.109). The auxiliary-space preconditioner needs
a definite mass term and ε→0 removes it locally.

🔑 **CONVENTIONS §6d called this in advance and in these words** — *"PI_1 =
omega_p/nu_m -> the sign of eps_eff (eps crosses 0 at wp = nu)… it is precisely
where eps changes sign, where the div-free PCG fails, and where the sustaining
question lives."* It was written as a SAMPLING argument, from the constitutive
relation, before any of this was measured. It is now measured. §6d's grid
diagnosis — *"PI_1's transition was STRADDLED BUT NEVER SAMPLED"* — was
identifying the one region the instrument cannot enter.

🔴 **So my "other end of the contrast" story was WRONG, and I should not have
written it.** I joined r2_n19 to sap_hot by a shared symptom ("0 NLEPS") that
turned out not to be a signature, and invented a single mechanism to cover both.
There are **two distinct regimes**, and only one of them is about contrast:

| regime | example | trigger |
|---|---|---|
| **ε near zero** | ne=1e19, ε=−2.1 | the mass term vanishes locally |
| **high +ε beside strong −ε** | sapphire+plasma, +11.6/−30.09 | strongly indefinite operator |

⚠️ I am NOT unifying them further. Both plausibly reduce to "the preconditioner
assumes something the operator no longer satisfies", and that sentence explains
nothing a test could distinguish. §6c's lesson was generalising from n=1 in both
directions; two regimes with two pieces of evidence each is where this stops.

### 🔑 The usable operating envelope for the eigensolver

At ne=1e20 (ε = −30.09), by positive-to-negative permittivity ratio:

| dielectric | ε | ratio ε₊/|ε₋| | outcome |
|---|---:|---:|---|
| vacuum | 1.0 | 0.033 | ✅ 238 s |
| quartz | 3.78 | 0.126 | ✅ ~300 s |
| sapphire | 11.6 | **0.386** | 🔴 >900 s, stagnates |

**Eigen is usable up to a ratio of at least 0.126 and unusable at 0.386.** That
is a bound with two brackets, not a cliff, and it is stated as one. It is also
enough to plan with: **quartz is measurable, sapphire is not, by this route.**

---

## 2026-08-23 — 🔴 MY REINFORCEMENT MECHANISM IS FALSIFIED, and the real one is measured

Committed in `h4_field`'s docstring **before** the solve: *"outer-qtz DILUTES the
bore field at the plasma radii… and that FALSIFIES my reinforcement mechanism."*

**Measured, in the exact dielectric geometry `h3_superpose` used (outer tube
only), over the plasma's absorbing skin (r = 6.7–8.5 mm, δ = 1.799 mm):**

| case | mean dE/E over the skin | |
|---|---:|---|
| outer-sap | **+10.1%** | CONCENTRATES |
| outer-qtz | **−5.6%** | **DILUTES** |

🔴 **Quartz gives the plasma a WEAKER field, and the perturbations still
REINFORCE (+2.42 MHz). "The dielectric concentrates the field where the plasma
sits" is NOT why. Dropped.** The sign of my prediction was right and the reason
was wrong — which is the whole point of having declared it in advance.

⚠️ Also settled: the concentrate/dilute sign is a **material** property, not an
inner-tube artifact. outer-sap +10.1% vs outer-qtz −5.6% at *identical* geometry
reproduces full-sap +10.2% vs full-quartz −6.3%. My earlier "not strictly
comparable" hedge was correct to make and turned out not to matter.

### 🔑 THE REAL MECHANISM: the PLASMA suppresses the DIELECTRIC, not the reverse

I had the direction backwards. The residual is a **difference of differences**,
and each difference is *within one mesh*:

```
quartz's shift, NO plasma   (mesh A):  -3.104 MHz
quartz's shift, WITH plasma (mesh B):  -0.684 MHz
residual                            :  +2.420 MHz
```

**The plasma suppresses the tube's frequency shift by 78%.** That is the same
+2.420 MHz I had been reporting as "the plasma pull grows 7.8%" — identical
arithmetic, but one framing is a small effect needing a subtle cause and the
other is a large effect with an obvious one. **I picked the framing that made the
number small and mysterious.** ([[measure-the-outcome-not-the-coefficient]].)

✅ **And the obvious cause is measured.** Slater's shift for a dielectric goes as
the ELECTRIC energy stored in it. Torch electric energy, normalised by total
magnetic energy, TE011 identified by exact frequency match:

| case | E_elec[torch]/E_mag | plasma's effect |
|---|---:|---:|
| vac_bare | 8.888e-04 | — |
| vac_hot | 2.279e-04 | **−74.4%** |
| qtz_bare | 3.616e-03 | — |
| qtz_hot | 9.148e-04 | **−74.7%** |

**The overdense plasma excludes field from the bore, cutting the electric energy
at the tube by ~75%, so the tube perturbs ~75% less.** Predicted shift
suppression 74.4–74.7%; **measured 78%**. First-order Slater, agreeing to ~3
points.

🔑 **The consistency check that seals it:** the fractional energy reduction is
**74.4% for a vacuum tube and 74.7% for a quartz tube** — essentially identical.
The shielding is a property of the PLASMA and is independent of what the tube is
made of, which is exactly what this mechanism predicts and what a
dielectric-driven story cannot explain.

### What this changes

- ✅ Superposition still fails; the number is unchanged at **+2.42 MHz**.
- ✅ The built cavity's loaded point is unchanged: **2.480882 GHz, Q = 156**.
- 🔴 The DIRECTION of the effect is the opposite of what I wrote: dielectric
  shifts get **suppressed** under load, they do not amplify the plasma.
- 🔑 **Design consequence, and it is the useful one:** *the torch material
  matters ~4× less in operation than cold measurements suggest.* Sapphire's
  −13.71 MHz cold becomes roughly −3 MHz loaded, if the 75% suppression holds at
  ε=11.6. That widens the material choice — and it is a PREDICTION, untested,
  because sap_hot does not converge.

### ✅ outer-qtz's other results, and a correction to the record's quartz numbers

The full run also fills a gap and moves one number:

| case | f GHz | shift MHz | Q |
|---|---:|---:|---:|
| no-torch | 2.450496 | 0.00 | 44,245 |
| outer-sap | 2.436782 | −13.71 | 44,280 |
| **outer-qtz** | **2.447392** | **−3.10** | **43,937** |
| full-sap | 2.435493 | −15.00 | 44,215 |
| full-quartz | 2.447135 | −3.36 | 43,895 |

✅ **−3.10 MHz reproduces `h3_superpose`'s df_torch(quartz) = −3.104 MHz exactly,
across two independently written rigs on separately built meshes.** That is the
strongest cross-check in this programme to date: different rig, different mesh
epoch, same number to 4 ppm of the carrier.

✅ **F2: outer-qtz SURVIVES** — worst bore departure 7.5% at r=6.6 mm, inside the
10% gate. Both quartz cases pass F2 and both sapphire cases fire (10.7%, 10.9%).
**The J₁ map survives a quartz torch and does not survive a sapphire one.**

⚠️ **The inner tubes are worth 0.26 MHz on quartz and 1.29 MHz on sapphire**
(outer→full: −3.10→−3.36, −13.71→−15.00). Small, and they are the only
difference, so the earlier claim that the concentrate/dilute SIGN was a material
property rather than an inner-tube effect is confirmed by a second route:
adding the inner tubes moves the magnitude a few percent and never the sign.

🔑 **All four F1 pass.** Every torch configuration measured — sapphire or quartz,
inner tubes or not — leaves TE011 inside 2.40–2.50 GHz. H1's design point is
robust to the torch across the whole material and geometry range tested.

---

## 2026-08-23 — COMMITTED PREDICTION, before the eps sweep returns

`h3_superpose` is running eps = 1.0, 2.0, 3.78, 6.0, 8.0, 11.6 as bare/hot pairs,
to ask whether the 78% suppression is a LAW or a coincidence at one dielectric.
Stated now, while the answer is unknown:

**I predict suppression is CONSTANT to within ~2 points across the range.**

The reasoning is not a hunch — it is the energy data already measured. Slater's
dielectric shift is proportional to `E_elec[torch] / W`, which is exactly the
quantity whose drop was measured:

| tube | E_elec[torch]/E_mag, cold → loaded | drop |
|---|---|---:|
| vacuum, ε=1.00 | 8.888e-04 → 2.279e-04 | **74.4%** |
| quartz, ε=3.78 | 3.616e-03 → 9.148e-04 | **74.7%** |

**0.3 points of drift over a 3.8× change in ε.** Linear extrapolation to ε=11.6
gives ~75.5%. If the mechanism is the plasma excluding field from a region — a
property of the plasma, not of what sits in that region — the fraction should
barely move.

⚠️ **The one thing that could break it**, and why the sweep is worth running
rather than asserting: at higher ε the tube BACK-REACTS more strongly, pulling
field into itself (measured: outer-sap CONCENTRATES +10.1%, outer-qtz DILUTES
−5.6%). A tube that reshapes the local field is no longer a passive probe of it,
and the sign of that back-reaction flips between quartz and sapphire. **The two
points I have are both on the DILUTING side of that flip.** Extrapolating across
a sign change is exactly the move CONVENTIONS §11 and §6b warn about.

🔑 So the honest position is: the mechanism predicts constancy, the back-reaction
is a named reason it might fail, and **ε = 6.0 and 8.0 are placed to straddle the
concentrate/dilute crossover** rather than to confirm anything.

**Falsifier, fixed now:** if suppression spans more than 5 points across the
converged range, it is NOT a law, the 78% must not be carried to sapphire, and
the "torch material matters 4× less in operation" design claim is withdrawn to a
quartz-only statement.

---

## 2026-08-23 — 🔴 H6 OPENED: sustainment under sample delivery, and it re-prioritises the driven rig

**User-raised.** H3's η = 0.95–0.995 was measured for a **clean, uniform plasma at
fixed ne = 1e20** — no aerosol, no matrix. The programme exists to measure
high-TDS soil extracts. That qualifier was never attached to the number, and
"TE011's azimuthal E has no axial path so TDS cannot short it" appears three
times in the record **only as an argument for ruling TM out** — never validated
for TE011.

### ✅ The EM half is largely de-risked already, by measurements made for other reasons

🔑 The sample travels up the central channel, r < 2 mm — **exactly where TE011's
field is zero**. `h3_annular` removed up to 12.5% of the plasma volume from that
core and the perturbation moved ≤0.5%, non-monotonically. **The same on-axis null
that makes TE011 unable to cold-ignite is what protects it from a conductive
sample column.** That is now an argument resting on measured field structure.

### 🔴 The thermal half is wide open, and lands exactly in the instrument's blind spot

Mass loading cools the plasma and lowers ne. η depends on ne steeply — and the
decade a sample is most likely to reach is the one decade with no data:

| ne | ε | η |
|---:|---:|---:|
| 1e18 | +0.689 | **0.185** |
| 1e19 | −2.109 | 🔴 **NO DATA — failed in BOTH rigs** |
| 1e20 | −30.089 | **0.947** |
| 1e21 | −309.9 | **0.956** |

**Sustainment falls 0.95 → 0.19 across two decades**, and ne = 1e19 failed in
`h3_loaded` (mesh ScaledJac) and in `h3_eigenprobe` (PCG stagnation, 92
non-convergences). Not bad luck: ε = −2.109 sits at the sign change that §6d
identified from the constitutive relation before any of it was measured.

🔑 **This merges two open items and raises their priority.** Sapphire's loaded
point needs driven because eigen stagnates at high ε⁺/|ε⁻|; H6 needs driven
because eigen stagnates at ε ≈ 0. **Same rig, two payoffs** — and it converts the
driven build from "nice to have for one number" into the gate on the terminal
hypothesis.

⚠️ Falsifier F3 is declared in advance: **if driven also fails at ε ≈ 0, the
limitation is the operator and not the eigen formulation, and no solver in this
toolchain answers H6.** Say so rather than reaching for a third solver — that is
§6c's over-correction in waiting.

⚠️ H6 is scoped to the EM/sustainment half only. Aerosol transport, desolvation
and atomisation efficiency are chemistry and belong with H5's external inputs.

---

## 2026-08-23 — 🔑 DRIVEN COST SCALES WITH Q, so it is CHEAPEST exactly where eigen fails

Before building the driven rig H6 and sapphire both need, I checked what it
costs. The number in the record — *"driven costs 2,500–2,900 s, eigen 155–882 s"*
(CONVENTIONS §6c) — is real and was measured on the **empty, high-Q** cavity. It
does not transfer, and the direction it fails in is the useful one.

**A driven sweep's cost is its sample count, and the step must resolve the
linewidth. Linewidth = f₀/Q, so samples ∝ Q.**

Calibrated on `e0k2_c11x8_drv` (16,000 samples in 1,542 s → 96 ms/sample), for a
±40 MHz band at 25 points across the 3 dB width:

| case | Q | linewidth | step needed | samples | est. solve |
|---|---:|---:|---:|---:|---:|
| empty cavity | 44,384 | 0.056 MHz | 2.2 kHz | 35,800 | ~3,450 s |
| with loop | 29,854 | 0.083 MHz | 3.3 kHz | 24,100 | ~2,320 s |
| **LOADED plasma** | **156** | **15.9 MHz** | **636 kHz** | **126** | **~12 s** |

🔑 **The loaded cavity needs 126 samples where the empty one needs 24,000 — a
190× reduction.** Driven solving for a loaded case is ~12 s of solver time
(assembly and setup will dominate the wall clock), against 238–400 s for the
eigen solves it replaces. **In the loaded regime driven is not the expensive
option; it is the cheap one.**

🔴 **This is CONVENTIONS §6 exactly — "do not reuse a parameter without
re-deriving it for the case."** The cost figure that sent H3 to eigenmode was
computed for a Q of 44,000 and applied to a problem whose Q is 156. Same shape as
E0l's 10.7 s toy inverting the fan-out answer: the benchmark was not imprecise,
it was in the wrong regime, and it pointed the wrong way.

🔑 **And the two methods are complementary in precisely the right way:**

- **eigen** cost is roughly Q-independent, but it **fails** where the operator is
  awkward — at ε ≈ 0 (H6's regime) and at high ε⁺/|ε⁻| (sapphire).
- **driven** has no NLEPS and no divergence-free projection, and gets **cheaper
  as Q falls** — i.e. cheaper the more heavily loaded the cavity is.

**The regimes where eigen fails are the regimes where driven is cheapest.** That
is not luck: both follow from the same fact, that a heavily loaded cavity has a
broad resonance and a strongly perturbed operator.

⚠️ Caveats before this is banked: the ±40 MHz band must actually contain the
loaded dip (it will move ~+31 MHz, so centre the band on the LOADED estimate, not
on 2.45); 25 points across the 3 dB width is a choice, not a derivation, and the
fit's sensitivity to it is untested; and per-sample cost was calibrated on a
different mesh size. **Treat ~12 s as an order of magnitude, not a budget.**

---

## 2026-08-23 — ✅ THE SUPPRESSION IS A LAW (over ε 2–6), and the eigen envelope tightens 3× 

The prediction committed before this sweep — *"suppression is CONSTANT to within
~2 points"*, derived from the measured energy fractions, with the back-reaction
named as the thing that could break it — is met.

| case | ε | cold MHz | loaded MHz | **suppressed** |
|---|---:|---:|---:|---:|
| e2 | 2.00 | −1.084 | −0.242 | **77.7%** |
| qtz | 3.78 | −3.104 | −0.684 | **78.0%** |
| e6 | 6.00 | −5.809 | −1.260 | **78.3%** |

**Spread 0.6 points over a 3× range in ε.** Each ratio is measured within one
mesh pair, so no comparison crosses a mesh.

🔑 **And it holds THROUGH the back-reaction crossover, which is the part that
matters.** I flagged that both my original points sat on the *diluting* side of
the flip (outer-qtz −5.6%, outer-sap +10.1%) and that extrapolating across a sign
change is what §11 and §6b warn about. ε=6 is at or past that crossover and the
suppression did not notice. **The named failure mode was tested and did not
occur** — which is worth more than the three points alone.

⚠️ There is a faint monotone drift, +0.3 points per ~1.9× in ε (77.7 → 78.0 →
78.3). Extrapolated once more it gives ~78.6% at sapphire. **That is an
extrapolation ~2× beyond the last measured point and it is labelled as one.**

### 🔴 e8 and sapphire did NOT converge — and that tightens the envelope 3×

| ε⁺ | ratio ε⁺/\|ε⁻\| | outcome |
|---:|---:|---|
| 1.00 | 0.033 | ✅ 238 s |
| 2.00 | 0.066 | ✅ |
| 3.78 | 0.126 | ✅ ~300 s |
| **6.00** | **0.199** | ✅ |
| **8.00** | **0.266** | 🔴 900 s, 19 NLEPS |
| 11.60 | 0.386 | 🔴 900 s (0 then 49 NLEPS) |

**The boundary is between ε⁺ = 6.0 and 8.0** against a plasma at ε = −30.089 —
ratio **0.199–0.266**, down from the 0.126–0.386 bracket. A 1.3× bracket instead
of a 3× one, and it cost two timeouts that were going to be spent anyway.

⚠️ Still a bracket, not a cliff. Nothing here says the transition is sharp, and
the two failures differ in how far they got (19 vs 0/49 NLEPS), which — per the
correction earlier today — is **not** a signature and should not be read as a
trend.

### 🔑 Sapphire is still reachable, and by the rig already built

Testing the law at ε=11.6 needs only the **frequency**, not Q. A dip *location*
is well defined even at the −0.06 dB the coupling forecast predicts for a loaded
cavity; it is the dip *width* that needs depth. So `h3_driven`'s coarse stage can
deliver sapphire's loaded f₀ despite being badly undercoupled, and the
suppression law is exactly the kind of question a shallow dip can still answer.

**Design claim, now resting on three points instead of one:** torch material
matters ~4.5× less in operation than cold measurements suggest. Sapphire's
−13.71 MHz cold should be ≈ **−2.9 MHz** loaded. ⚠️ Still a prediction — but a
prediction from a law that survived its own named falsifier, not from a single
coincidence.

### 🔴 CORRECTION: the rig printed "extrapolating to sapphire is justified". It is not.

`h3_superpose`'s law verdict ended *"Extrapolating it to sapphire is justified."*
**It is not, and the rig should never have said so.** Constancy over the measured
interval says nothing about a point 1.9× beyond the last one — and the two points
past it are unmeasured *precisely because* they are outside the range the
instrument can reach. That is CONVENTIONS §11 wearing a law's clothes.

✅ The message now names the interval, quantifies the drift instead of calling it
flat, and labels anything outside as extrapolation with its factor:

```
✅ CONSTANT within 5 points OVER eps 2-6 — a LAW on that interval
   ⚠️ drift +0.30 points per step; NOT flat, just nearly so.
   ⚠️ eps 8, 11.6 did NOT converge and are OUTSIDE the interval. Applying the
      law there is an EXTRAPOLATION (1.9x past the last point), not a
      measurement. Label it as one wherever it is used.
```

⚠️ **THIRD TIME TODAY a rig asserted past its own data**, and all three were in
runtime strings rather than in analysis:
1. `h3_superpose` printing "as predicted: the dielectric concentrates the field
   where the plasma sits" — a mechanism later FALSIFIED;
2. `h4_field` printing "an ordinary second-order cross-term needs no claim about
   the sign" — true when written, stale within the hour once the mechanism was
   measured;
3. this one.

🔑 **The pattern: a `print` is where a claim escapes review.** Analysis gets
re-read and re-scored (§10); a hardcoded string is written once, in the mood of
the moment, and then *printed as fact on every future run* — including runs whose
data contradicts it. **A verdict string must state what was measured and its
range, never what it implies.** The implication belongs in FINDINGS, where it can
be retracted.

### ✅ And a third confirmation that NLEPS count is not a signature

`sap_hot` has now been run three times under identical conditions and reached
**0, 49, and 115 NLEPS iterations**. All three timed out at 900 s. This is the
claim retracted earlier today, now with n=3 behind the retraction: **the count
only measures how many outer iterations fit in the timeout.**

---

## 2026-08-23 — 🔴 MY V1 ANCHOR WAS A §4b GEOMETRY MISMATCH — and the real number is far better news

`h3_driven`'s first case returned a coarse dip at 2.452380 GHz with
**|S11|min = −1.71 dB, Q_L ≈ 359**. I had declared V1 as *"ne=1e18 driven must
reproduce h3_loaded's eigen η = 0.185"*. From this dip:

    beta = 0.098,  Q0 = Q_L(1+beta) = 394,  eta = 1 - 394/44384 = 0.991

**0.991, not 0.185.** V1 will fire, and driven is not what is wrong.

### The mismatch

`h3_loaded`'s η = 0.185 was measured on a **SOLID COLUMN of radius 2 mm**.
`h3_driven` runs the **ANNULUS r = 2.0–8.5 mm** — h3_annular's operating point:

| | volume |
|---|---:|
| h3_loaded r2 (solid column) | 1,160 mm³ |
| h3_driven (annulus) | 19,790 mm³ |

**17.1× more plasma.** I anchored a measurement against a number from a different
geometry and wrote the falsifier into HYPOTHESES and FINDINGS before noticing.
CONVENTIONS §4b, in its own words: *"before calling a difference surprising, list
what else changed… if the answer is 'none', the comparison is not a
measurement."* Here what changed was the plasma itself.

⚠️ **Worse, it was avoidable by inspection.** The two rigs' own constants say
`RI, RO = 2.00, 8.50` and `R = 2 mm solid`. I copied the η value across without
copying the geometry it belonged to — the same move that made "one loop gave
β=0.067 then β=27.5" look like a mystery when it was two different cavities.

### 🔑 The number itself is a substantially better result for H6

**η ≈ 0.99 at ne = 1e18 — two decades below the operating point — for the
geometry that will actually be built.** The alarming picture in H6 (*"sustainment
collapses 0.95 → 0.19 between 1e20 and 1e18"*) was built on solid-column data and
does not describe the annulus. On the annulus, absorption stays ~99% across at
least two decades of density.

⚠️ **Not banked yet.** This is a COARSE-stage fit (20 kHz sampling of a ~6.8 MHz
feature, so the width is well resolved, but β comes from a −1.71 dB depth). The
fine stage is running. And the H6 conclusion needs the whole ne row, not its end.

### 🔴 There is no valid eigen anchor for this geometry, and that must be fixed

The only eigen measurement on the r=2.0–8.5 annulus is `h3_superpose`'s vac_hot
at **ne=1e20: Q=163, η=0.9963** — and that is exactly where the coupling forecast
says driven is weakest (β=0.003, −0.06 dB). So:

- the anchor I declared is the wrong geometry;
- the only right-geometry anchor sits where driven cannot fit.

✅ **The fix is to MAKE the anchor, not to borrow one:** one eigen solve of the
annulus at ne=1e18 (ε=+0.689, vacuum torch → ratio ~0.033, comfortably inside the
convergence envelope, ~250 s). That gives a well-coupled, same-geometry,
same-density point where driven and eigen can be compared directly. **Until it
exists, every gap number from this rig is UNANCHORED and must not be quoted** —
which is what the rig's own V1 message already says.

---

## 2026-08-23 — ✅ DRIVEN CROSSES THE GAP. F2 does NOT fire. The rig threw the answer away.

`h3_driven` reported 1 of 5 cases measured and V1 firing. **The run is far more
successful than its own report says**, and the failure was in FEATURE SELECTION,
not in the solver, the mesh, or the physics. Re-analysed offline from the saved
coarse sweeps (§10 — no re-solving):

| ne | ε | TE011 dip | depth |
|---:|---:|---:|---:|
| 1e18 | +0.689 | 2.4524 | −1.71 dB |
| 3e18 | **+0.067** | 2.4534 | −0.68 dB |
| 1e19 | **−2.109** | 2.4581 | −0.31 dB |
| 3e19 | −8.327 | 2.4729 | −0.26 dB |
| 1e20 | −30.089 | **2.4824** | −0.35 dB |

🔑 **A single mode, tracking smoothly and monotonically across the whole density
range — including ε = +0.067 (the sign change itself) and ε = −2.109, the point
that failed in BOTH eigen rigs.**

✅ **F2 DOES NOT FIRE.** The declared falsifier was *"if driven ALSO fails at
ε ≈ 0, the limitation is the OPERATOR and no solver in this toolchain answers
H6."* Driven sails through it. **The obstacle was the eigen formulation's
divergence-free projection, exactly as INSTRUMENT predicted** — *"the geometries
where the eigensolver diverges are exactly where driven should still work."*
That line has been in the record for weeks; this is the first time it has been
tested, and it holds.

✅ **And driven is VALIDATED against eigen at the anchor**: at ne=1e20 driven
gives **2.4824 GHz** against eigen's **2.481566** — **0.8 MHz** apart on a mesh
that additionally carries a coupling loop. Different solver, different mesh,
different formulation.

### 🔴 Why the rig discarded it: the global minimum is not the mode

At ne=1e20 the sweep contains **two** features — a broad one at 2.4472 (−1.28 dB)
and TE011 at 2.4824 (−0.35 dB). `analyse_driven` returns the **global** minimum,
so the rig locked onto the wrong one and every downstream guard then fired
correctly on a feature nobody wanted:

| ne | what the rig said | what was actually there |
|---|---|---|
| 3e18 | 3 dB outside band | TE011 at 2.4534, real |
| 1e19 | "no dip > 0.5 dB" | TE011 at 2.4581, −0.31 dB |
| 3e19 | "dip at the band edge" | edge feature, not TE011; TE011 at 2.4729 |
| 1e20 | 3 dB outside band | wrong feature picked; TE011 at 2.4824 |

🔑 **This is §1 in its purest form, and the record already names the cure:**
*"Always pair driven with eigen on the SAME mesh and match by ENERGY SIGNATURE"*
and E1b's *"mode identity across a large perturbation needs CONTINUATION, not
endpoint pairing."* Continuation is exactly what recovered it — the dip moves
2.4524 → 2.4824 in smooth monotonic steps, so following it from the anchored end
is unambiguous. **Selecting by "deepest" was the mistake; deepest ≠ wanted.**

⚠️ **My guards all behaved correctly and none of them could have saved this.**
Depth-threshold, band-edge and 3 dB-in-band each refused rather than fitting
noise — and each was refusing an honest measurement of the *wrong feature*.
**A guard on the quality of a fit cannot detect that the fit is of the wrong
thing.**

### 🔴 What is still NOT measured: η across the gap

Only ne=1e18 yields a resolvable width: **Q_L=359, β=0.098, Q₀=394,
η=0.9911**. The rest have 3 dB points outside the 45 MHz band, and the second
broad feature contaminates the baseline, so naive 3 dB crossings do not work.

⚠️ **And the two routes to Q₀ disagree by 12×**: width gives Q₀=394 at ne=1e18,
while β·Q_ext (using e0k2's Q_ext≈50,709) gives 4,975. **Q_ext is not
transferable** — it came from a different mesh, and β is not mesh-converged
(43% for a 1.25× refinement). Do not use it. This is the same trap R62/R112
recorded for β itself.

**So H6 has: the full frequency map, one η, and a validated method — not the η
row.** The pull is +2.0 MHz at ne=1e18 rising to +31.9 MHz at 1e20, relative to
the unloaded 2.4505.

### The fix, and it makes the rig cheaper

Widen and coarsen stage 1 — **2.30–2.65 GHz at 200 kHz ≈ 1,750 samples** — so
that features 15–100 MHz wide are fully bracketed and the interfering resonance
is visible rather than confusing. Then **select by continuation from the
eigen-anchored end**, not by global minimum, and refine only if needed. That is
fewer samples than the 2,250 currently spent per coarse stage.

---

## 2026-08-23 — ✅ H6's GAP IS BRIDGED. η ≥ 0.99 EVERYWHERE. F1 does not fire.

Fixed the selection (continuation, not global minimum) and re-scored **the same
saved sweeps** — §10 again, no re-solving:

| ne | ε | f₀ GHz | linewidth | Q_L | **η** | width |
|---:|---:|---:|---:|---:|---:|---|
| 1e18 | +0.689 | 2.4524 | 6.84 MHz | 359 | **0.9911** | 2-sided |
| 3e18 | **+0.067** | 2.4534 | 14.04 MHz | 175 | **0.9959** | 1-sided |
| **1e19** | **−2.109** | 2.4581 | 30.40 MHz | 81 | **0.9981** | 1-sided |
| 3e19 | −8.327 | 2.4729 | 27.44 MHz | 90 | **0.9979** | 1-sided |
| 1e20 | −30.089 | 2.4824 | 19.76 MHz | 126 | **0.9971** | 1-sided |

🔑 **F1 DOES NOT FIRE.** The declared falsifier was *"if η at ne=1e19 is below
0.5, the sustaining margin is one decade or less and mass loading is a HARD
nebuliser constraint."* **η(1e19) = 0.998.** Absorption stays above 99% across
**two full decades** of electron density.

✅ **Cross-validated against eigen where eigen works**: at ne=1e20 driven gives
η = 0.9971 against eigen's 0.9963 — **0.08%**. (Q₀ itself agrees only to ~21%,
but η = 1 − Q₀/44,384 is insensitive to Q₀ when Q₀ ≪ Q_bare. **η is the robust
quantity here and Q₀ is not** — worth remembering before anyone quotes a loaded
Q₀ to three digits.)

### 🔴 This overturns H6's central worry, which was mine and was wrong

H6 was opened this afternoon on the premise that *"sustainment collapses 0.95 →
0.19 between ne=1e20 and 1e18, and mass loading pushes ne DOWN into a decade we
cannot measure."* Both halves are now answered:

1. **The collapse is a SOLID-COLUMN artifact.** η = 0.185 came from a 2 mm solid
   column — 1,160 mm³. The annulus that will actually be built is 19,790 mm³,
   **17× the plasma**, and it does not collapse: η stays 0.991–0.998.
2. **The decade we could not measure is measured**, and it is the *best*
   absorbing point on the grid (η = 0.9981 at ε = −2.109). That is physically
   sensible: near ε ≈ 0 there is no field exclusion, the wave penetrates fully
   into a lossy volume, and absorption is maximal. **The region the eigensolver
   cannot enter is the region the plasma absorbs best.**

🔑 **So mass loading is NOT a hard EM constraint.** A sample that drops ne by two
decades still leaves >99% of dissipated power going into the plasma. H6's EM half
is answered positively; what remains is chemistry (aerosol transport,
desolvation, atomisation), which was scoped out of H6 deliberately.

### ⚠️ What is provisional

**Four of five widths are ONE-SIDED** — a symmetric-Lorentzian assumption, made
because the other flank runs into a neighbouring resonance at ~2.447 GHz or the
band edge. Two overlapping resonances are not symmetric, so these are
**indicative**. A wide re-run (2.30–2.65 GHz, 1,750 samples) is in flight to
replace them with two-sided widths.
⚠️ η is far less sensitive to this than Q_L is: halving a linewidth doubles Q_L
but moves η in the fourth decimal. **The conclusion does not rest on the widths.**

### 🔑 What actually fixed it — and what could not have

Selection by **continuation** from the unloaded TE011, following the mode in
smooth steps (+1.9, +1.0, +4.7, +14.8, +9.4 MHz), instead of taking the deepest
dip. At ne=1e20 that changes the answer from 2.4472 (a different, broader
resonance) to 2.4824 — which then agrees with eigen to 0.8 MHz.

⚠️ **Every quality guard I had — depth threshold, band edge, 3 dB-in-band —
fired correctly and none could have caught this**, because each was an honest
verdict about the *wrong feature*. **A guard on the quality of a fit cannot tell
you the fit is of the wrong thing.** The only defence is identifying the mode by
something other than the quantity being fitted: continuation here, energy
signature in the eigen rigs.

### ✅ CONFIRMED on the wide re-run — the full row, two-sided where it matters

| ne | ε | f₀ GHz | lw MHz | Q_L | β | **η** |
|---:|---:|---:|---:|---:|---:|---:|
| 1e18 | +0.689 | 2.4524 | 7.00 | 350 | 0.0981 | **0.9913** |
| 3e18 | +0.067 | 2.4534 | 14.00 | 175 | 0.0390 | **0.9959** |
| **1e19** | **−2.109** | 2.4580 | 30.80 | 80 | 0.0179 | **0.9982** |
| 3e19 | −8.327 | 2.4730 | 27.60 | 90 | 0.0149 | **0.9980** |
| 1e20 | −30.089 | 2.4824 | 18.20 | 136 | 0.0201 | **0.9969** |

✅ **V1 against eigen, same geometry** (h3_superpose vac_hot): f₀ **0.83 MHz**,
η **0.0006**. Driven and eigen agree.
✅ **F1: η(1e19) = 0.9982.** Absorption ≥ **99.1% over two decades** of ne.

🔑 **The one-sided fallback was sound.** Where the wide run produced a two-sided
width, it reproduced the narrow-band one-sided estimate: 3e18 gave 14.00 vs 14.04
MHz, 1e19 gave 30.80 vs 30.40, 3e19 gave 27.60 vs 27.44 — and η agreed to the
fourth decimal in every case. The symmetric-Lorentzian assumption was flagged as
provisional and has now been checked rather than assumed away.

🔴 **And the wide band proved the selection fix was necessary, not merely tidy.**
Every case has a minimum at **2.6232 GHz at −5.7 to −6.1 dB** — up to **19×
deeper than TE011's −0.31 dB**. A global-minimum selector would have locked onto
it at *every* density and returned a smooth, plausible, entirely wrong row.
Widening the band alone would have made things WORSE; only continuation saves it.
⚠️ That mode is the second m=0 candidate `h3_superpose` also reported
(2.623005). The cap loop couples to it far better than to TE011 — which is the
176 mm² mode-identity hazard the record warns about, now seen directly.

⚠️ `_report` then died on `KeyError: 'fine'` — I renamed the record key to
`wide_fit` in the driver and did not update the analysis. Cost nothing: §10, the
data was checkpointed per case and re-scored offline. **Fourth time today that
splitting driver from analysis turned a crash into a non-event.**

---

## 2026-08-23 — 🔴 CONTINUATION'S SEED MUST BE A MEASURED POINT IN THE SAME REGIME

`h3_sapphire` run 1 selected the wrong mode on its very first case, and it is a
different failure from the global-minimum one fixed an hour earlier.

I seeded continuation with the **analytic unloaded TE011** (2.4500 GHz), copying
the pattern from `h3_driven`. But `h3_sapphire` starts at **ne = 1e20**, where the
plasma pull is **+32 MHz**:

| candidate | distance from the 2.4500 seed |
|---|---:|
| **2.4472** (a competing feature) | **2.8 MHz** ← selected |
| 2.4824 (the real loaded TE011) | 32.4 MHz |
| 2.6232 (the deep interloper) | 173.2 MHz |

**The seed was outside the regime, so step one was the largest step of the run**,
and a competing feature sat ten times nearer than the truth.

🔑 **`h3_driven` gets away with the analytic seed only by accident of ordering** —
its first case is ne=1e18, where the pull is +2.4 MHz. Same seed, different
starting regime, wrong answer. **A pattern that works is not a pattern that is
right; it worked because of a property of that grid, not of the method.**

🔴 **And this would have produced a SELF-CONSISTENT WRONG ANSWER.** Quartz and
sapphire would each have tracked the same wrong feature in small steps, the
continuation guard would never have fired, and the *shifts between them* — which
is all the suppression law is made of — could have looked entirely plausible. A
crash is a gift by comparison.

✅ **Two fixes, and the second matters more:**
1. Seed from a **measured point in the same regime**: `SEED_GHZ = 2.4824`,
   h3_driven's ne=1e20 vacuum case — same density, same geometry, same rig family.
2. **ABORT after the first case** if it does not land within 1 MHz of that seed.
   V1 already checked this — but V1 runs at the END, by which time two more cases
   have been built on the bad seed. **A check that fires after the damage is a
   report, not a guard** (the same wording CONVENTIONS §6c used for the NLEPS
   budget, and the same mistake).

🔑 **The general rule, extending the continuation lesson:** continuation is only
as good as its first step. Seed it with something MEASURED in the regime you are
entering, and verify the first case against that seed before taking a second
step. An analytic value from a neighbouring regime is not a seed; it is a guess
that happens to be close sometimes.

---

## 2026-08-23 — ✅ THE SUPPRESSION LAW REACHES ε=11.6. MEASURED, not extrapolated.

`h3_sapphire`, driven, at the density eigen cannot solve. **Committed before the
run: sapphire's loaded shift is −2.9 ± 1.0 MHz.**

| case | ε | f₀ GHz | shift from vac | \|S11\| |
|---|---:|---:|---:|---:|
| vac | 1.00 | 2.4824 | — | −0.35 dB |
| qtz | 3.78 | 2.4818 | **−0.600 MHz** | −0.32 dB |
| **sap** | **11.60** | **2.4796** | **−2.800 MHz** | −0.27 dB |

**Measured −2.800 MHz. Predicted −2.9. A 0.1 MHz miss on a 1.0 MHz tolerance.**

✅ **V1** vacuum reproduces `h3_driven`'s ne=1e20 point to **0.00 MHz** on an
independently built mesh.
✅ **V2** quartz gives −0.600 MHz against **eigen's −0.684** — **84 kHz**, inside
the sweep's own ±100 kHz resolution. *This* is what licenses driven at ε=11.6:
the two solvers agree at a dielectric where both can work.
✅ **F1 does not fire.** ✅ **F3**: loaded f₀ = 2.4796 GHz, inside 2.40–2.50.

### The law across the full range

| ε | cold MHz | loaded MHz | suppressed | drift |
|---:|---:|---:|---:|---:|
| 2.00 | −1.084 | −0.242 | 77.7% | — |
| 3.78 | −3.104 | −0.684 | 78.0% | +0.29 |
| 6.00 | −5.809 | −1.260 | 78.3% | +0.35 |
| **11.60** | **−13.710** | **−2.800** | **79.6%** | **+1.27** |

**1.9 points across a 5.8× range in ε.** The drift is real and mildly increasing
(+0.3 per step to ε=6, +1.27 over the last, wider step), so the law is *nearly*
flat rather than flat — as it was already labelled. It is now measured over the
whole range that matters instead of extrapolated across half of it.

🔑 **THE DESIGN CLAIM NOW RESTS ON MEASUREMENT: a sapphire torch's −13.71 MHz
cold shift becomes −2.80 MHz loaded — 4.9× less.** Torch material is a far weaker
constraint in operation than any cold measurement suggests, and the material
choice can be made on thermal, optical and manufacturing grounds rather than on
frequency pull.

⚠️ The prediction was committed with an explicit retraction clause — *"if F1
fires, WITHDRAW the claim to a quartz-only statement; do NOT rescale the law to
fit."* It did not fire, so nothing is withdrawn. Recording that the clause
existed matters as much as the result: it is why the +0.1 MHz agreement is
evidence rather than a curve fitted after the fact.

### 🔑 What this closes

- Sapphire's loaded point: **2.4796 GHz** — the last number H3 was missing.
- The eigen convergence envelope is now a **limitation of one solver, not of the
  programme**: every question it blocked has been answered by driven.
- H1's design point survives the full stack — **torch AND plasma AND the highest
  ε on the table**, all measured rather than summed.

---

## 2026-08-23 — 🔑 THE TUNER PICKS THE DEEPEST IN-BAND DIP. That changes the coupling problem entirely.

**User observation:** on a real machine the LDMOS tuner chases the resonance by
minimising reflected power — and the same is true through ignition.

🔑 **So the hardware control law is exactly what `analyse_driven` does in
software, and what I spent today treating as a bug.** The tuner does not know or
care which mode it locks to; it finds the best-matched resonance in its band.
Every "wrong mode selection" I fixed in analysis is a real physical behaviour of
the machine.

### In every loop measured, the tuner would NOT lock to TE011

In-band (2.40–2.50 GHz) minima, loaded at ne=1e20:

| loop | deepest in-band | TE011 | tuner locks to |
|---|---:|---:|---|
| 11×8 | 2.4472 @ **−1.28 dB** | 2.4824 @ −0.35 | **not TE011** |
| 16×12 | 2.4494 @ **−1.98 dB** | 2.4832 @ −0.32 | **not TE011** |
| 22×16 | 2.4508 @ **−3.37 dB** | *not resolvable* | **not TE011** |
| 28×20 | 2.4428 @ **−13.45 dB** | 2.4812 @ −0.69 | **not TE011** |

### ✅ And that turns out to be GOOD, not bad — measured, not assumed

The obvious fear is that the tuner locks to a loss channel. It does not. η for
every minimum, from the saved sweeps (§10, no re-solving):

| loop | mode | β | Q₀ | **η** |
|---|---:|---:|---:|---:|
| 11×8 | 2.4472 | 0.0735 | 235 | **0.9947** |
| 11×8 | TE011 2.4824 | 0.0201 | 139 | 0.9969 |
| 28×20 | **2.4428** | **0.6495** | 196 | **0.9956** |
| 28×20 | TE011 2.4812 | 0.0396 | 106 | 0.9976 |

**The 2.44 GHz feature heats the plasma as well as TE011 does.** It is not a
parasitic loss; it is a second, better-matched route into the same plasma.

🔑 **NET POWER DELIVERED, at the 28×20 loop:**

| mode | β | absorbed | η | **net into plasma** |
|---|---:|---:|---:|---:|
| **2.4428** | 0.6495 | 95.5% | 0.9956 | **95.1%** |
| TE011 2.4812 | 0.0396 | 14.7% | 0.9976 | **14.6%** |

**6.5× more power into the plasma, and the tuner selects it automatically.**

⚠️ **The branch is ambiguous here and it does not matter:** −13.45 dB is β=0.649
undercoupled or 1.54 overcoupled. Both are near critical, so "well matched" holds
either way. The exact value needs the phase (`loopbranch.py`).

### 🔴 THE OPEN QUESTION, and it is the important one: WHAT IS THAT MODE?

η says power goes into the plasma VOLUME. It says nothing about field
**symmetry** — and the entire TE-only architecture rests on TE011's E being
**azimuthal**, because that is what has no axial path for a high-TDS sample to
short (the measured reason TM modes were ruled out for OPERATION).

**If the 2.44 GHz mode has E_z on axis, the tuner will confidently lock the
machine onto a mode a real sample will extinguish.** A driven sweep cannot tell:
it returns |S11|, not symmetry. This needs an eigen solve on the same mesh with
azimuthal binning, matched by energy signature — the pairing INSTRUMENT already
prescribes.

⚠️ **Correcting my own alarm from an hour ago:** the 2.6232 GHz mode — the one up
to 19× deeper than TE011 that broke my analysis — sits **OUTSIDE 2.40–2.50** and
the tuner cannot reach it. It is an ANALYSIS hazard, not a machine hazard. Those
are different lists and I had them merged.

### 🔑 Ignition is the same control problem, and the frequency map IS the trajectory

Before ignition the cavity is cold and empty; after it the plasma pulls TE011
**+31.6 MHz**. The tuner must acquire the cold resonance and then track a moving
target as ne rises. `h3_driven` already measured that trajectory:

| ne | 0 (cold) | 1e18 | 3e18 | 1e19 | 3e19 | 1e20 |
|---|---|---|---|---|---|---|
| f₀ GHz | 2.4505 | 2.4524 | 2.4534 | 2.4580 | 2.4730 | 2.4824 |

**Total excursion 32 MHz, monotonic, entirely inside the LDMOS band.** The
largest single step in the measured row is 15 MHz. That is a tuner
specification, and it was sitting in the data as a by-product of H6.

---

## 2026-08-23 — 🔴 CRITICAL COUPLING TO TE011 VIA A CAP LOOP IS GEOMETRICALLY UNREACHABLE

`h3_loopsize`, loaded at ne=1e20, five cap loops from 176 to 1,632 mm².
**Committed prediction: β ∝ area², critical near 1,200 mm².**

| loop | area mm² | f₀ | \|S11\| | **β** | predicted | Q₀ | Q_ext | reflected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 11×8 | 176 | 2.4824 | −0.35 | **0.0201** | 0.020 ✅ | 139 | 6,930 | 92.3% |
| 16×12 | 384 | 2.4832 | −0.32 | **0.0181** | 0.096 | 154 | 8,499 | 93.0% |
| 22×16 | 704 | — | — | *TE011 lost* | 0.322 | — | — | — |
| 28×20 | 1120 | 2.4812 | −0.69 | **0.0396** | 0.814 | 106 | 2,670 | 85.3% |
| 34×24 | 1632 | 2.4762 | −1.17 | **0.0674** | 1.728 | 54 | 797 | 76.3% |

✅ **V1**: the 176 mm² anchor reproduces the measured β = 0.0201 to **0.1%**.
🔴 **F1 FIRES at 0.05×.** **β ∝ area^0.54, not area².**
✅ **F2** every loop keeps f₀ in 2.40–2.50. ✅ **F3** η never falls — loop
conductor loss stays negligible against the plasma, so it is not the limit.

### 🔑 The extrapolation is the finding

At the measured exponent, β = 1 needs **232,000 mm²** — **142× the largest loop
tried, and 10× the entire end cap** (πa² = 24,300 mm²). **There is no cap loop
that critically couples to TE011 in this cavity.** That is a geometric
impossibility, not a tuning difficulty, and it is measured rather than argued.

⚠️ Why the small-loop model failed, and it was foreseeable: **H_r ∝ J₁(χ′₀₁r/a)
is zero on axis AND zero at the wall, peaking at 0.4805a.** The 11×8 loop already
straddles that peak (r = 34–50 mm). Widening adds area where H_r is *smaller*, so
captured flux saturates — area² assumes a uniform field over the loop and there
is not one. The same "uniform field across the aperture" assumption is what
retired the groove-depth scaling models (OPTIMIZER §2).

⚠️ **22×16 lost TE011 entirely** — only two minima remained and the continuation
guard refused a −32.4 MHz jump. Between 384 and 1,120 mm² the loop stops being a
perturbation and restructures the mode landscape; TE011 reappears at 28×20. **A
non-monotonic mode landscape is itself a reason not to size a coupler by
sweeping area.**

### 🔑 But coupling IS achievable — just not to TE011 directly

The 2.44 GHz mode reaches **β = 0.65 at 1,120 mm²** and carries **η = 0.9956**,
delivering **95.1% of source power into the plasma** against TE011's 14.6%. So
the cavity can be well matched; the question is which mode does the work, and
that is what the tuner decides — and what the groove may decide for it.

**Consequently the coupling problem is now one of three things, and NOT loop
area:** (a) accept the 2.44 mode if the groove shows it is TE-like; (b) a
different coupling structure (iris, probe, multi-loop); or (c) an external
matching network, which is standard practice and what the LDMOS tuner is for.

---

## 2026-08-23 — 🔴🔴 the groove omission: THE ENTIRE LOADED PROGRAMME MEASURED A CAVITY WITH NO MODE FILTER

**User-caught, and it invalidates the scope of almost everything measured today.**

The cavity design is **premised on a mode filter**. `GEO` — the shared geometry
baseline that **31 rigs** inherit — never passed `--groove`. So every loaded solve
this session meshed `groove = [0.0, 0.0]`:

| rig | what it produced | status |
|---|---|---|
| `h3_eigen`, `h3_annular` | η vs R, hollowing, power density | 🔴 bare cavity |
| `h3_driven` | H6's η across ne = 1e18–1e20 | 🔴 bare cavity |
| `h3_superpose` | the 78% suppression law, ε 2–6 | 🔴 bare cavity |
| `h3_sapphire` | sapphire's loaded point | 🔴 bare cavity |
| `h3_loopsize` | β vs loop area, the 2.44 GHz mode | 🔴 bare cavity |

**These are DESIGN numbers for a cavity nobody is building.** The filter is what
decides which modes exist — and today's headline results are *about the mode
landscape*: which mode the tuner selects, what couples, what the plasma loads.
Those are precisely the quantities a mode filter changes.

⚠️ **`--mode-filter 0` is NOT the omission**, and reading it as one is its own
trap. That flag is the **quartz annulus, a superseded device**; the groove
replaced it. Two parts share the phrase "mode filter" in this tree:

    --mode-filter <t>    quartz annulus   RETIRED
    --groove <w,depth>   annular slot     CURRENT — the design, frozen at 5x10

A reader checking "is the mode filter on?" finds `--mode-filter 0`, concludes it
was deliberately disabled, and moves on. **The current device has a different
flag and it was simply absent.**

### Why nothing caught it

- Nothing crashed. A groove-free cavity solves perfectly well.
- Every number was self-consistent, and cross-checks between rigs **agreed** —
  because they shared the same wrong baseline. **Agreement between two rigs that
  inherit the same defect is not validation** (§7d, one more instance).
- The sidecars recorded `groove: [0.0, 0.0]` faithfully. Nobody read it.
- H2's groove was "frozen at 5×10 mm and its variables have left the design
  space" — and *leaving the design space was silently implemented as leaving the
  geometry.*

🔑 **That last one is the real lesson: FREEZING A PARAMETER IS NOT REMOVING THE
PART.** H2 was retired with its groove settled, and "settled" became "absent"
because the settled value never went into the baseline. **A frozen design
parameter must be written into the shared geometry at its frozen value, in the
same commit that freezes it.**

### ✅ The structural fix (the groove omission)

1. **`GEO` now writes `--groove 0,0` explicitly** — the bare cavity is a
   DECLARATION, not an omission, and it is for the instrument rigs that compare
   against closed form where a plain cylinder is the point.
2. **`GEO_DESIGN` is the cavity being built** (`--groove 5,10`). Any rig whose
   output is a design number uses it.
3. **`run()` REFUSES a plasma solve on a groove-free mesh** unless the caller
   passes `allow_no_groove=True` and justifies it in the docstring. A plasma is
   the tell: bare is legitimate for instrument validation and never for a
   loaded, design-facing measurement.

### What survives, stated precisely

🔑 **The METHOD findings stand** — they are about the instrument, not the cavity:
driven cost ∝ Q; eigen's ε-contrast envelope; continuation vs global-minimum
selection; the seed rule; branch ambiguity; η robust where Q₀ is not; "a guard on
the quality of a fit cannot tell you the fit is of the wrong thing".

🔴 **Every DESIGN number is scope-invalid pending re-measurement with the groove**,
including: η(ne), the +31.6 MHz pull, loaded Q₀, the 78% suppression law,
sapphire's −2.80 MHz, β vs loop area, and the 2.44 GHz mode's existence and
depth. **Do not quote any of them.** They are not necessarily *wrong* — they are
measurements of the wrong cavity, and which of them survive is an empirical
question, not something to be argued.

---

## 2026-08-23 — 🔑 THE OPERATING POINT IS A CLOSED LOOP, AND THERE IS A COUPLING VALLEY

**User question: "why would the frequency stay static? We have to model the tuner
that adjusts the LDMOS frequency in response to reflected power."**

Correct, and it exposes something bigger than the tuner. Every number in this
programme has been produced by **imposing ne and measuring the EM response**. The
machine is a **closed loop**:

    delivered power  ->  ne  ->  f0 and beta  ->  delivered power

with the tuner a second loop tracking the dip. **An imposed ne is an assumed
answer**, and single-point figures like "6.6% net at 2.4824 GHz" describe one
slice of a trajectory, not an operating point.

### With the tuner tracking perfectly, delivered power is NON-MONOTONIC

Source at each density's own resonance (bare cavity — the groove omission applies):

| ne | f₀ GHz | pull | β | \|S11\| | absorbed | η | **net** |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1e18 | 2.4524 | +1.9 MHz | 0.0981 | 0.8213 | 32.5% | 0.9913 | **32.3%** |
| 3e18 | 2.4534 | +2.9 | 0.0390 | 0.9249 | 14.4% | 0.9959 | **14.4%** |
| 1e19 | 2.4580 | +7.5 | 0.0179 | 0.9649 | 6.9% | 0.9982 | **6.9%** |
| **3e19** | 2.4730 | +22.5 | **0.0149** | 0.9707 | 5.8% | 0.9980 | **5.8%** |
| 1e20 | 2.4824 | +31.9 | 0.0201 | 0.9606 | 7.7% | 0.9969 | **7.7%** |

🔴 **A COUPLING VALLEY AT ne ≈ 3e19.** Delivered power falls **5.6×** from
ne=1e18 to 3e19, then recovers. **The worst coupling is in the MIDDLE of the
ignition trajectory**, not at either end.

🔑 **This is a candidate ignition barrier, and the tuner cannot fix it** — the
tuner is already sitting at the dip; the valley is in β, not in frequency error.
If the plasma's power requirement at ~3e19 exceeds what the cavity delivers
there, the discharge cannot climb from ignition to the operating point. It would
stall or extinguish partway, and every endpoint measurement would still look
healthy.

⚠️ **η is NOT the problem** — it stays 0.991–0.998 across the whole row. The loss
is entirely in **coupling**: 68–94% of source power reflects. η has been the
reassuring number all session and it measures the wrong stage.

### What this changes about how the question must be asked

**P_delivered(ne) is measured. P_required(ne) is not**, and it is not an EM
quantity — it is a plasma power balance (radiation, conduction, convection over
the 92.3 mm column). The operating point is their intersection, and **whether a
PATH exists from ignition to that intersection is a separate question from
whether the endpoint is stable.** Both need asking; only the second has been.

⚠️ **Caveats, held firmly:**
- **Bare cavity (the groove omission).** These need the groove re-do, and the β
  non-monotonicity in particular may be an artifact of competing modes the
  filter removes — the groove changes which modes exist.
- **Perfect instantaneous tracking assumed.** A real tuner has finite bandwidth
  and slew rate; this is the optimistic bound, and the valley is where tracking
  is hardest because it is where the pull accelerates (+2.9 → +7.5 → +22.5 MHz).
- Five points, one decade apart. The valley's depth and width are not resolved.
