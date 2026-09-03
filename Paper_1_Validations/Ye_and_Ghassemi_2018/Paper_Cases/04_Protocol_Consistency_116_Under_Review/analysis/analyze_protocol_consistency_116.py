#!/usr/bin/env python3
"""Audit the Ye--Ghassemi 116-series protocol-consistency calculations.

This script is analysis-only. It never launches Orca. It samples the existing
CSV files at the eleven Table 2 stages using the same branch-aware rule and
normalised-error definition as scripts/table2_gate.py.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


PRIMARY_CASES = {
    "SWT1": {
        "BB": "116_01_swt1_bb_commonK796_protocol_ppfix",
        "MC": "116_02_swt1_mc_commonK796_protocol_ppfix",
    },
    "SWT2": {
        "BB": "116_03_swt2_bb_theta31_commonK796_protocol_ppfix",
        "MC": "116_04_swt2_mc_theta31_commonK796_protocol_ppfix",
    },
    "SWS3": {
        "BB": "116_05_sws3_bb_fixedpiston_commonK796_protocol_ppfix",
        "MC": "116_06_sws3_mc_fixedpiston_commonK796_protocol_ppfix",
    },
    "SWS4": {
        "BB": "116_07_sws4_bb_jrc1p19_fixedpiston_commonK796_ppfix",
        "MC": "116_08_sws4_mc_fixedpiston_commonK796_protocol_ppfix",
    },
}

CONTROL_CASES = {
    "SWT2": {
        "BB equilibrium-hold": "116_10_swt2_bb_theta31_commonK796_eqhold_ppfix",
        "MC equilibrium-hold": "116_11_swt2_mc_theta31_commonK796_eqhold_ppfix",
    },
    "SWS4": {
        "BB JRC=5 control": "116_09_sws4_bb_jrc5_fixedpiston_commonK796_control",
    },
}


def load_gate(project_root: Path):
    path = project_root / "scripts" / "table2_gate.py"
    spec = importlib.util.spec_from_file_location("orca_table2_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def paths_for(raw_root: Path, sample: str, case: str) -> tuple[Path, Path]:
    deck = raw_root / sample / f"{case}.i"
    csv_path = (
        raw_root / sample / "proposed_inputs" / "protocol_consistency_20260902"
        / "csv" / f"{case}.csv"
    )
    return deck, csv_path


def score_existing(gate, sample: str, model: str, case: str,
                   deck: Path, csv_path: Path) -> tuple[pd.DataFrame, list[dict], dict]:
    schedule_t, schedule_p = gate.parse_schedule(deck)
    stage_t = np.asarray(gate.stage_times(schedule_t, schedule_p, 0.15), dtype=float)
    raw = pd.read_csv(csv_path).sort_values("time").drop_duplicates("time", keep="last")
    raw = raw.reset_index(drop=True)
    t_end = float(raw["time"].iloc[-1])
    # Adaptive stepping can make the whole-run median much smaller than the
    # output interval at the final hold. Use the last 20 rows for the same
    # purpose: distinguish a completed run ending one output interval before
    # the schedule knot from a genuinely truncated calculation.
    tail_time = raw["time"].tail(min(20, len(raw))).to_numpy(float)
    dt_out = float(np.median(np.diff(tail_time))) if len(tail_time) > 2 else 0.0
    grace = 2.0 * dt_out

    columns = dict(gate.MODEL_COLUMNS)
    columns["dn_mm"] = gate.DN_CHANNELS[gate.DEFAULT_DN_CHANNEL]
    converted = pd.DataFrame({"time": pd.to_numeric(raw["time"], errors="coerce")})
    used = {}
    for key, candidates in columns.items():
        series, name = gate.first_column(raw, candidates)
        converted[key] = np.nan if series is None else series
        if name:
            used[key] = name

    indices: list[int | None] = []
    clamped: list[bool] = []
    for target_t in stage_t:
        if target_t > t_end + grace:
            indices.append(None)
            clamped.append(False)
        else:
            eligible = converted.index[converted["time"] <= min(target_t, t_end)]
            indices.append(int(eligible[-1]))
            clamped.append(target_t > t_end)

    table = pd.DataFrame({
        "sample": sample,
        "model": model,
        "case": case,
        "stage": np.arange(1, 12),
        "segment": gate.SEGMENTS,
        "Pi_target_MPa": gate.PI_TARGETS,
        "stage_time_s": stage_t,
        "sample_time_s": [np.nan if i is None else float(converted["time"].iloc[i]) for i in indices],
        "sample_clamped": clamped,
    })
    for key in gate.SCORED + gate.INFORMATIONAL:
        table[f"{key}_experiment"] = gate.TABLE2[sample][key]
        table[f"{key}_model"] = [np.nan if i is None else float(converted[key].iloc[i]) for i in indices]

    for key in ("dn_mm", "ds_mm"):
        datum = table[f"{key}_model"].iloc[0]
        if np.isfinite(datum):
            table[f"{key}_model"] -= datum

    metrics = []
    complete = bool(table["sample_time_s"].notna().all())
    for key in gate.SCORED:
        sub = table.iloc[1:] if key in ("dn_mm", "ds_mm") else table
        err = sub[f"{key}_model"] - sub[f"{key}_experiment"]
        err = err.dropna()
        paper_range = float(np.ptp(gate.TABLE2[sample][key]))
        rmse = float(np.sqrt(np.mean(np.square(err)))) if len(err) else np.nan
        metrics.append({
            "sample": sample,
            "model": model,
            "case": case,
            "observable": key,
            "stages_scored": int(len(err)),
            "rmse": rmse,
            "nRMSE_percent": 100.0 * rmse / paper_range if paper_range > 0 and len(err) else np.nan,
            "complete_11_stages": complete,
        })
    if complete:
        mean_five = float(np.mean([row["nRMSE_percent"] for row in metrics]))
    else:
        mean_five = np.nan
    metrics.append({
        "sample": sample,
        "model": model,
        "case": case,
        "observable": "mean_of_five",
        "stages_scored": 11 if complete else int(table["sample_time_s"].notna().sum()),
        "rmse": np.nan,
        "nRMSE_percent": mean_five,
        "complete_11_stages": complete,
    })

    reaction = pd.to_numeric(raw.get("reaction_vs_machine_spring_mpa_pp"), errors="coerce")
    command = pd.to_numeric(raw.get("axial_command_m_pp"), errors="coerce")
    after55 = raw["time"] >= 55.0
    health = {
        "sample": sample,
        "model": model,
        "case": case,
        "rows": len(raw),
        "final_time_s": t_end,
        "last_table2_time_s": float(stage_t[-1]),
        "remaining_to_last_stage_s": max(0.0, float(stage_t[-1]) - t_end),
        "stages_reached": int(table["sample_time_s"].notna().sum()),
        "complete_11_stages": complete,
        "post55_command_range_um": (
            float(np.ptp(command[after55].dropna())) * 1.0e6 if command is not None else np.nan
        ),
        "reaction_spring_rmse_MPa": (
            float(np.sqrt(np.mean(np.square(reaction.dropna())))) if reaction is not None else np.nan
        ),
        "reaction_spring_max_abs_MPa": (
            float(np.max(np.abs(reaction.dropna()))) if reaction is not None else np.nan
        ),
        "columns": ";".join(f"{key}={value}" for key, value in sorted(used.items())),
    }
    return table, metrics, health


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path,
                        default=Path("/media/geomechanics/Data4TB/projects/orca_4.0"))
    parser.add_argument("--raw-root", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    raw_root = (args.raw_root or project_root / "Paper_1_Validations" /
                "Ye_and_Ghassemi_2018" / "Protocol_Consistency_116_Raw_Archive").resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    gate = load_gate(project_root)

    cases = []
    for sample, models in PRIMARY_CASES.items():
        cases.extend((sample, model, case, "primary") for model, case in models.items())
    for sample, models in CONTROL_CASES.items():
        cases.extend((sample, model, case, "control") for model, case in models.items())

    stage_tables = []
    metric_rows = []
    health_rows = []
    for sample, model, case, role in cases:
        deck, csv_path = paths_for(raw_root, sample, case)
        if not deck.is_file() or not csv_path.is_file():
            health_rows.append({
                "sample": sample, "model": model, "case": case, "role": role,
                "complete_11_stages": False, "status": "missing deck or CSV",
            })
            continue
        table, metrics, health = score_existing(
            gate, sample, model, case, deck, csv_path
        )
        table.insert(3, "role", role)
        for row in metrics:
            row["role"] = role
        health["role"] = role
        health["status"] = "complete" if health["complete_11_stages"] else "partial"
        stage_tables.append(table)
        metric_rows.extend(metrics)
        health_rows.append(health)

    stages = pd.concat(stage_tables, ignore_index=True) if stage_tables else pd.DataFrame()
    metrics = pd.DataFrame(metric_rows)
    health = pd.DataFrame(health_rows)
    stages.to_csv(output_dir / "protocol_116_stage_values.csv", index=False)
    metrics.to_csv(output_dir / "protocol_116_metrics.csv", index=False)
    health.to_csv(output_dir / "protocol_116_health.csv", index=False)

    primary_means = metrics[(metrics["role"] == "primary") &
                            (metrics["observable"] == "mean_of_five")]
    print(health[["sample", "model", "case", "status", "final_time_s",
                  "last_table2_time_s", "remaining_to_last_stage_s",
                  "stages_reached"]].to_string(index=False))
    print("\nPrimary five-channel nRMSE (%):")
    print(primary_means[["sample", "model", "nRMSE_percent",
                         "complete_11_stages"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
