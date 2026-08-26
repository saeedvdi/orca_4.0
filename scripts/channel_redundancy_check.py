import sys, numpy as np
from pathlib import Path
ROOT=Path("/media/geomechanics/Data4TB/projects/orca_4.0"); sys.path.insert(0,str(ROOT/"scripts"))
import table2_gate as G
EX=ROOT/"Examples/YeGhasemmi2018"; R="results_csv_hpc_rorqual"
RUNS=[("SW-T1 93_01","SWT1",f"SWT1/{R}/93_01_swt1_final_c26p9_resc9p19_ppfix_hpc.csv"),
      ("SW-T1 100_01","SWT1",f"SWT1/{R}/100_01_swt1_vm55um_ppfix_hpc.csv"),
      ("SW-T2 93_03","SWT2",f"SWT2/{R}/93_03_swt2_final_theta30_resc9p71_ppfix_hpc.csv"),
      ("SW-S3 93_05","SWS3",f"SWS3/{R}/93_05_sw3_final_resc1p40_ppfix_hpc.csv"),
      ("SW-S4 93_07","SWS4",f"SWS4/{R}/93_07_sw4_final_theta30_jrc5_ppfix_hpc.csv")]
print(f"{'run':<14}{'n':>3}{'mean tau_err/sn_err':>22}{'sd':>8}{'implied dip deg':>18}{'R^2 tau~sn':>12}")
for lab,s,rel in RUNS:
    r=G.score_run(EX/rel,s,"biot_ab_20260815",0.15,"stage1",55.0); t=r["table"]
    a=t["sigma_n_MPa_err"].values; b=t["tau_MPa_err"].values
    m=np.abs(a)>0.05
    rat=b[m]/a[m]
    sl=np.polyfit(a,b,1)[0]
    R2=np.corrcoef(a,b)[0,1]**2
    print(f"{lab:<14}{m.sum():>3}{rat.mean():>22.3f}{rat.std():>8.3f}"
          f"{np.degrees(np.arctan(1/sl)):>18.2f}{R2:>12.4f}")
print()
print("cot(30 deg) = %.4f   cot(35) = %.4f   cot(25) = %.4f" % (1/np.tan(np.radians(30)),1/np.tan(np.radians(35)),1/np.tan(np.radians(25))))
