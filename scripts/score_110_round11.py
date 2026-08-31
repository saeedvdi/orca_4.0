#!/usr/bin/env python3
"""
Score the Kalantar Round-11 platen arms against their preregistered gate.

Reports, for every run given (or for the whole Round-11 set plus its baselines
when called with no arguments):

  dp_MPa   the rise in interface_pressure_pp over the pre-slip part of the ramp.
           Round 11 showed the OG-T deficit IS this number: 48.9 MPa of undrained
           poroelastic overpressure, times fault_pressure_coefficient = 1.0.  The
           round-12 drained-preload arm has to bring it under 3 MPa; ratio and slope
           only follow it.
  ratio    bb_effective_normal_stress_pp / effective_normal_paper_frame_mpa_pp,
           sampled at the last step before the joint has slipped 5 um.  This is
           the fraction of its due normal stress the joint actually receives.
  slope    d(bb_effective_normal_stress)/d(sigma_d), least squares over the
           pre-slip part of the ramp.  The correct value is sin^2(theta):
           0.2204 at 28 deg, 0.1922 at 26 deg, 0.2500 at 30 deg.
  peak     the largest tau/tau_limit reached, and the sigma_d at which
           tau/tau_limit first crosses 1.0.  The experiment holds OG-T to
           sigma_d = 160.43 MPa without yielding, so a crossing below that is
           a specimen that failed during its own preload.

GATE for 110_30_og_t_platen_bonded_r11: ratio >= 0.93, slope +0.20 +- 0.04, and
no crossing of tau/tau_limit = 1.0 below sigma_d = 160.43 MPa.

Usage:
    python3 scripts/score_110_round11.py [run.csv ...]
"""

import csv
import glob
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDY = os.path.join(ROOT, "Examples", "Kalantar2025")

SIGMA_D_TARGET = 160.43   # MPa, OG-T Table 2 stage 1
SLIP_SAMPLE_UM = 5.0      # sample the ratio before the joint has moved this far

# theta by specimen, for the correct slope
THETA = {"og_t": 28.0, "og_sh": 30.0, "og_sc": 30.0}

BASELINES = [
    "Kalantar2025/OGT/results_csv_hpc/110_16_og_t_traction_probe_r7_hpc.csv",
    "Kalantar2025/OGT/results_csv_hpc/110_14_og_t_preload_probe_hpc.csv",
    "Kalantar2025/OGT/results_csv_hpc/110_08_og_t_bbfast_r4_hpc.csv",
    "Kalantar2025/OGSH/results_csv_hpc/110_13_og_sh_bbfast_r6_hpc.csv",
    "Kalantar2025/OGSC/results_csv_hpc/110_15_og_sc_bbfast_r6_hpc.csv",
]


def num(row, key):
    try:
        return float(row.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def theta_for(name):
    for stem, th in THETA.items():
        if stem in name:
            return th
    return None


def score(path):
    with open(path) as fh:
        rows = list(csv.DictReader(fh))
    rows = [r for r in rows if num(r, "time") > 0]
    if not rows:
        return None

    name = os.path.basename(path)
    th = theta_for(name)
    # 110_14 is the 26-degree arm; its correct slope is sin^2(26)
    if "110_14" in name:
        th = 26.0

    pre = []
    ratio = None
    for r in rows:
        sd = num(r, "differential_stress_mpa_pp")
        slip_um = abs(num(r, "czm_shear_slip_mm_pp")) * 1000.0
        sn = num(r, "bb_effective_normal_stress_pp") / 1e6
        pn = num(r, "effective_normal_paper_frame_mpa_pp")
        if slip_um <= SLIP_SAMPLE_UM:
            if sd > 5.0:
                pre.append((sd, sn))
                if pn:
                    ratio = sn / pn
        else:
            break

    slope = None
    if len(pre) > 2:
        mx = sum(p[0] for p in pre) / len(pre)
        my = sum(p[1] for p in pre) / len(pre)
        den = sum((a - mx) ** 2 for a, _ in pre)
        if den > 0:
            slope = sum((a - mx) * (b - my) for a, b in pre) / den

    # Round 12 gate 1: the pore-pressure rise over the preload ramp. The whole OG-T
    # deficit is alpha_f * p, so this is the quantity the drained-preload arm has to
    # move; the ratio and the slope only follow it.
    p_first = num(rows[0], "interface_pressure_pp") / 1e6
    p_pre = [num(r, "interface_pressure_pp") / 1e6 for r in rows
             if abs(num(r, "czm_shear_slip_mm_pp")) * 1000.0 <= SLIP_SAMPLE_UM]
    dp = (max(p_pre) - p_first) if p_pre else None

    peak = 0.0
    cross_sd = None
    for r in rows:
        tl = num(r, "bb_limit_tau_pp") / 1e6
        tm = num(r, "shear_traction_magnitude_pa") / 1e6
        if tl <= 0:
            continue
        q = tm / tl
        peak = max(peak, q)
        if q >= 1.0 and cross_sd is None:
            cross_sd = num(r, "differential_stress_mpa_pp")

    return dict(name=name.replace("_hpc.csv", "").replace(".csv", ""),
                theta=th, ratio=ratio, slope=slope, peak=peak, cross=cross_sd, dp=dp,
                sd_max=max(num(r, "differential_stress_mpa_pp") for r in rows),
                slip_max=max(abs(num(r, "czm_shear_slip_mm_pp")) for r in rows) * 1000.0)


def main(argv):
    if argv:
        paths = argv
    else:
        paths = [os.path.join(STUDY, "..", p) for p in BASELINES]
        for pat in ("OGT/results_csv_*/110_3*_r11*.csv",
                    "OGSH/results_csv_*/110_3*_r11*.csv",
                    "OGSC/results_csv_*/110_3*_r11*.csv",
                    "OGT/results_csv_*/110_3*_r12*.csv"):
            paths += sorted(glob.glob(os.path.join(STUDY, pat)))

    print(f"{'run':44s}{'th':>5}{'target':>8}{'slope':>9}{'ratio':>8}"
          f"{'peak t/tl':>11}{'yield@sd':>10}{'sd_max':>9}{'slip_um':>10}{'dp_MPa':>9}")
    print("-" * 123)
    for p in paths:
        if not os.path.exists(p):
            print(f"{os.path.basename(p):44s}  (not run yet)")
            continue
        s = score(p)
        if s is None:
            print(f"{os.path.basename(p):44s}  (no time steps)")
            continue
        tgt = math.sin(math.radians(s["theta"])) ** 2 if s["theta"] else float("nan")
        f = lambda v, w, d: (f"{v:{w}.{d}f}" if v is not None else " " * (w - 1) + "-")
        print(f"{s['name']:44s}{s['theta'] or 0:5.0f}{tgt:8.4f}"
              f"{f(s['slope'], 9, 4)}{f(s['ratio'], 8, 3)}{s['peak']:11.3f}"
              f"{f(s['cross'], 10, 1)}{s['sd_max']:9.1f}{s['slip_max']:10.1f}"
              f"{f(s['dp'], 9, 2)}")

    print()
    print(f"GATE  110_36 (round 12, drained preload) passes on ALL FIVE:")
    print(f"        dp_MPa <= 3.0     ratio >= 0.93     slope = +0.22 +- 0.04")
    print(f"        no tau/tau_limit = 1.0 below sigma_d = {SIGMA_D_TARGET} MPa")
    print(f"        slip_um < 10 at the end of the preload")
    print(f"      If 110_36 fails, DISCARD 110_37 rather than analysing it.")
    print(f"PRIOR 110_30 (round 11) required ratio >= 0.93, slope = +0.20 +- 0.04 and")
    print(f"      no yield below {SIGMA_D_TARGET} MPa. It failed all three; the null fired.")
    print(f"NULL  if 110_32 (locked joint, zero slip) still shows ratio ~ 0.5, the")
    print(f"      shielding is elastic and no platen BC repairs it -- go at the")
    print(f"      interface map or the mesh instead, and treat a 110_30 pass as")
    print(f"      over-constraint.")


if __name__ == "__main__":
    main(sys.argv[1:])
