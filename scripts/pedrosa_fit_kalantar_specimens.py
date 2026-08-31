#!/usr/bin/env python3
"""
Fit the Pedrosa (1986) law k = k0 exp(-alpha sigma'_n) to Kalantar et al. (2025)'s OWN
specimens -- their Table 2 and our simulations of it -- and compare against their Figure 8.

The companion script `pedrosa_fit_vs_kalantar_fig8.py` does this for the four Ye & Ghassemi
specimens, using Kalantar's REANALYSIS of them (Figure 8 panels b, c, e, f). This one uses
Figure 8 panels (a) and (d), which are Kalantar's own OG-T and OG-SC, and adds the model.

WHY THIS IS THE OUT-OF-SAMPLE TEST THE SELF-PROPPING CLAIM NEEDS
----------------------------------------------------------------
k0_post/k0_pre is the self-propping gain and alpha_post/alpha_pre is how much more
stress-sensitive the propped fracture is. Kalantar's central result is that BOTH rise: the
gain is real but it is not retained, because alpha roughly doubles. That is the same
question this repository's Ye manuscript asks in its retained-aperture sections, measured
on a different rock by a different group.

Neither number is in Kalantar's Table 2, so neither was available to the calibration. The
aperture-law constants of the OG-SH deck have never been changed since round 1, and OG-SC's
were changed once (V_m and K_ni, re-anchored to Kalantar's own sigma_0/V_m). So the model
side of this comparison is a prediction, not a fit.

BRANCHES
--------
Fitting needs the slip event excluded from both branches. Read off Table 2's own tau column:

  OG-SC   pre 1-6, EVENT 7 (tau 12.95 -> 9.73), post 8-13
  OG-T    pre 1-6, EVENT 7-9 (tau 65.73 -> 62.49 -> 39.14 -> 21.80), post 10-17

OG-SH has no Figure 8 entry -- it never slipped in a single event, so the pre/post split
does not apply and it is excluded here. It carries the flow validation instead.

WHICH k TO FIT -- this was got wrong once and the error was large
-----------------------------------------------------------------
Fit Table 2's own printed `k_D` column, NOT a_h^2/12. Kalantar's Figure 8 fits k_D, and only
k_D reproduces it: on OG-SC's pressurization branch k_D gives k0 = 0.813 D, alpha = 0.0450
against their published 0.82 and 0.05, while a_h^2/12 gives 6.025 and 0.1156 -- wrong by 7x
and 2.3x. The two columns agree wherever k_D has resolution and diverge where it does not
(k_D is printed to 2 dp and pins at 0.17 over OG-SC's first three stages and at 0.02-0.03
over OG-T's first six).

WHY k0 IS NOT THE HEADLINE NUMBER
---------------------------------
k0 is the fit extrapolated to sigma'_n = 0, which is 25-60 MPa outside every branch in the
dataset, so it is exquisitely sensitive to alpha. Changing the k source moves OG-SC's
pre-branch k0 by 7x and OG-T's by eight orders of magnitude. Kalantar's own r^2 = 0.42 on
OG-T pre-slip, and the 0.06 printed on OG-T post-slip, report the same instability from
their side.

So this script reports three things and the paper should quote the last two:

  1. k0 and the k0 gain, for comparability with Figure 8 as published.
  2. alpha and the alpha RATIO -- dimensionless, no extrapolation.
  3. The permeability gain evaluated at MATCHED sigma'_n inside the common data window,
     which is an interpolation. On OG-SC this is the interesting number: it is BELOW 1,
     so the apparent 6-8x enhancement lives entirely in the extrapolation and the
     enhancement at matched stress is a stress-path effect, not retained aperture. That is
     the same conclusion the manuscript's own frame caveat reaches for the Ye specimens,
     reached here on another group's published fit.

Usage:
    python3 scripts/pedrosa_fit_kalantar_specimens.py [--csv OUT.csv]
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import kalantar_gate as kal  # noqa: E402
from table2_gate import first_column, parse_schedule  # noqa: E402

DARCY_M2 = 9.869233e-13

BRANCHES = {           # (pre stages, event stages, post stages) -- 1-based, Table 2 order
    "OG-SC": (list(range(1, 7)), [7], list(range(8, 14))),
    "OG-T":  (list(range(1, 7)), [7, 8, 9], list(range(10, 18))),
}

RUNS = {               # model runs, when they exist
    "OG-SC": ("Examples/Kalantar2025/OGSC/results_csv_hpc/110_15_og_sc_bbfast_r6_hpc.csv",
              "Examples/Kalantar2025/OGSC/110_15_og_sc_bbfast_r6.i"),
    "OG-T":  ("Examples/Kalantar2025/OGT/results_csv_hpc/110_30_og_t_platen_bonded_r11_hpc.csv",
              "Examples/Kalantar2025/OGT/110_30_og_t_platen_bonded_r11.i"),
}

FIG8 = {               # Kalantar Figure 8 panels (a) and (d), as published
    ("OG-T", "pre"):  (1.91, 0.08), ("OG-T", "post"):  (4.73, 0.16),
    ("OG-SC", "pre"): (0.82, 0.05), ("OG-SC", "post"): (5.25, 0.11),
}


def pedrosa(sigma_n_mpa, k_darcy):
    """OLS of ln k on sigma'_n. Returns dict with k0 [Darcy], alpha [1/MPa], r^2, n, range."""
    s = np.asarray(sigma_n_mpa, float)
    k = np.asarray(k_darcy, float)
    ok = np.isfinite(s) & np.isfinite(k) & (k > 0)
    s, k = s[ok], k[ok]
    if len(s) < 2:
        return None
    y = np.log(k)
    slope, intercept = np.polyfit(s, y, 1)
    pred = slope * s + intercept
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    return dict(k0=float(np.exp(intercept)), alpha=float(-slope),
                r2=1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan,
                n=len(s), lo=float(s.min()), hi=float(s.max()))


def model_at_stages(sample):
    """Sample the model at Table 2's own hold stages, as kalantar_gate does."""
    csv, deck = RUNS[sample]
    csv, deck = ROOT / csv, ROOT / deck
    if not csv.is_file():
        return None
    x, y = parse_schedule(deck)
    ref = kal.reference(sample)
    times = kal.kal_stage_times(x, y, ref, 0.15)
    raw = (pd.read_csv(csv).sort_values("time")
           .drop_duplicates("time", keep="last").reset_index(drop=True))
    t_end = float(pd.to_numeric(raw["time"], errors="coerce").max())
    frame = pd.DataFrame({"time": pd.to_numeric(raw["time"], errors="coerce")})
    for key, cands in kal.KAL_COLUMNS.items():
        series, _ = first_column(raw, cands)
        frame[key] = np.nan if series is None else series
    rows, reached = [], []
    for i, t in enumerate(times[:len(ref)]):
        if t > t_end + 1e-9:
            break
        at = frame[frame["time"] <= t + 1e-9]
        if at.empty:
            continue
        rows.append(at.iloc[-1])
        reached.append(int(ref["stage"][i]))
    if not rows:
        return None
    got = pd.DataFrame(rows).reset_index(drop=True)
    got["stage"] = reached
    got["complete"] = t_end >= float(x[-1]) - 1e-9
    return got


def fit_side(stages_frame, stage_col, sigma_col, k_col, want, k_scale):
    sel = stages_frame[stages_frame[stage_col].isin(want)]
    return pedrosa(sel[sigma_col].to_numpy(float),
                   sel[k_col].to_numpy(float) * k_scale)


def gain_at(fits, branch_pre, branch_post, sigma_n):
    p, q = fits[branch_pre], fits[branch_post]
    return ((q["k0"] * np.exp(-q["alpha"] * sigma_n)) /
            (p["k0"] * np.exp(-p["alpha"] * sigma_n)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=None)
    args = ap.parse_args()

    out = []
    for sample, (pre, event, post) in BRANCHES.items():
        ref = kal.reference(sample)
        print("=" * 100)
        print(f"{sample}   pre = stages {pre[0]}-{pre[-1]},  event = {event},  "
              f"post = stages {post[0]}-{post[-1]}")
        print("=" * 100)
        fits = {}

        # measured: Kalantar's own printed k_D column, in Darcy already
        for branch, want in (("pre", pre), ("post", post)):
            fits[("measured", branch)] = fit_side(ref, "stage", "sigma_n_eff_MPa",
                                                  "k_D", want, 1.0)
        for branch in ("pre", "post"):
            fits[("published", branch)] = dict(zip(("k0", "alpha"), FIG8[(sample, branch)]),
                                               r2=np.nan, n=np.nan, lo=np.nan, hi=np.nan)

        got = model_at_stages(sample)
        model_ok = got is not None and bool(got["complete"].iloc[0])
        if model_ok:
            for branch, want in (("pre", pre), ("post", post)):
                fits[("model", branch)] = fit_side(got, "stage", "sigma_n_MPa",
                                                   "k_1e12_m2", want, 1e-12 / DARCY_M2)

        print(f"  {'side':22s} {'branch':6s} {'k0 (D)':>10s} {'alpha':>9s} {'r^2':>6s} "
              f"{'n':>3s} {'sigma_n window':>16s}")
        for side, label in (("measured", "Table 2 k_D (ours)"),
                            ("published", "Kalantar Figure 8"),
                            ("model", "MODEL")):
            for branch in ("pre", "post"):
                f = fits.get((side, branch))
                if f is None:
                    continue
                rng = ("-" if not np.isfinite(f["lo"])
                       else f"{f['lo']:7.2f}-{f['hi']:6.2f}")
                r2 = "-" if not np.isfinite(f["r2"]) else f"{f['r2']:6.3f}"
                n = "-" if not np.isfinite(f["n"]) else f"{int(f['n']):3d}"
                print(f"  {label:22s} {branch:6s} {f['k0']:10.3f} {f['alpha']:9.4f} "
                      f"{r2:>6s} {n:>3s} {rng:>16s}")
                out.append(dict(sample=sample, side=side, branch=branch, **f))
        if not model_ok:
            state = ("no run on disk" if got is None
                     else f"run INCOMPLETE ({int(got['stage'].max())}/{len(ref)} stages)")
            print(f"  {'MODEL':22s} -- {state}, not fitted")

        sides = [s for s in ("measured", "published", "model") if ("model", "pre") in fits
                 or s != "model"]
        print()
        print(f"  {'':22s} {'alpha ratio':>13s} {'k0 gain':>10s}   "
              f"(k0 gain extrapolates to sigma_n = 0, far outside the data)")
        for side, label in (("measured", "Table 2 k_D (ours)"),
                            ("published", "Kalantar Figure 8"), ("model", "MODEL")):
            if (side, "pre") not in fits:
                continue
            p_, q_ = fits[(side, "pre")], fits[(side, "post")]
            print(f"  {label:22s} {q_['alpha'] / p_['alpha']:13.2f} "
                  f"{q_['k0'] / p_['k0']:10.2f}")

        live = [s for s in ("measured", "model") if (s, "pre") in fits]
        lo = max(fits[(s, b)]["lo"] for s in live for b in ("pre", "post"))
        hi = min(fits[(s, b)]["hi"] for s in live for b in ("pre", "post"))
        if hi > lo:
            print()
            print(f"  PERMEABILITY GAIN AT MATCHED sigma'_n -- an interpolation, "
                  f"common window {lo:.2f}-{hi:.2f} MPa")
            head = f"  {'sigma_n MPa':>12s}" + "".join(
                f"{lab:>12s}" for lab in ("measured", "published", "model")
                if lab != "model" or model_ok)
            print(head)
            for sn in np.linspace(lo, hi, 5):
                cells = ""
                for side in ("measured", "published", "model"):
                    if (side, "pre") not in fits:
                        continue
                    cells += f"{gain_at(fits, (side, 'pre'), (side, 'post'), sn):12.2f}"
                print(f"  {sn:12.2f}" + cells)
        print()

    if args.csv:
        pd.DataFrame(out).to_csv(args.csv, index=False)
        print(f"wrote {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
