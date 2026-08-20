#!/usr/bin/env bash
# Build Palace (AWS Labs) from source against the userspace conda-forge toolchain.
# No sudo required. Palace's CMake superbuild fetches and builds its own
# dependencies (MFEM, libCEED, HYPRE, METIS/ParMETIS, SuperLU_DIST, SLEPc...).
set -euo pipefail

export MAMBA_ROOT_PREFIX="$HOME/.local/share/mamba"
ENV_PREFIX="$MAMBA_ROOT_PREFIX/envs/emsim"
SRC="$HOME/.local/src/palace"
PREFIX="$HOME/.local/opt/palace"

# Use the conda-forge toolchain exclusively — mixing with system gcc breaks ABI.
export PATH="$ENV_PREFIX/bin:$PATH"
export CC="$ENV_PREFIX/bin/mpicc"
export CXX="$ENV_PREFIX/bin/mpicxx"
export FC="$ENV_PREFIX/bin/mpifort"
export CMAKE_PREFIX_PATH="$ENV_PREFIX"

mkdir -p "$(dirname "$SRC")"
if [ ! -d "$SRC/.git" ]; then
  git clone --depth 1 https://github.com/awslabs/palace.git "$SRC"
else
  git -C "$SRC" pull --ff-only || true
fi

rm -rf "$SRC/build"
mkdir -p "$SRC/build"
cd "$SRC/build"

# NOTE: do NOT use -G Ninja. Palace builds libCEED as an ExternalProject with a
# plain Makefile; with the Ninja generator CMake substitutes `ninja` as the make
# program and libCEED fails with "loading 'build.ninja': No such file".
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$PREFIX" \
  -DPALACE_WITH_OPENMP=ON \
  -DPALACE_WITH_SUPERLU=ON \
  -DPALACE_WITH_STRUMPACK=OFF \
  -DPALACE_WITH_MUMPS=OFF \
  -DPALACE_WITH_SLEPC=ON \
  -DPALACE_WITH_ARPACK=OFF \
  -DPALACE_WITH_LIBXSMM=OFF \
  -DPALACE_WITH_GSLIB=OFF

cmake --build . --parallel "$(nproc)"

echo
echo "=== BUILD COMPLETE ==="
"$PREFIX/bin/palace" --help 2>&1 | head -20 || ls -la "$PREFIX/bin"
