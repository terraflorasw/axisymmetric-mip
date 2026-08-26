// THE SERIES CAPACITOR — step 2 of item 7, and the whole 45x lever.
//
// The loop is an inductor: ~332 ohm of reactance at 2.45 GHz. Most of the drive
// voltage is spent pushing against that instead of driving CURRENT around the
// loop, and current is what links flux. Break the conductor and put a capacitor
// in SERIES; when X_C = X_L the loop is series-resonant, current jumps, and
// coupled power rises ~45x.
//
// It goes in the -y LEG, never the crossbar: the crossbar already carries the
// PORT gap, and two breaks in one segment would put the capacitor in series
// with the port rather than with the loop.
//
// 0.196 pF cancels 332 ohm. A bare 1 mm wire end across 0.5 mm gives only
// 0.056 pF — that is why attempt 1 made things WORSE. The FLANGES raise C by
// AREA (C = eps0*A/d) at a gap width that still meshes and will not arc.
include <amip.scad>
xm = (barrel_xo + barrel_xi) / 2;
translate([-xm, loop_hw, 0]) rotate([0, 0, -loop_phi]) {
    barrel_loop(with_cap = true);
    color([0.1,0.1,0.1]) translate([0,0,-8]) linear_extrude(0.4)
        rotate([0,0,loop_phi]) translate([xm, -loop_hw, 0])
            text(str("gap2 = ", gap2, " mm   flange_r = ", flange_r, " mm"),
                 size = 2, halign = "center");
}
