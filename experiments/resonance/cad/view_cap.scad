// CAP MOUNT — the loop lies in a radial plane, normal r-hat, so it links H_r.
// H_r is what survives at an end cap (H_z is normal there and must vanish),
// and it peaks at r = 0.4805 * a, which is where this loop is parked.
//
// 🔑 The RADIUS IS FREE here, which was the argument for preferring this mount.
// 🔴 But the "1.39x stronger" number attached to that argument was computed on
//    the LEGACY cavity (D/L 2.343). On H1's cavity the true ratio is 0.903 —
//    the BARREL is stronger — and the eigen pair agrees:
//    MEASURED Q_ext = 9,231 (cap) vs 8,716 (barrel).
include <amip.scad>
cavity(cut = true);
cap_loop();
h_field();
