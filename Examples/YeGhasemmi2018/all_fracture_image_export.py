"""Batch validation-image export for the Ye and Ghassemi (2018) campaign.

The public entry point, :func:`export_all_fracture_images`, discovers every CSV
in the four per-sample ``results_csv_hpc*`` directories.  For each result it
saves a 12-panel time-history comparison and an eight-panel Table 2 hold-stage
comparison in ``image_output_all_fractures/<sample>``.
"""

from __future__ import annotations

from pathlib import Path
import math
import re
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SAMPLES = ("SWT1", "SWT2", "SWS3", "SWS4")
PAPER_SAMPLE_NAMES = {
    "SWT1": "SW-T1",
    "SWT2": "SW-T2",
    "SWS3": "SW-S3",
    "SWS4": "SW-S4",
}
TABLE2_HOLD_TIMES_S = {
    "SWT1": np.array(
        [225.2, 556.9, 838.6, 1164.2, 1436.6, 1704.7,
         2063.5, 2336.9, 2629.0, 2952.2, 3256.8]
    ),
    "SWT2": np.array(
        [319.6, 766.3, 1223.5, 1628.8, 1992.5, 2319.3,
         2537.1, 2587.8, 2638.3, 2657.6, 2766.4]
    ),
    "SWS3": np.array(
        [335.9, 868.4, 1364.0, 1804.7, 2236.5, 2522.5,
         3019.0, 3475.3, 3854.0, 4241.6, 4674.7]
    ),
    "SWS4": np.array(
        [252.5, 570.5, 849.3, 1157.5, 1471.4, 1703.9,
         2046.8, 2359.3, 2668.7, 2968.5, 3293.5]
    ),
}


# Digitized time-history files shipped with this repository.  The spelling and
# capitalization intentionally match the original filenames.
VALIDATION_FILES = {
    "SWT1": {
        "injection_pressure": "SWT1_injection_pressure_MPa.csv",
        "production_pressure": "SWt1_produciton_pressure.csv",
        "differential_stress": "SWT1_differential_stress.csv",
        "piston_displacement": "SWT1_piston_displacement_mm.csv",
        "effective_normal_stress": "SWT1_effective_normal_stress.csv",
        "shear_stress": "SWT1_shear_stress.csv",
        "shear_slip": "SWT1_shear_slip_mm.csv",
        "normal_dilation": "SWT1_normal_dilation.csv",
        "flow_rate": "SWt1_flow_rate.csv",
        "permeability": "SWT1_fracture_permeability_m2.csv",
    },
    "SWT2": {
        "injection_pressure": "SWT2_injection_pressure_MPA.csv",
        "production_pressure": "SWT2_production_pressure_MPa.csv",
        "differential_stress": "SWt2_differential_stress.csv",
        "piston_displacement": "SWT2_piston_Displacement_mm.csv",
        "effective_normal_stress": "SWT2_effective_normal_stress_MPa.csv",
        "shear_stress": "SWT2_shear_stress_MPa.csv",
        "shear_slip": "SWt2_shear_dilation_mm.csv",
        "normal_dilation": "SWT2_normal_dilation_mm.csv",
        "flow_rate": "SWt2_flow_rate_ml:min.csv",
        "permeability": "SWt2_fracture_peremabiltiy_m2.csv",
    },
    "SWS3": {
        "injection_pressure": "Injection_pressure_vs_time_SW3.csv",
        "differential_stress": "differnetial_stress_vs_time_sw3.csv",
        "piston_displacement": "piston_disp_mm_vs_time_sw3.csv",
        "effective_normal_stress": "effective_normal_stress_mpa_Vs_time_SW3.csv",
        "shear_stress": "shear_stress_MPa_vs_time_sw3.csv",
        "shear_slip": "shear_slip_mm_vs_time_sw3.csv",
        "normal_dilation": "normal_dilation_mm_vs_time_sw3.csv",
        "flow_rate": "flow_Rate_mlmin_vs_time_sw3.csv",
        "permeability": "permeability_m2_vs_time_sw3.csv",
    },
    "SWS4": {
        "injection_pressure": "Ye2018_SW4_Injection_pressure_Vs_time.csv",
        "differential_stress": "Ye2018_SW4_Differential_Stress_Vs_time.csv",
        "effective_normal_stress": "Ye2018_SW4_normal_stress_Vs_time.csv",
        "shear_stress": "Ye2018_SW4_shear_stress_Vs_time.csv",
        "shear_slip": "Ye2018_SW4_shear_slip_Vs_time.csv",
        "normal_dilation": "Ye2018_SW4_normal_dilation_Vs_time.csv",
        "flow_rate": "Ye2018_SW4_flow_rate_Vs_time.csv",
        "permeability": "Ye2018_SW4_frac_perm_Vs_time.csv",
    },
}


# Twelve consistent time-history panels.  Each ``columns`` entry is
# (candidate CSV column, multiplier to the displayed unit).
VALIDATION_PANELS = {
    "injection_pressure": {
        "label": "Injection pressure (MPa)",
        "columns": (("injection_pressure_pp", 1.0e-6),),
    },
    "production_pressure": {
        "label": "Production pressure (MPa)",
        "columns": (("pp_outlet_pp", 1.0e-6),),
    },
    "differential_stress": {
        "label": "Differential stress (MPa)",
        "columns": (
            ("differential_stress_reaction_mpa_pp", 1.0),
            ("differential_stress_mpa_pp", 1.0),
        ),
    },
    "piston_displacement": {
        "label": "Piston displacement (mm)",
        "columns": (("axial_command_m_pp", 1.0e3),),
        "zero": True,
    },
    "effective_normal_stress": {
        "label": "Effective normal stress (MPa)",
        "columns": (
            ("effective_normal_paper_frame_mpa_pp", 1.0),
            ("effective_normal_compression_mpa_pp", 1.0),
            ("bb_effective_normal_stress_pp", 1.0e-6),
        ),
    },
    "shear_stress": {
        "label": "Shear stress (MPa)",
        "columns": (
            ("shear_stress_paper_frame_mpa_pp", 1.0),
            ("shear_traction_magnitude_pa", 1.0e-6),
        ),
    },
    "shear_slip": {
        "label": "Shear slip (mm)",
        "columns": (
            ("czm_shear_slip_mm_pp", 1.0),
            ("reported_czm_shear_slip_mm_pp", 1.0),
        ),
        "zero": True,
    },
    "normal_dilation": {
        "label": "Normal displacement / dilation (mm)",
        "columns": (
            ("czm_normal_dilation_paper_mm_pp", 1.0),
            ("frac_normal_dilation_paper_mm", 1.0),
        ),
        "zero": True,
    },
    "flow_rate": {
        "label": "Validation-equivalent flow (mL/min)",
        "columns": (
            ("flow_rate_validation_ml_min_pp", 1.0),
            ("flow_rate_pp", 1.0),
        ),
    },
    "hydraulic_aperture": {
        "label": "Hydraulic aperture (µm)",
        "columns": (
            ("hydraulic_aperture_um_pp", 1.0),
            ("hydraulic_aperture_pp", 1.0e6),
        ),
    },
    "permeability": {
        "label": "Fracture permeability (m²)",
        "columns": (("fracture_permeability_pp", 1.0),),
        "log": True,
    },
    "flow_imbalance": {
        "label": "Flow mass imbalance (%)",
        "columns": (("flow_mass_imbalance_fraction_pp", 100.0),),
    },
}


# Eight quantities reported by Ye and Ghassemi (2018), Table 2.
TABLE2_PANELS = {
    "injection_pressure": ("injection_pressure_MPa", 1.0),
    "effective_normal_stress": ("effective_normal_stress_MPa", 1.0),
    "shear_stress": ("shear_stress_MPa", 1.0),
    "shear_slip": ("shear_slip_mm", 1.0),
    "normal_dilation": ("normal_dilation_mm", 1.0),
    "flow_rate": ("flow_rate_ml_min", 1.0),
    "hydraulic_aperture": ("hydraulic_aperture_m", 1.0e6),
    "permeability": ("fracture_permeability_m2", 1.0),
}


def _read_numeric_csv(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if "time" not in frame.columns:
        raise KeyError(f"{path.name}: missing required time column")
    for column in frame.columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return (
        frame.dropna(subset=["time"])
        .sort_values("time")
        .drop_duplicates("time", keep="last")
        .reset_index(drop=True)
    )


def _read_two_column_csv(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(
        path, header=None, names=["time", "value"], comment="#"
    )
    frame = frame.apply(pd.to_numeric, errors="coerce").dropna()
    return (
        frame.sort_values("time")
        .drop_duplicates("time", keep="last")
        .reset_index(drop=True)
    )


def _load_validation(study_dir: Path, sample: str) -> dict[str, pd.DataFrame]:
    directory = study_dir / sample / sample
    loaded = {}
    for quantity, filename in VALIDATION_FILES[sample].items():
        path = directory / filename
        if path.is_file():
            frame = _read_two_column_csv(path)
            if len(frame) >= 2:
                loaded[quantity] = frame
    return loaded


def _load_table2(study_dir: Path, sample: str) -> pd.DataFrame:
    path = (
        study_dir / "Extracted_Data" / "Table2_4_Sample_CSV_Files"
        / f"{PAPER_SAMPLE_NAMES[sample]}_Table2.csv"
    )
    frame = pd.read_csv(path).sort_values("hold_stage_index").reset_index(drop=True)
    if len(frame) != len(TABLE2_HOLD_TIMES_S[sample]):
        raise ValueError(
            f"{path.name}: expected {len(TABLE2_HOLD_TIMES_S[sample])} stages, "
            f"found {len(frame)}"
        )
    frame["hold_time_s"] = TABLE2_HOLD_TIMES_S[sample]
    frame["branch"] = frame["segment"].astype(str).str.strip().str.lower()
    return frame


def _model_series(
    frame: pd.DataFrame, quantity: str
) -> tuple[np.ndarray, np.ndarray, str] | None:
    spec = VALIDATION_PANELS[quantity]
    for column, scale in spec["columns"]:
        if column not in frame.columns:
            continue
        time = pd.to_numeric(frame["time"], errors="coerce").to_numpy(float)
        value = pd.to_numeric(frame[column], errors="coerce").to_numpy(float) * scale
        finite = np.isfinite(time) & np.isfinite(value)
        if finite.any():
            order = np.argsort(time[finite])
            return time[finite][order], value[finite][order], column
    return None


def _reference_displacement(
    time: np.ndarray,
    value: np.ndarray,
    reference_time: float,
) -> np.ndarray:
    if not len(value):
        return value
    return value - np.interp(reference_time, time, value)


def _ranking_text(
    sample: str,
    result_stem: str,
    table2_ranking: pd.DataFrame | None,
) -> str:
    if table2_ranking is None or table2_ranking.empty:
        return "ranking unavailable"
    case = result_stem.removesuffix("_hpc")
    rows = table2_ranking.loc[
        table2_ranking["sample"].astype(str).eq(sample)
        & table2_ranking["case"].astype(str).eq(case)
    ]
    if rows.empty:
        if any(term in case.lower() for term in ("cyclic", "shutin")):
            return "nonstandard protocol; Table 2 shown for reference only"
        return "not present in Table 2 ranking"
    row = rows.iloc[0]
    status = str(row.get("run_status", "unknown"))
    rank = pd.to_numeric(row.get("rank_within_sample"), errors="coerce")
    error = pd.to_numeric(row.get("mean_nrmse_pct"), errors="coerce")
    if np.isfinite(rank) and np.isfinite(error):
        return f"{status}; rank #{int(rank)}; five-channel mean nRMSE {error:.3f}%"
    stages = pd.to_numeric(row.get("stages_reached"), errors="coerce")
    total = pd.to_numeric(row.get("total_stages"), errors="coerce")
    coverage = (
        f"; {int(stages)}/{int(total)} holds" if np.isfinite(stages + total) else ""
    )
    return f"{status}{coverage}; unranked"


def _safe_filename(stem: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", stem).strip("._")


def _plot_validation_12(
    sample: str,
    result_path: Path,
    frame: pd.DataFrame,
    validation: dict[str, pd.DataFrame],
    table2: pd.DataFrame,
    ranking_text: str,
    output_path: Path,
    dpi: int,
) -> list[str]:
    fig, axes = plt.subplots(4, 3, figsize=(18, 15), squeeze=False)
    used_columns = []
    for ax, (quantity, spec) in zip(axes.flat, VALIDATION_PANELS.items()):
        series = _model_series(frame, quantity)
        measured = validation.get(quantity)
        reference_time = (
            float(measured["time"].min())
            if measured is not None and not measured.empty
            else float(table2["hold_time_s"].iloc[0])
        )

        if series is None:
            ax.text(
                0.5, 0.5, "Model channel unavailable", transform=ax.transAxes,
                ha="center", va="center", color="0.35"
            )
            used_columns.append("")
        else:
            time, value, column = series
            if spec.get("zero", False):
                value = _reference_displacement(time, value, reference_time)
            ax.plot(time, value, color="tab:blue", linewidth=1.35, label="ORCA")
            used_columns.append(column)

        if measured is not None and not measured.empty:
            exp_value = measured["value"].to_numpy(float)
            if spec.get("zero", False):
                exp_value = exp_value - exp_value[0]
            ax.scatter(
                measured["time"], exp_value, s=13, facecolors="none",
                edgecolors="tab:orange", linewidths=0.9,
                label="Ye & Ghassemi digitized", zorder=5
            )

        if quantity in TABLE2_PANELS:
            paper_column, paper_scale = TABLE2_PANELS[quantity]
            paper_value = (
                pd.to_numeric(table2[paper_column], errors="coerce").to_numpy(float)
                * paper_scale
            )
            ax.scatter(
                table2["hold_time_s"], paper_value, marker="x", s=24,
                color="black", linewidths=0.9, label="Table 2 holds", zorder=6
            )

        ax.set_title(spec["label"], fontsize=10)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(spec["label"])
        if spec.get("log", False):
            positive = []
            if series is not None:
                positive.extend(value[np.isfinite(value)].tolist())
            if measured is not None:
                positive.extend(measured["value"].dropna().tolist())
            if positive and min(positive) > 0:
                ax.set_yscale("log")
        if not (measured is not None or quantity in TABLE2_PANELS):
            ax.text(
                0.02, 0.03, "simulation diagnostic; no direct paper series",
                transform=ax.transAxes, fontsize=7, color="0.35"
            )
        ax.tick_params(labelsize=8)

    handles, labels = [], []
    for ax in axes.flat:
        for handle, label in zip(*ax.get_legend_handles_labels()):
            if label not in labels:
                handles.append(handle)
                labels.append(label)
    fig.suptitle(
        f"{sample}: {result_path.name}\n12 validation/diagnostic histories — {ranking_text}",
        fontsize=13, y=0.995
    )
    if handles:
        fig.legend(handles, labels, loc="lower center", ncol=len(labels), fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 0.965))
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return used_columns


def _sample_at_holds(
    frame: pd.DataFrame,
    quantity: str,
    hold_times: np.ndarray,
) -> np.ndarray:
    series = _model_series(frame, quantity)
    if series is None:
        return np.full(len(hold_times), np.nan)
    time, value, _column = series
    sampled = np.interp(hold_times, time, value, left=np.nan, right=np.nan)
    if VALIDATION_PANELS[quantity].get("zero", False) and np.isfinite(sampled[0]):
        sampled = sampled - sampled[0]
    return sampled


def _plot_table2(
    sample: str,
    result_path: Path,
    frame: pd.DataFrame,
    table2: pd.DataFrame,
    ranking_text: str,
    output_path: Path,
    dpi: int,
) -> None:
    hold_times = TABLE2_HOLD_TIMES_S[sample]
    fig, axes = plt.subplots(4, 2, figsize=(14, 17), squeeze=False)
    for ax, (quantity, (paper_column, paper_scale)) in zip(
        axes.flat, TABLE2_PANELS.items()
    ):
        model_value = _sample_at_holds(frame, quantity, hold_times)
        paper_value = (
            pd.to_numeric(table2[paper_column], errors="coerce").to_numpy(float)
            * paper_scale
        )
        for branch, linestyle, paper_marker, model_marker in (
            ("loading", "-", "o", "^"),
            ("unloading", "--", "s", "v"),
        ):
            mask = table2["branch"].eq(branch).to_numpy()
            x = table2.loc[mask, "injection_pressure_MPa"]
            ax.plot(
                x, paper_value[mask], color="black", linestyle=linestyle,
                marker=paper_marker, markerfacecolor=("black" if branch == "loading" else "white"),
                markersize=5, linewidth=1.15, label=f"Table 2 {branch}"
            )
            ax.plot(
                x, model_value[mask], color="tab:blue", linestyle=linestyle,
                marker=model_marker, markerfacecolor=("tab:blue" if branch == "loading" else "white"),
                markersize=5, linewidth=1.15, label=f"ORCA {branch}"
            )
        ax.set_title(VALIDATION_PANELS[quantity]["label"], fontsize=10)
        ax.set_xlabel("Table 2 injection pressure (MPa)")
        ax.set_ylabel(VALIDATION_PANELS[quantity]["label"])
        ax.set_xticks([8, 12, 16, 20, 24, 28])
        if VALIDATION_PANELS[quantity].get("log", False):
            finite = np.r_[paper_value[np.isfinite(paper_value)], model_value[np.isfinite(model_value)]]
            if len(finite) and np.all(finite > 0):
                ax.set_yscale("log")
        ax.tick_params(labelsize=8)

    handles, labels = [], []
    for ax in axes.flat:
        for handle, label in zip(*ax.get_legend_handles_labels()):
            if label not in labels:
                handles.append(handle)
                labels.append(label)
    fig.suptitle(
        f"{sample}: {result_path.name}\nORCA hold stages versus Ye & Ghassemi (2018), Table 2 — {ranking_text}",
        fontsize=13, y=0.995
    )
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=9)
    fig.tight_layout(rect=(0, 0.045, 1, 0.965))
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _configured_end_time(input_path: Path | None) -> float:
    if input_path is None or not input_path.is_file():
        return np.nan
    matches = re.findall(
        r"(?m)^\s*end_time\s*=\s*([0-9.eE+-]+)\s*(?:#.*)?$",
        input_path.read_text(errors="replace"),
    )
    return float(matches[-1]) if matches else np.nan


def discover_hpc_results(study_dir: Path) -> pd.DataFrame:
    """Inventory every downloaded HPC CSV and its matching top-level input."""
    rows = []
    for sample in SAMPLES:
        sample_dir = study_dir / sample
        input_by_stem = {path.stem: path for path in sample_dir.glob("*.i")}
        result_paths = sorted(
            {
                path.resolve()
                for root in sample_dir.glob("results_csv_hpc*")
                if root.is_dir()
                for path in root.glob("*.csv")
                if path.is_file()
            },
            key=lambda path: path.name.lower(),
        )
        result_cases = set()
        for result_path in result_paths:
            case = result_path.stem.removesuffix("_hpc")
            result_cases.add(case)
            input_path = input_by_stem.get(case)
            rows.append({
                "sample": sample,
                "case": case,
                "input_file": str(input_path) if input_path else "",
                "result_file": str(result_path),
                "pair_status": "matched" if input_path else "result_without_input",
            })
        for case, input_path in sorted(input_by_stem.items()):
            if case not in result_cases:
                rows.append({
                    "sample": sample,
                    "case": case,
                    "input_file": str(input_path),
                    "result_file": "",
                    "pair_status": "input_without_hpc_result",
                })
    return pd.DataFrame(rows)


def export_all_fracture_images(
    study_dir: str | Path,
    table2_ranking: pd.DataFrame | None = None,
    output_directory: str | Path | None = None,
    *,
    dpi: int = 160,
    overwrite: bool = True,
    progress_every: int = 1,
) -> pd.DataFrame:
    """Export validation and Table 2 PNGs for every downloaded HPC result.

    Returns a manifest with one row per discovered input/result record.  Missing
    results are retained in the manifest, while each available result produces
    two PNGs.  Existing PNGs can be retained with ``overwrite=False``.
    """
    study_dir = Path(study_dir).resolve()
    output_root = (
        Path(output_directory).resolve()
        if output_directory is not None
        else study_dir / "image_output_all_fractures"
    )
    output_root.mkdir(parents=True, exist_ok=True)
    inventory = discover_hpc_results(study_dir)
    export_rows = []
    available = inventory.loc[inventory["result_file"].ne("")]
    total = len(available)
    completed = 0

    validation_by_sample = {
        sample: _load_validation(study_dir, sample) for sample in SAMPLES
    }
    table2_by_sample = {
        sample: _load_table2(study_dir, sample) for sample in SAMPLES
    }

    for record in inventory.itertuples(index=False):
        base = record._asdict()
        if not record.result_file:
            export_rows.append({
                **base,
                "rows": 0,
                "final_time_s": np.nan,
                "configured_end_s": _configured_end_time(Path(record.input_file)),
                "run_status": "missing result",
                "validation_png": "",
                "table2_png": "",
                "export_status": "not exported",
            })
            continue

        result_path = Path(record.result_file)
        input_path = Path(record.input_file) if record.input_file else None
        sample_output = output_root / record.sample
        sample_output.mkdir(parents=True, exist_ok=True)
        safe_stem = _safe_filename(result_path.stem)
        validation_png = sample_output / f"{safe_stem}__validation_12.png"
        table2_png = sample_output / f"{safe_stem}__table2.png"
        expected_end = _configured_end_time(input_path)

        try:
            frame = _read_numeric_csv(result_path)
            final_time = float(frame["time"].max()) if len(frame) else np.nan
            run_status = (
                "complete"
                if np.isfinite(expected_end) and final_time >= expected_end - 1.0e-6
                else "partial"
                if np.isfinite(final_time)
                else "unreadable"
            )
            rank_text = _ranking_text(
                record.sample, result_path.stem, table2_ranking
            )
            if overwrite or not validation_png.is_file():
                _plot_validation_12(
                    record.sample, result_path, frame,
                    validation_by_sample[record.sample],
                    table2_by_sample[record.sample], rank_text,
                    validation_png, dpi,
                )
            if overwrite or not table2_png.is_file():
                _plot_table2(
                    record.sample, result_path, frame,
                    table2_by_sample[record.sample], rank_text,
                    table2_png, dpi,
                )
            export_status = "OK"
        except Exception as exc:  # continue so one corrupt download does not stop the audit
            warnings.warn(f"Could not export {result_path}: {exc}")
            final_time = np.nan
            run_status = "error"
            export_status = f"ERROR: {exc}"

        completed += 1
        if progress_every and (completed % progress_every == 0 or completed == total):
            print(f"[{completed:>3}/{total}] {record.sample} / {result_path.name}: {export_status}")
        export_rows.append({
            **base,
            "rows": int(len(frame)) if "frame" in locals() else 0,
            "final_time_s": final_time,
            "configured_end_s": expected_end,
            "run_status": run_status,
            "validation_png": str(validation_png) if validation_png.is_file() else "",
            "table2_png": str(table2_png) if table2_png.is_file() else "",
            "export_status": export_status,
        })
        if "frame" in locals():
            del frame

    manifest = pd.DataFrame(export_rows).sort_values(
        ["sample", "pair_status", "case"]
    ).reset_index(drop=True)
    manifest_path = output_root / "image_export_manifest.csv"
    manifest.to_csv(manifest_path, index=False)
    print(f"Wrote {manifest_path}")
    return manifest
