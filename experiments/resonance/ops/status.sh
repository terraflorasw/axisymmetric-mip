#!/usr/bin/env bash
# What is running, here and on the instance. Read-only.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
set -uo pipefail
H="$AMIP_HOST"
# repo parent (holds aws.pem), derived from THIS script's location
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
echo "== local =="
n=$(ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -v Z | wc -l)
echo "  live palace: ${n:-0}"
ps -o pid=,etime=,args= -C palace-x86_64.bin 2>/dev/null | grep -v defunct \
  | awk '{print "   ",$1,$2,$NF}' || true
echo "== instance =="
timeout 30 ssh -i "$K" -o ConnectTimeout=10 $H \
  'n=$(ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -v Z | wc -l)
   echo "  live palace: $n"
   ps -o pid=,etime=,args= -C palace-x86_64.bin 2>/dev/null | grep -v defunct \
     | awk "{print \"   \",\$1,\$2,\$NF}"
   uptime | sed "s/^/  /"
   # the data volume: mounted, read-WRITE, and with room. A remount that
   # silently came back ro fails at write time, an hour into a solve.
   if ! mountpoint -q /opt/amip; then
     echo "  ❌ /opt/amip NOT MOUNTED"
   else
     opts=$(awk "\$2==\"/opt/amip\"{print \$4}" /proc/mounts | head -1)
     case ",$opts," in
       *,rw,*) ;;
       *) echo "  ❌ /opt/amip mounted READ-ONLY ($opts)" ;;
     esac
     # /proc/mounts can still say rw when the fs is wedged; prove it
     t=/opt/amip/.writetest.$$
     if touch "$t" 2>/dev/null; then rm -f "$t"; w=ok; else w=FAILED; fi
     free=$(df -h --output=avail /opt/amip | tail -1 | tr -d " ")
     used=$(df -h --output=pcent /opt/amip | tail -1 | tr -d " ")
     if [ "$w" = ok ]; then
       echo "  /opt/amip rw, write ok, $free free ($used used)"
     else
       echo "  ❌ /opt/amip write test FAILED ($free free)"
     fi
   fi' 2>&1 | tail -14
