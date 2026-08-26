# cad — drawings of what the solver actually meshes

**Opened 2026-08-25.** OpenSCAD, so the geometry is source-controlled, diffable
and viewable without running anything.

    python3 cad/scadgen.py          # regenerate amip_params.scad
    openscad cad/view_barrel.scad   # then any view

| file | |
|---|---|
| `scadgen.py` | reads `baselines.json` → emits `amip_params.scad` |
| `amip_params.scad` | 🔴 **GENERATED — do not edit** |
| `amip.scad` | module library, authored |
| `view_barrel.scad` | barrel mount — links **H_z**. Measured Q_ext **8,716** |
| `view_cap.scad` | cap mount — links **H_r**. Measured Q_ext **9,231** |
| `view_capacitor.scad` | the series gap + flanges (item 7 step 2) |
| `view_assembly.scad` | both mounts, one scale, with axes |

## The drawing cannot drift from the design

Every dimension comes through `values.get()` or `physics.design_point()` — the
same path the mesher uses. Change `baselines.json` and the drawing changes on
the next `scadgen.py`; a stale drawing shows up as a **diff**, not a surprise.
Verified by perturbing the groove to 6×12, regenerating, and restoring.

⚠️ **`loop_rw` and `loop_gap` are TENTATIVE** — the loop was forced into
existence so driven solves would have a port, and those two were never chosen
(`../NEXT.md` item 7). The generated file says so in a comment.

## What the geometry means

TE011's magnetic field splits by boundary condition, and that is the whole story
of the two mounts:

- **barrel wall** — H_r must vanish (it is normal to the conductor; `J1(x'01)=0`
  says so exactly), so **only H_z** exists. A loop in the z=0 mid-plane links it.
  The radius is **forced** to `a`.
- **end cap** — H_z must vanish, so **only H_r** exists, peaking at `0.4805a`.
  A loop in a radial plane links it, and its **radius is free** — which was the
  argument for preferring this mount.

🔴 **The "cap is 1.39× stronger" claim was computed on the LEGACY cavity**
(D/L 2.343, rejected by H1). The ratio is `(β/k_c)·maxJ₁/|J₀(x'₀₁)|`; the Bessel
part is 1.4447 and **β/k_c carries the shape**: 0.9604 legacy → 1.387, but
0.6252 on H1's cavity → **0.903**. The barrel is stronger, and the eigen pair
agrees. See `../KNOWN.md` § ITEM 7 STEP 1.

## Rendering

`openscad -o x.stl view.scad` works headless and is how these are validated
(all four export clean, zero warnings). **`-o x.png` segfaults on this box** —
it needs a GL context, and it crashes on `cube(10);` too, so it is the
environment, not the models. Use the GUI to look at them.

## Deferred — agreed 2026-08-25, not blocking

1. **OpenSCAD 2024, then import `baselines.json` directly.** This box has
   `2021.01`, which cannot read JSON, which is the only reason `scadgen.py`
   exists. On 2024 the params file and the generator both **go away** and
   `amip.scad` reads the store itself — one less generated artefact and one
   less way for a drawing to go stale.
2. **Fix headless rendering.** `-o x.png` segfaults (GL context); it dies on
   `cube(10);` too. Likely `xvfb-run` or a newer build. Until then PNGs cannot
   be produced from a script, so **CI cannot diff the drawings** — only the
   STL export path is automatable.

⚠️ Neither blocks the physics. Both are tooling debt, recorded so the
`scadgen.py` indirection is understood as a WORKAROUND rather than a design.
