#!/usr/bin/env python3
"""Find UNDERSPECIFIED quantities in baselines.json.

🔑 User, 2026-09-04: *"It's probably pervasive, not just beta. Every name in
every record has to be audited for underspecification."*

A name is underspecified when the values recorded under it differ along a
coordinate the caller is not obliged to state. Two failure shapes, and the
second is the dangerous one:

  VARYING-NOT-REQUIRED   the coordinate is in every context and its value
                         differs, but `required_context` does not demand it.
                         A query omitting it gets `Ambiguous` — a REFUSAL, so
                         this is a nuisance, not a silent wrong answer.

  🔴 PARTIALLY RECORDED  the coordinate is in SOME contexts and absent from
                         others. A query naming it matches ONLY the rows that
                         happen to record it and SILENTLY EXCLUDES the rest;
                         a query omitting it may match one row by accident.
                         **This is how `cavity.Q_ext.cold` handed a barrel run
                         the cap loop's 9,231.**

⚠️ SCOPE. This audits the STORE. It cannot audit prose (a table headed "Q_ext"
carries no coordinates at all — that is what `Q_LEDGER.md` is for) and it cannot
audit a coordinate nobody ever recorded: `size_factor` varies across every run
in this programme and appears in NO context, so it is invisible here by
construction. Absence of a coordinate is not evidence it does not matter.
"""
import json
import pathlib
import sys


def audit(store="baselines.json"):
    b = json.loads(pathlib.Path(store).read_text())
    rows = []
    for k in sorted(x for x in b if not x.startswith("_")):
        ctxs = (b[k] or {}).get("contexts") or []
        if len(ctxs) < 2:
            continue
        cs = [c.get("context", {}) for c in ctxs]
        keys = set().union(*[set(c) for c in cs])
        everywhere = {x for x in keys if all(x in c for c in cs)}
        req0 = set((ctxs[0].get("required_context") or []))
        # 🔑 A PARTIAL COORDINATE IS SAFE IF A REQUIRED ONE DETERMINES IT.
        # `port_bc` exists only for eigen rows and `extraction` only for driven
        # rows — but `solver` is REQUIRED, so once the caller names the solver
        # every surviving row agrees on whether that coordinate is present.
        # Flag only coordinates that are still ragged WITHIN a required-key group.
        partial = []
        for x in sorted(keys - everywhere):
            groups = {}
            for c in cs:
                g = tuple(sorted((r, str(c.get(r))) for r in req0))
                groups.setdefault(g, []).append(x in c)
            if any(len(set(v)) > 1 for v in groups.values()):
                partial.append(x)
        varying = sorted(x for x in everywhere
                         if len({str(c[x]) for c in cs}) > 1)
        req = set(ctxs[0].get("required_context", []))
        rows.append((k, len(ctxs), varying, partial, sorted(req)))
    return rows


def main():
    rows = audit()
    hard = [r for r in rows if r[3]]                      # partially recorded
    soft = [r for r in rows if not r[3] and set(r[2]) - set(r[4])]
    for k, n, varying, partial, req in rows:
        mark = "🔴" if partial else ("⚠️ " if set(varying) - set(req) else "✅")
        print(f"  {mark} {k:<30} {n} contexts  varies={varying}  required={req}")
        if partial:
            print(f"        🔴 PARTIALLY RECORDED: {partial} — a query naming one "
                  f"of these silently excludes the rows that omit it")
    print()
    print(f"  🔴 {len(hard)} key(s) partially recorded (silent-exclusion risk)")
    print(f"  ⚠️  {len(soft)} key(s) vary along a coordinate that is not required "
          f"(refusal risk, not silent)")
    print("\n  ⚠️ NOT AUDITABLE HERE: `size_factor` varies across every run in the "
          "programme\n     and appears in NO recorded context — invisible by "
          "construction.\n     See OPTIMIZER.md § THE SCHEMA CHANGE TO MAKE NOW.")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
