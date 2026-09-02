"""Absolute |E| at the named probes, and the margins that decide two blockers.

VERIFICATION   scales an eigenmode by U = Q*P/omega, the same relation used for
               the port-gap estimate that agreed with Palace's own port voltage.
FALSIFICATION  if a margin is below 1 the design does not survive at that power.

🔑 EVALUATION LAYER, DELIBERATELY SEPARATE FROM THE RIG (§10, and the
   separate-measurement-from-evaluation rule). The rig emits |E| in EIGENMODE
   units plus the mode energy; every judgement here — which power, which Q,
   which breakdown law, what counts as margin — is applied afterwards and can
   be re-run without re-solving.

    python3 fieldcheck.py --slug h3-groove-gap-01
"""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import slug as S
import values


def e_breakdown_air(d_mm):
    """Uniform-field breakdown in air at 1 atm, V/m. E[kV/cm] = 24.36+6.72/sqrt(d[cm]).

    ⚠️ UNIFORM FIELD. A wire-end gap is not uniform; edge enhancement lowers
    the real limit, so this is OPTIMISTIC and a margin near 1 is not a pass.
    """
    return (24.36 + 6.72 / math.sqrt(d_mm / 10.0)) * 1e5


def scale_to_power(u_mode_j, q_loaded, p_watt, f_hz):
    """Field scale factor from an eigenmode's arbitrary amplitude to P watts."""
    if not u_mode_j or not q_loaded:
        return None
    u_real = q_loaded * p_watt / (2 * math.pi * f_hz)
    return math.sqrt(u_real / u_mode_j)


def report(sl, p_watt=1000.0):
    f = values.get("source.f0.ghz") * 1e9
    atm = values.get("cavity.atmosphere")
    res = pathlib.Path(S.outfile(sl, "result.json"))
    if not res.exists():
        sys.exit(f"no result for {sl}")
    d = json.loads(res.read_text())
    print(f"  {sl}: |E| at {p_watt:.0f} W, cavity atmosphere = {atm}\n")
    print(f"  🔑 COLD is the worst case: a loaded cavity stores far less "
          f"(Q_L ~ 100 vs ~10^4).\n")
    any_row = False
    for pt in d.get("points", []):
        fl = pt.get("field_pec") or pt.get("field_lumped")
        if not fl or not fl.get("probe_E_named"):
            continue
        # pec Q is the UNLOADED Q; the driven state is the lumped one.
        # 🔴 SCALE BY THE Q THE SOURCE ACTUALLY SEES, OR NOT AT ALL.
        # This was `lumped Q or Q0`. For a cavity WITH a loop those differ by
        # ~37x (Q_L 1,090 vs Q0 40,716 at ld=11), so the fallback silently
        # inflates stored energy 37x and every field by sqrt(37) = 6.1x —
        # turning a 4x breakdown margin into an apparent 0.7x. A pec-only run
        # has no lumped Q at all, so it would trigger this on every case.
        # ⚠️ Q0 IS correct when there is no loop: then Q_L == Q0 and nothing is
        # extracted. So the rule is about the PORT, not about availability.
        q = (pt.get("te011_lumped") or {}).get("Q")
        if q is None:
            if not pt.get("ld"):
                q = pt.get("Q0")          # no loop: the source sees Q0
            else:
                print(f"  --- {pt.get('name')}   🔴 NO LOADED Q")
                print(f"      This case has a loop (ld={pt.get('ld')}) but no "
                      f"`lumped` solve, so the Q the source sees is unknown.")
                print(f"      REFUSING to scale from Q0="
                      f"{pt.get('Q0') or float('nan'):,.0f} — it is ~37x too "
                      f"large and would overstate every field by ~6x.")
                print("      Re-run with port_bcs including 'lumped'.")
                continue
        k = scale_to_power(fl.get("U_mode_J"), q, p_watt, f)
        if not k:
            continue
        any_row = True
        print(f"  --- {pt.get('name')}   Q_L={q:,.0f}  scale={k:,.0f}x")
        # 🔴 EVERY CONDUCTOR BREAK NEEDS A LIMIT, NOT JUST THE ONE WE THOUGHT
        # OF. Only `series_gap` was mapped, so a `port_gap` reading would have
        # printed a bare MV/m with no limit beside it — and the port gap is the
        # TIGHTER of the two (0.3 mm vs 0.5 mm) and carries the drive.
        # ⚠️ The port gap is the REQUESTED value, not read back from the mesh:
        # the sidecar records loop_gap2 and loop_mount but NOT the port gap or
        # [ld, lw]. That is NEXT.md's fourth debt; until it is paid this one
        # value is bound from baselines rather than from the artefact, which is
        # weaker (mesh-is-what-you-ordered) and is flagged in the output.
        # 🔑 wall_gap is the AZIMUTHAL loop's conductor-to-wall clearance. It
        # is not a fixed design value like the series and port gaps — it VARIES
        # WITH h, which is the axis being swept — so it comes from the mesh
        # sidecar per case, never from baselines. ⚠️ It is also the one gap the
        # rectangular family has no equivalent of, and the reason the arc has an
        # arc risk at all: at h = 2 mm with a 1 mm wire the clearance is 1.0 mm.
        gaps = {"wall_gap": pt.get("mesh_clearance_mm") or 0.0,
                "series_gap": pt.get("mesh_gap2_mm") or 0.0,
                "port_gap": pt.get("mesh_port_gap_mm")
                # 🔴 allow_tentative, SAID OUT LOUD as the store demands.
                # `loop.gap.mm` = 0.3 has NO PROVENANCE — "geometry.py default,
                # inherited", flagged tentative in baselines — and values.get()
                # refuses it by default. That refusal is CORRECT: this is the
                # TIGHTER of the two conductor breaks, it carries the drive, and
                # nobody chose it. Using it to compute a breakdown limit is
                # better than printing a field with no limit, but the margin
                # below is only as good as a number with no owner.
                or values.get("loop.gap.mm", allow_tentative=True)}
        _unverified = {"port_gap"} if not pt.get("mesh_port_gap_mm") else set()
        for nm, e_mode in sorted(fl["probe_E_named"].items()):
            e = e_mode * k
            g = gaps.get(nm)
            if g:
                lim = e_breakdown_air(g)
                m = lim / e if e else float("inf")
                flag = "✅" if m > 2 else ("⚠️ THIN" if m > 1 else "🔴 BREAKS DOWN")
                print(f"      {nm:<12}{e/1e6:>8.3f} MV/m   limit({g:g} mm) "
                      f"{lim/1e6:.2f}   margin {m:.2f}x {flag}"
                      + ("  ⚠️ TENTATIVE gap, from baselines not the mesh"
                         if nm in _unverified else ""))
            else:
                print(f"      {nm:<12}{e/1e6:>8.3f} MV/m")
    if not any_row:
        print("  (no named-probe fields recorded — the rig must be re-run "
              "with the probes in place)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--slug" not in a:
        sys.exit("usage: fieldcheck.py --slug <slug> [--power W]")
    sl = a[a.index("--slug") + 1]
    pw = float(a[a.index("--power") + 1]) if "--power" in a else 1000.0
    report(sl, pw)
