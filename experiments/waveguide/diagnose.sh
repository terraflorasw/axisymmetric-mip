#!/usr/bin/env bash
# Self-diagnostic for the waveguide harness. Checks the failure modes that have
# actually occurred in this project, not generic health. Always exits 0 — the
# report IS the payload. Lines prefixed "!!" need action.
cd "$(dirname "$0")" || exit 0
echo "== diagnostic $(date -u '+%Y-%m-%d %H:%M:%SZ') =="

# 1. Solver liveness. NB: -C filters only when -e is absent, and comm is
#    truncated to 15 chars, so the name is palace-x86_64.b not ...bin.
LIVE=$(ps -o pid=,stat=,etime=,pcpu= -C palace-x86_64.b 2>/dev/null | awk '$2 !~ /Z/')
NRANK=$(printf '%s' "$LIVE" | grep -c . )
ZOMB=$(ps -o stat= -C palace-x86_64.b 2>/dev/null | grep -c Z)
if [ "$NRANK" -gt 0 ]; then
  ET=$(printf '%s\n' "$LIVE" | head -1 | awk '{print $3}')
  CPU=$(printf '%s\n' "$LIVE" | awk '{s+=$4} END{printf "%.0f", s}')
  echo "solver: $NRANK ranks, elapsed $ET, ${CPU}% CPU total"
  # a solve pinned near 0% CPU is stalled, not working
  [ "${CPU%.*}" -lt 20 ] && echo "!! ranks alive but CPU ${CPU}% — likely stalled or swapping"
else
  echo "solver: idle"
fi
[ "$ZOMB" -gt 0 ] && echo "zombies: $ZOMB defunct (PID 1 does not reap; filter state Z)"

# Zombie filter is required HERE TOO: a defunct rank's argv is
# "[palace-x86_64.b] <defunct>", so an unfiltered head -1 sets ACTIVE to the
# literal string "<defunct>" and every in-flight run gets misreported as
# truncated. Every ps query needs the state filter, not just the liveness one.
ACTIVE=$(ps -o stat=,args= -C palace-x86_64.b 2>/dev/null \
         | awk '$1 !~ /Z/ {print $NF; exit}' | sed 's/\.json$//')

# 2. Lost-notification detection: any log whose sentinel records a failure.
for f in *.log; do
  [ -e "$f" ] || continue
  LAST=$(tail -1 "$f" 2>/dev/null)
  case "$LAST" in
    EXIT=0) ;;
    EXIT=*) echo "!! $f ended $LAST — job failed, result never acted on" ;;
  esac
done

# 3. Truncated results: eig.csv without domain-E.csv means the analysis would
#    silently read nothing and mode classification would be wrong.
for d in postpro/*/; do
  [ -e "$d/eig.csv" ] || continue
  [ -e "$d/domain-E.csv" ] && continue
  # acknowledged dead runs: touch <dir>/.aborted to stop reporting them
  [ -e "$d/.aborted" ] && continue
  # Skip work in flight. Directory mtime does NOT update when a file inside is
  # written, so a time test fails here; match the live solver's config instead.
  # Its argv ends in <tag>.json and the output dir is postpro/<tag>.
  if [ -n "$ACTIVE" ] && [ "${d%/}" = "postpro/$ACTIVE" ]; then
    echo "   ${d%/} in progress (this is the running solve)"
  else
    echo "!! ${d%/} has eig.csv but no domain-E.csv — killed or truncated;"
    echo "   analysing it would silently misclassify modes"
  fi
done

# 4. Resources. Big order-2 meshes have run this box to ~6 GB available.
MEMA=$(awk '/MemAvailable/{printf "%.1f", $2/1048576}' /proc/meminfo)
SWFREE=$(awk '/SwapFree/{printf "%.0f", $2/1048576}' /proc/meminfo)
DISK=$(df -BG --output=avail . | tail -1 | tr -dc '0-9')
echo "resources: ${MEMA} GiB RAM available, ${SWFREE} GiB swap free, ${DISK} GiB disk free"
# Free RAM is the WRONG alarm here: there is ~63 GiB of swap, so the box does
# not OOM, it thrashes. An MPI sparse solve touching swap degrades badly —
# the failure mode is a 40-minute solve quietly becoming a 6-hour one. Measure
# paging RATE, which is the actual thrash signal.
SO=$(vmstat 1 2 | tail -1 | awk '{print $8}')
[ "${SO:-0}" -gt 1024 ] && echo "!! swapping out ${SO} KiB/s — solve is thrashing, expect a large slowdown"
[ "${SWFREE:-99}" -lt 4 ] && echo "!! swap under 4 GiB free — an OOM kill becomes possible"
[ "${DISK:-99}" -lt 5 ] && echo "!! disk under 5 GiB — paraview output can consume this fast"
echo "== end =="
