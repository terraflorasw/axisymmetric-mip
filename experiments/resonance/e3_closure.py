"""E3 — the ENERGY-BALANCE CLOSURE. The declared falsifier for every eta.

PLAN E3: **eta_total = eta_plasma + eta_wall + eta_dielectric**, and
**F = the closure itself.** If the split does not sum to eta_total within a few
percent, the decomposition is WRONG and only eta_total may be quoted.
🔑 It has never been run. Every eta in the record is unfalsified.

## Method — one loss channel at a time, SAME MESH

Loss rates ADD in 1/Q, so if the three channels are independent:

    1/Q_all  ==  1/Q_wall + 1/Q_plasma + 1/Q_dielectric

Each term is measured by switching the OTHER two off on the SAME mesh:

    A  all on          wall sigma + plasma sigma + torch tand   -> Q_all
    B  WALL only       plasma sigma=0, torch tand=0             -> Q_wall
    C  PLASMA only     wall PEC,      torch tand=0              -> Q_plasma
    D  DIELECTRIC only wall PEC,      plasma sigma=0            -> Q_diel

🔴 **THE CLOSURE CAN ONLY FAIL ONE WAY, AND THAT IS THE POINT.** 1/Q addition is
exact IF the FIELD is the same in all four solves. It fails when a loss channel
is strong enough to REDISTRIBUTE the field — which is exactly when the
decomposition stops being meaningful. **So this is a test of whether "eta_plasma"
is a real quantity, not of arithmetic.**

⚠️ **RUN AT ne = 1e20, WHICH IS THE STRONGEST TEST, NOT THE OPERATING POINT.**
The plasma there is ~275x the wall loss, so the field is maximally perturbed. If
closure holds there it holds at the anchored 7.9e18, where the plasma perturbs
less. 🔴 It is ALSO the only density in reach: with the corrected nu_m the
anchored state sits at PI_1 = 2.46, inside h3_eigen's UNTESTED convergence gap
(0.56 < PI_1 < 5.58), and 3e18 is where eigen is known to FAIL outright.

## 🔴 AND A SECOND FINDING THIS RIG CARRIES

**Five rigs mesh the torch as VACUUM** (`--torch-material 1.0,3.5e-05`):
h3_driven, h3_groove, h3_margin, h3_step3, h3_loopsize. **The design torch is
`geometry.py`'s default — SAPPHIRE, eps = 11.6**, and that file says so in
terms: *"The build is ALL SAPPHIRE and PERMANENT... simulating quartz by default
would model a cavity we are not building."* Modelling it as eps=1 is further from
the design than the quartz that warning was written about.

🔑 It matters here twice over: **the DIELECTRIC is one of the three channels E3
must decompose** — with eps=1 there is almost nothing to decompose — and
`h4_field` measured a sapphire torch shifting f0 by **-15.00 MHz**, comparable to
the whole band margin.
✅ **So this rig meshes the DESIGN torch, and case E re-meshes with the vacuum
torch so the shift is measured rather than inferred.**
⚠️ h4_field's -15.00 MHz was on a GROOVE-FREE cavity and is discarded as a
number; it is quoted only as an order-of-magnitude expectation.

VERIFICATION
  V1  case A must reproduce a known point. ⚠️ There is NO prior loaded eigen on
      the design cavity, so V1 here is WEAK BY CONSTRUCTION: the check is that
      f0(A) sits below the vacuum-torch f0(E) by an amount of order 10 MHz, and
      that Q_all is dominated by the plasma. **Stated so it is not over-read.**
  V2  every case must mesh the SAME geometry — asserted from the sidecar, groove
      5x10 and the torch permittivity bound by `check_torch_bound`.
  V3  each single-channel Q must be LARGER than Q_all. A channel cannot dissipate
      more alone than with company.
FALSIFICATION
  🔴 F1  **THE CLOSURE.** If |1/Q_all - sum(1/Q_i)| / (1/Q_all) exceeds ~5%, the
         decomposition is WRONG and **only eta_total may be quoted** — every
         "eta_plasma" in the record becomes unquotable.
         ⚠️ ASSUMPTION: that the four solves see the same field. That is the
         thing being tested, so a failure is INFORMATIVE, not an error.
  🔴 F2  if eta_dielectric exceeds ~5%, the sapphire torch is a real loss term
         and PLAN's "dielectric is only ~2% of the loss budget" is wrong.
  ⚠️ F3 IS STALE AS OF 2026-08-25 AND WILL PROBABLY FIRE — CORRECTLY.
         Its -10 MHz expectation was set when eps was believed to be 11.6.
         Krupka et al. (Meas. Sci. Technol. 16 (2005) 1014, fig 10) measure
         eps PERPENDICULAR to the anisotropy axis at 9.39, and TE011's E_phi
         sees the perpendicular component. At 9.39 the shift is predicted to
         be NEAR ZERO. So F3 firing is the EXPECTED result, not a defect —
         CONVENTIONS 7w: a falsifier can fire for a reason its author never
         enumerated. Read a small shift as CONFIRMING R1, and re-state F3
         against the measured value rather than "fixing" the number.
  🔴 F3  if f0(sapphire) - f0(vacuum) is not of order -10 MHz, then either the
         torch binding is not reaching the solve or h4_field's -15.00 MHz does
         not transfer to a grooved cavity. **Both are findings; neither is noise.**
"""
import json
import math
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import solveconf
import eigmodes
import values
from e0_solver_vs_math import GEO, eigen_cfg, run
from e0k2_anchor import design_point, wall_sigma, LOOP_PHI, LOOP_RW, LOOP_GAP
from h3_loaded import drude, Z_FRAC, SECTORS, CAP_R_FRAC
from azimuthal import order as az_order
from e0k2_azim import sector_bins, read_sector_energy
from h3_ladder import purity, PROBE_PHI_DEG, PROBE_R_FRAC

# 🔑 THE RUN NAMES ITSELF FROM ITS SLUG (CONVENTIONS 7aw/7bd). Outputs carry
# slug + the hash of the config that produced them, so an edited config cannot
# silently reuse a filename.
import slug as S
SLUG = S.parse()
CFG = S.config(SLUG)
PRM = CFG["_run"]["parameters"]
TAG = S.out(SLUG)

# 🔑 FROM THE CONFIG, not a literal. 1e20 was never the operating point — it is
# 13x the anchored density, and a DIFFERENT regime (delta/shell 0.30 vs 1.06).
NE = float(PRM["ne"])
# 🔑 BOUND, NOT LITERAL (user, 2026-08-25: "no constants in any scripts").
# 🔴 AND THE VALUE CHANGED: eps was 11.6, which is eps_PARALLEL_c. TE011's E_phi
# sees eps_PERP_c = 9.39 (Krupka et al., Meas. Sci. Technol. 16 (2005) 1014,
# fig 10). This rig's case B measured the torch shift at 11.6, so THAT RESULT IS
# AT THE WRONG PERMITTIVITY and must be re-run before the shift is quoted.
TORCH_SAPPHIRE = (values.get("torch.sapphire.permittivity"),
                  values.get("torch.sapphire.loss_tangent", allow_tentative=True))
TORCH_VACUUM = (1.0, 3.5e-5)     # what five rigs have been meshing
RI, RO = 2.00, 8.50
LOOP_LD, LOOP_LW = values.get("loop.size.mm")
GROOVE = tuple(values.get("cavity.groove.mm"))

N_MODES = 8
EIGEN_TARGET = 2.38
CASE_TIMEOUT_S = 2700.0
WINDOW = (2.30, 2.65)
CLOSURE_TOL = 0.05               # F1
DIEL_ALARM = 0.05                # F2
SEED_GHZ = 2.4824                # h3_driven's loaded f0 (VACUUM torch) — a
                                 # starting point only; sapphire pulls it DOWN

# (label, wall_on, plasma_on, diel_on, torch)
# 🔑 CASES COME FROM THE CONFIG. Running all five costs two guaranteed 2700 s
# timeouts (A_all and C_plasma are sapphire+plasma, and the anchor is
# eps-near-zero), so which cases run is a per-question decision, not a constant.
_TORCH = {"sapphire": TORCH_SAPPHIRE, "vacuum": TORCH_VACUUM}
CASES = [(c["label"], bool(c["wall"]), bool(c["plasma"]), bool(c["dielectric"]),
          _TORCH[c["torch"]]) for c in PRM["cases"]]


def save(out):
    p = pathlib.Path(S.outfile(SLUG, "result.json"))
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def build(tag, torch, a, L, eps_p, sig_p, rec):
    zhi = Z_FRAC * L
    g = [x for x in GEO if x != "--no-torch"]
    g[g.index("--groove") + 1] = f"{GROOVE[0]:g},{GROOVE[1]:g}"
    args = (g + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                 "--sectors", str(SECTORS),
                 "--torch-material", f"{torch[0]},{torch[1]}",
                 "--plasma", f"{RI},{RO},{-zhi:.4f},{zhi:.4f}",
                 "--plasma-h", "1.000",
                 "--loop", f"{LOOP_LD},{LOOP_LW},{LOOP_RW},{LOOP_GAP}",
                 "--loop-cap", f"{CAP_R_FRAC * a:.4f}",
                 "--loop-phi", LOOP_PHI])
    rec["torch_req"] = list(torch)
    for sf in ("1.5", "1.42", "1.58"):
        r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                            "--size-factor", sf] + args,
                           capture_output=True, text=True)
        if not r.returncode and pathlib.Path(f"{tag}.msh").exists():
            rec["size_factor"] = sf
            return solveconf.load_meta(f"{tag}.msh")
        rec["_err"] = (r.stdout + r.stderr)[-200:]
    return None


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    w = 2.0 * math.pi * 2.45e9
    eps_p, sig_p = drude(NE, w)
    ne_anch, nu_anch, _ = ph.plasma_state(5245.0)
    print(f"  a={a:.4f} L={L:.4f}   ne={NE:.1e}  eps={eps_p:+.3f}  "
          f"sigma_p={sig_p:.4g} S/m")
    print(f"  torch: DESIGN = sapphire {TORCH_SAPPHIRE}, vs the {TORCH_VACUUM} "
          f"five rigs have been meshing")
    print(f"  ⚠️ run at 1e20 (strongest test AND the only convergent point); the "
          f"anchored {ne_anch:.1e} sits in eigen's untested gap\n", flush=True)

    out = {"ne": NE, "eps_p": eps_p, "sigma_p": sig_p,
           "torch_design": list(TORCH_SAPPHIRE), "torch_vacuum": list(TORCH_VACUUM),
           "closure_tol": CLOSURE_TOL, "cases": []}

    for label, wall_on, plasma_on, diel_on, torch in CASES:
        rec = {"case": label, "wall": wall_on, "plasma": plasma_on,
               "dielectric": diel_on, "torch": list(torch)}
        out["cases"].append(rec)
        print(f"  --- {label}:  wall={wall_on}  plasma={plasma_on}  "
              f"dielectric={diel_on}  torch_eps={torch[0]:g}", flush=True)
        mesh_tag = f"{TAG}_{'vac' if torch[0] == 1.0 else 'sap'}"
        if not pathlib.Path(f"{mesh_tag}.msh").exists():
            meta = build(mesh_tag, torch, a, L, eps_p, sig_p, rec)
            if meta is None:
                rec["error"] = f"mesh failed: {rec.pop('_err','')[:140]}"
                print(f"    🔴 {rec['error']}", flush=True); save(out); continue
        else:
            meta = solveconf.load_meta(f"{mesh_tag}.msh")
            rec["torch_req"] = list(torch)
        rec.pop("_err", None)
        gm = (meta.get("geometry_mm") or {}).get("groove") or [0, 0]
        rec["groove_meshed"] = list(map(float, gm))
        rec["tets"] = meta["tets"]
        if tuple(map(float, gm)) != GROOVE:
            rec["error"] = f"V2 FIRES: groove {gm} != {GROOVE}"
            print(f"    🔴 {rec['error']}", flush=True); save(out); continue
        attrs = meta["attributes"]

        c = eigen_cfg(f"{TAG}_{label}", meta, mesh=f"{mesh_tag}.msh",
                      sigma=(wall_sigma() if wall_on else None),
                      n=N_MODES, target=EIGEN_TARGET, port_bc="pec")
        c["Solver"]["Order"] = 2
        vols = sorted({v for k, v in attrs.items()
                       if isinstance(v, int) and k not in ("wall", "port")}
                      | set(attrs.get("air") or []))
        # 🔴 MATERIALS, ONE CHANNEL AT A TIME. Permittivity is MESH-BOUND
        # (check_torch_bound refuses a mismatch), so only the LOSS terms switch.
        plain = sorted(set(vols) - {attrs["plasma"], attrs["torch"]})
        mats = [{"Attributes": plain, "Permittivity": 1.0, "Permeability": 1.0}]
        mats.append({"Attributes": [attrs["torch"]], "Permittivity": torch[0],
                     "Permeability": 1.0,
                     "LossTan": (torch[1] if diel_on else 0.0)})
        mats.append({"Attributes": [attrs["plasma"]],
                     "Permittivity": (eps_p if plasma_on else 1.0),
                     "Permeability": 1.0,
                     "Conductivity": (sig_p if plasma_on else 0.0)})
        c["Domains"]["Materials"] = mats
        c["Domains"]["Postprocessing"]["Energy"] = (
            [{"Index": 1, "Attributes": [attrs["bore"]]}]
            + [{"Index": 10 + i, "Attributes": [v]} for i, v in enumerate(vols)])
        pts = [(rf * a, math.radians(pd))
               for rf in PROBE_R_FRAC for pd in PROBE_PHI_DEG]
        probe_pts = [{"r_mm": r, "phi_deg": math.degrees(p_)} for r, p_ in pts]
        c["Domains"]["Postprocessing"]["Probe"] = [
            {"Index": i + 1,
             "Center": [r * 1e-3 * math.cos(p_), r * 1e-3 * math.sin(p_), 0.0]}
            for i, (r, p_) in enumerate(pts)]
        try:
            run(f"{TAG}_{label}", c, allow_lossy_eigen=True,
                timeout=CASE_TIMEOUT_S)
        except RuntimeError as e:
            rec["error"] = str(e)[:170]
            print(f"    🔴 {rec['error']}", flush=True); save(out); continue

        modes = eigmodes.read(f"{TAG}_{label}")
        qs = {}
        for line in (pathlib.Path("postpro") / f"{TAG}_{label}" /
                     "eig.csv").read_text().splitlines()[1:]:
            pp = line.split(",")
            if len(pp) > 3:
                qs[round(float(pp[0]))] = float(pp[3])
        sec = read_sector_energy(f"{TAG}_{label}", sector_bins(meta))
        found = []
        for md in modes:
            if not (WINDOW[0] < md["f"] < WINDOW[1]):
                continue
            u = sec.get(float(md["m"]))
            if u is None and sec:
                u = sec[min(sec, key=lambda x: abs(x - md["m"]))]
            m_az, conf, harm = az_order(u) if u else (None, 0, {})
            idx = round(float(md["m"]))
            pu = purity(f"{TAG}_{label}", idx, probe_pts)
            found.append({"f_ghz": md["f"], "Q": qs.get(idx), "mode_index": idx,
                          "m_az": m_az, "A2_A0": harm.get(2, 0.0),
                          "P_min": (pu or {}).get("P_min"),
                          "spread": (pu or {}).get("spread")})
        rec["modes"] = found          # 🔴 save before labelling (§7q)
        save(out)
        if not found:
            rec["error"] = f"no modes in {WINDOW}"
            print(f"    🔴 {rec['error']}", flush=True); continue
        te = min(found, key=lambda f: abs(f["f_ghz"] - SEED_GHZ))
        rec.update(f0=te["f_ghz"], Q=te["Q"], P_min=te["P_min"],
                   spread=te["spread"])
        print(f"    f0={te['f_ghz']:.6f}  Q={te['Q']:>10,.1f}  "
              f"P>={te['P_min']:.4f}  ({len(found)} modes in window)",
              flush=True)
        save(out)

    # ---------------- THE CLOSURE
    print("\n" + "=" * 78)
    by = {c["case"]: c for c in out["cases"] if c.get("Q")}
    need = ("A_all", "B_wall", "C_plasma", "D_dielectric")
    if not all(k in by for k in need):
        missing = [k for k in need if k not in by]
        print(f"  🔴 CLOSURE CANNOT BE TESTED — missing {missing}.\n"
              f"     E3 is UNANSWERED; every eta in the record stays "
              f"unfalsified.")
        out["closure"] = f"not testable, missing {missing}"
        save(out); return

    inv = {k: 1.0 / by[k]["Q"] for k in need}
    tot, parts = inv["A_all"], inv["B_wall"] + inv["C_plasma"] + inv["D_dielectric"]
    err = abs(tot - parts) / tot
    print(f"  {'case':<14}{'Q':>13}{'1/Q':>14}{'share of 1/Q_all':>20}")
    for k in need:
        print(f"  {k:<14}{by[k]['Q']:>13,.1f}{inv[k]:>14.3e}"
              + (f"{inv[k]/tot*100:>19.2f}%" if k != "A_all" else f"{'—':>20}"))
    print(f"\n  1/Q_all      = {tot:.4e}")
    print(f"  sum of parts = {parts:.4e}")
    print(f"  discrepancy  = {err*100:.2f}%   (tolerance {CLOSURE_TOL*100:.0f}%)")
    out.update(closure_error=err, eta_wall=inv["B_wall"] / tot,
               eta_plasma=inv["C_plasma"] / tot,
               eta_dielectric=inv["D_dielectric"] / tot)

    if err <= CLOSURE_TOL:
        print("\n  ✅ **F1 DOES NOT FIRE — THE CLOSURE HOLDS.** The "
              "decomposition is valid at the\n     STRONGEST loading, so "
              "eta_plasma is a real quantity and may be quoted.")
        print(f"     eta_plasma = {out['eta_plasma']:.4f}   "
              f"eta_wall = {out['eta_wall']:.4f}   "
              f"eta_dielectric = {out['eta_dielectric']:.4f}")
        out["f1"] = "does not fire"
    else:
        print(f"\n  🔴 **F1 FIRES — THE CLOSURE FAILS BY {err*100:.1f}%.** The loss "
              f"channels are NOT\n     independent: a channel is strong enough to "
              f"redistribute the field.\n     🔴 **ONLY eta_total MAY BE QUOTED.** "
              f"Every 'eta_plasma' in the record is\n     unquotable until this is "
              f"understood.")
        out["f1"] = "FIRES"

    # V3 — a channel cannot dissipate more alone than with company
    for k in ("B_wall", "C_plasma", "D_dielectric"):
        if by[k]["Q"] < by["A_all"]["Q"]:
            print(f"  🔴 V3 FIRES: Q({k}) = {by[k]['Q']:,.0f} < Q(all) = "
                  f"{by['A_all']['Q']:,.0f} — impossible.")

    # F2 — is the dielectric really ~2%?
    ed = out["eta_dielectric"]
    print(f"\n  F2 dielectric share {ed*100:.2f}% — PLAN says '~2% of the loss "
          f"budget' "
          + ("✅ consistent" if ed <= DIEL_ALARM else
             "🔴 FIRES: the sapphire torch is a REAL loss term"))

    # F3 — the torch shift, measured
    if "E_vac_torch" in by:
        df = (by["A_all"]["f0"] - by["E_vac_torch"]["f0"]) * 1e3
        print(f"\n  🔑 THE TORCH SHIFT, MEASURED: sapphire {by['A_all']['f0']:.6f} "
              f"vs vacuum {by['E_vac_torch']['f0']:.6f}  ->  {df:+.2f} MHz")
        out["torch_shift_mhz"] = df
        if df > -3.0:
            print("  🔴 F3 FIRES — expected order -10 MHz (h4_field measured "
                  "-15.00 on a bare cavity).\n     Either the torch binding is "
                  "not reaching the solve, or that shift does not\n     transfer "
                  "to a grooved cavity. Both are findings.")
        else:
            print("  ✅ of the expected order. **Five rigs (h3_driven, "
                  "h3_groove, h3_margin,\n     h3_step3, h3_loopsize) mesh the "
                  "torch as VACUUM — their f0 is high by this\n     amount, and "
                  "every band margin derived from them is CONSERVATIVE by it.**")
    save(out)
    print(f"\n  result -> {S.outfile(SLUG, 'result.json')}", flush=True)


if __name__ == "__main__":
    main()
