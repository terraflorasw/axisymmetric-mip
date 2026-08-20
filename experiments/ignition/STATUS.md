# Status: superseded architecture, retained deliberately

**This experiment is the alumina dielectric-resonator ring — the MICAP/Radom
reverse-engineering. It is NOT AMIP work and was never updated for it.** It
models a ceramic ring inside a cylindrical enclosure; AMIP has no ceramic and
uses a cavity eigenmode. Current AMIP work is in
[`../waveguide/`](../waveguide/).

As of 2026-08-14, `refs/coupling-architecture.md` §0 names **AMIP** as the
architecture; this route was the previous decision.

## Why it is kept

1. **It is the baseline for AMIP's central claim.**
   `refs/axisymmetric-feed.md` §6 argues *"the ceramic buys compactness, not
   coupling"* from **Q × η = 47.5**, which is this experiment's D80 / scale 0.94
   result. Remove it and that claim loses its provenance.
2. **It is the fast path to a running plasma.** The ring is the only one of the
   candidate architectures known to work — MICAP ships. Building one for
   research is not what the patent constrains; selling one is
   (`refs/patent-landscape.md` §5). If a plasma is wanted before AMIP is
   validated, this design is complete.
3. **Its FINDINGS §5 documents the zombie-process trap** — `pgrep`/`ps` matching
   defunct processes because container PID 1 does not reap. Still live, and it
   bit the waveguide harness repeatedly.
4. The waveguide harness descends from this one. `geometry.py` there opens by
   explaining why it is a separate file rather than a reuse of this.

## What it established

| | |
|---|---|
| Patent dimensions do not reach 2.45 GHz | ~8–10% short with every parameter at its limit |
| Inverse design closes | ring at scale 0.874 lands TE on 2.450 GHz |
| Final geometry | D = 80 mm enclosure, ring scale 0.94, order-2 verified |
| Operating mode | TE 2.4170 GHz, Q 11,054, 56.7% of energy in the alumina |
| Ignition mode | TM₀₁₀ 2.4563 GHz, **+39 MHz** — mode-shift ignition closes |

⚠️ *Historical note: the ring's field was later measured (R5) at 6.09 kV/cm.*
🔴 **And as of 2026-08-15 the reduced-pressure route this section discusses is
dropped entirely** — AMIP ignites by capacitive electrode with argon as fallback.
The pressure figures below are retained as measurements, not as a plan.

⚠️ The ring's **field strength** was never computed, so its ignition margin is
unknown. 🔴 **R9 (2026-08-14) withdrew the "within 3%" reasoning**: the ring's Q
is 90.3% dielectric loss and its alumina tanδ is a placeholder, so Q × η spans
**8×** across plausible grades (9.4 to 77.5 against AMIP's 41.5). The ring's
field is now *measured* at 6.09 kV/cm for tanδ = 1×10⁻⁴ — but that spans
2.85–8.17 kV/cm, i.e. a 48–136 Torr start. **Quote the band, not the point.**

## Do not

- Treat its numbers as AMIP numbers. Different structure, different mode.
- Re-run it expecting to advance AMIP. It cannot.
