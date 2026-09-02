#!/usr/bin/env bash
# LOADED Q0, azimuthal loop SHORTED (closed ring), plasma ACTUALLY PRESENT.
# 🔴 eigen_cfg builds materials from the MESH SIDECAR, which does NOT carry the
#    plasma's Drude permittivity — the RIG computes that from n_e. A hand-rolled
#    eigen_cfg therefore gives the plasma region eps = 1.0 and silently solves a
#    COLD cavity. Measured 2026-08-31: cold and "loaded" returned IDENTICAL
#    eigenvalues to 6 figures. This is R101's failure mode.
# ✅ Drude values taken from the driven rig's own result.json for this ne.
cd /opt/amip/repo/experiments/resonance && source /opt/amip/env.sh
python3 - <<'PY'
import json, sys, e0_solver_vs_math as E, e0k2_anchor as A
M   = "h3-azimload-01.b593113a_n18p90_r2-8p5_ld11"
EPS, SIG, NE = -1.4560587808051757, 2.174640572452561, 7.9e18
m = json.load(open(M + ".meta.json"))
plasma = m["attributes"]["plasma"]
c = E.eigen_cfg("ring_loaded", m, mesh=M + ".msh", sigma=A.wall_sigma(),
                n=8, target=2.38, order=2, port_bc="pec", tol=1e-7)
c["Solver"]["Order"] = 2
c["Problem"]["Output"] = "/tmp/ring_loaded"
# put the plasma in
placed = False
for mat in c["Domains"]["Materials"]:
    if plasma in mat.get("Attributes", []):
        mat["Attributes"] = [a for a in mat["Attributes"] if a != plasma]
        placed = True
c["Domains"]["Materials"] = [mm for mm in c["Domains"]["Materials"] if mm["Attributes"]]
c["Domains"]["Materials"].append({"Attributes": [plasma],
                                  "Permittivity": EPS, "Conductivity": SIG})
# 🔑 FAIL CLOSED. Refuse to solve a "loaded" case whose plasma is vacuum.
got = [mm for mm in c["Domains"]["Materials"] if plasma in mm["Attributes"]]
assert len(got) == 1, "plasma attribute %s not uniquely assigned" % plasma
e, s = got[0]["Permittivity"], got[0].get("Conductivity")
if NE > 0 and (abs(e - 1.0) < 1e-9 or not s):
    sys.exit("🔴 REFUSING: ne=%.3g but plasma attr %d has eps=%s sigma=%s — "
             "that is VACUUM. eigen_cfg does not carry Drude values; the rig "
             "computes them. This is exactly R101." % (NE, plasma, e, s))
json.dump(c, open("/tmp/ring_loaded.json", "w"))
print("  plasma attr %d: eps=%.6f sigma=%.6f  (placed=%s)" % (plasma, e, s, placed))
PY
[ -f /tmp/ring_loaded.json ] || { echo "RINGQ2-REFUSED"; exit 1; }
timeout 3000 palace -np 32 /tmp/ring_loaded.json > /tmp/ring_loaded.sol 2>&1
echo "LOADED rc=$?"
awk -F, 'NR>1 && $2+0>2.2 && $2+0<2.8 {printf "   f=%.6f  Q=%.0f\n", $2, $4}' \
    /tmp/ring_loaded/eig.csv 2>/dev/null
echo "RINGQ2-DONE"
