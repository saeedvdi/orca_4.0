#!/usr/bin/env python3
"""
kalantar_parameter_audit.py -- recover Kalantar et al. (2025)'s own constants from
its own Table 2, before any deck is written.

WHY THIS RUNS FIRST
===================
The equivalent script for Ye & Ghassemi (2018) found that one of the four
specimens had a fracture angle in Table 1 that its own Table 2 contradicts
(SW-T2: printed 31 degrees, reduced at 30), and that error had already been
built into a mesh and run for months. The lesson is that a paper's stated
geometry is a claim, and its data table is a second, independent statement of
the same geometry. Check them against each other before cutting anything.

THE IDENTITY
============
Kalantar's equations (3) and (4) are the standard triaxial resolution onto a
plane inclined at theta to the core axis:

    sigma'_n = (sigma_3 - P_p) + (sigma_1 - sigma_3) sin^2(theta)      (3)
    tau      =                   (sigma_1 - sigma_3) sin(theta)cos(theta)  (4)
    P_p      = (P_i + P_o)/2                                            (5)

Dividing (3-part) by (4) eliminates the differential stress, which is the one
quantity Table 2 does not print:

    tan(theta) = (sigma'_n - sigma_3 + P_p) / tau

Every term on the right is tabulated or known, so theta can be recovered at
every hold stage independently. Two unknowns actually enter -- theta and
sigma_3 -- so the script solves for both by least squares across all stages of a
specimen rather than assuming either.

WHAT ELSE IT CHECKS
===================
1. How many of the six tabulated columns are independent. Q, k and a_h are one
   measurement (k is computed from Q through the paper's eq 7, a_h = sqrt(12k)),
   and sigma'_n and tau are one measurement (both are affine in sigma_1 alone
   once theta and sigma_3 are fixed). That leaves three independent channels per
   stage, not six, and a validation that reports six is counting the same defect
   repeatedly.
2. Whether a_h = sqrt(12k) reproduces the printed a_h, which tells us whether the
   k column is safe to score against or has been rounded into uselessness.
3. The critical-stress state each specimen was set to, against the paper's own
   fracture-strength criteria.

Run:  python3 scripts/kalantar_parameter_audit.py
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLE2 = ROOT / "Examples/Kalantar2025/validation/kalantar2025_table2.csv"

DARCY_M2 = 9.869233e-13  # 1 Darcy in m^2

# Paper section 2.3 and 2.1.
P_OUTLET_MPA = 3.0          # production pressure, constant through every test
EFFECTIVE_CONFINING_MPA = 30.0   # sigma'_c quoted for every shear-flow test

# Table 1: fracture angle measured from the specimen's long axis.
TABLE1 = {
    "OG-SH": {"type": "shear",   "length_mm": 120.00, "diameter_mm": 49.98, "theta_deg": 29.0},
    "OG-T":  {"type": "tensile", "length_mm": 100.00, "diameter_mm": 49.98, "theta_deg": 28.0},
    "OG-SC": {"type": "saw-cut", "length_mm": 100.00, "diameter_mm": 49.98, "theta_deg": 30.0},
}

# Figure 3b/3d/3f fitted fracture-strength criteria, tau = mu*sigma'_n + c (MPa).
STRENGTH_CRITERION = {
    "OG-SH": (0.7, 1.2),
    "OG-T":  (1.1, 0.0),
    "OG-SC": (0.4, 0.0),
}

# Section 2.2 / 3.2, averaged over the top and bottom surface of each fracture.
ROUGHNESS = {
    "OG-SH": {"Z2_before": 0.30, "JRC_before": 15.60, "Z2_after": 0.30, "JRC_after": 15.21},
    "OG-T":  {"Z2_before": 0.25, "JRC_before": 12.10, "Z2_after": 0.25, "JRC_after": 11.81},
    "OG-SC": {"Z2_before": 0.12, "JRC_before": 4.23,  "Z2_after": 0.08, "JRC_after": 1.36},
}
JRC_UNCERTAINTY = 2.10  # section 3.2 error propagation from the 0.012 mm scanner resolution


def rule(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def recover_geometry(frame: pd.DataFrame) -> dict:
    """Least-squares solve for theta and sigma_3 from the stress columns alone.

    sigma'_n = (sigma_3 - P_p) + tau*tan(theta) is linear in the two unknowns
    (sigma_3, tan theta), so this is an exact linear regression rather than an
    iteration:  sigma'_n + P_p = sigma_3 * 1 + tan(theta) * tau
    """
    pore = (frame["P_i_MPa"] + P_OUTLET_MPA) / 2.0
    lhs = frame["sigma_n_eff_MPa"].to_numpy() + pore.to_numpy()
    design = np.column_stack([np.ones(len(frame)), frame["tau_MPa"].to_numpy()])
    (sigma3, tan_theta), *_ = np.linalg.lstsq(design, lhs, rcond=None)
    residual = lhs - design @ np.array([sigma3, tan_theta])
    return {
        "sigma3_MPa": float(sigma3),
        "theta_deg": math.degrees(math.atan(tan_theta)),
        "max_abs_residual_MPa": float(np.abs(residual).max()),
        "rms_residual_MPa": float(np.sqrt((residual ** 2).mean())),
    }


def main() -> int:
    table = pd.read_csv(TABLE2)

    rule("1. FRACTURE ANGLE AND CONFINING STRESS, recovered from Table 2 alone")
    print("Solving  sigma'_n + P_p = sigma_3 + tau*tan(theta)  over every hold stage.")
    print("A residual at the 0.01 MPa level means the whole specimen's stress table is")
    print("reproduced by two constants, i.e. the recovery is not a fit but an identity.\n")
    print(f"{'sample':8s} {'n':>3s} {'Table 1 theta':>14s} {'recovered':>10s} "
          f"{'sigma_3':>9s} {'max resid':>10s} {'verdict':>10s}")
    recovered = {}
    for sample, group in table.groupby("sample", sort=False):
        got = recover_geometry(group)
        recovered[sample] = got
        printed = TABLE1[sample]["theta_deg"]
        delta = got["theta_deg"] - printed
        verdict = "agrees" if abs(delta) < 0.15 else f"OFF {delta:+.2f} deg"
        print(f"{sample:8s} {len(group):3d} {printed:13.1f}  {got['theta_deg']:9.3f} "
              f"{got['sigma3_MPa']:8.3f} {got['max_abs_residual_MPa']:9.4f}  {verdict:>10s}")
    print(f"\nsigma'_c = sigma_3 - P_p at P_i = P_o = {P_OUTLET_MPA:.0f} MPa should be "
          f"{EFFECTIVE_CONFINING_MPA:.0f} MPa (section 2.3):")
    for sample, got in recovered.items():
        print(f"    {sample:8s} sigma_3 - {P_OUTLET_MPA:.0f} = "
              f"{got['sigma3_MPa'] - P_OUTLET_MPA:.3f} MPa")

    rule("2. HOW MANY INDEPENDENT OBSERVABLES PER STAGE")
    print("Table 2 prints six columns. They are not six measurements.\n")
    print("  (a) k is computed FROM Q through eq (7) and a_h = sqrt(12k) FROM k, so")
    print("      Q, k and a_h are one channel. Check that a_h = sqrt(12k) holds:\n")
    print(f"    {'sample':8s} {'stages':>7s} {'median |err|':>13s} {'max |err|':>11s}")
    for sample, group in table.groupby("sample", sort=False):
        implied = np.sqrt(12.0 * group["k_D"].to_numpy() * DARCY_M2) * 1e6
        printed = group["a_h_um"].to_numpy()
        with np.errstate(divide="ignore", invalid="ignore"):
            err = np.where(printed > 0, np.abs(implied - printed) / printed * 100.0, np.nan)
        print(f"    {sample:8s} {len(group):7d} {np.nanmedian(err):12.1f}% "
              f"{np.nanmax(err):10.1f}%")
    print("\n      The k column is printed to two decimals, which is coarse where k < 0.1 D;")
    print("      a_h is the better-resolved statement of the same measurement.\n")
    print("  (b) sigma'_n and tau are both affine in sigma_1 once theta and sigma_3 are")
    print("      fixed, so they are one channel. Section 1 above IS the proof: two")
    print("      constants reproduce the whole sigma'_n column from the tau column.\n")
    print("  => three independent channels per stage: a flow rate, a slip, a stress.")

    rule("3. CRITICAL STRESS STATE AT THE START OF INJECTION")
    print("Paper: the axial load was set so tau = 0.85*tau_p (0.92 for OG-SH), with")
    print("tau_p from the fitted criterion at the test's effective normal stress.\n")
    print(f"{'sample':8s} {'criterion':>22s} {'stage-1 sigma_n':>15s} {'tau_p':>8s} "
          f"{'stage-1 tau':>12s} {'ratio':>7s}")
    for sample, group in table.groupby("sample", sort=False):
        mu, cohesion = STRENGTH_CRITERION[sample]
        first = group.iloc[0]
        peak = mu * first["sigma_n_eff_MPa"] + cohesion
        print(f"{sample:8s} {f'tau = {mu}*sn + {cohesion}':>22s} "
              f"{first['sigma_n_eff_MPa']:14.2f} {peak:8.2f} {first['tau_MPa']:11.2f} "
              f"{first['tau_MPa'] / peak:7.3f}")

    rule("4. ROUGHNESS, AND WHETHER ITS CHANGE IS RESOLVABLE")
    print(f"Reported JRC uncertainty is +/-{JRC_UNCERTAINTY:.2f} (section 3.2).\n")
    print(f"{'sample':8s} {'JRC before':>11s} {'JRC after':>10s} {'change':>8s} {'resolved':>9s}")
    for sample, values in ROUGHNESS.items():
        change = values["JRC_after"] - values["JRC_before"]
        print(f"{sample:8s} {values['JRC_before']:11.2f} {values['JRC_after']:10.2f} "
              f"{change:8.2f} {'no' if abs(change) < JRC_UNCERTAINTY else 'YES':>9s}")

    rule("5. WHAT THE SLIP COLUMN SAYS ABOUT WHEN EACH SPECIMEN MOVED")
    print("Cumulative shortening dL_s, and its increment stage to stage. A specimen")
    print("that slips on the pressure RAMPS rather than in the holds shows its whole")
    print("budget in one or two increments.\n")
    for sample, group in table.groupby("sample", sort=False):
        slip = group["dLs_mm"].to_numpy()
        steps = np.diff(slip, prepend=0.0)
        total = slip[-1]
        biggest = int(np.argmax(steps))
        print(f"  {sample:8s} total {total * 1000:6.1f} um   largest single step "
              f"{steps[biggest] * 1000:6.1f} um at stage {group.iloc[biggest]['stage']:.0f} "
              f"(P_i = {group.iloc[biggest]['P_i_MPa']:.0f} MPa) = "
              f"{steps[biggest] / total * 100:.0f}% of the budget")

    rule("6. OG-T RE-REDUCED ONTO ITS PHYSICAL 28-DEGREE PLANE")
    print("Section 1 shows OG-T's stress columns were reduced at 26.0 degrees, and the")
    print("mesh journal shows 26 degrees cannot be realised in a 100.00 x 49.98 mm core")
    print("(a through-going fracture needs 102.474 mm of axial extent). So Table 1's 28")
    print("degrees is the geometry and the published stress columns are in the wrong")
    print("frame. Recover the differential stress the experiment measured, then resolve")
    print("it onto the plane that actually exists:\n")
    print("    sigma_d      = tau_pub / (sin26 cos26)")
    print("    tau_28       = sigma_d sin28 cos28")
    print("    sigma'_n,28  = (sigma_3 - P_p) + sigma_d sin^2(28)\n")
    published = math.radians(25.999)
    physical = math.radians(TABLE1["OG-T"]["theta_deg"])
    frame = table[table["sample"] == "OG-T"].copy()
    pore = (frame["P_i_MPa"] + P_OUTLET_MPA) / 2.0
    sigma_d = frame["tau_MPa"] / (math.sin(published) * math.cos(published))
    frame["tau_28"] = sigma_d * math.sin(physical) * math.cos(physical)
    frame["sigma_n_28"] = (33.0 - pore) + sigma_d * math.sin(physical) ** 2
    print(f"{'stage':>5s} {'P_i':>4s} {'tau_pub':>8s} {'tau_28':>8s} "
          f"{'sn_pub':>8s} {'sn_28':>8s} {'sigma_d':>8s}")
    for _, row in frame.iterrows():
        print(f"{row['stage']:5.0f} {row['P_i_MPa']:4.0f} {row['tau_MPa']:8.2f} "
              f"{row['tau_28']:8.2f} {row['sigma_n_eff_MPa']:8.2f} "
              f"{row['sigma_n_28']:8.2f} "
              f"{row['tau_MPa'] / (math.sin(published) * math.cos(published)):8.2f}")
    scale = math.sin(physical) * math.cos(physical) / (math.sin(published) * math.cos(published))
    print(f"\n  tau scales by a constant {scale:.6f} (+{(scale - 1) * 100:.2f}%);")
    print(f"  peak shear moves {frame['tau_MPa'].max():.2f} -> {frame['tau_28'].max():.2f} MPa.")
    print("  sigma'_n does NOT scale by a constant -- the confining part is unchanged and")
    print("  only the deviatoric part moves, so the ratio tau/sigma'_n changes stage by")
    print("  stage. The published criterion tau = 1.1 sigma'_n was fitted in the 26-degree")
    print("  frame and must be refitted before it is used to set a critical stress state:")
    ratio = frame["tau_28"] / frame["sigma_n_28"]
    published_ratio = frame["tau_MPa"] / frame["sigma_n_eff_MPa"]
    pre_slip = frame["stage"] <= 7   # stages 8-9 are the slip event and its aftermath
    print(f"    pre-slip tau/sigma'_n   published frame {published_ratio[pre_slip].min():.3f}"
          f"-{published_ratio[pre_slip].max():.3f}   "
          f"28-degree frame {ratio[pre_slip].min():.3f}-{ratio[pre_slip].max():.3f}")

    rule("7. LOADING-FRAME STIFFNESS -- A MEASURED VALUE FOR A CONSTANT WE INFERRED")
    print("Section 2.3 states K_sys ~ 796 kN/mm for the MTS 815 frame. The Ye & Ghassemi")
    print("(2018) campaign had no such number and had to infer one from a single scored")
    print("run under a series-spring assumption, where it turned out to dominate every")
    print("magnitude in the model. Converting Kalantar's to the same units:\n")
    k_sys_n_per_m = 796e3 / 1e-3
    area = math.pi * (TABLE1["OG-T"]["diameter_mm"] / 2000.0) ** 2
    print(f"    K_sys      = 796 kN/mm = {k_sys_n_per_m:.3e} N/m")
    print(f"    specimen A = {area:.4e} m^2  (D = 49.98 mm)")
    print(f"    K_sys / A  = {k_sys_n_per_m / area / 1e12:.3f} MPa/um")
    print(f"\n  The Ye2018 campaign inferred 0.94 MPa/um for its frame. These are different")
    print(f"  machines, so this is not a calibration -- but it is the first independent")
    print(f"  check that the inferred value sits in the right decade, and it lands within")
    print(f"  a factor of {0.94 / (k_sys_n_per_m / area / 1e12):.2f}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
