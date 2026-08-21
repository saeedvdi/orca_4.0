#!/usr/bin/env python3
"""Plot the best-ranked Ye & Ghassemi case for every fracture sample.

The layout follows Ye & Ghassemi (2018), Figure 7: four sample panels, each
containing three stacked time-history axes. Stage boundaries follow the paper's
physical definition and are resolved from each selected input deck's actual
injection schedule:

* Stage 1: stick state below 24 MPa (SWT1/SWT2/SWS3) or 16 MPa (SWS4)
* Stage 2: injection loading from that threshold to the peak pressure
* Stage 3: unloading from the peak pressure

The selected result is the lowest-ranked complete case in
TABLE2_ERROR_ACCURACY_RANKING.csv. If rank 1 is tied, an authoritative
validation case is preferred. Flow rate and permeability are sampled at the
eleven Table-2 hold stages; all other histories are plotted continuously.
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import matplotlib

# Use a file-only backend for command-line execution, but preserve Jupyter's
# inline/widget backend when this module is imported by a notebook.
if __name__ == "__main__":
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator, ScalarFormatter
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RANKING_PATH = (
    PROJECT_ROOT
    / "doc"
    / "independent_analysis"
    / "TABLE2_ERROR_ACCURACY_RANKING.csv"
)
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "doc" / "independent_analysis" / "figures"

SAMPLE_ORDER = ("SWT1", "SWT2", "SWS3", "SWS4")
DISPLAY_NAME = {
    "SWT1": "SW-T1",
    "SWT2": "SW-T2",
    "SWS3": "SW-S3",
    "SWS4": "SW-S4",
}
PANEL_LABEL = dict(zip(SAMPLE_ORDER, "abcd"))
STICK_THRESHOLD_MPA = {"SWT1": 24.0, "SWT2": 24.0, "SWS3": 24.0, "SWS4": 16.0}

# Digitized histories used by the established sample-validation notebooks.
# Piston and production-pressure data are overlaid only where they exist.
VALIDATION_FILES = {
    "SWT1": {
        "piston": "SWT1_piston_displacement_mm.csv",
        "differential": "SWT1_differential_stress.csv",
        "injection": "SWT1_injection_pressure_MPa.csv",
        "production": "SWt1_produciton_pressure.csv",
        "slip": "SWT1_shear_slip_mm.csv",
        "dilation": "SWT1_normal_dilation.csv",
        "shear": "SWT1_shear_stress.csv",
        "normal": "SWT1_effective_normal_stress.csv",
        "permeability": "SWT1_fracture_permeability_m2.csv",
        "flow": "SWt1_flow_rate.csv",
    },
    "SWT2": {
        "piston": "SWT2_piston_Displacement_mm.csv",
        "differential": "SWt2_differential_stress.csv",
        "injection": "SWT2_injection_pressure_MPA.csv",
        "production": "SWT2_production_pressure_MPa.csv",
        "slip": "SWt2_shear_dilation_mm.csv",
        "dilation": "SWT2_normal_dilation_mm.csv",
        "shear": "SWT2_shear_stress_MPa.csv",
        "normal": "SWT2_effective_normal_stress_MPa.csv",
        "permeability": "SWt2_fracture_peremabiltiy_m2.csv",
        "flow": "SWt2_flow_rate_ml:min.csv",
    },
    "SWS3": {
        "piston": "piston_disp_mm_vs_time_sw3.csv",
        "differential": "differnetial_stress_vs_time_sw3.csv",
        "injection": "Injection_pressure_vs_time_SW3.csv",
        "slip": "shear_slip_mm_vs_time_sw3.csv",
        "dilation": "normal_dilation_mm_vs_time_sw3.csv",
        "shear": "shear_stress_MPa_vs_time_sw3.csv",
        "normal": "effective_normal_stress_mpa_Vs_time_SW3.csv",
        "permeability": "permeability_m2_vs_time_sw3_corrected.table2",
        "flow": "flow_Rate_mlmin_vs_time_sw3.csv",
    },
    "SWS4": {
        "differential": "Ye2018_SW4_Differential_Stress_Vs_time.csv",
        "injection": "Ye2018_SW4_Injection_pressure_Vs_time.csv",
        "slip": "Ye2018_SW4_shear_slip_Vs_time.csv",
        "dilation": "Ye2018_SW4_normal_dilation_Vs_time.csv",
        "shear": "Ye2018_SW4_shear_stress_Vs_time.csv",
        "normal": "Ye2018_SW4_normal_stress_Vs_time.csv",
        "permeability": "Ye2018_SW4_frac_perm_Vs_time.csv",
        "flow": "Ye2018_SW4_flow_rate_Vs_time.csv",
    },
}

SEGMENTS = ("loading",) * 6 + ("unloading",) * 5
PI_TARGETS = (8, 12, 16, 20, 24, 28, 24, 20, 16, 12, 8)
FLAT_TOL_MPA = 1.0e-3
TARGET_TOL_MPA = 0.35

COLORS = {
    "piston": "#00c92d",
    "differential": "#00cfd0",
    "injection": "#0047ff",
    "production": "#9a9a9a",
    "slip": "#ff00c8",
    "dilation": "#9b52ff",
    "shear": "#d6b600",
    "normal": "#191919",
    "permeability": "#07951c",
    "flow": "#083b9c",
    "stage": "#ff4b4b",
}

COLUMN_CANDIDATES = {
    "differential": (("differential_stress_reaction_mpa_pp", 1.0),
                     ("differential_stress_mpa_pp", 1.0)),
    "injection": (("injection_pressure_pp", 1.0e-6),),
    "production": (("pp_outlet_pp", 1.0e-6),),
    "slip": (("czm_shear_slip_mm_pp", 1.0),
             ("reported_czm_shear_slip_mm_pp", 1.0)),
    "dilation": (("czm_normal_dilation_paper_mm_pp", 1.0),
                 ("frac_normal_dilation_paper_mm", 1.0)),
    "shear": (("shear_stress_paper_frame_mpa_pp", 1.0),
              ("shear_traction_magnitude_pa", 1.0e-6)),
    "normal": (("effective_normal_paper_frame_mpa_pp", 1.0),
               ("bb_effective_normal_stress_pp", 1.0e-6),
               ("effective_normal_compression_mpa_pp", 1.0)),
    "permeability": (("fracture_permeability_pp", 1.0),),
    "flow": (("flow_rate_validation_ml_min_pp", 1.0),),
}


def finite_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().eq("true")


def select_best_cases(
    ranking: pd.DataFrame,
    case_names: dict[str, str] | None = None,
) -> dict[str, pd.Series]:
    if case_names is not None:
        selected: dict[str, pd.Series] = {}
        for sample in SAMPLE_ORDER:
            if sample not in case_names:
                raise KeyError(f"No manually selected case was provided for {sample}")
            rows = ranking.loc[
                ranking["sample"].eq(sample)
                & ranking["case"].eq(case_names[sample])
            ]
            if len(rows) != 1:
                raise ValueError(
                    f"{sample}: expected one ranking row for "
                    f"{case_names[sample]!r}; found {len(rows)}"
                )
            selected[sample] = rows.iloc[0]
        return selected

    complete = (
        ranking["run_status"].astype(str).str.lower().eq("complete")
        & finite_bool(ranking["comparable_for_ranking"])
    )
    selected: dict[str, pd.Series] = {}
    for sample in SAMPLE_ORDER:
        rows = ranking.loc[complete & ranking["sample"].eq(sample)].copy()
        if rows.empty:
            raise ValueError(f"No complete ranked case is available for {sample}")
        best_rank = pd.to_numeric(rows["rank_within_sample"], errors="raise").min()
        rows = rows.loc[rows["rank_within_sample"].eq(best_rank)].copy()
        rows["authoritative_preference"] = np.where(
            rows["selection_status"].eq("authoritative_validation"), 0, 1
        )
        rows = rows.sort_values(
            ["authoritative_preference", "mean_nrmse_pct", "case"],
            kind="stable",
        )
        selected[sample] = rows.iloc[0]
    return selected


def result_and_deck(row: pd.Series) -> tuple[Path, Path]:
    csv_path = PROJECT_ROOT / str(row["source_csv"])
    if not csv_path.is_file():
        raise FileNotFoundError(csv_path)
    stem = csv_path.stem.removesuffix("_hpc")
    deck = csv_path.parent.parent / f"{stem}.i"
    if not deck.is_file():
        raise FileNotFoundError(
            f"Could not map ranked result {csv_path.name} to input deck {deck}"
        )
    return csv_path, deck


def parse_schedule(deck: Path) -> tuple[np.ndarray, np.ndarray]:
    text = deck.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\[injection_pressure\](.*?)\[\]", text, re.S)
    if not match:
        raise ValueError(f"No [injection_pressure] block in {deck}")
    block = match.group(1)
    x_match = re.search(r"(?m)^\s*x\s*=\s*'([^']+)'", block)
    y_match = re.search(r"(?m)^\s*y\s*=\s*'([^']+)'", block)
    if not x_match or not y_match:
        raise ValueError(f"Injection schedule in {deck} has no quoted x/y arrays")
    time = np.array([float(value) for value in x_match.group(1).split()])
    pressure = np.array([float(value) for value in y_match.group(1).split()]) * 1.0e-6
    if len(time) != len(pressure):
        raise ValueError(f"Injection x/y length mismatch in {deck}")
    return time, pressure


def hold_stage_times(schedule_time: np.ndarray, schedule_pressure: np.ndarray) -> list[float]:
    peak_value = float(np.max(schedule_pressure))
    peak_indices = np.flatnonzero(
        np.abs(schedule_pressure - peak_value) <= FLAT_TOL_MPA
    )
    peak_start, peak_end = int(peak_indices[0]), int(peak_indices[-1])
    peak_stage = int(np.argmax(PI_TARGETS))
    times: list[float] = []
    cursor = -math.inf
    for stage, (segment, target) in enumerate(zip(SEGMENTS, PI_TARGETS)):
        if stage == peak_stage:
            chosen = peak_end
        else:
            lo, hi = (
                (0, peak_start)
                if segment == "loading"
                else (peak_end, len(schedule_time) - 1)
            )
            indices = np.arange(lo, hi + 1)
            indices = indices[schedule_time[indices] > cursor]
            near = indices[
                np.abs(schedule_pressure[indices] - target) <= TARGET_TOL_MPA
            ]
            chosen = (
                int(near[-1])
                if near.size
                else int(indices[np.argmin(np.abs(schedule_pressure[indices] - target))])
            )
        times.append(float(schedule_time[chosen]))
        cursor = float(schedule_time[chosen])
    return times


def stage_boundaries(
    sample: str, schedule_time: np.ndarray, schedule_pressure: np.ndarray
) -> tuple[float, float]:
    first_peak = int(np.argmax(schedule_pressure))
    loading_time = schedule_time[: first_peak + 1]
    loading_pressure = schedule_pressure[: first_peak + 1]
    threshold = STICK_THRESHOLD_MPA[sample]
    reached = np.flatnonzero(loading_pressure >= threshold - FLAT_TOL_MPA)
    if not reached.size:
        raise ValueError(f"{sample} injection schedule never reaches {threshold:g} MPa")
    stage_1_end = float(loading_time[reached[0]])
    peak = float(np.max(schedule_pressure))
    peak_indices = np.flatnonzero(np.abs(schedule_pressure - peak) <= FLAT_TOL_MPA)
    stage_2_end = float(schedule_time[peak_indices[-1]])
    return stage_1_end, stage_2_end


def model_series(frame: pd.DataFrame, key: str) -> np.ndarray:
    for column, scale in COLUMN_CANDIDATES[key]:
        if column in frame.columns:
            return pd.to_numeric(frame[column], errors="coerce").to_numpy(float) * scale
    candidates = ", ".join(name for name, _ in COLUMN_CANDIDATES[key])
    raise KeyError(f"No {key} column; tried {candidates}")


def load_validation_curves(sample: str) -> dict[str, pd.DataFrame]:
    directory = PROJECT_ROOT / "Examples" / "YeGhasemmi2018" / sample / sample
    curves: dict[str, pd.DataFrame] = {}
    for key, filename in VALIDATION_FILES[sample].items():
        path = directory / filename
        if not path.is_file():
            continue
        frame = pd.read_csv(path, header=None, names=("time", "value"))
        frame["time"] = pd.to_numeric(frame["time"], errors="coerce")
        frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
        curves[key] = (
            frame.dropna()
            .sort_values("time")
            .drop_duplicates("time", keep="last")
            .reset_index(drop=True)
        )
    return curves


def plot_validation_curve(
    ax: plt.Axes,
    curve: pd.DataFrame | None,
    color: str,
) -> None:
    """Overlay a complete digitized history with legible open markers."""
    if curve is None or curve.empty:
        return
    time = curve["time"].to_numpy(float)
    values = curve["value"].to_numpy(float)
    marker_interval = max(1, len(curve) // 18)
    ax.plot(
        time,
        values,
        color=color,
        linestyle="none",
        alpha=0.9,
        marker="o",
        markersize=2.0,
        markerfacecolor="white",
        markeredgecolor=color,
        markeredgewidth=0.55,
        markevery=marker_interval,
        zorder=6,
    )


def include_validation(values: np.ndarray, curve: pd.DataFrame | None) -> np.ndarray:
    if curve is None or curve.empty:
        return np.asarray(values, dtype=float)
    return np.concatenate(
        [np.asarray(values, dtype=float), curve["value"].to_numpy(float)]
    )


def align_absolute_reference(
    time: np.ndarray,
    values: np.ndarray,
    curve: pd.DataFrame | None,
    reference_time: float = 55.0,
) -> np.ndarray:
    """Align an incremental numerical command to an absolute measured channel."""
    if curve is None or curve.empty:
        return values
    model_indices = np.flatnonzero(np.isfinite(time) & (time >= reference_time))
    if not model_indices.size:
        return values
    measured_time = curve["time"].to_numpy(float)
    measured_value = curve["value"].to_numpy(float)
    measured_reference = float(
        np.interp(reference_time, measured_time, measured_value)
    )
    return values + measured_reference - values[int(model_indices[0])]


def deck_scalar(deck_text: str, name: str) -> float:
    match = re.search(rf"(?m)^\s*{re.escape(name)}\s*=\s*([0-9.eE+-]+)", deck_text)
    if not match:
        raise ValueError(f"Could not read {name} from input deck")
    return float(match.group(1))


def piston_command_mm(
    sample: str, frame: pd.DataFrame, deck: Path, time: np.ndarray
) -> np.ndarray:
    if "axial_command_m_pp" in frame.columns:
        return (
            pd.to_numeric(frame["axial_command_m_pp"], errors="coerce").to_numpy(float)
            * 1.0e3
        )

    # Older SWS3 outputs do not contain axial_command_m_pp. Reconstruct the
    # command from the exact ParsedFunction in its ranked input deck.
    text = deck.read_text(encoding="utf-8", errors="replace")
    initial = deck_scalar(text, "axial_pres_initial")
    final = deck_scalar(text, "axial_pres_final")
    command = np.where(
        time < 2.0,
        initial,
        np.where(
            time < 55.0,
            initial + (final - initial) * (time - 2.0) / 53.0,
            final,
        ),
    )
    if sample == "SWS3":
        retreat = np.clip((time - 2550.0) / 300.0, 0.0, 1.0) * 4.5e-6
        command = command + retreat
    return command * 1.0e3


def zero_at_time(time: np.ndarray, values: np.ndarray, reference_time: float = 55.0) -> np.ndarray:
    finite = np.isfinite(time) & np.isfinite(values)
    if not finite.any():
        return values
    indices = np.flatnonzero(finite & (time >= reference_time))
    index = int(indices[0]) if indices.size else int(np.flatnonzero(finite)[0])
    return values - values[index]


def sample_at_or_before(
    time: np.ndarray, values: np.ndarray, sample_times: list[float]
) -> np.ndarray:
    output = []
    for target in sample_times:
        indices = np.flatnonzero(time <= target + 1.0e-9)
        output.append(values[indices[-1]] if indices.size else np.nan)
    return np.asarray(output, dtype=float)


def set_axis_color(ax: plt.Axes, color: str, side: str, offset: int = 0) -> None:
    ax.tick_params(axis="y", colors=color, labelsize=4.8, pad=1.2, length=2.2)
    ax.yaxis.label.set_color(color)
    ax.spines[side].set_color(color)
    if offset:
        ax.spines[side].set_position(("outward", offset))
    if side == "left":
        ax.yaxis.set_label_position("left")
        ax.yaxis.tick_left()
        ax.spines["right"].set_visible(False)
    else:
        ax.yaxis.set_label_position("right")
        ax.yaxis.tick_right()
    ax.yaxis.set_major_locator(MaxNLocator(nbins=4))


def padded_limits(values: np.ndarray, fraction: float = 0.07) -> tuple[float, float]:
    finite = np.asarray(values)[np.isfinite(values)]
    if not finite.size:
        return 0.0, 1.0
    low, high = float(np.min(finite)), float(np.max(finite))
    span = high - low
    if span == 0:
        span = max(abs(high), 1.0) * 0.08
    return low - fraction * span, high + fraction * span


def add_stage_annotations(
    axes: list[plt.Axes], boundaries: tuple[float, float], end_time: float
) -> None:
    first, second = boundaries
    for ax in axes:
        ax.axvline(first, color=COLORS["stage"], linestyle="--", linewidth=0.55)
        ax.axvline(second, color=COLORS["stage"], linestyle="--", linewidth=0.55)
    top = axes[0]
    midpoints = (first / 2.0, (first + second) / 2.0, (second + end_time) / 2.0)
    alignments = ["center", "center", "center"]
    if (midpoints[2] - midpoints[1]) / end_time < 0.18:
        alignments[1:] = ["right", "left"]
    for midpoint, label, alignment in zip(
        midpoints, ("Stage 1", "Stage 2", "Stage 3"), alignments
    ):
        top.text(
            midpoint,
            1.075,
            label,
            transform=top.get_xaxis_transform(),
            ha=alignment,
            va="bottom",
            fontsize=5.4,
            fontweight="bold",
            clip_on=False,
        )


def plot_sample(
    fig: plt.Figure,
    subplotspec,
    sample: str,
    row: pd.Series,
) -> None:
    csv_path, deck = result_and_deck(row)
    frame = (
        pd.read_csv(csv_path, low_memory=False)
        .sort_values("time")
        .drop_duplicates("time", keep="last")
        .reset_index(drop=True)
    )
    time = pd.to_numeric(frame["time"], errors="coerce").to_numpy(float)
    plot_mask = np.isfinite(time) & (time >= 55.0)
    validation = load_validation_curves(sample)

    schedule_time, schedule_pressure = parse_schedule(deck)
    holds = hold_stage_times(schedule_time, schedule_pressure)
    boundaries = stage_boundaries(sample, schedule_time, schedule_pressure)
    end_time = min(float(time[np.isfinite(time)].max()), float(schedule_time[-1]))

    piston = piston_command_mm(sample, frame, deck, time)
    piston = align_absolute_reference(time, piston, validation.get("piston"))
    differential = model_series(frame, "differential")
    injection = model_series(frame, "injection")
    production = model_series(frame, "production")
    slip = zero_at_time(time, model_series(frame, "slip"))
    dilation = zero_at_time(time, model_series(frame, "dilation"))
    shear = model_series(frame, "shear")
    normal = model_series(frame, "normal")
    permeability = model_series(frame, "permeability")
    flow = model_series(frame, "flow")

    inner = subplotspec.subgridspec(3, 1, height_ratios=(1.0, 1.0, 0.78), hspace=0.24)
    top = fig.add_subplot(inner[0])
    middle = fig.add_subplot(inner[1], sharex=top)
    bottom = fig.add_subplot(inner[2], sharex=top)

    # Top: piston command + differential stress + injection/production pressure.
    top.plot(time[plot_mask], differential[plot_mask], color=COLORS["differential"], lw=0.85)
    plot_validation_curve(top, validation.get("differential"), COLORS["differential"])
    top.set_ylabel("Differential stress, MPa", fontsize=5.2)
    set_axis_color(top, COLORS["differential"], "left")
    top.set_ylim(*padded_limits(include_validation(differential[plot_mask], validation.get("differential"))))

    top_piston = top.twinx()
    top_piston.plot(time[plot_mask], piston[plot_mask], color=COLORS["piston"], lw=0.8)
    plot_validation_curve(top_piston, validation.get("piston"), COLORS["piston"])
    top_piston.set_ylabel("Piston displacement, mm", fontsize=5.2)
    set_axis_color(top_piston, COLORS["piston"], "left", 25)
    top_piston.set_ylim(*padded_limits(include_validation(piston[plot_mask], validation.get("piston"))))
    top_piston.ticklabel_format(axis="y", style="plain", useOffset=False)

    top_injection = top.twinx()
    top_injection.plot(time[plot_mask], injection[plot_mask], color=COLORS["injection"], lw=0.85)
    plot_validation_curve(top_injection, validation.get("injection"), COLORS["injection"])
    top_injection.set_ylabel("Injection pressure, MPa", fontsize=5.2)
    set_axis_color(top_injection, COLORS["injection"], "right")
    top_injection.set_ylim(*padded_limits(include_validation(injection[plot_mask], validation.get("injection"))))

    top_production = top.twinx()
    top_production.plot(time[plot_mask], production[plot_mask], color=COLORS["production"], lw=0.75)
    plot_validation_curve(top_production, validation.get("production"), COLORS["production"])
    top_production.set_ylabel("Production pressure, MPa", fontsize=5.2)
    set_axis_color(top_production, COLORS["production"], "right", 25)
    # Injection and production are pressures and share the same display range
    # in the reference figure. This also avoids scientific offset notation for
    # tiny solver noise around the nominally constant 5 MPa outlet pressure.
    top_production.set_ylim(top_injection.get_ylim())
    top_production.ticklabel_format(axis="y", style="plain", useOffset=False)

    # Middle: displacements and fracture-plane stresses.
    middle.plot(time[plot_mask], dilation[plot_mask], color=COLORS["dilation"], lw=0.85)
    plot_validation_curve(middle, validation.get("dilation"), COLORS["dilation"])
    middle.set_ylabel("Normal dilation, mm", fontsize=5.2)
    set_axis_color(middle, COLORS["dilation"], "left")
    middle.set_ylim(*padded_limits(include_validation(dilation[plot_mask], validation.get("dilation"))))

    middle_slip = middle.twinx()
    middle_slip.plot(time[plot_mask], slip[plot_mask], color=COLORS["slip"], lw=0.85)
    plot_validation_curve(middle_slip, validation.get("slip"), COLORS["slip"])
    middle_slip.set_ylabel("Shear slip, mm", fontsize=5.2)
    set_axis_color(middle_slip, COLORS["slip"], "left", 25)
    middle_slip.set_ylim(*padded_limits(include_validation(slip[plot_mask], validation.get("slip"))))

    middle_shear = middle.twinx()
    middle_shear.plot(time[plot_mask], shear[plot_mask], color=COLORS["shear"], lw=0.8)
    plot_validation_curve(middle_shear, validation.get("shear"), COLORS["shear"])
    middle_shear.set_ylabel("Shear stress, MPa", fontsize=5.2)
    set_axis_color(middle_shear, COLORS["shear"], "right")
    middle_shear.set_ylim(*padded_limits(include_validation(shear[plot_mask], validation.get("shear"))))

    middle_normal = middle.twinx()
    middle_normal.plot(time[plot_mask], normal[plot_mask], color=COLORS["normal"], lw=0.8)
    plot_validation_curve(middle_normal, validation.get("normal"), COLORS["normal"])
    middle_normal.set_ylabel("Effective normal stress, MPa", fontsize=5.2)
    set_axis_color(middle_normal, COLORS["normal"], "right", 25)
    middle_normal.set_ylim(*padded_limits(include_validation(normal[plot_mask], validation.get("normal"))))

    # Bottom: hold-stage permeability and flow, matching the paper's symbols.
    hold_array = np.asarray(holds)
    permeability_holds = sample_at_or_before(time, permeability, holds)
    flow_holds = sample_at_or_before(time, flow, holds)
    bottom.plot(
        hold_array,
        permeability_holds,
        color=COLORS["permeability"],
        lw=0.85,
    )
    plot_validation_curve(bottom, validation.get("permeability"), COLORS["permeability"])
    bottom.set_ylabel(r"Fracture permeability, m$^2$", fontsize=5.2)
    set_axis_color(bottom, COLORS["permeability"], "left")
    bottom.set_ylim(*padded_limits(include_validation(permeability_holds, validation.get("permeability")), fraction=0.12))
    formatter = ScalarFormatter(useMathText=True)
    formatter.set_powerlimits((0, 0))
    bottom.yaxis.set_major_formatter(formatter)
    bottom.yaxis.get_offset_text().set_color(COLORS["permeability"])
    bottom.yaxis.get_offset_text().set_size(4.8)

    bottom_flow = bottom.twinx()
    bottom_flow.plot(
        hold_array,
        flow_holds,
        color=COLORS["flow"],
        lw=0.85,
    )
    plot_validation_curve(bottom_flow, validation.get("flow"), COLORS["flow"])
    bottom_flow.set_ylabel("Flow rate, mL/min", fontsize=5.2)
    set_axis_color(bottom_flow, COLORS["flow"], "right")
    bottom_flow.set_ylim(*padded_limits(include_validation(flow_holds, validation.get("flow")), fraction=0.12))

    for ax in (top, middle):
        ax.tick_params(axis="x", labelbottom=False)
    bottom.set_xlabel("Time (s)", fontsize=5.4)
    bottom.tick_params(axis="x", labelsize=4.8, length=2.2)
    for ax in (top, middle, bottom):
        ax.set_xlim(0.0, end_time)
        ax.grid(False)
        ax.spines["top"].set_visible(False)

    add_stage_annotations([top, middle, bottom], boundaries, end_time)
    title = f"({PANEL_LABEL[sample]})  {DISPLAY_NAME[sample]}"
    top.set_title(title, loc="left", fontsize=6.4, fontweight="bold", pad=18)


def build_figure(
    ranking: pd.DataFrame,
    case_names: dict[str, str] | None = None,
) -> tuple[plt.Figure, dict[str, pd.Series]]:
    selected = select_best_cases(ranking, case_names)
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "axes.linewidth": 0.55,
            "xtick.major.width": 0.5,
            "ytick.major.width": 0.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )
    # AGU double-column width with a near-square aspect, matching the published
    # four-sample Figure-7 organization at final print size.
    figure = plt.figure(figsize=(7.2, 8.0))
    outer = figure.add_gridspec(2, 2, hspace=0.37, wspace=0.80)
    for sample, subplotspec in zip(SAMPLE_ORDER, outer):
        plot_sample(figure, subplotspec, sample, selected[sample])

    legend_handles = (
        Line2D([], [], color="#222222", linewidth=1.0, label="Numerical"),
        Line2D(
            [], [], color="#222222", linestyle="none", marker="o",
            markersize=3.0, markerfacecolor="white", markeredgewidth=0.6,
            label="Ye & Ghassemi (2018), digitized",
        ),
    )
    figure.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.995),
        frameon=False,
        ncol=2,
        fontsize=6.2,
        handlelength=2.2,
        columnspacing=1.8,
    )
    figure.subplots_adjust(left=0.14, right=0.86, bottom=0.055, top=0.93)
    return figure, selected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dpi", type=int, default=400)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ranking = pd.read_csv(RANKING_PATH)
    figure, selected = build_figure(ranking)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    png_path = args.output_dir / "YE2018_BEST_CASES_HYDROMECHANICAL.png"
    pdf_path = args.output_dir / "YE2018_BEST_CASES_HYDROMECHANICAL.pdf"
    figure.savefig(png_path, dpi=args.dpi, bbox_inches="tight")
    figure.savefig(pdf_path, bbox_inches="tight")
    plt.close(figure)

    print("Selected cases:")
    for sample in SAMPLE_ORDER:
        row = selected[sample]
        print(
            f"  {sample}: {row['case']} | rank {int(row['rank_within_sample'])} | "
            f"mean nRMSE {float(row['mean_nrmse_pct']):.6f}%"
        )
    print(f"PNG: {png_path}")
    print(f"PDF: {pdf_path}")


if __name__ == "__main__":
    main()
