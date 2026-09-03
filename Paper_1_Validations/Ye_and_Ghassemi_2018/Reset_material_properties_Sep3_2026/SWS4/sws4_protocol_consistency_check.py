#!/usr/bin/env python3
"""Reproducible SW-S4 protocol-consistency check against Ye and Ghassemi (2018).

The five scored observables and range-normalized RMSE definition match the
paper-wide Table 2 audit.  Normal and shear displacement are referenced to the
first hold, and that constructed zero is excluded from their RMSE values.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PI_TARGETS = np.array([8, 12, 16, 20, 24, 28, 24, 20, 16, 12, 8], dtype=float)
SEGMENTS = np.array(["loading"] * 6 + ["unloading"] * 5)
FLAT_TOL_MPA = 1.0e-6

# Ye and Ghassemi (2018), Table 2, SW-S4.  Aperture and permeability are
# derived from Q in the source paper and are intentionally not scored again.
TABLE2 = {
    "Q_ml_min": np.array([0.005, 0.012, 0.022, 0.035, 0.056, 0.113,
                           0.064, 0.037, 0.024, 0.013, 0.005]),
    "sigma_n_MPa": np.array([30.75, 28.73, 26.51, 22.92, 19.25, 15.31,
                              17.13, 19.00, 20.89, 22.82, 24.81]),
    "tau_MPa": np.array([12.56, 12.53, 12.14, 9.38, 6.48, 3.12,
                          2.82, 2.59, 2.41, 2.28, 2.27]),
    "dn_mm": np.array([0.000, 0.000, -0.001, -0.008, -0.021, -0.041,
                        -0.038, -0.036, -0.034, -0.033, -0.032]),
    "ds_mm": np.array([0.000, 0.000, 0.000, 0.017, 0.041, 0.075,
                        0.077, 0.078, 0.079, 0.079, 0.079]),
}

MODEL_COLUMNS = {
    "Q_ml_min": ("flow_rate_validation_ml_min_pp", 1.0),
    "sigma_n_MPa": ("effective_normal_paper_frame_mpa_pp", 1.0),
    "tau_MPa": ("shear_stress_paper_frame_mpa_pp", 1.0),
    # Use the global kinematic jump for both laws; this is the LVDT-like channel.
    "dn_mm": ("frac_normal_dilation_paper_mm", 1.0),
    "ds_mm": ("czm_shear_slip_mm_pp", 1.0),
}

DISPLAY = {
    "Q_ml_min": ("Flow rate", "mL/min"),
    "sigma_n_MPa": ("Effective normal stress", "MPa"),
    "tau_MPa": ("Shear stress", "MPa"),
    "dn_mm": ("Normal displacement", "mm"),
    "ds_mm": ("Shear displacement", "mm"),
}

CASE_LABELS = {
    "116_07_sws4_bb_jrc1p19_fixedpiston_commonK796_ppfix": "BB, measured JRC = 1.19",
    "116_08_sws4_mc_fixedpiston_commonK796_protocol_ppfix": "MC, corrected protocol",
    "116_09_sws4_bb_jrc5_fixedpiston_commonK796_control": "BB, JRC = 5 control",
}

VALIDATION_FILES = {
    "Q_ml_min": "Ye2018_SW4_flow_rate_Vs_time.csv",
    "sigma_n_MPa": "Ye2018_SW4_normal_stress_Vs_time.csv",
    "tau_MPa": "Ye2018_SW4_shear_stress_Vs_time.csv",
    "dn_mm": "Ye2018_SW4_normal_dilation_Vs_time.csv",
    "ds_mm": "Ye2018_SW4_shear_slip_Vs_time.csv",
}


def parse_schedule(deck: Path) -> tuple[np.ndarray, np.ndarray]:
    """Read the PiecewiseLinear injection-pressure schedule from an Orca deck."""
    text = deck.read_text(errors="ignore")
    match = re.search(r"\[injection_pressure\](.*?)\[\]", text, re.S)
    if not match:
        raise ValueError(f"No [injection_pressure] function in {deck}")
    xs = re.search(r"x\s*=\s*'([^']+)'", match.group(1))
    ys = re.search(r"y\s*=\s*'([^']+)'", match.group(1))
    if not xs or not ys:
        raise ValueError(f"The injection schedule in {deck} is not x/y PiecewiseLinear")
    x = np.array([float(value) for value in xs.group(1).split()])
    y_mpa = np.array([float(value) for value in ys.group(1).split()]) * 1.0e-6
    if len(x) != len(y_mpa):
        raise ValueError(f"Schedule length mismatch in {deck}")
    return x, y_mpa


def table2_stage_times(x: np.ndarray, y_mpa: np.ndarray,
                       target_tolerance_mpa: float = 0.15) -> np.ndarray:
    """Reproduce the authoritative branch-aware hold-stage sampling rule."""
    peak = float(np.max(y_mpa))
    at_peak = np.flatnonzero(np.abs(y_mpa - peak) <= FLAT_TOL_MPA)
    peak_start, peak_end = int(at_peak[0]), int(at_peak[-1])
    peak_stage = int(np.argmax(PI_TARGETS))
    times: list[float] = []
    cursor = -math.inf
    for stage, (segment, target) in enumerate(zip(SEGMENTS, PI_TARGETS)):
        if stage == peak_stage:
            chosen = peak_end
        else:
            lo, hi = ((0, peak_start) if segment == "loading"
                      else (peak_end, len(x) - 1))
            indices = np.arange(lo, hi + 1)
            indices = indices[x[indices] > cursor]
            if not len(indices):
                raise ValueError(f"No schedule point remains for Table 2 stage {stage + 1}")
            near = indices[np.abs(y_mpa[indices] - target) <= target_tolerance_mpa]
            chosen = int(near[-1] if len(near)
                         else indices[np.argmin(np.abs(y_mpa[indices] - target))])
        times.append(float(x[chosen]))
        cursor = float(x[chosen])
    return np.array(times)


def _load_history(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    if "time" not in data:
        raise KeyError(f"{path.name} has no time column")
    data = data.apply(pd.to_numeric, errors="coerce")
    return data.sort_values("time").drop_duplicates("time", keep="last").reset_index(drop=True)


def _sample_at_or_before(data: pd.DataFrame, times: np.ndarray, column: str) -> np.ndarray:
    sample_indices = []
    for time in times:
        candidates = data.index[data["time"] <= time]
        if not len(candidates):
            raise ValueError(f"No output at or before t={time:g} s")
        sample_indices.append(int(candidates[-1]))
    return data.loc[sample_indices, column].to_numpy(float)


def _first_crossing(data: pd.DataFrame, values: np.ndarray, threshold: float,
                    pressure_column: str = "injection_pressure_pp") -> tuple[float, float]:
    indices = np.flatnonzero(values >= threshold)
    if not len(indices):
        return np.nan, np.nan
    index = int(indices[0])
    pressure = (float(data[pressure_column].iloc[index]) * 1.0e-6
                if pressure_column in data else np.nan)
    return float(data["time"].iloc[index]), pressure


def _experimental_crossing(validation_dir: Path, stage1_time: float,
                           threshold: float) -> tuple[float, float]:
    slip = pd.read_csv(validation_dir / VALIDATION_FILES["ds_mm"], header=None,
                       names=["time", "value"]).sort_values("time")
    pressure = pd.read_csv(
        validation_dir / "Ye2018_SW4_Injection_pressure_Vs_time.csv",
        header=None, names=["time", "value"]
    ).sort_values("time")
    datum = float(np.interp(stage1_time, slip["time"], slip["value"]))
    indices = np.flatnonzero(slip["value"].to_numpy(float) - datum >= threshold)
    if not len(indices):
        return np.nan, np.nan
    time = float(slip["time"].iloc[int(indices[0])])
    p_mpa = float(np.interp(time, pressure["time"], pressure["value"]))
    return time, p_mpa


def _make_stage_figure(stage_table: pd.DataFrame, case_names: list[str],
                       output: Path) -> None:
    fig, axes = plt.subplots(3, 2, figsize=(12, 13))
    axes = axes.ravel()
    colors = ["#0072B2", "#D55E00", "#009E73"]
    for axis, key in zip(axes, DISPLAY):
        title, unit = DISPLAY[key]
        for branch, marker, fill in (("loading", "o", "black"),
                                      ("unloading", "s", "white")):
            mask = SEGMENTS == branch
            axis.plot(PI_TARGETS[mask], TABLE2[key][mask],
                      color="black", marker=marker, markerfacecolor=fill,
                      linestyle="-" if branch == "loading" else "--",
                      linewidth=1.5, label=f"Experiment, {branch}")
        for color, case in zip(colors, case_names):
            case_data = stage_table.loc[stage_table["case"] == case]
            for branch, marker, linestyle in (("loading", "^", "-"),
                                               ("unloading", "v", "--")):
                sub = case_data.loc[case_data["segment"] == branch]
                axis.plot(sub["Pi_target_MPa"], sub[key], color=color,
                          marker=marker, linestyle=linestyle, linewidth=1.1,
                          markerfacecolor=color if branch == "loading" else "white",
                          label=f"{CASE_LABELS.get(case, case)}, {branch}")
        axis.set_title(title)
        axis.set_xlabel("Injection pressure (MPa)")
        axis.set_ylabel(f"{title} ({unit})")
        axis.set_xticks([8, 12, 16, 20, 24, 28])
        axis.grid(alpha=0.25)
    axes[-1].axis("off")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, fontsize=8,
               bbox_to_anchor=(0.5, 0.01))
    fig.suptitle("SW-S4 protocol-consistency runs versus Ye and Ghassemi (2018), Table 2")
    fig.tight_layout(rect=(0, 0.09, 1, 0.97))
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _make_history_figure(histories: dict[str, pd.DataFrame], validation_dir: Path,
                         stage1_time: float, output: Path) -> None:
    fig, axes = plt.subplots(3, 2, figsize=(12, 13))
    axes = axes.ravel()
    colors = ["#0072B2", "#D55E00", "#009E73"]
    for axis, key in zip(axes, DISPLAY):
        title, unit = DISPLAY[key]
        observed = pd.read_csv(validation_dir / VALIDATION_FILES[key], header=None,
                               names=["time", "value"]).sort_values("time")
        if key in {"dn_mm", "ds_mm"}:
            observed = observed.copy()
            observed["value"] -= np.interp(stage1_time, observed["time"], observed["value"])
        axis.plot(observed["time"], observed["value"], color="black", linewidth=2,
                  label="Digitized experiment")
        for color, (case, data) in zip(colors, histories.items()):
            column, scale = MODEL_COLUMNS[key]
            values = data[column].to_numpy(float) * scale
            if key in {"dn_mm", "ds_mm"}:
                values = values - np.interp(stage1_time, data["time"], values)
            axis.plot(data["time"], values, color=color, linewidth=1,
                      label=CASE_LABELS.get(case, case))
        axis.set_title(title)
        axis.set_xlabel("Time (s)")
        axis.set_ylabel(f"{title} ({unit})")
        axis.grid(alpha=0.25)
    axes[-1].axis("off")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, fontsize=8,
               bbox_to_anchor=(0.5, 0.02))
    fig.suptitle("SW-S4 corrected-protocol histories versus digitized Figure 7 data")
    fig.tight_layout(rect=(0, 0.08, 1, 0.97))
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def run_analysis(base: str | Path | None = None, *, write_outputs: bool = True,
                 make_figures: bool = True) -> dict[str, object]:
    """Run the check and return notebook-friendly DataFrames and output paths."""
    base = Path(base).resolve() if base else Path(__file__).resolve().parent
    result_dir = base / "proposed_inputs" / "protocol_consistency_20260902" / "csv"
    validation_dir = base / "SWS4"
    csv_paths = sorted(result_dir.glob("116_0[789]*.csv"))
    if len(csv_paths) != 3:
        raise FileNotFoundError(f"Expected three 116_07--116_09 CSVs in {result_dir}; found {len(csv_paths)}")

    histories: dict[str, pd.DataFrame] = {}
    stage_frames: list[pd.DataFrame] = []
    metric_rows: list[dict[str, object]] = []
    health_rows: list[dict[str, object]] = []
    common_stage_times: np.ndarray | None = None

    for csv_path in csv_paths:
        case = csv_path.stem
        deck = base / f"{case}.i"
        schedule_time, schedule_pressure = parse_schedule(deck)
        stage_times = table2_stage_times(schedule_time, schedule_pressure)
        if common_stage_times is None:
            common_stage_times = stage_times
        elif not np.allclose(stage_times, common_stage_times):
            raise AssertionError(f"{case} does not use the common SW-S4 pressure schedule")

        data = _load_history(csv_path)
        histories[case] = data
        frame = pd.DataFrame({
            "case": case,
            "case_label": CASE_LABELS.get(case, case),
            "stage": np.arange(1, 12),
            "segment": SEGMENTS,
            "Pi_target_MPa": PI_TARGETS,
            "stage_time_s": stage_times,
        })
        scores = {}
        for key, (column, scale) in MODEL_COLUMNS.items():
            if column not in data:
                raise KeyError(f"{case}: missing required column {column}")
            model = _sample_at_or_before(data, stage_times, column) * scale
            if key in {"dn_mm", "ds_mm"}:
                model = model - model[0]
                scored_slice = slice(1, None)
            else:
                scored_slice = slice(None)
            frame[key] = model
            error = model[scored_slice] - TABLE2[key][scored_slice]
            rmse = float(np.sqrt(np.mean(error ** 2)))
            nrmse = 100.0 * rmse / float(np.ptp(TABLE2[key]))
            scores[key] = nrmse
            metric_rows.append({
                "case": case,
                "case_label": CASE_LABELS.get(case, case),
                "observable": key,
                "rmse": rmse,
                "nRMSE_percent": nrmse,
            })
        metric_rows.append({
            "case": case,
            "case_label": CASE_LABELS.get(case, case),
            "observable": "mean_of_five",
            "rmse": np.nan,
            "nRMSE_percent": float(np.mean(list(scores.values()))),
        })
        stage_frames.append(frame)

        stage1_slip = float(frame["ds_mm"].iloc[0])
        raw_slip = data[MODEL_COLUMNS["ds_mm"][0]].to_numpy(float)
        # frame stage-1 is zero by construction; use the raw value at stage 1 as datum.
        raw_stage1 = _sample_at_or_before(data, stage_times[:1], MODEL_COLUMNS["ds_mm"][0])[0]
        relative_slip = raw_slip - raw_stage1 + stage1_slip
        onset_time, onset_pressure = _first_crossing(data, relative_slip, 0.001)
        slip75_time, slip75_pressure = _first_crossing(data, relative_slip, 0.075)
        post_preload = data.loc[data["time"] >= 55.0]
        key_values = data[["time"] + [column for column, _ in MODEL_COLUMNS.values()]]
        spring_error = pd.to_numeric(post_preload["reaction_vs_machine_spring_mpa_pp"], errors="coerce")
        command = pd.to_numeric(post_preload["axial_command_m_pp"], errors="coerce")
        health_rows.append({
            "case": case,
            "case_label": CASE_LABELS.get(case, case),
            "rows": len(data),
            "final_time_s": float(data["time"].iloc[-1]),
            "complete": bool(data["time"].iloc[-1] >= stage_times[-1]),
            "finite_scored_channels": bool(np.isfinite(key_values.to_numpy()).all()),
            "post55_command_range_um": float((command.max() - command.min()) * 1.0e6),
            "spring_reaction_RMSE_MPa": float(np.sqrt(np.mean(spring_error ** 2))),
            "spring_reaction_max_abs_MPa": float(spring_error.abs().max()),
            "slip_0p001_time_s": onset_time,
            "slip_0p001_pressure_MPa": onset_pressure,
            "slip_0p075_time_s": slip75_time,
            "slip_0p075_pressure_MPa": slip75_pressure,
        })

    assert common_stage_times is not None
    experimental_onset = _experimental_crossing(validation_dir, common_stage_times[0], 0.001)
    experimental_slip75 = _experimental_crossing(validation_dir, common_stage_times[0], 0.075)
    health_rows.append({
        "case": "experiment",
        "case_label": "Digitized experiment",
        "rows": np.nan,
        "final_time_s": np.nan,
        "complete": True,
        "finite_scored_channels": True,
        "post55_command_range_um": np.nan,
        "spring_reaction_RMSE_MPa": np.nan,
        "spring_reaction_max_abs_MPa": np.nan,
        "slip_0p001_time_s": experimental_onset[0],
        "slip_0p001_pressure_MPa": experimental_onset[1],
        "slip_0p075_time_s": experimental_slip75[0],
        "slip_0p075_pressure_MPa": experimental_slip75[1],
    })

    stages = pd.concat(stage_frames, ignore_index=True)
    metrics = pd.DataFrame(metric_rows)
    health = pd.DataFrame(health_rows)
    peak_final = stages.loc[stages["stage"].isin([6, 11])].copy()
    peak_final["state"] = np.where(peak_final["stage"] == 6, "peak injection", "final unloading")

    stage_figure = base / "SWS4_protocol_consistency_Table2.png"
    history_figure = base / "SWS4_protocol_consistency_histories.png"
    if make_figures:
        _make_stage_figure(stages, list(histories), stage_figure)
        _make_history_figure(histories, validation_dir, common_stage_times[0], history_figure)
    if write_outputs:
        stages.to_csv(base / "SWS4_protocol_consistency_stage_values.csv", index=False)
        metrics.to_csv(base / "SWS4_protocol_consistency_metrics.csv", index=False)
        health.to_csv(base / "SWS4_protocol_consistency_health.csv", index=False)

    return {
        "stages": stages,
        "metrics": metrics,
        "health": health,
        "peak_final": peak_final,
        "stage_times_s": common_stage_times,
        "stage_figure": stage_figure,
        "history_figure": history_figure,
    }


if __name__ == "__main__":
    result = run_analysis()
    ranking = result["metrics"].loc[
        result["metrics"]["observable"] == "mean_of_five",
        ["case_label", "nRMSE_percent"],
    ].sort_values("nRMSE_percent")
    print("\nFive-channel Table 2 ranking")
    print(ranking.to_string(index=False, float_format=lambda value: f"{value:.3f}"))
    print("\nProtocol and slip-timing checks")
    print(result["health"].to_string(index=False, float_format=lambda value: f"{value:.4g}"))
    print("\nPeak and final stage values")
    columns = ["case_label", "state", "Q_ml_min", "sigma_n_MPa", "tau_MPa", "dn_mm", "ds_mm"]
    print(result["peak_final"][columns].to_string(index=False, float_format=lambda value: f"{value:.4g}"))
