# Next

**This file is the QUEUE. It holds no measurements.**
Read **`KNOWN.md`** first — that is what has been established, and it indexes
every document. Then `PLAN.md` (the FIXED experiment list, E0–E4), then
`CONVENTIONS.md`.

🔴 **PRUNED 2026-08-24.** This file had grown to 819 lines of layered narrative —
the same way `FINDINGS.md` did before it was removed for being unreadable. Every
conclusion in it is in `KNOWN.md`; the narrative is in git:

    git -C axisymmetric-mip log -p --follow experiments/resonance/NEXT.md

⚠️ **Do not re-grow it.** A result goes in `KNOWN.md`; a lesson goes in
`CONVENTIONS.md`; only the *queue* goes here.

## 🔑 STATE — 2026-09-04. Read this block and nothing else, unless chasing a citation.

⚠️ **THIS FILE IS 3x THE SIZE THAT GOT IT PRUNED.** Its own header says *"pruned
2026-08-24 ... 819 lines ... do not re-grow it"*. It is now ~2,490. **It needs
the CONVENTIONS treatment — canon at the top, narrative to evidence — and has not
had it.** Everything below this block is history, some of it stamped superseded.

### 🔑 THE QUEUE AS OF 2026-09-07 — the EM feasibility question is ANSWERED

Both things this file and `CLAUDE.md` carried as blockers are gone, and neither
was ever a lever:

- **Gas temperature.** ✅ Resolved 2026-08-24; `CLAUDE.md` carried it as a live
  blocker for **13 days** until 2026-09-07 while `KNOWN.md` said it was anchored.
  🔴 **And it is not a design variable at all** — user, 2026-09-07: *"Nitrogen has
  an innate limit and nothing about any cavity or waveguide changes that."*
- **Ignition.** ✅ Settled 2026-08-26 — cavity-only ignition is 13× short in
  field, so item 7's target is `coupling.beta` = 1 loaded. 🔑 **A striker is not a
  deficiency**: user, 2026-09-07 — *"Cavity-only ignition isn't present in MP-AES
  or MICAP either."*

So nothing upstream gates the cavity. **The next work is buildable parts**, and
the EM half of that is:

1. 🔑 **TOLERANCE SENSITIVITY** — `df₀/da`, `df₀/dL`, `df₀/d(groove)`. The
   programme knows mesher jitter (8 kHz) and differential resolution (~20 kHz)
   but has never asked what a **machining error** costs. This sets the machining
   spec, and it is answerable with the instrument as it stands.
2. 🔑 **TUNER RANGE**, which falls out of (1) — user, 2026-08-27: *"how much
   change in cavity impedance can be absorbed by the frequency and magnitude
   tuner"*, still uncharacterised beyond a napkin. Tolerance sets the range the
   tuner must cover, so (1) and (2) are one question asked twice.
3. **Real materials and features** — user: *"vacuum is also wrong for a real
   cavity"*. Wall finish, joints, the groove as a machined feature.
4. **Coupler thermals** — now that there is a measured number to design against
   (`KNOWN.md` § COUPLER DISSIPATION). Needs a tool Palace does not have.

⚠️ **AND A QUESTION NOT IN THE RECORD, worth answering before committing to a
build:** what does this architecture BUY over an iris or an inductive coupler?
82.6 % into electrons at VSWR 1.63 is a good number — good against *what*? If
there is a claim here (efficiency, tuning range, cost, robustness to sample
loading), a tolerance study should be scoped to protect it.

### 🔑 RECOVERED 2026-09-07 — the ignition and flow session that was killed mid-reply

An API safeguard false positive (`[bio]`) killed the session at 02:44 with
nothing written. **It is now landed, and nothing needs re-deriving to read it:**

- `../ignition-options/STARTER-FLUID.md` — option 4 evaluated. Potassium acetate
  through the existing nebuliser deposits its own susceptor (amorphous carbon,
  volumetric absorber at 2.45 GHz) and its own seed. Drops the ignition bar
  ~2,100 K. 🔴 Cold-start bootstrap unevidenced in OUR torch; the settling
  experiment is a domestic microwave, not a solve.
- `../torch-geometry/README.md` § THE FLOW SPLIT — **~12 slm in three streams at
  1 kW**, superseding the flat 20. Two derived claims WITHDRAWN there.

**The one EM item it generated, and it is cheap:** give the driven rig
**amorphous carbon's** (ε, σ) as the bore inclusion instead of a plasma's, and
read the watts landing in the deposit per bore diameter. Same rig, vacuum-class
cost. ⚠️ Answers absorption only, not temperature rise.

⚠️ **And a second EM route nobody has costed:** the grape paper measures **19×
field enhancement from a 0.5 mm dielectric gap.** Our bore is 150× short in field
at 1 kW. A deliberate dielectric feature in the torch is an ignition route that
is pure EM and therefore measurable here.

🔴 **Corrections that must not be re-imported:** VSWR 102 is superseded (it is a
point on a parametric σ sweep, not a state the machine occupies — the plain
barrel loop's band is VSWR 1.3–3.1 across σ 0.008–0.04, a window the gas passes
THROUGH). The "operating point is an outcome / ~4,530 K" balance is VOID — it
used LTE Saha where the record says n_e is kinetics-limited.

### ⏸️ PARKED — THE AZIMUTHAL RESONANT PEAK (opened 2026-09-07)

**Do not chase this.** It is a narrow, well-posed bug on an *alternative* coupler,
and the barrel already meets the requirement. It should not pull effort unless the
azimuthal buys something the barrel cannot.

At h = 10.5 the off-resonance pedestal is **gone** (−0.005 dB against the barrel's
−0.004) and the discretisation error fell 11×, so the near-wall placement caused
both. What remains: the on-resonance closure is 7.9 %, and `Q_L` = 2,302 (measured
two independent ways) cannot be reconciled with `Q₀` = 43,907 and a dip depth of
−9.405 dB at either coupling branch. 🔑 `Q₀(energy)` is a RATIO and survives a
common scale error; the closure is an ABSOLUTE and does not — so the peak is
mis-scaled, not physically wrong. ⚠️ The PROM converged on 6 samples at a greedy
error of 1.0e-05 against a 1e-3 tolerance, which argues against simple
under-sampling. **Cause NOT identified. Do not assume it is the PROM.**

### ⏸️ PARKED — SUPERVISOR / MONITOR DESIGN (opened 2026-09-05)

> User: *"There's no reason why the timeout should be tightly coupled when
> cancelling is just a simple kill."* ... *"We probably have to do better monitor
> design. But, nothing to do now."*

**Parked deliberately (§7k): recorded so it is not lost, NOT spawning work.**

🔴 **The defect:** policy (when to give up) is welded to mechanism (how to run).
`run(..., timeout=)` owns a `deadline` local, so extending a HEALTHY-but-slow
solve required a config edit -> new slug (configs are immutable) -> losing
everything computed, because a PROM build has no partial-result path.
⚠️ And wall-clock cannot distinguish **slow** from **stuck**, which is the only
distinction §7bp actually cares about. `NLEPS_BUDGET` is the right shape —
work done, not time elapsed — and driven solves never got an equivalent.

✅ **Done so far (mechanism only):** `run()` writes `<tag>.pgid` and clears it on
exit; `<tag>.extend_s` moves the deadline and is consumed on read. Cancellation
is now available to ANY supervisor.

➡️ **The real design, when it is time:** one supervisor, external to the solve,
where wall-clock expiry / no-progress / operator judgement / spot reclamation are
all the SAME event — "the process died" — and `run()` only reports it. That also
subsumes the monitor problem this session kept hitting: a chained launch left the
next run unwatched, `ops/remote.sh` prints the watch command as ADVICE, and
nothing refuses a launch with no watch armed.

🔑 Belongs on the CONVENTIONS §7.0 build queue as an UNENFORCED operational rule,
alongside "no constants in scripts".

### 🔑 WHY THE LOADED SOLVE OOMs — DIAGNOSED 2026-09-05, from the memory PROFILE

> User: *"At the start it was like 50GB when I saw it, then fell to around 32GB,
> and it's been ratcheting up since"*

**That profile is the diagnosis, and it overturned my first two guesses.**
Monotonic ratcheting during a solve means ACCUMULATION. A GMRES Krylov basis
grows within one linear solve and resets at the next — it cannot ratchet across a
whole run. The emitted config says what does:

    "AdaptiveTol": 0.001,  "AdaptiveMaxSamples": 40
    palace log: "Computing adaptive fast frequency response for:"

🔑 **Palace builds an adaptive PROM**: it adds sample frequencies, each
contributing a FULL-SIZE basis vector that is never freed, until the error
estimate clears AdaptiveTol or it hits 40 samples. The 50 GB spike then fall to
32 GB is mesh partition + assembly completing; everything after is the PROM.

✅ **AND IT EXPLAINS WHAT MESH SIZE COULD NOT:** on ONE 631,835-tet mesh the COLD
case solved and the LOADED case OOM-killed. Cold is well conditioned and reaches
tolerance in few samples. Loaded at eps = -1.456 is INDEFINITE (R4), needs far
more samples for the same tolerance, and therefore accumulates far more basis.
**Same mesh, different sample count, different memory.**

🔴 **I CALLED THIS WRONG TWICE. THE SOLVER LOG SETTLES IT: BOTH RATCHET, AND
GMRES IS THE BIG ONE.**

    grep "restart [0-9]+" <solver log>  ->  "restart 0"  AND NOTHING ELSE

**GMRES never recycles.** MaxIts=500 with no Restart, so the Krylov basis grows
monotonically for the WHOLE solve. Measured residual history on the sf 0.8
loaded case: iteration 14 -> 6.3e+01, 64 -> 1.2e+01, 164 -> 3.2e-01, and an
earlier sample reached 275 iterations at 3.9e-06. **So each PROM sample costs
~275-400 full-size basis vectors** — against only 40 PROM samples, the WITHIN-
SOLVE basis dominates by an order of magnitude.

➡️ **So `h3-betaconv3-0p8` (Restart=30) IS the right test after all**, and my
"wrong knob" note above was itself wrong. Bounding 400 vectors to 30 is a >10x
cut on the dominant term.
⚠️ **BUT restarted GMRES converges WORSE** — it discards the Krylov space it was
using to make progress. On a system this ill-conditioned (residual needs 8
decades and takes ~300 iterations UNrestarted) a restart of 30 may stagnate
entirely. **Memory and convergence trade directly here.** `AdaptiveMaxSamples`
remains the other knob and still costs accuracy.

🔑 **THE HONEST SEQUENCE OF MY OWN CLAIMS, since it is the lesson:** (1) "mesh is
too big" — refuted, the same mesh solved COLD; (2) "Krylov basis" — plausible,
unverified; (3) "no, it is the PROM" — asserted from the memory profile alone,
without reading the solver log; (4) the log shows BOTH, with GMRES dominant.
**Three of four were stated before looking at the one file that answers it.**

🔑 **PREDICTION, stated now:** memory is BOUNDED, not unbounded — the ratchet
stops at 40 samples. If 123 GB holds to that cap the run completes; the ceiling
is a sample count, not a leak.

### 🔑 MESH CONVERGENCE OF coupling.beta.loaded — 3 POINTS, 2026-09-04

Design cavity, barrel + gap2 2.25, ne = 7.9e18, driven. `h3-betaconv*`.

| sf | tets | Q_L | coupling.beta.loaded | Q0 | cavity.Q_ext.loaded |
|---:|---:|---:|---:|---:|---:|
| 1.5 | 124,203 | 60.59 | 0.2476 | 75.59 | 305 |
| 1.2 | 215,649 | 58.18 | 0.2882 (+16.4 %) | 74.95 (−0.9 %) | 260 (−14.8 %) |
| **1.0** | ~370,000 | 57.64 | **0.3007** (+4.3 %) | **74.97** (+0.0 %) | **249** (−4.1 %) |
| 0.8 | 631,835 | — | 🔴 **OOM** | — | — |

✅ **Q0 IS STABLE ACROSS ALL THREE: 75.59 / 74.95 / 74.97, inside ±0.9 %.** That
confirms OPTIMIZER §1's compensation claim by measurement: Q_L and beta move in
opposite directions and `Q0 = Q_L(1+beta)` barely notices.

🔴 **THE sf = 1.5 NUMBERS ARE WRONG BY ~20 %.** Every 2026-09-03/04 result used
1.5. beta 0.2476 -> 0.3007 is **+21 %**; `cavity.Q_ext.loaded` 305 -> 249 is
**−18 %**. Best available: **beta ≈ 0.30, Q_ext ≈ 249**, matching needs **≈3.3x**,
not the 4.04x reported from the coarse mesh.

⚠️ **CONVERGENCE IS NOT ESTABLISHED, AND I OVERCLAIMED IT ONCE TODAY.** beta's
steps shrank 16.4 % -> 4.3 %, and I called that converging. Then the COLD series
at the same four resolutions went **−23.1 %, −8.8 %, −18.2 %** — shrinking, then
jumping. **Two shrinking steps do not establish a trend**, which is §"this
programme keeps extrapolating before the curve has shown its shape", committed
again. I predicted cold Q_L ≈ 168 at sf 0.8; it is 144.

🔴 **THE 4th POINT IS BLOCKED BY MEMORY, NOT TIME.** sf 0.8 = 631,835 tets;
rc=137 at 637 s with the cap at 12,000 s. dmesg shows 21 OOM kills: 32 ranks x
~2.3 GB against 61 GB. ➡️ Settling convergence needs a **bigger-memory instance**,
not a longer run. Until then beta is *measured at three resolutions and still
moving 4 % at the finest one*.

⚠️ **ALSO UNEXPLAINED: cold f0 drifts −350 kHz monotonically** across the four
meshes (2.442800 -> 2.442450), **4.2x the E0 instrument floor**. f0 comes from
the dip LOCATION, not its width, so the shallow-dip excuse does not obviously
cover it. Not diagnosed. ret:beta-not-mesh-converged

### ✅ ESTABLISHED, survives everything this week

| | |
|---|---|
| **E0 instrument floor** | spurious splitting **1.86 kHz**, TE011 **+34 ppm** vs closed form. A difference must clear ~0.1 MHz to be the model rather than the solver. |
| **Design cavity, driven, barrel + gap2 2.25** | cold `cavity.Q_ext.cold` = **253**; loaded **305** at ne 7.3-8.6e18; **coupling beta.loaded = 0.2476** at 7.9e18 |
| **Torch shift** | design vs vacuum cold f0 = **-11.43 MHz**, against `e3-torch-01`'s independent -10.40. 136x the instrument floor. |
| **What is robust in all of it** | `Q_L` (linewidth) and `beta` (dip depth). Everything derived through `Q_EXT_MEASURED` is not — see `Q_LEDGER.md`. |

### 🔴 RETRACTED OR UNSUPPORTED

- **"Q_ext is geometric/state-independent"** — one coupler compared with itself.
  The only cross-coupler test disputes it, and is itself untrustworthy.
- **The coupling series (8,716 / 720 / 322) as DESIGN numbers** — all vacuum
  torch, pre-restoration.
- **7.9e18 as "the operating point"** — it is the MICAP-anchored density. The
  fork (~3e16 vs high density) is UNDECIDED and is a plasma question.
- **Every `Q0` column produced via `Q_EXT_MEASURED`** — a cap-loop constant.

### 🔴 THE ORDERING CHANGED. One measurement now gates the rest.

**Was:** field probe in the series gap -> constrained gap sweep -> beta = 1.
**Now:** that whole line only matters if the coupler still matters when loaded.

    0. MESH CONVERGENCE ON beta — sf 1.5 / 1.2 / 1.0 / 0.8, one loaded case.
    1. AZIMUTHAL, LOADED, DESIGN CAVITY, with a fit that returns a real Q_L.

🔴 **STEP 0 IS NEW, AND IT GATES STEP 1.** `KNOWN.md § NOT ESTABLISHED` and
`OPTIMIZER.md §1` both say **coupling.beta is NOT MESH-CONVERGED — it moved 43.1 %
for a 1.25x refinement while Q0 moved 0.12 %.** The series they demand has never
been run, and **every 2026-09-03/04 result is at sf = 1.5, its coarsest point.**
So `beta = 0.2476` and `Q_ext = 305` are quoted against the programme's own
do-not-quote list. ⚠️ **If beta is unconverged, the azimuthal-vs-barrel puzzle
(56x apart cold, 6 % apart loaded) may be a MESH artefact, and step 1 cannot
interpret its own answer.** `Q_L` and `Q0` are unaffected — they are the stable
pair. ret:beta-not-mesh-converged

- comes back **~14,000** -> loaded Q_ext IS loop-set. The coupler choice is a
  real 56x decision, the series gap (**barrel-only** — `geometry.py` cannot build
  one on the azimuthal mount) becomes decisive, and the gap-sweep line resumes.
- comes back **~300** -> loaded Q_ext is PLASMA-set, **the loop barely matters
  loaded**, and every "we need Nx more coupling" claim here is wrong at the root,
  including the 4.04x.

**Then, and only in the loop-set branch:** 2. field-probe the series gap (arcing
is the declared precondition). 3. gap sweep ON THE DESIGN CAVITY — it has never
been run there. **Not** another point at gap2 = 2.25.

### ⏸️ BLOCKED ON DECISIONS, not on solver time

- **Operating density** — the fork. A plasma question, not a cavity one.
- **Coupler family** — barrel + series gap (27x lever, vacuum-only evidence) vs
  azimuthal (novel, buildable, *no series gap possible*, 152x from a loaded
  match). `DISCLOSURE.md` claims the azimuthal one.

---

## 🔴🔴 "Q_ext IS GEOMETRIC" IS UNSUPPORTED WHEN LOADED — and the series gap is BARREL-ONLY

> User: *"The series gap is only measured for the barrel coupler. I don't think
> we did it for azimuthal"* ... *"Which invalidates the cold vs loaded Q_ext
> explanation"*

**Both correct, and the second follows from the first.**

### 1. The series gap CANNOT be built on the azimuthal mount

Not "not swept yet" — **not implemented**. Both rigs refuse:

    h3_driven.py:384   loop_gap2 requires loop_mount='barrel' (geometry.py:427)
    h3_loopq.py:325    gap2 requires mount=barrel (geometry.py:427)

So the **27x lever exists only on the barrel mount**. The azimuthal loop — the
novel, buildable direction, the one `DISCLOSURE.md` claims (*"PRIOR ART: NONE"*
for a wall-following loop) — has **no series gap available**, and sits at
Q_ext = 14,152 cold, **152x from a loaded match**.

### 2. Which invalidates my cold-vs-loaded explanation

I argued Q_ext is geometry-dominated: 27x with loop geometry, only 21% cold ->
loaded. **But that is one coupler compared with itself.** The only cross-coupler
loaded test available says the opposite:

| coupler | Q_ext COLD | beta LOADED | -> Q_ext LOADED |
|---|---:|---:|---:|
| barrel + series gap 2.25 | 253 | 0.2476 | 307 |
| azimuthal | 14,152 | 0.2334 | 326 |

**56x apart cold. Within 6% loaded.** If sound, loaded Q_ext is set by the
PLASMA, not the loop — which breaks `THE ORDER`'s arithmetic
(`beta(ne) = Q0(ne)/Q_ext`, Q_ext geometric), not merely my wording.

⚠️ **I do NOT think the azimuthal row IS sound — and that is not better news.**
Its loaded point has **`Q_L = None`** (the fit never got a linewidth), and the
file is already flagged: cold Q0 = 70,353, **above the bare cavity**, impossible.
If azimuthal Q_ext really held at 14,152 loaded, beta would be 76/14,152 =
**0.0054** -> a **-0.09 dB** dip, unfittable. The fit reports **-4.13 dB**, which
is what beta ~ 0.23 looks like — so it most likely locked onto a DIFFERENT
feature, plausibly one of the 2.338 / 2.604 minima the loaded sweeps show.

➡️ **EITHER WAY: there is NO trustworthy cross-coupler loaded measurement, so
"Q_ext is geometric" is unsupported when loaded — in both directions.** I stated
it as established on the strength of a single coupler compared with itself.

### ➡️ THE TEST THAT SETTLES IT

**Azimuthal, loaded, on the design cavity, with a fit that returns a real Q_L.**
One driven run. If azimuthal loaded Q_ext comes back near 14,000, Q_ext is
geometric and the barrel/azimuthal choice is a genuine 56x design decision. If it
comes back near 300, loaded Q_ext is plasma-set, **the loop barely matters
loaded**, and every "we need Nx more coupling" statement in this programme is
wrong at the root.

## 🔑 THE 4.04x IS NOT A DEFICIT — IT IS THE REMAINING TRAVEL ON THE KNOB

> User: *"Oh, the series gap. I didn't think we were considering that yet, since
> it's what we'll need to use to get coupling.beta.loaded to 1 (iirc)"*

**Correct, and it reframes the headline.** `gap2` is **not in `baselines.json`** —
unlike every other loop parameter — because it is a SWEPT variable whose sweep is
*"not bracketed — 27.0x at 2.25 mm, still falling"*. I treated 2.25 mm as part of
"the design cavity" when it is the **widest probe of an unfinished sweep**.

➡️ **So "coupling.beta.loaded = 0.2476, needs 4.04x" does NOT mean a 4x shortfall
to be found somewhere else.** It means **the knob that has already delivered 27x
has ~4x of travel left to do**, and the question is whether it can be turned that
far — not whether some other mechanism must supply it.

🔴 **AND THE STOPPERS ARE ALREADY NAMED, NONE OF THEM MEASURED AT THE REQUIRED
GAP:** mode purity `spread` accelerating toward the F2 threshold (0.0010 ->
0.0046 over 0.75 -> 2.25 mm), Q0 falling 26% over the same span, and the
**series-gap E-field, still UNMEASURED**, which sets the arcing limit. KNOWN.md
already concluded the next run must be *"CONSTRAINED, not another minimisation"*
and made the field probe a **PRECONDITION**.

⚠️ **DO NOT EXTRAPOLATE THE GAP SWEEP TO FIND THE 4x.** Its local slope changed
direction twice (-1.14, -0.75, -0.57, -0.89) and the record says so explicitly.
The honest statement is *"4x of travel remains on a knob whose limit is unknown
and whose three limiting constraints converge in the same region"*.

🔑 **AND ALL OF IT IS AT gap2 = 2.25 ON A VACUUM-TORCH SWEEP.** The 720/580/461/322
series is pre-restoration; only the two `h3-gap2load-*` points exist on the
design cavity, both at one gap. **The gap sweep has never been run on the cavity
we are building.**

## 🔴 "THE WHOLE MICAP BAND" IS NOT A BAND (2026-09-04)

> User: *"What is 'the whole MICAP band'?"*

**A phrase I used as a unit of evidence, which it is not.** It is:

- **TWO literature temperatures**, 5220 K and 5270 K — Kuonen/Hattendorf/Gunther,
  *JAAS* 39(5) 2024, Table 2, pressure-reduction method, measured on a **Radom
  N2 MICAP**. A different instrument, not this cavity.
- **Two SAMPLE-INTRODUCTION CONDITIONS**, not the endpoints of a range anything
  sweeps or operates over.
- Mapped through `plasma_state` (Saha, **LTE assumed**) to n_e = 7.3-8.6e18.
- **7.9e18 is the MIDPOINT INTERPOLATION at 5245 K — a temperature nobody
  measured.**

⚠️ `physics.py`'s own caveats, which the phrase hides: the temperature is the
plasma **as sampled through the MS interface at the sampling cone**, and the file
says outright *"Not the same region"* as the r = 2-8.5 mm annulus we model; LTE
makes n_e a **LOWER BOUND**; `nu_m` inherits an ORDER-ONLY cross-section.

🔴 **AND IT MADE A WEAK TEST SOUND LIKE A STRONG ONE.**

    7.3e18 -> 8.6e18  =  a factor of 1.178   (+/- 8 % about 7.9e18)
    cavity.Q_ext.loaded across it: 305.4 / 305.3 / 305.5  ->  spread 0.07 %

**Constancy over +/-8 % in density is nearly a tautology for a
geometry-dominated quantity**, not evidence of invariance. For contrast the
density sweep in this file spans 1e16 -> 7.9e18, **790x, nearly three decades**,
and Q_ext moves ~15 % over it.

✅ **SAY INSTEAD:** *`cavity.Q_ext.loaded` = 305 at n_e = 7.9e18 on the design
cavity; it does not move measurably over +/-8 % in density.*

🔑 **SAME FAILURE AS CALLING 7.9e18 "THE OPERATING POINT", TWICE IN ONE SESSION,
ON THE SAME NUMBER:** borrowing an authoritative-sounding label out of the record
and letting it carry weight the measurement underneath does not support. ➡️ When
a phrase names a RANGE, state the factor it spans before quoting anything as
constant across it.

## 🔴 "THE OPERATING POINT" AND THE MISSING STATE SUFFIXES (2026-09-04)

> User: *"Why did 7.9e18 re-enter the equation? And why are coupling.beta, beta,
> and Q_ext stated without specifying cold or loaded?"*

**Both are mine, and the first has a consequence bigger than the naming.**

### 1. 7.9e18 is NOT the operating point, and I called it that again

`THE FORK` (above) is explicit and UNDECIDED: *"Either operate near 3e16 with the
coupler we have, or build a ~30x stronger coupler to reach 3e17... **Which fork
depends on what density the plasma must run at, which is a PLASMA question, not
a cavity one.**"* I agreed with this on 2026-09-03 and then re-adopted 7.9e18 by
inheriting `h3-gap2load-01`'s `ne_grid` **mechanically**, without re-deciding it.
It is the **MICAP-ANCHORED DENSITY** — where an N2 MICAP sits at 5220-5270 K —
not a chosen operating point.

🔴 **AND THAT UNDERMINES THE HEADLINE, NOT JUST THE LABEL.** "beta = 1 needs
4.04x more coupling" is a statement about the **HIGH-DENSITY BRANCH OF AN
UNDECIDED FORK**. On the low branch the record already says the opposite: at
n_e ~ 3e16 this loop family delivers **73.8 % of incident power at VSWR 1.3**,
because *"the peak sits where coupling.beta passes through 1"* — **no coupling
gap at all**. So "we need 4x more coupler" is conditional on a decision nobody
has made, and I have been reporting it as a property of the machine.
➡️ Every coupling number in this programme should be read as **"at the MICAP
density"**, and the fork restated before any of it becomes a design requirement.

### 2. Every beta / Q_ext / Q0 must carry its STATE, and its DENSITY when loaded

⚠️ **`coupling.beta` IS NOT A KEY IN `baselines.json`.** It exists only in
GLOSSARY's SYMBOLS table. So writing `coupling.beta = 0.2476` uses a
canonical-LOOKING dotted name for a quantity with no canonical entry — while
`cavity.Q_ext` was being given a `.cold` suffix for exactly this reason.

| I wrote | should be |
|---|---|
| `coupling.beta = 0.2476` | coupling beta **.loaded**, design cavity, **ne = 7.9e18** |
| `Q_ext = 307` | `cavity.Q_ext.loaded` at ne = 7.9e18, design cavity |
| `Q_ext = 343` | `cavity.Q_ext.loaded` at ne = 7.9e18, **vacuum** cavity |
| "beta = 1 needs 4.04x" | ratio of `cavity.Q_ext.loaded` to `cavity.Q0.loaded`, same ne, same cavity |

🔑 **A coupling number needs THREE qualifiers, not one:** state (cold/loaded),
**density** (loaded only), and **cavity** (vacuum torch / design torch). Drop any
one and two different measurements print identically — which is how 8,716 / 720 /
322 and today's 307 sat in the same sentence yesterday while belonging to
different cavities.

➡️ **REPAIR:** add `coupling.beta.cold` / `coupling.beta.loaded` to
`baselines.json` as context-keyed entries (ne, cavity, loop), the way
`cavity.Q0.cold` already is — so the name cannot be written without its context.

## 🔴🔴 THE TWO RIGS NOW MESH DIFFERENT CAVITIES (2026-09-03)

`h3-gap2modes-01` **timed out** — 2700 s, 153 NLEPS iterations, no modes in
(2.35, 2.65). The rig refused correctly: *"NOTHING IN THIS SWEEP IS QUOTABLE."*
My `eigen_target = 2.32` broke convergence; 2.38 is the validated setting and I
moved it without evidence that it would still converge. That much is my error and
is cheap.

🔴 **THE EXPENSIVE PART IS ONE LINE IN ITS LOG: `torch: eps=9.39`.**

| rig | torch it meshes | why |
|---|---|---|
| `h3_loopq` (eigen) | **sapphire 9.39** | uses `GEO_DESIGN`, which carries the restored torch |
| `h3_driven` (driven) | **vacuum 1.0** | **HARDCODES** `--torch-material 1.0,3.5e-05` (line 316) |

**THE TORCH RESTORATION LANDED 2026-08-26** (KNOWN.md § THE TORCH RESTORATION,
f0 = 2.440236). Every coupling run predates it and meshed `eps = 1.0`:

    h3-loop-gap2-01   eps=1.0        h3-loop-barrel-01  eps=1.0
    h3-loop-gap2-02   eps=1.0        h3-lambda4-02      eps=1.0

➡️ **SO THE ENTIRE COUPLING SERIES — Q_ext 8,716 -> 720 -> 322, the 27x lever,
the wavelength/4 interior minimum — IS ON A VACUUM-TORCH CAVITY, NOT THE DESIGN
CAVITY.** And `h3-gap2load-01` matches them only because `h3_driven` hardcodes
the same obsolete torch. Two wrongs producing a valid internal comparison.

🔴 **AND EIGEN CAN NO LONGER CROSS-CHECK DRIVEN.** They mesh different cavities.
Every eigen-vs-driven agreement quoted from here on crosses the restoration
boundary — an epoch comparison (§ epoch comparisons are not measurements), which
is precisely the trap I walked into when I wrote this run's caveat claiming
*"h3_loopq meshes the same vacuum torch as h3_driven."* It does not, and the
config says so in its own log.

⚠️ **This does NOT retract the coupling numbers.** They are internally consistent
and were measured on one cavity. What it retracts is their applicability to the
DESIGN cavity, and any eigen/driven cross-check made after 2026-08-26. The torch
moves f0 by ~10.4 MHz — 124x the instrument floor E0 just established — so the
difference is real, not noise.

### ➡️ THE DECISION THIS FORCES, and it is not mine to make silently

**Which cavity is canonical for coupling work?**
1. **Vacuum torch** — keeps the whole gap2/wavelength-4 series valid and
   comparable, but measures a cavity nobody is building.
2. **Design (sapphire) torch** — correct, and **re-opens the coupling series**:
   `h3_driven` must stop hardcoding the torch, and 8,716 / 720 / 322 need
   re-measuring on the restored cavity.

🔑 Option 2 is the honest one and is what "re-verify from E0" implies. Its cost
is the coupling sweep, not the whole programme — and `coupling.beta = 0.312`
would have to be re-established on the design cavity before it can be quoted as
a design number.

## ✅✅ E0 RE-VERIFIED AT ORDER 2 — the instrument holds, and now has a NUMBER

**`e0-reverify-01`, EXIT=0.** Bare PEC cylinder, the one case where the closed
form is complete. Run under TODAY's code, after the label/binding repairs.
`e0.result.json` says *"NO VERDICT HERE"* — the verdict below is the re-runnable
evaluation layer applied to it, which is the design.

### The falsifier: TE011/TM111 splitting is IDENTICALLY ZERO

chi'01 = chi11 = 3.8317 exactly, so any splitting reported is the solver's own
symmetry breaking — a **zero-true-value** probe, stronger than any convergence
plot.

| case | modes near 2.450 | **spurious splitting** |
|---|---|---:|
| **fine** (103,678 tets) | 2.450084 / 2.450085 | **1.86 kHz** — 0.76 ppm |
| coarse (87,225 tets) | 2.450257 / 2.450424 | 166.7 kHz — 68 ppm |
| cond (finite-sigma wall) | 2.450023 / 2.450025 | **1.90 kHz** — 0.77 ppm |

### Accuracy against closed form, TE011

| case | solved | error |
|---|---|---:|
| coarse | 2.450257 | +105 ppm (+0.257 MHz) |
| **fine** | 2.450084 | **+34 ppm (+0.084 MHz)** |
| cond | 2.450023 | +9.5 ppm (+0.023 MHz) |

✅ **Refining 87k -> 104k tets cuts the error 105 -> 34 ppm and the spurious
splitting 167 -> 1.9 kHz.** Convergent, in the right direction, on both a
quantity with a known value and a quantity whose true value is exactly zero.

### 🔑 WHAT THIS LICENSES — and it is a BOUND, not a blessing

**The instrument's floor is ~2 kHz on a splitting and ~0.1 MHz on an absolute
f0.** A measured difference must clear that before it can be attributed to the
model rather than to the solver. Checking the programme's live claims against it:

| claim | size | vs the ~0.1 MHz floor |
|---|---:|---|
| groove pushes TM111 away | 63 MHz | 750x — safe |
| torch shift (`e3-torch-01`) | 10.4 MHz | 124x — safe |
| loaded slew, cold -> lit | 7.0 MHz | 83x — safe |
| driven vs eigen-lumped, cold gap2 | 0.36 MHz | **4x — thin but clears** |

⚠️ **The last row is the one to watch.** The mode-identity argument for
`h3-gap2load-01` rests on a 0.36 MHz agreement, only ~4x the fine-mesh error.
It clears, but it is not the comfortable margin the others have — another reason
`h3-gap2modes-01` (purity, m_az) is the right follow-up rather than a formality.

🔴 **E0 HAS NO RESUME and takes ~44 min** (391 + 280 + 1978 s). It survived only
because this instance lived long enough. If it must be re-run under reclamation
pressure, port `resume_set` the way `h3_driven` got it (§7bw).
⚠️ **And it writes `e0.result.json` — NOT slugged.** A re-run overwrites it
(§7ap). It is grandfathered, but that is the artefact this whole verdict rests
on; fetch it before re-running E0.

## 🔴🔴 RETRACTION — `h3-gap2load-01`'s Q0 AND Q_ext COLUMNS WERE WRONG (2026-09-03)

> User: *"Somethings wrong here. The Q_ext cold should be much higher, unless
> everything else about the cold cavity has been wrong so far"*

**Caught by the user, on a smell test I never ran.** The identity `Q0 =
Q_L(1+beta)` fails on EVERY point of this run. Reverse-solving `Q0 =
1/(1/Q_L - 1/X)` returns **X = 9,231 on all four cases, exactly.**

🔴 **`h3_driven` computes Q0 from an ASSUMED Q_ext**, `Q_EXT_EST` — the **plain
11x8 CAP loop's** cold external Q — on a **barrel + 2.25 mm series-gap** cavity
whose own eigen Q_ext is **322**. It is a hardcoded constant standing in for the
quantity the run exists to measure.

🔴 **AND MY DERIVATION WAS CIRCULAR.** I reported `Q_ext = Q0/beta`, dividing a
Q0 that was *itself derived from an assumed Q_ext* by an independently fitted
beta. It cannot be anything but wrong, and it produced a number (260-268) that
sat reassuringly close to the cold 270 — **the error made the answer look like
the confirmation I was hoping for.**

### Corrected — from MEASURED quantities only (Q_L from linewidth, beta from depth)

| case | Q_L | beta | Q0 = Q_L(1+beta) | **Q_ext = Q0/beta** | I reported |
|---|---:|---:|---:|---:|---:|
| cold (overcoupled root) | 267.3 | 112.1 | 30,235 | **270** | 270 ✅ |
| ne 7.3e18 | 84.5 | 0.3278 | 112 | **342** | ~~260~~ |
| ne 7.9e18 | 81.7 | 0.3124 | 107 | **343** | ~~264~~ |
| ne 8.6e18 | 79.1 | 0.2976 | 103 | **345** | ~~268~~ |

⚠️ **F3 NO LONGER HAS A CLEAN VERDICT, and the answer depends on the reference:**
- vs cold **driven** 270 -> **+27 %** — F3 (25 %) **FIRES**
- vs cold **eigen** 322.7 -> **+6.5 %** — does not fire

🔑 **The eigen reference is the better one, and here is why it is not special
pleading.** For beta >> 1, Q_ext -> Q_L, so the cold DRIVEN Q_ext is just its
Q_L — fitted from a **-0.155 dB** dip, where a 3 dB width does not exist. Eigen's
cold Q_L is 319 against driven's 267, **-16 %**, and that single quantity is the
entire discrepancy. The loaded dips (-5.3 to -5.9 dB) support a real 3 dB width;
the cold driven one does not. ➡️ **Best estimate: Q_ext moves ~+6 % cold ->
loaded, F3 does not fire — but the margin is small and the comparison mixes
solvers, which is exactly what § epoch comparisons warns about.** It is NOT the
3.6 % result I claimed.

### ✅ WHAT SURVIVES, AND IT IS THE DELIVERABLE

**`coupling.beta` is measured DIRECTLY from the dip depth and touches none of
this.** beta = 0.3278 / **0.3124** / 0.2976 across the anchored band stands, so
**beta = 1 needs 3.20x more coupling** — unchanged. The dips are deep and
one-sided, so the branch is unambiguous. Q_L stands too: it is the linewidth.

⚠️ **`cavity.Q0.loaded` = 104.6, PROMOTED TODAY, IS BUILT THE SAME WAY** — but it
survives, and the reason matters: on the plain cap loop beta ~ 0.013, so the
correction is **1.3 %** and Q0 ~ Q_L however wrong Q_ext is. On the series-gap
loop beta ~ 0.31, the correction is **31 %**, and it breaks. ✅ The two agree
independently: 104.6 (plain) vs 107 (series gap, corrected) — loaded Q0 is set
by plasma absorption, not by the loop, which is the physics one would expect.

➡️ **REPAIR:** `h3_driven` must derive Q0 from its OWN fitted beta, or refuse.
A constant from another loop geometry standing in for the measured quantity is
CONVENTIONS §2 inside the evaluation layer.

## 🔴 SUPERSEDED — ~~`cavity.Q_ext.loaded` IS MEASURED — and Q_ext IS state-independent~~ (2026-09-03)

> 🔴 **DO NOT QUOTE THIS ENTRY. Stamped in place 2026-09-04.**
>
> **What is wrong, and where the replacement is:**
>
> 1. **The Q_ext NUMBERS below (260 / 264 / 268) are WRONG.** They were derived
>    as `Q0/beta` from a Q0 computed with a CAP-loop constant. Correct values are
>    **342 / 343 / 345**. ➡️ *§ RETRACTION — h3-gap2load-01's Q0 AND Q_ext
>    COLUMNS WERE WRONG*, above.
> 2. **The CONCLUSION — "Q_ext is state-independent" — is UNSUPPORTED.** It rests
>    on one coupler compared with itself. The only cross-coupler loaded
>    comparison (azimuthal) disagrees, and is itself untrustworthy. ➡️ *§ "Q_ext
>    IS GEOMETRIC" IS UNSUPPORTED WHEN LOADED*, at the top of this file.
> 3. **The cavity is wrong for design purposes.** VACUUM torch, pre-restoration.
>    Design-cavity values are in `Q_LEDGER.md`. ➡️ *§ THE TWO RIGS NOW MESH
>    DIFFERENT CAVITIES*.
>
> ✅ **Still valid from this entry:** `Q_L`, and `coupling.beta` (0.3278 / 0.3124
> / 0.2976) — both come from the dip and the linewidth, and touch none of the
> above. The F3 verdict and every Q_ext figure do not.

### The original entry follows, unedited, for provenance

**`h3-gap2load-01`, driven, series-gap loop (barrel, gap2 2.25, 11x8, grooved,
vacuum torch). ✅ COMPLETE, EXIT=0, all four cases**, across three instances and
two spot reclamations. Artefact `h3-gap2load-01.bb71b6b6.result.json` fetched.

| case | f0 GHz | linewidth | Q_L | Q0 | coupling.beta | **Q_ext** | dip |
|---|---:|---:|---:|---:|---:|---:|---:|
| cold, branch-resolved | 2.454225 | 9.18 MHz | 267 | 30,192 | 112 | **269** | −0.155 dB |
| ne 7.3e18 | 2.459800 | 29.11 MHz | 84 | 85 | 0.3278 | **259** | −5.91 dB |
| **ne 7.9e18 — OPERATING POINT** | **2.460400** | **30.10 MHz** | **82** | **82** | **0.3124** | **264** | **−5.61 dB** |
| ne 8.6e18 | 2.461200 | 31.11 MHz | 79 | 80 | 0.2976 | **268** | −5.33 dB |

🔑 **F3 DOES NOT FIRE. Q_ext is 260 / 264 / 268 across the anchored band
against 270 cold — a total spread of 3.7 %**, compared
instrument-to-instrument (driven vs driven). **So *"Q_ext is cold, geometric"* —
the assumption `THE ORDER` uses to break the circular dependency, and which the
`cavity.Q_ext.cold` rename exposed as never tested — is now MEASURED and
SUPPORTED.** Every cold Q_ext in the record transfers to the loaded design.
⚠️ Against the cold EIGEN 322 it reads −19.5 %, but that mixes solvers; the
matched comparison is the one that means anything (§ epoch comparisons).

✅ **P1 HELD TO THE DECIMAL.** Predicted dip ≈ −5.8 dB before the run; measured
**−5.91** and **−5.61**. The point of choosing this geometry was to move the
measurement out of the branch-ambiguous regime that made the 11x8 loaded beta
unquotable, and it did.

🔑 **THE COUPLING GAP, ON THIS GEOMETRY: coupling.beta = 0.312, needing 3.20x.**
⚠️ **The target is NOT `cavity.Q0.loaded` = 104.6** — that key is the PLAIN 11x8
loop. The series gap adds loss (cold 27,863 vs 43,523), so Q0 loaded here is
**82**, and beta = 1 needs Q_ext = 82. Lower target, so the gap is 3.20x rather
than the ~3.1x the cold extrapolation implied — **two independent routes to the
same factor**, which is corroboration, not coincidence.

✅ **THE MODE-IDENTITY ALARM IS CLOSED — but the rig was right to raise it.**
Its summary said *"NEITHER. The coupled resonance is at neither eigen candidate.
Do not name this mode from frequency alone."* Both of its built-in references are
from OTHER geometries — `h3_cold` 2.440003 (different cavity) and the ladder
grooved-NO-loop 2.450561 (no loop at all). The matching reference is **this
geometry's own eigen**, `h3-loop-gap2-02` at gap2 = 2.25:

    eigen TE011 lumped  2.453860        driven cold  2.454225   ->  +0.36 MHz

Both are PORT-LOADED, which is why lumped is the comparison and pec (2.457037)
is not. ⚠️ **AND THE INHERITED IDENTIFICATION IS WEAKER THAN I FIRST WROTE.**
`h3-loop-gap2-02`'s record says `selected_by: "continuation +6.476 MHz"`, with
`P_min = 0.9949`, `spread = 0.0046` and **`m_az: None`**. So purity was MEASURED
and is good, but the mode was **selected by continuation and corroborated by
purity** — not identified by it, and its azimuthal index was never determined.
I called it "purity-based identification"; it is not. Continuation chains back to
a cold TE011 that was itself located empirically, so the attribution is a chain,
not an anchor.

⚠️ **CORRECTION TO MY OWN RETRACTION (2026-09-04). The artefact stores BOTH
branches — I said it did not.** Every point carries `beta_undercoupled`,
`beta_overcoupled`, `Q0_if_undercoupled` and `Q0_if_overcoupled`. **Every number
I "recomputed by hand" was already in the file under another name** —
`Q0_if_overcoupled` = 342.25 / 343.41 / 344.90 IS the corrected Q_ext, identical
by algebra since `Q_L(1+1/b) = Q_L(1+b)/b`. **I re-derived what I had not
finished reading.**

🔑 **AND `Q0` IS BRANCH-FREE BY DESIGN, not naive.** The rig's own comment: *"Was
`ql * (1 + b)` with b pinned to the UNDERCOUPLED root — a choice dressed as a
formula. Q_L comes from the LINEWIDTH and Q_ext from GEOMETRY; neither needs the
dip depth, so the beta/1-beta ambiguity never enters."* A considered trade:
immunity to the branch ambiguity, at the price of needing a Q_ext that matches
the geometry.

🔴 **SO THE DEFECT IS NARROWER AND SHARPER THAN I STATED.** Not a wrong formula —
**one constant from the wrong cavity**, `Q_EXT_MEASURED` = 9,231 (11x8 CAP loop),
applied to a barrel + series-gap cavity. It propagates into FOUR fields: `Q0`,
`beta_resolved`, `branch`, `error_amplification`. On the cold case it labels a
**beta = 112** cavity as `branch: undercoupled`.

➡️ **THE REPAIR IS THEREFORE SMALL AND WELL-DEFINED:** bind `Q_EXT_MEASURED` to
the geometry being meshed, or refuse to emit the branch-free `Q0` when the run's
loop differs from the one that constant came from. The branch-explicit fields
already carry the truth and need no change.
🔑 **CREDIT WHERE DUE:** the rig DID resolve it, in its summary, and its numbers
match a hand resolution to 0.1 %. My first reading called it a wrong branch
choice; that was unfair — it chose per-case and corrected in the summary.

⚠️ **"🔴 ne=1e19 missing — the gap is NOT bridged (F2)"** in the summary is the
RIG's own long-standing falsifier about the density gap, **not** this config's
F2 (shallow dips). Two different F2s in one log; do not read one as the other.

🔴 **UNEXPLAINED, AND FLAGGED BEFORE IT BECOMES A GIFT:** every loaded sweep
finds a **far deeper** minimum ~90 MHz below TE011 — `2.3648 @ −29.72 dB`,
`2.3650 @ −28.37 dB` — stable in frequency and nearly matched to the port. The
rig correctly selects TE011 by CONTINUATION, not depth. **What that mode is has
not been established**, and a −29 dB match sitting one linewidth-and-a-half from
the operating band is either an opportunity or a competing sink. It is NOT
quotable as either until identified (§ a competing in-band mode is an ALARM).

## ⚠️ `h3-gap2load-01` COLD CONTROL — F1 FIRED, AND THE FALSIFIER WAS MISWRITTEN

**Cold case, as reported by the rig:** `f0=2.454225  lw=9.18 MHz  Q_L=267
beta=0.0089  Q0=275`, dip **−0.155 dB**, branch chosen **undercoupled**.
Against the expected Q_ext ≈ 322 that is Q_ext ≈ 30,900 — **F1 fires as I wrote
it.** Stating that plainly first: the falsifier fired.

🔑 **BUT THE CAUSE IS THE BRANCH, NOT THE GEOMETRY — and it is arithmetic:**

    |S11| = |beta-1|/(beta+1)
      beta = 0.0089  ->  -0.155 dB      beta = 86.5  ->  -0.201 dB

**A hugely OVERCOUPLED cavity and a deeply UNDERCOUPLED one give the SAME
shallow dip.** Depth alone cannot separate them, and the two branches are exact
reciprocals — Q0 and Q_ext simply swap places.

| resolved as | Q0 | Q_ext |
|---|---:|---:|
| undercoupled (rig's choice) | 269 | 30,192 |
| **overcoupled (eigen-resolved)** | **30,192** | **269** |
| `h3-loop-gap2-02` EIGEN, same geometry | 27,863 | 322 |

✅ **On the correct branch the cold control PASSES: Q0 +8.4 %, Q_ext −16.5 %.**
And the whole residual is ONE quantity — driven `Q_L` = 267 vs eigen lumped 319,
**−16.3 %**, because the fitted width of a 0.155 dB dip runs ~19 % wide. Geometry
and instrument are sound; `loop_gap2 = 2.25` and `loop_mount = barrel` are
confirmed in the mesh sidecar.

🔎 **PRIOR ART — this is a KNOWN failure mode, documented at `h3_driven.py:406`:**
*"It hardcoded the UNDERCOUPLED branch. On 2026-08-24 that was WRONG for the
COLD case and RIGHT for every loaded one — the branch FLIPS as the plasma
loads... Both branches are now returned and the CALLER must resolve it."*
The rig stores `beta_undercoupled` and `beta_overcoupled`; **resolution is the
caller's job and I did not do it.**

🔴 **SO F1 WAS A BADLY DESIGNED FALSIFIER, AND THAT IS THE REAL FINDING.** I made
every loaded number conditional on an in-run cold control that sits in the one
regime this instrument provably cannot read — 86× overcoupled is exactly where
depth stops discriminating. **A control has to live where the instrument works.**
Cold + series gap does not; the eigen pair (319 / 27,863) is the right cold
reference for this geometry and needed no new solve.

✅ **THE RUN CONTINUES — the deliverable is NOT in the ambiguous regime.** At the
anchored density coupling.beta ≈ 104.6/322 ≈ 0.32, giving **−5.8 dB**: deep,
one-sided, unambiguous. The record says the branch choice is *right* for loaded
cases, and 0.32 is far from the reciprocal trap at 1.0.
➡️ **Read the loaded points off `beta_overcoupled`/`beta_undercoupled`
explicitly, not off whichever branch the rig selected.**

## 🔴 CORRECTION TO `h3-gap2load-01`'s OWN CONFIG — read before quoting it

**RUNNING** since 2026-09-03T03:45Z on `ec2-18-220-186-118`, 32 ranks, stamp
`bb71b6b6`. Watch: `ops/watch.sh h3-gap2load-01`.

🔴 **Its caveat says "Torch is SAPPHIRE (design torch, eps=9.39)". That is
WRONG — the mesh is a VACUUM torch, eps = 1.0.** I wrote the caveat and never
set `torch_material` in `parameters`, so the rig used its own value.

⚠️ **AND IT COULD NOT HAVE DONE OTHERWISE:** `h3_driven.py:316` **hardcodes**
`"--torch-material", "1.0,3.5e-05"` in the geometry args. It is not a parameter,
not overridable from the run config, and **not bound from
`torch.sapphire.permittivity`**. The rig cannot mesh the design torch at all.

🔑 **THE RUN IS STILL VALID, AND THE COMPARISON IS ACTUALLY CLEANER:**
- `h3-loop-gap2-02` — the source of the cold **322** — also meshed `eps = 1.0`.
  Same torch, so **F1 stands as written.**
- `h3-driven-anchor-01`, the source of `cavity.Q0.loaded` = 104.6, was vacuum
  torch too. So the coupling.beta arithmetic is on ONE torch throughout.
- ✅ The config is NOT being edited. `stamp()` is sha256 of the config file and
  every artefact carries it; an edit mid-run orphans the solves and silently
  empties the resume set. **The correction belongs here, not in the config.**

🔴 **WHAT THIS COSTS, STATED PLAINLY:** every coupling number in this programme
— 8,716, 720, 322, and whatever this run returns — is measured on a
**vacuum-torch cavity, not the design cavity.** The torch moves f0 by ~10.4 MHz
(`e3-torch-01`); whether it moves Q_ext is **unmeasured**. That is a second
instance of the same defect the `cavity.Q_ext.cold` rename exposed: a quantity
assumed transferable across a state nobody varied.

⚠️ **AND PREFLIGHT CANNOT SEE IT.** `r_hardcoded_value` inspects `ast.Assign`
with an uppercase target; this literal sits inside a list of CLI arguments, so
the linter reports a clean file. Same shape as the 2026-08-25 note in `_MEASURED`
itself: *"a linter that cannot see a class of value reports a clean sweep over
it."* ➡️ Extending the rule to string literals in `args` lists is cheap and
would have caught this before the run, not during it.

## 🔴 THE RENAME EXPOSED AN UNMEASURED ASSUMPTION — opened 2026-09-03

> User: *"cavity.Q_ext is underspecified, is it not? By the cavity.Q0.cold
> convention, it should be cavity.Q_ext.cold"*

✅ Renamed. Every recorded context under that key has **ne = 0.0**, so `.cold`
was always factually right — the bare name simply had nowhere to put the state.

🔴 **AND THAT IS EXACTLY WHERE AN ASSUMPTION WAS HIDING.** `THE ORDER` (above)
breaks the circular dependency by asserting *"Q_ext | the loop | ❌ NO (cold,
geometric)"* — i.e. that the external Q does not depend on cavity state. **That
has never been measured.** With the state suffix in the name, the gap is
visible: `cavity.Q_ext.cold` exists with three values; **`cavity.Q_ext.loaded`
does not exist at all.**

### ⚠️ AND `h3-driven-anchor-01` DOES **NOT** ALREADY ANSWER IT — I checked

The anchor result file carries `beta` and `Q_ext_implied` per point, and at the
anchored band they look clean and flat: **8,150 / 8,221 / 8,162**. I nearly
promoted them as `cavity.Q_ext.loaded`. **They are not quotable**, for a reason
the rig itself already knows:

| | |
|---|---|
| `h3_driven.SHALLOW_DB` | **0.30 dB** — *"too shallow to fit"* |
| measured \|S11\|min, loaded | **−0.221 dB** — below the guard |
| what the rig prints | *"deeply UNDERCOUPLED, beta and Q0 are LOW CONFIDENCE"* |

🔑 **AND THE SENSITIVITY MAKES IT CONCRETE.** A 2× error in `beta` moves
`Q_ext_implied` from 8,221 to **4,110 or 16,441** — because Q_ext = Q0/beta is
*directly* proportional to 1/beta. The SAME 2× error moves `Q0 = Q_L(1+beta)`
only **104.0 → 105.9**, because beta ≪ 1 makes that term a 1.3 % correction.

✅ **So `cavity.Q0.loaded` = 104.6 IS robust and was promoted. `Q_ext_implied`
is NOT, and was not.** One number from one fit is trustworthy and its neighbour
is worthless; which is which is decided by the algebra, not by how clean the
column looks.

⚠️ **A PROVENANCE GAP — IN THAT FILE, AND SINCE FIXED.** In
`h3-driven-anchor-01.result.json` the guard reached the log but not the artefact:
no `shallow` on `points[]`, `shallow_db` null. ✅ **Current code does record
both** — `h3-gap2load-01`'s cold checkpoint carries `"shallow": true` and the
threshold at top level. So this is a caveat on reading the OLD file, not a live
defect; my first note generalised from one artefact to the rig and was wrong.
The lesson stands for that file: **it does not carry the caveat that governs
it** — so a later reader (me, today) sees a tidy `Q_ext_implied` column
with nothing marking it low-confidence. Separate measurement from evaluation
means the evaluation has to travel WITH the data.

🔑 **THIS IS ALSO WHY THE SERIES-GAP RUN IS THE RIGHT ONE.** At coupling.beta ≈
0.32 the dip is ≈ **−5.8 dB**, ~26× the guard. The run does not merely measure
the coupler — **it moves the measurement into the regime where the instrument
works.**

🔑 **THIS IS NOW THE HIGHEST-VALUE RUN IN THE PROGRAMME**, because it is both
the deliverable and the test of the assumption:

    measure cavity.Q_ext.loaded at ne = 7.9e18, same loop, same mesh family

- If it matches `cavity.Q_ext.cold`, the assumption is earned rather than
  assumed, and every cold Q_ext ever measured transfers to the loaded design.
- If it does not, **every loaded coupling.beta in the record is wrong**, and the
  27x series-gap lever was optimised against the wrong target.

⚠️ **The coupling target is `cavity.Q_ext.loaded`, NOT `.cold`.** Prose that
said "beta = 1 needs Q_ext = 105" was quietly naming a quantity that has never
been measured. ✅ `cavity.Q0.loaded` was added the same day for the same reason:
the target Q0 had no canonical name, so prose called it "loaded Q0" and left the
reader to infer the cavity.

## ⚠️ SUPERSEDED LIVE STATE — written 2026-08-27, stale for a week

> 🔴 **Stamped 2026-09-04. `h3-ehratio-01` is NOT running**; that host was
> reclaimed on 2026-08-28. The current state is at the TOP of this file.
> ⚠️ **A "LIVE STATE" block that is not refreshed is worse than none** — it
> asserts a running rig on every read. Kept only for what it records about
> `h3-ehratio-01`'s configuration and its slice_note correction.

### The original block follows


**RUNNING:** `h3-ehratio-01` (stamp `d6043449`) on a NEW host — 4 cases
`ld = 5, 8, 11, 14`, lw 8, barrel, gap2 0.5, grooved, cold. **8 eigen solves**
(2 port BCs per case). `h3_loopq` has REAL resume keyed on the config stamp, so
a reclamation costs only the case in flight.

    ops/watch.sh h3-ehratio-01        # mirror: h3-ehratio-01.watch.log

**What it answers:** rho = |E|/(c|B|) at the loop. `series_gap` reads 9.30
where TE011's own value at that radius is 0.218 (`h3-field-01`) — but a series
capacitor has a voltage across it BY CONSTRUCTION, so that alone decides
nothing. The NEW `leg_intact` / `leg_broken` probes are where it decides: legs
are current maxima, so a flux-linking loop must be H-dominated there.
F1/F2/F3 are declared in the config, before the run.

**🔴 CORRECTION TO THAT CONFIG'S OWN RECORD — read before quoting it.** Its
`slice_note` says "no torch". **Wrong: the torch is SAPPHIRE, eps = 9.39** —
`GEO_DESIGN` carries the design torch by default and the log confirms it. So
this run IS on `h3-field-01`'s slice (the comparison that matters) but is NOT
on `h3-lambda4-02`'s, which was DRIVEN with a VACUUM torch. Same four ld
values; the torch moves f0 by ~10.4 MHz, i.e. ~0.42 % in L/(wavelength/4).
⚠️ **The config was NOT edited to fix this, deliberately:** `stamp()` is
sha256 of the config file and every artefact name carries it, so an edit
mid-run would orphan the solves and silently empty the resume set. The
correction belongs in the write-up.

**LANDED SINCE:** `h3-lambda4-02` finished — `KNOWN.md` § MEASURED, Q_ext has an
interior minimum near wavelength/4. ⚠️ Its heading first read "wavelength/4 CONFIRMED"
and was downgraded: **surviving a falsifier is not confirmation** (user). One
thing IS falsified — the monotonic-area prediction.

**NOT LANDED, ON PURPOSE:** the E-vs-H results. User: *"I don't think we should
be updating KNOWN without going through the full process."* `ehratio.py` is the
evaluation layer; the numbers are in the session and the result files only.

**🔑 THE WATCHER IS STANDARDIZED — see CONVENTIONS §7bq.** It had failed FOUR
times, never the same way twice, and CONVENTIONS had nothing on it. `ops/watch.sh
<slug>` is now the only watch command to type; every line is mirrored to disk so
a buffering caller cannot hide a live watch; `ops/status.sh` is a SNAPSHOT and
`ops/remote.sh` no longer calls it a watch.

## Instance

**UP.** Address in `ops/env.sh` (one line — it was hardcoded in 29 places once).
`ops/go ops/status.sh` for state; `ops/go ops/remote.sh <rig.py> 32` to launch.

**After a spot reclamation:** launch `c7a.8xlarge` **in the volume's AZ** (EBS is
AZ-scoped — the easy mistake), attach, set the address in `ops/env.sh`, then
`NOSYNC=1 ops/go ops/mount.sh`. Exercised four times.
⚠️ `mount.sh` also checks that **pyflakes is in the env** — it lives on
`/opt/amip/envs/emsim`, NOT the root filesystem, because root is wiped by every
reclamation. Without it `preflight` silently stops checking undefined names.


### 🔑 STANDING REQUIREMENT — EVERY eigen rig emits MODE PURITY

**6 probes, no extra solve.** `P = |E_φ|²/(|E_r|²+|E_φ|²+|E_z|²)` at ≥3 φ × ≥2 r;
report **P_min, P_max and SPREAD**. TE011 has P=1 at every φ, so the spread is the
discriminator, and it cannot alias.

🔑 **This is the first tool the programme has for "how does a cavity change alter
the modes", and almost everything downstream depends on it** — groove depth, loop
size, torch ε and n_e all perturb the mode landscape, and until now there was no
continuous measure of the result, only a binary label that could be wrong.

Implementation is in `h3_ladder.purity()`; the probe layout is
`PROBE_PHI_DEG=[0,40,80] × PROBE_R_FRAC=[0.4805, 0.25]`.
✅ Validated: rejects both TM111 polarisations AND TE311 (which A2/A0 binned as
m=0 with 0.0004), accepts bare TE011 at 0.9973–1.0000.
⚠️ Report P even when it PASSES — the value is the measurement, not the verdict.

### 🔑 STANDING REQUIREMENT — every H3 rig emits PRIORS, not just verdicts

**These results are CO-DEPENDENT.** Groove depth × loop size × n_e × torch
permittivity all move the same mode landscape, so the end state is not a list of
answers — it is a surrogate that can be optimised over the joint space.
`OPTIMIZER.md`'s own rule: *"a finding belongs there when stated as something a
surrogate can EVALUATE, not as a number."*

So every H3 rig must return, and its report must print:

| for the optimiser | not just |
|---|---|
| the CONSTRAINT value — how many modes in 2.40–2.50, and their margins | "the filter works" |
| the value AND its uncertainty (A2/A0, identification margin, one-sided vs two-sided width) | a bare number |
| the EVALUATION OUTCOME — converged / missing-data / infeasible, with NLEPS count | a silent gap |
| the COST — tets, ND dofs, seconds, NLEPS — so the cost model stays fitted | wall-clock in a log |
| **which other variables were held fixed, and at what** | an implicit context |

⚠️ **That last row is the co-dependence.** A number measured at one groove depth,
one loop size and one n_e is a SLICE. Record the slice coordinates or the
surrogate cannot place the point.

🔴 And a failed evaluation is **MISSING DATA, not a bad score** (§3). Scoring it
badly teaches the surrogate to avoid regions that are merely hard to solve.

---

## 🔴🔴 SCOPE REOPENED 2026-08-24 — THE MODEL WAS NEVER RESTORED

User: *"We simplified greatly to answer the instrument and methodology issues,
and then didn't add critical features back. That puts everything except viewports
back in scope (no viewports because we haven't chosen axial vs radial)."*

**BACK IN SCOPE:** torch material (**sapphire ε = 11.6**, not ε = 1 / absent) ·
**gas feed aperture** (−z cap) · **chimney/exhaust** (+z cap, 21 mm).
**STAYS OUT:** viewport + light trap — axial vs radial not chosen.

🔴 **No rig has EVER passed a non-zero chimney or feed.** As modelled, the torch
is sealed at both ends by solid metal. See `KNOWN.md`.
⚠️ **I raised an alarm about the feed aperture's RF seal and WITHDREW it**
(§7ak). The uniform-fill cutoff said sapphire gives 4.6 dB; field-weighted it
gives **53.8 dB — the seal holds**. The ceramic annulus carries only 18.8% of the
TE11 energy, so ε_eff is 3.0, not 11.6. **The apertures remain in scope as
COMPLETENESS items, not alarms**, and rank below the torch material.

⚠️ **E3 is running on a SEALED cavity with a sapphire torch.** Its 3-channel
closure is still valid for that geometry — but **apertures would add a RADIATION
channel it does not include**, so a re-run is needed once they are in.

**Scoping the restoration, in dependency order:**
1. **Decide the aperture dimensions.** `geometry.py` indicates chimney 21 mm
   (meeting torch outer radius 10 mm). Feed diameter and `torch_ext` need a
   decision — the feed must pass the torch and reach its plumbing.
2. **Re-mesh with torch + both apertures**, then re-run the frequency ladder:
   every f₀ in the record is for a torch-free, sealed cavity.
3. **Re-run E3** with the radiation channel present.
4. Then the loaded work (`h3_driven`, `h3_margin`) — band margins move with f₀.

## ⚠️ THE ORDER — and why the circular dependency is NOT real  🔴 PREMISE NOW IN DOUBT

> ⚠️ **Stamped in place 2026-09-04.** This section breaks the circular dependency
> by asserting **"Q_ext | the loop | ❌ NO (cold, geometric)"** — that external Q
> does not depend on cavity state, so ONE Q_ext per loop serves every density and
> `beta(ne) = Q0(ne)/Q_ext` is arithmetic.
>
> 🔴 **THAT PREMISE IS NOT ESTABLISHED.** Measured cold -> loaded on one coupler:
> **+21 %**. `h3_loopq`'s own docstring already put the load dependence at
> **~9 %**. And the only cross-coupler test (azimuthal vs barrel) suggests loaded
> Q_ext may not be loop-set at all. ➡️ *§ "Q_ext IS GEOMETRIC" IS UNSUPPORTED
> WHEN LOADED*, top of file — including the single run that would settle it.
>
> **The ORDER itself (item 8 then item 7) still stands as a sequencing argument.**
> What is in doubt is the claim that makes beta cheap: if Q_ext must be measured
> per (loop x density) rather than per loop, item 7 is a GRID, not a list.

**User, 2026-08-24: *"we have a few open threads now, and some circular
dependencies... We have to change only one thing at once."*** ✅ The threads are
real. **One of the dependencies is not.**

**The apparent circle:** coupling.beta and VSWR are DESIGN OUTPUTS of the loop (§7am) → so
measuring them at the anchored density seems worthless until the loop is chosen →
but choosing the loop needs the loaded Q₀ → which needs the anchored density.

🔑 **IT BREAKS, because H3 does not actually measure coupling.beta — it measures Q₀:**

| quantity | set by | depends on the other? |
|---|---|---|
| **Q₀(n_e)** | cavity + plasma | ❌ **NO** |
| **Q_ext** | the loop | ❌ **NO** (cold, geometric) |
| coupling.beta, VSWR, current, dump | **Q₀ / Q_ext** | derived — **arithmetic, not a solve** |

✅ **And in the LOADED regime the loop barely enters the extraction at all:**
Q₀ = 1/(1/Q_L − 1/Q_ext) with Q_L ≈ 155 and Q_ext = 9,231 gives **Q₀ = 1.017 ×
Q_L — a 1.7 % correction.** coupling.beta ≪ 1, so **Q₀ is essentially measured directly.**
⚠️ The error amplification that bites when Q₀ ≫ Q_L does **not** apply here.

🔑 **So item 8 and item 7 are INDEPENDENT, and neither invalidates the other.**
Run 8 → Q₀ at the operating point, permanent. Run 7 → Q_ext per loop family,
permanent. **coupling.beta for any loop × any density is then arithmetic on the pair.**

### The order

| | do | changes ONE thing | blocked by |
|---|---|---|---|
| **1st** | **item 8 — H3 at the anchored density** | **density** (torch, geometry, solver all unchanged) | **nothing** ✅ |
| 2nd | item 7 — Q_ext vs turns / mount | **loop** (cold, no plasma, no sapphire) | nothing ✅ |
| 3rd | one sapphire+plasma case at the **anchor** | **torch ε**, at the now-known density | needs 1st |
| 4th | E3 closure, or the preconditioner | — | needs 3rd's verdict |
| 5th | restoration: aperture dims → re-mesh → re-ladder | **geometry** | a DESIGN decision, not a measurement |

🔴 **WHY ITEM 8 IS FIRST and not item 7:** it is prepared, it is the only one
whose numbers were being **actively quoted wrong** (VSWR 80–89, coupling.beta, 45 A, 960 W,
the 400× spread are all interpolated), and it changes exactly one variable
against a **measured 43-minute baseline**.
⚠️ **Its one known offset is quantified, not a confound:** vacuum torch →
f₀ high by ≈ 13.9 MHz, Q high by ≈ 2.2 % (E3 case B). **Band margins carry that
offset; Q₀, coupling.beta and VSWR essentially do not.**
🔑 **Step 3 is also the test of the contrast diagnosis** — it predicts sapphire
+ plasma converges at the anchor (span +11.6/−1.46). **One case answers both.**

## 🔴 THE RE-DERIVE LIST — what is now known to be unsupported

**Opened 2026-08-25.** Each of these was believed, is now marked TENTATIVE or
open, and **must not be quoted until re-derived.**

| # | what | why it is not supportable now | cost |
|---|---|---|---|
| ~~R1~~ | ✅ **RESOLVED 2026-08-25 — ε_⊥c = 9.39, MEASURED** | Krupka, Huang & Tung, *Meas. Sci. Technol.* **16** (2005) 1014, fig 10: *"perpendicular to the anisotropy axis … **9.39 ± 0.5 %** for sapphire"*, by **TE0np modes in a cylindrical sample — our own mode family**. So **11.6 is ε_∥c** and `geometry.py` had the axes inverted. Canonical value updated; **the constant is NOT flipped yet** — that moves every stored f₀ and belongs with the restoration | — |
| ~~R2~~ | ✅ **CLOSED 2026-08-25 — torch shift = −10.40 MHz** | `e3-torch-01`, matched pair (B_sap ε=9.39 vs B_vac ε=1.0, wall-loss only). **Not the cancellation I predicted** — the R-era slope was 4.4× too large; the real sensitivity is **1.50 MHz per unit ε**. ⚠️ The old −13.87 was wrong twice: wrong ε *and* cross-geometry. 🔴 **~10.4 MHz is 6.5× the anchor band — the restoration KEEPS its urgency** | — |
| ~~R3~~ | ✅ **RESOLVED 2026-08-25 — NO SOLVE NEEDED** | Decimating the anchor's own sweep gives Q_L error vs samples-across-linewidth: 30 → −0.8 %, **16 → −7.0 %**. The cold case had **14 samples** and read **−7.1 %** against eigen. **The driven/eigen "disagreement" was SAMPLING, quantitatively.** ✅ Cold Q_ext = **9,117** (eigen) stands; the driven 8,462 is the artefact | — |
| **R4** | 🔴 **E3's closure (F1)** | ⚠️ **REDIAGNOSED 2026-08-25.** Not sapphire+plasma — `h3_qext`'s anchor case **timed out with a VACUUM torch** (159 PCG failures, 0 iterations) at ε = −1.46. **ε-near-zero conditioning, the prediction recorded before the run.** η_plasma stays unquotable | 🔴 **the PRECONDITIONER, and it does NOT depend on R1** |
| ~~R5~~ | 🔴 **FALSIFIED 2026-08-26 — the correction goes the OTHER WAY.** The design cavity MEASURES Q₀ = **43,259** (barrel) / 43,253 (cap), i.e. **−0.61 %** against the stored 43,523, not +1.46 %. ⚠️ **44,160 was `e3` B_sap = WALL LOSS ONLY**, excluding sapphire's tan δ = 3.5e-5. A partial-loss Q compared against a total-loss Q — §7c's η trap again. ✅ E3's channels recombine (1/44,160 + 1/1,911,259 → 43,163) to within **0.22 %** of the measurement, so both are corroborated. **Not promoted**: the stored value is CAP-mount and the design mount is item 7's open question. See KNOWN.md § THE TORCH RESTORATION | ✅ **done** |
| ~~R5-old~~ | ⚠️ ~~`eta.reference` = 43,523 — CONFIRMED, correction now sized~~ | ✅ Independently reproduced by `e3-torch-01` B_vac (43,522.8) from a rig that built its own mesh. 🔑 The design-torch value is **+1.46 %** higher (44,160.1), not the +2.0 % estimated at the wrong ε | re-measure with the restoration |

✅ **R1 WAS THE ROOT OF FOUR OF THE FIVE, AND IT IS NOW CLOSED BY A CITATION.** R2 collapses to *"probably ~0, verify"*; R5's 2 % η correction largely evaporates with it; **R4 was never dependent on it** — that is ε-near-zero conditioning and still needs the preconditioner. 🔑 **The remaining physics is R4 plus item 7.**

### ✅ ANSWERED 2026-08-25 — and my first answer was WRONG

⚠️ **I first landed "≳30 samples across the 3 dB width for <1 % in Q_L", derived
from ONE density. Testing it on three killed it:** 1e20 showed **0.0 % error at
TEN samples** while cold showed **−12.5 % at eight.** Sample count does not
determine the error.

🔑 **THE ERROR IS EDGE QUANTISATION.** Q_L comes from the 3 dB width, and the
edges were snapped to the nearest GRID POINT. Each edge can be off by up to one
step, so the bound is **|ΔQ_L/Q_L| ≲ 2/N** — and where it lands inside that
bound depends on whether the width happens to be commensurate with the step.
**1e20's 16.00 MHz width is exactly 80 × 200 kHz, so decimation moved nothing.
That is luck, not accuracy.**

✅ **THE FIX IS INTERPOLATION, NOT MORE SAMPLES** — linearly interpolate the
|S11| crossing, as for the vertex:

| density | N | grid edges | **interpolated edges** |
|---|---:|---:|---:|
| cold | 13 | −6.4 % | **+0.0 %** |
| cold | 6.5 | −18.1 % | **−0.8 %** |
| anchor | 14.8 | −7.3 % | **−0.3 %** |
| 1e20 | 9.9 | −1.1 % | **−0.1 %** |

> ✅ **SPEC: interpolate both the vertex AND the 3 dB crossings. Then ~10 samples
> across the width suffices for ≲1 %.** Without interpolation, no achievable
> sample count is reliable — only commensurate ones are accurate, and you cannot
> know in advance which those are.

### ~~CHEAP AND UNCLAIMED: the sweep step a target Q accuracy requires~~

**From the conjugate-pair framing (KNOWN.md).** Driven Q error tracks samples
across the linewidth: **14 → −7.1 %**, **80 → −3.3 %**. Two points, not a law.
**Nothing in this programme specifies a step for a target Q accuracy** — every
`COARSE_STEP`/`FINE_STEP` was chosen by feel.
✅ **One mesh we already have, three step sizes, Q vs samples.** It would size
every future driven sweep and retire R3 (cold Q_ext, sidelined as
under-resolved) at the same time.

## 🔴 THE GEO RE-RUN LIST — opened 2026-08-25, after the GEO fix

**User: *"We can't leave bugs in place just because they might invalidate
results. We have to fix, and then add a new queue item to verify or re-run."***
✅ The bugs are fixed. This is the verification debt they created.

### What was wrong

**`GEO` carried `A_MM, L_MM = 103.70, 88.53` — D/L = 2.343, the cavity H1
REJECTED.** H1's answer is D/L = 1.525 (a 88.0045, L 115.4158), stated plainly
in `KNOWN.md`. The literal sat as GEO's **default**, so any rig that did not
append its own `--radius/--length` meshed a cavity nobody is building.

✅ **The H3 design record is PROVEN unaffected — by artefact, not by argument
(§7bm).** Every H3 mesh SIDECAR records `radius 88.004517 / length 115.41576`,
which is H1's cavity. That is the consumer's own record of what it actually
meshed, so it discharges the burden. `h3-bore-01`, `h3-loop-barrel-01` and the
e3/h3_qext meshes all carry it. **Nothing measured this week moves.**

### What was fixed

| | |
|---|---|
| `cavity.d_over_l` = 1.525, `source.f0.ghz` = 2.45 | **declared** — the shape now has one home |
| `physics.design_point(d_over_l, f_ghz)` | the ONE derivation. `A_MM/L_MM` now DERIVED, so GEO cannot disagree with H1 again |
| `DL` in `e0k2_anchor` + `h2_groove` | were **two** copies of the same literal → bound |
| the frozen groove `(5.0, 10.0)` | was in **SEVEN** files → `cavity.groove.mm`, 7 consumers |
| the design loop `11.0, 8.0` | was in **NINE** files → `loop.size.mm`, 9 consumers |
| `CAP_R_FRAC`, `LOOP_RW`, `LOOP_GAP`, `LOOP_PHI` | bound; the last two are **TENTATIVE** and now say so at the call site |
| `e0q_wallloss` `AL = 3.5e7` | bound; `AG` = silver kept as an explicit COMPARATOR |
| `preflight` geometry pattern | geometry was **invisible** to the linter — that is why none of the above was ever flagged |

🔑 **Every bound site was asserted IDENTICAL to the literal it replaced before
the edit was kept.** 16 duplicates collapsed to 2 canonical names, no number
moved.

### 🔴 THE DEBT — rigs that meshed the LEGACY cavity

These used `GEO`/`GEO_DESIGN` **without** overriding, so they ran D/L = 2.343.
🔴 **UNDER §7bm THEY ARE INVALID UNTIL A RE-RUN SAYS OTHERWISE.** I first wrote
that their conclusions were "mostly self-consistent, because closed form was
evaluated at the same a/L they meshed". **That is an argument, not a
measurement, and it does not discharge the burden.** They are E0 instrument
rigs rather than design rigs, which affects PRIORITY, not validity.

⚠️ **Do not cite any number below until its rig is re-run.**

| rig | what it claims | action |
|---|---|---|
| `e0b_offset` | mesh offset invariance | re-run on H1's cavity |
| `e0f_geomorder` / `e0f2_geomorder` | geometric order | re-run |
| `e0j_frontier` | cost frontier | re-run — **sizing advice descends from this** |
| `e0kp_meshfloor` | mesh floor | re-run |
| `e0k_driven_vs_eigen` | driven vs eigen | re-run |
| `e0m_meshthreads` | thread scaling | re-run (cost only; low value) |
| `azimuthal`, `meshdiff`, `meshstage`, `cachetest` | utilities | no claim — no re-run |

⚠️ **`e0l_scaling`, `facetcount`, `resplit` keep the legacy literal ON PURPOSE**
— they ANALYSE meshes built at those dimensions, so binding them to H1 would
silently break the comparison. Each is now marked `# LEGACY` in place. **Nothing
in them is a design number.**

### 🔴 AND THE THIRD DEBT — 30 RESULT FILES CARRY NO STAMP

**User, 2026-08-25: *"result.json is not a valid filename."*** Correct, and
chasing it found a hole bigger than the name.

🔴 **`slug.check_stamps()` was KNOWN-SLUG-DRIVEN, so it was nearly blind.** It
only inspected slugs that already have a `baseline-*.json`. Every artefact whose
slug never got a config was invisible: **30 of 32 `*.result.json` files carry no
stamp and the check reported ONE.** ⚠️ *An audit that can only see what is
already registered is not an audit* (§7d) — and this is the second instance
today, after the linter that could not see geometry.

✅ **Fixed both ways:**
- `check_stamps()` now sweeps **what is on disk**, not what is registered.
- `outfile()` **refuses** a suffix that is a path, a config name, or one already
  carrying a stamp — so a double-stamped or unqualified artefact cannot be
  produced by the normal route.
- `slug.unstamped_artefacts()` makes the burn-down countable.

**The 30, by family:**

| family | files | status |
|---|---:|---|
| `e0b` `e0f` `e0f2` `e0j` `e0k` `e0kp` `e0m` | 7 | **already queued above** — same rigs, same re-run |
| `e3` | 7 | E3 closure; F1 still open anyway |
| `e0k2` | 6 | instrument anchors — several already superseded |
| `e0v` | 3 | — |
| `e0c` `e0d` `e0e` `e0q` `h1` `h3` `h4` | 7 | one each |

🔴 **UNDER §7bm THESE ARE NOT CITABLE AS CURRENT RESULTS WITHOUT A RE-RUN.**
Their inputs cannot be verified — that is precisely what the stamp exists to
prove. ⚠️ **This does NOT mean they are wrong**; it means the record cannot show
what produced them. The two that DO carry stamps (`h3-bore-01`,
`h3-loop-barrel-01`) are the only fully provenanced results in the tree.

🔑 **Priority: LOW, and deliberately so.** Most are E0 instrument rigs already
queued for the GEO re-run, which will re-produce them stamped as a side effect.
**Do not re-run them for the stamp alone** — re-run them when their claim is
needed, and take the stamp then.

### 🔴 THE FOURTH DEBT — THE MESH SIDECAR DOES NOT RECORD THE LOOP SIZE

**Opened 2026-08-27, by `h3-lambda4-02`.** `geometry_mm` records `loop_cap_r`,
`loop_mount`, `loop_gap2`, `loop_flange_r`, and `loop_phi_deg`/`loop_tilt_deg`
sit alongside it — **but not `[ld, lw]`, the loop's actual size.**

🔴 **This is the artefact the programme relies on to discharge §7bm.** The GEO
debt was closed "by artefact, not by argument" because every mesh sidecar
recorded `geometry_mm.radius/length`. For a loop sweep the equivalent record
does not exist, so when `h3_driven`'s tags collided there was **nothing in the
sidecar to bind a point to its ld** — it took a re-mesh (`verify_ld_tets.py`)
to do by measurement what the sidecar should have carried for free.

✅ **THE FIX IS ONE FIELD:** `geometry_mm.loop = [ld, lw, rw, gap]` in
`geometry.py`, alongside `groove`. Then assert it at the consumer, the way
`cavity.groove.mm` is asserted (`mesh-is-what-you-ordered`).
⚠️ It changes no mesh — sidecar content only — but it touches `geometry.py`,
which owns `GEO`/`GEO_DESIGN` and the groove. **Verify the tet count is
unchanged on one mesh before and after.**

### 🔴 THE OTHER DEBT — values still literal

The widened linter surfaced residue that was invisible before. It is
grandfathered so it cannot grow, and **the list may only shrink**:

- `h3_loaded.Q_BARE_WITH_LOOP = 29,854` and `Q_BARE_EMPTY = 44,384` — **both are
  RETRACTED η references** (§7c). These should be **DELETED, not bound.**
- `h3_step3.H3COLD_PICK_GHZ = 2.440003` — from a retracted `h3_cold` result.
- `h3_margin.NE = 1e20` — the superseded density (§7ab), in a rig still using it.
- `h3_qext.LOOPQ_EIGEN_NO_TORCH = 9,231` — has a canonical home
  (`cavity.Q_ext.cold`, no_torch context); bind it.

**Verification for the whole item:** re-running any one E0 rig on H1's cavity
must reproduce its CONCLUSION (the instrument claim) while changing its
NUMBERS. If a conclusion flips, that rig's claim depended on the cavity and was
never an instrument result.

## 🔴 THE MATERIALS QUEUE — opened 2026-08-27

**User: *"We should also try to get rid of all PEC that would also be a real part
in a real build. I'd guess aluminum for the cavity, copper otherwise."***

⚠️ **The premise needed one correction and the conclusion survives it.** Almost
nothing is spuriously PEC: `geometry.py:990` tags the wall TOPOLOGICALLY — every
face with a single adjacent volume — and the loop wire is cut OUT of the vacuum,
so its surface has one adjacent volume and is swept into attribute 90 with the
cavity wall. Confirmed from the resolved config Palace actually ran:
`Conductivity {Attributes:[90], 3.5e7}` and `PEC {Attributes:[91]}`, where 91 is
only the port face in the shorted control.

🔴 **So the loop is not PEC — it is ALUMINIUM, and indistinguishable from the
wall.** Two defects, one cause.

| A | **the loop is the wrong metal** | it should be copper 5.8e7, not the wall's 3.5e7 |
| B | **its loss cannot be separated from the wall's** | one attribute, one Conductivity entry, one number out |

⚠️ **B invalidates a claim I made today.** "The coupler eats 45.3 % of cold
dissipation at wavelength/4" is NOT supportable: the solve cannot tell wire loss from wall
loss. **What is measured is that the loop's PRESENCE raises dissipation on the
conducting surfaces by 83 % (Q₀ 44,414 → 24,292), location unknown.**

### The order, and why

| | do | why here |
|---|---|---|
| **A1** | **give the loop its own attribute + copper** | 🔴 **FIRST.** It moves every Q₀ and every loss number downstream. Re-running anything before it burns solves on numbers that will change (§7bp) |
| ~~A6~~ | ✅ **DONE** — the surface/volume rule has ONE definition | 🔴 **21 SITES ACROSS 18 FILES**, not the "nine" I first reported — I had capped the grep with `\| head`, and **undercounting a duplication is how you fix most of it and leave the rest to fail later**. All bound to `volume_attrs(meta)`, proven identical to the expression it replaced on a pre-loop sidecar. `e0k2_anchor.shared_energy_list` now takes `meta` instead of `attrs` (an attrs dict CANNOT say which entries are surfaces; only the sidecar can) and its five callers are updated. Zero new lint warnings, diffed against HEAD |
| A2 | re-run the three missing `h3-ehratio-01` cases | needs a SETTINGS decision (645 / 1,402 NLEPS without convergence is conditioning, not impatience) **and** A1 |
| ~~A3~~ | ✅ **DONE** — `h3_loopq`'s V1 anchor is configuration-aware | It matched the anchor case on `(ld, lw)` + `grooved` only, so every barrel+capacitor run was compared against a **cap loop with no capacitor**. Now SUPPRESSES with the reason instead of firing. `check_v1()` is a pure function of the points; all five paths exercised, two on real landed data |
| ~~A4~~ | ✅ **DONE** — item 7 step 4 **RETIRED**, not restated | Stronger than expected: **area is bounded by length**, area_max = (L + gaps)²/8, and the design sits at **97.5 %** of its own bound. The surviving axis is **aspect ratio at fixed L** — the radial/azimuthal split of the conductor |
| ~~A5~~ | ✅ **DONE** — item 7 step 3 reframed, and a probe added | The **port gap is the tighter break** (0.3 vs 0.5 mm) and carries the drive, yet had no probe while the series gap had one. `port_gap` added to `h3_loopq`; `fieldcheck` maps it to a limit. ⚠️ `values.get` REFUSED its width as TENTATIVE — correct, it has no owner |

### A1 — what it must prove, not just do

`loop.conductivity.s_per_m` = 5.8e7 is declared in `baselines.json` and consumed
by **NOTHING** — zero hits across every rig. This is its first consumer, so the
declared-but-unused pattern is exactly the risk.

- ✅ **V** tet count UNCHANGED (a boundary retag is not a geometry change);
  the wall attribute's face count drops by exactly the loop's faces; the new
  attribute contains only wire faces.
- 🔴 **F** if Q₀ on a known case does not move AT ALL, the new attribute is not
  being consumed and the change is cosmetic. Copper is less lossy than
  aluminium, so **Q₀ must RISE** — a fall means the assignment is inverted.
- 🔑 The payoff is the PARTITION: wall loss and loop loss as separate numbers,
  which is what the 83 % question actually needs.

### A3 — the V1 anchor fires on the wrong comparison

`h3_loopq` compares every run against `h3_step3`'s **cap loop with no series
capacitor** (Q_ext 9,117, coupling.beta 4.8) and printed *"THE ANCHOR DOES NOT REPRODUCE —
treat every other row as SUSPECT"* over a run whose own declared control passed
at 0.6–1.9 %. **A guard that fires when it should not trains you to ignore it.**
It should suppress on a non-cap config the way `eta` already does.

## THE QUEUE

| # | item | status |
|---|---|---|
| 1 | Matching network required | ✅ answered — tuner spec in `../control-loop/` |
| 2 | **Anchor n_e** | ✅ **7.3–8.6e18**, from MICAP's measured 5220–5270 K |
| **7** | 🔴 **DESIGN the loop — barrel mount, then the SERIES CAPACITOR** | **THE BIGGEST LEVER LEFT.** ~45× in Q_ext is calculated and never simulated; and I ∝ √VSWR, so it is the only thing that touches the tuner's thermal wall |
| 3 | Test the coupler class | 🔴 **REOPENED — and it is the biggest lever left.** ❌ Aperture is out (patented; the cavity IS the waveguide). 🔴 **But the LOOP was never designed** — forced into existence so driven solves would have a port; `h3_loopq` swept AREA only. **Q_ext = 9,231 floors ONE arbitrary family.** VSWR 85→20 needs 4.2×, coupling.beta=1 needs 84×. See CONVENTIONS §7al |
| 4 | **H3's HOT leg** | ✅ **DONE — H3 IS COMPLETE** |
| **5** | **PLAN E3 — the energy-balance closure** | ⚠️ **RAN (EXIT=0), 3 of 5 landed.** ✅ **B, D, E.** ✅ **F2 resolved by a bound** (η_diel ≤ 2.27%; PLAN's ~2% CONFIRMED). ✅ **E gave an eigen↔driven cross-check — 70 kHz and 3.42% — which RESTORES V1's anchor.** 🔴 **A, C failed on the sapphire+plasma ε-contrast, already documented in `h3_driven` lines 10–11 BEFORE E3 was written** (§7an). 🔴 **F1 untested; η_plasma unquotable** |
| 6 | H4 ignition | ⏸️ parked |
| ~~8~~ | ✅ **H3 AT THE ANCHORED DENSITY — DONE** | `h3-driven-anchor-01`, 9 points. **f₀ 2.458529, Q₀ 105, η 0.9976, VSWR 75–82, slew +7.04 MHz, margin 41.5 MHz.** ⚠️ vacuum torch (R1/R2) |

### 8. 🔴 H3 at the anchored density — the operating point was never solved

**User, 2026-08-24: *"E3 seems like a waste of time at 1e20. In fact, we probably
have to re-run H3 with the right number."*** ✅ Both correct.

🔴 **`NE_GRID` never contained the anchor.** 7.3–8.6e18 falls in the 3e18 → 1e19
gap — **3.3× wide, VSWR 43.3 → 99.3 across it**, the steepest limb, just below
the peak. **VSWR 80–89, Q₀ ≈ 109, coupling.beta ≈ 0.012, ~45 A, ~960 W and the 400× coupler
spread are ALL INTERPOLATED**, never solved.

✅ **PREPARED in `h3_driven.py` (edited, parses, NOT launched):**
- `N_E_ANCHOR = 7.9e18` with `_LO = 7.3e18`, `_HI = 8.6e18`, all three added to
  `NE_GRID` (now 9 points).
- The analysis block's hardcoded `P.get(1.0e20)` → `P.get(N_E_ANCHOR)`. **1e20
  was being reported as "the operating point" by the rig itself** (§7ab).
- ⚠️ **F1's premise is stale and I did NOT silently re-tune it.** It calls 1e19
  *"one decade below the operating point"* — true only when that meant 1e20;
  against 7.9e18, 1e19 is **above**. And η is flat 0.986–0.998 across the whole
  grid, so it cannot discriminate anyway (§7z). It now prints as a **recorded
  value, explicitly not a test**, pending a restatement.

    ops/go ops/remote.sh h3_driven.py 32      # DRIVEN — unaffected by the
                                              # eigen preconditioner defect

✅ **Backup at** `scratchpad/h3_driven.py.bak`.

**COST — measured, from the previous 6-point run (`h3_driven.log`, EXIT=0):**
COLD 441 s · 1e18 **986 s** · 3e18 319 s · 1e19 290 s · 3e19 286 s · 1e20 279 s
= **43 min.** The three anchor points bracket 3e18/1e19, both ~300 s, so
**+~15 min → ~58 min total.** 🔑 Driven cost scales with Q (samples ~ Q), which
is why 1e18 is the slow one and the loaded points are cheap.

🔴 **CAVEAT — THIS FIXES THE DENSITY, NOT THE GEOMETRY.** `h3_driven.py:235`
passes `--torch-material 1.0,3.5e-05`: **the torch is meshed as VACUUM.** E3
case B puts the sapphire torch at **≈ −13.9 MHz** (provisional). So the re-run's
f₀ and band margins will still be high by roughly that much, and the restoration
list above still applies. **Two known-wrong inputs; this corrects one.**
🔑 **Driven, not eigen** — fixed-ω linear solves, so **item 5's preconditioner
defect does not apply.** This is unblocked; E3 is not.
⚠️ `ops/go` will refuse to sync while E3 holds the instance. That guard is
correct — wait for E3 to finish rather than forcing `NOSYNC=1`.
| **7** | 🔴 **DESIGN the loop — barrel mount, then the SERIES CAPACITOR** | **Buildable now.** 🔑 A **45×** mechanism (Q_ext → ~320) is already in `geometry.py`, calculated and never simulated. Turns is NOT buildable |

### 7e. ✅ ITEM 7's MEASUREMENT PHASE IS CLOSED — and the objective changed

**User, 2026-08-25: *"We have enough information for optimization at this
point."*** ✅ Agreed. **9 Q_ext values across 4 design families**, spanning
8,716 → 322, with every control reproducing exactly.

| step | question | answer |
|---|---|---|
| 1 | barrel vs cap mount | ✅ barrel is **5.6 % better**, and free. My 1.93× prediction was falsified; the 1.39× field ratio behind it was a **legacy-cavity** number |
| 2 | does a series capacitor work? | ✅ **7.6×** at the bare-wire gap. Falsifier needed ≥4× |
| 2b | which way does the gap move it? | ✅ **wider** — 12.1× at 0.75 mm |
| 2c | where is the optimum? | 🔴 **not bracketed** — 27.0× at 2.25 mm, still falling |
| — | **is minimising Q_ext even right?** | 🔴 **NO** — see KNOWN.md § CORRECTION |

🔴 **THE OBJECTIVE IS NO LONGER "MINIMISE Q_ext".** Q_ext serves cold AND
loaded, whose Q₀ differ 265×, so the sweeps were sliding along a **trade**:
loaded VSWR 83 → 3.1 bought cold ignition power 556 W → 45 W. **The minimax
fixed loop is Q_ext ≈ 1,700 (VSWR ~16 in both states) — roughly where the gap
sweep STARTED.**

### ✅ MEASURED — THE AZIMUTHAL LOOP COUPLES ~10x LESS (2026-08-30)

**FIRST azimuthal Q_ext ever measured.** Reference geometry, h = 3 mm,
L(arc) = 12.24 mm, 1 mm wire, grooved, unwound 17.94 mm, clearance 2.00 mm.
Slug `h3-azim-01`, stamp `9e60089f`.

    pec     Q0    = 43,744   f0 = 2.439429   P>=1.0000  spread 0.0000
    lumped  Q_L   =  9,154   Q_ext = 11,576  coupling.beta = 3.779   OVERCOUPLED

⚠️ **PROVENANCE IS THE WATCH-LOG MIRROR, not the artefact.** The host was
reclaimed mid-grid; `h3-azim-01.9e60089f.result.json` is on the EBS volume and
has never been fetched. Numbers above are from `h3-azim-01.watch.log`. Re-fetch
and reconcile before this is cited anywhere.

**Against the rectangular barrel loop (13x6, `h3-aspect-02`): coupling.beta 36.8 -> 3.78.**
User: *"Already at that VSWR, it's workable."*

⚠️ **THE COMPARISON CROSSES RUNS.** The rectangular figure is from a DIFFERENT
aspect-ratio cavity, and the `-01`/`-02` offset is still unresolved and parked.
The ~10x gap is far larger than that offset so the DIRECTION holds, but the
ratio is not a measurement until both are on one cavity. See
[epoch comparisons are not measurements].

🔑 **The null hypothesis below is REFUTED.** It argued a topology could only move
VSWR through Q_ext, and predicted no benefit. Q_ext is exactly where it moved:
1,097 -> 11,576. The reasoning was right; the prediction of "no benefit" was
wrong, because it assumed the two topologies reach comparable loop areas at
comparable coupling. They do not — the azimuthal loop sits where it barely
perturbs the mode (P >= 1.0000, spread 0.0000, Q0 cost 0.75% vs 6-12%), so it
extracts far less energy for the same conductor length.

### ✅ MEASURED — coupling.beta ∝ AREA^4, and critical coupling is BRACKETED (2026-08-30)

Azimuthal wire loops, slug `h3-azim-01` stamp `9e60089f`, all P >= 0.9999.
Area = L x h. Q0 is flat at 43,744-43,937 across all four, so the loop barely
perturbs the mode and every difference is in Q_ext.

    h   L(arc)  A/mm^2   Q_ext     coupling.beta     VSWR
    2   10.2      21    112,004   0.392     2.55   undercoupled
    2   12.24     25     62,800   0.699     1.43   undercoupled
    2   14.2      29     31,111   1.410     1.41   OVERCOUPLED
    3   12.24     37     11,576   3.779     3.78   OVERCOUPLED

🔴 **SUPERSEDED — "area governs" HOLDS ONLY FOR h <= 3 mm.** See the
h=4 swap test below. Area^4 fits 6 points to <10% and then fails by 29%.

🔴🔴 **RETRACTED 2026-08-30 — THE SATURATION WAS THE WRONG VARIABLE.**
*User: "I also worry that h is mis-characterized. The distance to wall should be
the dominant term, so a thicker wire or strip has the same wall distance. h
should just be the height of the stud that the strip/wire sits on."*

`h` was the conductor CENTRELINE height; wall clearance was `h - t/2`, so it
moved with conductor thickness. Re-fitting the SAME wire data at L = 10.2
against CLEARANCE instead:

    vs centreline h (what was fitted) : 3.89 then 2.99   -> 23% apart
    vs CLEARANCE (the stud height)    : 2.27 then 2.12   ->  7% apart

**There is no saturation.** Centreline height and wall distance differ by a
fixed offset, so a power law in one cannot be a power law in the other — the
"saturation" is the residual of fitting the wrong variable. ⚠️ This also
retracts what was built on it: **"buy coupling with L, not h" is withdrawn.**
Both are live levers; L simply has the steeper exponent (3.87 vs ~2.2).

🔴 **AND WIRE-vs-STRIP WAS NEVER AT MATCHED WALL DISTANCE.** clearance = h-t/2,
so at every h the 5x1 strip sat 0.5 mm FURTHER out than the 1 mm wire —
systematically. The 3.0-4.0x ratio is confounded with that offset and must not
be quoted as a cross-section effect until re-measured at matched clearance.

⚠️ SUPERSEDED, kept for the record — the original claim:
🔑 **coupling.beta ∝ L^3.88 x f(h), and f SATURATES above h = 3 mm:**

    L-exponent at h=2 .......... 3.87     rock steady
    L-exponent at h=3 .......... 3.89
    h-exponent, L=10.2, 2->3 ... 3.89
    h-exponent, L=10.2, 3->4 ... 2.99     <-- saturates

✅ **THE h=4 SWAP TEST IS WHAT CAUGHT IT.** h=4/L=10.2 (A=42) vs h=3/L=14.2
(A=43): near-identical area, coupling.beta 4.486 vs 6.872 — 1.53x apart. Area alone
cannot produce that. Area^4 predicted 6.29, MEASURED 4.486, 29% low, against
residuals of 4-9% on every earlier point.

🔑 **Why A^4 looked so good first:** while both exponents sit near 3.9,
L^3.9 h^3.9 = (Lh)^3.9 ~ A^4. Area was NEVER the governing variable — it was a
coincidence of the two exponents matching inside h = 2-3, and it dies as soon
as height leaves that band. [epoch comparisons are not measurements] applies to
laws too: a fit that works over a narrow span is not a mechanism.

⚠️ Physical reading, UNVERIFIED: the loop stops gaining flux once it reaches
out of the strong near-wall H field. That is a ceiling on HEIGHT but not on
azimuthal run. **Buy coupling with L, not h.**

✅ The coupling.beta = 1 design point (h=2, L~13.4 mm) is INSIDE the validated band and
is unaffected — both exponents are ~3.88 there.


✅ **THE CONTROL DECIDED IT, OUT OF SAMPLE.** h=2/L=14.2 (unwound 17.90 mm) and
h=3/L=12.24 (unwound 17.94 mm) are the SAME conductor length split differently.
Unwound length predicted coupling.beta = 3.78; area^4 predicted 1.42. **MEASURED 1.410.**
Area governs; unwound length does not. This is why L and h were made
independent — the two hypotheses were 2.7x apart and one case separated them.

🔴 **I GOT THIS WRONG TWICE FIRST, and both are worth keeping:**
1. Predicted coupling.beta ∝ A² (textbook magnetic loop, flux ∝ area, coupling.beta ∝ flux²) —
   predicted 1.2 for the 21 mm² case, MEASURED 0.392.
2. Then fit L-only and h-only exponents from 2-point pairs (3.2 and 4.2),
   concluded "not a function of area at all, coupling.beta ∝ L^3.2 h^4.2". **REFUTED by
   the control**, which lands on the single-variable area^4 curve. Those pair
   exponents were local curvature in 2-point fits, not real anisotropy.
⚠️ A^4 is DOUBLE the textbook exponent and is so far EMPIRICAL ONLY — no
mechanism. Do not extrapolate outside 21-37 mm² on it.

🔑 **DESIGN POINT: coupling.beta = 1 at A ~ 26.8 mm^2** — at h=2, L ~ 13.38 mm;
at h=3, L ~ 8.92 mm. VSWR = 1. Interpolated on the A^4 fit, NOT measured;
the bracket around it IS measured (0.699 at 25, 1.410 at 29).

**Rectangular barrel 13x6 on `h3-aspect-02` was coupling.beta 36.8 / VSWR ~37.**
User on the first azimuthal point: *"Already at that VSWR, it's workable."*

### ⏳ OPEN — h=4 row, and the 9 strip cases

### ⏳ OPEN — does coupling.beta reach 1, and what sets it

18-case grid launched, 1 complete, host reclaimed at case 2 of 18.
Grid: L in {10.2, 12.24, 14.2} mm x h in {2,3,4} mm x {1 mm wire, 5x1 strip}.
L and h are INDEPENDENT (unwound = L + 2h - gap), so the L+2h = 18.24 diagonal
is an internal control on whether unwound length alone predicts Q_ext.

🔎 **PREDICTION, UNTESTED:** if coupling.beta scales as loop area squared, h=2/L=10.2 at
21 mm² against this 37 mm² gives coupling.beta ~ 3.78 x (21/37)² ~ 1.2, i.e. near
critical. That case was solving when the host died. It is a sharp, falsifiable
number — record what it actually returns, do not quietly drop it.

⚠️ **A dead spot on a SATURDAY is a first** — every prior reclamation was a
weekday. Do not assume weekend capacity is safe.

---

### 🔎 QUEUED — THE AZIMUTHAL LOOP, and the question is VSWR (2026-08-28)

**User: *"the other loop option: one that runs azimuthally along the wall at the
cavity equator ... My main interest in the other loop shape is if/how it manages
VSWR."*** ⚠️ Framed on VSWR deliberately — my first analysis emphasised mode
perturbation, which is not the question.

✅ **PRIOR ART: NONE.** No azimuthal / wall-following / equatorial loop appears in
`KNOWN`, `PLAN`, `NEXT`, `CONVENTIONS`, `HYPOTHESES` or `OPTIMIZER`. Only two
mounts have ever been meshed — cap and barrel.

### 🔴 THE NULL HYPOTHESIS IS "NO VSWR BENEFIT", AND IT IS STRONG

VSWR is set by coupling.beta = Q₀/Q_ext. **Q_ext is cold and geometric; Q₀ swings ~400×
cold→loaded.** So a topology can only move VSWR through Q_ext.

🔑 **Both topologies are the SAME optimisation** — a rectangle *closed through the
wall*, conductor on three sides, the wall closing the fourth for free:

| conductor 38 mm | max area | at |
|---|---:|---|
| radial (current) | 180.5 mm² | ld = 9.5 |
| azimuthal | **191.4 mm²** | h = 9.5 |

**6 %**, all of it the outer arc being longer than the inner. And the area sits
over the same J₀ range (r/a 0.875–1.0 vs 0.892–1.0). Same flux, same Q_ext, same
VSWR. **Against Q_ext moving 5.6× across the ld sweep, 6 % is nothing.**

### 🔑 THE ONE MECHANISM THAT COULD BREAK THE NULL — image loading

A conductor running **parallel and close to** the wall is image-loaded: its image
current largely cancels its own, cutting self-inductance and changing its
effective electrical length. A radial leg poking into the volume is not.
**Since wavelength/4 governs Q_ext (KNOWN.md § MEASURED), moving the effective length
moves the resonance — and Q_ext with it.**

> **The measurement:** Q_ext vs conductor length for the azimuthal loop, plotted
> against the radial curve already measured — **1,325 / 359 / 1,135 / 2,024 at
> L/(wavelength/4) = 0.82 / 1.02 / 1.22 / 1.41.**
>
> 🔴 **F1 — if azimuthal Q_ext falls on the SAME curve vs conductor length,**
> image loading is negligible, the topology is a MECHANICAL choice and not an
> electrical one, **VSWR is unchanged, and the decision goes to buildability.**
> 🔴 **F2 — if it falls on a DIFFERENT curve,** the wavelength/4 point has moved and there
> is a new axis: the same Q_ext at a different physical size, which is exactly
> what the tolerance problem wants (d ln Q_ext / d ln L ≈ 4–6.5 means ±0.37 mm
> is ±5 % in Q_ext).

⚠️ **What NOT to spend the run on.** Whether it perturbs TE011 less — the arc
runs *along* the wall current (K = H_z φ̂) the way the groove does, while radial
legs cross it — is a real and testable side-effect, but it is NOT the question.
Record Q₀ and purity because they come free; do not size the sweep for them.

### What it costs to build

A third branch in `geometry.py` beside cap and barrel. The arc is free —
`occ.addTorus` takes an angular extent — plus two radial legs and the existing
fuse/cut/port machinery. By analogy with the current design: **port gap in the
ARC** (the side parallel to the wall, as the crossbar is now), **series gap in a
radial leg**.
✅ **The 2026-08-27 loop-surface machinery carries over unchanged**: an arc at
z = 0 with circular cross-section still has z-extent exactly 2·lrw with centroid
at z = 0, so the copper attribute, the partition assertion and the leg probes all
work as-is.
🔴 **`geometry.py` is where this session's regression came from.** Same
discipline: `--dump-faces` first, tet-count A/B with the branch disabled, and the
partition assertion must pass before any solve.

### What item 7 still owes, in order

| | | blocked on |
|---|---|---|
| **1** | **Choose the target: minimax, coupling.beta = 1 loaded, or TWO LOOPS** | 🔴 **`../ignition-options/`** — the choice is theirs, not this programme's. 🔑 **Two loops (user, 2026-08-25) gives coupling.beta = 1 in BOTH states** and makes the choice moot; its cost is a second port in `geometry.py`, a switch, and an unmeasured mode perturbation |
| ~~2~~ | ✅ **DONE 2026-08-27 — series-gap E-field measured.** `fieldcheck`: **1.334 MV/m at 1 kW cold, limit 5.44, margin 4.08×** (ld 11, gap2 0.5). The precondition on gap widening is discharged | — |
| **3** | 🔑 **REFRAMED (A5) — the PORT gap is the tighter break and was NEVER probed.** 0.3 mm against the series gap's 0.5, and it carries the **drive**; the series gap had a probe and a margin, this had neither. ✅ `port_gap` probe added to `h3_loopq`, and `fieldcheck` now maps it to a limit. ⚠️ Its width is **TENTATIVE with no owner** — `values.get` REFUSED it until the call site said `allow_tentative`, so the margin is only as good as a number nobody chose. 🔑 It is also a **length trim**: 0.3 → 1.0 mm is −1.9 % in L ≈ **8–12 % in Q_ext** | nothing |
| ~~4~~ | 🔴 **RETIRED AS WRITTEN (A4) — "re-sweep AREA" cannot do what it says.** Area is **bounded by length**: with S = (L + gaps)/2, area ≤ S²/2, i.e. **area_max = (L + gaps)²/8**. The design's 176 mm² is **97.5 %** of the 180.5 mm² available at its own conductor length, so *"increase area"* and *"increase length"* are the same instruction and the length sweep already ran it. ✅ **The real independent axis is ASPECT RATIO at fixed L** — ld + lw constant changes the **radial/azimuthal split of the conductor** (how much links H_z), which is an orientation question, not an area one. Area along that line only spans 96–180 mm² and needs ld=16/lw=3 to move at all | nothing |
| 5 | Feed transition, support, material, cooling (7d.B) | **hardware design, not EM sweeps** |

⚠️ **Do not run another gap sweep before 1 and 2.** Widening further optimises
an objective that may be wrong, along an axis whose failure mode is unmeasured.

### 7d. 🔴 A BUILDABLE LOOP IS NOT THE SAME AS A LOW Q_ext — opened 2026-08-25

**User: *"I think we have more design to do on a buildable loop, beyond the VSWR
problem."*** ✅ Correct, and the gap is wider than it looks. Steps 1–2c have been
optimising **one number**. The loop as a physical object is barely specified.

#### A. Dimensions with NO provenance — and everything measured sits on them

| | value | status |
|---|---|---|
| `loop.wire_r.mm` | 1.0 | 🔴 **TENTATIVE** — a `geometry.py` default, never chosen |
| `loop.gap.mm` (PORT gap) | 0.3 | 🔴 **TENTATIVE** — same |
| `loop.size.mm` | 11 × 8 = 176 mm² | ⚠️ swept on the **CAP** at N=1; item 7 already records that it **does not transfer** to the barrel |

🔑 The store refuses these without `allow_tentative=True`, and `e0k2_anchor` has
to say so at the call site — so the lack of provenance is visible, not hidden.
**But Q_ext = 720 was measured on top of all three.**

#### B. Not in the model at all

- 🔴 **THE COAX TRANSITION DOES NOT EXIST.** `geometry.py` puts a **lumped port
  on an internal face** — its own comment says *"no coax transition needed"*,
  which is true of the SOLVER and false of the hardware. There is no connector,
  no dielectric bead, no wall penetration. A real feed adds reactance and its
  own discontinuity, and **Q_ext is measured at that face.**
- 🔴 **MECHANICAL SUPPORT.** A 0.3 mm port gap and a 0.75 mm series gap must be
  held rigid in a cantilevered 1 mm wire, 13 mm long. Nothing holds them. A
  dielectric bead in either gap **changes its capacitance**, which is the whole
  mechanism.
- 🔴 **LOOP MATERIAL IS UNSTATED.** The walls are declared (aluminium 6061,
  `wall.conductivity.s_per_m`). The loop is not — and at coupling.beta = 52 it carries the
  coupled current.

#### C. Failure modes never checked

- 🔴 **ARCING.** The series gap is a deliberate E-field concentrator at kW
  levels, and the **PORT gap at 0.3 mm is the tighter feature**. Neither has
  been checked against a breakdown limit. ✅ Answerable from solves already on
  disk — peak |E| in each gap.
- 🔴 **I²R heating** in a 1 mm conductor, and how it is removed.

#### D. 🔴 THE CAVITY'S OWN GAS ENVIRONMENT IS NOWHERE IN THE RECORD

Searched: no statement anywhere of whether the cavity volume is **air at
atmosphere, N₂-purged, sealed, or evacuated.** ⚠️ **This single unstated fact
DECIDES the arcing question** — Paschen breakdown over a sub-millimetre gap
differs by orders of magnitude between atmospheric air and vacuum, and vacuum
would raise multipactor instead. It is also the §7ab pattern again: a value
nobody chose, now load-bearing.

#### ✅ What is already answerable, and one answer

**Machining tolerance, DERIVED from the measured gap sweep** (Q_ext ∝ gap^−1.14
locally, 0.5 → 0.75 mm):

| gap tolerance | Q_ext | VSWR band |
|---|---:|---|
| ±0.02 mm | ±3.0 % | 6.7 – 7.1 |
| **±0.05 mm** | **±7.6 %** | **6.4 – 7.4** |
| ±0.10 mm | ±15.2 % | 5.9 – 7.9 |

✅ **The series gap is FORGIVING** — ±0.05 mm is routine machining and costs
nothing at VSWR 6.9. ⚠️ **The port gap is 0.3 mm and has never been swept**, so
its sensitivity is unknown and it is the tighter feature.

#### Sequencing

1. **Finish 2c** — bracket the Q_ext optimum (running).
2. **Arcing check** — peak |E| in both gaps from existing solves. No new solve.
   🔴 Blocked on D: state the cavity atmosphere first, or the limit is undefined.
3. **Port-gap sweep** — the untested tentative value, and the tighter feature.
4. **Step 3 (already queued)** — re-sweep AREA on the barrel; 176 mm² was a cap
   result and does not transfer.
5. Feed transition, support, material, cooling — **hardware design, not EM
   sweeps**, and the point at which this stops being a `resonance` question.

### 7. 🔴 DESIGN the coupling loop — the question we never asked

**coupling.beta is a DESIGN OUTPUT, not an observation** (`CONVENTIONS.md` §7am). Asking
*"what Q_ext do we WANT?"* gives, from numbers already in the record:

| state | Q₀ | Q_ext wanted | built 9,231 is |
|---|---:|---:|---|
| COLD (ignite) | 43,422 | **43,422** | 4.7× too LOW |
| LOADED @ 7.9e18 | 109 | **109** | **85× too HIGH** |

🔴 **The two states want couplers ~400× apart — no FIXED loop meets both.**
🔑 **Three of the loop's five axes are ALREADY pinned at maximum coupling**
(cap radius = J₁ peak, orientation normal, area = the sweep's Q_ext minimum).
⚠️ **These Q₀ figures are INTERPOLATED and are being re-measured now** (item 8);
the ratios above will shift when the anchor points land.

🔴 **REVISED after reading `geometry.py` — my first version of this item was
wrong twice.** (Checking buildability before writing the rig is what caught it.)

- 🔴 **TURNS IS NOT BUILDABLE.** There is no turns/helix parameter. **New OCC
  geometry, not a rig.** Deferred.
- 🔑 **THERE IS A THIRD AXIS I HAD RULED OUT, AND IT IS THE BIG ONE:** the
  **SERIES CAPACITOR** (`loop_gap2` + `loop_flange_r`), already implemented.
  `geometry.py:443–451` computes **0.196 pF cancels the loop's 332 Ω
  self-reactance, ~45× coupled power, Q_ext 14,442 → ~320.** Against our 9,231
  that lands near **205** — the same order as the **109** coupling.beta = 1 needs.
  ⚠️ **CALCULATED, NEVER SIMULATED.** One attempt failed (0.056 pF, gap too
  wide, |Γ| 0.568 → 0.904 — *worse*); **the fix — flange AREA, r ≈ 1.9 mm — was
  diagnosed and implemented but never tested.**

**The rig — eigen `port_bc` pairs as in `h3_loopq`, ONE CHANGE PER STEP:**
1. **Cap → barrel mount**, single turn, same 176 mm², **no capacitor.**
   Isolates mount. ⚠️ Required first because **`--loop-gap2` is REFUSED with
   `--loop-cap`**, so the capacitor cannot be tested on the current loop.
2. **Add the series gap on the barrel loop**, `loop_gap2` swept, `loop_flange_r`
   at and around 1.9 mm. **This is the 45× test.**
3. Only then re-sweep area around whatever wins — the 176 mm² optimum was found
   at N=1 **on the cap** and does not transfer.

🔑 **AND IT IS THE ONLY LEVER ON THE TUNER'S THERMAL WALL.** Load current goes
as **√VSWR**, so VSWR 79 → 20 takes **39.7 A → 20.0 A** — from 4.4× short of the
best microwave PIN die to **2.2×**. A phase detector removes the coupling.beta↔1/coupling.beta ambiguity
but **removes no current** (`../control-loop/SOURCE.md` § DOES THE DETECTOR
RETIRE THE TUNER). **Item 7 is upstream of the whole magnitude-tuning problem.**

✅ **Falsifier, restated:** if step 2 does not move Q_ext by ≥4×, the loop family
IS exhausted and `../control-loop/`'s requirement 1 is real. 🔑 **But it is no
longer reasonable to ASSUME that** — a 45× mechanism sat unused in the builder
while this programme called the coupling a fixed property.

✅ **Falsifier:** if neither axis moves Q_ext by ≥4×, **the loop family is
genuinely exhausted** and `../control-loop/`'s requirement 1 is real. **That is
a result either way**, and it is currently assumed rather than measured.
⚠️ Do not open magnitude-tuner design before this runs.

### 5. ⚠️ PLAN E3 — RAN, 3 OF 5 LANDED, CLOSURE STILL UNANSWERED

✅ **RAN 2026-08-24, EXIT=0.** B_wall 808 s · D_dielectric 403 s ·
E_vac_torch 1140 s. 🔴 **A_all and C_plasma timed out at 2700 s** on the
sapphire+plasma ε-contrast (+11.6 beside −30.09) — **a failure the record had
already documented** (§7an, and now a PRIOR ART row).

🔴 **The rig's own verdict:** *"CLOSURE CANNOT BE TESTED — missing
['A_all', 'C_plasma']. E3 is UNANSWERED; every eta in the record stays
unfalsified."*

🔑 **DO NOT simply relaunch A and C.** They would run at 1e20, which is a
**different regime** (δ/shell 0.30, plasma shields) from the anchored operating
point (δ/shell 1.06, transparent). **Do item 8 first**, then re-test whether
sapphire+plasma converges at the anchor, where the span is **+11.6/−1.46**
rather than +11.6/−30.09 — the contrast mechanism predicts it should.

**After a spot reclamation:** launch `c7a.8xlarge` **in the volume's AZ** (EBS is
AZ-scoped), attach, set the address in `ops/env.sh`, then
`NOSYNC=1 ops/go ops/mount.sh`.
⚠️ `mount.sh` also checks pyflakes is in `/opt/amip/envs/emsim` — **not** the
root filesystem, which every reclamation wipes.

**What it will test:**

**η_total = η_plasma + η_wall + η_dielectric must close within a few %, or only
η_total may be quoted.**

🔑 **It is the declared falsifier for EVERY η in the record**, and it has never
been run. Today produced a corrected η column (0.986–0.998 over n_e 1e18–1e20)
and nothing has tested whether the loss budget adds up.
✅ **Now is the right time**: η is referenced to a measured design-cavity Q₀
(43,523), the coupling branch is resolved, and n_e is anchored — so E3 would
test the right budget rather than one built on a wrong regime.
⚠️ **Needs per-region energy bins**, which `eigen_cfg` already emits (one Energy
index per volume). The plumbing exists.

🔑 **METHOD:** one loss channel at a time on the SAME mesh — A all on, B wall
only, C plasma only, D dielectric only — then test
**1/Q_all = 1/Q_wall + 1/Q_plasma + 1/Q_diel**. That identity is exact IF the
field is the same in all four; **it fails when a channel is strong enough to
redistribute the field, which is exactly when "η_plasma" stops being a real
quantity.** So it tests whether the decomposition EXISTS, not arithmetic.
⚠️ **Runs at ne = 1e20, the STRONGEST test, not the operating point** — the
plasma is ~275× the wall loss there. It is also the only convergent density:
with the corrected ν_m the anchored 7.9e18 sits at PI₁ = 2.46, inside eigen's
untested gap, and 3e18 is where eigen is known to FAIL.

🔴 **AND IT CARRIES A SECOND TEST, from a defect found while writing it:**
**five rigs mesh the torch as VACUUM** when the design is sapphire ε = 11.6
(see `KNOWN.md`). Case E re-meshes with the vacuum torch so the frequency shift
is **measured, not inferred** — expected order −10 MHz. If confirmed, **every
band margin in the record is conservative by that amount.**

### 6. ⏸️ H4 — ignition
Parked. ⚠️ **"No mode cold-ignites" is UN-ANCHORED** — its source rigs were
groove-free and are discarded. Route 3 (saline as an ignition baseline) is
recorded in `PLAN.md`'s *Parked* section and does not spawn runs.
🔴 **Ignition DYNAMICS have never been measured or modelled anywhere in this
programme.** Everything is steady-state. That gap blocks the tuner's SPEED
requirement in `../control-loop/`.

---

## SIBLING PROGRAMMES

| | |
|---|---|
| **`../control-loop/`** | LDMOS, matching, control. ⏸️ **PARKED** — n_e anchored (VSWR ~100:1, ~45 A, ~2.2 kV, ~960 W dump), but ⚠️ **only ONE upstream lever is spent**: the loop family was never chosen, and 4.2× in Q_ext would move magnitude tuning from impossible to off-the-shelf. **Do not open tuner design before that is answered** |
| **`../spectroscopy/`** | Why any of it exists. ✅ Supplied the n_e anchor. 🔴 Top open item: **is LTE fair?** Non-LTE puts n_e ABOVE Saha — asymmetric, and it pushes toward the VSWR peak |

---

## STANDING REQUIREMENTS FOR ANY NEW RIG

- **Emit MODE PURITY** from every eigen solve (above).
- **Emit PRIORS, not just verdicts** — the value AND its uncertainty, the
  evaluation outcome, the cost, and which variables were held fixed and at what.
  `OPTIMIZER.md` is the consumer.
- **`eigen_cfg` now REFUSES** a looped mesh without an explicit `port_bc`
  (GATE 4) and a mesh the sidecar does not describe (GATE 5). Neither is
  optional; both cost a launch to learn.

### 🔧 AFTER THE AZIMUTHAL GRID — two resume inefficiencies (2026-08-30)

Both seen recovering `h3-azim-01` from the Saturday reclamation. Neither is
wrong, both waste time on every resume:

1. **Resume is per-CASE, not per-solve.** Case 2's `pec` had completed (it was
   the newest entry in postpro) but its `lumped` had not, so the whole case
   re-ran and a ~10 min pec was recomputed. Key the resume on the solve, not
   the case.
2. **The mesh-retry ladder is not memoised.** Case 2 needed size-factor 1.42
   and 7 chords. The winning mesh is cached, but the rig re-walks the ladder
   from the default and FAILED attempts are not cached, so it repeats the
   failures before reaching the cached winner. Record the winning
   `(size_factor, chords)` per case in the result and try it FIRST on resume.

⚠️ Not done during the run: the rig shells out to `geometry.py` per case and
editing it mid-run is what cost 6 of 16 grid points. See [frozen is not removed].

### ⚠️ EIGEN CANNOT ANSWER THE IMPEDANCE QUESTION (2026-08-30)

**User: *"Can we even test impedance with PEC?"*** — the loop is NOT PEC (the
A-queue removed it): wall attr 90 = 3.5e7 aluminium, loop attr 92 = 5.8e7
copper, port attr 91 = 50 ohm LumpedPort. Conductor loss IS modelled.

🔴 **But the limit is the SOLVER, not the material.** An eigen solve with a
lumped port returns Q_ext — a coupling MAGNITUDE. There is no complex Z in that
output. R + jX against 50 ohm, and whether the loop's reactance cancels or adds,
has no representation in it.

- ✅ the 6 strip cases CAN answer: does cross-section change coupling strength,
  and does it shift the prefactor of the coupling.beta ∝ L^3.88 law
- 🔴 they CANNOT answer: does a 5x1 strip MATCH 50 ohm better than a 1 mm wire

Same point from the other side: KNOWN records that **|S11| cannot distinguish
coupling.beta from 1/coupling.beta**, resolved by `e0k2_anchor.branch_from_phase`. Magnitude is
not enough; PHASE carries the impedance information.

### 🔴 REFUTED-AND-REPLACED — a strip changes the EXPONENT, not a prefactor (2026-08-30)

Azimuthal, h = 2, grooved, slug `h3-azim-01` stamp `71364f1e`. Same h, same
arc, same enclosed area to the conductor centreline — only the cross-section
differs (1 mm round wire vs 5x1 mm strip, wide face parallel to the wall):

    L        wire coupling.beta   strip coupling.beta   ratio
    10.2      0.392       0.129       3.04
    12.24     0.699       0.229       3.05

Predicted the second from the first at a constant 3.04x: 191,000 vs MEASURED
Q_ext 190,750 — **0.1%**. So the cross-section factor is SEPARABLE from the
geometry: it moves the PREFACTOR and leaves the L^3.88 exponent untouched.

🔴🔴 **THE THIRD POINT REFUTED ALL OF THAT, ONE CASE LATER.**

    L        wire coupling.beta   strip coupling.beta   ratio
    10.2      0.392       0.129       3.04
    12.24     0.699       0.229       3.05
    14.2      1.410       0.370       3.81   <-- predicted 0.464, 20% off

**The ratio is NOT constant in L.** The two conductors have DIFFERENT
EXPONENTS, measured over the same 10.2 -> 14.2 span at h = 2:

    1 mm round wire ... coupling.beta ∝ L^3.87
    5x1 mm strip ...... coupling.beta ∝ L^3.19

Cross-section changes the SHAPE of the law, not a multiplier on it. The 0.1%
"confirmation" at L=12.24 was two points agreeing on a line, which any two
points do.

🔑 **THE SAME ERROR TWICE, ONE LEVEL APART.** The user objected that one WIDTH
cannot establish a width response. It then turned out two LENGTHS could not
establish the L response either — a constant extrapolated from the minimum
number of points that can produce one. [epoch comparisons are not measurements]
has a sibling: **a fit through N points does not survive point N+1 unless N was
chosen to test it, not to produce it.**

🔴 **SCOPE — ONE WIDTH, AND NOW NOT EVEN A CLEAN RATIO.** *User: "Independent at 5mm width. We would
have to try different widths to ascertain 'the strip divides beta by 3.04 at
every size'."* I called this a "3x knob on coupling", which claims a RESPONSE
CURVE from a single sampled point. Two conductors give ONE ratio.

    ✅ established: a 5x1 strip couples WEAKER than a 1 mm wire at every
       (h, L) measured — 3.0x to 3.8x — and the mode stays clean (P >= 0.9999)
    ✅ established: the two cross-sections obey DIFFERENT L-exponents,
       3.87 (wire) vs 3.19 (strip), over 10.2-14.2 mm at h = 2
    🔴 NOT established: any constant ratio; how either exponent varies with
       WIDTH; that the strip exponent is stable outside this span; that a
       thicker ROUND wire moves coupling the other way at all

➡️ To earn the knob, sweep WIDTH at fixed h and L — e.g. 2x1, 3x1, 5x1, 8x1
against the 1 mm wire, one geometry, one variable. Cheap: h=2 cases solve fast
and the arcs {10.2, 12.24, 14.2} are known to mesh.

### 🔴 CORRECTION — THE MINIMAX IS NOT THE TARGET (2026-08-30)

**User: *"The minimax loop is not an accepted solution, so it's not appropriate
to make claims like 'we need more coupling to reach Q_ext ~ 2,100'. We've found
coupling.beta = 1 unloaded, we're looking for coupling.beta = 1 loaded."***

🔑 I quoted the minimax as the objective. It is not one — and KNOWN marks that
very line **"Design implication, NOT a decision ... Do not adopt a leg depth
from this line."** I adopted a target from a line that says not to. The minimax
is what a SINGLE fixed coupler is reduced to (VSWR ~20 in both states); the
DUAL-LOOP plan exists precisely so that compromise is not needed.

**The objective is coupling.beta = 1 in EACH state, with a coupler for each:**

    coupling.beta = 1 COLD   ✅ bracketed — h=2, L ~ 13.4 mm (Q_ext ~ Q0cold ~ 43,700)
    coupling.beta = 1 LOADED ⏳ OPEN — needs Q_ext ~ Q0loaded, and Q0loaded is UNMEASURED

⚠️ **The scale of the loaded ask is not small.** If Q0loaded is order 100-200,
coupling.beta = 1 loaded wants Q_ext of the same order — **30-60x below the smallest
Q_ext this programme has measured (6,362)**. Running coupling.beta ∝ L^3.88 backwards
puts that near L ~ 37 mm at h=3, area ~111 mm², far outside the validated
10.2-14.2 band and into the range where **F2** asks whether purity degrades with
loop area. Whether an azimuthal loop can get there without hybridising TE011 is
GENUINELY OPEN. Do not assume the extrapolation holds — it already broke once,
at h=4.

🔑 **Measure Q0loaded FIRST.** Every number above is conditional on it.

➡️ **Carry the impedance question into the DRIVEN rig**, which is needed for
loaded work anyway (PRIOR ART: eigen with sapphire + plasma does not converge).

### ✅ RE-MEASURED WITH A CORRECT PORT — the strip sweep (2026-08-31)

Slug `h3-azimwidth-01` stamp `c1dffc3d`. ALL at **standoff 2.0 mm** (the WALL
GAP, held fixed) and a port face of **0.9 x the conductor's HALF-EXTENT** — the
same face-to-conductor ratio for every conductor, which is what the earlier data
did not have.

    conductor      10.2    12.24    14.2      L-exponent
    wire (ref)    1.897    3.779   6.872       3.89
    2x1           1.262    2.215   3.654       3.21
    3x1             -      2.260   3.798          -
    5x1           1.180    2.156   3.840       3.57
    8x1           1.119    2.205   3.911       3.78
    5x0.5         1.170    1.948   2.965       2.81
    5x0.25        1.662      -       -            -

🔑 **WIRE vs STRIP: 1.6-1.8x, not 7-8x.** At matched wall gap AND matched port
ratio the round wire couples 1.61x (arc 10.2) to 1.79x (arc 14.2) more than a
5x1 strip. Every larger figure this programme reported — 3.04, 4.13, 7.19, 7.89,
8.54 — was the port face, not the conductor.

🔑 **CROSS-SECTION ROTATES THE CURVE, IT DOES NOT SHIFT IT.** The L-exponent
rises monotonically with conductor size in BOTH dimensions:

    width  2 -> 5 -> 8 mm  :  3.21 -> 3.57 -> 3.78
    thick  0.5 -> 1.0 mm   :  2.81 -> 3.57

At any single arc the widths differ by only ~5%, which is near the mesh-to-mesh
reproducibility, and the ordering even flips between arcs — because the curves
CROSS near arc 12. ⚠️ A single-arc comparison cannot see this. Fit exponents.

🔴 **THE 5x0.25 SERIES IS UNUSABLE — 1 of 3 points.** arc 12.24 TIMED OUT at
7200 s; arc 14.2's pec continuation BROKE. The one point that landed (1.662)
also breaks the thickness trend, sitting ABOVE both thicker strips rather than
below. ⚠️ Its port face is ~0.225 mm across a ~0.12 mm gap element — two
elements — which is the regime `e0k2_anchor` records a face floating in. **Do
not quote 5x0.25.** If thin strips matter, refine the gap mesh first.

⚠️ Also lost: 3x1 arc 10.2, pec continuation BROKE (nearest converged mode
+147.5 MHz, the 2.598-2.607 GHz cluster). 15 of 18 cases returned results; all
three failures were REFUSALS, not mislabelled modes.

🔑 **THE SOLVER STRUGGLES NEAREST coupling.beta = 1** — the L=13.0/13.4 wire cases, and
both 5x0.25 failures. That is the most design-relevant point on the curve, and
it is an argument for the DRIVEN solver on any near-critical geometry.

### 🔴🔴 SUPERSEDED — THE PORT FACE DOMINATES Q_ext (2026-08-30)

Strip 5x1, standoff 2.0, arc 12.24 — IDENTICAL geometry, identical mesh
settings, identical solver settings. ONLY the port-face half-width changed:

    pw    face      Q_L      implied Q_ext   implied coupling.beta
    0.9   1.80 mm   29,465      ~90,000         0.49
    0.45  0.90 mm   13,826      ~20,200         2.17

🔴 **HALVING THE FACE CHANGES coupling.beta BY 4.5x.** A well-posed lumped port is
INSENSITIVE to this. Q_ext is therefore set by an arbitrary modelling choice,
not by the loop.

**WHAT THIS INVALIDATES — every azimuthal COUPLING number:**
  - coupling.beta ∝ A^4.07 and the "critical coupling at A ~ 26.7 mm^2" bracket
  - the L-exponents (wire 3.87-3.89, strip 3.19-3.37)
  - every wire-vs-strip ratio (3.0x, 4.1x, 7.2-8.5x matched-standoff)
  - the 18-case `h3-azimwidth-01` sweep, and the 9 strip cases of `71364f1e`
  - "VSWR 1.09 at h=3 L=12.24 strip", "coupling.beta = 1 bracketed"

⚠️ **AND THE TWO FAMILIES SIT AT DIFFERENT POINTS ON THIS CURVE.** `_rc_p` is
the wire's RADIUS but the strip's FULL thickness, so at the same factor the
wire's face is INSET (0.9x its half-extent) and every strip's OVERSHOOTS
(1.8x). Wire-vs-strip is thus not merely uncertain — it is a comparison across
a steep artefact.

✅ **WHAT SURVIVES — everything from the `pec` solves**, where the gap is
SHORTED and the face plays no part: Q0 (43,378-44,083 across the whole grid),
mode purity (P >= 0.9999 throughout), f0, the 0.75% Q0 cost of an azimuthal
loop vs 6-12% for the rectangular one, and the groove behaviour. The MODE work
is intact. The COUPLING work is not.

🔑 **THE FIX IS PHYSICAL, NOT NUMERICAL.** The face represents where a feed
actually attaches, so its size is a DESIGN INPUT. It must come from the real
connector cross-section, be declared in `baselines.json` like any other
canonical value, and be held CONSTANT across every conductor — then all
comparisons sit at one feed. `0.9 * _rc_p` is a factor times the conductor,
which is why it silently differed between families.

⚠️ Also open, and NOT the same question: the face is a flat rectangle in the
**z = 0 plane** (radial x tangential). The conductor's cross-section at the gap
is (radial x AXIAL). For a 5 mm-tall strip the face spans none of the axial
extent. Whether that is right depends on how Palace integrates the lumped
element and is NOT resolvable by argument — measure it.

### 🔴 SUPERSEDED — the original suspicion, kept because it was right for the wrong reason

Found 2026-08-30 while checking probe readings. In `geometry.py`:

    _rc_p = (_strip[1] if _strip else lrw)
    _pw   = 0.9 * _rc_p

🔴 **THE TWO BRANCHES DO NOT MEAN THE SAME THING.** `lrw` is a wire RADIUS (a
half-extent), so a wire gets a face inset to 90% of its conductor — the intent.
`_strip[1]` is a strip's FULL radial thickness, so a 5x1 strip gets a face of
+-0.9 mm against a conductor of +-0.5 mm: it OVERSHOOTS by 0.4 mm per side.

⚠️ Separately, the face is a flat rectangle in the **z = 0 plane** spanning
radial x tangential. That was validated on a ROUND WIRE. A 5 mm-tall strip
extends +-2.5 mm in z and the face does not.

**Consequence: every strip coupling.beta may carry a systematic port error** — the nine
cases of `h3-azim-01` stamp `71364f1e` (coupling.beta 0.129-1.664) and the 18 of
`h3-azimwidth-01`. They are SELF-CONSISTENT and the mode is clean
(P >= 0.9999), which is why nothing flagged it.

✅ **DECISIVE TEST, and it is cheap.** `AMIP_PORT_PW` is already a hashed
parameter. **A correct port gives Q_ext INSENSITIVE to reasonable changes in
face width.** Sweep it on ONE strip case — e.g. 0.4 / 0.6 / 0.9 — at fixed
geometry:
  - Q_ext flat  -> the face is fine, strip results stand
  - Q_ext moves -> the strip betas need re-deriving, and the wire/strip ratio
    is an instrument artefact rather than a cross-section effect

🔑 Do this BEFORE quoting any wire-vs-strip ratio, including the
matched-standoff series A now running — which was specifically built to make
that ratio meaningful.

### 🔴 LOADED, FIRST ATTEMPT — Q0loaded STILL UNMEASURED (2026-08-31)

Slug `h3-azimload-01` stamp `b593113a`, driven, azimuthal wire loop at standoff
2.0 / arc 12.24 (the reference coupler). ne = 0 then 7.9e18.

✅ **WHAT LANDED, and it does not depend on the coupling model:**

    cold    f0 = 2.450325 GHz   dip -16.29 dB   (selected by CONTINUATION)
    loaded  f0 = 2.455755 GHz   dip  -4.13 dB
    LOADED PULL = +5.43 MHz

⚠️ Compare the DISCARDED groove-free value of +31.6 MHz — this is 6x smaller.
Continuation also correctly rejected a DEEPER feature at 2.6048 GHz (-22.10 dB)
as not-the-mode, which is exactly the trap `h3_sapphire` fell into.

🔴 **THE COLD CROSS-CHECK FAILED — and it was there to catch this.**

    driven cold, dip -16.29 dB -> coupling.beta = 0.734 (under) or 1.362 (over)
    eigen  cold, SAME mesh     -> coupling.beta = 3.779
    eigen's coupling.beta would give a -4.71 dB dip; driven measured -16.29 dB

🔴🔴 **CORRECTED — THE TWO RUNS ARE DIFFERENT CAVITIES, and the solvers are
not in disagreement at all.** From the mesh sidecars:

    eigen  (h3_loopq azim grid) : torch_material = [9.39, 3.5e-05]  SAPPHIRE
    driven (h3_azimload cold)   : torch_material = [1.0,  3.5e-05]  VACUUM

That is the whole 11 MHz f0 offset (2.4394 vs 2.4503) and a different field at
the loop, hence a different coupling.beta. Each rig is right for its own purpose — the
driven rig meshes a VACUUM torch for its cold reference BY DESIGN — but the two
numbers were never comparable. ⚠️ I wrote "same geometry, same mesh, same port
face" here without checking the sidecars, and then built a port-face hypothesis
on top of it. [epoch comparisons are not measurements], again, and this time I
had the artefacts on disk that would have shown it in one command.

✅ The loop itself was built correctly in BOTH: loop_mount azim, standoff 2.0,
centreline 3.0, port_face 1.80 mm. (The driven mesh tag says `ld11` — that is
unused radial-loop defaults leaking into the NAME, not the geometry.)

🔴 **AND SO THE OBVIOUS SHORTCUT IS ALSO VOID.** Q0loaded = coupling.beta x Q_ext (with
Q_ext taken as cold and geometric) gives ~2,700 — but it inherits coupling.beta from the
method that just failed validation, and Q_ext from the port face that is not
physically anchored. Do NOT quote 2,700.

🔴 **THE PORT-FACE HYPOTHESIS WAS WRONG HERE** (it is still a real effect on
Q_ext — 4.5x across the overshoot boundary — but both runs used the SAME face,
so it cannot produce a difference BETWEEN them).

⚠️ **AND THE PRESCRIPTION IT CAME WITH WAS WRONG TOO.** "Pin the face to the
real connector cross-section and declare it in baselines.json" treats a
MODELLING artefact as a design parameter. A lumped port is a surface impedance
Z_s = R*W/L over the face; what matters is how much of the conductor's actual
current it intercepts. In a real build the coupling is set by the loop's FLUX
LINKAGE, not by the connector aperture. ➡️ The face should BE the conductor's
cross-section at the gap, and the right check is CONVERGENCE toward that — not
a connector dimension.

➡️ **The real next step:** run the eigen azimuthal case on a VACUUM-torch
cavity so eigen and driven can be compared like with like. Until then there is
no evidence the two solvers disagree.

⚠️ Why the width failed, for whoever retries: the loaded dip is only 4.13 dB
deep, so the 3 dB points sit ~1.1 dB above a nearly flat baseline, and the
high-side walk turned at 2.4652 GHz on competing structure. A shallow dip on a
sloping baseline cannot give a linewidth. Isolate the mode with a band centred
on it, or drive harder toward coupling.beta = 1 so the dip deepens.

✅ FIXED: `_report` KeyError'd on a fit with no `linewidth_mhz`, killing the
summary of a run whose result file held BOTH located dips. It now prints what
exists and dashes what does not.

### 🔴 THE FEED TOPOLOGY WAS NEVER CHOSEN (2026-08-31)

**User: *"Doesn't picking the adapter type seem premature at this point, when we
haven't established anything else about how the coupler enters the cavity, or
how it's connected to the cavity on the far side from the inlet?"*** — yes, and
asking for SMA/N-type was doubly wrong, because the same message called the
port face a modelling convenience. Both cannot be true.

**WHAT THE MODEL ACTUALLY BUILDS** (geometry.py, azimuthal mount):

    wall --leg--  quarter-arc --GAP--  quarter-arc  --leg-- wall
                                ^ port face, mid-arc at phi = 0

Both legs are galvanically joined to the wall; a 0.3 mm gap is cut at the
CENTRE of the arc and the port bridges it. Verified against the mesh: for the
2x1 strip at standoff 2.0 the port spans r 85.0545-85.9546 inside a conductor
at 85.0045-86.0045, 2 mm inside the wall at 88.0045.

🔴 **NOBODY CHOSE THIS.** It was inherited from the radial loop, where the gap
sits mid-crossbar for its own reasons. A coax-fed loop normally grounds the
outer conductor AT THE WALL PENETRATION, with the inner conductor forming the
loop — so the driven gap is at the ENTRY, not mid-arc.

🔴 **DOWNGRADED 2026-09-01 — I OVERSTATED THIS.** *User: "Why can't the coupler
simply enter through a hole? As opposed to specifying every detail about the
adapter."* Right: it is ONE geometric decision, not a shopping list.

✅ **THE MINIMAL REALISTIC FEED, and it needs no connector model:**
    coax OUTER grounds at a HOLE in the wall; INNER passes through and becomes
    one leg; the loop runs round; the FAR leg grounds to the wall. A lumped
    port across the hole still terminates in 50 ohm. Coax dimensions matter
    only if you later want the connector's own reactance.

🔑 **AND IT IS THE SAME CIRCUIT CLASS AS WHAT IS ALREADY BUILT** — a series-fed
loop returning through the wall. The only difference is WHERE around the loop
the source sits, and that is small:

    unwound loop = 17.94 mm = 0.147 wavelength = wavelength/6.8
    phase around the loop            = 53 deg
    mid-arc vs entry feed shifts it  = ~26 deg

**So the existing Q_ext numbers are NOT invalidated by this** — 26 deg is a
perturbation, not a different circuit. It was wrong to call this a blocker or
to rank it above the port face.

➡️ **Worth doing anyway, and cheap:** put the hole in, drive at the entry, and
compare Q_ext against the mid-arc model. That also puts the port REFERENCE
PLANE at the wall, which is where VSWR would actually be measured — a real gain
for the design deliverable, independent of how much the number moves.

### ✅ COLD ANCHORED / 🔴 EIGEN STALLS ON PLASMA — closed-ring azimuthal loop (2026-08-31)

**User: *"We're not trying to hit Beta = 1 loaded yet, so I don't think the
0.3mm gap should be there at this point."*** ✅ Right, and it dissolves the port
face, the feed topology and the coupling branch in one move. `port_bc="pec"`
SHORTS the gap, so the loop is electrically a CLOSED RING — a conductor the
mode must coexist with, nothing more. No new mesh needed: the driven run's own
meshes were reused.

✅ **COLD, closed ring, VACUUM torch, standoff 2.0 / arc 12.24 wire:**

    f = 2.381453  Q = 13,094
    f = 2.381793  Q = 13,107
    f = 2.450751  Q = 43,875   <- TE011
    f = 2.604939  Q = 20,994
    f = 2.607576  Q = 20,577

🔑 **AND IT VALIDATES DRIVEN AGAINST EIGEN AT LAST.** The driven sweep put its
cold dip at 2.450325 GHz on THIS SAME MESH — **0.43 MHz apart, 0.017%**. The
earlier apparent 3x disagreement was entirely the sapphire-vs-vacuum torch
mismatch. The two solvers agree on this cavity. The 2.6049/2.6076 pair is the
same competitor cluster driven saw at 2.6048.

🔴 **LOADED: EIGEN DOES NOT CONVERGE.** ne = 7.9e18, plasma attr 12 at
eps = -1.456, sigma = 2.1746 (the driven rig's own Drude values):

    PCG solver did NOT converge in 1000 iterations (avg. reduction 9.987e-01)
    Linear solver did not converge, norm(Ax-b)/norm(b) = 1.117e+00
    nconv = 0

🔴 **THIS DOES NOT EXTEND THE PRIOR ART — IT REPRODUCES IT, and I did not
search.** `NEXT.md` item **R4** already records it: *"h3_qext's anchor case
TIMED OUT WITH A VACUUM TORCH (159 PCG failures, 0 iterations) at eps = -1.46.
**eps-near-zero conditioning**, the prediction recorded before the run."* Same
eps (-1.456), same torch, same PCG stagnation. The diagnosis was already there,
and so was the fix it points to: **a PRECONDITIONER**, not a different torch and
not a different solver.
⚠️ `h3_driven`'s docstring says sapphire + plasma fails and *"neither ingredient
alone fails"* — R4 is the correction to that line, and it predates this run.
🔑 Second prior-art miss of the session, after the viewport. Both were in files
already open.

🔴 **AND A TRAP THAT ALMOST PASSED SILENTLY.** The first loaded attempt returned
eigenvalues IDENTICAL to cold to 6 figures — because `eigen_cfg` builds
materials from the MESH SIDECAR, which does NOT carry the plasma's Drude
permittivity (the RIG computes it from n_e). Every volume came out eps = 1.0,
so the "loaded" solve was a COLD solve. This is R101's exact failure, and the
guard that catches it lives in the RIG — bypassed by hand-rolling the solve.
✅ The re-run carries an explicit fail-closed check: refuse if ne > 0 and the
plasma attribute has eps = 1.0.

➡️ **THE PATH LEFT FOR Q0 LOADED.** Eigen stalls; driven cannot fit a linewidth
because the loaded dip is only 4.13 dB deep on a sloping baseline; and with the
ring SHORTED there is no port to drive at all. The remaining route is ENERGY
BALANCE from a driven solve: Q0 = omega * W_stored / P_dissipated, both of which
Palace can report per domain (`Domains.Postprocessing.Energy` is already wired
in h3_driven). That needs no linewidth and no port model.

### 🔑 Q_L BY ENERGY BALANCE — and TE011 IS EXTINGUISHED AT THE ANCHOR DENSITY (2026-09-01)

Computed from artefacts ALREADY on the volume — no new solve. Steady state on
resonance: the port delivers exactly what the materials dissipate, so

    Q_L = omega * W_stored / P_delivered      W = E_elec + E_mag (domain-E.csv)
                                              P = 0.5*Re{V I*}  (port-V/I.csv)

⚠️ This is Q_L, NOT Q0 — it includes the port. I mislabelled it first time.

✅ **COLD, and it closes the coupling question without any |S11| branch:**

    Q_L (driven, energy balance, port LIVE)   = 10,602   @ 2.450450
    Q0  (eigen, ring SHORTED, same mesh)      = 43,875   @ 2.450751
    ->  coupling.beta = Q0/Q_L - 1 = 3.14        Q_ext = Q0/coupling.beta = 13,977

🔑 coupling.beta from TWO INDEPENDENT SOLVES, not from a dip depth — so the branch
ambiguity that has dogged every driven number simply does not arise.
⚠️ The two use different port BCs (shorted vs 50 ohm) and their f0 differs by
300 kHz, so this coupling.beta is good to ~10%, not better.
🔴 Note the dip-depth method gave 0.734 or 1.362 for the same case. NEITHER is
3.14. **Dip depth is unreliable here; energy balance is not.**

🔴🔴 **LOADED AT ne = 7.9e18: TE011 IS GONE.** Every local maximum of stored
energy across 2.30-2.65 GHz:

    f=2.45760  W=2.620e-10 J  (0.149% of peak)  |S11| -4.13 dB   <- TE011
    f=2.60500  W=1.075e-07 J  ( 61%)            |S11| -21.67 dB
    f=2.60600  W=1.761e-07 J  (100%)            |S11| -3.01 dB

TE011's stored energy is **3,250x below its cold value** and its Q_L is **~3.6**.
|S11| sits near -4 dB across the WHOLE band: ~60% of the drive is absorbed at
every frequency. That is broadband absorption, not a resonance. The rig's
"-4.13 dB dip" is the top of a featureless hump.

🔑 **WHY, AND IT IS NOT A SOLVER ARTEFACT:**

🔴 **CORRECTED 2026-09-01 — I QUOTED THE WRONG THRESHOLD.** First written as
"106x over-dense" using the COLLISIONLESS critical density. That is a formula
outside its domain (cf. the Q_ext = 165 error). With nu = 6.5*omega this plasma
is COLLISION-DOMINATED and nu^2 beats omega^2 by 42x, so eps = 1 -
wp^2/(omega^2 + nu^2) stays near 1 far above n_c:

    collisionless n_c (wp = omega)   = 7.446e16 m^-3   <- NOT the threshold here
    COLLISIONAL threshold (eps = 0)  = 3.217e18 m^-3   <- the real one
    the programme's anchor           = 7.900e18 m^-3   = 2.5x over, NOT 106x

✅ The anchor IS over-dense — eps = -1.456 is negative and the mode really is
extinguished. Only the FACTOR was wrong, and it matters because it moves the
interesting density range by two orders.

    eps across density:  1e16 +0.997   3e17 +0.907   3e18 +0.067
                         7.4e16 +0.977  1e18 +0.689   7.9e18 -1.456

At 2.5x the collisional threshold the plasma is a lossy MIRROR: the field
reaches ~1.9 mm into 6.5 mm of plasma, the bore is excluded, and TE011 — whose
E_phi lives in the bore — cannot exist.

➡️ **CONSEQUENCE: "Q0 loaded for TE011" is ill-posed at this density.** There is
no mode to have a Q. The design question is not "how do I couple to a loaded
TE011" but "at what density does TE011 still exist", which is exactly what
`h3_loaded` was built to map: *"what plasma does TE011 sustain? A 2-D map, not
a point."*

➡️ **NEXT: sweep ne through 1e18-1e19**, where eps actually crosses zero.
⚠️ NOT 1e16-1e17 — that was the mis-derived range, and the sweep launched on
2026-09-01 (`h3-azimne-01`, stamp 4b8c220c) is mis-centred because of it: four
of its nine points sit below 1.5e17 where eps > 0.95 and nothing happens, and
those are the EXPENSIVE ones because driven cost scales with Q. It still
brackets the transition with 1e18 / 3e18 / 7.9e18.
Energy balance works on driven artefacts, needs no linewidth, no port branch
and no eigen convergence, so it runs where both other methods failed.


## 📋 PLAN FOR THE NEXT SESSION (written 2026-09-01, no instance up)

The 2026-09-01 spot died ~04:00 local, mid-sweep. `h3-azimne-01` never reached
its end-of-run fetch, so ITS RESULTS ARE ON THE EBS VOLUME AND NOT LOCAL.

### 1. RECOVER FIRST — before launching anything (~10 min)

    ops/env.sh -> new address
    NOSYNC=1 ops/go ops/mount.sh
    ops/go ops/fetch.sh
    cd /opt/amip/repo/experiments/resonance && python3 /tmp/parse.py ...   # or:
    grep -aE "^  --- ne|selected .* GHz" h3-azimne-01.log

Cold + ne = 1e16 / 3e16 / 7.4e16 had completed before it died; more may have.
**Extract Q_L for each completed density** with
`ops/oneoff/qL_energy_balance.py <postpro_dir> <f0_ghz>`. The number to watch
is stored energy as a FRACTION OF THE BAND PEAK: at 7.9e18 TE011 was 0.149%
(gone); a surviving mode should be tens of percent.

### 2. THEN the re-centred sweep — this is the real measurement

eps crosses zero at 3.22e18, so the transition is 1e18-1e19, NOT 1e16-1e17:

    ne=1.00e+18  eps=+0.6891
    ne=1.80e+18  eps=+0.4404
    ne=2.50e+18  eps=+0.2228
    ne=3.20e+18  eps=+0.0051
    ne=4.00e+18  eps=-0.2436
    ne=5.50e+18  eps=-0.7099
    ne=7.90e+18  eps=-1.4561
    ne=1.20e+19  eps=-2.7307

Eight points, all in the interesting band, and all CHEAPER than the ones the
mis-centred sweep spent its time on (driven cost scales with Q; these have low
Q). Reuse `baseline-h3-azimne-01.json` — change only `ne_grid`, and amend
provenance so the stamp moves.
⚠️ Cold (ne=0) MUST stay first and is mandatory: it is the continuation seed
and the rig hard-exits without it. It is also the expensive point, so a
reclamation during it loses the run.

### 3. WHAT THE ANSWER LOOKS LIKE

The density where TE011's stored-energy fraction collapses IS the design
constraint — it says what plasma this cavity can actually run. That is
`h3_loaded`'s original question ("what plasma does TE011 sustain? A 2-D map,
not a point"), and the 7.9e18 anchor silently assumed it away.

### 🔧 WORTH DOING, NOT BLOCKING — feed through a hole

The model drives a mid-arc gap with both legs grounded (inherited from the
radial loop). The buildable version is a HOLE in the wall: coax outer grounds
there, inner becomes one leg, far leg grounds. Same circuit class — a series-fed
loop returning through the wall — with the source moved ~26 deg around a
wavelength/6.8 loop. ⚠️ I first called this a blocker upstream of all coupling work;
that was wrong. It is a modest perturbation, worth measuring by building both
and comparing Q_ext, and it usefully puts the port reference plane at the wall
where VSWR is actually measured.

### ✅ INSTRUMENT STATUS, so nobody re-derives it

    eigen  + plasma        🔴 STALLS (PCG stagnation, nconv=0) even at eps_torch=1
    driven + 3 dB width    🔴 loaded dip 4.13 dB on a sloping baseline: unfittable
    driven + dip depth     🔴 gave coupling.beta 0.734/1.362 where the truth was 3.14
    driven + ENERGY BALANCE ✅ WORKS — Q_L = omega*W/P from artefacts it already writes
    eigen  port_bc=pec     ✅ WORKS for Q0 (loop shorted = closed ring), COLD only

### ✅✅ THE DENSITY SWEEP — TE011 HAS AN OPERATING POINT, AT ~3e16 NOT 7.9e18 (2026-09-01)

`h3-azimne-01` stamp `4b8c220c` completed ALL 9 densities before the 04:00 spot
death (it exited 1 on the V1/report step, but every postpro dir is on the
volume). Azimuthal wire loop, standoff 2.0 / arc 12.24, vacuum torch.
Q_L by ENERGY BALANCE — `ops/oneoff/qL_energy_balance.py`.

     n_e (m^-3)   eps      f0 (GHz)   W/W_peak     Q_L     |S11|
      0.00e+00  +1.000   2.450450   100.00%    10602   -4.29
      1.00e+16  +0.997   2.450400   100.00%     9678   -8.71
      3.00e+16  +0.991   2.450400   100.00%     6182   -8.47
      7.40e+16  +0.977   2.450400   100.00%     2964   -7.47
      1.50e+17  +0.953   2.450600    49.33%     1107   -4.65
      3.00e+17  +0.907   2.450600    18.62%      441   -4.88
      1.00e+18  +0.689   2.450800     2.41%       57   -4.41
      3.00e+18  +0.067   2.452200     0.39%        9   -4.17
      7.90e+18  -1.456   2.457600     0.15%        4   -4.13

🔴 **THE MECHANISM IS ABSORPTION, NOT CUTOFF — my "over-dense mirror" was
wrong.** Q_L is already down 3.6x at 7.4e16 and down to 57 at 1e18, where
eps = +0.689 and the plasma is comfortably UNDER-dense. sigma rises linearly
with n_e (0.0028 -> 2.175 S/m) and that is what kills the mode. Cutoff
(eps < 0) only arrives at 7.9e18, long after TE011 has gone.

🔑 **THE DESIGN NUMBER** — using the cold Q_ext = 13,977 as load-independent
(Q0 = 43,875 from eigen with the ring SHORTED, Q_L = 10,602 from driven energy
balance, same mesh):

     n_e       Q0_loaded  coupling.beta    P_in->cav  eta_plasma  OVERALL to plasma
     1.0e16      31465  2.2512      85.2%      28.3%       24.1%
     3.0e16      11085  0.7931      98.7%      74.8%       73.8%  <- OPTIMUM
     7.4e16       3762  0.2691      66.8%      91.4%       61.1%
     1.5e17       1202  0.0860      29.2%      97.3%       28.4%
     3.0e17        455  0.0326      12.2%      99.0%       12.1%
     7.9e18          4  0.0003       0.1%     100.0%        0.1%  <- THE ANCHOR

✅ **At n_e ~ 3e16 this loop puts 73.8% of INCIDENT power into the plasma at
VSWR 1.3.** At the programme's assumed anchor it puts in 0.1% — a factor of 700.

🔑 It is a genuine OPTIMUM, not a monotone: below it the plasma absorbs too
little of what enters (eta 28% at 1e16); above it the cavity reflects nearly
everything (12% enters at 3e17) because Q0 has collapsed far below Q_ext. The
peak sits where coupling.beta passes through 1.

⚠️ **THREE CAVEATS, none small:**
  1. Q_ext assumed LOAD-INDEPENDENT (geometric). The whole coupling.beta column rests on it.
  2. The plasma is a STATIC UNIFORM Drude annulus at r = 2-8.5 mm. This says
     what the CAVITY wants, not what a real discharge will do — that is
     `h3_loaded`'s map.
  3. The optimum is a property of THIS loop's Q_ext = 13,977. A stronger
     coupler moves it to higher density: matching at 3e17 needs Q_ext ~ 455,
     about 30x stronger than anything the azimuthal family has reached (the
     corrected sweep spanned Q_ext ~ 11,000-39,000).

➡️ **THE FORK.** Either operate near 3e16 with the coupler we have, or build a
~30x stronger coupler to reach 3e17. coupling.beta ∝ L^3.88 says that is L ~ 30 mm at
h = 2 — a 2.4x extrapolation beyond the validated 10.2-14.2 mm band, and larger
loops perturb the mode more. **Which fork depends on what density the plasma
must run at, which is a PLASMA question, not a cavity one.**


### 🔧 COAX FEED THROUGH A HOLE — BUILT AND VERIFIED IN GEOMETRY, NOT YET SOLVED (2026-09-02)

*User: "Why can't the coupler simply enter through a hole?"* — implemented.
`--loop-hole r_mm,stub_mm`. Default None reproduces every earlier run byte for
byte (control checked: loop area 121.8 mm^2, unchanged).

✅ **VERIFIED AGAINST THE MESH, not the sidecar:**

    physical groups: (2,90) wall  (2,91) PORT  (2,92) loop
    attr 91 : 210 nodes  r 96.0045..96.0321  z -2.2993..+2.2975
    port_face_mm (outer,inner dia) = [4.6, 2.0]   tets 75,724

The annulus sits at the stub mouth (r = a + 8 = 96.004 mm), outer 4.6 mm /
inner 2.0 mm dia — the coax cross-section. The feed leg runs through to
r = 96.01 (attr 92), and the stub's outer surface is at r = 96.03 (attr 90).

🔑 **TWO NUMBERS THE PHYSICS CHOSE, NOT A CATALOGUE:**
  - **hole radius 2.3 mm**, because Z0 = 59.96*ln(2.3/1.0) = **49.9 ohm** against
    a 1 mm inner conductor in air. That is the whole "what connector" question.
  - **the leg MUST pass through.** An empty 2.3 mm hole has a TE11 cutoff of
    29.3 GHz — ~5 e-foldings of decay over an 8 mm stub, i.e. a dead end. With
    the inner conductor it is a COAX, and TEM has no cutoff.

✅ **THE HOLE IS ELECTRICALLY BENIGN.** Eigen with the face shorted:
TE011 Q0 = 43,900 at 2.439396 vs ~43,800 without a hole — 0.2%. And MFEM loaded
it, so the per-sector fuse is manifold (the chimney/feed hazard, 7bn).

🔴 **A LUMPED PORT CANNOT DESCRIBE IT — from Palace's source, not a guess.**
`configfile.cpp ParseStringAsDirection`: a string Direction "r" maps to
CYLINDRICAL, but about the GLOBAL z axis. This coax enters through the BARREL,
so its inner->outer field lies in the theta-z plane. Also
`ParseElementData`: "Cannot specify CoordinateSystem with string Direction" —
CoordinateSystem is only legal beside an ARRAY Direction.
✅ Palace supports **WavePort** (mode_idx, d_offset, excitation, attributes),
which solves the port's own modal field and needs no direction.
⚠️ DRIVEN ONLY — wave ports are frequency-dependent. Q0 keeps coming from eigen
with the face shorted (port_bc="pec"), which needs no port model at all.
`solveconf.driven()` now emits a WavePort when the sidecar carries
`loop_hole_mm`, and a LumpedPort otherwise.

🔴 **NOT YET DONE: the end-to-end driven solve.** The spot died mid-test and it
lived in /tmp, so nothing of it survives. **Next session: rebuild the coax mesh
and run one driven sweep** — the open question is simply whether Palace accepts
a WavePort on this annulus, and what Q_L it gives with the reference plane AT
THE WALL, against the mid-arc-fed Q_ext = 13,977.

### 🔴 A BUG CLASS THAT BIT THREE TIMES THIS SESSION — metadata asserting what the artefact lacks

  1. `surface_attributes` was the literal `["wall","port","loop"]` regardless of
     what was built, so the first coax mesh — which really had only groups 90
     and 92 — still advertised a port. `volume_attrs()` TRUSTS that list to
     tell surfaces from volumes, so a config could reference attribute 91 into
     thin air. ✅ Now derived from whether a port face exists.
  2. `loop_azim`'s first element silently changed meaning (centreline ->
     standoff) while configs kept the old value.
  3. `eigen_cfg` gave the plasma eps = 1.0 because the Drude values live in the
     RIG, not the mesh — so a "loaded" solve was a COLD solve, identical to 6
     figures.

🔑 **All three were caught only because something downstream happened to look
wrong.** Verify metadata against the ARTEFACT (`ops/oneoff/mesh_attr_extents.py`
reads the mesh's real physical groups), never against what the writer intended.


### 🔧 COAX WAVE PORT — FIVE FAULTS FIXED, THE SOLVE STILL UNTESTED (2026-09-02)

The geometry is right and every guard passes; what has never run is Palace
accepting the wave port. Two spots died mid-test, both times with the run in
/tmp. **One driven sweep is all that is outstanding.**

✅ **VERIFIED:** `COAX MOUTH: exterior face 288, 13.48 mm^2 (annulus wants
13.48)` — the mouth is found by area to 4 significant figures.

**The five faults, in the order they surfaced** (each hid the next):

  1. **Silent rsync.** The sync carrying the WavePort code ran while the spot
     was being reclaimed; output went to /dev/null so it "succeeded". The next
     box came up with the OLD code and the mesh cache served OLD meshes. The
     symptom — a sidecar field reading None for an unconditional parameter —
     looked exactly like a code bug in code that was already correct.
     ➡️ CONVENTIONS: never `rsync.sh >/dev/null`; assert on the far side.
  2. **`driven()` returns a tuple**, not a dict — my test harness assumed dict.
  3. **Inserted the port face.** A LUMPED port is an INTERIOR face you insert;
     a WAVE port is an EXTERIOR boundary you IDENTIFY. Inserting a coincident
     annulus was wrong — though this was NOT the cause of the Palace error, and
     I rebuilt it on that wrong theory because I had truncated the message.
     ➡️ CONVENTIONS: read the whole error before grepping it.
  4. **The mouth was in BOTH `wall` and `port`.** Every exterior face lands in
     `wall` unless excluded, so tagging it `port` too put two boundary elements
     on one face: *"A non-periodic face (288) cannot have multiple boundary
     elements! Attributes: 91 90"* — the message named the face AND both
     attributes, i.e. the entire diagnosis, in the clause I had cut off.
  5. **The area partition check.** wall+loop no longer covered the exterior,
     because a coax port is a THIRD exterior class. ✅ This guard fired
     immediately and exactly — the discrepancy was 13.477 mm^2, the mouth. It
     now counts an exterior port.

🔑 **EVERY ONE OF THESE WAS MISUSE, NOT A TOOL DEFECT** — and that is why they
are METHODOLOGY rather than lost time. Palace and gmsh did what they were told
each time: the port face overshot because it was BUILT that way; `h` meant
centreline because it was PARAMETERISED that way; the sidecar claimed a port
because that string was HARDCODED; the plasma solved as vacuum because
`eigen_cfg` reads the mesh and the Drude values live in the rig; the wave port
needs PEC and that is documented behaviour nobody had read. Knowledge of correct
use IS the method, and it is normally acquired exactly this way.

🔑 **THE ASYMMETRY WORTH KEEPING:** the three GEOMETRY guards (loop area,
standoff/centreline, area partition) each caught their fault precisely and at
once. The METADATA that asserted what the artefact contained caught nothing and
caused three separate wrong turns. Guard on measurements of the artefact, not
on declarations about it.

➡️ **NEXT SESSION, first thing:** rebuild the coax mesh and run one driven
sweep. `/tmp/wpt2.sh` is the recipe (kept as ops/oneoff/). The open question is
only whether Palace accepts a WavePort on this annulus, and what Q_L it gives
with the reference plane AT THE WALL, against the mid-arc-fed Q_ext = 13,977.


### 🔴 COAX WAVE PORT — ACCEPTED AND CORRECTLY ORIENTED, BUT ITS BOUNDARY MODE DOES NOT CONVERGE (2026-09-02)

✅ **The wave port works as a configuration.** Palace parses it, finds it on
attribute 91, and — the part that matters — computes its orientation correctly:

    91: Index = 1, mode = 1, d = 0.000e+00 m,  n = (+0.8,+0.5,-0.0)

n is the radial direction at phi = 31.87 deg (cos = 0.849, sin = 0.528), i.e.
the coax axis. Palace understands the geometry. This settles the question the
whole coax exercise was for: **a wave port CAN describe a barrel-entering coax
where a lumped port cannot.**

🔴 **But it does not solve.** The run stalls at:

    Calculating boundary modes at wave ports for omega/2pi = 2.438e+00 GHz

for the FIRST frequency — 39 minutes with no progress and no error. That is a
small 2D eigenproblem on a 210-node annulus and should be near-instant, so this
is NON-CONVERGENCE, not cost.

⚠️ **Do not read the earlier PROM run as a different failure.** Both runs stall
in the same place; the PROM one merely hid it behind an offline phase that
writes nothing. Palace's driven template sets `AdaptiveTol 0.001` /
`AdaptiveMaxSamples 40`, so it builds a reduced-order model before writing ANY
frequency point — a healthy long run and a hung one look identical from
outside. **Set `AdaptiveTol = 0` when diagnosing.**

🔎 **LEADING HYPOTHESIS — the port face is too coarse.** The annulus spans
r_inner 1.0 to r_outer 2.3 mm with ~0.433 mm elements: about 3 elements across
the gap, and only 210 nodes on the face. A 2D modal solve wants more. ➡️ Next
attempt: refine specifically ON the port face (a mesh field keyed to the mouth,
not just the stub volume) and retry. If it still stalls, the alternatives are a
coax stub long enough to use a lumped port on a TEM cross-section, or accepting
the mid-arc drive, whose Q_ext = 13,977 stands and whose source position differs
by only ~26 deg on a wavelength/6.8 loop.

✅ Everything upstream is verified and committed: the hole, the through-leg, the
mouth identified by area to 4 s.f., the wall/port exclusivity, and the area
partition guard extended to a third exterior class.


### ✅ COAX FEED MEASURED — Q_ext ~12,800, ~11% weaker than the mid-arc drive (2026-09-03)

Azimuthal wire loop, standoff 2.0 / arc 12.24, coax entering through a 2.3 mm
hole (Z0 = 49.9 ohm), reference plane AT THE WALL. `--sectors 1`, PEC walls,
wave port, plain sweep (AdaptiveTol = 0), 41 pts @ 25 kHz.

    resonance            f0 = 2.439900 GHz
    +-90 deg bandwidth   188.6 kHz   ->  Q_ext = 12,938
    phase slope / 4                  ->  Q_ext = 12,729     (1.6% apart)

🔑 **LIKE FOR LIKE, and the comparison nearly went wrong.** Q_ext = 13,977 is
from the VACUUM-torch cavity; this coax mesh carries the default SAPPHIRE torch
(eps 9.39). f0 gives it away — 2.4399 vs 2.4504. The correct comparison is the
sapphire-cavity mid-arc case, same loop and standoff:

    mid-arc gap,  sapphire torch : Q_ext = 11,576   (Q0 43,744 / coupling.beta 3.779)
    coax at wall, sapphire torch : Q_ext ~ 12,800

🔴 **AND THE DIRECTION OF THAT COMPARISON WAS WRONG.** *User, 2026-09-03: "The
mid arc was basically never viable anyway, so it can't be considered a
baseline."* Correct — the mid-arc gap drives a loop with BOTH legs grounded and
NO feed entering the cavity. It is not buildable, so it is not a reference.

✅ **THE COAX IS THE BASELINE. Q_ext ~12,800 is the number** for this loop.
The mid-arc value is a PROXY, and the ~11% gap measures how good a proxy it was
— a statement about the old corpus, not about the coax.

**What that means for the mid-arc corpus** (`h3-azim-01`, `h3-azimwidth-01`):
  ✅ RELATIVE results are probably usable — L-exponents, the wire/strip
     comparison, the width and thickness trends. All were measured within ONE
     feed geometry, so the feed's offset largely divides out.
  🔴 ABSOLUTE Q_ext and coupling.beta from those runs are proxy values and should be
     restated on the coax basis before they drive anything.

⚠️ **CONSEQUENCE FOR THE DENSITY WORK, NOT YET DONE.** The operating-point
analysis (optimum ~3e16, 73.8% delivered) used Q_ext = 13,977 — a MID-ARC value
on the VACUUM-torch cavity. The coax figure measured here is on the SAPPHIRE
cavity, so the substitution cannot simply be made. ➡️ Measure coax Q_ext on the
vacuum-torch cavity, then redo the coupling.beta/efficiency table. Expect the optimum to
shift SLIGHTLY LOWER in density: the peak sits where Q0_loaded ~ Q_ext, so a
larger Q_ext is matched by a larger Q0_loaded, which occurs at lower n_e.

🔴 **TWO INSTRUMENT FACTS, both hard-won:**
  1. **A wave port needs PEC on the conductors bounding it.** With
     `Conductivity` (finite sigma) the 2D boundary-mode solve NEVER converges —
     39 min, no progress, no error. Recorded in CONVENTIONS. Three wrong
     theories were chased first: a coincident inserted face, sectors > 1, and
     port-face resolution.
  2. **A wave port's absolute power is NOT normalised to 1 W.** Energy balance
     assuming it gave Q_ext = 2.3e6, ~113x wrong. Use only
     normalisation-INDEPENDENT extraction from a wave port: phase slope or the
     +-90 deg bandwidth. (Energy balance remains correct for a LUMPED port,
     where port-V/I are written and the power is real.)

⚠️ PEC walls make Q_L == Q_ext, which is why this measures coupling cleanly —
but it also means such a run says NOTHING about Q0. Take Q0 from an eigen solve
with the port shorted.


### 🔴 TWO SOURCES OF TRUTH FOR THE COLLISION FREQUENCY (2026-09-03)

Found while disambiguating the three sigmas — a naming audit surfacing a
BINDING defect, which is CONVENTIONS §2, not a naming problem.

    h3_loaded.py:147   NU_M = 1.0e11        HARDCODED. drude() uses it, so it
                                            set eps/sigma for EVERY plasma solve
    physics.plasma_state(5245)  nu_m = 6.295e10   DERIVED from T_gas, pressure
                                            and the momentum cross-section

**1.59x apart, and neither is bound to the other.** Identical in shape to R110's
wall metal: *"a decision recorded in one place and never bound to the thing that
consumes it. A baseline nobody reads is a claim, not a fact."*

**CONSEQUENCE — it moves the plasma physics, not just a label:**

    nu = 1.000e11 (used)     eps(7.9e18) = -1.456   eps = 0 at n_e = 3.22e18
    nu = 6.295e10 (derived)  eps(7.9e18) = -4.99    eps = 0 at n_e = 1.32e18

The over-dense threshold moves by **2.44x**. Every plasma solve in the record
used nu = 1e11.

⚠️ **WHICH IS RIGHT IS NOT OBVIOUS, AND THAT IS THE POINT.** `NU_M` is labelled
"N2 at 1 atm"; the derived value carries `MOMENTUM_CROSS_SECTION_M2`'s
order-of-magnitude uncertainty, which `physics.py` states plainly. Both are
estimates. The defect is that TWO EXIST and the code silently picks one.

➡️ **REPAIR — HALF DONE 2026-09-03, and the plan changed on prior art.**

✅ `drude(ne, w, nu=None)` now takes the collision rate explicitly, so a caller
can bind it to the SAME state that set `ne`. The default is still `NU_M`, and is
**bit-identical to the old form** (asserted over n_e = 1e18/7.9e18/1e20), so no
recorded result moves. `NU_M` now carries both figures, the 1.59x ratio and the
2.44x threshold shift, at the definition.

🔎 **PRIOR ART changed the second half.** `physics.plasma_state` was written as
the fix for EXACTLY this defect — its own header says the code "used to set NE
and NU_M independently, and nothing errored when they disagreed". So the answer
is **not** a new `baselines.json` row: n_e, nu_m and n_gas are ONE STATE derived
from ONE temperature, and adding a standalone `plasma.collision_frequency` row
would mint a THIRD source of truth while claiming to remove the second.
`h3_loaded` simply never adopted the function that already exists.

🔴 **THE REMAINING HALF IS A DECISION, NOT A REFACTOR — and it is yours.**
Switching the default from 1.0e11 to the derived 6.295e10 changes every loaded
eps: eps(7.944e18) goes **-1.470 -> -5.019**. That is a physics change, so it is
not being made silently as part of a naming audit. Deciding it needs the gas
temperature, which is the **blocker already owned by `spectroscopy/`**.

⚠️ **DOES NOT INVALIDATE THE DENSITY SWEEP'S SHAPE.** Q_L(n_e) was MEASURED at
the eps/sigma the solves actually used, so the curve stands as measured. What
moves is the eps ANNOTATION on each row, and hence where "over-dense" is said to
begin — the collapse is collisional absorption well below cutoff either way.

## ✅ DONE 2026-09-05 — ops/solverprogress.sh goes silent after greedy convergence

**2026-09-05, found by the user twice in one run** ("1h again, 80GB steady",
then "97 minutes, 80GB steady").

The poller keys on `Greedy iteration`. When adaptive sampling CONVERGES those
lines stop, and Palace moves to evaluating the PROM over the band — printing
`It <n>/<total>  ω/2π = ... GHz`, a better progress signal than the one being
watched. Between greedy termination and the case artefact the watch is silent
again, which is §7ce reproduced one phase later.

🔧 **Fix:** match `Greedy iteration|^It [0-9]+/[0-9]+` and emit the last of
either. ⚠️ Keep the dedup keyed on the matched line WITHOUT elapsed time (§7ce)
— `It n/N` changes every poll by design, so it needs a coarser key (e.g. every
100th point) or it re-floods.

✅ FIXED before the next launch, as this note required. Matches
`Greedy iteration|^It n/N` and buckets the sweep counter per 100 points, so the
evaluation phase emits ~17 events rather than one per poll.

## ✅ DISCHARGED 2026-09-05 08:47Z — instance shut down

**User, 2026-09-05:** *"Go as far as you can, and when you're done, please be
sure to shut the instance off"*

    ops/go ops/shutdown.sh     # syncs, UNMOUNTS /opt/amip, verifies, powers down

⚠️ Recorded in a FILE, not held in a head or a session. This is the shape that
fails: a final step that depends on someone remembering it after the interesting
work is over (§7cb, §7cc). An idle instance bills at the solving rate, and
2026-08-27 lost 24 minutes to exactly this.

✅ `ops/go ops/shutdown.sh` ran clean: 0 live processes, `/opt/amip` unmounted
AND VERIFIED, instance confirmed unreachable after 10 s. The EBS volume survives
and holds every solved case. Artefacts were fetched BEFORE the shutdown.

## ✅ DECISION 2026-09-06 — OPTIMISE THE COUPLER FOR THE LOADED STATE

**User:** *"I don't think minimax is a valid target either. I think we should
optimize the cavity for loaded."* And: *"It would mean that the circulator is not
optional, yeah."*

🔑 **THE MINIMAX IS RETIRED AS A TARGET.** Its mechanism was never wrong — one
`cavity.Q_ext` serves two states whose Q₀ differ by ~265× — but it was trading
loaded performance to protect a COLD state whose value was never measured.

➡️ **MEASURED-ish, and it decides the trade** (`coldfield.py`, re-runnable):

🔴 **CORRECTED 2026-09-06 — THE FIRST NUMBERS HERE WERE WRONG.** `coldfield.py`
used **KC_A = 2.405**, the first zero of J0 — a **TM01** constant. TE011 goes as
`J1(chi'01 r/a)` with **chi'01 = 3.8317**, the first zero of J1 (= J0'). ✅ The
check that catches it in one line, now a `self_test()`: the constant must
reproduce the DESIGN FREQUENCY — chi'01 gives 2.4500 GHz, 2.405 gives 1.8404 GHz.
Caught by reading `probecheck.py`, which states the profile correctly.

| cold state | delivered of 1 kW | \|E\| r=2 mm | \|E\| r=8.5 mm |
|---|---:|---:|---:|
| measured (`coupling.beta.cold` = 156, overcoupled) | 25.3 W | 0.009 kV/cm | 0.040 kV/cm |
| **hypothetical PERFECT cold match** | 1000 W | **0.526 kV/cm** | **2.200 kV/cm** |

⚠️ **AND THE CONCLUSION IS WEAKER THAN FIRST STATED.** The original entry said a
perfect cold match *"falls short by 2–20×"*. At the OUTER torch radius it does
not — 2.20 kV/cm **reaches the bottom of the 2–5 kV/cm band.** It is short by
~4× at r = 2 mm, and short across the bore only against the upper end.

✅ **WHAT STILL STANDS, AND IT IS THE PART THE DECISION RESTS ON:** the MEASURED
cold state delivers **0.009–0.040 kV/cm — 50–550× short.** The gap between the
cold state we have and any useful field is enormous, and closing it requires a
PERFECT match that then only just reaches the band's lower edge at the widest
radius. **So the cold match is still not worth buying at the price of loaded
performance** — but the margin is thinner than this entry first claimed, and a
reader should not quote "2–20×".

🔴 **AND TE011 HAS NO E-FIELD ON THE AXIS.** `E_phi ~ J1(kc r)`, `J1(0) = 0`
identically — zero on the centreline by symmetry, rising with radius. The
start-cycle field is an OFF-AXIS quantity, quoted across the bore.

⚠️ **NO TRANSIENT TO EXPLOIT.** Fill time `2Q/omega` is **19 ns** measured cold,
1.5 us at a perfect match. A "first few milliseconds" window is thousands of time
constants: the steady-state numbers ARE the start-cycle numbers.

🔴 **THE CIRCULATOR IS NOT OPTIONAL — it is now load-bearing.** Optimising for
loaded means accepting a large cold mismatch, and `../control-loop/README.md`
already budgets **up to 961 W of 1 kW into the dump**. That was a tolerance; it is
now a REQUIREMENT, and the dump-load duty must be sized for the whole start
cycle, not a transient.

✅ **`coupling.beta.loaded` = 1 IS A VALID TARGET.** An earlier draft of this
entry said "target NEAR beta = 1, not AT it", treating the vanishing reflected
wave as a control problem. **That was wrong and is retracted here.**
🔑 User, 2026-09-06: *"this just implies the tuner doesn't need to change its
outputs. And it can tell, because the dual directional coupler would say 0%
reflected vs 100% forward."* **The null IS the setpoint.** A dual directional
coupler reads forward and reflected separately, so beta = 1 is an unambiguous
0%-reflected state, not a blind one. A servo needs a DIRECTION signal only when
it is AWAY from target — which is precisely where a reflected wave exists to
carry the phase — and crossing the null flips that phase by 180°.
⚠️ What actually remains is an ordinary **dead-band** around the setpoint, floored
by coupler directivity (~20 dB), inside which beta = 1 and beta = 1.02 are
indistinguishable. That is a resolution limit at the target, not a reason to move
the target. `../control-loop/`'s own remedy already said this: catch the crossing
by the **|Γ| minimum** and apply it with a state machine.
🔑 **AND THE LIMIT IS SIGNAL, NOT RESOLUTION.** User, 2026-09-06: the FPGA that
does frequency tuning can also do the phase discrimination. Correct, and already
recorded — `../control-loop/README.md`, credited to the user 2026-08-25: at f₀,
Γ = (beta−1)/(beta+1) is REAL, so **beta and 1/beta differ by exactly 180°**,
±45° resolution is ample, and coupler directivity clears the operating points by
16–20 dB. One complex-Γ measurement serves the frequency servo AND the branch.
⚠️ Listed there as *"argued, not designed"*. At beta = 1 there is simply no
reflected wave to take a phase OF, so the crossing is caught by the **|Γ| minimum
and a state machine**, not by better phase resolution.

⚠️ **MAGNITUDE TUNING IS UNSOLVED — WHICH IS NOT THE SAME AS IMPOSSIBLE.**
User, 2026-09-06: *"it says its unsolved, not that it doesn't exist. We know we
can get VSWR to under 5, so it's plausible, not improbable."* Correct, and an
earlier draft of this entry said "there is no magnitude tuner" — **that was an
overstatement and is retracted here.** `../control-loop/` item 2 rejected **four
PIN-diode candidates**, for a real structural reason (low C_j needs a small die,
a small die has high thermal resistance, so parts that work at 2.45 GHz cannot
carry 39–42 A) — but that is four candidates in ONE technology family, not a
proof. Mechanical stub/sliding-short tuners were never evaluated here.
🔑 **AND THE REQUIREMENT MAY BE MILD.** If the coupler geometry is optimised for
LOADED, the tuner is trimming a residual, not spanning the ~400× between states —
a much easier specification than the one those four candidates were rejected
against. ⚠️ Note the 39–42 A figure is a CURRENT in the tuning element set by the
cavity fields, so it does not automatically shrink with the mismatch; the
requirement depends on where the tuner sits.
➡️ **THE DECISION DOES NOT REST ON THIS.** It rests on the cold-field estimate
above: a perfect cold match falls 2–20× short inside the bore, so the cold state
is not worth buying at any price in loaded performance. A magnitude tuner, if one
is found, only makes the loaded-optimised design better.

⚠️ **OPEN, and it bounds the start-cycle discussion:** `../control-loop/` item 4 —
*"Tuner SPEED requirement — NOT DERIVABLE, set by ignition dynamics, which no
programme here has measured. Everything in resonance is steady-state."*

⚠️ **THE FIELD NUMBERS ARE AN ESTIMATE, NOT A MEASUREMENT.** Analytic TE011 in a
BARE cylinder: no groove, no quartz torch (eps 9.39), no loop. ➡️ To settle them,
re-run a cold rig WITH PROBES — `fieldcheck.py` is the evaluation layer already
waiting for that data and today reports *"no named-probe fields recorded"*.

## 🔴 THE COUPLER-FAMILY COMPARISON IS UNFAIR IN A KNOWN DIRECTION

**User, 2026-09-06:** *"We never concluded that we're building the loaded cavity
with the barrel and gap2 coupler."* And: *"there will be a lot of claims about the
barrell loop **relative to the cap loop**, not the azimuthal."*

✅ **BOTH CORRECT, AND I HAD DRIFTED.** I described barrel + gap2 as "the coupler
we're actually building." Nothing decided that — it is what the most recent rigs
happened to mesh. `NEXT.md § BLOCKED ON DECISIONS` still lists **coupler family**
as open, and ⚠️ **`DISCLOSURE.md` claims the AZIMUTHAL one.**

🔴 **AND THE BARREL ARM HAS NO DIMENSIONS OF ITS OWN.** From § *Dimensions with NO
provenance*:

| | value | status |
|---|---|---|
| `loop.wire_r.mm` | 1.0 | 🔴 TENTATIVE — a `geometry.py` default, never chosen |
| `loop.gap.mm` (port gap) | 0.3 | 🔴 TENTATIVE — same |
| `loop.size.mm` | 11 × 8 | ⚠️ swept on the **CAP** at N=1; *"does not transfer to the barrel"* |

🔑 **THE THREE-WAY IS MASQUERADING AS PAIRWISE.** There are THREE families — cap,
barrel + series gap, azimuthal — and most barrel claims are anchored to the CAP
(the 5.6 % mount edge; `h3_loopq` compares every run against `h3_step3`'s cap loop;
`Q_EXT_MEASURED` = 9,231 is the cap loop's). **A barrel result stated "relative to
cap" says nothing about the azimuthal decision.**

⚠️ **SO THE COMPARISON IS BIASED, AND THE DIRECTION IS KNOWN.** The azimuthal arm
was characterised — `h3-azimwidth-01` swept conductors 10.2/12.24/14.2, wire vs
strip, fitted L-exponents. The barrel arm got two defaults and a cap optimum the
record itself calls non-transferable. **Comparing them today compares a
characterised azimuthal against an arbitrary barrel.**

➡️ **PREREQUISITE, before any cross-family number means anything:** the barrel arm
needs its own dimension sweep — size ON THE BARREL, wire radius, port gap. Until
then a barrel-vs-azimuthal verdict is not a measurement of the families, it is a
measurement of how well each was tuned.

⚠️ **AND IT DEMOTES THE gap2 LEVER FURTHER.** `dQ_ext/d(gap2)` optimises ONE
coordinate of a geometry unplaced in the other three. It is barrel-only
(`geometry.py` cannot build a series gap on the azimuthal mount), so it is also
moot if the azimuthal family wins.

✅ **UNAFFECTED:** `h3-betafloor-*`. Mesh repeatability at fixed geometry is a
property of the DISCRETISATION, not of the loop dimensions — it stands whichever
coupler wins and however the barrel is eventually sized.

🔑 **THE CRITICAL PATH IS STILL ONE NUMBER:** `cavity.Q_ext.loaded` on the
azimuthal coupler (`h3-azimload-02`, failed — no measurable 3 dB width). ~14,000
-> loop-set, the family choice is real. ~300 -> plasma-set, the loop barely
matters loaded and much of the above stops mattering. **A method fix, not a
re-run:** the PROM converged (4.83e-04); the FIT could not find a 3 dB crossing
inside 2.30-2.65 GHz.

## ✅ DECISION 2026-09-06 — THE CAP LOOP IS RETIRED; THE BARREL IS A BASELINE ONLY

**User:** *"The only value, at this point, to having the barrell coupler is as
something to compare azimuthal to. The cap loop is basically retired. I don't want
to chase anything in the barrell loop because it doesn't compare well to azimuthal
for the tests we've done, and I don't want to waste time on it."*

➡️ **CONSEQUENCES, and they REMOVE work rather than add it:**

1. 🔴 **NO BARREL DIMENSION SWEEP.** The prerequisite recorded above — size on the
   barrel, wire radius, port gap — is **WITHDRAWN, not deferred.** The barrel is
   not being optimised, so its three tentative dimensions no longer block
   anything.
2. 🔴 **NO gap2 LEVER SWEEP.** `dQ_ext/d(gap2)` is barrel-only and was already two
   gates downstream. **Dropped.** ⚠️ Which also retires the open question of
   whether gap2 = 2.25 is an interior optimum — it does not matter for a baseline.
3. 🔴 **`h3-betafloor-b` and `-c` CANCELLED.** Two more barrel replicates is
   exactly the waste this decision forbids. ✅ Replicate **A is finished out** — it
   was minutes from converging, and paired against `h3-betaconv2-1p0` it already
   gives an independent-mesh floor.
4. ✅ **THE CAP LOOP IS RETIRED.** ⚠️ But `Q_EXT_MEASURED` = 9,231 is a CAP-loop
   constant still embedded in the record, and `h3_loopq` compares every run
   against `h3_step3`'s cap loop. **Retiring the loop does not retire its
   constants** — those remain the source of the identity failures.

⚠️ **WHAT THE BARREL MAY AND MAY NOT BE USED FOR.** As a baseline it can answer
*"is the azimuthal in the right ballpark"*. It CANNOT support a family verdict —
*"azimuthal beats barrel"* would compare a characterised arm against an
unoptimised one, and the bias direction is known. Any such statement must say so.

🔑 **THE CRITICAL PATH IS UNCHANGED AND NOW UNCONTESTED:** `cavity.Q_ext.loaded`
on the AZIMUTHAL coupler. `h3-azimload-02` failed on the FIT, not the solve (PROM
converged at 4.83e-04; no 3 dB crossing inside 2.30-2.65 GHz). A method fix.

## 🔑 REFRAMING 2026-09-06 — THE SPECTROSCOPY BLOCKER IS THE WRONG CONDITION

**User:** *"the condition is what a Nitrogen plasma is able to excite, not what the
spectrometer is expected to see. And the 5250K operating temperature is largely
determined by Nitrogen re-association, not the microwave power. So the coupler
should be optimized for Nitrogen disassociation."*

**As currently written the blocker is a spectrometer requirement.** `KNOWN.md`:
*"resonance is BLOCKED on one answer from `../spectroscopy/`: the required GAS
TEMPERATURE"*, with the chain **T_gas → Saha → n_e → the coupler's operating
point**. `NEXT.md`'s anchor entry is the same: *"Anchor n_e — 7.3–8.6e18, from
MICAP's measured 5220–5270 K."*

➡️ **THREE CONSEQUENCES, and they change what must be measured:**

1. 🔴 **THE CONDITION IS EXCITATION CAPABILITY, NOT DETECTION.** What the plasma
   can excite is a property of the DISCHARGE; what the spectrometer sees is a
   property of the instrument downstream. Deriving a cavity requirement from the
   latter imports an unrelated instrument's limits into the coupler design.
2. 🔴 **5250 K IS NOT A POWER SETPOINT — IT IS BUFFERED.** If the operating
   temperature is set largely by N2 **re-association**, the gas temperature is
   held by the dissociation/recombination balance rather than by delivered
   microwave power. ⚠️ **Then T_gas is a poor control variable and a poor design
   target**: more power does not proportionally raise it, it goes into
   dissociating more N2. `KNOWN.md`'s *"gas temperature is measurable by optical
   [means]"* stays true — it just stops being the quantity the coupler is FOR.
3. ➡️ **THE COUPLER FIGURE OF MERIT BECOMES POWER INTO N2 DISSOCIATION.**
   Not "reach 5250 K", not "match at the Saha density for 5250 K".

⚠️ **WHAT THIS DOES NOT DO — it does not by itself unblock the density fork.** The
coupler still has to be matched at SOME `plasma.n_e`, and `cavity.Q0.loaded`
varies strongly with it. What changes is WHERE that number must come from: a
dissociation/recombination balance for N2 at the operating pressure and flow,
rather than a Saha inversion of a MICAP temperature measured on another
instrument. ⚠️ `ret:operating-point-79e18` stands either way — 7.9e18 was never
measured here.

🔴 **UNVERIFIED HERE.** This is the user's physics, recorded as the governing
condition; no rig in `resonance/` has measured a dissociation fraction, and the
programme's plasma is a STATIC UNIFORM Drude annulus that models neither
dissociation nor recombination. ➡️ It belongs to `../spectroscopy/` and
`../torch-geometry/` (gas flow sets residency, which sets the balance) — resonance
consumes the answer, it cannot produce it.

## 🔴 CRITICAL COUPLING FOR N2 DISSOCIATION — BLOCKED ON AN UNMADE DECISION

**User, 2026-09-06:** *"So, we have to find the critical coupling for Nitrogen
disassociation"* / *"we probably have to model the plasma as a lossy dielectric"*.

✅ **THE TARGET IS WELL-POSED.** Critical coupling is `coupling.beta.loaded` = 1,
i.e. **`cavity.Q_ext.loaded` = `cavity.Q0.loaded`**. `Q0.loaded` is a CAVITY
property, so resonance can produce it — the coupler is then read off it.

🔴 **BUT `Q0.loaded` DEPENDS ON A PLASMA STATE THAT IS INTERNALLY INCONSISTENT.**
`h3_loaded.py` records it and states the required action:

    NU_M, used by every rig            1.000e11 rad/s   round, "N2 at 1 atm"
    physics.plasma_state(T_anchor)     6.295e10 rad/s   DERIVED from T
    ⚠️ "Decide which before any further loaded number is quoted"

**The decision was never made, and every loaded number since has been quoted.**
At `plasma.n_e` = 7.9e18, 2.45 GHz:

| collision rate | eps_r | sigma (S/m) |
|---|---:|---:|
| `NU_M` = 1e11 — **what every rig solved** | **−1.456** | **2.175** |
| state-consistent 6.295e10 | −4.987 | 3.337 |

**3.4× in eps, 1.53× in sigma.** ⚠️ `drude()` already accepts `nu`; NO rig passes
it. `plasma_state` is called only by `e3_closure.py`.

🔑 **AND IT IS NOT A LOSSY DIELECTRIC AT THE DISSOCIATION POINT.** With the
state-consistent rate the sign change sits near **4700–4800 K**; at 5250 K,
`eps` = −5.12 — **over-dense, metal-like**, not a lossy dielectric. ⚠️ Under the
rigs' `NU_M` the crossing moves to n_e ≈ 3.22e18 vs 1.32e18 — *"eps = 0 moves
2.44×"*. **Which regime the design sits in depends on the unmade decision.**

➡️ **WHAT RESONANCE CAN DELIVER WITHOUT THE PLASMA PROGRAMME.** Not a single
number — a **curve**: `cavity.Q0.loaded` over the plasma state, on the DESIGN
cavity. Critical coupling is then `Q_ext = Q0.loaded` read off it.
🔑 **Parameterise it by (eps, sigma), NOT by n_e.** That is the user's "lossy
dielectric" framing taken literally, and it is the robust one: it carries no
Drude, no Saha, and no collision-rate assumption. The plasma programme then
supplies one (eps, sigma) for the dissociating state and the coupler follows.
⚠️ It also makes the map survive the `NU_M` decision, which n_e-parameterised
results do not.

⚠️ **DIRECTION OF THE ERROR, IF THE STATE-CONSISTENT RATE IS RIGHT:** sigma is
54 % HIGHER, so absorption is higher and `cavity.Q0.loaded` is LOWER than the
recorded 74.31 — meaning critical coupling needs **more** coupling than the 3.06×
implied by today's numbers, not less.

## 🔑 THE OBJECTIVE IS N2 DISSOCIATION — AND THE EM LEVER LEFT IS 1.41x

**User, 2026-09-06:** *"Just to clarify, we're looking for optimizing Nitrogen
dissociation, not Q0, not loop coupling, and so on."*

✅ **SO THE FIGURE OF MERIT IS `P_plasma / P_incident`**, and it factors:

    P_plasma / P_incident = (1 - |Γ|²) · eta_plasma

Both terms are measured on the design cavity at the anchored state:

| coupling | `coupling.beta.loaded` | into cavity | **→ plasma** |
|---|---:|---:|---:|
| measured now (barrel + gap2 2.25) | 0.301 | 71.1 % | **70.9 %** |
| 2× stronger | 0.601 | 93.8 % | 93.5 % |
| **CRITICAL** | **1.000** | **100 %** | **99.7 %** |
| 2× past critical | 2.000 | 88.9 % | 88.6 % |

🔑 **eta_plasma IS ALREADY 99.705 %** — of the power the cavity dissipates, walls
and dielectric take 0.295 %. **There is nothing to win there.** The cavity's only
remaining job is to stop REFLECTING.

🔴 **THE ENTIRE REMAINING EM LEVER IS 1.41x** (70.9 % → 99.7 %). Coupler family,
gap2, loop dimensions, and `coupling.beta.loaded`'s mesh convergence ALL live
inside that 1.41×, and **nothing in the cavity can exceed 99.7 %.**
⚠️ This reframes the mesh worry: β moving 8.56 % between meshes is worth a few
percent of delivered power. It matters for HITTING β = 1, not for how much β = 1
is worth.

➡️ **OUTCOME CHECK (§ measure the outcome, not the coefficient).** N2 → 2N is
945 kJ/mol; at 20 °C, 1 atm:

| | P_plasma | fully dissociates | of the assumed 20 L/min |
|---|---:|---:|---:|
| now | 709 W | 1.08 L/min | 5.42 % |
| critical | 997 W | 1.52 L/min | 7.62 % |

⚠️ **A THERMODYNAMIC CEILING, NOT A PREDICTION.** It assumes every joule breaks a
bond — no radiative or convective loss — so the real figure is LOWER. And it
assumes the WHOLE flow must dissociate, which is wrong: only the central channel
carries sample. **Both caveats are large and point opposite ways**, so this bounds
the problem rather than answering it.

🔑 **WHAT THIS MEANS FOR THE QUEUE.** The cavity work is nearly finished as an
optimisation: reach critical coupling at the dissociating state and the EM side is
done to within 0.3 %. Everything beyond 1.41× must come from POWER or FLOW or
where the gas goes — `../torch-geometry/` and `../control-loop/`, not resonance.
➡️ `h3-q0map-01` still earns its keep: it locates β = 1 across the plasma state,
which is the 1.41×. But it should be the LAST large cavity optimisation, not the
first of a series.

## 🔑 REFINEMENT 2026-09-06 — COLD HAS NO ABSORBER, NOT MERELY A POOR MATCH

**User:** *"an EM field trivially shifts free electrons and can't really reach the
valence-bound electrons. So, while cold there's basically no free electrons. Upon
avalanche, the goal of the cavity should be to dump power into the free electron
cloud that forms."*

✅ **AND IT STRENGTHENS THE DECISION ABOVE.** The field couples to FREE charge —
Drude sigma IS electron momentum transfer. Bound electrons appear as
**permittivity, not loss**: the quartz torch's eps = 9.39 STORES energy, it does
not absorb it.

🔴 **SO AT sigma = 0 THERE IS NOTHING TO COUPLE TO.** The plasma region is
electromagnetically vacuum, `eta_plasma` = 0, and **a perfectly matched cold
cavity delivers 1 kW into the copper walls.** That is a stronger statement than
this file's earlier one (*"the cold field falls short of breakdown"*): even
granting a perfect match AND a sufficient field, the power has nowhere useful to
go until free electrons exist.

🔑 **AND IT CLOSES WITH WHAT IS ALREADY ESTABLISHED.** `h3-field-01` (2026-08-26):
**cavity-only ignition does not exist — 13x short at best**, bore field
0.020 MV/m against N2 breakdown ~3 MV/m. A striker is therefore mandatory, and
**the cavity's job BEGINS once the seed cloud exists.** Cold coupling is not a
design objective at all.

➡️ **WHICH IS THE QUESTION `h3-q0map-01` NOW ANSWERS.**
🔴 **AND A MAGNITUDE TUNER WILL EXIST.** User, 2026-09-06: *"'no magnitude tuner
exists' is wrong as stated: it will be there, but has not yet been specified
because we don't have enough information yet."* ⚠️ **THIS IS THE SECOND TIME I
WROTE THAT ERROR IN ONE SESSION** — it was corrected once above and restated here
anyway. `../control-loop/` item 2 says magnitude tuning is UNSOLVED; four
PIN-diode candidates were rejected. Unsolved is not absent, and it is not
impossible.

✅ **SO THE MAP'S OUTPUT IS A RANGE, NOT A POINT.** The plasma travels from a
striker-made seed to the developed state, and the map gives absorbed power versus
sigma along that path. That yields **the span of `cavity.Q_ext` needed to stay
matched across the trajectory** — which IS the missing information the tuner
specification is waiting on. A single match point is what you would want only if
the coupling were frozen; it is not.

⚠️ **The question therefore has two answers, and both are useful:** where power
delivery COLLAPSES (a bottleneck the tuner must clear, or the fixed geometry must
be placed to avoid), and how WIDE the required `Q_ext` span is (the tuner's
range). If the span is narrow, a fixed coupler may suffice after all.

⚠️ **NOT ANSWERED HERE, and it is a plasma question:** what sigma the striker
actually leaves behind, and whether the cloud grows or decays at each sigma. The
map gives the EM half — power in versus state — not the kinetics.

## ✅ DISCHARGED 2026-09-07 11:57Z — instance shut down

**User:** *"Going to bed, please run the instance as far as you can, and then
turn it off"*

    ops/go ops/shutdown.sh     # syncs, UNMOUNTS /opt/amip, verifies, powers down

⚠️ In a FILE, not in a head or a session. This is the shape that fails: a final
step nobody is awake to notice was skipped. Discharged once already on
2026-09-05; the obligation does not carry over, it is re-earned each time.

🔑 **"AS FAR AS YOU CAN" — the queue, in order:**
1. `h3-q0map-01` finishes rows 6-8 (sigma 0.0826 / 0.2753 / 2.1746).
2. Analyse: does `sigma * Q_plasma = 125.7` hold, and where does it BEND?
   That bend is the shielding transition and it should coincide with the probe
   profile falling below TE011's shape. Two independent signatures of the same
   physics — if only one moves, distrust it.
3. ⚠️ IF the law holds to row 7 and breaks at row 8, the transition is somewhere
   in **sigma 0.28 - 2.17, an 8x gap with no points in it.** Filling it is the
   obvious follow-on and is prepared as `h3-q0map-02`. Launch ONLY if rows 6-8
   actually land — do not launch on a guess about where the bend is.
4. Then shut down. **Do not leave it idle while deciding.**

✅ **DISCHARGED.** All four queue items done: `h3-q0map-01` finished (8 rows),
the law was analysed and DID bend, `h3-q0map-02` was launched on that evidence
(4 rows, filling the 8× gap), and `ops/go ops/shutdown.sh` ran clean —
0 live processes, `/opt/amip` unmounted AND VERIFIED, instance confirmed
unreachable after 10 s. **Both artefacts were verified LOCAL before the halt:**
12 points, all fitted, all with probe fields.

⚠️ Nothing was started that could not finish and be fetched first, as this note
required.

## ➡️ WHERE THE PROGRAMME STANDS, AND WHAT IS WORTH DOING NEXT (2026-09-07)

### ✅ THE CAVITY SIDE IS ESSENTIALLY DONE

`h3-q0map-01/-02` measured twelve plasma states on the design cavity. What that
settled, and each is in `Q_LEDGER.md`:

1. **`cavity.Q_ext.loaded` is geometric** — 2.3 % over a 520× change in
   `cavity.Q0.loaded`, 0.2 % from an independently recorded value.
2. **The coupling branch resolves by series consistency**, not by phase.
3. **`cavity.Q0.loaded` is interpolable** across four decades of sigma.
4. **Shielding is a gradient, not a threshold**, and is NOT the eps = 0 crossing.
5. **82.6 % of incident power reaches the electrons at sigma ≈ 0.02**, with the
   PLAIN loop, at VSWR 1.63.

🔴 **AND IT DISSOLVED THE COUPLER PROBLEM RATHER THAN SOLVING IT.** The design
does not need a stronger coupler; it needs to know WHICH SIGMA it runs at. The
operating point is worth **22×** and the coupler ~1.4×.
`ret:three-x-more-coupling`

### 🔴 SO THE BLOCKER IS NOT IN THIS PROGRAMME

Everything above is a function of sigma. **Which sigma the discharge sits at is a
PLASMA question** and resonance cannot answer it — `ret:operating-point-79e18`
stands, and `CLAUDE.md` already says resonance is blocked on `../spectroscopy/`.
⚠️ The sigma→`plasma.n_e` mapping ALSO needs the unmade `NU_M` decision
(1e11 vs 6.295e10, worth 3.4× in eps).

### ➡️ THE CANDIDATES, HONESTLY RANKED

| | what | cost | why / why not |
|---|---|---|---|
| **A** | 🔑 **Decide `NU_M`** — bind `drude()` to `plasma_state(T)` or keep 1e11, and say which | ~0, one argument at three call sites | **Cheapest thing on the list.** Until it is decided, every sigma→density statement is provisional. `h3_loaded.py` demanded this decision and it was never made. ⚠️ Changing it moves eps 3.4× and re-labels the whole map's x-axis |
| **B** | Re-run ONE map row with the state-consistent collision rate | ~40 min | Turns A from a judgement into a measurement: how far does the curve actually move? |
| **C** | Probe-based E/N at the optimum | ~40 min | The probes work and are validated. Gives the field the electrons actually see at sigma 0.02 — the input a kinetics calculation needs |
| **D** | Same map for the AZIMUTHAL coupler | ~6 h | Settles the coupler family with a like-for-like comparison. ⚠️ `DISCLOSURE.md` claims azimuthal; its loaded `Q_ext` has never been measured (`h3-azimload-02` found NO resonance) |
| **E** | ~~gap2 lever sweep~~ | — | 🔴 **NOT WORTH IT.** Barrel-only, and a stronger coupler is only wanted if the discharge sits HIGH — which is unknown, and if it does, VSWR 102 is beyond any tuner anyway |
| **F** | ~~sf 0.6 convergence~~ | — | 🔴 **NOT WORTH IT.** `coupling.beta.loaded` is unconverged at ~9 %, and every conclusion above survives that: the 22× operating-point effect dwarfs it |

🔴 **RE-RANKED 2026-09-07 — A IS DEMOTED.** User: *"a plasma_state of 5245K is
the result of Nitrogen re-association... the 1e11 figure would be accurate for
Nitrogen entering the torch. We're interested in the boundary in-between."*
`NU_M` is not one number to decide, it is a RANGE the gas traverses
(~1.6e12 → 6.3e10). And the 82.6 % optimum at sigma ≈ 0.02 is reachable at EVERY
stage of that boundary, with eps staying in 0.963–0.999 — inside the map's
densely-sampled rows. **So nu does not gate the cavity design.**
⚠️ I had called A a blocker because "every sigma→density statement is
provisional". True, but it is provisional for the PLASMA side's ionisation
target, not for ours. Fixing `drude()`'s inconsistency is HOUSEKEEPING.
`Q_LEDGER.md § THE OPTIMUM SURVIVES THE COLLISION-RATE QUESTION`

🔑 **RECOMMENDED NOW: C, then D.**
- **C — probe-based E/N at the optimum (~40 min).** Promoted to first. The probes
  are validated to 0.6 % and already wired. E/N at sigma ≈ 0.02 is exactly the
  input a kinetics calculation of the transit needs, and kinetics is now the
  binding question. ⚠️ It also needs an ELECTRON TEMPERATURE to become a rate;
  resonance can supply the field, not T_e.
- **D — the same map for the AZIMUTHAL coupler (~6 h).** The one real open design
  question, and `DISCLOSURE.md` claims that family. ⚠️ Worth it only if the
  discharge does NOT sit near sigma 0.02 — if it does, the plain barrel loop
  already delivers 82.6 % and the family choice is nearly moot.
- **A — bind `drude()` to a stated nu (~0).** Do it as housekeeping when next
  editing that file. Not a gate.
- **B — re-run one row at a different nu.** ⚠️ NOW REDUNDANT: the analysis above
  answers what it would have measured, for free.

⚠️ **D IS THE ONE REAL OPEN DESIGN QUESTION**, and it is expensive. Worth it only
once the operating sigma is known: if the discharge sits near 0.02, the plain
barrel loop already delivers 82.6 % and the family choice is nearly moot.

### ⚠️ HOUSEKEEPING, NOT SCIENCE

- `CONVENTIONS.md` is at **699/700 lines** — the next rule trips the size gate.
  A pruning pass is due, and it is a judgement call about what is still
  load-bearing, so it needs the user.
- `h3_driven._report` crashed twice on prescribed sweeps (`{ne}` formatting).
  Fixed locally; the fix has NOT been exercised on a real run.

## ⏸ PROPOSED — RING EMF DIRECT FROM PALACE, VIA MAGNETIC SURFACE FLUX

**User, 2026-09-07:** *"I think we can get this in Palace by defining a 2D disk
surface that represents the torch cross-section, integrating the Hz flux through
it, and multiplying by the angular frequency ω."*

✅ **SUPPORTED, AND BETTER THAN THE CURRENT ROUTE.** `EMF = ω·Φ`,
`Φ = ∫B·n dA`. Verified against the installed schema:
- `Boundaries.Postprocessing.SurfaceFlux` with **`Type: "Magnetic"`** integrates
  the magnetic flux density over a boundary.
- It works on **INTERNAL** surfaces — `TwoSided` and `Center` exist precisely for
  them, and a torch cross-section disc is one.
- `geometry.py` already tags internal faces (`TAG_PORT = 91` is an internal
  lumped-port face), so this is established practice, not new machinery.

🔑 **WHY IT BEATS WHAT WAS USED ON 2026-09-07.** The 115 kV peak EMF was computed
from `U = Q_L·P_del/ω` plus the ANALYTIC bare-cylinder TE011 shape — no groove, no
loop, no torch dielectric. The probes agree with that shape to ≤1 % INSIDE the
bore but `field_peak` measured **−14 %**, so the peak figure is optimistic by
about that much. **A flux integral carries none of that error.**

➡️ **WHAT IT NEEDS**
1. `geometry.py`: meshed interior discs at **z = 0** (the mid-plane, where `B_z`
   peaks), at **r = 2.0 / 4.25 / 8.5 mm** — the probe radii, so the two methods
   cross-check. ⚠️ Genuine meshed surfaces, not cut planes.
2. `solveconf`: a `SurfaceFlux` entry per disc, `Type: "Magnetic"`.
   ⚠️ **Set `TwoSided`/`Center` EXPLICITLY** — these are interior surfaces and the
   normal orientation decides the sign; inheriting the default makes it ambiguous.
3. An evaluation layer step: `EMF(r) = 2·pi·f·Phi(r)`.

⚠️ **IT IS A NEW MESH FAMILY** — adding tagged interior surfaces changes the mesh,
so it CANNOT reuse the cached meshes `h3-q0map-*` and `h3-azimmap-01` ran on. Any
comparison against those maps is cross-mesh (§4b), though the mesh-to-mesh floor
measured 1e-11 on the loaded quantities, so that is a small price.

🔑 **AND THE NUMBER IS STATE-DEPENDENT, BY CONSTRUCTION.** `ωΦ` is the EMF for a
ring at that radius, but the solved `B_z` ALREADY includes the back-EMF of the
induced plasma current. So it is the SELF-CONSISTENT drive, not the vacuum one —
which is what is wanted, but it means the EMF cannot be quoted independently of
sigma. ⚠️ Do not treat a single flux number as a property of the cavity.

➡️ **VALUE:** it turns the ring EMF from a derived estimate into a measurement,
and the radial profile is what the ~18× drive gradient across the annulus
(350 V inner → 6.2 kV outer at 1 kW) currently rests on.

## ⚠️ WHAT `DISCLOSURE.md` ACTUALLY IS — AND WHY THE AZIMUTHAL RUN'S PURPOSE CHANGED

**User, 2026-09-07:** *"I also forget what we were chasing with the azimuthal
loop. I think it was to see if it would change how we could achieve Beta = 1
loaded with a 7.9e18 plasma, which turned out to be completely wrong for
different reasons."*

✅ **CORRECT — THE ORIGINAL GATE IS CLOSED, BY A DIFFERENT RIG.** It read:
*"comes back ~14,000 -> loaded Q_ext IS loop-set... comes back ~300 -> the loop
barely matters loaded."* **Resolved to LOOP-SET** — but by `h3-q0map-01`, where
`cavity.Q_ext.loaded` held to 2.3 % across a 520× change in `cavity.Q0.loaded`.
🔴 **And the target it fed is retracted** (`ret:three-x-more-coupling`): at
sigma 2.175 only 3.8 % of incident power reaches the electrons at ANY coupling.

🔴 **TWO CORRECTIONS TO WHAT I SAID ON 2026-09-07.**
1. I reported `DISCLOSURE.md` as **absent from the tree and unverifiable**. It is
   at the **REPO ROOT** (`axisymmetric-mip/DISCLOSURE.md`), 183 lines. I searched
   `experiments/resonance/` only — one level too deep.
2. I framed it as a proprietary claim, and said measuring the azimuthal arm as
   worse would be *"awkward"*. **It is a DEFENSIVE PUBLICATION** — *"published
   deliberately, without restriction"*, to place the design in the public domain
   as prior art. ⚠️ **It does not commit the programme to BUILDING the design**,
   so a measurement that ranks it below the barrel costs nothing and the
   publication stands regardless.

➡️ **SO THE RUN'S PURPOSE IS NOW NARROWER AND CLEANER:** not "settle a gate" and
not "protect a claim", but **measure how a published design performs against a
baseline that turned out stronger than expected.**

🔑 **AND THE DISCLOSURE IS RIGHT ABOUT THE TRAP.** Disclosure 2's substance is the
PARAMETERISATION: standoff = the WALL GAP (invariant under conductor
cross-section, unlike a centreline height) and **arc LENGTH, not angle** — it
calls this *"the part most easily got wrong."* That is exactly the convention
`h3-azimwidth-01` used to fit `arc^3.89`, and exactly why reasoning like "move it
closer to the wall to couple harder" is BACKWARDS: standoff sets both the wall gap
AND the enclosed area, so a smaller standoff links LESS flux.
