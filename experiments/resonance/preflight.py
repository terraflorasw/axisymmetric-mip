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
import io
import re
import sys
import tokenize

ERROR, WARN = "ERROR", "warn"


def code_only(src):
    """`src` with COMMENT and STRING contents blanked, line numbers preserved.

    🔴 WITHOUT THIS THE LINTER FLAGS ITS OWN DOCUMENTATION. Every rule below
    quotes the pattern it forbids, so preflight.py reported 7 errors against
    itself and reap.py 1 — all of them prose explaining why not to do the thing.
    A checker that cannot tell code from commentary trains you to ignore it,
    which is worse than not having it.
    """
    out = src.splitlines(keepends=True)
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError):
        return src
    for t in toks:
        if t.type not in (tokenize.COMMENT, tokenize.STRING):
            continue
        (r1, c1), (r2, c2) = t.start, t.end
        for r in range(r1, r2 + 1):
            line = out[r - 1]
            a = c1 if r == r1 else 0
            b = c2 if r == r2 else len(line.rstrip("\n"))
            out[r - 1] = line[:a] + " " * (b - a) + line[b:]
    return "".join(out)


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
    def is_setup(n):
        f = n.value.func
        return (isinstance(f, ast.Attribute) and f.attr == "insert"
                and isinstance(f.value, ast.Attribute) and f.value.attr == "path")
    bad = [n for n in tree.body
           if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
           and not is_setup(n)]
    if bad:
        return [(ERROR, bad[0].lineno,
                 "top-level calls with no `if __name__ == \"__main__\"` guard — "
                 "importing this file will RUN it.")]
    return []


def _fixture_lines(tree):
    """Lines belonging to the BAD/GOOD test fixtures.

    They deliberately CONTAIN the forbidden patterns — that is their whole
    purpose — so a rule needing raw string contents must not report them.
    A test fixture is not code under test.
    """
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id in ("BAD", "GOOD")
                for t in n.targets):
            out |= set(range(n.lineno, (n.end_lineno or n.lineno) + 1))
    return out


def r_help_percent(src, tree):
    """RAW: this rule must see string contents."""
    skip = _fixture_lines(tree)
    """argparse expands help with `% params`. A bare % crashes --help. '23% low'
    parses as %o; '9.2% WORSE' as %W. Made twice in one session."""
    out = []
    for m in re.finditer(r'help\s*=\s*(("(?:[^"\\]|\\.)*"\s*)+)', src, re.S):
        txt = m.group(1)
        # 🔴 `%(?!%)` was WRONG: in a correctly-escaped "%%" the SECOND % is
        # followed by a space, so it matched and reported a false positive —
        # and my "fix" for it then turned %% into %%%. Count RUNS instead: an
        # odd-length run contains an unescaped %, an even one does not.
        for pm in (m for m in re.finditer(r"%+", txt) if len(m.group()) % 2):
            ln = src[:m.start()].count("\n") + 1
            if ln not in skip:
                out.append((ERROR, ln,
                            "unescaped %% in an argparse help string — crashes "
                            "--help. Double it."))
            break
    return out


def r_ps_e_with_C(src, tree=None):
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
    inside = {ln for f in ast.walk(tree)
              if isinstance(f, ast.FunctionDef) and f.name == "match_exact"
              for ln in range(f.lineno, (f.end_lineno or f.lineno) + 1)}
    return [(WARN, i + 1, "nearest-value matching — check the target is below "
             "the solved ceiling and the pick is not already claimed "
             "(physics.match_exact).")
            for i, l in enumerate(src.splitlines())
            if re.search(r"min\(.*key=lambda.*abs\(", l) and i + 1 not in inside]



def r_undefined_name(src, tree):
    """🔴 A NameError that only fires at CALL TIME, forty minutes into a run.

    Twice in one session a rig was launched and died seconds in on an import
    removed during a refactor — `eigen_cfg` both times, dropped when the rig was
    converted to driven and not restored when it was converted back. `ast.parse`
    cannot see it: the syntax is fine, and the name is only looked up when the
    function actually runs.

    ⚠️ Delegates to pyflakes rather than hand-rolling scope analysis. A
    hand-rolled version would have to get comprehensions, walrus, global/nonlocal
    and star-imports right, and CONVENTIONS §7 is explicit that a checker which
    cannot see its subject is worse than none — this project has already shipped
    one scanner that returned a clean bill of health because it was blanking the
    very strings it was meant to read.

    Reports as an ERROR: an undefined name is not a style opinion.
    """
    try:
        from pyflakes.api import check
        from pyflakes.reporter import Reporter
    except ImportError:
        return [(WARN, 1, "pyflakes not installed — undefined names are NOT "
                          "being checked. `pip install pyflakes`.")]
    buf, errbuf = io.StringIO(), io.StringIO()
    check(src, "<rig>", Reporter(buf, errbuf))
    out = []
    for line in buf.getvalue().splitlines():
        # "<rig>:LINE:COL message"
        parts = line.split(":", 3)
        if len(parts) < 4:
            continue
        msg = parts[3].strip()
        if "undefined name" in msg:
            try:
                ln = int(parts[1])
            except ValueError:
                ln = 1
            out.append((ERROR, ln, f"{msg} — this is a NameError waiting for "
                                   f"the line to execute, not a style issue"))
    return out

# rules needing the raw source (they inspect string CONTENTS); all others are
# run against code_only() so prose about a pattern is not mistaken for it
RAW = {"r_help_percent", "r_undefined_name", "r_none_format"}


# ---------------------------------------------------------------- shell rules
# .sh files get their own set: no AST, and the hazards are different. Added
# after `pkill -f` killed a shell for the THIRD time in one session — twice
# locally (exit 144) and once over ssh, taking the remote shell with it.

def sh_pkill(src, _t=None):
    return [(ERROR, i + 1, "pkill -f matches the CALLING shell's own argv "
             "(and over ssh, the remote shell). Use `ps -o pid=,args= -C name` "
             "then kill by PID, or reap.py.")
            for i, l in enumerate(src.splitlines())
            if re.search(r"\bpkill\b.*-f|\bpkill\s+-\w*f", l)
            and not l.strip().startswith("#")]


def sh_unguarded_mkfs(src, _t=None):
    """mkfs with no blkid/-n guard destroys a volume on the SECOND run."""
    out = []
    lines = src.splitlines()
    for i, l in enumerate(lines):
        if l.strip().startswith("#") or "mkfs" not in l:
            continue
        ctx = " ".join(lines[max(0, i - 2):i + 1])
        if "blkid" not in ctx and "-n" not in l:
            out.append((ERROR, i + 1, "mkfs with no guard — on a re-run this "
                        "destroys the volume. Prefix with `blkid DEV || `."))
    return out


def sh_rm_rf_var(src, _t=None):
    """`rm -rf $X/` deletes / when X is empty or unset."""
    return [(ERROR, i + 1, "rm -rf on an unbraced variable — if it is empty "
             "this targets /. Use \"${VAR:?}\".")
            for i, l in enumerate(src.splitlines())
            # 🔴 WAS `\s+$[A-Za-z_]` — `$` is an END-OF-LINE ANCHOR, so this
            # could never match and the rule NEVER FIRED. Found 2026-08-25 by
            # the self-test, which is the only reason it was caught. The shell
            # sigil needs escaping: `\$`. (The same escape, inverted, is how the
            # r_hardcoded_value regexes were wrong on the way in.)
            if re.search(r"rm\s+-[rf]{2}\s+\$[A-Za-z_]", l)
            and not l.strip().startswith("#")]


# 🔴 ONE WATCHER. 2026-09-04/05: a bespoke poll-ssh-grep loop was hand-written
# for EVERY launch across two days, while ops/watchrig.sh — the tested mechanism
# with 16 tests — sat unused. Each hand-rolled version reproduced a failure it
# had already fixed: no mirroring, no blindness check, host death caught 20 min
# late, and a filter tuned three times.
# 🔑 A watch must answer all three: (a) progress, (b) solve exit, (c) MACHINE
# exit. ops/wait.sh answered only (b) and was expunged.
# ✅ A legitimately-sanctioned watcher carries `sanctioned-watcher:` and a reason.
_ADHOC_WATCH = re.compile(
    r"(while +true|until +\[|until +!)[\s\S]{0,400}?(ssh|remote )[\s\S]{0,400}?sleep"
    r"|tail +-f[^\n]*\.log"
    r"|until[^\n]{0,80}grep[^\n]{0,80}EXIT=")


def sh_adhoc_watch(src):
    """A hand-rolled remote watch loop. Use ops/watch.sh."""
    if "sanctioned-watcher:" in src:
        return []
    m = _ADHOC_WATCH.search(src)
    if not m:
        return []
    line = src[:m.start()].count("\n") + 1
    return [(ERROR, line,
             "hand-rolled remote watch loop. Use `ops/watch.sh <slug>` — it "
             "emits progress, detects SOLVE exit AND MACHINE exit, mirrors to "
             "<slug>.watch.log, and warns when its filter is blind. If it lacks "
             "something, FIX THE WATCHER (ops/watchrig_test.sh has 16 tests). "
             "A sanctioned exception carries `sanctioned-watcher: <why>`.")]


SHELL_RULES = [sh_adhoc_watch, sh_pkill, sh_unguarded_mkfs, sh_rm_rf_var, r_ps_e_with_C]
SH_BAD = {
    "sh_adhoc_watch": 'while true; do\n  ssh host "grep EXIT= run.log"\n  sleep 60\ndone\n',

    "sh_pkill": "pkill -TERM -f myjob.py\n",
    "sh_unguarded_mkfs": "sudo mkfs.ext4 /dev/nvme1n1\n",
    "sh_rm_rf_var": 'rm -rf $PREFIX/build\n',
    "r_ps_e_with_C": "ps -eo pid= -C palace\n",
}
SH_GOOD = ('sudo blkid "$DEV" || sudo mkfs.ext4 "$DEV"\n'
           'ps -o pid=,args= -C palace | tail -n +1 | xargs -r kill\n'
           'rm -rf "${PREFIX:?}/build"\n')
# ---------------------------------------------------------------------------
# 🔴 User, 2026-08-25: *"There might be a linter opportunity. Any value not read
# from baselines.json is an error."*
#
# baselines.json was created 2026-08-20 with wall_sigma() as the pattern: bind
# the name, REFUSE if undeclared. It ended with ONE entry while 49 measured
# values went into rigs as literals. The audit that found them is
# hardcoded_audit.py; this rule is what stops the next one.
#
# 🔑 RATCHET, NOT BIG BANG. Every finding below is GRANDFATHERED by (file, name)
# so the gate does not brick 27 existing rigs. A NEW hardcoded value is an ERROR
# immediately. THIS LIST MAY ONLY SHRINK — deleting an entry is the fix, adding
# one is how the rule dies.
#
# Worst of what it grandfathers, so the burn-down has an order:
#   NE = 1e20 in NINE rigs   — anchored at 7.3-8.6e18 on 2026-08-24; 13x high
#   44,384 in EIGHT places under FIVE names — a RETRACTED eta.reference (7c)
#   35,000,000 in THREE rigs — wall_sigma() exists precisely to bind this
_HARDCODED_GRANDFATHERED = {
    "dimensionless.py":          {"C_MM_GHZ", "EPS0", "F0"},
    "e0k2_anchor.py":            {"BAND_HALFWIDTH_MHZ"},
    "e0k2_sizeq.py":             {"BARE_Q"},
    "e0l_scaling.py":            {"A_MM", "L_MM"},
    "e3_closure.py":             {"NE"},
    "facetcount.py":             {"A_MM", "L_MM"},
    "h1_aspect.py":              {"F0", "SIGMA"},
    "h2_groove.py":              {"SIGMA", "WIDTH"},
    "h2b_groovescale.py":        {"Q_TE011_BARE", "REFERENCE_GHZ", "SIGMA"},
    "h3_annular.py":             {"NE", "Q_REF"},
    "h3_cold.py":                {"NE_HOT", "Q_EMPTY_NO_LOOP"},
    "h3_driven.py":              {"COARSE_MIN_DEPTH_DB"},
    "h3_eigen.py":               {"Q_BARE"},
    "h3_eigenprobe.py":          {"R_MM"},
    "h3_groove.py":              {"NE"},
    "h3_hot.py":                 {"T_COLD_K"},
    "h3_ladder.py":              {"LOOP_D", "LOOP_HW"},
    "h3_loaded.py":              {"Q_BARE_EMPTY", "Q_BARE_WITH_LOOP", "Z_FRAC"},
    "h3_loopq.py":               {"ANCHOR_LOOP", "F_NOLOOP_GROOVED", "Q_NOLOOP_GROOVED", "V1_TOL_FRAC"},
    "h3_loopsize.py":            {"BETA_TARGET", "NE"},
    "h3_margin.py":              {"COLD_F0_FALLBACK", "GROOVE_W", "NE"},
    "h3_qext.py":                {"LOOPQ_EIGEN_NO_TORCH"},
    "h3_sapphire.py":            {"NE"},
    "h3_step3.py":               {"ANCHOR_GROOVED_GHZ", "DRIVEN_DIP_GHZ", "H3COLD_PICK_GHZ"},
    "h3_superpose.py":           {"NE", "Q_BARE"},
    "h4_field.py":               {"Q_BARE"},
    "h4_seed.py":                {"ETA_FLOOR", "ETA_SAT", "Q_BARE"},
    "physics.py":                {"ETA0", "T_GAS_ANCHOR_K"},
    "probecheck.py":             {"NE", "R_MM"},
    "resplit.py":                {"A_MM", "L_MM"},
    "results.py":                {"EPS0"},
}


# 🔴 A DUPLICATE KEY IN THE DICT ABOVE SILENTLY DROPS THE FIRST ENTRY.
# 2026-08-25: appending geometry residue re-used five file names that were
# already keys, so h3_loaded's two RETRACTED Qs stopped being grandfathered and
# the ratchet quietly changed shape. Python does not warn. This does.
def _assert_no_dupe_keys():
    import pathlib as _pl, re as _re, collections as _c
    src = _pl.Path(__file__).read_text(encoding="utf-8")
    body = _re.search(r"_HARDCODED_GRANDFATHERED = \{(.*?)\n\}", src, _re.S)
    if not body:
        return
    keys = _re.findall(r'^\s*"([^"]+)":', body.group(1), _re.M)
    dupes = [k for k, c in _c.Counter(keys).items() if c > 1]
    if dupes:
        raise SystemExit(f"preflight: duplicate grandfather keys {dupes} — the "
                         f"later entry silently REPLACES the earlier one. Merge "
                         f"them.")


_MEASURED = [
    (re.compile(r"Q"), lambda v: abs(v) > 50, "a Q"),
    (re.compile(r"SIGMA|COND"), lambda v: abs(v) > 1e5, "a conductivity"),
    (re.compile(r"GHZ|FREQ|F0|_F$"), lambda v: 0.1 < abs(v) < 100, "a frequency"),
    (re.compile(r"NE|N_E|DENS"), lambda v: abs(v) > 1e14, "a density"),
    (re.compile(r"EPS|PERMIT|TAND"), lambda v: 0 < abs(v) < 100, "a material property"),
    (re.compile(r"TEMP|_K$|KELVIN"), lambda v: abs(v) > 100, "a temperature"),
    # 🔴 ADDED 2026-08-25. The rule only ever looked at names matching the
    # patterns above, so GEOMETRY was INVISIBLE to it: `DL = 1.525` lived in two
    # files, the frozen groove `(5.0, 10.0)` in SEVEN, the design loop
    # `11.0, 8.0` in NINE — and `A_MM, L_MM = 103.70, 88.53`, a cavity H1
    # REJECTED, sat as GEO's default in a fourth. None of it was grandfathered;
    # none of it was ever seen. A linter that cannot see a class of value
    # reports a clean sweep over it.
    (re.compile(r"GROOVE|LOOP|CAP_R|^A_MM|^L_MM|^DL$|D_OVER"),
     lambda v: abs(v) > 0, "a geometry dimension"),
]
_MACHINERY = re.compile(r"^(N_|MAX|MIN|TOL|STEP|TIMEOUT|SIZE_|SECTORS|ORDER|"
                        r"SAMPLES|SEED|DPI|VERBOSE|DEBUG|.*_S$|.*_DEG$|"
                        r".*_ITER.*|.*_COUNT)")


def r_hardcoded_value(src, tree, path=None):
    """A MEASURED value must come from baselines.json, not from a literal."""
    if tree is None:
        return []
    fname = (path or "").split("/")[-1]
    allowed = _HARDCODED_GRANDFATHERED.get(fname, set())
    skip = _fixture_lines(tree)
    out = []
    for node in tree.body:
        if not isinstance(node, ast.Assign) or node.lineno in skip:
            continue
        for t in node.targets:
            if not isinstance(t, ast.Name) or not t.id.isupper():
                continue
            if _MACHINERY.match(t.id) or t.id in allowed:
                continue
            v = node.value
            if isinstance(v, ast.Constant) and isinstance(v.value, (int, float)):
                val = v.value
            elif (isinstance(v, ast.UnaryOp) and isinstance(v.op, ast.USub)
                  and isinstance(v.operand, ast.Constant)):
                val = -v.operand.value
            elif isinstance(v, ast.Tuple) and v.elts:
                # ⚠️ TUPLE ONLY, NEVER LIST. `(11.6, 3.5e-5)` is one compound
                # VALUE — eps and tan-delta of a material. `[1e18, 1e19, 1e20]`
                # is a SWEEP AXIS, the independent variable of an experiment,
                # and flagging it is nonsense. Including lists made this rule
                # fire on e0q's SIGMAS, h3_hot's T_WALL_K and h3_loaded's NE —
                # three legitimate sweeps — which is how a ratchet bricks a
                # corpus (CONVENTIONS 7aw).
                # 🔴 A TUPLE HID ONE. e3_closure's
                # `TORCH_SAPPHIRE = (11.6, 3.5e-5)` carried the sapphire
                # permittivity — the value that turned out to be the WRONG AXIS
                # — and this rule walked straight past it because it only
                # looked at scalars. Take the first numeric element.
                first = v.elts[0]
                if isinstance(first, ast.Constant) and isinstance(
                        first.value, (int, float)):
                    val = first.value
                else:
                    continue
            else:
                continue          # a call (values.get(...), wall_sigma()) is fine
            if isinstance(val, bool):
                continue
            # 🔴 A gmsh PHYSICAL-GROUP ID IS NOT A MEASUREMENT. `TAG_LOOP = 92`
            # matched the geometry pattern on "LOOP" with `abs(v) > 0` and was
            # reported as a hardcoded dimension on every single run of the main
            # geometry file. `TAG_GROOVE` hit the identical false positive and
            # was silenced by GRANDFATHERING it — the wrong direction for a
            # ratchet that may only shrink, and it left a standing ERROR that
            # trains the reader to skim past preflight output.
            # Narrow on purpose: TAG_<NAME> holding a small positive integer.
            if (t.id.startswith("TAG_") and isinstance(val, int)
                    and 0 < val < 1000):
                continue
            for pat, rng, what in _MEASURED:
                if pat.search(t.id) and rng(val):
                    out.append((ERROR, node.lineno,
                                f"{t.id} = {val!r} looks like {what} hardcoded. "
                                f"Measured values live in baselines.json: "
                                f"values.get('<name>', **context). If it is not "
                                f"a measurement, rename it so it does not read "
                                f"as one."))
                    break
    return out


# ---------------------------------------------------------------------------
# 🔴 User, 2026-08-25: *"Any output files have to contain the slug as well, so
# that we don't have the results.json collision from before."*
#
# `h3_driven` wrote `h3_driven.result.json` — named for the PROGRAM. Every run
# of that program aimed at the same path, so a re-run overwrote the previous
# run's numbers, and an rsync then pushed a day-old copy back over the fresh
# one with its mtime preserved, making the clobber invisible (CONVENTIONS 7ap).
# There were 29 such files in this directory when the rule was written.
#
# 🔑 RATCHET: the 32 existing rigs are grandfathered. A NEW rig must take its
# tag from slug.parse()/slug.out(), and THIS LIST MAY ONLY SHRINK.
_RIG_NAMED_TAGS = {
    "e0k",
    "e0k2",
    "e0k2_azim",
    "e0k2_bare",
    "e0k2_betacause",
    "e0k2_portfix",
    "e0k2_sizeq",
    "e0kp",
    "e0q",
    "e3_closure",
    "h1",
    "h2",
    "h2b",
    "h3_annular",
    "h3_cold",
    "h3_driven",
    "h3_eigen",
    "h3_eigenprobe",
    "h3_groove",
    "h3_hot",
    "h3_ladder",
    "h3_loaded",
    "h3_loopq",
    "h3_loopsize",
    "h3_margin",
    "h3_qext",
    "h3_sapphire",
    "h3_step3",
    "h3_superpose",
    "h4_field",
    "h4_seed",
    "probecheck",
}


# 🔴 REFUSABLE VALUES AND THE PRINTS THAT FORGET THEM. 2026-09-04: making
# `Q_EXT_MEASURED` and `Q0_COLD_EIGEN` refusable (None when the store has no
# value for THIS geometry) was correct — and it crashed three separate runs,
# each time in a PRINT, each time after a solve had already cost 1,000+ s, and
# once BEFORE `save()` so the case was lost outright.
# 🔑 Print-only consumers are the easiest to miss: they sit on no success path
# any test exercises. Making a value refusable is only HALF the change.
# 🔴 NAME-BASED, AND THAT IS THE BLIND SPOT. 2026-09-06: `ne` became REFUSABLE
# (None on a prescribed-(eps, sigma) sweep) and this list was not updated, so the
# rule could not see it and h3-q0map-01 died formatting `{ne:.1e}` — AFTER a
# 1,699 s solve, the exact cost this rule exists to prevent.
# ⚠️ Making a value refusable is therefore TWO edits, and the second is easy to
# skip because the code works until the None actually arrives.
# ⚠️ `ne` needs boundaries or it matches `line`, `n_e`, `done`.
_REFUSABLE = re.compile(r"Q0_COLD_EIGEN|Q_EXT_MEASURED|Q_EXT_EST|q0c|_q0ref"
                        r"|(?<![\w.])ne(?![\w.])")
# 🔑 SOME NAMES ARE REFUSABLE ONLY IN ONE FILE. `ne` is None ONLY on h3_driven's
# prescribed-(eps, sigma) path; in h3_eigen / h3_loaded / h4_seed it always comes
# from a real density grid and cannot be None. Flagging it everywhere produced 8
# findings across 5 rigs that are all FALSE — and a noisy rule is a rule people
# learn to ignore, which is worse than no rule.
# ⚠️ Absent from this map = refusable EVERYWHERE, which is the safe default.
_REFUSABLE_ONLY_IN = {"ne": {"h3_driven.py"}}
# 🔴 THE SPEC MAY CARRY FILL AND ALIGNMENT, AND THIS MISSED THEM. `[,.0-9]*`
# matched `{ne:.1e}` and `{ne:,.0f}` but NOT `{ne:>9.1e}` or `{ne:>8.2f}` — and
# `>` alignment is the house style for every table in this repo. So the rule was
# blind to the most common shape it exists to catch, and h3-q0map-01 died on
# `{p['ne']:>9.1e}` — the FOURTH such site, after 1,699 s and 8 solves.
# ✅ Accept any spec that ENDS in a numeric presentation type.
_NUMFMT = re.compile(r"\{[^{}]*?(" + _REFUSABLE.pattern + r")[^{}]*?:[^{}]*?[fdge]\}")


# 🔴 THE 5x RULE'S BLIND SPOT. "No constants in scripts" (INCIDENTS 7bi) is the
# most-repeated rule in this programme — learned 5 times — because
# `r_hardcoded_value` only ever saw module-level UPPERCASE assignments. It could
# not see a physical value passed as a CLI-ARG STRING LITERAL, which is where all
# three of 2026-09-03/04's wrong-cavity constants lived, including
# `"--torch-material", "1.0,3.5e-05"` — the line that made `h3_driven` unable to
# mesh the design cavity at all, for nine days, silently.
# 🔑 RATCHET, following `_HARDCODED_GRANDFATHERED`: the 51 existing pairs are
# grandfathered so this does not brick 28 rigs. A NEW one is an error.
# **THIS LIST MAY ONLY SHRINK.**
_CLI_LITERAL_GRANDFATHERED = {
    # ✅ EXEMPT entries are NOT debt: the literal IS the experiment (a
    #    perturbation, a sweep axis, or throwaway geometry for a utility).
    # 🔴 DEBT entries are real physical values that should bind. THIS is
    #    what 'the list may only shrink' is about — count the DEBT lines.
    'cachetest.py': ['--length', '--order', '--radius', '--sectors', '--size-factor'],  # ✅ EXEMPT: arbitrary geometry — this rig tests CACHE IDENTITY, not physics
    'e0_solver_vs_math.py': ['--chimney', '--feed', '--groove', '--mode-filter', '--n-wl', '--order', '--sectors', '--trap', '--viewport'],  # 🔴 DEBT: bind these
    'e0b_offset.py': ['--offset'],  # ✅ EXEMPT: --offset is a deliberate rigid-motion PERTURBATION, not a measurement
    'e0c_rigid.py': ['--offset'],  # ✅ EXEMPT: ditto — rigid-motion probe
    'e0d_transverse.py': ['--rotate'],  # ✅ EXEMPT: --rotate is the probe itself
    'e0i_rigid_at_order2.py': ['--offset', '--rotate'],  # ✅ EXEMPT: rigid-motion probe at order 2
    'e0k2_portfix.py': ['--sectors'],  # 🔴 DEBT: bind these
    # ⚠️ DO NOT BIND: 25.8x19.4 (1,001 mm^2) is NOT the canonical 11x8
    #    (176 mm^2) — 5.7x the area. This rig predates loop.size.mm and its
    #    results are cited NOWHERE in KNOWN/NEXT/OPTIMIZER. Binding it to the
    #    canonical loop would silently CHANGE WHAT IT MESHES and rewrite what
    #    the run actually did. The literal is the RECORD of its geometry.
    'e0k_driven_vs_eigen.py': ['--loop', '--loop-phi'],  # ✅ EXEMPT: historical geometry
    'meshstage.py': ['--ho-optimize', '--order'],  # ✅ EXEMPT: --order/--ho-optimize are the SWEEP AXIS of this rig
    'portcheck.py': ['--sectors'],  # 🔴 DEBT: bind these
}


_CLI_FLAG = re.compile(r"^--[a-z][a-z-]*$")
_CLI_NUM = re.compile(r"^[0-9][0-9.,e+-]*$")


def r_cli_literal(src, tree, path=None):
    """A physical value passed as a CLI-arg string literal, not bound."""
    if tree is None:
        return []
    fname = (path or "").split("/")[-1]
    alw = set(_CLI_LITERAL_GRANDFATHERED.get(fname, ()))
    skip = _fixture_lines(tree)
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.List, ast.Tuple)):
            continue
        els = node.elts
        for a, b in zip(els, els[1:]):
            if not (isinstance(a, ast.Constant) and isinstance(a.value, str)
                    and isinstance(b, ast.Constant) and isinstance(b.value, str)):
                continue
            if not (_CLI_FLAG.match(a.value) and _CLI_NUM.match(b.value)):
                continue
            if a.value in alw or getattr(a, "lineno", 0) in skip:
                continue
            out.append((ERROR, getattr(a, "lineno", 0),
                        f'{a.value} "{b.value}" is a physical value passed as a '
                        f'CLI string literal. Bind it from baselines.json (or '
                        f'take it from the run config) — this is the blind spot '
                        f'that hid the hardcoded torch for nine days.'))
    return out


def r_none_format(src, tree, path=None):
    """A refusable value formatted with a numeric spec and no None guard."""
    out = []
    lines = src.split("\n")
    # 🔑 PRIOR ART, not a new mechanism: `_fixture_lines` already exists for
    # exactly this — the BAD/GOOD fixtures deliberately contain the forbidden
    # pattern, so a raw-text rule must not report them. r_hardcoded_value uses it.
    skip = _fixture_lines(tree) if tree is not None else set()
    for i, line in enumerate(lines, 1):
        if i in skip:
            continue
        # the explicit marker may sit on the line or just above the block it
        # covers — a bounded lookback is safe BECAUSE the marker is explicit;
        # the same lookback on a keyword like "is not None" would not be.
        if any("refusable-ok" in lines[j]
               for j in range(max(0, i - 4), min(len(lines), i))):
            continue
        # 🔑 THIS RULE IS IN `RAW` — it must see comments, because its own
        # escape IS a comment. The cost is that it also sees format specs quoted
        # inside comments and docstrings, so skip comment-only lines.
        if line.lstrip().startswith("#"):
            continue
        m = _NUMFMT.search(line)
        if not m:
            continue
        # guarded if the same line carries an explicit None test or uses _q()
        # ✅ EXPLICIT ESCAPE, not a wider proximity window. A guard can sit on
        # an enclosing `if`, which no same-line test can see and which a
        # multi-line heuristic would get wrong in both directions. Mark it
        # `refusable-ok: <why>` — same convention as `q:ok` and `ret:<id>`.
        # 🔴 THE GROUP IS LOad-BEARING. This was `r"if\s+" + _REFUSABLE.pattern`,
        # and alternation binds LOOSER than concatenation — so it parsed as
        #   (if\s+Q0_COLD_EIGEN) | Q_EXT_MEASURED | Q_EXT_EST | q0c | _q0ref
        # i.e. every name AFTER the first matched BARE, anywhere on the line, and
        # the rule treated its own targets as already-guarded. It could only ever
        # fire for Q0_COLD_EIGEN. Found 2026-09-06 when adding `ne` and asking why
        # the new name still did not trip it.
        # ⚠️ SO THE RULE WAS ~80% DEAD SINCE IT WAS WRITTEN — the rule created
        # because "this exact shape killed three runs on 2026-09-04, each after a
        # solve", and which then failed to catch a fourth on 2026-09-06.
        if ("is not None" in line or "_q(" in line or "refusable-ok" in line
                or re.search(r"if\s+(?:" + _REFUSABLE.pattern + r")", line)):
            continue
        _only = _REFUSABLE_ONLY_IN.get(m.group(1))
        # ⚠️ basename by split, not pathlib — preflight imports ast/io/re/sys/
        # tokenize and nothing else, deliberately: it must run anywhere.
        if _only and (path is None or path.replace("\\", "/").rsplit("/", 1)[-1]
                      not in _only):
            continue
        out.append((ERROR, i,
                    f"{m.group(1)} is REFUSABLE (None when the store has no value "
                    f"for this geometry) but is formatted with a numeric spec and "
                    f"no guard on this line. Use _q(), or test it. This exact "
                    f"shape killed three runs on 2026-09-04, each after a solve."))
    return out


def r_output_not_slugged(src, tree, path=None):
    """A module-level literal TAG names the PROGRAM, so every run collides."""
    if tree is None:
        return []
    skip = _fixture_lines(tree)
    out = []
    for node in tree.body:
        if not isinstance(node, ast.Assign) or node.lineno in skip:
            continue
        for t in node.targets:
            if (isinstance(t, ast.Name) and t.id == "TAG"
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)):
                if node.value.value in _RIG_NAMED_TAGS:
                    continue
                out.append((ERROR, node.lineno,
                            f'TAG = "{node.value.value}" names the PROGRAM, not '
                            f'the RUN — every run of it writes to the same '
                            f'.result.json and overwrites the last. Take the '
                            f'tag from the slug: TAG = slug.parse(); outputs '
                            f'via slug.out()/slug.outfile().'))
    return out



_MATERIAL_KW = re.compile(r"eps|tand|sigma|cond|permit|loss")


def r_material_kwarg(src, tree, path=None):
    """A material property as a keyword DEFAULT is still a constant in a script.

    🔴 User, 2026-08-25: "there should be absolutely no constants in any
    scripts." geometry.py held FIFTY-EIGHT keyword defaults, sixteen of them
    physical — including `torch_eps=11.6`, which was the WRONG ANISOTROPY AXIS
    for the entire programme. r_hardcoded_value could not see any of them: they
    are lowercase kwargs inside a `dict(...)` call, not module-level UPPERCASE
    assignments. The largest constant store in the corpus was unchecked.

    ⚠️ Scoped to MATERIAL properties, not dimensions. Dimensions come from the
    slug config for every real run (7ba) and their defaults are the burn-down
    list; a material default is what silently persists.
    """
    if tree is None:
        return []
    skip = _fixture_lines(tree)
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or node.lineno in skip:
            continue
        for kw in node.keywords:
            if not kw.arg or not _MATERIAL_KW.search(kw.arg):
                continue
            v = kw.value
            if isinstance(v, ast.Constant) and isinstance(v.value, (int, float)) \
                    and not isinstance(v.value, bool) and v.value not in (0, 1):
                out.append((ERROR, node.lineno,
                            f"{kw.arg}={v.value!r} is a MATERIAL property as a "
                            f"keyword default — a constant in a script. Bind it: "
                            f"values.get('<canonical.name>'). geometry.py's "
                            f"torch_eps=11.6 was the wrong anisotropy axis and "
                            f"nothing could see it."))
    return out



# ── the rename that broke two consumers, 2026-08-25 ──────────────────────────
# `wall.conductivity` -> `wall.conductivity.s_per_m` was applied to the store and
# to e0k2_anchor.wall_sigma(). solveconf.py and condcheck.py each did their OWN
# json.loads(baselines.json)[literal key] and nothing knew they existed. A rig
# failed 40 minutes in, from a guard whose entire purpose was to catch a missing
# wall metal. r_hardcoded_value could not see it: the VALUE was not hardcoded,
# the NAME was.
# 🔑 A canonical name has consumers, and a store with no consumer index cannot
# tell you what a rename breaks. Route every read through values.get().
_BASELINE_ACCESSORS = {"values.py", "slug.py", "migrate_slugs.py", "preflight.py"}


def r_direct_baseline_read(src, tree, path=None):
    """A canonical name must be read through values.get(), not by literal key."""
    if tree is None or path is None:
        return []
    import os
    if os.path.basename(path) in _BASELINE_ACCESSORS:
        return []
    try:
        import json as _j, pathlib as _p
        names = set(_j.loads((_p.Path(__file__).with_name("baselines.json"))
                             .read_text()).keys())
    except Exception:
        return []
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Subscript):
            continue
        k = n.slice
        if isinstance(k, ast.Constant) and isinstance(k.value, str):
            nm = k.value
            if nm in names or (
                    "." in nm and any(x.startswith(nm + ".") for x in names)):
                out.append((ERROR, n.lineno,
                            f"reads canonical name {nm!r} by literal key. "
                            f"Renaming that name will break this silently and "
                            f"the store cannot tell you it happened — this is "
                            f"how h3-bore-01 died 40 min in. "
                            f"Use values.get({nm!r})."))
    return out

RULES = [r_none_format, r_cli_literal, r_direct_baseline_read, r_timeout, r_pkill, r_main_guard, r_help_percent, r_ps_e_with_C,
         r_falsy_numeric_flag, r_bare_background, r_nearest_match,
         r_undefined_name, r_hardcoded_value,
         r_output_not_slugged, r_material_kwarg]

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
    # 🔴 an ungrandfathered file (self-test passes no path) hardcoding a Q
    "r_hardcoded_value": "Q_BARE = 44384.0\n",
    # 🔴 a NEW rig naming its outputs after itself
    "r_cli_literal": 'X = ["--torch-material", "1.0,3.5e-05"]\n',
    "r_none_format": 'print(f"{Q0_COLD_EIGEN:,.0f}")\n',
    "r_output_not_slugged": 'TAG = "my_new_rig"\n',
    "r_material_kwarg": "P = dict(torch_eps=11.6)\n",
    "r_nearest_match": "y = min(v, key=lambda x: abs(x - t))\n",
    # the real failure: an import dropped in a refactor, used in a function
    "r_undefined_name": "def f():\n    return eigen_cfg(1)\n"
                        "if __name__ == '__main__':\n    f()\n",
}
GOOD = ('import subprocess\n'
        'def f():\n    subprocess.Popen(["x"]).wait(timeout=5)\n'
        'if __name__ == "__main__":\n    f()\n')

BAD["r_direct_baseline_read"] = (
    # the literal line from solveconf.py that the 2026-08-25 rename orphaned
    'import json, pathlib\n'
    'b = json.loads(pathlib.Path("baselines.json").read_text())\n'
    '_sig = b["wall.conductivity"]["value"]\n')



def lint(path):
    src = open(path).read()
    if path.endswith((".sh", ".bash")) or src.startswith("#!/usr/bin/env bash") \
            or src.startswith("#!/bin/bash"):
        return [f for rule in SHELL_RULES for f in rule(src)]
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [(ERROR, e.lineno or 0, f"SyntaxError: {e.msg}")]
    blanked = code_only(src)
    out = []
    for rule in RULES:
        text = src if rule.__name__ in RAW else blanked
        # 🔑 r_hardcoded_value grandfathers by (FILE, name), so it needs the
        # path. Passing it positionally to every rule would break their
        # signatures, so it is opt-in by keyword.
        if "path" in rule.__code__.co_varnames[:rule.__code__.co_argcount]:
            out += rule(text, tree, path=path)
        else:
            out += rule(text, tree)
    return out


def self_test():
    _assert_no_dupe_keys()
    ok = True
    for rule in SHELL_RULES:
        src = SH_BAD[rule.__name__]
        hit, miss = rule(src), rule(SH_GOOD)
        good = bool(hit) and not miss
        ok &= good
        print(f"  {'✅' if good else '🔴'} {rule.__name__:<22} "
              f"fires on known-bad: {bool(hit)}   quiet on known-good: "
              f"{not miss}")
    for rule in RULES:
        src = BAD[rule.__name__]
        # 🔑 path-taking rules return [] when path is None, so calling them
        # without one makes them PASS the self-test while being dead in the
        # sweep — a check that cannot fail (7d). Thread the same opt-in
        # keyword lint() uses, with a name that is not an accessor.
        kw = ({"path": "rig_under_test.py"}
              if "path" in rule.__code__.co_varnames[:rule.__code__.co_argcount]
              else {})
        hit = rule(src, ast.parse(src), **kw)
        miss = rule(GOOD, ast.parse(GOOD), **kw)
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
    _assert_no_dupe_keys()
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
