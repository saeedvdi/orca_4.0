#!/usr/bin/env python3
"""Score an ORCA run against Ye & Ghassemi (2018) Table 2, for any of the four samples.

Table 2 tabulates, for each specimen, eleven injection hold stages (six on the
loading ramp at Pi = 8, 12, 16, 20, 24, 28 MPa, then five unloading at 24, 20,
16, 12, 8 MPa) and eight quantities per stage.

Only FIVE of those eight are independent measurements, and only those five are
scored here:

    Q          flow rate            (mL/min)
    sigma'_n   effective normal     (MPa)
    tau        shear stress         (MPa)
    d_n        normal displacement  (mm)
    d_s        shear displacement   (mm)

The other two, a_h and k, are not independent: the paper back-computes a_h from
the measured Q through the cubic law and then defines k = a_h^2/12, so k is a
pure function of Q and carries no information beyond it. They are reported as
informational columns and excluded from the score.

Stage detection
---------------
The four samples do NOT share a schedule shape. SW-T1 and SW-T2 use a clean
staircase whose plateaus sit exactly on the target pressures, so plateau
detection works. SW-S3 and SW-S4 use digitized schedules; SW-S3 in particular
has flat runs for only about six of the eleven stages, so strict plateau
detection silently loses stages there.

This script therefore uses a method that behaves identically on both shapes:
split the deck's own [injection_pressure] function at its peak into a loading
and an unloading branch, then walk the eleven targets in order behind a
monotonic time cursor, taking for each the LAST schedule point within
--tol-mpa of the target (or, failing that, the single nearest point). On a
staircase that lands on the end of the hold; on a digitized ramp it lands on
the closest approach. The model is then sampled at the last output row at or
before that time.

The d_n channel
---------------
Two postprocessors in these decks both claim to be "normal displacement in the
paper's sign convention", and they are NOT the same observable across the two
constitutive laws:

    czm_normal_dilation_paper_mm_pp   reads ``normal_opening_total``
    frac_normal_dilation_paper_mm     reads the global normal jump directly

``normal_opening_total`` is a constitutive decomposition, and the two materials
decompose differently::

    ADOrcaBartonBandisContactTractionFastAD
        normal_opening_total = irreversible + reversible + ELASTIC
    ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile  (the MC baseline)
        normal_opening_total = plastic + reversible          <- no elastic term

The MC material's elastic closure never reaches that channel. With
``reversible_normal_compliance`` at its default of zero -- which is what the
94-series sets -- the MC d_n column is the plastic normal jump alone, so it is
monotone by construction and reports **exactly zero** recovery on the unloading
branch no matter what the mechanics did. Measured on the 94-series finals:

    specimen   recovery on normal_opening_total   recovery on the global jump
    SW-S3                        0.00 um                        12.74 um
    SW-S4                        0.00 um                         9.64 um
    SW-T1                        0.00 um                          0.84 um
    SW-T2                        0.00 um                          1.27 um

Scoring MC on ``normal_opening_total`` therefore charges the baseline for a
missing reporting term, not for a missing mechanism, and it does so only on one
side of the comparison the campaign exists to make. On SW-S4 that alone is
1.9 percentage points of mean nRMSE (8.97 -> 7.07).

The default channel here is the **global kinematic jump**, which is what the
experiment's LVDTs measure and which both materials emit. For the ppfix-frame
BBFast finals the two channels are numerically identical, so this default
changes no Barton-Bandis score; it changes the Mohr-Coulomb ones, in the
baseline's favour. Pass ``--dn-channel total`` to reproduce the pre-2026-08-25
campaign numbers.

The d_n / d_s datum
-------------------
Table 2 reports d_n = d_s = 0.000 at stage 1 for all four samples, so the model
is zeroed at stage 1 rather than at a preload timestamp. This removes a
per-sample constant (each deck's preload end differs, and one notebook's
PRELOAD_END_S disagrees with the deck's own first plateau) at the cost of
making stage 1 exactly zero by construction -- stage 1 is therefore NOT an
independent test of d_n or d_s, and is excluded from their score. Pass
--datum preload --preload-time T for the older convention.

Usage
-----
    python table2_gate.py run.csv
    python table2_gate.py baseline.csv fixed.csv          # A/B, side by side
    python table2_gate.py --label 'alpha=1e-12' a.csv --label 'alpha=0.6' b.csv
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Ye & Ghassemi (2018), Table 2.
#
# Provenance of each block, so these can be re-checked against the paper:
#   SWS4  SW4_July10/export_table2_comparison.py          TABLE2_ROWS
#   SWS3  SW3_July18/Ye2018_SW3_validation_audit_corrected_v2.ipynb
#                                        TABLE2_LOADING + TABLE2_UNLOADING
#   SWT1  SWT1/Ye2018_SWT1_vs_validation.ipynb            TABLE2
#   SWT2  SWT2/Ye2018_SWT2_vs_validation.ipynb            TABLE2
# (all four in orca_3.0_full/Examples/YeGhasemmi2018/)
#
# k is normalised to units of 1e-12 m^2 here; the SWS3/SWS4 sources tabulate it
# as 1e-13 m^2, so those columns are divided by 10 relative to the source.
# ---------------------------------------------------------------------------

SEGMENTS = ["loading"] * 6 + ["unloading"] * 5
PI_TARGETS = [8, 12, 16, 20, 24, 28, 24, 20, 16, 12, 8]

TABLE2 = {
    "SWS4": {
        "Q_ml_min":    [0.005, 0.012, 0.022, 0.035, 0.056, 0.113, 0.064, 0.037, 0.024, 0.013, 0.005],
        "dn_mm":       [0.000, 0.000, -0.001, -0.008, -0.021, -0.041, -0.038, -0.036, -0.034, -0.033, -0.032],
        "ds_mm":       [0.000, 0.000, 0.000, 0.017, 0.041, 0.075, 0.077, 0.078, 0.079, 0.079, 0.079],
        "sigma_n_MPa": [30.75, 28.73, 26.51, 22.92, 19.25, 15.31, 17.13, 19.00, 20.89, 22.82, 24.81],
        "tau_MPa":     [12.56, 12.53, 12.14, 9.38, 6.48, 3.12, 2.82, 2.59, 2.41, 2.28, 2.27],
        "ah_um":       [0.74, 0.75, 0.79, 0.83, 0.90, 1.07, 0.94, 0.85, 0.81, 0.77, 0.74],
        "k_1e12_m2":   [0.046, 0.047, 0.052, 0.058, 0.067, 0.095, 0.074, 0.060, 0.055, 0.049, 0.046],
    },
    "SWS3": {
        "Q_ml_min":    [0.022, 0.050, 0.078, 0.121, 0.150, 0.860, 0.460, 0.310, 0.210, 0.130, 0.054],
        "dn_mm":       [0.000, 0.000, 0.000, 0.000, 0.000, -0.044, -0.044, -0.044, -0.043, -0.042, -0.041],
        "ds_mm":       [0.000, 0.000, 0.000, 0.001, 0.001, 0.071, 0.072, 0.072, 0.073, 0.073, 0.073],
        "sigma_n_MPa": [31.65, 29.58, 27.53, 25.48, 23.42, 15.25, 17.27, 19.14, 21.01, 22.86, 24.79],
        "tau_MPa":     [14.70, 14.57, 14.48, 14.38, 14.26, 3.55, 3.19, 2.95, 2.68, 2.44, 2.31],
        "ah_um":       [1.22, 1.21, 1.20, 1.26, 1.25, 2.10, 1.81, 1.72, 1.68, 1.66, 1.64],
        "k_1e12_m2":   [0.124, 0.121, 0.121, 0.132, 0.130, 0.366, 0.274, 0.247, 0.234, 0.230, 0.225],
    },
    "SWT1": {
        "Q_ml_min":    [0.053, 0.114, 0.190, 0.280, 0.389, 6.220, 4.270, 2.870, 1.900, 1.120, 0.462],
        "dn_mm":       [0.000, 0.000, 0.000, -0.001, -0.003, -0.157, -0.139, -0.130, -0.123, -0.118, -0.113],
        "ds_mm":       [0.000, 0.000, 0.001, 0.002, 0.008, 0.532, 0.539, 0.534, 0.529, 0.525, 0.521],
        "sigma_n_MPa": [65.47, 63.35, 61.27, 59.14, 56.94, 31.79, 33.45, 35.35, 37.29, 39.22, 41.14],
        "tau_MPa":     [67.16, 66.96, 66.82, 66.63, 66.32, 29.35, 28.72, 28.57, 28.48, 28.36, 28.23],
        "ah_um":       [1.63, 1.59, 1.62, 1.66, 1.72, 4.05, 3.81, 3.61, 3.49, 3.40, 3.36],
        "k_1e12_m2":   [0.22, 0.21, 0.22, 0.23, 0.25, 1.37, 1.21, 1.09, 1.02, 0.97, 0.94],
    },
    "SWT2": {
        "Q_ml_min":    [0.115, 0.276, 0.450, 0.750, 1.505, 11.100, 7.200, 5.150, 3.540, 2.160, 0.910],
        "dn_mm":       [0.000, -0.001, -0.002, -0.003, -0.005, -0.142, -0.142, -0.139, -0.139, -0.133, -0.130],
        "ds_mm":       [0.000, 0.001, 0.003, 0.007, 0.015, 0.571, 0.572, 0.566, 0.565, 0.557, 0.552],
        "sigma_n_MPa": [66.74, 64.53, 62.37, 60.19, 57.88, 29.36, 31.26, 33.23, 35.23, 37.18, 39.14],
        "tau_MPa":     [74.87, 74.54, 74.25, 73.94, 73.40, 27.48, 27.29, 27.24, 27.25, 27.15, 27.09],
        "ah_um":       [2.11, 2.13, 2.16, 2.31, 2.69, 4.92, 4.54, 4.39, 4.30, 4.24, 4.21],
        "k_1e12_m2":   [0.37, 0.38, 0.39, 0.44, 0.60, 2.02, 1.72, 1.61, 1.54, 1.50, 1.48],
    },
}

# The two d_n channels, most-preferred first within each. "kinematic" is the
# default and is the like-for-like observable; "total" reproduces the campaign's
# pre-2026-08-25 numbers and is retained so historical scores can be regenerated.
DN_CHANNELS = {
    "kinematic": [("frac_normal_dilation_paper_mm", 1.0),
                  ("czm_normal_dilation_paper_mm_pp", 1.0)],
    "total":     [("czm_normal_dilation_paper_mm_pp", 1.0),
                  ("frac_normal_dilation_paper_mm", 1.0)],
}
DEFAULT_DN_CHANNEL = "kinematic"


SCORED = ["Q_ml_min", "sigma_n_MPa", "tau_MPa", "dn_mm", "ds_mm"]
INFORMATIONAL = ["ah_um", "k_1e12_m2"]

# Flatness tolerance used only to decide which schedule points belong to the
# peak plateau. 1 kPa, matching export_table2_comparison.py's flat_tol_pa.
FLAT_TOL_MPA = 1.0e-3

# Absolute-error gate widths, from SW4_67_FINAL_FOUR/BACK_ANALYSIS_AND_FINAL_SELECTION.md
# gate #4. Only defined for the two displacements; the others are reported
# without a PASS/FAIL because no gate width was ever established for them.
GATE_WIDTH = {"ds_mm": 0.002, "dn_mm": 0.003}

# Model column candidates, most-preferred first, with the scale that converts to
# the paper's unit. The paper-frame postprocessors resolve onto the fracture
# plane with the paper's own theta and are preferred where the deck emits them;
# SW-S4's decks predate them and fall through to the BB/local channels, which is
# the mapping export_table2_comparison.py used.
MODEL_COLUMNS = {
    "Pi_MPa":      [("injection_pressure_pp", 1e-6)],
    "Q_ml_min":    [("flow_rate_validation_ml_min_pp", 1.0)],
    "sigma_n_MPa": [("effective_normal_paper_frame_mpa_pp", 1.0),
                    ("bb_effective_normal_stress_pp", 1e-6),
                    ("effective_normal_compression_mpa_pp", 1.0)],
    "tau_MPa":     [("shear_stress_paper_frame_mpa_pp", 1.0),
                    ("shear_traction_magnitude_pa", 1e-6)],
    # Placeholder: the active d_n candidates are chosen per run by
    # dn_candidates() from DN_CHANNELS. See "The d_n channel" above -- the two
    # postprocessors are not the same observable across the two laws.
    "dn_mm":       [("frac_normal_dilation_paper_mm", 1.0),
                    ("czm_normal_dilation_paper_mm_pp", 1.0)],
    "ds_mm":       [("czm_shear_slip_mm_pp", 1.0)],
    "ah_um":       [("hydraulic_aperture_um_pp", 1.0),
                    ("hydraulic_aperture_pp", 1e6)],
    "k_1e12_m2":   [("fracture_permeability_pp", 1e12)],
}


def detect_sample(*paths: Path) -> str:
    """Infer the sample code from any of the supplied paths."""
    blob = " ".join(str(p) for p in paths).lower()
    # Check the explicit directory codes first, then the deck-name conventions.
    for code, patterns in (
        ("SWS3", ("sws3", "/sw3", "_sw3_", "swss3")),
        ("SWS4", ("sws4", "/sw4", "_sw4_", "swss4")),
        ("SWT1", ("swt1",)),
        ("SWT2", ("swt2",)),
    ):
        if any(p in blob for p in patterns):
            return code
    raise SystemExit(
        "Could not infer the sample from the path(s); pass --sample SWS3|SWS4|SWT1|SWT2:\n  "
        + "\n  ".join(str(p) for p in paths)
    )


def find_deck(csv_path: Path, tag: str | None) -> Path:
    """Locate the deck that produced a results CSV.

    Runs launched by run_biot_ab_local.sh carry a campaign tag appended to the
    csv_file_base, so <deck>_<tag>.csv must map back to <deck>.i one directory up.
    """
    stem = csv_path.stem
    stems = [stem]
    # Cluster submissions deliberately append ``_hpc`` to csv_file_base so a
    # delivered result cannot overwrite a local run of the same deck.  The
    # input deck itself keeps the unsuffixed name.
    if stem.endswith("_hpc"):
        stems.append(stem[:-4])
    if tag and stem.endswith("_" + tag):
        stems.append(stem[: -(len(tag) + 1)])
    # results_csv/<name>.csv -> ../<name>.i is the layout every sample dir uses.
    roots = [csv_path.parent.parent, csv_path.parent]
    for s in stems:
        for root in roots:
            candidate = root / (s + ".i")
            if candidate.is_file():
                return candidate
    raise SystemExit(f"Could not find the deck for {csv_path} (tried stems {stems})")


def parse_schedule(deck: Path) -> tuple[np.ndarray, np.ndarray]:
    text = deck.read_text(errors="ignore")
    match = re.search(r"\[injection_pressure\](.*?)\[\]", text, re.S)
    if not match:
        raise SystemExit(f"No [injection_pressure] function in {deck}")
    block = match.group(1)
    xs = re.search(r"x\s*=\s*'([^']+)'", block)
    ys = re.search(r"y\s*=\s*'([^']+)'", block)
    if not xs or not ys:
        raise SystemExit(f"[injection_pressure] in {deck} is not an x/y PiecewiseLinear")
    x = np.array([float(v) for v in xs.group(1).split()])
    y = np.array([float(v) for v in ys.group(1).split()]) * 1e-6
    if len(x) != len(y):
        raise SystemExit(f"[injection_pressure] in {deck} has {len(x)} x but {len(y)} y")
    return x, y


def stage_times(x: np.ndarray, y: np.ndarray, tol_mpa: float) -> list[float]:
    """Time of each of the eleven Table-2 stages, in order.

    The schedule is split at its peak plateau so that a loading target and the
    same-valued unloading target cannot be confused, and a monotonic cursor
    keeps the eleven times strictly increasing.

    Stage 6 is anchored to the END of the peak plateau rather than resolved by
    tolerance. Two reasons, and both bite in practice:

      * np.argmax returns the FIRST index attaining the maximum, so on the
        SW-T1/SW-T2 staircases a tolerance search over [0, argmax] can only
        ever return the START of the 28 MPa hold -- the slip event would be
        sampled before it happened.
      * SW-S3's digitized schedule overshoots to 28.57 MPa, so the actual peak
        hold sits outside any sane tolerance around the nominal 28 and would be
        skipped in favour of a point on the ramp below it.

    Stage 6 is the peak of the schedule by definition, so taking the plateau end
    is exact and removes the tolerance sensitivity from the one stage that
    matters most.
    """
    # Plateau membership uses its own tight flatness tolerance, NOT tol_mpa:
    # the target-matching tolerance is ~0.35 MPa, wide enough to swallow the
    # ramp points either side of the peak and push stage 6 past the hold (on
    # SW-S4 it landed 67 s late, at 27.79 MPa on the way down).
    peak_value = float(np.max(y))
    at_peak = np.flatnonzero(np.abs(y - peak_value) <= FLAT_TOL_MPA)
    peak_start, peak_end = int(at_peak[0]), int(at_peak[-1])
    peak_stage = int(np.argmax(PI_TARGETS))

    times: list[float] = []
    cursor = -math.inf

    for stage, (segment, target) in enumerate(zip(SEGMENTS, PI_TARGETS)):
        if stage == peak_stage:
            chosen = peak_end
        else:
            lo, hi = (0, peak_start) if segment == "loading" else (peak_end, len(x) - 1)
            idx = np.arange(lo, hi + 1)
            idx = idx[x[idx] > cursor]
            if idx.size == 0:
                raise SystemExit(
                    f"No schedule points left for stage {stage + 1} "
                    f"({segment} {target} MPa) after t={cursor:g}s"
                )
            near = idx[np.abs(y[idx] - target) <= tol_mpa]
            # Last point inside the tolerance = end of the hold on a staircase,
            # or the far side of the closest approach on a digitized ramp.
            chosen = int(near[-1]) if near.size else int(idx[np.argmin(np.abs(y[idx] - target))])
        times.append(float(x[chosen]))
        cursor = float(x[chosen])

    return times


def dn_recovery_split(raw: pd.DataFrame) -> dict | None:
    """Compare the two d_n channels on one run, in micrometres.

    ``recovery`` is how far d_n comes back from its most-open excursion by the
    end of the run -- the quantity Table 2's unloading branch actually tests.
    A material whose ``normal_opening_total`` omits the elastic term reports
    recovery of exactly zero here while the global jump reports the real value;
    that difference is a reporting artefact and must not be read as physics.
    Returns None when the run does not carry both channels.
    """
    tot_col, kin_col = "czm_normal_dilation_paper_mm_pp", "frac_normal_dilation_paper_mm"
    if tot_col not in raw.columns or kin_col not in raw.columns:
        return None
    out = {}
    for tag, col in (("total", tot_col), ("kinematic", kin_col)):
        v = pd.to_numeric(raw[col], errors="coerce").dropna().to_numpy() * 1.0e3
        if v.size == 0:
            return None
        # Paper sign convention: opening is negative, so the most-open state is
        # the minimum and recovery is the climb back from it.
        out[tag] = {"min_um": float(v.min()), "final_um": float(v[-1]),
                    "recovery_um": float(v[-1] - v.min())}
    out["recovery_gap_um"] = out["kinematic"]["recovery_um"] - out["total"]["recovery_um"]
    return out


def first_column(df: pd.DataFrame, candidates) -> tuple[pd.Series | None, str | None]:
    for name, scale in candidates:
        if name in df.columns:
            return pd.to_numeric(df[name], errors="coerce") * scale, name
    return None, None


def score_run(csv_path: Path, sample: str, tag: str | None, tol_mpa: float,
              datum: str, preload_time: float,
              dn_channel: str = DEFAULT_DN_CHANNEL) -> dict:
    if dn_channel not in DN_CHANNELS:
        raise SystemExit(f"unknown --dn-channel {dn_channel!r}; "
                         f"choose one of {sorted(DN_CHANNELS)}")
    deck = find_deck(csv_path, tag)
    x, y = parse_schedule(deck)
    times = stage_times(x, y, tol_mpa)

    raw = pd.read_csv(csv_path)
    raw = raw.sort_values("time").drop_duplicates("time", keep="last").reset_index(drop=True)
    t_end = float(raw["time"].iloc[-1])

    columns = dict(MODEL_COLUMNS)
    columns["dn_mm"] = DN_CHANNELS[dn_channel]

    model = pd.DataFrame({"time": pd.to_numeric(raw["time"], errors="coerce")})
    used: dict[str, str] = {}
    for key, candidates in columns.items():
        series, name = first_column(raw, candidates)
        model[key] = np.nan if series is None else series
        if name:
            used[key] = name

    # Report how far apart the two d_n channels are on THIS run. They coincide
    # for the ppfix Barton-Bandis decks and diverge for the Mohr-Coulomb ones;
    # surfacing it here is what stops the asymmetry from being invisible again.
    dn_divergence = dn_recovery_split(raw)

    # Sample the last output row at or before each stage time.
    #
    # A run that stops a fraction of an output interval short of the final stage time is not a
    # truncated run -- it is a completed run whose last CSV row simply predates the schedule's
    # final point. SW-S3 hits this exactly: end_time = 4802 against a schedule whose last knot is
    # at 4802.4 s, which silently dropped stage 11 (the end of unloading) from every SW-S3 score
    # in the campaign. Allow a grace window of two output intervals and record where it was used;
    # a genuinely truncated run misses by hundreds of seconds and still scores None.
    dt_out = float(np.median(np.diff(model["time"]))) if len(model) > 2 else 0.0
    grace = 2.0 * dt_out
    rows, clamped = [], []
    for t in times:
        if t > t_end + grace:
            rows.append(None)
            clamped.append(False)
            continue
        clamped.append(t > t_end)
        rows.append(int(model.index[model["time"] <= min(t, t_end)][-1]))

    out = pd.DataFrame({
        "stage": range(1, 12),
        "segment": SEGMENTS,
        "Pi_target_MPa": PI_TARGETS,
        "stage_time_s": times,
        "sample_time_s": [np.nan if r is None else float(model["time"].iloc[r]) for r in rows],
        "Pi_model_MPa": [np.nan if r is None else float(model["Pi_MPa"].iloc[r]) for r in rows],
        "sample_clamped": clamped,
    })

    paper = TABLE2[sample]
    for key in SCORED + INFORMATIONAL:
        out[key + "_paper"] = paper[key]
        out[key + "_model"] = [np.nan if r is None else float(model[key].iloc[r]) for r in rows]

    # Displacement datum.
    if datum == "stage1":
        offsets = {k: out[k + "_model"].iloc[0] for k in ("dn_mm", "ds_mm")}
    else:
        ref = int(model.index[(model["time"] - preload_time).abs().idxmin()])
        offsets = {k: float(model[k].iloc[ref]) for k in ("dn_mm", "ds_mm")}
    for k, off in offsets.items():
        if np.isfinite(off):
            out[k + "_model"] = out[k + "_model"] - off

    for key in SCORED + INFORMATIONAL:
        out[key + "_err"] = out[key + "_model"] - out[key + "_paper"]
        denom = out[key + "_paper"].abs()
        out[key + "_pct"] = np.where(denom > 1e-12, 100.0 * out[key + "_err"] / denom, np.nan)

    reached = int(out["sample_time_s"].notna().sum())
    return {
        "csv": csv_path, "deck": deck, "sample": sample, "table": out,
        "t_end": t_end, "reached": reached, "used": used,
        "datum": datum, "offsets": offsets,
        "dn_channel": dn_channel, "dn_divergence": dn_divergence,
    }


def summarise(res: dict) -> pd.DataFrame:
    """Per-observable error summary over the stages the run actually reached.

    Stage 1 is dropped for the two displacements when the stage-1 datum is in
    use, because it is zero there by construction and would flatter the mean.
    """
    out = res["table"]
    rows = []
    for key in SCORED:
        sub = out
        if res["datum"] == "stage1" and key in ("dn_mm", "ds_mm"):
            sub = out.iloc[1:]
        err = sub[key + "_err"].dropna()
        pct = sub[key + "_pct"].replace([np.inf, -np.inf], np.nan).dropna()
        rows.append({
            "observable": key,
            "n": len(err),
            "mean_abs_err": err.abs().mean() if len(err) else np.nan,
            "rmse": float(np.sqrt((err ** 2).mean())) if len(err) else np.nan,
            "max_abs_err": err.abs().max() if len(err) else np.nan,
            "mean_abs_pct": pct.abs().mean() if len(pct) else np.nan,
            "gate": GATE_WIDTH.get(key, np.nan),
            "in_gate": (f"{int((err.abs() <= GATE_WIDTH[key]).sum())}/{len(err)}"
                        if key in GATE_WIDTH and len(err) else "-"),
        })
    return pd.DataFrame(rows)


def normalised_scores(res: dict) -> dict[str, float]:
    """Return the campaign's range-normalised RMSE percentages.

    This is the metric used by ``TABLE2_ERROR_ACCURACY_RANKING.csv``.  Keep it
    next to ``score_run`` so ranking generators and one-off checks cannot drift
    into subtly different normalisation or displacement-datum conventions.
    """
    if res["reached"] != len(PI_TARGETS):
        return {}

    out = res["table"]
    scores: dict[str, float] = {}
    for key in SCORED:
        sub = out.iloc[1:] if res["datum"] == "stage1" and key in ("dn_mm", "ds_mm") else out
        err = sub[key + "_err"].dropna()
        paper_range = float(np.ptp(TABLE2[res["sample"]][key]))
        if len(err) == 0 or paper_range <= 0.0:
            return {}
        scores[key] = 100.0 * float(np.sqrt((err ** 2).mean())) / paper_range
    scores["mean"] = float(np.mean(list(scores.values())))
    scores["accuracy"] = 100.0 - scores["mean"]
    return scores


def fmt(v, width=10, prec=4):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return " " * (width - 1) + "-"
    return f"{v:>{width}.{prec}g}"


def print_run(res: dict) -> None:
    out = res["table"]
    print(f"\n{'=' * 100}")
    print(f"{res['sample']}  {res['csv'].name}")
    print(f"  deck        {res['deck'].name}")
    print(f"  run end     t = {res['t_end']:.1f} s;  stages reached {res['reached']}/11")
    cl = res["table"].loc[res["table"]["sample_clamped"], "stage"].tolist()
    if cl:
        print(f"  NOTE        stage(s) {cl} sampled at the run's last row, within two output "
              f"intervals of the schedule time (run ended marginally short, not truncated)")
    print(f"  datum       {res['datum']} "
          f"(dn offset {res['offsets']['dn_mm']:.6g} mm, ds offset {res['offsets']['ds_mm']:.6g} mm)")
    print(f"  columns     " + ", ".join(f"{k}<-{v}" for k, v in res["used"].items()))
    div = res.get("dn_divergence")
    if div is not None:
        gap = div["recovery_gap_um"]
        flag = "" if abs(gap) < 0.5 else "   <-- channels disagree; see 'The d_n channel'"
        print(f"  d_n channel {res['dn_channel']};  unloading recovery: "
              f"kinematic {div['kinematic']['recovery_um']:+.2f} um, "
              f"normal_opening_total {div['total']['recovery_um']:+.2f} um{flag}")
    print(f"{'=' * 100}")

    hdr = f"{'st':>2} {'seg':<10}{'Pi':>4}{'t_s':>9}{'Pi_mod':>8}"
    for key in SCORED:
        hdr += f"{key.split('_')[0]:>10}{'paper':>10}{'err':>10}"
    print(hdr)
    for _, r in out.iterrows():
        line = (f"{int(r['stage']):>2} {r['segment']:<10}{int(r['Pi_target_MPa']):>4}"
                f"{fmt(r['stage_time_s'], 9, 5)}{fmt(r['Pi_model_MPa'], 8, 4)}")
        for key in SCORED:
            line += (fmt(r[key + '_model']) + fmt(r[key + '_paper']) + fmt(r[key + '_err']))
        print(line)

    print("\n  summary (scored observables only; a_h and k are derived from Q and excluded)")
    s = summarise(res)
    print("   " + s.to_string(index=False).replace("\n", "\n   "))


def print_ab(results: list[dict], labels: list[str]) -> None:
    """Side-by-side: which run is closer to the paper, observable by observable."""
    print(f"\n{'#' * 100}")
    print("A/B  " + "   vs   ".join(labels))
    print(f"{'#' * 100}")

    common = min(r["reached"] for r in results)
    if common < 11:
        print(f"\n  NOTE: only {common}/11 stages are common to all runs; "
              f"the comparison below uses those {common}.")

    header = f"{'observable':<14}{'n':>4}"
    for lab in labels:
        header += f"{lab[:16] + ' MAE':>22}"
    header += f"{'  verdict':<28}"
    print("\n" + header)
    print("-" * len(header))

    for key in SCORED:
        maes, sl = [], slice(1, common) if key in ("dn_mm", "ds_mm") else slice(0, common)
        for r in results:
            err = r["table"][key + "_err"].iloc[sl].dropna()
            maes.append(err.abs().mean() if len(err) else np.nan)
        line = f"{key:<14}{len(err):>4}"
        for m in maes:
            line += fmt(m, 22, 5)
        if len(maes) == 2 and all(np.isfinite(m) for m in maes):
            a, b = maes
            if a == b:
                verdict = "  identical"
            else:
                better = labels[0] if a < b else labels[1]
                ratio = (min(a, b) / max(a, b)) if max(a, b) > 0 else 1.0
                verdict = f"  {better} closer ({100 * (1 - ratio):.1f}% lower)"
            line += verdict
        print(line)

    print("\n  Per-stage error difference (B - A, positive = B further from paper)")
    if len(results) == 2:
        diff = pd.DataFrame({"stage": results[0]["table"]["stage"],
                             "Pi": results[0]["table"]["Pi_target_MPa"],
                             "segment": results[0]["table"]["segment"]})
        for key in SCORED:
            a = results[0]["table"][key + "_err"].abs()
            b = results[1]["table"][key + "_err"].abs()
            diff[key] = b - a
        print("   " + diff.to_string(index=False, float_format=lambda v: f"{v:.4g}")
              .replace("\n", "\n   "))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="+", type=Path, help="one or more results CSVs")
    ap.add_argument("--label", action="append", default=[],
                    help="label for each CSV, in order (defaults to the file stem)")
    ap.add_argument("--sample", choices=sorted(TABLE2), help="override sample detection")
    ap.add_argument("--tag", default="biot_ab_20260815",
                    help="campaign tag to strip when mapping a CSV back to its deck")
    ap.add_argument("--tol-mpa", type=float, default=0.15,
                    help="how close a schedule point must sit to a target to count as that hold")
    ap.add_argument("--datum", choices=["stage1", "preload"], default="stage1")
    ap.add_argument("--dn-channel", choices=sorted(DN_CHANNELS), default=DEFAULT_DN_CHANNEL,
                    help="which normal-displacement channel to score; 'kinematic' (default) is "
                         "the global jump both laws emit, 'total' is the per-material "
                         "normal_opening_total decomposition used before 2026-08-25")
    ap.add_argument("--preload-time", type=float, default=55.0)
    ap.add_argument("--csv-out", type=Path, help="write the per-stage table(s) here")
    args = ap.parse_args()

    results = []
    for path in args.csv:
        if not path.is_file():
            raise SystemExit(f"No such CSV: {path}")
        sample = args.sample or detect_sample(path, find_deck(path, args.tag))
        results.append(score_run(path, sample, args.tag, args.tol_mpa,
                                 args.datum, args.preload_time, args.dn_channel))

    labels = list(args.label) + [r["csv"].stem for r in results[len(args.label):]]

    for res, lab in zip(results, labels):
        res["label"] = lab
        print_run(res)

    if len(results) > 1:
        samples = {r["sample"] for r in results}
        if len(samples) > 1:
            print(f"\nWARNING: comparing across different samples {sorted(samples)}; "
                  "the Table-2 targets differ, so the MAEs are not comparable.")
        cols = [tuple(sorted(r["used"].items())) for r in results]
        if len(set(cols)) > 1:
            print("\nWARNING: the runs resolved different model columns; "
                  "an A/B difference may be a reporting-channel difference.")
        print_ab(results, labels)

    if args.csv_out:
        frames = []
        for res, lab in zip(results, labels):
            f = res["table"].copy()
            f.insert(0, "run", lab)
            f.insert(0, "sample", res["sample"])
            frames.append(f)
        pd.concat(frames, ignore_index=True).to_csv(args.csv_out, index=False)
        print(f"\nwrote {args.csv_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
