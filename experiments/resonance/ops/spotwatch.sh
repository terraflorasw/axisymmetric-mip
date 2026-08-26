#!/usr/bin/env bash
# Record spot interruption notices ON THE PERSISTENT VOLUME, so that after an
# instance dies we can tell a RECLAMATION from any other termination.
#
# 🔴 WRITTEN 2026-08-26. ops/watchrig.sh says "likely RECLAIMED" whenever the
# host stops answering — but unreachable is unreachable, and it cannot
# distinguish a spot reclamation from a crash, an OOM kill, or a manual stop.
# The user noticed the difference first: "this time doesn't look like an
# interruption, because I got no notification."
#
# AWS publishes the notice at IMDS `/latest/meta-data/spot/instance-action`
# about two minutes before termination. That is on the INSTANCE, which is
# exactly what disappears — so the notice is written to /opt/amip, which
# survives.
#
#   nohup ops/spotwatch.sh >/dev/null 2>&1 &
set -uo pipefail
LOG="${SPOTWATCH_LOG:-/opt/amip/spot-interruptions.log}"
IMDS=http://169.254.169.254/latest

# 🔑 LOG WHEN WATCHING STARTED (user, 2026-08-26). Without a start line the log
# records only DEATHS, so the only interval derivable from it is death-to-death
# — which includes the hand-off gap where no instance exists and therefore
# OVERSTATES how long instances actually survive. I made exactly that error:
# computed death-to-death, called it lifetime, and inferred a pattern from it.
# ⚠️ The start of WATCHING is not the start of the INSTANCE either, so record
# the kernel uptime too — then true lifetime is available regardless of when
# this was launched.
_stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
_uptime_s() { awk '{printf "%d", $1}' /proc/uptime 2>/dev/null || echo "?"; }
_TOK0=$(curl -s -X PUT "$IMDS/api/token" \
        -H "X-aws-ec2-metadata-token-ttl-seconds: 300" --max-time 3 2>/dev/null)
_ID0=$(curl -s --max-time 3 -H "X-aws-ec2-metadata-token: ${_TOK0:-}" \
       "$IMDS/meta-data/instance-id" 2>/dev/null)
echo "$(_stamp) WATCH_START instance=${_ID0:-unknown} uptime_s=$(_uptime_s)" >> "$LOG"
sync
while true; do
  TOK=$(curl -s -X PUT "$IMDS/api/token" \
        -H "X-aws-ec2-metadata-token-ttl-seconds: 300" --max-time 3 2>/dev/null)
  if [ -n "$TOK" ]; then
    CODE=$(curl -s -o /tmp/.spotnotice -w '%{http_code}' --max-time 3 \
           -H "X-aws-ec2-metadata-token: $TOK" \
           "$IMDS/meta-data/spot/instance-action" 2>/dev/null)
    if [ "$CODE" = "200" ]; then
      ID=$(curl -s --max-time 3 -H "X-aws-ec2-metadata-token: $TOK" \
           "$IMDS/meta-data/instance-id" 2>/dev/null)
      echo "$(_stamp) SPOT_INTERRUPTION instance=$ID uptime_s=$(_uptime_s) $(cat /tmp/.spotnotice)" >> "$LOG"
      sync
      exit 0          # the notice fires once; nothing left to watch
    fi
  fi
  sleep 5
done
