"""Per-sample diagnostics for the Ye & Ghassemi (2018) Series-108 runs."""

from pathlib import Path
import re

from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SERIES108_BY_SAMPLE = {
    "SWT1": {
        "108_01_swt1_ctrl_hold1e6": dict(
            mechanism="control", protocol_end=3500.0, end_time=1003500.0
        ),
        "108_03_swt1_reconf3p5x": dict(
            mechanism="reconfinement", protocol_end=3500.0, end_time=6200.0
        ),
        "108_07_swt1_unldtau150": dict(
            mechanism="retention lag",
            protocol_end=3500.0,
            end_time=63500.0,
            parent="100_01_swt1_vm55um_ppfix_hpc.csv",
        ),
        "108_08_swt1_unldtau1500": dict(
            mechanism="retention lag",
            protocol_end=3500.0,
            end_time=63500.0,
            parent="100_01_swt1_vm55um_ppfix_hpc.csv",
        ),
        "108_09_swt1_unldtau15000": dict(
            mechanism="retention lag",
            protocol_end=3500.0,
            end_time=63500.0,
            parent="100_01_swt1_vm55um_ppfix_hpc.csv",
        ),
        "108_11_swt1_creeptc1e5": dict(
            mechanism="closure creep", protocol_end=3500.0, end_time=1003500.0
        ),
        "108_15_swt1_creeptc1e4": dict(
            mechanism="closure creep", protocol_end=3500.0, end_time=1003500.0
        ),
        "108_16_swt1_creeptc1e6": dict(
            mechanism="closure creep", protocol_end=3500.0, end_time=1003500.0
        ),
    },
    "SWT2": {
        "108_04_swt2_reconf3p5x": dict(
            mechanism="reconfinement", protocol_end=2852.53, end_time=5552.53
        ),
        "108_10_swt2_unldtau1500": dict(
            mechanism="retention lag",
            protocol_end=2852.53,
            end_time=62852.5,
            parent="100_04_swt2_apscale0p0177_ppfix_hpc.csv",
        ),
        "108_12_swt2_creeptc1e5": dict(
            mechanism="closure creep", protocol_end=2852.53, end_time=1002852.5
        ),
    },
    "SWS3": {
        "108_05_sw3_reconf3p5x": dict(
            mechanism="reconfinement", protocol_end=4802.0, end_time=7502.0
        ),
        "108_13_sw3_creeptc1e5": dict(
            mechanism="closure creep", protocol_end=4802.0, end_time=1004802.0
        ),
    },
    "SWS4": {
        "108_02_sw4_ctrl_hold1e6": dict(
            mechanism="control", protocol_end=3500.0, end_time=1003500.0
        ),
        "108_06_sw4_reconf3p5x": dict(
            mechanism="reconfinement", protocol_end=3500.0, end_time=6200.0
        ),
        "108_14_sw4_creeptc1e5": dict(
            mechanism="closure creep", protocol_end=3500.0, end_time=1003500.0
        ),
    },
}


def _read_csv(path: Path) -> pd.DataFrame:
    return (
        pd.read_csv(path)
        .sort_values("time")
        .drop_duplicates("time", keep="last")
        .reset_index(drop=True)
    )


def _row_at_or_before(df: pd.DataFrame, time_s: float):
    rows = df[df.time <= time_s + 1e-9]
    return None if rows.empty else rows.iloc[-1]


def _relative_change(new: float, old: float, scale: float = 100.0) -> float:
    return np.nan if old == 0 else scale * (new - old) / old


def _deck_scalar(deck_text: str, name: str) -> float:
    match = re.search(rf"^\s*{name}\s*=\s*([0-9.eE+-]+)", deck_text, re.M)
    if match is None:
        raise ValueError(f"{name} not found in Series-108 deck")
    return float(match.group(1))


def run_series108_checks(
    sample: str, base: Path, sweeps: Path, end_time_tolerance_s: float = 1.0
):
    """Display and return the Series-108 checks for one sample notebook."""
    cfg_by_run = SERIES108_BY_SAMPLE[sample]
    result_dirs = [
        base / "results_csv_hpc_rorqual",
        sweeps / "results_csv_hpc_rorqual",
    ]
    data = {}
    health_rows = []

    for stem, cfg in cfg_by_run.items():
        path = next(
            (directory / f"{stem}_hpc.csv" for directory in result_dirs
             if (directory / f"{stem}_hpc.csv").exists()),
            None,
        )
        if path is None:
            health_rows.append(
                dict(
                    run=stem,
                    mechanism=cfg["mechanism"],
                    state="MISSING CSV",
                    rows=0,
                    t_end_s=np.nan,
                    expected_end_s=cfg["end_time"],
                    completion_pct=np.nan,
                    numeric_finite=np.nan,
                )
            )
            continue
        df = _read_csv(path)
        data[stem] = df
        t_end = float(df.time.iloc[-1])
        complete = t_end >= cfg["end_time"] - end_time_tolerance_s
        finite = bool(np.isfinite(df.select_dtypes(include=[np.number]).to_numpy()).all())
        health_rows.append(
            dict(
                run=stem,
                mechanism=cfg["mechanism"],
                state="complete" if complete else "TRUNCATED",
                rows=len(df),
                t_end_s=t_end,
                expected_end_s=cfg["end_time"],
                completion_pct=100 * t_end / cfg["end_time"],
                numeric_finite=finite,
            )
        )

    health = pd.DataFrame(health_rows).set_index("run")
    display(health.round(3))

    control_rows = []
    for stem, cfg in cfg_by_run.items():
        if cfg["mechanism"] != "control" or stem not in data:
            continue
        start = _row_at_or_before(data[stem], cfg["protocol_end"])
        end = data[stem].iloc[-1]
        ah_ppm = _relative_change(
            end.hydraulic_aperture_um_pp, start.hydraulic_aperture_um_pp, 1e6
        )
        q_ppm = _relative_change(
            end.flow_rate_validation_ml_min_pp,
            start.flow_rate_validation_ml_min_pp,
            1e6,
        )
        slip_delta_um = (
            end.cumulative_plastic_slip_pp - start.cumulative_plastic_slip_pp
        ) * 1e6
        complete = health.loc[stem, "state"] == "complete"
        control_rows.append(
            dict(
                run=stem,
                aperture_start_um=start.hydraulic_aperture_um_pp,
                aperture_end_um=end.hydraulic_aperture_um_pp,
                aperture_drift_ppm=ah_ppm,
                flow_drift_ppm=q_ppm,
                plastic_slip_delta_um=slip_delta_um,
                stationary_within_10ppm=complete
                and abs(ah_ppm) <= 10
                and abs(q_ppm) <= 10
                and abs(slip_delta_um) <= 1e-6,
            )
        )
    control = pd.DataFrame(control_rows).set_index("run") if control_rows else pd.DataFrame()
    if not control.empty:
        display(control.round(6))

    retention_rows = []
    for stem, cfg in cfg_by_run.items():
        if cfg["mechanism"] != "retention lag" or stem not in data:
            continue
        parent_candidates = [
            base / "results_csv_hpc_rorqual" / cfg["parent"],
            sweeps / "results_csv_hpc_rorqual" / cfg["parent"],
        ]
        parent_path = next((path for path in parent_candidates if path.exists()), None)
        if parent_path is None:
            retention_rows.append(dict(run=stem, state="PARENT CSV MISSING"))
            continue
        parent = _read_csv(parent_path)
        end, reference = data[stem].iloc[-1], parent.iloc[-1]
        ah_pct = _relative_change(
            end.hydraulic_aperture_um_pp, reference.hydraulic_aperture_um_pp
        )
        q_pct = _relative_change(
            end.flow_rate_validation_ml_min_pp,
            reference.flow_rate_validation_ml_min_pp,
        )
        n_delta = (
            end.effective_normal_compression_mpa_pp
            - reference.effective_normal_compression_mpa_pp
        )
        slip_delta_um = (
            end.cumulative_plastic_slip_pp - reference.cumulative_plastic_slip_pp
        ) * 1e6
        complete = health.loc[stem, "state"] == "complete"
        retention_rows.append(
            dict(
                run=stem,
                state="complete" if complete else "TRUNCATED",
                aperture_delta_um=(
                    end.hydraulic_aperture_um_pp - reference.hydraulic_aperture_um_pp
                ),
                aperture_delta_pct=ah_pct,
                flow_delta_pct=q_pct,
                normal_stress_delta_MPa=n_delta,
                plastic_slip_delta_um=slip_delta_um,
                endpoint_within_0p1pct=complete
                and abs(ah_pct) <= 0.1
                and abs(q_pct) <= 0.1,
            )
        )
    retention = (
        pd.DataFrame(retention_rows).set_index("run") if retention_rows else pd.DataFrame()
    )
    if not retention.empty:
        display(retention.round(6))

    reconf_rows = []
    reconf_plot = []
    for stem, cfg in cfg_by_run.items():
        if cfg["mechanism"] != "reconfinement" or stem not in data:
            continue
        limb = data[stem][data[stem].time >= cfg["protocol_end"] - 1e-9].copy()
        deck_text = (sweeps / f"{stem}.i").read_text()
        match = re.search(
            r"^initial_hydraulic_aperture\s*=\s*([0-9.eE+-]+)", deck_text, re.M
        )
        if match is None:
            raise ValueError(f"initial_hydraulic_aperture not found in {stem}.i")
        a_h0_um = float(match.group(1)) * 1e6
        virgin = a_h0_um + limb.normal_stress_aperture_um_pp.to_numpy(float)
        actual = limb.hydraulic_aperture_um_pp.to_numpy(float)
        normal = limb.effective_normal_compression_mpa_pp.to_numpy(float)
        gap = actual - virgin
        crossing = np.nan
        if gap[0] <= 0:
            verdict = "already at/below virgin at limb start"
        else:
            hit = np.flatnonzero(gap <= 0)
            if len(hit):
                j = int(hit[0])
                i = max(0, j - 1)
                crossing = (
                    normal[j]
                    if j == i or gap[j] == gap[i]
                    else normal[i]
                    - gap[i] * (normal[j] - normal[i]) / (gap[j] - gap[i])
                )
                verdict = "crossing observed"
            else:
                verdict = "no crossing in reached range"
        reconf_rows.append(
            dict(
                run=stem,
                state=health.loc[stem, "state"],
                normal_start_MPa=normal[0],
                normal_max_MPa=np.max(normal),
                gap_to_virgin_start_um=gap[0],
                gap_to_virgin_end_um=gap[-1],
                minimum_gap_um=np.min(gap),
                crossing_normal_MPa=crossing,
                verdict=verdict,
            )
        )
        reconf_plot.append((stem, normal, actual, virgin))
    reconfinement = (
        pd.DataFrame(reconf_rows).set_index("run") if reconf_rows else pd.DataFrame()
    )
    if not reconfinement.empty:
        display(reconfinement.round(6))

    # Closure creep: reintegrate the exported mean-stress history analytically over
    # the post-protocol hold and report when hydraulic aperture returns to a_h0.
    creep_rows = []
    for stem, cfg in cfg_by_run.items():
        if cfg["mechanism"] != "closure creep" or stem not in data:
            continue
        df = data[stem]
        limb = df[df.time >= cfg["protocol_end"] - 1e-9].copy().reset_index(drop=True)
        deck_text = (sweeps / f"{stem}.i").read_text()
        a_h0_um = _deck_scalar(deck_text, "initial_hydraulic_aperture") * 1e6
        a_max_um = _deck_scalar(deck_text, "closure_creep_max_aperture") * 1e6
        tau_s = _deck_scalar(deck_text, "closure_creep_time")
        n_ref_mpa = _deck_scalar(deck_text, "closure_creep_reference_stress") / 1e6
        exponent = _deck_scalar(deck_text, "closure_creep_stress_exponent")
        time = limb.time.to_numpy(float)
        normal = np.maximum(0.0, limb.effective_normal_compression_mpa_pp.to_numpy(float))
        model = limb.closure_creep_aperture_um_pp.to_numpy(float)
        rate = np.where(normal > 0, (normal / n_ref_mpa) ** exponent / tau_s, 0.0)
        exposure = np.zeros_like(time)
        if len(time) > 1:
            exposure[1:] = np.cumsum(0.5 * (rate[1:] + rate[:-1]) * np.diff(time))
        analytic = a_max_um - (a_max_um - model[0]) * np.exp(-exposure)
        error_pct = 100 * np.max(np.abs(model - analytic)) / max(a_max_um, 1e-30)
        crossed = np.flatnonzero(limb.hydraulic_aperture_um_pp.to_numpy(float) <= a_h0_um)
        crossing_time = float(time[crossed[0]]) if len(crossed) else np.nan
        complete = health.loc[stem, "state"] == "complete"
        creep_rows.append(
            dict(
                run=stem,
                state="complete" if complete else "TRUNCATED",
                creep_end_um=model[-1],
                analytic_end_um=analytic[-1],
                max_error_pct_of_a_max=error_pct,
                aperture_crossing_time_s=crossing_time,
                crossed_a_h0=np.isfinite(crossing_time),
            )
        )
    creep = pd.DataFrame(creep_rows).set_index("run") if creep_rows else pd.DataFrame()
    if not creep.empty:
        display(creep.round(6))

    temporal = [
        (stem, cfg, data[stem])
        for stem, cfg in cfg_by_run.items()
        if stem in data
        and cfg["mechanism"] in {"control", "retention lag", "closure creep"}
    ]
    n_panels = int(bool(temporal)) + int(bool(reconf_plot))
    if n_panels:
        _, axes = plt.subplots(1, n_panels, figsize=(6 * n_panels, 4), squeeze=False)
        panel = 0
        if temporal:
            ax = axes[0, panel]
            panel += 1
            for stem, cfg, df in temporal:
                hold = df[df.time >= cfg["protocol_end"] - 1e-9]
                ax.plot(
                    (hold.time - cfg["protocol_end"]) / 3600,
                    hold.hydraulic_aperture_um_pp,
                    label=stem.split("_", 2)[-1],
                )
            ax.set(
                xlabel="elapsed hold time [h]",
                ylabel="hydraulic aperture [um]",
                title="Long-hold and retention response",
            )
            ax.legend()
        if reconf_plot:
            ax = axes[0, panel]
            for stem, normal, actual, virgin in reconf_plot:
                ax.plot(normal, actual, label=f"{stem}: post-stimulation")
                ax.plot(normal, virgin, "--", label=f"{stem}: virgin backbone")
            ax.set(
                xlabel="effective normal compression [MPa]",
                ylabel="hydraulic aperture [um]",
                title="Reconfinement at matched normal stress",
            )
            ax.legend()
        plt.show()

    missing = health.index[health.state.eq("MISSING CSV")].tolist()
    if missing:
        print("Not interpreted because CSV is missing:", ", ".join(missing))

    return dict(
        health=health,
        control=control,
        retention=retention,
        reconfinement=reconfinement,
        creep=creep,
        data=data,
    )
