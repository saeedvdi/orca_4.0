#!/usr/bin/env python3
"""Score the 112--115 paper-strengthening runs after they complete.

The loading-only selections are made programmatically before unloading scores
are read into the selection table, preventing accidental unloading-data leakage.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path("/home/geomechanics/Documents/ChatGPT/Orca_4.0")
ORCA = Path("/media/geomechanics/Data4TB/projects/orca_4.0")
YG = ORCA / "Examples/YeGhasemmi2018"
GATE_PATH = ORCA / "scripts/table2_gate.py"
RUN_REL = Path("proposed_inputs/paper_compelling_20260902")
COMMON_RESULTS = YG / "SWS4/proposed_inputs/results/results_csv"


CASES = {
    "109_01_sw4_floor1nm_g028_ppfix": ("SWS4", "control", "base"),
    "110_01_sw3_floor1nm_g040_ppfix": ("SWS3", "control", "base"),
    "111_01_swt1_floor1nm_control_ppfix": ("SWT1", "control", "base"),
    "111_03_swt2_floor1nm_control_ppfix": ("SWT2", "control", "base"),
    "112_01_swt1_dt0375_ppfix": ("SWT1", "time step / 2", "robustness"),
    "112_02_swt1_eta200gpa_s_ppfix": ("SWT1", "viscosity / 2", "robustness"),
    "112_03_sw4_dt075_ppfix": ("SWS4", "time step / 2", "robustness"),
    "112_04_sw4_mesh3_ppfix": ("SWS4", "nominal size-3 mesh", "robustness"),
    "113_01_sw3_dscale0304_ppfix": ("SWS3", "dilation -20%", "identifiability"),
    "113_02_sw3_dscale0456_ppfix": ("SWS3", "dilation +20%", "identifiability"),
    "113_03_sw3_gouge032_ppfix": ("SWS3", "gouge loss -20%", "identifiability"),
    "113_04_sw3_gouge048_ppfix": ("SWS3", "gouge loss +20%", "identifiability"),
    "113_05_sw3_closure096_ppfix": ("SWS3", "hydraulic closure -20%", "identifiability"),
    "113_06_sw3_closure144_ppfix": ("SWS3", "hydraulic closure +20%", "identifiability"),
    "114_01_swt2_ascale01416_ppfix": ("SWT2", "aperture scale -20%", "prediction"),
    "114_02_swt2_ascale02124_ppfix": ("SWT2", "aperture scale +20%", "prediction"),
    "115_01_swt1_extended_depressurization_ppfix": (
        "SWT1", "extended post-slip depressurization", "closure diagnostic"
    ),
    "115_02_swt2_extended_depressurization_ppfix": (
        "SWT2", "extended post-slip depressurization", "closure diagnostic"
    ),
    "115_03_sws3_extended_depressurization_ppfix": (
        "SWS3", "extended post-slip depressurization", "closure diagnostic"
    ),
    "115_04_sws4_extended_depressurization_ppfix": (
        "SWS4", "extended post-slip depressurization", "closure diagnostic"
    ),
}

BASE = {
    "SWT1": "111_01_swt1_floor1nm_control_ppfix",
    "SWT2": "111_03_swt2_floor1nm_control_ppfix",
    "SWS3": "110_01_sw3_floor1nm_g040_ppfix",
    "SWS4": "109_01_sw4_floor1nm_g028_ppfix",
}

SWS3_SELECTION = (
    BASE["SWS3"],
    "113_01_sw3_dscale0304_ppfix",
    "113_02_sw3_dscale0456_ppfix",
    "113_03_sw3_gouge032_ppfix",
    "113_04_sw3_gouge048_ppfix",
    "113_05_sw3_closure096_ppfix",
    "113_06_sw3_closure144_ppfix",
)
SWT2_SELECTION = (
    BASE["SWT2"],
    "114_01_swt2_ascale01416_ppfix",
    "114_02_swt2_ascale02124_ppfix",
)


def load_gate():
    spec = importlib.util.spec_from_file_location("table2_gate_compelling", GATE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


GATE = load_gate()


def csv_path(stem: str, sample: str) -> Path:
    if stem == "109_01_sw4_floor1nm_g028_ppfix":
        return YG / "SWS4/proposed_inputs/paper_revision_20260901_followup/csv" / f"{stem}.csv"
    if stem in {"110_01_sw3_floor1nm_g040_ppfix", "111_01_swt1_floor1nm_control_ppfix",
                "111_03_swt2_floor1nm_control_ppfix"}:
        return COMMON_RESULTS / f"{stem}.csv"
    return YG / sample / RUN_REL / "csv" / f"{stem}.csv"


def deck_path(stem: str, sample: str) -> Path:
    return YG / sample / "proposed_inputs" / f"{stem}.i"


def split_nrmse(result: dict, key: str, start: int, stop: int) -> float:
    subset = result["table"].iloc[start:stop]
    if result["datum"] == "stage1" and key in ("dn_mm", "ds_mm") and start == 0:
        subset = subset.iloc[1:]
    error = subset[f"{key}_err"].dropna().to_numpy(dtype=float)
    paper_range = float(np.ptp(GATE.TABLE2[result["sample"]][key]))
    if error.size == 0 or paper_range <= 0:
        return float("nan")
    return 100.0 * float(np.sqrt(np.mean(error**2))) / paper_range


def score_all() -> tuple[pd.DataFrame, dict[str, dict]]:
    missing = []
    for stem, (sample, _, _) in CASES.items():
        if not csv_path(stem, sample).exists():
            missing.append(str(csv_path(stem, sample)))
    if missing:
        raise SystemExit("Missing completed CSV files:\n" + "\n".join(missing))

    deck_map = {stem: deck_path(stem, sample) for stem, (sample, _, _) in CASES.items()}
    GATE.find_deck = lambda path, tag: deck_map[path.stem]

    rows = []
    scored: dict[str, dict] = {}
    for stem, (sample, label, family) in CASES.items():
        path = csv_path(stem, sample)
        result = GATE.score_run(path, sample, None, 0.15, "stage1", 55.0, "kinematic")
        scored[stem] = result
        full = GATE.normalised_scores(result)
        table = result["table"]
        initial, peak, final = table.iloc[0], table.iloc[5], table.iloc[10]
        k0 = float(initial["k_1e12_m2_model"])
        row = {
            "stem": stem,
            "sample": sample,
            "label": label,
            "family": family,
            "rows": len(pd.read_csv(path)),
            "stages_reached": result["reached"],
            "peak_permeability_1e12_m2": float(peak["k_1e12_m2_model"]),
            "final_permeability_1e12_m2": float(final["k_1e12_m2_model"]),
            "peak_ratio": float(peak["k_1e12_m2_model"] / k0),
            "final_ratio": float(final["k_1e12_m2_model"] / k0),
            "full_flow_nRMSE_percent": full["Q_ml_min"],
            "loading_flow_nRMSE_percent": split_nrmse(result, "Q_ml_min", 0, 6),
            "unloading_flow_nRMSE_percent": split_nrmse(result, "Q_ml_min", 6, 11),
            "full_five_channel_mean_nRMSE_percent": full["mean"],
        }
        for key in ("sigma_n_MPa", "tau_MPa", "dn_mm", "ds_mm"):
            row[f"loading_{key}_nRMSE_percent"] = split_nrmse(result, key, 0, 6)
            row[f"unloading_{key}_nRMSE_percent"] = split_nrmse(result, key, 6, 11)
        rows.append(row)
    return pd.DataFrame(rows), scored


def robustness(summary: pd.DataFrame, scored: dict[str, dict]) -> pd.DataFrame:
    records = []
    for stem in summary.loc[summary["family"] == "robustness", "stem"]:
        sample = CASES[stem][0]
        base_stem = BASE[sample]
        test = scored[stem]["table"]
        base = scored[base_stem]["table"]
        record = {"sample": sample, "stem": stem, "label": CASES[stem][1], "base": base_stem}
        for key in ("Q_ml_min_model", "k_1e12_m2_model", "sigma_n_MPa_model", "tau_MPa_model",
                    "dn_mm_model", "ds_mm_model"):
            delta = (test[key] - base[key]).abs()
            scale = max(float(base[key].abs().max()), 1.0e-12)
            record[f"max_abs_delta_{key}"] = float(delta.max())
            record[f"max_delta_percent_of_base_max_{key}"] = 100.0 * float(delta.max()) / scale
        test_row = summary.loc[summary["stem"] == stem].iloc[0]
        base_row = summary.loc[summary["stem"] == base_stem].iloc[0]
        record["delta_peak_ratio_percent"] = 100.0 * (test_row["peak_ratio"] / base_row["peak_ratio"] - 1.0)
        record["delta_final_ratio_percent"] = 100.0 * (test_row["final_ratio"] / base_row["final_ratio"] - 1.0)
        record["delta_flow_nRMSE_percentage_points"] = (
            test_row["full_flow_nRMSE_percent"] - base_row["full_flow_nRMSE_percent"]
        )
        records.append(record)
    return pd.DataFrame(records)


def loading_only_selection(summary: pd.DataFrame, stems: tuple[str, ...], test_name: str) -> pd.DataFrame:
    candidates = summary.set_index("stem").loc[list(stems)].reset_index()
    # Selection sees only the loading score.
    selected_stem = str(candidates.loc[candidates["loading_flow_nRMSE_percent"].idxmin(), "stem"])
    candidates["selected_from_loading_only"] = candidates["stem"].eq(selected_stem)
    candidates.insert(0, "test", test_name)
    return candidates[[
        "test", "sample", "stem", "label", "loading_flow_nRMSE_percent",
        "selected_from_loading_only", "unloading_flow_nRMSE_percent", "full_flow_nRMSE_percent",
        "peak_ratio", "final_ratio",
    ]]


def extended_depressurization() -> pd.DataFrame:
    cases = {
        "SWT1": ("115_01_swt1_extended_depressurization_ppfix", 3700.0, 4100.0, 4500.0),
        "SWT2": ("115_02_swt2_extended_depressurization_ppfix", 3052.5, 3452.5, 3852.5),
        "SWS3": ("115_03_sws3_extended_depressurization_ppfix", 5002.4, 5402.4, 5802.4),
        "SWS4": ("115_04_sws4_extended_depressurization_ppfix", 3700.0, 4100.0, 4500.0),
    }
    rows = []
    for sample, (stem, high_time, mid_time, low_time) in cases.items():
        raw = pd.read_csv(csv_path(stem, sample)).sort_values("time").drop_duplicates("time", keep="last")
        for pressure_fraction, target in ((1.0, high_time), (0.5, mid_time), (0.15, low_time)):
            index = int((raw["time"] - target).abs().idxmin())
            point = raw.loc[index]
            rows.append({
                "sample": sample,
                "stem": stem,
                "pressure_difference_fraction": pressure_fraction,
                "target_time_s": target,
                "sample_time_s": float(point["time"]),
                "injection_pressure_MPa": float(point["injection_pressure_pp"]) / 1.0e6,
                "effective_normal_compression_MPa": float(point["effective_normal_compression_mpa_pp"]),
                "normal_stress_aperture_um": float(point["normal_stress_aperture_um_pp"]),
                "hydraulic_aperture_um": float(point["hydraulic_aperture_um_pp"]),
                "permeability_1e12_m2": float(point["fracture_permeability_pp"]) * 1.0e12,
                "cumulative_plastic_slip_mm": float(point["cumulative_plastic_slip_pp"]) * 1.0e3,
                "cumulative_dilation_um": float(point["cumulative_dilation_pp"]) * 1.0e6,
                "gouge_loss_um": float(point["slip_damage_aperture_um_pp"]),
            })
    output = pd.DataFrame(rows)
    for sample in cases:
        mask = output["sample"].eq(sample)
        high = output.loc[mask & output["pressure_difference_fraction"].eq(1.0)].iloc[0]
        output.loc[mask, "permeability_change_from_high_pressure_percent"] = (
            100.0 * (output.loc[mask, "permeability_1e12_m2"] / high["permeability_1e12_m2"] - 1.0)
        )
        output.loc[mask, "plastic_slip_change_from_high_pressure_mm"] = (
            output.loc[mask, "cumulative_plastic_slip_mm"] - high["cumulative_plastic_slip_mm"]
        )
        output.loc[mask, "dilation_change_from_high_pressure_um"] = (
            output.loc[mask, "cumulative_dilation_um"] - high["cumulative_dilation_um"]
        )
        output.loc[mask, "gouge_change_from_high_pressure_um"] = (
            output.loc[mask, "gouge_loss_um"] - high["gouge_loss_um"]
        )
    return output


def main() -> None:
    summary, scored = score_all()
    robust = robustness(summary, scored)
    closure = extended_depressurization()
    selection = pd.concat(
        [
            loading_only_selection(summary, SWS3_SELECTION, "SW-S3 seven-candidate loading selection"),
            loading_only_selection(summary, SWT2_SELECTION, "SW-T2 aperture-scale loading selection"),
        ],
        ignore_index=True,
    )
    summary.to_csv(ROOT / "compelling_matrix_summary.csv", index=False)
    robust.to_csv(ROOT / "compelling_matrix_robustness.csv", index=False)
    selection.to_csv(ROOT / "compelling_matrix_loading_unloading_selection.csv", index=False)
    closure.to_csv(ROOT / "compelling_matrix_extended_depressurization.csv", index=False)

    print("\nLoading-only selections (unloading score revealed after selection):")
    print(selection.loc[selection["selected_from_loading_only"]].to_string(index=False))
    print("\nNumerical robustness:")
    print(robust[["sample", "label", "delta_peak_ratio_percent", "delta_final_ratio_percent",
                  "delta_flow_nRMSE_percentage_points"]].to_string(index=False))
    print("\nExtended post-slip depressurization:")
    print(closure.to_string(index=False))


if __name__ == "__main__":
    main()
