#!/usr/bin/env python3
"""The preload identity on the ROUND-3 runs, against fracture-tip clearance.

Requirement during the axial ramp:
    d sigma'_n = sin^2(theta) * d sigma_1  -  d p_fracture
evaluated on the CONSTITUTIVE channel (bb_effective_normal_stress_pp), an area
average over the whole interface. The window is the axial ramp only: from the
first loaded row to where sigma_1 first reaches 98 % of its running maximum, so
the pore correction stays small on every specimen.
"""
import math
import numpy as np, pandas as pd

BASE = "/media/geomechanics/Data4TB/projects/orca_4.0/Examples/Kalantar2025/"
RUNS = [("OG-SH", 29.0, 120.0, f"{BASE}OGSH/results_csv_hpc/110_02_og_sh_bbfast_r3_hpc.csv"),
        ("OG-SC", 30.0, 100.0, f"{BASE}OGSC/results_csv_hpc/110_06_og_sc_bbfast_r3_hpc.csv"),
        ("OG-T",  28.0, 100.0, f"{BASE}OGT/results_csv_hpc/110_04_og_t_bbfast_r3_hpc.csv")]
D = 49.98

print(f"{'spec':6}{'th':>5}{'tipclr':>8} | {'ds1':>7}{'dp':>6}{'pred dsn':>9}"
      f"{'meas dsn':>9}{'ratio':>7} | {'slip_um':>8}  window")
for name, th, L, path in RUNS:
    d = pd.read_csv(path).sort_values("time").drop_duplicates("time", keep="last")
    t = d["time"].to_numpy()
    s1 = d["sigma1_reaction_mpa_pp"].to_numpy()
    sn = d["bb_effective_normal_stress_pp"].to_numpy() / 1e6
    p = d["injection_pressure_pp"].to_numpy() / 1e6
    sl = d["reported_czm_shear_slip_mm_pp"].to_numpy() * 1e3

    lo = 1
    peak = s1.max()
    hi = int(np.argmax(s1 >= 0.98 * peak))
    if hi <= lo:
        hi = len(t) - 1
    ds1, dp = s1[hi] - s1[lo], p[hi] - p[lo]
    pred = math.sin(math.radians(th)) ** 2 * ds1 - dp
    meas = sn[hi] - sn[lo]
    clr = (L - D / math.tan(math.radians(th))) / 2.0
    print(f"{name:6}{th:5.0f}{clr:8.2f} | {ds1:7.2f}{dp:6.2f}{pred:9.2f}"
          f"{meas:9.2f}{meas/pred:7.3f} | {sl[hi]:8.1f}  {t[lo]:.1f}-{t[hi]:.1f}s")
