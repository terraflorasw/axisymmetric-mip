#!/usr/bin/env bash
# Phase 1 eigenmode run. Usage: ./run-eigenmode.sh [nprocs]
set -euo pipefail
export MAMBA_ROOT_PREFIX="$HOME/.local/share/mamba"
ENV="$MAMBA_ROOT_PREFIX/envs/emsim"
PALACE="$HOME/.local/opt/palace/bin/palace"
NP="${1:-$(lscpu -p=Core,Socket 2>/dev/null | grep -v "^#" | sort -u | wc -l)}"

[ -x "$PALACE" ] || { echo "Palace not built yet — see build-palace.sh"; exit 1; }
[ -f ring.msh ]  || "$HOME/.local/bin/micromamba" run -n emsim python geometry.py --out ring.msh

export PATH="$ENV/bin:$PATH"
mkdir -p postpro
"$PALACE" -np "$NP" eigenmode.json 2>&1 | tee eigenmode.log
"$HOME/.local/bin/micromamba" run -n emsim python analyse.py
