#!/usr/bin/env python3
"""
kalantar_gate.py -- score a 110-series run against Kalantar et al. (2025) Table 2.

Reuses table2_gate's stage-walking machinery (parse the deck's own injection
schedule, find each hold plateau, sample the last output row at or before the end
of the hold) so a Kalantar run and a Ye2018 run are read the same way.

WHAT IS DIFFERENT FROM table2_gate, AND WHY
===========================================
1. THE SCORED CHANNELS ARE NOT THE SAME ON EVERY SPECIMEN.

   On Ye2018, Q was the well-resolved channel. Here it is not, and which channel
   to trust depends on the specimen. Table 2 prints Q to three decimals in mL/min:

       OG-SH   0.461 - 3.614 mL/min    every stage has 3+ significant figures
       OG-SC   0.006 - 0.438           most stages have 1-2
       OG-T    0.000 - 0.109           several stages are 0.000 or 0.001

   Since a_h ~ Q^(1/3), a Q printed as 0.001 carries roughly +/-14 % in aperture
   from rounding alone, and 0.000 carries no information at all. Meanwhile a_h is
   printed to 2 decimals in um on every stage. So on OG-T and OG-SC the aperture
   column is the HIGH-precision measurement and Q is the derived, degraded one --
   the reverse of Ye2018. Scoring Q equally on all three specimens would let
   OG-T's rounding noise dominate the verdict.

   Stages whose Q is below Q_FLOOR are dropped from the Q channel only; they still
   score on stress, aperture and slip.

2. THERE IS NO NORMAL-DISPLACEMENT COLUMN AT ALL.

   Ye2018's d_n was the least redundant channel per
   `ye2018-q-is-a-stress-readout-not-an-aperture-one`. Kalantar reports shear
   displacement (dL_s, eq 6, frame-corrected) and no normal component, so the
   aperture law is constrained here only through a_h. Expect this validation to be
   weaker on the aperture law and stronger on slip than Ye2018 was.

3. OG-T IS SCORED IN THE 28-DEGREE FRAME.

   Table 2's stress columns for OG-T were reduced at 25.999 deg, which the geometry
   cannot realise (see the journal headers and audit section 6). The stresses are
   re-reduced here to the 28 deg the specimen actually is, by recovering
   sigma_1 - sigma_3 from the printed tau and re-projecting. tau scales by a
   constant 1.0521; sigma'_n does NOT, because only its deviatoric part moves.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd

from table2_gate import (MODEL_COLUMNS, first_column, fmt, parse_schedule,
                         stage_times)

ROOT = Path(__file__).resolve().parents[1]
TABLE2_CSV = ROOT / "Examples/Kalantar2025/validation/kalantar2025_table2.csv"

P_OUT_MPA = 3.0
SIGMA3_MPA = 33.0
THETA_TABLE2 = {"OG-SH": 29.0, "OG-T": 25.999, "OG-SC": 30.0}   # the REDUCTION angle
THETA_DECK = {"OG-SH": 29.0, "OG-T": 28.0, "OG-SC": 30.0}       # the SPECIMEN angle

# Below this, Table 2's printed Q has fewer than two significant figures.
Q_FLOOR_ML_MIN = 0.010

SCORED_ALWAYS = ["sigma_n_MPa", "tau_MPa", "ah_um", "ds_mm"]
SCORED_IF_RESOLVED = ["Q_ml_min"]

KAL_COLUMNS = dict(MODEL_COLUMNS)
KAL_COLUMNS["ds_mm"] = [("reported_czm_shear_slip_mm_pp", 1.0),
                        ("czm_shear_slip_mm_pp", 1.0)]


def reference(sample: str) -> pd.DataFrame:
    """Table 2 for one specimen, re-reduced to the deck's fracture angle."""
    raw = pd.read_csv(TABLE2_CSV, comment="#")
    frame = raw[raw["sample"] == sample].copy().reset_index(drop=True)

    th_t2 = math.radians(THETA_TABLE2[sample])
    th_dk = math.radians(THETA_DECK[sample])
    pore = (frame["P_i_MPa"] + P_OUT_MPA) / 2.0
    # tau = (s1 - s3) sin cos  ->  recover the deviator, then re-project.
    deviator = frame["tau_MPa"] / (math.sin(th_t2) * math.cos(th_t2))
    frame["tau_MPa"] = deviator * math.sin(th_dk) * math.cos(th_dk)
    frame["sigma_n_MPa"] = (SIGMA3_MPA - pore) + deviator * math.sin(th_dk) ** 2

    frame = frame.rename(columns={"Q_ml_min": "Q_ml_min", "a_h_um": "ah_um",
                                  "dLs_mm": "ds_mm"})
    frame["Pi_MPa"] = frame["P_i_MPa"]
    return frame


def score(csv_path: Path, sample: str, deck: Path, tol_mpa: float) -> dict:
    x, y = parse_schedule(deck)
    times = stage_times(x, y, tol_mpa)
    ref = reference(sample)
    if len(times) != len(ref):
        print(f"  !! deck schedule gives {len(times)} hold stages, Table 2 has "
              f"{len(ref)}. Scoring the overlap only.")
    n = min(len(times), len(ref))

    raw = (pd.read_csv(csv_path).sort_values("time")
           .drop_duplicates("time", keep="last").reset_index(drop=True))
    model = pd.DataFrame({"time": pd.to_numeric(raw["time"], errors="coerce")})
    used = {}
    for key, candidates in KAL_COLUMNS.items():
        series, name = first_column(raw, candidates)
        model[key] = np.nan if series is None else series
        if name:
            used[key] = name

    rows = []
    for i in range(n):
        at = model[model["time"] <= times[i] + 1e-9]
        if at.empty:
            continue
        rows.append(at.iloc[-1])
    got = pd.DataFrame(rows).reset_index(drop=True)

    out = {"sample": sample, "csv": csv_path, "used": used,
           "stages": n, "channels": {}}
    for key in SCORED_ALWAYS + SCORED_IF_RESOLVED:
        if key not in got or got[key].isna().all():
            out["channels"][key] = None
            continue
        obs = ref[key].to_numpy()[:len(got)].astype(float)
        sim = got[key].to_numpy().astype(float)
        mask = np.isfinite(obs) & np.isfinite(sim)
        if key == "Q_ml_min":
            mask &= ref["Q_ml_min"].to_numpy()[:len(got)] >= Q_FLOOR_ML_MIN
        if mask.sum() == 0:
            out["channels"][key] = None
            continue
        span = np.ptp(obs[mask]) or (np.abs(obs[mask]).max() or 1.0)
        out["channels"][key] = {
            "n": int(mask.sum()),
            "nrmse_pct": 100.0 * math.sqrt(np.mean((sim[mask] - obs[mask]) ** 2)) / span,
            "mae": float(np.mean(np.abs(sim[mask] - obs[mask]))),
            "dropped": int(len(obs) - mask.sum()),
        }
    return out


def report(res: dict) -> None:
    print(f"\n{res['sample']}   {res['csv'].name}   {res['stages']} hold stages")
    print(f"  {'channel':<14}{'n':>4}{'dropped':>9}{'nRMSE %':>10}{'MAE':>12}"
          f"   source column")
    scored = []
    for key in SCORED_ALWAYS + SCORED_IF_RESOLVED:
        c = res["channels"].get(key)
        if c is None:
            print(f"  {key:<14}{'--':>4}{'':>9}{'not emitted by the deck':>22}")
            continue
        scored.append(c["nrmse_pct"])
        print(f"  {key:<14}{c['n']:>4}{c['dropped']:>9}{fmt(c['nrmse_pct'],10,2)}"
              f"{fmt(c['mae'],12,4)}   {res['used'].get(key,'?')}")
    if scored:
        print(f"  {'MEAN':<14}{'':>13}{fmt(float(np.mean(scored)),10,2)}")
        print(f"\n  Reproducibility floor is 0.1 percentage points of mean nRMSE "
              f"(orca-cross-machine-reproducibility-floor).\n  Do not rank two runs "
              f"that differ by less than that.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv", nargs="+", type=Path)
    ap.add_argument("--sample", choices=sorted(THETA_DECK))
    ap.add_argument("--deck", type=Path, help="deck whose schedule defines the stages")
    ap.add_argument("--tol-mpa", type=float, default=0.15)
    args = ap.parse_args()

    for path in args.csv:
        sample = args.sample
        if sample is None:
            blob = str(path).lower()
            for code, key in (("og_sh", "OG-SH"), ("og_t", "OG-T"), ("og_sc", "OG-SC")):
                if code in blob:
                    sample = key
            if sample is None:
                raise SystemExit(f"cannot infer specimen from {path}; pass --sample")
        deck = args.deck
        if deck is None:
            guess = sorted(path.parent.parent.glob("110_*.i"))
            if not guess:
                raise SystemExit(f"cannot find the deck for {path}; pass --deck")
            deck = guess[0]
        report(score(path, sample, deck, args.tol_mpa))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
