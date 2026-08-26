// amip.scad — module library for the AMIP TE011 cavity and its coupling loop.
//
// Mirrors geometry.py's ACTUAL construction, not a stylised version:
//   * barrel loop  : a U in the z = 0 plane, legs RADIAL, normal z-hat -> links H_z
//   * cap loop     : a U in a radial plane, legs AXIAL,  normal r-hat -> links H_r
//   * series cap   : a break in the -y leg ONLY, with a flange disc each side
//   * groove       : a corner ring, OUTWARD past each end cap
//
// Dimensions come from amip_params.scad, which is generated from baselines.json.
// Nothing here is a literal dimension.

include <amip_params.scad>

$fa = 2;
$fs = 0.6;

C_WALL   = [0.62, 0.66, 0.70, 0.14];   // cavity air, translucent
C_COPPER = [0.72, 0.45, 0.20];         // the loop
C_FLANGE = [0.95, 0.75, 0.25];         // capacitor discs
C_PORT   = [0.20, 0.70, 0.95];         // the driven gap
C_FIELD  = [0.30, 0.55, 0.95, 0.55];   // H-field indicators

// a rod between two points — used for every conductor segment
module rod(p1, p2, r) {
    d = [p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]];
    len = norm(d);
    if (len > 1e-9)
        translate(p1)
            rotate([0, acos(d[2]/len), atan2(d[1], d[0])])
                cylinder(h = len, r = r);
}

// a disc of radius r and thickness t, centred at p, axis along +x
module disc_x(p, r, t) { rod(p, [p[0]+t, p[1], p[2]], r); }

// ── the cavity air volume, including the corner grooves ─────────────────────
module cavity_air() {
    union() {
        cylinder(h = cav_l, r = cav_r, center = true);
        // the mode filter: a ring beyond EACH end cap, groove_w wide, groove_d deep
        for (s = [-1, 1])
            translate([0, 0, s * (cav_l/2 + groove_d/2)])
                difference() {
                    cylinder(h = groove_d, r = cav_r, center = true);
                    cylinder(h = groove_d + 1, r = cav_r - groove_w, center = true);
                }
    }
}

// quarter-cut so the interior is visible; cut=false gives the whole volume
module cavity(cut = true) {
    color(C_WALL)
        if (cut)
            difference() {
                cavity_air();
                translate([0, -cav_r*2, -cav_l])
                    cube([cav_r*2, cav_r*2, cav_l*3]);
            }
        else cavity_air();
}

// ── BARREL loop: legs radial (along x) at y = +/-loop_hw, in the z = 0 plane ──
// with_cap = true breaks the -y leg and adds the flange discs.
module barrel_loop(with_cap = false) {
    xm = (barrel_xo + barrel_xi) / 2;      // capacitor sits mid-leg
    rotate([0, 0, loop_phi]) {
        color(C_COPPER) {
            // +y leg: always solid
            rod([barrel_xo, loop_hw, 0], [barrel_xi, loop_hw, 0], loop_rw);
            // -y leg: solid, or broken by the series capacitor
            if (with_cap) {
                // ⚠️ x DECREASES along the leg. The OUTER piece ends at the
                // HIGHER x of the gap; reversing this makes the pieces OVERLAP
                // by gap2 and the conductor stays continuous (attempt 2).
                rod([barrel_xo, -loop_hw, 0], [xm + gap2/2, -loop_hw, 0], loop_rw);
                rod([xm - gap2/2, -loop_hw, 0], [barrel_xi, -loop_hw, 0], loop_rw);
            } else {
                rod([barrel_xo, -loop_hw, 0], [barrel_xi, -loop_hw, 0], loop_rw);
            }
            // crossbar at x = barrel_xi, split by the PORT gap at mid-span
            rod([barrel_xi, -loop_hw, 0], [barrel_xi, -loop_gap/2, 0], loop_rw);
            rod([barrel_xi,  loop_gap/2, 0], [barrel_xi, loop_hw, 0], loop_rw);
        }
        if (with_cap)
            color(C_FLANGE) {
                disc_x([xm + gap2/2, -loop_hw, 0], flange_r, flange_t);
                disc_x([xm - gap2/2 - flange_t, -loop_hw, 0], flange_r, flange_t);
            }
        color(C_PORT)
            translate([barrel_xi, 0, 0]) cube([loop_rw*1.8, loop_gap, 0.4], center = true);
    }
}

// ── CAP loop: legs axial (along z) at r = cap_r, y = +/-loop_hw ──────────────
// Rises from just outside the -z cap to loop_d INSIDE it.
module cap_loop() {
    zo = -cav_l/2 - 2;
    zi = -cav_l/2 + loop_d;
    rotate([0, 0, loop_phi]) {
        color(C_COPPER) {
            rod([cap_r, -loop_hw, zo], [cap_r, -loop_hw, zi], loop_rw);
            rod([cap_r,  loop_hw, zo], [cap_r,  loop_hw, zi], loop_rw);
            rod([cap_r, -loop_hw, zi], [cap_r, -loop_gap/2, zi], loop_rw);
            rod([cap_r,  loop_gap/2, zi], [cap_r, loop_hw, zi], loop_rw);
        }
        color(C_PORT)
            translate([cap_r, 0, zi]) cube([loop_rw*1.8, loop_gap, 0.4], center = true);
    }
}

// ── field indicators ────────────────────────────────────────────────────────
module arrow(p, dir, len, r) {
    d = dir / norm(dir);
    tip = [p[0]+d[0]*len, p[1]+d[1]*len, p[2]+d[2]*len];
    rod(p, tip, r);
    translate(tip) rotate([0, acos(d[2]), atan2(d[1], d[0])])
        cylinder(h = r*4, r1 = r*2.2, r2 = 0);
}

// H_z lives at the MID-PLANE and is all that survives at the barrel wall.
// H_r lives at the END CAPS and vanishes at the mid-plane.
module h_field(n = 16) {
    color(C_FIELD) {
        for (i = [0:n-1]) {
            th = i * 360 / n;
            rotate([0, 0, th])
                arrow([cav_r - 3, 0, -14], [0, 0, 1], 28, 0.8);   // H_z at the wall
        }
        for (i = [0:n-1]) {
            th = i * 360 / n;
            rotate([0, 0, th]) {
                arrow([cav_r*cap_r_frac - 14, 0, -cav_l/2 + 3], [1, 0, 0], 28, 0.8);
                arrow([cav_r*cap_r_frac + 14, 0,  cav_l/2 - 3], [-1, 0, 0], 28, 0.8);
            }
        }
    }
}

module axes(len = 120) {
    color([0.9,0.2,0.2]) rod([0,0,0],[len,0,0],0.5);
    color([0.2,0.8,0.2]) rod([0,0,0],[0,len,0],0.5);
    color([0.3,0.4,0.9]) rod([0,0,0],[0,0,len],0.5);
}
