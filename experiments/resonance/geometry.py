#!/usr/bin/env python3
"""
TE011 circular cavity + ICP torch — geometry for the ceramic-free,
iris-free route.

See refs/axisymmetric-feed.md. Reference geometry is a = 94.3 mm, L = 100 mm,
which puts TE011 at 2.4506 GHz analytically.

No ceramic, no iris, no coupling structure. Phase 1 solves the UNLOADED modes;
the feed is a perturbation and belongs in a driven model.

--------------------------------------------------------------------------
Why this file exists rather than reusing experiments/ignition/geometry.py:
the deliverable here is the azimuthal index m of every mode, and the ignition
harness infers m from DEGENERACY (m=0 singly, m!=0 in pairs). That fails for
this cavity, because chi'_0n == chi_1n identically, so TE0np and TM1np are
EXACTLY degenerate — a 3-fold cluster that degeneracy alone cannot untangle.

Instead the air volume is split into N azimuthal sectors as separate physical
groups. Palace integrates field energy per domain, so an m=0 mode shows equal
energy in every sector and an m!=0 mode does not. The variation survives any
rotation of a degenerate pair provided 2m is not a multiple of N, so N=5
resolves m=1..4 unambiguously — every mode in the 2-3 GHz window.
--------------------------------------------------------------------------

    python geometry.py [--out cav.msh] [--radius 94.3] [--length 100]
                       [--sectors 5] [--order 2]
"""
from __future__ import annotations

import argparse
import json
import hashlib
import math
import os
import pathlib
import shutil
import sys

_COAX_PHI = 0.0        # set by build() when a coax hole is made
_COAX_MOUTH = None     # (r_mouth, r_hole, r_inner) for the wave port
_PORT_FACE_MM = None   # set by build() when an azimuthal port face is made
import time

import gmsh

# --------------------------------------------------------------------------
# Parameters — all lengths in metres
# --------------------------------------------------------------------------
def _bind(name, allow_tentative=False):
    """A material property, bound from baselines.json. REFUSES if undeclared.

    🔑 Same contract as e0k2_anchor.wall_sigma(): bind the canonical name or
    refuse. A default that silently falls back is a constant with extra steps.
    """
    import values
    try:
        return values.get(name, allow_tentative=allow_tentative)
    except Exception as e:
        raise RuntimeError(
            f"geometry.py cannot bind {name!r} from baselines.json ({e}). "
            f"Refusing to build: an undeclared material property is how "
            f"eps=11.6 (the WRONG AXIS for sapphire) survived this whole "
            f"programme.") from None


P = dict(
    cav_r=94.3e-3,          # cavity radius   -> TE011 at 2.4506 GHz with L=100
    cav_len=100.0e-3,       # cavity length
    # R99: torch tubes. The build is ALL SAPPHIRE and PERMANENT (not a
    # swappable consumable), so sapphire is the DEFAULT — simulating quartz by
    # default would model a cavity we are not building. Quartz stays reachable
    # as --torch-material 3.78,1e-4 for the development/commissioning build.
    torch_od=20.0e-3,       # standard Fassel outer tube
    torch_wall=1.5e-3,
    inter_od=16.0e-3,       # intermediate tube; 0 disables
    inter_wall=1.0e-3,
    inter_end=-20.0e-3,     # z where it stops (absolute; mid-plane is 0)
    inj_od=5.0e-3,          # injector; 0 disables
    inj_id=2.0e-3,
    inj_end=-25.0e-3,
    # R109: rigid translation of the WHOLE model, in metres. Physics is exactly
    # invariant under it, so any change in a solved quantity is pure mesh
    # artifact. This is the microscope's "translate the slide" probe — the
    # companion to rotating it, and the ONLY one that can see an artifact
    # co-located with the symmetry axis, where our torch and plasma live.
    air_coarsen=1.0,
    offset=(0.0, 0.0, 0.0),
    # E0c: rigid ROTATION about z, radians. For an axisymmetric
    # cavity this is an exact symmetry of BOTH the physics and the
    # solid, so the OCC shape is unchanged — only its parametric
    # seam moves, and gmsh then lays out a different mesh. A purer
    # probe than translation: not even the bounding box changes.
    rotate=0.0,
    # E0d: WHICH axis to rotate about. z is the CAVITY AXIS, so a
    # z-rotation leaves the axisymmetric solid literally unchanged.
    # A TRANSVERSE rotation (x or y) tilts the cavity axis away
    # from the coordinate axis entirely — a much stronger probe,
    # because E0b showed the mesh inherits the cavity's azimuthal
    # symmetry only while those two axes coincide.
    rotate_axis=(0.0, 0.0, 1.0),
    # 🔑 BOUND, NOT LITERAL. User, 2026-08-25: "there should be absolutely no
    # constants in any scripts." A material property in a script is a value with
    # no provenance, no unit check and no retraction path — which is exactly how
    # eps = 11.6 survived being the WRONG AXIS for the whole programme.
    # ⚠️ The three material defaults below now come from baselines.json and
    # REFUSE if undeclared (the wall_sigma() pattern). The DIMENSION defaults
    # further up are still literals: they are overridden by the slug config for
    # every real run (CONVENTIONS 7ba), and they are the burn-down list.
    # 🔴🔴 THIS VALUE WAS WRONG BY THE AXIS. RESOLVED 2026-08-25.
    # Krupka, Huang & Tung, Meas. Sci. Technol. 16 (2005) 1014, figure 10:
    # "Dielectric loss tangents PERPENDICULAR TO THE ANISOTROPY AXIS ... the
    # measured permittivity was ... 9.39 +-0.5% for sapphire." Measured with
    # TE0np modes in a cylindrical sample — the SAME mode family as this cavity.
    # TE011's E is azimuthal, so with the c-axis along the tube E_phi sees
    # eps_PERP_c = 9.39, NOT 11.6. 11.6 is eps_PARALLEL_c.
    # ⚠️ R98's comment at --torch-material asserts the reverse, and R32's check
    # was CIRCULAR (see baselines.json torch.sapphire.permittivity).
    # 🔴 NOT CHANGED HERE YET: flipping it moves every stored f0, so it belongs
    # to one deliberate re-mesh with the apertures (NEXT.md restoration).
    # The canonical value is already 9.39 in baselines.json.
    torch_eps=_bind("torch.sapphire.permittivity"),
    torch_tand=_bind("torch.sapphire.loss_tangent", allow_tentative=True),
    # Coupling loop for the DRIVEN model. Rectangular, in the z=0 plane, so
    # its normal is z-hat and it links H_z -> the TE011 operating mode.
    # A series gap at the far side carries the lumped port.
    loop_d=0.0,             # radial depth (m); 0 disables the loop
    port_pw=None,           # port-face radial half-width, as a multiple of the
                            # conductor radius. In P for cache correctness.
    arc_chords=None,        # AZIMUTHAL: number of straight chords in the arc.
                            # In P so the MESH CACHE keys on it — different
                            # counts are different geometry.
    loop_strip=None,        # (axial, radial) m: rectangular conductor. The
                            # AXIAL dimension is the wide one, so the broad face
                            # is parallel to the wall. None = round wire.
    loop_hole=None,         # (r_hole, stub_len) m: COAX ENTRY. A radial
                            # clearance tube through the barrel wall at the
                            # FEED leg's azimuth. The leg passes through it as
                            # the coax inner conductor; the tube wall is the
                            # outer. None = the leg is trimmed at the wall and
                            # grounded, which is what every run before
                            # 2026-09-01 did.
    loop_azim=None,         # (h, arc LENGTH) m: AZIMUTHAL loop — an arc at
                            # r = a - h in the z=0 plane, closed to the wall by
                            # two radial legs. None = the radial loop.
    loop_w=8.5e-3,          # half-width; loop area ~ 2*w*d
    # R69: mount the loop on the -z END CAP at this radius instead of on the
    # barrel wall. 0 keeps the barrel loop, which is what every run before R69
    # used -- not by choice, but because the barrel wall is the ONLY place in
    # the barrel where E_phi = 0 and metal is legal. Both end caps are also
    # E_phi nulls (E_phi ~ sin(pi z/L)), an entire surface never used, where
    # H_r peaks at r = 0.4805a = 49.83 mm. A cap loop's normal is RADIAL, so it
    # links H_r rather than H_z, and its radius is a free variable for the
    # first time.
    loop_cap_r=0.0,
    loop_rw=1.0e-3,         # wire radius — never a filament, see ignition-study 7
    loop_gap=0.3e-3,        # series gap; must be << wire radius (see build)
    loop_phi=0.0,           # azimuthal position (rad)
    # R62: second gap in a radial leg = the SERIES capacitor. Zero disables.
    # Parallel-plate estimate C = eps0*pi*r_w^2/g gives 0.196 pF at g = 0.14 mm
    # for r_w = 1 mm, but fringing between round wire ends makes the real value
    # larger, so the gap is SWEPT and Q_ext measured rather than computed.
    loop_gap2=0.0,
    # R62: FLANGE DISCS on the capacitor gap faces. A bare 1 mm wire end at a
    # meshable 0.5 mm gap gives only ~0.056 pF (-1183 ohm), which BLOCKS the loop
    # current instead of resonating with its +332 ohm — measured: |Gamma| went
    # 0.568 -> 0.904 at a 0.15 mm bare gap, i.e. coupling got WORSE. C = eps0*A/d
    # says the fix is AREA, not a smaller gap: 0.196 pF at 0.5 mm needs ~1.9 mm
    # radius. That is also the more buildable part — holding 0.14 mm between bare
    # wire ends is a fitter's problem, a 0.5 mm gap between discs is not.
    loop_flange_r=0.0, loop_flange_t=0.3e-3,
    # Tilt about the radial axis. 0 = loop in the z=0 plane, normal z-hat,
    # links H_z -> TE011 only. 90 deg = normal phi-hat, links H_phi -> TM020
    # only. 45 deg couples to BOTH at -3 dB each, so one driven sweep yields
    # both resonances and both Q values. The port Direction must rotate with it.
    loop_tilt=0.0,          # radians
    # Radial viewport: a hole through the side wall at mid-plane, backed by a
    # below-cutoff stub. TE011's side-wall current is purely azimuthal and peaks
    # at mid-plane, so this is the worst case for it. A 15 mm bore has TE11
    # cutoff at 11.7 GHz, so at 2.45 GHz it is 4.8x below cutoff and does not
    # propagate — the Q cost is current crowding, not radiation.
    # R57/R92: viewport and trap are PART OF THE DESIGN and are now ON by
    # default. 10 mm each, sized from the spectrometer's etendue at f/15 (an
    # Echelle, the usual ICP-OES choice) over the 103.7 mm plasma-to-wall path —
    # NOT from Q, which is what produced the unjustified 25 mm.
    # ⚠️ THIS CHANGES EVERY MESH BUILT FROM NOW ON. Every result file written
    # before 2026-08-19 was built with view_d = 0 and no trap. Do not difference
    # across that boundary; the sidecar records both so it is detectable.
    view_d=10.0e-3,         # viewport diameter (m); 0 disables
    # R12: a conductive sub-region inside the bore, so the plasma can be given a
    # realistic shape instead of filling the whole bore column. Zero disables and
    # the geometry is byte-identical to before.
    pl_ri=0.0, pl_ro=0.0, pl_zlo=0.0, pl_zhi=0.0,
    # R21: capacitive ignition electrode — a conducting band around the torch OD.
    # It is a SHORTED TURN to TE011's azimuthal E, so axial position decides
    # whether it is harmless or fatal. Zero width disables.
    el_zc=0.0, el_w=0.0, el_t=1.0e-3,
    # R29: axial exhaust CHIMNEY through the +z end cap — the plume port, sized
    # below cutoff so it does not radiate (21 mm bore -> TE11 cutoff 8.4 GHz).
    # Modelled as air continuing past the cap, terminated by the same finite-
    # conductivity WALL as everything else at its far end,
    # exactly as the radial viewport stub is. Zero diameter disables.
    chim_d=0.0, chim_len=41.0e-3,
    # R49: the GAS-FEED FEEDTHROUGH on the -z cap. The torch has to penetrate
    # that cap to reach its plumbing, and until now the model ended the tube
    # flush against solid metal — the aperture did not exist at all. Unlike the
    # chimney this one is DIELECTRIC-LOADED, because the torch wall sits in it,
    # and a dielectric drops the below-cutoff frequency by ~sqrt(eps). Zero
    # diameter disables. torch_ext extends the outer tube (and the gas inside
    # it) below z0 by that distance; it requires feed_d > 0, or the tube would
    # protrude into nothing and the topological rule would clad it in metal.
    feed_d=0.0, feed_len=41.0e-3, torch_ext=0.0, torch_ext_top=0.0,
    # R54: GEOMETRIC MODE FILTER — a circumferential groove cut into each end
    # cap at the barrel corner, replacing the quartz annulus. It interrupts
    # TM111's RADIAL cap current while TE011's cap current, being purely
    # azimuthal, runs parallel to it. The corner is where discrimination is
    # perfect: TE011's cap current ∝ J1(chi'01 r/a) is ZERO at r=a by the
    # boundary condition, while TM111's ∝ J1'(chi11 r/a) is 0.40 of its maximum.
    # At mid-radius the situation inverts, which is why the groove must not go
    # there. Width is measured inward from r = a; depth is beyond the cap.
    groove_w=0.0, groove_d=0.0, tag_groove=False, plasma_sectors=False,
    view_len=25.0e-3,       # stub length, terminated by the wall (not PEC)
    # R57: the LIGHT TRAP — a second radial aperture diametrically opposite the
    # viewport. Its job is optical, not electromagnetic: it turns the far wall
    # (a concave mirror with the plasma at its centre of curvature) into a
    # controlled dark background that cannot drift. Modelled as a wall-terminated
    # below-cutoff stub like the viewport — the real termination is an external
    # absorber, but at ~108 dB of cutoff attenuation the cavity cannot tell.
    trap_d=10.0e-3, trap_len=25.0e-3, trap_phi=math.radians(288.0),
    view_phi=math.radians(108.0),   # a sector centre at N=5
    striker_h=0.0,          # annular striker ridge height (m); 0 disables
    striker_rtip=1.0e-3,    # ridge tip radius — NEVER a sharp edge, see below
    striker_r=11.0e-3,      # ridge major radius (centre of the annulus)
    # R36: deliberate bore OVALITY, a(phi) = a + ov*cos(2*phi). Machining
    # roundness is an m=2 perturbation, which is invisible to every axisymmetric
    # feature in this model and had never been simulated. Value is the PEAK
    # RADIAL DEVIATION in metres, i.e. the drawing's roundness tolerance:
    # the bore becomes an ellipse with semi-axes a+ov (x) and a-ov (y).
    # Only the cavity WALL is made oval — the torch, filter ID and loop stay
    # round, which is what a bored-and-clamped aluminium body actually does.
    ovality=0.0,
    filter_t=0.0,            # dielectric filter thickness per end cap (m)
    # 🔑 BOUND, not literal. Registered as torch.quartz.permittivity and marked
    # TENTATIVE: 3.78 is a plausible handbook value for FUSED quartz but this
    # programme has never cited one. ⚠️ Krupka et al. measure SINGLE-CRYSTAL
    # quartz at 4.43 perpendicular to the c-axis — a different material; it does
    # NOT transfer.
    filter_eps=_bind("torch.quartz.permittivity", allow_tentative=True),
    bore_h=5.0e-3,          # bore mesh size — air, so wavelength-limited
    # R15: the R12 plasma sub-region got NO explicit size — it is carved out of
    # the bore before set_pts runs, so it inherited only the background field
    # (1.5 mm near the quartz, growing to 15 mm). The RF skin depth in a sigma =
    # 30 S/m plasma at 2.45 GHz is 1.86 mm, so the loaded Q was being computed on
    # a mesh that barely resolves one skin depth. Zero follows bore_h.
    plasma_h=0.0,
    sectors=5,              # azimuthal energy sectors; 1 disables
    elems_per_wl=8.0,
)

C0 = 299_792_458.0
F0 = 2.45e9
CHI01P = 3.8317059702075125      # first root of J0'
CHI11 = 3.8317059702075125       # first root of J1 — identical, hence the
                                 # structural TE0n / TM1n degeneracy

# Physical group tags, fixed so eigenmode.json can reference them
TAG_BORE = 1
TAG_TORCH = 2            # R111: renamed from TAG_QUARTZ. The torch
                         # tubes — SAPPHIRE since R99, not quartz.
TAG_AIR0 = 3            # air sectors occupy TAG_AIR0 .. TAG_AIR0+sectors-1
TAG_FILTER = 8           # R111: renamed from TAG_BRAKE. The torch_v
                         # annulus that separates TE011 from TM111.
TAG_UPSTREAM = 11       # gas in the annular feed channels
TAG_PLASMA = 12         # R12: conductive sub-region inside the bore
TAG_PLASMA0 = 20        # R83: plasma split into ns AZIMUTHAL sectors, 20..20+ns-1,
                        # so the uniformity of POWER DEPOSITION around the torus
                        # can be measured. The whole C1 criterion was a
                        # whole-cavity, cold, stored-energy proxy for this.
                        # Only with --plasma-sectors; otherwise the plasma stays
                        # one volume on TAG_PLASMA and nothing existing moves.
TAG_GAP = 14            # 🔑 2026-08-26: the SERIES-GAP region as its own
                        # volume, so domain-E reports the energy stored IN the
                        # gap. The 27x coupling lever is not understood -- R62's
                        # series-LC model predicted the OPPOSITE sign and a
                        # refit was retracted at 44% residual -- and "electric
                        # or magnetic coupling" is a statement about an ENERGY
                        # SPLIT that nothing currently measures.
TAG_GROOVE = 13         # R81: the corner groove as its OWN volume, so the
                        # fraction of a mode's energy INSIDE the slot can be
                        # measured instead of inferred. Only with --tag-groove;
                        # without it the groove is fused into the air wedges
                        # exactly as before and no existing result moves.
# R111: renamed from TAG_PEC. Nothing here is a perfect conductor. Attribute 90
# carries Palace's finite CONDUCTIVITY boundary — real metal with a real skin
# depth — on every exterior surface: cavity wall, end caps, and the walls and far
# ends of the viewport, light trap, chimney and feed. The metal is bound from
# baselines (`wall.conductivity`, aluminium 3.5e7), not from the config template.
TAG_WALL = 90
TAG_PORT = 91          # lumped-port face in the loop gap (internal)
TAG_LOOP = 92          # the coupling loop's own surface — COPPER, not the
#                        wall's aluminium, and its own attribute so its loss can
#                        be separated. Before 2026-08-27 the wire's surface was
#                        swept into TAG_WALL by the topological rule below (it is
#                        an exterior face like any other), so the coupler was
#                        modelled as ALUMINIUM and its dissipation was
#                        indistinguishable from the cavity's.


def mesh_size(eps_r: float, f: float, n: float) -> float:
    return C0 / (f * math.sqrt(eps_r)) / n


def f_te011(a: float, L: float) -> float:
    return C0 / (2 * math.pi) * math.sqrt((CHI01P / a) ** 2 + (math.pi / L) ** 2)


def build(p: dict, out: str, msh_order: int) -> None:
    gmsh.initialize()
    # Meshing threads. DEFAULT 1 — deliberately, so every mesh ever built by
    # this file still reproduces byte for byte. gmsh here IS built with OpenMP
    # (General.BuildOptions lists it), so this option is live, not inert. But
    # Mesh.Algorithm3D is 1 (Delaunay), which is largely serial; the threaded
    # win is in 1D/2D and in the order-2 HighOrderOptimize pass below. Raising
    # it is only legitimate once ops/gmshcaps.sh has shown the output is still
    # deterministic at that thread count — a non-reproducible mesh would break
    # the same-mesh rule that the whole error budget rests on (METHODOLOGY 2b).
    gmsh.option.setNumber("General.NumThreads", max(1, int(p.get("threads", 1))))
    gmsh.model.add("te011_cavity")
    occ = gmsh.model.occ

    a = p["cav_r"]
    L = p["cav_len"]
    z0 = -L / 2.0
    ns = max(1, int(p["sectors"]))

    t_ro = p["torch_od"] / 2.0
    t_ri = t_ro - p["torch_wall"]

    # Cavity air as ns azimuthal wedges, each ANNULAR — the torch core is
    # punched out before sectoring.
    #
    # Sectoring the full disc instead put all ns wedge planes through the axis,
    # slicing the 1.5 mm quartz shell and meeting in a line at r=0. That
    # produced a sliver element at minSICN 1.5e-5: positive, so it passes an
    # "inverted?" test, but degenerate enough to wreck the conditioning of the
    # eigensolve. The sectors only ever needed to partition the AIR, so the
    # core is left whole and the pathology disappears.
    # R36 ovality: an ANISOTROPIC DILATION about the axis, applied to the wedge
    # while it is still a plain cylinder and BEFORE the torch bore is punched.
    # Order matters — dilating afterwards would make the torch hole elliptical
    # too, which is not the part being toleranced.
    ov = p.get("ovality", 0.0)
    sx, sy = (1.0 + ov / a, 1.0 - ov / a) if ov else (1.0, 1.0)

    def ovalise(dts):
        if ov:
            occ.dilate(dts, 0, 0, 0, sx, sy, 1.0)

    wedges = []
    for k in range(ns):
        w = occ.addCylinder(0, 0, z0, 0, 0, L, a, angle=2 * math.pi / ns)
        if k:
            occ.rotate([(3, w)], 0, 0, 0, 0, 0, 1, k * 2 * math.pi / ns)
        ovalise([(3, w)])
        hole = occ.addCylinder(0, 0, z0, 0, 0, L, t_ro)
        # NB: do not name this `out` — that shadows the output filename
        # parameter, and gmsh.write() then fails 150 lines later with an
        # AttributeError that looks nothing like its cause.
        annulus, _ = occ.cut([(3, w)], [(3, hole)],
                             removeObject=True, removeTool=True)
        if len(annulus) != 1:
            sys.exit(f"ERROR: wedge {k} cut produced {len(annulus)} volumes")
        wedges.append(annulus[0])

    # Optional dielectric BRAKE — an annulus lying flat against each end cap.
    #
    # Not a resonator: it has no in-band resonance of its own and does not
    # generate the plasma. Its only job is to split the TE0np / TM1np
    # degeneracy, which it can do because the two modes have opposite field
    # structure at the end plane:
    #
    #   every TE mode   transverse E ~ sin(p*pi*z/L)  ->  ZERO on both caps
    #   every TM_mn1    E_z          ~ cos(p*pi*z/L)  ->  MAXIMUM on both caps
    #
    # So it pulls the whole TM family down and leaves the whole TE family
    # alone, and because TE011's E vanishes there it adds almost no loss to
    # the mode being kept. Being a full annulus it is rotationally symmetric,
    # so unlike an iris it introduces no azimuthal mixing.
    tb = p["filter_t"]
    filters = []
    if tb > 0:
        for zb in (z0, z0 + L - tb):
            o = occ.addCylinder(0, 0, zb, 0, 0, tb, a)
            ovalise([(3, o)])       # filter OD follows the bore; its ID stays round
            i = occ.addCylinder(0, 0, zb, 0, 0, tb, t_ro)
            cut, _ = occ.cut([(3, o)], [(3, i)],
                             removeObject=True, removeTool=True)
            filters.extend(cut)

    # Optional annular STRIKER ridge on the -z end cap.
    #
    # Metal cannot touch the bore gas: it is enclosed by the quartz torch, and
    # anything inside the torch is in the sample path, where erosion becomes
    # permanent spectral background. The ridge therefore lives OUTSIDE the
    # torch, exploiting the fact that TM020's E_z is TANGENTIAL to the torch
    # wall and so continuous across it — an enhancement raised just outside
    # appears just inside.
    #
    # Rounded top, never a sharp edge: ignition-study.md 7 warns that sharp
    # corners give spuriously unbounded field and simulate an ignition that
    # does not exist. Enhancement and reach trade directly, beta ~ 1 + h/r_tip
    # with the perturbation decaying over ~r_tip.
    sh, srt, srr = p["striker_h"], p["striker_rtip"], p["striker_r"]
    if sh > 0:
        body = None
        if sh > srt:
            bo = occ.addCylinder(0, 0, z0, 0, 0, sh - srt, srr + srt)
            bi = occ.addCylinder(0, 0, z0, 0, 0, sh - srt, srr - srt)
            body, _ = occ.cut([(3, bo)], [(3, bi)],
                              removeObject=True, removeTool=True)
        tor = occ.addTorus(0, 0, z0 + sh - srt, srr, srt)
        striker = occ.fuse(body, [(3, tor)])[0] if body else [(3, tor)]
        # Cut the ridge OUT of the air, then delete it. The resulting void has
        # a single adjacent volume per face, so the topological rule below
        # tags it as WALL (finite conductivity) automatically.
        cut_wedges = []
        for wdg in wedges:
            res, _ = occ.cut([wdg], striker,
                             removeObject=True, removeTool=False)
            cut_wedges.extend(res)
        if len(cut_wedges) != len(wedges):
            sys.exit(f"ERROR: striker cut split a wedge "
                     f"({len(wedges)} -> {len(cut_wedges)})")
        wedges = cut_wedges
        occ.remove(striker, recursive=True)

    # --- coupling loop + lumped port face --------------------------------
    # Built as a U in the z=0 plane: two radial legs into the cavity joined by
    # a crossbar, closed through the wall. A gap at the crossbar mid-span holds
    # the port. Palace allows lumped ports on INTERNAL boundaries, so the port
    # is just an embedded face in the gap — no coax transition needed.
    ld, lw, lrw, lg = p["loop_d"], p["loop_w"], p["loop_rw"], p["loop_gap"]
    lcr = p["loop_cap_r"]
    port_face = None
    gap2_centre = None
    port_centre = None
    # 🔑 STANDOFF -> CENTRELINE, HERE, where the cross-section is known.
    # The INPUT is the stud height (the wall gap); the conductor grows AWAY
    # from the wall, so the gap is invariant under thickness. Everything
    # downstream still speaks centreline, so this is the only conversion.
    _sto = p.get("loop_azim_standoff")
    if _sto:
        _st = p.get("loop_strip")
        _thalf = (_st[1] / 2.0) if _st else p["loop_rw"]
        p["loop_azim"] = (float(_sto[0]) + _thalf, float(_sto[1]))
    _azim = p.get("loop_azim")
    if _azim:
        # --- AZIMUTHAL loop, 2026-08-29 ------------------------------------
        # An ARC at r = a - h in the z = 0 plane, spanning `arc` radians about
        # loop_phi, closed to the wall by two RADIAL legs. The port gap sits at
        # the arc's mid-span.
        #
        # 🔑 WHY IT IS NOT JUST ANOTHER SHAPE. For TE011 a magnetic coupler must
        # link H_z, so its area lies in the r-phi plane either way — but the
        # radial loop spans a range of r at fixed phi, sampling H_z across the
        # J0 profile and running its LEGS ACROSS the wall current
        # (K = n x H = H_z phi-hat). This one spans a range of PHI at fixed r,
        # and TE011 is m = 0, so its whole area sits at ONE value of H_z, the
        # near-maximum next to the wall, with its conductor running ALONG the
        # wall current the way the annular groove does.
        # ⚠️ It also sits hard against a conducting boundary, so its own
        # self-inductance is image-loaded — and Q_ext goes as the coupling
        # coefficient M/sqrt(L1*L2), not as M alone. Nothing measured so far
        # prices that, which is exactly why h is the axis to sweep.
        #
        # 🔴 NO SERIES CAPACITOR HERE (user, 2026-08-29). The conductor-to-wall
        # gap IS a capacitance that varies with h, so adding a lumped series gap
        # would confound the axis being swept. That same gap is also the ARC
        # RISK: it narrows as h does, and h - lrw is the clearance to probe.
        _h, _arclen = float(_azim[0]), float(_azim[1])
        _strip = p.get("loop_strip")          # (axial, radial) or None
        if lcr > 0:
            sys.exit("ERROR: --loop-azim and --loop-cap are different mounts")
        if p["loop_gap2"] > 0:
            sys.exit("ERROR: --loop-gap2 with --loop-azim — the wall gap is "
                     "already a capacitance that varies with h; a second one "
                     "confounds the axis being swept")
        _R = a - _h
        _thalf = (_strip[1] / 2.0) if _strip else lrw
        _clear = _h - _thalf
        if _R <= _thalf or _clear <= 0:
            sys.exit(f"ERROR: standoff {_clear*1e3:.3f} mm leaves the conductor "
                     f"touching or inside the wall (centreline {_h*1e3:.2f} mm, "
                     f"conductor half-extent {_thalf*1e3:.2f} mm)")
        print(f"  AZIM: standoff {_clear*1e3:.3f} mm (the WALL GAP) + conductor "
              f"half-extent {_thalf*1e3:.3f} mm -> centreline {_h*1e3:.3f} mm",
              flush=True)
        # 🔑 ARC LENGTH -> ANGLE HERE, not in the caller. The angle depends on
        # R = a - h, so specifying an ANGLE would couple h and L; specifying a
        # LENGTH keeps them independent, which is the point of the sweep.
        _psi = lg / (2.0 * _R)              # half-angle of the port gap
        _th = _arclen / (2.0 * _R)          # half-angle of the whole arc
        if _th <= _psi:
            sys.exit(f"ERROR: --loop-azim arc {_arclen*1e3:.2f} mm is not "
                     f"longer than its own port gap {lg*1e3:.2f} mm")
        if _strip and _arclen < _strip[0]:
            sys.exit(f"ERROR: arc {_arclen*1e3:.2f} mm is SHORTER than the "
                     f"strip is wide ({_strip[0]*1e3:.2f} mm) — that is not an "
                     f"arc, it is a stub, and the two are not comparable")
        segs = []
        _out = _h + 2.0e-3          # legs reach outside; the cut trims them

        # 🔴 TORUS ARC + ANGULAR GAP — the only construction measured to
        # produce a VALID mesh. The alternatives, and why they are not here:
        #   · torus + FLAT SLAB gap: flat faces meeting a curved tube produced
        #     inverted order-2 elements (ScaledJac -1.6) and the high-order
        #     optimiser ground indefinitely.
        #   · POLYLINE chords + flat slab: completed, but Palace/MFEM refused
        #     the result outright — "MFEM abort: STable3D::operator()" — on BOTH
        #     port BCs, so the mesh itself was malformed.
        # ⚠️ I changed the ARC and the GAP at the same time and then chased
        # failures across both for hours. One variable at a time.
        # 🔴 KNOWN LIMITATION: the gap faces are planes at +-psi, so the port
        # face spanning them is an annular SECTOR, and Palace's lumped port
        # requires a FLAT element ("bounding box discovered length should match
        # projected length"). pec solves; lumped does not. Q_ext therefore
        # needs the port face fixed — that is the open problem, on a mesh that
        # is otherwise known good.
        def _arc_seg(angle):
            """One arc segment spanning [0, angle], round wire or strip."""
            if not _strip:
                return (3, occ.addTorus(0.0, 0.0, 0.0, _R, lrw, -1, angle))
            _w, _t = _strip                    # axial (wide), radial (thin)
            _r = occ.addRectangle(_R - _t / 2.0, -_w / 2.0, 0.0, _t, _w)
            occ.rotate([(2, _r)], 0, 0, 0, 1, 0, 0, math.pi / 2.0)
            _rev = occ.revolve([(2, _r)], 0, 0, 0, 0, 0, 1, angle)
            return next((d, t) for d, t in _rev if d == 3)

        def _leg(ang, extra=0.0):
            """One radial leg at azimuth `ang`, round wire or strip.

            `extra` lengthens it OUTWARD so a feed leg can run through a coax
            clearance tube instead of being trimmed at the wall."""
            # 🔴 START THE LEG *INSIDE* THE ARC, not on its centreline.
            # Butting them at r = R makes the two solids meet TANGENTIALLY, and
            # tangent contacts are where OCC's booleans go marginal: removing
            # the fuse fixed h = 3 mm and broke h = 5 mm, the failure simply
            # MOVING rather than going away. Overlapping by one conductor
            # radius makes the intersection transverse and the boolean robust.
            # 🔴 OVERLAP RADIALLY, so use the RADIAL dimension. This was
            # max(_strip), which for a 5x1 strip is the AXIAL 5 mm — the legs
            # then jutted 5 mm inward past the arc, adding conductor that is
            # not part of the loop (measured: 323 mm^2 of surface where the
            # design demands 225). The arc is only _strip[1] thick radially, so
            # that much overlap penetrates it fully and no more.
            _ov = (_strip[1] if _strip else lrw)
            _r0 = _R - _ov
            _reach = _out + _ov + extra
            if not _strip:
                return (3, occ.addCylinder(
                    _r0 * math.cos(ang), _r0 * math.sin(ang), 0.0,
                    _reach * math.cos(ang),
                    _reach * math.sin(ang), 0.0, lrw))
            _w, _t = _strip
            _b = occ.addBox(_r0, -_t / 2.0, -_w / 2.0, _reach, _t, _w)
            occ.rotate([(3, _b)], 0, 0, 0, 0, 0, 1, ang)
            return (3, _b)

        # 🔴 THE GAP IS A FLAT SLOT, NOT AN ANGULAR SECTOR — and it has to be.
        # First version built two arc segments ending at +-psi, so the gap faces
        # were planes normal to phi-hat at two DIFFERENT angles and the port
        # face had to be an annular sector to match them. Palace then refused
        # the lumped port:
        #   Verification failed: bounding box length 1.5518e-03 should match
        #   projected length 1.5357e-03  (palace::UniformElementData)
        # — a lumped port element must be FLAT, and a curved one is 1.05% out.
        # ✅ Build the arc whole and cut a PARALLEL-SIDED slab out of it at
        # phi = 0. The gap faces are then parallel planes, a flat rectangle
        # spans them exactly, and it is also how a real gap would be machined.
        for _sgn in (+1.0, -1.0):
            _seg = _arc_seg(_th - _psi)
            occ.rotate([_seg], 0, 0, 0, 0, 0, 1, _psi if _sgn > 0 else -_th)
            segs.append(_seg)
        if lg <= 0:
            # 🔑 ONE ARC, NOT TWO HALVES FUSED. With no gap the two halves meet
            # exactly at phi = 0 and the fuse leaves a degenerate seam there:
            # gmsh's high-order optimiser then grinds with rel decr ~0.999 and
            # never converges (measured 2026-08-31, two size factors). Build
            # the whole arc as a single solid instead — there is no gap to cut.
            for _d, _t2 in segs:
                occ.remove([(_d, _t2)], recursive=True)
            segs = [_arc_seg(2.0 * _th)]
            occ.rotate(segs, 0, 0, 0, 0, 0, 1, -_th)
        # 🔑 COAX ENTRY. Without a hole BOTH legs are trimmed at the wall and
        # grounded, and the loop is driven at a mid-arc gap — the topology
        # every run before 2026-09-01 used. With a hole, the FEED leg (-theta)
        # runs on through a radial clearance tube as the coax INNER conductor
        # and the tube wall is the OUTER. Same circuit class either way (a
        # series-fed loop returning through the wall); it moves the source
        # ~26 deg around a lambda/6.8 loop, and puts the port reference plane
        # AT THE WALL where VSWR is actually measured.
        _hole = p.get("loop_hole")
        _feed_ang = -_th                     # the leg that goes through
        for _sgn in (+1.0, -1.0):
            if _hole and _sgn < 0:
                _rh, _stub = _hole
                if _rh <= (_strip[1] / 2.0 if _strip else lrw):
                    sys.exit(f"ERROR: --loop-hole radius {_rh*1e3:.2f} mm does "
                             f"not clear the conductor "
                             f"{(_strip[1]/2 if _strip else lrw)*1e3:.2f} mm — "
                             f"the inner conductor would short to the tube.")
                segs.append(_leg(_sgn * _th, extra=_stub + 1.0e-3))
            else:
                segs.append(_leg(_sgn * _th))

        if p["loop_phi"]:
            occ.rotate(segs, 0, 0, 0, 0, 0, 1, p["loop_phi"])

        if _hole:
            # the tube is VACUUM: it EXTENDS the domain outward through the
            # wall, so it is FUSED into the wedge that contains it, not cut.
            _rh, _stub = _hole
            _ha = (p["loop_phi"] + _feed_ang) % (2.0 * math.pi)
            _wsp = 2.0 * math.pi / ns
            _k = int(_ha / _wsp)
            # 🔴 REFUSE a tube straddling a sector boundary: it would have to be
            # fused into two wedges and OCC leaves a non-manifold seam there
            # (the chimney/feed hazard, CONVENTIONS 7bn).
            _margin = math.asin(min(1.0, _rh / a)) * 1.5
            _off = _ha - _k * _wsp
            if _off < _margin or (_wsp - _off) < _margin:
                sys.exit(f"ERROR: --loop-hole at phi={math.degrees(_ha):.2f} deg "
                         f"is within {math.degrees(_margin):.2f} deg of a sector "
                         f"boundary ({ns} sectors). Rotate with --loop-phi.")
            _r0 = a - 1.5e-3                 # start INSIDE so the fuse is transverse
            _len = _stub + 1.5e-3
            _tube = occ.addCylinder(_r0 * math.cos(_ha), _r0 * math.sin(_ha), 0.0,
                                    _len * math.cos(_ha), _len * math.sin(_ha),
                                    0.0, _rh)
            _fused, _ = occ.fuse([wedges[_k]], [(3, _tube)],
                                 removeObject=True, removeTool=True)
            if len(_fused) != 1:
                sys.exit(f"ERROR: coax tube fused into {len(_fused)} solids, "
                         f"expected 1 — the wedge is no longer simply connected.")
            wedges[_k] = _fused[0]
            globals()["_COAX_PHI"] = _ha
            print(f"  COAX HOLE: r={_rh*1e3:.2f} mm, stub {_stub*1e3:.2f} mm "
                  f"outside the wall at phi={math.degrees(_ha):.2f} deg "
                  f"(sector {_k} of {ns}); feed leg runs through it",
                  flush=True)
            # 🔑 THE PORT MOVES TO THE COAX MOUTH. An annulus at the stub's
            # outer end, inner conductor (the leg) to outer (the tube). This
            # puts the reference plane AT THE WALL, which is where VSWR is
            # actually measured — the mid-arc gap referenced it to a plane
            # floating inside the cavity.
            # 🔴 A LUMPED PORT CANNOT DESCRIBE THIS. Palace's cylindrical
            # coordinate system is about the GLOBAL z axis (configfile.cpp
            # ParseStringAsDirection: 'r' -> CYLINDRICAL), but this coax enters
            # through the BARREL, so its inner->outer field lies in the
            # theta-z plane. Use a WAVE PORT, which solves the port's own modal
            # field and needs no direction. Driven only — wave ports are
            # frequency-dependent, so Q0 still comes from eigen with this face
            # shorted (port_bc="pec").
            if lg > 0:
                sys.exit("ERROR: --loop-hole drives at the coax mouth, so the "
                         "arc must be CONTINUOUS. Pass gap=0 in --loop "
                         "(a mid-arc gap AND a coax feed is two drives).")
            # 🔴 DO NOT INSERT A FACE HERE. The stub mouth is ALREADY a
            # boundary of the domain; adding a coincident annulus as a fragment
            # tool gave Palace
            #   Verification failed: ((e1 >= 0 && e2 >= 0) ||
            #                         face_to_be.find(f) == face_to_be.end())
            # — a face marked as a boundary element that is not one. A LUMPED
            # port wants an INTERIOR face bridging a gap, so inserting is right
            # there; a WAVE port wants the domain's real EXTERIOR boundary, so
            # it must be IDENTIFIED among the exterior faces, like wall and
            # loop already are. Done below, after the boolean settles.
            _rin = (_strip[1] / 2.0) if _strip else lrw
            globals()["_PORT_FACE_MM"] = [2 * _rh * 1e3, 2 * _rin * 1e3]
            globals()["_COAX_MOUTH"] = (a + _stub, _rh, _rin)
            # 🔑 NO FRAGMENT TOOL for a coax port — the mouth is identified
            # among the exterior faces further down. `pf` must still be BOUND,
            # because `port_face = pf` runs unconditionally below and neither
            # the `lg > 0` branch nor the `elif not _hole` branch fires here.
            pf = None
            print(f"  COAX PORT: annulus at r={(a+_stub)*1e3:.2f} mm, "
                  f"inner {_rin*1e3:.2f} -> outer {_rh*1e3:.2f} mm "
                  f"(Z0 = {59.96*math.log(_rh/_rin):.1f} ohm in air). "
                  f"⚠️ WAVE PORT only — a lumped port cannot orient this.",
                  flush=True)
        cut_w = []
        for wdg in wedges:
            res, _ = occ.cut([wdg], segs, removeObject=True, removeTool=False)
            cut_w.extend(res)
        wedges = cut_w
        occ.remove(segs, recursive=True)
        # 🔴 THE PORT FACE MUST BE AN ANNULAR SECTOR, NOT A RECTANGLE.
        # First attempt reused the barrel's flat rectangle with xi -> R. The
        # barrel's gap is a STRAIGHT segment, so a rectangle spans it exactly;
        # this gap is an ARC, whose end caps are planes normal to phi-hat at
        # +-psi. A flat rectangle's edges cut through those caps — tilted only
        # ~0.1 deg, but enough to fragment the face into FOUR slivers and hand
        # tetgen a self-intersecting complex:
        #     port face(s) [338, 339, 496, 497]   (should be ONE)
        #     Error: PLC Error: A segment and a facet intersect at point
        # It failed at h = 12, 8, 5 and 2 mm and survived at 3 mm, which was
        # luck on marginal geometry, not correctness.
        # ✅ Sweep a RADIAL SEGMENT through the gap angle instead, so the face
        # is the gap, exactly, by construction.
        # ✅ FLAT rectangle spanning the flat slot, exactly as the barrel loop
        # does — same construction, same "+Y" Direction, and phi-hat is along
        # the conductor here just as it is along the barrel's crossbar.
        # 🔴 THE PORT FACE MUST BE FLAT, AND NO SECTOR WIDTH WILL DO.
        # Palace's lumped element compares its bounding-box length against its
        # projection. For an annular sector the mismatch is
        #     (2*pw*rc * 2psi) / (R * 2psi) = 2*pw*rc / R
        # — independent of the gap. MEASURED: 1.048% at pw = 0.9, and 0.249% at
        # pw = 0.2125, i.e. exactly proportional. BOTH REJECTED, so the
        # tolerance is tighter than 0.25% and reaching ~0.1% would need a face
        # 42 um wide on a 2 mm conductor. The sector is out.
        # ✅ FLAT rectangle instead, inset to the INNER radius's offset so it
        # never overhangs the conductor's angular end faces. The first flat
        # attempt used lg/2 at the mean radius and overhung by ~1.6 um at the
        # outer edge — slivers, and a PLC self-intersection. Inset it and the
        # worst case is being ~3 um SHORT at the outer edge, ~1% of the gap.
        # ⚠️ e0k2_anchor warns that a face inset by 2% "floats, drives nothing
        # and S11 comes back varying 0.036 dB with no error raised". 1% is
        # inside that, but it is the thing to check first if S11 looks flat.
        # 🔴 HALF-EXTENT IN BOTH BRANCHES. This was `_strip[1]` — the strip's
        # FULL radial thickness — beside `lrw`, a wire RADIUS. Same factor,
        # different quantity: the wire's face landed at 0.9x its half-extent
        # (inside) and EVERY strip's at 1.8x (overshooting into vacuum).
        # MEASURED 2026-08-30, strip 5x1, standoff 2.0, arc 12.24, face
        # half-width as a multiple of the conductor's half-extent:
        #     1.8x (overshoot) -> Q_L 29,465 -> beta 0.487
        #     0.9x (inside)    -> Q_L 13,826 -> beta 2.169
        #     0.4x (inside)    -> Q_L 11,508 -> beta 2.807
        # 4.5x across the overshoot boundary, 1.29x well inside it. The
        # overshoot is the artefact; it made strips look ~8x weaker than wires
        # when the matched-face figure is ~1.7x.
        _rc_p = ((_strip[1] / 2.0) if _strip else lrw)   # conductor half-extent
        _pw = (p.get("port_pw") or 0.9) * _rc_p
        # 🔑 FAIL-CLOSED ON OVERSHOOT. A face wider than the conductor drives
        # vacuum and silently dilutes the coupling — no warning, plausible
        # numbers, self-consistent across a whole sweep. This guard is the one
        # that would have caught it.
        if _pw > _rc_p * 1.0000001:
            sys.exit(f"ERROR: port face half-width {_pw*1e3:.4f} mm exceeds the "
                     f"conductor half-extent {_rc_p*1e3:.4f} mm. The face would "
                     f"drive VACUUM beyond the conductor, which dilutes Q_ext "
                     f"without any error being raised (measured 4.5x in beta). "
                     f"Use port_pw <= 1.0.")
        # 🔑 gap = 0 MEANS NO PORT — A CLOSED RING. Asked for 2026-08-31 when
        # the question became "what are Q0 and f0 of the LOADED cavity with an
        # azimuthal loop in it", not "what is beta". With no gap there is no
        # port face, no feed topology to choose, no coupling branch to resolve
        # and no face-width sensitivity: the loop is simply a conductor the
        # mode has to live with. eigen_cfg(port_bc=None) is then legal, because
        # the mesh carries no port attribute.
        # ⚠️ _psi = lg/(2R) is 0 here, so the old code built a ZERO-HEIGHT
        # rectangle — a degenerate face, not an absent one.
        if lg > 0:
            _half = (_R - _pw) * _psi      # inner-radius offset: never overhangs
            pf = occ.addRectangle(_R - _pw, -_half, 0.0, 2.0 * _pw, 2.0 * _half)
            globals()["_PORT_FACE_MM"] = [2 * _pw * 1e3, 2 * _half * 1e3]
            print(f"  PORT face: FLAT, {2*_pw*1e3:.2f} x {2*_half*1e3:.4f} mm, "
                  f"inset {(_R*_psi - _half)*1e6:.2f} um at the outer edge "
                  f"({100*(_R*_psi - _half)/(lg/2):.1f}% of the half-gap)",
                  flush=True)
            if p["loop_phi"]:
                occ.rotate([(2, pf)], 0, 0, 0, 0, 0, 1, p["loop_phi"])
        elif not _hole:
            pf = None
            globals()["_PORT_FACE_MM"] = None
            print("  AZIM: loop_gap = 0 — CLOSED RING, no port face, no port "
                  "attribute. Use eigen port_bc=None.", flush=True)
        # 🔴 else: a COAX HOLE already built the port face (an annulus at the
        # stub mouth) further up, and `pf` must survive. Without this guard the
        # `lg == 0` branch nulled it, `port_face = pf` below took None, and the
        # mesh came out with NO PORT — while still reporting
        # surface_attributes ['wall','port','loop'], so it looked fine.
        port_face = pf
        _c, _s = math.cos(p["loop_phi"]), math.sin(p["loop_phi"])
        port_centre = (_R * _c, _R * _s, 0.0)
    elif ld > 0 and lcr > 0:
        # --- R69: CAP-MOUNTED loop -----------------------------------------
        # The same U, rotated so its normal is RADIAL: two AXIAL legs at
        # (x = lcr, y = +/-lw) rising from just outside the -z cap to a depth
        # ld inside it, joined by a crossbar along y carrying the port gap.
        #
        # 🔢 Linking H_r rather than H_z is the point. On the cap H_r peaks at
        # r = 0.4805a and is 1.39x the |H_z| a barrel loop sees at the wall
        # (1.93x in coupled power); more importantly the RADIUS is free, which
        # it never is on the barrel.
        #
        # ⚠️ z INCREASES along these legs (zo = z0 - 2 mm outside, zi = z0 + ld
        # inside), the opposite of the barrel loop where x DECREASES. That sign
        # is what R62 got wrong and spent two runs on, so the series-capacitor
        # split is simply refused here rather than re-derived.
        if p["loop_gap2"] > 0:
            sys.exit("ERROR: --loop-gap2 is not supported with --loop-cap "
                     "(R62 closed the series-capacitor route; the leg-split "
                     "sign convention differs and is not worth re-deriving)")
        if p["loop_tilt"]:
            sys.exit("ERROR: --loop-tilt is meaningless with --loop-cap: tilt "
                     "rotates about the radial axis, which is the cap loop's "
                     "own normal")
        if lcr + lrw >= a:
            sys.exit(f"ERROR: --loop-cap {lcr*1e3:.1f} mm + wire radius "
                     f"reaches the barrel at a = {a*1e3:.1f} mm")
        zo, zi = z0 - 2.0e-3, z0 + ld        # start outside the cap; cut trims it
        segs = [(3, occ.addCylinder(lcr, yy, zo, 0, 0, zi - zo, lrw))
                for yy in (-lw, +lw)]
        segs.append((3, occ.addCylinder(lcr, -lw, zi, 0, lw - lg / 2, 0, lrw)))
        segs.append((3, occ.addCylinder(lcr, lg / 2, zi, 0, lw - lg / 2, 0, lrw)))
        wire = occ.fuse([segs[0]], segs[1:])[0]
        if p["loop_phi"]:
            occ.rotate(wire, 0, 0, 0, 0, 0, 1, p["loop_phi"])
        cut_w = []
        for wdg in wedges:
            res, _ = occ.cut([wdg], wire, removeObject=True, removeTool=False)
            cut_w.extend(res)
        wedges = cut_w
        # ⚠️ THE CAP LOOP AND THE MODE FILTER COMPETE FOR THE SAME SURFACE.
        # The filter is a full quartz annulus lying FLAT against each end cap,
        # r = t_ro..a, tb thick — so a loop rising from z0 to z0+ld passes
        # straight THROUGH it. Cutting the wire from the air wedges alone left
        # wire and quartz as overlapping solids, and gmsh ground for >10 min on
        # a mesh that normally takes 40 s, with no error raised.
        #
        # Physically this is a clearance hole through the quartz for each leg,
        # which is buildable but is a real design interaction: R69's cap route
        # REQUIRES modifying the mode filter, and R71 may call for a THICKER
        # filter, which makes the penetration deeper.
        cut_b = []
        for br in filters:
            res, _ = occ.cut([br], wire, removeObject=True, removeTool=False)
            cut_b.extend(res)
        if filters and not cut_b:
            sys.exit("ERROR: cap loop cut removed the mode filter entirely")
        filters = cut_b
        occ.remove(wire, recursive=True)
        # Port face: same construction as the barrel loop -- a thin rectangle
        # in a z = const plane spanning the gap along y, so "Direction" is +Y
        # and lies IN the surface as Palace requires. It must TOUCH both
        # conductor ends; inset even 2% and it floats and drives nothing.
        pf = occ.addRectangle(lcr - 0.9 * lrw, -lg / 2, zi, 1.8 * lrw, lg)
        if p["loop_phi"]:
            occ.rotate([(2, pf)], 0, 0, 0, 0, 0, 1, p["loop_phi"])
        port_face = pf
        # R112: the PORT gap needs the same refinement R62 gave the SERIES gap.
        # Rectangle centre is (lcr, 0, zi) before the phi rotation.
        _c, _s = math.cos(p["loop_phi"]), math.sin(p["loop_phi"])
        port_centre = (lcr * _c, lcr * _s, zi)
    elif ld > 0:
        xo, xi = a + 2.0e-3, a - ld          # start outside the wall; the cut trims it
        segs = []
        # R62: an optional SECOND GAP in one radial leg — the SERIES capacitor.
        #
        # The design specifies "loop + series C", and the coupler section
        # computes that 0.196 pF cancels the loop's 332 ohm self-reactance,
        # raising coupled power ~45x and taking Q_ext from 14,442 to ~320 —
        # exactly what R56 measured as the requirement for matching a lit
        # plasma. It had never been simulated: Palace's lumped-port R and C are
        # in PARALLEL, so setting C on the port does not create a series
        # element. A true series capacitor is a break in the conductor.
        #
        # It goes in a LEG, not the crossbar: the crossbar already carries the
        # port gap, and two gaps in one segment would put port and capacitor in
        # series with each other rather than the capacitor in series with the
        # loop.
        g2 = p["loop_gap2"]
        for yy in (-lw, +lw):                # radial legs
            if g2 > 0 and yy < 0:            # break the -y leg only
                xm = (xo + xi) / 2.0
                gap2_centre = (xm, yy, 0.0)
                # ⚠️ x DECREASES along the leg (xo = a+2 mm outside the wall,
                # xi = a-ld inside), so the outer piece must end at the HIGHER
                # x of the gap and the inner piece start at the LOWER one.
                # Getting this backwards makes the two pieces OVERLAP by exactly
                # g2 instead of separating — the conductor stays continuous, the
                # PEC surface count is unchanged, and Q_ext does not move. That
                # is what attempt 2 measured.
                segs.append((3, occ.addCylinder(xo, yy, 0,
                                                (xm + g2 / 2) - xo, 0, 0, lrw)))
                segs.append((3, occ.addCylinder(xm - g2 / 2, yy, 0,
                                                xi - (xm - g2 / 2), 0, 0, lrw)))
                fr, ft = p["loop_flange_r"], p["loop_flange_t"]
                if fr > lrw:
                    # discs on the two facing ends, extending INTO each piece
                    segs.append((3, occ.addCylinder(xm + g2 / 2, yy, 0,
                                                    ft, 0, 0, fr)))
                    segs.append((3, occ.addCylinder(xm - g2 / 2 - ft, yy, 0,
                                                    ft, 0, 0, fr)))
            else:
                segs.append((3, occ.addCylinder(xo, yy, 0, xi - xo, 0, 0, lrw)))
        # crossbar, split by the gap
        segs.append((3, occ.addCylinder(xi, -lw, 0, 0, lw - lg / 2, 0, lrw)))
        segs.append((3, occ.addCylinder(xi, lg / 2, 0, 0, lw - lg / 2, 0, lrw)))
        wire = occ.fuse([segs[0]], segs[1:])[0]
        if p["loop_tilt"]:
            # rotate about the radial axis through the loop, i.e. the x-axis
            occ.rotate(wire, xi, 0, 0, 1, 0, 0, p["loop_tilt"])
        if p["loop_phi"]:
            occ.rotate(wire, 0, 0, 0, 0, 0, 1, p["loop_phi"])
        cut_w = []
        for wdg in wedges:
            res, _ = occ.cut([wdg], wire, removeObject=True, removeTool=False)
            cut_w.extend(res)
        wedges = cut_w
        occ.remove(wire, recursive=True)
        # port face spanning the gap, in the z=0 plane, normal z-hat.
        # Direction "+Y" is across the gap, along the wire.
        # Lumped-port face. Palace requires "Direction" to lie IN the surface
        # (the direction across the gap from one conductor to the other), not
        # normal to it — a face normal to +Y aborts with "Specified direction
        # does not align sufficiently with bounding box axes".
        #
        # So: a rectangle in the z=0 plane spanning the gap along y, with
        # Direction "+Y". It must TOUCH both conductor ends; inset even 2% and
        # it floats, drives nothing, and S11 comes back varying 0.036 dB over
        # the whole sweep with no error raised.
        pf = occ.addRectangle(xi - 0.9 * lrw, -lg / 2, 0, 1.8 * lrw, lg)
        if p["loop_tilt"]:
            occ.rotate([(2, pf)], xi, 0, 0, 1, 0, 0, p["loop_tilt"])
        if p["loop_phi"]:
            occ.rotate([(2, pf)], 0, 0, 0, 0, 0, 1, p["loop_phi"])
        port_face = pf
        # R112: see the cap branch. Centre is (xi, 0, 0) before rotation; the
        # tilt is about the x-axis THROUGH that point, so it does not move it.
        _c, _s = math.cos(p["loop_phi"]), math.sin(p["loop_phi"])
        port_centre = (xi * _c, xi * _s, 0.0)

    # --- R21 capacitive electrode ------------------------------------------
    # Cut from the air like the loop, so the topological rule tags it WALL. Inner
    # radius is the torch OD: the band sits against the quartz, outside the gas.
    if p["el_w"] > 0:
        ez, ew, et = p["el_zc"], p["el_w"], p["el_t"]
        ring_o = occ.addCylinder(0, 0, ez - ew / 2, 0, 0, ew, t_ro + et)
        ring_i = occ.addCylinder(0, 0, ez - ew / 2, 0, 0, ew, t_ro)
        band = occ.cut([(3, ring_o)], [(3, ring_i)],
                       removeObject=True, removeTool=True)[0]
        cut_e = []
        for wdg in wedges:
            res, _ = occ.cut([wdg], band, removeObject=True, removeTool=False)
            cut_e.extend(res)
        wedges = cut_e
        occ.remove(band, recursive=True)

    def fuse_radial(wedges_, dts, phi):
        """Fuse a radial stub into ONLY the wedge whose azimuth contains it.

        🔴 The original pattern fused the stub into EVERY wedge. With ns = 1 that
        is correct. With ns > 1 the stub is disjoint from four of the five, and
        a fuse of disjoint solids returns BOTH — so the wedge count grows and
        volume classification fails with "geometry changed?". The viewport has
        therefore only ever been simulated at ns = 1, and the 36/108/288
        azimuthal allocation of entry 93 was not buildable.

        A CUT of a disjoint tool is harmless (the wedge comes back unchanged),
        which is why the loop and electrode paths never showed this.
        """
        n = len(wedges_)
        if n == 1:
            res, _ = occ.fuse([wedges_[0]], dts, removeObject=True,
                              removeTool=True)
            return res
        k = int((phi % (2 * math.pi)) / (2 * math.pi / n)) % n
        res, _ = occ.fuse([wedges_[k]], dts, removeObject=True, removeTool=True)
        if len(res) != 1:
            sys.exit(f"ERROR: radial stub at {math.degrees(phi):.1f} deg fused "
                     f"into wedge {k} produced {len(res)} volumes — it straddles "
                     "a sector plane. Put it on a sector CENTRE.")
        return wedges_[:k] + res + wedges_[k + 1:]

    # --- radial viewport ---------------------------------------------------
    vd = p["view_d"]
    if vd > 0:
        vx = math.cos(p["view_phi"]); vy = math.sin(p["view_phi"])
        stub = occ.addCylinder(a*vx*0.99, a*vy*0.99, 0,
                               p["view_len"]*vx, p["view_len"]*vy, 0, vd/2)
        wedges = fuse_radial(wedges, [(3, stub)], p["view_phi"])

    # --- R57 light trap: a second radial aperture, diametrically opposite ----
    td = p["trap_d"]
    if td > 0:
        if abs(((p["trap_phi"] - p["view_phi"]) % (2 * math.pi)) - math.pi) > 1e-6:
            sys.exit("ERROR: --trap must be diametrically OPPOSITE the viewport "
                     f"(view_phi {math.degrees(p['view_phi']):.1f} deg, trap_phi "
                     f"{math.degrees(p['trap_phi']):.1f} deg). Its whole purpose "
                     "is to sit on the optical axis behind the plasma.")
        tx, ty = math.cos(p["trap_phi"]), math.sin(p["trap_phi"])
        tstub = occ.addCylinder(a*tx*0.99, a*ty*0.99, 0,
                                p["trap_len"]*tx, p["trap_len"]*ty, 0, td/2)
        wedges = fuse_radial(wedges, [(3, tstub)], p["trap_phi"])

    # --- R29 axial chimney on the +z end cap -------------------------------
    # Fused into the air like the viewport stub, so the topological rule tags
    # its wall and far end finite-conductivity metal — a below-cutoff tube closed
    # at the top.
    #
    # It meets the wedge only over the ring t_ro..chim_d/2 (10 -> 10.5 mm): the
    # rest of its footprint lands on the torch and bore end faces, which are
    # fragment TOOLS and so get split conformally. That 0.5 mm ring is finer
    # than MeshSizeMin, so watch the jacobian report on the first build.
    # --- cap holes: ONE feature, both ends -------------------------------
    # 🔑 User, 2026-08-25: *"Isn't 'chimney' overwrought? It's just the hole in
    # the end cap opposite the other torch-bottom hole."* Correct. R29
    # ("chimney", +z) and R49 ("feed", -z) were written separately and are
    # STRUCTURALLY IDENTICAL — same addCylinder, same fuse loop, differing only
    # in z. Two names and two R-numbers for a clearance hole through an end cap.
    # The names mislead: once the outer tube passes through BOTH caps, neither
    # is exhaust — the gas is inside the tube at both ends.
    #
    # 🔴 AND THEY SHARED A BUG. Both fused ONE FULL CYLINDER into EVERY wedge.
    # The groove's comment below already names this exact hazard: "Fusing one
    # full ring into every wedge (the pattern the chimney uses, which is safe
    # at ns=1) would overlap ns copies of the same solid once ns > 1." It was
    # right, and nobody applied it to the chimney. MEASURED 2026-08-25, no
    # torch involved: sectors=1 + chimney is fine; sectors=5 + chimney is
    # NON-MANIFOLD; sectors=5 + feed is NON-MANIFOLD. gmsh accepts all of them;
    # MFEM rejects at load (CONVENTIONS 7bn).
    # ⚠️ Never seen because GEO ships `--chimney 0,41 --feed 0,41` — both OFF.
    def cap_hole(wedges, z_start, length, diameter):
        """Fuse a clearance hole through a cap into the wedges, PER SECTOR."""
        if not (diameter > 0 and length > 0):
            return wedges
        out = []
        for k, wdg in enumerate(wedges):
            if ns > 1:
                # an angular WEDGE of the hole, rotated onto this sector, so
                # each wedge gets its own solid instead of ns copies of one.
                piece = [(3, occ.addCylinder(0, 0, z_start, 0, 0, length,
                                             diameter / 2,
                                             angle=2 * math.pi / ns))]
                if k:
                    occ.rotate(piece, 0, 0, 0, 0, 0, 1, k * 2 * math.pi / ns)
                r_, _ = occ.fuse([wdg], piece, removeObject=True,
                                 removeTool=True)
            else:
                # ns == 1: the original full-cylinder path, kept EXACTLY so
                # every existing single-sector mesh stays byte-identical.
                cyl = [(3, occ.addCylinder(0, 0, z_start, 0, 0, length,
                                           diameter / 2))]
                r_, _ = occ.fuse([wdg], cyl, removeObject=True,
                                 removeTool=True)
            out.extend(r_)
        return out

    wedges = cap_hole(wedges, z0 + L, p["chim_len"], p["chim_d"])

    # --- R54 geometric mode filter: corner groove in both end caps ---------
    # Built PER SECTOR and fused into its own wedge. Fusing one full ring into
    # every wedge (the pattern the chimney uses, which is safe at ns=1) would
    # overlap ns copies of the same solid once ns > 1.
    gw, gd = p["groove_w"], p["groove_d"]
    groove_tool = []
    if gw > 0 and gd > 0:
        if gw >= a:
            sys.exit("ERROR: --groove width must be less than the cavity radius")
        grooved = []
        for k, wdg in enumerate(wedges):
            pieces = []
            for zs in (z0 - gd, z0 + L):
                go = occ.addCylinder(0, 0, zs, 0, 0, gd, a,
                                     angle=2 * math.pi / ns)
                gi = occ.addCylinder(0, 0, zs, 0, 0, gd, a - gw,
                                     angle=2 * math.pi / ns)
                ring, _ = occ.cut([(3, go)], [(3, gi)],
                                  removeObject=True, removeTool=True)
                if k:
                    occ.rotate(ring, 0, 0, 0, 0, 0, 1, k * 2 * math.pi / ns)
                ovalise(ring)
                pieces += ring
            if p["tag_groove"]:
                # R81: keep the slot as its own volume. It ABUTS the wedge (the
                # groove lives beyond the cap plane, the wedge ends at it), so
                # fragment makes the interface conformal without merging them —
                # and then the slot can be given its own attribute and its energy
                # fraction MEASURED. Fusing, which is what happens otherwise,
                # makes the slot geometrically indistinguishable from the cavity.
                groove_tool.extend(pieces)
                grooved.append(wdg)
                continue
            res, _ = occ.fuse([wdg], pieces, removeObject=True,
                              removeTool=True)
            grooved.extend(res)
        if len(grooved) != len(wedges):
            sys.exit(f"ERROR: groove fuse changed the wedge count "
                     f"({len(wedges)} -> {len(grooved)})")
        wedges = grooved

    # --- R49 gas-feed feedthrough on the -z end cap ------------------------
    if p["feed_d"] > 0 and p["feed_len"] > 0:
        wedges = cap_hole(wedges, z0 - p["feed_len"], p["feed_len"],
                          p["feed_d"])
    elif p["torch_ext"] > 0:
        sys.exit("ERROR: --torch-ext requires --feed; an unenclosed tube would "
                 "be tagged PEC by the exterior-face rule and simulated as a "
                 "metal-clad rod.")

    # --- torch assembly, standard Fassel ---------------------------------
    # Modelling only the outer tube was wrong in two ways. The intermediate
    # tube and injector displace gas — and the injector sits ON AXIS, exactly
    # where TM020's E_z peaks. And the plasma forms DOWNSTREAM of the
    # intermediate tube, in the last 20-30 mm before the tip, not uniformly
    # along the whole length.
    #
    # So the energy-integration region (attribute 1) is now the PLASMA ZONE,
    # the clear bore downstream of the intermediate tube — not the whole tube.
    # eta values from here are therefore not directly comparable with earlier
    # entries, which integrated over all 85 mm.
    def tube_of(ro, ri, za, zb):
        o = occ.addCylinder(0, 0, za, 0, 0, zb - za, ro)
        i = occ.addCylinder(0, 0, za, 0, 0, zb - za, ri)
        return occ.cut([(3, o)], [(3, i)],
                       removeObject=True, removeTool=True)[0]

    z_int = min(p["inter_end"], z0 + L)
    z_inj = min(p["inj_end"], z0 + L)
    # R49: the outer tube starts BELOW the -z cap when it is fed through one, so
    # the aperture is loaded by the tube wall rather than being an air hole.
    z_bot = z0 - p["torch_ext"]
    # 🔴 THE OUTER TUBE PASSES THROUGH **BOTH** END CAPS (user, 2026-08-25):
    # one end is the gas entry, the other "basically eliminates fouling" —
    # a tube that stopped at the +z cap would dump exhaust onto the cap and
    # chimney walls instead of carrying it out.
    #
    # It is also what makes the mesh VALID. The tube used to end exactly at
    # z0+L while the chimney began exactly there, so the tube's top face
    # (annulus 8.5..10) and the chimney's bottom face (disc 0..10.5) were
    # COPLANAR AND OVERLAPPING — a face shared by three elements, which gmsh
    # accepted and MFEM rejected at load (CONVENTIONS 7bn). The chimney is
    # fused into the air at line ~623, LONG BEFORE the torch exists to be
    # split against it, so the "fragment tools split it conformally" comment
    # there does not apply. Running the tube through removes the shared face
    # rather than trying to make it conformal.
    z_top = z0 + L + p["torch_ext_top"]
    torch_in = list(tube_of(t_ro, t_ri, z_bot, z_top))
    if p["inter_od"] > 0 and z_int > z0:
        torch_in += tube_of(p["inter_od"] / 2,
                             p["inter_od"] / 2 - p["inter_wall"], z0, z_int)
    if p["inj_od"] > 0 and z_inj > z0:
        torch_in += tube_of(p["inj_od"] / 2, p["inj_id"] / 2, z0, z_inj)

    plasma = [(3, occ.addCylinder(0, 0, z_int, 0, 0, z0 + L - z_int, t_ri))]
    ups = occ.addCylinder(0, 0, z_bot, 0, 0, z_int - z_bot, t_ri)
    upstream = occ.cut([(3, ups)], torch_in,
                       removeObject=True, removeTool=False)[0]
    tube = torch_in
    nq, npl = len(tube), len(plasma)

    # out_map[i] lists volumes derived from input i — provenance, rather than
    # guessing identity from bounding boxes. The filter overlaps the wedges, so
    # its pieces appear under both and are subtracted out below.
    nb = len(filters)
    # The port face is a TOOL in the fragment, not an embed(). embed() refuses
    # a face that touches other entities ("PLC Error: a segment and a facet
    # intersect"), but the face must touch both conductor ends to drive the
    # loop. Fragmenting makes it share edges with them conformally.
    pf_tool = [(2, port_face)] if port_face is not None else []
    # R12 sub-volume goes LAST in the tool list: appending cannot shift the
    # provenance index of anything already there, which is the failure mode that
    # would silently mis-tag the bore.
    pl_sub = []
    if p["pl_ro"] > 0:
        dz = p["pl_zhi"] - p["pl_zlo"]
        # R83: when sectored, build the plasma as ns angular wedges sharing the
        # SAME angular boundaries as the air sectors. Aligning them matters — a
        # plasma wedge boundary offset from an air wedge boundary makes slivers,
        # and a sliver at the plasma edge is where the deposition integral is
        # least trustworthy.
        nps = ns if p["plasma_sectors"] else 1
        for k in range(nps):
            ang = 2 * math.pi / nps if nps > 1 else None
            oc = (occ.addCylinder(0, 0, p["pl_zlo"], 0, 0, dz, p["pl_ro"],
                                  angle=ang) if ang
                  else occ.addCylinder(0, 0, p["pl_zlo"], 0, 0, dz, p["pl_ro"]))
            if p["pl_ri"] > 0:
                ic = (occ.addCylinder(0, 0, p["pl_zlo"], 0, 0, dz, p["pl_ri"],
                                      angle=ang) if ang
                      else occ.addCylinder(0, 0, p["pl_zlo"], 0, 0, dz,
                                           p["pl_ri"]))
                piece = occ.cut([(3, oc)], [(3, ic)],
                                removeObject=True, removeTool=True)[0]
            else:
                piece = [(3, oc)]
            if k:
                occ.rotate(piece, 0, 0, 0, 0, 0, 1, k * 2 * math.pi / nps)
            pl_sub += piece
    # 🔑 GAP SUB-VOLUME. A sphere centred on the series gap, big enough to
    # contain the gap AND its near fringing field, which is where the stored
    # energy actually sits. Sized from the electrode, not the gap: at wide gaps
    # the fringing extends ~the electrode radius beyond the faces.
    # ⚠️ APPENDED LAST, like pl_sub and groove_tool, for the same reason —
    # appending cannot shift a provenance index that already exists.
    gap_sub = []
    if gap2_centre is not None:
        _fr = max(p["loop_flange_r"], p["loop_rw"])
        _rad = max(p["loop_gap2"] / 2.0 + _fr, 2.0 * _fr)
        gap_sub = [(3, occ.addSphere(gap2_centre[0], gap2_centre[1],
                                     gap2_centre[2], _rad))]

    # ⚠️ groove_tool goes after pl_sub for the same reason pl_sub goes after
    # everything else: appending cannot shift a provenance index that already
    # exists. Inserting it anywhere earlier would silently re-tag the bore.
    # R109 — RIGID TRANSLATION, applied HERE and nowhere else.
    #
    # 🔴 Applying it AFTER the fragment does not work, and fails in a way worth
    # recording: `out_map` is captured from the fragment, so translating
    # afterwards leaves every tag in it referring to the pre-translate model.
    # Only dim-3 entities move, the internal port face (attribute 91) is left
    # behind unmeshed, and Palace dies with "Unknown port boundary attribute
    # 91" after 8 s. Translating the INPUTS instead means the fragment, the
    # output map, and every tag derived from it are all computed on the
    # translated geometry and stay consistent.
    #
    # Everything downstream is then safe: classification is the output map,
    # WALL is topological (single adjacent volume), and mesh sizing is global
    # options rather than a coordinate field — so a rigid shift changes the
    # MESH and nothing else, which is the whole point of the probe.
    _off = p.get("offset") or (0.0, 0.0, 0.0)
    _rot = p.get("rotate") or 0.0
    _all = (wedges + filters + tube + plasma + upstream + pf_tool + pl_sub
            + groove_tool)
    if _rot:
        # rotate FIRST, about the cavity axis through the origin, then translate
        _ax = p.get("rotate_axis") or (0.0, 0.0, 1.0)
        occ.rotate(_all, 0, 0, 0, *_ax, _rot)
        print(f"  E0c rigid rotation {math.degrees(_rot):+.1f} deg about z "
              f"about {_ax} — physics invariant; solid invariant "
              "ONLY for the z axis")
    if any(_off):
        occ.translate(_all, *_off)
        print(f"  R109 rigid offset ({_off[0]*1e3:+.2f},{_off[1]*1e3:+.2f},"
              f"{_off[2]*1e3:+.2f}) mm — physics invariant, mesh changed")

    _, out_map = occ.fragment(wedges + filters,
                              tube + plasma + upstream + pf_tool + pl_sub
                              + groove_tool + gap_sub)
    occ.synchronize()

    def tags_of(i):
        return {t for d, t in out_map[i] if d == 3}

    filter_v = set().union(*(tags_of(ns + j) for j in range(nb))) if nb else set()
    torch_v = set().union(*(tags_of(ns + nb + j) for j in range(nq)))
    bore_v = set().union(*(tags_of(ns + nb + nq + j) for j in range(npl)))
    up_v = set().union(*(tags_of(ns + nb + nq + npl + j)
                         for j in range(len(upstream))))
    nu = len(upstream)
    port_v = ({t for d, t in out_map[ns + nb + nq + npl + nu] if d == 2}
              if port_face is not None else set())
    # R81: the groove volumes, if they were kept separate. Index is the very end
    # of the tool list, which is why it could be appended without disturbing
    # anything above.
    groove_v = set()
    if groove_tool:
        gbase = ns + nb + nq + npl + nu + len(pf_tool) + len(pl_sub)
        groove_v = set().union(*(tags_of(gbase + j)
                                 for j in range(len(groove_tool))))
        if not groove_v:
            sys.exit("ERROR: --tag-groove produced no groove volumes. The slot "
                     "was requested as a separate region and did not survive the "
                     "fragment — do NOT read a result from this mesh.")
    # 🔑 THE GAP REGION, resolved from provenance like every other sub-volume.
    gap_v = set()
    if gap_sub:
        _gb = (ns + nb + nq + npl + nu + len(pf_tool) + len(pl_sub)
               + len(groove_tool))
        gap_v = set().union(*(tags_of(_gb + j) for j in range(len(gap_sub))))
        # the sphere straddles conductor and air; keep only what is NOT metal.
        gap_v = gap_v - torch_v - bore_v - up_v - groove_v - filter_v
        if not gap_v:
            sys.exit("ERROR: the series-gap sub-volume produced no air volume. "
                     "It was requested as a separate region and did not survive "
                     "the fragment — do NOT read an energy split from this mesh.")

    air_sectors = [sorted(tags_of(k) - filter_v - torch_v - bore_v - up_v
                          - groove_v - gap_v)
                   for k in range(ns)]

    if not torch_v or not bore_v or any(not s for s in air_sectors):
        for dim, tag in gmsh.model.getEntities(3):
            bb = gmsh.model.getBoundingBox(dim, tag)
            print(f"    vol {tag}: bbox {[f'{v*1e3:.1f}' for v in bb]}")
        sys.exit("ERROR: volume classification failed — geometry changed?")

    # R12: carve the conductive sub-region out of the bore. They must be
    # DISJOINT — Palace assigns materials by attribute, so an overlap is
    # ambiguous rather than additive.
    plasma_v = set()
    plasma_sec = []
    if pl_sub:
        base = ns + nb + nq + npl + nu + len(pf_tool)
        per = [tags_of(base + j) & bore_v for j in range(len(pl_sub))]
        plasma_v = set().union(*per)
        bore_v = bore_v - plasma_v
        if not plasma_v:
            sys.exit("ERROR: R12 sub-volume produced no bore overlap.")
        if p["plasma_sectors"]:
            # R83: one attribute per azimuthal sector. An EMPTY sector is fatal,
            # not cosmetic — a missing wedge reads as zero deposited power there
            # and would look exactly like perfect screening.
            for k, v in enumerate(per):
                if not v:
                    sys.exit(f"ERROR: plasma sector {k} is empty. Deposition "
                             "uniformity cannot be measured on a torus with a "
                             "missing wedge.")
                gmsh.model.addPhysicalGroup(3, sorted(v), tag=TAG_PLASMA0 + k,
                                            name=f"plasma_s{k + 1}")
            plasma_sec = list(range(TAG_PLASMA0, TAG_PLASMA0 + len(per)))
            print(f"  plasma in {len(per)} azimuthal sectors -> attributes "
                  f"{plasma_sec[0]}..{plasma_sec[-1]}")
        else:
            gmsh.model.addPhysicalGroup(3, sorted(plasma_v), tag=TAG_PLASMA,
                                        name="plasma")
            print(f"  plasma sub-region: {len(plasma_v)} vols -> attribute "
                  f"{TAG_PLASMA}")
    gmsh.model.addPhysicalGroup(3, sorted(bore_v), tag=TAG_BORE, name="bore")
    gmsh.model.addPhysicalGroup(3, sorted(torch_v), tag=TAG_TORCH, name="torch")
    for k, tags in enumerate(air_sectors):
        gmsh.model.addPhysicalGroup(3, tags, tag=TAG_AIR0 + k,
                                    name=f"air_s{k + 1}")
    if filter_v:
        gmsh.model.addPhysicalGroup(3, sorted(filter_v), tag=TAG_FILTER,
                                    name="filter")
    if up_v:
        gmsh.model.addPhysicalGroup(3, sorted(up_v), tag=TAG_UPSTREAM,
                                    name="upstream")
    if groove_v:
        gmsh.model.addPhysicalGroup(3, sorted(groove_v), tag=TAG_GROOVE,
                                    name="groove")
        print(f"  groove tagged separately: {len(groove_v)} vols -> attribute "
              f"{TAG_GROOVE}")
    if gap_v:
        gmsh.model.addPhysicalGroup(3, sorted(gap_v), tag=TAG_GAP,
                                    name="series_gap")
        print(f"  series gap tagged separately: {len(gap_v)} vols -> attribute "
              f"{TAG_GAP}  (energy split measurable)")

    # The striker solid is DELETED, leaving a void. Its surface then has a
    # single adjacent volume, so the topological rule below tags it PEC
    # automatically — no special case needed.
    # WALL (attribute 90, finite conductivity — NOT PEC): the cavity wall and
    # both end caps. Internal sector-boundary faces
    # must NOT be included — they are fictitious, and making them conducting
    # would turn the cavity into ns separate wedge resonators.
    # Topology, not coordinates: an exterior face is one with a single
    # adjacent volume. The cavity is closed, so every exterior face is wall.
    #
    # A bounding-box test was tried first and is WRONG for sectors. The bbox
    # corner of a 72-degree wedge's outer face lies outside the arc, so
    # hypot(x,y) there is ~1.38a, not a, and the wall silently failed to be
    # tagged. Palace then applied its natural (magnetic-wall) condition to most
    # of the cavity, which produced a spectrum of localised junk at Q ~ 3e8.
    pec = [tag for dim, tag in gmsh.model.getEntities(2)
           if len(gmsh.model.getAdjacencies(2, tag)[0]) == 1]
    if not pec:
        sys.exit("ERROR: no exterior surfaces found — cannot apply PEC")
    # 🔎 DIAGNOSTIC ONLY, ADDITIVE, CHANGES NOTHING. Dumps the exterior-face
    # inventory so the rule that separates the LOOP from the WALL can be chosen
    # from MEASUREMENT rather than derived. This file already records that the
    # first coordinate rule for the wall was wrong, and the wire reaches r = a
    # at its entry, so a radius test cannot separate them either.
    if p.get("dump_faces"):
        print("  --- exterior face inventory (dim=2) ---")
        for t in sorted(pec):
            try:
                area = gmsh.model.occ.getMass(2, t)
                com = gmsh.model.occ.getCenterOfMass(2, t)
                bb = gmsh.model.getBoundingBox(2, t)
                ext = (bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2])
            except Exception as e:
                print(f"    face {t}: <query failed: {e}>")
                continue
            print(f"    face {t:>5}  type={gmsh.model.getType(2, t):<12}"
                  f" area={area*1e6:>12.3f} mm^2"
                  f"  com=({com[0]*1e3:8.3f},{com[1]*1e3:8.3f},{com[2]*1e3:8.3f})"
                  f"  extent=({ext[0]*1e3:7.3f},{ext[1]*1e3:7.3f},"
                  f"{ext[2]*1e3:7.3f})")
        print("  --- end inventory ---")
    # 🔑 SPLIT THE LOOP OUT OF THE WALL. Both are exterior faces — the wire is
    # CUT OUT of the vacuum, so its surface has a single adjacent volume exactly
    # like the barrel — which is why one attribute held both.
    #
    # 🔴 THE RULE WAS CHOSEN FROM A MEASUREMENT, NOT DERIVED. `--dump-faces` on
    # the design cavity shows every wire face has z-extent EXACTLY 2*lrw with
    # its centroid at z = 0, while the caps have z-extent 0, the groove 10, the
    # chimney 41 and the barrel 135.4. A RADIUS test cannot work: the leg
    # reaches r = a where it enters the barrel.
    # ⚠️ This holds for the BARREL mount, where the whole loop lies in the z = 0
    # plane. The CAP loop's legs are AXIAL, so its z-extent is ld, not 2*lrw,
    # and the rule does not transfer — that case keeps the old behaviour and
    # SAYS SO rather than silently mis-tagging.
    # ---- CONDUCTOR CENTRELINE, sampled ------------------------------------
    # 🔴 THE z-EXTENT RULE WAS NOT TOPOLOGY-INVARIANT. It was measured on the
    # radial family, where every conductor face is a cylinder or a disc and its
    # bounding box is exactly 2*lrw tall. A TORUS is split differently by OCC,
    # and the same rule found 10 faces / 142.4 mm^2 at h = 5 mm but only
    # 5 / 58.6 at h = 3 — half the conductor silently left in the wall
    # attribute and modelled as aluminium, which is the exact failure the
    # 2026-08-27 split exists to prevent.
    # ✅ A face belongs to the conductor iff its CENTROID lies within the
    # conductor's own cross-section of the centreline PATH — which we know
    # exactly, because we just built it. That cannot depend on how OCC chooses
    # to subdivide a surface.
    # 🔑 And it is safe against the wall: the barrel survives as ONE large face
    # per sector (~15,000 mm^2) whose centroid is nowhere near the loop, even
    # though the leg centrelines pass through it.
    def _centreline():
        """Sampled points along the conductor centreline, cavity frame."""
        step = 0.25e-3
        pts = []
        if p.get("loop_azim"):
            _hh, _al = float(p["loop_azim"][0]), float(p["loop_azim"][1])
            _RR = a - _hh
            _tt = _al / (2.0 * _RR)
            n = max(2, int(_al / step))
            for i in range(n + 1):                       # the arc
                th = -_tt + 2.0 * _tt * i / n
                pts.append((_RR * math.cos(th), _RR * math.sin(th), 0.0))
            # ⚠️ SAMPLE WHAT WAS BUILT, NOT WHAT WAS INTENDED. The legs start
            # one radial thickness INSIDE the arc (see _leg) so the boolean is
            # transverse; the path has to include that or the area check
            # compares the built surface against a shorter conductor.
            _ovp = (p["loop_strip"][1] if p.get("loop_strip") else p["loop_rw"])
            m = max(2, int((_hh + 2.0e-3 + _ovp) / step))
            for sgn in (+1.0, -1.0):                     # the two legs
                th = sgn * _tt
                for j in range(m + 1):
                    r = (_RR - _ovp) + (_hh + 2.0e-3 + _ovp) * j / m
                    pts.append((r * math.cos(th), r * math.sin(th), 0.0))
        elif ld > 0 and lcr <= 0:                        # radial, barrel
            xo_, xi_ = a + 2.0e-3, a - ld
            n = max(2, int(abs(xo_ - xi_) / step))
            for yy in (-lw, +lw):                        # the two legs
                for j in range(n + 1):
                    pts.append((xo_ + (xi_ - xo_) * j / n, yy, 0.0))
            m = max(2, int(2.0 * lw / step))
            for j in range(m + 1):                       # the crossbar
                pts.append((xi_, -lw + 2.0 * lw * j / m, 0.0))
        else:
            return None
        c_, s_ = math.cos(p["loop_phi"]), math.sin(p["loop_phi"])
        return [(x * c_ - y * s_, x * s_ + y * c_, z) for x, y, z in pts]

    loop_faces = []
    # 🔴 THE RULE KEYS ON THE CONDUCTOR'S AXIAL HEIGHT, WHICH IS NOT ALWAYS
    # 2*lrw. A 5x1 mm strip lying broad-face-to-the-wall is 5 mm tall in z, so
    # the round-wire assumption would MISS its faces, drop them back into the
    # wall attribute, and model the coupler as aluminium again — silently
    # undoing the 2026-08-27 split for the one topology it was extended for.
    # ⚠️ AZIMUTHAL LOOPS HAVE ld = 0. The z-extent rule still holds — the arc
    # lies in the z = 0 plane with a circular cross-section, so its faces are
    # 2*lrw tall with centroid at z = 0, exactly like the barrel's. But the
    # GUARD said `ld > 0`, which would have silently sent the arc back into the
    # wall attribute and modelled it as aluminium again.
    _path = _centreline()
    if _path is not None:
        # half the conductor's largest cross-section dimension, plus a margin
        _reff = (0.5 * math.hypot(*p["loop_strip"]) if p.get("loop_strip")
                 else p["loop_rw"])
        _near = _reff * 1.25
        # 🔴 AND AN AREA CAP, because proximity ALONE is not enough. The barrel
        # survives as one face per sector whose CENTROID sits at r = 82.3 mm,
        # phi = 36 deg — and the loop is deliberately placed at the sector
        # centre, so at h = 5 mm (R = 83) that centroid falls 0.7 mm from the
        # arc's centreline and the barrel was swallowed whole: 15,111 mm^2
        # tagged as conductor against 140 expected. The conductor's faces are
        # ALL small by construction; nothing else about them is.
        _inside0 = [q for q in _path if math.hypot(q[0], q[1]) <= a]
        _per0 = (2.0 * (p["loop_strip"][0] + p["loop_strip"][1])
                 if p.get("loop_strip") else 2.0 * math.pi * p["loop_rw"])
        _cap = 3.0 * len(_inside0) * 0.25e-3 * _per0      # 3x the whole conductor
        for t in pec:
            if gmsh.model.occ.getMass(2, t) > _cap:
                continue
            com = gmsh.model.occ.getCenterOfMass(2, t)
            if min(math.dist(com, q) for q in _path) <= _near:
                loop_faces.append(t)
        if not loop_faces:
            sys.exit("ERROR: the loop-surface split found NO faces. The wire is "
                     "meshed but its surface was not identified, so it would be "
                     "tagged as cavity wall and modelled as aluminium. Re-run "
                     "with --dump-faces and check the z-extent rule.")
    elif ld > 0:
        print("  ⚠️ CAP loop: surface NOT split out — the z-extent rule is for "
              "the barrel mount only.\n"
              "     The loop is tagged as WALL and will be modelled as "
              "ALUMINIUM, not copper.")
    # 🔑 COAX WAVE PORT: find the stub mouth among the EXTERIOR faces. Its
    # centroid sits on the coax axis at r = a + stub, and its area is the
    # annulus between the hole and the inner conductor.
    if _COAX_MOUTH is not None:
        _rm, _rh_m, _rin_m = _COAX_MOUTH
        _want_a = math.pi * (_rh_m ** 2 - _rin_m ** 2)
        _cands = []
        for t in pec:
            com = gmsh.model.occ.getCenterOfMass(2, t)
            _d = math.hypot(com[0] - _rm * math.cos(_COAX_PHI),
                            com[1] - _rm * math.sin(_COAX_PHI))
            if _d < _rh_m and abs(com[2]) < _rh_m:
                _cands.append((t, gmsh.model.occ.getMass(2, t), _d))
        _hit = [(t, ar) for t, ar, _ in _cands
                if 0.7 * _want_a <= ar <= 1.4 * _want_a]
        if len(_hit) != 1:
            sys.exit(f"ERROR: coax mouth not uniquely identified — wanted one "
                     f"exterior face of ~{_want_a*1e6:.2f} mm^2 near the stub "
                     f"mouth, found {len(_hit)} of {len(_cands)} nearby "
                     f"candidates: {[(t, round(ar*1e6,3)) for t,ar,_ in _cands]}")
        port_v = {_hit[0][0]}
        print(f"  COAX MOUTH: exterior face {_hit[0][0]}, "
              f"{_hit[0][1]*1e6:.2f} mm^2 (annulus wants {_want_a*1e6:.2f}) "
              f"-> attribute {TAG_PORT}, WAVE PORT")
    # 🔴 AND IT MUST NOT ALSO BE WALL. Every exterior face lands in `wall`
    # unless excluded, so tagging the mouth as `port` too put TWO boundary
    # elements on one face and Palace refused the mesh:
    #   "A non-periodic face cannot have multiple boundary elements!"
    # (geodata.cpp GetFaceToBdrElementMap). A LUMPED port never hits this — its
    # face is interior, so it was never in `pec` to begin with.
    wall_faces = [t for t in pec
                  if t not in set(loop_faces) and t not in port_v]
    gmsh.model.addPhysicalGroup(2, wall_faces, tag=TAG_WALL, name="wall")
    if loop_faces:
        gmsh.model.addPhysicalGroup(2, sorted(loop_faces), tag=TAG_LOOP,
                                    name="loop")
        _la = sum(gmsh.model.occ.getMass(2, t) for t in loop_faces) * 1e6
        _wa = sum(gmsh.model.occ.getMass(2, t) for t in wall_faces) * 1e6
        _pa = sum(gmsh.model.occ.getMass(2, t) for t in pec) * 1e6
        # 🔴 THE PARTITION MUST BE EXACT. If the classes do not sum to the
        # original exterior area, a face was dropped or double-counted and some
        # of the cavity is now unbounded — Palace would apply its natural BC
        # there and produce the localised junk this file records at Q ~ 3e8.
        # 🔑 A COAX PORT IS A THIRD EXTERIOR CLASS. Until 2026-09-02 the port
        # was always an INTERIOR face (a lumped port bridging a gap), so
        # wall+loop covered everything. The coax mouth is an exterior face, so
        # it must be counted here — this guard caught its omission immediately,
        # the discrepancy being exactly the mouth's 13.477 mm^2.
        _pta = sum(gmsh.model.occ.getMass(2, t) for t in port_v
                   if t in set(pec)) * 1e6
        if abs(_wa + _la + _pta - _pa) > 1e-6 * max(_pa, 1.0):
            sys.exit(f"ERROR: wall+loop+port area {_wa + _la + _pta:.6f} "
                     f"(wall {_wa:.3f} + loop {_la:.3f} + port {_pta:.3f}) "
                     f"!= exterior "
                     f"{_pa:.6f} mm^2 — the split is not a partition.")
        # 🔴 CHECK THE AREA AGAINST WHAT THE CONDUCTOR MUST HAVE. Face COUNT
        # is not a check — OCC may legitimately split a surface any number of
        # ways. Area is invariant, and it is what would have caught h = 3
        # returning 58.6 mm^2 where the geometry demands ~113.
        _inside = [q for q in _path if math.hypot(q[0], q[1]) <= a]
        _plen = len(_inside) * 0.25e-3
        _per = (2.0 * (p["loop_strip"][0] + p["loop_strip"][1])
                if p.get("loop_strip") else 2.0 * math.pi * p["loop_rw"])
        _want = _plen * _per * 1e6
        if not (0.6 * _want <= _la <= 1.6 * _want):
            sys.exit(
                f"ERROR: the loop surface is {_la:.1f} mm^2 but the conductor "
                f"path ({_plen*1e3:.1f} mm inside the cavity, perimeter "
                f"{_per*1e3:.2f} mm) demands ~{_want:.1f} mm^2.\n"
                f"  🔑 Face identification has missed part of the conductor, or "
                f"taken part of the wall. Re-run with --dump-faces.")
        print(f"  loop: {len(loop_faces)} face(s) -> attribute {TAG_LOOP}, "
              f"{_la:.1f} mm^2 (want ~{_want:.1f}); wall keeps "
              f"{len(wall_faces)}, {_wa:.1f} mm^2")
    if port_v:
        gmsh.model.addPhysicalGroup(2, sorted(port_v), tag=TAG_PORT, name="port")
        print(f"  port face(s) {sorted(port_v)} -> attribute {TAG_PORT}")
    print(f"  PEC: {len(pec)} exterior surfaces")

    # ----------------------------------------------------------------------
    # Mesh sizing
    # ----------------------------------------------------------------------
    n = p["elems_per_wl"]
    # E1c: coarsen the AIR only, leaving the thin-wall floor alone. The air
    # carries ~99% of the field but is smooth; the 1.0-1.5 mm tube walls carry
    # ~0.06% of TE011's energy but SET THE MESH FLOOR. A single global size
    # factor couples them, which is why sf 2.5 — fine on an empty cavity —
    # self-intersects on the loaded one.
    h_air = mesh_size(1.0, F0, n) * p.get("air_coarsen", 1.0)
    h_qtz = min(mesh_size(p["torch_eps"], F0, n), p["torch_wall"])
    # The bore is air on a 122 mm wavelength — it needs nothing like the wall
    # resolution. Meshing it at h_qtz cost 57k tets for no accuracy.
    h_bore = p["bore_h"]

    print(f"  target h: air {h_air*1e3:.1f} mm | quartz {h_qtz*1e3:.2f} mm "
          f"| bore {h_bore*1e3:.1f} mm")

    # R15: MeshSizeMin is a HARD FLOOR — gmsh clamps every requested size to it,
    # including one asked for by a field. At h_qtz*0.8 = 1.2 mm it silently
    # discarded plasma refinements of 1.0 and 0.6 mm: both came back as the same
    # 1.2 mm mesh (14,703 vs 14,586 tets), and the "convergence study" was
    # comparing a mesh against itself. Lowering the floor does not refine
    # anything on its own — the background field still asks for 1.5 mm at the
    # torch wall — it only stops the floor from overriding a deliberate request.
    h_min = h_qtz * 0.8
    if p["plasma_h"] > 0:
        h_min = min(h_min, p["plasma_h"] * 0.8)
    # R62: the series-capacitor gap is a sub-millimetre void that must be
    # RESOLVED, not merely present. A first attempt left it below the mesh floor
    # and Q_ext came back identical to 4 significant figures across gaps of
    # 0, 0.15, 0.30 and 0.60 mm — the geometry differed (checksums), the
    # discretisation did not, and the capacitor contributed nothing.
    h_gap2 = (p["loop_gap2"] / 2.5) if p["loop_gap2"] > 0 else 0.0
    if h_gap2:
        h_min = min(h_min, h_gap2 * 0.8)
    # 🔴 R112: THE SAME BUG, ONE GAP OVER. R62 diagnosed exactly this for the
    # SERIES gap and fixed it there only — the PRIMARY port gap was left below
    # the floor. Measured consequence: the lumped port surface meshed with
    # **2 elements**, on a 1.8 x 0.30 mm rectangle against a 1.2 mm floor. The
    # port IS the drive point, so beta rode on how those two triangles happened
    # to fall: the SAME geometry at 1 and 5 azimuthal sectors gave beta 0.5598
    # and 0.3411, a 39% spread, and the loop-area sizing sweep came back
    # NON-MONOTONIC (1.50, 0.87, 0.56, 1.85) for the same reason.
    #
    # ⚠️ Q0 = Q_L(1+beta) SURVIVED this, because Q_L and beta come from the same
    # S11 curve and track whatever the actual coupling was — four driven-vs-eigen
    # comparisons agreed to 4.9-8.8% throughout. What was never trustworthy is
    # beta as a DESIGN quantity: "what coupling will this loop give?"
    # ⚠️ `ld > 0` IS A RADIAL-TOPOLOGY ASSUMPTION, and it is the third one this
    # file made. An azimuthal loop has ld = 0, so this left h_gap at zero, the
    # port ball was never created, and the conductor got NO local refinement —
    # cavity-scale elements around a 1 mm wire. The slivers that produced would
    # not curve at order 2, and gmsh's high-order optimiser ground through
    # "finalized after 200 iterations, because the maximum number of steps was
    # taken" indefinitely. The radial control converges in 19 iterations.
    h_gap = (p["loop_gap"] / 2.5
             if ((ld > 0 or p.get("loop_azim")) and p["loop_gap"] > 0) else 0.0)
    if h_gap:
        h_min = min(h_min, h_gap * 0.8)
    # 🔑 THE COAX ANNULUS NEEDS ITS OWN FLOOR. h_gap keys on loop_gap, which is
    # exactly ZERO for a coax feed (the arc is continuous), so the 1.3 mm-wide
    # annular channel got NO refinement and gmsh's high-order optimiser thrashed
    # — rel decr 1.033, objective RISING, same signature as the seamed ring.
    _hole_p = p.get("loop_hole")
    h_coax = 0.0
    if _hole_p:
        _rin_p = (p["loop_strip"][1] / 2.0 if p.get("loop_strip")
                  else p["loop_rw"])
        h_coax = (_hole_p[0] - _rin_p) / 3.0     # 3 elements across the gap
        h_min = min(h_min, h_coax * 0.8)
    gmsh.option.setNumber("Mesh.MeshSizeMin", h_min)
    gmsh.option.setNumber("Mesh.MeshSizeFactor", p.get("size_factor", 1.0))
    gmsh.option.setNumber("Mesh.MeshSizeMax", h_air)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 12)
    # OFF deliberately. The torch wall needs ~1.5 mm elements; the cavity is
    # 189 mm across and needs ~15 mm. Letting the fine torch mesh extend from
    # its boundary floods the air domain — it cost 271k tets against the ~40k
    # the physics needs. Gradation is instead controlled explicitly by the
    # distance field below.
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)

    # Grow from the torch wall out to the air size over ~4 torch radii.
    t_ro = p["torch_od"] / 2.0
    dist = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(
        dist, "SurfacesList",
        [s for _, s in gmsh.model.getBoundary(
            [(3, t) for t in sorted(torch_v)], oriented=False)])
    thr = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(thr, "InField", dist)
    gmsh.model.mesh.field.setNumber(thr, "SizeMin", h_qtz)
    gmsh.model.mesh.field.setNumber(thr, "SizeMax", h_air)
    gmsh.model.mesh.field.setNumber(thr, "DistMin", 2.0e-3)
    gmsh.model.mesh.field.setNumber(thr, "DistMax", 3.0 * t_ro)
    # R15: refine the R12 plasma sub-region as a FIELD, not via set_pts.
    #
    # set_pts only prescribes sizes at boundary POINTS, and this model runs with
    # Mesh.MeshSizeExtendFromBoundary = 0 — so a point size does not propagate
    # into a volume's interior. Prescribing plasma_h that way changed the mesh by
    # 795 tets when it should have changed it by ~29,000: silently ignored.
    # A Cylinder field covers the region by coordinates instead, and Min against
    # the threshold keeps the torch-wall gradation intact.
    bg = thr
    if p["plasma_h"] > 0 and p["pl_ro"] > 0:
        cyl = gmsh.model.mesh.field.add("Cylinder")
        gmsh.model.mesh.field.setNumber(cyl, "Radius", p["pl_ro"])
        gmsh.model.mesh.field.setNumber(cyl, "VIn", p["plasma_h"])
        gmsh.model.mesh.field.setNumber(cyl, "VOut", h_air)
        gmsh.model.mesh.field.setNumber(cyl, "XCenter", 0.0)
        gmsh.model.mesh.field.setNumber(cyl, "YCenter", 0.0)
        gmsh.model.mesh.field.setNumber(cyl, "ZCenter",
                                        (p["pl_zlo"] + p["pl_zhi"]) / 2.0)
        gmsh.model.mesh.field.setNumber(cyl, "XAxis", 0.0)
        gmsh.model.mesh.field.setNumber(cyl, "YAxis", 0.0)
        gmsh.model.mesh.field.setNumber(cyl, "ZAxis",
                                        p["pl_zhi"] - p["pl_zlo"])
        mn = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(mn, "FieldsList", [thr, cyl])
        bg = mn
        print(f"  plasma refinement: {p['plasma_h']*1e3:.2f} mm inside "
              f"r<{p['pl_ro']*1e3:.1f}, z {p['pl_zlo']*1e3:.1f}.."
              f"{p['pl_zhi']*1e3:.1f}")
    # 🔑 REFINE THE WHOLE COAX CHANNEL. h_gap keys on loop_gap, which is ZERO
    # for a coax feed (the arc is continuous), so the 1.3 mm annular channel got
    # no refinement at all and gmsh's high-order optimiser thrashed — rel decr
    # 1.033, objective RISING, the same signature as the seamed ring.
    # ⚠️ CHAINED onto `bg` with a Min, like every other field here. A first
    # attempt appended to a `fields` list that does not exist, and named the
    # field `cyl` — which is the PLASMA field's name a few lines above.
    if _hole_p:
        _rh_p, _stub_p = _hole_p
        _r0p, _r1p = a - 2.0e-3, a + _stub_p + 1.0e-3
        ccyl = gmsh.model.mesh.field.add("Cylinder")
        gmsh.model.mesh.field.setNumber(ccyl, "Radius", _rh_p * 1.4)
        gmsh.model.mesh.field.setNumber(ccyl, "VIn", h_coax)
        gmsh.model.mesh.field.setNumber(ccyl, "VOut", h_air)
        gmsh.model.mesh.field.setNumber(ccyl, "XCenter",
                                        0.5 * (_r0p + _r1p) * math.cos(_COAX_PHI))
        gmsh.model.mesh.field.setNumber(ccyl, "YCenter",
                                        0.5 * (_r0p + _r1p) * math.sin(_COAX_PHI))
        gmsh.model.mesh.field.setNumber(ccyl, "ZCenter", 0.0)
        gmsh.model.mesh.field.setNumber(ccyl, "XAxis",
                                        (_r1p - _r0p) * math.cos(_COAX_PHI))
        gmsh.model.mesh.field.setNumber(ccyl, "YAxis",
                                        (_r1p - _r0p) * math.sin(_COAX_PHI))
        gmsh.model.mesh.field.setNumber(ccyl, "ZAxis", 0.0)
        mnc = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(mnc, "FieldsList", [bg, ccyl])
        bg = mnc
        print(f"  COAX MESH: {h_coax*1e3:.4f} mm elements in a "
              f"{_rh_p*1.4*1e3:.2f} mm cylinder along the stub", flush=True)

    # R62: a Ball of fine elements around the capacitor gap. Small radius, so
    # the cost is local: the field must resolve the gap, not the whole loop.
    if h_gap2 and gap2_centre is not None:
        ball = gmsh.model.mesh.field.add("Ball")
        # Radius kept tight: the capacitance lives within ~1 wire radius of the
        # gap, and a 4x ball cost 1.36M tets for one 0.3 mm feature.
        _rb = max(1.5 * p["loop_rw"], p["loop_flange_r"] + 0.8e-3)
        gmsh.model.mesh.field.setNumber(ball, "Radius", _rb)
        gmsh.model.mesh.field.setNumber(ball, "Thickness", 2.0 * p["loop_rw"])
        gmsh.model.mesh.field.setNumber(ball, "VIn", h_gap2)
        gmsh.model.mesh.field.setNumber(ball, "VOut", h_air)
        gmsh.model.mesh.field.setNumber(ball, "XCenter", gap2_centre[0])
        gmsh.model.mesh.field.setNumber(ball, "YCenter", gap2_centre[1])
        gmsh.model.mesh.field.setNumber(ball, "ZCenter", gap2_centre[2])
        mn2 = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(mn2, "FieldsList", [bg, ball])
        bg = mn2
        print(f"  gap2 refinement: {h_gap2*1e3:.3f} mm within "
              f"{4e3*p['loop_rw']:.1f} mm of the capacitor")
    # 🔴 R112: the same Ball for the PRIMARY PORT gap. Lowering the floor above
    # does NOT refine anything on its own — as R15's comment says, the floor
    # only stops a deliberate request being overridden. Without this field the
    # port stays at 2 elements no matter what the floor is.
    if h_gap and port_centre is not None:
        pball = gmsh.model.mesh.field.add("Ball")
        # ⚠️ WIDER FOR AN AZIMUTHAL LOOP. Its gap is a flat slot cut through a
        # CURVED tube, so flat faces meet a curved surface right where the mesh
        # is finest. At 1.5*rw the transition was abrupt enough to produce
        # INVERTED order-2 elements (ScaledJac < 0) that the high-order
        # optimiser could not untangle — rel decr 1e-298 over 100 iterations.
        # A radial loop's gap is a flat slot through a STRAIGHT bar and does not
        # have the problem, which is why 1.5 was enough there.
        # ⚠️ 4.0 was added to grade the FLAT-SLOT gap, a construction that is
        # no longer here — and it costs: a 4x radius of 0.12 mm elements took
        # h = 2 mm from 20 s to over 90. The angular gap does not need it.
        _rp = 1.5 * p["loop_rw"]
        gmsh.model.mesh.field.setNumber(pball, "Radius", _rp)
        gmsh.model.mesh.field.setNumber(pball, "Thickness", 2.0 * p["loop_rw"])
        gmsh.model.mesh.field.setNumber(pball, "VIn", h_gap)
        gmsh.model.mesh.field.setNumber(pball, "VOut", h_air)
        gmsh.model.mesh.field.setNumber(pball, "XCenter", port_centre[0])
        gmsh.model.mesh.field.setNumber(pball, "YCenter", port_centre[1])
        gmsh.model.mesh.field.setNumber(pball, "ZCenter", port_centre[2])
        mnp = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(mnp, "FieldsList", [bg, pball])
        bg = mnp
        print(f"  PORT refinement: {h_gap*1e3:.3f} mm within {_rp*1e3:.1f} mm "
              f"of the port gap (floor now {h_min*1e3:.3f} mm)")
    # 🔴 REFINE ALONG THE WHOLE ARC, NOT JUST AT THE PORT.
    # The port ball is a single sphere of radius 1.5*rw at the gap. That covers
    # a radial loop's crossbar, which is short and straight — but an azimuthal
    # arc runs +-8.5 mm away from the port, so nearly all of the conductor sat
    # in cavity-scale elements. Balls along the centreline, overlapping, so the
    # whole wire is resolved.
    _az = p.get("loop_azim")
    if _az:
        _hh, _al = float(_az[0]), float(_az[1])
        _RR = a - _hh
        _rc = ((p["loop_strip"][0] / 2.0) if p.get("loop_strip")
               else p["loop_rw"])
        _vin = _rc / 2.0                    # resolve the conductor itself
        _rad = 2.0 * _rc
        _n = max(5, int(math.ceil(_al / _rad)) + 1)   # overlapping cover
        _pts = []
        for _i in range(_n):                # along the arc
            _t = -_al / (2.0 * _RR) + _i * (_al / _RR) / (_n - 1)
            _pts.append((_RR * math.cos(_t), _RR * math.sin(_t), 0.0))
        for _sgn in (+1.0, -1.0):           # and out along each leg
            _t = _sgn * _al / (2.0 * _RR)
            for _k in range(1, 4):
                _r = _RR + _k * (_hh / 3.0)
                _pts.append((_r * math.cos(_t), _r * math.sin(_t), 0.0))
        _flds = []
        for _x, _y, _z in _pts:
            _c, _s2 = math.cos(p["loop_phi"]), math.sin(p["loop_phi"])
            _xr, _yr = _x * _c - _y * _s2, _x * _s2 + _y * _c
            _b = gmsh.model.mesh.field.add("Ball")
            gmsh.model.mesh.field.setNumber(_b, "Radius", _rad)
            gmsh.model.mesh.field.setNumber(_b, "Thickness", 2.0 * _rad)
            gmsh.model.mesh.field.setNumber(_b, "VIn", _vin)
            gmsh.model.mesh.field.setNumber(_b, "VOut", h_air)
            gmsh.model.mesh.field.setNumber(_b, "XCenter", _xr)
            gmsh.model.mesh.field.setNumber(_b, "YCenter", _yr)
            gmsh.model.mesh.field.setNumber(_b, "ZCenter", _z)
            _flds.append(_b)
        _mn = gmsh.model.mesh.field.add("Min")
        gmsh.model.mesh.field.setNumbers(_mn, "FieldsList", [bg] + _flds)
        bg = _mn
        h_min = min(h_min, _vin * 0.8)
        print(f"  ARC refinement: {_vin*1e3:.3f} mm within {_rad*1e3:.1f} mm of "
              f"{len(_pts)} points along the conductor")
    gmsh.model.mesh.field.setAsBackgroundMesh(bg)

    def set_pts(tags, h):
        for t in tags:
            for d, pt in gmsh.model.getBoundary([(3, t)], recursive=True,
                                                oriented=False):
                if d == 0:
                    gmsh.model.mesh.setSize([(0, pt)], h)

    for tags in air_sectors:
        set_pts(tags, h_air)
    if filter_v:
        set_pts(sorted(filter_v), min(h_air, max(tb, 1.0e-3)))
    set_pts(sorted(torch_v), h_qtz)
    set_pts(sorted(bore_v), h_bore)
    if plasma_v:
        # R15. Without this the conductive region is meshed by the background
        # field alone, and the skin depth it is supposed to resolve is not a
        # length the mesher knows about.
        set_pts(sorted(plasma_v), p["plasma_h"] or h_bore)
    if up_v:
        set_pts(sorted(up_v), min(h_bore, p['inj_id']))

    gmsh.model.mesh.generate(3)

    # NOTE: gmsh's high-order optimiser can fail with a C++ std::runtime_error
    # ("Failed to reach critical value ... ScaledJac") that calls terminate().
    # It never becomes a Python exception, so try/except CANNOT catch it — the
    # process dies with SIGABRT (exit 134). The caller must treat a non-zero
    # exit as a mesh failure and retry with --size-factor or --order 1.
    # Perturbing the mesh size changes the element topology and almost always
    # dodges the pathological element.
    if msh_order > 1:
        # E0m: the HIGH-ORDER PASS is the non-deterministic stage. Geometric
        # order 1 is bit-identical across repeats; order 2 never is, differing
        # in ~2,540 node COORDINATES (~12 um) with identical topology. This
        # iterative optimiser is where the jitter enters, so it is exposed as a
        # flag rather than hardcoded — 2 keeps existing behaviour exactly.
        gmsh.option.setNumber("Mesh.HighOrderOptimize",
                              int(p.get("ho_optimize", 2)))
        gmsh.option.setNumber("Mesh.HighOrderPassMax", 25)
        gmsh.option.setNumber("Mesh.HighOrderIterMax", 200)
        gmsh.model.mesh.setOrder(msh_order)

    # Threshold is deliberately NOT zero. A curved element at minSICN 1e-5 is
    # not inverted, so a "v <= 0" test passes it, but it is degenerate enough
    # to destroy the conditioning of the eigensolve — a silent wrong answer
    # rather than a crash. Anything below SLIVER is treated as a defect.
    SLIVER = 1.0e-3

    def count_inverted():
        bad, worst = 0, 1.0
        for etype in gmsh.model.mesh.getElementTypes(3):
            tags, _ = gmsh.model.mesh.getElementsByType(etype)
            q = gmsh.model.mesh.getElementQualities(list(tags), "minSICN")
            bad += sum(1 for v in q if v < SLIVER)
            worst = min(worst, min(q) if len(q) else 1.0)
        return bad, worst

    bad, worst = count_inverted()
    for attempt in range(3):
        if bad == 0:
            break
        print(f"  {bad} degenerate elements (worst minSICN {worst:.2e}) — "
              f"repair pass {attempt + 1}")
        gmsh.model.mesh.optimize("HighOrderFastCurving", force=True)
        gmsh.model.mesh.optimize("HighOrder", force=True)
        bad, worst = count_inverted()

    if bad:
        sys.exit(f"ERROR: {bad} elements still degenerate (worst minSICN "
                 f"{worst:.2e}, need >{SLIVER:.0e}). Coarsen or use --order 1.")
    print(f"  jacobian check: OK — worst minSICN {worst:.3e}")

    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(out)

    _ETYPE = {1: 4, 2: 11, 3: 29, 4: 30}   # tet4 / tet10 / tet20 / tet35
    ne = len(gmsh.model.mesh.getElementsByType(_ETYPE[msh_order])[0])
    nn = len(gmsh.model.mesh.getNodes()[0])
    print(f"  mesh: {ne} tets, {nn} nodes, order {msh_order} -> {out}")
    _mat = ("SAPPHIRE" if abs(p["torch_eps"] - 11.6) < 0.3 else
            "quartz" if abs(p["torch_eps"] - 3.78) < 0.3 else "custom")
    print(f"  torch: {_mat}  eps={p['torch_eps']} tand={p['torch_tand']}")
    print(f"  domains: bore={TAG_BORE} torch={TAG_TORCH} "
          f"air={TAG_AIR0}..{TAG_AIR0 + ns - 1}"
          + (f" filter={TAG_FILTER}" if filter_v else "")
          + (f" upstream={TAG_UPSTREAM}" if up_v else "")
          + f"  pec={TAG_WALL}")

    # R50: write a SIDECAR so the mesh describes itself.
    #
    # The Palace config has to agree with the mesh on things the mesh already
    # knows, and every time that agreement was maintained by hand it eventually
    # broke:
    #   · R47 died in 7 s because the loop moved to phi = 36 deg while the port
    #     Direction stayed at the phi = 0 value copied between eight scripts.
    #     Palace refuses a direction that does not lie in the port face, so this
    #     one failed loudly — the next such mismatch might not.
    #   · a --filter 0 run leaves attribute 8 absent, and a config still binding a
    #     material to it is describing a model it is not solving.
    #   · the ACHIEVED size-factor is what matters for comparability, and only
    #     the mesher knows whether the requested one succeeded.
    #
    # Port direction is DERIVED here, from the loop the mesher actually built:
    #     dir = Rz(phi) . (0, cos tilt, sin tilt)
    # verified in R47 against Palace's own reported bounding-box axis.
    lt, lp = p["loop_tilt"], p["loop_phi"]
    meta = {
        "mesh": pathlib.Path(out).name,
        # 🔴 WHICH ATTRIBUTES ARE SURFACES, SAID STRUCTURALLY.
        # Consumers used to tell surfaces from volumes with a hardcoded
        # `k not in ("wall", "port")`, in THREE places. Adding `loop` on
        # 2026-08-27 therefore made a SURFACE be classified as a volume and
        # handed a vacuum material — and GATE 4, whose whole job is "no surface
        # reaches the solver by default", enumerated surfaces with the same
        # tuple and so was blind to exactly the attribute it needed to catch.
        # A list that must be remembered is not a mechanism. This is.
        # 🔴 REFLECT THE MESH, DO NOT ASSERT A CONSTANT. This was the literal
        # ["wall","port","loop"] regardless of what was built, so a mesh with
        # NO port face still advertised one — and `volume_attrs()` trusts this
        # list to tell surfaces from volumes, so a config could reference a
        # non-existent attribute 91. Caught 2026-09-02 on the first coax mesh,
        # which really did come out with only groups 90 and 92.
        # 🔴 KEY ON port_v, THE THING ACTUALLY TAGGED. `port_face` is the
        # fragment TOOL and is None for a coax feed, whose port is identified
        # among the exterior faces instead — keying on it would have reported
        # no port for a mesh that has one, the mirror of the bug this replaced.
        "surface_attributes": (["wall"]
                               + (["port"] if port_v else [])
                               + ["loop"]),
        "threads": max(1, int(p.get("threads", 1))),
        "port_direction": [-math.sin(lp) * math.cos(lt),
                           math.cos(lp) * math.cos(lt),
                           math.sin(lt)] if (p["loop_d"] > 0
                                             or p.get("loop_azim")) else None,
        "loop_phi_deg": math.degrees(lp),
        "loop_tilt_deg": math.degrees(lt),
        "sectors": ns,
        "attributes": {
            "bore": TAG_BORE, "torch": TAG_TORCH,
            "air": list(range(TAG_AIR0, TAG_AIR0 + ns)),
            "filter": TAG_FILTER if filter_v else None,
            "upstream": TAG_UPSTREAM if up_v else None,
            "plasma": (None if plasma_sec else
                       (TAG_PLASMA if plasma_v else None)),
            "plasma_sectors": plasma_sec or None,
            "groove": TAG_GROOVE if groove_v else None,
            "series_gap": TAG_GAP if gap_v else None,
            "wall": TAG_WALL, "port": TAG_PORT if port_v else None,
            # None when the loop was not split out (no loop, or a CAP loop,
            # where the z-extent rule does not hold). A consumer that binds
            # copper MUST check this rather than assume the attribute exists.
            "loop": TAG_LOOP if loop_faces else None,
        },
        # R62: a conductor-breaking flag MUST create new faces. A gap that
        # overlapped instead of separating left this at 23 both with and without
        # --loop-gap2, while Q_ext sat flat across every gap width. Two sweeps.
        "pec_surfaces": len(pec),
        "size_factor": p.get("size_factor", 1.0),
        "mesh_order": msh_order,
        "tets": ne, "nodes": nn,
        "geometry_mm": {
            "radius": a * 1e3, "length": L * 1e3,
            "filter_t": p["filter_t"] * 1e3, "ovality": p["ovality"] * 1e3,
            "chimney": [p["chim_d"] * 1e3, p["chim_len"] * 1e3],
            "feed": [p["feed_d"] * 1e3, p["feed_len"] * 1e3],
            "torch_ext": p["torch_ext"] * 1e3,
            "torch_ext_top": p["torch_ext_top"] * 1e3,
            "torch": [p["torch_od"] * 1e3, p["torch_wall"] * 1e3],
            "intermediate": [p["inter_od"] * 1e3, p["inter_wall"] * 1e3,
                             p["inter_end"] * 1e3],
            "injector": [p["inj_od"] * 1e3, p["inj_id"] * 1e3,
                         p["inj_end"] * 1e3],
            "offset": [x * 1e3 for x in (p.get("offset") or (0, 0, 0))],
            "air_coarsen": p.get("air_coarsen", 1.0),
            "rotate_deg": math.degrees(p.get("rotate") or 0.0),
            "rotate_axis": list(p.get("rotate_axis") or (0, 0, 1)),
            "torch_material": [p["torch_eps"], p["torch_tand"]],
            "viewport": [p["view_d"] * 1e3, p["view_len"] * 1e3,
                         math.degrees(p["view_phi"])],
            "trap": [p["trap_d"] * 1e3, p["trap_len"] * 1e3,
                     math.degrees(p["trap_phi"])],
            "groove": [p["groove_w"] * 1e3, p["groove_d"] * 1e3],
            # 🔴 THE LOOP'S SIZE WAS NEVER IN THE SIDECAR. `loop_mount`,
            # `loop_gap2`, `loop_cap_r`, `loop_flange_r`, `loop_phi_deg` and
            # `loop_tilt_deg` were all recorded — but not [ld, lw], the two
            # numbers that define the coupler. So when h3_driven's tags
            # collided on 2026-08-27 there was NOTHING in the artefact to bind
            # a point to its ld, and it took a re-mesh to do by measurement
            # what the sidecar should have carried. NEXT.md's fourth debt.
            "loop": [p["loop_d"] * 1e3, p["loop_w"] * 1e3,
                     p["loop_rw"] * 1e3, p["loop_gap"] * 1e3],
            # 🔑 [h_mm, arc_deg, unwound conductor mm, wall clearance mm].
            # The conductor length is DERIVED here, in the thing that built the
            # geometry, so no consumer has to re-derive it: two legs of h plus
            # the arc, less the port gap. The clearance h - lrw is the
            # conductor-to-wall gap — the capacitance that varies with h, and
            # the arc risk.
            # [h_mm, arc_mm, arc_deg, unwound_mm, wall clearance_mm].
            # 🔑 UNWOUND IS DERIVED HERE, in the thing that built the geometry:
            # the arc less its port gap, plus two legs of h. No consumer should
            # have to re-derive it — that omission is what forced a re-mesh to
            # bind ld back to its points on 2026-08-27.
            "loop_azim": ([p["loop_azim"][0] * 1e3,
                           p["loop_azim"][1] * 1e3,
                           math.degrees(p["loop_azim"][1]
                                        / (a - p["loop_azim"][0])),
                           (p["loop_azim"][1] - p["loop_gap"]
                            + 2 * p["loop_azim"][0]) * 1e3,
                           (p["loop_azim"][0]
                            - ((p["loop_strip"][1] / 2.0) if p.get("loop_strip")
                               else p["loop_rw"])) * 1e3]
                          if p.get("loop_azim") else None),
            # 🔑 NAMED, because the positional list above has been read wrong.
            # Its [0] is the CENTRELINE height; before 2026-08-30 that was also
            # what the --loop-azim INPUT meant, so wall clearance moved with
            # conductor thickness and wire/strip were never compared at the
            # same wall distance. The input is now the STANDOFF. Never infer
            # which one an "h" is — read these two fields.
            "loop_azim_standoff_mm": ((p["loop_azim"][0]
                                       - ((p["loop_strip"][1] / 2.0)
                                          if p.get("loop_strip")
                                          else p["loop_rw"])) * 1e3
                                      if p.get("loop_azim") else None),
            "loop_azim_centreline_mm": (p["loop_azim"][0] * 1e3
                                        if p.get("loop_azim") else None),
            # 🔑 THE PORT FACE, RECORDED. Q_ext depends on it strongly (4.5x
            # across the overshoot boundary), and it was NOT in the sidecar
            # while nine strip cases were measured against it.
            # 🔑 the coax, so solveconf can tell a wave port from a lumped one
            "loop_hole_mm": ([p["loop_hole"][0] * 1e3, p["loop_hole"][1] * 1e3]
                             if p.get("loop_hole") else None),
            "port_pw": (p.get("port_pw") or 0.9),
            "port_face_mm": _PORT_FACE_MM,
            # [axial_mm, radial_mm] or None for a round wire
            "loop_strip": ([p["loop_strip"][0] * 1e3, p["loop_strip"][1] * 1e3]
                           if p.get("loop_strip") else None),
            "arc_chords": p.get("arc_chords"),
            "plasma_h": p["plasma_h"] * 1e3,
            "loop_cap_r": p["loop_cap_r"] * 1e3,
            # 🔑 THREE MOUNTS NOW. This was a two-way cap/barrel choice, so an
            # azimuthal loop reported itself as "barrel" and h3_loopq's
            # mesh-is-what-you-ordered guard correctly refused the run:
            # "MOUNT MISMATCH: meshed 'barrel', requested 'azim'". The guard was
            # right; the sidecar was the thing that could not describe what it
            # had built.
            "loop_mount": ("azim" if p.get("loop_azim")
                           else "cap" if p["loop_cap_r"] > 0 else "barrel"),
            "loop_gap2": p["loop_gap2"] * 1e3,
            "loop_flange_r": p["loop_flange_r"] * 1e3,
        },
        # R50: the mesh SIZING actually applied, so a silent clamp is visible.
        # Mesh.MeshSizeMin is a hard floor — gmsh clamps every requested size to
        # it, including one asked for by a field — and that silently discarded
        # R15's 1.0 and 0.6 mm plasma refinements, which both came back as the
        # same 1.2 mm mesh while the run reported a convergence verdict.
        "sizing_mm": {
            "min": h_min * 1e3,
            "air": h_air * 1e3,
            "quartz": h_qtz * 1e3,
            "bore": h_bore * 1e3,
            "plasma_requested": p["plasma_h"] * 1e3 or None,
            "plasma_clamped": bool(p["plasma_h"] and p["plasma_h"] < h_min),
        },
    }
    side = pathlib.Path(out).with_suffix(".meta.json")
    side.write_text(json.dumps(meta, indent=2) + "\n")
    print(f"  sidecar: {side.name}"
          + (f"  port dir ({meta['port_direction'][0]:+.4f}, "
             f"{meta['port_direction'][1]:+.4f}, {meta['port_direction'][2]:+.4f})"
             if meta["port_direction"] else "  no port"))

    gmsh.finalize()


# ---------------------------------------------------------------------------
# MESH CACHE
#
# Meshing is no longer the cheap step. At 32 ranks an E1b case solves in ~4.3
# min and meshes in ~5.2 — the mesh is now the critical path, and we rebuild it
# byte-for-byte identically on every re-run of the same experiment.
#
# 🔑 This is a REUSE cache, not an approximation. A hit returns the exact file a
# rebuild would have produced, so it does not weaken METHODOLOGY 2b (same-mesh
# differencing) — it enforces it harder than rebuilding does, because a rebuild
# is only identical if nothing drifted, while a hit is identical by
# construction and verified by hash.
#
# THE KEY is the fully-resolved parameter dict P, the geometric order, the gmsh
# version, and the SHA-256 OF THIS FILE. Hashing P rather than argv means
# `--sectors 1` and `--azimuthal-bins 1` share an entry and flag order does not
# matter; hashing the source means any edit to the geometry code invalidates
# every entry, which is the property that makes the cache safe to leave on.
#
# Deleting meshcache/ is always safe: the next run rebuilds.
# ---------------------------------------------------------------------------
CACHE_VERSION = 1


def _cache_dir() -> pathlib.Path:
    d = os.environ.get("AMIP_MESH_CACHE")
    return (pathlib.Path(d) if d
            else pathlib.Path(__file__).resolve().parent / "meshcache")


def _sha_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def cache_key(p: dict, order: int) -> tuple:
    """(key, material). Everything that can change a mesh goes in the key."""
    material = {
        "cache_version": CACHE_VERSION,
        # default=repr so an unexpected type cannot silently collide with
        # another; it changes the key instead of raising or hashing as equal.
        "params": json.dumps(p, sort_keys=True, default=repr),
        "order": order,
        "gmsh_api": str(getattr(gmsh, "GMSH_API_VERSION", "unknown")),
        "geometry_py": _sha_file(pathlib.Path(__file__).resolve()),
    }
    blob = json.dumps(material, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest(), material


def cache_lookup(key: str, out: str):
    """Restore a hit to `out`. Returns True on hit, False on miss."""
    ent = _cache_dir() / key[:16]
    mesh, meta, rec = ent / "mesh.msh", ent / "meta.json", ent / "entry.json"
    if not (mesh.exists() and meta.exists() and rec.exists()):
        return False
    try:
        info = json.loads(rec.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"  cache: entry {key[:16]} unreadable ({e}) — rebuilding")
        return False
    # A cache that is trusted without checking is a way to make every future
    # run wrong at once. Verify before use; a corrupt entry is a miss, loudly.
    got = _sha_file(mesh)
    if got != info.get("mesh_sha256"):
        print(f"  🔴 cache: entry {key[:16]} CORRUPT (sha mismatch) — rebuilding")
        return False
    outp = pathlib.Path(out)
    shutil.copyfile(mesh, outp)
    m = json.loads(meta.read_text())
    m["mesh"] = outp.name
    m["from_cache"] = {"key": key[:16], "built": info.get("built"),
                       "mesh_sha256": got}
    outp.with_suffix(".meta.json").write_text(json.dumps(m, indent=2) + "\n")
    print(f"  ✅ cache HIT {key[:16]}  ({m.get('tets', 0):,} tets, built "
          f"{info.get('built', '?')}) — meshing skipped")
    return True


def cache_store(key: str, out: str, material: dict) -> None:
    ent = _cache_dir() / key[:16]
    outp = pathlib.Path(out)
    meta = outp.with_suffix(".meta.json")
    if not (outp.exists() and meta.exists()):
        return
    try:
        ent.parent.mkdir(parents=True, exist_ok=True)
        tmp = ent.with_name(ent.name + f".tmp{os.getpid()}")
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        shutil.copyfile(outp, tmp / "mesh.msh")
        shutil.copyfile(meta, tmp / "meta.json")
        (tmp / "entry.json").write_text(json.dumps({
            "key": key,
            "mesh_sha256": _sha_file(tmp / "mesh.msh"),
            "built": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "bytes": outp.stat().st_size,
            "material": material,
        }, indent=2) + "\n")
        # atomic: a reader sees a complete entry or no entry, never a torn one
        # (the same failure the journal was hardened against).
        if ent.exists():
            shutil.rmtree(ent, ignore_errors=True)
        os.replace(tmp, ent)
        print(f"  cache: stored {key[:16]} ({outp.stat().st_size/1e6:.1f} MB)")
    except OSError as e:
        # A cache is an optimisation. It must never be able to fail a run.
        print(f"  cache: store failed ({e}) — continuing")


def sanity_check(p: dict) -> None:
    """Analytic anchor. An FEM result far from this is a modelling error."""
    a, L = p["cav_r"], p["cav_len"]
    print("  sanity check (independent of FEM):")
    print(f"    TE01 cutoff radius   = {CHI01P / (2*math.pi*F0/C0)*1e3:.1f} mm "
          f"(have {a*1e3:.1f})")
    if a < CHI01P / (2 * math.pi * F0 / C0):
        print("    *** BELOW CUTOFF — TE01 cannot exist at 2.45 GHz ***")
    print(f"    TE011 (empty)        = {f_te011(a, L)/1e9:.4f} GHz")
    print(f"    TM111 (empty)        = {f_te011(a, L)/1e9:.4f} GHz  "
          f"<- exactly degenerate, by chi'_01 == chi_11")
    print("    The torch pulls both down slightly; the split between them is")
    print("    the number worth looking at.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="cav.msh")
    ap.add_argument("--radius", type=float, default=None, help="mm")
    ap.add_argument("--length", type=float, default=None, help="mm")
    # R50 rename: "sectors" reads as hardware — it misled the project's own
    # author into taking sectors=4 for a 4-port feed. They are azimuthal ENERGY
    # BINS: fictitious internal partitions of the air volume that exist only so
    # Palace reports energy per wedge, from which the mode's azimuthal index m
    # is inferred. They are NOT boundaries; tagging their planes PEC would turn
    # one cavity into N wedge resonators.
    ap.add_argument("--azimuthal-bins", dest="sectors", type=int, default=None,
                    help="azimuthal energy bins (5 resolves m=1..4). Bins are a "
                         "MEASUREMENT construct, not a feed or a boundary")
    ap.add_argument("--sectors", dest="sectors", type=int, default=None,
                    help="azimuthal energy sectors. 🔴 NOT 'm=1..4': energy "
                         "goes as cos^2(m*phi), so mode m lands on angular "
                         "harmonic k=2m, and with N sectors k folds to "
                         "min(k%%N, N-k%%N). At N=5, m=4 -> harmonic 2, the "
                         "SAME as m=1, and m=5 -> harmonic 0, the same as m=0. "
                         "N=5 separates only m=0,1,2; N=9 separates m=0..4. "
                         "Choose N from the m that physics.spectrum() says are "
                         "in the window, plus margin for slot/loop resonances "
                         "the closed form does not predict.")
    ap.add_argument("--no-torch", action="store_true",
                    help="omit the quartz tube (bore becomes plain air)")
    ap.add_argument("--loop-tilt", type=float, default=None,
                    help="loop tilt in degrees: 0=TE011 only, 90=TM020 only, 45=both")
    ap.add_argument("--viewport", type=float, default=None,
                    help="radial viewport diameter in mm")
    ap.add_argument("--loop", type=str, default=None,
                    help="d,w,rw,gap in mm — coupling loop for the driven model")
    ap.add_argument("--no-inner", action="store_true",
                    help="outer tube only — no intermediate, no injector")
    ap.add_argument("--striker", type=str, default=None,
                    help="h,r_tip,r_ring in mm")
    # R88: the torch was fully modelled (outer + intermediate + injector) but
    # every dimension lived in the parameter dict with no way to set it. Grouped
    # comma flags to match --groove / --plasma / --loop.
    ap.add_argument("--viewport-phi", type=float, default=None,
                    help="R57: viewport azimuth in DEGREES (default 180). Put it "
                         "on a sector centre — 108 at N=5 with the loop at 36")
    ap.add_argument("--trap", type=str, default=None,
                    help="R57: d,len,phi in mm,mm,deg — the LIGHT TRAP aperture, "
                         "which must sit diametrically opposite the viewport "
                         "(288 at N=5 with the viewport at 108)")
    ap.add_argument("--torch-tube", type=str, default=None,
                    help="R88: od,wall in mm — the OUTER tube (default 20,1.5)")
    ap.add_argument("--intermediate", type=str, default=None,
                    help="R88: od,wall,end in mm — the intermediate tube; end is "
                         "the absolute z where it stops, mid-plane = 0 "
                         "(default 16,1.0,-20). od=0 disables")
    ap.add_argument("--injector", type=str, default=None,
                    help="R88: od,id,end in mm — the injector; end is the tip's "
                         "absolute z (default 5,2,-25). od=0 disables")
    ap.add_argument("--rotate", type=float, default=None,
                    help="E0c: rigid rotation about z in DEGREES. For an "
                         "axisymmetric cavity this changes neither the physics "
                         "nor the solid — only the mesh. Pure instrument probe.")
    ap.add_argument("--air-coarsen", dest="air_coarsen", type=float,
                    default=None,
                    help="E1c: multiply the AIR element size only, leaving the "
                         "thin-wall floor untouched. Decouples the two scales "
                         "that a global --size-factor couples.")
    ap.add_argument("--rotate-axis", dest="rotate_axis", type=str,
                    default=None,
                    help="E0d: x, y or z (default z, the cavity axis). A "
                         "TRANSVERSE axis tilts the cavity off the coordinate "
                         "axis — the strongest rigid-motion probe available.")
    ap.add_argument("--offset", type=str, default=None,
                    help="R109: dx,dy,dz in mm — RIGID translation of the whole "
                         "model. Physics is exactly invariant, so any change in "
                         "a result is pure mesh artifact. Use it to probe the "
                         "noise floor; an x/y shift is the only probe that sees "
                         "artifacts sitting ON the symmetry axis.")
    ap.add_argument("--torch-material", type=str, default=None,
                    help="R88: eps_r,tand — 11.6,3.5e-5 sapphire (DEFAULT, R99); "
                         "3.78,1e-4 quartz for the development build. R98: "
                         "11.6 is eps_PERP_c — what "
                         "E_phi sees with the c-axis longitudinal (R32 "
                         "measured it reproduces isotropic 11.6 exactly). "
                         "9.4 is eps_PARALLEL_c: 23%% low for our field. "
                         "🔴 2026-08-25 RESOLVED: THIS AXIS ASSIGNMENT IS "
                         "WRONG. Krupka et al., Meas. Sci. Technol. 16 (2005) "
                         "1014, fig 10, measured eps PERPENDICULAR to the "
                         "anisotropy axis = 9.39 +-0.5%% for single-crystal "
                         "sapphire, by TE0np modes in a cylindrical sample. So "
                         "eps_PERP_c = 9.39 and 11.6 is eps_PARALLEL_c. TE011's "
                         "E_phi sees the PERPENDICULAR component, i.e. 9.39. "
                         "R32 could not arbitrate: its 'c-longitudinal "
                         "reproduces isotropic 11.6' only confirms the "
                         "simulation used 11.6 perpendicular, the assumption "
                         "under test. See baselines.json.")
    ap.add_argument("--plasma-sectors", dest="plasma_sectors",
                    action="store_true",
                    help="R83: split the plasma toroid into the same number of "
                         "azimuthal sectors as the air, so the UNIFORMITY OF "
                         "POWER DEPOSITION around it can be measured. Requires "
                         "--plasma and --sectors > 1.")
    ap.add_argument("--tag-groove", dest="tag_groove",
                    action="store_true",
                    help="R81: give the groove its own attribute so the energy "
                         "fraction INSIDE the slot can be measured rather than "
                         "inferred. Changes the mesh partitioning, so do not "
                         "compare Q across it.")
    ap.add_argument("--groove", type=str, default=None,
                    help="R54: w,depth in mm — circumferential mode-filter "
                         "groove at the cap/barrel corner, both end caps")
    # 🔴 --loop-azim WAS CENTRELINE HEIGHT AND IS NOW REFUSED (2026-08-30).
    # It is kept ONLY so an old config fails loudly instead of silently meaning
    # something new. Renaming rather than redefining is the lesson of the
    # groove omission, where a stale label rode a renumbering onto a live
    # result and 31 rigs measured the wrong cavity.
    ap.add_argument("--loop-azim", default=None, metavar="REFUSED",
                    help="🔴 REFUSED. h was the conductor CENTRELINE height, so "
                         "wall clearance was h - t/2 and MOVED with conductor "
                         "thickness — wire and strip were never compared at the "
                         "same wall distance. Use --loop-azim-standoff, whose "
                         "first value is the STUD HEIGHT (the wall gap itself). "
                         "To convert an old value: standoff = h - t/2, i.e. "
                         "h - rw for a round wire, h - radial/2 for a strip.")
    ap.add_argument("--loop-hole", default=None, metavar="r_mm,stub_mm",
                    help="COAX ENTRY: a radial clearance tube of radius r_mm "
                         "through the barrel wall at the FEED leg's azimuth, "
                         "extending stub_mm outside. The leg passes through as "
                         "the inner conductor. Without it the leg is trimmed "
                         "at the wall and grounded — a mid-arc-driven loop, "
                         "which is what every run before 2026-09-01 used. "
                         "🔑 Same circuit class (series-fed loop returning "
                         "through the wall); it moves the source ~26 deg "
                         "around a lambda/6.8 loop and puts the port reference "
                         "plane AT THE WALL, where VSWR is actually measured.")
    ap.add_argument("--loop-azim-standoff", default=None, metavar="standoff_mm,arc_mm",
                    help="AZIMUTHAL loop: an arc of length arc_mm at "
                         "r = a - h_mm, closed to the wall by two radial legs. "
                         "🔑 ARC LENGTH, not angle — that is what makes h and L "
                         "INDEPENDENT, since a fixed angle at different h is a "
                         "different length. Unwound conductor = arc + 2h. "
                         "Mutually exclusive with --loop-cap; refuses "
                         "--loop-gap2.")
    ap.add_argument("--loop-strip", default=None, metavar="axial_mm,radial_mm",
                    help="Rectangular conductor instead of round wire, e.g. "
                         "5,1 for a 5x1 mm strip. The AXIAL dimension is the "
                         "wide one, so the broad face lies parallel to the "
                         "wall. Default: round wire of radius --loop rw.")
    ap.add_argument("--dump-faces", action="store_true",
                    help="DIAGNOSTIC: print the exterior CAD-face inventory "
                         "(tag, type, area, centroid, extent) and continue. "
                         "Changes no geometry.")
    ap.add_argument("--loop-gap2", type=float, default=None,
                    help="R62: second gap in a loop leg, mm — the SERIES "
                         "capacitor that tunes out loop self-reactance")
    ap.add_argument("--loop-flange", type=float, default=None,
                    help="R62: flange disc radius at the capacitor gap, mm — "
                         "raises C by AREA at a meshable gap width")
    ap.add_argument("--loop-cap", type=float, default=None,
                    help="R69: mount the loop on the -z END CAP at this radius "
                         "in mm instead of on the barrel wall. Links H_r, not "
                         "H_z. Radius is a free variable here; on the barrel it "
                         "is forced to a, the only E_phi null in the barrel. "
                         "H_r peaks at 0.4805a = 49.83 mm")
    ap.add_argument("--loop-phi", type=float, default=None,
                    help="R47: loop azimuth in degrees. At --sectors 5 the "
                         "sector planes are at 0/72/144/... and the loop at 0 "
                         "straddles one, splitting the port face; put it at a "
                         "sector CENTRE (36) instead")
    ap.add_argument("--feed", type=str, default=None,
                    help="R49: d,len in mm — gas-feed feedthrough tube on the "
                         "-z end cap, below cutoff, terminated PEC")
    ap.add_argument("--torch-ext-top", type=float, default=None,
                    help="extend the outer tube ABOVE the +z cap by mm, so it "
                         "passes through the chimney instead of butting against "
                         "it. Required whenever --chimney is used with a torch.")
    ap.add_argument("--torch-ext", type=float, default=None,
                    help="R49: extend the outer tube below the -z cap by mm, "
                         "dielectrically loading the feed aperture")
    ap.add_argument("--bore-h", type=float, default=None,
                    help="bore mesh size in mm (default 5)")
    ap.add_argument("--plasma-h", type=float, default=None,
                    help="R15: mesh size in mm inside the R12 plasma "
                         "sub-region; must resolve the RF skin depth")
    ap.add_argument("--chimney", type=str, default=None,
                    help="R29: d,len in mm — axial exhaust chimney on the "
                         "+z end cap, below cutoff, terminated PEC")
    ap.add_argument("--ovality", type=float, default=None,
                    help="R36: peak radial deviation in mm — the bore becomes "
                         "an ellipse, semi-axes a+ov and a-ov")
    # R50 rename: the part is a MODE FILTER (entry 85). "Dielectric filter" was
    # this project's own coinage and maps onto no RF literature or vendor
    # vocabulary. Old flag kept as an alias so the ~18 closed drivers that are
    # the evidence trail remain runnable.
    ap.add_argument("--mode-filter", dest="mode_filter", type=float,
                    default=None,
                    help="mode filter thickness per end cap, mm (quartz annulus "
                         "that separates TE011 from TM111)")
    ap.add_argument("--brake", dest="mode_filter", type=float, default=None,
                    help="R111 DEPRECATED alias for --mode-filter. The part is a "
                         "MODE FILTER; it was never a brake. Kept only so the "
                         "closed evidence-trail drivers still run.")
    ap.add_argument("--filter-eps", dest="filter_eps", type=float, default=None,
                    help="mode-filter relative permittivity (default fused "
                         "quartz 3.78; R107 measured sapphire as 9.2%% WORSE)")
    ap.add_argument("--electrode", type=str, default=None,
                    help="R21: zc,w,t in mm — capacitive band at the torch OD")
    ap.add_argument("--plasma", type=str, default=None,
                    help="R12: ri,ro,zlo,zhi in mm — conductive sub-region in the bore")
    ap.add_argument("--size-factor", type=float, default=None,
                    help="scale all mesh sizes; perturb to dodge "
                         "a curving failure")
    ap.add_argument("--n-wl", type=float, default=None)
    ap.add_argument("--order", type=int, default=2, choices=(1, 2, 3, 4),
                    help="GEOMETRIC mesh order — how closely the "
                         "elements follow the true cylinder. Distinct "
                         "from the SOLVER order. E0f: order 1 chords "
                         "the circle (reads too small, f high); order "
                         "2+ curves to it.")
    ap.add_argument("--ho-optimize", dest="ho_optimize", type=int, default=2,
                    choices=(0, 1, 2, 3, 4),
                    help="Mesh.HighOrderOptimize. Default 2 (unchanged). E0m "
                         "found this pass is why two identical commands produce "
                         "different meshes; 0 disables it.")
    ap.add_argument("--no-cache", dest="no_cache", action="store_true",
                    help="rebuild the mesh even if an identical one is cached, "
                         "and do not store the result. The cache is keyed on "
                         "the resolved parameters AND the sha256 of this file, "
                         "so a hit is the same mesh a rebuild would produce; "
                         "use this only to test that claim.")
    ap.add_argument("--threads", type=int, default=1,
                    help="gmsh meshing threads (General.NumThreads). Default "
                         "1 so meshes stay byte-reproducible; >1 is only safe "
                         "once ops/gmshcaps.sh --determinism has confirmed it "
                         "for this geometry.")
    a = ap.parse_args()

    # R50: name the old flags where they are used, without breaking them.
    _old = [f for f in ("--filter", "--sectors") if f in sys.argv]
    if _old:
        print("  note: " + ", ".join(_old) + " is a deprecated alias for "
              + ", ".join({"--filter": "--mode-filter",
                           "--sectors": "--azimuthal-bins"}[f] for f in _old)
              + " (R50); both work")

    P["threads"] = a.threads
    # 🔴 P IS BUILT BY EXPLICIT ASSIGNMENT, NOT vars(a). A new flag that is not
    # copied here reaches build() as a MISSING KEY and its feature silently
    # never runs — the same "declared with no consumer" shape as
    # loop.conductivity.s_per_m. Adding the argparse entry is half the change.
    P["dump_faces"] = a.dump_faces
    P["arc_chords"] = (int(os.environ["AMIP_ARC_CHORDS"])
                       if os.environ.get("AMIP_ARC_CHORDS") else None)
    P["port_pw"] = (float(os.environ["AMIP_PORT_PW"])
                    if os.environ.get("AMIP_PORT_PW") else None)
    if a.loop_azim:
        sys.exit(
            "ERROR: --loop-azim is REFUSED. Its h was the conductor CENTRELINE "
            "height, so the wall clearance was h - t/2 and changed with "
            "conductor thickness — a wire and a strip at the same h sat at "
            "DIFFERENT wall distances, which confounded every cross-section "
            "comparison made before 2026-08-30.\n"
            "  Use --loop-azim-standoff, whose first value is the STUD HEIGHT, "
            "i.e. the wall gap itself; the conductor then grows AWAY from the "
            "wall and the gap is invariant under thickness.\n"
            "  Convert: standoff = h - rw (round wire) or h - radial/2 (strip).")
    if a.loop_azim_standoff:
        _hh, _aa = (float(x) for x in a.loop_azim_standoff.split(","))
        # 🔑 (STANDOFF, ARC LENGTH) — both metres. The standoff is the WALL GAP;
        # the centreline is derived downstream as standoff + t/2, so wall
        # distance is invariant under conductor cross-section BY CONSTRUCTION.
        P["loop_azim_standoff"] = (_hh * 1e-3, _aa * 1e-3)
        # the arc IS the loop, so a radial depth would be a second one
        P["loop_d"] = 0.0
    P["loop_strip"] = (tuple(float(x) * 1e-3 for x in a.loop_strip.split(","))
                       if a.loop_strip else None)
    P["loop_hole"] = (tuple(float(x) * 1e-3 for x in a.loop_hole.split(","))
                      if a.loop_hole else None)
    P["ho_optimize"] = a.ho_optimize
    if a.radius is not None:
        P["cav_r"] = a.radius * 1e-3
    if a.length is not None:
        P["cav_len"] = a.length * 1e-3
    if a.sectors is not None:
        P["sectors"] = a.sectors
    if a.n_wl is not None:
        P["elems_per_wl"] = a.n_wl
    # 🔴 numeric flag: 0 is falsy. Harmless today because the default IS 0 —
    # which is exactly the state --viewport was in before its default changed
    # and the flag silently stopped working.
    if a.loop_tilt is not None:
        P['loop_tilt'] = math.radians(a.loop_tilt)
    # 🔴 R113: `if a.viewport:` — 0.0 is FALSY, so `--viewport 0` was silently
    # ignored. Harmless while the default was 0; the moment R98 flipped the
    # default to 10 mm it became "this flag cannot turn the feature off", and
    # R112 benchmarked a cavity with a 10 mm stub in it against a closed form
    # for a right circular cylinder. Guard numeric flags on `is not None`.
    if a.viewport is not None:
        P['view_d'] = a.viewport * 1e-3
    if a.loop:
        d, w, rw, g = (float(v) for v in a.loop.split(','))
        P['loop_d'], P['loop_w'] = d*1e-3, w*1e-3
        P['loop_rw'], P['loop_gap'] = rw*1e-3, g*1e-3
    if a.electrode:
        zc, w, t = (float(v) for v in a.electrode.split(","))
        P['el_zc'], P['el_w'], P['el_t'] = zc*1e-3, w*1e-3, t*1e-3
    if a.plasma:
        ri, ro, zlo, zhi = (float(v) for v in a.plasma.split(","))
        P['pl_ri'], P['pl_ro'] = ri*1e-3, ro*1e-3
        P['pl_zlo'], P['pl_zhi'] = zlo*1e-3, zhi*1e-3
    if a.no_inner:
        P['inter_od'] = 0.0
        P['inj_od'] = 0.0
    if a.striker:
        h, rt, rr = (float(v) for v in a.striker.split(','))
        P['striker_h'], P['striker_rtip'], P['striker_r'] = (
            h * 1e-3, rt * 1e-3, rr * 1e-3)
    # R88 torch geometry. Validated rather than trusted: three concentric tubes
    # that overlap, or a tube wall thicker than its own radius, produce a mesh
    # that is geometrically nonsense but solves happily.
    def _mm(spec, n, name):
        v = [float(x) for x in spec.split(",")]
        if len(v) != n:
            sys.exit(f"ERROR: {name} needs {n} comma-separated values, got {len(v)}")
        return v
    if a.torch_tube:
        od, w = _mm(a.torch_tube, 2, "--torch-tube")
        if w <= 0 or w >= od / 2:
            sys.exit(f"ERROR: --torch-tube wall {w} must be >0 and < od/2 ({od/2})")
        P["torch_od"], P["torch_wall"] = od * 1e-3, w * 1e-3
    if a.intermediate:
        od, w, ze = _mm(a.intermediate, 3, "--intermediate")
        if od > 0 and (w <= 0 or w >= od / 2):
            sys.exit(f"ERROR: --intermediate wall {w} must be >0 and < od/2")
        P["inter_od"], P["inter_wall"], P["inter_end"] = (od * 1e-3, w * 1e-3,
                                                          ze * 1e-3)
    if a.injector:
        od, idd, ze = _mm(a.injector, 3, "--injector")
        if od > 0 and not (0 <= idd < od):
            sys.exit(f"ERROR: --injector id {idd} must be >=0 and < od {od}")
        P["inj_od"], P["inj_id"], P["inj_end"] = od * 1e-3, idd * 1e-3, ze * 1e-3
    if a.air_coarsen is not None:
        P["air_coarsen"] = a.air_coarsen
    if a.rotate_axis is not None:
        P["rotate_axis"] = {"x": (1.0, 0.0, 0.0), "y": (0.0, 1.0, 0.0),
                            "z": (0.0, 0.0, 1.0)}[a.rotate_axis.strip().lower()]
    if a.rotate is not None:
        P["rotate"] = math.radians(a.rotate)
    if a.offset:
        dx, dy, dz = _mm(a.offset, 3, "--offset")
        P["offset"] = (dx * 1e-3, dy * 1e-3, dz * 1e-3)
    if a.torch_material:
        eps, td = _mm(a.torch_material, 2, "--torch-material")
        P["torch_eps"], P["torch_tand"] = eps, td
    # concentricity: injector inside intermediate inside outer, with clearance
    _tri = P["torch_od"] / 2 - P["torch_wall"]
    if P["inter_od"] > 0 and P["inter_od"] / 2 >= _tri:
        sys.exit(f"ERROR: intermediate OD/2 ({1e3*P['inter_od']/2:.2f} mm) must "
                 f"be inside the outer tube bore ({1e3*_tri:.2f} mm)")
    if P["inj_od"] > 0 and P["inter_od"] > 0:
        _iri = P["inter_od"] / 2 - P["inter_wall"]
        if P["inj_od"] / 2 >= _iri:
            sys.exit(f"ERROR: injector OD/2 ({1e3*P['inj_od']/2:.2f} mm) must be "
                     f"inside the intermediate bore ({1e3*_iri:.2f} mm)")

    if a.viewport_phi is not None:
        P["view_phi"] = math.radians(a.viewport_phi)
    if a.trap:
        td, tl, tp = _mm(a.trap, 3, "--trap")
        if td > 0 and a.viewport is None and P["view_d"] <= 0:
            sys.exit("ERROR: --trap without a viewport. The trap exists to be the "
                     "dark background BEHIND the plasma as seen through the "
                     "viewport; alone it is just a hole in the cavity.")
        P["trap_d"], P["trap_len"], P["trap_phi"] = (td * 1e-3, tl * 1e-3,
                                                     math.radians(tp))
    P["tag_groove"] = bool(a.tag_groove)
    P["plasma_sectors"] = bool(a.plasma_sectors)
    if a.plasma_sectors and not a.plasma:
        sys.exit("ERROR: --plasma-sectors without --plasma: nothing to sector.")
    if a.plasma_sectors and (a.sectors or 1) < 2:
        sys.exit("ERROR: --plasma-sectors needs --sectors > 1; deposition "
                 "uniformity around a torus cannot be measured in one bin.")
    if a.tag_groove and not a.groove:
        sys.exit("ERROR: --tag-groove without --groove: nothing to tag.")
    if a.groove:
        gw, gd = (float(v) for v in a.groove.split(","))
        P["groove_w"], P["groove_d"] = gw * 1e-3, gd * 1e-3
    if a.loop_cap is not None:
        P['loop_cap_r'] = a.loop_cap * 1e-3
    if a.loop_flange is not None:
        P["loop_flange_r"] = a.loop_flange * 1e-3
    if a.loop_gap2 is not None:
        P["loop_gap2"] = a.loop_gap2 * 1e-3
    if a.loop_phi is not None:
        P["loop_phi"] = math.radians(a.loop_phi)
    if a.feed:
        fd, fl = (float(v) for v in a.feed.split(","))
        P["feed_d"], P["feed_len"] = fd * 1e-3, fl * 1e-3
    if a.torch_ext_top is not None:
        P["torch_ext_top"] = a.torch_ext_top * 1e-3
    if a.torch_ext is not None:
        P["torch_ext"] = a.torch_ext * 1e-3
    if a.bore_h is not None:
        P["bore_h"] = a.bore_h * 1e-3
    if a.plasma_h is not None:
        P["plasma_h"] = a.plasma_h * 1e-3
    if a.chimney:
        cd, cl = (float(v) for v in a.chimney.split(","))
        P["chim_d"], P["chim_len"] = cd * 1e-3, cl * 1e-3
    if a.ovality is not None:
        P["ovality"] = a.ovality * 1e-3
    if a.mode_filter is not None:
        P["filter_t"] = a.mode_filter * 1e-3
    if a.filter_eps is not None:
        P["filter_eps"] = a.filter_eps
    if a.size_factor is not None:
        P["size_factor"] = a.size_factor
    if a.no_torch:
        P["torch_eps"] = 1.0

    print("TE011 cavity geometry")
    print(f"  cavity {P['cav_r']*2e3:.1f} mm dia x {P['cav_len']*1e3:.1f} mm  "
          f"({P['sectors']} sectors)"
          + (f"  filter {P['filter_t']*1e3:.1f} mm eps_r {P['filter_eps']}"
             if P['filter_t'] > 0 else "  no filter"))
    sanity_check(P)

    key, material = cache_key(P, a.order)
    if a.no_cache:
        print(f"  cache: bypassed (--no-cache), key would be {key[:16]}")
        build(P, a.out, a.order)
    elif not cache_lookup(key, a.out):
        t0 = time.time()
        build(P, a.out, a.order)
        print(f"  meshed in {time.time() - t0:.1f}s")
        cache_store(key, a.out, material)
