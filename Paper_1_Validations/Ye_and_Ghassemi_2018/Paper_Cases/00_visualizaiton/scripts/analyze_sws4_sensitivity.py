#!/usr/bin/env python3
"""Analyze the three SW-S4 hydraulic sensitivity runs against the calibrated case."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
try:
    from netCDF4 import Dataset
except ModuleNotFoundError:  # Stage metrics remain available without Exodus field sampling.
    Dataset = None

# Manuscript figure style: serif text and math so these panels match the rest of
# the paper's figures, and 600 dpi on every raster export. Times New Roman is not
# installed here, so Nimbus Roman (its metric-compatible URW clone) leads the stack.
plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Nimbus Roman", "Times New Roman", "DejaVu Serif", "serif"],
        "mathtext.fontset": "stix",
        "figure.dpi": 600,
        "savefig.dpi": 600,
    }
)


PAPER_CASES = Path(__file__).resolve().parents[3]
VALIDATION = PAPER_CASES.parent
ORCA = VALIDATION.parents[1]
DECK = PAPER_CASES / "01_Main_Validation/SWS4/BB/93_07_sw4_final_theta30_jrc5_ppfix.i"
RUN_DIR = PAPER_CASES / "02_Mechanism_Tests/SWS4_Legacy_Ablations"
FOLLOWUP_DIR = PAPER_CASES / "02_Mechanism_Tests/SWS4_109"
OUT = Path(__file__).resolve().parent

RUNS = {
    "Calibrated BB": {
        "csv": PAPER_CASES / "01_Main_Validation/SWS4/BB/93_07_sw4_final_theta30_jrc5_ppfix_hpc.csv",
        "exodus": None,
        "floor_m": 0.74e-6,
    },
    "No dilation": {
        "csv": RUN_DIR / "results/sws4_ab_no_dilation.csv",
        "exodus": None,
        "floor_m": 0.74e-6,
    },
    "No gouge": {
        "csv": RUN_DIR / "results/sws4_ab_no_gouge.csv",
        "exodus": None,
        "floor_m": 0.74e-6,
    },
    "Strong gouge, relaxed floor": {
        "csv": RUN_DIR / "results/sws4_loss_g056.csv",
        "exodus": None,
        "floor_m": 1.0e-9,
    },
    "Calibrated gouge, relaxed floor": {
        "csv": FOLLOWUP_DIR / "results/109_01_sw4_floor1nm_g028_ppfix.csv",
        "exodus": None,
        "floor_m": 1.0e-9,
    },
    "Intermediate gouge, relaxed floor": {
        "csv": FOLLOWUP_DIR / "results/109_02_sw4_floor1nm_g042_ppfix.csv",
        "exodus": None,
        "floor_m": 1.0e-9,
    },
    "No hydraulic dilation, relaxed floor": {
        "csv": FOLLOWUP_DIR / "results/109_03_sw4_floor1nm_nodilation_ppfix.csv",
        "exodus": None,
        "floor_m": 1.0e-9,
    },
}


def load_gate():
    path = ORCA / "scripts/table2_gate.py"
    spec = importlib.util.spec_from_file_location("table2_gate", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module.find_deck = lambda csv_path, tag: DECK
    return module


GATE = load_gate()


def sample_stages(csv_path: Path, times: list[float]) -> pd.DataFrame:
    raw = pd.read_csv(csv_path).sort_values("time")
    rows = []
    for stage, target_time in enumerate(times, start=1):
        row = raw.loc[raw["time"] <= target_time].iloc[-1].copy()
        row["stage"] = stage
        rows.append(row)
    return pd.DataFrame(rows).set_index("stage")


def exodus_aperture(exodus_path: Path | None, times: list[float], floor_m: float) -> dict[int, dict]:
    output = {}
    if Dataset is None or exodus_path is None or not exodus_path.is_file():
        return output
    with Dataset(exodus_path) as dataset:
        exodus_time = np.asarray(dataset.variables["time_whole"][:], dtype=float)
        aperture = dataset.variables["vals_elem_var1eb3"]
        for stage in (1, 6, 11):
            index = np.flatnonzero(exodus_time <= times[stage - 1] + 1.0e-9)[-1]
            values = np.asarray(aperture[index, :], dtype=float)
            output[stage] = {
                "field_min_aperture_um": float(values.min() * 1.0e6),
                "field_mean_aperture_um": float(values.mean() * 1.0e6),
                "field_max_aperture_um": float(values.max() * 1.0e6),
                "field_fraction_at_floor": float(np.mean(values <= floor_m * (1.0 + 1.0e-6))),
            }
    return output


def build_metrics() -> pd.DataFrame:
    schedule_x, schedule_y = GATE.parse_schedule(DECK)
    times = GATE.stage_times(schedule_x, schedule_y, 0.15)
    records = []
    for run_name, config in RUNS.items():
        stages = sample_stages(config["csv"], times)
        score = GATE.score_run(config["csv"], "SWS4", None, 0.15, "stage1", 55.0, "kinematic")
        nrmse = GATE.normalised_scores(score)
        field = exodus_aperture(config["exodus"], times, config["floor_m"])
        k0 = float(stages.loc[1, "fracture_permeability_pp"])
        for stage in range(1, 12):
            row = stages.loc[stage]
            record = {
                "run": run_name,
                "stage": stage,
                "segment": GATE.SEGMENTS[stage - 1],
                "injection_pressure_target_MPa": GATE.PI_TARGETS[stage - 1],
                "permeability_m2": float(row["fracture_permeability_pp"]),
                "permeability_ratio": float(row["fracture_permeability_pp"] / k0),
                "hydraulic_aperture_um": float(row["hydraulic_aperture_pp"] * 1.0e6),
                "flow_rate_ml_min": float(row["flow_rate_validation_ml_min_pp"]),
                "effective_normal_stress_MPa": float(row["effective_normal_paper_frame_mpa_pp"]),
                "shear_stress_MPa": float(row["shear_stress_paper_frame_mpa_pp"]),
                "normal_displacement_mm": float(row["frac_normal_dilation_paper_mm"]),
                "shear_displacement_mm": float(row["czm_shear_slip_mm_pp"]),
                "normal_stress_aperture_um": float(row["normal_stress_aperture_pp"] * 1.0e6),
                "cumulative_dilation_um": float(row["cumulative_dilation_pp"] * 1.0e6),
                "roughness_state": float(row["roughness_state_pp"]),
                "gouge_loss_um": float(row["slip_damage_aperture_pp"] * 1.0e6),
                "flow_nRMSE_percent": nrmse["Q_ml_min"],
                "five_channel_mean_nRMSE_percent": nrmse["mean"],
                "aperture_floor_um": config["floor_m"] * 1.0e6,
                "field_min_aperture_um": np.nan,
                "field_mean_aperture_um": np.nan,
                "field_max_aperture_um": np.nan,
                "field_fraction_at_floor": np.nan,
            }
            if stage in field:
                record.update(field[stage])
            records.append(record)
    return pd.DataFrame(records)


def build_figure(metrics: pd.DataFrame) -> None:
    colors = {
        "Experiment": "#111111",
        "Calibrated BB": "#4c78a8",
        "No dilation": "#f58518",
        "No gouge": "#54a24b",
        "Strong gouge, relaxed floor": "#e45756",
        "Calibrated gouge, relaxed floor": "#b279a2",
        "Intermediate gouge, relaxed floor": "#ff9da6",
        "No hydraulic dilation, relaxed floor": "#9d755d",
    }
    experiment = np.asarray(GATE.TABLE2["SWS4"]["k_1e12_m2"], dtype=float)
    experiment /= experiment[0]

    display = {
        "Calibrated BB": "Calibrated\n(g=0.28, floor=0.74)",
        "No dilation": "No dilation\n(floor=0.74)",
        "No gouge": "No gouge\n(floor=0.74)",
        "Strong gouge, relaxed floor": "g=0.56\n(floor=0.001)",
        "Calibrated gouge, relaxed floor": "g=0.28\n(floor=0.001)",
        "Intermediate gouge, relaxed floor": "g=0.42\n(floor=0.001)",
        "No hydraulic dilation, relaxed floor": "No hyd. dilation\n(floor=0.001)",
    }

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.6), constrained_layout=True,
                             gridspec_kw={"width_ratios": [1.35, 1.0]})
    stages = np.arange(1, 12)
    axes[0].plot(stages, experiment, color=colors["Experiment"], marker="o", linewidth=2.0,
                 label="Experiment")
    for run_name in RUNS:
        selected = metrics.loc[metrics["run"] == run_name]
        linestyle = "--" if run_name == "Calibrated gouge, relaxed floor" else "-"
        marker = None if run_name == "Calibrated gouge, relaxed floor" else "o"
        axes[0].plot(selected["stage"], selected["permeability_ratio"],
                     linewidth=1.7, linestyle=linestyle, marker=marker,
                     color=colors[run_name], label=display[run_name])
    axes[0].axhline(1.0, color="0.45", linestyle="--", linewidth=1.0)
    axes[0].axvline(6.0, color="0.75", linestyle=":", linewidth=1.0)
    axes[0].set_xlabel("Injection stage")
    axes[0].set_ylabel("Permeability / initial permeability")
    axes[0].set_xticks(stages)
    axes[0].grid(alpha=0.2)
    axes[0].set_title("(a) Evolution through loading and unloading")

    peak = [float(experiment[5])]
    final = [float(experiment[10])]
    labels = ["Experiment"]
    for run_name in RUNS:
        selected = metrics.loc[metrics["run"] == run_name].set_index("stage")
        peak.append(selected.loc[6, "permeability_ratio"])
        final.append(selected.loc[11, "permeability_ratio"])
        labels.append(display[run_name])
    y = np.arange(len(labels))
    width = 0.36
    axes[1].barh(y - width / 2, peak, width, color="#72b7b2", label="Peak")
    axes[1].barh(y + width / 2, final, width, color="#b279a2", label="Final")
    axes[1].axvline(1.0, color="0.3", linestyle="--", linewidth=1.0)
    axes[1].set_yticks(y, labels)
    axes[1].invert_yaxis()
    axes[1].set_xlabel("Permeability / initial permeability")
    axes[1].set_title("(b) Peak enhancement and final retention")
    axes[1].legend(frameon=False)
    axes[1].grid(axis="x", alpha=0.2)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, ncol=4, loc="outside lower center", frameon=False)
    figure_dir = OUT / "figures"
    figure_dir.mkdir(exist_ok=True)
    fig.savefig(figure_dir / "Figure_SWS4_Hydraulic_Sensitivity.pdf", bbox_inches="tight")
    fig.savefig(figure_dir / "Figure_SWS4_Hydraulic_Sensitivity.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    metrics = build_metrics()
    result_dir = OUT / "results"
    result_dir.mkdir(exist_ok=True)
    metrics.to_csv(result_dir / "sws4_hydraulic_sensitivity_metrics.csv", index=False)
    build_figure(metrics)
    summary = metrics.loc[metrics["stage"].isin([1, 6, 11]), [
        "run", "stage", "permeability_ratio", "hydraulic_aperture_um",
        "flow_rate_ml_min", "flow_nRMSE_percent", "five_channel_mean_nRMSE_percent",
        "field_min_aperture_um", "field_mean_aperture_um", "field_max_aperture_um",
        "field_fraction_at_floor",
    ]]
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
