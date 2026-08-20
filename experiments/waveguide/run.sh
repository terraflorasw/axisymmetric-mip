#!/usr/bin/env bash
# TE011 cavity eigenmode run. Usage: ./run.sh [nprocs]
set -euo pipefail
export MAMBA_ROOT_PREFIX="$HOME/.local/share/mamba"
ENV="$MAMBA_ROOT_PREFIX/envs/emsim"
PALACE="$HOME/.local/opt/palace/bin/palace"
MM="$HOME/.local/bin/micromamba"
NP="${1:-$(lscpu -p=Core,Socket 2>/dev/null | grep -v "^#" | sort -u | wc -l)}"

[ -x "$PALACE" ] || { echo "Palace not built — see ../ignition/build-palace.sh"; exit 1; }
[ -f cav.msh ] || "$MM" run -n emsim python geometry.py --out cav.msh

export PATH="$ENV/bin:$PATH"
mkdir -p postpro
"$PALACE" -np "$NP" eigenmode.json 2>&1 | tee cav.log
"$MM" run -n emsim python analyse.py
