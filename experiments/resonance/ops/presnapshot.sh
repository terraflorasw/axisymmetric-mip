#!/usr/bin/env bash
# Prepare the volume for snapshotting: clean, RE-VERIFY, then hand over.
#
# 🔴 The verification must run AFTER the cleaning, not before. Deleting the
# 2.6 GB build tree is the last thing that could break the install, and a
# snapshot of a broken toolchain propagates to every future launch — where it
# will present as a fresh mystery rather than as something baked in.
set -euo pipefail
# repo parent (holds aws.pem), derived from THIS script's location
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
H="$AMIP_HOST"
echo "== refuse if anything is running =="
BUSY=$(timeout 30 ssh -i "$K" $H \
  'ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -v Z | wc -l')
[ "$BUSY" -eq 0 ] || { echo "🔴 $BUSY rank(s) running — wait"; exit 1; }

timeout 900 ssh -i "$K" $H 'bash -s' <<'REMOTE'
set -euo pipefail
echo "== before =="
du -sh /opt/amip 2>/dev/null | sed 's/^/  /'
du -sh /opt/amip/src /opt/amip/mamba 2>/dev/null | sed 's/^/  /'

echo "== clean: build tree and package cache =="
# ${VAR:?} so an unset variable cannot turn this into `rm -rf /`
rm -rf "${HOME:?}/../../opt/amip/src/palace/build" 2>/dev/null || \
  sudo rm -rf /opt/amip/src/palace/build
/opt/amip/bin/micromamba clean -a -y >/dev/null 2>&1 || true
echo "  done"

echo "== after =="
du -sh /opt/amip | sed 's/^/  /'

echo "== RE-VERIFY the cleaned toolchain =="
source /opt/amip/env.sh
cd /opt/amip/repo/experiments/resonance
python3 physics.py 2>&1 | tail -2 | sed 's/^/  /'
python3 -c "import gmsh; print('  gmsh', gmsh.GMSH_API_VERSION)"
"$PALACE_BIN" --help >/dev/null 2>&1 && echo "  ✅ palace runs" || \
  { echo "  🔴 PALACE BROKEN AFTER CLEAN — do NOT snapshot"; exit 1; }
echo "  ✅ toolchain intact after cleaning"
REMOTE

cat <<'TXT'

== NEXT, on the instance ==
  sync && sudo umount /opt/amip     # a mounted, written filesystem can
                                    # snapshot torn — same class of problem as
                                    # a half-written JSON summary
== THEN ==
  EC2 → Volumes → select → Actions → Create snapshot
  aws ec2 create-snapshot --volume-id vol-XXXX \
    --description "amip toolchain: emsim + palace 3c83b9d, E0 verified"
TXT
