#!/usr/bin/env python3
"""Where exactly does OG-SC burst, and what is its envelope doing there?"""
import math
import numpy as np, pandas as pd

C = ("/media/geomechanics/Data4TB/projects/orca_4.0/Examples/Kalantar2025/"
     "OGSC/results_csv_hpc/110_06_og_sc_bbfast_r3_hpc.csv")
d = pd.read_csv(C).sort_values("time").drop_duplicates("time", keep="last")

cols = ["time", "injection_pressure_pp", "bb_effective_normal_stress_pp",
        "bb_limit_tau_pp", "czm_tau_2_pp", "bb_jrc_mobilized_pp",
        "cohesion_effective_pp", "bb_dilation_angle_pp",
        "reported_czm_shear_slip_mm_pp", "hydraulic_aperture_um_pp",
        "effective_normal_paper_frame_mpa_pp", "shear_stress_paper_frame_mpa_pp"]
cols = [c for c in cols if c in d.columns]
d = d[cols].copy()

sn = d["bb_effective_normal_stress_pp"]
tl = d["bb_limit_tau_pp"]
tc = d["czm_tau_2_pp"].abs()
# put everything in MPa
for name, s in (("sn", sn), ("tl", tl), ("tc", tc)):
    d[name] = s / 1e6 if s.abs().max() > 1e4 else s
d["ratio"] = d["tc"] / d["tl"]
d["mu_lim"] = d["tl"] / d["sn"]

print("first crossing of tau/tau_limit >= 1:")
hit = d[d["ratio"] >= 1.0]
print(hit.head(1)[["time", "injection_pressure_pp", "sn", "tc", "tl", "ratio",
                   "reported_czm_shear_slip_mm_pp"]].to_string(index=False))

print("\ntrace every 200 s up to t=5200:")
sub = d[d["time"] <= 5200]
sub = sub[np.isclose(sub["time"] % 200.0, 0.0, atol=1.0)]
print(sub[["time", "injection_pressure_pp", "sn", "tc", "tl", "ratio", "mu_lim",
           "cohesion_effective_pp", "bb_dilation_angle_pp",
           "reported_czm_shear_slip_mm_pp", "hydraulic_aperture_um_pp"]]
      .to_string(index=False, float_format=lambda v: f"{v:9.4f}"))

# What the Barton-Bandis formula alone would give, at the deck's constants.
JRC, JCS, PHI_R = 4.23, 153.0, 22.660
print("\nBB formula vs the material's own limit (pre-burst rows):")
for t in (400, 1600, 2800, 4000, 4400, 4800):
    r = d[d["time"] <= t].iloc[-1]
    ang = PHI_R + JRC * math.log10(JCS / r["sn"])
    print(f"  t={t:5.0f}  sn={r['sn']:7.3f}  tau_lim(model)={r['tl']:7.3f}  "
          f"BB(no coh)={r['sn']*math.tan(math.radians(ang)):7.3f}  "
          f"angle={ang:6.3f} deg   model mu={r['mu_lim']:6.4f} "
          f"-> {math.degrees(math.atan(r['mu_lim'])):6.3f} deg")
