# One-off diagnostics — NOT rigs

🔴 These are hand-run scripts kept for REPRODUCIBILITY, not measurement rigs.
Everything here bypasses the slug/config/provenance machinery, and hand-rolled
solves cost this programme four separate errors on 2026-08-31 alone:
`mpirun -n 32 palace` (32 duplicate 1-rank solves), `target=2.45e9` when the
units are GHz, a kill pattern that matched its own shell, and — the dangerous
one — `eigen_cfg` giving the plasma eps = 1.0 so a "loaded" solve was silently
a COLD solve (R101's failure mode).

**If a result matters, put it in a rig.** Use these only to reproduce what is
already recorded in NEXT.md.

- `ring_loaded_q0.sh` — azimuthal loop SHORTED (`port_bc="pec"`, a closed ring:
  no port, no coupling, no feed topology). Reuses the `h3-azimload-01` meshes on
  the EBS volume. Produced the COLD anchor Q0 = 43,875 @ 2.450751 GHz, and
  showed eigen STALLS on plasma (PCG stagnation, nconv=0) even with a vacuum
  torch. Carries a fail-closed guard against the eps=1.0 trap.
- `parse_loopq_log.py` — pairs each h3_loopq case with ITS OWN result. A paste
  of two greps misaligns the moment one case yields no result, and silently
  shifted every row after a continuation break.
- `mesh_attr_extents.py` — r/z extents of a mesh attribute. Used to prove the
  port face sits INSIDE the cavity and that the pre-fix face overshot the
  conductor by 0.4 mm into vacuum.
