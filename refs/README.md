# refs — citations, and which PDFs may live here

🔴 **PDFs in `refs/` are DEFAULT-DENY in `.gitignore`.** This repo carries
`LICENSE-CODE`, `LICENSE-HARDWARE` and `DISCLOSURE.md` — it is meant to be
published — so committing a publisher PDF is redistribution, not filing.
**Being able to READ a paper is not permission to REDISTRIBUTE it.**

➡️ **THIS FILE IS THE RECORD.** Every reference is cited here with the numbers
the programme actually uses, so **no conclusion depends on a PDF being present.**
A PDF is a convenience for the person at this machine; the citation is the
provenance. Checked in the file itself, not assumed from the publisher.

## Load-bearing references

| ref | used for | licence | PDF in repo? |
|---|---|---|---|
| **Engelhard, Scheffer, Maue, Hieftje & Buscher**, *Spectrochim. Acta B* **62** (2007) 1161–1168 | 🔑 **the Q1 anchor** — wall temperature of a gas-cooled Fassel torch | 🔴 **© 2007 Elsevier B.V., all rights reserved** | ❌ **no — must not be committed** |
| **Punjabi et al.**, *Processes* **7** (2019) 133 | Q3 gas-phase field vs sheath flow | ✅ CC BY 4.0 (verified in file) | ✅ yes |
| **Krupka, Huang & Tung**, *Meas. Sci. Technol.* **16** (2005) 1014–1020 | `torch.sapphire.permittivity` = 9.39 (quartz 4.43) | ⚠️ © 2005 IOP Publishing | ⚠️ **tracked — see below** |
| **Kuonen, Hattendorf & Günther**, *JAAS* **39**(5) (2024) 1388–1397 | the T_gas anchor, 5220/5270 K → n_e | ⚠️ © RSC — verify | ⚠️ tracked |
| **Zhang et al.**, *Processes* **12** (2024) 2505 | metal-acetate pyrolysis, `I_D/I_G` ranking | ✅ CC BY | ✅ yes |
| PNAS, *Linking plasma formation in grapes…* | 19× field enhancement, K/Na seeded ignition | ⚠️ verify | ⚠️ tracked |
| `ef0c01938_si_001` (ACS SI) | carbon-foam microwave plasma | ⚠️ verify | ⚠️ tracked |
| vendor datasheets (GC4400, MA4PK, UMX5601, Si PIN) | LDMOS / diode / component specs | ⚠️ vendor documents | ⚠️ tracked |

## 🔑 Engelhard 2007 — the numbers, because the PDF cannot be here

**Instrument:** SPECTRO CIROS CCD ICP-OES, free-running generator, **27.12 MHz**,
max 2 kW; load-coil ID 25 mm. IR camera Agema Thermovision 550. Emissivity of
fused quartz calibrated **0.50 → 0.35 over 873–1323 K**; transmission **20 %**
between 3.75 and 4.02 µm; both corrected for.

| | conventional Fassel | SHIP low-flow |
|---|---:|---:|
| RF power | **1400 W** | 1100 W |
| total Ar | **14 L/min** | 0.6 L/min |
| outer / plasma gas | **12 L/min** | — |
| auxiliary | **1 L/min** | 0.2 L/min |
| central carrier | **1 L/min** | 0.4 L/min |
| external cooling air | — | 40 m/s |
| **max wall T** | **725 ± 44 K** (after 3rd coil turn) | **1580 ± 95 K** (24 m/s air) |
| between first two turns | 525 ± 32 K · 560 ± 34 K | — |
| at 48 m/s cooling air | — | 1275 ± 75 K |
| min→max spread | 250 K | 750 K |

**Fused quartz properties (their Table 1):** strain temperature 1398 K ·
**maximum continuous working temperature 1433 K** · annealing 1493 K ·
short-term max 1573 K · softening 1983 K · **thermal conductivity 1.46 W/m·K at
373 K**.

**Their stated operating window:** above ~1073 K harms long-term torch stability;
below 373 K causes sample deposition.

🔑 **Why it matters here:** its conventional torch runs **12 / 1 / 1 L/min at
1400 W** against this programme's **10 / 1 / 1 at ~1000 W** — the closest
published match in the record, with the wall cooled by the **outer plasma gas**.
And its low-flow torch at **1580 K exceeds quartz's own 1433 K continuous
rating**, which is measured support for the sapphire decision.

## ✅ SOLVED — closed refs live on the VOLUME and move by an explicit command

> **STATED, user 2026-09-08:** *"we can store the refs on the instance, and rsync
> them. For example, we can have `refs/closed/` in gitignore and use a separate
> rsync command for it (since the default honors gitignore)."*

✅ **Implemented and VERIFIED 2026-09-08.** The premise was checked, not assumed:
`rsync.sh` carries `--filter=':- .gitignore'`, so the default sync really does
skip ignored paths.

| | |
|---|---|
| local | `refs/closed/` — gitignored wholesale |
| durable | **`/opt/amip/refs-closed/` on the VOLUME**, which survives spot reclamation |
| mover | **`ops/refs.sh {push\|pull\|list}`** — a separate, explicit command |
| record | **this file** — tracked, and carries the numbers |

🔴 **DELIBERATELY OUTSIDE `/opt/amip/repo`.** If closed refs sat inside the repo
copy, the next person reasoning about "what is in the repo" would be wrong on
both machines.

✅ **THE SAFETY PROPERTY WAS PROVEN, NOT ASSUMED.** After a real push and a real
default sync: the PDF is present at `/opt/amip/refs-closed/` and **absent from
`/opt/amip/repo/refs/`**.

### 🔑 AND THE TEST FOUND SOMETHING: rsync's `!` IS NOT git's `!`

A faithful dry run (same source root as `rsync.sh`) transfers **only `refs/` and
`refs/README.md`** — **every** PDF is excluded, including
`processes-07-00133-v3.pdf`, which git's `!refs/…` explicitly UN-ignores.

🔑 **One file, `.gitignore`, is read by two consumers that disagree about
negation.** In git, `!` un-ignores; in an rsync filter file `!` is a list-clearing
token, so the allow-lines simply do not do what they say when rsync reads them.
✅ **The disagreement is in the SAFE direction** — rsync excludes *more*, so no
closed ref can leak — and that is why this is recorded rather than fixed.
⚠️ **The consequence to know:** open-access PDFs do not reach the instance by the
default sync either. Nothing currently needs them there.
⚠️ **And the PDFs presently sitting in `/opt/amip/repo/refs/` are STALE RESIDUE**
from before this policy — `rsync.sh` has no `--delete`, so previously-synced
files persist. They are on a private machine, not redistributed, but the instance
does not reflect current policy.

*(Same shape as the record's recurring lesson: verify with the CONSUMER that
actually runs, not the one you had in mind.)*

## ⚠️ TO DECIDE — PDFs already committed before this policy existed

`Krupka`, `Kuonen`, the PNAS grape paper, the ACS SI and the vendor datasheets
are **already tracked**, from before this file existed. `.gitignore` does not
untrack them.

🔴 **Not actioned — this is the user's call**, and removing them from HISTORY is
a rewrite, not a delete. Options: leave as-is; `git rm --cached` so they stop
being distributed going forward; or rewrite history (`git filter-repo`;
`filter-branch` is deprecated). **The citations above mean the programme loses
nothing scientific either way.**

🔴 **ONE CAVEAT SPECIFIC TO THIS REPO, worth knowing BEFORE the rewrite.**
`DISCLOSURE.md` is a **defensive publication**, and its value is as *dated* prior
art. A history rewrite changes commit hashes; it can preserve author/committer
dates, but only if that is done deliberately. ➡️ **Preserve dates, and prefer
rewriting BEFORE anything is published or pushed** — once a hash is cited
somewhere external, rewriting orphans the reference. Same shape as §7.5's
identifier rule: an identifier others may hold is append-only.
