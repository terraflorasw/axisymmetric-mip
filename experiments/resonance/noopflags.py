"""Which rigs pass a geometry.py flag set to the value it already defaults to?

E0's "coarse" mesh was built with --n-wl 8, and 8.0 is the default. The flag did
nothing, so coarse and fine were the same mesh and E0's resolution comparison was
vacuous for the whole life of the programme.

A flag set to its own default is INVISIBLE: the rig reads as if it varied
something, the mesh reads as if it were asked for, and nothing anywhere says
otherwise. This finds the rest of them.

⚠️ Not every match is a bug. Passing a default EXPLICITLY can be documentation
("this is deliberately the default"). What makes E0's fatal is that the value was
meant to CONTRAST with another mesh. Reported for judgement, not auto-condemned.
"""
import ast
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import preflight

# flag -> the P key it sets, for the flags that carry a scalar default
FLAGS = {
    "--n-wl": "elems_per_wl",
    "--size-factor": "size_factor",
    "--order": None,            # argparse default, handled separately
    "--mode-filter": "filter_t",
    "--filter-eps": "filter_eps",
    "--viewport": "view_d",
    "--torch-ext": "torch_ext",
    "--ovality": "ovality",
    "--threads": None,
    "--ho-optimize": None,
}
SCALE = {"filter_t": 1e3, "view_d": 1e3, "torch_ext": 1e3, "ovality": 1e3}
ARGPARSE_DEFAULTS = {"--order": 2.0, "--threads": 1.0, "--ho-optimize": 2.0}


def geometry_defaults():
    src = pathlib.Path("geometry.py").read_text()
    m = re.search(r"^P = dict\((.*?)^\)", src, re.S | re.M)
    if not m:
        m = re.search(r"^P = \{(.*?)^\}", src, re.S | re.M)
    body = m.group(1) if m else ""
    out = {}
    for key, val in re.findall(r"(\w+)\s*=\s*([0-9.eE+-]+)", body):
        try:
            out[key] = float(val)
        except ValueError:
            pass
    return out


def main():
    d = geometry_defaults()
    if not d:
        print("  🔴 could not parse geometry.py defaults — REPORTED, not passed")
        return 2
    print(__doc__)
    print(f"  parsed {len(d)} scalar defaults from geometry.py\n")
    hits = 0
    for f in sorted(pathlib.Path(".").glob("e*.py")):
        # 🔴 NOT a regex over the text, and NOT preflight.code_only either.
        # Regex over raw text flagged the COMMENT documenting this very bug.
        # code_only() blanks strings — and the flags ARE strings, so it found
        # nothing at all. Walk the AST: list/tuple literals are exactly where
        # geometry arguments live, and comments and docstrings cannot reach it.
        try:
            tree = ast.parse(f.read_text())
        except SyntaxError:
            print(f"  🔴 {f.name}: will not parse — REPORTED, not skipped")
            continue
        pairs = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.List, ast.Tuple)):
                continue
            items = [e.value if isinstance(e, ast.Constant) else None
                     for e in node.elts]
            for x, y in zip(items, items[1:]):
                if isinstance(x, str) and isinstance(y, str):
                    pairs.append((x, y))
        for flag, key in FLAGS.items():
            for val in [y for x, y in pairs if x == flag]:
                try:
                    v = float(val)
                except ValueError:
                    continue
                if flag in ARGPARSE_DEFAULTS:
                    dv = ARGPARSE_DEFAULTS[flag]
                elif key and key in d:
                    dv = d[key] * SCALE.get(key, 1.0)
                else:
                    continue
                if abs(v - dv) < 1e-9:
                    hits += 1
                    print(f"  ⚠️ {f.name:<26} {flag} {val:<8} == default "
                          f"{dv:g}  — this flag does NOTHING")
    print()
    if hits:
        print(f"  {hits} flag(s) set to their own default. Each is either "
              f"deliberate documentation or a silent no-op; a flag meant to "
              f"CONTRAST two cases is the fatal kind (E0's --n-wl 8).")
    else:
        print("  ✅ no geometry flag is set to its own default value")
    return 0


if __name__ == "__main__":
    sys.exit(main())
