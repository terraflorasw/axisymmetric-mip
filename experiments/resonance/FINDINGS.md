# FINDINGS — resonance

Append-only, newest at the bottom, dated UTC. Every entry carries a
**verification** and a **falsification**. See `README.md` for the rules.

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
