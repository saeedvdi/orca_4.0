#!/usr/bin/env python3
"""Analyze the completed SW-S3 and tensile-fracture mechanism tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PAPER_CASES = Path(__file__).resolve().parents[2]
VALIDATION = PAPER_CASES.parent
ORCA = VALIDATION.parents[1]
OUT = Path(__file__).resolve().parent
GATE_PATH = ORCA / "scripts/table2_gate.py"

CASES = {
    "110_01_sw3_floor1nm_g040_ppfix": ("SWS3", "SW-S3 control", "control"),
    "110_02_sw3_floor1nm_nodilation_ppfix": ("SWS3", "SW-S3 no hydraulic dilation", "no dilation"),
    "110_03_sw3_floor1nm_nogouge_ppfix": ("SWS3", "SW-S3 no gouge loss", "no gouge"),
    "111_01_swt1_floor1nm_control_ppfix": ("SWT1", "SW-T1 control", "control"),
    "111_02_swt1_floor1nm_nokinematic_ppfix": ("SWT1", "SW-T1 no kinematic mapping", "no kinematic"),
    "111_03_swt2_floor1nm_control_ppfix": ("SWT2", "SW-T2 control", "control"),
    "111_04_swt2_floor1nm_nokinematic_ppfix": ("SWT2", "SW-T2 no kinematic mapping", "no kinematic"),
}

CONTROL = {
    "SWS3": "110_01_sw3_floor1nm_g040_ppfix",
    "SWT1": "111_01_swt1_floor1nm_control_ppfix",
    "SWT2": "111_03_swt2_floor1nm_control_ppfix",
}

PARENTS = {
    "SWS3": (
        PAPER_CASES / "01_Main_Validation/SWS3/BB/100_06_sw3_resc1p30_unld0p00_ppfix_hpc.csv",
        PAPER_CASES / "01_Main_Validation/SWS3/BB/100_06_sw3_resc1p30_unld0p00_ppfix.i",
    ),
    "SWT1": (
        PAPER_CASES / "01_Main_Validation/SWT1/BB/107_01_swt1_coh27p2_apscale0p01512_ppfix.csv",
        PAPER_CASES / "01_Main_Validation/SWT1/BB/107_01_swt1_coh27p2_apscale0p01512_ppfix.i",
    ),
    "SWT2": (
        PAPER_CASES / "01_Main_Validation/SWT2/BB/100_04_swt2_apscale0p0177_ppfix_hpc.csv",
        PAPER_CASES / "01_Main_Validation/SWT2/BB/100_04_swt2_apscale0p0177_ppfix.i",
    ),
}

CASE_PATHS = {
    stem: PAPER_CASES
    / "02_Mechanism_Tests"
    / ("SWS3_110" if stem.startswith("110_") else "SWT1_111" if "swt1" in stem else "SWT2_111")
    for stem in CASES
}


def load_gate():
    spec = importlib.util.spec_from_file_location("table2_gate_followup", GATE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module.find_deck = lambda csv_path, tag: CASE_PATHS[csv_path.stem] / "inputs" / f"{csv_path.stem}.i"
    return module


GATE = load_gate()


def build_metrics() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict]]:
    stage_frames: list[pd.DataFrame] = []
    summaries: list[dict] = []
    scored: dict[str, dict] = {}

    for stem, (sample, label, variant) in CASES.items():
        csv_path = CASE_PATHS[stem] / "results" / f"{stem}.csv"
        raw = pd.read_csv(csv_path)
        score = GATE.score_run(csv_path, sample, None, 0.15, "stage1", 55.0, "kinematic")
        nrmse = GATE.normalised_scores(score)
        scored[stem] = score
        table = score["table"].copy()
        table.insert(0, "variant", variant)
        table.insert(0, "label", label)
        table.insert(0, "stem", stem)
        table.insert(0, "sample", sample)
        stage_frames.append(table)

        initial = table.iloc[0]
        peak = table.iloc[5]
        final = table.iloc[10]
        k0 = float(initial["k_1e12_m2_model"])
        min_stage_mean_aperture_um = float(table["ah_um_model"].min())
        summaries.append({
            "sample": sample,
            "stem": stem,
            "label": label,
            "variant": variant,
            "rows": len(raw),
            "run_end_s": score["t_end"],
            "stages_reached": score["reached"],
            "duplicate_times": int(raw["time"].duplicated().sum()),
            "nan_cells": int(raw.isna().sum().sum()),
            "minimum_scored_stage_mean_aperture_um": min_stage_mean_aperture_um,
            "floor_um": 0.001,
            "scored_stage_mean_aperture_reaches_floor": bool(min_stage_mean_aperture_um <= 0.001001),
            "initial_flow_ml_min": float(initial["Q_ml_min_model"]),
            "peak_flow_ml_min": float(peak["Q_ml_min_model"]),
            "final_flow_ml_min": float(final["Q_ml_min_model"]),
            "initial_aperture_um": float(initial["ah_um_model"]),
            "peak_aperture_um": float(peak["ah_um_model"]),
            "final_aperture_um": float(final["ah_um_model"]),
            "initial_permeability_1e12_m2": k0,
            "peak_permeability_1e12_m2": float(peak["k_1e12_m2_model"]),
            "final_permeability_1e12_m2": float(final["k_1e12_m2_model"]),
            "peak_permeability_ratio": float(peak["k_1e12_m2_model"] / k0),
            "final_permeability_ratio": float(final["k_1e12_m2_model"] / k0),
            "flow_nRMSE_percent": nrmse["Q_ml_min"],
            "sigma_n_nRMSE_percent": nrmse["sigma_n_MPa"],
            "tau_nRMSE_percent": nrmse["tau_MPa"],
            "dn_nRMSE_percent": nrmse["dn_mm"],
            "ds_nRMSE_percent": nrmse["ds_mm"],
            "five_channel_mean_nRMSE_percent": nrmse["mean"],
        })

    stages = pd.concat(stage_frames, ignore_index=True)
    summary = pd.DataFrame(summaries)

    for sample, control_stem in CONTROL.items():
        control = scored[control_stem]["table"].set_index("stage")
        for index in summary.index[summary["sample"] == sample]:
            stem = summary.loc[index, "stem"]
            case = scored[stem]["table"].set_index("stage")
            for key, output in (
                ("sigma_n_MPa_model", "max_delta_sigma_n_MPa_vs_control"),
                ("tau_MPa_model", "max_delta_tau_MPa_vs_control"),
                ("dn_mm_model", "max_delta_dn_mm_vs_control"),
                ("ds_mm_model", "max_delta_ds_mm_vs_control"),
            ):
                summary.loc[index, output] = float((case[key] - control[key]).abs().max())

    return stages, summary, scored


def compare_parents(scored: dict[str, dict]) -> pd.DataFrame:
    records = []
    original_find_deck = GATE.find_deck
    try:
        for sample, control_stem in CONTROL.items():
            parent_csv, parent_deck = PARENTS[sample]
            GATE.find_deck = lambda csv_path, tag, deck=parent_deck: deck
            parent = GATE.score_run(parent_csv, sample, None, 0.15, "stage1", 55.0, "kinematic")
            parent_nrmse = GATE.normalised_scores(parent)
            control = scored[control_stem]
            control_nrmse = GATE.normalised_scores(control)
            row = {
                "sample": sample,
                "parent_csv": str(parent_csv),
                "relaxed_floor_control_csv": str(CASE_PATHS[control_stem] / "results" / f"{control_stem}.csv"),
                "parent_flow_nRMSE_percent": parent_nrmse["Q_ml_min"],
                "control_flow_nRMSE_percent": control_nrmse["Q_ml_min"],
                "parent_five_channel_mean_nRMSE_percent": parent_nrmse["mean"],
                "control_five_channel_mean_nRMSE_percent": control_nrmse["mean"],
            }
            for key, output in (
                ("Q_ml_min_model", "max_delta_flow_ml_min"),
                ("ah_um_model", "max_delta_hydraulic_aperture_um"),
                ("k_1e12_m2_model", "max_delta_permeability_1e12_m2"),
                ("sigma_n_MPa_model", "max_delta_sigma_n_MPa"),
                ("tau_MPa_model", "max_delta_tau_MPa"),
                ("dn_mm_model", "max_delta_dn_mm"),
                ("ds_mm_model", "max_delta_ds_mm"),
            ):
                row[output] = float((control["table"][key] - parent["table"][key]).abs().max())
            records.append(row)
    finally:
        GATE.find_deck = original_find_deck
    return pd.DataFrame(records)


def build_figure(stages: pd.DataFrame) -> None:
    colors = {"experiment": "#111111", "control": "#4C78A8", "no dilation": "#F58518",
              "no gouge": "#54A24B", "no kinematic": "#E45756"}
    sample_title = {"SWS3": "(a) SW-S3", "SWT1": "(b) SW-T1", "SWT2": "(c) SW-T2"}
    fig, axes = plt.subplots(1, 3, figsize=(14.2, 4.6), sharex=True, constrained_layout=True)
    x = np.arange(1, 12)

    for ax, sample in zip(axes, ("SWS3", "SWT1", "SWT2")):
        experiment = np.asarray(GATE.TABLE2[sample]["k_1e12_m2"], dtype=float)
        experiment /= experiment[0]
        ax.plot(x, experiment, color=colors["experiment"], marker="o", linewidth=2.0,
                label="Experiment")
        subset = stages.loc[stages["sample"] == sample]
        for label, case in subset.groupby("label", sort=False):
            variant = str(case["variant"].iloc[0])
            k = case["k_1e12_m2_model"].to_numpy(dtype=float)
            ax.plot(x, k / k[0], marker="o", linewidth=1.8, color=colors[variant], label=label)
        ax.axvline(6, color="0.7", linestyle=":", linewidth=1.0)
        ax.axhline(1, color="0.5", linestyle="--", linewidth=1.0)
        ax.set_title(sample_title[sample])
        ax.set_xticks(x)
        ax.set_xlabel("Injection stage")
        ax.grid(alpha=0.2)
        ax.legend(frameon=False, fontsize=8)

    axes[0].set_ylabel("Permeability / stage-1 permeability")
    figure_dir = OUT / "figures"
    figure_dir.mkdir(exist_ok=True)
    fig.savefig(figure_dir / "Figure_Followup_110_111_Mechanism_Tests.pdf", bbox_inches="tight")
    fig.savefig(figure_dir / "Figure_Followup_110_111_Mechanism_Tests.png", dpi=300,
                bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    stages, summary, scored = build_metrics()
    parent_comparison = compare_parents(scored)
    result_dir = OUT / "results"
    result_dir.mkdir(exist_ok=True)
    stages.to_csv(result_dir / "followup_110_111_stage_metrics.csv", index=False)
    summary.to_csv(result_dir / "followup_110_111_summary_metrics.csv", index=False)
    parent_comparison.to_csv(result_dir / "followup_110_111_parent_control_comparison.csv", index=False)
    build_figure(stages)
    cols = [
        "sample", "variant", "stages_reached", "peak_flow_ml_min", "final_flow_ml_min",
        "peak_aperture_um", "final_aperture_um", "peak_permeability_1e12_m2",
        "final_permeability_1e12_m2", "peak_permeability_ratio", "final_permeability_ratio",
        "flow_nRMSE_percent", "five_channel_mean_nRMSE_percent",
        "max_delta_sigma_n_MPa_vs_control", "max_delta_tau_MPa_vs_control",
        "max_delta_dn_mm_vs_control", "max_delta_ds_mm_vs_control",
    ]
    print(summary[cols].to_string(index=False, float_format=lambda value: f"{value:.6g}"))


if __name__ == "__main__":
    main()
