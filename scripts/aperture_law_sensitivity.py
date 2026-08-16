#!/usr/bin/env python
"""Compare the two fracture-permeability laws on SW-S4's own constants.

    /home/geomechanics/miniforge/bin/python scripts/aperture_law_sensitivity.py

CONTEXT. The Barton-Bandis-Bakhtar swap was found to destabilise SW-S4 near the slip
event while the additive control ran divergence-free end to end. That conclusion came
from run behaviour. This script asks whether the LAWS THEMSELVES explain it.

ANSWER: no, not at fixed JRC. Over SW-S4's real operating range the two laws give
transmissivities within a factor of 1.45. The instability is not a stiffness-of-the-
formula effect. See the three ruled-out mechanisms below.

WHAT IT DID SURFACE: the Bakhtar deck's offset calibration is inconsistent with its
own use_mobilized_jrc = true setting, which is a latent hazard with a very sharp edge.

    ADDITIVE  (ADOrcaRoughnessDamageFracturePermeability)
        a_h = a_h0 + stress_aperture + aperture_scale * E + dilation + prop - gouge
    BAKHTAR   (ADOrcaBartonBandisBakhtarFracturePermeability)
        e_h [um] = (E [um] + offset [um])^2 / JRC^2.5

Both then take k = e^2/12 and T = e^3/(12 mu), and T is what
OrcaFractureFlowInterfaceKernel feeds back into the pressure equation.

RULED OUT #1 -- "Bakhtar is quadratic in E, so T goes as E^6 instead of E^3."
    True of the bare formula, false in the deck. The deck calibrates
    offset[um] = sqrt(a_h0[um] * bb_jrc^2.5) = 30.79 um, which dominates SW-S4's
    mechanical apertures (peak 1.16 um, from 68_03's mechanical_aperture_pp). In
    that regime (E + 30.79)^2 is very nearly linear in E. Measured log-sensitivity
    dlnT/dlnE reaches 0.37, not 6.

RULED OUT #2 -- "e_h saturates the max_hydraulic_aperture = 8 um clamp, and hitting a
    non-differentiable clamp mid-Newton wrecks convergence."
    Not at fixed JRC: e_h stays at 0.74-0.84 um across the whole operating range,
    an order of magnitude below the clamp.

RULED OUT #3 -- "mobilized JRC degrades during slip and 1/JRC^2.5 blows up."
    Not observable in the data present: bb_jrc_mobilized_pp is pinned at 17.5 for all
    1302 post-zero rows of 68_03. It never moves.

    CAVEAT on #3: 68_03 is the ADDITIVE deck, which does not consume JRC for
    permeability at all. No Bakhtar run output exists in this repo to check against
    (that work was done in orca_3.0 / orca_3.0_full). So #3 is unsupported here
    rather than disproven, and the table at the bottom of this script is why it is
    still worth checking there.

THE LATENT HAZARD. The offset is computed once from the CONSTANT bb_jrc = 17.5:

    offset[um] = sqrt(a_h0[um] * bb_jrc^2.5)

but the formula divides by the MOBILIZED JRC, which use_mobilized_jrc = true lets
move. The calibration "reproduces a_h0 at E = 0" therefore holds only while
JRC_mob == 17.5. The offset alone is 30.79 um, so at E = 0 the law returns
30.79^2 / JRC_mob^2.5 -- and that reaches the 8 um clamp at JRC_mob = 6.75, a drop
of only 2.6x. See the final table.
"""

import csv
import os
from math import sqrt

# --- SW-S4 deck constants ---------------------------------------------------
# 68_02_sw4_bbfast_tail6p75_eta3p25_m0_bakhtar_kernel_SV.i  (Bakhtar)
# 68_03_sw4_bbfast_tail6p50_eta3p25_m0_kernel_SV.i          (additive control)
# The pair differs only in the permeability material.
A_H0 = 0.74e-6          # initial_hydraulic_aperture, m       (both decks)
APERTURE_SCALE = 0.001  # additive deck only
JRC = 17.5              # bb_jrc                              (both decks)
MAX_APERTURE = 8e-6     # max_hydraulic_aperture              (both decks)
MU = 1.002e-3

OFFSET_UM = sqrt(A_H0 * 1e6 * JRC ** 2.5)

# Mechanical apertures spanning SW-S4's measured range. Peak below is 68_03's
# observed max; the range is extended a little past it deliberately.
E_RANGE_M = [0.0, 1e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6]

ADDITIVE_CSV = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, "Examples",
    "YeGhasemmi2018", "SWS4", "results_csv",
    "68_03_sw4_bbfast_tail6p50_eta3p25_m0.csv")


def bakhtar_eh_m(E_m, jrc=JRC):
    E_um = E_m * 1e6 + OFFSET_UM
    eh = (E_um ** 2 / jrc ** 2.5) * 1e-6
    return min(eh, MAX_APERTURE)


def additive_ah_m(E_m):
    # Only the terms that depend on E. The stress-aperture, dilation and gouge terms
    # are additive constants at a fixed stress state and do not change the
    # sensitivity argument -- dropping them makes the additive law look STIFFER than
    # it is, so this comparison is conservative against the additive side.
    return A_H0 + APERTURE_SCALE * E_m


def report_observed_range():
    if not os.path.exists(ADDITIVE_CSV):
        print("(additive run CSV not found; skipping observed-range check)\n")
        return
    with open(ADDITIVE_CSV) as fh:
        rows = list(csv.DictReader(fh))
    def rng(col):
        v = [float(r[col]) for r in rows
             if float(r["time"]) > 0 and r[col] not in ("", "nan")]
        return min(v), max(v)
    lo, hi = rng("mechanical_aperture_pp")
    print("observed in 68_03 (additive control, %d rows past t=0):" % (len(rows) - 1))
    print("   mechanical_aperture   %.4f to %.4f um" % (lo * 1e6, hi * 1e6))
    lo, hi = rng("bb_jrc_mobilized_pp")
    print("   bb_jrc_mobilized      %.4f to %.4f %s"
          % (lo, hi, "(never moves)" if lo == hi else ""))
    print()


def main():
    print("SW-S4: a_h0 = %.2f um, bb_jrc = %.1f, aperture_scale = %g, clamp = %.1f um"
          % (A_H0 * 1e6, JRC, APERTURE_SCALE, MAX_APERTURE * 1e6))
    print("Bakhtar calibrated offset = %.4f um (reproduces a_h0 at E = 0, "
          "ONLY at JRC = %.1f)" % (OFFSET_UM, JRC))
    print()
    report_observed_range()

    hdr = ("%-12s %12s %12s %14s %14s"
           % ("E [um]", "add a_h[um]", "bak e_h[um]", "add dlnT/dlnE", "bak dlnT/dlnE"))
    print(hdr)
    print("-" * len(hdr))
    for E_m in E_RANGE_M:
        ah, eh = additive_ah_m(E_m), bakhtar_eh_m(E_m)
        s_add = 3.0 * (APERTURE_SCALE * E_m) / ah
        s_bak = 6.0 * (E_m * 1e6) / (E_m * 1e6 + OFFSET_UM)
        print("%-12.4f %12.4f %12.4f %14.6f %14.4f"
              % (E_m * 1e6, ah * 1e6, eh * 1e6, s_add, s_bak))

    print()
    print("transmissivity ratio bakhtar/additive (T = e^3/12mu):")
    worst = 0.0
    for E_m in E_RANGE_M:
        r = bakhtar_eh_m(E_m) ** 3 / additive_ah_m(E_m) ** 3
        worst = max(worst, r)
        print("   E = %7.4f um   T_bak/T_add = %6.2f" % (E_m * 1e6, r))
    print("worst over the operating range: %.2f -- too small to be the "
          "instability on its own." % worst)

    print()
    print("LATENT HAZARD: e_h at E = 0 as the mobilized JRC degrades away from the")
    print("value the offset was calibrated at.")
    print("   %-10s %14s %14s" % ("JRC_mob", "e_h [um]", "vs a_h0"))
    for j in [17.5, 15.0, 12.0, 10.0, 8.0, 6.75, 5.0, 3.0, 1.0]:
        raw = (OFFSET_UM ** 2) / (j ** 2.5)
        tag = "  CLAMPED at %.0f um" % (MAX_APERTURE * 1e6) if raw > MAX_APERTURE * 1e6 else ""
        print("   %-10.2f %14.2f %13.1fx%s" % (j, raw, raw / (A_H0 * 1e6), tag))


if __name__ == "__main__":
    main()
