# Single source of truth for the instance address.
#
# 🔴 This was hardcoded in 29 places. A spot reclamation on 2026-08-21 killed the
# instance mid-run, and every one of those would have needed editing to point at
# the replacement. Spot instances are reclaimed; the address is not a constant.
#
# Override without editing:  AMIP_HOST=ubuntu@new-host ops/go ops/status.sh
# 🔴 EXPORTED. `ops/go` sources this and then exec's the target script as a
# separate process; without export the child sees nothing and dies on
# "AMIP_HOST: unbound variable" — which is what ops/remote.sh did. A single
# source of truth has to actually REACH the thing that consumes it.
export AMIP_HOST
AMIP_HOST="${AMIP_HOST:-ubuntu@ec2-18-222-232-209.us-east-2.compute.amazonaws.com}"
