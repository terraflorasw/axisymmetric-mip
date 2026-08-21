# DEPLOY — running this programme on a rented machine

**Nothing large is uploaded.** The instance has far better download bandwidth
than a laptop's wifi has upload, so Palace is REBUILT there rather than shipped.
Only this experiment directory crosses the link, and it is a few hundred KB.

## What moves, and what is fetched

| | size | how |
|---|---|---|
| this directory | ~300 KB | **upload** — the only thing that crosses wifi |
| conda env `emsim` | 352 packages | **fetch** from conda-forge using `emsim.lock.txt` (pinned, `--explicit`) |
| Palace | 335 MB built | **rebuild** on the instance from the pinned commit below |

## Volume layout — toolchain ON the data volume, nothing in the OS

🔑 **This is what the dev container already does**: nothing is installed in the
OS except python3, gcc/g++ and git. The conda env and Palace both live under a
single directory. Keep that on EC2 and **no AMI is ever needed** — a spot reclaim
means launching a stock instance, attaching the volume, and resuming.

| | |
|---|---|
| root volume | **stock AMI, untouched.** Ephemeral, replaceable, never customised |
| **data volume** | conda env + Palace + repo + meshes + results |

🔴 **THE CONSTRAINT: the mount path must be IDENTICAL on every instance.** The
toolchain is relocatable but NOT path-independent —

```
Palace RPATH   .../opt/palace/lib   .../envs/emsim/lib     ← absolute
conda bin/     52 scripts with the env prefix baked in
```

⚠️ So do **not** install under a home directory, whose path depends on the user
AWS happens to create. Pick a neutral prefix and mount there every time:

⚠️ **An EBS volume is ATTACHED AFTER LAUNCH, not in the launch wizard** — that
section only creates NEW volumes. Launch first, then EC2 → Volumes → Attach.
🔴 **The volume and the instance must be in the SAME AVAILABILITY ZONE**, so pin
the spot request's subnet to the volume's AZ or the attach will not be offered.

```bash
lsblk                      # the device you asked for is NOT the name it gets:
                           # /dev/sdf appears as /dev/nvme1n1 on Nitro

# 🔴 mkfs ONLY THE FIRST TIME. On every later boot this would destroy the
# toolchain and every result on the volume. Guard it, do not remember it:
sudo blkid /dev/nvme1n1 || sudo mkfs.ext4 /dev/nvme1n1

sudo mkdir -p /opt/amip
sudo mount /dev/nvme1n1 /opt/amip          # SAME path on every instance
echo '/dev/nvme1n1 /opt/amip ext4 defaults,nofail 0 2' | sudo tee -a /etc/fstab
```

Then build with prefixes ON that volume, so the RPATHs bake in a stable path:

```bash
micromamba create -p /opt/amip/envs/emsim --file emsim.lock.txt
micromamba install -p /opt/amip/envs/emsim cmake      # even the build tool
cmake -DCMAKE_INSTALL_PREFIX=/opt/amip/palace ...
```

✅ **The OS then needs almost nothing** — conda-forge supplies cmake and can
supply the compilers too, so a stock Amazon Linux or Ubuntu image is enough.

⚠️ **Size it for toolchain PLUS data**, since both now live here: ~5 GB
toolchain (after `micromamba clean -a` and deleting the Palace build tree),
~30 GB working headroom → **50 GB gp3**, about $4/month. gp3 gives full
3000 IOPS / 125 MB/s at any size; volumes grow but never shrink.

## The snapshot — built ONCE, then every launch is free

🔑 Volumes are AZ-scoped; **snapshots are REGION-scoped**. So the AZ pinning that
an attached volume forces on a spot request applies only to the initial build.
After that a launch creates its volume FROM THE SNAPSHOT, in whatever AZ spot
gives you, attached automatically.

### One time only

```bash
# 1. launch, attach the volume, mount it — AZ must match, this once
sudo blkid /dev/nvme1n1 || sudo mkfs.ext4 /dev/nvme1n1
sudo mkdir -p /opt/amip && sudo mount /dev/nvme1n1 /opt/amip
sudo chown "$USER" /opt/amip

# 2. build the toolchain INTO the volume (see the next section)

# 3. 🔴 VERIFY BEFORE SNAPSHOTTING. A snapshot of a broken toolchain
#    propagates to every future launch, and it will look like a fresh problem
#    each time.
python3 physics.py            # must print ALL PASS
python3 preflight.py *.py     # must exit 0
python3 e0_solver_vs_math.py  # max|Δ| ≈ 0.36 MHz at solver order 2

# 4. quiesce the filesystem, or the snapshot may be inconsistent
sync && sudo umount /opt/amip
```

Then **EC2 → Volumes → select → Actions → Create snapshot**, or:

```bash
aws ec2 create-snapshot --volume-id vol-XXXX \
  --description "amip toolchain: emsim + palace 3c83b9d"
```

⚠️ **Unmount first.** A snapshot taken while the filesystem is mounted and being
written can capture a torn state — the same class of problem as the JSON summary
that `journal.py` replaced, at filesystem scale.

### Every launch after

In the launch wizard, **Add new volume → from Snapshot → select it**. It is
created and attached at launch, already formatted, in the instance's own AZ.

```bash
sudo mkdir -p /opt/amip
sudo mount /dev/nvme1n1 /opt/amip          # SAME path — RPATH depends on it
echo '/dev/nvme1n1 /opt/amip ext4 defaults,nofail 0 2' | sudo tee -a /etc/fstab
git clone git@github.com:terraflorasw/axisymmetric-mip.git
```

✅ **No rebuild, no AZ pinning, no attach step, no mkfs.** Re-snapshot only when
the toolchain changes — which is rare, since both the Palace commit and
`emsim.lock.txt` are pinned.

| | |
|---|---:|
| snapshot storage, ~5 GB | ~$0.25/month |
| later snapshots | incremental — only changed blocks |

## Getting the code there — NO credentials on the instance

🔴 **Do not put a GitHub key on a spot instance.** It is a machine you do not
control, it is destroyed and recreated constantly, and a personal SSH key grants
your whole account. A deploy key or fine-grained PAT is better but is still a
credential living on disposable hardware.

✅ **Push the code instead.** The tracked tree is ~14 MB — smaller than one mesh
— so it costs seconds even over wifi, and every credential stays on the laptop.

🔴 **rsync does NOT respect .gitignore.** `--filter=':- .gitignore'` approximates
it, but rsync's pattern semantics differ from git's on negations and `**`, so it
is an approximation you have to trust. Worse, writing an `--exclude` list by hand
creates a SECOND list that must agree with `.gitignore` forever — the same
maintained-by-hand failure as a stale name or a hand-written whitelist.

✅ **Let git produce the manifest.** `git archive` emits exactly the tracked tree
and needs no rsync at all (⚠️ rsync is absent from some minimal images):

```bash
# 🔴 NEVER a literal address here. Spot instances are reclaimed — twice on
# 2026-08-21 alone — and this line was still naming a host two reclamations
# dead. ops/env.sh is the ONE place the address lives.
. experiments/resonance/ops/env.sh    # exports AMIP_HOST
H="$AMIP_HOST"

# UP — exactly what git tracks, nothing else. One source of truth.
git archive HEAD | ssh -i ./aws.pem $H \
  'mkdir -p /opt/amip/repo && tar -x -C /opt/amip/repo'

# UP, for work not yet committed (resonance/ during the transition)
tar cz --exclude='*.msh' --exclude='postpro' --exclude='__pycache__' \
       --exclude='*.bak*' --exclude='*_p.log' -C amip/experiments resonance \
  | ssh -i ./aws.pem $H 'mkdir -p /opt/amip && tar xz -C /opt/amip'

# DOWN — only what the run produced. An ALLOWLIST: with unknown filenames a
# whitelist fails safe and a blacklist fails silently.
ssh -i ./aws.pem $H 'cd /opt/amip/resonance && tar cz \
  $(ls *.result.json *.criteria.json *.jsonl *.log 2>/dev/null) postpro' \
  | tar xz -C amip/experiments/resonance
```

🔑 **Then commit on the laptop**, where the key already is. git never runs on the
instance at all, and the instance never holds anything that could authenticate as
you.

⚠️ `--delete` on the UP sync only: the laptop is the source of truth for code.
It is deliberately absent from the DOWN sync, which must never remove local
results.

## Palace — the exact build

```
repo    https://github.com/awslabs/palace
commit  3c83b9db0014f87dea003873064f843fa802ac32   ← matches the "Git changeset ID"
                                                     printed in every solve log here
```

| option | |
|---|---|
| `CMAKE_BUILD_TYPE` | `Release` |
| `PALACE_WITH_OPENMP` | **ON** |
| `PALACE_WITH_SLEPC` | **ON** |
| `PALACE_WITH_SUNDIALS` | **ON** |
| `PALACE_WITH_SUPERLU` | **ON** |
| ARPACK · MUMPS · STRUMPACK · GSLIB · LIBXSMM | OFF |
| **CUDA · HIP · MAGMA · CUDSS** | **OFF** — CPU build, deliberately |

```bash
# 1. environment (fetched, not uploaded)
micromamba create -n emsim --file emsim.lock.txt

# 2. Palace, from the pinned commit — builds its own externs (MFEM, hypre,
#    libCEED, SLEPc, SuperLU). On 16 cores this is minutes, not the hour it
#    would take to upload the binary.
git clone https://github.com/awslabs/palace && cd palace
git checkout 3c83b9db0014f87dea003873064f843fa802ac32
cmake -B build -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=$HOME/.local/opt/palace \
      -DPALACE_WITH_OPENMP=ON -DPALACE_WITH_SLEPC=ON \
      -DPALACE_WITH_SUNDIALS=ON -DPALACE_WITH_SUPERLU=ON
cmake --build build -j"$(nproc)" --target install
```

⚠️ A rebuild will not be bit-identical to this laptop's binary, and that is
fine — **the acceptance test compares against mathematics, not against here.**

## Acceptance test — run BEFORE trusting any result

```bash
python3 physics.py            # closed-form self-test — must print ALL PASS
python3 preflight.py *.py     # harness lint — must exit 0
python3 e0_solver_vs_math.py  # solver vs the exact spectrum
```

🔑 **E0 is the acceptance test.** It checks the new machine against
`physics.spectrum()`, so a different box with differently-built libraries has to
reproduce **mathematics**. Expected there, from this laptop:

| | |
|---|---|
| solver order 1 | max\|Δ\| ≈ 16.6 MHz, degenerate splitting ≈ 1.2 MHz |
| **solver order 2** | **max\|Δ\| ≈ 0.36 MHz, splitting ≈ 0.014 MHz** |

✅ E0e showed the pipeline is bit-exact for a fixed mesh, so a *material*
difference in these numbers is a signal about the build, not noise.

## Sizing — what actually binds

| | |
|---|---|
| RAM | **not a constraint.** Peak ~3 GB |
| VRAM | **irrelevant to a CPU build.** A CUDA build is a separate project with an unmeasured payoff at our ~1–2M DOF size |
| **physical cores** | **the constraint.** 4 here (8 logical). PRRTE allocates by physical core, so `-np 4` is already full |
| memory bandwidth | 🔴 **UNMEASURED** |

**The workload is fan-out.** Aspect ratios, length ladders, material states and
ensemble members are independent solves wanting ~4 ranks each, so throughput is
physical cores ÷ 4.

| box | physical cores | concurrent solves |
|---|---:|---:|
| this laptop | 4 | **1** |
| c6a.8xlarge | 16 | **4** |
| c7a.8xlarge (no SMT) | 32 | **8** |

🔴 **Run `-np 1 / 2 / 4` on an idle machine before committing.** Near-linear to 4
means cores bind and core count buys throughput. Flattening by 2–3 means memory
bandwidth binds and a many-core single socket will not deliver its core count.
**I have asserted this workload is bandwidth-bound and never measured it.**
