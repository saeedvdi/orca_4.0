#!/usr/bin/env python3
"""Score the mesh-3 convergence twins against their mesh-5 finals (task #81).

The mesh-3 runs are a *discretisation* check, not a calibration: the deck is
byte-identical apart from the mesh, so any difference between the pair is
numerical.  Several mesh-3 runs hit the wall clock before ``end_time``, so this
script never compares end states.  It compares the two runs on the **shared
time window only**, and it reports how much of the injection protocol that
window actually covers, so a truncated pair can still be quoted honestly
(``converged over stages 1-N``) instead of silently scored on a short run.

Usage
-----
    python scripts/mesh3_convergence.py              # all pairs
    python scripts/mesh3_convergence.py SWT2         # one specimen
"""

from __future__ import annotations

import csv
import os
import re
import sys

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                    "Examples", "YeGhasemmi2018")

# The four scored channels, in the paper's reporting frame.
CHANNELS = {
    "Q (ml/min)":    "flow_rate_validation_ml_min_pp",
    "sigma'_n (MPa)": "effective_normal_paper_frame_mpa_pp",
    "tau (MPa)":     "shear_stress_paper_frame_mpa_pp",
    "d_n (mm)":      "czm_normal_dilation_paper_mm_pp",
}

# (specimen, mesh-5 final, mesh-3 twin).  Both members of a pair differ only in
# the mesh, so a difference here is discretisation error and nothing else.
PAIRS = [
    ("SWS3", "93_05_sw3_final_resc1p40_ppfix",  "93_06_sw3_final_resc1p40_ppfix_mesh3"),
    ("SWS3", "94_05_sw3_mc_final",              "94_06_sw3_mc_final_mesh3"),
    ("SWS4", "93_07_sw4_final_theta30_jrc5_ppfix",
             "93_08_sw4_final_theta30_jrc5_ppfix_mesh3"),
    ("SWS4", "94_07_sw4_mc_final",              "94_08_sw4_mc_final_mesh3"),
    ("SWT1", "93_01_swt1_final_c26p9_resc9p19_ppfix",
             "93_02_swt1_final_c26p9_resc9p19_ppfix_mesh3"),
    ("SWT1", "94_01_swt1_mc_final",             "94_02_swt1_mc_final_mesh3"),
    ("SWT2", "93_03_swt2_final_theta30_resc9p71_ppfix",
             "93_04_swt2_final_theta30_resc9p71_ppfix_mesh3"),
    ("SWT2", "94_03_swt2_mc_final",             "94_04_swt2_mc_final_mesh3"),
]


def load(spec: str, deck: str) -> dict[str, np.ndarray] | None:
    path = os.path.join(ROOT, spec, "results_csv_hpc_rorqual", deck + "_hpc.csv")
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return None
    out = {}
    for key in rows[0]:
        try:
            out[key] = np.array([float(r[key]) for r in rows])
        except (ValueError, KeyError):
            pass
    return out


def end_time(spec: str, deck: str) -> float | None:
    path = os.path.join(ROOT, spec, deck + ".i")
    if not os.path.exists(path):
        return None
    m = re.search(r"^\s*end_time\s*=\s*([0-9.eE+-]+)", open(path).read(), re.M)
    return float(m.group(1)) if m else None


def coverage(ref: dict[str, np.ndarray], t_cut: float) -> tuple[float, float, float]:
    """How much of the *loading* the shared window actually contains.

    Wall-clock fraction is the wrong measure here.  Every protocol pressurises
    to a peak and then depressurises, so a run that dies at 59 % of ``end_time``
    may still contain the entire pressurisation branch (SW-S3) while one that
    dies at 22 % contains nothing but the preload (SW-T1).  What matters is the
    position of the cut relative to peak injection, and how much of the flow
    response has developed by then.

    Returns ``(pct_of_pressurisation, P_at_cut_MPa, pct_of_Q_range)``.
    """
    t, p = ref["time"], ref["injection_pressure_pp"]
    t_peak = float(t[int(np.argmax(p))])
    pct = 100.0 * min(t_cut / t_peak, 1.0) if t_peak > 0 else float("nan")
    p_cut = float(np.interp(t_cut, t, p)) / 1.0e6
    q = ref.get("flow_rate_validation_ml_min_pp")
    q_pct = float("nan")
    if q is not None and q.max() > 0:
        q_pct = 100.0 * float(np.interp(t_cut, t, q)) / float(q.max())
    return pct, p_cut, q_pct


def compare(spec: str, ref: str, tri: str) -> None:
    a, b = load(spec, ref), load(spec, tri)
    print(f"\n{'=' * 78}\n{spec}   mesh5 = {ref}\n{' ' * len(spec)}   mesh3 = {tri}")
    if a is None or b is None:
        print("  MISSING csv -- skipped")
        return

    et = end_time(spec, tri)
    t5, t3 = a["time"], b["time"]
    t_common = min(t5.max(), t3.max())
    pct = 100.0 * t3.max() / et if et else float("nan")

    cov, p_cut, q_pct = coverage(a, t_common)

    print(f"  mesh3 reached t = {t3.max():.1f} s of {et:.1f} s "
          f"({pct:.1f} % of wall-clock protocol)")
    print(f"  shared window 0 -> {t_common:.1f} s = {cov:.1f} % of the "
          f"pressurisation branch")
    print(f"    at the cut: P_inj = {p_cut:.2f} MPa, "
          f"Q has developed to {q_pct:.1f} % of its full range")
    if pct < 99.5:
        verdict = ("USABLE -- covers the full pressurisation branch"
                   if cov >= 99.0 else
                   "PARTIAL -- misses peak injection" if cov >= 50.0 else
                   "NOT USABLE -- window is preload only, the two meshes "
                   "agree trivially there")
        print(f"  *** TRUNCATED: {verdict} ***")

    grid = np.linspace(t_common * 0.0, t_common, 2000)
    print(f"\n  {'channel':16} {'mesh5 range':>22} {'max |diff|':>11} "
          f"{'rel RMS':>9} {'rel max':>9}")
    for label, col in CHANNELS.items():
        if col not in a or col not in b:
            print(f"  {label:16} -- column absent")
            continue
        v5 = np.interp(grid, t5, a[col])
        v3 = np.interp(grid, t3, b[col])
        scale = np.abs(v5).max()
        if scale <= 0:
            print(f"  {label:16} identically zero in mesh5")
            continue
        d = v3 - v5
        rms = float(np.sqrt(np.mean(d ** 2)) / scale * 100.0)
        mx = float(np.abs(d).max() / scale * 100.0)
        print(f"  {label:16} [{v5.min():9.4g},{v5.max():9.4g}] "
              f"{np.abs(d).max():11.4g} {rms:8.2f}% {mx:8.2f}%")


def matched_stage_score(spec: str, ref: str, tri: str) -> None:
    """Score both meshes against Table 2 over the stages the coarse run reached.

    ``table2_gate.normalised_scores`` deliberately refuses to score a run that
    did not reach all eleven stages, which is right for the campaign ranking and
    useless here.  This re-scores *both* members of the pair over the same
    truncated stage set, with the Table-2 range recomputed over that same set,
    so the two numbers are comparable to each other.

    They are **not** comparable to the eleven-stage scores in the manuscript's
    Table 5 -- different stage set, different normalising range.  Quote the
    delta, never the level.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import table2_gate as g

    res5 = g.score_run(g.Path(os.path.join(ROOT, spec, "results_csv_hpc_rorqual",
                                           ref + "_hpc.csv")),
                       spec, None, 0.25, "stage1", 0.0)
    res3 = g.score_run(g.Path(os.path.join(ROOT, spec, "results_csv_hpc_rorqual",
                                           tri + "_hpc.csv")),
                       spec, None, 0.25, "stage1", 0.0)
    n = int(res3["reached"])
    if n < 2:
        print(f"  matched-stage score: mesh3 reached {n} stage(s) -- not scored")
        return

    print(f"\n  matched-stage nRMSE over stages 1-{n} of 11 "
          f"(range renormalised over those stages; NOT comparable to Table 5)")
    print(f"  {'observable':12} {'mesh5':>9} {'mesh3':>9} {'change':>9}")
    means = {"m5": [], "m3": []}
    for key in g.SCORED:
        rng = float(np.ptp(g.TABLE2[spec][key][:n]))
        if rng <= 0:
            continue
        row = []
        for res in (res5, res3):
            tab = res["table"].iloc[:n]
            if res["datum"] == "stage1" and key in ("dn_mm", "ds_mm"):
                tab = tab.iloc[1:]
            err = tab[key + "_err"].dropna()
            row.append(100.0 * float(np.sqrt((err ** 2).mean())) / rng)
        means["m5"].append(row[0])
        means["m3"].append(row[1])
        print(f"  {key:12} {row[0]:8.2f}% {row[1]:8.2f}% {row[1] - row[0]:+8.2f}")
    m5, m3 = float(np.mean(means["m5"])), float(np.mean(means["m3"]))
    print(f"  {'MEAN':12} {m5:8.2f}% {m3:8.2f}% {m3 - m5:+8.2f}")


def main() -> None:
    want = sys.argv[1:] or None
    for spec, ref, tri in PAIRS:
        if want and spec not in want:
            continue
        compare(spec, ref, tri)
        try:
            matched_stage_score(spec, ref, tri)
        except Exception as exc:            # a missing deck must not kill the sweep
            print(f"  matched-stage score unavailable: {exc}")
    print()


if __name__ == "__main__":
    main()
