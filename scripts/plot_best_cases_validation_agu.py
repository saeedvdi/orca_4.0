#!/usr/bin/env python3
"""AGU-style Ye & Ghassemi validation comparison for the best four cases.

The output is deliberately split into mechanical and hydraulic/dilation pages.
Every axes contains exactly two data series: digitized experimental data from
Ye & Ghassemi (2018) and the selected numerical result. No twin axes are used.
"""

from __future__ import annotations

from pathlib import Path
import string

import matplotlib

# Preserve Jupyter's inline/widget backend when imported by the notebook.
if __name__ == "__main__":
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
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
DEFAULT_CASES = {
    "SWT1": "99_01_swt1_vm50um_ppfix",
    "SWT2": "100_04_swt2_apscale0p0177_ppfix",
    "SWS3": "92_03_sw3_final_paperjrc_resc1p40",
    "SWS4": "93_07_sw4_final_theta30_jrc5_ppfix",
}

VALIDATION_FILES = {
    "SWT1": {
        "differential_stress": "SWT1_differential_stress.csv",
        "injection_pressure": "SWT1_injection_pressure_MPa.csv",
        "flow_rate": "SWt1_flow_rate.csv",
        "permeability": "SWT1_fracture_permeability_m2.csv",
        "normal_dilation": "SWT1_normal_dilation.csv",
        "effective_normal_stress": "SWT1_effective_normal_stress.csv",
        "shear_slip": "SWT1_shear_slip_mm.csv",
        "shear_stress": "SWT1_shear_stress.csv",
    },
    "SWT2": {
        "differential_stress": "SWt2_differential_stress.csv",
        "injection_pressure": "SWT2_injection_pressure_MPA.csv",
        "flow_rate": "SWt2_flow_rate_ml:min.csv",
        "permeability": "SWt2_fracture_peremabiltiy_m2.csv",
        "normal_dilation": "SWT2_normal_dilation_mm.csv",
        "effective_normal_stress": "SWT2_effective_normal_stress_MPa.csv",
        "shear_slip": "SWt2_shear_dilation_mm.csv",
        "shear_stress": "SWT2_shear_stress_MPa.csv",
    },
    "SWS3": {
        "differential_stress": "differnetial_stress_vs_time_sw3.csv",
        "injection_pressure": "Injection_pressure_vs_time_SW3.csv",
        "flow_rate": "flow_Rate_mlmin_vs_time_sw3.csv",
        "permeability": "permeability_m2_vs_time_sw3_corrected.table2",
        "normal_dilation": "normal_dilation_mm_vs_time_sw3.csv",
        "effective_normal_stress": "effective_normal_stress_mpa_Vs_time_SW3.csv",
        "shear_slip": "shear_slip_mm_vs_time_sw3.csv",
        "shear_stress": "shear_stress_MPa_vs_time_sw3.csv",
    },
    "SWS4": {
        "differential_stress": "Ye2018_SW4_Differential_Stress_Vs_time.csv",
        "injection_pressure": "Ye2018_SW4_Injection_pressure_Vs_time.csv",
        "flow_rate": "Ye2018_SW4_flow_rate_Vs_time.csv",
        "permeability": "Ye2018_SW4_frac_perm_Vs_time.csv",
        "normal_dilation": "Ye2018_SW4_normal_dilation_Vs_time.csv",
        "effective_normal_stress": "Ye2018_SW4_normal_stress_Vs_time.csv",
        "shear_slip": "Ye2018_SW4_shear_slip_Vs_time.csv",
        "shear_stress": "Ye2018_SW4_shear_stress_Vs_time.csv",
    },
}

MODEL_COLUMNS = {
    "differential_stress": (
        ("differential_stress_reaction_mpa_pp", 1.0),
        ("differential_stress_skeleton_bulk_pp", 1.0),
        ("differential_stress_mpa_pp", 1.0),
    ),
    "injection_pressure": (("injection_pressure_pp", 1.0e-6),),
    "flow_rate": (("flow_rate_validation_ml_min_pp", 1.0),),
    "permeability": (("fracture_permeability_pp", 1.0e13),),
    "normal_dilation": (
        ("czm_normal_dilation_paper_mm_pp", 1.0),
        ("frac_normal_dilation_paper_mm", 1.0),
    ),
    "effective_normal_stress": (
        ("effective_normal_paper_frame_mpa_pp", 1.0),
        ("effective_normal_compression_mpa_pp", 1.0),
        ("bb_effective_normal_stress_pp", 1.0e-6),
    ),
    "shear_slip": (
        ("czm_shear_slip_mm_pp", 1.0),
        ("reported_czm_shear_slip_mm_pp", 1.0),
    ),
    "shear_stress": (
        ("shear_stress_paper_frame_mpa_pp", 1.0),
        ("shear_traction_magnitude_pa", 1.0e-6),
    ),
}

VALIDATION_SCALE = {
    "differential_stress": 1.0,
    "injection_pressure": 1.0,
    "flow_rate": 1.0,
    "permeability": 1.0e13,
    "normal_dilation": 1.0,
    "effective_normal_stress": 1.0,
    "shear_slip": 1.0,
    "shear_stress": 1.0,
}

MECHANICAL_SPECS = (
    ("differential_stress", "Differential stress\n(MPa)"),
    ("effective_normal_stress", "Effective normal stress\n(MPa)"),
    ("shear_stress", "Shear stress\n(MPa)"),
    ("shear_slip", "Shear slip\n(mm)"),
)
HYDRAULIC_SPECS = (
    ("injection_pressure", "Injection pressure\n(MPa)"),
    ("normal_dilation", "Normal dilation\n(mm)"),
    ("permeability", "Permeability\n($10^{-13}$ m$^2$)"),
    ("flow_rate", "Flow rate\n(mL min$^{-1}$)"),
)

NUMERICAL_COLOR = "#0072B2"  # Okabe-Ito blue; accessible on white.
EXPERIMENT_COLOR = "#202020"


def resolve_cases(
    case_names: dict[str, str] | None = None,
) -> tuple[pd.DataFrame, dict[str, pd.Series]]:
    """Resolve manually named cases against the ranking and verify their files."""
    names = DEFAULT_CASES if case_names is None else case_names
    missing_samples = set(SAMPLE_ORDER).difference(names)
    if missing_samples:
        raise KeyError(f"Missing selected case name(s): {sorted(missing_samples)}")

    ranking = pd.read_csv(RANKING_PATH)
    selected: dict[str, pd.Series] = {}
    rows = []
    for sample in SAMPLE_ORDER:
        matches = ranking.loc[
            ranking["sample"].eq(sample) & ranking["case"].eq(names[sample])
        ]
        if len(matches) != 1:
            raise ValueError(
                f"{sample}: expected one ranking row for {names[sample]!r}; "
                f"found {len(matches)}"
            )
        row = matches.iloc[0]
        result_path = PROJECT_ROOT / str(row["source_csv"])
        if not result_path.is_file():
            raise FileNotFoundError(result_path)
        selected[sample] = row
        rows.append(
            {
                "sample": sample,
                "case": row["case"],
                "rank": int(row["rank_within_sample"]),
                "mean_nRMSE_pct": float(row["mean_nrmse_pct"]),
                "selection_status": row["selection_status"],
            }
        )
    return pd.DataFrame(rows), selected


def validation_directory(sample: str) -> Path:
    return PROJECT_ROOT / "Examples" / "YeGhasemmi2018" / sample / sample


def load_validation(sample: str) -> dict[str, pd.DataFrame]:
    directory = validation_directory(sample)
    curves: dict[str, pd.DataFrame] = {}
    for key, filename in VALIDATION_FILES[sample].items():
        path = directory / filename
        if not path.is_file():
            raise FileNotFoundError(path)
        frame = pd.read_csv(path, header=None, names=("time", "value"))
        frame["time"] = pd.to_numeric(frame["time"], errors="coerce")
        frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
        frame = (
            frame.dropna()
            .sort_values("time")
            .drop_duplicates("time", keep="last")
            .reset_index(drop=True)
        )
        frame["value"] *= VALIDATION_SCALE[key]
        curves[key] = frame
    return curves


def load_numerical(row: pd.Series) -> pd.DataFrame:
    path = PROJECT_ROOT / str(row["source_csv"])
    frame = pd.read_csv(path, low_memory=False)
    frame["time"] = pd.to_numeric(frame["time"], errors="coerce")
    return (
        frame.dropna(subset=["time"])
        .sort_values("time")
        .drop_duplicates("time", keep="last")
        .reset_index(drop=True)
    )


def numerical_series(frame: pd.DataFrame, key: str) -> np.ndarray:
    for column, scale in MODEL_COLUMNS[key]:
        if column in frame.columns:
            return pd.to_numeric(frame[column], errors="coerce").to_numpy(float) * scale
    attempted = ", ".join(column for column, _ in MODEL_COLUMNS[key])
    raise KeyError(f"No numerical channel for {key}; tried {attempted}")


def padded_limits(*arrays: np.ndarray, fraction: float = 0.06) -> tuple[float, float]:
    finite = []
    for array in arrays:
        values = np.asarray(array, dtype=float)
        finite.extend(values[np.isfinite(values)].tolist())
    if not finite:
        return 0.0, 1.0
    low, high = min(finite), max(finite)
    span = high - low
    if span <= 0.0:
        span = max(abs(high), 1.0) * 0.1
    return low - fraction * span, high + fraction * span


def apply_agu_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.size": 7.0,
            "axes.titlesize": 7.4,
            "axes.labelsize": 7.0,
            "xtick.labelsize": 6.2,
            "ytick.labelsize": 6.2,
            "axes.linewidth": 0.65,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )


def plot_comparison_page(
    specs: tuple[tuple[str, str], ...],
    selected: dict[str, pd.Series],
) -> plt.Figure:
    apply_agu_style()
    figure, axes = plt.subplots(
        len(SAMPLE_ORDER),
        len(specs),
        figsize=(7.2, 8.55),
        sharex="row",
        squeeze=False,
    )
    letters = iter(string.ascii_lowercase)

    for row_index, sample in enumerate(SAMPLE_ORDER):
        validation = load_validation(sample)
        model = load_numerical(selected[sample])
        model_time = model["time"].to_numpy(float)
        model_mask = np.isfinite(model_time) & (model_time >= 55.0)
        validation_end = max(float(frame["time"].max()) for frame in validation.values())
        model_end = float(model_time[model_mask].max())
        end_time = min(validation_end, model_end)

        for column_index, (key, title) in enumerate(specs):
            ax = axes[row_index, column_index]
            measured = validation[key]
            measured_time = measured["time"].to_numpy(float)
            measured_value = measured["value"].to_numpy(float)
            model_value = numerical_series(model, key)

            # The full digitized history is retained as a thin line. Open markers
            # are thinned only for readability; the underlying values are not.
            markevery = max(1, len(measured) // 30)
            ax.plot(
                measured_time,
                measured_value,
                color=EXPERIMENT_COLOR,
                linewidth=0.65,
                marker="o",
                markersize=2.25,
                markerfacecolor="white",
                markeredgecolor=EXPERIMENT_COLOR,
                markeredgewidth=0.55,
                markevery=markevery,
                zorder=3,
            )
            ax.plot(
                model_time[model_mask],
                model_value[model_mask],
                color=NUMERICAL_COLOR,
                linewidth=1.1,
                zorder=2,
            )

            visible_validation = measured_value[
                np.isfinite(measured_time) & (measured_time <= end_time)
            ]
            visible_model = model_value[model_mask & (model_time <= end_time)]
            ax.set_ylim(*padded_limits(visible_validation, visible_model))
            ax.set_xlim(0.0, end_time)
            ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
            ax.xaxis.set_major_locator(MaxNLocator(nbins=4))
            ax.tick_params(direction="out", length=2.6, width=0.6, pad=1.5)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.grid(axis="y", color="#D9D9D9", linewidth=0.35, alpha=0.65)
            ax.text(
                0.025,
                0.955,
                f"({next(letters)})",
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=6.7,
                fontweight="bold",
                bbox={
                    "facecolor": "white",
                    "edgecolor": "none",
                    "alpha": 0.82,
                    "pad": 0.45,
                },
                zorder=8,
            )
            if row_index == 0:
                ax.set_title(title, pad=5.5, fontweight="bold")
            if row_index == len(SAMPLE_ORDER) - 1:
                ax.set_xlabel("Time (s)")
            else:
                ax.tick_params(axis="x", labelbottom=False)

    legend_handles = (
        Line2D(
            [], [], color=EXPERIMENT_COLOR, linewidth=0.65, marker="o",
            markersize=3.0, markerfacecolor="white", markeredgewidth=0.6,
            label="Ye & Ghassemi (2018), digitized experiment",
        ),
        Line2D(
            [], [], color=NUMERICAL_COLOR, linewidth=1.25,
            label="Best-ranked numerical case",
        ),
    )
    figure.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.54, 0.987),
        frameon=False,
        ncol=2,
        handlelength=2.2,
        columnspacing=1.8,
        fontsize=7.1,
    )
    figure.subplots_adjust(
        left=0.105,
        right=0.992,
        bottom=0.065,
        top=0.905,
        wspace=0.34,
        hspace=0.29,
    )
    # Figure-coordinate row labels remain stable under tight PDF bounding boxes.
    for row_index, sample in enumerate(SAMPLE_ORDER):
        position = axes[row_index, 0].get_position()
        rank = int(selected[sample]["rank_within_sample"])
        figure.text(
            0.019,
            0.5 * (position.y0 + position.y1),
            f"{DISPLAY_NAME[sample]}\nrank {rank}",
            rotation=90,
            ha="center",
            va="center",
            fontsize=7.2,
            fontweight="bold",
        )
    return figure


def build_figures(
    case_names: dict[str, str] | None = None,
) -> tuple[dict[str, plt.Figure], pd.DataFrame]:
    selection_table, selected = resolve_cases(case_names)
    figures = {
        "mechanical": plot_comparison_page(MECHANICAL_SPECS, selected),
        "hydraulic": plot_comparison_page(HYDRAULIC_SPECS, selected),
    }
    return figures, selection_table


def save_figures(
    figures: dict[str, plt.Figure],
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    dpi: int = 400,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "mechanical_pdf": output_dir / "YE2018_BEST_CASES_VALIDATION_MECHANICAL_AGU.pdf",
        "hydraulic_pdf": output_dir / "YE2018_BEST_CASES_VALIDATION_HYDRAULIC_AGU.pdf",
        "combined_pdf": output_dir / "YE2018_BEST_CASES_VALIDATION_AGU.pdf",
        "mechanical_png": output_dir / "YE2018_BEST_CASES_VALIDATION_MECHANICAL_AGU.png",
        "hydraulic_png": output_dir / "YE2018_BEST_CASES_VALIDATION_HYDRAULIC_AGU.png",
    }
    figures["mechanical"].savefig(paths["mechanical_pdf"], bbox_inches="tight")
    figures["hydraulic"].savefig(paths["hydraulic_pdf"], bbox_inches="tight")
    figures["mechanical"].savefig(paths["mechanical_png"], dpi=dpi, bbox_inches="tight")
    figures["hydraulic"].savefig(paths["hydraulic_png"], dpi=dpi, bbox_inches="tight")
    with PdfPages(paths["combined_pdf"]) as pdf:
        pdf.savefig(figures["mechanical"], bbox_inches="tight")
        pdf.savefig(figures["hydraulic"], bbox_inches="tight")
    return paths


def main() -> None:
    figures, selection_table = build_figures()
    paths = save_figures(figures)
    print(selection_table.to_string(index=False))
    for name, path in paths.items():
        print(f"{name}: {path}")
    for figure in figures.values():
        plt.close(figure)


if __name__ == "__main__":
    main()
