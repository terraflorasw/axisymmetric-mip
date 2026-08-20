#!/usr/bin/env python3
"""Structured RESULTS for a solved run. Measurements only — no interpretation.

Every driver here has printed a human-readable table to a log and nothing else.
So the log is prose, not data, and every re-examination has meant re-deriving the
spectrum from postpro/ with one-off Python. That has happened perhaps a dozen
times in one session and it is where several errors came from: a hand-written
recompute is an unreviewed analysis, and it gets no second look.

🔑 THE SPLIT THIS FILE EXISTS TO ENFORCE:

    criteria      declared IN ADVANCE, in the driver's docstring    (pre-commitment)
    measurement   this file — raw numbers plus provenance           (durable)
    evaluation    evaluate.py — labels, criteria, verdict           (re-runnable)

The verdict block used to do all three at once, and it has been wrong four times
across two authors (R54 three ways, R74's unimodal detector, R79's excluded band,
R59's mode-hopping tracker) while the underlying tables survived every time. R54's
own conclusion was "the raw table is what stands". This makes that structural: a
bad evaluation becomes a rerun instead of a retraction.

⚠️ NO LABELS ARE STORED HERE. Not "TE011", not "TM111". Those are hypotheses, and
two of them were wrong this session — R77 identified a mode as TM111 that was not,
and R59's tracker re-identified its target at every depth. A label is an output of
evaluation, so it belongs with the evaluation, where it can be revised without
touching the measurement.

⚠️ THE WINDOW IS ALWAYS RECORDED. band, step, sample count and the peak threshold
go in every file, so a mode's absence from a result is automatically qualified as
absence FROM A STATED WINDOW. "Absent from a window is not absent" has now cost
this project three times (R54's retracted TM111/TM020, R77's excluded 2.3431,
R59's unlocated TM111). A reader should not have to find the docstring to know
what was searched.

⚠️ MESH IDENTITY IS RECORDED — md5, tets, size-factor, geometry. Comparability
between runs becomes checkable rather than assumed, which is the R27/R11 failure.

Everything is DERIVED from the mesh sidecar and the Palace config, never passed in
by hand — the R50 principle, one level up from where R50 applied it.
"""
import csv
import hashlib
import json
import pathlib
import time

import dq
import modes

SCHEMA = 1
PEAK_REL = 0.001          # keep everything above 0.1% of the window maximum
EPS0 = 8.8541878128e-12


def _groove_frac(base, tag, i):
    """p_elec[80] + p_mag[80] at sample i, or None if the mesh has no groove tag."""
    p = pathlib.Path(base) / tag / "domain-E.csv"
    if not p.exists():
        return None
    with open(p) as fh:
        rows = [{k.strip(): v.strip() for k, v in r.items() if k}
                for r in csv.DictReader(fh)]
    if not rows or i >= len(rows) or "p_elec[80]" not in " ".join(rows[0]):
        return None
    e = m = 0.0
    for k, v in rows[i].items():
        if "p_elec[80]" in k:
            e = float(v)
        elif "p_mag[80]" in k:
            m = float(v)
    return e + m


def _plasma_sectors(base, tag, i, lo=20, hi=40):
    """p_elec[20..] at sample i — the azimuthal deposition profile, or []."""
    p = pathlib.Path(base) / tag / "domain-E.csv"
    if not p.exists():
        return []
    with open(p) as fh:
        rows = [{k.strip(): v.strip() for k, v in r.items() if k}
                for r in csv.DictReader(fh)]
    if not rows or i >= len(rows):
        return []
    hdr = " ".join(rows[0])
    out = []
    for a in range(lo, hi):
        if f"p_elec[{a}]" not in hdr:
            continue
        for k, v in rows[i].items():
            if f"p_elec[{a}]" in k:
                out.append(float(v))
                break
    return out


def _peaks(recs, rel=PEAK_REL):
    U = [r["U"] for r in recs]
    um = max(U) if U else 0.0
    return [i for i in range(2, len(U) - 2)
            if U[i] == max(U[i - 2:i + 3]) and U[i] > rel * um]


def extract(tag, base="postpro"):
    """Everything measurable about a solved run, with its provenance.

    Reads the Palace config for the window and the materials, and the mesh
    sidecar for geometry — so the record cannot disagree with what was solved.
    """
    cfgp = pathlib.Path(f"{tag}.json")
    cfg = json.loads(cfgp.read_text()) if cfgp.exists() else {}
    mesh = cfg.get("Model", {}).get("Mesh")
    meta = {}
    md5 = None
    if mesh and pathlib.Path(mesh).exists():
        md5 = hashlib.md5(pathlib.Path(mesh).read_bytes()).hexdigest()
        mp = pathlib.Path(mesh).with_suffix(".meta.json")
        if mp.exists():
            meta = json.loads(mp.read_text())
    samples = (cfg.get("Solver", {}).get("Driven", {}).get("Samples") or [{}])[0]

    recs = dq.load(tag, base)
    if not recs:
        raise RuntimeError(f"{tag}: no records in {base}/{tag}")
    sect = modes.sector_energy(tag, base)
    U = [r["U"] for r in recs]
    um = max(U)

    # plasma conductivity, if any — the difference between a cold and a lit run,
    # read back OUT of the config rather than remembered by the caller
    sigma = None
    for m in cfg.get("Domains", {}).get("Materials", []):
        if "Conductivity" in m:
            sigma = m["Conductivity"]

    out = []
    for i in _peaks(recs):
        r = recs[i]
        b1, b2 = modes.azimuthal(sect[i]) if sect else (None, None)
        out.append(dict(
            i=i, f=r["f"], U=r["U"], rel=r["U"] / um,
            bore_h=r["pm"], bore_e=r["pe"],
            pm_over_pe=(r["pm"] / r["pe"]) if r["pe"] else None,
            Q0=r["Q0"], gamma=r["gamma"], s_db=r["s_db"],
            eta=1.0 - r["gamma"] ** 2, b1=b1, b2=b2,
            # R81: fraction of this mode's energy INSIDE the groove, when the
            # mesh tags it. None means the mesh did not tag it — which is NOT
            # the same as zero, and must never be read as "no energy in the
            # slot".
            groove_frac=_groove_frac(base, tag, i),
            # R83: electric-energy fraction in each plasma azimuthal sector.
            # Deposited power is (sigma/eps0) * E_elec, so with one sigma across
            # the torus these fractions ARE the deposition profile. Empty list
            # means the mesh was not sectored — never read that as uniform.
            plasma_sectors=_plasma_sectors(base, tag, i)))

    return dict(
        schema=SCHEMA, tag=tag, written=time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                      time.gmtime()),
        mesh=mesh, mesh_md5=md5,
        tets=meta.get("tets"), size_factor=meta.get("size_factor"),
        sectors=meta.get("sectors"), loop_phi_deg=meta.get("loop_phi_deg"),
        loop_tilt_deg=meta.get("loop_tilt_deg"),
        geometry_mm=meta.get("geometry_mm"),
        order=cfg.get("Solver", {}).get("Order"),
        # ⚠️ the window. Every absence claim must be read against this.
        window=dict(f_min=samples.get("MinFreq"), f_max=samples.get("MaxFreq"),
                    step=samples.get("FreqStep"), n_samples=len(recs),
                    peak_rel_threshold=PEAK_REL),
        plasma_sigma=sigma, lit=sigma is not None,
        u_max=um, modes=out)


def write(tag, base="postpro", extra=None):
    d = extract(tag, base)
    if extra:
        d["extra"] = extra
    p = pathlib.Path(f"{tag}.result.json")
    p.write_text(json.dumps(d, indent=1))
    return d


def load(tag):
    return json.loads(pathlib.Path(f"{tag}.result.json").read_text())


def sweep(tags, name, base="postpro", extra=None):
    """Write per-case results AND a sweep index that pins comparability.

    ⚠️ A sweep is only a sweep if every case shares a size-factor (R27). That is
    asserted here rather than trusted, and the index records the fact so a later
    reader does not have to take it on faith.
    """
    got = {}
    for t in tags:
        try:
            got[t] = write(t, base)
        except Exception as e:
            got[t] = dict(tag=t, error=str(e))
    facs = {t: d.get("size_factor") for t, d in got.items() if "error" not in d}
    common = len(set(facs.values())) == 1
    idx = dict(schema=SCHEMA, sweep=name,
               written=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               cases=list(tags), size_factors=facs,
               comparable=common,
               note=("all cases share a size-factor" if common else
                     "🔴 MIXED SIZE-FACTORS — differences between these cases "
                     "are partly discretisation, not geometry (R27)"),
               extra=extra or {})
    pathlib.Path(f"{name}.sweep.json").write_text(json.dumps(idx, indent=1))
    return idx, got


if __name__ == "__main__":
    import sys
    for t in sys.argv[1:]:
        try:
            d = write(t)
            w = d["window"]
            print(f"  {t}: {len(d['modes'])} modes, window "
                  f"{w['f_min']}-{w['f_max']} @ {w['step']}, "
                  f"{d['tets']:,} tets, sf {d['size_factor']}, "
                  f"{'LIT sigma=' + str(d['plasma_sigma']) if d['lit'] else 'cold'}")
        except Exception as e:
            print(f"  🔴 {t}: {e}")
