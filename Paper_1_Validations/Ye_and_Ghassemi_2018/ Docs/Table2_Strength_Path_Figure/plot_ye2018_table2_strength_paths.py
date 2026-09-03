#!/usr/bin/env python3
"""Plot Ye and Ghassemi (2018) Table 2 stress paths and strength limits.

The protocol116 case set is the default.  The older calibrated cases are
available only through --case-set legacy --allow-legacy and are visibly marked
as a prototype.  Every plotted stage is exported to CSV.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

import matplotlib

if __name__ == "__main__":
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd


SAMPLES = ("SWT1", "SWT2", "SWS3", "SWS4")
DISPLAY = {"SWT1": "SW-T1", "SWT2": "SW-T2", "SWS3": "SW-S3", "SWS4": "SW-S4"}


def find_project_root() -> Path:
    starts = (Path(__file__).resolve().parent, Path.cwd().resolve())
    for start in starts:
        for candidate in (start, *start.parents):
            if (candidate / "scripts" / "table2_gate.py").is_file():
                return candidate
    fallback = Path("/media/geomechanics/Data4TB/projects/orca_4.0")
    if (fallback / "scripts" / "table2_gate.py").is_file():
        return fallback
    raise FileNotFoundError("Could not locate the Orca project root")


ROOT = find_project_root()
sys.path.insert(0, str(ROOT / "scripts"))
import table2_gate as gate  # noqa: E402


# Paths are relative to ROOT.  The protocol paths are the canonical locations
# expected after completed HPC results have been returned to the project.
CASE_SETS = {
    "legacy": {
        "SWT1": {
            "BB": (
                "Examples/YeGhasemmi2018/SWT1/Sweeps/results_csv_local/107_01_swt1_coh27p2_apscale0p01512_ppfix.csv",
                "Examples/YeGhasemmi2018/SWT1/Sweeps/107_01_swt1_coh27p2_apscale0p01512_ppfix.i",
            ),
            "MC": (
                "Examples/YeGhasemmi2018/SWT1/results_csv_mc_sweep_hpc/SWT1_OrcaMohrCoulombContactTraction_pb04.csv",
                "Examples/YeGhasemmi2018/SWT1/SWT1_OrcaMohrCoulombContactTraction.i",
            ),
        },
        "SWT2": {
            "BB": (
                "Examples/YeGhasemmi2018/SWT2/Sweeps/results_csv_hpc_rorqual/100_04_swt2_apscale0p0177_ppfix_hpc.csv",
                "Examples/YeGhasemmi2018/SWT2/Sweeps/100_04_swt2_apscale0p0177_ppfix.i",
            ),
            "MC": (
                "Examples/YeGhasemmi2018/SWT2/results_csv_mc_sweep_hpc/SWT2_OrcaMohrCoulombContactTraction_pb04.csv",
                "Examples/YeGhasemmi2018/SWT2/SWT2_OrcaMohrCoulombContactTraction.i",
            ),
        },
        "SWS3": {
            "BB": (
                "Examples/YeGhasemmi2018/SWS3/Sweeps/results_csv_hpc_rorqual/100_06_sw3_resc1p30_unld0p00_ppfix_hpc.csv",
                "Examples/YeGhasemmi2018/SWS3/Sweeps/100_06_sw3_resc1p30_unld0p00_ppfix.i",
            ),
            "MC": (
                "Examples/YeGhasemmi2018/SWS3/results_csv_mc_sweep_hpc/SWS3_OrcaMohrCoulombContactTraction_pb06.csv",
                "Examples/YeGhasemmi2018/SWS3/SWS3_OrcaMohrCoulombContactTraction.i",
            ),
        },
        "SWS4": {
            "BB": (
                "Examples/YeGhasemmi2018/SWS4/Sweeps/results_csv_hpc_rorqual/93_07_sw4_final_theta30_jrc5_ppfix_hpc.csv",
                "Examples/YeGhasemmi2018/SWS4/Sweeps/93_07_sw4_final_theta30_jrc5_ppfix.i",
            ),
            "MC": (
                "Examples/YeGhasemmi2018/SWS4/results_csv_mc_sweep_hpc/SWS4_OrcaMohrCoulombContactTraction_center.csv",
                "Examples/YeGhasemmi2018/SWS4/SWS4_OrcaMohrCoulombContactTraction.i",
            ),
        },
    },
    "protocol116": {
        "SWT1": {
            "BB": (
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWT1/proposed_inputs/protocol_consistency_20260902/csv/116_01_swt1_bb_commonK796_protocol_ppfix.csv",
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWT1/116_01_swt1_bb_commonK796_protocol_ppfix.i",
            ),
            "MC": (
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWT1/proposed_inputs/protocol_consistency_20260902/csv/116_02_swt1_mc_commonK796_protocol_ppfix.csv",
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWT1/116_02_swt1_mc_commonK796_protocol_ppfix.i",
            ),
        },
        "SWT2": {
            "BB": (
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWT2/proposed_inputs/protocol_consistency_20260902/csv/116_03_swt2_bb_theta31_commonK796_protocol_ppfix.csv",
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWT2/116_03_swt2_bb_theta31_commonK796_protocol_ppfix.i",
            ),
            "MC": (
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWT2/proposed_inputs/protocol_consistency_20260902/csv/116_04_swt2_mc_theta31_commonK796_protocol_ppfix.csv",
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWT2/116_04_swt2_mc_theta31_commonK796_protocol_ppfix.i",
            ),
        },
        "SWS3": {
            "BB": (
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWS3/proposed_inputs/protocol_consistency_20260902/csv/116_05_sws3_bb_fixedpiston_commonK796_protocol_ppfix.csv",
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWS3/116_05_sws3_bb_fixedpiston_commonK796_protocol_ppfix.i",
            ),
            "MC": (
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWS3/proposed_inputs/protocol_consistency_20260902/csv/116_06_sws3_mc_fixedpiston_commonK796_protocol_ppfix.csv",
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWS3/116_06_sws3_mc_fixedpiston_commonK796_protocol_ppfix.i",
            ),
        },
        "SWS4": {
            "BB": (
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWS4/proposed_inputs/protocol_consistency_20260902/csv/116_07_sws4_bb_jrc1p19_fixedpiston_commonK796_ppfix.csv",
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWS4/116_07_sws4_bb_jrc1p19_fixedpiston_commonK796_ppfix.i",
            ),
            "MC": (
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWS4/proposed_inputs/protocol_consistency_20260902/csv/116_08_sws4_mc_fixedpiston_commonK796_protocol_ppfix.csv",
                "Examples/YeGhasemmi2018/protocol_consistency_20260902/SWS4/116_08_sws4_mc_fixedpiston_commonK796_protocol_ppfix.i",
            ),
        },
    },
}


# Reference limits used only for plotting the analytical envelopes.  Values are
# those baked into the selected cases.  MC sweep values differ from the parent
# deck defaults, so keeping this explicit table is essential for provenance.
BB_PARAMETERS = {
    "SWT1": dict(jrc=15.32, jcs_mpa=150.0, phi_peak_base_deg=29.756,
                 cohesion_peak_mpa=27.20, phi_residual_deg=29.756,
                 cohesion_residual_mpa=9.19),
    "SWT2": dict(jrc=14.63, jcs_mpa=150.0, phi_peak_base_deg=29.756,
                 cohesion_peak_mpa=33.20, phi_residual_deg=29.756,
                 cohesion_residual_mpa=9.71),
    "SWS3": dict(jrc=1.96, jcs_mpa=150.0, phi_peak_base_deg=29.756,
                 cohesion_peak_mpa=1.67, phi_residual_deg=8.45,
                 cohesion_residual_mpa=1.30),
    "SWS4": dict(jrc=5.0, jcs_mpa=150.0, phi_peak_base_deg=22.72,
                 cohesion_peak_mpa=0.0, phi_residual_deg=6.50,
                 cohesion_residual_mpa=0.0),
}

MC_PARAMETERS = {
    "SWT1": dict(mu_rough=0.509312, mu_smooth=0.640304,
                 cohesion_rough_mpa=40.7374, cohesion_smooth_mpa=7.8115),
    "SWT2": dict(mu_rough=0.508576, mu_smooth=0.640304,
                 cohesion_rough_mpa=47.2549, cohesion_smooth_mpa=8.2535),
    "SWS3": dict(mu_rough=0.952344, mu_smooth=0.166432,
                 cohesion_rough_mpa=2.3805, cohesion_smooth_mpa=1.19),
    "SWS4": dict(mu_rough=0.9804, mu_smooth=0.1139,
                 cohesion_rough_mpa=3.225, cohesion_smooth_mpa=0.0),
}


PATH_STYLE = {
    "Table 2": dict(color="#202020", linestyle="-", marker="o", linewidth=1.30),
    "BB": dict(color="#D55E00", linestyle="-", marker="^", linewidth=1.15),
    "MC": dict(color="#0072B2", linestyle="--", marker="s", linewidth=1.15),
}

# Last loading-stage treated as the nominal pre-failure branch. These limits
# follow the specimen-specific onset windows used in the Ye validation audit.
PREFailure_LAST_STAGE = {"SWT1": 5, "SWT2": 5, "SWS3": 5, "SWS4": 3}


def set_style() -> None:
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Nimbus Roman", "Times New Roman", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 7.0,
        "axes.titlesize": 7.6,
        "axes.labelsize": 7.2,
        "xtick.labelsize": 6.3,
        "ytick.labelsize": 6.3,
        "legend.fontsize": 6.4,
        "axes.linewidth": 0.65,
        "lines.linewidth": 1.1,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.dpi": 600,
        "savefig.facecolor": "white",
    })


def first_series(raw: pd.DataFrame, candidates: list[tuple[str, float]]) -> pd.Series:
    for name, scale in candidates:
        if name in raw:
            return pd.to_numeric(raw[name], errors="coerce") * scale
    names = ", ".join(name for name, _ in candidates)
    raise KeyError(f"None of the required columns are present: {names}")


def read_end_time(deck: Path) -> float:
    match = re.search(r"^\s*end_time\s*=\s*([0-9.eE+-]+)", deck.read_text(errors="replace"), re.M)
    if not match:
        raise ValueError(f"No end_time found in {deck}")
    return float(match.group(1))


def model_stage_table(sample: str, model_name: str, csv_path: Path, deck: Path) -> pd.DataFrame:
    raw = pd.read_csv(csv_path).sort_values("time").drop_duplicates("time", keep="last")
    raw = raw.reset_index(drop=True)
    raw["time"] = pd.to_numeric(raw["time"], errors="coerce")
    end_time = read_end_time(deck)
    actual_end = float(raw["time"].iloc[-1])
    if actual_end < end_time - 1.0:
        raise RuntimeError(
            f"{sample} {model_name} is incomplete: {actual_end:g}/{end_time:g} s. "
            "The final figure is not produced from partial results."
        )

    schedule_t, schedule_p = gate.parse_schedule(deck)
    stage_t = gate.stage_times(schedule_t, schedule_p, tol_mpa=0.15)
    dt_out = float(np.nanmedian(np.diff(raw["time"]))) if len(raw) > 2 else 0.0
    indices = []
    for time in stage_t:
        if time > actual_end + 2.0 * dt_out:
            raise RuntimeError(f"{sample} {model_name} did not reach the Table 2 stage at {time:g} s")
        available = raw.index[raw["time"] <= min(time, actual_end)]
        if not len(available):
            raise RuntimeError(f"{sample} {model_name}: no output at or before {time:g} s")
        indices.append(int(available[-1]))

    sigma = first_series(raw, gate.MODEL_COLUMNS["sigma_n_MPa"])
    tau = first_series(raw, gate.MODEL_COLUMNS["tau_MPa"])
    ds = first_series(raw, gate.MODEL_COLUMNS["ds_mm"])
    pi = first_series(raw, gate.MODEL_COLUMNS["Pi_MPa"])
    limit_candidates = (
        [("bb_limit_tau_pp", 1.0e-6), ("limit_tau_pp", 1.0e-6)]
        if model_name == "BB"
        else [("mc_limit_tau_pp", 1.0e-6), ("limit_tau_pp", 1.0e-6)]
    )
    strength = first_series(raw, limit_candidates)

    ds_values = np.asarray([float(ds.iloc[i]) for i in indices])
    ds_values -= ds_values[0]
    return pd.DataFrame({
        "sample": sample,
        "series": model_name,
        "stage": np.arange(1, 12),
        "segment": gate.SEGMENTS,
        "Pi_target_MPa": gate.PI_TARGETS,
        "Pi_model_MPa": [float(pi.iloc[i]) for i in indices],
        "stage_time_s": stage_t,
        "sample_time_s": [float(raw["time"].iloc[i]) for i in indices],
        "sigma_n_MPa": [float(sigma.iloc[i]) for i in indices],
        "tau_MPa": [float(tau.iloc[i]) for i in indices],
        "ds_mm": ds_values,
        "strength_limit_MPa": [float(strength.iloc[i]) for i in indices],
        "source_csv": str(csv_path.relative_to(ROOT)),
        "source_deck": str(deck.relative_to(ROOT)),
    })


def experimental_table(sample: str) -> pd.DataFrame:
    table = gate.TABLE2[sample]
    return pd.DataFrame({
        "sample": sample,
        "series": "Table 2",
        "stage": np.arange(1, 12),
        "segment": gate.SEGMENTS,
        "Pi_target_MPa": gate.PI_TARGETS,
        "Pi_model_MPa": gate.PI_TARGETS,
        "stage_time_s": np.nan,
        "sample_time_s": np.nan,
        "sigma_n_MPa": table["sigma_n_MPa"],
        "tau_MPa": table["tau_MPa"],
        "ds_mm": table["ds_mm"],
        "strength_limit_MPa": np.nan,
        "source_csv": "Ye and Ghassemi (2018), Table 2",
        "source_deck": "not applicable",
    })


def collect(case_set: str) -> pd.DataFrame:
    tables = []
    for sample in SAMPLES:
        tables.append(experimental_table(sample))
        for model_name in ("BB", "MC"):
            csv_rel, deck_rel = CASE_SETS[case_set][sample][model_name]
            csv_path, deck = ROOT / csv_rel, ROOT / deck_rel
            if not csv_path.is_file():
                raise FileNotFoundError(f"Missing {case_set} result: {csv_path}")
            if not deck.is_file():
                raise FileNotFoundError(f"Missing {case_set} deck: {deck}")
            tables.append(model_stage_table(sample, model_name, csv_path, deck))
    frame = pd.concat(tables, ignore_index=True)
    if frame.groupby(["sample", "series"]).size().ne(11).any():
        raise AssertionError("Every specimen/series must contain exactly eleven stages")
    return frame


def bb_limits(sample: str, sigma: np.ndarray, case_set: str) -> tuple[np.ndarray, np.ndarray]:
    p = dict(BB_PARAMETERS[sample])
    if case_set == "protocol116" and sample == "SWS4":
        p["jrc"] = 1.19
    s = np.maximum(np.asarray(sigma, dtype=float), 1.0e-6)
    angle = p["phi_peak_base_deg"] + p["jrc"] * np.log10(p["jcs_mpa"] / s)
    peak = p["cohesion_peak_mpa"] + s * np.tan(np.radians(np.clip(angle, 0.0, 85.0)))
    residual = p["cohesion_residual_mpa"] + s * np.tan(np.radians(p["phi_residual_deg"]))
    return peak, residual


def mc_limits(sample: str, sigma: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p = MC_PARAMETERS[sample]
    s = np.asarray(sigma, dtype=float)
    rough = p["cohesion_rough_mpa"] + p["mu_rough"] * s
    smooth = p["cohesion_smooth_mpa"] + p["mu_smooth"] * s
    return rough, smooth


def bb_tangent_slope(sample: str, sigma_mpa: float, case_set: str) -> float:
    """Analytical d(tau)/d(sigma_n') for the nonlinear peak BB envelope."""
    p = dict(BB_PARAMETERS[sample])
    if case_set == "protocol116" and sample == "SWS4":
        p["jrc"] = 1.19
    sigma = max(float(sigma_mpa), 1.0e-6)
    theta_deg = p["phi_peak_base_deg"] + p["jrc"] * math.log10(p["jcs_mpa"] / sigma)
    theta = math.radians(min(max(theta_deg, 0.0), 85.0))
    curvature = math.radians(p["jrc"]) / math.log(10.0)
    return math.tan(theta) - curvature / (math.cos(theta) ** 2)


def linear_fit(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """Return slope, intercept and R-squared for one stress-path branch."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    keep = np.isfinite(x) & np.isfinite(y)
    x, y = x[keep], y[keep]
    if len(x) < 2 or np.ptp(x) <= 1.0e-12:
        return np.nan, np.nan, np.nan
    slope, intercept = np.polyfit(x, y, 1)
    fitted = slope * x + intercept
    ss_res = float(np.sum((y - fitted) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = np.nan if ss_tot <= 1.0e-20 else 1.0 - ss_res / ss_tot
    return float(slope), float(intercept), float(r2)


def path_slope_rows(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sample in SAMPLES:
        last = PREFailure_LAST_STAGE[sample]
        for series in ("Table 2", "BB", "MC"):
            tab = frame.loc[
                frame["sample"].eq(sample) & frame["series"].eq(series)
            ].sort_values("stage")
            pre = tab.loc[tab["stage"].le(last)]
            unload = tab.loc[tab["stage"].ge(7)]
            transition = tab.loc[tab["stage"].isin((last, last + 1))]
            pre_m, pre_b, pre_r2 = linear_fit(pre["sigma_n_MPa"], pre["tau_MPa"])
            un_m, un_b, un_r2 = linear_fit(unload["sigma_n_MPa"], unload["tau_MPa"])
            tr_m, tr_b, _ = linear_fit(transition["sigma_n_MPa"], transition["tau_MPa"])
            rows.append({
                "sample": sample,
                "series": series,
                "pre_failure_last_stage": last,
                "pre_failure_slope": pre_m,
                "pre_failure_intercept_MPa": pre_b,
                "pre_failure_R2": pre_r2,
                "transition_secant_slope": tr_m,
                "transition_intercept_MPa": tr_b,
                "unloading_slope": un_m,
                "unloading_intercept_MPa": un_b,
                "unloading_R2": un_r2,
            })
    return pd.DataFrame(rows)


def envelope_slope_rows(frame: pd.DataFrame, case_set: str) -> pd.DataFrame:
    rows = []
    for sample in SAMPLES:
        last = PREFailure_LAST_STAGE[sample]
        exp = frame.loc[
            frame["sample"].eq(sample)
            & frame["series"].eq("Table 2")
            & frame["stage"].eq(last)
        ].iloc[0]
        sigma_ref = float(exp["sigma_n_MPa"])
        bb_peak_m = bb_tangent_slope(sample, sigma_ref, case_set)
        bb_res_m = math.tan(math.radians(BB_PARAMETERS[sample]["phi_residual_deg"]))
        mc = MC_PARAMETERS[sample]
        rows.append({
            "sample": sample,
            "reference_stage": last,
            "reference_sigma_n_MPa": sigma_ref,
            "BB_peak_tangent_slope": bb_peak_m,
            "BB_peak_equivalent_angle_deg": math.degrees(math.atan(bb_peak_m)),
            "BB_post_weakening_slope": bb_res_m,
            "BB_post_weakening_angle_deg": math.degrees(math.atan(bb_res_m)),
            "MC_rough_slope": mc["mu_rough"],
            "MC_rough_angle_deg": math.degrees(math.atan(mc["mu_rough"])),
            "MC_smooth_slope": mc["mu_smooth"],
            "MC_smooth_angle_deg": math.degrees(math.atan(mc["mu_smooth"])),
        })
    return pd.DataFrame(rows)


def accuracy_rows(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sample in SAMPLES:
        exp = frame.loc[
            frame["sample"].eq(sample) & frame["series"].eq("Table 2")
        ].sort_values("stage")
        for series in ("BB", "MC"):
            model = frame.loc[
                frame["sample"].eq(sample) & frame["series"].eq(series)
            ].sort_values("stage")
            for key, label in (("sigma_n_MPa", "Effective normal stress"),
                               ("tau_MPa", "Shear stress")):
                measured = exp[key].to_numpy(float)
                predicted = model[key].to_numpy(float)
                error = predicted - measured
                span = float(np.ptp(measured))
                rmse = float(np.sqrt(np.mean(error ** 2)))
                rows.append({
                    "sample": sample,
                    "model": series,
                    "quantity": label,
                    "RMSE": rmse,
                    "MAE": float(np.mean(np.abs(error))),
                    "bias_model_minus_Table2": float(np.mean(error)),
                    "nRMSE_pct": np.nan if span <= 0.0 else 100.0 * rmse / span,
                })
    return pd.DataFrame(rows)


def wide_stage_comparison(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sample in SAMPLES:
        series = {
            name: frame.loc[
                frame["sample"].eq(sample) & frame["series"].eq(name)
            ].sort_values("stage").reset_index(drop=True)
            for name in ("Table 2", "BB", "MC")
        }
        for i in range(11):
            exp, bb, mc = series["Table 2"].iloc[i], series["BB"].iloc[i], series["MC"].iloc[i]
            rows.append({
                "sample": sample,
                "stage": int(exp["stage"]),
                "branch": exp["segment"],
                "Pi_MPa": float(exp["Pi_target_MPa"]),
                "sigma_Table2": float(exp["sigma_n_MPa"]),
                "sigma_BB": float(bb["sigma_n_MPa"]),
                "sigma_BB_error": float(bb["sigma_n_MPa"] - exp["sigma_n_MPa"]),
                "sigma_MC": float(mc["sigma_n_MPa"]),
                "sigma_MC_error": float(mc["sigma_n_MPa"] - exp["sigma_n_MPa"]),
                "tau_Table2": float(exp["tau_MPa"]),
                "tau_BB": float(bb["tau_MPa"]),
                "tau_BB_error": float(bb["tau_MPa"] - exp["tau_MPa"]),
                "tau_MC": float(mc["tau_MPa"]),
                "tau_MC_error": float(mc["tau_MPa"] - exp["tau_MPa"]),
            })
    return pd.DataFrame(rows)


def markdown_table(frame: pd.DataFrame, formats: dict[str, str] | None = None) -> str:
    formats = formats or {}
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for _, row in frame.iterrows():
        values = []
        for column in columns:
            value = row[column]
            if pd.isna(value):
                values.append("--")
            elif column in formats:
                values.append(format(value, formats[column]))
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_comparison_report(frame: pd.DataFrame, case_set: str, tag: str,
                            output_dir: Path) -> list[Path]:
    stage = wide_stage_comparison(frame)
    accuracy = accuracy_rows(frame)
    path_slopes = path_slope_rows(frame)
    envelope_slopes = envelope_slope_rows(frame, case_set)

    stem = output_dir / f"Figure_Ye2018_Table2_Strength_Paths_{tag}"
    stage_csv = Path(str(stem) + "_comparison.csv")
    accuracy_csv = Path(str(stem) + "_accuracy.csv")
    slope_csv = Path(str(stem) + "_slopes.csv")
    report_md = Path(str(stem) + "_comparison.md")
    stage.to_csv(stage_csv, index=False)
    accuracy.to_csv(accuracy_csv, index=False)
    path_slopes.merge(envelope_slopes, on="sample", how="left").to_csv(slope_csv, index=False)

    status = (
        "This is a legacy-protocol prototype and must not be used as the final "
        "protocol-consistent comparison."
        if case_set == "legacy"
        else "This report uses the eight primary 116 protocol-consistency cases."
    )
    summary = accuracy.copy()
    summary["RMSE"] = summary["RMSE"].round(4)
    summary["MAE"] = summary["MAE"].round(4)
    summary["bias_model_minus_Table2"] = summary["bias_model_minus_Table2"].round(4)
    summary["nRMSE_pct"] = summary["nRMSE_pct"].round(2)
    slope_show = path_slopes[[
        "sample", "series", "pre_failure_last_stage", "pre_failure_slope",
        "pre_failure_R2", "transition_secant_slope", "unloading_slope", "unloading_R2"
    ]].copy()
    for column in slope_show.columns[3:]:
        slope_show[column] = slope_show[column].round(4)
    env_show = envelope_slopes.copy()
    for column in env_show.columns[2:]:
        env_show[column] = env_show[column].round(4)

    stage_show = stage.copy()
    for column in stage_show.columns[4:]:
        stage_show[column] = stage_show[column].round(3)
    report = rf"""# Ye and Ghassemi Table 2 stress-path comparison: {tag}

{status}

## Definitions

All errors are model minus Table 2. RMSE, MAE, and bias use all eleven ordered holds. nRMSE is $100\,\mathrm{{RMSE}}$ divided by the measured range of the relevant specimen and quantity.

The pre-failure and unloading path slopes are ordinary least-squares fits of $\tau=m\sigma_n'+b$ over their stated stages. The transition slope is a two-point secant from the last nominal pre-failure stage to the next loading stage. These are stress-path slopes, not friction coefficients.

The MC envelope slopes equal the stated friction coefficients. The BB peak envelope is nonlinear, so its reported slope is the analytical tangent $\mathrm{{d}}\tau/\mathrm{{d}}\sigma_n'$ evaluated at the Table 2 normal stress of the last nominal pre-failure stage. The BB post-weakening slope is $\tan\phi_r$.

## Accuracy summary

{markdown_table(summary)}

## Stress-path slopes

{markdown_table(slope_show)}

## Strength-envelope slopes

{markdown_table(env_show)}

## Complete stage-by-stage values

Stress values and signed errors are in MPa.

{markdown_table(stage_show)}
"""
    report_md.write_text(report)
    return [stage_csv, accuracy_csv, slope_csv, report_md]


def padded(values: np.ndarray, fraction: float = 0.08) -> tuple[float, float]:
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    low, high = float(finite.min()), float(finite.max())
    span = max(high - low, 1.0)
    return low - fraction * span, high + fraction * span


def style_axis(ax: plt.Axes) -> None:
    ax.grid(color="#D8D8D8", linewidth=0.4, alpha=0.65)
    ax.set_axisbelow(True)
    ax.tick_params(direction="out", length=2.7, width=0.6, pad=1.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5))


def plot_path(ax: plt.Axes, table: pd.DataFrame, norm, cmap) -> None:
    label = str(table["series"].iloc[0])
    st = PATH_STYLE[label]
    x = table["sigma_n_MPa"].to_numpy(float)
    y = table["tau_MPa"].to_numpy(float)
    ax.plot(x, y, color=st["color"], linestyle=st["linestyle"],
            linewidth=st["linewidth"], alpha=0.90, zorder=2)
    ax.scatter(x, y, c=table["Pi_target_MPa"], cmap=cmap, norm=norm,
               marker=st["marker"], s=23, edgecolor=st["color"], linewidth=0.75,
               zorder=4)
    # Label only the experimental initial, peak, and final holds. Repeating
    # these labels on both model paths makes the clustered stages unreadable.
    if label == "Table 2":
        for idx, text_value in ((0, "8 L"), (5, "28"), (10, "8 U")):
            ax.annotate(text_value, (x[idx], y[idx]), xytext=(3, 3),
                        textcoords="offset points", fontsize=5.8, color=st["color"])


def add_envelopes(ax: plt.Axes, sample: str, xlim: tuple[float, float], case_set: str) -> None:
    grid = np.linspace(max(0.25, xlim[0]), xlim[1], 300)
    bb_peak, bb_residual = bb_limits(sample, grid, case_set)
    mc_rough, mc_smooth = mc_limits(sample, grid)
    ax.plot(grid, bb_peak, color=PATH_STYLE["BB"]["color"], linestyle=":",
            linewidth=0.90, alpha=0.85)
    ax.plot(grid, bb_residual, color=PATH_STYLE["BB"]["color"], linestyle="-.",
            linewidth=0.80, alpha=0.60)
    ax.plot(grid, mc_rough, color=PATH_STYLE["MC"]["color"], linestyle=":",
            linewidth=0.90, alpha=0.85)
    ax.plot(grid, mc_smooth, color=PATH_STYLE["MC"]["color"], linestyle="-.",
            linewidth=0.80, alpha=0.60)


def add_slope_box(ax: plt.Axes, sample: str, frame: pd.DataFrame, case_set: str) -> None:
    path = path_slope_rows(frame)
    measured = path.loc[
        path["sample"].eq(sample) & path["series"].eq("Table 2")
    ].iloc[0]
    env = envelope_slope_rows(frame, case_set).loc[
        lambda table: table["sample"].eq(sample)
    ].iloc[0]
    text = (
        "Slopes, $m=\\mathrm{d}\\tau/\\mathrm{d}\\sigma_n'$\n"
        f"Table 2: pre {measured['pre_failure_slope']:.2f}; unload {measured['unloading_slope']:.2f}\n"
        f"BB: peak tangent {env['BB_peak_tangent_slope']:.2f}; residual {env['BB_post_weakening_slope']:.2f}\n"
        f"MC: rough {env['MC_rough_slope']:.2f}; smooth {env['MC_smooth_slope']:.2f}"
    )
    ax.text(0.025, 0.965, text, transform=ax.transAxes, ha="left", va="top",
            fontsize=5.4, linespacing=1.18,
            bbox={"facecolor": "white", "edgecolor": "#B8B8B8",
                  "linewidth": 0.45, "alpha": 0.88, "pad": 2.2}, zorder=8)


def strength_panel(ax: plt.Axes, sample: str, frame: pd.DataFrame, case_set: str,
                   norm, cmap, panel: str) -> None:
    sub = frame.loc[frame["sample"].eq(sample)]
    xlim = padded(sub["sigma_n_MPa"].to_numpy(float), 0.10)
    add_envelopes(ax, sample, xlim, case_set)
    for series in ("Table 2", "BB", "MC"):
        plot_path(ax, sub.loc[sub["series"].eq(series)], norm, cmap)
    ax.set_xlim(*xlim)
    y_all = []
    for line in ax.lines:
        y_all.extend(np.asarray(line.get_ydata(), dtype=float))
    ax.set_ylim(*padded(np.asarray(y_all), 0.08))
    ax.set_xlabel(r"Effective normal stress, $\sigma_n'$ (MPa)")
    ax.set_ylabel(r"Shear stress, $\tau$ (MPa)")
    ax.set_title(f"({panel}) {DISPLAY[sample]}", loc="left", fontweight="bold")
    style_axis(ax)
    add_slope_box(ax, sample, frame, case_set)


def common_legend(figure: plt.Figure, y: float) -> None:
    handles = [
        Line2D([], [], color=PATH_STYLE[name]["color"],
               linestyle=PATH_STYLE[name]["linestyle"], marker=PATH_STYLE[name]["marker"],
               markerfacecolor="white", markersize=4.2, linewidth=1.2, label=name)
        for name in ("Table 2", "BB", "MC")
    ]
    handles.extend([
        Line2D([], [], color=PATH_STYLE["BB"]["color"], linestyle=":", label="BB initial limit"),
        Line2D([], [], color=PATH_STYLE["BB"]["color"], linestyle="-.", label="BB post-weakening limit"),
        Line2D([], [], color=PATH_STYLE["MC"]["color"], linestyle=":", label="MC rough limit"),
        Line2D([], [], color=PATH_STYLE["MC"]["color"], linestyle="-.", label="MC smooth limit"),
    ])
    figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.47, y),
                  ncol=4, frameon=False, columnspacing=1.3, handlelength=2.4)


def add_status(figure: plt.Figure, case_set: str) -> None:
    if case_set == "legacy":
        figure.text(0.5, 0.008, "LEGACY-PROTOCOL PROTOTYPE — NOT THE FINAL 116 VALIDATION",
                    ha="center", va="bottom", color="#9B1C1C", fontsize=7.0,
                    fontweight="bold")


def plot_main(frame: pd.DataFrame, case_set: str) -> plt.Figure:
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.65))
    norm = matplotlib.colors.Normalize(vmin=8.0, vmax=28.0)
    cmap = matplotlib.colormaps["viridis"]
    for panel, sample, ax in zip("abcd", SAMPLES, axes.flat):
        strength_panel(ax, sample, frame, case_set, norm, cmap, panel)
    common_legend(fig, 0.995)
    sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(sm, ax=axes, fraction=0.025, pad=0.025)
    cbar.set_label("Injection pressure (MPa)")
    cbar.set_ticks((8, 12, 16, 20, 24, 28))
    fig.subplots_adjust(left=0.085, right=0.895, bottom=0.09, top=0.885,
                        wspace=0.30, hspace=0.34)
    add_status(fig, case_set)
    return fig


def plot_kalantar_style(frame: pd.DataFrame, case_set: str) -> plt.Figure:
    fig, axes = plt.subplots(4, 2, figsize=(7.2, 9.2))
    norm = matplotlib.colors.Normalize(vmin=8.0, vmax=28.0)
    cmap = matplotlib.colormaps["viridis"]
    letters = iter("abcdefgh")
    for row, sample in enumerate(SAMPLES):
        sub = frame.loc[frame["sample"].eq(sample)]
        left = axes[row, 0]
        for series in ("Table 2", "BB", "MC"):
            tab = sub.loc[sub["series"].eq(series)]
            st = PATH_STYLE[series]
            left.plot(tab["ds_mm"], tab["tau_MPa"], color=st["color"],
                      linestyle=st["linestyle"], linewidth=st["linewidth"])
            left.scatter(tab["ds_mm"], tab["tau_MPa"], c=tab["Pi_target_MPa"],
                         cmap=cmap, norm=norm, marker=st["marker"], s=21,
                         edgecolor=st["color"], linewidth=0.7, zorder=4)
        left.set_xlabel("Cumulative shear displacement (mm)")
        left.set_ylabel(r"Shear stress, $\tau$ (MPa)")
        left.set_title(f"({next(letters)}) {DISPLAY[sample]} response", loc="left", fontweight="bold")
        style_axis(left)
        strength_panel(axes[row, 1], sample, frame, case_set, norm, cmap, next(letters))
    common_legend(fig, 0.997)
    sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(sm, ax=axes, fraction=0.017, pad=0.018)
    cbar.set_label("Injection pressure (MPa)")
    cbar.set_ticks((8, 12, 16, 20, 24, 28))
    fig.subplots_adjust(left=0.09, right=0.90, bottom=0.06, top=0.92,
                        wspace=0.30, hspace=0.43)
    add_status(fig, case_set)
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-set", choices=tuple(CASE_SETS), default="protocol116")
    parser.add_argument("--allow-legacy", action="store_true",
                        help="required acknowledgement when plotting legacy cases")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    if args.case_set == "legacy" and not args.allow_legacy:
        raise SystemExit("Legacy plotting requires --allow-legacy; it is not the final validation dataset")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    set_style()
    frame = collect(args.case_set)
    tag = "Protocol116" if args.case_set == "protocol116" else "Legacy_Prototype"

    outputs = []
    for base, figure in (
        (f"Figure_Ye2018_Table2_Strength_Paths_{tag}", plot_main(frame, args.case_set)),
        (f"Figure_Ye2018_Table2_Kalantar_Style_{tag}", plot_kalantar_style(frame, args.case_set)),
    ):
        for suffix in ("pdf", "png"):
            path = args.output_dir / f"{base}.{suffix}"
            figure.savefig(path, dpi=600 if suffix == "png" else None)
            outputs.append(path)
        plt.close(figure)

    data_path = args.output_dir / f"Figure_Ye2018_Table2_Strength_Paths_{tag}_data.csv"
    frame.to_csv(data_path, index=False)
    outputs.append(data_path)
    outputs.extend(write_comparison_report(frame, args.case_set, tag, args.output_dir))
    for path in outputs:
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Output was not created correctly: {path}")
        print(path)


if __name__ == "__main__":
    main()
