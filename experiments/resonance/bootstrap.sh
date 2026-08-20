#!/usr/bin/env bash
# bootstrap.sh — stand up the toolchain on a fresh EC2 instance.
#
# Run ONCE on a new volume, then snapshot. Every later launch creates its volume
# from that snapshot and skips straight to the acceptance test.
#
#   scp -i aws.pem bootstrap.sh emsim.lock.txt ubuntu@HOST:~/
#   ssh -i aws.pem ubuntu@HOST 'bash bootstrap.sh'
#
# Deliberately NOT idempotent-by-guessing: each step checks whether it is
# already done and skips, so re-running after an interruption is safe.
set -euo pipefail
PREFIX=/opt/amip
PALACE_COMMIT=3c83b9db0014f87dea003873064f843fa802ac32

say() { printf '\n\033[1m== %s\033[0m\n' "$*"; }

say "hardware — verify you got what you paid for"
lscpu | grep -E 'Model name|^CPU\(s\)|Thread\(s\) per core|NUMA node\(s\)' | sed 's/^/  /'
free -g | sed -n 2p | sed 's/^/  /'
echo "  glibc: $(ldd --version | head -1 | grep -oE '[0-9]+\.[0-9]+$')  (env built against 2.39)"
lsblk | sed 's/^/  /'

say "volume at $PREFIX"
DEV=$(lsblk -rno NAME,TYPE,MOUNTPOINT | awk '$2=="disk" && $3=="" {print "/dev/"$1}' | tail -1)
if mountpoint -q "$PREFIX"; then
  echo "  already mounted"
elif [ -n "${DEV:-}" ]; then
  # 🔴 format ONLY if unformatted — this guard is the difference between a
  # fresh volume and destroying a toolchain plus every result on it
  sudo blkid "$DEV" >/dev/null 2>&1 || { echo "  formatting $DEV"; sudo mkfs.ext4 -q "$DEV"; }
  sudo mkdir -p "$PREFIX" && sudo mount "$DEV" "$PREFIX" && sudo chown "$USER" "$PREFIX"
  grep -q "$PREFIX" /etc/fstab || \
    echo "$DEV $PREFIX ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab >/dev/null
  echo "  mounted $DEV"
else
  echo "  🔴 no unmounted disk found — attach the volume first"; exit 1
fi

say "os packages — conda supplies gcc, cmake and the rest; these are what a
     minimal Ubuntu 24.04 cloud image genuinely lacks"
# bzip2: micromamba ships as .tar.bz2 and `tar -xvj` needs it. NOT present on
# the stock cloud image — found the hard way on the first real launch, because
# this script was written from what a dev container happened to have.
sudo apt-get update -qq && sudo apt-get install -y -qq git bzip2 curl ca-certificates

say "micromamba + environment"
export MAMBA_ROOT_PREFIX="$PREFIX/mamba"
if [ ! -x "$PREFIX/bin/micromamba" ]; then
  mkdir -p "$PREFIX/bin"
  curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest \
    | tar -xvj -C "$PREFIX" bin/micromamba
fi
MM="$PREFIX/bin/micromamba"
[ -d "$PREFIX/envs/emsim" ] || "$MM" create -y -p "$PREFIX/envs/emsim" --file emsim.lock.txt
echo "  env: $("$PREFIX/envs/emsim/bin/python3" -V)"
"$PREFIX/envs/emsim/bin/python3" -c "import gmsh; print('  gmsh', gmsh.GMSH_API_VERSION)"

say "palace @ $PALACE_COMMIT"
export PATH="$PREFIX/envs/emsim/bin:$PATH"
if [ ! -x "$PREFIX/palace/bin/palace" ]; then
  # 🔴 NOT -q. A quiet clone of a repo with submodules is several silent
  # minutes, which is indistinguishable from a hang — and that is exactly what
  # it looked like on the first real run.
  if [ ! -d "$PREFIX/src/palace" ]; then
    echo "  cloning (several minutes, progress below)..."
    git clone --progress https://github.com/awslabs/palace "$PREFIX/src/palace"
  fi
  cd "$PREFIX/src/palace"
  echo "  checkout $PALACE_COMMIT"
  git checkout "$PALACE_COMMIT"
  cmake -B build -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX="$PREFIX/palace" \
        -DPALACE_WITH_OPENMP=ON -DPALACE_WITH_SLEPC=ON \
        -DPALACE_WITH_SUNDIALS=ON -DPALACE_WITH_SUPERLU=ON 2>&1 \
        | tee "$PREFIX/cmake-configure.log"
  # ⚠️ Was `>/dev/null`, which hid the error on failure. Then `| tail -5`,
  # which BUFFERS — nothing prints until configure ends, so a slow step looks
  # like a hang. Both are the same fault: output the operator cannot see.
  # A bootstrap should be verbose; it runs once.
  # 🔴 NO --target install. Palace is a CMake SUPERBUILD: the default target
  # builds the externs (mfem, hypre, libCEED, metis, SLEPc, SuperLU) and
  # installs into CMAKE_INSTALL_PREFIX as it goes. `make help` lists all,
  # clean, depend and the subprojects — no install target exists, so asking
  # for one fails with "No rule to make target".
  echo "  building with $(nproc) jobs — externs (mfem, hypre, libCEED, metis,"
  echo "  SLEPc, SuperLU, SUNDIALS) dominate this, not Palace itself"
  time cmake --build build -j"$(nproc)"
fi
[ -x "$PREFIX/palace/bin/palace" ] || { echo "  🔴 palace binary missing"; exit 1; }
echo "  palace: $("$PREFIX/palace/bin/palace" --help 2>&1 | head -1 | cut -c1-60)"

say "self-check — every piece the acceptance test will need"
ok=1
for f in "$PREFIX/envs/emsim/bin/python3" "$PREFIX/palace/bin/palace" \
         "$PREFIX/envs/emsim/bin/mpirun"; do
  [ -x "$f" ] && echo "  ✅ $f" || { echo "  🔴 MISSING $f"; ok=0; }
done
"$PREFIX/envs/emsim/bin/python3" -c "import gmsh" 2>/dev/null \
  && echo "  ✅ gmsh importable" || { echo "  🔴 gmsh not importable"; ok=0; }
[ "$ok" = 1 ] || exit 1

say "environment file"
cat > "$PREFIX/env.sh" <<ENVEOF
# source this before running anything. Written by bootstrap.sh.
# 🔴 Palace shells out to mpiexec, which is NOT on a bare login PATH — without
# this the solver returns in 0 s and a driver reports "no resonance", which
# looks exactly like a cavity that does not resonate.
export MAMBA_ROOT_PREFIX=$PREFIX/mamba
export CONDA_ENV=$PREFIX/envs/emsim
export PALACE_BIN=$PREFIX/palace/bin/palace
export PATH=\$CONDA_ENV/bin:$PREFIX/palace/bin:\$PATH
ENVEOF
echo "  wrote $PREFIX/env.sh"

say "NEXT — the acceptance test, BEFORE snapshotting"
cat <<'TXT'
  source /opt/amip/env.sh        # ← REQUIRED: sets python3, mpirun and PALACE_BIN

  git clone git@github.com:terraflorasw/axisymmetric-mip.git
  cd axisymmetric-mip/experiments/resonance
  python3 physics.py             # must print ALL PASS
  python3 preflight.py *.py      # must exit 0
  python3 e0_solver_vs_math.py   # order 2: max|Δ| ~0.36 MHz, splitting ~0.014

  🔴 Only then:  sync && sudo umount /opt/amip  → snapshot the volume.
     A snapshot of a broken toolchain propagates to every future launch.
TXT
