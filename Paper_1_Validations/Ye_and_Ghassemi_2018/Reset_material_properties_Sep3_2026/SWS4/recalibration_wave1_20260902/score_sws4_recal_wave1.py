#!/usr/bin/env python3
"""Rank SW-S4 Wave-1 peak screens against the first six Table 2 stages."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

import sws4_protocol_consistency_check as common


def find_results(requested: str | None) -> Path:
    candidates = []
    if requested:
        candidates.append(Path(requested).expanduser().resolve())
    candidates.extend([
        HERE / "peak_screen",
        HERE / "csv",
        PARENT / "proposed_inputs" / "sws4_recalibration_wave1_20260902" / "peak_screen",
        PARENT / "proposed_inputs" / "sws4_recalibration_wave1_20260902" / "csv",
    ])
    for candidate in candidates:
        if candidate.is_dir() and any(candidate.glob("117_*.csv")):
            return candidate
    searched = "\n".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"No 117-series CSVs found. Searched:\n{searched}")


def score(results_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    metric_rows = []
    stage_frames = []
    for csv_path in sorted(results_dir.glob("117_*.csv")):
        case = csv_path.stem
        deck = HERE / f"{case}.i"
        schedule_t, schedule_p = common.parse_schedule(deck)
        stage_times = common.table2_stage_times(schedule_t, schedule_p)[:6]
        data = pd.read_csv(csv_path).apply(pd.to_numeric, errors="coerce")
        data = data.sort_values("time").drop_duplicates("time", keep="last")
        if float(data["time"].max()) < stage_times[-1]:
            print(f"Skipping incomplete peak screen {csv_path.name}: "
                  f"t_end={data['time'].max():.1f} < {stage_times[-1]:.1f} s")
            continue

        frame = pd.DataFrame({
            "case": case,
            "stage": np.arange(1, 7),
            "Pi_target_MPa": common.PI_TARGETS[:6],
            "stage_time_s": stage_times,
        })
        scores = []
        for key in ("sigma_n_MPa", "tau_MPa", "dn_mm", "ds_mm"):
            column, scale = common.MODEL_COLUMNS[key]
            values = common._sample_at_or_before(data, stage_times, column) * scale
            if key in {"dn_mm", "ds_mm"}:
                values -= values[0]
                use = slice(1, None)
            else:
                use = slice(None)
            frame[key] = values
            error = values[use] - common.TABLE2[key][:6][use]
            nrmse = 100.0 * np.sqrt(np.mean(error ** 2)) / np.ptp(common.TABLE2[key])
            scores.append(float(nrmse))
            metric_rows.append({"case": case, "observable": key,
                                "nRMSE_percent": float(nrmse)})

        raw_stage1 = common._sample_at_or_before(
            data, stage_times[:1], common.MODEL_COLUMNS["ds_mm"][0]
        )[0]
        relative_slip = data[common.MODEL_COLUMNS["ds_mm"][0]].to_numpy(float) - raw_stage1
        onset_t, onset_p = common._first_crossing(data, relative_slip, 0.001)
        metric_rows.append({
            "case": case,
            "observable": "mechanical_mean",
            "nRMSE_percent": float(np.mean(scores)),
            "onset_time_s": onset_t,
            "onset_pressure_MPa": onset_p,
            "peak_tau_MPa": float(frame["tau_MPa"].iloc[-1]),
            "peak_dn_mm": float(frame["dn_mm"].iloc[-1]),
            "peak_ds_mm": float(frame["ds_mm"].iloc[-1]),
        })
        stage_frames.append(frame)

    if not stage_frames:
        raise RuntimeError("No complete peak-screen CSV was available to score")
    stages = pd.concat(stage_frames, ignore_index=True)
    metrics = pd.DataFrame(metric_rows)
    ranking = metrics.loc[metrics["observable"].eq("mechanical_mean")].copy()
    ranking = ranking.sort_values(["nRMSE_percent", "case"]).reset_index(drop=True)
    return ranking, stages


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", help="Directory containing downloaded 117-series CSVs")
    parser.add_argument("--output", help="Optional ranking CSV path")
    args = parser.parse_args()
    results_dir = find_results(args.results)
    ranking, stages = score(results_dir)
    print(f"Results directory: {results_dir}")
    print(ranking.to_string(index=False, float_format=lambda value: f"{value:.4g}"))
    if args.output:
        output = Path(args.output).expanduser().resolve()
        ranking.to_csv(output, index=False)
        stages.to_csv(output.with_name(output.stem + "_stage_values.csv"), index=False)
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
