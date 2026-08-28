#!/usr/bin/env python3
"""Register and analyse the completed Ye--Ghassemi MC parameter sweep.

The four specimen notebooks deliberately use explicit ``cases`` dictionaries:
only a named case participates in completion checks and plots.  This updater
adds the nine downloaded MC runs to those dictionaries, records the Slurm
overrides that produced each CSV, and updates the cross-specimen MC/BBFast
notebook to use the independently ranked MC winner for each specimen.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
YG = ROOT / "Examples" / "YeGhasemmi2018"

NOTEBOOKS = {
    "SWT1": YG / "SWT1" / "Ye2018_SWT1_num_vs_validation.ipynb",
    "SWT2": YG / "SWT2" / "Ye2018_SWT2_num_vs_validation.ipynb",
    "SWS3": YG / "SWS3" / "Ye2018_SWS3_num_vs_validation.ipynb",
    "SWS4": YG / "SWS4" / "Ye2018_SW4_num_vs_validation.ipynb",
}

TAGS = ("center", "pb01", "pb02", "pb03", "pb04", "pb05", "pb06", "pb07", "pb08")
COLORS = (
    "#111111", "#56B4E9", "#009E73", "#E69F00", "#CC79A7",
    "#0072B2", "#D55E00", "#F0E442", "#999999",
)

PARAMETERS = {
    "SWT1": {
        "mu_r": (0.5536, 0.509312, 0.509312, 0.509312, 0.509312, 0.597888, 0.597888, 0.597888, 0.597888),
        "c_r": (3.7034e7, 3.33306e7, 3.33306e7, 4.07374e7, 4.07374e7, 3.33306e7, 3.33306e7, 4.07374e7, 4.07374e7),
        "mu_s": (0.5717, 0.503096, 0.640304, 0.503096, 0.640304, 0.503096, 0.640304, 0.503096, 0.640304),
        "c_s": (9.19e6, 1.05685e7, 1.05685e7, 7.8115e6, 7.8115e6, 7.8115e6, 7.8115e6, 1.05685e7, 1.05685e7),
        "D_r": (1.5e-4, 1.875e-4, 1.125e-4, 1.875e-4, 1.125e-4, 1.125e-4, 1.875e-4, 1.125e-4, 1.875e-4),
    },
    "SWT2": {
        "mu_r": (0.5528, 0.508576, 0.508576, 0.508576, 0.508576, 0.597024, 0.597024, 0.597024, 0.597024),
        "c_r": (4.2959e7, 3.86631e7, 3.86631e7, 4.72549e7, 4.72549e7, 3.86631e7, 3.86631e7, 4.72549e7, 4.72549e7),
        "mu_s": (0.5717, 0.503096, 0.640304, 0.503096, 0.640304, 0.503096, 0.640304, 0.503096, 0.640304),
        "c_s": (9.71e6, 1.11665e7, 1.11665e7, 8.2535e6, 8.2535e6, 8.2535e6, 8.2535e6, 1.11665e7, 1.11665e7),
        "D_r": (1.5e-4, 1.875e-4, 1.125e-4, 1.875e-4, 1.125e-4, 1.125e-4, 1.875e-4, 1.125e-4, 1.875e-4),
    },
    "SWS3": {
        "mu_r": (0.8818, 0.811256, 0.811256, 0.811256, 0.811256, 0.952344, 0.952344, 0.952344, 0.952344),
        "c_r": (2.645e6, 2.3805e6, 2.3805e6, 2.9095e6, 2.9095e6, 2.3805e6, 2.3805e6, 2.9095e6, 2.9095e6),
        "mu_s": (0.1486, 0.130768, 0.166432, 0.130768, 0.166432, 0.130768, 0.166432, 0.130768, 0.166432),
        "c_s": (1.4e6, 1.61e6, 1.61e6, 1.19e6, 1.19e6, 1.19e6, 1.19e6, 1.61e6, 1.61e6),
        "D_r": (4e-5, 5e-5, 3e-5, 5e-5, 3e-5, 3e-5, 5e-5, 3e-5, 5e-5),
    },
    "SWS4": {
        "mu_r": (0.9804, 0.901968, 0.901968, 0.901968, 0.901968, 1.058832, 1.058832, 1.058832, 1.058832),
        "c_r": (3.225e6, 2.9025e6, 2.9025e6, 3.5475e6, 3.5475e6, 2.9025e6, 2.9025e6, 3.5475e6, 3.5475e6),
        "mu_s": (0.1139, 0.100232, 0.127568, 0.100232, 0.127568, 0.100232, 0.127568, 0.100232, 0.127568),
        "c_s": (0.0,) * 9,
        "D_r": (8e-5, 1e-4, 6e-5, 1e-4, 6e-5, 6e-5, 1e-4, 6e-5, 1e-4),
    },
}


def source(cell: dict) -> str:
    return "".join(cell.get("source", []))


def set_source(cell: dict, text: str) -> None:
    cell["source"] = text.splitlines(keepends=True)


def mc_entries(sample: str) -> str:
    lines = [
        "    # Completed 2026-08-27 MC equal-budget sweep.  Every entry is explicit so it can",
        "    # be ranked, reordered, or removed without filesystem auto-discovery.",
    ]
    params = PARAMETERS[sample]
    for i, (tag, color) in enumerate(zip(TAGS, COLORS)):
        name = f"{sample}_OrcaMohrCoulombContactTraction_{tag}"
        values = {key: vals[i] for key, vals in params.items()}
        lines.extend(
            [
                f"    {name!r}: {{",
                f"        'csv': MC_RESULTS / {name + '.csv'!r},",
                "        'input': MC_INPUT,",
                "        'style': ':',",
                f"        'color': {color!r},",
                "        'kind': 'mc_parameter_sweep',",
                "        'required': True,",
                f"        'sweep_tag': {tag!r},",
                f"        'parameters': {values!r},",
                "    },",
            ]
        )
    return "\n".join(lines) + "\n"


def update_specimen_notebook(sample: str, path: Path) -> None:
    nb = json.loads(path.read_text())
    setup = source(nb["cells"][1])
    if "mc_parameter_sweep" in setup:
        # Idempotent repair pass for notebooks already registered by this
        # updater.  The campaign cleanup retired the old consolidated-artifact
        # files and moved the extracted Table-2 files beside the output
        # notebooks.  Also accommodate SW-S4's older summary-column spelling.
        legacy_index = next(
            (i for i, cell in enumerate(nb["cells"])
             if cell.get("cell_type") == "code"
             and "CONSOLIDATED_ANALYSIS_PATH" in source(cell)),
            None,
        )
        if legacy_index is not None:
            set_source(
                nb["cells"][legacy_index],
                "print('Legacy consolidated ranking artifacts were retired; the live authoritative Table-2 ranking is executed at the end of this notebook.')\n",
            )
            nb["cells"][legacy_index]["execution_count"] = None
            nb["cells"][legacy_index]["outputs"] = []

        for cell in nb["cells"]:
            text = source(cell)
            text = text.replace(
                "BASE.parent / 'Extracted_Data' / 'Table2_4_Sample_CSV_Files'",
                "BASE.parent / 'Output_Image_Comparison' / 'Extracted_Data' / 'Table2_4_Sample_CSV_Files'",
            )
            text = text.replace(
                "assert mc_integrity['reached_input_end'].all(), 'At least one selected MC run is truncated.'",
                "reach_column = ('reached_input_end' if 'reached_input_end' in mc_integrity "
                "else 'reached_intended_end_time')\n"
                "assert mc_integrity[reach_column].all(), 'At least one selected MC run is truncated.'",
            )
            set_source(cell, text)

        path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
        return

    setup = setup.replace(
        "RESULTS = BASE / 'results_csv'\nHPC_RESULTS = BASE / 'results_csv_hpc_rorqual'",
        "RESULTS = BASE / 'results_csv'\n"
        "SWEEPS = BASE / 'Sweeps'\n"
        "HPC_RESULTS = SWEEPS / 'results_csv_hpc_rorqual'",
    )
    setup = setup.replace(
        "LOCAL_RESULTS = BASE / 'results_csv_local'",
        "LOCAL_RESULTS = SWEEPS / 'results_csv_local'",
    )
    old_result_dirs = (
        "RESULT_DIRS = [RESULTS, HPC_RESULTS, LOCAL_RESULTS]"
        if sample == "SWT1"
        else "RESULT_DIRS = [RESULTS, HPC_RESULTS]"
    )
    setup = setup.replace(
        old_result_dirs,
        old_result_dirs.replace("]", ", MC_RESULTS]")
        .replace("RESULT_DIRS", "MC_RESULTS = BASE / 'results_csv_mc_sweep_hpc'\n"
                 f"MC_INPUT = BASE / '{sample}_OrcaMohrCoulombContactTraction.i'\n"
                 "RESULT_DIRS"),
    )
    setup = setup.replace(
        "input_decks = sorted(BASE.glob('*.i'))",
        "input_decks = sorted([*BASE.glob('*.i'), *SWEEPS.glob('*.i')])",
    )

    # The campaign cleanup moved historical decks/results under Sweeps.  Keep
    # the existing manual selections valid while adding the new base-level MC deck.
    before_cases, after_cases = setup.split("cases = {", 1)
    case_body, after_selected = after_cases.split("\n}\n\nselected_cases", 1)
    case_body = case_body.replace("'input': BASE /", "'input': SWEEPS /")
    setup = (
        before_cases
        + "cases = {"
        + case_body
        + "\n\n"
        + mc_entries(sample)
        + "}\n\nselected_cases"
        + after_selected
    )
    set_source(nb["cells"][1], setup)

    # The normal notebook summary now enforces the downloaded MC integrity
    # checks.  It intentionally selects by dictionary kind, not directory scan.
    summary_index = next(
        i for i, cell in enumerate(nb["cells"])
        if cell.get("cell_type") == "code" and "summary = pd.DataFrame" in source(cell)
    )
    summary_src = source(nb["cells"][summary_index])
    summary_src += """

# Integrity gate for explicitly selected MC sweep cases only.
mc_case_names = {
    name for name, cfg in selected_cases.items()
    if cfg.get('kind') == 'mc_parameter_sweep'
}
mc_integrity = summary.loc[summary['case'].isin(mc_case_names)].copy()
if len(mc_integrity) != len(mc_case_names):
    missing = sorted(mc_case_names.difference(mc_integrity['case']))
    raise AssertionError(f'MC sweep cases were selected but not loaded: {missing}')
assert mc_integrity['reached_input_end'].all(), 'At least one selected MC run is truncated.'
assert (~mc_integrity['csv_is_stale']).all(), 'At least one selected MC CSV predates its input deck.'
assert (~mc_integrity['monitored_nan_or_inf']).all(), 'At least one selected MC run contains NaN/Inf.'
print(f'PASS: all {len(mc_integrity)} explicitly selected MC sweep files reached input end with finite monitored data.')
"""
    set_source(nb["cells"][summary_index], summary_src)

    # Add the authoritative five-independent-channel gate.  The older notebook
    # Table-2 panels are retained for visualization; this block supplies the
    # campaign metric, correct stage-1 datum, and kinematic d_n comparison.
    nb["cells"].extend(
        [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Completed MC sweep: authoritative Table 2 ranking\n",
                    "\n",
                    "This final check scores only cases explicitly present in `cases`. It uses the five independent Table 2 observables, the stage-1 displacement datum, and the common kinematic normal jump. Derived hydraulic aperture and permeability remain plotted above but are not counted twice in the headline score.\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": """
import sys

PROJECT_ROOT = BASE.parents[2]
if str(PROJECT_ROOT / 'scripts') not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))
import table2_gate

authoritative_rows = []
for case_name, cfg in selected_cases.items():
    if case_name not in loaded_cases:
        continue
    tag = cfg.get('sweep_tag')
    result = table2_gate.score_run(
        cfg['csv'], SAMPLE, tag=tag, tol_mpa=0.15,
        datum='stage1', preload_time=55.0, dn_channel='kinematic',
    )
    scores = table2_gate.normalised_scores(result)
    authoritative_rows.append({
        'case': case_name,
        'kind': cfg.get('kind', 'unspecified'),
        'stages': result['reached'],
        'Q nRMSE (%)': scores.get('Q_ml_min', np.nan),
        'effective normal nRMSE (%)': scores.get('sigma_n_MPa', np.nan),
        'shear stress nRMSE (%)': scores.get('tau_MPa', np.nan),
        'normal displacement nRMSE (%)': scores.get('dn_mm', np.nan),
        'shear displacement nRMSE (%)': scores.get('ds_mm', np.nan),
        'mean nRMSE (%)': scores.get('mean', np.nan),
    })

authoritative_ranking = (
    pd.DataFrame(authoritative_rows)
    .sort_values(['mean nRMSE (%)', 'case'], na_position='last')
    .reset_index(drop=True)
)
display(authoritative_ranking.style.format(precision=3))
mc_authoritative = authoritative_ranking.loc[
    authoritative_ranking['kind'].eq('mc_parameter_sweep')
]
assert len(mc_authoritative) == len(mc_case_names)
assert mc_authoritative['stages'].eq(11).all()
print(f"Best completed MC case: {mc_authoritative.iloc[0]['case']} "
      f"({mc_authoritative.iloc[0]['mean nRMSE (%)']:.3f}% mean nRMSE)")
""".lstrip().splitlines(keepends=True),
            },
        ]
    )
    path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
    # Apply path/legacy compatibility changes through the idempotent branch.
    update_specimen_notebook(sample, path)


def update_comparison_notebook() -> None:
    path = YG / "Output_Image_Comparison" / "All_fracture_samples_mc_vs_bbfast_comparison.ipynb"
    nb = json.loads(path.read_text())

    replacements = {
        0: """# Best tuned Mohr–Coulomb versus final BBFast comparison

This notebook compares the completed 2026-08-27 nine-run Mohr–Coulomb (MC)
parameter sweep with the final BBFast result for SW-T1, SW-T2, SW-S3, and
SW-S4. It retains every MC run in the integrity/ranking table and selects the
best MC case only after applying the same authoritative Table-2 metric.

The headline metric uses eleven ordered pressure stages, the stage-1
displacement datum, and five independent observables: flow rate, effective
normal stress, shear stress, normal displacement, and shear displacement.
Hydraulic aperture and permeability are derived from flow and are not counted
again. The normal-displacement channel is the global kinematic jump measured
by the experiment for both constitutive laws.
""",
        2: """## Matched cases and sweep parameters

The final BBFast selections are compared with the independently lowest-error
MC sweep member. The center MC run is retained as a control: it reproduces the
older 102-series behavior closely and isolates the improvement caused by the
new strength/onset sweep. Three selected MC optima lie on the tested parameter
bounds, which is reported explicitly rather than treated as proof of a global
optimum.
""",
        3: """PAIR_SPECS = {
    "SWT1": {
        "display": "SW-T1",
        "bb_case": "107_01_swt1_coh27p2_apscale0p01512_ppfix",
        "bb_csv": "Examples/YeGhasemmi2018/SWT1/Sweeps/results_csv_local/107_01_swt1_coh27p2_apscale0p01512_ppfix.csv",
        "mc_case": "SWT1_OrcaMohrCoulombContactTraction_pb04",
        "mc_tag": "pb04",
        "mc_csv": "Examples/YeGhasemmi2018/SWT1/results_csv_mc_sweep_hpc/SWT1_OrcaMohrCoulombContactTraction_pb04.csv",
        "center_case": "SWT1_OrcaMohrCoulombContactTraction_center",
        "center_csv": "Examples/YeGhasemmi2018/SWT1/results_csv_mc_sweep_hpc/SWT1_OrcaMohrCoulombContactTraction_center.csv",
        "best_parameters": "low mu_r, high c_r, high mu_s, low c_s, low D_r",
    },
    "SWT2": {
        "display": "SW-T2",
        "bb_case": "100_04_swt2_apscale0p0177_ppfix",
        "bb_csv": "Examples/YeGhasemmi2018/SWT2/Sweeps/results_csv_hpc_rorqual/100_04_swt2_apscale0p0177_ppfix_hpc.csv",
        "mc_case": "SWT2_OrcaMohrCoulombContactTraction_pb04",
        "mc_tag": "pb04",
        "mc_csv": "Examples/YeGhasemmi2018/SWT2/results_csv_mc_sweep_hpc/SWT2_OrcaMohrCoulombContactTraction_pb04.csv",
        "center_case": "SWT2_OrcaMohrCoulombContactTraction_center",
        "center_csv": "Examples/YeGhasemmi2018/SWT2/results_csv_mc_sweep_hpc/SWT2_OrcaMohrCoulombContactTraction_center.csv",
        "best_parameters": "low mu_r, high c_r, high mu_s, low c_s, low D_r",
    },
    "SWS3": {
        "display": "SW-S3",
        "bb_case": "100_06_sw3_resc1p30_unld0p00_ppfix",
        "bb_csv": "Examples/YeGhasemmi2018/SWS3/Sweeps/results_csv_hpc_rorqual/100_06_sw3_resc1p30_unld0p00_ppfix_hpc.csv",
        "mc_case": "SWS3_OrcaMohrCoulombContactTraction_pb06",
        "mc_tag": "pb06",
        "mc_csv": "Examples/YeGhasemmi2018/SWS3/results_csv_mc_sweep_hpc/SWS3_OrcaMohrCoulombContactTraction_pb06.csv",
        "center_case": "SWS3_OrcaMohrCoulombContactTraction_center",
        "center_csv": "Examples/YeGhasemmi2018/SWS3/results_csv_mc_sweep_hpc/SWS3_OrcaMohrCoulombContactTraction_center.csv",
        "best_parameters": "high mu_r, low c_r, high mu_s, low c_s, high D_r",
    },
    "SWS4": {
        "display": "SW-S4",
        "bb_case": "93_07_sw4_final_theta30_jrc5_ppfix",
        "bb_csv": "Examples/YeGhasemmi2018/SWS4/Sweeps/results_csv_hpc_rorqual/93_07_sw4_final_theta30_jrc5_ppfix_hpc.csv",
        "mc_case": "SWS4_OrcaMohrCoulombContactTraction_center",
        "mc_tag": "center",
        "mc_csv": "Examples/YeGhasemmi2018/SWS4/results_csv_mc_sweep_hpc/SWS4_OrcaMohrCoulombContactTraction_center.csv",
        "center_case": "SWS4_OrcaMohrCoulombContactTraction_center",
        "center_csv": "Examples/YeGhasemmi2018/SWS4/results_csv_mc_sweep_hpc/SWS4_OrcaMohrCoulombContactTraction_center.csv",
        "best_parameters": "center point; every tested perturbation was worse",
    },
}

MC_PARAMETER_VALUES = """ + repr(PARAMETERS) + """
MC_TAGS = """ + repr(TAGS) + """

for spec in PAIR_SPECS.values():
    for key in ("bb_csv", "mc_csv", "center_csv"):
        path = ROOT / spec[key]
        if not path.is_file():
            raise FileNotFoundError(path)

pd.DataFrame([{
    "specimen": spec["display"],
    "final BBFast": spec["bb_case"],
    "best tuned MC": spec["mc_case"],
    "best MC parameter corner": spec["best_parameters"],
} for spec in PAIR_SPECS.values()])
""",
        4: """## Result integrity and full-sweep ranking

Every one of the 36 downloaded MC CSVs is checked—not only the four winners.
A result is accepted only if time is nondecreasing, every numeric value is
finite, and the authoritative scorer reaches all eleven Table-2 stages.
Duplicate rows at imposed schedule discontinuities are reported and normalized
by retaining the converged row after the jump. Selection is then the minimum
five-channel mean nRMSE within each specimen.
""",
        5: """def score(path: str, sample: str, tag=None) -> dict:
    return table2_gate.score_run(
        ROOT / path, sample, tag=tag, tol_mpa=0.15,
        datum="stage1", preload_time=55.0, dn_channel="kinematic",
    )


SWEEP_RESULTS = {}
sweep_health_rows = []
sweep_score_rows = []
for sample, spec in PAIR_SPECS.items():
    sample_dir = ROOT / "Examples" / "YeGhasemmi2018" / sample
    params = MC_PARAMETER_VALUES[sample]
    for index, tag in enumerate(MC_TAGS):
        stem = f"{sample}_OrcaMohrCoulombContactTraction_{tag}"
        path = sample_dir / "results_csv_mc_sweep_hpc" / f"{stem}.csv"
        exodus = sample_dir / "results_exodus_mc_sweep_hpc" / f"{stem}.e"
        raw = pd.read_csv(path, low_memory=False)
        numeric = raw.select_dtypes(include=[np.number]).to_numpy()
        result = table2_gate.score_run(
            path, sample, tag=tag, tol_mpa=0.15,
            datum="stage1", preload_time=55.0, dn_channel="kinematic",
        )
        scores = table2_gate.normalised_scores(result)
        SWEEP_RESULTS[(sample, tag)] = result
        sweep_health_rows.append({
            "specimen": spec["display"], "tag": tag, "rows": len(raw),
            "end time (s)": float(raw["time"].iloc[-1]),
            "stages": result["reached"],
            "time monotonic": bool(raw["time"].is_monotonic_increasing),
            "duplicate times": int(raw["time"].duplicated().sum()),
            "non-finite numeric": int((~np.isfinite(numeric)).sum()),
            "Exodus present": exodus.is_file(),
            "Exodus bytes": exodus.stat().st_size if exodus.is_file() else 0,
        })
        sweep_score_rows.append({
            "specimen code": sample, "specimen": spec["display"], "tag": tag,
            "mu rough": params["mu_r"][index], "cohesion rough (Pa)": params["c_r"][index],
            "mu smooth": params["mu_s"][index], "cohesion smooth (Pa)": params["c_s"][index],
            "roughness decay (m)": params["D_r"][index],
            "Q nRMSE (%)": scores["Q_ml_min"],
            "effective normal nRMSE (%)": scores["sigma_n_MPa"],
            "shear stress nRMSE (%)": scores["tau_MPa"],
            "normal displacement nRMSE (%)": scores["dn_mm"],
            "shear displacement nRMSE (%)": scores["ds_mm"],
            "mean nRMSE (%)": scores["mean"],
        })

sweep_health = pd.DataFrame(sweep_health_rows)
sweep_ranking = pd.DataFrame(sweep_score_rows).sort_values(
    ["specimen code", "mean nRMSE (%)"]
).reset_index(drop=True)
assert len(sweep_health) == 36
assert sweep_health["stages"].eq(11).all()
assert sweep_health["time monotonic"].all()
assert sweep_health["non-finite numeric"].eq(0).all()

best_mc = (
    sweep_ranking.sort_values("mean nRMSE (%)")
    .groupby("specimen code", as_index=False).first()
)
expected = {sample: spec["mc_tag"] for sample, spec in PAIR_SPECS.items()}
assert best_mc.set_index("specimen code")["tag"].to_dict() == expected
display(sweep_health)
display(sweep_ranking.style.format(precision=4))
print("PASS: all 36 MC CSVs are complete, finite, score all 11 stages, and the selected winner is independently reproducible.")
print(f"Exodus files present locally: {int(sweep_health['Exodus present'].sum())}/36")

RESULTS = {}
comparison_health_rows = []
for sample, spec in PAIR_SPECS.items():
    RESULTS[sample] = {
        "BBFast": score(spec["bb_csv"], sample),
        "MC best": SWEEP_RESULTS[(sample, spec["mc_tag"])],
        "MC center": SWEEP_RESULTS[(sample, "center")],
    }
    for model, result in RESULTS[sample].items():
        comparison_health_rows.append({
            "specimen": spec["display"], "model": model,
            "end time (s)": result["t_end"], "stages": result["reached"],
        })
display(pd.DataFrame(comparison_health_rows))
""",
        6: """## Headline accuracy comparison

`BB reduction` is $100(1-E_{BB}/E_{MC})$; positive values mean BBFast is more
accurate. The center-to-best change measures what the new MC tuning actually
earned. Changes smaller than 0.1 percentage points should not be interpreted
against the campaign reproducibility floor.
""",
        7: """headline_rows = []
observable_rows = []
for sample, spec in PAIR_SPECS.items():
    scores = {model: table2_gate.normalised_scores(result) for model, result in RESULTS[sample].items()}
    bb, mc, center = scores["BBFast"], scores["MC best"], scores["MC center"]
    headline_rows.append({
        "specimen": spec["display"],
        "BBFast mean nRMSE (%)": bb["mean"],
        "best MC mean nRMSE (%)": mc["mean"],
        "MC center mean nRMSE (%)": center["mean"],
        "MC improvement, center−best (pp)": center["mean"] - mc["mean"],
        "MC/BB error ratio": mc["mean"] / bb["mean"],
        "BB reduction relative to MC (%)": 100.0 * (1.0 - bb["mean"] / mc["mean"]),
    })
    for observable in table2_gate.SCORED:
        observable_rows.append({
            "specimen": spec["display"], "observable": observable,
            "BBFast nRMSE (%)": bb[observable], "MC nRMSE (%)": mc[observable],
            "BB reduction relative to MC (%)": 100.0 * (1.0 - bb[observable] / mc[observable]),
            "better model": "BBFast" if bb[observable] < mc[observable] else "MC",
        })

headline = pd.DataFrame(headline_rows)
observable_scores = pd.DataFrame(observable_rows)
display(headline.style.format(precision=3))
bb_mean = headline["BBFast mean nRMSE (%)"].mean()
mc_mean = headline["best MC mean nRMSE (%)"].mean()
overall_reduction = 100.0 * (1.0 - bb_mean / mc_mean)
print(f"Four-specimen mean: BBFast = {bb_mean:.3f}%, best tuned MC = {mc_mean:.3f}%")
print(f"Tuned MC carries {mc_mean / bb_mean:.2f}x the BBFast error.")
print(f"BBFast reduces mean error by {overall_reduction:.1f}% relative to tuned MC.")
""",
        8: """fig, ax = plt.subplots(figsize=(8.2, 4.2))
x = np.arange(len(headline)); width = 0.36
bb_values = headline["BBFast mean nRMSE (%)"].to_numpy()
mc_values = headline["best MC mean nRMSE (%)"].to_numpy()
bb_bars = ax.bar(x - width / 2, bb_values, width, label="BBFast", color="#0072B2")
mc_bars = ax.bar(x + width / 2, mc_values, width, label="best tuned MC", color="#D55E00")
ax.bar_label(bb_bars, fmt="%.2f", padding=2, fontsize=8)
ax.bar_label(mc_bars, fmt="%.2f", padding=2, fontsize=8)
ax.set_xticks(x, headline["specimen"]); ax.set_ylabel("Mean range-normalised RMSE (%)")
ax.set_title("Final BBFast versus independently selected tuned MC")
ax.grid(axis="y", alpha=0.25); ax.legend(frameon=False)
ax.set_ylim(0, max(mc_values) * 1.22); plt.tight_layout(); plt.show()
""",
        9: """### Interpretation

The completed sweep overturns the earlier claim that scalar MC tuning cannot
repair the premature weakening. The tuned cases reduce the center-point error
strongly for SW-T1, SW-T2, and SW-S3 and place slip at the correct peak stage.
The final BBFast case nevertheless has the lower combined error for every
specimen. The separation is decisive for SW-T1, moderate for SW-T2, and small
for the two saw cuts. Therefore the defensible conclusion is improved overall
accuracy and transferability of BBFast—not universal failure of MC.
""",
        12: """The tuned comparison is deliberately more demanding than the old 102-series baseline comparison. BBFast remains better in the large majority of individual channels, but MC now wins selected channels for the saw cuts. Those exceptions must be reported: they show that the constitutive conclusion comes from the combined response and cross-specimen consistency, not from claiming that BBFast wins every plotted quantity.
""",
        14: source(nb["cells"][14]).replace('["MC 102"]', '["MC best"]').replace('label="MC"', 'label="best tuned MC"').replace('and MC response', 'and tuned-MC response'),
        15: """### What the MC tuning fixed—and what remains

At loading stage 5 the selected MC cases now remain essentially locked for
SW-T1, SW-T2, and SW-S3, just as the experiment and BBFast do. The previous
premature-weakening diagnosis applied to the center/102 parameters, not to the
MC constitutive law after tuning. The remaining tensile-fracture differences
are mainly the post-peak residual traction, normal-displacement recovery, and
hydraulic response.
""",
        16: source(nb["cells"][16]).replace('["MC 102"]', '["MC best"]'),
        17: """The stage table shows that tuned MC can reproduce the onset stage and much of the peak drop. For SW-T1 and SW-T2 it still retains too much post-peak shear traction and gives a less accurate unloading normal-displacement path than BBFast. SW-S3 is close: MC is better in flow and shear displacement, while BBFast retains the lower combined error. SW-S4 is also close and its center point is already the best tested MC member. The contrast is therefore strongest for the rough tensile fracture and weakens toward the saw cuts.

*Normal-displacement channel.* All scores use the global kinematic jump. The MC material's `normal_opening_total` omits its elastic closure term and would report zero unloading recovery; using it would unfairly worsen MC for a reporting-channel reason rather than a physical one.
""",
        18: """## SW-S3 strict-match sensitivity

The headline BBFast result `100_06` includes a zero unloading-retention mechanism without an MC counterpart. The existing `99_06` BBFast run retains the same 1.30 MPa residual cohesion without that additional refinement, so it is also scored as the strictest available constitutive comparator.
""",
        19: """sws3_strict_path = (
    "Examples/YeGhasemmi2018/SWS3/Sweeps/results_csv_hpc_rorqual/"
    "99_06_sw3_resc1p30_ppfix_hpc.csv"
)
sws3_strict = table2_gate.normalised_scores(score(sws3_strict_path, "SWS3"))
sws3_best = table2_gate.normalised_scores(RESULTS["SWS3"]["BBFast"])
sws3_mc = table2_gate.normalised_scores(RESULTS["SWS3"]["MC best"])
pd.DataFrame([
    {"comparison role": "nominal best BBFast", "case": "100_06", "mean nRMSE (%)": sws3_best["mean"]},
    {"comparison role": "strictest available BBFast match", "case": "99_06", "mean nRMSE (%)": sws3_strict["mean"]},
    {"comparison role": "best tuned MC", "case": "pb06", "mean nRMSE (%)": sws3_mc["mean"]},
]).style.format({"mean nRMSE (%)": "{:.3f}"})
""",
        20: """The SW-S3 conclusion is not controlled by the BBFast unloading-retention choice: both BBFast comparators remain below the tuned MC score. The margin is modest, however, so SW-S3 should be presented as supporting evidence rather than the decisive constitutive discriminator.
""",
        22: source(nb["cells"][22]).replace('["MC 102"]', '["MC best"]'),
        23: """## Conclusions for the paper

1. All 36 MC sweep CSV histories are complete, finite, and reach all eleven Table-2 stages; selection bias from truncated histories is excluded. Exodus availability is reported separately and is not inferred from CSV completion.
2. Tuning matters. It removes the premature stage-5 weakening seen in the center/102 cases and reduces the four-specimen MC average to about 5.7% mean nRMSE.
3. The final BBFast cases still have the lower combined error for all four specimens, averaging about 3.5%. The advantage is strongest for SW-T1 and progressively less decisive for SW-T2, SW-S3, and SW-S4.
4. The optimized MC direction is not transferable: both tensile specimens select `pb04`, SWS3 selects the nearly opposite `pb06` corner, and SWS4 selects the center. This specimen-specific retuning burden is part of the evidence for BBFast, alongside its lower error.
5. Do not claim that MC cannot reproduce peak onset or that BBFast wins every observable. The fair claim is that, under an equal nine-run MC tuning budget and a common five-channel metric, BBFast gives the best combined response with a more consistent physically structured law.
6. Because three MC winners lie on design boundaries, these runs establish the best case within the tested design—not a mathematical global MC optimum. A paper should state that scope explicitly.
""",
    }

    for index, text in replacements.items():
        set_source(nb["cells"][index], text)
        if nb["cells"][index].get("cell_type") == "code":
            nb["cells"][index]["execution_count"] = None
            nb["cells"][index]["outputs"] = []

    path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")


def main() -> None:
    for sample, path in NOTEBOOKS.items():
        update_specimen_notebook(sample, path)
        print(path.relative_to(ROOT))
    update_comparison_notebook()
    print((YG / "Output_Image_Comparison" / "All_fracture_samples_mc_vs_bbfast_comparison.ipynb").relative_to(ROOT))


if __name__ == "__main__":
    main()
