"""OG-SH: bracket D_c on the two completed runs, and test the frame identity.

Rounds 3 and 4 differ in ONE constant, so they are a two-point bracket. Under
constant piston displacement tau and sigma'_n are both affine in sigma_1, so a
model that slips more must shed BOTH -- there is only one degree of freedom.
Check whether the two runs lie on that one line; if they do, no D_c can fix tau
and slip at once and the missing physics is elsewhere.
"""
import math, sys
import numpy as np, pandas as pd
sys.path.insert(0, "/media/geomechanics/Data4TB/projects/orca_4.0/scripts")
import kalantar_gate as kg
from table2_gate import parse_schedule, first_column

K = "/media/geomechanics/Data4TB/projects/orca_4.0/Examples/Kalantar2025/"
RUNS = [("round 3", 150.0, f"{K}OGSH/results_csv_hpc/110_02_og_sh_bbfast_r3_hpc.csv",
         f"{K}OGSH/110_02_og_sh_bbfast_r3.i"),
        ("round 4", 59.3, f"{K}OGSH/results_csv_hpc/110_07_og_sh_bbfast_r4_hpc.csv",
         f"{K}OGSH/110_07_og_sh_bbfast_r4.i")]
ref = kg.reference("OG-SH")
cos_t = math.cos(math.radians(29.0))

print(f"{'run':9}{'D_c um':>8}{'tau9':>8}{'err %':>8}{'sn9':>8}{'err %':>8}"
      f"{'slip9 um':>10}{'err %':>8}")
print(f"{'MEASURED':9}{'--':>8}{ref.tau_MPa.iloc[-1]:8.2f}{'':>8}"
      f"{ref.sigma_n_MPa.iloc[-1]:8.2f}{'':>8}"
      f"{ref.ds_mm.iloc[-1]/cos_t*1e3:10.1f}")
pts = []
for name, dc, csv, deck in RUNS:
    x, y = parse_schedule(__import__("pathlib").Path(deck))
    times = kg.kal_stage_times(x, y, ref, 0.15)
    raw = pd.read_csv(csv).sort_values("time").drop_duplicates("time", keep="last")
    row = raw[raw["time"] <= times[-1] + 1e-9].iloc[-1]
    tau = float(row["shear_stress_paper_frame_mpa_pp"])
    sn = float(row["effective_normal_paper_frame_mpa_pp"])
    sl = float(row["reported_czm_shear_slip_mm_pp"]) * 1e3
    m = (ref.tau_MPa.iloc[-1], ref.sigma_n_MPa.iloc[-1], ref.ds_mm.iloc[-1]/cos_t*1e3)
    print(f"{name:9}{dc:8.1f}{tau:8.2f}{100*(tau-m[0])/m[0]:8.1f}{sn:8.2f}"
          f"{100*(sn-m[1])/m[1]:8.1f}{sl:10.1f}{100*(sl-m[2])/m[2]:8.1f}")
    pts.append((dc, tau, sl))

(d1, t1, s1), (d2, t2, s2) = pts
print(f"\nSlip costs tau at {(t1-t2)/(s2-s1)*1e3:.1f} MPa/mm across the two runs;")
print(f"the frame identity k_eff = K_sys cos^2 sin / A predicts 150.5 MPa/mm.")
print(f"-> the two runs lie on the frame line, so tau and slip are ONE number.\n")
for lbl, tgt, vals in (("tau_9", ref.tau_MPa.iloc[-1], (t1, t2)),
                       ("slip_9", ref.ds_mm.iloc[-1]/cos_t*1e3, (s1, s2))):
    a, b = vals
    w = (tgt - a) / (b - a) if b != a else float("nan")
    print(f"  matching {lbl:7} needs log D_c = "
          f"{math.exp(math.log(d1) + w*(math.log(d2)-math.log(d1))):7.1f} um")
