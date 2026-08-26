// Both mounts in one view, at the same scale, for comparison.
// Barrel loop drawn at phi = 36 deg; cap loop offset to phi = 216 deg so the
// two do not overlap. Neither is drawn with the capacitor.
include <amip.scad>
cavity(cut = true);
barrel_loop(with_cap = false);
rotate([0, 0, 180]) cap_loop();
axes();
