#!/usr/bin/env bash
# Mount the persistent data volume at /opt/amip on a replacement instance.
#
# 🔴 THIS SCRIPT NEVER FORMATS. bootstrap.sh owns mkfs, guarded by a blkid
# check; here an unformatted device means the WRONG device is attached, or the
# wrong volume, and the correct response is to stop. The volume carries the
# toolchain, the Palace build and every solved case — a mistaken mkfs is not
# recoverable from anything on this laptop.
#
# 🔴 DO NOT LET ops/go SYNC BEFORE THE MOUNT. /opt/amip on an unmounted
# instance is an empty directory on the ROOT volume; rsync would happily write
# the repo into it, the mount would then shadow it, and the result looks like a
# successful sync that vanished. Always:  NOSYNC=1 ops/go ops/mount.sh
#
#   NOSYNC=1 ops/go ops/mount.sh --inspect   # look, change nothing
#   NOSYNC=1 ops/go ops/mount.sh             # mount and verify
#
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
set -uo pipefail
H="$AMIP_HOST"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
PREFIX=/opt/amip
MODE="${1:-mount}"

echo "== $H =="
timeout 60 ssh -i "$K" -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new \
  "$H" "MODE='$MODE' PREFIX='$PREFIX' bash -s" <<'REMOTE'
set -uo pipefail

echo "-- block devices --"
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT | sed 's/^/  /'

if mountpoint -q "$PREFIX"; then
  echo "-- already mounted --"
else
  # Candidate = a whole disk, no filesystem label of its own mounted anywhere,
  # and no mounted partitions. Ask the direct question rather than assuming
  # nvme1n1: EBS device naming on Nitro is not guaranteed stable.
  mapfile -t CAND < <(lsblk -rno NAME,TYPE,MOUNTPOINT | awk '$2=="disk" && $3=="" {print $1}' \
    | while read -r d; do
        # a disk whose CHILDREN are mounted (the root volume) is not a candidate
        m=$(lsblk -rno MOUNTPOINT "/dev/$d" | grep -c .)
        [ "$m" = "0" ] && echo "/dev/$d"
      done)

  if [ "${#CAND[@]}" -eq 0 ]; then
    echo "  🔴 no unmounted disk found — is the volume attached?"; exit 1
  elif [ "${#CAND[@]}" -gt 1 ]; then
    echo "  🔴 ${#CAND[@]} unmounted disks: ${CAND[*]}"
    echo "     REFUSING to guess which one holds the data."; exit 1
  fi
  DEV="${CAND[0]}"
  FSTYPE=$(sudo blkid -o value -s TYPE "$DEV" 2>/dev/null)
  UUID=$(sudo blkid -o value -s UUID "$DEV" 2>/dev/null)
  echo "-- candidate: $DEV  fstype=${FSTYPE:-NONE}  uuid=${UUID:-none} --"

  if [ -z "$FSTYPE" ]; then
    echo "  🔴 $DEV HAS NO FILESYSTEM. That is not the data volume."
    echo "     This script does not format. Stopping."; exit 1
  fi
  if [ "$FSTYPE" != "ext4" ]; then
    echo "  🔴 $DEV is $FSTYPE, expected ext4. Stopping."; exit 1
  fi

  if [ "$MODE" = "--inspect" ]; then
    echo "  (inspect) would mount $DEV at $PREFIX"; exit 0
  fi

  sudo mkdir -p "$PREFIX"
  sudo mount "$DEV" "$PREFIX" || { echo "  🔴 mount failed"; exit 1; }
  echo "  mounted $DEV at $PREFIX"

  # fstab BY UUID, not by device path: nvme names can shuffle across launches
  # and a stale /dev/nvme1n1 line would mount the wrong disk at boot. nofail so
  # a missing volume never blocks boot.
  if [ -n "$UUID" ] && ! grep -q "$PREFIX" /etc/fstab; then
    echo "UUID=$UUID $PREFIX ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab >/dev/null
    echo "  fstab: UUID=$UUID"
  fi
  [ -w "$PREFIX" ] || { sudo chown "$USER" "$PREFIX"; echo "  chown $USER $PREFIX"; }
fi

echo "-- verify: is it MOUNTED, WRITABLE, and does it hold what we expect? --"
ok=1
mountpoint -q "$PREFIX" && echo "  ✅ $PREFIX is a mountpoint" || { echo "  🔴 NOT MOUNTED"; ok=0; }
t="$PREFIX/.writetest.$$"
if touch "$t" 2>/dev/null; then rm -f "$t"; echo "  ✅ writable"; else echo "  🔴 WRITE TEST FAILED"; ok=0; fi
for f in "$PREFIX/env.sh" "$PREFIX/palace/bin/palace" "$PREFIX/envs/emsim/bin/python3" \
         "$PREFIX/envs/emsim/bin/mpirun"; do
  [ -x "$f" ] || [ -f "$f" ] && echo "  ✅ $f" || { echo "  🔴 MISSING $f"; ok=0; }
done
[ -d "$PREFIX/repo" ] && echo "  ✅ $PREFIX/repo" || echo "  ⚠️  $PREFIX/repo absent — rsync.sh will create it"
# 🔴 WAS a count of postpro/h2b_* against "5 expected". That prefix is from the
# pre-slug era and no longer exists, so it printed "0 (5 expected)" on EVERY
# mount — a check whose expectation is permanently wrong. A verify block that
# always shows a discrepancy is one nobody reads, which is worse than no check.
# ✅ Now it asks the only question that matters after a reclamation: does this
# volume actually carry the work, or have we mounted an empty/wrong one?
n=$(ls -d "$PREFIX"/repo/experiments/resonance/postpro/*/ 2>/dev/null | wc -l)
if [ "$n" -eq 0 ]; then
  echo "  🔴 postpro is EMPTY — this is not the working volume, or the repo"
  echo "     copy is missing. STOP and check before running anything."
else
  echo "  ✅ postpro holds $n solved cases (newest: $(ls -t "$PREFIX"/repo/experiments/resonance/postpro 2>/dev/null | head -1))"
fi
df -h "$PREFIX" | tail -1 | awk '{print "  space: "$4" free ("$5" used)"}'
# 🔴 pyflakes must live in the ENV ON THIS VOLUME. Installed to the root
# filesystem it is lost by every reclamation AND it sits in an interpreter no
# rig ever runs (rigs source env.sh -> envs/emsim/bin/python3). preflight then
# DEGRADES SILENTLY (warns, exits 0) and the instance-side gate — the last one
# before solver time is spent — becomes weaker than the local one without
# saying so at a moment anyone is reading. Report it here, where a fresh
# instance is being certified.
if "$PREFIX/envs/emsim/bin/python3" -c 'import pyflakes' 2>/dev/null; then
  echo "  ✅ pyflakes (preflight checks undefined names)"
else
  echo "  🔴 pyflakes MISSING — preflight will NOT check undefined names."
  echo "     /opt/amip/envs/emsim/bin/pip install --no-deps pyflakes"
  echo "     (the ENV on this volume — NOT apt, which installs to the root fs"
  echo "      that reclamation wipes, and to an interpreter no rig runs)"
fi
echo "-- rigs running: --"
r=$(ps -C python3 -o args= 2>/dev/null | grep -c "^python3 -u [a-z]") || true
p=$(ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -v Z | wc -l) || true
echo "  rig python3: ${r:-0}   palace ranks: ${p:-0}"
[ "$ok" = 1 ] || { echo "🔴 volume is NOT usable"; exit 1; }
echo "✅ volume ready"
REMOTE
