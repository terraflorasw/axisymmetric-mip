"""Read e0.result.json and state the three things E0 exists to establish."""
import json
import pathlib
import sys


def main():
    p = pathlib.Path("e0.result.json")
    if not p.exists():
        sys.exit("no e0.result.json")
    d = json.load(open(p))
    ex = d["exact"]
    print(f"  {'mode':>7}{'exact GHz':>12}{'fine Δ':>10}{'coarse Δ':>10}"
          f"{'cond Δ':>10}{'f-c':>9}")
    fine, coarse = d.get("fine", []), d.get("coarse", [])
    cond = d.get("cond", d.get("e0cond", []))

    def nearest(lst, f):
        return min(lst, key=lambda x: abs(x - f)) if lst else None
    worst_fc = 0.0
    for k, fx in sorted(ex.items(), key=lambda kv: kv[1]):
        a, b = nearest(fine, fx), nearest(coarse, fx)
        c = nearest(cond, fx) if cond else None
        if a is None or b is None:
            continue
        da, db = 1e3 * (a - fx), 1e3 * (b - fx)
        dc = 1e3 * (c - fx) if c is not None else float("nan")
        worst_fc = max(worst_fc, abs(da - db))
        print(f"  {k:>7}{fx:>12.5f}{da:>10.3f}{db:>10.3f}{dc:>10.3f}"
              f"{da-db:>9.3f}")
    print(f"\n  worst |fine − coarse| = {worst_fc:.3f} MHz  "
          f"(mesher floor 8 kHz, E0kp)")
    print(f"  keys present: {sorted(d)}")


if __name__ == "__main__":
    main()
