// BARREL MOUNT — the loop lies in the z = 0 mid-plane, normal z-hat, so it
// links H_z. That is the ONLY field component surviving at the barrel wall:
// H_r must vanish there (it is normal to the conductor), and J1(x'01) = 0
// says so exactly.
//
// The radius is NOT free here — the wall is the only place it can sit.
// MEASURED Q_ext = 8,716  (h3-loop-barrel-01, 2026-08-25)
include <amip.scad>
cavity(cut = true);
barrel_loop(with_cap = false);
h_field();
