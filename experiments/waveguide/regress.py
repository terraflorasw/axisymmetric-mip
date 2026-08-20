#!/usr/bin/env python3
"""Regression net — re-derive the VALID baselines from stored solver output.

R50, and the first thing built in the refactor, because the audit's rule applies
to the refactor itself: do not change code you cannot regress.

TWO TIERS, and this is tier 1:

  tier 1 (here)   Re-analysis of postpro/ CSVs already on disk. Seconds, no
                  solver. Covers the ENTIRE analysis layer — extraction, peak
                  finding, mode selection, azimuthal DFT — which is where three
                  of the night's bugs lived and where every future refactor of
                  dq.py / modes.py can break something silently.
  tier 2 (later)  Full solves on pinned meshes. Hours. Run rarely.

⚠️ ONLY ✅-VALID BASELINES ARE PINNED HERE. AUDIT.md classifies 34 of 57 entries
as contingent on R62 and several more as weakened. Pinning a contingent value
would make a choice that is still open look authoritative — the exact failure the
audit exists to prevent. Entries deliberately NOT covered are listed at the end.

⚠️ These checks re-read the SAME CSVs with the SAME code, so agreement should be
essentially exact. A tolerance here is not measurement error — it is how much
refactoring drift we are willing to accept silently. Keep it tight.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import modes

FAILED = []
CHECKED = 0


def check(name, got, want, tol, unit="", note=""):
    global CHECKED
    CHECKED += 1
    ok = got is not None and abs(got - want) <= tol
    mark = "✅" if ok else "🔴"
    g = "None" if got is None else f"{got:.5f}"
    print(f"  {mark} {name:<42} {g:>12} vs {want:>10.5f} {unit} {note}")
    if not ok:
        FAILED.append(name)
    return ok


def f_of(tag, which):
    ms = modes.peaks(tag)
    m = getattr(modes, which)(ms)
    return m["f"] if m else None


def q_of(tag, which):
    ms = modes.peaks(tag)
    m = getattr(modes, which)(ms)
    return m["Q0"] if m else None


print(__doc__)
print("=" * 78)

# ---------------------------------------------------------------- known answer
print("\nKNOWN-ANSWER: the azimuthal DFT against synthetic patterns")
c = [(k + 0.5) * 2 * math.pi / 5 for k in range(5)]
b1, b2 = modes.azimuthal([1.0] * 5)
check("uniform (m=0) -> bin1", b1, 0.0, 1e-9)
check("uniform (m=0) -> bin2", b2, 0.0, 1e-9)
b1, b2 = modes.azimuthal([math.cos(p) ** 2 for p in c])
check("cos^2(phi)  (m=1) -> bin2", b2, 0.5, 1e-9)
check("cos^2(phi)  (m=1) -> bin1", b1, 0.0, 1e-9)
b1, b2 = modes.azimuthal([math.cos(2 * p) ** 2 for p in c])
check("cos^2(2phi) (m=2) -> bin1", b1, 0.5, 1e-9)
check("cos^2(2phi) (m=2) -> bin2", b2, 0.0, 1e-9)

# --------------------------------------------------------- the three bug guards
print("\nBUG GUARDS: the wrong-mode picks that fired three times tonight")
ms = modes.peaks("s5_nomf")
tm = modes.tm111(ms)
check("TM111 unfiltered is 2.40022 NOT the 2.42236 hybrid",
      tm["f"] if tm else None, 2.40022, 5e-5, "GHz", "(R54/R61 mis-pick)")
te = modes.te011(ms)
check("TE011 unfiltered is 2.41974 NOT the 1.2% family",
      te["f"] if te else None, 2.41974, 5e-5, "GHz", "(R39 mis-pick)")
try:
    modes.tm111(modes.peaks("choff"))
    print("  🔴 TM111 selection did NOT refuse on a sectors=1 run")
    FAILED.append("tm111 refuses without sector data")
    CHECKED += 1
except ValueError:
    CHECKED += 1
    print("  ✅ TM111 selection refuses on a sectors=1 run rather than guessing")

# ------------------------------------------------------------- design point
print("\nDESIGN POINT (choff.msh, order 1)")
check("te011.f_raw_order1", f_of("choff", "te011"), 2.41692, 5e-5, "GHz")
check("tm020.f_raw_order1", f_of("choff", "tm020"), 2.37546, 5e-5, "GHz")
check("te011.q0", q_of("choff", "te011"), 45728, 250, "")
check("tm020.q0", q_of("choff", "tm020"), 23443, 150, "")

print("\nORDER-2 CONVERGED (r38o2) AND THE OFFSETS")
check("te011.f_converged", f_of("r38o2", "te011"), 2.44146, 5e-5, "GHz")
check("tm020.f_converged", f_of("r38o2", "tm020"), 2.39552, 5e-5, "GHz")
o_te = (f_of("r38o2", "te011") - f_of("r38o1", "te011")) * 1000
o_tm = (f_of("r38o2", "tm020") - f_of("r38o1", "tm020")) * 1000
check("offset.te011  (supersedes +31.6)", o_te, 24.54, 0.05, "MHz")
check("offset.tm020", o_tm, 20.06, 0.05, "MHz")

print("\nAPERTURES (c2141 vs choff)")
check("effect.chimney_te011",
      (f_of("c2141", "te011") - f_of("choff", "te011")) * 1000, -0.06, 0.05, "MHz")
check("effect.chimney_tm020",
      (f_of("c2141", "tm020") - f_of("choff", "tm020")) * 1000, 1.26, 0.05, "MHz")

print("\nTM111 AND AZIMUTHAL IDENTIFICATION")
check("tm111.f_filtered", f_of("s5_mf", "tm111"), 2.35094, 5e-5, "GHz")
check("tm111.f_unfiltered", f_of("s5_nomf", "tm111"), 2.40022, 5e-5, "GHz")
mf, nomf = modes.peaks("s5_mf"), modes.peaks("s5_nomf")
sep_f = (modes.te011(mf)["f"] - modes.tm111(mf)["f"]) * 1000
sep_n = (modes.te011(nomf)["f"] - modes.tm111(nomf)["f"]) * 1000
check("filter TE011-TM111 separation, filtered", sep_f, 64.3, 0.2, "MHz")
check("filter TE011-TM111 separation, bare", sep_n, 19.5, 0.2, "MHz")
check("te011.azimuthal_floor (bin1)", modes.te011(mf)["b1"], 0.0046, 5e-4)
check("tm111 identification: bin2 at filtered TM111",
      modes.tm111(mf)["b2"], 0.2034, 5e-4, "", "(m=1)")

print("\nOPERATIONAL TILT (R60/R61)")
t45, t00 = modes.peaks("t45"), modes.peaks("t00")
r45 = modes.tm020(t45)["rel"] / modes.te011(t45)["rel"]
r00 = modes.tm020(t00)["rel"] / modes.te011(t00)["rel"]
check("TM020 suppression at 0 deg", -10 * math.log10(r00 / r45), 18.3, 0.3, "dB")
z0n, z0m = modes.peaks("z0_nomf"), modes.peaks("z0_mf")
check("te011.m2_contamination_unfiltered",
      modes.te011(z0n)["b1"] / modes.te011(z0m)["b1"], 8.5, 0.5, "x floor")

print("\nPLASMA (R15 converged mesh)")
# modes.loaded(), not modes.te011(): a plasma-loaded resonance carries ~0.43%
# bore-H against an unloaded TE011's ~2.08%, so the unloaded discriminator
# correctly refuses it. This distinction was found BY this net on its first run.
pl = modes.loaded(modes.peaks("p_06"))
check("plasma.q_loaded at sigma=30", pl["Q0"] if pl else None, 320, 15, "",
      "(R15: 311/319/320 over 7.4x refinement)")
check("  loaded resonance bore-H is NOT unloaded-TE011-like",
      pl["pm"] if pl else None, 0.0043, 0.0010, "", "(2.08% unloaded)")

# ------------------------------------------------- config derived from mesh
print("\nCONFIG DERIVATION (R50 — the mesh describes itself)")
import json as _json, tempfile, os
import solveconf
_d = tempfile.mkdtemp()


def _sidecar(**kw):
    meta = {"mesh": "x.msh", "port_direction": kw["dir"], "loop_phi_deg": kw["phi"],
            "loop_tilt_deg": kw["tilt"], "sectors": kw["ns"],
            "attributes": {"bore": 1, "quartz": 2,
                           "air": list(range(3, 3 + kw["ns"])),
                           "brake": kw["brake"], "upstream": 11, "plasma": None,
                           "pec": 90, "port": 91},
            "size_factor": 0.96, "mesh_order": 2, "tets": 1, "nodes": 1,
            "geometry_mm": {}}
    m = pathlib.Path(_d) / "x.msh"
    m.with_suffix(".meta.json").write_text(_json.dumps(meta))
    return str(m)


# the exact vector Palace reported as its own axis when R47 aborted
_R47 = [-0.41562693777745346, 0.5720614028176844, 0.7071067811865475]
c, _m, _drop = solveconf.driven(_sidecar(dir=_R47, phi=36, tilt=45, ns=5,
                                         brake=8), "t", (2.34, 2.50))
_got = c["Boundaries"]["LumpedPort"][0]["Direction"]
check("port Direction matches R47's Palace-reported axis",
      max(abs(a - b) for a, b in zip(_got, _R47)), 0.0, 1e-12, "",
      "(the crash that cost a run)")
_air = [m["Attributes"] for m in c["Domains"]["Materials"] if len(m["Attributes"]) > 1]
check("5 sectors -> air material spans attrs 3..7",
      float(len(_air[0]) if _air else 0), 5.0, 0)
check("5 sectors -> 6 energy bins (bore + 5)",
      float(len(c["Domains"]["Postprocessing"]["Energy"])), 6.0, 0)

c2, _m2, drop2 = solveconf.driven(_sidecar(dir=[0.0, 1.0, 0.0], phi=0, tilt=0,
                                           ns=1, brake=None), "t2", (2.34, 2.50))
_has8 = any(m["Attributes"] == [8] for m in c2["Domains"]["Materials"])
CHECKED += 1
if _has8 or not drop2:
    print("  🔴 material bound to absent attribute 8 (--brake 0)")
    FAILED.append("absent-attribute material dropped")
else:
    print("  ✅ material on absent attribute 8 dropped, and reported")
CHECKED += 1
try:
    solveconf.load_meta(str(pathlib.Path(_d) / "nosuch.msh"))
    print("  🔴 missing sidecar did not raise")
    FAILED.append("missing sidecar raises")
except FileNotFoundError:
    print("  ✅ missing sidecar raises rather than guessing")

# ------------------------------------------------------ offsets, geometry-bound
print("\nOFFSETS (R50 — the number that was 7.06 MHz wrong for the project's life)")
import offsets as _off
_rec = _off.from_runs("choff.msh", "r38o1", "r38o2")
check("offset.te011 measured from stored runs",
      _rec["offsets_mhz"]["TE011"], 24.54, 0.05, "MHz")
check("offset.tm020 measured from stored runs",
      _rec["offsets_mhz"]["TM020"], 20.06, 0.05, "MHz")
check("applying it reproduces te011.f_converged",
      _off.converged("choff.msh", "TE011", modes.te011(modes.peaks("choff"))["f"]),
      2.44146, 5e-5, "GHz")
CHECKED += 1
try:
    import shutil as _sh
    _sh.copy("choff.offset.json", "s5_mf.offset.json")
    _off.converged("s5_mf.msh", "TE011", 2.4)
    print("  🔴 a foreign-geometry offset was applied without complaint")
    FAILED.append("offset refuses foreign geometry")
except ValueError:
    print("  ✅ offset measured on another geometry is REFUSED "
          "(the +31.6 failure mode)")
finally:
    pathlib.Path("s5_mf.offset.json").unlink(missing_ok=True)
CHECKED += 1
try:
    _off.converged("t45.msh", "TE011", 2.4)
    print("  🔴 an unmeasured geometry returned an offset anyway")
    FAILED.append("offset requires measurement")
except FileNotFoundError:
    print("  ✅ unmeasured geometry raises rather than borrowing an offset")

# ------------------------------------------------- mesh no-op postconditions
print("\nMESH POSTCONDITIONS (R50 — replaying the two real no-ops)")
import json as __j, tempfile as __t, os as __o
import meshcheck
__d = __t.mkdtemp()


def __meta(tag, tets, ph, clamped, fac=0.96, mn=1.2):
    pathlib.Path(__d, f"{tag}.meta.json").write_text(__j.dumps(
        {"tets": tets, "size_factor": fac, "geometry_mm": {"plasma_h": ph},
         "sizing_mm": {"min": mn, "plasma_requested": ph,
                       "plasma_clamped": clamped}}))


__cwd = __o.getcwd()
__o.chdir(__d)
try:
    __meta("a", 14703, 1.0, True)
    __meta("b", 14586, 0.6, True)
    CHECKED += 1
    try:
        meshcheck.check(["a", "b"])
        print("  🔴 R15's clamped pair was NOT caught")
        FAILED.append("clamped-refinement no-op caught")
    except meshcheck.NoOp:
        print("  ✅ R15's clamped pair caught (1.0 vs 0.6 -> same 1.2 mm mesh)")
    __meta("c", 141500, 1.2, False, 0.93, 0.96)
    __meta("d", 245266, 0.8, False, 0.93, 0.64)
    __meta("e", 445438, 0.6, False, 0.93, 0.48)
    CHECKED += 1
    print("  ✅ R15's FIXED sweep passes" if meshcheck.check(["c", "d", "e"],
          strict=False) else "  🔴 fixed sweep wrongly rejected")
    __meta("f", 103293, 0.0, False)
    __meta("g", 102852, 0.0, False)
    CHECKED += 1
    print("  ✅ shape-only change (ovality, 0.4%) does not false-positive"
          if meshcheck.check(["f", "g"], strict=False)
          else "  🔴 ovality wrongly rejected as a no-op")
finally:
    __o.chdir(__cwd)

print("\n" + "=" * 78)
if FAILED:
    print(f"🔴 {len(FAILED)} of {CHECKED} FAILED: {', '.join(FAILED)}")
else:
    print(f"✅ all {CHECKED} checks pass")

print("""
NOT COVERED HERE, deliberately:
  · every ⚠️ PROVISIONAL entry (34 of 57, contingent on R62) — pinning them would
    make an open choice look settled
  · every 🔶 WEAKENED entry — the number is right, the reason for it is not, so a
    passing test would endorse the reason
  · anything needing a solve: mesh element counts, size-factor fallbacks, the
    geometry no-op guards. Those are tier 2, on pinned meshes.
  · match.* and the sigma sweep — R56's runs are on disk but the design point
    they describe is exactly what R62 may move""")
sys.exit(1 if FAILED else 0)
