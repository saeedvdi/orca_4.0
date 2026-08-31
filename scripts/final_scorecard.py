#!/usr/bin/env python3
"""
Score the Ye & Ghassemi (2018) decks of record -- Barton-Bandis and the equal-budget
Mohr-Coulomb baseline -- and print the table the manuscript quotes.

The eight runs below are the campaign's final selection, from
Examples/YeGhasemmi2018/Docs/Final_ye_ghaseemi_simulations.txt, section
"AUTHORITATIVE FINAL SELECTION AND IMPROVEMENT AUDIT -- 2026-08-27". Scoring is
delegated to scripts/table2_gate.py so there is one implementation of the metric:
range-normalised RMSE per channel over the eleven Table-2 hold stages, stage-1 datum
for the two displacements, arithmetic mean over the five scored channels.

The d_n channel is the global kinematic jump for BOTH laws (the 2026-08-25 correction).
The two constitutive materials decompose their reported normal opening differently, so
scoring the local channel charged the Mohr-Coulomb baseline for a missing reporting term
rather than for a modelling error.

Usage:
    python3 scripts/final_scorecard.py [--csv]
"""

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import table2_gate as gate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
YE = ROOT / "Examples/YeGhasemmi2018"

JRC = {"SWT1": 15.32, "SWT2": 14.63, "SWS3": 1.96, "SWS4": 1.19}
LABEL = {"SWT1": "SW-T1", "SWT2": "SW-T2", "SWS3": "SW-S3", "SWS4": "SW-S4"}

BB = {
    "SWT1": "SWT1/Sweeps/results_csv_local/107_01_swt1_coh27p2_apscale0p01512_ppfix.csv",
    "SWT2": "SWT2/Sweeps/results_csv_hpc_rorqual/100_04_swt2_apscale0p0177_ppfix_hpc.csv",
    "SWS3": "SWS3/Sweeps/results_csv_hpc_rorqual/100_06_sw3_resc1p30_unld0p00_ppfix_hpc.csv",
    "SWS4": "SWS4/Sweeps/results_csv_hpc_rorqual/93_07_sw4_final_theta30_jrc5_ppfix_hpc.csv",
}
MC = {
    "SWT1": "SWT1/results_csv_mc_sweep_hpc/SWT1_OrcaMohrCoulombContactTraction_pb04.csv",
    "SWT2": "SWT2/results_csv_mc_sweep_hpc/SWT2_OrcaMohrCoulombContactTraction_pb04.csv",
    "SWS3": "SWS3/results_csv_mc_sweep_hpc/SWS3_OrcaMohrCoulombContactTraction_pb06.csv",
    "SWS4": "SWS4/results_csv_mc_sweep_hpc/SWS4_OrcaMohrCoulombContactTraction_center.csv",
}

CHANNELS = ["Q_ml_min", "sigma_n_MPa", "tau_MPa", "dn_mm", "ds_mm"]


def one(sample, rel):
    path = YE / rel
    if not path.exists():
        return None
    # The Mohr-Coulomb sweep writes <deck>_<tag>.csv beside a single generic deck in the
    # specimen root, so the trailing token is the campaign tag, not part of the deck name.
    tag = None
    m = re.search(r"_(pb\d+|center)$", path.stem)
    if m:
        tag = m.group(1)
    res = gate.score_run(path, sample, tag, 0.15, "stage1", 55.0)
    sc = gate.normalised_scores(res)
    if sc is None or "mean" not in sc:
        return None
    out = {c: sc.get(c) for c in CHANNELS}
    out["mean"] = sc["mean"]
    out["reached"] = res["reached"]
    out["deck"] = Path(rel).stem.replace("_hpc", "")
    return out


def main():
    rows = []
    for sample in ("SWT1", "SWT2", "SWS3", "SWS4"):
        bb, mc = one(sample, BB[sample]), one(sample, MC[sample])
        rows.append(dict(sample=sample, bb=bb, mc=mc))

    if "--csv" in sys.argv[1:]:
        recs = []
        for r in rows:
            for law, d in (("barton_bandis", r["bb"]), ("mohr_coulomb", r["mc"])):
                if d:
                    recs.append(dict(sample=LABEL[r["sample"]], law=law, deck=d["deck"],
                                     stages=d["reached"],
                                     **{c: d[c] for c in CHANNELS}, mean=d["mean"]))
        pd.DataFrame(recs).to_csv(sys.stdout, index=False)
        return

    def f(v, w=9):
        return " " * (w - 1) + "-" if v is None else f"{v:{w}.3f}"

    print("Ye & Ghassemi (2018) decks of record. Range-normalised RMSE per channel, %.")
    print("d_n uses the global kinematic jump for both laws.\n")
    hdr = (f"{'specimen':10s}{'law':16s}{'stg':>5}{'Q':>9}{'sigma_n':>9}{'tau':>9}"
           f"{'d_n':>9}{'d_s':>9}{'mean':>9}")
    print(hdr)
    print("-" * len(hdr))
    bb_means, mc_means = [], []
    for r in rows:
        for name, d in (("Barton-Bandis", r["bb"]), ("Mohr-Coulomb", r["mc"])):
            if not d:
                print(f"{LABEL[r['sample']] if name.startswith('B') else '':10s}{name:16s}  MISSING")
                continue
            print(f"{LABEL[r['sample']] if name.startswith('B') else '':10s}{name:16s}"
                  f"{d['reached']:>3d}/11" + "".join(f(d[c]) for c in CHANNELS) + f(d["mean"]))
            (bb_means if name.startswith("B") else mc_means).append(d["mean"])
        if r["bb"] and r["mc"]:
            print(f"{'':10s}{'gain (MC/BB)':16s}{'':5s}" + " " * 45 +
                  f"{r['mc']['mean'] / r['bb']['mean']:9.2f}x")
        print()

    if bb_means:
        print(f"campaign mean, Barton-Bandis  {sum(bb_means) / len(bb_means):.3f} %")
    if mc_means:
        print(f"campaign mean, Mohr-Coulomb   {sum(mc_means) / len(mc_means):.3f} %")
    print("\nJRC ordering of the gain (it should track roughness):")
    for r in sorted(rows, key=lambda r: -JRC[r["sample"]]):
        if r["bb"] and r["mc"]:
            print(f"  {LABEL[r['sample']]}  JRC {JRC[r['sample']]:5.2f}"
                  f"   gain {r['mc']['mean'] / r['bb']['mean']:5.2f}x")


if __name__ == "__main__":
    main()
