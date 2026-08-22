#!/usr/bin/env python3
"""
analyze_104.py -- read the 104 follow-ups against the 101 runs they interrogate.

    /home/geomechanics/miniforge/bin/python scripts/analyze_104.py

Reuses analyze_101's shut-in metrics unchanged, so the 104 numbers are computed
by exactly the code that produced the 101 numbers they are compared against.
The headline is `end_to_matched_permeability_ratio`: the end state against the
LOADING path at the same effective normal stress, which differences out
reversible closure.

Runs partial files; a shut-in deck says nothing until it is past its own
shut-in instant, and this reports how far each one has got.
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_101 import (  # noqa: E402
    Case,
    EXAMPLES,
    analyze_shutin,
    expected,
    load,
)
from build_101_decks import (  # noqa: E402
    SHUTIN_OBSERVE,
    SHUTIN_OBSERVE_SLOW,
    SHUTIN_TAU_FAST,
    SHUTIN_TAU_SLOW,
)

# 104 case, its 101 mirror, what changed, and the preregistered prediction
TRIOS = [
    (Case("SWS4", "104_01_sw4_shutin_nogouge", "104-1", "gouge-fill OFF", "shutin",
          hold=0.0, tau=SHUTIN_TAU_FAST, observe=SHUTIN_OBSERVE),
     "101_12_sw4_shutin_nohold", "use_slip_damage true -> false",
     "k ratio crosses 1.0 (mirror: 0.859)"),
    (Case("SWS4", "104_02_sw4_shutin_dscale0p038", "104-1", "dilation gain raised", "shutin",
          hold=0.0, tau=SHUTIN_TAU_FAST, observe=SHUTIN_OBSERVE),
     "101_12_sw4_shutin_nohold", "dilation_scale 0.0117 -> 0.038",
     "k ratio rises; clearing 1.0 means the dilation arm alone suffices"),
    (Case("SWS3", "104_03_sw3_shutin_nogouge", "104-1", "gouge-fill OFF (sign control)", "shutin",
          hold=0.0, tau=SHUTIN_TAU_FAST, observe=SHUTIN_OBSERVE),
     "101_11_sw3_shutin_nohold", "use_slip_damage true -> false",
     "k ratio rises above 1.497"),
    (Case("SWT2", "104_04_swt2_shutin_slowtau", "104-2", "slow bleed-off", "shutin",
          hold=200.0, tau=SHUTIN_TAU_SLOW, observe=SHUTIN_OBSERVE_SLOW),
     "101_10_swt2_shutin_nohold", "tau 150 -> 1500 s (no parameter change)",
     "within ~2% of 1.459"),
    (Case("SWS3", "104_05_sw3_shutin_slowtau", "104-2", "slow bleed-off", "shutin",
          hold=200.0, tau=SHUTIN_TAU_SLOW, observe=SHUTIN_OBSERVE_SLOW),
     "101_11_sw3_shutin_nohold", "tau 150 -> 1500 s (no parameter change)",
     "within ~2% of 1.497"),
]

MIRROR_CSV = "results_csv_hpc_rorqual"


def mirror_metrics(sample, stem, hold, tau, observe):
    """Recompute the 101 mirror through the same code path."""
    case = Case(sample, stem, "mirror", "", "shutin",
                hold=hold, tau=tau, observe=observe)
    if not case.csv_path.is_file():
        return None
    return analyze_shutin(case, load(case))


def main():
    rows = []
    for case, mirror, changed, prediction in TRIOS:
        print("=" * 100)
        print(f"{case.stem}   [{case.group}]  {case.design}")
        print(f"   mirror     {mirror}")
        print(f"   changed    {changed}")
        print(f"   predicted  {prediction}")
        print("=" * 100)

        if not case.csv_path.is_file():
            print(f"   no CSV yet at {case.csv_path.relative_to(ROOT)}\n")
            continue

        frame = load(case)
        end_time, _, t_shut = expected(case)
        t_now = float(frame["time"].iloc[-1])
        print(f"   reached t = {t_now:.1f} of {end_time:.1f} s "
              f"({100 * t_now / end_time:.0f}%);  shut-in at {t_shut:.1f} s")
        if t_now < t_shut:
            print("   -> not past shut-in.  Nothing decided; re-run later.\n")
            continue

        res = analyze_shutin(case, frame)
        # The mirror ran the fast schedule, so for arm 2 its hold/tau differ.
        mir = mirror_metrics(case.sample, mirror, 0.0, SHUTIN_TAU_FAST, SHUTIN_OBSERVE)

        k_new = res["end_to_matched_permeability_ratio"]
        a_new = res["end_to_matched_aperture_ratio"]
        print(f"   {'':14s}{'k ratio':>12s}{'aperture':>12s}{'slip end mm':>14s}"
              f"{'post-shutin um':>16s}")
        if mir:
            print(f"   {'mirror (101)':14s}{mir['end_to_matched_permeability_ratio']:12.3f}"
                  f"{mir['end_to_matched_aperture_ratio']:12.3f}"
                  f"{mir['slip_at_shutin_mm']:14.6f}"
                  f"{mir['maximum_post_shutin_growth_mm'] * 1e3:16.3f}")
        print(f"   {'104 deck':14s}{k_new:12.3f}{a_new:12.3f}"
              f"{res['slip_at_shutin_mm']:14.6f}"
              f"{res['maximum_post_shutin_growth_mm'] * 1e3:16.3f}")

        if mir:
            k_old = mir["end_to_matched_permeability_ratio"]
            delta = 100.0 * (k_new - k_old) / k_old
            crossed = (k_old < 1.0) != (k_new < 1.0)
            note = "  <== SIGN FLIPPED" if crossed else ""
            print(f"   change {delta:+.1f}%   "
                  f"{'still below 1.0' if k_new < 1.0 else 'above 1.0'}{note}")
            rows.append(dict(case=case.stem, group=case.group, mirror=mirror,
                             changed=changed, k_mirror=k_old, k_104=k_new,
                             pct_change=delta, sign_flipped=crossed))
        print()

    if rows:
        out = ROOT / "doc/independent_analysis/DISCUSSION_104_METRICS.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rows).to_csv(out, index=False, float_format="%.9g")
        print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
