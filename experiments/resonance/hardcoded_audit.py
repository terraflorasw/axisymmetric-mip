#!/usr/bin/env python3
"""Audit the corpus for MEASURED values hardcoded as module-level literals.

🔴 User, 2026-08-25: *"That's what baselines.json was for, but we kind of
drifted away from it. We should audit everything for hardcoded values."*

`baselines.json` was created 2026-08-20 to be the single store, with
`wall_sigma()` as the pattern: bind the name, REFUSE if undeclared. It ended
with ONE entry while every other measured value went into a rig as a literal.

WHAT THE FIRST RUN FOUND (2026-08-25), worst first:
  n_e = 1e20 in NINE rigs  -- the density was anchored at 7.3-8.6e18 on
                              2026-08-24. 13x too high. Every one of these,
                              re-run today, measures a plasma we do not build.
  44,384 in EIGHT places under FIVE names (BARE_Q, Q_BARE, Q_BARE_EMPTY,
                              Q_EMPTY_NO_LOOP, Q_TE011_BARE) -- and it is a
                              RETRACTED eta.reference (CONVENTIONS 7c).
  35,000,000 in THREE rigs -- despite wall_sigma() existing to bind exactly
                              this from baselines.json AND refuse without it.
  Q_REF means two things   -- 44,414 (h3_annular) vs 43,523 (h3_driven).

⚠️ HEURISTIC BY DESIGN. It flags on NAME pattern x VALUE range, so it
over-reports machinery and misses values with unusual names. It is a prompt to
look, not an authority. `preflight.r_hardcoded_value` is the ENFORCING version.
"""
import ast, pathlib, json, re, sys
ROOT=pathlib.Path('.')
# names that are plainly machinery, not measurements
MACH=re.compile(r'^(N_|MAX|MIN|TOL|STEP|TIMEOUT|SIZE_|SECTORS|ORDER|SAMPLES|'
                r'.*_S$|.*_DEG$|.*_ITER.*|.*_COUNT|SEED|DPI|VERBOSE|DEBUG)')
# value ranges that smell like MEASURED physics
def smells(name, v):
    if isinstance(v,bool) or not isinstance(v,(int,float)): return None
    a=abs(v)
    if 'Q' in name and a>50: return 'Q-like'
    if re.search(r'(SIGMA|COND)', name) and a>1e5: return 'conductivity'
    if re.search(r'(GHZ|FREQ|F0|_F$)', name) and 0.1<a<100: return 'frequency'
    if re.search(r'(NE|N_E|DENS)', name) and a>1e14: return 'density'
    if re.search(r'(EPS|PERMIT|TAND|LOSS)', name) and 0<a<100: return 'material'
    if re.search(r'(MM|RADIUS|LENGTH|DEPTH|WIDTH|GAP|_LD|_LW|_RW)', name) and 0<a<1000: return 'dimension'
    if re.search(r'(TEMP|_K$|KELVIN)', name) and a>100: return 'temperature'
    if re.search(r'(VSWR|BETA|ETA)', name): return 'derived-coupling'
    return None
def scan():
  rows=[]
  for f in sorted(ROOT.glob('*.py')):
    try: tree=ast.parse(f.read_text())
    except Exception: continue
    for node in tree.body:
        if not isinstance(node,ast.Assign): continue
        for t in node.targets:
            if not isinstance(t,ast.Name): continue
            n=t.id
            if not n.isupper() or MACH.match(n): continue
            v=node.value
            val=None
            if isinstance(v,ast.Constant) and isinstance(v.value,(int,float)): val=v.value
            elif isinstance(v,ast.UnaryOp) and isinstance(v.op,ast.USub) and isinstance(v.operand,ast.Constant):
                val=-v.operand.value
            elif isinstance(v,ast.Tuple) and all(isinstance(e,ast.Constant) and isinstance(e.value,(int,float)) for e in v.elts):
                val=tuple(e.value for e in v.elts)
            if val is None: continue
            probe = val[0] if isinstance(val,tuple) else val
            k=smells(n,probe)
            if k: rows.append((f.name,node.lineno,n,val,k))
  return rows


def main():
    print(json.dumps(scan()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
