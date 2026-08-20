#!/usr/bin/env python3
"""preflight.py — refuse to launch a rig that carries a known-fatal pattern.

Every rule here comes from a failure that actually happened in this project,
most of them TWICE, all of them already written down in prose that did not stop
them. Prose is read at the start of a task; the mistake happens forty minutes
later at a keystroke, when attention is on the physics. A gate that runs does
what a document cannot.

    python3 preflight.py rig_x.py [more.py ...]   lint; exit 1 on any ERROR
    python3 preflight.py --self-test              prove every rule fires

🔑 THE SELF-TEST IS NOT OPTIONAL. A linter that never fires is theatre — it
raises confidence without lowering the error rate, which is worse than nothing.
Each rule is checked against a KNOWN-BAD sample it must catch and a KNOWN-GOOD
sample it must not.
"""
import ast
import re
import sys

ERROR, WARN = "ERROR", "warn"


def r_timeout(src, tree):
    """subprocess.run(timeout=) RAISES BUT DOES NOT KILL. Cost: 4 leaked ranks
    per timeout, 12 processes thrashing the user's machine mid-standup."""
    out = []
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call) and
                isinstance(n.func, ast.Attribute) and n.func.attr == "run" and
                isinstance(n.func.value, ast.Name) and
                n.func.value.id == "subprocess" and
                any(k.arg == "timeout" for k in n.keywords)):
            out.append((ERROR, n.lineno,
                        "subprocess.run(timeout=) raises but does NOT kill the "
                        "child. Use Popen + wait(timeout) + kill()."))
    return out


def r_pkill(src, tree):
    """pkill -f matches the harness wrapper's argv and kills the CALLING SHELL.
    Observed three times here (exit 144), twice in one afternoon."""
    return [(ERROR, i + 1, "pkill -f matches the harness wrapper's own argv and "
             "kills the calling shell. Use reap.py, or ps + kill by PID.")
            for i, l in enumerate(src.splitlines()) if "pkill" in l and "-f" in l]


def r_main_guard(src, tree):
    """Importing a script to reuse its helpers EXECUTES it. Cost: a full run
    launched by an import, twice, once leaving an untracked foreground job."""
    if "__main__" in src:
        return []
    bad = [n for n in tree.body
           if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)]
    if bad:
        return [(ERROR, bad[0].lineno,
                 "top-level calls with no `if __name__ == \"__main__\"` guard — "
                 "importing this file will RUN it.")]
    return []


def r_help_percent(src, tree):
    """argparse expands help with `% params`. A bare % crashes --help. '23% low'
    parses as %o; '9.2% WORSE' as %W. Made twice in one session."""
    out = []
    for m in re.finditer(r'help\s*=\s*(("(?:[^"\\]|\\.)*"\s*)+)', src, re.S):
        txt = m.group(1)
        for pm in re.finditer(r"%(?!%)", txt):
            out.append((ERROR, src[:m.start()].count("\n") + 1,
                        "unescaped %% in an argparse help string — crashes "
                        "--help. Double it."))
            break
    return out


def r_ps_e_with_C(src, tree):
    """`ps -eo … -C name`: -e selects EVERY process and silently overrides -C,
    so a finished job looks alive."""
    return [(ERROR, i + 1, "ps -e overrides -C silently; drop -e.")
            for i, l in enumerate(src.splitlines())
            if re.search(r"ps\s+-e\w*o", l) and " -C " in l]


def r_falsy_numeric_flag(src, tree):
    """`if a.x:` on a numeric argparse flag ignores 0. `--viewport 0` could not
    disable the viewport once its default became 10 mm, and a benchmark then
    ran against a cavity with a stub in it."""
    types = dict(re.findall(r'add_argument\("--([a-z0-9-]+)"[^)]*?type=(\w+)',
                            src, re.S))
    out = []
    for m in re.finditer(r"^\s*if a\.([a-z_0-9]+):\s*$", src, re.M):
        flag = m.group(1).replace("_", "-")
        if types.get(flag) in ("float", "int"):
            out.append((ERROR, src[:m.start()].count("\n") + 1,
                        f"`if a.{m.group(1)}:` on a numeric flag — 0 is falsy "
                        "and silently ignored. Use `is not None`."))
    return out


def r_bare_background(src, tree):
    """A shell `&` with no run_in_background makes the job invisible to the
    harness: no completion notification, nothing re-invokes on exit."""
    return [(WARN, i + 1, "bare `&` backgrounding — invisible to the harness.")
            for i, l in enumerate(src.splitlines())
            # trailing quote counts: these appear inside shell strings
            if re.search(r"&\s*[\'\"]?\s*$", l)
            and ("nohup" in l or "python" in l)]


def r_nearest_match(src, tree):
    """min(..., key=abs(x - target)) with no ceiling check fabricated a -27.6
    MHz error for a mode that was never in the solved set."""
    return [(WARN, i + 1, "nearest-value matching — check the target is below "
             "the solved ceiling and the pick is not already claimed "
             "(physics.match_exact).")
            for i, l in enumerate(src.splitlines())
            if re.search(r"min\(.*key=lambda.*abs\(", l)]


RULES = [r_timeout, r_pkill, r_main_guard, r_help_percent, r_ps_e_with_C,
         r_falsy_numeric_flag, r_bare_background, r_nearest_match]

BAD = {
    "r_timeout": "import subprocess\nsubprocess.run(['x'], timeout=5)\n",
    "r_pkill": "import os\nos.system('pkill -f rig_x.py')\n",
    "r_main_guard": "def f():\n    pass\nf()\n",
    "r_help_percent": 'import argparse\nap=argparse.ArgumentParser()\n'
                      'ap.add_argument("--x", help="23% low")\n',
    "r_ps_e_with_C": "cmd = 'ps -eo pid= -C palace'\n",
    "r_falsy_numeric_flag": 'import argparse\nap=argparse.ArgumentParser()\n'
                            'ap.add_argument("--viewport", type=float)\n'
                            'a=ap.parse_args()\nif a.viewport:\n    pass\n',
    "r_bare_background": "x = 'nohup python3 job.py &'\n",
    "r_nearest_match": "y = min(v, key=lambda x: abs(x - t))\n",
}
GOOD = ('import subprocess\n'
        'def f():\n    subprocess.Popen(["x"]).wait(timeout=5)\n'
        'if __name__ == "__main__":\n    f()\n')


def lint(path):
    src = open(path).read()
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [(ERROR, e.lineno or 0, f"SyntaxError: {e.msg}")]
    return [f for rule in RULES for f in rule(src, tree)]


def self_test():
    ok = True
    for rule in RULES:
        src = BAD[rule.__name__]
        hit = rule(src, ast.parse(src))
        miss = rule(GOOD, ast.parse(GOOD))
        good = bool(hit) and not miss
        ok &= good
        print(f"  {'✅' if good else '🔴'} {rule.__name__:<22} "
              f"fires on known-bad: {bool(hit)}   quiet on known-good: "
              f"{not miss}")
    print(f"\n  {'✅ every rule discriminates' if ok else '🔴 A RULE DOES NOT FIRE — it is theatre'}")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    files = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not files:
        sys.exit("usage: preflight.py <file.py> ... | --self-test")
    bad = 0
    for f in files:
        fs = lint(f)
        errs = [x for x in fs if x[0] == ERROR]
        bad += len(errs)
        print(f"{f}: {len(errs)} error(s), {len(fs)-len(errs)} warning(s)")
        for lvl, ln, msg in sorted(fs, key=lambda x: x[1]):
            print(f"  {'🔴' if lvl == ERROR else '⚠️ '} line {ln}: {msg}")
    sys.exit(1 if bad else 0)
