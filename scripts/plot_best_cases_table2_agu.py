#!/usr/bin/env python3
"""Plot the best cases against Ye & Ghassemi (2018) Table 2.

Numerical values are solid colored curves through the eleven sampled hold
stages. Published Table 2 values are same-colored open points only.
"""

from __future__ import annotations

from pathlib import Path
import string
import sys

import matplotlib

if __name__ == "__main__":
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import plot_best_cases_figure7 as best  # noqa: E402
import table2_gate as gate  # noqa: E402


PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "doc" / "independent_analysis" / "figures"

DEFAULT_CASES = {
    "SWT1": "99_01_swt1_vm50um_ppfix",
    "SWT2": "100_04_swt2_apscale0p0177_ppfix",
    "SWS3": "92_03_sw3_final_paperjrc_resc1p40",
    "SWS4": "93_07_sw4_final_theta30_jrc5_ppfix",
}

# key, model column, paper column, title, color
MECHANICAL_SPECS = (
    ("Pi", "Pi_model_MPa", "Pi_target_MPa", "Injection pressure\n(MPa)", "#0057E7"),
    (
        "sigma_n_MPa",
        "sigma_n_MPa_model",
        "sigma_n_MPa_paper",
        "Effective normal stress\n(MPa)",
        "#202020",
    ),
    ("tau_MPa", "tau_MPa_model", "tau_MPa_paper", "Shear stress\n(MPa)", "#D5AE00"),
    ("ds_mm", "ds_mm_model", "ds_mm_paper", "Shear slip\n(mm)", "#E600A9"),
)
HYDRAULIC_SPECS = (
    ("dn_mm", "dn_mm_model", "dn_mm_paper", "Normal dilation\n(mm)", "#8B55E8"),
    ("Q_ml_min", "Q_ml_min_model", "Q_ml_min_paper", "Flow rate\n(mL min$^{-1}$)", "#123C91"),
    ("ah_um", "ah_um_model", "ah_um_paper", "Hydraulic aperture\n($\\mu$m)", "#009E9A"),
    (
        "k_1e12_m2",
        "k_1e12_m2_model",
        "k_1e12_m2_paper",
        "Permeability\n($10^{-12}$ m$^2$)",
        "#008F28",
    ),
)


def resolve_cases(
    case_names: dict[str, str] | None = None,
) -> tuple[pd.DataFrame, dict[str, pd.Series]]:
    ranking = pd.read_csv(best.RANKING_PATH)
    selected = best.select_best_cases(ranking, case_names or DEFAULT_CASES)
    selection_table = pd.DataFrame(
        [
            {
                "sample": sample,
                "case": selected[sample]["case"],
                "rank": int(selected[sample]["rank_within_sample"]),
                "mean_nRMSE_pct": float(selected[sample]["mean_nrmse_pct"]),
                "selection_status": selected[sample]["selection_status"],
            }
            for sample in best.SAMPLE_ORDER
        ]
    )
    return selection_table, selected


def score_selected_cases(
    selected: dict[str, pd.Series],
) -> dict[str, dict]:
    scored: dict[str, dict] = {}
    for sample in best.SAMPLE_ORDER:
        csv_path, _deck = best.result_and_deck(selected[sample])
        scored[sample] = gate.score_run(
            csv_path=csv_path,
            sample=sample,
            tag="hpc",
            tol_mpa=0.35,
            datum="stage1",
            preload_time=55.0,
        )
        if scored[sample]["reached"] != 11:
            raise ValueError(
                f"{sample}: selected case reached "
                f"{scored[sample]['reached']}/11 Table 2 stages"
            )
    return scored


def padded_limits(*arrays: np.ndarray, fraction: float = 0.08) -> tuple[float, float]:
    values = np.concatenate([np.asarray(array, dtype=float) for array in arrays])
    values = values[np.isfinite(values)]
    if not values.size:
        return 0.0, 1.0
    low, high = float(values.min()), float(values.max())
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
            "axes.titlesize": 7.3,
            "axes.labelsize": 6.8,
            "xtick.labelsize": 6.1,
            "ytick.labelsize": 6.1,
            "axes.linewidth": 0.65,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": "white",
        }
    )


def plot_page(
    specs: tuple[tuple[str, str, str, str, str], ...],
    scored: dict[str, dict],
) -> plt.Figure:
    apply_agu_style()
    figure, axes = plt.subplots(
        len(best.SAMPLE_ORDER),
        len(specs),
        figsize=(7.2, 8.3),
        sharex=True,
        squeeze=False,
    )
    letters = iter(string.ascii_lowercase)

    for row_index, sample in enumerate(best.SAMPLE_ORDER):
        table = scored[sample]["table"]
        pressure = table["Pi_target_MPa"].to_numpy(float)
        for column_index, (_key, model_column, paper_column, title, color) in enumerate(specs):
            ax = axes[row_index, column_index]
            model = pd.to_numeric(table[model_column], errors="coerce").to_numpy(float)
            paper = pd.to_numeric(table[paper_column], errors="coerce").to_numpy(float)

            ax.plot(pressure, model, color=color, linewidth=1.2, zorder=2)
            ax.plot(
                pressure,
                paper,
                linestyle="none",
                marker="o",
                markersize=3.25,
                markerfacecolor="white",
                markeredgecolor=color,
                markeredgewidth=0.8,
                zorder=4,
            )
            ax.set_xlim(7.0, 29.0)
            ax.set_xticks((8, 12, 16, 20, 24, 28))
            ax.set_ylim(*padded_limits(model, paper))
            ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
            ax.tick_params(direction="out", length=2.5, width=0.6, pad=1.4)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.grid(axis="y", color="#D9D9D9", linewidth=0.35, alpha=0.65)
            ax.text(
                0.025,
                0.95,
                f"({next(letters)})",
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=6.6,
                fontweight="bold",
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 0.4},
                zorder=8,
            )
            if row_index == 0:
                ax.set_title(title, pad=5.0, fontweight="bold")
            if row_index == len(best.SAMPLE_ORDER) - 1:
                ax.set_xlabel("Table 2 injection pressure (MPa)")
            else:
                ax.tick_params(axis="x", labelbottom=False)

    figure.subplots_adjust(
        left=0.10,
        right=0.992,
        bottom=0.07,
        top=0.90,
        wspace=0.34,
        hspace=0.30,
    )
    for row_index, sample in enumerate(best.SAMPLE_ORDER):
        position = axes[row_index, 0].get_position()
        figure.text(
            0.018,
            0.5 * (position.y0 + position.y1),
            best.DISPLAY_NAME[sample],
            rotation=90,
            ha="center",
            va="center",
            fontsize=7.3,
            fontweight="bold",
        )

    figure.legend(
        handles=(
            Line2D([], [], color="#222222", linewidth=1.2, label="Numerical hold-stage state"),
            Line2D(
                [], [], color="#222222", linestyle="none", marker="o",
                markersize=3.4, markerfacecolor="white", markeredgewidth=0.8,
                label="Ye & Ghassemi (2018), Table 2",
            ),
        ),
        loc="upper center",
        bbox_to_anchor=(0.53, 0.985),
        frameon=False,
        ncol=2,
        fontsize=7.0,
        handlelength=2.2,
        columnspacing=1.8,
    )
    return figure


def comparison_frame(scored: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for sample in best.SAMPLE_ORDER:
        table = scored[sample]["table"]
        for _, stage in table.iterrows():
            for key in gate.SCORED + gate.INFORMATIONAL:
                rows.append(
                    {
                        "sample": sample,
                        "stage": int(stage["stage"]),
                        "segment": stage["segment"],
                        "injection_pressure_MPa": stage["Pi_target_MPa"],
                        "quantity": key,
                        "numerical": stage[f"{key}_model"],
                        "table2": stage[f"{key}_paper"],
                        "numerical_minus_table2": stage[f"{key}_err"],
                    }
                )
    return pd.DataFrame(rows)


def build_figures(
    case_names: dict[str, str] | None = None,
) -> tuple[dict[str, plt.Figure], pd.DataFrame, pd.DataFrame]:
    selection_table, selected = resolve_cases(case_names)
    scored = score_selected_cases(selected)
    figures = {
        "mechanical": plot_page(MECHANICAL_SPECS, scored),
        "hydraulic": plot_page(HYDRAULIC_SPECS, scored),
    }
    return figures, selection_table, comparison_frame(scored)


def save_outputs(
    figures: dict[str, plt.Figure],
    comparison: pd.DataFrame,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    dpi: int = 400,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "combined_pdf": output_dir / "YE2018_BEST_CASES_TABLE2_AGU.pdf",
        "mechanical_pdf": output_dir / "YE2018_BEST_CASES_TABLE2_MECHANICAL_AGU.pdf",
        "hydraulic_pdf": output_dir / "YE2018_BEST_CASES_TABLE2_HYDRAULIC_AGU.pdf",
        "mechanical_png": output_dir / "YE2018_BEST_CASES_TABLE2_MECHANICAL_AGU.png",
        "hydraulic_png": output_dir / "YE2018_BEST_CASES_TABLE2_HYDRAULIC_AGU.png",
        "comparison_csv": output_dir / "YE2018_BEST_CASES_TABLE2_COMPARISON.csv",
    }
    figures["mechanical"].savefig(paths["mechanical_pdf"], bbox_inches="tight")
    figures["hydraulic"].savefig(paths["hydraulic_pdf"], bbox_inches="tight")
    figures["mechanical"].savefig(paths["mechanical_png"], dpi=dpi, bbox_inches="tight")
    figures["hydraulic"].savefig(paths["hydraulic_png"], dpi=dpi, bbox_inches="tight")
    with PdfPages(paths["combined_pdf"]) as pdf:
        pdf.savefig(figures["mechanical"], bbox_inches="tight")
        pdf.savefig(figures["hydraulic"], bbox_inches="tight")
    comparison.to_csv(paths["comparison_csv"], index=False)
    return paths


def main() -> None:
    figures, selection_table, comparison = build_figures()
    paths = save_outputs(figures, comparison)
    print(selection_table.to_string(index=False))
    for name, path in paths.items():
        print(f"{name}: {path}")
    for figure in figures.values():
        plt.close(figure)


if __name__ == "__main__":
    main()
