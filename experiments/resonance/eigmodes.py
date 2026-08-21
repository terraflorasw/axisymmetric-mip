"""Eigenmode results WITH SIGNATURES, and pairing by what a mode IS.

🔴 WHY THIS EXISTS. E1b measured the loading perturbation by matching each solve
INDEPENDENTLY against the empty closed-form spectrum. That works only while the
effect is smaller than the mode spacing:

    loading moves TM020 ~144 MHz, TM010 ~130 MHz
    mode spacing is 50-100 MHz

So "nearest to the empty value" was guaranteed to find the wrong mode. TM010
dropped out of the window entirely, got paired with TM110, and the mispairing
cascaded into a reported +607 MHz shift — which the sign falsifier caught, but
only after four solves.

🔑 THE FIX IS TO PAIR BY FIELD DISTRIBUTION, NOT BY FREQUENCY. A TE mode stays a
TE mode under loading: its energy stays where it was, even as its frequency
moves a long way. Palace's `p_elec[i]` / `p_mag[i]` give the fraction of each
mode's energy in region i, and that vector is a fingerprint.

⚠️ IT IS NOT A PERFECT INVARIANT. Loading DOES redistribute energy — that is the
physics being measured — so signatures shift too, just far less than
frequencies. Where a mode genuinely hybridises the fingerprint blurs, and this
module REPORTS ITS OWN MATCH DISTANCE so that case is visible instead of silent.
"""
import math
import pathlib


def read(tag, base="postpro"):
    """[{m, f, sig}] for one eigenmode solve. sig is the energy fingerprint."""
    d = pathlib.Path(base) / tag
    eig, dom = d / "eig.csv", d / "domain-E.csv"
    if not eig.exists() or not dom.exists():
        raise FileNotFoundError(f"{d}: need eig.csv and domain-E.csv")

    def rows(p):
        lines = p.read_text().splitlines()
        head = [h.strip() for h in lines[0].split(",")]
        return head, [[x.strip() for x in l.split(",")] for l in lines[1:] if l.strip()]

    eh, er = rows(eig)
    dh, dr = rows(dom)
    cols = [i for i, h in enumerate(dh) if h.startswith(("p_elec[", "p_mag["))]
    by_m = {}
    for r in dr:
        try:
            by_m[round(float(r[0]))] = [float(r[i]) for i in cols]
        except (ValueError, IndexError):
            pass
    out = []
    for r in er:
        try:
            m, f = round(float(r[0])), float(r[1])
        except (ValueError, IndexError):
            continue
        if m in by_m:
            out.append({"m": m, "f": f, "sig": by_m[m]})
    return sorted(out, key=lambda x: x["f"])


def _dist(a, b):
    """Euclidean distance between two signatures.

    🔴 REFUSES ON A LENGTH MISMATCH. This was `zip(a, b)`, which SILENTLY
    TRUNCATES to the shorter — so comparing a 2-region driven signature against
    a 6-region eigenmode one returned a small, confident, meaningless number.
    Two solves with different energy-region lists are not comparable, and the
    failure has to be loud: it is invisible in the result otherwise.
    """
    if len(a) != len(b):
        raise ValueError(
            f"signature length mismatch: {len(a)} vs {len(b)}. The two solves "
            f"emitted different energy regions, so their fingerprints are not "
            f"comparable. Give both configs the SAME Domains.Postprocessing."
            f"Energy list.")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def match(a, b, warn_at=0.05):
    """Pair modes of solve `a` to solve `b` BY SIGNATURE, one-to-one.

    Returns [(mode_a, mode_b, distance, flag)]. Uses scipy's optimal assignment
    when available, otherwise a greedy fallback — greedy is stated rather than
    hidden, because greedy can mis-assign when two modes are similar.

    🔑 `flag` marks a pair whose fingerprints disagree more than `warn_at`.
    Nothing is dropped: a doubtful pair is REPORTED as doubtful. A matcher that
    discards its uncertain cases hides exactly the ones worth looking at.
    """
    cost = [[_dist(x["sig"], y["sig"]) for y in b] for x in a]
    try:
        from scipy.optimize import linear_sum_assignment
        ri, ci = linear_sum_assignment(cost)
        pairs = list(zip(ri, ci))
        how = "optimal"
    except ImportError:
        used, pairs, how = set(), [], "greedy (scipy absent)"
        for i in range(len(a)):
            j = min((j for j in range(len(b)) if j not in used),
                    key=lambda j: cost[i][j], default=None)
            if j is not None:
                used.add(j)
                pairs.append((i, j))
    return [(a[i], b[j], cost[i][j], cost[i][j] > warn_at) for i, j in pairs], how


if __name__ == "__main__":
    import sys
    for t in sys.argv[1:]:
        ms = read(t)
        print(f"{t}: {len(ms)} modes, signature length {len(ms[0]['sig'])}")
        for m in ms[:6]:
            s = " ".join(f"{v:6.4f}" for v in m["sig"][:6])
            print(f"  m={m['m']:>3} f={m['f']:.6f}  sig[{s} ...]")


# ---------------------------------------------------------------------------
# THE EXACT DEGENERACY, SEPARATED PROPERLY
#
# 🔴 NINE RIGS COMPUTED THIS WRONG, IDENTICALLY. Each took the two modes NEAREST
# the exact TE011 frequency and called their gap "the TE011/TM111 splitting":
#
#     n = sorted(freqs, key=lambda x: abs(x - EX["TE011"]))[:2]
#     splitting = abs(n[1] - n[0])
#
# But TM111 is m=1 and therefore DOUBLY degenerate — cos(phi) and sin(phi). So
# the two nearest modes are both TM111, and what was reported as the TE011/TM111
# splitting is actually TM111's internal POLARISATION splitting. Measured by E0q,
# which resolved the triplet by Q:
#
#     2.44432  Q 18,034   TM111 (a)
#     2.44433  Q 18,031   TM111 (b)     <- these two were being compared
#     2.44446  Q 36,548   TE011         <- the actual partner, 0.14 MHz away
#
# The rigs reported 0.014 MHz. The real TE011<->TM111 splitting is 0.14 MHz —
# ten times larger, and a different quantity.
#
# TWO DISCRIMINATORS, because Q only works on a lossy wall:
#   Q            TE011 has ~2x the Q of TM111 (no axial wall currents). Clean,
#                but PEC solves report Q ~1e12-1e15, which is noise.
#   multiplicity m=1 comes in pairs, m=0 does not. Works everywhere, including
#                PEC. The two modes closest TO EACH OTHER are TM111.
# ---------------------------------------------------------------------------


def te011_tm111(freqs, exact_te011, qs=None, fmin=None, fmax=None):
    """Separate the TE011/TM111 triplet. Returns a dict, or None if it cannot.

    freqs  frequencies (GHz) from one solve
    exact  physics.spectrum()[...] value the pair sits on
    qs     optional, aligned with freqs; used when the wall is lossy
    fmin   the floor of the region the SOLVER SEARCHED (Palace's Target).
    fmax   the ceiling, if one was imposed.

    🔴 WHY fmin EXISTS — H2b, 2026-08-21. This function reported TM111 at
    2.60631 for a geometry where H2 had measured 2.38675. It was not a bad
    pairing; the mode WAS NOT IN THE FILE. H2b solved with `target=2.40` while
    the groove pushes TM111 DOWNWARD, so past ~8 mm of depth TM111 leaves the
    window through the floor. The three modes nearest the exact TE011 frequency
    were then TE011 plus an unrelated degenerate pair at 2.606 — which even has
    a plausible Q ratio, 0.472 against TM111's 0.456. Every guard passed. H2
    got the same measurement right only because it used the default
    `target=1.05` and searched the whole spectrum.

    🔑 THE RULE, and it is general: **a nearest-neighbour answer is only
    trustworthy if the thing it found is NEARER than the edge of the region
    that was searched.** Otherwise an unseen mode could be closer, and
    "nearest" is an artifact of where you stopped looking. Declaring fmin is
    how the caller states where it stopped. Without it this falls back to the
    lowest mode RETURNED, which is weaker — the solver may have been cut off
    by its mode count rather than by a real gap — and the result says so.
    """
    order = sorted(range(len(freqs)), key=lambda i: abs(freqs[i] - exact_te011))
    pick = order[:3]
    if len(pick) < 3:
        return None
    f = [freqs[i] for i in pick]
    q = [qs[i] for i in pick] if qs else None

    how = "multiplicity"
    te_i = None
    # 🔴 A PEC SOLVE REPORTS Q ~1e12-1e15 — noise, not a measurement, and the
    # RATIO test passes on noise happily (6.1e15 > 1.5 x 7.3e13) and then picks
    # the wrong mode. Caught by this file's own self-test. Physical wall Q here
    # is ~1e4; demand plausibility BEFORE trusting the ratio.
    Q_PLAUSIBLE = (1e2, 1e7)
    if q and min(q) > 0 and all(Q_PLAUSIBLE[0] < x < Q_PLAUSIBLE[1] for x in q):
        hi = max(range(3), key=lambda i: q[i])
        rest = [q[i] for i in range(3) if i != hi]
        # TE011 stands out by ~2x; demand a clear margin before trusting Q
        if q[hi] > 1.5 * max(rest):
            te_i, how = hi, "Q"
    if te_i is None:
        # the m=1 pair are the two closest TO EACH OTHER; the odd one is TE011
        gaps = [(abs(f[a] - f[b]), a, b) for a, b in ((0, 1), (0, 2), (1, 2))]
        _g, a, b = min(gaps)
        te_i = ({0, 1, 2} - {a, b}).pop()

    pair = [i for i in range(3) if i != te_i]
    tm = (f[pair[0]] + f[pair[1]]) / 2.0

    # 🔴 THE WINDOW-EDGE TEST. How far below/above `exact` did the search
    # actually look? Anything picked from beyond that reach is a mode we
    # settled for, not the nearest one that exists.
    lo = fmin if fmin is not None else min(freqs)
    hi = fmax if fmax is not None else max(freqs)
    declared = fmin is not None or fmax is not None
    reach_lo, reach_hi = exact_te011 - lo, hi - exact_te011
    dist = abs(tm - exact_te011)
    # 🔑 A BALL, NOT A SIDE. If the nearest candidate sits `dist` away, the
    # claim "nearest" is only justified when the search covered the WHOLE
    # interval [exact-dist, exact+dist]. Checking only the side the candidate
    # happens to lie on is not enough — H2b's false TM111 was 156 MHz ABOVE
    # exact, where the window ran 343 MHz, while the real mode was 63 MHz
    # BELOW, where the window ran only 50 MHz. Guarding the candidate's own
    # side passes that case happily.
    reach = min(reach_lo, reach_hi)
    if dist > reach:
        side = "below" if reach_lo < reach_hi else "above"
        print(f"    🔴 te011_tm111 REFUSES: candidate TM111 at {tm:.5f} is "
              f"{1e3*dist:.1f} MHz from the exact {exact_te011:.5f}, but the "
              f"search only reached {1e3*reach:.1f} MHz {side} it "
              f"(window {lo:.5f}-{hi:.5f}). A nearer mode could lie outside "
              f"the solved window, so 'nearest' is an artifact of where the "
              f"search stopped. Re-solve wider; do NOT trust this match.")
        return None

    # Touching the edge is not a refusal — it is an admission. Report it.
    at_edge = min(pick) == freqs.index(min(freqs)) or tm in (min(freqs), max(freqs))
    return {"te011": f[te_i], "tm111": tm,
            "window": {"lo": lo, "hi": hi, "declared": declared,
                       "reach_lo_mhz": 1e3 * reach_lo,
                       "reach_hi_mhz": 1e3 * reach_hi,
                       "at_edge": bool(at_edge)},
            # 🔴 RETURN THE INDICES. h1_aspect re-searched for the TM111 pair by
            # frequency within 100 kHz of their own mean, which comes back EMPTY
            # whenever the pair splits by more than ~200 kHz — silently
            # disabling the falsifier that checks the mode identification. Ask
            # the function that already knows, do not re-derive.
            "te011_index": pick[te_i],
            "tm111_indices": [pick[i] for i in pair],
            "tm111_pair_mhz": 1e3 * abs(f[pair[0]] - f[pair[1]]),
            "splitting_mhz": 1e3 * abs(f[te_i] - tm),
            "how": how,
            "triplet": sorted(f)}



def follow(ref, cur, indices, reject_at=0.010):
    """Follow named modes of solve `ref` into solve `cur` BY SIGNATURE.

    ref, cur   [{m, f, sig}] from read()
    indices    positions in `ref` to follow
    Returns    {index: {f, m, dist, found, why}}

    🔑 THIS IS THE ANSWER TO A MODE THAT MOVED. Frequency proximity fails once
    the perturbation exceeds the mode spacing — that is E1b's grave and H2b's.
    A TE mode stays a TE mode: its energy distribution is nearly invariant even
    when its frequency moves 60 MHz.

    Measured on the H2b groove sweep, control -> grooved, where the answer is
    independently known:

        true match (TM111, exp-eta1)          d = 0.0007
        TE011, every case, 0 to 20 mm depth   d <= 0.00004
        best NON-match (TM111 absent)         d = 0.0261, 0.0306, 0.0344

    A 40x gap. `reject_at=0.010` sits 14x above the true match and 2.6x below
    the nearest false one. ⚠️ That is ONE true match against three non-matches,
    which is a discriminator, not a law — it should be re-checked whenever a
    new kind of perturbation is introduced (a torch, a plasma), and the
    distance is returned on EVERY call so it can be caught being wrong.

    🔴 One-to-one assignment, not independent nearest: two reference modes must
    not both claim the same current mode. That is why this delegates to match()
    rather than looping over minima.
    """
    pairs, how = match(ref, cur, warn_at=reject_at)
    out = {}
    for a, b, d, _flag in pairs:
        i = ref.index(a)
        if i not in indices:
            continue
        found = d <= reject_at
        out[i] = {"f": b["f"], "m": b["m"], "dist": d, "found": found,
                  "how": how,
                  "why": None if found else
                  (f"best signature distance {d:.4f} exceeds {reject_at:.4f} — "
                   f"the mode is NOT in this solve (it left the window), or it "
                   f"hybridised. Either way it was not identified.")}
    for i in indices:
        if i not in out:
            out[i] = {"f": None, "m": None, "dist": None, "found": False,
                      "how": how, "why": "no assignment returned for this mode"}
    return out


if __name__ == "__main__":
    ok = True

    def chk(name, got, want, tol=1e-9):
        global ok
        good = abs(got - want) <= tol
        ok &= good
        print(f"  {'✅' if good else '🔴'} {name:<46} {got:.6f} (want {want:.6f})")

    print("eigmodes.te011_tm111 self-test — real E0q numbers\n")
    F = [2.44432, 2.44433, 2.44446]
    Q = [18034.0, 18031.0, 36548.0]

    r = te011_tm111(F, 2.444385, Q)
    print(f"  with Q      -> how={r['how']}, te011={r['te011']}")
    chk("TE011 picked by Q", r["te011"], 2.44446)
    chk("splitting (MHz)", r["splitting_mhz"], 0.135, 1e-3)
    chk("TM111 pair split (MHz)", r["tm111_pair_mhz"], 0.010, 1e-3)

    r2 = te011_tm111(F, 2.444385)
    print(f"  without Q   -> how={r2['how']}, te011={r2['te011']}")
    chk("TE011 picked by multiplicity", r2["te011"], 2.44446)
    chk("same splitting without Q", r2["splitting_mhz"], r["splitting_mhz"])

    # the OLD method, for contrast: two nearest to exact
    old = sorted(F, key=lambda x: abs(x - 2.444385))[:2]
    print(f"\n  old two-nearest method gave {1e3*abs(old[1]-old[0]):.3f} MHz "
          f"— that is the TM111 PAIR, not the TE011/TM111 splitting")

    # PEC-style: Q is garbage, must fall back to multiplicity
    r3 = te011_tm111(F, 2.444385, [8.0e12, 6.1e15, 7.3e13])
    print(f"  PEC-noise Q -> how={r3['how']} (must be 'multiplicity')")
    ok &= (r3["how"] == "multiplicity")
    print(f"  {'✅' if r3['how'] == 'multiplicity' else '🔴'} "
          f"{'PEC Q rejected as implausible':<46}")
    chk("PEC case still finds TE011", r3["te011"], 2.44446)


    # -----------------------------------------------------------------
    # KNOWN-BAD INPUT — the real H2b anchor solve, gd=10 mm, target 2.40.
    # 🔴 Every guard this file had passed on it and it returned a confident
    # 2.60631 for a mode H2 had measured at 2.38675. A self-test that only
    # feeds a checker good input cannot catch the checker being wrong.
    # -----------------------------------------------------------------
    print("\n  known-bad: H2b anchor, TM111 pushed BELOW the solved window")
    AF = [2.451001, 2.606157, 2.606471, 2.738979,
          2.739783, 2.749847, 2.750165, 2.792937]
    AQ = [44256.0, 20911.0, 20929.0, 18216.0,
          18279.0, 19563.0, 19624.0, 10834.0]

    bad = te011_tm111(AF, 2.45, AQ)                  # no fmin: weaker fallback
    good_refuse = bad is None
    ok &= good_refuse
    print(f"  {'✅' if good_refuse else '🔴'} "
          f"{'refuses without a declared window':<46} "
          f"{'None' if good_refuse else bad['tm111']}")

    bad2 = te011_tm111(AF, 2.45, AQ, fmin=2.40)      # the window it really used
    good_refuse2 = bad2 is None
    ok &= good_refuse2
    print(f"  {'✅' if good_refuse2 else '🔴'} "
          f"{'refuses with fmin=2.40 declared':<46} "
          f"{'None' if good_refuse2 else bad2['tm111']}")

    # ...and the SAME numbers must be accepted once the search really did
    # cover the region, which is what H2 did with target=1.05. Here TM111 is
    # present at 2.38675, so the answer exists and must be found.
    HF = sorted(AF + [2.386700, 2.386800])
    HQ = [AQ[AF.index(f)] if f in AF else 20000.0 for f in HF]
    goodr = te011_tm111(HF, 2.45, HQ, fmin=1.05)
    accepted = goodr is not None and abs(goodr["tm111"] - 2.38675) < 1e-4
    ok &= accepted
    print(f"  {'✅' if accepted else '🔴'} "
          f"{'accepts when TM111 IS in the window':<46} "
          f"{goodr['tm111'] if goodr else 'None'}")

    print(f"\n  {'✅ ALL PASS' if ok else '🔴 FAILURES ABOVE'}")
