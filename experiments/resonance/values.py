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


# 🔴 RENAMING A CANONICAL NAME BROKE TWO CONSUMERS SILENTLY, 2026-08-25.
# `wall.conductivity` -> `wall.conductivity.s_per_m` (the unit-suffix rule, 7be)
# was applied to the store and to e0k2_anchor.wall_sigma(). It was NOT applied to
# solveconf.py or condcheck.py, which each did their OWN json lookup with the key
# hardcoded — and nothing knew they existed. A rig failed 40 minutes later with
# "wall conductivity not declared", from a guard whose whole purpose was to stop
# exactly that.
# ✅ An alias makes a rename NON-BREAKING. The old name resolves, loudly enough
# to find in a grep, and consumers migrate on their own schedule.
ALIASES = {
    "wall.conductivity": "wall.conductivity.s_per_m",
    "cavity.f0.cold": "cavity.f0.cold.ghz",
}


def _rows(name, store=None):
    d = _load(store)
    if name not in d and name in ALIASES:
        name = ALIASES[name]
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



# ---------------------------------------------------------------------------
# 🔑 User, 2026-08-25: *"we included units in the baselines schema, but that
# might leave room for this sort of thing. If the name includes the units, it's
# much harder to just read 'delta_f' and miss 'units: GHz'."*
#
# ✅ Right — and the case that prompted it proves NEITHER HALF IS SUFFICIENT
# ALONE. `e0e.result.json` had `delta_mhz` holding GHz: the name DID carry a
# unit, and the name was WRONG. A separate `unit:` field is missable; a unit in
# the name is loud but unverified. **So the name carries it AND the declared
# field checks it.**
#
#     cavity.f0.cold.ghz      unit "GHz"     ✅ agree
#     cavity.f0.cold.mhz      unit "GHz"     🔴 caught
#     cavity.f0.cold          unit "GHz"     🔴 caught — dimensional, unmarked
#     cavity.Q_ext            unit "1"       ✅ dimensionless: no suffix
UNIT_SUFFIX = {
    "GHz": "ghz", "MHz": "mhz", "kHz": "khz", "Hz": "hz",
    "S/m": "s_per_m", "K": "k", "W": "w", "A": "a", "V": "v",
    "mm": "mm", "m": "m", "s": "s", "ohm": "ohm", "pF": "pf",
    "deg": "deg",
}


def check_units(store=None):
    """Every dimensional name must END with its unit. Findings as (lvl, msg)."""
    d = _load(store)
    out = []
    for name, e in sorted(d.items()):
        if name.startswith("_") or not isinstance(e, dict) or "unit" not in e:
            continue
        u = e["unit"]
        want = UNIT_SUFFIX.get(u)
        tail = name.rsplit(".", 1)[-1]
        if u == "1":
            if tail in UNIT_SUFFIX.values():
                out.append(("ERROR", f"{name}: unit is '1' (dimensionless) but "
                                     f"the name ends in {tail!r}, a unit."))
            continue
        if want is None:
            out.append(("WARN", f"{name}: unit {u!r} has no registered suffix; "
                                f"add it to values.UNIT_SUFFIX so the name can "
                                f"be checked."))
        elif tail != want:
            out.append(("ERROR",
                        f"{name}: declares unit {u!r} but the name ends "
                        f"{tail!r}, not {want!r}. A name that carries the WRONG "
                        f"unit is worse than one that carries none — "
                        f"`delta_mhz` held GHz and read as a 1000x error."))
    return out


# ── who reads this name? (7bl) ────────────────────────────────────────────────
# The rename that broke solveconf and condcheck was undetectable because the
# store had no idea who read it. Now that every read goes through get(), the
# consumers are findable by AST: a call to values.get() with a literal name.
def consumers(name, root=None):
    """Every (file, line) that reads `name` through get(). Resolves aliases."""
    import ast as _ast, pathlib as _p
    root = _p.Path(root) if root else _p.Path(__file__).parent
    canon = ALIASES.get(name, name)
    hits = []
    for f in sorted(root.glob("*.py")):
        try:
            tree = _ast.parse(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for n in _ast.walk(tree):
            if not isinstance(n, _ast.Call) or not n.args:
                continue
            # 🔑 MUST be values.get()/_bind(), not any callable named `get`.
            # The first version counted `base.get("wall.conductivity", ...)` —
            # a plain dict lookup — and reported 4 consumers where there were 2.
            # An index that over-reports is not much better than none (7bl).
            fn = n.func
            if isinstance(fn, _ast.Attribute):
                ok = (isinstance(fn.value, _ast.Name)
                      and fn.value.id == "values" and fn.attr in ("get", "_bind"))
            else:
                ok = getattr(fn, "id", None) in ("get", "_bind")
            if not ok:
                continue
            a = n.args[0]
            if isinstance(a, _ast.Constant) and isinstance(a.value, str):
                if ALIASES.get(a.value, a.value) == canon:
                    hits.append((f.name, n.lineno,
                                 "alias" if a.value != canon else "canonical"))
    return hits

if __name__ == "__main__":
    import sys
    d = _load()
    if "--check-units" in sys.argv:
        fs = check_units()
        for lvl, m in fs:
            print(f"  {'🔴' if lvl == 'ERROR' else '⚠️ '} {m}")
        print(f"  {'✅ every dimensional name carries its unit' if not fs else ''}")
        sys.exit(1 if any(l == "ERROR" for l, _ in fs) else 0)
    if "--consumers" in sys.argv:
        i = sys.argv.index("--consumers")
        if i + 1 >= len(sys.argv):
            sys.exit("usage: values.py --consumers <canonical.name>")
        nm = sys.argv[i + 1]
        rows = consumers(nm)
        print(f"{nm}: {len(rows)} consumer(s)")
        for f, ln, how in rows:
            print(f"  {f}:{ln}" + ("   ⚠️  via ALIAS — migrate before removing"
                                   if how == "alias" else ""))
        sys.exit(0)
    names = sys.argv[1:] or sorted(k for k in d if not k.startswith("_"))
    for n in names:
        print(describe(n));  print()




