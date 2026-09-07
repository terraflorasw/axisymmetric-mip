#!/usr/bin/env bash
# 🔴 EXPUNGED 2026-09-05. Use: ops/watch.sh <slug>
#
# This blocked until a rig finished and then printed a tail. Measured against
# the three things a watch must do, it failed two:
#
#   (a) poll for PROGRESS ......... 🔴 NO — it blocked, then printed at the end.
#                                   A job stepping through cases looked exactly
#                                   like a job doing nothing.
#   (b) notify on SOLVE exit ...... ✅ yes (grep '^EXIT=')
#   (c) notify on INSTANCE exit ... 🔴 NO — ssh failure was not distinguished
#                                   from a slow poll.
#
# Its own header records the cost: an earlier version "declared a healthy
# e1b_loaded dead while geometry.py was 3 minutes into meshing".
#
# 🔑 ops/watch.sh + ops/watchrig.sh answer all three, are covered by
# ops/watchrig_test.sh (16 tests), mirror everything to <slug>.watch.log so a
# buffering caller cannot destroy the stream, warn when the filter matches
# nothing ("this watch may be blind"), and run the end-of-run policy — fetch,
# then say the instance is idle and billing.
#
# ⚠️ REFUSING, not silently forwarding: a caller that wanted a BLOCKING wait
# would get a STREAMING watch and might not notice. Change the call site.
echo "🔴 ops/wait.sh is EXPUNGED — it did not emit progress and did not detect" >&2
echo "   host death. Use:  ops/watch.sh ${1:-<slug>}" >&2
echo "   (read the header of this file for the measured reasons)" >&2
exit 2
