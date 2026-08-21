#!/usr/bin/env bash
# Is this gmsh actually able to mesh in parallel? Read-only, cheap.
# General.NumThreads is INERT unless gmsh was built with OpenMP, and even then
# only some 3D algorithms are threaded. Ask the binary, do not assume.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
H="$AMIP_HOST"
timeout 60 ssh -i "$K" -o ConnectTimeout=15 $H '
  source /opt/amip/env.sh
  echo "== build options =="
  python3 -c "
import gmsh
gmsh.initialize()
print(\"  version:\", gmsh.option.getString(\"General.Version\"))
try:
    print(\"  build opts:\", gmsh.option.getString(\"General.BuildOptions\"))
except Exception as e:
    print(\"  build opts unavailable:\", e)
print(\"  NumThreads default:\", gmsh.option.getNumber(\"General.NumThreads\"))
for k in (\"Mesh.MaxNumThreads1D\",\"Mesh.MaxNumThreads2D\",\"Mesh.MaxNumThreads3D\"):
    try: print(f\"  {k}:\", gmsh.option.getNumber(k))
    except Exception as e: print(f\"  {k}: n/a\")
print(\"  Mesh.Algorithm (2D):\", gmsh.option.getNumber(\"Mesh.Algorithm\"))
print(\"  Mesh.Algorithm3D:\", gmsh.option.getNumber(\"Mesh.Algorithm3D\"))
gmsh.finalize()
"
' 2>&1 | tail -15
