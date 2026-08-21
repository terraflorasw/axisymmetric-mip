"""Which solves ran at which SOLVER ORDER, across every run journal.

E0g established order 1 is 12-17 MHz wrong and mode-dependent by 40x. Any result
resting on an order-1 solve is therefore not a measurement of the cavity, it is a
measurement of the discretisation. This counts them rather than asserting a
sweeping claim -- the scope of an invalidation has to be established, not
guessed.
"""
import collections
import json
import pathlib
import sys


def main():
    files = sorted(pathlib.Path(".").glob("*.jsonl"))
    if not files:
        print("  no run journals (*.jsonl) found")
        return 2
    by = collections.Counter()
    tot = collections.Counter()
    for f in files:
        for line in f.read_text().splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue          # torn tail: skip the record, keep the file
            if r.get("event") != "solve":
                continue
            o = r.get("order")
            by[(f.stem, o)] += 1
            tot[o] += 1
    print(f"  {len(files)} journal(s)\n")
    print(f"  {'run':<28}{'order':>6}{'solves':>8}")
    for (run, order), n in sorted(by.items(), key=lambda x: (x[0][0], str(x[0][1]))):
        flag = "   🔴 ORDER-1" if order == 1 else ""
        print(f"  {run:<28}{str(order):>6}{n:>8}{flag}")
    print(f"\n  totals by order: {dict(sorted(tot.items(), key=lambda x: str(x[0])))}")
    n1 = tot.get(1, 0)
    print(f"  order-1 solves: {n1} of {sum(tot.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
