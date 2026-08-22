#!/usr/bin/env python3
"""Build the executed-analysis source notebook for the 102 MC/BBFast pairs."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "Examples"
    / "YeGhasemmi2018"
    / "All_fracture_samples_mc_vs_bbfast_comparison.ipynb"
)


def code(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(source.strip())


def markdown(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(source.strip())


def main() -> None:
    notebook = nbf.v4.new_notebook()
    notebook.metadata = {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3"},
    }
    notebook.cells = [
        markdown(
            r"""
# Best-case Mohr–Coulomb versus BBFast comparison

This notebook compares the completed 102-series Mohr–Coulomb (MC) validation
runs with their equivalent best-physical-case Barton–Bandis/BBFast runs for
SW-T1, SW-T2, SW-S3, and SW-S4.

The comparison uses the campaign's authoritative Table-2 gate:

- eleven ordered injection stages;
- the stage-1 displacement datum;
- five independent observables: flow rate $Q$, effective normal stress
  $\sigma'_n$, shear stress $\tau$, normal displacement $d_n$, and shear
  displacement $d_s$;
- range-normalised RMSE (nRMSE) for each observable.

The 102 cases test whether carrying the latest selected scalar refinements onto
the audited 94-series MC transfer changes the constitutive comparison. They are
monotonic validation runs; cyclic and shut-in comparisons require separate
matched schedules.
"""
        ),
        code(
            r"""
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display


def find_project_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "scripts" / "table2_gate.py").is_file():
            return candidate
    raise FileNotFoundError("Could not locate scripts/table2_gate.py")


ROOT = find_project_root(Path.cwd().resolve())
sys.path.insert(0, str(ROOT / "scripts"))
import table2_gate  # noqa: E402

pd.set_option("display.max_columns", 40)
pd.set_option("display.width", 180)
plt.rcParams.update({
    "figure.dpi": 115,
    "font.size": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

print(f"Project root: {ROOT}")
"""
        ),
        markdown(
            r"""
## Matched cases

The BBFast column uses the nominal best physical case from the updated ranking.
The MC column uses the corresponding 102-series transfer. The old 94-series MC
case is retained only to determine whether the new scalar refinement materially
changed the baseline.

SW-S3 requires one qualification: BBFast `100_06` also sets normal unloading
retention to zero, while the MC material has no equivalent parameter. The
already-completed BBFast `99_06` case is therefore also scored below as the
strictest available one-block comparator; no additional SW-S3 run is needed.
"""
        ),
        code(
            r"""
PAIR_SPECS = {
    "SWT1": {
        "display": "SW-T1",
        "bb_case": "100_01_swt1_vm55um_ppfix",
        "bb_csv": "Examples/YeGhasemmi2018/SWT1/results_csv_hpc_rorqual/100_01_swt1_vm55um_ppfix_hpc.csv",
        "mc_case": "102_01_swt1_mc_vm55um_ppfix",
        "mc_csv": "Examples/YeGhasemmi2018/SWT1/results_csv_hpc_rorqual/102_01_swt1_mc_vm55um_ppfix_hpc.csv",
        "old_mc_case": "94_01_swt1_mc_final",
        "old_mc_csv": "Examples/YeGhasemmi2018/SWT1/results_csv_hpc_rorqual/94_01_swt1_mc_final_hpc.csv",
    },
    "SWT2": {
        "display": "SW-T2",
        "bb_case": "100_04_swt2_apscale0p0177_ppfix",
        "bb_csv": "Examples/YeGhasemmi2018/SWT2/results_csv_hpc_rorqual/100_04_swt2_apscale0p0177_ppfix_hpc.csv",
        "mc_case": "102_02_swt2_mc_apscale0p0177_ppfix",
        "mc_csv": "Examples/YeGhasemmi2018/SWT2/results_csv_hpc_rorqual/102_02_swt2_mc_apscale0p0177_ppfix_hpc.csv",
        "old_mc_case": "94_03_swt2_mc_final",
        "old_mc_csv": "Examples/YeGhasemmi2018/SWT2/results_csv_hpc_rorqual/94_03_swt2_mc_final_hpc.csv",
    },
    "SWS3": {
        "display": "SW-S3",
        "bb_case": "100_06_sw3_resc1p30_unld0p00_ppfix",
        "bb_csv": "Examples/YeGhasemmi2018/SWS3/results_csv_hpc_rorqual/100_06_sw3_resc1p30_unld0p00_ppfix_hpc.csv",
        "mc_case": "102_03_sw3_mc_resc1p30_ppfix",
        "mc_csv": "Examples/YeGhasemmi2018/SWS3/results_csv_hpc_rorqual/102_03_sw3_mc_resc1p30_ppfix_hpc.csv",
        "old_mc_case": "94_05_sw3_mc_final",
        "old_mc_csv": "Examples/YeGhasemmi2018/SWS3/results_csv_hpc_rorqual/94_05_sw3_mc_final_hpc.csv",
    },
    "SWS4": {
        "display": "SW-S4",
        "bb_case": "93_07_sw4_final_theta30_jrc5_ppfix",
        "bb_csv": "Examples/YeGhasemmi2018/SWS4/results_csv_hpc_rorqual/93_07_sw4_final_theta30_jrc5_ppfix_hpc.csv",
        "mc_case": "102_04_sw4_mc_theta30_jrc5_ppfix",
        "mc_csv": "Examples/YeGhasemmi2018/SWS4/results_csv_hpc_rorqual/102_04_sw4_mc_theta30_jrc5_ppfix_hpc.csv",
        "old_mc_case": "94_07_sw4_mc_final",
        "old_mc_csv": "Examples/YeGhasemmi2018/SWS4/results_csv_hpc_rorqual/94_07_sw4_mc_final_hpc.csv",
    },
}

for spec in PAIR_SPECS.values():
    for key in ("bb_csv", "mc_csv", "old_mc_csv"):
        path = ROOT / spec[key]
        if not path.is_file():
            raise FileNotFoundError(path)

pd.DataFrame([
    {
        "specimen": spec["display"],
        "best BBFast": spec["bb_case"],
        "MC 102": spec["mc_case"],
        "old MC control": spec["old_mc_case"],
    }
    for spec in PAIR_SPECS.values()
])
"""
        ),
        markdown(
            r"""
## Result integrity

A result is accepted only if its time column is monotonic and unique, every
numeric value is finite, and the schedule scorer reaches all eleven Table-2
stages. These checks separate a completed but inaccurate model from a damaged
or truncated result file.
"""
        ),
        code(
            r"""
def score(path: str, sample: str) -> dict:
    return table2_gate.score_run(
        ROOT / path,
        sample,
        tag=None,
        tol_mpa=0.15,
        datum="stage1",
        preload_time=55.0,
    )


RESULTS = {}
health_rows = []
for sample, spec in PAIR_SPECS.items():
    RESULTS[sample] = {}
    for model, key in (("BBFast", "bb_csv"), ("MC 102", "mc_csv"), ("MC 94", "old_mc_csv")):
        path = ROOT / spec[key]
        raw = pd.read_csv(path, low_memory=False)
        numeric = raw.select_dtypes(include=[np.number]).to_numpy()
        result = score(spec[key], sample)
        RESULTS[sample][model] = result
        health_rows.append({
            "specimen": spec["display"],
            "model": model,
            "rows": len(raw),
            "end time (s)": float(raw["time"].iloc[-1]),
            "stages": f"{result['reached']}/11",
            "time monotonic": bool(raw["time"].is_monotonic_increasing),
            "duplicate times": int(raw["time"].duplicated().sum()),
            "non-finite numeric": int((~np.isfinite(numeric)).sum()),
        })

health = pd.DataFrame(health_rows)
display(health)
assert health["stages"].eq("11/11").all()
assert health["time monotonic"].all()
assert health["duplicate times"].eq(0).all()
assert health["non-finite numeric"].eq(0).all()
print("PASS: all paired and control results are complete and numerically well formed.")
"""
        ),
        markdown(
            r"""
## Headline accuracy comparison

The table below is the primary quantitative comparison. `BB reduction` is
$100(1-E_{BB}/E_{MC})$; positive values mean BBFast is more accurate. The
campaign treats changes smaller than 0.1 percentage points as unresolved
against the reproducibility floor.
"""
        ),
        code(
            r"""
headline_rows = []
observable_rows = []
for sample, spec in PAIR_SPECS.items():
    scores = {
        model: table2_gate.normalised_scores(result)
        for model, result in RESULTS[sample].items()
    }
    bb = scores["BBFast"]
    mc = scores["MC 102"]
    old = scores["MC 94"]
    headline_rows.append({
        "specimen": spec["display"],
        "BBFast mean nRMSE (%)": bb["mean"],
        "MC 102 mean nRMSE (%)": mc["mean"],
        "old MC 94 mean nRMSE (%)": old["mean"],
        "MC change, 102−94 (pp)": mc["mean"] - old["mean"],
        "MC/BB error ratio": mc["mean"] / bb["mean"],
        "BB reduction relative to MC (%)": 100.0 * (1.0 - bb["mean"] / mc["mean"]),
    })
    for observable in table2_gate.SCORED:
        observable_rows.append({
            "specimen": spec["display"],
            "observable": observable,
            "BBFast nRMSE (%)": bb[observable],
            "MC nRMSE (%)": mc[observable],
            "BB reduction relative to MC (%)": 100.0 * (1.0 - bb[observable] / mc[observable]),
            "better model": "BBFast" if bb[observable] < mc[observable] else "MC",
        })

headline = pd.DataFrame(headline_rows)
observable_scores = pd.DataFrame(observable_rows)
display(headline.style.format(precision=3))

bb_mean = headline["BBFast mean nRMSE (%)"].mean()
mc_mean = headline["MC 102 mean nRMSE (%)"].mean()
overall_reduction = 100.0 * (1.0 - bb_mean / mc_mean)
print(f"Four-specimen mean: BBFast = {bb_mean:.3f}%, MC = {mc_mean:.3f}%")
print(f"MC carries {mc_mean / bb_mean:.2f}× the BBFast error.")
print(f"BBFast reduces mean error by {overall_reduction:.1f}% relative to MC.")
"""
        ),
        code(
            r"""
fig, ax = plt.subplots(figsize=(8.2, 4.2))
x = np.arange(len(headline))
width = 0.36
bb_values = headline["BBFast mean nRMSE (%)"].to_numpy()
mc_values = headline["MC 102 mean nRMSE (%)"].to_numpy()

bb_bars = ax.bar(x - width / 2, bb_values, width, label="BBFast", color="#0072B2")
mc_bars = ax.bar(x + width / 2, mc_values, width, label="Mohr–Coulomb", color="#D55E00")
ax.bar_label(bb_bars, fmt="%.2f", padding=2, fontsize=8)
ax.bar_label(mc_bars, fmt="%.2f", padding=2, fontsize=8)
ax.set_xticks(x, headline["specimen"])
ax.set_ylabel("Mean range-normalised RMSE (%)")
ax.set_title("Best-case BBFast versus matched 102-series MC")
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False)
ax.set_ylim(0, max(mc_values) * 1.18)
plt.tight_layout()
plt.show()
"""
        ),
        markdown(
            r"""
### Interpretation

The updated scalar refinements do not rescue the MC baseline. Relative to the
old 94-series MC results, SW-T1 changes by +0.078 percentage points and SW-S4
by −0.004 points, both below the 0.1-point reproducibility floor. The resolved
changes on SW-T2 (+0.220 points) and SW-S3 (+0.273 points) make MC slightly
worse. A further monotonic scalar-tuning run is therefore not justified.

Across the selected pairs, BBFast reduces the four-specimen mean nRMSE from
19.107% to 3.828%, an 80.0% reduction. The improvement is largest on the two
tensile fractures and smallest on the progressive SW-S4 saw-cut response.
"""
        ),
        markdown(
            r"""
## Per-observable comparison

The constitutive conclusion should not rest only on an average. The next table
shows every specimen–observable combination separately.
"""
        ),
        code(
            r"""
observable_pivot = observable_scores.pivot(
    index=["specimen", "observable"],
    columns="better model",
    values="BB reduction relative to MC (%)",
)
display(observable_scores.style.format({
    "BBFast nRMSE (%)": "{:.3f}",
    "MC nRMSE (%)": "{:.3f}",
    "BB reduction relative to MC (%)": "{:+.1f}",
}))

counts = observable_scores["better model"].value_counts()
print(f"BBFast is better in {counts.get('BBFast', 0)}/20 scored specimen-observable pairs.")
print(f"MC is better in {counts.get('MC', 0)}/20 pairs.")
"""
        ),
        markdown(
            r"""
The sole exception is SW-S4 shear slip: MC gives 6.178% nRMSE and BBFast
7.082%. BBFast remains better for SW-S4 flow, effective normal stress, shear
stress, and especially normal dilation. Consequently, the paper should say
**19 of 20 channels improve**, not that every channel improves.
"""
        ),
        markdown(
            r"""
## Where the trajectories separate

The panels retain the eleven ordered stages rather than reducing each curve to
one score. Stage 6 is the peak-pressure hold; stages 7–11 are unloading.
"""
        ),
        code(
            r"""
PLOT_KEYS = [
    ("Q_ml_min", "$Q$ (mL/min)"),
    ("sigma_n_MPa", "$\\sigma'_n$ (MPa)"),
    ("tau_MPa", "$\\tau$ (MPa)"),
    ("dn_mm", "$d_n$ (mm)"),
    ("ds_mm", "$d_s$ (mm)"),
]

fig, axes = plt.subplots(4, 5, figsize=(15, 10), sharex=True, squeeze=False)
for row, (sample, spec) in enumerate(PAIR_SPECS.items()):
    bb = RESULTS[sample]["BBFast"]["table"]
    mc = RESULTS[sample]["MC 102"]["table"]
    stage = bb["stage"].to_numpy()
    for col, (key, label) in enumerate(PLOT_KEYS):
        ax = axes[row, col]
        ax.plot(stage, bb[f"{key}_paper"], "o-", color="#202020", ms=3.5, lw=1.0, label="Experiment")
        ax.plot(stage, bb[f"{key}_model"], "o-", color="#0072B2", ms=3.0, lw=1.2, label="BBFast")
        ax.plot(stage, mc[f"{key}_model"], "s--", color="#D55E00", ms=3.0, lw=1.1, label="MC")
        ax.axvline(6.5, color="#999999", lw=0.7, ls=":")
        ax.grid(alpha=0.2)
        if row == 0:
            ax.set_title(label)
        if col == 0:
            ax.set_ylabel(spec["display"])
        if row == 3:
            ax.set_xlabel("Table-2 stage")
            ax.set_xticks(range(1, 12, 2))

handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.01))
fig.suptitle("Stage-by-stage experimental, BBFast, and MC response", y=1.035, fontsize=12)
plt.tight_layout()
plt.show()
"""
        ),
        markdown(
            r"""
### Premature weakening in MC

For SW-T1, SW-T2, and SW-S3, the decisive separation occurs at loading stage 5,
one pressure stage before the experimental peak event. MC has already generated
most of its final shear displacement, while the experiment and BBFast remain
nearly stuck. The stage-6 endpoints can look reasonable again, but the path
between stages 4 and 6 is incorrect.
"""
        ),
        code(
            r"""
stage5_rows = []
for sample, spec in PAIR_SPECS.items():
    bb = RESULTS[sample]["BBFast"]["table"].iloc[4]
    mc = RESULTS[sample]["MC 102"]["table"].iloc[4]
    stage5_rows.append({
        "specimen": spec["display"],
        "pressure target (MPa)": mc["Pi_target_MPa"],
        "experimental ds (mm)": mc["ds_mm_paper"],
        "BBFast ds (mm)": bb["ds_mm_model"],
        "MC ds (mm)": mc["ds_mm_model"],
        "experimental tau (MPa)": mc["tau_MPa_paper"],
        "BBFast tau (MPa)": bb["tau_MPa_model"],
        "MC tau (MPa)": mc["tau_MPa_model"],
    })

stage5 = pd.DataFrame(stage5_rows)
display(stage5.style.format(precision=3))
"""
        ),
        markdown(
            r"""
This is a constitutive-path discrepancy rather than a failed simulation. The
linear MC transfer is matched to BBFast at onset, but its single evolving
roughness state cannot reproduce the separate peak-to-residual strength and
dilation histories carried by BBFast. Closure and aperture-scale adjustments
change the hydraulic response but do not move the premature MC weakening onto
the measured stage.

SW-S4 behaves differently: slip develops progressively, and MC follows shear
displacement slightly better. Its normal-dilation trajectory remains much
worse, so the specimen still favours BBFast in the combined score.
"""
        ),
        markdown(
            r"""
## SW-S3 strict-match sensitivity

The headline comparison uses the nominal best BBFast result, `100_06`, even
though its zero unloading-retention mechanism has no MC counterpart. For a
strictest-available constitutive comparison, use the existing `99_06` BBFast
result, which shares the 1.30 MPa residual cohesion without that extra best-case
unloading refinement.
"""
        ),
        code(
            r"""
sws3_strict_path = (
    "Examples/YeGhasemmi2018/SWS3/results_csv_hpc_rorqual/"
    "99_06_sw3_resc1p30_ppfix_hpc.csv"
)
sws3_strict = table2_gate.normalised_scores(score(sws3_strict_path, "SWS3"))
sws3_best = table2_gate.normalised_scores(RESULTS["SWS3"]["BBFast"])
sws3_mc = table2_gate.normalised_scores(RESULTS["SWS3"]["MC 102"])

pd.DataFrame([
    {"comparison role": "nominal best BBFast", "case": "100_06", "mean nRMSE (%)": sws3_best["mean"]},
    {"comparison role": "strictest available BBFast match", "case": "99_06", "mean nRMSE (%)": sws3_strict["mean"]},
    {"comparison role": "MC", "case": "102_03", "mean nRMSE (%)": sws3_mc["mean"]},
]).style.format({"mean nRMSE (%)": "{:.3f}"})
"""
        ),
        markdown(
            r"""
The SW-S3 conclusion is insensitive to this choice: BBFast scores 4.354% using
the nominal best case or 4.451% using the strict comparator, versus 18.744% for
MC. The existing result therefore resolves the caveat without a new run.
"""
        ),
        markdown(
            r"""
## Detailed stage tables

These tables preserve the numerical values used in every plotted trajectory.
Displacements are expressed relative to stage 1, matching the campaign score.
"""
        ),
        code(
            r"""
for sample, spec in PAIR_SPECS.items():
    bb = RESULTS[sample]["BBFast"]["table"]
    mc = RESULTS[sample]["MC 102"]["table"]
    detail = pd.DataFrame({
        "stage": bb["stage"],
        "branch": bb["segment"],
        "Pi target (MPa)": bb["Pi_target_MPa"],
    })
    for key, short in (
        ("Q_ml_min", "Q"),
        ("sigma_n_MPa", "sigma_n"),
        ("tau_MPa", "tau"),
        ("dn_mm", "dn"),
        ("ds_mm", "ds"),
    ):
        detail[f"{short} experiment"] = bb[f"{key}_paper"]
        detail[f"{short} BBFast"] = bb[f"{key}_model"]
        detail[f"{short} MC"] = mc[f"{key}_model"]
    print(spec["display"])
    display(detail.style.format(precision=4))
"""
        ),
        markdown(
            r"""
## Conclusions for the paper

1. All four 102-series MC simulations are complete and scoreable; their poor
   agreement is not caused by truncation or damaged output.
2. For the updated best-case pairs, BBFast lowers the four-specimen mean nRMSE
   from **19.107% to 3.828%**, an **80.0% reduction**.
3. BBFast is more accurate in **19 of 20** specimen–observable comparisons.
   The exception is SW-S4 shear displacement, where MC is modestly better.
4. The large SW-T1, SW-T2, and SW-S3 error is created by premature MC
   weakening at loading stage 5, not by the final post-slip endpoint alone.
5. The 102 refinements do not support another monotonic MC tuning run. The
   model discrepancy lies in the weakening/dilation path that the comparison
   is intended to test.
6. These results complete the **monotonic** comparison only. A direct
   MC-versus-BBFast cyclic or shut-in claim requires matched MC versions of the
   101-series schedules and should not be inferred from this notebook.
"""
        ),
    ]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, OUTPUT)
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
