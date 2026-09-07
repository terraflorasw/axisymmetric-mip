#!/usr/bin/env python3
"""Find quantities quoted in PROSE without their qualifying coordinates.

🔑 User, 2026-09-04: *"The prose has to also include fully qualified names. So,
no 'beta at 7.9e18'."*

**Prose is the unenforced layer.** `audit_names.py` checks the store,
`verify_identities.py` checks artefacts, `preflight.py` checks code. Nothing
checked the documents — and the documents are what a human reads and quotes.

"beta at 7.9e18" names a density and nothing else. The same symbol at that same
density is **0.2476** on the design cavity and **0.3124** on the vacuum one, and
`coupling.beta.cold` is ~112 — a different branch entirely. A number without its
coordinates is not a measurement, it is a rumour.

WHAT IT FLAGS
  a quantity name adjacent to a numeric value, with a required qualifier missing
  from the same line (and, for table rows, from the header above).

⚠️ FALSE POSITIVES ARE EXPECTED and are not silenced by loosening the rule.
Narrative sentences legitimately discuss a quantity generically. Mark a reviewed
line with `q:ok` to silence it — the same explicit-escape approach as
`audit_stale.py`, chosen because keyword proximity was tuned three times on
2026-09-04 and was still wrong.
"""
import pathlib
import re
import sys

DOCS = ["KNOWN.md", "NEXT.md", "Q_LEDGER.md", "OPTIMIZER.md", "VERIFY.md",
        "HYPOTHESES.md", "PLAN.md", "INSTRUMENT.md"]

# quantity -> qualifiers that must appear near it. `state` is always required;
# `density` only once the state is loaded.
STATE = r"(cold|loaded|unloaded|bare)"
CAVITY = r"(design|vacuum|sapphire|no[- ]torch|torch)"
LOOP = r"(cap|barrel|azim|gap2|series[- ]gap|no[- ]loop|11x8|loop)"
DENSITY = r"(\d\.?\d*e\+?\d\d|n_e|ne\s*=|cold)"

QUANTS = {
    r"coupling\.beta|(?<![\w.])beta(?![\w.])": [("state", STATE), ("density", DENSITY),
                                                ("cavity", CAVITY), ("loop", LOOP)],
    r"Q_ext":  [("state", STATE), ("cavity", CAVITY), ("loop", LOOP)],
    r"(?<![\w.])Q0(?![\w.])": [("state", STATE), ("loop", LOOP)],
    r"(?<![\w.])Q_L(?![\w.])": [("state", STATE), ("loop", LOOP)],
    r"(?<![\w.])eta(?![\w.])": [("state", STATE), ("cavity", CAVITY)],
}
NUM = re.compile(r"\d")


def main():
    hits = 0
    for doc in DOCS:
        p = pathlib.Path(doc)
        if not p.exists():
            continue
        lines = p.read_text().split("\n")
        for i, line in enumerate(lines):
            if "q:ok" in line or line.lstrip().startswith(">"):
                continue
            # a fully-qualified canonical name carries its own coordinates
            probe = re.sub(r"(cavity|coupling|plasma)\.[A-Za-z_.]+", "", line)
            if not NUM.search(probe):
                continue
            ctx = (lines[i - 1] + " " + probe).lower() if i else probe.lower()
            for qpat, quals in QUANTS.items():
                m = re.search(qpat, probe)
                if not m:
                    continue
                # 🔑 A DEFINITION IS NOT A MEASUREMENT. `Q0 = Q_L(1+beta)` and
                # `1/Q_ext = 1/Q_L - 1/Q0` are algebra and need no coordinates;
                # `Q_ext = 9,117` is a value and needs all of them. Require an
                # actual NUMBER within a few characters of the quantity, so
                # generic prose stops firing. (First run: 351 hits, mostly
                # formulas. Refining the RULE, not loosening the qualifiers.)
                tail = probe[m.end():m.end() + 14]
                if not re.search(r"[=:~]?\s*[-+]?\d[\d,.]*", tail):
                    continue
                missing = [nm for nm, qp in quals
                           if not re.search(qp, ctx, re.I)]
                # ⚠️ do NOT rebind `m` here — it holds the quantity match used
                # above. Shadowing it worked only because of the break below.
                if "loaded" not in ctx:
                    missing = [x for x in missing if x != "density"]
                if missing:
                    hits += 1
                    print(f"  {doc}:{i+1}  missing {missing}")
                    print(f"      {line.strip()[:104]}")
                break
    print(f"\n  🔴 {hits} unqualified quantity mention(s)")
    print("  ⚠️ CANDIDATES. Narrative prose may legitimately be generic — mark a")
    print("     reviewed line with `q:ok`. Do NOT loosen the pattern instead:")
    print("     keyword proximity was tuned three times on 2026-09-04 and was")
    print("     still wrong, which is why the escape is explicit.")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
