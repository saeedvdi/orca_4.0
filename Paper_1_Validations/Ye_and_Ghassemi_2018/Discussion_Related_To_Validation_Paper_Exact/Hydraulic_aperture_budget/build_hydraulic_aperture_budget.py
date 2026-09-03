#!/usr/bin/env python3
"""Build mechanism-resolved hydraulic diagnostics from the selected ORCA runs."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


VALIDATION = Path(__file__).resolve().parents[2]
ROOT = VALIDATION.parents[1]
CASES = VALIDATION / "Paper_Cases/01_Main_Validation"
OUT = Path(__file__).resolve().parents[1]

BB = {
    "SW-T1": {
        "sample": "SWT1",
        "csv": CASES / "SWT1/BB/107_01_swt1_coh27p2_apscale0p01512_ppfix.csv",
        "deck": CASES / "SWT1/BB/107_01_swt1_coh27p2_apscale0p01512_ppfix.i",
        "a0_um": 1.63,
        "aperture_scale": 0.01512,
        "dilation_scale": 0.0,
        "retention_residual": 0.714876033058,
    },
    "SW-T2": {
        "sample": "SWT2",
        "csv": CASES / "SWT2/BB/100_04_swt2_apscale0p0177_ppfix_hpc.csv",
        "deck": CASES / "SWT2/BB/100_04_swt2_apscale0p0177_ppfix.i",
        "a0_um": 2.11,
        "aperture_scale": 0.0177,
        "dilation_scale": 0.0,
        "retention_residual": 0.747330960854,
    },
    "SW-S3": {
        "sample": "SWS3",
        "csv": CASES / "SWS3/BB/100_06_sw3_resc1p30_unld0p00_ppfix_hpc.csv",
        "deck": CASES / "SWS3/BB/100_06_sw3_resc1p30_unld0p00_ppfix.i",
        "a0_um": 1.22,
        "aperture_scale": 0.001,
        "dilation_scale": 0.038,
        "retention_residual": 0.28,
    },
    "SW-S4": {
        "sample": "SWS4",
        "csv": CASES / "SWS4/BB/93_07_sw4_final_theta30_jrc5_ppfix_hpc.csv",
        "deck": CASES / "SWS4/BB/93_07_sw4_final_theta30_jrc5_ppfix.i",
        "a0_um": 0.74,
        "aperture_scale": 0.001,
        "dilation_scale": 0.0117,
        "retention_residual": 0.28,
    },
}

MC = {
    "SW-T1": {
        "sample": "SWT1",
        "csv": CASES / "SWT1/MC/SWT1_OrcaMohrCoulombContactTraction_pb04.csv",
        "deck": CASES / "SWT1/MC/SWT1_OrcaMohrCoulombContactTraction.i",
    },
    "SW-T2": {
        "sample": "SWT2",
        "csv": CASES / "SWT2/MC/SWT2_OrcaMohrCoulombContactTraction_pb04.csv",
        "deck": CASES / "SWT2/MC/SWT2_OrcaMohrCoulombContactTraction.i",
    },
    "SW-S3": {
        "sample": "SWS3",
        "csv": CASES / "SWS3/MC/SWS3_OrcaMohrCoulombContactTraction_pb06.csv",
        "deck": CASES / "SWS3/MC/SWS3_OrcaMohrCoulombContactTraction.i",
    },
    "SW-S4": {
        "sample": "SWS4",
        "csv": CASES / "SWS4/MC/SWS4_OrcaMohrCoulombContactTraction_center.csv",
        "deck": CASES / "SWS4/MC/SWS4_OrcaMohrCoulombContactTraction.i",
    },
}


def load_gate():
    path = ROOT / "scripts/table2_gate.py"
    spec = importlib.util.spec_from_file_location("table2_gate", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


GATE = load_gate()


def stage_rows(csv_path: Path, deck_path: Path) -> pd.DataFrame:
    frame = pd.read_csv(csv_path)
    x, y = GATE.parse_schedule(deck_path)
    times = GATE.stage_times(x, y, tol_mpa=0.15)
    rows = []
    for stage, target_time in enumerate(times, start=1):
        eligible = frame.loc[frame["time"] <= target_time]
        if eligible.empty:
            idx = (frame["time"] - target_time).abs().idxmin()
            row = frame.loc[idx].copy()
        else:
            row = eligible.iloc[-1].copy()
        row["stage"] = stage
        rows.append(row)
    return pd.DataFrame(rows).set_index("stage")


def permeability_values(rows: pd.DataFrame) -> np.ndarray:
    if "fracture_permeability_pp" in rows:
        return rows["fracture_permeability_pp"].to_numpy(dtype=float)
    aperture = rows["hydraulic_aperture_pp"].to_numpy(dtype=float)
    return aperture**2 / 12.0


def build_metrics() -> pd.DataFrame:
    records = []
    for specimen, cfg in BB.items():
        exp = np.asarray(GATE.TABLE2[cfg["sample"]]["k_1e12_m2"], dtype=float) * 1.0e-12
        for source, values in (
            ("Experiment", exp),
            ("BB", permeability_values(stage_rows(cfg["csv"], cfg["deck"]))),
            ("MC", permeability_values(stage_rows(MC[specimen]["csv"], MC[specimen]["deck"]))),
        ):
            records.append(
                {
                    "specimen": specimen,
                    "source": source,
                    "initial_permeability_m2": values[0],
                    "peak_permeability_m2": values[5],
                    "final_permeability_m2": values[10],
                    "peak_enhancement_ratio": values[5] / values[0],
                    "final_retention_ratio": values[10] / values[0],
                }
            )
    return pd.DataFrame.from_records(records)


def aperture_components(cfg: dict) -> pd.DataFrame:
    rows = stage_rows(cfg["csv"], cfg["deck"])
    roughness = rows["roughness_state_pp"].clip(lower=0.0, upper=1.0)
    retention = cfg["retention_residual"] + (1.0 - cfg["retention_residual"]) * roughness
    result = pd.DataFrame(index=rows.index)
    result["Reference"] = cfg["a0_um"]
    result["Stress opening"] = rows["normal_stress_aperture_pp"] * 1.0e6
    result["Geometric opening"] = (
        cfg["aperture_scale"] * rows["mechanical_aperture_pp"] * 1.0e6
    )
    result["Retained dilation"] = (
        cfg["dilation_scale"] * rows["cumulative_dilation_pp"] * retention * 1.0e6
    )
    result["Gouge loss"] = -rows["slip_damage_aperture_pp"] * 1.0e6
    result["Total"] = rows["hydraulic_aperture_pp"] * 1.0e6
    return result


def build_figure() -> None:
    chosen = [1, 6, 11]
    labels = ["Initial\n8 MPa", "Peak\n28 MPa", "Final\n8 MPa"]
    colors = {
        "Reference": "#4c78a8",
        "Stress opening": "#72b7b2",
        "Geometric opening": "#f58518",
        "Retained dilation": "#54a24b",
        "Gouge loss": "#e45756",
    }
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 7.2), constrained_layout=True)
    for ax, (specimen, cfg) in zip(axes.flat, BB.items()):
        comp = aperture_components(cfg).loc[chosen]
        x = np.arange(len(chosen), dtype=float)
        positive_bottom = np.zeros(len(chosen))
        negative_bottom = np.zeros(len(chosen))
        for name in colors:
            values = comp[name].to_numpy(dtype=float)
            bottom = np.where(values >= 0.0, positive_bottom, negative_bottom)
            ax.bar(x, values, bottom=bottom, width=0.66, color=colors[name], label=name)
            positive_bottom += np.where(values >= 0.0, values, 0.0)
            negative_bottom += np.where(values < 0.0, values, 0.0)
        ax.plot(x, comp["Total"], color="black", marker="o", linewidth=1.7, label="Total aperture")
        ax.axhline(0.0, color="0.2", linewidth=0.7)
        ax.set_title(specimen)
        ax.set_xticks(x, labels)
        ax.set_ylabel("Hydraulic-aperture contribution ($\\mu$m)")
        ax.grid(axis="y", alpha=0.22)
    handles, legend_labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, ncol=3, loc="outside lower center", frameon=False)
    figure_dir = OUT / "Figures"
    figure_dir.mkdir(exist_ok=True)
    fig.savefig(figure_dir / "Figure_Hydraulic_Aperture_Budget.pdf", bbox_inches="tight")
    fig.savefig(figure_dir / "Figure_Hydraulic_Aperture_Budget.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    metrics = build_metrics()
    metrics.to_csv(OUT / "hydraulic_enhancement_retention_metrics.csv", index=False)
    component_frames = []
    for specimen, cfg in BB.items():
        frame = aperture_components(cfg).reset_index()
        frame.insert(0, "specimen", specimen)
        component_frames.append(frame)
    pd.concat(component_frames, ignore_index=True).to_csv(
        OUT / "hydraulic_aperture_components_by_stage.csv", index=False
    )
    build_figure()
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()
