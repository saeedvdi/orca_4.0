#!/usr/bin/env python3
"""
Fit the Pedrosa (1986) law k = k0 exp(-alpha * sigma'_n) to the Ye & Ghassemi (2018)
specimens, separately on the pressurization and depressurization branches, and compare
against Kalantar et al. (2025) Figure 8.

WHY THIS IS AN INDEPENDENT CHECK
--------------------------------
Kalantar et al. (2025) section 4.2 / Figure 8 fits this two-parameter law twice per
specimen -- once pre-slip, once post-slip. Panels (a) and (d) are their own OG-T and
OG-SC. Panels (b), (c), (e) and (f) are a REANALYSIS OF YE & GHASSEMI'S SW-T1, SW-T2,
SW-S3 and SW-S4: the same four specimens this repository calibrates, reduced by a
different group with a different method, and published after our decks were built.

The ratio k0_post / k0_pre is the self-propping gain -- how much of the injection-induced
permeability enhancement survives once the fracture is re-clamped. It is the quantity the
Ye & Ghassemi protocol was never designed to report and that Table 2 does not tabulate, so
it is a genuinely out-of-sample target for a model calibrated against Table 2.

METHOD
------
Stage sampling is delegated to scripts/table2_gate.py, so the fitted points are exactly
the eleven Table-2 hold stages used for scoring -- no separate sampling convention.

  pre-slip   stages 1-5   (8, 12, 16, 20, 24 MPa pressurization, before the event)
  post-slip  stages 7-11  (24, 20, 16, 12, 8 MPa depressurization, after the event)

Stage 6 is the 28 MPa peak at which the slip event occurs and belongs to neither branch;
it is excluded from both fits and reported separately.

The fit is ordinary least squares of ln k on sigma'_n, which is what makes the law linear;
alpha is the negative slope and k0 the intercept. Reported in Darcy and 1/MPa to match the
paper. r^2 is on the log-transformed variable, as the published fit is.

Running the SAME fit on Table 2 itself (the `paper` rows) reproduces Kalantar's published
numbers from our side and so validates the reduction before the model is judged by it.

Usage:
    python3 scripts/pedrosa_fit_vs_kalantar_fig8.py [--csv]
"""

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import table2_gate as gate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DARCY_M2 = 9.869233e-13

PRE_STAGES = [1, 2, 3, 4, 5]
POST_STAGES = [7, 8, 9, 10, 11]

# The four decks of record, from Examples/YeGhasemmi2018/Docs/Final_ye_ghaseemi_simulations.txt
# ("AUTHORITATIVE FINAL SELECTION AND IMPROVEMENT AUDIT -- 2026-08-27").
FINALS = {
    "SWT1": "Examples/YeGhasemmi2018/SWT1/Sweeps/results_csv_local/"
            "107_01_swt1_coh27p2_apscale0p01512_ppfix.csv",
    "SWT2": "Examples/YeGhasemmi2018/SWT2/Sweeps/results_csv_hpc_rorqual/"
            "100_04_swt2_apscale0p0177_ppfix_hpc.csv",
    "SWS3": "Examples/YeGhasemmi2018/SWS3/Sweeps/results_csv_hpc_rorqual/"
            "100_06_sw3_resc1p30_unld0p00_ppfix_hpc.csv",
    "SWS4": "Examples/YeGhasemmi2018/SWS4/Sweeps/results_csv_hpc_rorqual/"
            "93_07_sw4_final_theta30_jrc5_ppfix_hpc.csv",
}

PAPER_LABEL = {"SWT1": "SW-T1", "SWT2": "SW-T2", "SWS3": "SW-S3", "SWS4": "SW-S4"}

KALANTAR_CSV = ROOT / "Examples/Kalantar2025/validation/kalantar2025_figure8_pedrosa_fits.csv"


def pedrosa_fit(sigma_n_mpa, k_darcy):
    """Least squares of ln k on sigma'_n. Returns (k0 [Darcy], alpha [1/MPa], r2, n)."""
    x = np.asarray(sigma_n_mpa, dtype=float)
    y = np.asarray(k_darcy, dtype=float)
    ok = np.isfinite(x) & np.isfinite(y) & (y > 0)
    x, y = x[ok], y[ok]
    if len(x) < 3:
        return None
    ln_y = np.log(y)
    slope, intercept = np.polyfit(x, ln_y, 1)
    pred = slope * x + intercept
    ss_res = float(np.sum((ln_y - pred) ** 2))
    ss_tot = float(np.sum((ln_y - ln_y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return dict(k0=math.exp(intercept), alpha=-slope, r2=r2, n=len(x))


def branch_fits(table, side):
    """side is 'paper' or 'model'. Returns dict of pre/post/gain."""
    k = table[f"k_1e12_m2_{side}"] * 1e-12 / DARCY_M2
    sn = table[f"sigma_n_MPa_{side}"]
    stage = table["stage"]
    out = {}
    for name, stages in (("pre", PRE_STAGES), ("post", POST_STAGES)):
        sel = stage.isin(stages)
        out[name] = pedrosa_fit(sn[sel], k[sel])
    if out["pre"] and out["post"]:
        out["gain"] = out["post"]["k0"] / out["pre"]["k0"]
    else:
        out["gain"] = None
    return out


def published():
    df = pd.read_csv(KALANTAR_CSV, comment="#")
    df = df[df["source"] == "Ye2018"]
    out = {}
    for label, grp in df.groupby("sample"):
        rec = {}
        for _, r in grp.iterrows():
            key = "pre" if r["branch"].startswith("pre") else "post"
            rec[key] = dict(k0=float(r["k0_darcy"]), alpha=float(r["alpha_per_MPa"]),
                            r2=float(r["r_squared"]))
        if "pre" in rec and "post" in rec:
            rec["gain"] = rec["post"]["k0"] / rec["pre"]["k0"]
        out[label] = rec
    return out


def main():
    as_csv = "--csv" in sys.argv[1:]
    pub = published()
    rows = []

    for sample, rel in FINALS.items():
        csv_path = ROOT / rel
        if not csv_path.exists():
            print(f"{sample}: MISSING {rel}", file=sys.stderr)
            continue
        res = gate.score_run(csv_path, sample, None, 0.15, "stage1", 55.0)
        table = res["table"]
        if int(table["sample_time_s"].notna().sum()) < 11:
            print(f"{sample}: incomplete run, {res['reached']}/11 stages -- skipped",
                  file=sys.stderr)
            continue
        model = branch_fits(table, "model")
        paper = branch_fits(table, "paper")
        label = PAPER_LABEL[sample]
        rows.append(dict(sample=label, model=model, paper=paper, pub=pub.get(label, {}),
                         csv=rel))

    if as_csv:
        recs = []
        for r in rows:
            for side, d in (("model", r["model"]), ("table2_refit", r["paper"])):
                for br in ("pre", "post"):
                    if d[br]:
                        recs.append(dict(sample=r["sample"], side=side, branch=br,
                                         k0_darcy=d[br]["k0"], alpha_per_MPa=d[br]["alpha"],
                                         r2=d[br]["r2"], n=d[br]["n"]))
            for br in ("pre", "post"):
                if br in r["pub"]:
                    recs.append(dict(sample=r["sample"], side="kalantar_fig8", branch=br,
                                     k0_darcy=r["pub"][br]["k0"],
                                     alpha_per_MPa=r["pub"][br]["alpha"],
                                     r2=r["pub"][br]["r2"], n=np.nan))
        pd.DataFrame(recs).to_csv(sys.stdout, index=False)
        return

    def f(v, w=8, p=3):
        return " " * (w - 1) + "-" if v is None or not np.isfinite(v) else f"{v:{w}.{p}f}"

    print("Pedrosa k = k0 exp(-alpha sigma'_n) fitted to the eleven Table-2 stages.")
    print("pre = stages 1-5 (pressurization), post = stages 7-11 (depressurization);")
    print("stage 6, the 28 MPa peak where the event occurs, is excluded from both.\n")

    hdr = (f"{'specimen':10s}{'source':16s}{'k0 pre':>9}{'k0 post':>9}{'gain':>8}"
           f"{'a pre':>9}{'a post':>9}{'r2 pre':>8}{'r2 post':>9}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        for name, d in (("model", r["model"]),
                        ("Table 2 refit", r["paper"]),
                        ("Kalantar Fig 8", r["pub"])):
            pre, post = d.get("pre"), d.get("post")
            if not pre or not post:
                continue
            print(f"{r['sample'] if name == 'model' else '':10s}{name:16s}"
                  f"{f(pre['k0'], 9)}{f(post['k0'], 9)}{f(d.get('gain'), 8, 2)}"
                  f"{f(pre['alpha'], 9, 4)}{f(post['alpha'], 9, 4)}"
                  f"{f(pre.get('r2'), 8, 2)}{f(post.get('r2'), 9, 2)}")
        print()

    print("READING IT.")
    print("  gain = k0_post / k0_pre is the self-propping gain. It is NOT a Table-2")
    print("  observable, so agreement with the Kalantar column is out-of-sample.")
    print("  'Table 2 refit' applies the identical fit to the published data, so any")
    print("  disagreement between it and the Kalantar column is a reduction-method")
    print("  difference, not a model error -- read it before judging the model row.")


if __name__ == "__main__":
    main()
