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
