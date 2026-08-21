#!/usr/bin/env python3
"""Analyze every available 101-series cyclic and shut-in result.

The 101 decks intentionally replace the paper's monotonic schedule, so they do
not belong in the Table-2 accuracy ranking.  This reader applies the campaign
metrics preregistered in ``doc/DISCUSSION_DECKS_101.md`` and writes three
machine-readable files:

* ``DISCUSSION_101_RUN_INDEX.csv`` -- all 16 decks and completion state;
* ``DISCUSSION_101_CYCLIC_METRICS.csv`` -- values at every mid-hold probe;
* ``DISCUSSION_101_SHUTIN_METRICS.csv`` -- arrest and retained-flow metrics.

Usage:
    python scripts/analyze_101.py
    python scripts/analyze_101.py --output-dir doc/independent_analysis
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from build_101_decks import (
    P_FLOOR,
    SHUTIN_OBSERVE,
    SHUTIN_OBSERVE_SLOW,
    SHUTIN_TAU_FAST,
    SHUTIN_TAU_SLOW,
    SPECS,
    T_SETTLE,
    cyclic_schedule,
    shutin_expression,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "Examples/YeGhasemmi2018"
DEFAULT_OUTPUT = ROOT / "doc/independent_analysis"
SWS4_SETTLING_SLIP_LIMIT_MM = 1.0e-4

DAMAGE = {
    "SWT1": (1.50e-4, 1.40),
    "SWT2": (1.50e-4, 1.40),
    "SWS3": (6.00e-5, 1.40),
    "SWS4": (7.45e-5, 1.10),
}

CYCLIC_COLUMNS = {
    "injection_pressure_mpa": ("injection_pressure_pp", 1.0e-6),
    "hydraulic_aperture_um": ("hydraulic_aperture_um_pp", 1.0),
    "flow_ml_min": ("flow_rate_validation_ml_min_pp", 1.0),
    "permeability_1e13_m2": ("fracture_permeability_1e13_m2_pp", 1.0),
    "shear_slip_mm": ("reported_czm_shear_slip_mm_pp", 1.0),
    "normal_dilation_mm": ("czm_normal_dilation_paper_mm_pp", 1.0),
    "effective_normal_mpa": ("effective_normal_paper_frame_mpa_pp", 1.0),
    "dilation_angle_deg": ("bb_dilation_angle_pp", 1.0),
    "slip_damage_aperture_um": ("slip_damage_aperture_um_pp", 1.0),
    "cumulative_plastic_slip_m": ("cumulative_plastic_slip_pp", 1.0),
    "strength_margin_mpa": ("strength_margin_mpa_pp", 1.0),
}


@dataclass(frozen=True)
class Case:
    sample: str
    stem: str
    group: str
    design: str
    kind: str
    peaks: tuple[float, ...] = ()
    hold: float = 0.0
    tau: float = 0.0
    observe: float = 0.0

    @property
    def csv_path(self) -> Path:
        return (
            EXAMPLES / self.sample / "results_csv_hpc_rorqual" /
            f"{self.stem}_hpc.csv"
        )


def cases() -> list[Case]:
    items: list[Case] = []
    for sample, number in (("SWT1", 1), ("SWT2", 2), ("SWS3", 3), ("SWS4", 4)):
        peak = SPECS[sample][2]
        items.append(Case(sample, f"101_{number:02d}_{sample.lower().replace('sws', 'sw')}_cyclic3_eq",
                          "A", "equal-peak 3-cycle", "cyclic", (peak, peak, peak)))
    for sample, number in (("SWT1", 5), ("SWT2", 6), ("SWS3", 7), ("SWS4", 8)):
        peak = SPECS[sample][2]
        items.append(Case(sample, f"101_{number:02d}_{sample.lower().replace('sws', 'sw')}_cyclic3_esc",
                          "B", "escalating-peak 3-cycle", "cyclic",
                          (peak - 4.0, peak - 2.0, peak)))
    for sample, number in (("SWT1", 9), ("SWT2", 10), ("SWS3", 11), ("SWS4", 12)):
        items.append(Case(sample, f"101_{number:02d}_{sample.lower().replace('sws', 'sw')}_shutin_nohold",
                          "C", "shut-in, no hold, tau=150 s", "shutin",
                          hold=0.0, tau=SHUTIN_TAU_FAST, observe=SHUTIN_OBSERVE))
    items.extend([
        Case("SWT1", "101_13_swt1_shutin_slowtau", "D",
             "shut-in, 200 s hold, tau=1500 s", "shutin",
             hold=200.0, tau=SHUTIN_TAU_SLOW, observe=SHUTIN_OBSERVE_SLOW),
        Case("SWS4", "101_14_sw4_shutin_slowtau", "D",
             "shut-in, 200 s hold, tau=1500 s", "shutin",
             hold=200.0, tau=SHUTIN_TAU_SLOW, observe=SHUTIN_OBSERVE_SLOW),
        Case("SWT1", "101_15_swt1_cyclic2_frame2x", "E",
             "equal-peak 2-cycle, frame 2x", "cyclic",
             (SPECS["SWT1"][2],) * 2),
        Case("SWT1", "101_16_swt1_cyclic2_frame0p5x", "E",
             "equal-peak 2-cycle, frame 0.5x", "cyclic",
             (SPECS["SWT1"][2],) * 2),
    ])
    return items


def expected(case: Case) -> tuple[float, list[tuple[str, int, float]], float | None]:
    _, ambient, peak, time_to_peak = SPECS[case.sample]
    start = T_SETTLE[case.sample]
    if case.group == "E":
        start = 2.0
    ramp_rate = (peak - ambient) / (time_to_peak - 2.0)
    if case.kind == "cyclic":
        _, _, end, probes = cyclic_schedule(ambient, list(case.peaks), ramp_rate, start)
        return end, probes, None
    _, t_shut, end = shutin_expression(
        ambient, peak, time_to_peak - 2.0, start, case.hold, case.tau, case.observe
    )
    return end, [], t_shut


def load(case: Case) -> pd.DataFrame:
    frame = pd.read_csv(case.csv_path)
    required = {"time", *[name for name, _ in CYCLIC_COLUMNS.values()],
                "slip_rate_mm_per_s_pp"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{case.csv_path}: missing columns {missing}")
    frame = frame.sort_values("time").drop_duplicates("time", keep="last").reset_index(drop=True)
    return frame


def nearest_index(frame: pd.DataFrame, time: float) -> int:
    values = frame["time"].to_numpy(float)
    pos = int(np.searchsorted(values, time))
    candidates = [p for p in (pos - 1, pos) if 0 <= p < len(values)]
    return min(candidates, key=lambda p: abs(values[p] - time))


def value(row: pd.Series, output_name: str) -> float:
    source, scale = CYCLIC_COLUMNS[output_name]
    return float(row[source]) * scale


def completion(frame: pd.DataFrame, expected_end: float) -> tuple[str, float, float]:
    end = float(frame["time"].iloc[-1])
    dt = float(np.median(np.diff(frame["time"]))) if len(frame) > 2 else 0.0
    complete = end >= expected_end - 2.0 * dt
    return ("complete" if complete else "partial"), end, expected_end


def validity(case: Case, frame: pd.DataFrame, run_status: str) -> tuple[str, float | None]:
    """Apply the preregistered SW-S4 pre-injection falsifier."""
    if run_status != "complete":
        return "partial_run", None
    if case.sample != "SWS4":
        return "valid", None
    idx = nearest_index(frame, T_SETTLE["SWS4"])
    slip = float(frame.iloc[idx][CYCLIC_COLUMNS["shear_slip_mm"][0]])
    if abs(slip) > SWS4_SETTLING_SLIP_LIMIT_MM:
        return "qualified_failed_pre_injection_falsifier", slip
    return "valid", slip


def analyze_cyclic(case: Case, frame: pd.DataFrame) -> list[dict]:
    expected_end, probes, _ = expected(case)
    status, run_end, _ = completion(frame, expected_end)
    rows: list[dict] = []
    dc, exponent = DAMAGE[case.sample]
    for hold, cycle, probe_time in probes:
        idx = nearest_index(frame, probe_time)
        source = frame.iloc[idx]
        row = {
            "sample": case.sample,
            "case": case.stem,
            "group": case.group,
            "design": case.design,
            "run_status": status,
            "run_end_s": run_end,
            "expected_end_s": expected_end,
            "hold": hold.replace(" ", "_"),
            "cycle": cycle,
            "probe_time_s": probe_time,
            "sample_time_s": float(source["time"]),
        }
        for output_name in CYCLIC_COLUMNS:
            row[output_name] = value(source, output_name)
        slip = max(row["cumulative_plastic_slip_m"], 0.0)
        row["weakening_state_w"] = math.exp(-((slip / dc) ** exponent))
        rows.append(row)

    # Matched-hold changes relative to cycle 1.  Deltas are used for signed
    # kinematic channels; ratios are used for positive hydraulic channels.
    for row in rows:
        if row["cycle"] <= 0:
            continue
        reference = next(
            r for r in rows if r["hold"] == row["hold"] and r["cycle"] == 1
        )
        for key in ("hydraulic_aperture_um", "flow_ml_min", "permeability_1e13_m2"):
            denominator = reference[key]
            row[key + "_ratio_to_cycle1"] = (
                row[key] / denominator if abs(denominator) > 1.0e-30 else np.nan
            )
        for key in ("shear_slip_mm", "normal_dilation_mm"):
            row[key + "_change_from_cycle1"] = row[key] - reference[key]
    return rows


def analyze_shutin(case: Case, frame: pd.DataFrame) -> dict:
    expected_end, _, t_shut = expected(case)
    assert t_shut is not None
    status, run_end, _ = completion(frame, expected_end)
    i_shut = nearest_index(frame, t_shut)
    at_shut = frame.iloc[i_shut]
    after = frame.iloc[i_shut:].copy()
    end = frame.iloc[-1]

    slip_column = CYCLIC_COLUMNS["shear_slip_mm"][0]
    rate_column = "slip_rate_mm_per_s_pp"
    max_slip_idx = int(after[slip_column].idxmax())
    max_rate_idx = int(after[rate_column].idxmax())
    global_rate_idx = int(frame[rate_column].idxmax())

    # Match the end-state effective normal stress on the initial loading ramp.
    # Exclude t=0 initialisation rows, and stop at shut-in so the match cannot
    # select the later unloading branch itself.
    start = T_SETTLE[case.sample]
    loading = frame[(frame["time"] >= start) & (frame["time"] <= t_shut)].copy()
    sigma_column = CYCLIC_COLUMNS["effective_normal_mpa"][0]
    target_sigma = float(end[sigma_column])
    match_idx = int((loading[sigma_column] - target_sigma).abs().idxmin())
    matched = frame.loc[match_idx]

    def scaled(source: pd.Series, name: str) -> float:
        return value(source, name)

    slip_shut = scaled(at_shut, "shear_slip_mm")
    slip_max = float(frame.loc[max_slip_idx, slip_column])
    slip_end = scaled(end, "shear_slip_mm")
    aperture_match = scaled(matched, "hydraulic_aperture_um")
    aperture_end = scaled(end, "hydraulic_aperture_um")
    perm_match = scaled(matched, "permeability_1e13_m2")
    perm_end = scaled(end, "permeability_1e13_m2")
    post_rate_lag = float(frame.loc[max_rate_idx, "time"] - t_shut)
    if abs(post_rate_lag) < 1.0e-6:
        post_rate_lag = 0.0
    return {
        "sample": case.sample,
        "case": case.stem,
        "group": case.group,
        "design": case.design,
        "run_status": status,
        "run_end_s": run_end,
        "expected_end_s": expected_end,
        "shutin_time_s": t_shut,
        "sampled_shutin_time_s": float(at_shut["time"]),
        "slip_at_shutin_mm": slip_shut,
        "maximum_post_shutin_slip_mm": slip_max,
        "maximum_post_shutin_slip_time_s": float(frame.loc[max_slip_idx, "time"]),
        "maximum_post_shutin_growth_mm": slip_max - slip_shut,
        "net_slip_to_end_mm": slip_end - slip_shut,
        "maximum_post_shutin_rate_mm_s": float(frame.loc[max_rate_idx, rate_column]),
        "maximum_post_shutin_rate_lag_s": post_rate_lag,
        "global_maximum_rate_mm_s": float(frame.loc[global_rate_idx, rate_column]),
        "global_maximum_rate_lag_from_shutin_s": float(frame.loc[global_rate_idx, "time"] - t_shut),
        "end_injection_pressure_mpa": scaled(end, "injection_pressure_mpa"),
        "end_effective_normal_mpa": target_sigma,
        "matched_loading_time_s": float(matched["time"]),
        "matched_loading_effective_normal_mpa": float(matched[sigma_column]),
        "matched_loading_aperture_um": aperture_match,
        "end_aperture_um": aperture_end,
        "end_to_matched_aperture_ratio": aperture_end / aperture_match,
        "matched_loading_permeability_1e13_m2": perm_match,
        "end_permeability_1e13_m2": perm_end,
        "end_to_matched_permeability_ratio": perm_end / perm_match,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)

    index_rows: list[dict] = []
    cyclic_rows: list[dict] = []
    shutin_rows: list[dict] = []
    for case in cases():
        expected_end, _, _ = expected(case)
        if not case.csv_path.is_file():
            index_rows.append({
                "sample": case.sample, "case": case.stem, "group": case.group,
                "design": case.design, "result_status": "missing", "run_status": "not_run",
                "analysis_status": "missing_result",
                "pre_injection_slip_at_800s_mm": np.nan,
                "run_end_s": np.nan, "expected_end_s": expected_end,
                "source_csv": str(case.csv_path.relative_to(ROOT)),
            })
            continue
        frame = load(case)
        status, run_end, _ = completion(frame, expected_end)
        analysis_status, settling_slip = validity(case, frame, status)
        index_rows.append({
            "sample": case.sample, "case": case.stem, "group": case.group,
            "design": case.design, "result_status": "present", "run_status": status,
            "analysis_status": analysis_status,
            "pre_injection_slip_at_800s_mm": settling_slip,
            "run_end_s": run_end, "expected_end_s": expected_end,
            "source_csv": str(case.csv_path.relative_to(ROOT)),
        })
        if case.kind == "cyclic":
            rows = analyze_cyclic(case, frame)
            for row in rows:
                row["analysis_status"] = analysis_status
            cyclic_rows.extend(rows)
        else:
            row = analyze_shutin(case, frame)
            row["analysis_status"] = analysis_status
            shutin_rows.append(row)

    index = pd.DataFrame(index_rows)
    cyclic = pd.DataFrame(cyclic_rows)
    shutin = pd.DataFrame(shutin_rows)
    index.to_csv(output / "DISCUSSION_101_RUN_INDEX.csv", index=False, float_format="%.9g")
    cyclic.to_csv(output / "DISCUSSION_101_CYCLIC_METRICS.csv", index=False, float_format="%.9g")
    shutin.to_csv(output / "DISCUSSION_101_SHUTIN_METRICS.csv", index=False, float_format="%.9g")

    print(f"101 inventory: {len(index)} decks, {(index.run_status == 'complete').sum()} complete, "
          f"{(index.result_status == 'missing').sum()} missing")
    print(f"cyclic probes: {len(cyclic)} rows; shut-in cases: {len(shutin)} rows")
    for path in ("DISCUSSION_101_RUN_INDEX.csv", "DISCUSSION_101_CYCLIC_METRICS.csv",
                 "DISCUSSION_101_SHUTIN_METRICS.csv"):
        print(f"wrote {(output / path).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
