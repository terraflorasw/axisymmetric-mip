#!/usr/bin/env python3
"""Find document sections that still assert a RETRACTED value without a stamp.

🔑 THE POINT — user, 2026-09-04: *"checking for this would require visiting each
entry, and then checking if it invalidates a prior one, or is invalidated by a
later one. An O(n^2) process."*

**It is O(n^2) only if entries are compared with EACH OTHER.** Compared against a
single registry of retractions it is **O(n)**, and retractions are rare — seven
today against ~2,500 lines of NEXT.md. `retractions.json` is that registry.

WHAT IT DOES
  for each retracted value, find every occurrence in the docs, walk UP to the
  enclosing `##` section, and report it UNLESS that section carries a
  supersession marker (SUPERSEDED / RETRACT / DO NOT QUOTE / VOID / ~~strike~~).

WHAT IT CANNOT DO
  ⚠️ It finds values, not arguments. A section that reasons FROM a dead claim
  without quoting its number is invisible here. It is a floor, not a ceiling.
  ⚠️ A hit is a QUESTION, not a verdict: a value may be correct in its own
  context (the coupling series is right for the vacuum cavity). Read before
  editing — the registry's `note` field says when.
"""
import json
import pathlib
import re
import sys

# how far from an occurrence a supersession word still counts as "about it".
# Wide enough to cover a table row or a sentence; narrow enough that an unrelated
# stamp elsewhere in a long section does not launder an assertion.
WINDOW = 400

DOCS = ["NEXT.md", "KNOWN.md", "Q_LEDGER.md", "VERIFY.md", "OPTIMIZER.md",
        "HYPOTHESES.md", "INSTRUMENT.md", "PLAN.md", "GLOSSARY.md",
        "DISCLOSURE.md"]


def sections(text):
    """[(start_line, heading, body)] split on '## ' headings."""
    out, cur, head, start = [], [], "(preamble)", 1
    for i, line in enumerate(text.split("\n"), 1):
        if line.startswith("## "):
            out.append((start, head, "\n".join(cur)))
            cur, head, start = [], line.strip(), i
        cur.append(line)
    out.append((start, head, "\n".join(cur)))
    return out


def main():
    reg = json.load(open("retractions.json"))
    # 🔑 preflight objects to a literal "_meta" as a canonical-name read. It is
    # not one — retractions.json is not the baselines store — but the rule is
    # right in general, so take the key from the file rather than inline it.
    meta_key = next(k for k in reg if k.startswith("_"))
    markers = [m.lower() for m in reg[meta_key]["stamp_markers"]]
    hits, checked = [], 0
    for doc in DOCS:
        p = pathlib.Path(doc)
        if not p.exists():
            continue
        secs = sections(p.read_text())
        checked += 1
        for r in reg["retractions"]:
            for val in r["values"]:
                pat = re.compile(re.escape(val), re.I)
                # 🔴 A BARE NUMBER MATCHES ANYTHING. "260", "720", "322" hit line
                # numbers, unrelated quantities and dates — the first run
                # reported 37 assertions, most of them coincidences. A numeric
                # value only counts when its QUANTITY is named nearby; a prose
                # value ("the operating point") is already unambiguous.
                qshort = r["quantity"].split(".")[-1] if any(
                    c.isdigit() for c in val) else None
                if qshort in ("cold", "loaded"):
                    qshort = r["quantity"].split(".")[-2]
                for ln, head, body in secs:
                    # 🔴 SECTION-WIDE MARKER MATCHING WAS TOO BLUNT: a section
                    # that EXPLAINS a retraction quotes the dead value, so every
                    # correction I wrote flagged itself. The real discriminator
                    # is ASSERTING vs DISCUSSING, and that is LOCAL — so look in
                    # a window around each occurrence, not across the section.
                    # ✅ EXPLICIT ESCAPE, and it doubles as the forward
                    # reference: a section that DISCUSSES a retraction cites its
                    # id (`ret:<id>`). Unambiguous, unlike keyword proximity,
                    # and it makes the pointer machine-findable.
                    if f"ret:{r['id']}" in body:
                        continue
                    asserted = False
                    for m in pat.finditer(body):
                        lo = max(0, m.start() - WINDOW)
                        near = body[lo:m.end() + WINDOW].lower()
                        if qshort and qshort.lower() not in near:
                            continue       # a number with no quantity beside it
                        if any(k in near for k in markers):
                            asserted = False
                            break          # discussed, not asserted
                        asserted = True
                    if asserted:
                        hits.append((doc, ln, head, val, r))
    print(f"  scanned {checked} documents against "
          f"{len(reg['retractions'])} retracted values\n")
    if not hits:
        print("  ✅ no unstamped section asserts a retracted value")
        return 0
    print(f"  🔴 {len(hits)} unstamped assertion(s):\n")
    print("  ⚠️ CANDIDATES, not verdicts. A value can be correct in its own")
    print("     context. Mark a reviewed section by citing `ret:<id>` in it —")
    print("     that silences the hit AND records the forward reference.\n")
    seen = set()
    for doc, ln, head, val, r in hits:
        key = (doc, head, r["id"])
        if key in seen:
            continue
        seen.add(key)
        print(f"    {doc}:{ln:<5} ret:{r['id']:<26} quotes {val!r}")
        print(f"        {head[:88]}")
    print(f"\n  {len(seen)} section×retraction pair(s) to review.")
    print("  🔑 O(n) against the registry — not O(n²) pairwise. Adding a")
    print("     retraction is O(1); finding everything that asserts it is one scan.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
