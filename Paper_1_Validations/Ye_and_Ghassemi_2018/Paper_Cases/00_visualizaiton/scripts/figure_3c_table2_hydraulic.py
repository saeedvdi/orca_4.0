"""Standalone exporter generated from AGU_manuscript_figure_exports.ipynb.

Run this file directly.  It contains its own path discovery, case selection,
data loading, scoring, styling, plotting, validation, and PDF export logic.
"""

from pathlib import Path
import importlib.util
import os
import shutil
import subprocess
import sys


def _ensure_scientific_python() -> None:
    """Re-launch with a Python that provides the required plotting packages."""
    required = ("matplotlib", "numpy", "pandas")
    if all(importlib.util.find_spec(package) is not None for package in required):
        return

    candidates = (
        os.environ.get("ORCA_PYTHON"),
        shutil.which("python"),
        str(Path.home() / "miniforge" / "bin" / "python"),
        str(Path.home() / "miniconda3" / "bin" / "python"),
    )
    current = Path(sys.executable).resolve()
    checked: set[Path] = set()
    for raw_candidate in candidates:
        if not raw_candidate:
            continue
        candidate = Path(raw_candidate).expanduser()
        if not candidate.is_file():
            continue
        candidate = candidate.resolve()
        if candidate == current or candidate in checked:
            continue
        checked.add(candidate)
        probe = subprocess.run(
            [
                str(candidate),
                "-c",
                "import matplotlib, numpy, pandas",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if probe.returncode == 0:
            os.execv(
                str(candidate),
                [str(candidate), str(Path(__file__).resolve()), *sys.argv[1:]],
            )

    missing = [
        package
        for package in required
        if importlib.util.find_spec(package) is None
    ]
    raise ModuleNotFoundError(
        "Missing required packages: "
        + ", ".join(missing)
        + ". Set ORCA_PYTHON to a Python executable containing them."
    )


_ensure_scientific_python()

import matplotlib.pyplot as plt
import pandas as pd

def find_project_root(start=Path.cwd().resolve()):
    for candidate in (start, *start.parents):
        if ((candidate / 'scripts' / 'table2_gate.py').is_file()
                and (candidate / 'Examples' / 'YeGhasemmi2018').is_dir()):
            return candidate
    fallback = Path('/media/geomechanics/Data4TB/projects/orca_4.0')
    if (fallback / 'scripts' / 'table2_gate.py').is_file():
        return fallback
    raise FileNotFoundError('Could not locate the ORCA project root')

PROJECT_ROOT = find_project_root()

# Export beside this standalone script, independent of the current directory.
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DEPENDENCY_DIR = PROJECT_ROOT / 'scripts'
if str(DEPENDENCY_DIR) not in sys.path:
    sys.path.insert(0, str(DEPENDENCY_DIR))
import table2_gate as gate

from types import SimpleNamespace
# The plotting backend is intentionally kept in this notebook.
import string
from cycler import cycler
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import LogLocator, MaxNLocator
from matplotlib.text import Text
import numpy as np
RANKING_PATH = (
    PROJECT_ROOT
    / "Examples"
    / "YeGhasemmi2018"
    / "Docs"
    / "Memory"
    / "TABLE2_ERROR_ACCURACY_RANKING.csv"
)

SAMPLE_ORDER = ("SWT1", "SWT2", "SWS3", "SWS4")
DISPLAY_NAME = {
    "SWT1": "SW-T1",
    "SWT2": "SW-T2",
    "SWS3": "SW-S3",
    "SWS4": "SW-S4",
}

# Authoritative final selections after the 2026-08-27 equal-budget MC sweep.
FINAL_BB_CASES = {
    "SWT1": "107_01_swt1_coh27p2_apscale0p01512_ppfix",
    "SWT2": "100_04_swt2_apscale0p0177_ppfix",
    "SWS3": "100_06_sw3_resc1p30_unld0p00_ppfix",
    "SWS4": "93_07_sw4_final_theta30_jrc5_ppfix",
}

FINAL_MC_CASES = {
    "SWT1": "SWT1_OrcaMohrCoulombContactTraction_pb04",
    "SWT2": "SWT2_OrcaMohrCoulombContactTraction_pb04",
    "SWS3": "SWS3_OrcaMohrCoulombContactTraction_pb06",
    "SWS4": "SWS4_OrcaMohrCoulombContactTraction_center",
}

FINAL_MC_RESULT_PATHS = {
    sample: (
        PROJECT_ROOT / "Examples" / "YeGhasemmi2018" / sample
        / "results_csv_mc_sweep_hpc" / f"{case}.csv"
    )
    for sample, case in FINAL_MC_CASES.items()
}

MESH_CASES = {
    "SWT1": (
        "93_01_swt1_final_c26p9_resc9p19_ppfix",
        "93_02_swt1_final_c26p9_resc9p19_ppfix_mesh3",
    ),
    "SWT2": (
        "93_03_swt2_final_theta30_resc9p71_ppfix",
        "93_04_swt2_final_theta30_resc9p71_ppfix_mesh3",
    ),
    "SWS3": (
        "93_05_sw3_final_resc1p40_ppfix",
        "93_06_sw3_final_resc1p40_ppfix_mesh3",
    ),
    "SWS4": (
        "93_07_sw4_final_theta30_jrc5_ppfix",
        "93_08_sw4_final_theta30_jrc5_ppfix_mesh3",
    ),
}

# parent BBFast, exponent-1 BBFast control, matched 102-series MC transfer
WEAKENING_CASES = {
    "SWT1": (
        "100_01_swt1_vm55um_ppfix",
        "103_01_swt1_weakexp1p0_ppfix",
        "102_01_swt1_mc_vm55um_ppfix",
    ),
    "SWT2": (
        "100_04_swt2_apscale0p0177_ppfix",
        "103_02_swt2_weakexp1p0_ppfix",
        "102_02_swt2_mc_apscale0p0177_ppfix",
    ),
    "SWS3": (
        "100_06_sw3_resc1p30_unld0p00_ppfix",
        "103_03_sw3_weakexp1p0_ppfix",
        "102_03_sw3_mc_resc1p30_ppfix",
    ),
}

FIGURE_FILENAMES = {
    "mesh_sensitivity": "Figure_Mesh_Sensitivity.pdf",
    "validation_histories": "Figure_Validation_Histories.pdf",
    "table2_mechanical": "Figure_Table2_Mechanical_All_Specimens.pdf",
    "table2_hydraulic": "Figure_Table2_Hydraulic_All_Specimens.pdf",
    "hydraulic_response": "Figure_Hydraulic_Response.pdf",
    "bb_mc_comparison": "Figure_BBFast_vs_MC.pdf",
    "weakening_control": "Figure_Weakening_Controls.pdf",
}

PRESSURES = np.asarray(gate.PI_TARGETS, dtype=float)
STAGES = np.arange(1, len(PRESSURES) + 1)

BLACK = "#202020"
GRAY = "#767676"
BLUE = "#0072B2"
ORANGE = "#D55E00"
GREEN = "#009E73"
PURPLE = "#8B55E8"
YELLOW = "#F0E442"

# ---------------------------------------------------------------------------
# Reproducible figure-production controls.  Keep these in one place so the
# notebook previews and the exported manuscript PDFs cannot silently diverge.
# ---------------------------------------------------------------------------
TIMES_FONT_CANDIDATES = (
    "Times New Roman",  # Windows/macOS when installed
    "Times",
    "Nimbus Roman",     # Times-compatible font available on this Linux host
    "TeX Gyre Termes",
    "DejaVu Serif",     # portable last resort
)


def _first_available_font(candidates: tuple[str, ...]) -> str:
    for name in candidates:
        try:
            font_manager.findfont(name, fallback_to_default=False)
        except (ValueError, RuntimeError):
            continue
        return name
    raise RuntimeError("No Times-compatible serif font is installed")


AGU_FONT_NAME = _first_available_font(TIMES_FONT_CANDIDATES)
AGU_FIGURE_DPI = 600
AGU_SAVE_DPI = 600
AGU_TEXT_SIZES_PT = {
    "base": 7.0,
    "title": 7.4,
    "axis_label": 6.9,
    "tick": 6.0,
    "legend": 6.5,
}
AGU_MAX_TEXT_SIZE_PT = 8.5
AGU_COLOR_CYCLE = (BLUE, ORANGE, GREEN, PURPLE, BLACK, GRAY)
FIGURE_SIZES_IN = {
    "mesh_sensitivity": (3.45, 2.75),
    "validation_histories": (7.2, 7.75),
    "table2_mechanical": (7.2, 6.8),
    "table2_hydraulic": (7.2, 5.3),
    "hydraulic_response": (7.2, 7.5),
    "bb_mc_comparison": (7.2, 8.45),
    "weakening_control": (7.2, 2.8),
}


def apply_agu_style() -> None:
    """Apply the single controlled style used by every AGU manuscript figure."""
    plt.rcParams.update(
        {
            "font.family": AGU_FONT_NAME,
            "font.size": AGU_TEXT_SIZES_PT["base"],
            "axes.titlesize": AGU_TEXT_SIZES_PT["title"],
            "axes.labelsize": AGU_TEXT_SIZES_PT["axis_label"],
            "xtick.labelsize": AGU_TEXT_SIZES_PT["tick"],
            "ytick.labelsize": AGU_TEXT_SIZES_PT["tick"],
            "legend.fontsize": AGU_TEXT_SIZES_PT["legend"],
            "mathtext.fontset": "stix",
            "figure.dpi": AGU_FIGURE_DPI,
            "savefig.dpi": AGU_SAVE_DPI,
            "axes.prop_cycle": cycler(color=AGU_COLOR_CYCLE),
            "axes.linewidth": 0.65,
            "lines.linewidth": 1.15,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )


def validate_agu_style() -> dict[str, object]:
    """Check the global figure controls before any manuscript figure is saved."""
    checks = {
        "font": plt.rcParams["font.family"] == [AGU_FONT_NAME],
        "math_font": plt.rcParams["mathtext.fontset"] == "stix",
        "figure_dpi": int(round(float(plt.rcParams["figure.dpi"]))) == AGU_FIGURE_DPI,
        "save_dpi": int(round(float(plt.rcParams["savefig.dpi"]))) == AGU_SAVE_DPI,
        "color_cycle": tuple(plt.rcParams["axes.prop_cycle"].by_key()["color"]) == AGU_COLOR_CYCLE,
        "legend_size": float(plt.rcParams["legend.fontsize"]) == AGU_TEXT_SIZES_PT["legend"],
        "pdf_true_type": plt.rcParams["pdf.fonttype"] == 42,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError(f"AGU figure style check failed: {', '.join(failed)}")
    return checks


def validate_figure(figure_key: str, figure: plt.Figure) -> dict[str, object]:
    """Validate one figure's size, DPI, text sizes, and legends before export."""
    validate_agu_style()
    if figure_key not in FIGURE_SIZES_IN:
        raise KeyError(f"Unknown AGU figure key: {figure_key}")
    expected = np.asarray(FIGURE_SIZES_IN[figure_key], dtype=float)
    actual = np.asarray(figure.get_size_inches(), dtype=float)
    if not np.allclose(actual, expected, rtol=0.0, atol=1e-6):
        raise AssertionError(
            f"{figure_key}: expected {tuple(expected)} inches, got {tuple(actual)}"
        )
    if int(round(float(figure.dpi))) != AGU_FIGURE_DPI:
        raise AssertionError(f"{figure_key}: expected figure DPI {AGU_FIGURE_DPI}, got {figure.dpi}")

    texts = figure.findobj(Text)
    oversized = [text.get_text() for text in texts if text.get_fontsize() > AGU_MAX_TEXT_SIZE_PT]
    if oversized:
        raise AssertionError(
            f"{figure_key}: text exceeds {AGU_MAX_TEXT_SIZE_PT} pt: {oversized[:3]}"
        )
    legends = list(figure.legends)
    legends.extend(legend for ax in figure.axes
                   if (legend := ax.get_legend()) is not None)
    legend_texts = [text for legend in legends for text in legend.get_texts()]
    oversized_legends = [text.get_text() for text in legend_texts
                         if text.get_fontsize() > AGU_TEXT_SIZES_PT["legend"] + 1e-9]
    if oversized_legends:
        raise AssertionError(
            f"{figure_key}: legend text exceeds {AGU_TEXT_SIZES_PT['legend']} pt: "
            f"{oversized_legends[:3]}"
        )
    return {
        "figure_key": figure_key,
        "width_in": float(actual[0]),
        "height_in": float(actual[1]),
        "figure_dpi": int(round(float(figure.dpi))),
        "save_dpi": AGU_SAVE_DPI,
        "font": AGU_FONT_NAME,
        "text_max_pt": max((text.get_fontsize() for text in texts), default=0.0),
        "legend_count": len(legends),
    }


def _ranking() -> pd.DataFrame:
    if not RANKING_PATH.is_file():
        raise FileNotFoundError(RANKING_PATH)
    return pd.read_csv(RANKING_PATH)


def result_path(sample: str, row: pd.Series) -> Path:
    """Resolve a ranked result after campaign folders have been reorganized."""
    recorded = PROJECT_ROOT / str(row["source_csv"])
    if recorded.is_file():
        return recorded
    sample_root = PROJECT_ROOT / "Examples" / "YeGhasemmi2018" / sample
    candidates = [
        path
        for path in sample_root.rglob(recorded.name)
        if "partial_every_step" not in path.parts
    ]
    if not candidates:
        raise FileNotFoundError(recorded)
    # SWT1 currently contains equivalent Sweeps/sweeeep archival copies.  Use
    # the canonical capitalized directory deterministically when both exist.
    candidates.sort(
        key=lambda path: (
            0 if "Sweeps" in path.parts else 1,
            len(path.parts),
            str(path),
        )
    )
    return candidates[0]


def resolve_case(
    sample: str,
    case: str,
    ranking: pd.DataFrame | None = None,
    verify_result: bool = True,
) -> pd.Series:
    """Resolve one named case and verify that its result CSV exists."""
    ranking = _ranking() if ranking is None else ranking
    rows = ranking.loc[ranking["sample"].eq(sample) & ranking["case"].eq(case)]
    if rows.empty and FINAL_MC_CASES.get(sample) == case:
        path = FINAL_MC_RESULT_PATHS[sample]
        if verify_result and not path.is_file():
            raise FileNotFoundError(path)
        scored = gate.score_run(
            csv_path=path,
            sample=sample,
            tag=case.rsplit("_", 1)[-1],
            tol_mpa=0.15,
            datum="stage1",
            preload_time=55.0,
            dn_channel="kinematic",
        )
        normalised = gate.normalised_scores(scored)
        return pd.Series(
            {
                "sample": sample,
                "case": case,
                "mean_nrmse_pct": normalised["mean"],
                "stages_reached": scored["reached"],
                "source_csv": str(path.relative_to(PROJECT_ROOT)),
            }
        )
    if len(rows) != 1:
        raise ValueError(f"{sample}: expected exactly one row for {case!r}; found {len(rows)}")
    row = rows.iloc[0]
    if verify_result:
        result_path(sample, row)
    return row


def score_case(sample: str, case: str, ranking: pd.DataFrame | None = None) -> dict:
    """Extract and score all eleven ordered Table 2 stages for one result."""
    row = resolve_case(sample, case, ranking)
    tag = case.rsplit("_", 1)[-1] if FINAL_MC_CASES.get(sample) == case else "hpc"
    result = gate.score_run(
        csv_path=result_path(sample, row),
        sample=sample,
        tag=tag,
        tol_mpa=0.15,
        datum="stage1",
        preload_time=55.0,
        dn_channel="kinematic",
    )
    if int(result["reached"]) != 11:
        raise ValueError(f"{sample} / {case}: reached {result['reached']}/11 stages")
    return result


def preflight(
    bb_cases: dict[str, str] = FINAL_BB_CASES,
    mc_cases: dict[str, str] = FINAL_MC_CASES,
) -> pd.DataFrame:
    """Return the selected-case inventory; raise early on missing files/cases."""
    ranking = _ranking()
    rows: list[dict] = []
    for model, mapping in (("BBFast", bb_cases), ("Mohr-Coulomb", mc_cases)):
        for sample in SAMPLE_ORDER:
            row = resolve_case(sample, mapping[sample], ranking)
            rows.append(
                {
                    "model": model,
                    "sample": DISPLAY_NAME[sample],
                    "case": row["case"],
                    "mean_nRMSE_pct": float(row["mean_nrmse_pct"]),
                    "stages": f"{int(row['stages_reached'])}/11",
                    "result_csv": str(result_path(sample, row).relative_to(PROJECT_ROOT)),
                }
            )
    return pd.DataFrame(rows)


def _score_map(case_map: dict[str, str]) -> dict[str, dict]:
    ranking = _ranking()
    return {sample: score_case(sample, case_map[sample], ranking) for sample in SAMPLE_ORDER}


def _panel_style(ax: plt.Axes, letter: str | None = None) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(direction="out", length=2.5, width=0.6, pad=1.4)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.35, alpha=0.7)
    if letter is not None:
        ax.text(
            0.02,
            0.96,
            f"({letter})",
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=6.6,
            fontweight="bold",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.82, "pad": 0.4},
            zorder=10,
        )


def _stage_axis(ax: plt.Axes, show_labels: bool = True, stage5: bool = False) -> None:
    ax.set_xlim(0.6, 11.4)
    ax.set_xticks(STAGES)
    if show_labels:
        ax.set_xticklabels([f"{int(p)}" for p in PRESSURES])
        ax.set_xlabel("Ordered stage (injection pressure, MPa)")
    else:
        ax.tick_params(axis="x", labelbottom=False)
    ax.axvline(6.5, color="#A0A0A0", linewidth=0.55, linestyle=":", zorder=0)
    ax.axvspan(6.5, 11.4, color="#F1F1F1", alpha=0.40, zorder=-5)
    if stage5:
        ax.axvspan(4.72, 5.28, color=YELLOW, alpha=0.22, zorder=-4)


def _limits(*arrays: np.ndarray, pad: float = 0.08) -> tuple[float, float]:
    values = np.concatenate([np.asarray(a, dtype=float).ravel() for a in arrays])
    values = values[np.isfinite(values)]
    if values.size == 0:
        return 0.0, 1.0
    low, high = float(values.min()), float(values.max())
    span = high - low
    if span == 0.0:
        span = max(abs(high), 1.0) * 0.1
    return low - pad * span, high + pad * span


def _model_and_paper(result: dict, key: str) -> tuple[np.ndarray, np.ndarray]:
    table = result["table"]
    return (
        pd.to_numeric(table[f"{key}_model"], errors="coerce").to_numpy(float),
        pd.to_numeric(table[f"{key}_paper"], errors="coerce").to_numpy(float),
    )
TABLE2_HYDRAULIC_SPECS = (
    ("Q_ml_min", "Flow rate\n(mL min$^{-1}$)", False),
    ("ah_um", "Hydraulic aperture\n(µm)", False),
    ("k_1e12_m2", "Fracture permeability\n($10^{-12}$ m$^2$)", True),
)

# The two test families occupy distinctly different hydraulic ranges.  Pairing
# their y scales keeps comparisons within each family direct without flattening
# the lower-range SW-S3/SW-S4 responses against the SW-T1/SW-T2 range.
TABLE2_SCALE_GROUPS = (
    ("SWT1", "SWT2"),
    ("SWS3", "SWS4"),
)


def _table2_values(result: dict, key: str) -> tuple[np.ndarray, np.ndarray]:
    table = result["table"]
    if key == "Pi":
        model_column, paper_column = "Pi_model_MPa", "Pi_target_MPa"
    else:
        model_column, paper_column = f"{key}_model", f"{key}_paper"
    return (
        pd.to_numeric(table[model_column], errors="coerce").to_numpy(float),
        pd.to_numeric(table[paper_column], errors="coerce").to_numpy(float),
    )


def _figure_table2_specimens(
    specs: tuple[tuple[str, str, bool], ...],
    figure_key: str,
    bb_cases: dict[str, str] = FINAL_BB_CASES,
    mc_cases: dict[str, str] = FINAL_MC_CASES,
) -> plt.Figure:
    """Build one focused Table 2 comparison for all four specimens."""
    apply_agu_style()
    bb_scored = _score_map(bb_cases)
    mc_scored = _score_map(mc_cases)
    figure, axes = plt.subplots(
        len(specs), len(SAMPLE_ORDER),
        figsize=FIGURE_SIZES_IN[figure_key], squeeze=False,
    )

    for row_index, (key, row_label, use_log_scale) in enumerate(specs):
        group_limits = {}
        for scale_group in TABLE2_SCALE_GROUPS:
            group_values = []
            for sample in scale_group:
                bb_model, paper = _table2_values(bb_scored[sample], key)
                mc_model, _ = _table2_values(mc_scored[sample], key)
                group_values.extend((paper, bb_model, mc_model))
            if use_log_scale:
                finite = np.concatenate(
                    [values[np.isfinite(values) & (values > 0)] for values in group_values]
                )
                limits = (float(finite.min()) / 1.25, float(finite.max()) * 1.25)
            else:
                limits = _limits(*group_values, pad=0.07)
            group_limits.update({sample: limits for sample in scale_group})

        for column_index, sample in enumerate(SAMPLE_ORDER):
            ax = axes[row_index, column_index]
            bb_table = bb_scored[sample]["table"]
            mc_table = mc_scored[sample]["table"]
            bb_model, paper = _table2_values(bb_scored[sample], key)
            mc_model, _ = _table2_values(mc_scored[sample], key)
            for branch, linestyle, paper_marker, model_marker in (
                ("loading", "-", "o", "^"),
                ("unloading", "--", "s", "v"),
            ):
                bb_mask = bb_table["segment"].astype(str).str.strip().str.lower().eq(branch).to_numpy()
                mc_mask = mc_table["segment"].astype(str).str.strip().str.lower().eq(branch).to_numpy()
                bb_x = pd.to_numeric(bb_table.loc[bb_mask, "Pi_target_MPa"], errors="coerce")
                mc_x = pd.to_numeric(mc_table.loc[mc_mask, "Pi_target_MPa"], errors="coerce")
                filled = branch == "loading"
                ax.plot(
                    bb_x, paper[bb_mask], color=BLACK, linestyle=linestyle,
                    marker=paper_marker, markerfacecolor=BLACK if filled else "white",
                    markeredgecolor=BLACK, linewidth=0.95, markersize=3.1, zorder=5,
                )
                ax.plot(
                    bb_x, bb_model[bb_mask], color=BLUE, linestyle=linestyle,
                    marker=model_marker, markerfacecolor=BLUE if filled else "white",
                    markeredgecolor=BLUE, linewidth=0.95, markersize=3.0, zorder=4,
                )
                ax.plot(
                    mc_x, mc_model[mc_mask], color=ORANGE, linestyle=linestyle,
                    marker=model_marker, markerfacecolor=ORANGE if filled else "white",
                    markeredgecolor=ORANGE, linewidth=0.95, markersize=3.0, zorder=3,
                )

            ax.set_xlim(6.7, 29.3)
            ax.set_xticks([8, 12, 16, 20, 24, 28])
            ax.set_ylim(*group_limits[sample])
            if use_log_scale:
                ax.set_yscale("log")
            ax.yaxis.set_major_locator(LogLocator(numticks=4) if use_log_scale else MaxNLocator(nbins=4))
            _panel_style(ax)
            if column_index == 0:
                ax.set_ylabel(row_label)
            elif column_index != 2:
                ax.tick_params(axis="y", labelleft=False)
            if row_index == 0:
                ax.set_title(DISPLAY_NAME[sample], pad=5.0, fontweight="bold")
            if row_index == len(specs) - 1:
                ax.set_xlabel("Table 2 injection pressure (MPa)")
            else:
                ax.tick_params(axis="x", labelbottom=False)

    figure.legend(
        handles=(
            Line2D([], [], color=BLACK, marker="o", markersize=3.4, label="Ye & Ghassemi (2018), Table 2"),
            Line2D([], [], color=BLUE, marker="^", markersize=3.4, label="Barton-Bandis simulation"),
            Line2D([], [], color=ORANGE, marker="^", markersize=3.4, label="Mohr-Coulomb simulation"),
            Line2D([], [], color=GRAY, linestyle="-", marker="o", markerfacecolor=GRAY, markersize=3.4, label="Loading"),
            Line2D([], [], color=GRAY, linestyle="--", marker="s", markerfacecolor="white", markersize=3.4, label="Unloading"),
        ),
        loc="upper center", bbox_to_anchor=(0.54, 0.995), ncol=5, frameon=False,
    )
    axes_top = 0.90 if len(specs) == 4 else 0.85
    figure.subplots_adjust(left=0.13, right=0.995, bottom=0.075, top=axes_top, wspace=0.28, hspace=0.24)
    validate_figure(figure_key, figure)
    return figure


def figure_table2_hydraulic(
    bb_cases: dict[str, str] = FINAL_BB_CASES,
    mc_cases: dict[str, str] = FINAL_MC_CASES,
) -> plt.Figure:
    """Figure 3c: three Table 2 hydraulic quantities for all specimens."""
    return _figure_table2_specimens(TABLE2_HYDRAULIC_SPECS, "table2_hydraulic", bb_cases, mc_cases)


OUTPUT_FILENAME = 'Figure_Table2_Hydraulic_All_Specimens.pdf'


def main() -> Path:
    """Build and export this figure; return the absolute PDF path."""
    figure = figure_table2_hydraulic(FINAL_BB_CASES, FINAL_MC_CASES)
    validate_figure('table2_hydraulic', figure)
    output_path = OUTPUT_DIR / OUTPUT_FILENAME
    figure.savefig(
        output_path,
        format="pdf",
        dpi=AGU_SAVE_DPI,
        bbox_inches="tight",
        facecolor="white",
        metadata={
            "Title": OUTPUT_FILENAME.removesuffix(".pdf").replace("_", " "),
            "Author": "ORCA Ye--Ghassemi validation workflow",
            "Subject": "AGU manuscript result figure",
        },
    )
    print(output_path)
    return output_path


if __name__ == "__main__":
    main()
