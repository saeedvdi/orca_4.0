#!/usr/bin/env python3
"""
score_103_control.py -- read the 103 exponent-control runs, finished or not.

    /home/geomechanics/miniforge/bin/python scripts/score_103_control.py

WHY THIS READS PARTIAL RUNS
===========================
The whole question is WHEN the joint yields: at Table-2 stage 5 (as the
transferred Mohr-Coulomb arm does) or at stage 6 (as the calibrated BBFast parent
does).  Stage 6 is roughly 55-65% of the way through each deck, and MOOSE writes
CSV incrementally, so the answer exists long before the run ends.  This script
therefore reports what is decided so far and says plainly what is not yet.

The full five-channel nRMSE still needs all eleven stages and is printed only
once a run has them.

WHAT TO LOOK AT
===============
The `verdict` line.  For each specimen the three arms are:

    parent   the 100-series BBFast best case          (exponent 1.4)
    control  the 103 deck, THE ONLY CHANGE being      (exponent 1.0)
    pair     the 102-series Mohr-Coulomb arm          (exponent 1 by construction)

PREDICTION, pre-registered in the deck headers and in
scripts/build_103_weakening_exponent_decks.py: the control should behave like the
pair, not like its own parent -- yielding a stage early with ~0.5 mm of slip and
shear stress collapsing toward residual while the measurement is still on the
high-strength branch.

FALSIFIER: if the control still holds through stage 5, the weakening exponent is
NOT what places the transition, and the next suspect is the normal-unloading path
(every MC arm's normal jump is frozen after slip: SW-T1 closes 2.0 nm against a
9.6 MPa rise in sigma'_n where its BBFast pair closes 36.4 um).

A partial result is only meaningful once the run has passed its own stage 5 time;
before that the script says so rather than guessing.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import table2_gate as G  # noqa: E402

EX = ROOT / "Examples" / "YeGhasemmi2018"

# sample, 103 control stem, 100-series parent, 102-series MC pair
TRIOS = [
    ("SWT1", "103_01_swt1_weakexp1p0_ppfix",
     "100_01_swt1_vm55um_ppfix", "102_01_swt1_mc_vm55um_ppfix"),
    ("SWT2", "103_02_swt2_weakexp1p0_ppfix",
     "100_04_swt2_apscale0p0177_ppfix", "102_02_swt2_mc_apscale0p0177_ppfix"),
    ("SWS3", "103_03_sw3_weakexp1p0_ppfix",
     "100_06_sw3_resc1p30_unld0p00_ppfix", "102_03_sw3_mc_resc1p30_ppfix"),
]

# Where each arm's CSV lives.  The controls may be running locally; the parents
# and pairs came off the cluster.
SUBDIRS = ["results_csv_local", "results_csv_hpc_rorqual", "results_csv_hpc", "results_csv"]


def find_csv(sample, stem):
    for sub in SUBDIRS:
        for suffix in ("_local", "_hpc", ""):
            p = EX / sample / sub / f"{stem}{suffix}.csv"
            if p.exists():
                return p
    return None


def at(df, t):
    sub = df[df["time"] <= t + 1e-9]
    return None if sub.empty else sub.iloc[-1]


def main():
    for sample, ctrl, parent, pair in TRIOS:
        print("=" * 100)
        print(f"{sample}   control {ctrl}")
        print(f"         parent  {parent}   (exponent 1.4)")
        print(f"         pair    {pair}   (Mohr-Coulomb, exponent 1)")
        print("=" * 100)

        deck = EX / sample / f"{ctrl}.i"
        x, y = G.parse_schedule(deck)
        stages = G.stage_times(x, y, 0.15)
        t5, t6 = stages[4], stages[5]

        arms = {}
        for label, stem in (("parent", parent), ("control", ctrl), ("pair", pair)):
            p = find_csv(sample, stem)
            if p is None:
                print(f"  {label}: no CSV found for {stem}")
                continue
            arms[label] = pd.read_csv(p).sort_values("time")

        if "control" not in arms:
            print()
            continue

        t_now = float(arms["control"]["time"].iloc[-1])
        end = float(G.parse_schedule(deck)[0][-1])
        print(f"  control has reached t = {t_now:.1f} s of {end:.1f} "
              f"({100 * t_now / end:.0f}%);  stage 5 at {t5:.0f} s, stage 6 at {t6:.0f} s")

        if t_now < t5:
            print("  -> not yet past stage 5.  Nothing is decided; re-run this script later.\n")
            continue

        print()
        print(f"  {'':9s}{'stage 5: slip mm':>20s}{'tau MPa':>10s}"
              f"{'   |   stage 6: slip mm':>26s}{'tau MPa':>10s}")
        for label in ("parent", "control", "pair"):
            if label not in arms:
                continue
            r5, r6 = at(arms[label], t5), at(arms[label], t6)
            def fmt(r, col, scale=1.0):
                return "      --" if r is None else f"{r[col] * scale:8.4f}"
            print(f"  {label:9s}{fmt(r5,'reported_czm_shear_slip_mm_pp'):>20s}"
                  f"{fmt(r5,'shear_stress_paper_frame_mpa_pp'):>10s}"
                  f"{fmt(r6,'reported_czm_shear_slip_mm_pp'):>26s}"
                  f"{fmt(r6,'shear_stress_paper_frame_mpa_pp'):>10s}")
        paper = G.TABLE2[sample]
        print(f"  {'measured':9s}{paper['ds_mm'][4]:20.4f}{paper['tau_MPa'][4]:10.4f}"
              f"{paper['ds_mm'][5]:26.4f}{paper['tau_MPa'][5]:10.4f}")

        # --- verdict ---------------------------------------------------------
        s5 = {k: at(v, t5) for k, v in arms.items()}
        if s5.get("control") is not None and s5.get("parent") is not None \
                and s5.get("pair") is not None:
            c = float(s5["control"]["reported_czm_shear_slip_mm_pp"])
            p = float(s5["parent"]["reported_czm_shear_slip_mm_pp"])
            m = float(s5["pair"]["reported_czm_shear_slip_mm_pp"])
            # Which arm is the control closer to, on a log scale (the two differ
            # by orders of magnitude, so a linear distance would be meaningless).
            lp, lm, lc = (np.log10(max(v, 1e-9)) for v in (p, m, c))
            near = "its PARENT (exponent is not the mechanism)" if abs(lc - lp) < abs(lc - lm) \
                else "its MC PAIR (exponent IS the mechanism)"
            print()
            print(f"  verdict at stage 5: control slip {c:.4f} mm vs parent {p:.4f} "
                  f"and pair {m:.4f}  ->  control resembles {near}")

        # --- full score, only if all eleven stages are there ------------------
        print()
        for label, stem in (("parent", parent), ("control", ctrl), ("pair", pair)):
            if label not in arms:
                continue
            res = G.score_run(find_csv(sample, stem), sample,
                              "biot_ab_20260815", 0.15, "stage1", 55.0)
            sc = G.normalised_scores(res)
            if sc:
                print(f"  {label:9s} mean nRMSE {sc['mean']:7.3f}%   "
                      + "  ".join(f"{k.split('_')[0]}={sc[k]:6.3f}" for k in G.SCORED))
            else:
                print(f"  {label:9s} {res['reached']}/11 stages -- not scoreable yet")
        print()


if __name__ == "__main__":
    main()
