#!/usr/bin/env python3
"""Build a Palace driven config FROM THE MESH's sidecar, not by hand.

R50. Three config/mesh disagreements in one night, all of them the same shape —
a value that the mesh already knew, maintained separately by hand:

  port Direction   R47 died in 7 s: loop at phi = 36 deg, Direction still the
                   phi = 0 value copied between eight scripts. Palace refuses a
                   direction outside the port face, so it failed LOUDLY. The
                   quieter version of this bug is the dangerous one.
  materials on     --brake 0 leaves attribute 8 absent. A config still binding a
  absent attrs     material to it describes a model it is not solving.
  sector energy    --sectors 5 needs materials on attributes 3..7 and an Energy
                   block per sector; getting it wrong yields no azimuthal data
                   and no error.

Everything here is derived from `<mesh>.meta.json`, which geometry.py writes at
mesh time. The config cannot disagree with the mesh because it is not told
anything the mesh did not say.
"""
import copy
import json
import pathlib

TEMPLATE = "w890.json"


def load_meta(mesh):
    p = pathlib.Path(mesh).with_suffix(".meta.json")
    if not p.exists():
        raise FileNotFoundError(
            f"{p.name} missing — rebuild the mesh with the current geometry.py. "
            "A config assembled without it is guessing at the port direction "
            "and the attribute list.")
    meta = json.loads(p.read_text())
    # R111: refuse a PRE-RENAME sidecar rather than half-read it. The old keys
    # named materials and idealisations that are no longer true — "quartz" for a
    # sapphire torch, "pec" for a finite-conductivity wall, "brake" for the mode
    # filter. Silently falling back to them is how a wrong name becomes a wrong
    # result; failing loudly costs one rebuild.
    stale = {"quartz", "pec", "brake"} & set(meta.get("attributes", {}))
    if stale:
        raise ValueError(
            f"{p.name} predates the R111 rename (has {sorted(stale)}). "
            "Rebuild the mesh with the current geometry.py — attribute NUMBERS "
            "are unchanged, only the names, so nothing about the physics moves.")
    return meta


def driven(mesh, tag, band, step=2e-5, order=1, materials=None,
           energy_bins=True, template=TEMPLATE):
    """A driven config for `mesh`, with everything mesh-dependent derived.

    materials: {attribute: {...}} overrides/additions, e.g. a plasma
               conductivity on the TAG_PLASMA attribute. Attributes absent from
               the mesh are DROPPED with the reason stated, never silently.
    """
    meta = load_meta(mesh)
    attrs = meta["attributes"]
    c = copy.deepcopy(json.loads(pathlib.Path(template).read_text()))
    c["Model"]["Mesh"] = pathlib.Path(mesh).name
    c["Problem"]["Output"] = f"postpro/{tag}"
    c["Solver"]["Order"] = order
    c["Solver"]["Driven"]["Samples"] = [{"Type": "Linear", "MinFreq": band[0],
                                         "MaxFreq": band[1], "FreqStep": step}]

    if meta["port_direction"] is None:
        raise ValueError(f"{meta['mesh']} has no coupling loop — a driven solve "
                         "needs one")
    c["Boundaries"]["LumpedPort"][0]["Direction"] = meta["port_direction"]
    c["Boundaries"]["LumpedPort"][0]["Attributes"] = [attrs["port"]]
    c["Boundaries"]["Conductivity"][0]["Attributes"] = [attrs["wall"]]
    # R110: BIND THE WALL METAL FROM baselines.json, not from the template.
    # R58 adopted bare electropolished aluminium (3.5e7) on optical grounds and
    # wrote it to baselines; the template kept SILVER (6.3e7) and nothing ever
    # connected the two. Every solve since has used silver walls, so every
    # absolute Q in the record is ~33% high. Exactly the R101 failure again:
    # a decision recorded in one place and never bound to the thing that
    # consumes it. A baseline nobody reads is a claim, not a fact.
    try:
        # 🔑 ONE ACCESSOR. This did its OWN json read with the key hardcoded,
        # so the 2026-08-25 rename to wall.conductivity.s_per_m broke it while
        # e0k2_anchor.wall_sigma() kept working — two bindings, one updated.
        # values.get() resolves aliases, so a rename is non-breaking here now.
        import values
        _sig = values.get("wall.conductivity.s_per_m")
    except Exception as e:
        # 🔴 WAS "never fail a solve over this", and printed a warning while
        # substituting the TEMPLATE — which is SILVER, 6.3e7. This programme's
        # baselines.json starts EMPTY by design, so the lookup failed on every
        # single solve and the whole resonance record ran silver walls: every
        # absolute Q ~34% high (sqrt(6.3/3.5)). R110 fixed exactly this bug in
        # the old programme and the "start empty" policy silently undid it.
        #
        # A warning that does not stop anything is a warning nobody acts on. An
        # undeclared wall metal now REFUSES to solve.
        raise RuntimeError(
            f"wall conductivity not declared in baselines.json ({e}). "
            f"Refusing to fall back to the template's {c['Boundaries']['Conductivity'][0]['Conductivity']:.3g} S/m "
            f"— that is silver, and substituting it silently is how every Q in "
            f"this record became ~34% high. Declare wall.conductivity "
            f"(kind=input, with source) in baselines.json.")
    else:
        _was = c["Boundaries"]["Conductivity"][0]["Conductivity"]
        c["Boundaries"]["Conductivity"][0]["Conductivity"] = _sig
        if abs(_was - _sig) / _sig > 1e-9:
            print(f"    wall: {_sig:.3g} S/m from baselines "
                  f"(template said {_was:.3g})", flush=True)

    # 🔴 THE LOOP IS A DIFFERENT METAL AND, UNTIL 2026-08-27, WAS NOT ONE.
    # geometry.py tagged the wire's surface into TAG_WALL (it is an exterior
    # face like any other), so the coupler solved as ALUMINIUM and its loss was
    # indistinguishable from the cavity's. It now has attribute 92.
    #
    # 🔴🔴 FAIL CLOSED. A mesh that DECLARES a loop attribute and gets no
    # Conductivity entry for it is WORSE than before the split: Palace applies
    # its default PEC to any unlisted boundary, so the coupler would become
    # LOSSLESS — and a lossless resonant element at λ/4 is exactly the thing
    # whose loss we are trying to measure. So this refuses rather than warns.
    _loop_attr = attrs.get("loop")
    if _loop_attr is not None:
        try:
            _lsig = values.get("loop.conductivity.s_per_m")
        except Exception as e:
            raise RuntimeError(
                f"the mesh declares a loop surface (attribute {_loop_attr}) but "
                f"loop.conductivity.s_per_m is not usable ({e}). REFUSING: an "
                f"unlisted boundary attribute is PEC in Palace, so solving now "
                f"would model the coupler as LOSSLESS — worse than the "
                f"aluminium it had before it was split out. Declare the loop "
                f"metal, or mesh without the split.")
        c["Boundaries"]["Conductivity"].append(
            {"Attributes": [_loop_attr], "Conductivity": _lsig,
             "Permeability": 1.0, "Thickness": 0.0, "External": False})
        print(f"    loop: {_lsig:.3g} S/m on attribute {_loop_attr} "
              f"(wall is {_sig:.3g})", flush=True)

    # Air sectors: one material over every air attribute the mesh actually has.
    air = attrs["air"]
    mats, dropped = [], []
    for m in c["Domains"]["Materials"]:
        a = m["Attributes"]
        if a == [3]:
            mats.append(dict(m, Attributes=list(air)))
        elif a == [attrs["bore"]]:
            mats.append(m)
        elif a == [attrs["torch"]]:
            # R101: THE TORCH'S PERMITTIVITY MUST COME FROM THE MESH.
            # geometry.py's --torch-material fed only the mesh SIZING and the
            # sidecar label; the solver went on reading the template's
            # 3.78/1e-4. A sapphire mesh therefore solved as quartz, and the two
            # meshes were BYTE-IDENTICAL, so nothing downstream could notice.
            # This is exactly the class R50 built this module to kill: a value
            # the mesh already knew, maintained separately by hand. It stayed
            # latent because no driven rig had ever passed --torch-material.
            tm = (meta.get("geometry_mm") or {}).get("torch_material")
            if tm is None:
                print(f"    ⚠️ torch material from TEMPLATE "
                      f"(eps={m.get('Permittivity')}, "
                      f"tand={m.get('LossTan')}) — this mesh's sidecar has no "
                      "torch_material. Rebuild with the current geometry.py to "
                      "bind it from the mesh.", flush=True)
                mats.append(m)
            else:
                mats.append(dict(m, Permittivity=float(tm[0]),
                                 LossTan=float(tm[1])))
                print(f"    torch: eps={float(tm[0])} tand={float(tm[1])} "
                      "(from mesh sidecar)", flush=True)
        elif a == [8]:
            if attrs["filter"] is None:
                dropped.append("brake (attribute 8 absent — --brake 0)")
            else:
                mats.append(m)
        elif a == [11]:
            if attrs["upstream"] is None:
                dropped.append("upstream (attribute 11 absent)")
            else:
                mats.append(m)
        else:
            mats.append(m)
    # R81: the groove, when tagged, is a separate VOLUME of air. It needs a
    # material or Palace rejects the mesh — and it is air, not a new medium: the
    # point of tagging is to measure where a mode's energy IS, not to change the
    # physics. A tagged mesh and an untagged one must differ only in bookkeeping.
    if attrs.get("groove") is not None:
        air_mat = next((m for m in c["Domains"]["Materials"]
                        if m["Attributes"] == [3]), None)
        if air_mat is None:
            raise ValueError("groove is tagged but the template has no air "
                             "material to copy — refusing to guess its medium")
        mats.append(dict(air_mat, Attributes=[attrs["groove"]]))

    for attr, spec in (materials or {}).items():
        if attr is None:
            dropped.append("a requested material on an attribute the mesh lacks")
            continue
        mats.append(dict(spec, Attributes=[attr]))
    c["Domains"]["Materials"] = mats

    # Index 1 stays the bore so dq.py keeps working; sectors follow.
    energy = [{"Index": 1, "Attributes": [attrs["bore"]]}]
    if energy_bins and len(air) > 1:
        energy += [{"Index": 2 + i, "Attributes": [a]} for i, a in enumerate(air)]
    # R81: index 80 is the GROOVE. This is the measurement the whole tagging
    # exists for — the fraction of a mode's energy inside the slot separates
    # "cavity mode the groove perturbs" from "mode the groove created", which
    # three rounds of inference from bore-H/bore-E/azimuthal-DFT could not.
    # Indices 1-7 are bore and air sectors, 90 is the plasma; 80 collides with
    # neither.
    if attrs.get("groove") is not None:
        energy.append({"Index": 80, "Attributes": [attrs["groove"]]})
    # R83: one Energy index per plasma azimuthal sector, numbered to match its
    # attribute (20..20+ns-1). This is the measurement C1 was a proxy for —
    # deposited power per unit azimuth IN THE PLASMA, lit, rather than stored
    # energy over the whole cold cavity.
    for a_ in (attrs.get("plasma_sectors") or []):
        energy.append({"Index": a_, "Attributes": [a_]})
    c["Domains"]["Postprocessing"]["Energy"] = energy

    return c, meta, dropped


def write(mesh, tag, band, **kw):
    c, meta, dropped = driven(mesh, tag, band, **kw)
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    d = meta["port_direction"]
    print(f"  config {tag}.json from {meta['mesh']}: "
          f"port ({d[0]:+.4f},{d[1]:+.4f},{d[2]:+.4f}) "
          f"tilt {meta['loop_tilt_deg']:.0f}° phi {meta['loop_phi_deg']:.0f}°, "
          f"{len(meta['attributes']['air'])} air bin(s), "
          f"size-factor {meta['size_factor']}", flush=True)
    for d_ in dropped:
        print(f"    dropped: {d_}", flush=True)
    return meta
