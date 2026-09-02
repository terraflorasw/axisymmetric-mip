#!/usr/bin/env bash
# Build the coax-fed azimuthal loop and run ONE driven sweep through its wave
# port. The only untested link is whether Palace accepts a WavePort on the
# annulus; everything upstream is verified (mouth found by area to 4 s.f.).
#   hole r = 2.3 mm -> Z0 = 49.9 ohm against a 1 mm inner conductor in air
#   gap  = 0        -> continuous arc; the drive is at the coax, not mid-arc
cd /opt/amip/repo/experiments/resonance && source /opt/amip/env.sh
B="--radius 88.004517 --length 115.41576 --order 2 --sectors 5 --mode-filter 0 --groove 5,10 --viewport 0 --trap 0,0,0 --chimney 21,41 --feed 21,41 --torch-ext 41 --torch-ext-top 41 --loop-phi 36"
AMIP_ARC_CHORDS=7 timeout 1500 python3 -u geometry.py --out /tmp/C2.msh $B \
    --size-factor 1.5 --loop 0,0,1.0,0 --loop-azim-standoff 2,12.24 \
    --loop-hole 2.3,8 > /tmp/C2.log 2>&1
echo "MESH rc=$?"
grep -aoE "COAX (HOLE|PORT|MOUTH|MESH):[^I]{0,95}|ERROR[^I]{0,150}" /tmp/C2.log | head -5
python3 - <<'PY'
import json, solveconf
c, _m, d = solveconf.driven("/tmp/C2.msh", "coaxwp", (2.430, 2.450),
                            step=1e-4, order=2)
c["Problem"]["Output"] = "/tmp/coaxwp"; c["Model"]["Mesh"] = "/tmp/C2.msh"
json.dump(c, open("/tmp/coaxwp.json", "w"))
print("  WavePort:", json.dumps(c["Boundaries"].get("WavePort")))
PY
timeout 2400 palace -np 32 /tmp/coaxwp.json > /tmp/coaxwp.sol 2>&1
echo "PALACE rc=$?"
# 🔴 WHOLE message — the diagnosis lives in the clause after the assertion
grep -aA4 "Verification failed\|MFEM abort" /tmp/coaxwp.sol | head -8
head -3 /tmp/coaxwp/port-S.csv 2>/dev/null
echo "COAXWP-DONE"
