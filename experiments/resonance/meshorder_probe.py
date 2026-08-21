"""Geometric order of every mesh present, newest last. Read-only probe."""
import glob
import json
import os


def main():
    rows = []
    for f in sorted(glob.glob("*.meta.json")):
        try:
            d = json.load(open(f))
        except (json.JSONDecodeError, OSError):
            continue
        rows.append((os.path.getmtime(f), f, d.get("mesh_order"),
                     d.get("geometry_mm", {}).get("radius"),
                     d.get("tets")))
    rows.sort()
    print(f"  {'mesh':<24}{'geom order':>11}{'radius':>9}{'tets':>10}")
    for _t, f, o, r, n in rows[-12:]:
        print(f"  {f:<24}{str(o):>11}{str(r):>9}{n if n else '':>10}")
    orders = {o for _t, _f, o, _r, _n in rows}
    print(f"\n  distinct geometric orders across all meshes: {sorted(orders, key=str)}")


if __name__ == "__main__":
    main()
