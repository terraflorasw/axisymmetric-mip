#!/usr/bin/env bash
# Geometric order of the meshes a run is actually building. Read-only.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
timeout 60 ssh -i "$K" $H \
  'cd /opt/amip/repo/experiments/resonance || exit 9
   source /opt/amip/env.sh
   python3 - <<PYEOF
import json, glob, os
rows=[]
for f in sorted(glob.glob("*.meta.json")):
    try: d=json.load(open(f))
    except Exception: continue
    rows.append((os.path.getmtime(f), f, d.get("mesh_order"),
                 d.get("geometry_mm",{}).get("radius")))
rows.sort()
print(f"  {\"mesh\":<22}{\"geom order\":>11}{\"radius\":>9}")
for _t,f,o,r in rows[-10:]:
    print(f"  {f:<22}{str(o):>11}{str(r):>9}")
PYEOF'
