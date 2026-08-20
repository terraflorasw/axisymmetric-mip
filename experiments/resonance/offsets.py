#!/usr/bin/env python3
"""The order-1 → converged offset, measured and BOUND TO ITS GEOMETRY.

R50, and the audit called this the single most load-bearing number in the file.

It was **+31.6 MHz for the life of the project and it was wrong by 7.06 MHz.**
R38 measured +24.54. The failure was not the arithmetic — it was that an offset
measured at a = 101.43 / L = 87.67 was carried across two design points to
a = 103.70 / L = 88.53 and applied as though it were a constant. It is not a
constant: it is a discretisation error, so it depends on the geometry AND the
mesh AND the mode.

So it is stored per-mesh, with a FINGERPRINT of the geometry it was measured on,
and applying it to a different geometry raises instead of quietly returning a
plausible number. That is the whole point: the old failure was silent.

    measured on choff.msh   TE011 +24.54   TM020 +20.06

⚠️ MODE-SPECIFIC. Applying TE011's offset to TM020 corrupts the SEPARATION, which
is what the entire degeneracy argument rests on. There is no single "the offset".
"""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import modes
import solveconf

# Geometry that changes the discretisation error. Mesh sizing enters through
# size_factor and mesh_order; shape enters through the rest.
FINGERPRINT_KEYS = ("radius", "length", "brake_t", "ovality",
                    "chimney", "feed", "torch_ext", "groove")
TOL_MM = 0.01


def fingerprint(meta):
    g = meta["geometry_mm"]
    return {"geom": {k: g.get(k) for k in FINGERPRINT_KEYS},
            "size_factor": meta["size_factor"],
            "mesh_order": meta["mesh_order"],
            "sectors": meta["sectors"]}


def _same(a, b):
    if a.keys() != b.keys():
        return False
    for k in a:
        x, y = a[k], b[k]
        if isinstance(x, dict):
            if not _same(x, y):
                return False
        elif isinstance(x, list):
            if len(x) != len(y) or any(abs(p - q) > TOL_MM for p, q in zip(x, y)):
                return False
        elif isinstance(x, (int, float)) and isinstance(y, (int, float)):
            if abs(x - y) > TOL_MM:
                return False
        elif x != y:
            return False
    return True


def from_runs(mesh, tag_order1, tag_order2):
    """Derive offsets by differencing an order-1 and order-2 run of ONE mesh.

    Both runs must be of the same mesh — that is what makes this a solver-order
    difference rather than a mesh difference, which carries 1-3 MHz of scatter
    and would swamp the quantity being measured (R36).
    """
    o1, o2 = modes.peaks(tag_order1), modes.peaks(tag_order2)
    out = {}
    for name, fn in (("TE011", modes.te011), ("TM020", modes.tm020)):
        a, b = fn(o1), fn(o2)
        if a and b:
            out[name] = (b["f"] - a["f"]) * 1000.0
    meta = solveconf.load_meta(mesh)
    return {"mesh": pathlib.Path(mesh).name, "offsets_mhz": out,
            "from": [tag_order1, tag_order2], "fingerprint": fingerprint(meta)}


def store(mesh, rec):
    p = pathlib.Path(mesh).with_suffix(".offset.json")
    p.write_text(json.dumps(rec, indent=2) + "\n")
    return p


def load(mesh):
    p = pathlib.Path(mesh).with_suffix(".offset.json")
    if not p.exists():
        raise FileNotFoundError(
            f"{p.name} missing — the order-1 -> converged offset has not been "
            f"measured for this geometry. It is NOT a constant: +31.6 was "
            f"carried across two design points and was 7.06 MHz wrong. Measure "
            f"it (order 1 vs order 2 on this mesh) rather than borrowing one.")
    return json.loads(p.read_text())


def converged(mesh, mode, f_raw_ghz):
    """Apply the offset measured FOR THIS GEOMETRY. Raises otherwise."""
    rec = load(mesh)
    want = fingerprint(solveconf.load_meta(mesh))
    if not _same(rec["fingerprint"], want):
        raise ValueError(
            f"offset in {pathlib.Path(mesh).stem}.offset.json was measured on a "
            f"DIFFERENT geometry:\n  measured: {rec['fingerprint']}\n  "
            f"current:  {want}\nRe-measure. This is exactly how +31.6 survived "
            f"two design points.")
    if mode not in rec["offsets_mhz"]:
        raise KeyError(
            f"no offset measured for {mode} on this mesh. Do NOT substitute "
            f"another mode's — TE011 and TM020 differ by 4.5 MHz and using one "
            f"for both corrupts the separation.")
    return f_raw_ghz + rec["offsets_mhz"][mode] / 1000.0


if __name__ == "__main__":
    if len(sys.argv) == 4:
        rec = from_runs(sys.argv[1], sys.argv[2], sys.argv[3])
        p = store(sys.argv[1], rec)
        print(f"  {p.name}: " + ", ".join(
            f"{k} {v:+.2f} MHz" for k, v in rec["offsets_mhz"].items()))
    else:
        print("usage: offsets.py <mesh.msh> <order1-tag> <order2-tag>")
