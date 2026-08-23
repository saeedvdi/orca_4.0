#!/usr/bin/env python3
"""Recompute and update the authoritative monotonic Table-2 ranking.

The existing CSV is the case manifest: it supplies model-family and selection
metadata.  NEW_CASES adds completed monotonic result files that arrived after
the last ranking update.  Every numeric score and completion field is rebuilt
from the result CSV and its matching input deck through ``table2_gate``.

Usage:
    python scripts/update_table2_ranking.py          # verify, print summary
    python scripts/update_table2_ranking.py --write  # replace ranking CSV
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import table2_gate


ROOT = Path(__file__).resolve().parents[1]
RANKING = ROOT / "doc/independent_analysis/TABLE2_ERROR_ACCURACY_RANKING.csv"
TOL_MPA = 0.15

NEW_CASES = [
    {
        "sample": "SWS3",
        "case": "84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV",
        "series": "84",
        "model_family": "BBFast",
        "mesh": "mesh5",
        "selection_status": "historical_unphysical",
        "source_csv": "Examples/YeGhasemmi2018/SWS3/results_csv/84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV_biot_ab_20260815.csv",
        "notes": "historical alpha approximately zero arm; numerically scoreable but alpha < porosity is not a selectable physical calibration",
    },
    {
        "sample": "SWS3",
        "case": "84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV_biot0p6",
        "series": "84",
        "model_family": "BBFast",
        "mesh": "mesh5",
        "selection_status": "historical_sensitivity",
        "source_csv": "Examples/YeGhasemmi2018/SWS3/results_csv/84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV_biot0p6_biot_ab_20260815.csv",
        "notes": "historical physical-Biot A/B arm before the SW-S3 strength refit",
    },
    {
        "sample": "SWS3",
        "case": "86_01_sw3_bbfast_biot0p6_phir8p45_m0_kernel_SV",
        "series": "86",
        "model_family": "BBFast",
        "mesh": "mesh5",
        "selection_status": "historical_calibration",
        "source_csv": "Examples/YeGhasemmi2018/SWS3/results_csv/86_01_sw3_bbfast_biot0p6_phir8p45_m0_kernel_SV.csv",
        "notes": "historical SW-S3 residual-friction refit",
    },
    {
        "sample": "SWS3",
        "case": "86_02_sw3_bbfast_biot0p6_phir9p00_m0_kernel_SV",
        "series": "86",
        "model_family": "BBFast",
        "mesh": "mesh5",
        "selection_status": "historical_calibration",
        "source_csv": "Examples/YeGhasemmi2018/SWS3/results_csv/86_02_sw3_bbfast_biot0p6_phir9p00_m0_kernel_SV.csv",
        "notes": "partial historical SW-S3 residual-friction refit",
    },
    {
        "sample": "SWS4",
        "case": "68_02_sw4_bbfast_tail6p75_eta3p25_m0_kernel_SV",
        "series": "68",
        "model_family": "BBFast",
        "mesh": "mesh5",
        "selection_status": "historical_calibration",
        "source_csv": "Examples/YeGhasemmi2018/SWS4/results_csv/68_02_sw4_bbfast_tail6p75_eta3p25_m0_kernel_SV.csv",
        "notes": "partial legacy calibration run",
    },
    {
        "sample": "SWS4",
        "case": "68_03_sw4_bbfast_tail6p50_eta3p25_m0",
        "series": "68",
        "model_family": "BBFast",
        "mesh": "mesh5",
        "selection_status": "historical_calibration",
        "source_csv": "Examples/YeGhasemmi2018/SWS4/results_csv/68_03_sw4_bbfast_tail6p50_eta3p25_m0.csv",
        "notes": "partial legacy calibration run",
    },
    {
        "sample": "SWT1",
        "case": "Ye2018_SWT1_BBFast_sweep_19_F0p95_Pp0p60_T40p00_U0p94_A0p0160_Kinematic_IOsafe_kernel_SV",
        "series": "legacy",
        "model_family": "BBFast",
        "mesh": "mesh5",
        "selection_status": "historical_unphysical",
        "source_csv": "Examples/YeGhasemmi2018/SWT1/results_csv/Ye2018_SWT1_BBFast_sweep_19_F0p95_Pp0p60_T40p00_U0p94_A0p0160_Kinematic_IOsafe_kernel_SV_biot_ab_20260815.csv",
        "notes": "historical alpha approximately zero arm; numerically scoreable but alpha < porosity is not a selectable physical calibration",
    },
    {
        "sample": "SWT1",
        "case": "Ye2018_SWT1_BBFast_sweep_19_F0p95_Pp0p60_T40p00_U0p94_A0p0160_Kinematic_IOsafe_kernel_SV_biot0p6",
        "series": "legacy",
        "model_family": "BBFast",
        "mesh": "mesh5",
        "selection_status": "historical_sensitivity",
        "source_csv": "Examples/YeGhasemmi2018/SWT1/results_csv/Ye2018_SWT1_BBFast_sweep_19_F0p95_Pp0p60_T40p00_U0p94_A0p0160_Kinematic_IOsafe_kernel_SV_biot0p6_biot_ab_20260815.csv",
        "notes": "historical physical-Biot A/B arm",
    },
    {
        "sample": "SWT2",
        "case": "Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe_kernel_SV",
        "series": "legacy",
        "model_family": "BBFast",
        "mesh": "mesh5",
        "selection_status": "historical_unphysical",
        "source_csv": "Examples/YeGhasemmi2018/SWT2/results_csv/Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe_kernel_SV_biot_ab_20260815.csv",
        "notes": "historical alpha approximately zero arm; numerically scoreable but alpha < porosity is not a selectable physical calibration",
    },
    {
        "sample": "SWT2",
        "case": "Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe_kernel_SV_biot0p6",
        "series": "legacy",
        "model_family": "BBFast",
        "mesh": "mesh5",
        "selection_status": "historical_sensitivity",
        "source_csv": "Examples/YeGhasemmi2018/SWT2/results_csv/Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe_kernel_SV_biot0p6_biot_ab_20260815.csv",
        "notes": "historical physical-Biot A/B arm",
    },
    {
        "sample": "SWT1",
        "case": "100_01_swt1_vm55um_ppfix",
        "series": "100",
        "model_family": "BBFast",
        "mesh": "mesh5",
        "selection_status": "targeted_calibration_probe",
        "source_csv": "Examples/YeGhasemmi2018/SWT1/results_csv_hpc_rorqual/100_01_swt1_vm55um_ppfix_hpc.csv",
        "notes": "maximum closure 50->55 um; new nominal SWT1 minimum and a resolved improvement over 99_01",
    },
    {
        "sample": "SWT1",
        "case": "100_02_swt1_vm50um_apscale0p0155_ppfix",
        "series": "100",
        "model_family": "BBFast",
        "mesh": "mesh5",
        "selection_status": "targeted_calibration_probe",
        "source_csv": "Examples/YeGhasemmi2018/SWT1/results_csv_hpc_rorqual/100_02_swt1_vm50um_apscale0p0155_ppfix_hpc.csv",
        "notes": "combines maximum closure 50 um with aperture scale 0.0155; improves on 99_01 but is weaker than 100_01",
    },
    {
        "sample": "SWS3",
        "case": "100_05_sw3_resc1p25_ppfix",
        "series": "100",
        "model_family": "BBFast",
        "mesh": "mesh5",
        "selection_status": "targeted_calibration_probe",
        "source_csv": "Examples/YeGhasemmi2018/SWS3/results_csv_hpc_rorqual/100_05_sw3_resc1p25_ppfix_hpc.csv",
        "notes": "residual cohesion 1.30->1.25 MPa; 0.015-point gain over 99_06 is below the reproducibility floor",
    },
    {
        "sample": "SWS3",
        "case": "100_06_sw3_resc1p30_unld0p00_ppfix",
        "series": "100",
        "model_family": "BBFast",
        "mesh": "mesh5",
        "selection_status": "targeted_calibration_probe",
        "source_csv": "Examples/YeGhasemmi2018/SWS3/results_csv_hpc_rorqual/100_06_sw3_resc1p30_unld0p00_ppfix_hpc.csv",
        "notes": "combines residual cohesion 1.30 MPa with zero unload retention; nominal SWS3 minimum but only 0.097 points below 99_06",
    },
    # --- 102 series: the Mohr-Coulomb baseline rebuilt on the best BBFast
    # calibration of each specimen.  The question these answer is whether the
    # MC/BBFast accuracy gap is calibration or constitutive form: each 102 deck
    # transplants the scalar refinement that won the BBFast ranking onto the
    # matched MC envelope.  Every one lands within 0.28 points of its 94-series
    # sibling, so the gap does not move -- which is the result, not a failure.
    {
        "sample": "SWT1",
        "case": "102_01_swt1_mc_vm55um_ppfix",
        "series": "102",
        "model_family": "Mohr-Coulomb",
        "mesh": "mesh5",
        "selection_status": "best_case_constitutive_baseline",
        "source_csv": "Examples/YeGhasemmi2018/SWT1/results_csv_hpc_rorqual/102_01_swt1_mc_vm55um_ppfix_hpc.csv",
        "notes": "MC on 100_01's 55 um maximum closure; 0.078 points WORSE than 94_01, so the BBFast gain does not transfer",
    },
    {
        "sample": "SWT2",
        "case": "102_02_swt2_mc_apscale0p0177_ppfix",
        "series": "102",
        "model_family": "Mohr-Coulomb",
        "mesh": "mesh5",
        "selection_status": "best_case_constitutive_baseline",
        "source_csv": "Examples/YeGhasemmi2018/SWT2/results_csv_hpc_rorqual/102_02_swt2_mc_apscale0p0177_ppfix_hpc.csv",
        "notes": "MC on 100_04's aperture scale 0.0177; 0.220 points worse than 94_03",
    },
    {
        "sample": "SWS3",
        "case": "102_03_sw3_mc_resc1p30_ppfix",
        "series": "102",
        "model_family": "Mohr-Coulomb",
        "mesh": "mesh5",
        "selection_status": "best_case_constitutive_baseline",
        "source_csv": "Examples/YeGhasemmi2018/SWS3/results_csv_hpc_rorqual/102_03_sw3_mc_resc1p30_ppfix_hpc.csv",
        "notes": "MC on 99_06's residual cohesion 1.30 MPa; 0.273 points worse than 94_05",
    },
    {
        "sample": "SWS4",
        "case": "102_04_sw4_mc_theta30_jrc5_ppfix",
        "series": "102",
        "model_family": "Mohr-Coulomb",
        "mesh": "mesh5",
        "selection_status": "best_case_constitutive_baseline",
        "source_csv": "Examples/YeGhasemmi2018/SWS4/results_csv_hpc_rorqual/102_04_sw4_mc_theta30_jrc5_ppfix_hpc.csv",
        "notes": "MC on the 93_07 calibration; 0.004 points from 94_07, i.e. the same run to within the reproducibility floor",
    },
    # --- 103 series: the single-parameter mechanism control.  These are BBFast
    # decks with the slip-weakening exponent dropped 1.4 -> 1.0, the exponent MC
    # uses, and nothing else changed.  They are NOT calibration candidates and
    # must not compete with the BBFast decks for a family rank, so they carry
    # their own model_family.  Reading them as "bad BBFast runs" inverts their
    # meaning: on the tensile pair the whole MC/BBFast gap is supposed to open
    # up, and it does.
    {
        "sample": "SWT1",
        "case": "103_01_swt1_weakexp1p0_ppfix",
        "series": "103",
        "model_family": "BBFast linear-weakening control",
        "mesh": "mesh5",
        "selection_status": "mechanism_control",
        "source_csv": "Examples/YeGhasemmi2018/SWT1/results_csv_hpc_rorqual/103_01_swt1_weakexp1p0_ppfix_hpc.csv",
        "notes": "exponent 1.4->1.0 alone moves 93_01 from 4.435 to 24.354, i.e. onto its MC pair at 25.272; prediction confirmed",
    },
    {
        "sample": "SWT2",
        "case": "103_02_swt2_weakexp1p0_ppfix",
        "series": "103",
        "model_family": "BBFast linear-weakening control",
        "mesh": "mesh5",
        "selection_status": "mechanism_control",
        "source_csv": "Examples/YeGhasemmi2018/SWT2/results_csv_hpc_rorqual/103_02_swt2_weakexp1p0_ppfix_hpc.csv",
        "notes": "exponent 1.4->1.0 alone moves 93_03 from 2.428 to 23.339, i.e. onto its MC pair at 23.144; prediction confirmed",
    },
    {
        "sample": "SWS3",
        "case": "103_03_sw3_weakexp1p0_ppfix",
        "series": "103",
        "model_family": "BBFast linear-weakening control",
        "mesh": "mesh5",
        "selection_status": "mechanism_control",
        "source_csv": "Examples/YeGhasemmi2018/SWS3/results_csv_hpc_rorqual/103_03_sw3_weakexp1p0_ppfix_hpc.csv",
        "notes": "exponent 1.4->1.0 moves 93_05 only 4.574->5.267 against an MC pair at 18.470; the preregistered falsifier fires here",
    },
]

SCORE_COLUMNS = {
    "Q_ml_min": "q_nrmse_pct",
    "sigma_n_MPa": "sigma_n_nrmse_pct",
    "tau_MPa": "tau_nrmse_pct",
    "dn_mm": "dn_nrmse_pct",
    "ds_mm": "ds_nrmse_pct",
}


def rebuild() -> pd.DataFrame:
    frame = pd.read_csv(RANKING, dtype={"series": str})
    for item in NEW_CASES:
        if not frame["case"].eq(item["case"]).any():
            frame = pd.concat([frame, pd.DataFrame([item])], ignore_index=True)

    for idx, row in frame.iterrows():
        source = ROOT / str(row["source_csv"])
        if not source.is_file():
            raise FileNotFoundError(f"ranking source is absent: {source}")
        result = table2_gate.score_run(
            source, str(row["sample"]), "biot_ab_20260815", TOL_MPA, "stage1", 55.0
        )
        complete = result["reached"] == len(table2_gate.PI_TARGETS)
        frame.at[idx, "run_status"] = "complete" if complete else "partial"
        frame.at[idx, "comparable_for_ranking"] = complete
        frame.at[idx, "stages_reached"] = result["reached"]
        frame.at[idx, "total_stages"] = len(table2_gate.PI_TARGETS)
        frame.at[idx, "run_end_s"] = result["t_end"]
        scores = table2_gate.normalised_scores(result)
        if complete:
            for source_name, column in SCORE_COLUMNS.items():
                frame.at[idx, column] = scores[source_name]
            frame.at[idx, "mean_nrmse_pct"] = scores["mean"]
            frame.at[idx, "accuracy_pct_100_minus_mean_nrmse"] = scores["accuracy"]
        else:
            for column in [*SCORE_COLUMNS.values(), "mean_nrmse_pct",
                           "accuracy_pct_100_minus_mean_nrmse"]:
                frame.at[idx, column] = np.nan
            frame.at[idx, "notes"] = (
                f"partial run; error and accuracy omitted; excluded from ranking"
            )

    frame["rank_within_sample"] = np.nan
    frame["rank_within_sample_model_family"] = np.nan
    eligible = frame["comparable_for_ranking"].map(
        lambda value: value is True or str(value).strip().lower() == "true"
    )
    # The published metric is six-decimal.  Rank that published value so
    # numerically identical reruns do not split on sub-ulp CSV noise.
    frame["_rank_score"] = frame["mean_nrmse_pct"].round(6)
    frame.loc[eligible, "rank_within_sample"] = (
        frame.loc[eligible].groupby("sample")["_rank_score"].rank(method="min")
    )
    frame.loc[eligible, "rank_within_sample_model_family"] = (
        frame.loc[eligible].groupby(["sample", "model_family"])["_rank_score"]
        .rank(method="min")
    )

    sample_order = {"SWS3": 0, "SWS4": 1, "SWT1": 2, "SWT2": 3}
    frame["_sample_order"] = frame["sample"].map(sample_order)
    frame["_eligible_order"] = (~eligible).astype(int)
    frame = frame.sort_values(
        ["_sample_order", "_eligible_order", "rank_within_sample", "case"],
        na_position="last",
    ).drop(columns=["_sample_order", "_eligible_order", "_rank_score"]).reset_index(drop=True)

    for column in ("rank_within_sample", "rank_within_sample_model_family",
                   "stages_reached", "total_stages"):
        frame[column] = frame[column].astype("Int64")
    frame["comparable_for_ranking"] = frame["comparable_for_ranking"].map(
        {True: "true", False: "false"}
    )

    columns = list(pd.read_csv(RANKING, nrows=0).columns)
    return frame[columns]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="replace the ranking CSV")
    args = parser.parse_args()
    frame = rebuild()
    if args.write:
        frame.to_csv(RANKING, index=False, float_format="%.6f")
        print(f"wrote {RANKING.relative_to(ROOT)}")
    for sample, group in frame.groupby("sample", sort=False):
        complete = group[group["comparable_for_ranking"].eq("true")]
        best = complete.sort_values(["mean_nrmse_pct", "case"]).iloc[0]
        qualifier = (
            " [nonselectable historical/unphysical]"
            if best["selection_status"] == "historical_unphysical"
            else ""
        )
        print(
            f"{sample}: {len(complete)} ranked, "
            f"{len(group) - len(complete)} partial; numerical best {best['case']} "
            f"({best['mean_nrmse_pct']:.6f}%){qualifier}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
