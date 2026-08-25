#!/usr/bin/env python3
"""
kalantar_gate.py -- score a 110-series run against Kalantar et al. (2025) Table 2.

Reads a run the same way table2_gate does -- parse the deck's own injection
schedule, find each hold plateau, sample the last output row at or before the end
of the hold -- but walks the stages against Table 2's own (branch, P_i) columns.
table2_gate.stage_times cannot be reused directly: it hard-codes Ye2018's eleven
targets, so on a Kalantar schedule it goes looking for a 24 MPa loading stage that
does not exist.

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

   So OG-SH is scored on Q and the other two on a_h. Stages whose Q is below
   Q_FLOOR are dropped from the Q channel only; they are still reported.

2. THERE IS NO NORMAL-DISPLACEMENT COLUMN AT ALL.

   Ye2018's d_n was the least redundant channel per
   `ye2018-q-is-a-stress-readout-not-an-aperture-one`. Kalantar reports shear
   displacement (dL_s, eq 6, frame-corrected) and no normal component, so the
   aperture law is constrained here only through a_h -- and dL_s turns out to be a
   readout of tau rather than an independent channel, see (4). Expect this
   validation to be weaker on the aperture law than Ye2018 was, not stronger.

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

from table2_gate import MODEL_COLUMNS, first_column, fmt, parse_schedule

ROOT = Path(__file__).resolve().parents[1]
TABLE2_CSV = ROOT / "Examples/Kalantar2025/validation/kalantar2025_table2.csv"

P_OUT_MPA = 3.0
SIGMA3_MPA = 33.0
THETA_TABLE2 = {"OG-SH": 29.0, "OG-T": 25.999, "OG-SC": 30.0}   # the REDUCTION angle
THETA_DECK = {"OG-SH": 29.0, "OG-T": 28.0, "OG-SC": 30.0}       # the SPECIMEN angle

# Below this, Table 2's printed Q has fewer than two significant figures.
Q_FLOOR_ML_MIN = 0.010

# ---------------------------------------------------------------------------
# 4. TABLE 2 HOLDS TWO INDEPENDENT MEASUREMENTS PER STAGE, NOT FIVE.
#
# The rig runs at constant piston displacement, so eq (6) with dL = 0 plus eq (4)
# gives an ALGEBRAIC identity, not a correlation:
#
#     dL_s = -A dtau / (K_sys sin(theta) cos(theta))
#
# Checked against Table 2 (predicted vs fitted slope): OG-T 0.9999 at r = -1.0000,
# OG-SC 0.9962, OG-SH 1.0416 -- the last inside its own 1 um print resolution.
# And sigma'_n and tau are both affine in sigma_1, so they are one measurement too.
#
# So sigma'_n, tau and dL_s are THREE READOUTS OF THE SAME FORCE. Scoring all of
# them and taking the mean counts one defect three times, which is how the first
# version of this script was written. It now scores ONE force channel and ONE
# flow channel; the rest are printed as diagnostics and excluded from the mean.
#
# dL_s in particular is a FRAME check, not a physics check: with axial_bc_penalty
# set to K_sys/A -- which the builder does -- any deck that gets tau(t) right gets
# dL_s(t) for free. Its expected slope is printed beside it; a deviation there
# means the penalty is wrong, not that the joint law is.
#
# One more asymmetry: dL_s is axial SHORTENING, delta*cos(theta), while the model
# reports in-plane slip. The 1/cos(theta) factor is applied below.
# ---------------------------------------------------------------------------
SCORED_FORCE = "tau_MPa"
# Which flow channel carries the information depends on the specimen -- see (1).
SCORED_FLOW = {"OG-SH": "Q_ml_min", "OG-T": "ah_um", "OG-SC": "ah_um"}
DIAGNOSTIC = ["sigma_n_MPa", "ah_um", "Q_ml_min", "ds_mm"]

KAL_COLUMNS = dict(MODEL_COLUMNS)
KAL_COLUMNS["ds_mm"] = [("reported_czm_shear_slip_mm_pp", 1.0),
                        ("czm_shear_slip_mm_pp", 1.0)]

K_SYS = 796e3 / 1e-3
SAMPLE_AREA = math.pi * 0.02499 ** 2


def expected_dtau_dls(sample: str) -> float:
    """MPa of tau per um of axial shortening, from the series-spring identity."""
    th = math.radians(THETA_DECK[sample])
    return K_SYS * math.sin(th) * math.cos(th) / SAMPLE_AREA / 1e12


def kal_stage_times(x: np.ndarray, y: np.ndarray, ref: pd.DataFrame,
                    tol_mpa: float) -> list[float]:
    """End of each Table-2 hold plateau, in stage order.

    table2_gate.stage_times cannot be reused: it hard-codes Ye2018's eleven
    (segment, target) pairs, so on a Kalantar schedule it walks off looking for a
    24 MPa loading stage that does not exist. Here the targets come from Table 2's
    own P_i and branch columns, which is exact rather than assumed.

    The schedule is split at its peak plateau so a loading target and the
    same-valued unloading target cannot be confused, and a monotonic cursor keeps
    the times strictly increasing.
    """
    peak = float(np.max(y))
    at_peak = np.flatnonzero(np.abs(y - peak) <= 1e-6 * max(1.0, abs(peak)))
    peak_start, peak_end = int(at_peak[0]), int(at_peak[-1])

    times: list[float] = []
    cursor = -math.inf
    for _, row in ref.iterrows():
        target = row["Pi_MPa"]        # parse_schedule returns y in MPa
        loading = row["branch"] == "pressurization"
        lo, hi = (0, peak_start) if loading else (peak_end, len(x) - 1)
        idx = np.arange(lo, hi + 1)
        idx = idx[x[idx] > cursor]
        hit = idx[np.abs(y[idx] - target) <= tol_mpa]
        if hit.size == 0:
            raise SystemExit(f"no schedule point at {row['Pi_MPa']:g} MPa on the "
                             f"{row['branch']} branch after t={cursor:g}s")
        # END of the plateau: the last consecutive point still at this level.
        j = int(hit[0])
        while j + 1 < len(x) and abs(y[j + 1] - target) <= tol_mpa:
            j += 1
        times.append(float(x[j]))
        cursor = float(x[j])
    return times


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
    ref = reference(sample)
    times = kal_stage_times(x, y, ref, tol_mpa)
    if len(times) != len(ref):
        print(f"  !! deck schedule gives {len(times)} hold stages, Table 2 has "
              f"{len(ref)}. Scoring the overlap only.")
    n = min(len(times), len(ref))

    raw = (pd.read_csv(csv_path).sort_values("time")
           .drop_duplicates("time", keep="last").reset_index(drop=True))
    t_end = float(pd.to_numeric(raw["time"], errors="coerce").max())
    deck_end = float(x[-1])
    complete_pct = 100.0 * t_end / deck_end if deck_end else 100.0
    complete = t_end >= deck_end - 1e-9
    model = pd.DataFrame({"time": pd.to_numeric(raw["time"], errors="coerce")})
    used = {}
    for key, candidates in KAL_COLUMNS.items():
        series, name = first_column(raw, candidates)
        model[key] = np.nan if series is None else series
        if name:
            used[key] = name

    rows = []
    reached = 0
    for i in range(n):
        # Never recycle the last available CSV row into holds that the run did not
        # reach.  Before this guard, a truncated OG-T round-5 snapshot at t=3305.5 s
        # was silently repeated through all later holds and printed a plausible but
        # invalid 17-stage score.
        if times[i] > t_end + 1e-9:
            break
        at = model[model["time"] <= times[i] + 1e-9]
        if at.empty:
            continue
        rows.append(at.iloc[-1])
        reached += 1
    got = pd.DataFrame(rows).reset_index(drop=True)

    scored_keys = [SCORED_FORCE, SCORED_FLOW[sample]]
    out = {"sample": sample, "csv": csv_path, "used": used, "stages": n,
           "reached_stages": reached, "t_end": t_end, "deck_end": deck_end,
           "complete_pct": complete_pct, "complete": complete,
           "scored": scored_keys, "channels": {}}
    cos_t = math.cos(math.radians(THETA_DECK[sample]))
    for key in dict.fromkeys(scored_keys + DIAGNOSTIC):
        if key not in got or got[key].isna().all():
            out["channels"][key] = None
            continue
        obs = ref[key].to_numpy()[:len(got)].astype(float)
        sim = got[key].to_numpy().astype(float)
        # Table 2's dL_s is axial shortening = delta cos(theta); the model reports
        # in-plane slip. Put the measurement into the model's frame, not the reverse.
        if key == "ds_mm":
            obs = obs / cos_t
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
            "bias": float(np.mean(sim[mask] - obs[mask])),
            "dropped": int(len(obs) - mask.sum()),
        }
    return out


def report(res: dict) -> None:
    sample = res["sample"]
    state = ("complete" if res["complete"] else
             f"INCOMPLETE {res['complete_pct']:.1f}% -- diagnostics only, NOT SCOREABLE")
    print(f"\n{sample}   {res['csv'].name}   {res['reached_stages']}/"
          f"{res['stages']} hold stages   [{state}]")
    print(f"  {'channel':<14}{'n':>4}{'drop':>6}{'nRMSE %':>10}{'MAE':>12}"
          f"{'bias':>12}   source column")
    scored = []
    for key in dict.fromkeys(res["scored"] + DIAGNOSTIC):
        mark = "*" if key in res["scored"] and res["complete"] else " "
        c = res["channels"].get(key)
        if c is None:
            print(f" {mark}{key:<14}{'--':>4}{'not emitted by the deck':>28}")
            continue
        if key in res["scored"] and res["complete"]:
            scored.append(c["nrmse_pct"])
        print(f" {mark}{key:<14}{c['n']:>4}{c['dropped']:>6}{fmt(c['nrmse_pct'],10,2)}"
              f"{fmt(c['mae'],12,4)}{fmt(c['bias'],12,4)}   {res['used'].get(key,'?')}")
    if scored:
        print(f"  {'MEAN (* only)':<14}{'':>20}{fmt(float(np.mean(scored)),10,2)}")
    elif not res["complete"]:
        print("  NO SCORE: the run has not reached the deck end time; channel values "
              "above are reached-stage diagnostics only.")
    star_note = "* = SCORED" if res["complete"] else "* would be scored only after completion"
    print(f"\n  {star_note}. One force channel ({SCORED_FORCE}) and one flow channel "
          f"({SCORED_FLOW[sample]}).\n    The others are readouts of the same two "
          f"measurements and are shown for diagnosis only:\n    sigma'_n and tau are "
          f"both affine in sigma_1, and constant-piston-displacement\n    control makes "
          f"dL_s an exact algebraic readout of tau.")
    print(f"    Expected d(tau)/d(dL_s) = {expected_dtau_dls(sample):.4f} MPa/um. A "
          f"deviation on ds_mm\n    means axial_bc_penalty is wrong, not the joint law.")
    print(f"    Reproducibility floor is 0.1 pp of mean nRMSE "
          f"(orca-cross-machine-reproducibility-floor);\n    do not rank two runs that "
          f"differ by less than that.")


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
