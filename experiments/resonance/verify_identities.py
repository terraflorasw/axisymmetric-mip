#!/usr/bin/env python3
"""Check every stored result against the identities its numbers MUST satisfy.

🔴 WHY THIS EXISTS. 2026-09-03, found by the user, not by any check here:
`h3_driven` computed Q0 as `1/(1/Q_L - 1/Q_EXT_EST)` where `Q_EXT_EST` is a
CONSTANT — the plain 11x8 CAP loop's cold external Q — applied to a barrel
cavity with a 2.25 mm series gap whose own Q_ext is 322. Every Q0 it wrote was
Q_L corrected by an assumption about the quantity the run existed to measure.
Then a Q_ext derived as Q0/beta was circular, and landed close enough to the
expected value to read as confirmation.

🔑 THE POINT: none of that needed a solver to catch. The raw measurements were
fine. `Q0 = Q_L(1+beta)` is an IDENTITY, and it fails on those points by 30%.
A file that cannot satisfy its own algebra is wrong regardless of how carefully
it was solved.

➡️ Run this over the corpus after ANY change to a derivation, and before
quoting a Q from an artefact:

    python3 verify_identities.py              # every *.result.json
    python3 verify_identities.py <file>...    # named files

Exit 1 if any identity fails, so it can gate a workflow.

⚠️ WHAT THIS DOES NOT DO. It checks internal consistency, NOT correctness. A
run can satisfy every identity and still measure the wrong cavity (see
§ THE FILTER) or the wrong mode. Consistency is necessary, never sufficient.
"""
import glob
import json
import sys

import values

TOL = 0.02          # 2% — well inside any real fit error, far under the 30% seen

# 🔑 BOUND, NOT COPIED. preflight flagged this as a hardcoded Q the first time it
# was written — in the script whose whole subject is constants standing in for
# measurements. Adding a LOSSY loop can only LOWER Q0, so any Q0 above the bare
# cavity on a looped mesh is impossible, not merely suspicious.
# 🔴 AND IT MUST NAME THE CAVITY. 2026-09-05: this call CRASHED AT IMPORT —
# `cavity.Q0.cold` gained `required_context` during the underspecification audit,
# so the checker that found the 10 identity failures had been DEAD ever since,
# and nothing said so. A gate that cannot start does not fail loudly; it fails
# by not being there. (Found only by running it against a new artefact.)
# ⚠️ This is the CEILING for a sanity check, not a matched reference: the value
# is the cap-loop cavity's, and it is used only to reject the impossible — a
# looped Q0 ABOVE the bare cavity, which is how h3-azimload-01's 70,353 was
# caught. Naming the coordinates makes it explicit which cavity bounds which.
BARE_Q0_MAX = values.get("cavity.Q0.cold", solver="eigen",
                         mesh="vacuum_torch", port_bc="pec",
                         mount="cap", gap2_mm=0.0, loop_mm=[11.0, 8.0])


def _num(*vals):
    for v in vals:
        if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0:
            return float(v)
    return None


def points(d):
    if isinstance(d, dict) and isinstance(d.get("points"), list):
        return [p for p in d["points"] if isinstance(p, dict)]
    return []


def check(path):
    """(failures, checked, skipped) for one result file."""
    try:
        d = json.load(open(path))
    except Exception as e:
        return [(path, None, f"unreadable: {e}")], 0, 0
    fails, checked, skipped = [], 0, 0
    for p in points(d):
        wf = p.get("wide_fit") if isinstance(p.get("wide_fit"), dict) else {}
        QL = _num(p.get("Q_L"), wf.get("Q_L"))
        Q0 = _num(p.get("Q0"), wf.get("Q0"))
        b = _num(p.get("beta"), wf.get("beta"))
        qe = _num(p.get("Q_ext"), p.get("q_ext"), wf.get("Q_ext"))
        ne = p.get("ne")
        tag = f"ne={ne}" if ne is not None else p.get("name") or p.get("tag") or "?"

        # 🔑 IDENTITY 1 — Q0 against the resonator relation Q0 = Q_L(1+beta).
        # ⚠️ READ THE FAILURE CORRECTLY. h3_driven's `Q0` is BRANCH-FREE BY
        # DESIGN: Q0 = 1/(1/Q_L - 1/Q_ext), chosen so the beta/1-beta ambiguity
        # never enters. So a mismatch here does NOT mean the rig used a wrong
        # formula — it means the Q_ext CONSTANT that formula depends on is from a
        # different geometry. The correctly-branched values are already stored
        # beside it as Q0_if_undercoupled / Q0_if_overcoupled.
        # 🔴 But the constant propagates into FOUR fields: Q0, beta_resolved,
        # branch, and error_amplification. On the cold case that mislabels a
        # beta=112 cavity as "undercoupled".
        if QL and Q0 and b:
            checked += 1
            pred = QL * (1.0 + b)
            if abs(pred - Q0) / Q0 > TOL:
                # a CONSTANT implied Q_ext across points is the signature of an
                # assumed constant standing in for the measured quantity
                imp = 1.0 / (1.0 / QL - 1.0 / Q0) if Q0 > QL else float("nan")
                fails.append((path, tag,
                              f"Q0={Q0:,.1f} but Q_L(1+beta)={pred:,.1f} "
                              f"({(Q0/pred-1)*100:+.0f}%) — implies an assumed "
                              f"Q_ext of {imp:,.0f}"))
        else:
            skipped += 1

        # 🔑 IDENTITY 2 — Q_ext = Q0/beta, where both are recorded.
        if Q0 and b and qe:
            checked += 1
            pred = Q0 / b
            if abs(pred - qe) / qe > TOL:
                fails.append((path, tag,
                              f"Q_ext={qe:,.0f} but Q0/beta={pred:,.0f} "
                              f"({(qe/pred-1)*100:+.0f}%)"))

        # 🔑 IDENTITY 3 — a lossy loop cannot RAISE Q0 above the bare cavity.
        # h3-azimload-01 recorded Q0=70,353 cold. That is 1.6x the bare cavity.
        if Q0 and Q0 > BARE_Q0_MAX * 1.02:
            checked += 1
            fails.append((path, tag,
                          f"Q0={Q0:,.0f} EXCEEDS the bare cavity "
                          f"{BARE_Q0_MAX:,.0f} — adding a lossy loop cannot "
                          f"raise Q0. Physically impossible, not just off."))
    return fails, checked, skipped


def main(argv):
    files = argv[1:] or sorted(glob.glob("*.result.json"))
    if not files:
        print("  no result files"); return 0
    allf, C, S = [], 0, 0
    for f in files:
        fl, c, s = check(f)
        allf += fl; C += c; S += s
    print(f"  {len(files)} file(s) · {C} identity check(s) · {S} point(s) not checkable")
    if not allf:
        print("  ✅ every checkable point satisfies its identities")
        print("  ⚠️ consistency is NECESSARY, not sufficient — this says nothing "
              "about whether the right cavity or the right mode was measured.")
        return 0
    print(f"\n  🔴 {len(allf)} FAILURE(S):")
    for path, tag, msg in allf:
        print(f"    {path}")
        print(f"      [{tag}] {msg}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
