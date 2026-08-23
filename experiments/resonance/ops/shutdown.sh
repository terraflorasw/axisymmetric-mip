#!/usr/bin/env bash
# Bring the instance down CLEANLY at the end of a session.
#
# 🔴 ORDER MATTERS AND THE GUARDS ARE NOT OPTIONAL.
#   1. REFUSE if a rig or any Palace rank is alive — halting mid-solve loses
#      the case in flight and, worse, can leave a half-written result file that
#      the next session reads as complete.
#   2. sync, then UNMOUNT /opt/amip, and VERIFY the unmount succeeded. DEPLOY.md:
#      a snapshot (or a halt) taken while the filesystem is mounted and being
#      written risks a corrupt volume. The volume is the only thing of value —
#      the instance is disposable, the toolchain and every solved case are not.
#   3. only then halt.
#
# ⚠️ This is a SPOT instance: "instance initiated shutdown behavior" is normally
# TERMINATE, so this ends the instance. That is intended — the data volume is a
# SEPARATE EBS volume and survives, as it has through two reclamations already.
#
#   ops/go ops/shutdown.sh            # refuses if anything is running
#   ops/go ops/shutdown.sh --force    # halt even if a rig is alive (say why)
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
H="$AMIP_HOST"
set -uo pipefail
FORCE="${1:-}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}

echo "== pre-flight: is anything still running? =="
BUSY=$(timeout 30 ssh -i "$K" -o ConnectTimeout=15 "$H" \
  'r=$(ps -C python3 -o args= 2>/dev/null | grep -c "^python3 -u [eh][0-9]")
   g=$(ps -C python3 -o args= 2>/dev/null | grep -c "geometry\.py")
   n=$(ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -v Z | wc -l)
   echo $(( ${r:-0} + ${g:-0} + ${n:-0} ))' 2>/dev/null)
if [ -z "$BUSY" ]; then
  echo "  🔴 could not reach the instance. It may already be down."
  exit 1
fi
echo "  live rig/mesh/rank processes: $BUSY"
if [ "$BUSY" != "0" ] && [ "$FORCE" != "--force" ]; then
  echo "  🔴 REFUSING to shut down with $BUSY process(es) alive."
  echo "     Halting mid-solve loses the case in flight and can leave a"
  echo "     half-written result the next session reads as complete."
  echo "     Wait, or re-run with --force if you know it is safe."
  exit 1
fi
[ "$BUSY" != "0" ] && echo "  ⚠️ --force given: halting with $BUSY process(es) alive"

echo "== unmount the data volume, and VERIFY =="
timeout 120 ssh -i "$K" "$H" '
  sync
  if ! mountpoint -q /opt/amip; then
    echo "  /opt/amip already unmounted"
  else
    cd /
    # lazy umount would return success while the fs is still in use, which is
    # exactly the silent failure this check exists to prevent. Plain umount.
    if sudo umount /opt/amip; then
      echo "  unmounted /opt/amip"
    else
      echo "  🔴 umount FAILED — something still holds it:"
      sudo lsof +D /opt/amip 2>/dev/null | head -10 || true
      sudo fuser -vm /opt/amip 2>&1 | head -10 || true
      exit 1
    fi
  fi
  if mountpoint -q /opt/amip; then
    echo "  🔴 STILL MOUNTED after umount — refusing to halt"; exit 1
  fi
  echo "  ✅ verified unmounted"' || {
  echo "  🔴 unmount step failed — NOT halting. The volume is the only thing"
  echo "     of value here; a dirty halt is not worth saving a few cents."
  exit 1
}

echo "== halt =="
# 🔴 The connection dies WITH the machine, so ssh returns non-zero. That is
# success, not failure. Do not treat the exit code as the outcome — verify by
# probing afterwards.
timeout 30 ssh -i "$K" "$H" 'sudo shutdown -h now' >/dev/null 2>&1
echo "  halt issued; ssh drops with the machine, so its exit code means nothing"
echo "  verifying the instance is actually gone..."
for i in 1 2 3 4 5 6; do
  sleep 10
  if ! timeout 12 ssh -i "$K" -o ConnectTimeout=8 -o BatchMode=yes "$H" \
       'exit 0' >/dev/null 2>&1; then
    echo "  ✅ instance is unreachable — down after $((i*10))s"
    echo
    echo "  ⚠️ The EBS DATA VOLUME survives and is now cleanly unmounted."
    echo "     Recover with: launch a spot c7a.8xlarge IN THE VOLUME'S AZ,"
    echo "     attach it, set the new address in ops/env.sh, then"
    echo "     NOSYNC=1 ops/go ops/mount.sh"
    exit 0
  fi
  echo "    still reachable after $((i*10))s..."
done
echo "  🔴 STILL REACHABLE after 60s. The halt may not have taken."
echo "     Check the AWS console; do not assume it is down."
exit 1
