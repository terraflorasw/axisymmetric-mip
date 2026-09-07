#!/usr/bin/env python3
"""Audit CONVENTIONS.md against INCIDENTS.md, and against its own size limit.

🔴 WHY. On 2026-09-04 CONVENTIONS was split: the RULES stayed, 79 incident
narratives moved to INCIDENTS.md. The distillation was done by hand and **lost
five real rules**, one of which had been written the previous day. A hand-made
canon needs a machine-checked contract with its evidence.

WHAT IT CHECKS
  1. COVERAGE     every incident has a rule citing it (except declared status-only)
  2. DANGLING     every id cited by a rule actually exists
  3. SIZE         the canon stays readable — that is a FUNCTIONAL requirement,
                  not aesthetics: at 3,454 lines the file stopped being consulted
                  and its rules were re-discovered and re-appended
  4. RECURRENCE   rules cited 3+ times, i.e. where the discipline does not hold

⚠️ It cannot check that a rule is RIGHT, or that the repo OBEYS it. `preflight.py`
and `verify_identities.py` do the obeying half, for the rules that are mechanical.
"""
import pathlib
import re
import sys

CANON = "CONVENTIONS.md"
EVIDENCE = "INCIDENTS.md"
# 🔑 A LIMIT, NOT A TARGET. The canon must fit in one reading. If a genuine rule
# does not fit, MERGE rules — do not raise this number. Raising it is how the
# file got to 3,454 lines the first time.
MAX_CANON_LINES = 700


def ids_in(text):
    return set(re.findall(r"^#{2,3} (7[a-z]+)[.— ]", text, re.M))


def citations(text):
    """{id: times cited} across all *(...)* citation groups."""
    out = {}
    for grp in re.findall(r"\*\(([^)]*)\)\*", text):
        for i in re.findall(r"\b(7[a-z]+)\b", grp):
            out[i] = out.get(i, 0) + 1
    return out


def status_only(text):
    m = re.search(r"STATUS-ONLY INCIDENTS[^:]*:\*\*\s*(.+?)\n\n", text, re.S)
    return set(re.findall(r"`(7[a-z]+)`", m.group(1))) if m else set()


def main():
    canon = pathlib.Path(CANON).read_text()
    ev = pathlib.Path(EVIDENCE).read_text()
    inc, cited, skip = ids_in(ev), citations(canon), status_only(canon)
    nlines = len(canon.split("\n"))
    fail = []

    lost = sorted(inc - set(cited) - skip)
    if lost:
        fail.append(f"{len(lost)} incident(s) with NO rule in canon: {lost}")
    dangling = sorted(set(cited) - inc)
    if dangling:
        fail.append(f"{len(dangling)} dangling citation(s): {dangling}")
    if nlines > MAX_CANON_LINES:
        fail.append(f"canon is {nlines} lines, over the {MAX_CANON_LINES} limit "
                    f"— MERGE rules, do not raise the limit")

    print(f"  {CANON}: {nlines} lines · {EVIDENCE}: {len(inc)} incidents · "
          f"{len(cited)} cited · {len(skip)} status-only")
    # 🔴 THE METRIC WAS BACKWARDS TWICE. v1 counted ids cited by many RULES (an
    # incident that taught several lessons). v2 fixed the direction but scanned
    # LINE by line, so a citation on a bullet's CONTINUATION line was invisible —
    # and the worst offender ("no constants in scripts", 5 ids) is exactly that
    # shape, so the metric reported nothing and looked like good news.
    # ✅ v3 scans per BULLET: a rule runs from "- " to the next bullet or heading.
    bullets, cur = [], None
    for line in canon.split("\n"):
        if re.match(r"^\s*[-|] ", line):
            if cur:
                bullets.append(cur)
            cur = line
        elif cur is not None and line.strip() and not line.startswith("#"):
            cur += " " + line.strip()
        elif line.startswith("#"):
            if cur:
                bullets.append(cur)
            cur = None
    if cur:
        bullets.append(cur)

    hot = []
    for b in bullets:
        n = len({i for grp in re.findall(r"\*\(([^)]*)\)\*", b)
                 for i in re.findall(r"\b7[a-z]+\b", grp)})
        if n >= 3:
            rule = re.sub(r"\*\([^)]*\)\*", "", b)
            rule = re.sub(r"[*`]|^\s*[-|]\s*|[🔴⚠️✅🔑]", "", rule).strip()
            hot.append((n, rule[:76]))
    if hot:
        print("\n  🔑 RULES LEARNED REPEATEDLY — where the discipline does not hold:")
        for n, rule in sorted(hot, reverse=True):
            print(f"      learned {n}x  {rule}")

    # 🔴 THE BUILD QUEUE (§7.0). A rule without a refusal is a wish: every rule
    # that held on 2026-09-04 was machine-enforced, and every rule violated that
    # day was documented only. So the useful ranking is not "most violated" but
    # "most violated AND still unenforced" — that is where a check buys the most.
    queue = []
    for b in bullets:
        cites = {i for grp in re.findall(r"\*\(([^)]*)\)\*", b)
                 for i in re.findall(r"\b7[a-z]+\b", grp)}
        if len(cites) < 3:
            continue
        if "⚙️" in b and "PARTIAL" not in b:
            continue                       # fully enforced
        state = "PARTIAL " if "PARTIAL" in b else ("UNENFORCED" if "🖐️" in b
                                                   else "UNTAGGED  ")
        rule = re.sub(r"\*\([^)]*\)\*", "", b)
        rule = re.sub(r"[*`]|^\s*[-|]\s*|[🔴⚠️✅🔑⚙️🖐️]", "", rule).strip()
        queue.append((len(cites), state, rule[:64]))
    if queue:
        print("\n  🔴 BUILD QUEUE — learned 3+ times and NOT fully enforced:")
        for n, state, rule in sorted(queue, reverse=True):
            print(f"      {n}x  {state}  {rule}")
        print("      ➡️ adding enforcement to one of these beats adding a rule.")

    if fail:
        print("\n  🔴 AUDIT FAILED:")
        for f in fail:
            print(f"      {f}")
        return 1
    print("\n  ✅ canon covers every incident, no dangling citations, within size")
    return 0


if __name__ == "__main__":
    sys.exit(main())
