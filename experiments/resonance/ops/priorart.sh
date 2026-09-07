#!/usr/bin/env bash
# Has this failed before?  ops/priorart.sh <term> [term...]
#
# 🔴 RUN THIS BEFORE FORMING A HYPOTHESIS ABOUT A FAILURE. CONVENTIONS already
# says "when a solve fails, the FIRST question is 'has this failed before?'" —
# the rule was violated TWICE on 2026-09-02/03 (the viewport's ns=1 constraint,
# and R4's eps-near-zero conditioning), both times costing hours chasing a
# symptom the record had already diagnosed. The rule was not missing. A trigger
# was.
#
# Searches, in the order the answer is usually found:
#   1. NEXT.md R-items      — the table of what went wrong and why
#   2. KNOWN.md PRIOR ART   — which rig already solved what
#   3. CONVENTIONS.md       — instrument behaviour learned the hard way
#   4. rig docstrings/comments — the corpus; the index is only a convenience
#   5. geometry.py comments — constraints discovered while building meshes
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1
[ $# -ge 1 ] || { sed -n '2,20p' "$0"; exit 1; }
# 🔴 THE RECORD MIXES GREEK AND ASCII — "ε-near-zero" and "eps-near-zero",
# "λ/4" and "lambda/4", "χ′₀₁" and "chi'_01". A search for one form MISSES the
# other, and that is exactly how R4 was missed on 2026-09-03: it is written with
# a Greek epsilon. Every term is therefore searched in both alphabets.
_variants() {
  printf '%s\n' "$1"
  # 🔴 \< \> ARE LOAD-BEARING. Without them s/chi/χ/ rewrote "machine" to
  # "maχne", so a prior-art search for it searched a string that cannot exist —
  # the same class of silent miss this tool was built to stop.
  # ⚠️ η, ν, σ and the ₀ subscripts were MISSING here: `eta` and `η` returned
  # different result sets, as did Q0/Q₀ and f0/f₀ (audit 2026-09-03).
  printf '%s\n' "$1" | sed 's/\<eps\>/ε/g; s/\<lambda\>/λ/g; s/\<omega\>/ω/g; s/\<beta\>/β/g; s/\<chi\>/χ/g; s/\<eta\>/η/g; s/\<nu\>/ν/g; s/\<sigma\>/σ/g; s/\<Q0\>/Q₀/g; s/\<f0\>/f₀/g'
  printf '%s\n' "$1" | sed 's/Q₀/Q0/g; s/f₀/f0/g; s/ε/eps/g; s/λ/lambda/g; s/ω/omega/g; s/β/beta/g; s/χ/chi/g; s/η/eta/g; s/ν/nu/g; s/σ/sigma/g'
  # ✅ THE WAVELENGTH IS A THREE-WAY. From 2026-09-03 the record writes it out as
  # `wavelength`, but git history, the earlier documents and the literature all
  # carry `λ` and `lambda` — and `lambda` is ALSO Python's keyword, which is why
  # the word was spelled out. All three forms must find each other, or the
  # rename would itself become the search failure this tool exists to prevent.
  # ⚠️ ONE MAPPING PER LINE: sed applies substitutions in sequence, so combining
  # them round-trips wavelength -> λ -> wavelength and emits no new variant.
  printf '%s\n' "$1" | sed 's/\<wavelength\>/λ/g'
  printf '%s\n' "$1" | sed 's/\<wavelength\>/lambda/g'
  printf '%s\n' "$1" | sed 's/\<lambda\>/wavelength/g'
  printf '%s\n' "$1" | sed 's/λ/wavelength/g'
}
for t0 in "$@"; do
 for t in $(_variants "$t0" | sort -u); do
  echo "═══ \"$t\""
  for f in NEXT.md KNOWN.md CONVENTIONS.md INSTRUMENT.md HYPOTHESES.md; do
    n=$(grep -icF -- "$t" "$f" 2>/dev/null || true)
    [ "${n:-0}" -gt 0 ] && { echo "── $f ($n)"; grep -inF -- "$t" "$f" | head -4 | cut -c1-160 | sed 's/^/   /'; }
  done
  n=$(grep -ilF -- "$t" ./*.py 2>/dev/null | tr '\n' ' ')
  [ -n "$n" ] && { echo "── rigs: $n"; grep -inF -- "$t" ./*.py 2>/dev/null | head -4 | cut -c1-160 | sed 's/^/   /'; }
  echo
 done
done
