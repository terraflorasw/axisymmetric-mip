#!/usr/bin/env python3
"""Canonical NAMES for measured values, with CONTEXT as a first-class axis.

🔴 WHY THIS EXISTS. Every serious error on 2026-08-24/25 was one shape: a name
that meant different measured things in different contexts, and a value imported
across that boundary without anyone noticing.

    Q_ext    9,231 (eigen pair, NO-torch mesh)          h3_loopq
             9,117 (eigen pair, vacuum-torch mesh)      h3_step3 V1_ANCHOR
             8,462 (driven S11 dip, vacuum-torch mesh)  h3_driven
      -> I published a "9% eigen-vs-driven disagreement" that compared the
         first to the third. Different cavities. CONVENTIONS 7aq.

    cold Q0  43,422 / 43,523 / 29,037 / 40,645
      -> four numbers, all "the cold Q0", differing by mesh, by extraction
         method, and by coupling branch. CONVENTIONS 7at.

    eta ref  44,384 / 29,854 / 12,368 / 43,523
      -> CONVENTIONS 7c has caught this ONE name four times.

🔑 THE FIX IS NOT MORE CAREFUL COPYING. It is that a name alone must not resolve.
`get("cavity.Q_ext")` is a REFUSAL; `get("cavity.Q_ext", solver="driven_dip",
mesh="vacuum_torch", ne=0.0)` is an answer. Ambiguity raises and PRINTS THE
ALTERNATIVES, which is exactly the moment the mistake was being made.

⚠️ THIS GENERALISES THREE GUARDS THIS PROGRAMME ALREADY HAND-ROLLED:
    e0k2_anchor.wall_sigma()  binds baselines.json and REFUSES if absent
    h3_driven.Q_REF_CONFIG    asserts groove/loop match before using Q_REF
    eigen_cfg GATE 4 / GATE 5 refuse an implicit port BC / a mismatched mesh
Same instinct each time, re-implemented each time, covering one value each.

USAGE
    from values import get, entries, describe
    q = get("cavity.Q_ext", solver="eigen_pair", mesh="vacuum_torch", ne=0.0)
    describe("cavity.Q_ext")        # every recorded context, for a human
"""
import json
import pathlib

STORE = pathlib.Path(__file__).with_name("baselines.json")


class Ambiguous(RuntimeError):
    """More than one recorded value matches. The caller under-specified."""


class Unknown(RuntimeError):
    """No recorded value matches. Never guess; never fall back to a default."""


def _load(store=None):
    """The global store, or a run's own copy (baseline-<slug>.json).

    🔑 A rig reads from ITS OWN copy so the global can move without changing
    what the run used. Same schema either way.
    """
    return json.loads(pathlib.Path(store or STORE).read_text())


def _rows(name, store=None):
    d = _load(store)
    if name not in d:
        known = sorted(k for k in d if not k.startswith("_"))
        raise Unknown(f"'{name}' is not a canonical name. Known: {known}")
    e = d[name]
    if "contexts" not in e:          # legacy single-value entry (wall.conductivity)
        return [{"value": e["value"], "context": {}, "_legacy": True, **e}]
    return e["contexts"]


def _fmt(r):
    c = " ".join(f"{k}={v!r}" for k, v in sorted(r.get("context", {}).items()))
    tag = (" 🔴RETRACTED" if r.get("retracted")
           else " ⚠️TENTATIVE" if r.get("status") == "tentative" else "")
    return (f"    {r['value']!r:>12}  [{c}]  rig={r.get('rig','?')} "
            f"{r.get('date','?')}{tag}")


def entries(name, include_retracted=False, allow_tentative=False, store=None):
    """Recorded rows for `name`.

    🔴 TENTATIVE IS EXCLUDED BY DEFAULT. A value that is measured but not yet
    trustworthy is exactly the kind that used to get asserted because there was
    nowhere else to put it (slug.promote's sideline). It is recorded and
    visible, and it does NOT silently become an input.
    """
    out = []
    for r in _rows(name, store):
        if r.get("retracted") and not include_retracted:
            continue
        if r.get("status") == "tentative" and not allow_tentative:
            continue
        out.append(r)
    return out


def describe(name):
    e = _load()[name]
    out = [f"{name}  ({e.get('unit','1')}) — {e.get('description','')}"]
    out += [_fmt(r) for r in _rows(name)]
    return "\n".join(out)


def get(name, allow_tentative=False, store=None, **ctx):
    """The value recorded for `name` in EXACTLY this context, or a refusal.

    🔴 A partial context that matches several rows RAISES. That is the point:
    the caller who has not said which mesh/solver/density they mean does not
    have an answer, and silently getting one is how 7aq happened.
    """
    rows = entries(name, allow_tentative=allow_tentative, store=store)
    hit = [r for r in rows
           if all(r.get("context", {}).get(k) == v for k, v in ctx.items())]
    if not hit:
        tent = [r for r in entries(name, allow_tentative=True, store=store)
                if r.get("status") == "tentative"
                and all(r.get("context", {}).get(k) == v for k, v in ctx.items())]
        extra = ("\n  ⚠️ A TENTATIVE value matches. It is deliberately not "
                 "returned; pass allow_tentative=True and say so at the call "
                 "site, or promote it once it has a verification.\n"
                 + "\n".join(_fmt(r) for r in tent)) if tent else ""
        raise Unknown(
            f"no value for '{name}' with context {ctx}.{extra}\n"
            f"  recorded:\n" + "\n".join(_fmt(r) for r in rows) +
            f"\n  🔑 Do not substitute the nearest one — that is CONVENTIONS "
            f"7aq. Measure it in THIS context, or state why another transfers.")
    if len(hit) > 1:
        keys = sorted({k for r in hit for k in r.get("context", {})}
                      - set(ctx))
        raise Ambiguous(
            f"'{name}' is ambiguous under context {ctx} — {len(hit)} match:\n"
            + "\n".join(_fmt(r) for r in hit) +
            f"\n  🔑 Discriminate with: {keys}")
    return hit[0]["value"]


if __name__ == "__main__":
    import sys
    d = _load()
    names = sys.argv[1:] or sorted(k for k in d if not k.startswith("_"))
    for n in names:
        print(describe(n));  print()
