#!/usr/bin/env python
"""Score every Ye & Ghassemi (2018) sample deck against its digitized validation curves.

    /home/geomechanics/miniforge/bin/python scripts/sample_scorecard.py

WHY THIS EXISTS.  Each sample had its own notebook and its own eyeball comparison,
so a discrepancy that is shared by all four samples -- i.e. a parameter problem
rather than a per-sample calibration problem -- was invisible.  This puts all
four on one table, in one set of units, with the same metrics.

For each observable it reports:

    peak      the extreme value of each curve and the ratio sim/exp.  For the
              displacement channels the extreme is taken by MAGNITUDE, so the
              ratio's sign reports whether the two curves agree about direction
              (see score() -- the repo's two dilation files disagree).
    t_peak    when that extreme occurs, and the lag sim - exp.  A ratio near 1
              with a large lag means the magnitude is calibrated but the timing
              is not -- a different fix from a magnitude error.
    rmse      root-mean-square difference over the digitized time support,
              after interpolating the simulation onto the digitized times,
              normalised by the experimental peak-to-peak range.

Digitized files are two-column (time, value) with no header, occasionally with
a stray header line; both are handled.  Units are converted to the deck's.

TWO GUARDS AGAINST BAD VALIDATION DATA, both added after they fired for real:

  * a file that is CONSTANT is rejected rather than scored, because a ratio
    against a constant still prints a plausible-looking number
    (SWT1_piston_displacement_mm.csv has span exactly 0.0);
  * displacement channels are zeroed at t=0 on both sides and the removed
    offset is printed, because an un-zeroed LVDT baseline makes the raw
    comparison meaningless rather than merely wrong
    (SWT1_shear_slip_mm.csv starts at -48.73 mm).

Both were found by this script disagreeing with the eye, and both turned out to
be the data rather than the model.  Check the digitized series before tuning a
deck against it.
"""

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.normpath(os.path.join(HERE, os.pardir, "Examples", "YeGhasemmi2018"))

# sample -> (results csv, digitized subdir, {observable: (digitized file, sim column, scale)})
# scale multiplies the SIMULATION column to reach the digitized file's units.
SAMPLES = {
    "SW-S3": dict(
        csv="SWS3/results_csv/84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV_biot_ab_20260815.csv",
        csv_b="SWS3/results_csv/84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV_biot0p6_biot_ab_20260815.csv",
        vdir="SWS3/SWS3",
        obs={
            "differential_stress_MPa": ("differnetial_stress_vs_time_sw3.csv", "differential_stress_mpa_pp", 1.0),
            "injection_pressure_MPa": ("Injection_pressure_vs_time_SW3.csv", "injection_pressure_pp", 1e-6),
            "flow_rate_mlmin": ("flow_Rate_mlmin_vs_time_sw3.csv", "flow_rate_validation_ml_min_pp", 1.0),
            "frac_perm_m2": ("permeability_m2_vs_time_sw3_corrected.table2", "fracture_permeability_pp", 1.0),
            "normal_dilation_mm": ("normal_dilation_mm_vs_time_sw3.csv", "czm_normal_dilation_paper_mm_pp", 1.0),
            "eff_normal_stress_MPa": ("effective_normal_stress_mpa_Vs_time_SW3.csv", "bb_effective_normal_stress_pp", 1e-6),
            "shear_slip_mm": ("shear_slip_mm_vs_time_sw3.csv", "czm_shear_slip_mm_pp", 1.0),
            "shear_stress_MPa": ("shear_stress_MPa_vs_time_sw3.csv", "shear_stress_paper_frame_mpa_pp", 1.0),
        },
    ),
    "SW-T1": dict(
        csv="SWT1/results_csv/Ye2018_SWT1_BBFast_sweep_19_F0p95_Pp0p60_T40p00_U0p94_A0p0160_Kinematic_IOsafe_kernel_SV_biot_ab_20260815.csv",
        csv_b="SWT1/results_csv/Ye2018_SWT1_BBFast_sweep_19_F0p95_Pp0p60_T40p00_U0p94_A0p0160_Kinematic_IOsafe_kernel_SV_biot0p6_biot_ab_20260815.csv",
        vdir="SWT1/SWT1",
        obs={
            "differential_stress_MPa": ("SWT1_differential_stress.csv", "differential_stress_mpa_pp", 1.0),
            "injection_pressure_MPa": ("SWT1_injection_pressure_MPa.csv", "injection_pressure_pp", 1e-6),
            "flow_rate_mlmin": ("SWt1_flow_rate.csv", "flow_rate_validation_ml_min_pp", 1.0),
            "frac_perm_m2": ("SWT1_fracture_permeability_m2.csv", "fracture_permeability_pp", 1.0),
            "normal_dilation_mm": ("SWT1_normal_dilation.csv", "czm_normal_dilation_paper_mm_pp", 1.0),
            "eff_normal_stress_MPa": ("SWT1_effective_normal_stress.csv", "bb_effective_normal_stress_pp", 1e-6),
            "shear_slip_mm": ("SWT1_shear_slip_mm.csv", "czm_shear_slip_mm_pp", 1.0),
            "shear_stress_MPa": ("SWT1_shear_stress.csv", "shear_stress_paper_frame_mpa_pp", 1.0),
        },
    ),
}

# How each observable's "peak" is defined. "magnitude" is used for the
# zero-baselined displacement channels -- see score().
PEAK_RULE = {"normal_dilation_mm": "magnitude", "shear_slip_mm": "magnitude"}


# Displacement channels are LVDT readings and are only meaningful as a CHANGE
# from the start of the test. Some digitized files were captured without zeroing
# the instrument baseline -- SWT1_shear_slip_mm.csv starts at -48.73 mm -- which
# makes a raw comparison meaningless rather than merely wrong. For these channels
# both curves are shifted to start at zero and the removed offset is reported, so
# the correction stays visible instead of being silently absorbed.
ZERO_BASELINE = {"normal_dilation_mm", "shear_slip_mm"}


def load_digitized(path):
    """Two columns, time then value. Tolerates a header row and blank lines.

    Returns (frame, note); `note` is non-None only when the file is unusable.
    """
    try:
        d = pd.read_csv(path, header=None, names=["t", "v"], comment="#")
    except Exception as exc:  # pragma: no cover - diagnostics only
        return None, "unreadable: %s" % exc
    d = d.apply(pd.to_numeric, errors="coerce").dropna()
    if len(d) < 3:
        return None, "fewer than 3 numeric rows"
    d = d.sort_values("t").reset_index(drop=True)
    if d["v"].max() - d["v"].min() == 0.0:
        # Not a flat measurement -- a file with no data in it. Scoring against a
        # constant would still print a ratio, so refuse and say why.
        return None, "CONSTANT at %.5f -- file holds no data" % d["v"].iloc[0]
    return d, None


def score(sim_t, sim_v, exp_t, exp_v, use_min):
    if use_min == "magnitude":
        # Used for the zero-baselined displacement channels, where the two files
        # in the repo disagree about which way is positive (SW-S3's dilation ends
        # at -0.042 mm, SW-T1's at +0.521 mm). Taking the largest-magnitude
        # excursion scores the size of the response without silently adopting
        # either sign convention; the ratio's SIGN then shows whether the two
        # curves agree about direction, which is the thing worth seeing.
        i_s = int(np.argmax(np.abs(sim_v)))
        i_e = int(np.argmax(np.abs(exp_v)))
    else:
        pick = np.argmin if use_min else np.argmax
        i_s, i_e = pick(sim_v), pick(exp_v)
    peak_s, peak_e = sim_v[i_s], exp_v[i_e]
    ratio = peak_s / peak_e if peak_e != 0 else float("nan")

    lo, hi = exp_t.min(), exp_t.max()
    m = (sim_t >= lo) & (sim_t <= hi)
    if m.sum() < 2:
        return peak_s, peak_e, ratio, sim_t[i_s], exp_t[i_e], float("nan")
    interp = np.interp(exp_t, sim_t[m], sim_v[m])
    rng = exp_v.max() - exp_v.min()
    nrmse = np.sqrt(np.mean((interp - exp_v) ** 2)) / rng if rng > 0 else float("nan")
    return peak_s, peak_e, ratio, sim_t[i_s], exp_t[i_e], nrmse


def main():
    arms = [("alpha=1e-12 (base)", "csv"), ("alpha=0.6", "csv_b")]
    for name, cfg in SAMPLES.items():
      for arm_label, arm_key in arms:
        if arm_key not in cfg:
            continue
        csv_path = os.path.join(EX, cfg[arm_key])
        print("=" * 100)
        print(name, " ", arm_label)
        print("  ", os.path.basename(csv_path))
        if not os.path.exists(csv_path):
            print("   results csv missing -- run not finished")
            continue
        sim = pd.read_csv(csv_path)
        print("   %d rows, t = %.1f .. %.1f s" % (len(sim), sim["time"].min(), sim["time"].max()))
        print()
        print("   %-24s %13s %13s %8s   %9s %9s %8s   %7s"
              % ("observable", "sim peak", "exp peak", "ratio", "t_sim", "t_exp", "lag", "nRMSE"))
        for obs, (vfile, col, scale) in cfg["obs"].items():
            vpath = os.path.join(EX, cfg["vdir"], vfile)
            if not os.path.exists(vpath):
                print("   %-24s  digitized file not found: %s" % (obs, vfile))
                continue
            if col not in sim.columns:
                print("   %-24s  sim column not found: %s" % (obs, col))
                continue
            exp, err = load_digitized(vpath)
            if exp is None:
                print("   %-24s  %s" % (obs, err))
                continue
            sim_v = sim[col].to_numpy() * scale
            exp_v = exp["v"].to_numpy()
            note = ""
            if obs in ZERO_BASELINE:
                off_s, off_e = sim_v[0], exp_v[0]
                sim_v = sim_v - off_s
                exp_v = exp_v - off_e
                if abs(off_e) > 0.05 * (exp_v.max() - exp_v.min()):
                    note = "  [exp baseline %+.3f removed]" % off_e
            ps, pe, r, ts, te, nr = score(
                sim["time"].to_numpy(), sim_v,
                exp["t"].to_numpy(), exp_v, PEAK_RULE.get(obs, False))
            flag = "" if 0.85 <= abs(r) <= 1.15 else "   <-- off"
            print("   %-24s %13.5g %13.5g %8.3f   %9.1f %9.1f %8.1f   %6.1f%%%s%s"
                  % (obs, ps, pe, r, ts, te, ts - te, 100 * nr, flag, note))
        print()


if __name__ == "__main__":
    main()
