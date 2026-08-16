#!/usr/bin/env python
"""Compare the two Barton-Bandis friction parameterizations now in use.

    /home/geomechanics/miniforge/bin/python scripts/friction_envelope_compare.py

The four sample decks split into two families that were calibrated
independently and ended up attributing shear strength to DIFFERENT terms of the
same law:

    phi_peak = phi_r + JRC * log10(JCS / sigma'_n)      (clamped at 85 deg)
    tau_lim  = sigma'_n * tan(phi_peak)

    S-family (SW-S3, SW-S4):  phi_r = 7.5 deg,  JCS = 300 MPa
    T-family (SW-T1, SW-T2):  phi_r = 44-46 deg, JCS = 150 MPa

Both families reproduce their own measured tau, so the peak values alone cannot
distinguish them.  What distinguishes them is the STRESS SENSITIVITY.  phi_r is
constant; the roughness term JRC*log10(JCS/sigma'_n) grows as sigma'_n falls.
The S-family draws most of its friction from the stress-dependent term and the
T-family from the constant term, so the two predict different responses to the
one thing this study is about: injection lowering sigma'_n.

d(tau)/d(sigma'_n) is the quantity that matters for slip onset and for how far
slip runs once it starts.  This script tabulates it.

All four decks set use_mobilized_jrc = false, use_scale_correction = false and
pore_pressure_strength_coefficient = 0, so the law above is exactly what each
one evaluates and the comparison is like-for-like.
"""

from math import degrees, log10, pi, radians, tan

MAX_FRICTION_DEG = 85.0  # source default, none of the decks override it

# name, phi_r [deg], JRC, JCS [Pa], representative sigma'_n operating range [MPa]
FAMILIES = [
    ("SW-S3", 7.5, 23.35, 3.0e8, (15.0, 33.0)),
    ("SW-S4", 7.5, 17.50, 3.0e8, (15.0, 33.0)),
    ("SW-T1", 44.1, 15.32, 1.5e8, (35.0, 67.0)),
    ("SW-T2", 46.29182452, 14.63, 1.5e8, (35.0, 67.0)),
]

# A physically-conventional granite set, for reference only.
REFERENCE = ("granite ref", 30.0, None, 1.5e8, None)


def phi_peak(phi_r, jrc, jcs, sn_pa):
    return min(MAX_FRICTION_DEG, phi_r + jrc * log10(max(1e-30, jcs / sn_pa)))


def tau(phi_r, jrc, jcs, sn_pa):
    return sn_pa * tan(radians(phi_peak(phi_r, jrc, jcs, sn_pa)))


def main():
    print("PEAK FRICTION ANGLE AND ITS DECOMPOSITION")
    print("How much of the strength is the constant phi_r, and how much is the")
    print("stress-dependent roughness term?  Evaluated at each sample's own sigma'_n.")
    print()
    print("  %-8s %8s %7s %8s | %9s %9s %9s %8s  %8s"
          % ("sample", "sigma'n", "phi_r", "JCS", "roughness", "phi_peak", "mu", "phi_r/", "tau"))
    print("  %-8s %8s %7s %8s | %9s %9s %9s %8s  %8s"
          % ("", "[MPa]", "[deg]", "[MPa]", "[deg]", "[deg]", "tan()", "phi_pk", "[MPa]"))
    for name, phi_r, jrc, jcs, rng in FAMILIES:
        for sn_mpa in rng:
            sn = sn_mpa * 1e6
            rough = jrc * log10(jcs / sn)
            pk = phi_peak(phi_r, jrc, jcs, sn)
            print("  %-8s %8.1f %7.2f %8.0f | %9.2f %9.2f %9.3f %7.0f%%  %8.2f"
                  % (name, sn_mpa, phi_r, jcs / 1e6, rough, pk, tan(radians(pk)),
                     100.0 * phi_r / pk, tau(phi_r, jrc, jcs, sn) / 1e6))
    print()

    print("STRESS SENSITIVITY -- the discriminating quantity")
    print("Injection lowers sigma'_n.  d(tau)/d(sigma'_n) says how fast the fault")
    print("sheds strength as it does, which sets both slip onset and slip run-out.")
    print("Computed by central difference over +/-1 MPa.")
    print()
    print("  %-8s %10s %12s %12s %12s"
          % ("sample", "sigma'n", "tau", "dtau/dsn", "vs Coulomb"))
    print("  %-8s %10s %12s %12s %12s"
          % ("", "[MPa]", "[MPa]", "[-]", "mu=tan(phi_pk)"))
    for name, phi_r, jrc, jcs, rng in FAMILIES:
        for sn_mpa in rng:
            sn = sn_mpa * 1e6
            h = 1e6
            d = (tau(phi_r, jrc, jcs, sn + h) - tau(phi_r, jrc, jcs, sn - h)) / (2 * h)
            mu = tan(radians(phi_peak(phi_r, jrc, jcs, sn)))
            print("  %-8s %10.1f %12.2f %12.3f %12.3f"
                  % (name, sn_mpa, tau(phi_r, jrc, jcs, sn) / 1e6, d, mu))
    print()
    print("A pure Coulomb fault has dtau/dsn = mu exactly.  The gap between the")
    print("last two columns is the roughness term's contribution to the slope:")
    print("the larger the gap, the more the fault weakens on top of the direct")
    print("effective-stress reduction.")
    print()

    print("WHAT A SHARED phi_r WOULD COST EACH FAMILY")
    print("Holding JCS at the paper's intact-strength value and re-solving for the")
    print("JRC that reproduces each sample's own tau at its mid-range sigma'_n.")
    print()
    for jcs_target_mpa in (150.0, 300.0):
        print("  with JCS = %.0f MPa and phi_r = 30 deg (granite reference):" % jcs_target_mpa)
        for name, phi_r, jrc, jcs, rng in FAMILIES:
            sn_mpa = 0.5 * (rng[0] + rng[1])
            sn = sn_mpa * 1e6
            tau_target = tau(phi_r, jrc, jcs, sn)
            # solve phi_r + JRC log10(JCS/sn) = atan(tau_target/sn)
            need_deg = degrees(__import__("math").atan(tau_target / sn))
            lever = log10(jcs_target_mpa * 1e6 / sn)
            jrc_needed = (need_deg - 30.0) / lever if lever > 0 else float("nan")
            print("     %-8s sigma'n %5.1f MPa  tau %6.2f MPa  phi_pk %5.2f deg"
                  "  -> JRC must be %6.2f  (deck has %5.2f)"
                  % (name, sn_mpa, tau_target / 1e6, need_deg, jrc_needed, jrc))
        print()


if __name__ == "__main__":
    main()
